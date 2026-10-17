"""hero_v3_pix.py - hand-built pixel renderer for hero v3 ('Black Prince', docs_art/outfits_v3/hero.png) on the shared
guide grid hero_v3_guides.json.  No image generation: every frame is drawn at 1x from explicit joint positions with
aliased polygons, then flat-shaded (light from upper-left) and given a 1 px dark outline.  Poses are hand-keyed per
frame (POSES below).  Coordinates: x = px from the body centre column (+x = viewer's right / forward in side view),
y = guide row (0 = crown, 60 = sole line)."""
import json, os, math, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, '..', 'hero_v3_guides.json')))
CW, CH = G['grid']['spriteCanvas']; TOP = G['grid']['canvasCrownRow']; CX = G['grid']['canvasCenterX']
# ---- palette (16 colours) ----
OUT = (12, 8, 16); SU_D = (32, 28, 42); SU = (56, 50, 70); SU_L = (96, 88, 118)
HA_D = (20, 18, 30); HA = (38, 36, 58); HA_L = (84, 86, 128)
SK_D = (196, 140, 116); SK = (238, 196, 166)
GO_D = (150, 104, 38); GO = (222, 176, 70); GO_L = (255, 230, 140)
CR_D = (84, 12, 30); CR = (140, 24, 42); CR_L = (190, 46, 60)
EYE = (226, 40, 52)
PALETTE = [OUT, SU_D, SU, SU_L, HA_D, HA, HA_L, SK_D, SK, GO_D, GO, GO_L, CR_D, CR, CR_L, EYE]
SUIT = (SU_L, SU, SU_D); SUIT_N = (SU_L, (70, 64, 88), SU); HAIR = (HA_L, HA, HA_D); GOLD = (GO_L, GO, GO_D); CRIM = (CR_L, CR, CR_D); SKIN = (SK, SK, SK_D)
def dim(t): return (t[1], t[2], t[2])          # far-side limbs: one step darker

class Canvas:
    def __init__(s, light=1):
        s.rgb = np.zeros((CH, CW, 3), np.uint8); s.z = np.full((CH, CW), -99, np.int16); s.grp = np.zeros((CH, CW), np.int16)
        s.light = light; s.lines = []; s.anch = {}; s.meas = {}
    # --- rasterisers (aliased, 1x) ---
    @staticmethod
    def P(x, y): return (CX + x, TOP + y)
    def poly(s, pts):
        im = Image.new('L', (CW, CH), 0); ImageDraw.Draw(im).polygon([s.P(x - .5, y) for x, y in pts], fill=1); return np.asarray(im) > 0
    def ell(s, x0, y0, x1, y1):
        im = Image.new('L', (CW, CH), 0); a, b = s.P(x0, y0), s.P(x1, y1); ImageDraw.Draw(im).ellipse([a[0], a[1], b[0] - 1, b[1] - 1], fill=1); return np.asarray(im) > 0
    def seg(s, p0, p1, r0, r1=None):
        """tapered capsule from p0 to p1 with half-widths r0, r1"""
        r1 = r0 if r1 is None else r1; (x0, y0), (x1, y1) = p0, p1; dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1e-3
        nx, ny = -dy / L, dx / L
        m = s.poly([(x0 + nx * r0, y0 + ny * r0), (x1 + nx * r1, y1 + ny * r1), (x1 - nx * r1, y1 - ny * r1), (x0 - nx * r0, y0 - ny * r0)])
        m |= s.ell(x0 - r0, y0 - r0, x0 + r0 + .01, y0 + r0 + .01) | s.ell(x1 - r1, y1 - r1, x1 + r1 + .01, y1 + r1 + .01); return m
    def px(s, x, y, c, z=50, grp=0):
        X, Y = int(round(CX + x)), int(round(TOP + y))
        if 0 <= X < CW and 0 <= Y < CH and s.z[Y, X] <= z: s.rgb[Y, X] = c; s.z[Y, X] = z; s.grp[Y, X] = grp
    def hline(s, x0, x1, y, c, z=50, grp=0, only=None):
        for x in range(int(round(x0)), int(round(x1)) + 1):
            X, Y = CX + x, int(round(TOP + y))
            if only is not None and not only[Y, X]: continue
            s.px(x, y, c, z, grp)
    # --- painting ---
    def paint(s, m, ramp, z, grp, shade=True):
        lt, md, dk = ramp
        full = m; m = m & (s.z <= z)          # z-buffer: never paint over a nearer part
        s.rgb[m] = md
        if shade:
            L = s.light
            def sh(k): return np.roll(full, k * L, axis=1)
            light2 = full & sh(1) & ~sh(2); dark2 = full & sh(-1) & ~sh(-2)
            top2 = full & np.roll(full, 1, 0) & ~np.roll(full, 2, 0)
            s.rgb[dark2 & m] = dk; s.rgb[(light2 | (top2 & ~dark2)) & m] = lt
        s.z[m] = z; s.grp[m] = grp; return m
    def outline(s, sep_groups=()):
        f = s.z > -99; out = np.zeros_like(f)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nf = np.roll(np.roll(f, dy, 0), dx, 1); out |= f & ~nf
            nz = np.roll(np.roll(s.z, dy, 0), dx, 1); ng = np.roll(np.roll(s.grp, dy, 0), dx, 1)
            sep = np.isin(s.grp, sep_groups) & nf & (nz < s.z - 4) & (ng != s.grp)
            out |= sep
        s.rgb[out] = OUT; return out
    def rgba(s):
        a = (s.z > -99).astype(np.uint8) * 255; return np.dstack([s.rgb, a])

