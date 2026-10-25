"""felt v5 (build_felt_v4): the great capital wall, gatehouse, towers, side walls, far royal castle — all drawn in code (inkart)."""
import math, random
import numpy as np
from PIL import Image
from inkart import Pic, PAL, C, tone, mix, masonry, crack, moss_post, soot_post, ivy, fbm, vnoise
T = 32                       # art px per tile (D=2)
WALL_Y = 28                  # foot line of the north wall face
FACE_TOP = 15                # curtain face top (13 tiles = ~6.5 hero heights)
GATE_X = 75.5; ARCH_W = 8; ARCH_SPRING = 22; ARCH_APEX = 17.2
COLLAPSE = [(32, 48, 24.8), (103, 118, 24.6)]          # (x0, x1, lowest top y) broken curtain runs
TOWERS = [(10, 9, 10.0), (30, 8, 10.5), (52, 8, 9.5), (99, 8, 9.8), (121, 8, 10.4), (141, 8, 10.2)]  # (cx, w, top y)
GH = dict(x0=60, x1=91, tl=(60, 68.5), tr=(82.5, 91), top=3.0, ctop=7.0)
def P(x, y): return x * T, y * T
def jag(x0, x1, ybase, depth, seed, low=None):
    """broken top profile: returns f(xpx)->ypx"""
    r = np.random.RandomState(seed); n = int((x1 - x0) * T / 6) + 3; xs = np.linspace(x0 * T, x1 * T, n)
    ys = np.cumsum(r.randn(n)) * 2.2; ys -= np.linspace(ys[0], ys[-1], n); ys = ybase * T + ys
    if low is not None:
        mid = (x0 + x1) / 2 * T; half = (x1 - x0) / 2 * T
        dip = np.clip(1 - np.abs(xs - mid) / half, 0, 1) ** .7; ys = ys + dip * (low - ybase) * T + r.randn(n) * dip * 9
    sq = np.where(r.rand(n) < .25, r.randn(n) * 5, 0); ys = ys + sq
    return lambda x: float(np.interp(x, xs, ys))
def curtain_top_fn():
    fns = [(a, b, jag(a, b, FACE_TOP, 0, 11 + i, low)) for i, (a, b, low) in enumerate(COLLAPSE)]
    base = jag(0, 150, FACE_TOP, 0, 5)
    def f(x):
        for a, b, g in fns:
            if a * T <= x <= b * T: return max(base(x), g(x))
        return min(base(x), FACE_TOP * T + 6)
    return f
def merlons(p, x0, x1, ytop, h=0.85, mw=1.0, gap=.62, seed=0, broken=.18, col='stone_l', skipx=None):
    r = random.Random(seed); x = x0 + r.uniform(0, .4)
    while x + mw <= x1:
        if not (skipx and skipx(x * T)) and r.random() > broken:
            hh = h * r.uniform(.75, 1.05); xa, xb = x * T, (x + mw) * T; yb = ytop * T; yt = yb - hh * T
            chip = r.uniform(0, 5) if r.random() < .4 else 0
            p.fill([(xa, yb), (xa, yt + chip), (xa + (xb - xa) * .5, yt + r.uniform(-1, 1)), (xb, yt + (5 - chip if chip else 0)), (xb, yb)], tone(col, r.uniform(.92, 1.08)), wob=.5, line=1.1)
            p.shade([(xa + (xb - xa) * .62, yt + 2), (xb, yt + 2), (xb, yb), (xa + (xb - xa) * .62, yb)], .3, 0)
            p.light([(xa + 1, yt + 1), (xb - 1, yt + 1), (xb - 1, yt + 4), (xa + 1, yt + 4)], .25, 0)
        x += mw + gap
def string_course(p, x0, x1, y, seed=0, col='stone_l'):
    yy = y * T; p.fill([(x0 * T, yy - 4), (x1 * T, yy - 4), (x1 * T, yy + 3), (x0 * T, yy + 3)], col, wob=.4, line=1.1)
    p.shade([(x0 * T, yy + 3), (x1 * T, yy + 3), (x1 * T, yy + 9), (x0 * T, yy + 9)], .45, .3); p.light([(x0 * T, yy - 4), (x1 * T, yy - 4), (x1 * T, yy - 2), (x0 * T, yy - 2)], .35, 0)
def slit(p, cx, y0, y1, w=.28):
    x0, x1 = (cx - w / 2) * T, (cx + w / 2) * T
    p.fill([(x0 - 3, y0 * T - 2), (x1 + 3, y0 * T - 2), (x1 + 3, y1 * T + 2), (x0 - 3, y1 * T + 2)], 'stone_l', wob=.3, line=.9)
    p.fill([(x0, y0 * T + 3), ((x0 + x1) / 2, y0 * T), (x1, y0 * T + 3), (x1, y1 * T), (x0, y1 * T)], 'void', wob=.2, line=1.0)
