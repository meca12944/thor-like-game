"""felt v5 small props, all drawn in code (inkart). each fn -> (Pic, ax, ay) with (ax,ay)=foot anchor in image px (D=2, 32px/tile)."""
import math, random
import numpy as np
from inkart import Pic, PAL, C, tone, mix, masonry, crack, moss_post, soot_post, ivy
T = 32
def _P(w, h, seed): return Pic(int(w), int(h), seed)
def barrel(seed=0, tipped=False):
    p = _P(30, 40, seed); r = random.Random(seed)
    if tipped:
        p.ell(15, 30, 13, 8, 'wood', wob=.3, line=1.2); p.ell(26, 30, 3, 8, 'wood_d', wob=.2, line=1.0)
        for x in (8, 18): p.stroke([(x, 22), (x, 38)], 1.2, 220)
        return p, 15, 38
    p.fill([(4, 10), (26, 10), (28, 22), (26, 36), (4, 36), (2, 22)], 'wood', wob=.3, line=1.2)
    for x in (9, 15, 21): p.stroke([(x, 11), (x + (x - 15) * .1, 35)], .6, 140)
    for y in (14, 31): p.stroke([(3, y), (27, y)], 1.6, 230)
    p.ell(15, 10, 11, 3.5, 'wood_l', wob=.2, line=1.1); p.shade([(19, 11), (27, 11), (27, 36), (19, 36)], .3)
    return p, 15, 37
def crate(seed=0, s=1.0):
    p = _P(36 * s, 40 * s, seed); w = 28 * s; x0 = 4 * s; y0 = 12 * s
    p.fill([(x0, y0), (x0 + w, y0), (x0 + w, y0 + 24 * s), (x0, y0 + 24 * s)], 'wood', wob=.3, line=1.2)
    p.fill([(x0, y0), (x0 + w, y0), (x0 + w - 3 * s, y0 - 8 * s), (x0 + 3 * s, y0 - 8 * s)], 'wood_l', wob=.3, line=1.1)
    p.stroke([(x0 + 2, y0 + 2), (x0 + w - 2, y0 + 24 * s - 2)], 1.2, 210); p.stroke([(x0 + 2, y0 + 12 * s), (x0 + w - 2, y0 + 12 * s)], .7, 150)
    p.shade([(x0 + w * .65, y0), (x0 + w, y0), (x0 + w, y0 + 24 * s), (x0 + w * .65, y0 + 24 * s)], .25)
    return p, 18 * s, y0 + 24 * s + 1
def sacks(seed=0):
    p = _P(44, 34, seed); r = random.Random(seed)
    for cx, cy, s in ((14, 24, 1), (30, 25, .95), (22, 16, .85)):
        p.fill([(cx - 10 * s, cy + 7), (cx - 11 * s, cy - 2), (cx - 5 * s, cy - 9 * s), (cx - 2, cy - 12 * s), (cx + 3, cy - 11 * s), (cx + 6 * s, cy - 9 * s), (cx + 11 * s, cy - 1), (cx + 10 * s, cy + 7)], tone('cloth', r.uniform(.9, 1.08)), wob=.5, line=1.1)
        p.stroke([(cx - 3, cy - 11 * s), (cx + 3, cy - 10 * s)], 1.1)
    return p, 22, 32
def woodpile(seed=0, n=3):
    p = _P(60, 40, seed); r = random.Random(seed)
    for row in range(n):
        y = 32 - row * 8
        for k in range(5 - row):
            x = 8 + row * 5 + k * 10; p.ell(x, y, 5, 4.4, 'wood_l', n=9, wob=.3, line=1.0); p.ell(x, y, 2, 1.6, 'wood', n=6, wob=.2, line=.5)
    return p, 30, 37
def brazier(seed=0):
    p = _P(34, 52, seed)
    for a, b in (((8, 50), (14, 26)), ((26, 50), (20, 26)), ((17, 50), (17, 26))): p.stroke([a, b], 1.8, 235)
    p.fill([(4, 18), (30, 18), (25, 30), (9, 30)], 'iron', wob=.3, line=1.3)
    p.ell(17, 18, 13, 4, 'ember', wob=.4, line=1.1); p.dots(7, 15, 27, 20, 14, 'glow', (.7, 1.5))
    return p, 17, 50