def ik(h, a, L1, L2, bend=1):
    """2-bone IK: hip h, ankle a -> knee.  bend=+1 knee toward +x."""
    dx, dy = a[0] - h[0], a[1] - h[1]; d = math.hypot(dx, dy)
    if d >= L1 + L2 - 1e-3: return (h[0] + dx * L1 / d, h[1] + dy * L1 / d)
    c = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d); ang = math.acos(max(-1, min(1, c))); base = math.atan2(dy, dx)
    t = base - bend * ang; return (h[0] + L1 * math.cos(t), h[1] + L1 * math.sin(t))

# ---------------------------------------------------------------- body
B = G['bodies']['male']; R_ = B['rows']; J = B['joints']
HIPY = J['hipY']; ANK = R_['ankle']
def shear(p, pose):
    """bob (+down) for everything above the hips, lean (+x at the crown, 0 at hipY) for the upper body"""
    x, y = p; b = pose.get('bob', 0); ln = pose.get('lean', 0)
    if y <= HIPY + .01: x += ln * (HIPY - y) / HIPY
    return (x, y + b)
def U(pose, pts): return [shear(p, pose) for p in pts]

Z = dict(capeB=5, hairB=8, armF=12, legF=14, legN=20, pelvis=24, torso=26, cape_side=27, hairM=28, armN=40, paul=44, head=46, hairF=48, capeOver=36)
GR = dict(leg=1, leg2=2, torso=3, arm=4, arm2=5, head=6, hair=7, cape=8, paul=9)

def draw_leg_front(c, pose, side, view, z, grp, far=False):
    lg = pose[side]; hx = (-1 if (side == 'R') == (view == 'front') else 1) * (J['hipX'] + .4)
    hip = (hx, HIPY + pose.get('bob', 0)); ax, ay = lg['a']; ax += hx
    kf = lg.get('kf', 0); dims = SUIT if not far else dim(SUIT)
    knee = ((hip[0] + ax) / 2 + lg.get('kx', 0), hip[1] + (ay - hip[1]) * (14 / 23.) + kf * .8); c.anch['knee' + side] = knee; c.anch['ankle' + side] = (ax, ay)
    m = c.seg(hip, knee, 3.0 + .3 * kf, 2.5 + .3 * kf) | c.seg(knee, (ax, ay), 2.3 + .2 * kf, 2.1)
    c.paint(m, dims, z, grp)
    if kf > .3: c.px(knee[0] - .5 * c.light, knee[1], SU_L, z, grp)
    bt = max(R_['bootTop'] + (ay - ANK) * .6, knee[1] + 1.5)
    bm = c.seg((ax, bt + 1), (ax, ay), 2.5, 2.4); c.paint(bm, dims, z + 1, grp)
    for x in range(-2, 3):
        c.px(ax + x, bt + (abs(x) == 2) * 0 + (x == 0) * 1, GO if not far else GO_D, z + 1, grp)
    # foot
    if lg.get('toe'):   # heel lifted: only the toe shows (2 rows)
        fm = c.ell(ax - 2.3, ay + .2, ax + 2.4, ay + 2.6)
    else:
        fm = c.ell(ax - 2.6, ay - .2, ax + 2.6, ay + 3.0) | c.ell(ax - 2.0 + (1 if hx > 0 else -1) * .6, ay + .5, ax + 2.0 + (1 if hx > 0 else -1) * .6, ay + 3.0)
    c.paint(fm, (SU, SU_D, OUT) if view == 'front' else (SU_D, SU_D, OUT), z + 2, grp)
    if view == 'front' and not lg.get('toe'): c.px(ax + (.5 if hx > 0 else -.5), ay + 1.2, GO_D if far else GO, z + 2, grp)
    if view == 'back': c.px(ax, ay + 1.2, GO_D, z + 2, grp)