def corbels(p, x0, x1, y, seed=0):
    r = random.Random(seed); x = x0 + .2
    p.fill([(x0 * T - 6, (y - .55) * T), (x1 * T + 6, (y - .55) * T), (x1 * T + 6, y * T), (x0 * T - 6, y * T)], 'stone_l', wob=.4, line=1.1)
    while x < x1 - .3:
        xa = x * T; p.fill([(xa, y * T), (xa + .45 * T, y * T), (xa + .38 * T, (y + .5) * T), (xa + .07 * T, (y + .5) * T)], 'stone', wob=.3, line=.9)
        p.fill([(xa + .5 * T, y * T), (xa + .95 * T, y * T), (xa + .95 * T, (y + .32) * T), (xa + .5 * T, (y + .32) * T)], 'void', wob=.2, line=.6, la=120)
        x += .95
def statue(p, cx, ytop, ybot, seed=0):
    """worn knight in a niche: helm, mantle, kite shield, sword point-down; intact (no gore)."""
    h = (ybot - ytop) * T; X = cx * T; Y = ytop * T; s = h / 8.0
    p.fill([(X - 2.1 * s, Y + 8 * s), (X - 2.1 * s, Y + 1.4 * s), (X, Y - .3 * s), (X + 2.1 * s, Y + 1.4 * s), (X + 2.1 * s, Y + 8 * s)], 'stone_dd', wob=.5, line=1.4)   # niche
    p.hatch([(X - 2.0 * s, Y + 1.5 * s), (X, Y), (X + 2 * s, Y + 1.5 * s), (X + 2 * s, Y + 7.9 * s), (X - 2 * s, Y + 7.9 * s)], 3.2, 70, .5, 70)
    stc = 'stone_l'
    p.fill([(X - 1.5 * s, Y + 7.6 * s), (X - 1.1 * s, Y + 3.0 * s), (X - .55 * s, Y + 2.2 * s), (X + .55 * s, Y + 2.2 * s), (X + 1.1 * s, Y + 3.0 * s), (X + 1.5 * s, Y + 7.6 * s)], stc, wob=.6, line=1.3)   # mantle
    p.ell(X, Y + 1.7 * s, .55 * s, .62 * s, stc, wob=.4, line=1.3)                                 # helm
    p.stroke([(X - .4 * s, Y + 1.75 * s), (X + .4 * s, Y + 1.75 * s)], 1.2, 220)                     # visor slit
    p.fill([(X - 1.2 * s, Y + 3.3 * s), (X + .1 * s, Y + 3.3 * s), (X + .1 * s, Y + 5.3 * s), (X - .55 * s, Y + 6.4 * s), (X - 1.2 * s, Y + 5.3 * s)], 'stone', wob=.4, line=1.3)  # shield
    p.stroke([(X - .55 * s, Y + 3.4 * s), (X - .55 * s, Y + 6.2 * s)], .8, 160); p.stroke([(X - 1.1 * s, Y + 4.2 * s), (X, Y + 4.2 * s)], .8, 160)
    p.fill([(X + .62 * s, Y + 3.0 * s), (X + .78 * s, Y + 3.0 * s), (X + .78 * s, Y + 7.5 * s), (X + .7 * s, Y + 7.8 * s), (X + .62 * s, Y + 7.5 * s)], 'stone_l', wob=.2, line=1.0)  # sword
    p.fill([(X + .3 * s, Y + 3.2 * s), (X + 1.1 * s, Y + 3.2 * s), (X + 1.1 * s, Y + 3.4 * s), (X + .3 * s, Y + 3.4 * s)], 'stone_l', wob=.1, line=.9)
    p.shade([(X + .2 * s, Y + 2.2 * s), (X + 1.5 * s, Y + 3 * s), (X + 1.5 * s, Y + 7.6 * s), (X + .2 * s, Y + 7.6 * s)], .3, .3)
    p.fill([(X - 1.9 * s, Y + 7.6 * s), (X + 1.9 * s, Y + 7.6 * s), (X + 2.1 * s, Y + 8.4 * s), (X - 2.1 * s, Y + 8.4 * s)], 'stone_l', wob=.4, line=1.2)   # plinth
    crack(p, X - .3 * s, Y + 2.6 * s, 2.6 * s, seed + 3, .9)
