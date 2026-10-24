#!/usr/bin/env python3
"""Trail of Extinction - title C idle loop (hero stands still, only background moves).

Deterministic procedural animation on top of frame 0 of title_c_loop_bg.mp4.
  * camera locked, hero pixels pasted back from the still on every frame
  * clouds  : periodic travelling-wave warp of an inpainted sky plate (billows/drifts left)
  * smoke   : travelling-wave warp along the painted castle plumes, rising up-left
  * grass   : small periodic displacement warp, masked to the lower ground
  * ash/embers : periodic particle systems (respawn schedule repeats every loop)
  * crows   : 3 silhouettes orbiting the castle, integer flap count per loop
Every effect is a function of phase = t/T, so frame N == frame 0 (seamless) and
all warps are exactly zero at t = 0 (frame 0 == the still, apart from particles).

usage: python3 make_idle.py [--src title_c_loop_bg.mp4] [--out DIR] [--frames 216]
"""
import argparse, os, subprocess, math
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument('--src', default='/tmp/tlg/docs_art/title_screen/title_c_loop_bg.mp4')
ap.add_argument('--still', default='', help='optional PNG still (overrides --src frame 0)')
ap.add_argument('--out', default='/workspace/title_idle')
ap.add_argument('--frames', type=int, default=216)   # 9.0 s @ 24 fps
ap.add_argument('--fps', type=int, default=24)
ap.add_argument('--crf', type=int, default=12)
ap.add_argument('--only', type=str, default='', help='comma list of frame idx to dump as PNG only')
args = ap.parse_args()

OUT = args.out; WORK = os.path.join(OUT, 'work'); os.makedirs(WORK, exist_ok=True)
N, FPS = args.frames, args.fps
T = N / FPS
W, H = 1920, 1080
TAU = 2 * math.pi

# ---------------------------------------------------------------- still
if args.still:
    base8 = cv2.imread(args.still)
else:
    f0 = os.path.join(WORK, 'f0.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', args.src, '-frames:v', '1', f0], check=True)
    base8 = cv2.imread(f0)
assert base8.shape == (H, W, 3)
base = base8.astype(np.float32)
L = cv2.cvtColor(base8, cv2.COLOR_BGR2GRAY).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def smooth(m, r):
    k = int(r) * 2 + 1
    return cv2.GaussianBlur(m.astype(np.float32), (k, k), r / 2.0)

def dil(m, r):
    if r <= 0: return m.astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    return cv2.dilate(m.astype(np.uint8), k)

def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