def draw_arm_front(c, pose, side, view, z, grp):
    s = pose.get('arm' + side, 0); sx = (-1 if (side == 'R') == (view == 'front') else 1)
    sh = shear((sx * J['shoulderX'], J['shoulderY']), pose)
    pump = pose.get('pump', 0); out = pose.get('armOut', 0)
    # forward swing (toward the viewer in 'front', away in 'back') shortens the arm on screen; the hand moves in
    fwd = s if view == 'front' else -s
    el = (sh[0] + sx * (1.1 + out * .6 + .5 * max(-fwd, 0)), sh[1] + 9 - abs(s) * .9 - pump * 1.5)
    wr = (el[0] + sx * (.4 - 1.6 * max(fwd, 0) + 1.0 * max(-fwd, 0) + out), el[1] + 7.5 - max(fwd, 0) * 2.6 - max(-fwd, 0) * 1.2 - pump * 3.5)
    behind = fwd < -.25
    ramp = SUIT if not behind else dim(SUIT)
    m = c.seg(sh, el, 2.3, 2.1) | c.seg(el, wr, 2.1, 1.9); c.meas['arm' + side] = m
    zz = z if not behind else Z['armF']
    c.paint(m, ramp, zz, grp)
    for t in (.55, .7):   # gold bracer
        bx = el[0] + (wr[0] - el[0]) * t; by = el[1] + (wr[1] - el[1]) * t
        c.hline(bx - 1.6, bx + 1.6, by, GO if not behind else GO_D, zz, grp, only=m)
    hm = c.ell(wr[0] - 1.7, wr[1] - .6, wr[0] + 1.7, wr[1] + 3.2 - pump * .6); c.anch['hand' + side] = (wr[0], wr[1] + 1.2)
    c.paint(hm, (SU, SU_D, SU_D), zz + 1, grp)
    if view == 'front': c.px(wr[0], wr[1] + 1, CR if not behind else CR_D, zz + 1, grp)

def head_front(c, pose):
    P = lambda pts: U(pose, pts); hd = pose.get('hair', {}); hdx, hdy = hd.get('dx', 0), hd.get('dy', 0)
    # long back hair (behind body)
    hb = c.poly(P([(-5.8, 4), (5.8, 4), (6.4 + hdx, 15 + hdy), (6.0 + hdx, 22 + hdy), (-6.0 + hdx, 22 + hdy), (-6.4 + hdx, 15 + hdy)]))
    c.paint(hb, HAIR, Z['hairB'], GR['hair'])
    face = c.poly(P([(-4.6, 4), (4.6, 4), (4.7, 9), (3.8, 11.5), (2.0, 13), (-2.0, 13), (-3.8, 11.5), (-4.7, 9)]))
    c.paint(face, SKIN, Z['head'], GR['head'], shade=False); c.meas['face'] = face
    b0 = pose.get('bob', 0); ln0 = pose.get('lean', 0) * (HIPY - 11) / HIPY
    for y in (10, 11): c.px(3.9 * c.light + ln0, y + b0, SK_D, Z['head'] + 1, GR['head'])   # jaw shade on the dark side
    neck = c.poly(P([(-1.6, 12.5), (1.6, 12.5), (1.6, 14.5), (-1.6, 14.5)])); c.paint(neck, SKIN, Z['torso'] + 2, GR['head'], shade=False)
    c.hline(-1.6 + ln0, 1.6 + ln0, 13 + b0, SK_D, Z['torso'] + 2, GR['head'])
    cap = c.ell(*shear((-5.6, 0), pose), *shear((5.7, 11.5), pose)) & (np.arange(CH)[:, None] <= TOP + 6 + pose.get('bob', 0))
    bangs = c.poly(P([(-5.4, 3), (5.4, 3), (5.2, 6.0), (4.0, 5.0), (2.6, 6.6), (1.2, 4.6), (.2, 5.2), (-1.2, 4.4), (-2.8, 6.4), (-4.2, 5.0), (-5.2, 6.4)]))
    locks = c.poly(P([(-5.8, 3), (-4.6, 5), (-4.7, 11), (-4.4 + hdx, 22 + hdy), (-5.6 + hdx, 23 + hdy), (-6.4 + hdx, 16 + hdy), (-6.2, 10)])) | \
            c.poly(P([(5.8, 3), (4.6, 5), (4.7, 11), (4.4 + hdx, 22 + hdy), (5.6 + hdx, 23 + hdy), (6.4 + hdx, 16 + hdy), (6.2, 10)]))
    c.paint(cap | bangs | locks, HAIR, Z['hairF'], GR['hair'])
    b = pose.get('bob', 0); ln = pose.get('lean', 0) * (HIPY - 8) / HIPY
    for x in (-2, 2):
        c.px(x + ln, 8 + b, EYE, Z['hairF'], GR['head']); c.px(x - (1 if x < 0 else -1) * 1 + ln, 8 + b, OUT, Z['hairF'], GR['head'])
        c.px(x + ln, 7 + b, OUT, Z['hairF'], GR['head'])
    c.px(ln - .3, 10 + b, SK_D, Z['head'], GR['head']); c.hline(-1 + ln, ln, 12 + b, SK_D, Z['head'], GR['head'])
    c.px(-3.6 + ln, 1 + b, HA_L, Z['hairF'], GR['hair']); c.px(-2.6 + ln, 1 + b, HA_L, Z['hairF'], GR['hair'])