def tower(p, cx, w, top, foot, seed, broken=False, slits=3, courses=(14, 21.5), mach=True):
    x0, x1 = cx - w / 2, cx + w / 2; r = random.Random(seed)
    tf = jag(x0 - .2, x1 + .2, top, 0, seed, low=(top + r.uniform(3, 6)) if broken else None)
    prot = foot - WALL_Y; depth = (prot + 3.0) * .55   # top platform seen from above
    # top platform (stone flags) above the face top
    if not broken: p.fill([(x0 * T - 4, (top - depth) * T), (x1 * T + 4, (top - depth) * T), (x1 * T + 4, top * T), (x0 * T - 4, top * T)], 'stone', wob=.6, line=1.2)
    if not broken: masonry(p, x0 * T, (top - depth) * T + 4, x1 * T, top * T, rowh=7, col='stone_l', var=.15, la=90, lw=.6, holes=0, seed=seed + 1)
    if not broken: p.shade([(x0 * T, (top - depth) * T), (x1 * T, (top - depth) * T), (x1 * T, (top - depth + .5) * T), (x0 * T, (top - depth + .5) * T)], .4, .3)
    if not broken: merlons(p, x0 + .1, x1 - .1, top - depth + .55, .55, .8, .5, seed + 2, .3, 'stone')   # back parapet (small, far)
    # face
    ft = lambda x: tf(x)
    p.fill([(x0 * T, foot * T)] + [(x, ft(x)) for x in np.linspace(x0 * T, x1 * T, 40)] + [(x1 * T, foot * T)], 'stone', wob=.4, line=1.6)
    masonry(p, x0 * T, top * T - 30, x1 * T, foot * T, top=ft, rowh=16, col='stone', var=.14, holes=.02, seed=seed + 3, bottom_dark=.25)
    for side in (x0, x1 - .7):                       # corner quoins
        yy = foot * T; k = 0
        while yy > ft(side * T + 10) + 10:
            ww = (.95 if k % 2 else .65) * T; xa = side * T if side == x0 else x1 * T - ww
            p.fill([(xa, yy - 15), (xa + ww, yy - 15), (xa + ww, yy - 1), (xa, yy - 1)], tone('stone_l', r.uniform(.94, 1.04)), wob=.35, line=1.0)
            yy -= 16; k += 1
    for cy in courses:
        if cy * T > ft(cx * T) + 20: string_course(p, x0 - .1, x1 + .1, cy, seed)
    if mach and not broken: corbels(p, x0 - .15, x1 + .15, top + 1.5, seed); merlons(p, x0 - .1, x1 + .1, top + .05, 1.0, 1.0, .55, seed + 4, .2)
    elif not broken: merlons(p, x0, x1, top, .9, 1.0, .55, seed + 4, .25)
    for i in range(slits):
        sx = cx + (i - (slits - 1) / 2) * (w / (slits + .4)); sy = 16 + (i % 2) * 2.6
        if sy * T > ft(sx * T) + 30: slit(p, sx, sy, sy + 1.5)
    # base batter
    p.fill([(x0 * T - 10, foot * T), (x0 * T - 2, (foot - 1.4) * T), (x1 * T + 2, (foot - 1.4) * T), (x1 * T + 10, foot * T)], 'stone_l', wob=.5, line=1.3)
    masonry(p, x0 * T - 8, (foot - 1.4) * T, x1 * T + 8, foot * T, rowh=11, col='stone_l', var=.12, holes=0, seed=seed + 5)
    p.shade([(x0 * T - 10, (foot - .5) * T), (x1 * T + 10, (foot - .5) * T), (x1 * T + 10, foot * T), (x0 * T - 10, foot * T)], .35, .5)
    p.shade([(x1 * T - w * T * .22, top * T), (x1 * T, top * T), (x1 * T, foot * T), (x1 * T - w * T * .22, foot * T)], .22, 0)   # east side a touch darker
    for i in range(3): crack(p, r.uniform(x0, x1) * T, r.uniform(top + 2, foot - 6) * T, r.uniform(40, 120), seed + 40 + i, 1.2)
    return tf
