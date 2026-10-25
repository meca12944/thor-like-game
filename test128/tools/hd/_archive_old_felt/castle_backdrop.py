"""castle_backdrop: the royal castle soaring far behind the wall (owner 10-25 「성 뒷편 뷰를 우리 인트로 영상처럼 높은 성으로」).
Reference: the title walk intro (assets/title/title_c_bg.mp4) and the Felt arrival CG (assets/cg/anim/cg_felt_arrival.mp4):
a pyramid of needle spires on a hill (the centre spire tallest, smaller spires stepping down), dark grey stone, ember-lit windows,
smoke columns leaning with the wind, a heavy sepia overcast sky, fog swallowing the hill and the burnt city below.
Everything is code-drawn (inkart: ink outlines, flat cels, watercolour bleed, sepia). Output = one opaque sky picture per map
(world.js hd.backdrop: drawn behind the wall band, clipped to the sky, pinned near the top of the view + parallax; fog bands,
drifting smoke, ember glow and the light break in the clouds are animated by world.js — the lists returned here feed it)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from inkart import Pic, fbm, vnoise, tone, mix, C

def sky(W, H, hor, seed=1):
    """sepia overcast: dark brown-grey top, pale warm horizon; wind-stretched cloud masses with lit tops / dark bellies (watercolour)."""
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H
    top, mid, low = np.array([70, 64, 60.]), np.array([150, 136, 120.]), np.array([222, 206, 178.])
    t = np.clip(yy / (hor / H), 0, 1)[..., None]
    col = np.where(t < .55, top + (mid - top) * (t / .55), mid + (low - mid) * ((t - .55) / .45))
    n = fbm(H, W * 1, 160, seed, 4); n2 = fbm(H, W, 46, seed + 9, 3)
    n = ndimage.zoom(fbm(H, W // 3 + 1, 70, seed + 3, 4), (1, 3.0), order=1)[:H, :W] * .6 + n * .25 + n2 * .15   # stretched along the wind
    d = np.clip((n - .44) / .2, 0, 1) * np.clip(1.25 - t[..., 0] * .9, 0, 1)                               # cloud density, thinner at the horizon
    up = np.roll(d, 10, 0); belly = np.clip(d - up * .9, 0, 1); lit = np.clip(up - d * .7, 0, 1)
    ccol = col * .78 + np.array([90, 82, 78.]) * .22
    col = col * (1 - .55 * d[..., None]) + ccol * .55 * d[..., None]
    col = col * (1 - .35 * belly[..., None]) + np.array([58, 52, 52.]) * .35 * belly[..., None]
    col = col + (np.array([236, 220, 190.]) - col) * (.5 * lit * np.clip(1 - t[..., 0] * .4, 0, 1))[..., None]
    g = ndimage.gaussian_filter(np.hypot(ndimage.sobel(d, 0), ndimage.sobel(d, 1)), 1.2)
    col *= (1 - .18 * np.clip(g / .6, 0, 1))[..., None]                                                    # pigment pooling at the cloud edges
    return col

def light_break(col, W, H, x, y, rx, ry, a=.35):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); m = np.exp(-(((xx - x) / rx) ** 2 + ((yy - y) / ry) ** 2)) * a
    col[:] = col + (np.array([240, 222, 186.]) - col) * m[..., None]

def hills(col, W, H, y0, amp, colr, seed, a=1.0, step=90):
    r = np.random.RandomState(seed); xs = np.arange(W)
    xp = np.arange(0, W + step, step); k = np.interp(xs, xp, r.rand(len(xp)) * amp)
    k = ndimage.gaussian_filter1d(k, step / 3) + ndimage.gaussian_filter1d(r.rand(W) * amp * .15, 4)
    yy = np.mgrid[0:H, 0:W][0]; m = (yy > (y0 - k)[None, :]).astype(np.float32); m = ndimage.gaussian_filter(m, .8) * a
    col[:] = col * (1 - m[..., None]) + np.array(colr, np.float32) * m[..., None]; return m

def castle(p, cx, base, Hc, Wc, seed, glows, smokes, pitch=1.0):
    """the castle on its hill into Pic p (pixel units). base = hill foot y, Hc = tip height above base, Wc = half width."""
    r = random.Random(seed); P = Hc / 40.
    st, st_d, roof = (80, 75, 76), (58, 54, 56), (50, 46, 48)
    # the hill (crag), with a broken road zigzag
    hp = [(cx - Wc * 1.25, base + 2 * P)]
    for i in range(1, 24):
        u = i / 24 * 2 - 1; hp.append((cx + u * Wc * 1.25, base - Hc * .30 * (1 - abs(u) ** 1.6) + r.uniform(-1, 1) * P * .8))
    hp.append((cx + Wc * 1.25, base + 2 * P)); p.fill(hp, (92, 84, 80), wob=1.2, line=1.0, la=190)
    p.shade([(cx + Wc * .1, base - Hc * .3), (cx + Wc * 1.25, base + 2 * P), (cx + Wc * .2, base + 2 * P)], .35, 1.0)
    for k in range(18):                                                                     # crag ledges
        x = cx + r.uniform(-1, 1) * Wc; y = base - r.uniform(0, Hc * .22) * (1 - abs(x - cx) / (Wc * 1.25))
        p.stroke([(x - r.uniform(2, 6) * P, y), (x + r.uniform(2, 6) * P, y + r.uniform(-.6, .6) * P)], .9, 150)
    towers = []
    tiers = [(0, .26, Hc * .30, (.40, .62)), (1, .52, Hc * .20, (.22, .40)), (2, .78, Hc * .10, (.13, .26)), (3, 1.02, Hc * .0, (.07, .15))]
    for ti, span, lift, (h0, h1) in tiers:
        tb = base - lift; n = int(5 + ti * 4)
        # the hall block that ties the tier together (crenellated)
        hb = Hc * (.06 + .02 * ti); xa, xb = cx - Wc * span * .92, cx + Wc * span * .92
        pts = [(xa, tb + 2 * P), (xa, tb - hb)]
        x = xa
        while x < xb - 2 * P:
            pts += [(x + 1.2 * P, tb - hb), (x + 1.2 * P, tb - hb - 1.1 * P), (x + 2.2 * P, tb - hb - 1.1 * P), (x + 2.2 * P, tb - hb)]; x += 2.2 * P
        pts += [(xb, tb - hb), (xb, tb + 2 * P)]
        towers.append(('hall', ti, pts, tb, hb))
        for j in range(n):
            u = (j + .5) / n * 2 - 1 + r.uniform(-.05, .05); x = cx + u * Wc * span
            if ti == 0 and abs(u) < .2: continue
            hh = Hc * r.uniform(h0, h1) * (1 - .35 * abs(u) ** 1.5) * 1.15; w = P * r.uniform(2.2, 3.4) * (1.1 - ti * .08)
            towers.append(('tower', ti, x, tb + r.uniform(0, 1.5) * P, w, hh, r.random()))
    # the keep: the tallest spire at the centre (tip = base - Hc) with two flanking spires
    towers.append(('tower', -1, cx, base - Hc * .30, P * 5.4, Hc * .42, 2.0))
    for s in (-1, 1): towers.append(('tower', -1, cx + s * P * 6.5, base - Hc * .30, P * 4.2, Hc * .52 * .62, 3.0 + (s > 0)))
    towers.sort(key=lambda t: (t[1] if t[0] == 'tower' else t[1] - .5))
    broken = set(r.sample(range(len(towers)), 7)); lean_done = False
    for i, t in enumerate(towers):
        if t[0] == 'hall':
            _, ti, pts, tb, hb = t; c = tone(st, 1.0 + ti * .04)
            p.fill(pts, c, wob=.5, line=1.0, la=200)
            for k in range(int((pts[-1][0] - pts[0][0]) / (3.2 * P))):
                wx = pts[0][0] + (k + .5) * 3.2 * P; wy = tb - hb * .55
                if r.random() < .55: p.rect(wx - .35 * P, wy - .9 * P, wx + .35 * P, wy + .5 * P, (40, 34, 34), wob=.1, line=0)
                if r.random() < .08: p.rect(wx - .35 * P, wy - .9 * P, wx + .35 * P, wy + .5 * P, (214, 120, 60), wob=.1, line=0); glows.append([wx, wy, 2.2 * P])
            continue
        _, ti, x, tb, w, hh, sd = t; rr = random.Random(int(sd * 1e4) + i)
        is_keep = ti == -1; brk = (i in broken) and not is_keep
        lean = 0.0
        if brk and not lean_done and ti in (1, 2) and x > cx: lean = .12; lean_done = True
        top = tb - hh; c = tone(st, 1.0 + max(ti, 0) * .05 + rr.uniform(-.04, .04))
        def L(px, py): return (px + (tb - py) * lean, py)                                          # leaning (half-fallen) tower
        body = [L(x - w / 2, tb + 2 * P), L(x - w / 2, top), L(x + w / 2, top), L(x + w / 2, tb + 2 * P)]
        if brk:                                                                              # broken off: a jagged stump, no roof
            jag = [L(x - w / 2, top)]
            for k in range(1, 5): jag.append(L(x - w / 2 + w * k / 5, top + rr.uniform(-.5, 2.8) * P))
            jag.append(L(x + w / 2, top + rr.uniform(1, 3) * P)); body = [L(x - w / 2, tb + 2 * P)] + jag + [L(x + w / 2, tb + 2 * P)]
        p.fill(body, c, wob=.4, line=1.1 if ti < 2 else .9, la=215)
        p.shade([L(x + w * .12, top), L(x + w / 2, top), L(x + w / 2, tb + 2 * P), L(x + w * .12, tb + 2 * P)], .42, .2)
        p.light([L(x - w / 2 + .4 * P, top + P), L(x - w / 2 + 1.0 * P, top + P), L(x - w / 2 + 1.0 * P, tb), L(x - w / 2 + .4 * P, tb)], .14, .2)
        for k in range(int(hh / (3.4 * P))):                                                 # window slits + string courses
            wy = top + (k + .9) * 3.4 * P
            if wy > tb - P: break
            p.stroke([L(x - w / 2, wy + 1.2 * P), L(x + w / 2, wy + 1.2 * P)], .6, 110, .2)
            if rr.random() < .7:
                ember = rr.random() < (.16 if ti < 2 else .08); wc = (220, 122, 58) if ember else (38, 32, 32)
                a_, b_ = L(x - .3 * P, wy - .9 * P), L(x + .3 * P, wy + .5 * P); p.rect(a_[0], a_[1], b_[0], b_[1], wc, wob=.1, line=0)
                if ember: glows.append([L(x, wy)[0], wy, 2.6 * P])
        if not brk:                                                                          # needle spire roof + pinnacles
            sh = w * rr.uniform(2.6, 4.6) if not is_keep else w * 4.2
            if is_keep and sd == 2.0: sh = top - (base - Hc)                                  # the centre needle reaches the very top
            tip = L(x, top - sh)
            flat = (not is_keep) and rr.random() < .28
            if flat:                                                                         # flat crenellated top + a thin turret needle
                for m in range(3): mx = x - w / 2 + (m + .5) * w / 3; p.rect(mx - .32 * w / 3, top - 1.1 * P, mx + .32 * w / 3, top + .1 * P, c, wob=.1, line=.7, la=200)
                tx_ = x + w * rr.choice([-.28, .28]); p.fill([(tx_ - .6 * P, top), (tx_, top - w * 1.9), (tx_ + .6 * P, top)], roof, wob=.1, line=.7, la=210)
                continue
            p.fill([L(x - w / 2 - .35 * P, top + .2 * P), L(x - w * .18, top - sh * .45), tip, L(x + w * .18, top - sh * .45), L(x + w / 2 + .35 * P, top + .2 * P)], roof, wob=.2, line=1.0, la=225)
            p.shade([tip, L(x + w / 2 + .35 * P, top + .2 * P), L(x + w * .05, top + .2 * P)], .45, .1)
            for s in (-1, 1):
                if w > 2.6 * P: px_ = x + s * (w / 2 - .2 * P); p.fill([L(px_ - .45 * P, top + .2 * P), L(px_, top - w * .9), L(px_ + .45 * P, top + .2 * P)], roof, wob=.1, line=.7, la=200)
            if is_keep and sd == 2.0:
                for k in range(3):                                                           # ribbed tiers on the needle
                    yk = top - sh * (.25 + .22 * k); hw = (w / 2 + .5 * P) * (1 - (top - yk) / sh)
                    p.stroke([(x - hw - .6 * P, yk), (x + hw + .6 * P, yk)], .9, 200, .1)
                    for s in (-1, 1): p.fill([(x + s * (hw + .2 * P) - .3 * P, yk), (x + s * (hw + .2 * P), yk - 2.4 * P), (x + s * (hw + .2 * P) + .3 * P, yk)], roof, wob=0, line=.6, la=200)
        if rr.random() < .22 and ti < 3 and not is_keep: smokes.append([x + rr.uniform(-.3, .3) * w, top + (2 if brk else 4) * P])
    # the collapsed east side: a tall tower snapped in half, its spire fallen against the next roofs
    xb = cx + Wc * .42; yb = base - Hc * .26; hb = Hc * .30; wb = 3.4 * P
    p.fill([(xb - wb / 2, yb), (xb - wb / 2, yb - hb), (xb - wb * .1, yb - hb + 2.2 * P), (xb + wb * .2, yb - hb - .8 * P), (xb + wb / 2, yb - hb + 3.4 * P), (xb + wb / 2, yb)], tone(st, 1.05), wob=.4, line=1.1, la=220)
    p.shade([(xb + wb * .1, yb - hb), (xb + wb / 2, yb - hb + 3.4 * P), (xb + wb / 2, yb), (xb + wb * .1, yb)], .42, .2)
    ang = math.radians(64); L_ = Hc * .30; ox_, oy_ = xb + wb * .7, yb - hb + 5 * P
    def R(u, v): return (ox_ + u * math.cos(ang) - v * math.sin(ang), oy_ + u * math.sin(ang) + v * math.cos(ang))
    p.fill([R(0, -wb / 2), R(L_ * .55, -wb / 2), R(L_, 0), R(L_ * .55, wb / 2), R(0, wb / 2), R(-.8 * P, 0)], roof, wob=.4, line=1.1, la=220)
    p.shade([R(0, 0), R(L_, 0), R(L_ * .55, wb / 2), R(0, wb / 2)], .4, .2)
    # the crag skirt in front of the lowest walls (the castle stands on a rock; no tower feet in the fog)
    sk = [(cx - Wc * 1.3, base + 14 * P)]
    for i in range(41):
        u = i / 40 * 2 - 1; sk.append((cx + u * Wc * 1.3, base - Hc * .07 * (1 - u * u) - r.uniform(0, 1.6) * P + (abs(u) > .95) * 2 * P))
    sk.append((cx + Wc * 1.3, base + 14 * P)); p.fill(sk, (84, 78, 74), wob=1.0, line=1.0, la=180)
    for k in range(26):
        x = cx + r.uniform(-1.2, 1.2) * Wc; y = base - r.uniform(0, Hc * .05)
        p.stroke([(x, y), (x + r.uniform(-3, 3) * P, y + r.uniform(1.5, 3) * P)], .8, 140)
    # rubble cone under the collapsed side
    xr = cx + Wc * .55; p.fill([(xr - 7 * P, base - Hc * .08), (xr - 2 * P, base - Hc * .16), (xr + 4 * P, base - Hc * .13), (xr + 9 * P, base - Hc * .05)], (110, 102, 98), wob=1.0, line=.9, la=170)
    return towers

def city(p, W, y, h, seed, col=(84, 78, 76)):
    """the burnt royal city at the hill foot: broken roofs and gables, one dark band."""
    r = random.Random(seed); pts = [(0, y + h)]; x = 0
    while x < W:
        bw = r.uniform(.8, 2.2) * h * .35; bh = r.uniform(.35, 1) * h; kind = r.random()
        if kind < .45: pts += [(x, y + h - bh * .7), (x + bw / 2, y + h - bh), (x + bw, y + h - bh * .7)]        # gable
        elif kind < .7: pts += [(x, y + h - bh * .6), (x + bw * .3, y + h - bh * .9), (x + bw * .45, y + h - bh * .5), (x + bw, y + h - bh * .7)]  # broken
        else: pts += [(x, y + h - bh * .5), (x + bw, y + h - bh * .5)]
        x += bw
    pts += [(W, y + h)]; p.fill(pts, col, wob=.6, line=.8, la=150)

def wall_line(p, W, foot, Hw, seed, gates=(), col=(88, 82, 80)):
    """the colossal outer wall seen from outside (prologue): a long dark curtain with square towers, merlons, one gate arch."""
    r = random.Random(seed); P = Hw / 13.; top = foot - Hw
    p.fill([(0, foot + 2 * P), (0, top)] + [(x, top - (1.2 * P if (int(x / (2 * P)) % 2) else 0)) for x in np.arange(0, W, P * 1.0)] + [(W, top), (W, foot + 2 * P)], col, wob=.4, line=1.0, la=200)
    for k in range(int(Hw / (1.6 * P))): p.stroke([(0, top + (k + 1) * 1.6 * P + r.uniform(-.2, .2) * P), (W, top + (k + 1) * 1.6 * P)], .5, 70, .4)
    x = r.uniform(4, 9) * P
    while x < W:
        tw = r.uniform(4.5, 6.5) * P; th = Hw * r.uniform(1.18, 1.38)
        p.fill([(x, foot + 2 * P), (x, foot - th), (x + tw, foot - th), (x + tw, foot + 2 * P)], tone(col, 1.06), wob=.4, line=1.1, la=210)
        for m in range(3): mx = x + (m + .5) * tw / 3; p.rect(mx - .7 * P, foot - th - 1.4 * P, mx + .7 * P, foot - th, tone(col, 1.06), wob=.2, line=.8)
        p.shade([(x + tw * .6, foot - th), (x + tw, foot - th), (x + tw, foot + 2 * P), (x + tw * .6, foot + 2 * P)], .4, .2)
        for k in range(3): p.rect(x + tw / 2 - .3 * P, foot - th + (k * 3.5 + 2.5) * P, x + tw / 2 + .3 * P, foot - th + (k * 3.5 + 3.6) * P, (40, 34, 34), wob=.1, line=0)
        x += tw + r.uniform(16, 26) * P
    for gx in gates:                                                      # gate arch: a tall dark mouth with a lit sliver
        gw = 5 * P; gt = foot - Hw * .62
        p.fill([(gx - gw, foot + 2 * P), (gx - gw, gt + gw)] + [(gx + gw * math.cos(math.pi * (1 - i / 12)), gt + gw - gw * math.sin(math.pi * i / 12)) for i in range(13)] + [(gx + gw, foot + 2 * P)], (30, 26, 28), wob=.2, line=1.2, la=230)
        for side in (-1, 1): p.fill([(gx + side * gw * 1.1, foot + 2 * P), (gx + side * gw * 1.1, foot - Hw * 1.5), (gx + side * gw * 2.3, foot - Hw * 1.5), (gx + side * gw * 2.3, foot + 2 * P)], tone(col, 1.1), wob=.3, line=1.1, la=210)
    for gx in gates:
        gw = 5 * P; p.fill([(gx - gw, foot + 2 * P), (gx - gw, foot - 5 * P)] + [(gx + gw * math.cos(a), foot - 5 * P - gw * .9 * math.sin(a)) for a in np.linspace(math.pi, 0, 12)] + [(gx + gw, foot + 2 * P)], (34, 30, 30), wob=.2, line=1.2)

def compose(Wt, Ht, ppt, cx_t, base_t, Hc_t, Wc_t, seed=11, city_t=None, wall=None, hor_t=None, top_fade=None):
    """-> (RGB Image, meta) ; tiles: cx_t castle centre x, base_t hill foot y, Hc_t tip height, Wc_t half width (all in picture tiles); top_fade = tiles over which the sky (and the smoke) fades into one flat colour at the top edge."""
    W, H = int(Wt * ppt), int(Ht * ppt); hor = (hor_t or base_t) * ppt
    col = sky(W, H, hor, seed)
    light_break(col, W, H, cx_t * ppt, (base_t - Hc_t * .45) * ppt, Wc_t * 1.6 * ppt, Hc_t * .55 * ppt, .42)
    hills(col, W, H, hor - 3.2 * ppt, 2.6 * ppt, (150, 140, 130), seed + 1, .9, 140)                    # far ranges (fogged)
    hills(col, W, H, hor - 1.6 * ppt, 2.0 * ppt, (128, 120, 114), seed + 2, .9, 100)
    tf = None
    if top_fade:                                                          # flat sky at the very top so a taller view meets a plain fill (prologue vista)
        tf = np.clip(1 - np.arange(H) / (top_fade * ppt), 0, 1); tf = (tf * tf * (3 - 2 * tf))[:, None]; skc = col[int(top_fade * ppt * .9):int(top_fade * ppt * 1.1)].reshape(-1, 3).mean(0)
        col = col * (1 - tf[..., None]) + skc * tf[..., None]
    glows, smokes = [], []
    p = Pic(W, H, seed); castle(p, cx_t * ppt, base_t * ppt, Hc_t * ppt, Wc_t * ppt, seed, glows, smokes)
    if city_t: city(p, W, (base_t - city_t[1]) * ppt, city_t[1] * ppt, seed + 5)
    ci = np.asarray(p.finish(far=.22, bleed=.3, sepia=.28, desat=.25), np.float32)
    # smoke columns (baked, soft) — world.js adds drifting puffs on the same sources
    sm = np.zeros((H, W), np.float32); r = random.Random(seed + 7)
    srcs = sorted(smokes, key=lambda s: s[1])[:6] + [[cx_t * ppt + r.uniform(-1, 1) * Wc_t * ppt * .9, (base_t - r.uniform(1, 3)) * ppt] for _ in range(3)]
    for sx, sy in srcs:
        for k in range(26):
            t = k / 26; x = sx + t * 12 * ppt + math.sin(t * 5 + sx) * ppt * .6; y = sy - t * 18 * ppt; rad = (.45 + t * 2.4) * ppt
            yy0, yy1, xx0, xx1 = int(max(0, y - rad * 2)), int(min(H, y + rad * 2)), int(max(0, x - rad * 2)), int(min(W, x + rad * 2))
            if yy1 <= yy0 or xx1 <= xx0: continue
            gy, gx = np.mgrid[yy0:yy1, xx0:xx1]; sm[yy0:yy1, xx0:xx1] = np.maximum(sm[yy0:yy1, xx0:xx1], np.exp(-((gx - x) ** 2 + (gy - y) ** 2) / (rad * rad)) * (1 - t) ** .7 * .85)
    sm = ndimage.gaussian_filter(sm * (.75 + .5 * fbm(H, W, 18, seed + 8, 2)), 2)
    if tf is not None: sm = sm * (1 - tf)
    a = ci[..., 3:4] / 255.; col = col * (1 - a) + ci[..., :3] * a
    if wall:
        q = Pic(W, H, seed + 21); wall_line(q, W, wall['foot'] * ppt, wall['h'] * ppt, seed + 21, [g * ppt for g in wall.get('gates', ())])
        wi = np.asarray(q.finish(far=.12, bleed=.3, sepia=.28, desat=.25), np.float32)
    col = col * (1 - .62 * sm[..., None]) + np.array([52, 46, 46.]) * .62 * sm[..., None]
    # fog: the hill and the city half buried (stronger near the foot), a lighter band at the tip height
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32); fn = fbm(H, W, 70, seed + 4, 3)
    strat = .6 + .4 * np.sin(yy / ppt * 1.3 + fn * 5)                                              # stratus bands
    fog = np.clip((yy - (base_t - Hc_t * .30) * ppt) / (Hc_t * .42 * ppt), 0, 1) ** 1.4 * (.5 + .5 * fn) * strat
    fcol = np.array([190, 180, 166.]); col = col * (1 - .78 * fog[..., None]) + fcol * .78 * fog[..., None]
    if wall:
        a = wi[..., 3:4] / 255.; col = col * (1 - a) + wi[..., :3] * a
        f2 = np.clip((yy - (wall['foot'] - wall['h'] * .35) * ppt) / (wall['h'] * .5 * ppt), 0, 1) * (.5 + .5 * fn); col = col * (1 - .55 * f2[..., None]) + fcol * .55 * f2[..., None]
    grain = vnoise(H, W, 2.5, seed + 30); col *= (.965 + .07 * grain)[..., None]
    meta = dict(glows=[[round(g[0], 1), round(g[1], 1), round(g[2], 1)] for g in glows], smoke=[[round(s[0], 1), round(s[1], 1)] for s in srcs],
                tip=[cx_t * ppt, (base_t - Hc_t) * ppt])
    if tf is not None: meta['sky'] = '#%02x%02x%02x' % tuple(int(v) for v in skc)
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)), meta

if __name__ == '__main__':
    im, meta = compose(180, 44, 20, 90, 34, 30, 30, seed=11, city_t=(0, 3.2))
    im.save('/tmp/v6/bd_test.png'); print(im.size, len(meta['glows']), len(meta['smoke']))