def torch_post(seed=0):
    p = _P(18, 72, seed)
    p.fill([(7, 70), (7, 18), (11, 18), (11, 70)], 'wood_d', wob=.3, line=1.1)
    p.fill([(4, 18), (14, 18), (12, 10), (6, 10)], 'iron', wob=.3, line=1.0); p.ell(9, 9, 5, 3, 'ember', wob=.3, line=.9)
    return p, 9, 70
def lantern_post(seed=0):
    p = _P(36, 90, seed)
    p.fill([(9, 88), (9, 10), (13, 10), (13, 88)], 'iron', wob=.2, line=1.0); p.stroke([(11, 12), (26, 12)], 1.6); p.stroke([(11, 20), (20, 12)], 1.0)
    p.stroke([(25, 12), (25, 17)], .8); p.fill([(20, 17), (30, 17), (29, 30), (21, 30)], 'glow', wob=.2, line=1.3); p.fill([(19, 15), (31, 15), (25, 11)], 'iron', wob=.2, line=1.0)
    p.fill([(5, 88), (17, 88), (16, 82), (6, 82)], 'stone', wob=.3, line=1.0)
    return p, 11, 88
def tent(seed=0, col='cloth', w=3.6, h=2.4):
    W, H = int(w * T + 16), int(h * T + 20); p = _P(W, H, seed); r = random.Random(seed)
    bx0, bx1, by = 8, W - 8, H - 6; ax = W / 2
    p.fill([(ax - 6, 10), (ax + 6, 10), (bx1, by), (bx0, by)], tone(col, .95), wob=.6, line=1.4)
    p.fill([(ax - 6, 10), (ax + 6, 10), (ax + w * T * .32, by - 26), (ax - w * T * .32, by - 26)], tone(col, 1.08), wob=.5, line=1.1)
    p.fill([(ax, 16), (ax + 12, by), (ax - 12, by)], 'void', wob=.4, line=1.2)   # opening
    p.fill([(ax, 18), (ax - 12, by), (ax - 20, by - 2)], tone(col, .8), wob=.4, line=1.0)
    for k in range(3):
        x = r.uniform(bx0 + 10, bx1 - 20); y = r.uniform(30, by - 20); p.fill([(x, y), (x + 12, y + 1), (x + 12, y + 10), (x, y + 9)], tone(col, .78), wob=.4, line=.8)
    p.stroke([(ax, 12), (ax, 1)], 1.6); p.stroke([(bx0, by), (bx0 - 6, by + 4)], .7); p.stroke([(bx1, by), (bx1 + 6, by + 4)], .7)
    p.shade([(ax, 10), (ax + 6, 10), (bx1, by), (ax + 12, by)], .25)
    return p, W / 2, by + 1
def campring(seed=0):
    p = _P(84, 52, seed); r = random.Random(seed)
    for k in range(13):
        a = k / 13 * 2 * math.pi; x = 42 + 32 * math.cos(a); y = 28 + 16 * math.sin(a)
        p.ell(x, y, r.uniform(5, 7), r.uniform(3.5, 5), tone('stone', r.uniform(.85, 1.1)), n=8, wob=.4, line=1.0)
    p.ell(42, 28, 24, 11, 'char', wob=.4, line=.6)
    for a in (.4, 2.1, 3.6, 5.0):
        p.fill([(42 + 4 * math.cos(a), 28 + 2 * math.sin(a)), (42 + 18 * math.cos(a), 28 + 8 * math.sin(a)), (42 + 18 * math.cos(a) + 3, 28 + 8 * math.sin(a) + 3), (42 + 4 * math.cos(a) + 3, 28 + 2 * math.sin(a) + 3)], 'wood_d', wob=.2, line=.9)
    return p, 42, 44