def build_band(seed=1):
    """the whole north wall (curtain + towers + gatehouse) on one canvas: 150 x (WALL_Y+5) tiles"""
    W, H = 150 * T, (WALL_Y + 5) * T; p = Pic(W, H, seed)
    top = curtain_top_fn(); r = random.Random(seed)
    gx0, gx1 = GH['x0'], GH['x1']
    # --- curtain walkway (behind the parapet), only where intact
    wk = lambda x: top(x) <= FACE_TOP * T + 8
    xs = np.arange(0, W + 1, 8)
    segs = []; cur = None
    for x in xs:
        if wk(x) and not (gx0 * T < x < gx1 * T):
            cur = cur or [x]; cur_end = x
        elif cur: segs.append((cur[0], cur_end)); cur = None
    if cur: segs.append((cur[0], cur_end))
    for a, b in segs:
        p.fill([(a, (FACE_TOP - 2.7) * T), (b, (FACE_TOP - 2.7) * T), (b, FACE_TOP * T), (a, FACE_TOP * T)], 'stone_d', wob=.6, line=1.2)
        masonry(p, a, (FACE_TOP - 2.3) * T, b, FACE_TOP * T, rowh=8, col='stone', var=.16, la=110, lw=.6, holes=0, seed=int(a))
        merlons(p, a / T, b / T, FACE_TOP - 2.2, .5, .7, .45, int(a) + 1, .35, 'stone')
    # --- curtain face
    face = [(0, WALL_Y * T + 4)] + [(x, top(x)) for x in xs] + [(W, WALL_Y * T + 4)]
    p.fill(face, 'stone', wob=.4, line=1.6)
    masonry(p, 0, FACE_TOP * T - 30, W, WALL_Y * T + 4, top=top, rowh=17, col='stone', var=.14, holes=.025, seed=seed + 2, bottom_dark=.2)
    # broken edge core (rubble fill inside the wall) where collapsed
    for a, b, low in COLLAPSE:
        for x in np.arange(a * T, b * T, 5):
            y = top(x); p.fill([(x, y), (x + 6, top(x + 6)), (x + 6, top(x + 6) + r.uniform(5, 11)), (x, y + r.uniform(5, 11))], tone('stone_d', r.uniform(.8, 1.1)), wob=.8, line=.7, la=180)
        for i in range(5): crack(p, r.uniform(a, b) * T, top(r.uniform(a, b) * T) + 8, r.uniform(60, 160), seed + 90 + i + int(a), 1.4)
    # parapet band + merlons on intact curtain
    for a, b in segs:
        p.fill([(a, (FACE_TOP - .6) * T), (b, (FACE_TOP - .6) * T), (b, (FACE_TOP + .5) * T), (a, (FACE_TOP + .5) * T)], 'stone_l', wob=.5, line=1.2)
        merlons(p, a / T, b / T, FACE_TOP - .55, .95, 1.05, .6, int(a) + 7, .22, 'stone_l')
        string_course(p, a / T, b / T, FACE_TOP + .6, int(a))
    # batter / plinth
    p.fill([(0, WALL_Y * T + 4), (0, (WALL_Y - 1.6) * T), (W, (WALL_Y - 1.6) * T), (W, WALL_Y * T + 4)], 'stone_l', wob=.5, line=1.4)
    masonry(p, 0, (WALL_Y - 1.6) * T, W, WALL_Y * T + 4, rowh=12, col='stone_l', var=.12, holes=0, seed=seed + 3)
    string_course(p, 0, 150, WALL_Y - 1.6, seed)
    # arrow slits + drains + patches + cracks along the curtain
    for x in np.arange(3, 148, 6.5):
        if gx0 - 1 < x < gx1 + 1: continue
        if top(x * T) < (FACE_TOP + 2) * T and r.random() < .7: slit(p, x + r.uniform(-.8, .8), FACE_TOP + 2.2, FACE_TOP + 3.8)
        if r.random() < .3:   # drain spout + stain
            dy = r.uniform(19, 24)
            if top(x * T) < (dy - 2) * T:
                p.fill([((x - .3) * T, dy * T), ((x + .3) * T, dy * T), ((x + .3) * T, (dy + .4) * T), ((x - .3) * T, (dy + .4) * T)], 'void', wob=.2, line=1)
                p.shade([((x - .25) * T, (dy + .4) * T), ((x + .25) * T, (dy + .4) * T), ((x + .45) * T, (WALL_Y - 1.6) * T), ((x - .45) * T, (WALL_Y - 1.6) * T)], .4, 1.0)
    for i in range(26):
        x = r.uniform(2, 148)
        if gx0 - 1 < x < gx1 + 1: continue
        crack(p, x * T, max(top(x * T) + 6, r.uniform(FACE_TOP + 1, 22) * T), r.uniform(50, 200), seed + 200 + i, r.uniform(1.0, 1.6))
    # soot from the burning + moss at the foot / on ledges
    def soot_w(yy, xx):
        s = np.clip(1 - (yy - FACE_TOP * T) / (9 * T), 0, 1) * .9
        for a, b, low in COLLAPSE: s = s + np.clip(1 - np.abs(xx - (a + b) / 2 * T) / ((b - a) / 2 * T + 60), 0, 1) * .7
        return np.clip(s, 0, 1) * (yy < WALL_Y * T)
    p.post.append(soot_post(soot_w, .5, 3))
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - (WALL_Y - 5) * T) / (5 * T), 0, 1) + np.clip(1 - np.abs(yy - (FACE_TOP + .6) * T) / 14, 0, 1) * .8, .75, 'moss', 10, 4, .62))
    for i in range(22):
        x = r.uniform(2, 148)
        if gx0 < x < gx1: continue
        ivy(p, x * T, top(x * T) + 4, r.uniform(60, 260), seed + 300 + i)
    # --- towers (in front of the curtain) + their cast shadow on the curtain (light from the upper left)
    for cx, w, tp in TOWERS + [((GH['tl'][0] + GH['tl'][1]) / 2, 8.5, 3), ((GH['tr'][0] + GH['tr'][1]) / 2, 8.5, 3)]:
        xr = (cx + w / 2) * T; p.shade([(xr, max(tp, FACE_TOP - 1) * T), (xr + 2.6 * T, (max(tp, FACE_TOP - 1) + 2.2) * T), (xr + 2.6 * T, WALL_Y * T + 4), (xr, WALL_Y * T + 4)], .42, .8)
    for i, (cx, w, tp) in enumerate(TOWERS):
        tower(p, cx, w, tp, WALL_Y + 2.5, seed + 500 + i * 17, broken=(i in (2, 4)))
    # --- gatehouse
    gate(p, seed + 900)
    return p
