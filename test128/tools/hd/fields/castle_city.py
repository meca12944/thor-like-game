"""castle_city: the royal capital around the illustrator's castle (owner 10-25 「뒷 벽이랑 성벽이랑, 뒤에 왕도하고 일체화 시켜야지」).
A code-drawn silhouette layer in the castle's own stone (castle_tone ramp, black ink, drip streaks) that fills the sky / dark tone left and right of the
castle picture: a far haze of roofs and spires, a nearer town of gabled houses, keeps and round towers, and in front a continuous city wall at the
castle's own outer-band height (merlons ~1352, face to 1440) with drum towers — so Felt's wall, the city wall and the castle's wall band read as one ring.
Everything is drawn once (no tile, no repeat: every building is its own random draw); it lives in the castle's 2560x1440 source frame, from XA to XB,
at scale S. world.js drawBackdrop draws it before the castle picture (same scale / anchor as the castle's front band) and stretches its bottom row down
to the clip line, so a breach never shows sky under it. The ends fade out (alpha) far past anything a screen shows.
run: python3 tools/hd/fields/castle_city.py   (writes assets/world/castle_far/city.webp + city.json; castle_far.backdrop() picks it up)"""
import os, sys, json, math, random
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkart
from inkart import Pic
import castle_tone as CT
ROOT = CT.ROOT; OUT = 'assets/world/castle_far/'
XA, XB, YA, YB = -3400, 5960, 520, 1440          # source px box
S = .5; CX = 1278                                  # castle centre (source x)
CW = (20, 2537)                                    # castle picture's opaque span
WALL_TOP, FACE_TOP = 1352, 1386                    # merlon tops / wall face top (the castle's own outer band)
HAZE = np.array([118, 102, 80.])                   # the warm horizon behind (sky.webp low rows under its dim veil)
def P(X, Y): return ((X - XA) * S, (Y - YA) * S)
def dist(X):
    """0 at the castle's flanks -> 1 far out: the town falls away and fades with distance"""
    d = X - CW[0] if X < CX else CW[1] - X
    return float(np.clip(-d / 3600., 0, 1)) if d < 0 else 0.
def rise(X):
    """the town climbs the castle hill: up to ~260 source px higher right at the castle's flanks"""
    d = CW[0] - X if X < CX else X - CW[1]
    return 260. * math.exp(-max(0., d + 200) / 700.)
def roof_house(p, r, X, base, w, h, rh, col='stone', roof='stone_dd', lit=None, broken=False):
    x0, y0 = P(X, base); x1, y1 = P(X + w, base - h)
    p.fill([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], col, wob=.3, line=.9)
    if r.random() < .6: inkart.masonry(p, x0, y1, x1, y0, rowh=5.5, col=col, var=.12, la=90, lw=.5, holes=.02, seed=r.randrange(9999), wmin=1.0, wmax=2.2)
    apx = x0 + (x1 - x0) * r.uniform(.4, .6); ry = y1 - rh * S
    if broken:   # a fallen-in roof: ragged ridge, rafters
        pts = [(x0 - 1.5, y1)] + [(x, ry + r.uniform(0, rh * S * .8)) for x in np.linspace(x0, x1, 5)] + [(x1 + 1.5, y1)]
        p.fill(pts, roof, wob=.5, line=.9)
        for k in range(r.randint(1, 3)): xx = r.uniform(x0 + 2, x1 - 2); p.stroke([(xx, y1), (xx + r.uniform(-3, 3), ry + 2)], .7, 200, .2)
    else:
        p.fill([(x0 - 1.5, y1), (apx, ry), (x1 + 1.5, y1)], roof, wob=.3, line=.9)
        p.shade([(apx, ry), (x1 + 1.5, y1), (apx, y1)], .35, .2)
        if r.random() < .4: cx_ = r.uniform(x0 + 3, x1 - 4); p.rect(cx_, ry + (y1 - ry) * .3 - 5, cx_ + 2.5, y1, 'stone_d', wob=.2, line=.7)   # chimney
    p.shade([(x0 + (x1 - x0) * .62, y1), (x1, y1), (x1, y0), (x0 + (x1 - x0) * .62, y0)], .3, .2)
    for k in range(r.randint(0, 3)):
        wx = r.uniform(x0 + 2, x1 - 4); wy = r.uniform(y1 + 3, y0 - 6)
        c = (226, 150, 66) if (lit and r.random() < lit) else 'void'
        p.rect(wx, wy, wx + 1.8, wy + 3.0, c, wob=0, line=.5)