rng_noise = np.random.RandomState(7)
def lowfreq_noise(scale, seed):
    r = np.random.RandomState(seed)
    small = r.rand(H // scale + 3, W // scale + 3).astype(np.float32)
    big = cv2.resize(small, (W + 3 * scale, H + 3 * scale), interpolation=cv2.INTER_CUBIC)
    return big[scale:scale + H, scale:scale + W] * 2 - 1

# ---------------------------------------------------------------- hero mask
hero_png = os.path.join(WORK, 'hero_mask.png')
cv2.setRNGSeed(0)
gm = np.zeros((H, W), np.uint8)
bgm = np.zeros((1, 65), np.float64); fgm = np.zeros((1, 65), np.float64)
cv2.grabCut(base8, gm, (545, 450, 455, 540), bgm, fgm, 6, cv2.GC_INIT_WITH_RECT)
hm = ((gm == 1) | (gm == 3))
n, lab, st, _ = cv2.connectedComponentsWithStats(hm.astype(np.uint8))
hm = lab == (1 + np.argmax(st[1:, 4]))
dark = L < 70
hm[(yy >= 860) & ~dark] = False                      # grabcut leaks into the road
boot = np.zeros_like(hm)
for (x0, y0, x1, y1) in [(695, 860, 765, 995), (765, 860, 825, 985)]:
    boot[y0:y1, x0:x1] = True
hm |= boot & dark
sw = np.zeros((H, W), np.uint8); cv2.line(sw, (792, 700), (992, 942), 255, 16)
hm |= (sw > 0) & (L < 200) & ~((yy > 720) & (L > 175))  # sword blade
hm = cv2.morphologyEx(hm.astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(hm)
keep = np.zeros_like(hm)
for i in range(1, n):
    if st[i, 4] > 150: keep[lab == i] = 255
cv2.imwrite(hero_png, keep)
hero_hard = keep > 0
HERO = np.maximum(dil(hero_hard, 3).astype(np.float32), smooth(dil(hero_hard, 5), 3))[..., None]
ys, xs = np.nonzero(hero_hard)
HERO_BBOX = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)

# ---------------------------------------------------------------- sky / structures
hz_pts = np.array([(0, 452), (200, 466), (420, 478), (640, 490), (860, 498), (1000, 500),
                   (1300, 505), (1560, 505), (1700, 486), (1920, 482)], np.float32)
horizon = np.interp(np.arange(W), hz_pts[:, 0], hz_pts[:, 1]).astype(np.float32)
sky_region = (yy < horizon[None, :]).astype(np.float32)
SKY = smooth(sky_region * sstep(0, 1, (horizon[None, :] - 6 - yy) / 18), 4)   # fades out near horizon

Lb = smooth(L, 15)
struct = ((L < 86) | (L < Lb - 20))
boxes = np.zeros((H, W), bool)
boxes[110:740, 0:500] = True          # dead trees left
boxes[300:640, 960:1620] = True       # castle
boxes[520:820, 1580:1840] = True      # right dead tree
struct &= boxes
struct = cv2.morphologyEx(struct.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) > 0
struct |= ~sky_region.astype(bool)    # everything below the horizon is "structure" for the sky pass
inpaint_reg = dil(struct, 3)
STRUCT = np.maximum(inpaint_reg.astype(np.float32), smooth(dil(struct, 6), 3))
plate_src = base8.copy()
plate = cv2.inpaint(plate_src, (inpaint_reg * 255).astype(np.uint8), 9, cv2.INPAINT_TELEA).astype(np.float32)
plate[inpaint_reg == 0] = base[inpaint_reg == 0]
SKYM = (SKY * (1 - STRUCT))[..., None]

# Sky motion = pure periodic warp (no cross-fade, so the painted brush texture stays crisp).
# Each term is A*(sin(theta + w t) - sin(theta)): zero at t=0, periodic in T, and its
# phase travels leftwards (clouds) or upwards (smoke).
nzA = smooth(lowfreq_noise(300, 11), 60); nzB = smooth(lowfreq_noise(300, 12), 60); nzC = smooth(lowfreq_noise(120, 13), 30)
top = 0.45 + 0.55 * np.clip(1 - yy / 470, 0, 1)            # high clouds move more (parallax)
CLOUD_TERMS = [  # (axis, amplitude field, theta field, cycles per loop)
    ('x', 10.0 * top, TAU * (xx / 1100.0 + yy / 1600.0 + 0.25 * nzA), 1),
    ('y', 4.0 * top, TAU * (xx / 800.0 - yy / 600.0 + 0.25 * nzB), 1),
    ('x', 3.0 * top, TAU * (xx / 480.0 + 0.2 * nzB), 2),
    ('y', 1.5 * top, TAU * (xx / 400.0 + yy / 350.0 + 0.2 * nzA), 2),
]
# smoke plumes: soft ellipses along the painted plumes
smk = np.zeros((H, W), np.float32)
for (cx, cy, ax, ay, ang) in [(1045, 445, 70, 60, -35), (1300, 340, 45, 70, -15),
                              (1455, 395, 70, 120, -35), (1405, 300, 80, 60, -30),
                              (1500, 470, 30, 40, -20), (1110, 395, 40, 40, -30)]:
    cv2.ellipse(smk, (cx, cy), (ax, ay), ang, 0, 360, 1.0, -1)
SMOKE = smooth(smooth(smk, 40), 30)
along = yy + 0.45 * xx       # plumes lean up-left, waves travel along them
SMOKE_TERMS = [
    ('y', 4.0 * SMOKE, TAU * (along / 170.0 + 0.15 * nzC), 3),
    ('x', 2.5 * SMOKE, TAU * (along / 240.0 + 0.15 * nzA), 3),
    ('y', 1.0 * SMOKE, TAU * (along / 110.0 + 0.15 * nzC), 5),
]
SKY_TERMS = [(ax_, A.astype(np.float32), th.astype(np.float32), np.sin(th).astype(np.float32), k)
             for (ax_, A, th, k) in CLOUD_TERMS + SMOKE_TERMS]

def sky_disp(t):
    dx = np.zeros((H, W), np.float32); dy = np.zeros((H, W), np.float32)
    for ax_, A, th, s0, k in SKY_TERMS:
        d = A * (np.sin(th + TAU * k * t / T) - s0)
        if ax_ == 'x': dx += d
        else: dy += d
    return dx, dy

# ---------------------------------------------------------------- grass mask
hsv = cv2.cvtColor(base8, cv2.COLOR_BGR2HSV).astype(np.float32)
tex = np.sqrt(np.maximum(smooth(L * L, 4) - smooth(L, 4) ** 2, 0))
road = (L > 150) & (hsv[..., 1] < 70)
road = smooth(dil(road, 4), 6)
ground = sstep(560, 700, yy) * (1 - sky_region)
GRASS = ground * sstep(6, 16, tex) * (1 - road) * (1 - smooth(dil(hero_hard, 14), 6))
GRASS = smooth(GRASS, 3)
amp = (0.6 + 2.6 * sstep(560, 1080, yy)) * GRASS          # px
gphi = TAU * (xx / 420.0 + 0.35 * lowfreq_noise(90, 21) + yy / 900.0)
gphi2 = TAU * (xx / 170.0 + 0.5 * lowfreq_noise(50, 22))

def grass_dx(t):
    w1 = TAU * 3 * t / T; w2 = TAU * 8 * t / T
    d = 0.75 * (np.sin(w1 + gphi) - np.sin(gphi)) + 0.25 * (np.sin(w2 + gphi2) - np.sin(gphi2))
    return (amp * d).astype(np.float32)

# ---------------------------------------------------------------- particles
def sprite(r_px, elong=1.0, ang=0.0, ss=4):
    R = int(math.ceil(r_px * max(1, elong) * 2 + 2))
    sz = (2 * R + 1) * ss
    m = np.zeros((sz, sz), np.float32)
    c = sz // 2
    cv2.ellipse(m, (c, c), (max(1, int(r_px * elong * ss)), max(1, int(r_px * ss))), ang, 0, 360, 1.0, -1, cv2.LINE_AA)
    m = cv2.resize(m, (2 * R + 1, 2 * R + 1), interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(m, (0, 0), 0.6)

def blit(canvas_c, canvas_a, spr, x, y, color, alpha):
    """premultiplied 'over' of a sprite at subpixel-ish centre (x,y)"""
    h, w = spr.shape; x0 = int(round(x)) - w // 2; y0 = int(round(y)) - h // 2
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb: return
    a = spr[ya - y0:yb - y0, xa - x0:xb - x0] * alpha
    ca = canvas_a[ya:yb, xa:xb]; cc = canvas_c[ya:yb, xa:xb]
    cc *= (1 - a)[..., None]; cc += a[..., None] * np.array(color, np.float32)
    ca *= (1 - a); ca += a

prng = np.random.RandomState(1234)
ASH = []
for i in range(330):
    z = prng.rand() ** 1.6                     # 0 far .. 1 near
    m = int(prng.choice([2, 3]))               # spawns per loop
    life = T / m
    spawns = []
    for j in range(m):
        spawns.append(dict(x=prng.uniform(-50, W + 250), y=prng.uniform(40, H - 20),
                           vx=-(25 + 110 * z) * prng.uniform(0.7, 1.3), vy=prng.uniform(-14, 10),
                           wob=prng.uniform(4, 18), wf=prng.randint(1, 4), wp=prng.rand() * TAU))
    light = prng.rand() < 0.45
    col = (205, 200, 192) if light else (48, 44, 42)    # BGR
    ASH.append(dict(z=z, m=m, life=life, off=prng.rand() * T, sp=spawns, col=col,
                    a=(0.35 + 0.5 * z) * (0.8 if light else 1.0),
                    spr=sprite(0.7 + 1.6 * z, elong=prng.uniform(1.0, 2.2), ang=prng.uniform(0, 180))))
EMB = []
for i in range(46):
    m = int(prng.choice([2, 3])); life = T / m
    right = prng.rand() < 0.7
    spawns = []
    for j in range(m):
        if right: sx, sy = prng.uniform(1050, 1960), prng.uniform(820, 1090)
        else: sx, sy = prng.uniform(0, 560), prng.uniform(840, 1090)
        spawns.append(dict(x=sx, y=sy, vx=-prng.uniform(15, 55), vy=-prng.uniform(18, 45),
                           wob=prng.uniform(6, 20), wf=prng.randint(1, 4), wp=prng.rand() * TAU))
    r = prng.uniform(1.0, 2.1)
    EMB.append(dict(m=m, life=life, off=prng.rand() * T, sp=spawns, r=r, fl=prng.randint(4, 10),
                    flp=prng.rand() * TAU, core=sprite(r), glow=cv2.GaussianBlur(sprite(r * 2.2), (0, 0), 2.0)))

def particle_pos(p, t):
    tt = (t + p['off']) % T
    j = int(tt // p['life']) % p['m']; u = (tt - j * p['life']) / p['life']   # 0..1
    s = p['sp'][j]; lt = u * p['life']
    x = s['x'] + s['vx'] * lt + s['wob'] * math.sin(TAU * s['wf'] * u + s['wp'])
    y = s['y'] + s['vy'] * lt + 0.6 * s['wob'] * math.cos(TAU * s['wf'] * u * 1.3 + s['wp'])
    env = math.sin(math.pi * u) ** 0.7
    return x, y, env, u

# ---------------------------------------------------------------- crows
CROWS = [dict(c=(1262, 330), rx=170, ry=38, per=1, ph=0.0, span=17, tilt=-6, flaps=27),
         dict(c=(1290, 300), rx=250, ry=58, per=1, ph=0.0, span=20, tilt=4, flaps=24, rev=True),
         dict(c=(1285, 305), rx=330, ry=80, per=1, ph=0.0, span=14, tilt=-3, flaps=21)]
CROW_COL = (30, 34, 40)   # BGR, warm ink black

def crow_state(c, t):
    s = -1 if c.get('rev') else 1
    a = s * TAU * c['per'] * t / T + c['ph']
    x = c['c'][0] + c['rx'] * math.cos(a)
    y = c['c'][1] + c['ry'] * math.sin(a) + 6 * math.sin(2 * a)
    # the orbit is above eye level (horizon ~y490), so the near half of the circle is the
    # upper half on screen and the far half dips behind the towers
    front = math.sin(a) < 0
    vx = -s * c['rx'] * math.sin(a)   # screen direction of travel
    depth = 0.82 - 0.18 * math.sin(a)
    return x, y, front, vx, depth

def crow_find_hidden_phase(c):
    """pick an orbit phase so the crow sits behind the castle at t=0 (keeps frame 0 == still)"""
    best, bp = -1, 0.0
    for ph in np.linspace(0, TAU, 720, endpoint=False):
        c2 = dict(c, ph=ph); x, y, front, _, _ = crow_state(c2, 0.0)
        if front or not (0 <= int(x) < W and 0 <= int(y) < H): continue
        xi, yi = int(x), int(y)
        cover = STRUCT[max(0, yi - 10):yi + 10, max(0, xi - 14):xi + 14].min()
        if cover > best: best, bp = cover, ph
    return bp, best

for c in CROWS:
    c['ph'], cov = crow_find_hidden_phase(c)
    c['hidden0'] = cov

def draw_crow(cc, ca, c, t):
    x, y, front, vx, depth = crow_state(c, t)
    ss = 4; span = c['span'] * depth
    # flap: integer flaps per loop, with a slow glide modulation (also periodic)
    f = TAU * c['flaps'] * t / T
    glide = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(TAU * 2 * t / T + c['ph']))
    up = math.cos(f) * glide                         # +1 wings up, -1 wings down
    dirx = 1 if vx >= 0 else -1
    R = int(span) + 6; sz = (2 * R + 1) * ss; cx = cy = sz // 2
    m = np.zeros((sz, sz), np.uint8)
    hs = span * 0.5 * ss
    tip_y = -up * hs * 0.55; elb_y = -up * hs * 0.22 - hs * 0.05
    pts_l = [(cx - hs, cy + tip_y), (cx - hs * 0.45, cy + elb_y), (cx, cy)]
    pts_r = [(cx + hs, cy + tip_y), (cx + hs * 0.45, cy + elb_y), (cx, cy)]
    th = max(1, int(span * 0.13 * ss))
    for pts in (pts_l, pts_r):
        p = np.array(pts, np.int32)
        cv2.polylines(m, [p], False, 255, th, cv2.LINE_AA)
        # wing chord (gives the wing some area near the body)
        cv2.fillPoly(m, [np.array([pts[2], pts[1], (pts[1][0], pts[1][1] + th * 0.9), (pts[2][0], pts[2][1] + th * 1.2)], np.int32)], 255, cv2.LINE_AA)
    bl = span * 0.32 * ss
    cv2.ellipse(m, (cx, int(cy + th * 0.6)), (int(bl * 0.6), max(1, int(th * 0.75))), 0, 0, 360, 255, -1, cv2.LINE_AA)
    cv2.circle(m, (int(cx + dirx * bl * 0.62), int(cy + th * 0.3)), max(1, int(th * 0.6)), 255, -1, cv2.LINE_AA)  # head
    tail = np.array([(cx - dirx * bl * 0.5, cy + th * 0.4), (cx - dirx * bl * 0.95, cy + th * 0.1),
                     (cx - dirx * bl * 0.95, cy + th * 1.3)], np.int32)
    cv2.fillPoly(m, [tail], 255, cv2.LINE_AA)
    M = cv2.getRotationMatrix2D((cx, cy), c['tilt'] * dirx, 1.0)
    m = cv2.warpAffine(m, M, (sz, sz), flags=cv2.INTER_LINEAR)
    spr = cv2.resize(m.astype(np.float32) / 255, (2 * R + 1, 2 * R + 1), interpolation=cv2.INTER_AREA)
    spr = cv2.GaussianBlur(spr, (0, 0), 0.5)
    blit(cc, ca, spr, x, y, CROW_COL, 0.92 * (0.85 + 0.15 * depth))
    return front

# ---------------------------------------------------------------- render
def render(k):
    t = k / FPS
    t = t % T
    img = base.copy()
    # grass sway
    dx = grass_dx(t)
    if np.any(dx):
        warped = cv2.remap(base, xx - dx, yy + 0.25 * np.abs(dx), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        g = GRASS[..., None]
        img = img * (1 - g) + warped * g
    # sky: clouds then smoke, on the inpainted plate
    sdx, sdy = sky_disp(t)
    sky = cv2.remap(plate, xx - sdx, yy - sdy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    # crows behind the castle are drawn into the sky before structures go back on
    cc = np.zeros_like(base); ca = np.zeros((H, W), np.float32)
    fronts = []
    for c in CROWS:
        x, y, front, _, _ = crow_state(c, t)
        if not front: draw_crow(cc, ca, c, t)
        else: fronts.append(c)
    sky = sky * (1 - ca[..., None]) + cc
    img = img * (1 - SKYM) + sky * SKYM
    # front crows, ash, embers (all go behind the hero)
    cc = np.zeros_like(base); ca = np.zeros((H, W), np.float32)
    for c in fronts: draw_crow(cc, ca, c, t)
    for p in ASH:
        x, y, env, u = particle_pos(p, t)
        blit(cc, ca, p['spr'], x, y, p['col'], p['a'] * env)
    img = img * (1 - ca[..., None]) + cc
    glow = np.zeros_like(base)
    for p in EMB:
        x, y, env, u = particle_pos(p, t)
        fl = 0.65 + 0.35 * math.sin(TAU * p['fl'] * ((t + p['off']) % T) / T * 3 + p['flp'])
        e = env * fl
        for spr, colr, gain in ((p['glow'], (40, 90, 230), 0.7), (p['core'], (120, 200, 255), 1.0)):
            hh, ww = spr.shape; x0 = int(round(x)) - ww // 2; y0 = int(round(y)) - hh // 2
            xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + ww), min(H, y0 + hh)
            if xa < xb and ya < yb:
                glow[ya:yb, xa:xb] += (spr[ya - y0:yb - y0, xa - x0:xb - x0] * e * gain)[..., None] * np.array(colr, np.float32)
    img = 255 - (255 - img) * (1 - np.clip(glow / 255, 0, 1))   # screen blend
    # hero lock
    img = img * (1 - HERO) + base * HERO
    return np.clip(img + 0.5, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    if args.only:
        for k in [int(s) for s in args.only.split(',')]:
            cv2.imwrite(os.path.join(WORK, f'fr_{k:04d}.png'), render(k))
        raise SystemExit
    # ---- YUV-domain delta encode -------------------------------------------------------
    # The source's own decoded YUV420 planes of frame 0 are reused, and only the RGB delta
    # (render - still) is converted (BT.709 limited) and added.  Unchanged pixels (hero, most
    # of the frame at t=0) therefore carry *bit-identical* YUV to title_c_loop_bg.mp4 frame 0
    # before x264, so the cut to the walking video has no colour-matrix/rounding shift.
    yraw = subprocess.run(['ffmpeg', '-v', 'error', '-i', args.src, '-frames:v', '1', '-f', 'rawvideo',
                           '-pix_fmt', 'yuv420p', '-'], stdout=subprocess.PIPE, check=True).stdout
    Y0 = np.frombuffer(yraw[:W * H], np.uint8).reshape(H, W).astype(np.float32)
    U0 = np.frombuffer(yraw[W * H:W * H * 5 // 4], np.uint8).reshape(H // 2, W // 2).astype(np.float32)
    V0 = np.frombuffer(yraw[W * H * 5 // 4:], np.uint8).reshape(H // 2, W // 2).astype(np.float32)
    def to_yuv(fr):
        d = fr.astype(np.float32) - base8.astype(np.float32)          # BGR delta
        B, G, R = d[..., 0], d[..., 1], d[..., 2]
        dy = 219 / 255 * (0.2126 * R + 0.7152 * G + 0.0722 * B)
        du = 224 / 255 * (-0.114572 * R - 0.385428 * G + 0.5 * B)
        dv = 224 / 255 * (0.5 * R - 0.454153 * G - 0.045847 * B)
        du = du.reshape(H // 2, 2, W // 2, 2).mean((1, 3)); dv = dv.reshape(H // 2, 2, W // 2, 2).mean((1, 3))
        q = lambda a: np.clip(np.round(a), 0, 255).astype(np.uint8).tobytes()
        return q(Y0 + dy) + q(U0 + du) + q(V0 + dv)
    yuv_path = os.path.join(WORK, 'idle_yuv420p.raw')
    keep_idx = {0, 1, N - 1}
    with open(yuv_path, 'wb') as fh:
        for k in range(N):
            fr = render(k)
            if k in keep_idx: cv2.imwrite(os.path.join(WORK, f'raw_{k:04d}.png'), fr)
            fh.write(to_yuv(fr))
            if k % 24 == 0: print('frame', k, flush=True)
    cv2.imwrite(os.path.join(WORK, f'raw_{N:04d}.png'), render(N))   # wrap frame (should == frame 0)
    mp4 = os.path.join(OUT, 'title_c_idle_bg.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-s', f'{W}x{H}',
                    '-r', str(FPS), '-i', yuv_path, '-c:v', 'libx264', '-preset', 'slow', '-crf', str(args.crf),
                    '-x264-params', f'keyint={N}:min-keyint={N}:scenecut=0', '-pix_fmt', 'yuv420p',
                    # tag BT.709/limited in the bitstream only (no pixel conversion, unlike -color_range)
                    '-bsf:v', 'h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0',
                    '-movflags', '+faststart', mp4], check=True)
    print('hero bbox', HERO_BBOX, 'crow cover at t0', [round(float(c['hidden0']), 3) for c in CROWS])
    print('wrote', mp4)