def well(seed=0):
    p = _P(96, 110, seed)
    p.fill([(10, 106), (10, 74), (86, 74), (86, 106)], 'stone', wob=.4, line=1.4)
    masonry(p, 10, 74, 86, 106, rowh=9, col='stone', holes=0, seed=seed)
    p.ell(48, 74, 38, 11, 'stone_l', wob=.4, line=1.3); p.ell(48, 74, 30, 7.5, 'void', wob=.3, line=1.0)
    for x in (16, 80): p.fill([(x - 3, 76), (x + 3, 76), (x + 3, 22), (x - 3, 22)], 'wood_d', wob=.3, line=1.1)
    p.fill([(2, 26), (94, 26), (80, 4), (16, 4)], 'roof', wob=.5, line=1.3); p.stroke([(14, 36), (82, 36)], 1.8)
    p.stroke([(48, 36), (48, 58)], .7); p.fill([(42, 58), (54, 58), (53, 70), (43, 70)], 'wood', wob=.2, line=1.0)
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - 86) / 20, 0, 1), .6, 'moss', 6, seed + 3, .5))
    return p, 48, 106
def board(seed=0):
    p = _P(84, 92, seed); r = random.Random(seed)
    for x in (12, 72): p.fill([(x - 3, 90), (x - 3, 14), (x + 3, 14), (x + 3, 90)], 'wood_d', wob=.3, line=1.1)
    p.fill([(6, 18), (78, 18), (78, 62), (6, 62)], 'wood', wob=.4, line=1.3)
    for k in range(6):
        x = r.uniform(10, 58); y = r.uniform(21, 46); p.fill([(x, y), (x + 15, y + r.uniform(-1, 1)), (x + 15, y + 14), (x, y + 13)], 'paper', wob=.4, line=.8)
        for j in range(3): p.stroke([(x + 2, y + 4 + j * 3), (x + 12, y + 4 + j * 3)], .4, 110)
    p.fill([(2, 18), (82, 18), (74, 6), (10, 6)], 'roof', wob=.4, line=1.1)
    return p, 42, 90
def signpost(seed=0):
    p = _P(70, 84, seed)
    p.fill([(32, 82), (32, 8), (38, 8), (38, 82)], 'wood_d', wob=.3, line=1.1)
    p.fill([(38, 14), (62, 14), (68, 20), (62, 26), (38, 26)], 'wood_l', wob=.3, line=1.1)
    p.fill([(32, 30), (8, 30), (2, 36), (8, 42), (32, 42)], 'wood_l', wob=.3, line=1.1)
    p.fill([(38, 46), (58, 46), (64, 52), (58, 58), (38, 58)], 'wood', wob=.3, line=1.1)
    for y in (20, 36, 52): p.stroke([(14, y), (56, y)], .5, 90)
    return p, 35, 82
def memorial(seed=0):
    p = _P(int(5.5 * T), int(2.6 * T), seed); r = random.Random(seed); W = p.w if hasattr(p, 'w') else int(5.5 * T)
    top = lambda x: 22 + 6 * math.sin(x / 20 + seed) + (8 if 60 < x < 80 else 0)
    pts = [(6, 76)] + [(x, top(x)) for x in range(6, 170, 8)] + [(170, 76)]
    p.fill(pts, 'stone', wob=.5, line=1.4); masonry(p, 6, 14, 170, 76, top=top, rowh=10, col='stone', holes=0, seed=seed)
    for k in range(16):
        x = r.uniform(14, 160); y = r.uniform(34, 66); p.stroke([(x, y), (x + r.uniform(5, 12), y)], .6, 150)
    for k in range(5):
        x = 16 + k * 34 + r.uniform(-4, 4); p.fill([(x - 3, 80), (x + 3, 80), (x + 3, 70), (x - 3, 70)], 'paper', wob=.2, line=.8); p.ell(x, 68, 1.6, 3, 'glow', n=6, wob=0, line=.4)
    for k in range(4):
        x = 30 + k * 38; p.fill([(x, 30), (x + 4, 30), (x + 6 + r.uniform(0, 4), 52), (x + 2, 52)], r.choice(['cloth_r', 'cloth_b', 'cloth_o']), wob=.4, line=.7)
    for k in range(4):
        x = r.uniform(20, 150); p.ell(x, 80, 4, 2, 'herb', n=6, wob=.3, line=.6); p.dots(x - 4, 77, x + 4, 80, 4, 'cloth_o', (.8, 1.3))
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - 55) / 25, 0, 1), .55, 'moss', 6, seed + 5, .55))
    return p, 88, 80