def round_tower(p, r, X, base, w, h, cone=True, crenel=True, slit=True, col='stone_l'):
    x0, y0 = P(X - w / 2, base); x1, y1 = P(X + w / 2, base - h); cx = (x0 + x1) / 2
    p.fill([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], col, wob=.3, line=1.1)
    inkart.masonry(p, x0, y1, x1, y0, rowh=5.0, col=col, var=.1, la=110, lw=.55, holes=.02, seed=r.randrange(9999), wmin=.9, wmax=1.8)
    p.shade([(x0 + (x1 - x0) * .58, y1), (x1, y1), (x1, y0), (x0 + (x1 - x0) * .58, y0)], .42, .2)   # round: light from the upper left
    p.light([(x0, y1), (x0 + (x1 - x0) * .22, y1), (x0 + (x1 - x0) * .22, y0), (x0, y0)], .12, .2)
    if crenel:
        cy = y1; ow = (x1 - x0) * 1.08; ox = cx - ow / 2
        p.fill([(ox, cy + 4), (ox, cy - 1), (ox + ow, cy - 1), (ox + ow, cy + 4)], col, wob=.2, line=.9)          # corbelled parapet
        n = max(3, int(ow / 6))
        for k in range(n):
            if k % 2 == 0: xa = ox + k * ow / n; p.rect(xa, cy - 5, xa + ow / n, cy - 1, col, wob=.2, line=.8)
        for k in range(n): xa = ox + (k + .5) * ow / n; p.stroke([(xa, cy + 4), (xa, cy + 6)], .6, 180, 0)
        y1 = cy - 5
    if cone:
        ch = (x1 - x0) * r.uniform(.8, 1.35); p.fill([(cx - (x1 - x0) * .5, y1 + 1), (cx, y1 - ch), (cx + (x1 - x0) * .5, y1 + 1)], 'stone_dd', wob=.2, line=1.0)
        p.shade([(cx, y1 - ch), (cx + (x1 - x0) * .5, y1 + 1), (cx, y1 + 1)], .4, .1)
        p.stroke([(cx, y1 - ch), (cx, y1 - ch - 5)], .7, 200, 0)
    if slit:
        for k in range(r.randint(1, 3)):
            sy = P(0, base - h * r.uniform(.25, .85))[1]; sx = cx + r.uniform(-.15, .15) * (x1 - x0)
            p.rect(sx - .7, sy, sx + .7, sy + 4, 'void', wob=0, line=.4)
def keep(p, r, X, base, w, h, broken=False, col='stone'):
    x0, y0 = P(X - w / 2, base); x1, y1 = P(X + w / 2, base - h)
    if broken: top = [(x, y1 + r.uniform(0, (y0 - y1) * .35)) for x in np.linspace(x0, x1, 6)]
    else: top = [(x0, y1), (x1, y1)]
    p.fill([(x0, y0)] + top + [(x1, y0)], col, wob=.3, line=1.1)
    inkart.masonry(p, x0, y1, x1, y0, top=(lambda x: float(np.interp(x, [q[0] for q in top], [q[1] for q in top]))) if broken else None, rowh=5.5, col=col, var=.12, la=110, lw=.55, holes=.03, seed=r.randrange(9999))
    p.shade([(x0 + (x1 - x0) * .66, y1), (x1, y1), (x1, y0), (x0 + (x1 - x0) * .66, y0)], .38, .2)
    if not broken:
        n = max(3, int((x1 - x0) / 6))
        for k in range(0, n, 2): xa = x0 + k * (x1 - x0) / n; p.rect(xa, y1 - 4, xa + (x1 - x0) / n, y1, col, wob=.2, line=.8)
    for k in range(r.randint(1, 4)):
        wx = r.uniform(x0 + 2, x1 - 4); wy = r.uniform(y1 + 5, y0 - 10); p.fill([(wx, wy + 5), (wx, wy + 1.5), (wx + 1.2, wy), (wx + 2.4, wy + 1.5), (wx + 2.4, wy + 5)], 'void', wob=0, line=.4)