def torso_front(c, pose, view):
    P = lambda pts: U(pose, pts)
    tor = c.poly(P([(-7.5, 14.6), (7.5, 14.6), (9.4, 16.6), (9.2, 19), (7.6, 23), (6.2, 28.5), (6.4, 30.5), (-6.4, 30.5), (-6.2, 28.5), (-7.6, 23), (-9.2, 19), (-9.4, 16.6)]))
    c.paint(tor, SUIT, Z['torso'], GR['torso'])
    col = c.poly(P([(-2.8, 14.0), (2.8, 14.0), (3.0, 16.5), (-3.0, 16.5)])); c.paint(col, SUIT, Z['torso'] + 1, GR['torso'], shade=False)
    b = pose.get('bob', 0)
    def L(x, y): return shear((x, y), pose)
    c.hline(L(-2.8, 14)[0], L(2.8, 14)[0], 14 + b, GO_D if view == 'back' else GO, Z['torso'] + 1, GR['torso'])
    if view == 'front':
        for y in range(16, 29): c.px(L(0, y)[0], y + b, GO_D if y > 22 else GO, Z['torso'] + 1, GR['torso'])
        for i, (x, y) in enumerate([(-4.5, 17), (-3.5, 18), (-2.5, 19), (-1.5, 20), (1.5, 20), (2.5, 19), (3.5, 18), (4.5, 17)]):
            c.px(L(x, y)[0], y + b, GO, Z['torso'] + 1, GR['torso'])
        for y in (23, 24, 25): c.px(L(-4.6, y)[0], y + b, SU_L, Z['torso'] + 1, GR['torso']); c.px(L(4.6, y)[0], y + b, SU_D, Z['torso'] + 1, GR['torso'])
    else:
        for y in range(16, 29): c.px(L(0, y)[0], y + b, SU_D, Z['torso'] + 1, GR['torso'])
    # belt
    by = 29 + b; c.hline(L(-6.2, 29)[0], L(6.2, 29)[0], by, GO_D if view == 'back' else GO, Z['torso'] + 2, GR['torso'], only=tor)
    c.hline(L(-6.2, 30)[0], L(6.2, 30)[0], by + 1, SU_D, Z['torso'] + 2, GR['torso'], only=tor)
    if view == 'front':
        for x in (-1, 0, 1):
            for y in (29, 30, 31): c.px(L(x, y)[0], y + b, GO, Z['torso'] + 3, GR['torso'])
        c.px(L(0, 30)[0], 30 + b, CR_L, Z['torso'] + 3, GR['torso']); c.px(L(-1, 31)[0], 31 + b, GO_D, Z['torso'] + 3, GR['torso'])
    pel = c.poly(P([(-6.4, 30.5), (6.4, 30.5), (6.6, 35.5), (1.2, 36.6), (-1.2, 36.6), (-6.6, 35.5)]))
    c.paint(pel, SUIT, Z['pelvis'], GR['torso']); c.meas['pelvis'] = pel; c.meas['belt'] = 29 + b
    if view == 'front':
        for y in (32, 33, 34): c.px(L(-3, y)[0] - (y - 32) * .3, y + b, GO_D, Z['pelvis'] + 1, GR['torso']); c.px(L(3, y)[0] + (y - 32) * .3, y + b, GO_D, Z['pelvis'] + 1, GR['torso'])

def pauldron(c, pose, cx, flip=1, z=None, gem=True, k=1.25):
    P = lambda pts: U(pose, [(cx + flip * x * k, 16 + (y - 16) * k) for x, y in pts])
    m = c.poly(P([(-3.6, 14.6), (-0.5, 13.6), (2.8, 14.4), (4.3, 16.6), (3.9, 19.8), (1.8, 21.2), (-.8, 19.2), (-2.8, 17.4)]))
    c.paint(m, (GO_L, SU, SU_D), z or Z['paul'], GR['paul'])
    er = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    # gold rim one pixel inside the outline
    inner = m & ~er; rim = inner & ~(np.roll(inner, 1, 0) & np.roll(inner, -1, 0) & np.roll(inner, 1, 1) & np.roll(inner, -1, 1))
    c.rgb[rim] = GO; c.rgb[rim & (np.roll(m, 2, 0) == 0)] = GO_L
    if gem:
        g = shear((cx + flip * .8, 16.8), pose); c.px(g[0], g[1], CR_L, (z or Z['paul']) + 1, GR['paul']); c.px(g[0], g[1] + 1, CR, (z or Z['paul']) + 1, GR['paul'])