def gate(p, seed):
    r = random.Random(seed); gx0, gx1 = GH['x0'], GH['x1']; tl, tr = GH['tl'], GH['tr']
    cx0, cx1 = tl[1], tr[0]; foot_c = WALL_Y + 1.0; foot_t = WALL_Y + 3.5
    # centre block: top with a V-collapse over the arch
    cf = jag(cx0 - .3, cx1 + .3, GH['ctop'], 0, seed, low=13.6)
    ax0, ax1 = GATE_X - ARCH_W / 2, GATE_X + ARCH_W / 2
    def opening(x, y):   # inside the pointed arch?
        if not (ax0 * T <= x <= ax1 * T): return False
        if y >= ARCH_SPRING * T: return True
        R = ARCH_W * .8 * T; dxl = x - (ax0 * T + R); dxr = x - (ax1 * T - R); yy = y - ARCH_SPRING * T
        return (dxl ** 2 + yy ** 2 <= R ** 2) and (dxr ** 2 + yy ** 2 <= R ** 2)
    depth = 3.2 * .55
    xs = np.linspace(cx0 * T, cx1 * T, 60)
    p.fill([(cx0 * T, foot_c * T)] + [(x, cf(x)) for x in xs] + [(cx1 * T, foot_c * T)], 'stone', wob=.4, line=1.6)
    masonry(p, cx0 * T, GH['ctop'] * T - 30, cx1 * T, foot_c * T, top=cf, rowh=17, col='stone', var=.13, holes=.015, seed=seed + 1, bottom_dark=.2)
    for x in np.arange(cx0 * T, cx1 * T, 5):
        y = cf(x)
        if y > (GH['ctop'] + 1.2) * T: p.fill([(x, y), (x + 6, cf(x + 6)), (x + 6, cf(x + 6) + r.uniform(4, 10)), (x, y + r.uniform(4, 10))], tone('stone_d', r.uniform(.8, 1.1)), wob=.8, line=.7, la=180)
    # arch: archivolt rings (recessed steps) + voussoirs + keystone
    R = ARCH_W * .8 * T
    def arch_poly(grow, n=40):
        pts = []; cxl = ax0 * T + R; cxr = ax1 * T - R; Rg = R + grow
        a_end = math.acos((GATE_X * T - cxl) / Rg) if abs((GATE_X * T - cxl) / Rg) <= 1 else 0
        for t in np.linspace(math.pi, math.pi + (math.pi - a_end) if False else 0, 2): pass
        # left arc (centre cxl): from angle pi (left spring) up to apex; right arc mirrored
        apex_y = None
        L = []
        for t in np.linspace(0, 1, n):
            ang = math.pi + t * (math.pi / 2 - (math.acos(min(1, (GATE_X * T - cxl) / Rg)) if Rg > 0 else 0))
            L.append((cxl + Rg * math.cos(ang), ARCH_SPRING * T + Rg * math.sin(ang)))
        Rr = [(2 * GATE_X * T - x, y) for x, y in reversed(L)]
        return [(ax0 * T - grow, foot_c * T)] + L + Rr[1:] + [(ax1 * T + grow, foot_c * T)]
    p.shade(arch_poly(2.4 * T), .25, .6)
    for k, (g, c) in enumerate([(1.7 * T, 'stone_l'), (.95 * T, 'stone_d'), (.48 * T, 'stone_dd')]):
        pp_ = p.fill(arch_poly(g), c, wob=.4, line=1.6)
        if k == 1: p.hatch(arch_poly(g), 3.5, 65, .55, 90)
    outer = arch_poly(1.7 * T); inner = arch_poly(.95 * T)   # voussoirs: wedge stones across the outer ring
    for i in range(1, len(outer) - 1, 2):
        x, y = outer[i]; xi, yi = inner[i]; p.stroke([(x, y), (xi, yi)], 1.3, 225, .2)
        if i % 4 == 1: p.light([(x, y), (outer[min(i + 2, len(outer) - 1)][0], outer[min(i + 2, len(outer) - 1)][1]), (inner[min(i + 2, len(inner) - 1)][0], inner[min(i + 2, len(inner) - 1)][1]), (xi, yi)], .22, 0)
    kx = GATE_X * T; ky = outer[41][1]
    p.fill([(kx - 20, ky - 10), (kx + 20, ky - 10), (kx + 13, ky + 44), (kx - 13, ky + 44)], 'stone_l', wob=.4, line=1.7)
    crack(p, kx + 2, ky - 6, 70, seed + 7, 1.5)
    # carved crest above the arch (worn): crown over crossed swords in a roundel
    cy = (ARCH_APEX - 2.6) * T
    if cf(kx) < cy - 40:
        p.ell(kx, cy, 30, 30, 'stone_l', wob=.5, line=1.5); p.ell(kx, cy, 23, 23, 'stone', wob=.5, line=1.0)
        p.fill([(kx - 13, cy + 2), (kx - 13, cy - 10), (kx - 7, cy - 4), (kx, cy - 13), (kx + 7, cy - 4), (kx + 13, cy - 10), (kx + 13, cy + 2)], 'stone_l', wob=.5, line=1.2)
        p.stroke([(kx - 15, cy + 16), (kx + 15, cy + 5)], 1.4); p.stroke([(kx + 15, cy + 16), (kx - 15, cy + 5)], 1.4)
        crack(p, kx - 20, cy - 20, 60, seed + 8, 1.0)
    # punch the opening (transparent, after the ink): the tunnel is a separate prop behind the hero
    h_, w_ = p.h, p.w; x0i, x1i = int(ax0 * T) - 1, int(ax1 * T) + 2; y0i, y1i = int(ARCH_APEX * T) - 4, min(h_, int(foot_c * T) + 8)
    yy, xx = np.mgrid[y0i:y1i, x0i:x1i]; m = np.vectorize(opening)(xx, yy); cut = np.zeros((h_, w_), bool); cut[y0i:y1i, x0i:x1i] = m
    p.meta['cut'] = cut
    # portcullis remnant hanging in the arch (iron, bent, some bars gone): its own small picture laid over after the cut
    pc = Pic(x1i - x0i, int(5.5 * T), seed + 1); ox, oy = x0i, int(ARCH_APEX * T) - 4
    for i in range(9):
        bx = (ax0 + .55 + i * (ARCH_W - 1.1) / 8) * T - ox; yb = (ARCH_SPRING - .3 + r.uniform(-.8, 1.4)) * T - oy
        if i in (3, 6): yb = (ARCH_SPRING - 2.2) * T - oy
        yt = 2 + abs(bx + ox - kx) * .75
        bend = r.uniform(-4, 4) if i % 3 == 0 else 0
        if opening(bx + ox, yt + oy + 4): pc.fill([(bx - 2.4, yt), (bx + 2.4, yt), (bx + 2.4 + bend, yb), (bx + bend, yb + 7), (bx - 2.4 + bend, yb)], 'iron', wob=.3, line=1.0)
    for j in range(3):
        yy_ = (ARCH_APEX + 1.3 + j * 1.25) * T - oy; xa = (ax0 + .9 - (j == 2) * .3) * T - ox; xb = (ax1 - .9 + (j == 2) * .3) * T - ox
        if j == 0: xa += 1.4 * T; xb -= 1.4 * T
        pc.fill([(xa, yy_), (xb, yy_ + r.uniform(-3, 3)), (xb, yy_ + 5), (xa, yy_ + 5)], 'iron', wob=.4, line=1.0)
    p.meta['portc_pic'] = (pc, ox, oy)
    p.meta['portc'] = True
    # flanking gate towers (protrude more), statues in niches, banner hooks
    for i, (x0, x1) in enumerate((tl, tr)):
        cxx = (x0 + x1) / 2; w = x1 - x0
        tower(p, cxx, w, GH['top'], foot_t, seed + 30 + i * 11, broken=(i == 1), slits=2, courses=(10.5, 23.5))
        statue(p, cxx, 13.4, 22.6, seed + 50 + i)
        for hy in (11.0,):
            p.fill([((cxx - .25) * T, hy * T), ((cxx + .25) * T, hy * T), ((cxx + .25) * T, (hy + .3) * T), ((cxx - .25) * T, (hy + .3) * T)], 'iron', wob=.2, line=.8)
    # chains hanging from the broken V
    for cxs in (GATE_X - 2.4, GATE_X + 3.1):
        y0 = cf(cxs * T) + 4; L = r.uniform(70, 120); pts = []
        for k in range(int(L / 5)): pts.append((cxs * T + math.sin(k * .3) * 2, y0 + k * 5))
        for k in range(0, len(pts) - 1, 2): p.ell(pts[k][0], pts[k][1] + 2, 2.2, 3.2, 'iron', n=8, wob=0, line=.7)