def spire(p, r, X, base, w, h):
    x0, y0 = P(X - w / 2, base); x1, y1 = P(X + w / 2, base - h * .45); cx = (x0 + x1) / 2
    p.fill([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], 'stone_l', wob=.3, line=1.0)
    inkart.masonry(p, x0, y1, x1, y0, rowh=5.0, col='stone_l', var=.1, la=100, lw=.5, holes=.01, seed=r.randrange(9999))
    p.shade([(cx + 1, y1), (x1, y1), (x1, y0), (cx + 1, y0)], .4, .2)
    for k in range(2): wy = y1 + (y0 - y1) * (.2 + k * .35); p.fill([(cx - 1.5, wy + 7), (cx - 1.5, wy + 2), (cx, wy), (cx + 1.5, wy + 2), (cx + 1.5, wy + 7)], 'void', wob=0, line=.4)
    tip = P(X, base - h)[1]; p.fill([(x0 - 1, y1 + 1), (cx, tip), (x1 + 1, y1 + 1)], 'stone_dd', wob=.2, line=1.0)
    p.shade([(cx, tip), (x1 + 1, y1 + 1), (cx, y1 + 1)], .45, .1)
    for t in (.35, .65): yy = y1 + (tip - y1) * t; hw = (x1 - x0) / 2 * (1 - t) + 1; p.stroke([(cx - hw, yy), (cx + hw, yy)], .5, 160, 0)
    p.stroke([(cx, tip), (cx, tip - 6)], .7, 220, 0)
def town(p, r, base, ytop, lit, haze_row=False):
    """a band of buildings along x (skips the castle's opaque core), tops near ytop(X)"""
    X = XA + r.uniform(0, 40)
    while X < XB:
        if CW[0] + 420 < X < CW[1] - 420: X += 60; continue          # hidden behind the castle anyway
        d = dist(X); top = ytop(X); kind = r.random(); east = X > CX
        hmax = max(30, base - top)
        if kind < .1 * (1 - d) + .05:
            w = r.uniform(24, 34); spire(p, r, X + w / 2, base, w, hmax * r.uniform(1.0, 1.35)); X += w + r.uniform(10, 50)
        elif kind < .3:
            w = r.uniform(40, 70); round_tower(p, r, X + w / 2, base, w, hmax * r.uniform(.7, 1.05), cone=r.random() < .65, col=r.choice(['stone_l', 'stone'])); X += w + r.uniform(6, 40)
        elif kind < .45:
            w = r.uniform(70, 130); keep(p, r, X + w / 2, base, w, hmax * r.uniform(.6, .95), broken=east and r.random() < .45); X += w + r.uniform(0, 30)
        else:
            w = r.uniform(45, 110); h = hmax * r.uniform(.35, .7); roof_house(p, r, X, base, w, h, min(w * .55, hmax - h) * r.uniform(.6, 1.0), col=r.choice(['stone', 'stone_l', 'stone_d']), lit=lit, broken=east and r.random() < .3); X += w * r.uniform(.6, 1.0)