def deadtree(seed=0, h=5.0):
    r = random.Random(seed); H = int(h * T + 20); W = int(h * T * .9); p = _P(W, H, seed)
    def br(x, y, a, L, w, d):
        if d > 5 or L < 5: return
        x2, y2 = x + L * math.cos(a), y - L * math.sin(a)
        p.fill([(x - w * math.sin(a), y - w * math.cos(a)), (x2 - w * .6 * math.sin(a), y2 - w * .6 * math.cos(a)), (x2 + w * .6 * math.sin(a), y2 + w * .6 * math.cos(a)), (x + w * math.sin(a), y + w * math.cos(a))], 'char' if d < 2 else 'wood_d', wob=.3, line=.9 if d < 3 else .6)
        for k in range(r.choice((1, 2, 2, 3))): br(x2, y2, a + r.uniform(-.75, .75), L * r.uniform(.55, .78), w * .62, d + 1)
    br(W / 2, H - 8, math.pi / 2 + r.uniform(-.12, .12), h * T * .38, 6.5, 0)
    p.fill([(W / 2 - 12, H - 6), (W / 2 + 12, H - 6), (W / 2 + 7, H - 14), (W / 2 - 7, H - 14)], 'char', wob=.4, line=1.0)
    return p, W / 2, H - 6
def stump(seed=0):
    p = _P(40, 34, seed)
    p.fill([(6, 30), (8, 12), (32, 12), (34, 30)], 'wood_d', wob=.5, line=1.2); p.ell(20, 12, 12, 4, 'wood_l', wob=.4, line=1.0)
    p.ell(20, 12, 5, 1.7, 'wood', n=7, line=.5); p.fill([(2, 31), (10, 26), (12, 31)], 'wood_d', wob=.3, line=.8)
    return p, 20, 31
def bush(seed=0, col='moss_d', s=1.0):
    r = random.Random(seed); p = _P(52 * s, 40 * s, seed)
    for k in range(9):
        x = r.uniform(10, 42) * s; y = r.uniform(14, 30) * s; p.ell(x, y, r.uniform(6, 10) * s, r.uniform(5, 8) * s, tone(col, r.uniform(.85, 1.15)), n=9, wob=.6, line=.9, la=180)
    for k in range(7):
        x = r.uniform(8, 44) * s; p.stroke([(x, 36 * s), (x + r.uniform(-6, 6), r.uniform(6, 20) * s)], .6, 180)
    return p, 26 * s, 36 * s
def rubble(seed=0, w=3.0, h=1.4, col='stone'):
    r = random.Random(seed); W, H = int(w * T + 12), int(h * T + 14); p = _P(W, H, seed)
    for k in range(int(w * 10)):
        t = r.random(); x = 6 + t * w * T; mh = h * T * (1 - abs(t - .5) * 1.7); y = H - 5 - r.uniform(0, max(mh, 4))
        s_ = r.uniform(4, 11); p.fill([(x - s_, y + s_ * .5), (x - s_ * .6, y - s_ * .5), (x + s_ * .7, y - s_ * .6), (x + s_, y + s_ * .4)], tone(col, r.uniform(.75, 1.15)), wob=.4, line=1.0)
    for k in range(3):
        x = r.uniform(10, W - 30); y = r.uniform(H * .3, H - 10); p.fill([(x, y), (x + r.uniform(18, 30), y - r.uniform(2, 8)), (x + r.uniform(18, 30), y - r.uniform(0, 4) + 4), (x, y + 4)], 'char', wob=.3, line=.9)
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - H * .5) / H, 0, 1), .5, 'moss', 5, seed + 4, .55))
    return p, W / 2, H - 4