def tunnel(seed=3):
    """the vaulted passage seen through the arch: dark, converging, a pale far opening (the ash field)."""
    ax0, ax1 = GATE_X - ARCH_W / 2, GATE_X + ARCH_W / 2; Wp = (ARCH_W + .6) * T; y0 = ARCH_APEX - .3; y1 = WALL_Y + .2
    Hp = (y1 - y0) * T; p = Pic(Wp, Hp, seed); ox = (ax0 - .3) * T; oy = y0 * T
    L = lambda x, y: (x - ox, y - oy)
    p.rect(0, 0, Wp, Hp, 'stone_dd', wob=0, line=0)
    fx0, fx1, fy0, fy1 = (GATE_X - 2.0) * T, (GATE_X + 2.0) * T, (ARCH_SPRING - 1.2) * T, (WALL_Y - 3.6) * T
    # side walls converge to the far opening
    p.fill([L(ax0 * T, ARCH_SPRING * T), L(fx0, fy0), L(fx0, fy1), L(ax0 * T, y1 * T)], 'stone_d', wob=.3, line=1.0)
    p.fill([L(ax1 * T, ARCH_SPRING * T), L(fx1, fy0), L(fx1, fy1), L(ax1 * T, y1 * T)], tone('stone_d', .85), wob=.3, line=1.0)
    for k in range(1, 6):   # vault ribs
        t = k / 6; xa = ax0 * T + (fx0 - ax0 * T) * t; xb = ax1 * T + (fx1 - ax1 * T) * t; ya = ARCH_SPRING * T + (fy0 - ARCH_SPRING * T) * t; yb = (WALL_Y + .2) * T + (fy1 - (WALL_Y + .2) * T) * t
        p.stroke([L(xa, yb), L(xa, ya), L((xa + xb) / 2, ya - (xb - xa) * .35), L(xb, ya), L(xb, yb)], 1.0, 150, .3)
    p.fill([L(ax0 * T, y1 * T), L(fx0, fy1), L(fx1, fy1), L(ax1 * T, y1 * T)], 'stone', wob=.3, line=1.0)   # floor
    for k in range(1, 7):
        t = (k / 7) ** 1.6; yy = y1 * T + (fy1 - y1 * T) * t; xa = ax0 * T + (fx0 - ax0 * T) * t; xb = ax1 * T + (fx1 - ax1 * T) * t
        p.stroke([L(xa, yy), L(xb, yy)], .7, 120, .3)
    # far opening (pointed) with pale field light + a dead tree silhouette
    R = (fx1 - fx0) * .8; sp = fy0 + 10
    far = [L(fx0, fy1)] + [L(fx0 + R * (1 + math.cos(a)) - R + 0 if False else fx1 - R + R * math.cos(a), sp + R * math.sin(a)) for a in np.linspace(math.pi, math.pi * 1.5 - .35, 10)]
    far = [L(fx0, fy1), L(fx0, sp)] + [L(fx1 - R + R * math.cos(a), sp + R * math.sin(a)) for a in np.linspace(math.pi, math.pi * 1.62, 8)] + [L(fx0 + R + R * math.cos(a), sp + R * math.sin(a)) for a in np.linspace(math.pi * 1.38, math.pi * 2, 8)] + [L(fx1, sp), L(fx1, fy1)]
    p.fill(far, (122, 114, 104), wob=.3, line=1.2)   # v7 (owner 10-25 「하늘은 그리지 말고」): a dim fog-dark opening, not a pale sky
    p.fill([L(fx0, fy1), L(fx0, fy1 - 10), L(fx0 + 30, fy1 - 14), L(fx1 - 20, fy1 - 9), L(fx1, fy1 - 12), L(fx1, fy1)], (96, 90, 84), wob=.6, line=.8, la=140)
    tx = fx0 + 40; p.stroke([L(tx, fy1 - 12), L(tx + 2, fy1 - 40), L(tx - 6, fy1 - 52)], 1.2, 150); p.stroke([L(tx + 2, fy1 - 34), L(tx + 12, fy1 - 46)], .9, 150)
    def dark(pp, col, a):
        h, w = a.shape; yy, xx = np.mgrid[0:h, 0:w]; cxp = (GATE_X * T - ox); d = np.hypot((xx - cxp) / (w * .5), (yy - (fy0 + fy1) / 2 + oy) / (h * .6))
        f = np.clip(.45 + .55 * (1 - np.clip(d, 0, 1)), .35, 1); bright = (col.mean(2) > 190)
        col[:] = np.where(bright[..., None], col, col * f[..., None] * .85)
    p.post.append(dark)
    return p, ox, oy
