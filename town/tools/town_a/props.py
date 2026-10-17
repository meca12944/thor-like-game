# [town_a] procedural outdoor props + trees (art px, A=0.6)
import numpy as np, math
from px import *
from bld import stone_courses, planks, blotch

def canopy(c, clumps, pal, seed, light=(-.55, -.83)):
    """clumps: list of (cx,cy,r) drawn back (top) to front (bottom)."""
    R = np.random.default_rng(seed); H, W = c.h, c.w
    yy, xx = np.mgrid[0:H, 0:W]
    tex = blotch(H, W, seed, 3, 2.0) + (R.random((H, W)) - .5) * .9
    for (cx, cy, r) in sorted(clumps, key=lambda t: t[1]):
        dx, dy = (xx - cx) / r, (yy - cy) / r
        d2 = dx * dx + dy * dy
        # bumpy edge
        ang = np.arctan2(dy, dx); bump = 1 + .09 * np.sin(ang * 7 + cx) + .05 * np.sin(ang * 13 + cy)
        m = d2 < bump * bump
        if not m.any(): continue
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        L = -(dx * light[0] + dy * light[1]) * .8 + nz * .35 + tex * .22
        idx = np.clip((L + .9) * 3.0, 0, len(pal) - 1).astype(int)
        edge = m & (d2 > (bump * .9) ** 2)
        idx[edge] = np.maximum(idx[edge] - 2, 0)
        cols = np.array(pal)[idx]
        c.a[m] = cols[m]
    # leaf-cluster highlights
    al = c.a[..., 3] > 0
    for k in range(int(W * H / 60)):
        x, y = int(R.integers(0, W)), int(R.integers(0, H))
        if al[y, x] and c.a[y, x, 1] > pal[3][1]:
            c.put(x, y, pal[min(len(pal) - 1, 5 + int(R.integers(0, 2)))]); c.put(x + 1, y, pal[5])