def column(seed=0, h=3.0, broken=True):
    r = random.Random(seed); H = int(h * T + 20); p = _P(48, H, seed)
    top = 14 + r.uniform(0, 10)
    pts = [(10, H - 12), (10, top + 6), (16, top), (24, top + 5), (30, top - 2), (38, top + 4), (38, H - 12)] if broken else [(10, H - 12), (10, 10), (38, 10), (38, H - 12)]
    p.fill(pts, 'stone_l', wob=.4, line=1.3)
    for x in (16, 22, 28, 33): p.stroke([(x, top + 8), (x, H - 14)], .6, 120)
    p.fill([(4, H - 4), (44, H - 4), (42, H - 14), (6, H - 14)], 'stone', wob=.3, line=1.2)
    p.shade([(28, top), (38, top), (38, H - 12), (28, H - 12)], .3); crack(p, 20, top + 10, 30, seed, 1.0)
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - H * .6) / H, 0, 1), .6, 'moss', 6, seed, .5))
    return p, 24, H - 4
def grave(seed=0, kind=0):
    r = random.Random(seed); p = _P(36, 44, seed)
    if kind == 0: p.fill([(8, 40), (8, 14)] + [(18 + 10 * math.cos(a), 14 - 9 * math.sin(a)) for a in np.linspace(math.pi, 0, 9)] + [(28, 14), (28, 40)], 'stone', wob=.4, line=1.2)
    elif kind == 1: p.fill([(15, 40), (15, 18), (7, 18), (7, 12), (15, 12), (15, 4), (21, 4), (21, 12), (29, 12), (29, 18), (21, 18), (21, 40)], 'stone_l', wob=.3, line=1.2)
    else: p.fill([(6, 40), (8, 16), (16, 10), (30, 14), (30, 40)], tone('stone', .9), wob=.5, line=1.2)
    p.stroke([(12, 24), (24, 24)], .5, 110); p.stroke([(12, 28), (22, 28)], .5, 110)
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - 24) / 16, 0, 1), .7, 'moss', 5, seed, .5))
    p.fill([(3, 41), (33, 41), (31, 37), (5, 37)], 'moss_d', wob=.5, line=.6, la=150)
    return p, 18, 41
def banner(seed=0, col='cloth_r', h=4.0, torn=.5):
    r = random.Random(seed); H = int(h * T + 10); p = _P(60, H, seed)
    p.fill([(8, H - 4), (8, 6), (12, 6), (12, H - 4)], 'wood_d', wob=.3, line=1.1); p.ell(10, 5, 3, 3, 'iron_l', n=7, line=.8)
    p.stroke([(10, 12), (50, 12)], 1.4)
    L = h * T * .45; pts = [(14, 12), (48, 12), (48, 12 + L * .8)] + [(48 - k * 5, 12 + L * (.8 + .2 * r.random()) - (r.random() < torn) * r.uniform(4, 14)) for k in range(1, 7)] + [(14, 12 + L)]
    p.fill(pts, tone(col, .9), wob=.6, line=1.2)
    p.ell(31, 12 + L * .38, 7, 8, tone('cloth_o', .8), n=9, wob=.4, line=.9)   # faded crest
    p.post.append(soot_post(lambda yy, xx: np.clip((yy - 12 - L * .5) / L, 0, 1), .5, seed))
    return p, 10, H - 4
def laundry(seed=0, w=4.0):
    r = random.Random(seed); W = int(w * T); p = _P(W + 10, 80, seed)
    for x in (5, W + 3): p.fill([(x - 2, 78), (x - 2, 10), (x + 2, 10), (x + 2, 78)], 'wood_d', wob=.3, line=1.0)
    pts = [(5 + t * (W - 2), 14 + 10 * math.sin(t * math.pi)) for t in np.linspace(0, 1, 12)]; p.stroke(pts, .7, 200)
    for k in range(5):
        t = (k + .7) / 6; x = 5 + t * (W - 2); y = 14 + 10 * math.sin(t * math.pi)
        p.fill([(x - 7, y), (x + 7, y + 1), (x + 6 + r.uniform(-2, 2), y + r.uniform(16, 26)), (x - 6, y + r.uniform(16, 26))], r.choice(['cloth', 'cloth_b', 'cloth_r', 'paper']), wob=.5, line=.9)
    return p, W / 2 + 5, 78