def far_castle(seed=9, Wt=120, kxt=None):
    """royal castle far behind the wall: a cool grey strip, light ink, fog at its foot (parallax prop)."""
    W, H = Wt * T, 15 * T; p = Pic(W, H, seed); r = random.Random(seed); B = H - 6
    p.fill([(0, B), (0, B - 3.2 * T)] + [(x, B - 3.2 * T - (r.random() < .2) * 10) for x in np.arange(40, W, 40)] + [(W, B - 3.2 * T), (W, B)], (150, 148, 150), wob=.6, line=1.0, la=150)
    for x in np.arange(4 * T, W - 3 * T, r.uniform(9, 13) * T):
        tw, th = r.uniform(1.6, 2.4) * T, r.uniform(4.4, 6.2) * T; xa = x
        p.fill([(xa, B), (xa, B - th), (xa + tw / 2, B - th - tw * .9), (xa + tw, B - th), (xa + tw, B)], (140, 139, 143), wob=.5, line=1.0, la=150)
    kx = (kxt * T if kxt else W / 2); base = B - 3 * T
    p.fill([(kx - 15 * T, B), (kx - 15 * T, base - 3 * T), (kx + 15 * T, base - 3 * T), (kx + 15 * T, B)], (136, 135, 140), wob=.5, line=1.0, la=150)
    for dx, tw, th in [(-11, 3, 8), (-6, 3.6, 10.5), (0, 5, 13.5), (6, 3.6, 10), (11, 3, 7.5)]:
        xa = kx + dx * T - tw * T / 2
        p.fill([(xa, base), (xa, base - th * T + 3 * T), (xa + tw * T / 2, base - th * T), (xa + tw * T, base - th * T + 3 * T), (xa + tw * T, base)], (128, 127, 134), wob=.5, line=1.1, la=160)
        for k in range(int(th / 2.5)): p.fill([(xa + tw * T * .42, base - (k * 2.4 + 2) * T), (xa + tw * T * .58, base - (k * 2.4 + 2) * T), (xa + tw * T * .58, base - (k * 2.4 + 1.4) * T), (xa + tw * T * .42, base - (k * 2.4 + 1.4) * T)], (92, 90, 96), wob=.1, line=0)
    p.fill([(kx - .15 * T, base - 13.5 * T), (kx + .15 * T, base - 13.5 * T), (kx + .15 * T, base - 15.5 * T), (kx - .15 * T, base - 15.5 * T)], (110, 108, 114), wob=0, line=.8, la=140)
    def fog(pp, col, a):
        h, w = a.shape; yy = np.mgrid[0:h, 0:w][0]; f = np.clip((yy - (B - 6 * T)) / (6 * T), 0, 1) ** 1.3
        col[:] = col * (1 - .55 * f[..., None]) + np.array([196, 190, 182.]) * .55 * f[..., None]
        top = np.clip(1 - yy / (H * .7), 0, 1); col[:] = col * (1 - .2 * top[..., None]) + np.array([170, 168, 172.]) * .2 * top[..., None]
    p.post.append(fog)
    return p