def cape_front(c, pose, view):
    cp = pose.get('cape', {}); sw = cp.get('sway', 0); fl = cp.get('flare', 0); lf = cp.get('lift', 0); fu = cp.get('flut', 0)
    hem = (55 if view == 'front' else 50.5) - lf
    def side(sg):
        return [shear((sg * 8.2, 16), pose), shear((sg * (11 + fl * .4), 30), pose), (sg * (12.6 + fl) + sw, 44 - lf * .6), (sg * (13.6 + fl) + sw, hem - (fu if sg > 0 else -fu) * .5)]
    Lp, Rp = side(-1), side(1)
    hm = [(Lp[-1][0] + (Rp[-1][0] - Lp[-1][0]) * t, Lp[-1][1] + (Rp[-1][1] - Lp[-1][1]) * t + .45 * math.sin(math.pi * 3 * t + fu)) for t in np.linspace(0, 1, 13)]
    if view == 'front':
        m = c.poly(Lp + hm + Rp[::-1]); c.paint(m, CRIM, Z['capeB'], GR['cape'])
        for sg, sd in ((-1, Lp), (1, Rp)):   # black outer edge band + gold edge
            inner = [(x - sg * 1.6, y) for x, y in sd]
            band = c.poly(sd + inner[::-1]) & m; c.rgb[band] = SU_D
            edge = c.poly(sd + [(x - sg * .7, y) for x, y in sd][::-1]) & m; c.rgb[edge] = GO_D
        for fx in (-6.5, 6.5):   # lining folds
            for y in range(36, int(hem)):
                c.px(fx * (1 + (y - 36) / 60.) + sw * (y - 36) / 20., y, CR_D, Z['capeB'], GR['cape'])
        for x, y in hm: c.px(x, y - .6, GO_D, Z['capeB'], GR['cape'])
    else:
        Lp = [shear((-6.2, 15.5), pose)] + Lp[1:]; Rp = [shear((6.2, 15.5), pose)] + Rp[1:]
        m = c.poly(Lp + hm + Rp[::-1]); c.paint(m, SUIT, Z['capeOver'], GR['cape'])
        for fx in (-4.5, 0, 4.5):
            for y in range(20, int(hem)):
                c.px(fx * (1 + (y - 20) / 35.) + sw * (y - 20) / 35., y, SU_D, Z['capeOver'], GR['cape'])
        for sg, sd in ((-1, Lp), (1, Rp)):
            edge = c.poly(sd + [(x - sg * 1.0, y) for x, y in sd][::-1]) & m; c.rgb[edge] = GO_D
        for x, y in hm:
            for k in (0, ): c.px(x, y - .4, GO, Z['capeOver'], GR['cape'])
        # crimson lining peeks where the hem flips
        if lf > 0 or fl > 0:
            for x, y in hm[1::3]: c.px(x, y - 1.4, CR, Z['capeOver'], GR['cape'])

def head_back(c, pose):
    P = lambda pts: U(pose, pts); hd = pose.get('hair', {}); hdx, hdy = hd.get('dx', 0), hd.get('dy', 0)
    cap = c.ell(*shear((-5.8, 0), pose), *shear((5.9, 14.5), pose))
    panel = c.poly(P([(-6.3, 6), (6.3, 6), (6.0 + hdx, 18 + hdy * .5), (4.6 + hdx, 28.5 + hdy), (0, 29.5 + hdy), (-4.6 + hdx, 28.5 + hdy), (-6.0 + hdx, 18 + hdy * .5)]))
    m = cap | panel; c.paint(m, HAIR, Z['hairM'] + 20, GR['hair']); c.meas['face'] = cap
    b = pose.get('bob', 0)
    for fx in (-2.5, 1.5):
        for y in range(5, 28): c.px(fx + hdx * (y - 5) / 25, y + b + hdy * (y > 15), HA_D, Z['hairM'] + 20, GR['hair'])
    for x in (-3, -2, -1): c.px(x, 1 + b, HA_L, Z['hairM'] + 20, GR['hair'])
    c.px(-4, 2 + b, HA_L, Z['hairM'] + 20, GR['hair'])

def common_anchors(c, pose):
    for k, p in (('crown', (0, 0)), ('eye', (0, 8)), ('neck', (0, 14)), ('capeRoot', (0, 15)), ('belt', (0, 29)), ('hip', (0, HIPY))): c.anch[k] = shear(p, pose)