def anvil(seed=0):
    p = _P(44, 34, seed)
    p.fill([(14, 32), (16, 22), (28, 22), (30, 32)], 'wood_d', wob=.3, line=1.1)
    p.fill([(2, 10), (34, 10), (40, 13), (30, 16), (28, 22), (16, 22), (14, 16), (8, 14)], 'iron', wob=.2, line=1.2); p.light([(8, 10), (34, 10), (34, 12), (8, 12)], .25)
    return p, 22, 32
def grindstone(seed=0):
    p = _P(46, 44, seed)
    for x in (10, 36): p.stroke([(x, 42), (x, 18)], 1.6)
    p.ell(23, 20, 14, 14, 'stone_l', n=14, wob=.3, line=1.2); p.ell(23, 20, 3, 3, 'wood_d', n=7, line=.8); p.stroke([(23, 20), (40, 26)], 1.4)
    return p, 23, 42
def haystack(seed=0):
    r = random.Random(seed); p = _P(70, 54, seed)
    p.fill([(6, 50), (10, 30), (22, 14), (40, 10), (56, 20), (64, 36), (66, 50)], 'thatch', wob=.7, line=1.2)
    for k in range(60): x = r.uniform(10, 62); y = r.uniform(16, 48); p.stroke([(x, y), (x + r.uniform(-2, 2), y + r.uniform(3, 6))], .5, 120, .2)
    p.post.append(soot_post(lambda yy, xx: np.clip((xx - 30) / 40, 0, 1) * .5, .5, seed))
    return p, 36, 50
def rack(seed=0, kind='herb'):
    r = random.Random(seed); p = _P(80, 64, seed)
    for x in (6, 74): p.fill([(x - 2, 62), (x - 2, 8), (x + 2, 8), (x + 2, 62)], 'wood_d', wob=.3, line=1.0)
    p.stroke([(4, 10), (76, 10)], 1.6); p.stroke([(4, 34), (76, 34)], 1.2)
    for k in range(8):
        x = 12 + k * 8
        if kind == 'herb':
            p.fill([(x - 3, 11), (x + 3, 11), (x + 2, 26), (x - 2, 26)], r.choice(['herb', 'moss', 'thatch_d']), wob=.5, line=.7)
        else:
            p.fill([(x - 1, 34), (x + 1, 34), (x + 1, 4), (x, 1), (x - 1, 4)], 'iron_l', wob=.1, line=.7); p.stroke([(x - 3, 30), (x + 3, 30)], 1.0)
    return p, 40, 62
def stakes(seed=0, w=3.0):
    r = random.Random(seed); W = int(w * T); p = _P(W, 70, seed); xs = []
    for k in range(4):
        x = 8 + k * (W - 16) / 3 + r.uniform(-4, 4); t = r.uniform(26, 44); xs.append((x, t))
        p.fill([(x - 2.5, 68), (x - 2.5, t + 3), (x, t), (x + 2.5, t + 3), (x + 2.5, 68)], 'wood_d', wob=.3, line=1.0)
    for (a, ta), (b, tb) in zip(xs[:-1], xs[1:]):
        for j in range(4): p.stroke([(a, ta + 4 + j * 7), (b, tb + 6 + j * 8 + r.uniform(-3, 3))], .45, 150, .2)
    return p, W / 2, 68