FINISH = None   # a13: build_felt5 sets castle_tone.clean_finish (the castle's stone) for the side-wall chunks
def side_wall_chunks(x0, x1, y0, y1, hfn, seed, L=3.0, inner='right'):
    """N-S wall run on the map edge, cut in y-chunks (y-sorted props). returns list of (Image, x_tl_tiles, y_foot, ax, ay)"""
    out = []; r = random.Random(seed); y = y0
    while y < y1 - .01:
        yb = min(y1, y + L); h = hfn((y + yb) / 2)
        if h <= .05: y = yb; continue
        w = (x1 - x0); Wp = int((w + .6) * T); Hp = int((L + h + .9) * T); p = Pic(Wp, Hp, seed + int(y * 7)); ox = .3 * T
        fb = Hp - 4; ft = fb - h * T; tt = ft - L * T
        jt = jag(0, w, 0, 0, seed + int(y * 3)); tf = lambda xx: ft + (jt(xx - ox) if h > 1.2 else 0) * .6
        # top surface (rubble, flags, grass) displaced up by h
        p.fill([(ox, tt), (ox + w * T, tt), (ox + w * T, ft), (ox, ft)], 'stone_d', wob=.9, line=1.1)
        masonry(p, ox + 2, tt + 2, ox + w * T - 2, ft, rowh=9, col='stone', var=.2, la=100, lw=.6, holes=.05, seed=seed + int(y * 11))
        ie = ox + w * T - 5 if inner == 'right' else ox + 5
        p.shade([(ie - 6, tt), (ie + 6, tt), (ie + 6, ft), (ie - 6, ft)], .35, .6)
        for k in range(4): p.ell(r.uniform(ox + 8, ox + w * T - 8), r.uniform(tt + 6, ft - 4), r.uniform(4, 8), r.uniform(3, 5), tone('stone_l', r.uniform(.9, 1.05)), wob=.6, line=1.0)
        # south face of this chunk
        p.fill([(ox, fb), (ox, ft), (ox + w * T, ft), (ox + w * T, fb)], 'stone', wob=.4, line=1.4)
        masonry(p, ox, ft, ox + w * T, fb, rowh=16, col='stone', var=.14, holes=.02, seed=seed + int(y * 13), bottom_dark=.2)
        p.post.append(moss_post(lambda yy, xx, ft=ft: np.clip((yy - ft) / 60., 0, 1) * .3 + (yy < ft) * .5, .7, 'moss', 8, 6 + int(y), .6))
        p.post.append(soot_post(lambda yy, xx, ft=ft, fb=fb: np.clip(1 - (yy - ft) / (fb - ft + 1), 0, 1) * (yy > ft) * .6, .45, int(y)))
        if r.random() < .5: crack(p, r.uniform(ox + 10, ox + w * T - 10), ft + 6, r.uniform(30, (fb - ft)), seed + int(y * 17), 1.2)
        out.append(((FINISH or Pic.finish)(p), x0 - .3, yb, (x0 - x0 + .3) * T, fb - 0))
        y = yb
    return out
if __name__ == '__main__':
    import sys
    p = build_band(); im = p.finish(cut=p.meta['cut']); pc, ox, oy = p.meta['portc_pic']; im.alpha_composite(pc.finish(), (ox, oy)); im.save('/tmp/v5/band.png'); print(im.size)
    tp, ox, oy = tunnel(); tp.finish().save('/tmp/v5/tunnel.png'); far_castle().finish(far=.4).save('/tmp/v5/far.png')