def render_fb(pose, view):
    """front (down) / back (up) view"""
    c = Canvas(light=1); common_anchors(c, pose)
    if view == 'front':
        cape_front(c, pose, 'front')
        # draw the far leg first (the one stepping away / lifted toe)
        order = sorted(('R', 'L'), key=lambda s: -pose[s].get('back', 0))
        for i, s in enumerate(order): draw_leg_front(c, pose, s, view, Z['legF'] + i * 4, GR['leg'] + i, far=pose[s].get('back', 0) > 0)
        torso_front(c, pose, view)
        draw_arm_front(c, pose, 'R', view, Z['armN'], GR['arm']); draw_arm_front(c, pose, 'L', view, Z['armN'], GR['arm2'])
        pauldron(c, pose, 7.4, 1)
        head_front(c, pose)
    else:
        order = sorted(('R', 'L'), key=lambda s: -pose[s].get('back', 0))
        for i, s in enumerate(order): draw_leg_front(c, pose, s, view, Z['legF'] + i * 4, GR['leg'] + i, far=pose[s].get('back', 0) > 0)
        torso_front(c, pose, view)
        cape_front(c, pose, 'back')
        draw_arm_front(c, pose, 'R', view, Z['armN'], GR['arm']); draw_arm_front(c, pose, 'L', view, Z['armN'], GR['arm2'])
        pauldron(c, pose, -7.4, -1, gem=False)
        head_back(c, pose)
    c.outline(sep_groups=(GR['arm'], GR['arm2'], GR['leg'], GR['leg2'], GR['paul'], GR['hair'], GR['cape'], GR['torso']))
    return c

# ---------------------------------------------------------------- side view (facing +x); left = mirrored geometry, own light
def foot_side(c, a, fa, ramp, z, grp, gold=True):
    t = math.radians(fa); ca, sa = math.cos(t), math.sin(t)
    def r(x, y): return (a[0] + x * ca - y * sa, a[1] + x * sa + y * ca)   # +fa rotates toe down (heel up)
    m = c.poly([r(-2.0, -1.2), r(1.4, -1.6), r(4.4, .8), r(4.6, 2.2), r(-2.1, 2.4)])
    c.paint(m, ramp, z, grp)
    if gold:
        p = r(3.6, 1.0); c.px(p[0], p[1], GO_D, z, grp); p = r(-1.4, 1.4); c.px(p[0], p[1], GO_D, z, grp)