def wagon(seed=0):
    r = random.Random(seed); W, H = int(5.2 * T), int(3.8 * T); p = _P(W, H, seed)
    yb = H - 6
    p.fill([(16, yb - 26), (W - 30, yb - 26), (W - 30, yb - 46), (16, yb - 46)], 'wood', wob=.3, line=1.3)
    for x in np.arange(22, W - 30, 10): p.stroke([(x, yb - 45), (x, yb - 27)], .6, 140)
    p.fill([(14, yb - 46), (W - 28, yb - 46), (W - 36, yb - 96), (22, yb - 96)], 'paper', wob=.6, line=1.4)   # canvas
    for x in np.linspace(30, W - 44, 5): p.stroke([(x, yb - 47), (x + 2, yb - 95)], 1.0, 180)
    p.fill([(40, yb - 80), (70, yb - 82), (72, yb - 60), (42, yb - 58)], tone('cloth_b', .9), wob=.4, line=.9)   # patch
    p.fill([(W - 30, yb - 36), (W - 4, yb - 30), (W - 4, yb - 26), (W - 30, yb - 30)], 'wood_d', wob=.2, line=1.0)   # shaft
    for cx in (36, W - 52):
        p.ell(cx, yb - 15, 15, 15, 'wood_d', n=14, wob=.3, line=1.3); p.ell(cx, yb - 15, 11, 11, 'void', n=12, wob=.2, line=.6, alpha=0)
        for a in np.linspace(0, math.pi, 4, endpoint=False): p.stroke([(cx + 12 * math.cos(a), yb - 15 + 12 * math.sin(a)), (cx - 12 * math.cos(a), yb - 15 - 12 * math.sin(a))], 1.0)
        p.ell(cx, yb - 15, 3, 3, 'iron', n=7, line=.7)
    p.fill([(W - 46, yb - 48), (W - 32, yb - 48), (W - 33, yb - 62), (W - 45, yb - 62)], 'glow', wob=.2, line=1.1)  # lantern
    return p, W / 2, yb
def bench(seed=0):
    p = _P(76, 34, seed)
    p.fill([(4, 14), (72, 14), (70, 20), (6, 20)], 'wood', wob=.3, line=1.1)
    for x in (12, 62): p.stroke([(x, 20), (x - 2, 32)], 2.0)
    return p, 38, 32
def table(seed=0):
    p = _P(84, 50, seed)
    p.fill([(6, 20), (78, 20), (72, 30), (12, 30)], 'wood_l', wob=.3, line=1.2)
    for x in (14, 70): p.stroke([(x, 30), (x, 46)], 2.0)
    p.ell(30, 18, 5, 3, 'wood_d', n=7, line=.8); p.fill([(52, 12), (60, 12), (59, 20), (53, 20)], 'cloth_o', wob=.2, line=.8)
    return p, 42, 46
def cart(seed=0):
    p = _P(90, 60, seed)
    p.fill([(6, 18), (66, 18), (64, 38), (8, 38)], 'wood', wob=.4, line=1.2)
    for x in (18, 30, 42, 54): p.stroke([(x, 19), (x, 37)], .6, 140)
    p.stroke([(64, 30), (88, 36)], 1.8); p.ell(36, 42, 13, 13, 'wood_d', n=12, wob=.3, line=1.2); p.ell(36, 42, 3, 3, 'iron', n=6, line=.7)
    p.fill([(14, 18), (26, 8), (40, 12), (52, 6), (60, 18)], 'cloth', wob=.6, line=1.0)
    return p, 40, 56
def statue(seed=0):
    """village founder: a whole, armoured standing figure leaning on a sword — head intact."""
    p = _P(70, 170, seed)
    p.fill([(8, 166), (62, 166), (58, 140), (12, 140)], 'stone', wob=.4, line=1.3); masonry(p, 12, 140, 58, 166, rowh=9, holes=0, seed=seed)
    p.fill([(22, 140), (48, 140), (46, 96), (52, 70), (46, 52), (24, 52), (18, 70), (24, 96)], 'stone_l', wob=.4, line=1.3)
    p.ell(35, 42, 9, 10, 'stone_l', n=12, wob=.3, line=1.2); p.fill([(26, 40), (44, 40), (42, 30), (28, 30)], 'stone', wob=.3, line=1.0)
    p.fill([(33, 138), (37, 138), (37, 90), (33, 90)], 'iron_l', wob=.1, line=1.0); p.stroke([(26, 90), (44, 90)], 2.0)
    p.shade([(36, 52), (48, 52), (46, 140), (36, 140)], .3)
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - 90) / 80, 0, 1) + (yy < 40) * .5, .6, 'moss', 6, seed, .5))
    return p, 35, 166
