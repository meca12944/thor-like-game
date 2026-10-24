#!/usr/bin/env python3
"""Trail of Extinction (사멸의 궤적) - 6 dark sword-slash trail design proposals.
Procedural pixel art (PIL + numpy). Design preview only: no game code / assets touched.
Run: python3 make.py   (outputs next to this file)

Shape (all styles): body-centred half-moon sweep. Arc centre = hero body, radius R = reach*0.7 (70px at the
~124px-tall 256-canvas scale). Hit1/Hit2 = 140 deg, Hit3 = 170 deg. Filled fan (= hitbox) behind the hero,
rim trail in front, thicker/brighter toward the tip, blade afterimages, tip sparkle, speed lines.
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
HERO = os.path.join(HERE, '..', 'dark_v3prop', 'east.png')
N = 256
YY, XX = np.mgrid[0:N, 0:N].astype(np.float32)

def hx(c):
    c = c.lstrip('#'); return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)

BG = '#1a1c22'; BG2 = '#16181d'; BG3 = '#1e2128'; SHADOW = '#111217'
BLADE = dict(o='#0d0f13', d='#5d6670', m='#9aa3ad', h='#cfd5db')

# ---------------------------------------------------------------- arcs (hit1 / hit2 / hit3)
CX, CY = 128, 128            # hero body centre (torso) on the 256 canvas
R = 70.0                     # = attack reach x 0.7
ARCS = {
    'A1': dict(c=(CX, CY), R=R, sq=0.55, rot=0.0,   a0=-70.0, a1=70.0),    # horizontal 140
    'A2': dict(c=(CX, CY), R=R, sq=0.60, rot=-28.0, a0=70.0,  a1=-70.0),   # reverse diagonal 140
    'A3': dict(c=(CX, CY - 12), R=R, sq=0.85, rot=0.0, a0=-130.0, a1=40.0),# overhead slam 170
}
# 8 frames per hit. delays: 60fps ticks (6 / 2 / 2 / 2 / 3 / 3 / 3 / 6 ticks)
FRAMES = [
    dict(head=None, tail=0.0, fade=0.0, blade=-0.06),   # 0 anticipation (wind-up glint)
    dict(head=0.35, tail=0.0, fade=0.0, blade=0.35),    # 1 swipe
    dict(head=0.72, tail=0.0, fade=0.0, blade=0.72),    # 2 swipe
    dict(head=1.00, tail=0.0, fade=0.0, blade=1.00),    # 3 full trail
    dict(head=1.00, tail=0.22, fade=0.25, blade=1.04),  # 4 fade
    dict(head=1.00, tail=0.48, fade=0.50, blade=1.06),  # 5 fade
    dict(head=1.00, tail=0.72, fade=0.75, blade=1.07),  # 6 fade
    dict(head=1.00, tail=0.96, fade=0.95, blade=1.07),  # 7 remnants
]
DELAYS = [100, 33, 33, 33, 50, 50, 50, 100]
TIMES = list(np.cumsum([0] + DELAYS[:-1]) / 1000.0)

GEO = {}
def geo(k):
    if k in GEO: return GEO[k]
    a = ARCS[k]; cx, cy = a['c']; t = math.radians(a['rot'])
    px, py = XX - cx, YY - cy
    qx = px * math.cos(t) + py * math.sin(t)
    qy = (-px * math.sin(t) + py * math.cos(t)) / a['sq']
    r = np.hypot(qx, qy); th = np.degrees(np.arctan2(qy, qx))
    s = (th - a['a0']) / (a['a1'] - a['a0'])
    GEO[k] = dict(r=r, s=s, a=a); return GEO[k]

def pt(k, s, rr):
    a = ARCS[k]; th = math.radians(a['a0'] + s * (a['a1'] - a['a0'])); t = math.radians(a['rot'])
    qx, qy = rr * math.cos(th), rr * math.sin(th) * a['sq']
    return (a['c'][0] + qx * math.cos(t) - qy * math.sin(t), a['c'][1] + qx * math.sin(t) + qy * math.cos(t))

def tangent(k, s):
    p0, p1 = pt(k, s - 0.01, R), pt(k, s + 0.01, R); d = (p1[0] - p0[0], p1[1] - p0[1]); l = math.hypot(*d) or 1
    return (d[0] / l, d[1] / l)

def normal_out(k, s):
    c = ARCS[k]['c']; p = pt(k, s, R); d = (p[0] - c[0], p[1] - c[1]); l = math.hypot(*d) or 1
    return (d[0] / l, d[1] / l)

def snoise(cell, seed, shift=(0, 0)):
    """smooth value noise (bilinear) -> thresholding gives crisp organic pixel shapes"""
    rng = np.random.default_rng(seed); g = rng.random((N // cell + 3, N // cell + 3)).astype(np.float32)
    x = (XX + shift[0]) / cell; y = (YY + shift[1]) / cell
    x = np.mod(x, g.shape[1] - 2); y = np.mod(y, g.shape[0] - 2)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    a = g[y0, x0]; b = g[y0, x0 + 1]; c = g[y0 + 1, x0]; d = g[y0 + 1, x0 + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy

def bnoise(cell, seed):
    rng = np.random.default_rng(seed); g = rng.random((N // cell + 1, N // cell + 1)).astype(np.float32)
    return g[(YY // cell).astype(int), (XX // cell).astype(int)]

# ---------------------------------------------------------------- layer helpers
class Layer:
    def __init__(self): self.a = np.zeros((N, N, 4), np.uint8)
    def paint(self, m, col): self.a[m] = hx(col)
    def px(self, x, y, col):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < N and 0 <= y < N: self.a[y, x] = hx(col)
    def rect(self, x, y, w, h, col):
        for i in range(w):
            for j in range(h): self.px(x + i, y + j, col)
    def mask(self): return self.a[..., 3] > 0
    def outline(self, col, m=None, diag=True):
        m = self.mask() if m is None else m
        d = dil(m, diag) & ~self.mask(); self.paint(d, col)
    def line(self, p0, p1, col, w=1):
        n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))) + 1
        for i in range(n + 1):
            t = i / max(n, 1); x = p0[0] + (p1[0] - p0[0]) * t; y = p0[1] + (p1[1] - p0[1]) * t
            self.px(x, y, col)
            if w > 1: self.px(x + 1, y, col)
    def over(self, other):
        m = other.a[..., 3] > 0; self.a[m] = other.a[m]

def dil(m, diag=True):
    o = m.copy()
    sh = [(0, 1), (0, -1), (1, 0), (-1, 0)] + ([(1, 1), (1, -1), (-1, 1), (-1, -1)] if diag else [])
    for dy, dx in sh: o |= np.roll(np.roll(m, dy, 0), dx, 1)
    return o

def edge_in(m):
    """pixels of m touching outside (4-conn)"""
    e = np.zeros_like(m)
    for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]: e |= ~np.roll(np.roll(m, dy, 0), dx, 1)
    return m & e

# ---------------------------------------------------------------- shared shape pieces
def visible(G, F):
    """0..1 cut factor along the arc for the current frame (tail retracts with a short taper)"""
    s = G['s']; head = F['head']
    v = (s >= 0) & (s <= head)
    cut = np.clip((s - F['tail']) / 0.10, 0, 1) if F['tail'] > 0 else np.ones_like(s)
    return v, cut

def rim_width(G, F, wmin, wmax, tip=0.05):
    """thicker toward the tip (head), pointed tip, soft start"""
    s = G['s']; head = F['head']; u = np.clip(s / head, 0, 1)
    w = wmin + (wmax - wmin) * u ** 1.4
    w = w * np.clip((head - s) / tip, 0, 1) ** 0.55 * np.clip(s / 0.06, 0, 1) ** 0.6
    return w, u

def fan(G, F, st, back, r0=0.18):
    """filled fan (hitbox) behind the hero, two flat tones + inner band"""
    if F['head'] is None or F['fade'] >= 0.7: return
    v, cut = visible(G, F); r = G['r']
    rin = R * (r0 + (1 - r0) * min(1.0, F['fade'] * 1.45))   # fade: the fan collapses outward into the rim
    m = v & (r >= rin) & (r < R - 1) & (cut > 0.5)
    back.paint(m, st.fan[0])
    back.paint(m & (r > R * 0.55), st.fan[1])
    back.paint(m & (r > R * 0.80), st.fan[2])
    back.outline(st.fan_line, m, diag=False)

def afterimages(k, F, st, back):
    if F['head'] is None or F['fade'] > 0: return
    for i, ds in enumerate((0.09, 0.18, 0.27)):
        s = F['blade'] - ds
        if s < 0: break
        p0, p1 = pt(k, s, R * 0.30), pt(k, s, R - 5)
        back.line(p0, p1, st.ghost[min(i, len(st.ghost) - 1)])

def speedlines(k, F, st, L):
    if F['head'] is None or F['fade'] > 0: return
    rng = np.random.default_rng(st.seed + int(F['head'] * 100))
    for i in range(4):
        s0 = F['head'] - 0.05 - i * 0.07 - rng.random() * 0.03
        if s0 < 0.02: break
        rr = R + 3 + i % 2 * 3 + rng.integers(0, 3)
        ln = 0.05 + rng.random() * 0.05
        p0, p1 = pt(k, s0 - ln, rr), pt(k, s0, rr)
        L.line(p0, p1, st.speed if i else st.spark[0])

def sparkle(k, F, st, L):
    if F['head'] is None or F['fade'] > 0: return
    x, y = pt(k, F['head'], R - 2); big = 3 if F['head'] < 1 else 2
    c0, c1 = st.spark
    for i in range(1, big + 1):
        col = c0 if i < big else c1
        for dx, dy in ((i, 0), (-i, 0), (0, i), (0, -i)): L.px(x + dx, y + dy, col)
    L.px(x + 1, y + 1, c1); L.px(x - 1, y - 1, c1); L.px(x + 1, y - 1, c1); L.px(x - 1, y + 1, c1)
    L.px(x, y, c0)

def blade(k, F, L, behind):
    s = F['blade']; p0 = pt(k, s, R * 0.26); p1 = pt(k, s, R - 6)
    B = Layer(); B.line(p0, p1, BLADE['m'], 2)
    B.line(pt(k, s, R * 0.26), pt(k, s, R * 0.26 + 6), BLADE['d'], 2)
    B.px(*p1, BLADE['h']); B.px(*pt(k, s, R - 9), BLADE['h'])
    B.outline(BLADE['o'], diag=False)
    (behind if p1[1] < ARCS[k]['c'][1] - 6 else L).over(B)

class Particles:
    """deterministic particles; born when the head passes s_b, simulated in seconds"""
    def __init__(self, k, seed, n, srange, roff, speed, up, grav, life, kinds):
        rng = np.random.default_rng(seed); self.k = k; self.p = []
        for i in range(n):
            s = srange[0] + (srange[1] - srange[0]) * rng.random() ** 1.0
            ro = roff[0] + (roff[1] - roff[0]) * rng.random()
            nx, ny = normal_out(k, s); tx, ty = tangent(k, s)
            sp = speed[0] + (speed[1] - speed[0]) * rng.random()
            vx = nx * sp + tx * sp * 0.3 * (rng.random() - 0.3); vy = ny * sp + up * (0.5 + rng.random())
            self.p.append(dict(s=s, pos=pt(k, s, R - ro), v=(vx, vy), g=grav, life=life[0] + (life[1] - life[0]) * rng.random(),
                               kind=kinds[rng.integers(0, len(kinds))], ph=rng.random() * 6.28))
    def alive(self, fi):
        F = FRAMES[fi]
        if F['head'] is None: return
        for p in self.p:
            born = next((j for j in range(1, 8) if FRAMES[j]['head'] is not None and FRAMES[j]['head'] >= p['s']), None)
            if born is None or born > fi: continue
            age = TIMES[fi] - TIMES[born] + 0.016
            if age > p['life']: continue
            x = p['pos'][0] + p['v'][0] * age + math.sin(p['ph'] + age * 9) * 1.5 * (p['kind'] in ('ash',))
            y = p['pos'][1] + p['v'][1] * age + 0.5 * p['g'] * age * age
            yield p, x, y, age / p['life']

# ---------------------------------------------------------------- styles
class Style:
    seed = 1
    def render(self, k, fi, back, L): pass

class Ashen(Style):
    n = 1; key = 'ashen_crescent'; ko = '잿빛 초승달'; en = 'Ashen Crescent'; seed = 11
    mood = 'Cold bone-white blade-moon with a dead black heart; embers smoulder off the trailing edge like a pyre going out.'
    pal = dict(outline='#0a090c', core='#141118', core2='#2b2628', bone_d='#7f7768', bone='#b8b09b', bone_h='#e3ddcc',
               ash='#5a544c', emb_d='#7a2a10', emb='#cf5f1d', emb_h='#f19a3c',
               fan0='#1f1c1e', fan1='#252121', fan2='#2d2826', fanline='#0e0d10')
    def __init__(self):
        P = self.pal; self.fan = (P['fan0'], P['fan1'], P['fan2']); self.fan_line = P['fanline']
        self.ghost = (P['bone_d'], P['ash'], P['core2']); self.speed = P['bone_d']; self.spark = (P['bone_h'], P['emb_h'])
        self.parts = {k: Particles(k, self.seed + i, 34, (0.0, 0.55), (4, 16), (6, 22), -28, 30, (0.18, 0.45),
                                   ['e1', 'e1', 'e2']) for i, k in enumerate(ARCS)}
    def render(self, k, fi, back, L):
        P = self.pal; F = FRAMES[fi]; G = geo(k)
        if F['head'] is None:
            x, y = pt(k, F['blade'], R - 6); L.px(x, y, P['emb_h']); L.px(x + 1, y, P['emb']); L.px(x - 1, y, P['emb']); return
        fan(G, F, self, back); afterimages(k, F, self, back)
        v, cut = visible(G, F); w, u = rim_width(G, F, 5, 20)
        w = w * cut * (1 - 0.45 * F['fade'])
        d = R - G['r']; vv = d / np.maximum(w, 1e-3)
        m = v & (d >= 0) & (d < w) & (w > 0.7)
        if F['fade'] > 0: m &= snoise(4, self.seed) > F['fade'] * 0.75 * (0.6 + vv)
        hi = P['bone_h'] if F['fade'] < 0.3 else P['bone']
        L.paint(m, P['core']); L.paint(m & (vv < 0.62), P['core2'])
        L.paint(m & (vv < 0.50), P['bone_d'] if F['fade'] < 0.6 else P['ash'])
        L.paint(m & (vv < 0.36), P['bone'] if F['fade'] < 0.6 else P['bone_d'])
        L.paint(m & (vv < 0.14) & (u > 0.45), hi)                       # tip side brighter
        tailz = m & (u < 0.32) & (vv < 0.5) & (bnoise(1, 5) < 0.45)
        L.paint(tailz, P['ash'])                                         # charred trailing end
        L.paint(m & (u < 0.4) & (vv > 0.45) & (bnoise(1, 6) > 0.86), P['emb'])  # ember specks in the core
        L.outline(P['outline'])
        for p, x, y, a in self.parts[k].alive(fi):
            c = P['emb_h'] if a < 0.35 else P['emb'] if a < 0.7 else P['emb_d']
            L.px(x, y, c)
            if p['kind'] == 'e2' and a < 0.6: L.px(x + 1, y, P['emb_d'])
        speedlines(k, F, self, L); sparkle(k, F, self, L)

class Abyss(Style):
    n = 2; key = 'abyss_rift'; ko = '심연 균열'; en = 'Abyss Rift'; seed = 22
    mood = 'The swing does not cut the air, it tears it: a black wound in space edged with violet, leaking void shards.'
    pal = dict(void='#030206', star='#2a1b52', rim_d='#2b1d63', rim='#5d3ba3', rim_h='#9a6fe6', shard_h='#c9adff',
               outline='#120c26', fan0='#0f0b18', fan1='#130d20', fan2='#191029', fanline='#07050c')
    def __init__(self):
        P = self.pal; self.fan = (P['fan0'], P['fan1'], P['fan2']); self.fan_line = P['fanline']
        self.ghost = (P['rim'], P['rim_d'], P['star']); self.speed = P['rim_d']; self.spark = (P['shard_h'], P['rim'])
        self.parts = {k: Particles(k, self.seed + i, 30, (0.05, 1.0), (-4, 22), (14, 40), -6, -4, (0.25, 0.6),
                                   ['dot', 'h2', 'v2', 'dia']) for i, k in enumerate(ARCS)}
        rng = np.random.default_rng(self.seed); self.jo = rng.random(64); self.ji = rng.random(64)
    def render(self, k, fi, back, L):
        P = self.pal; F = FRAMES[fi]; G = geo(k)
        if F['head'] is None:
            x, y = pt(k, F['blade'], R - 6); L.px(x, y, P['void'])
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): L.px(x + dx, y + dy, P['rim_h'])
            return
        fan(G, F, self, back)
        stars = (bnoise(1, 9) > 0.985) & (G['r'] < R - 2) & (G['r'] > R * 0.3) & visible(G, F)[0] & (F['fade'] < 0.5)
        back.paint(stars, P['star']); afterimages(k, F, self, back)
        v, cut = visible(G, F); w, u = rim_width(G, F, 4, 18, tip=0.07)
        w = w * cut * max(0.0, 1 - F['fade']) ** 1.2
        idx = np.clip((G['s'] * 63).astype(int), 0, 63)
        hw = w / 2; rc = R - hw - 1
        jo = 0.6 + 0.8 * self.jo[idx]; ji = 0.6 + 0.8 * self.ji[idx]   # jagged tear edges
        d = G['r'] - rc
        m = v & (((d >= 0) & (d < hw * jo)) | ((d < 0) & (-d < hw * ji))) & (w > 0.8)
        L.paint(m, P['void'])
        e = edge_in(m)
        L.paint(e, P['rim']); L.paint(e & (d > 0) & (u > 0.55), P['rim_h'])          # bright outer rim on tip side
        L.paint(m & ~e & (bnoise(1, 4) > 0.97), P['star'])
        # closing seam
        if 0 < F['fade'] < 0.9:
            seam = v & (np.abs(G['r'] - (R - 2)) < 0.7) & (cut > 0) & ~m
            L.paint(seam, P['rim_d'])
        L.outline(P['outline'])
        for p, x, y, a in self.parts[k].alive(fi):
            c = P['shard_h'] if a < 0.3 else P['rim_h'] if a < 0.65 else P['rim']
            L.px(x, y, c)
            if p['kind'] == 'h2': L.px(x + 1, y, P['rim_d'])
            if p['kind'] == 'v2': L.px(x, y + 1, P['rim_d'])
            if p['kind'] == 'dia' and a < 0.7:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): L.px(x + dx, y + dy, P['rim'])
                L.px(x, y, P['shard_h'])
        speedlines(k, F, self, L); sparkle(k, F, self, L)

class BloodInk(Style):
    n = 3; key = 'blood_ink'; ko = '혈묵'; en = 'Blood Ink'; seed = 33
    mood = 'One sumi-e stroke in blood: heavy brush landing, dry-brush (kasure) tail, splatter flicked off the end.'
    pal = dict(edge='#1c0408', dark='#420810', body='#6b0e16', sheen='#93202a', dry='#2c060b',
               fan0='#1f1015', fan1='#251217', fan2='#2c1419', fanline='#0f0508')
    def __init__(self):
        P = self.pal; self.fan = (P['fan0'], P['fan1'], P['fan2']); self.fan_line = P['fanline']
        self.ghost = (P['dark'], P['dry'], P['dry']); self.speed = P['dark']; self.spark = (P['sheen'], P['body'])
        rng = np.random.default_rng(self.seed); self.cuts = 0.62 + 0.36 * rng.random(9); self.scut = 0.06 * rng.random(9)
        self.splat = {}
        for i, k in enumerate(ARCS):
            r2 = np.random.default_rng(self.seed + 10 + i); lst = []
            for j in range(18):
                s = 0.45 + 0.6 * r2.random() ** 0.6; s = min(s, 1.04)
                lst.append(dict(s=s, off=3 + 16 * r2.random() ** 1.5, rad=[0, 0, 1, 1, 1.5, 2.2][r2.integers(0, 6)],
                                along=(r2.random() - 0.5) * 0.04))
            self.splat[k] = lst
    def render(self, k, fi, back, L):
        P = self.pal; F = FRAMES[fi]; G = geo(k)
        if F['head'] is None:
            x, y = pt(k, F['blade'], R - 6); L.px(x, y, P['sheen']); L.px(x, y + 1, P['body']); L.px(x, y + 2, P['dark']); return
        fan(G, F, self, back); afterimages(k, F, self, back)
        s = G['s']; head = F['head']; v, cut = visible(G, F)
        # brush: blunt heavy landing, thick body, harai taper only at the end of the full swing
        w = 22 * np.clip(s / 0.07, 0, 1) ** 0.45
        w = w * (0.55 + 0.45 * np.clip(s / max(head, 1e-3), 0, 1))           # tip side thicker
        w = w * np.clip((1.0 - s) / 0.30, 0, 1) ** 0.7 * (1 if head >= 1 else 1) + 0 * s
        if head < 1:   # rounded wet head while moving
            w = 22 * np.clip(s / 0.07, 0, 1) ** 0.45 * (0.55 + 0.45 * np.clip(s / head, 0, 1))
            capm = s > head - 0.05
            w = np.where(capm, w * np.sqrt(np.clip(1 - ((s - (head - 0.05)) / 0.05) ** 2, 0, 1)), w)
        w = w * cut
        rc = R - 1 - w / 2 + 2 * np.sin(np.clip(s, 0, 1) * math.pi)
        d = G['r'] - rc; vv = d / np.maximum(w / 2, 1e-3)    # -1 inner .. 1 outer
        m = v & (np.abs(d) < w / 2) & (w > 1.0)
        b = np.clip(((vv + 1) / 2 * 9).astype(int), 0, 8)
        cutb = self.cuts[b] - (1 - head) * 0  # kasure streaks near the end
        gaps = (s > cutb) & (bnoise(2, 3) > 0.35) & (head >= 1 - 1e-6)
        gaps |= (s < self.scut[b]) & (bnoise(2, 8) > 0.5)
        m &= ~gaps
        if F['fade'] > 0.5: m &= snoise(4, self.seed) > (F['fade'] - 0.45) * 1.6
        body = P['body'] if F['fade'] < 0.5 else P['dark']
        L.paint(m, body)
        L.paint(m & (b % 3 == 1), P['dark'])                                       # bristle lines
        L.paint(m & (vv > 0.25) & (vv < 0.55) & (s > 0.35) & (F['fade'] < 0.25), P['sheen'])   # wet sheen tip side
        L.paint(edge_in(m), P['edge'])
        # splatter
        if F['fade'] < 0.95:
            for sp in self.splat[k]:
                if sp['s'] > head + 0.02: continue
                ss = min(sp['s'] + sp['along'], 1.06)
                x, y = pt(k, ss, R + sp['off'] - 6)
                rr = sp['rad'] * (1 if F['fade'] < 0.6 else 0.7)
                S = Layer()
                if rr <= 0.5: S.px(x, y, P['body'] if F['fade'] < 0.5 else P['dark'])
                else:
                    mm = (XX - x) ** 2 + (YY - y) ** 2 <= rr * rr + 0.6
                    S.paint(mm, body); S.paint(edge_in(mm), P['edge'])
                L.over(S)
        speedlines(k, F, self, L); sparkle(k, F, self, L)

class Steel(Style):
    n = 4; key = 'shattered_steel'; ko = '파쇄 강철'; en = 'Shattered Steel'; seed = 44
    mood = 'A cold hairline of tempered steel that cracks and rains down as angular shards, like a blade snapping in the dark.'
    pal = dict(outline='#0f1318', shadow='#45515e', body='#6d7d8d', hi='#a8b5c1', glint='#dce3ea',
               fan0='#1a1f27', fan1='#1d232c', fan2='#222933', fanline='#0b0e12')
    def __init__(self):
        P = self.pal; self.fan = (P['fan0'], P['fan1'], P['fan2']); self.fan_line = P['fanline']
        self.ghost = (P['body'], P['shadow'], P['shadow']); self.speed = P['shadow']; self.spark = (P['glint'], P['hi'])
        rng = np.random.default_rng(self.seed)
        self.cuts = np.sort(np.concatenate([[0.0], rng.uniform(0.04, 0.97, 15), [1.0]]))
        self.frag = []
        for i in range(len(self.cuts) - 1):
            self.frag.append(dict(thr=0.08 + 0.75 * (i / 16) + 0.1 * rng.random(), vx=(rng.random() - 0.5) * 30,
                                  vy=-10 - 20 * rng.random(), spin=rng.choice([-1, 1]) * (2 + 4 * rng.random()),
                                  split=0.3 + 0.4 * rng.random(), j=rng.random()))
    def segpoly(self, k, s0, s1, w0, w1, frac):
        a = pt(k, s0, R - 1); b = pt(k, s1, R - 1); c = pt(k, s1, R - 1 - w1); d = pt(k, s0, R - 1 - w0)
        m = pt(k, s0 + (s1 - s0) * frac, R - 1 + 2)   # angular spike on outer edge
        return [a, m, b, c, d]
    def render(self, k, fi, back, L):
        P = self.pal; F = FRAMES[fi]; G = geo(k)
        if F['head'] is None:
            x, y = pt(k, F['blade'], R - 6); L.px(x, y, P['glint']); L.px(x - 1, y - 1, P['hi']); L.px(x + 1, y + 1, P['hi']); return
        fan(G, F, self, back)
        # cold radial streaks inside the fan
        if F['fade'] < 0.5:
            vv_, _ = visible(G, F)
            back.paint(vv_ & (np.mod(G['s'] * 40, 1) < 0.06) & (G['r'] > R * 0.6) & (G['r'] < R - 3), self.pal['fan2'])
        afterimages(k, F, self, back)
        v, _ = visible(G, {**F, 'tail': 0}); w, u = rim_width(G, F, 2, 6, tip=0.08)
        d = R - 1 - G['r']; vv = d / np.maximum(w, 1e-3)
        m = v & (d >= 0) & (d < w) & (w > 0.6)
        # cracks + broken segments
        for i in range(len(self.cuts) - 1):
            s0, s1 = self.cuts[i], self.cuts[i + 1]; fr = self.frag[i]
            if F['fade'] > 0:
                m &= ~((G['s'] > s1 - 0.004 * (1 + 6 * F['fade'])) & (G['s'] < s1 + 0.004 * (1 + 6 * F['fade'])))
            if F['fade'] > fr['thr']:
                m &= ~((G['s'] >= s0) & (G['s'] < s1))
        L.paint(m, P['body']); L.paint(m & (vv > 0.6), P['shadow']); L.paint(m & (vv < 0.3), P['hi'])
        L.paint(m & (vv < 0.3) & (u > 0.8), P['glint'])
        # falling fragments
        img = Image.new('L', (N, N), 0); dr = ImageDraw.Draw(img)
        for i in range(len(self.cuts) - 1):
            fr = self.frag[i]
            if not (F['fade'] > fr['thr']): continue
            s0, s1 = self.cuts[i], self.cuts[i + 1]
            age = (F['fade'] - fr['thr']) * 0.55
            sm = s0 + (s1 - s0) * fr['split']
            wa = 2 + 4 * s0 ** 1.4; wb = 2 + 4 * s1 ** 1.4
            for half, (a0, a1) in enumerate(((s0, sm), (sm, s1))):
                poly = self.segpoly(k, a0, a1, wa, wb, fr['j'])
                cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
                ang = math.radians(round(fr['spin'] * age * 40 / 22.5) * 22.5 * (1 if half else -1))
                ox = (fr['vx'] + (6 if half else -6)) * age; oy = fr['vy'] * age + 0.5 * 260 * age * age
                q = [(cx + ox + (x - cx) * math.cos(ang) - (y - cy) * math.sin(ang),
                      cy + oy + (x - cx) * math.sin(ang) + (y - cy) * math.cos(ang)) for x, y in poly]
                if age < 0.35: dr.polygon(q, fill=1)
        fm = np.array(img) > 0
        L.paint(fm, P['body']); top = fm & ~np.roll(fm, 1, 0); L.paint(top, P['hi'])
        L.paint(fm & ~np.roll(fm, -1, 0), P['shadow'])
        L.outline(P['outline'])
        # sparks at fresh breaks
        for i in range(len(self.cuts) - 1):
            fr = self.frag[i]
            if 0 < F['fade'] - fr['thr'] < 0.2:
                x, y = pt(k, self.cuts[i + 1], R - 2); L.px(x, y - 2, P['glint']); L.px(x + 2, y - 3, P['hi'])
        speedlines(k, F, self, L); sparkle(k, F, self, L)

class Wraith(Style):
    n = 5; key = 'wraith_smoke'; ko = '망령 연기'; en = 'Wraith Smoke'; seed = 55
    mood = 'Grave-smoke dragged behind the blade with a thin ghost-light thread inside; it curls upward and is gone.'
    pal = dict(outline='#0a0b0f', smoke_d='#1f222b', smoke='#2c303c', smoke_l='#3e4353', core_g='#8b96a6', core='#d6dee8',
               fan0='#1d1f26', fan1='#21242c', fan2='#262a33', fanline='#0e0f13')
    def __init__(self):
        P = self.pal; self.fan = (P['fan0'], P['fan1'], P['fan2']); self.fan_line = P['fanline']
        self.ghost = (P['core_g'], P['smoke_l'], P['smoke']); self.speed = P['smoke_l']; self.spark = (P['core'], P['core_g'])
        self.parts = {k: Particles(k, self.seed + i, 16, (0.08, 0.95), (-2, 10), (4, 12), -34, -10, (0.25, 0.6),
                                   ['puff']) for i, k in enumerate(ARCS)}
    def render(self, k, fi, back, L):
        P = self.pal; F = FRAMES[fi]; G = geo(k); t = TIMES[fi]
        if F['head'] is None:
            x, y = pt(k, F['blade'], R - 6); L.px(x, y, P['core']); L.px(x, y - 1, P['core_g']); L.px(x, y - 2, P['smoke_l']); return
        fan(G, F, self, back); afterimages(k, F, self, back)
        v, cut = visible(G, F); w, u = rim_width(G, F, 6, 22, tip=0.06)
        w = w * np.maximum(cut, 0) * (1 + 0.25 * F['fade'])
        n1 = snoise(5, self.seed, (0, t * 60)); n2 = snoise(3, self.seed + 1, (t * 20, t * 90))
        d = R - G['r'] + (n1 - 0.5) * 9 * (0.3 + u)
        vv = d / np.maximum(w, 1e-3)
        m = v & (d >= 0) & (d < w) & (w > 0.8)
        m &= n2 > 0.12 + F['fade'] * 0.85 + np.where(u < 0.25, 0.25 - u, 0)
        S = Layer()
        S.paint(m, P['smoke']); S.paint(m & (vv > 0.6), P['smoke_d']); S.paint(m & (vv < 0.3), P['smoke_l'])
        S.paint(m & (n2 > 0.78) & (vv < 0.7), P['smoke_l'])
        for p, x, y, a in self.parts[k].alive(fi):     # rising wisps
            rr = 1.5 + 3 * a
            if a > 0.85: continue
            mm = ((XX - x) ** 2 + ((YY - y) * 1.3) ** 2 <= rr * rr) & (n2 > 0.2 + 0.6 * a)
            S.paint(mm & ~S.mask(), P['smoke']); S.paint(mm & (YY < y - rr * 0.3) & (S.mask()), P['smoke_l'])
        S.outline(P['outline'])
        L.over(S)
        if F['fade'] < 0.6:   # ghost core thread
            dc = R - 3 - (1 - u) * 6
            core = v & (np.abs(G['r'] - dc) < 0.75) & (u > 0.12) & (cut > 0.3)
            if F['fade'] > 0: core &= bnoise(2, 77) > F['fade'] * 1.3
            L.paint(dil(core, False) & L.mask() & ~core, P['core_g'])
            L.paint(core, P['core'] if F['fade'] < 0.3 else P['core_g'])
        speedlines(k, F, self, L); sparkle(k, F, self, L)

class Gilt(Style):
    n = 6; key = 'dusk_gilt'; ko = '황혼 금선'; en = 'Dusk Gilt'; seed = 66
    mood = 'A tired gold hairline, the colour of the hero\'s tarnished trim, shedding ash and a few last embers at dusk.'
    pal = dict(outline='#1c170c', g_d='#6b5a2e', g='#8a7340', g_h='#a08a55', g_tip='#c2a96e',
               ash_d='#3a3835', ash='#5a5650', ash_l='#7e786d', emb_d='#6a3214', emb='#b8682a', emb_h='#e0a050',
               fan0='#1c1c1d', fan1='#201f1d', fan2='#26231d', fanline='#0e0d0b')
    def __init__(self):
        P = self.pal; self.fan = (P['fan0'], P['fan1'], P['fan2']); self.fan_line = P['fanline']
        self.ghost = (P['g_d'], P['ash_d'], P['ash_d']); self.speed = P['g_d']; self.spark = (P['g_tip'], P['g'])
        self.parts = {k: Particles(k, self.seed + i, 44, (0.0, 1.0), (-3, 8), (3, 12), -16, -6, (0.35, 0.8),
                                   ['ash', 'ash', 'ash', 'ash', 'ember']) for i, k in enumerate(ARCS)}
    def render(self, k, fi, back, L):
        P = self.pal; F = FRAMES[fi]; G = geo(k)
        if F['head'] is None:
            x, y = pt(k, F['blade'], R - 6); L.px(x, y, P['g_tip']); L.px(x + 1, y, P['g']); L.px(x, y + 1, P['g_d']); return
        fan(G, F, self, back); afterimages(k, F, self, back)
        v, cut = visible(G, F); w, u = rim_width(G, F, 1.0, 3.6, tip=0.06)
        d = R - 1 - G['r']; vv = d / np.maximum(w, 1e-3)
        m = v & (d >= 0) & (d < w) & (w > 0.5) & (cut > 0.5)
        dash = (np.mod(G['s'] * 90, 1) < 0.45)
        m &= ~(dash & (u < 0.3 + F['fade']))                  # line breaks into dashes from the tail
        if F['fade'] > 0: m &= snoise(3, 12) > F['fade'] * 0.75
        g0 = P['g'] if F['fade'] < 0.5 else P['g_d']
        L.paint(m, g0); L.paint(m & (vv < 0.4) & (u > 0.3), P['g_h'] if F['fade'] < 0.3 else P['g'])
        L.paint(m & (vv > 0.66), P['g_d'])
        L.paint(m & (u > 0.9) & (vv < 0.5) & (F['fade'] == 0), P['g_tip'])
        L.outline(P['outline'], diag=False)
        for p, x, y, a in self.parts[k].alive(fi):
            if p['kind'] == 'ash':
                c = P['ash_l'] if a < 0.3 else P['ash'] if a < 0.7 else P['ash_d']
                L.px(x, y, c)
                if int(p['ph'] * 10) % 3 == 0: L.px(x + 1, y, P['ash_d'])
            else:
                c = P['emb_h'] if a < 0.35 else P['emb'] if a < 0.7 else P['emb_d']
                L.px(x, y - a * 8, c)
        speedlines(k, F, self, L); sparkle(k, F, self, L)

STYLES = [Ashen(), Abyss(), BloodInk(), Steel(), Wraith(), Gilt()]

# ---------------------------------------------------------------- composition
def ground():
    g = Layer(); g.paint(np.ones((N, N), bool), BG)
    n = bnoise(2, 999); g.paint(n > 0.93, BG3); g.paint(n < 0.06, BG2)
    sh = ((XX - 132) / 22) ** 2 + ((YY - 191) / 5) ** 2 <= 1; g.paint(sh, SHADOW)
    return g

def hero_sprite():
    h = np.array(Image.open(HERO).convert('RGBA'))
    h[134:, 146:] = 0          # remove the hanging blade; the swinging blade is drawn per frame
    L = Layer(); L.a = h; return L

GROUND = ground(); HSPR = hero_sprite()
BEHIND_S = {'A3': 0.32}   # overhead slam: wind-up part of the arc passes behind the head

def frame(st, k, fi, with_hero=True):
    back, front = Layer(), Layer()
    st.render(k, fi, back, front)
    bs = BEHIND_S.get(k)
    if bs is not None:
        mv = (front.a[..., 3] > 0) & (geo(k)['s'] < bs) & (YY < 100)
        back.a[mv] = front.a[mv]; front.a[mv] = 0
    blade(k, FRAMES[fi], front, back)
    out = Layer(); out.a = GROUND.a.copy(); out.over(back)
    if with_hero: out.over(HSPR)
    out.over(front)
    return out.a

CROP = (40, 30, 232, 222)   # 192x192 action window
def crop(a, sc):
    im = Image.fromarray(a, 'RGBA').crop(CROP).convert('RGB')
    return im.resize((im.width * sc, im.height * sc), Image.NEAREST)

def save_gif(frames, delays, path):
    allc = np.unique(np.concatenate([np.array(f).reshape(-1, 3) for f in frames]), axis=0)
    if len(allc) <= 256:
        pal = Image.new('P', (1, 1)); flat = list(allc.flatten()) + [0] * (768 - allc.size); pal.putpalette(flat)
        ps = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    else:
        big = Image.new('RGB', (frames[0].width, frames[0].height * len(frames)))
        for i, f in enumerate(frames): big.paste(f, (0, i * f.height))
        pal = big.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        ps = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=delays, loop=0, disposal=1, optimize=False)
    return len(allc)

def font(sz, bold=True):
    for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc' % ('Bold' if bold else 'Regular'), '/home/box/.fonts/NotoSansKR.ttf']:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz, index=1) if p.endswith('.ttc') else ImageFont.truetype(p, sz)
            except Exception: pass
    return ImageFont.load_default()

def hit_seq():
    seq, dl = [], []
    for k in ARCS:
        for fi in range(8):
            seq.append((k, fi)); dl.append(DELAYS[fi])
        dl[-1] = 150
    dl[-1] = 400
    return seq, dl

def main():
    seq, dl = hit_seq(); info = {}
    rendered = {}
    for st in STYLES:
        for k, fi in seq: rendered[(st.n, k, fi)] = frame(st, k, fi)
    for st in STYLES:
        frs = [crop(rendered[(st.n, k, fi)], 3) for k, fi in seq]
        p = os.path.join(HERE, 'style_%d_%s.gif' % (st.n, st.key)); info[st.n] = save_gif(frs, dl, p)
        # native-scale sheets (for implementation): rows A1/A2/A3, 8 frames each, 256 canvas, transparent trail only
        sheet = Image.new('RGBA', (N * 8, N * 3))
        for r, k in enumerate(ARCS):
            for fi in range(8):
                back, front = Layer(), Layer(); st.render(k, fi, back, front); blade(k, FRAMES[fi], front, back)
                b = Layer(); b.over(back); b.over(front)
                sheet.paste(Image.fromarray(b.a, 'RGBA'), (fi * N, r * N))
        sheet.save(os.path.join(HERE, 'style_%d_%s_sheet_native.png' % (st.n, st.key)))
    # combined gif 3x2
    sc = 2; cw = (CROP[2] - CROP[0]) * sc; chh = (CROP[3] - CROP[1]) * sc; lab = 34
    f1 = font(20); f2 = font(13, False)
    allf = []
    for k, fi in seq:
        im = Image.new('RGB', (cw * 3, (chh + lab) * 2), hx('#0c0d10')[:3]); dr = ImageDraw.Draw(im); dr.fontmode = '1'
        for i, st in enumerate(STYLES):
            x, y = (i % 3) * cw, (i // 3) * (chh + lab)
            im.paste(crop(rendered[(st.n, k, fi)], sc), (x, y + lab))
            dr.text((x + 10, y + 6), '%d. %s' % (st.n, st.ko), font=f1, fill=(214, 206, 188))
            dr.text((x + 10 + dr.textlength('%d. %s' % (st.n, st.ko), font=f1) + 10, y + 12), st.en, font=f2, fill=(130, 126, 118))
            dr.text((x + cw - 40, y + 12), {'A1': 'HIT1', 'A2': 'HIT2', 'A3': 'HIT3'}[k], font=f2, fill=(110, 104, 96))
        allf.append(im)
    info['all'] = save_gif(allf, dl, os.path.join(HERE, 'slash_designs_all.gif'))
    # board
    KEY = [0, 1, 2, 3, 5, 6]; sc = 2; cw = (CROP[2] - CROP[0]) * sc; ch = (CROP[3] - CROP[1]) * sc
    labw = 330; gap = 36; head = 70; rowh = ch + 34
    W = labw + len(KEY) * cw + gap + 3 * cw + 20
    board = Image.new('RGB', (W, head + rowh * 6 + 10), hx('#0c0d10')[:3]); dr = ImageDraw.Draw(board)
    dr.text((20, 14), '사멸의 궤적 — 주인공 검흔/검기 다크 디자인 6종 (Trail of Extinction · dark slash trail proposals)', font=font(26), fill=(222, 214, 196))
    names = ['예비동작 anticipation', '휘두름 1 swipe', '휘두름 2 swipe', '완성 궤적 full', '소멸 1 fade', '소멸 2 fade']
    fs = font(14, False)
    for i, nm in enumerate(names): dr.text((labw + i * cw + 6, head - 22), nm, font=fs, fill=(140, 134, 124))
    for i, nm in enumerate(['1타 가로베기 A1 (140°)', '2타 역사선 A2 (140°)', '3타 내려찍기 A3 (170°)']):
        dr.text((labw + len(KEY) * cw + gap + i * cw + 6, head - 22), nm, font=fs, fill=(160, 150, 120))
    fL = font(30); fE = font(16); fM = font(13, False)
    for r, st in enumerate(STYLES):
        y = head + r * rowh
        dr.rectangle([8, y, W - 8, y + rowh - 6], outline=(40, 42, 50))
        dr.text((22, y + 18), '%d. %s' % (st.n, st.ko), font=fL, fill=(226, 218, 200))
        dr.text((24, y + 62), st.en, font=fE, fill=(150, 144, 132))
        # palette swatches
        cols = [c for kk, c in st.pal.items() if not kk.startswith('fan')][:12]
        for j, c in enumerate(cols):
            xx = 24 + (j % 6) * 46; yy = y + 100 + (j // 6) * 54
            dr.rectangle([xx, yy, xx + 38, yy + 30], fill=hx(c)[:3], outline=(70, 70, 76))
            dr.text((xx, yy + 33), c, font=font(11, False), fill=(120, 116, 110))
        # mood (wrapped)
        words = st.mood.split(); line = ''; ly = y + 222
        for wd in words:
            if dr.textlength(line + ' ' + wd, font=fM) > labw - 40:
                dr.text((24, ly), line.strip(), font=fM, fill=(120, 116, 108)); ly += 18; line = ''
            line += ' ' + wd
        dr.text((24, ly), line.strip(), font=fM, fill=(120, 116, 108))
        for i, fi in enumerate(KEY): board.paste(crop(rendered[(st.n, 'A1', fi)], sc), (labw + i * cw, y + 14))
        for i, k in enumerate(ARCS): board.paste(crop(rendered[(st.n, k, 3)], sc), (labw + len(KEY) * cw + gap + i * cw, y + 14))
        dr.line([labw + len(KEY) * cw + gap // 2, y + 14, labw + len(KEY) * cw + gap // 2, y + 14 + ch], fill=(60, 56, 50), width=2)
    board.save(os.path.join(HERE, 'slash_designs_board.png'))
    print('unique colours per gif:', info)

if __name__ == '__main__':
    main()