def leg_side(c, pose, side, z, grp, far):
    lg = pose[side]; hip = (pose.get('hipdx', 0) + .3, HIPY + pose.get('bob', 0)); a = lg['a']
    ramp = SUIT_N if not far else dim(SUIT)
    knee = ik(hip, a, 14.0, 9.8, bend=1); c.anch['knee' + side] = knee; c.anch['ankle' + side] = a
    thigh = c.seg(hip, knee, 2.8, 2.3); shin = c.seg(knee, a, 2.2, 1.9)
    c.paint(thigh | shin, ramp, z, grp)
    # boot: from 3/4 down the shin to the ankle, gold cuff
    bt = (knee[0] + (a[0] - knee[0]) * .32, knee[1] + (a[1] - knee[1]) * .32)
    bm = c.seg(bt, a, 2.4, 2.2); c.paint(bm, ramp, z + 1, grp)
    dx, dy = a[0] - knee[0], a[1] - knee[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
    for k in (-1.6, -.6, .5, 1.5):
        c.px(bt[0] + nx * k, bt[1] + ny * k, GO if not far else GO_D, z + 1, grp)
    c.px(knee[0] + 1.6, knee[1], SU_L if not far else SU, z, grp)   # knee guard glint
    foot_side(c, a, lg.get('fa', 0), (SU, SU_D, OUT) if not far else (SU_D, SU_D, OUT), z + 2, grp)
def arm_side(c, pose, side, z, grp, far):
    sw = pose.get('arm' + side, 0); pump = pose.get('pump', 0)
    sh = shear((-.4, 17.0), pose)
    a1 = math.radians(sw * 28 + pose.get('armBase', 0))
    a2 = a1 + math.radians(12 + max(sw, 0) * 30 + pump * 70 + pose.get('elbow', 0))
    el = (sh[0] + 8.6 * math.sin(a1), sh[1] + 8.6 * math.cos(a1)); wr = (el[0] + 7.4 * math.sin(a2), el[1] + 7.4 * math.cos(a2))
    ramp = SUIT_N if not far else dim(SUIT)
    m = c.seg(sh, el, 2.3, 2.0) | c.seg(el, wr, 2.0, 1.8); c.paint(m, ramp, z, grp); c.meas['arm' + side] = m
    for t in (.5, .65):
        bx = el[0] + (wr[0] - el[0]) * t; by = el[1] + (wr[1] - el[1]) * t
        dx, dy = wr[0] - el[0], wr[1] - el[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
        for k in (-1.2, 0, 1.2): c.px(bx + nx * k, by + ny * k, GO if not far else GO_D, z, grp)
    hm = c.ell(wr[0] - 1.6, wr[1] - 1.2, wr[0] + 1.7, wr[1] + 2.0); c.paint(hm, (SU, SU_D, SU_D), z + 1, grp); c.anch['hand' + side] = (wr[0], wr[1] + .5)
    if not far: c.px(wr[0] + .5, wr[1] + .3, CR, z + 1, grp)
    return sh
def head_side(c, pose):
    P = lambda pts: U(pose, pts); hd = pose.get('hair', {}); hdx, hdy = hd.get('dx', 0), hd.get('dy', 0)
    stream = pose.get('hairStream', 0)
    skull = c.ell(*shear((-5.2, 0), pose), *shear((4.8, 13.4), pose))
    face = c.poly(P([(.4, 3.5), (4.4, 4.2), (4.8, 7.5), (5.6, 9.6), (4.8, 10.6), (4.6, 12.0), (3.4, 13.1), (.6, 13.4)]))
    c.paint(face, SKIN, Z['head'], GR['head'], shade=False); c.meas['face'] = face
    hairm = c.poly(P([(-1.5, .3), (2.6, .2), (4.6, 2.0), (5.2, 4.4), (4.2, 4.6), (3.4, 3.8), (2.6, 5.6), (1.4, 4.4), (.4, 7.0), (.2, 10.5),
                      (-.6, 13.5), (-1.6 + hdx * .3, 17 + hdy * .4), (-2.4 + hdx * .6 - stream * .5, 22 + hdy * .8 - stream * .4), (-3.6 + hdx - stream, 27 + hdy - stream * 1.2),
                      (-5.4 + hdx - stream * 1.4, 26.4 + hdy - stream * 1.8), (-6.2 + hdx * .6 - stream, 19 + hdy * .5 - stream * .8), (-6.2, 12), (-5.6, 3)])) | (skull & c.poly(P([(-6, -1), (1, -1), (0, 14), (-6, 14)])))
    c.paint(hairm, HAIR, Z['hairF'], GR['hair'])
    b = pose.get('bob', 0); L = lambda x, y: (shear((x, y), pose))
    for y in range(4, 25): q = L(-3.6 + (hdx - stream) * max(0, y - 13) / 16, y); c.px(q[0], q[1] + (hdy - stream) * max(0, y - 13) / 16, HA_D, Z['hairF'], GR['hair'])
    for x, y in ((-1, 1), (0, 1), (1, 1), (-2, 2)): q = L(x, y); c.px(q[0], q[1], HA_L, Z['hairF'], GR['hair'])
    q = L(3.2, 8); c.px(q[0], q[1], EYE, Z['hairF'] + 1, GR['head'])
    q = L(3.4, 7); c.px(q[0], q[1], OUT, Z['hairF'] + 1, GR['head']); c.px(q[0] + 1, q[1], OUT, Z['hairF'] + 1, GR['head'])
    q = L(4.2, 12); c.px(q[0], q[1], SK_D, Z['head'] + 1, GR['head'])
    for y in (10, 11, 12): q = L(1.0, y); c.px(q[0], q[1], SK_D, Z['head'] + 1, GR['head'])
    neck = c.poly(P([(-.2, 12.5), (2.8, 12.5), (2.8, 14.5), (-.2, 14.5)])); c.paint(neck, SKIN, Z['torso'] + 2, GR['head'], shade=False)
def torso_side(c, pose, near_paul):
    P = lambda pts: U(pose, pts); L = lambda x, y: shear((x, y), pose); b = pose.get('bob', 0)
    tor = c.poly(P([(-3.6, 14.4), (2.6, 14.4), (4.8, 17.0), (5.4, 20.5), (4.6, 25.5), (3.8, 29.5), (-3.4, 29.5), (-4.0, 25), (-4.8, 19), (-4.8, 16)]))
    c.paint(tor, SUIT, Z['torso'], GR['torso'])
    col = c.poly(P([(-1.2, 13.8), (3.0, 13.8), (3.4, 16.4), (-1.2, 16.4)])); c.paint(col, SUIT, Z['torso'] + 2, GR['torso'], shade=False)
    q0, q1 = L(-1.2, 14), L(3.0, 14); c.hline(q0[0], q1[0], 14 + b, GO, Z['torso'] + 2, GR['torso'])
    for y in range(17, 29): q = L(3.2 - abs(y - 21) * .12, y); c.px(q[0], q[1], GO_D if y > 22 else GO, Z['torso'] + 1, GR['torso'])
    q0, q1 = L(-3.4, 29), L(3.6, 29); c.hline(q0[0], q1[0], 29 + b, GO, Z['torso'] + 2, GR['torso'], only=tor)
    q0, q1 = L(-3.4, 30), L(3.6, 30); c.hline(q0[0], q1[0], 30 + b, SU_D, Z['torso'] + 2, GR['torso'])
    q = L(3.2, 30); c.px(q[0], q[1], GO, Z['torso'] + 3, GR['torso']); c.px(q[0] - 1, q[1], CR_L, Z['torso'] + 3, GR['torso'])
    pel = c.poly(P([(-3.8, 30.0), (3.9, 30.0), (4.2, 34.6), (2.5, 36.6), (-2.6, 36.6), (-4.2, 34.6)])); c.paint(pel, SUIT, Z['pelvis'], GR['torso']); c.meas['pelvis'] = pel; c.meas['belt'] = 29 + b
def cape_side(c, pose):
    cp = pose.get('cape', {}); tr = cp.get('trail', 0); lf = cp.get('lift', 0); fu = cp.get('flut', 0)
    top = [shear((-3.6, 14.6), pose), shear((1.0, 14.6), pose)]
    fh = (-1.2 - tr * .45, 55 - lf * .6); bh = (-9.4 - tr, 54.4 - lf - fu * .3)
    F = [shear((1.0, 17), pose), shear((-.6 - tr * .1, 30), pose), (-1.2 - tr * .3, 44 - lf * .2), fh]
    Bk = [shear((-5.4, 17), pose), shear((-7.2 - tr * .3, 30), pose), (-8.6 - tr * .75, 44 - lf * .6), bh]
    hem = [(bh[0] + (fh[0] - bh[0]) * t, bh[1] + (fh[1] - bh[1]) * t + .6 * math.sin(math.pi * 2 * t + fu)) for t in np.linspace(0, 1, 9)]
    m = c.poly(top + F + hem[::-1] + Bk[::-1]); c.paint(m, SUIT, Z['capeB'], GR['cape'])
    # crimson lining shows along the hem when the cape lifts/trails
    lw = 1 + .5 * tr + .4 * lf
    lin = c.poly(hem + [(x + .4 * lw, y - lw) for x, y in hem][::-1]) & m; c.rgb[lin] = CR
    for x, y in hem: c.px(x, y - .3, GO, Z['capeB'], GR['cape'])
    for t in np.linspace(0, 1, 30):   # gold edge along the back + one fold
        p0 = (Bk[1][0] + (bh[0] - Bk[1][0]) * t, Bk[1][1] + (bh[1] - Bk[1][1]) * t)
        c.px(p0[0] + .7, p0[1], GO_D, Z['capeB'], GR['cape'])
        f = ((Bk[1][0] + F[1][0]) / 2 + (bh[0] - Bk[1][0]) * t * .7, 30 + (52 - lf - 30) * t); c.px(f[0], f[1], SU_D, Z['capeB'], GR['cape'])
def render_side(pose, facing='right'):
    """facing right natively.  'left' = the same geometry mirrored, but lit from the upper-left again and with the
    pauldron (character's LEFT shoulder) on the near side - so left is a real view, not a flipped sprite."""
    left = facing == 'left'; c = Canvas(light=-1 if left else 1); common_anchors(c, pose)
    cape_side(c, pose)
    near, farl = ('R', 'L') if not left else ('L', 'R')
    arm_side(c, pose, farl, Z['armF'], GR['arm2'], True)
    leg_side(c, pose, farl, Z['legF'], GR['leg2'], True)
    leg_side(c, pose, near, Z['legN'], GR['leg'], False)
    torso_side(c, pose, left)
    head_side(c, pose)
    arm_side(c, pose, near, Z['armN'], GR['arm'], False)
    if left: pauldron(c, pose, .2, 1, z=Z['armN'] + 3, k=1.0)
    else:
        q = shear((-.6, 15.4), pose)
        for x in (-2, -1, 0, 1): c.px(q[0] + x, q[1], GO_D, Z['armN'] + 3, GR['paul'])
    c.outline(sep_groups=(GR['arm'], GR['arm2'], GR['leg'], GR['leg2'], GR['paul'], GR['hair'], GR['cape'], GR['torso']))
    if left:
        c.rgb = c.rgb[:, ::-1].copy(); c.z = c.z[:, ::-1].copy(); c.grp = c.grp[:, ::-1].copy()
        c.meas = {k: (v[:, ::-1].copy() if isinstance(v, np.ndarray) else v) for k, v in c.meas.items()}
        c.anch = {k: (-v[0] - 1, v[1]) for k, v in c.anch.items()}
    return c