def tree(kind='oak', seed=1, scale=1.0):
    R = rng(seed); pal = P['leaf']
    if kind in ('oak', 'round'):
        w, h = int(120 * scale), int(150 * scale)
        c = Canvas(w, h); tw = int(14 * scale); tx = w // 2 - tw // 2; ty0 = int(h * .55)
        # trunk
        for y in range(ty0, h - 4):
            for x in range(tx, tx + tw):
                k = (x - tx) / tw; col = P['wood'][1 if k > .7 else (3 if k < .3 else 2)]
                if (y + x * 3) % 7 == 0: col = P['wood'][1]
                c.put(x, y, col)
        for side in (-1, 1):  # roots
            for k in range(8):
                c.rect(w // 2 + side * (tw // 2 + k) - (1 if side < 0 else 0), h - 6 + k // 3, w // 2 + side * (tw // 2 + k) + 1, h - 4, P['wood'][2])
        cl = []
        n = 9
        for i in range(n):
            a = i / n * math.tau; rr = R.uniform(.25, .38) * w
            cl.append((w / 2 + math.cos(a) * w * .26 + R.uniform(-4, 4), h * .36 + math.sin(a) * h * .17 + R.uniform(-4, 4), rr * .62))
        cl.append((w / 2, h * .32, w * .3)); cl.append((w / 2 - w * .1, h * .25, w * .22)); cl.append((w / 2 + w * .12, h * .42, w * .24))
        canopy(c, cl, pal, seed)
        # canopy shadow on trunk
        m = np.zeros((h, w), bool); m[ty0:ty0 + int(10 * scale), tx:tx + tw] = True; c.shade(m & (c.a[..., 1] < 120), .6)
        c.outline()
        return c, (w // 2, h - 4), (w // 2, h - 6, tw * .9, 6 * scale)   # img, anchor(foot) , collision ellipse rel (cx,cy,rx,ry) in art px
    if kind == 'pine':
        w, h = int(84 * scale), int(160 * scale); c = Canvas(w, h)
        tw = int(10 * scale); c.rect(w // 2 - tw // 2, h - 30, w // 2 + tw // 2, h - 4, P['wood'][2]); c.vline(w // 2 + tw // 2 - 2, h - 30, h - 4, P['wood'][1])
        layers = 6
        dark = ramp('#0e2018', '#16301f', '#1f4228', '#2b5632', '#3a6a3c', '#4f8048', '#6a9a58')
        for i in range(layers):
            t = i / (layers - 1); yt = int(h * (.02 + t * .62)); yb_ = int(yt + h * .24); half = int(w * (.16 + t * .34))
            pts = [(w / 2, yt), (w / 2 + half, yb_), (w / 2 - half, yb_)]
            mk = Image.new('L', (w, h), 0); ImageDraw.Draw(mk).polygon(pts, fill=255); m = np.asarray(mk) > 0
            ys, xs = np.nonzero(m)
            for y, x in zip(ys, xs):
                fx = (x - w / 2) / max(1, half); fy = (y - yt) / max(1, yb_ - yt)
                v = .55 - fx * .55 + (1 - fy) * .2 + R.uniform(-.18, .18)
                if fy > .82 and ((x + i * 3) % 5 < 2): v -= .45
                c.a[y, x] = dark[int(np.clip(v * 4.2, 0, 6))]
        c.outline()
        return c, (w // 2, h - 4), (w // 2, h - 6, tw, 5 * scale)
    if kind == 'bush':
        w, h = int(56 * scale), int(40 * scale); c = Canvas(w, h)
        cl = [(w * .3, h * .55, h * .38), (w * .7, h * .55, h * .38), (w * .5, h * .42, h * .42), (w * .5, h * .66, h * .32)]
        canopy(c, cl, pal, seed)
        if R.random() < .5:
            fl = R.choice([hexc('#f4a6c4'), hexc('#ffffff'), hexc('#f6e27a'), hexc('#e8607e')])
            al = c.a[..., 3] > 0
            for k in range(14):
                x, y = R.randint(3, w - 4), R.randint(3, h - 6)
                if al[y, x]: c.put(x, y, fl); c.put(x + 1, y, dk(fl, .85))
        c.outline()
        return c, (w // 2, h - 3), (w // 2, h - 6, w * .4, 6 * scale)

# ---------------- small props ----------------
def barrel(seed=1, water=False):
    c = Canvas(26, 32); w = P['wood']
    for x in range(2, 24):
        k = (x - 2) / 21; bul = int(2 * math.sin(k * math.pi))
        for y in range(5 - bul // 2, 31):
            col = w[3 + (k < .35) - (k > .72)]
            if (x - 2) % 5 == 0: col = w[1]
            c.put(x, y, col)
    for y in (9, 24): c.rect(1, y, 25, y + 2, P['iron'][3]); c.hline(1, 25, y, P['iron'][5])
    c.ellipse(13, 6, 11, 4, w[1]); c.ellipse(13, 6, 9, 3, P['water'][3] if water else w[4])
    if water: c.hline(8, 14, 5, P['water'][6])
    c.outline(); return c, (13, 30), (13, 27, 11, 5)

def crate(seed=1, w_=26, h_=26):
    c = Canvas(w_, h_ + 6); w = P['wood']
    c.rect(1, 0, w_ - 1, 7, w[4]); c.hline(1, w_ - 1, 0, w[5])
    planks(c, 1, 7, w_ - 1, h_ + 5, w, seed, pw=5, vertical=False)
    c.rect(1, 7, 4, h_ + 5, w[2]); c.rect(w_ - 4, 7, w_ - 1, h_ + 5, w[2])
    for t in range(h_ - 4):
        x = 4 + int(t * (w_ - 8) / (h_ - 4)); c.rect(x, 7 + t, x + 3, 8 + t, w[2])
    c.outline(); return c, (w_ // 2, h_ + 4), (w_ // 2, h_, w_ * .45, 5)

def sacks(seed=1):
    c = Canvas(34, 26); s = P['cloth_cream']
    for (cx, cy, r) in ((10, 16, 9), (24, 16, 9), (17, 10, 8)):
        c.ellipse(cx, cy, r, r * .85, s[3]); c.ellipse(cx - 2, cy - 2, r * .5, r * .4, s[4])
        c.rect(cx - 2, cy - r, cx + 2, cy - r + 3, s[1])
    c.outline(); return c, (17, 24), (17, 21, 15, 5)

def lamp(seed=1):
    c = Canvas(22, 92); ir = P['iron']
    c.rect(9, 18, 13, 88, ir[2]); c.vline(9, 18, 88, ir[4]); c.rect(6, 82, 16, 90, ir[2]); c.hline(6, 16, 82, ir[4])
    c.rect(5, 6, 17, 20, ir[1]); c.rect(7, 8, 15, 18, hexc('#ffe9a0')); c.rect(8, 9, 14, 17, hexc('#fff6d0'))
    c.rect(3, 4, 19, 7, ir[2]); c.rect(8, 0, 14, 4, ir[2]); c.rect(4, 19, 18, 21, ir[2])
    c.outline(); return c, (11, 89), (11, 87, 5, 3)

def bench(seed=1, mossy=False):
    c = Canvas(56, 30); w = P['wood']
    c.rect(2, 4, 54, 9, w[3]); c.hline(2, 54, 4, w[5]); c.hline(2, 54, 8, w[1])   # backrest
    c.rect(2, 14, 54, 20, w[4]); c.hline(2, 54, 14, w[5]); c.hline(2, 54, 19, w[1])  # seat
    for x in (5, 47): c.rect(x, 2, x + 4, 28, P['wood_d'][3]); c.vline(x, 2, 28, P['wood_d'][4])
    if mossy:
        R = rng(seed)
        for k in range(40): c.put(R.randint(3, 52), R.choice([4, 5, 14, 15, 16, 19]), P['leaf'][R.randint(2, 5)])
    c.outline(); return c, (28, 28), (28, 24, 26, 5)

def well(seed=1, mossy=True):
    c = Canvas(56, 74)
    for x in (6, 46): c.rect(x, 6, x + 4, 52, P['wood'][2]); c.vline(x, 6, 52, P['wood'][4])
    c.poly([(0, 10), (28, 0), (56, 10), (52, 14), (28, 5), (4, 14)], P['roof_brown'][3]); c.hline(4, 52, 13, P['roof_brown'][1])
    c.rect(14, 18, 42, 20, P['wood'][3]); c.rect(25, 20, 31, 34, P['wood'][3])  # bucket
    c.rect(24, 20, 32, 22, P['iron'][3])
    c.ellipse(28, 50, 26, 10, P['stone'][2])
    stone_courses(c, 2, 50, 54, 72, P['stone'], seed, rowh=(5, 6), sw=(7, 11))
    c.ellipse(28, 50, 22, 7, P['stone'][4]); c.ellipse(28, 50, 18, 5, P['water'][1]); c.hline(20, 30, 49, P['water'][4])
    if mossy:
        R = rng(seed)
        for k in range(60):
            x = R.randint(3, 52); y = R.randint(52, 71)
            if c.a[y, x, 3]: c.put(x, y, P['leaf'][R.randint(2, 5)])
    c.outline(); return c, (28, 71), (28, 64, 26, 9)

def notice_board(seed=1):
    c = Canvas(46, 52); w = P['wood']
    for x in (4, 38): c.rect(x, 8, x + 4, 50, w[2])
    c.rect(1, 4, 45, 34, w[1]); c.rect(3, 6, 43, 32, w[3])
    R = rng(seed)
    for (x, y, ww, hh) in ((6, 9, 12, 14), (21, 8, 10, 10), (33, 11, 8, 12), (20, 20, 12, 10)):
        c.rect(x, y, x + ww, y + hh, hexc('#efe6cc')); c.put(x + ww // 2, y, hexc('#c03030'))
        for yy in range(y + 3, y + hh - 1, 2): c.hline(x + 2, x + ww - 2, yy, hexc('#9a8e78'))
    c.rect(0, 1, 46, 5, P['roof_brown'][3]); c.hline(0, 46, 1, P['roof_brown'][5])
    c.outline(); return c, (23, 50), (23, 47, 20, 4)

def signpost(seed=1, arrows=((1, 0), (-1, 2))):
    c = Canvas(60, 60); w = P['wood']
    c.rect(28, 6, 32, 58, w[2]); c.vline(28, 6, 58, w[4])
    for (d, row) in arrows:
        y = 8 + row * 7
        if d > 0: c.poly([(30, y), (52, y), (57, y + 4), (52, y + 8), (30, y + 8)], w[4]); c.hline(30, 52, y, w[5])
        else: c.poly([(30, y), (8, y), (3, y + 4), (8, y + 8), (30, y + 8)], w[3]); c.hline(8, 30, y, w[5])
    c.outline(); return c, (30, 58), (30, 56, 4, 3)

def dummy(seed=1):
    c = Canvas(40, 70); w = P['wood']; hy = P['hay']
    c.rect(18, 20, 22, 68, w[2]); c.rect(4, 26, 36, 30, w[3]); c.hline(4, 36, 26, w[5])   # post + arms
    c.ellipse(20, 40, 11, 14, hy[3]); c.ellipse(17, 36, 6, 7, hy[4])     # straw body
    for y in (32, 46): c.hline(10, 30, y, P['cloth_red'][2])
    c.ellipse(20, 14, 8, 8, hy[3]); c.ellipse(18, 12, 4, 4, hy[4]); c.rect(16, 13, 18, 15, OUT); c.rect(22, 13, 24, 15, OUT)
    R = rng(seed)
    for k in range(20): c.put(R.randint(10, 30), R.randint(28, 52), hy[R.randint(1, 5)])
    c.outline(); return c, (20, 68), (20, 66, 7, 4)

def target(seed=1):
    c = Canvas(40, 56); w = P['wood']
    for x in (8, 30): c.rect(x, 18, x + 3, 55, w[2])
    for r, col in ((16, hexc('#efe6cc')), (12, hexc('#c83a30')), (8, hexc('#efe6cc')), (4, hexc('#c83a30'))): c.ellipse(20, 22, r, r, col)
    c.outline(); return c, (20, 54), (20, 52, 14, 3)

def weapon_rack(seed=1):
    c = Canvas(54, 50); w = P['wood']
    c.rect(2, 14, 52, 18, w[3]); c.rect(2, 34, 52, 38, w[3])
    for x in (4, 48): c.rect(x, 6, x + 3, 48, w[2])
    for i, x in enumerate(range(10, 46, 8)):
        c.rect(x, 2, x + 2, 42, P['iron'][4] if i % 2 else w[4]); c.put(x, 2, P['iron'][5])
        if i % 2: c.rect(x - 2, 30, x + 4, 32, P['gold'][3])
    c.outline(); return c, (27, 48), (27, 45, 25, 4)

def scarecrow(seed=1, hat=True):
    c = Canvas(48, 80); w = P['wood']; hy = P['hay']; cl = P['cloth_blue'] if seed % 2 else P['cloth_red']
    c.rect(22, 20, 26, 78, w[2]); c.rect(4, 30, 44, 34, w[3])
    c.poly([(12, 30), (36, 30), (34, 58), (14, 58)], cl[3]); c.vline(24, 30, 58, cl[1])
    for y in range(30, 58, 6): c.hline(14, 34, y, cl[2])
    c.rect(2, 32, 8, 36, hy[4]); c.rect(40, 32, 46, 36, hy[4])
    c.ellipse(24, 20, 9, 9, cl[4] if False else hexc('#e8d8b0')); c.rect(20, 18, 22, 20, OUT); c.rect(26, 18, 28, 20, OUT); c.hline(21, 28, 23, OUT)
    if hat: c.ellipse(24, 12, 14, 3, hy[2]); c.poly([(16, 12), (32, 12), (28, 2), (20, 2)], hy[3])
    c.outline(); return c, (24, 78), (24, 76, 6, 4)

def haystack(seed=1):
    c = Canvas(70, 52); hy = P['hay']; R = rng(seed)
    yy, xx = np.mgrid[0:52, 0:70]
    m = ((xx - 35) / 34) ** 2 + ((yy - 34) / 30) ** 2 < 1
    m &= yy < 50
    for y, x in zip(*np.nonzero(m)):
        v = .5 - (x - 35) / 70 - (y - 30) / 80 + R.uniform(-.25, .25)
        col = hy[int(np.clip(v * 4 + 2, 0, 5))]
        if (x + y * 2) % 9 == 0: col = hy[1]
        c.a[y, x] = col
    c.outline(); return c, (35, 49), (35, 42, 30, 9)

def chest(seed=1, kind='wood', opened=False):
    c = Canvas(34, 30); w = P['wood'] if kind != 'gold' else P['wood_d']; ir = P['gold'] if kind == 'gold' else P['iron']
    if opened:
        c.rect(3, 2, 31, 10, w[2]); c.rect(5, 4, 29, 9, w[1])
    else:
        c.rect(2, 4, 32, 14, w[4]); c.hline(2, 32, 4, w[5]); c.rect(2, 12, 32, 14, w[2])
    c.rect(2, 14, 32, 28, w[3]); planks(c, 2, 14, 32, 28, w, seed, pw=5, vertical=False)
    for x in (6, 26): c.rect(x, 4 if not opened else 10, x + 3, 28, ir[3]); c.vline(x, 4, 28, ir[5])
    c.rect(15, 11, 19, 18, P['gold'][4]); c.put(16, 15, OUT)
    if kind == 'gold':
        for k in range(0, 34, 3): c.rect(k, 17 + (k // 3) % 2, k + 2, 19 + (k // 3) % 2, P['gold'][5])
        c.rect(13, 16, 21, 24, P['gold'][3]); c.rect(15, 18, 19, 22, P['gold'][1])
    c.outline(); return c, (17, 28), (17, 25, 15, 5)

def basket(seed=1):
    c = Canvas(30, 22); hy = P['hay']
    c.ellipse(15, 8, 13, 4, hy[1]); 
    for y in range(8, 21):
        for x in range(3, 28):
            col = hy[3 if (x + y) % 4 < 2 else 2]
            c.put(x, y, col)
    c.ellipse(15, 8, 11, 3, P['cloth_cream'][4]); c.ellipse(15, 8, 13, 4, hy[4]) if False else None
    c.rect(4, 2, 6, 8, hy[2]); c.rect(24, 2, 26, 8, hy[2]); c.hline(5, 26, 1, hy[2])
    c.outline(); return c, (15, 20), (15, 17, 12, 4)

def laundry(seed=1, span=110):
    c = Canvas(span + 8, 70); w = P['wood']; R = rng(seed)
    for x in (2, span + 2): c.rect(x, 4, x + 4, 68, w[2]); c.vline(x, 4, 68, w[4])
    for x in range(4, span + 4):
        t = (x - 4) / span; y = int(10 + 8 * math.sin(t * math.pi)); c.put(x, y, hexc('#d8d0c0'))
    cols = [P['cloth_red'], P['cloth_blue'], P['cloth_cream'], P['cloth_purple'], P['cloth_green']]
    x = 12
    while x < span - 14:
        ww = R.randint(12, 20); hh = R.randint(16, 30); pal = R.choice(cols)
        t = (x - 4) / span; y = int(10 + 8 * math.sin(t * math.pi))
        c.rect(x, y + 1, x + ww, y + 1 + hh, pal[3]); c.vline(x, y + 1, y + 1 + hh, pal[4]); c.vline(x + ww - 1, y + 1, y + 1 + hh, pal[2])
        c.hline(x, x + ww, y + hh, pal[1]); c.rect(x + 2, y, x + 4, y + 3, w[4])
        x += ww + R.randint(4, 9)
    c.outline(); return c, ((span + 8) // 2, 68), None

def bell_tower(seed=1):
    c = Canvas(64, 150); w = P['wood']
    for x in (8, 52): c.rect(x, 30, x + 5, 148, w[2]); c.vline(x, 30, 148, w[4])
    for y in (60, 100, 136): c.rect(8, y, 57, y + 4, w[3])
    for t in range(40): c.rect(13 + t, 100 - t, 15 + t, 101 - t, w[2])
    c.poly([(0, 34), (32, 6), (64, 34), (58, 38), (32, 14), (6, 38)], P['roof_red'][3]); c.poly([(10, 34), (32, 14), (54, 34)], P['roof_red'][2])
    c.hline(6, 58, 36, P['roof_red'][1])
    c.poly([(24, 40), (40, 40), (44, 58), (20, 58)], P['gold'][3]); c.ellipse(32, 41, 8, 4, P['gold'][4]); c.rect(30, 58, 34, 62, P['gold'][2])
    c.vline(26, 42, 56, P['gold'][5])
    c.rect(31, 62, 33, 120, hexc('#c8b890'))
    c.outline(); return c, (32, 148), (32, 146, 26, 5)

def cart(seed=1):
    c = Canvas(70, 44); w = P['wood']
    c.rect(4, 8, 58, 26, w[3]); planks(c, 4, 8, 58, 26, w, seed, pw=5, vertical=False); c.rect(2, 6, 60, 9, w[4])
    c.rect(56, 22, 70, 25, w[2])
    for cx in (16, 46):
        c.ellipse(cx, 32, 10, 10, w[1]); c.ellipse(cx, 32, 8, 8, w[3]); c.ellipse(cx, 32, 2, 2, P['iron'][3])
        for a in range(0, 360, 45): c.put(cx + int(6 * math.cos(math.radians(a))), 32 + int(6 * math.sin(math.radians(a))), w[1])
    for k in range(10): c.ellipse(10 + k * 5, 6, 4, 3, P['hay'][3 + k % 2])
    c.outline(); return c, (35, 42), (32, 34, 30, 7)

def anvil(seed=1):
    c = Canvas(34, 26); ir = P['iron']
    c.rect(4, 4, 30, 10, ir[3]); c.hline(4, 30, 4, ir[5]); c.poly([(30, 4), (34, 6), (30, 10)], ir[3])
    c.rect(12, 10, 22, 16, ir[2]); c.rect(8, 16, 26, 22, ir[2]); c.rect(6, 20, 28, 25, P['wood'][2])
    c.outline(); return c, (17, 24), (17, 21, 12, 4)

def woodpile(seed=1):
    c = Canvas(50, 30); w = P['wood']
    for row in range(3):
        for k in range(5 - row):
            cx = 7 + k * 9 + row * 4.5; cy = 24 - row * 8
            c.ellipse(cx, cy, 5, 4, w[2]); c.ellipse(cx, cy, 3, 2, w[4]); c.put(int(cx), int(cy), w[5])
    c.outline(); return c, (25, 28), (25, 24, 23, 5)

def flowerpot(seed=1):
    c = Canvas(20, 24); R = rng(seed)
    c.poly([(3, 12), (17, 12), (15, 23), (5, 23)], hexc('#b05a38')); c.hline(3, 17, 12, hexc('#d8805a'))
    fl = R.choice([hexc('#e8607e'), hexc('#f6e27a'), hexc('#b67ad8'), hexc('#ffffff')])
    for k in range(18):
        x, y = R.randint(3, 16), R.randint(1, 12); c.put(x, y, P['leaf'][R.randint(2, 5)])
    for k in range(6): c.put(R.randint(4, 15), R.randint(1, 9), fl)
    c.outline(); return c, (10, 23), (10, 21, 7, 3)

def trough(seed=1):
    c = Canvas(52, 22); w = P['wood']
    c.rect(2, 6, 50, 20, w[3]); c.rect(4, 6, 48, 10, P['water'][3]); c.hline(6, 30, 7, P['water'][5])
    for x in (4, 44): c.rect(x, 14, x + 4, 22, w[1])
    c.outline(); return c, (26, 20), (26, 16, 24, 5)

def stall(seed=1, cols=('cloth_red', 'cloth_cream')):
    c = Canvas(80, 70); w = P['wood']
    for x in (4, 72): c.rect(x, 16, x + 4, 68, w[2])
    from bld import draw_awning
    draw_awning(c, 0, 80, 10, 12, [P[cols[0]], P[cols[1]]], seed)
    c.rect(4, 44, 76, 60, w[3]); c.hline(4, 76, 44, w[5]); planks(c, 4, 46, 76, 60, w, seed, pw=4)
    R = rng(seed)
    for k in range(12):
        x = 8 + k * 5; col = R.choice([hexc('#e05a3a'), hexc('#f0c040'), hexc('#7ab040'), hexc('#c05080')])
        c.ellipse(x, 41, 3, 3, col)
    c.outline(); return c, (40, 68), (40, 62, 36, 6)

def rock(seed=1, big=False):
    R = rng(seed); w, h = (44, 34) if big else (24, 18); c = Canvas(w, h)
    yy, xx = np.mgrid[0:h, 0:w]
    m = ((xx - w / 2) / (w / 2 - 1)) ** 2 + ((yy - h * .55) / (h * .45)) ** 2 < 1
    st = P['stone']
    for y, x in zip(*np.nonzero(m)):
        v = .6 - (x - w / 2) / w - (y - h / 2) / h + R.uniform(-.15, .15); c.a[y, x] = st[int(np.clip(v * 3 + 1.5, 0, 5))]
    if big:
        for k in range(30):
            x, y = R.randint(2, w - 3), R.randint(h // 2, h - 3)
            if c.a[y, x, 3]: c.put(x, y, P['leaf'][R.randint(2, 4)])
    c.outline(); return c, (w // 2, h - 2), (w // 2, h - 5, w * .45, h * .25)

def grate(seed=1):
    c = Canvas(40, 22); ir = P['iron']
    c.rect(0, 0, 40, 22, P['stone'][3]); c.rect(3, 3, 37, 19, ir[0])
    for x in range(5, 36, 4): c.rect(x, 3, x + 2, 19, ir[3]); c.vline(x, 3, 19, ir[4])
    c.hline(3, 37, 3, ir[4]); c.outline(); return c, (20, 21), None

def gate_pillar(seed=1):
    c = Canvas(30, 110)
    stone_courses(c, 2, 14, 28, 108, P['stone'], seed, rowh=(7, 9), sw=(8, 13))
    c.rect(0, 8, 30, 15, P['stone'][4]); c.hline(0, 30, 8, P['stone'][5]); c.rect(6, 0, 24, 8, P['stone'][3]); c.ellipse(15, 2, 6, 3, P['stone'][4])
    c.outline(); return c, (15, 107), (15, 102, 14, 6)