def city_wall(p, r):
    """the outer ring: continuous curtain at the castle's band height, drum towers, drip-stained"""
    x0, _ = P(XA, 0); x1, _ = P(XB, 0); yt = P(0, FACE_TOP)[1]; yb = P(0, YB)[1] + 2; ym = P(0, WALL_TOP)[1]
    p.fill([(x0, yb), (x0, yt), (x1, yt), (x1, yb)], 'stone', wob=.3, line=1.1)
    inkart.masonry(p, x0, yt, x1, yb, rowh=5.5, col='stone', var=.12, la=120, lw=.55, holes=.025, seed=r.randrange(9999), bottom_dark=.25)
    p.fill([(x0, yt + 3), (x0, yt - 1.5), (x1, yt - 1.5), (x1, yt + 3)], 'stone_l', wob=.2, line=.9)      # walk ledge
    xx = x0
    while xx < x1:   # merlons, a few knocked out
        w_ = r.uniform(5, 7.5); g = r.uniform(4, 6)
        if r.random() > .12: p.rect(xx, ym + r.uniform(0, 2.5) * (r.random() < .2), xx + w_, yt - 1, 'stone_l', wob=.25, line=.9)
        xx += w_ + g
    X = XA + r.uniform(100, 300)
    while X < XB:
        if CW[0] + 120 < X < CW[1] - 120: X += 80; continue
        w = r.uniform(90, 130); top = WALL_TOP - r.uniform(90, 150) * (1 - .4 * dist(X))
        round_tower(p, r, X, YB + 4, w, YB + 4 - top, cone=r.random() < .5, col='stone_l')
        X += r.uniform(380, 560)
def build(seed=1025):
    Wp, Hp = int((XB - XA) * S), int((YB - YA) * S) + 2
    r = random.Random(seed)
    far = Pic(Wp, Hp, seed); mid = Pic(Wp, Hp, seed + 1); front = Pic(Wp, Hp, seed + 2)
    town(far, r, FACE_TOP + 10, lambda X: 1040 + 220 * dist(X) - rise(X) * 1.2 + r.uniform(-50, 30), 0)
    town(mid, r, FACE_TOP + 4, lambda X: 1150 + 150 * dist(X) - rise(X) + r.uniform(-30, 30), .12)
    city_wall(front, r)
    layers = []
    for pic, hz, dr in ((far, .5, .5), (mid, .22, .8), (front, .0, 1.0)):
        im = CT.clean_finish(pic, desat=.2, sepia=.2, bleed=.15); layers.append((im, hz, dr))
    ref_im = layers[2][0]; T = CT.Tone(ref_im, mix=.62, keep=.5, big=14, cel=.6, lift=1.25, detail=.35, flat=1.5)
    out = Image.new('RGBA', (Wp, Hp))
    for k, (im, hz, dr) in enumerate(layers):
        im = CT.drips(T.apply(im), seed + k, dens=dr, lmin=4, lmax=40, wmax=1.6, a0=.7)
        a = np.asarray(im, np.float32).copy()
        if hz: a[..., :3] = a[..., :3] * (1 - hz) + HAZE * hz
        out.alpha_composite(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    a = np.asarray(out, np.float32).copy(); h, w = a.shape[:2]; xs = XA + np.arange(w) / S
    ys = YA + np.arange(h) / S
    fog = np.clip((ys - 1260) / 180., 0, 1)[:, None] * .22 * np.clip(1 - (ys - FACE_TOP) / 40., 0, 1)[:, None]   # ground haze at the town's foot, over the wall's top
    dd = np.array([dist(x) for x in xs])[None]
    a[..., :3] = a[..., :3] * (1 - fog[..., None]) + HAZE * fog[..., None]
    a[..., :3] = a[..., :3] * (1 - .25 * dd[..., None]) + HAZE * .25 * dd[..., None]                        # aerial perspective far out
    fade = np.clip(np.minimum(xs - XA, XB - xs) / 500., 0, 1); a[..., 3] *= fade[None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    bb = out.getbbox(); y0 = bb[1]; out = out.crop((0, y0, Wp, Hp))
    meta = {'img': OUT + 'city.webp', 'x0': XA, 'y0': YA + y0 / S, 'w': XB - XA, 'h': (Hp - y0) / S}
    out.save(os.path.join(ROOT, OUT + 'city.webp'), 'WEBP', quality=88, method=6)
    json.dump(meta, open(os.path.join(ROOT, OUT + 'city.json'), 'w')); print(meta, out.size)
    return meta
if __name__ == '__main__': build()
