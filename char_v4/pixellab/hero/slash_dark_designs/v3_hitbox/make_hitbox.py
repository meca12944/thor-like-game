#!/usr/bin/env python3
"""사멸의 궤적 — dark slash trails v3: hitbox-exact, NATIVE game pixel scale.
Design preview only. Reads hero frames from ./hero_ref (extracted read-only from the main clone hero8 atlas);
writes only into this folder. No game code / assets touched.

Units: 1 px = 1 field (logical) px of the 384x216 game screen. Hero figure = H128FIG 30 px (atlas 117 px fig -> x30/117).
Origin of every spec = hero FEET (hero.x, hero.y), +x = facing (east), +y = down (screen).
"""
import os, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'hero_ref')
K3 = 3                                   # game display scale used for previews (384x216 -> 1152x648)
H128FIG = 30; ATLAS_FIG = 117            # world.js L1128 / L1187: sc = k*H128FIG/117
HSC = H128FIG / ATLAS_FIG

# ---------------------------------------------------------------- game numbers (main test128/world.js @9bd16684)
GK_REACH = [32, 30, 37]                  # L1214 field px per hit
SWEEP_K = 0.7                            # research README: body-centred sweep radius = reach*0.7
ARC_DEG = [140, 140, 170]                # research / GK span (L1193); code GK_ARC = 130/143/156 (cosA, unused by gkTouch)
TICK = 1 / 60
ATK = dict(dur=16, a0=3, a1=10)          # L45 ATK {dur .26, a0 .05, a1 .16} s -> 60fps ticks
ATK3 = dict(dur=23, a0=4, a1=14)         # L46 ATK3 {dur .38, a0 .07, a1 .24}
GROUND_SQ = 0.8                          # L809 field hit test: ddy / .8 (ground-plane squash)
BODY_DY = -13                            # body centre above feet: GK side origin (-78+27 atlas) * 30/117 = -13.1 (L1193/L1231)
FADE_T = 10                              # visual fade after the active window (no hit)

# ---------------------------------------------------------------- native window
W, H = 76, 64
FX, FY = 26, 54                          # hero feet on the native canvas
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
PX, PY = XX + 0.5 - FX, YY + 0.5 - FY    # pixel centres relative to the feet

def hx(c):
    c = c.lstrip('#'); return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)
BG = '#1a1c22'; BG2 = '#16181d'; BG3 = '#1e2128'; SHADOW = '#111217'

# ---------------------------------------------------------------- hitbox shapes
class Arc:
    """filled elliptical fan: centre c (feet-relative), radius R along the facing axis, ry = R*sq, rotated rot deg.
    hit(p) = r <= R and angle within [a0, a1] (sweep a0 -> a1). r measured in the un-squashed frame."""
    kind = 'arc'
    def __init__(s, name, c, R, sq, rot, a0, a1):
        s.name, s.c, s.R, s.sq, s.rot, s.a0, s.a1 = name, c, R, sq, rot, a0, a1
        s.g = s.geo(PX, PY)
    def geo(s, px, py):
        t = math.radians(s.rot); dx, dy = px - s.c[0], py - s.c[1]
        qx = dx * math.cos(t) + dy * math.sin(t); qy = (-dx * math.sin(t) + dy * math.cos(t)) / s.sq
        r = np.hypot(qx, qy); th = np.degrees(np.arctan2(qy, qx)); sp = (th - s.a0) / (s.a1 - s.a0)
        inside = (r <= s.R) & (sp >= 0) & (sp <= 1)
        return dict(s=sp, e=s.R - r, fr=r / s.R, inside=inside)
    def pt(s, sv, off=0.0):          # point at sweep fraction sv, 'off' px inside the outer rim (neg = outside)
        th = math.radians(s.a0 + sv * (s.a1 - s.a0)); t = math.radians(s.rot); rr = s.R - off
        qx, qy = rr * math.cos(th), rr * math.sin(th) * s.sq
        return (FX + s.c[0] + qx * math.cos(t) - qy * math.sin(t), FY + s.c[1] + qx * math.sin(t) + qy * math.cos(t))
    def nrm(s, sv):
        p = s.pt(sv); c = (FX + s.c[0], FY + s.c[1]); d = (p[0] - c[0], p[1] - c[1]); l = math.hypot(*d) or 1; return (d[0] / l, d[1] / l)
    def tan(s, sv):
        p0, p1 = s.pt(sv - .01), s.pt(sv + .01); d = (p1[0] - p0[0], p1[1] - p0[1]); l = math.hypot(*d) or 1; return (d[0] / l, d[1] / l)
    def spec(s):
        return dict(shape='elliptic_fan', origin_from_feet=list(s.c), radius_R=round(s.R, 2), rx=round(s.R, 2), ry=round(s.R * s.sq, 2),
                    squash_y=s.sq, rot_deg=s.rot, angle_from_deg=s.a0, angle_to_deg=s.a1, arc_deg=abs(s.a1 - s.a0),
                    filled_from_r=0, rim_at_r=round(s.R, 2),
                    rule='p in hitbox <=> r(p) <= R and angle(p) in sweep; r,angle measured after un-rotating by rot and dividing y by squash')

class Band:
    """straight band (oriented rectangle) from P0 to P1 (sweep direction), full width Wd."""
    kind = 'band'
    def __init__(s, name, p0, p1, Wd):
        s.name, s.p0, s.p1, s.Wd = name, p0, p1, Wd
        d = (p1[0] - p0[0], p1[1] - p0[1]); s.L = math.hypot(*d); s.t = (d[0] / s.L, d[1] / s.L)
        n = (-s.t[1], s.t[0]); s.n = n if n[1] < 0 else (-n[0], -n[1])     # normal pointing up
        s.g = s.geo(PX, PY)
    def geo(s, px, py):
        dx, dy = px - s.p0[0], py - s.p0[1]
        sp = (dx * s.t[0] + dy * s.t[1]) / s.L; dd = dx * s.n[0] + dy * s.n[1]
        inside = (sp >= 0) & (sp <= 1) & (np.abs(dd) <= s.Wd / 2)
        return dict(s=sp, e=2 * np.abs(dd), fr=1 - np.abs(dd) / (s.Wd / 2), inside=inside, d=dd)
    def pt(s, sv, off=0.0):
        return (FX + s.p0[0] + s.t[0] * s.L * sv - s.n[0] * off * .35, FY + s.p0[1] + s.t[1] * s.L * sv - s.n[1] * off * .35)
    def nrm(s, sv): return s.n
    def tan(s, sv): return s.t
    def spec(s):
        return dict(shape='band', p_start_from_feet=[round(v, 2) for v in s.p0], p_end_from_feet=[round(v, 2) for v in s.p1],
                    length=round(s.L, 2), width=s.Wd, dir_deg=round(math.degrees(math.atan2(s.t[1], s.t[0])), 1),
                    rule='p in hitbox <=> 0 <= along <= length and |across| <= width/2 (along measured from p_start)')

R1, R2, R3 = [GK_REACH[i] * SWEEP_K for i in range(3)]
O = (0.0, float(BODY_DY))
SH = dict(
    H1=Arc('H1', O, R1, GROUND_SQ, 0.0, -ARC_DEG[0] / 2, ARC_DEG[0] / 2),             # 1타 가로베기: top -> bottom
    H2=Arc('H2', O, R2, GROUND_SQ, -15.0, ARC_DEG[1] / 2, -ARC_DEG[1] / 2),            # 2타 되베기: bottom -> top, tilted 15
    V=Arc('V', (2.0, -16.0), R3, GROUND_SQ, 0.0, -100.0, 70.0),                         # 3타 내려베기: rx=R, ry=.8R, 170
)
# X: two diagonal bands crossing at C (forward of the body centre); both inside reach R3 of O (corners included)
XW = 6.0; XC = (12.0, float(BODY_DY)); XPHI = math.radians(35)   # band width, cross point, tilt from vertical
def x_len():
    lo, hi = 1.0, 40.0
    for _ in range(60):
        L = (lo + hi) / 2; ok = True
        for sgn in (1, -1):
            dvec = (math.sin(XPHI) * sgn, math.cos(XPHI)); n = (-dvec[1], dvec[0])
            for a in (-1, 1):
                for b in (-1, 1):
                    x = XC[0] + dvec[0] * L / 2 * a + n[0] * XW / 2 * b - O[0]; y = XC[1] + dvec[1] * L / 2 * a + n[1] * XW / 2 * b - O[1]
                    if math.hypot(x, y) > R3: ok = False
        lo, hi = (L, hi) if ok else (lo, L)
    return lo
XL = x_len()
def band(sgn, rev):
    dvec = (math.sin(XPHI) * sgn, math.cos(XPHI))
    a = (XC[0] - dvec[0] * XL / 2, XC[1] - dvec[1] * XL / 2); b = (XC[0] + dvec[0] * XL / 2, XC[1] + dvec[1] * XL / 2)
    return (b, a) if rev else (a, b)
SH['XA'] = Band('XA', *band(-1, False), XW)      # '/' : top-right -> bottom-left
SH['XB'] = Band('XB', *band(1, False), XW)       # '\' : top-left  -> bottom-right

# timeline per segment (game ticks @60fps). strokes: (shape, a0, a1). pose: (anim, start tick)
SEGS = [
    dict(id='H1', ko='1타 가로베기 (가로)', hit=1, strokes=[('H1', ATK['a0'], ATK['a1'])], pose=[('hit1_right', 0)], T=22),
    dict(id='H2', ko='2타 되베기 (가로·역)', hit=2, strokes=[('H2', ATK['a0'], ATK['a1'])], pose=[('hit2_right', 0)], T=22),
    dict(id='V', ko='3타 내려베기 (세로)', hit=3, strokes=[('V', ATK3['a0'], ATK3['a1'])], pose=[('hit3_right', 0)], T=26),
    dict(id='X', ko='X 교차베기 (제안)', hit='X', strokes=[('XA', 3, 10), ('XB', 10, 17)], pose=[('hit1_right', 0), ('hit2_right', 7)], T=30),
]
STEP = 2                                   # 1 GIF frame = 2 ticks (33 ms)

def ease(x): x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 2
def state(a0, a1, t):
    sw = max(2.0, 0.6 * (a1 - a0))
    if t < a0 - 2: return None
    if t < a0: return dict(head=None, tail=0, fade=0, active=False, t=t, a0=a0, sw=sw)
    if t <= a1: return dict(head=ease((t - a0 + 1) / sw), tail=0.0, fade=0.0, active=True, t=t, a0=a0, sw=sw)
    f = (t - a1) / FADE_T
    if f >= 1: return None
    return dict(head=1.0, tail=f, fade=f, active=False, t=t, a0=a0, sw=sw)
def born_tick(a0, sw, sv):
    for k in range(0, 40):
        if ease((k + 1) / sw) >= sv: return a0 + k
    return a0 + 40

# ---------------------------------------------------------------- pixel helpers
def snoise(cell, seed, shift=(0, 0)):
    rng = np.random.default_rng(seed); g = rng.random((H // cell + 3, W // cell + 3)).astype(np.float32)
    x = np.mod((XX + shift[0]) / cell, g.shape[1] - 2); y = np.mod((YY + shift[1]) / cell, g.shape[0] - 2)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    return g[y0, x0] * (1 - fx) * (1 - fy) + g[y0, x0 + 1] * fx * (1 - fy) + g[y0 + 1, x0] * (1 - fx) * fy + g[y0 + 1, x0 + 1] * fx * fy
def bnoise(cell, seed):
    rng = np.random.default_rng(seed); g = rng.random((H // cell + 1, W // cell + 1)).astype(np.float32)
    return g[(YY // cell).astype(int), (XX // cell).astype(int)]
def dil(m, diag=True):
    o = m.copy()
    for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)] + ([(1, 1), (1, -1), (-1, 1), (-1, -1)] if diag else []):
        o |= np.roll(np.roll(m, dy, 0), dx, 1)
    return o
def edge_in(m):
    e = np.zeros_like(m)
    for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]: e |= ~np.roll(np.roll(m, dy, 0), dx, 1)
    return m & e

class Layer:
    def __init__(s): s.a = np.zeros((H, W, 4), np.uint8)
    def paint(s, m, col): s.a[m] = hx(col)
    def px(s, x, y, col):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < W and 0 <= y < H: s.a[y, x] = hx(col)
    def mask(s): return s.a[..., 3] > 0
    def outline(s, col, diag=False):
        m = s.mask(); s.paint(dil(m, diag) & ~m, col)
    def line(s, p0, p1, col):
        n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))) + 1
        for i in range(n + 1):
            t = i / max(n, 1); s.px(p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, col)
    def over(s, o):
        m = o.a[..., 3] > 0; s.a[m] = o.a[m]
    def clip(s, m): s.a[~m] = 0

# ---------------------------------------------------------------- shared trail pieces (native scale)
def visible(G, S):
    sv = G['s']; v = G['inside'] & (sv >= 0) & (sv <= S['head'])
    cut = np.clip((sv - S['tail']) / 0.10, 0, 1) if S['tail'] > 0 else np.ones_like(sv)
    return v, cut
def rim_width(G, S, wmin, wmax, tip=0.06):
    sv = G['s']; head = S['head']; u = np.clip(sv / head, 0, 1)
    w = wmin + (wmax - wmin) * u ** 1.4
    w = w * np.clip((head - sv) / tip, 0, 1) ** 0.55 * np.clip(sv / 0.06, 0, 1) ** 0.6
    return w, u
def fan(sh, S, st, back):
    """hitbox fill = everything swept so far (3 flat tones by distance to the rim); collapses outward on fade"""
    if S['head'] is None or S['fade'] >= 0.7: return
    G = sh.g; v, cut = visible(G, S); fr = G['fr']
    m = v & (fr >= min(1.0, S['fade'] * 1.45)) & (cut > 0.5)
    back.paint(m, st.fan[0]); back.paint(m & (fr > .55), st.fan[1]); back.paint(m & (fr > .80), st.fan[2])
    back.paint(edge_in(m) & (G['e'] >= 1.5), st.fan_line)
def afterimages(sh, S, st, back):
    if sh.kind != 'arc' or S['head'] is None or S['fade'] > 0 or S['head'] >= 1: return
    for i, ds in enumerate((0.10, 0.20)):
        sv = S['head'] - ds
        if sv < 0: break
        back.line(sh.pt(sv, sh.R * 0.7), sh.pt(sv, 2.5), st.ghost[min(i, len(st.ghost) - 1)])
def speedlines(sh, S, st, D):
    if sh.kind != 'arc' or S['head'] is None or S['fade'] > 0: return
    rng = np.random.default_rng(st.seed + int(S['head'] * 100))
    for i in range(3):
        s0 = S['head'] - 0.06 - i * 0.09 - rng.random() * 0.03
        if s0 < 0.04: break
        off = 4 + (i % 2) * 2 + int(rng.integers(0, 2)); ln = 0.06 + rng.random() * 0.05
        D.line(sh.pt(s0 - ln, off), sh.pt(s0, off), st.speed)
def sparkle(sh, S, st, D):
    if S['head'] is None or S['fade'] > 0: return
    x, y = sh.pt(S['head'], 0.6); big = 2 if S['head'] < 1 else 1
    c0, c1 = st.spark
    for i in range(1, big + 1):
        for dx, dy in ((i, 0), (-i, 0), (0, i), (0, -i)): D.px(x + dx, y + dy, c0 if i < big else c1)
    D.px(x, y, c0)
def glint(sh, S, D, cols):
    x, y = sh.pt(0.0, 1.0); D.px(x, y, cols[0])
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): D.px(x + dx, y + dy, cols[1])

class Particles:
    def __init__(s, sh, seed, n, srange, roff, speed, up, grav, life, kinds):
        rng = np.random.default_rng(seed); s.p = []
        for i in range(n):
            sv = srange[0] + (srange[1] - srange[0]) * rng.random(); ro = roff[0] + (roff[1] - roff[0]) * rng.random()
            nx, ny = sh.nrm(sv); tx, ty = sh.tan(sv); sp = speed[0] + (speed[1] - speed[0]) * rng.random()
            vx = nx * sp + tx * sp * 0.3 * (rng.random() - 0.3); vy = ny * sp + up * (0.5 + rng.random())
            s.p.append(dict(s=sv, pos=sh.pt(sv, ro), v=(vx, vy), g=grav, life=life[0] + (life[1] - life[0]) * rng.random(),
                            kind=kinds[rng.integers(0, len(kinds))], ph=rng.random() * 6.28))
    def alive(s, S):
        if S['head'] is None: return
        for p in s.p:
            b = born_tick(S['a0'], S['sw'], p['s'])
            if b > S['t']: continue
            age = (S['t'] - b) * TICK + 0.016
            if age > p['life']: continue
            x = p['pos'][0] + p['v'][0] * age + math.sin(p['ph'] + age * 9) * 0.6 * (p['kind'] == 'ash')
            y = p['pos'][1] + p['v'][1] * age + 0.5 * p['g'] * age * age
            yield p, x, y, age / p['life']

# ---------------------------------------------------------------- styles (body = clipped to the hitbox, decor = free)
class Style:
    seed = 1
    def parts(s, sh):
        if sh.name not in s._parts: s._parts[sh.name] = s.make_parts(sh, s.seed + len(s._parts))
        return s._parts[sh.name]
    def make_parts(s, sh, seed): return None

class Ashen(Style):
    n = 1; key = 'ashen_crescent'; ko = '잿빛 초승달'; en = 'Ashen Crescent'; seed = 11
    pal = dict(outline='#0a090c', core='#141118', core2='#2b2628', bone_d='#7f7768', bone='#b8b09b', bone_h='#e3ddcc',
               ash='#5a544c', emb_d='#7a2a10', emb='#cf5f1d', emb_h='#f19a3c', fan0='#1f1c1e', fan1='#252121', fan2='#2d2826', fanline='#0e0d10')
    def __init__(s):
        P = s.pal; s.fan = (P['fan0'], P['fan1'], P['fan2']); s.fan_line = P['fanline']; s._parts = {}
        s.ghost = (P['bone_d'], P['ash']); s.speed = P['ash']; s.spark = (P['bone_h'], P['emb_h'])
    def make_parts(s, sh, seed): return Particles(sh, seed, 12, (0.0, 0.55), (1, 4), (3, 8), -9, 10, (0.18, 0.45), ['e1', 'e1', 'e2'])
    def body(s, sh, S, back, L):
        P = s.pal; G = sh.g; fan(sh, S, s, back); afterimages(sh, S, s, back)
        v, cut = visible(G, S); w, u = rim_width(G, S, 1.2, 4.6); w = w * cut * (1 - .45 * S['fade']); e = G['e']
        m = v & (e < w) & (w > 0.7)
        if S['fade'] > 0: m &= snoise(2, s.seed) > S['fade'] * .75 * (.6 + e / np.maximum(w, 1e-3))
        L.paint(m, P['core']); L.paint(m & (e < 3), P['core2']); L.paint(m & (e < 2), P['bone_d'] if S['fade'] < .6 else P['ash'])
        L.paint(m & (e < 1), P['bone'] if S['fade'] < .6 else P['bone_d'])
        L.paint(m & (e < 1) & (u > .45) & (S['fade'] < .3), P['bone_h'])
        L.paint(m & (u < .3) & (e < 2) & (bnoise(1, 5) < .4), P['ash'])
        L.paint(m & (u < .4) & (e >= 2) & (bnoise(1, 6) > .8), P['emb'])
        L.outline(P['outline'])
    def decor(s, sh, S, D):
        P = s.pal
        if S['head'] is None: glint(sh, S, D, (P['emb_h'], P['emb'])); return
        for p, x, y, a in s.parts(sh).alive(S):
            D.px(x, y, P['emb_h'] if a < .35 else P['emb'] if a < .7 else P['emb_d'])
        speedlines(sh, S, s, D); sparkle(sh, S, s, D)

class Abyss(Style):
    n = 2; key = 'abyss_rift'; ko = '심연 균열'; en = 'Abyss Rift'; seed = 22
    pal = dict(void='#030206', star='#2a1b52', rim_d='#2b1d63', rim='#5d3ba3', rim_h='#9a6fe6', shard_h='#c9adff',
               outline='#120c26', fan0='#0f0b18', fan1='#130d20', fan2='#191029', fanline='#07050c')
    def __init__(s):
        P = s.pal; s.fan = (P['fan0'], P['fan1'], P['fan2']); s.fan_line = P['fanline']; s._parts = {}
        s.ghost = (P['rim'], P['rim_d']); s.speed = P['rim_d']; s.spark = (P['shard_h'], P['rim'])
        rng = np.random.default_rng(s.seed); s.ji = rng.random(48)
    def make_parts(s, sh, seed): return Particles(sh, seed, 12, (0.05, 1.0), (-1, 6), (5, 13), -2, -1, (0.25, 0.6), ['dot', 'h2', 'dia'])
    def body(s, sh, S, back, L):
        P = s.pal; G = sh.g; fan(sh, S, s, back)
        v0 = visible(G, S)[0]
        back.paint((bnoise(1, 9) > .975) & (G['fr'] > .3) & (G['e'] > 2) & v0 & (S['fade'] < .5), P['star']); afterimages(sh, S, s, back)
        v, cut = visible(G, S); w, u = rim_width(G, S, 1.5, 5.4, tip=.08); w = w * cut * max(0.0, 1 - S['fade']) ** 1.2; e = G['e']
        idx = np.clip((G['s'] * 47).astype(int), 0, 47); ji = .55 + .9 * s.ji[idx]
        m = v & (e < w * ji) & (w > .8)
        L.paint(m, P['void']); ed = edge_in(m)
        L.paint(ed, P['rim']); L.paint(m & (e < 1) & (u > .5), P['rim_h'])
        L.paint(m & ~ed & (bnoise(1, 4) > .93), P['star'])
        if 0 < S['fade'] < .9: L.paint(v & (np.abs(e - .5) < .5) & (cut > 0) & ~m, P['rim_d'])
        L.outline(P['outline'])
    def decor(s, sh, S, D):
        P = s.pal
        if S['head'] is None: glint(sh, S, D, (P['void'], P['rim_h'])); return
        for p, x, y, a in s.parts(sh).alive(S):
            D.px(x, y, P['shard_h'] if a < .3 else P['rim_h'] if a < .65 else P['rim'])
            if p['kind'] == 'h2': D.px(x + 1, y, P['rim_d'])
            if p['kind'] == 'dia' and a < .5:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): D.px(x + dx, y + dy, P['rim'])
                D.px(x, y, P['shard_h'])
        speedlines(sh, S, s, D); sparkle(sh, S, s, D)

class BloodInk(Style):
    n = 3; key = 'blood_ink'; ko = '혈묵'; en = 'Blood Ink'; seed = 33
    pal = dict(edge='#1c0408', dark='#420810', body='#6b0e16', sheen='#93202a', dry='#2c060b',
               fan0='#1f1015', fan1='#251217', fan2='#2c1419', fanline='#0f0508')
    def __init__(s):
        P = s.pal; s.fan = (P['fan0'], P['fan1'], P['fan2']); s.fan_line = P['fanline']; s._parts = {}
        s.ghost = (P['dark'], P['dry']); s.speed = P['dark']; s.spark = (P['sheen'], P['body'])
        rng = np.random.default_rng(s.seed); s.cuts = .62 + .36 * rng.random(9); s.scut = .06 * rng.random(9)
    def make_parts(s, sh, seed):
        r2 = np.random.default_rng(seed); out = []
        for j in range(9):
            out.append(dict(s=min(.45 + .6 * r2.random() ** .6, 1.0), off=-(r2.random() ** 1.5) * 4, rad=[0, 0, 0, 1][r2.integers(0, 4)]))
        return out
    def body(s, sh, S, back, L):
        P = s.pal; G = sh.g; fan(sh, S, s, back); afterimages(sh, S, s, back)
        sv = G['s']; head = S['head']; v, cut = visible(G, S)
        w = 6.5 * np.clip(sv / .07, 0, 1) ** .45 * (.55 + .45 * np.clip(sv / max(head, 1e-3), 0, 1))
        if head >= 1: w = w * np.clip((1 - sv) / .3, 0, 1) ** .7
        else:
            cap = sv > head - .05; w = np.where(cap, w * np.sqrt(np.clip(1 - ((sv - (head - .05)) / .05) ** 2, 0, 1)), w)
        w = w * cut; e = G['e']; vv = e / np.maximum(w, 1e-3)
        m = v & (e < w) & (w > 1.0)
        b = np.clip((vv * 9).astype(int), 0, 8)
        gaps = (sv > s.cuts[b]) & (bnoise(1, 3) > .35) & (head >= 1 - 1e-6); gaps |= (sv < s.scut[b]) & (bnoise(1, 8) > .5)
        m &= ~gaps
        if S['fade'] > .5: m &= snoise(2, s.seed) > (S['fade'] - .45) * 1.6
        body = P['body'] if S['fade'] < .5 else P['dark']
        L.paint(m, body); L.paint(m & (b % 3 == 2), P['dark'])
        L.paint(m & (e < 1) & (sv > .35) & (S['fade'] < .25), P['sheen'])
        L.paint(edge_in(m) & (e >= 1), P['edge'])
    def decor(s, sh, S, D):
        P = s.pal
        if S['head'] is None: glint(sh, S, D, (P['sheen'], P['dark'])); return
        if S['fade'] < .95:
            for sp in s.parts(sh):
                if sp['s'] > S['head'] + .02: continue
                x, y = sh.pt(sp['s'], sp['off'] - 1); c = P['body'] if S['fade'] < .5 else P['dark']
                D.px(x, y, c)
                if sp['rad'] and S['fade'] < .6: D.px(x + 1, y, P['edge']); D.px(x, y + 1, P['edge'])
        speedlines(sh, S, s, D); sparkle(sh, S, s, D)

class Steel(Style):
    n = 4; key = 'shattered_steel'; ko = '파쇄 강철'; en = 'Shattered Steel'; seed = 44
    pal = dict(outline='#0f1318', shadow='#45515e', body='#6d7d8d', hi='#a8b5c1', glint='#dce3ea',
               fan0='#1a1f27', fan1='#1d232c', fan2='#222933', fanline='#0b0e12')
    def __init__(s):
        P = s.pal; s.fan = (P['fan0'], P['fan1'], P['fan2']); s.fan_line = P['fanline']; s._parts = {}
        s.ghost = (P['body'], P['shadow']); s.speed = P['shadow']; s.spark = (P['glint'], P['hi'])
        rng = np.random.default_rng(s.seed); s.cuts = np.sort(np.concatenate([[0.0], rng.uniform(.06, .95, 7), [1.0]]))
        s.frag = [dict(thr=.08 + .75 * (i / 8) + .1 * rng.random(), vx=(rng.random() - .5) * 10, vy=-3 - 7 * rng.random(),
                       spin=rng.choice([-1, 1]) * (2 + 4 * rng.random()), j=rng.random()) for i in range(len(s.cuts) - 1)]
    def body(s, sh, S, back, L):
        P = s.pal; G = sh.g; fan(sh, S, s, back)
        if S['fade'] < .5 and sh.kind == 'arc':
            vv_ = visible(G, S)[0]; back.paint(vv_ & (np.mod(G['s'] * 14, 1) < .08) & (G['fr'] > .55) & (G['e'] > 2), s.pal['fan2'])
        afterimages(sh, S, s, back)
        v = visible(G, {**S, 'tail': 0})[0]; w, u = rim_width(G, S, 1.0, 2.6, tip=.08); e = G['e']
        m = v & (e < w) & (w > .6)
        for i in range(len(s.cuts) - 1):
            s0, s1 = s.cuts[i], s.cuts[i + 1]
            if S['fade'] > 0: m &= ~((G['s'] > s1 - .006 * (1 + 4 * S['fade'])) & (G['s'] < s1 + .006 * (1 + 4 * S['fade'])))
            if S['fade'] > s.frag[i]['thr']: m &= ~((G['s'] >= s0) & (G['s'] < s1))
        L.paint(m, P['body']); L.paint(m & (e >= 1.5), P['shadow']); L.paint(m & (e < 1), P['hi'])
        L.paint(m & (e < 1) & (u > .8), P['glint']); L.outline(P['outline'])
    def decor(s, sh, S, D):
        P = s.pal
        if S['head'] is None: x, y = sh.pt(0, 1); D.px(x, y, P['glint']); D.px(x - 1, y - 1, P['hi']); D.px(x + 1, y + 1, P['hi']); return
        img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
        for i in range(len(s.cuts) - 1):
            fr = s.frag[i]
            if not S['fade'] > fr['thr']: continue
            age = (S['fade'] - fr['thr']) * FADE_T * TICK * 2.2
            if age > .3: continue
            s0, s1 = s.cuts[i], s.cuts[i + 1]; wa = 1 + 1.6 * s0 ** 1.4; wb = 1 + 1.6 * s1 ** 1.4
            poly = [sh.pt(s0, 0), sh.pt(s0 + (s1 - s0) * fr['j'], -.8), sh.pt(s1, 0), sh.pt(s1, wb), sh.pt(s0, wa)]
            cx = sum(p[0] for p in poly) / 5; cy = sum(p[1] for p in poly) / 5
            ang = math.radians(round(fr['spin'] * age * 40 / 22.5) * 22.5)
            ox = fr['vx'] * age; oy = fr['vy'] * age + .5 * 85 * age * age
            dr.polygon([(cx + ox + (x - cx) * math.cos(ang) - (y - cy) * math.sin(ang), cy + oy + (x - cx) * math.sin(ang) + (y - cy) * math.cos(ang)) for x, y in poly], fill=1)
        fm = np.array(img) > 0
        Fr = Layer(); Fr.paint(fm, P['body']); Fr.paint(fm & ~np.roll(fm, 1, 0), P['hi']); Fr.outline(P['outline']); D.over(Fr)
        for i in range(len(s.cuts) - 1):
            if 0 < S['fade'] - s.frag[i]['thr'] < .2: x, y = sh.pt(s.cuts[i + 1], 0); D.px(x, y - 1, P['glint'])
        speedlines(sh, S, s, D); sparkle(sh, S, s, D)

class Wraith(Style):
    n = 5; key = 'wraith_smoke'; ko = '망령 연기'; en = 'Wraith Smoke'; seed = 55
    pal = dict(outline='#0a0b0f', smoke_d='#1f222b', smoke='#2c303c', smoke_l='#3e4353', core_g='#8b96a6', core='#d6dee8',
               fan0='#1d1f26', fan1='#21242c', fan2='#262a33', fanline='#0e0f13')
    def __init__(s):
        P = s.pal; s.fan = (P['fan0'], P['fan1'], P['fan2']); s.fan_line = P['fanline']; s._parts = {}
        s.ghost = (P['core_g'], P['smoke_l']); s.speed = P['smoke_l']; s.spark = (P['core'], P['core_g'])
    def make_parts(s, sh, seed): return Particles(sh, seed, 7, (0.1, 0.95), (0, 3), (1, 4), -11, -3, (0.25, 0.6), ['puff'])
    def body(s, sh, S, back, L):
        P = s.pal; G = sh.g; t = S['t'] * TICK; fan(sh, S, s, back); afterimages(sh, S, s, back)
        v, cut = visible(G, S); w, u = rim_width(G, S, 2.0, 6.5, tip=.06); w = w * np.maximum(cut, 0) * (1 + .25 * S['fade'])
        n1 = snoise(3, s.seed, (0, t * 20)); n2 = snoise(2, s.seed + 1, (t * 7, t * 30))
        e = G['e'] + (n1 - .5) * 3 * (.3 + u); vv = e / np.maximum(w, 1e-3)
        m = v & (e >= -0.5) & (e < w) & (w > .8)
        m &= n2 > .12 + S['fade'] * .85 + np.where(u < .25, .25 - u, 0)
        Sm = Layer(); Sm.paint(m, P['smoke']); Sm.paint(m & (vv > .6), P['smoke_d']); Sm.paint(m & (vv < .3), P['smoke_l'])
        Sm.outline(P['outline']); L.over(Sm)
        if S['fade'] < .6:
            dc = 1.5 + (1 - u) * 2
            core = v & (np.abs(G['e'] - dc) < .55) & (u > .12) & (cut > .3)
            if S['fade'] > 0: core &= bnoise(1, 77) > S['fade'] * 1.3
            L.paint(core, P['core'] if S['fade'] < .3 else P['core_g'])
    def decor(s, sh, S, D):
        P = s.pal
        if S['head'] is None: x, y = sh.pt(0, 1); D.px(x, y, P['core']); D.px(x, y - 1, P['core_g']); return
        for p, x, y, a in s.parts(sh).alive(S):
            if a > .85: continue
            rr = .8 + 1.2 * a; mm = ((XX + .5 - x) ** 2 + ((YY + .5 - y) * 1.3) ** 2 <= rr * rr)
            D.paint(mm & ~D.mask(), P['smoke'] if a < .5 else P['smoke_d']); D.px(x, y - rr * .5, P['smoke_l'])
        speedlines(sh, S, s, D); sparkle(sh, S, s, D)

class Gilt(Style):
    n = 6; key = 'dusk_gilt'; ko = '황혼 금선'; en = 'Dusk Gilt'; seed = 66
    pal = dict(outline='#1c170c', g_d='#6b5a2e', g='#8a7340', g_h='#a08a55', g_tip='#c2a96e',
               ash_d='#3a3835', ash='#5a5650', ash_l='#7e786d', emb_d='#6a3214', emb='#b8682a', emb_h='#e0a050',
               fan0='#1c1c1d', fan1='#201f1d', fan2='#26231d', fanline='#0e0d0b')
    def __init__(s):
        P = s.pal; s.fan = (P['fan0'], P['fan1'], P['fan2']); s.fan_line = P['fanline']; s._parts = {}
        s.ghost = (P['g_d'], P['ash_d']); s.speed = P['g_d']; s.spark = (P['g_tip'], P['g'])
    def make_parts(s, sh, seed): return Particles(sh, seed, 16, (0.0, 1.0), (-1, 3), (1, 4), -5, -2, (0.35, 0.8), ['ash', 'ash', 'ash', 'ember'])
    def body(s, sh, S, back, L):
        P = s.pal; G = sh.g; fan(sh, S, s, back); afterimages(sh, S, s, back)
        v, cut = visible(G, S); w, u = rim_width(G, S, 1.0, 2.4, tip=.06); e = G['e']
        m = v & (e < w) & (w > .5) & (cut > .5)
        m &= ~((np.mod(G['s'] * 30, 1) < .45) & (u < .3 + S['fade']))
        if S['fade'] > 0: m &= snoise(2, 12) > S['fade'] * .75
        L.paint(m, P['g'] if S['fade'] < .5 else P['g_d']); L.paint(m & (e >= 1.4), P['g_d'])
        L.paint(m & (e < 1) & (u > .3), P['g_h'] if S['fade'] < .3 else P['g'])
        L.paint(m & (u > .85) & (e < 1) & (S['fade'] == 0), P['g_tip']); L.outline(P['outline'])
    def decor(s, sh, S, D):
        P = s.pal
        if S['head'] is None: x, y = sh.pt(0, 1); D.px(x, y, P['g_tip']); D.px(x + 1, y, P['g']); return
        for p, x, y, a in s.parts(sh).alive(S):
            if p['kind'] == 'ash': D.px(x, y, P['ash_l'] if a < .3 else P['ash'] if a < .7 else P['ash_d'])
            else: D.px(x, y - a * 3, P['emb_h'] if a < .35 else P['emb'] if a < .7 else P['emb_d'])
        speedlines(sh, S, s, D); sparkle(sh, S, s, D)

STYLES = [Ashen(), Abyss(), BloodInk(), Steel(), Wraith(), Gilt()]

# ---------------------------------------------------------------- hero (in-game hero8 frames, displayed size)
REFJ = json.load(open(os.path.join(REF, 'hero_ref.json')))
_HC = {}
def hero_cell(key, scale):
    if (key, scale) in _HC: return _HC[(key, scale)]
    im = Image.open(os.path.join(REF, 'c%s.png' % key)).convert('RGBA'); a = np.array(im)
    rgb = a[..., :3].astype(int); wh = (rgb.min(-1) >= 150) & (rgb.max(-1) - rgb.min(-1) < 40) & (a[..., 3] > 0)
    if wh.sum() > 1000: a[wh] = 0          # strip the baked white crescent of the current hit3 frames (replaced by the trail)
    im = Image.fromarray(a, 'RGBA'); w, h, ax, ay = REFJ['cells'][key]
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    r = im.convert('RGBa').resize((nw, nh), Image.LANCZOS).convert('RGBA'); ra = np.array(r)
    ra[..., 3] = np.where(ra[..., 3] >= 110, 255, 0); r = Image.fromarray(ra, 'RGBA')
    _HC[(key, scale)] = (r, ax * scale, ay * scale); return _HC[(key, scale)]
BAKED_SWAP = {'7_182': '7_181', '7_183': '7_181'}   # hit1/hit2 frames 182-183 carry a baked grey/white smear trail -> use pose 181
def pose_key(anim, tick):
    fr = REFJ['anims'][anim]; acc = 0
    for s_, c, tk in fr:
        acc += tk
        if tick < acc: k_ = '%d_%d' % (s_, c); return BAKED_SWAP.get(k_, k_)
    k_ = '%d_%d' % (fr[-1][0], fr[-1][1]); return BAKED_SWAP.get(k_, k_)
def pose_at(seg, t):
    an, st = seg['pose'][0]
    for a, s0 in seg['pose']:
        if t >= s0: an, st = a, s0
    return pose_key(an, t - st)

# ---------------------------------------------------------------- composition
def ground():
    g = Layer(); g.paint(np.ones((H, W), bool), BG); n = bnoise(2, 999); g.paint(n > .93, BG3); g.paint(n < .06, BG2)
    g.paint(((XX + .5 - FX) / 7) ** 2 + ((YY + .5 - FY) / 2) ** 2 <= 1, SHADOW); return g
GROUND = ground()

def layers(st, seg, t):
    back, front, decor = Layer(), Layer(), Layer(); hit_now = np.zeros((H, W), bool); info = []
    for name, a0, a1 in seg['strokes']:
        sh = SH[name]; S = state(a0, a1, t)
        info.append(dict(name=name, active=bool(S and S['active']), head=(S or {}).get('head')))
        if S is None: continue
        if S['active']: hit_now |= sh.g['inside'] & (sh.g['s'] <= S['head'])
        b, f, d = Layer(), Layer(), Layer()
        if S['head'] is not None:
            st.body(sh, S, b, f)
            b.clip(sh.g['inside']); f.clip(sh.g['inside'])          # trail body never leaves the hitbox
            if name == 'V':                                           # overhead start passes behind the head
                mv = f.mask() & (sh.g['s'] < .3); b.a[mv] = f.a[mv]; f.a[mv] = 0
        st.decor(sh, S, d)
        back.over(b); front.over(f); decor.over(d)
    return back, front, decor, hit_now, info

def up(a, k): return Image.fromarray(a, 'RGBA').resize((W * k, H * k), Image.NEAREST)
def compose(st, seg, t, k=K3, with_bg=True, debug=False):
    back, front, decor, hit_now, info = layers(st, seg, t)
    base = Layer(); base.a = GROUND.a.copy() if with_bg else np.zeros((H, W, 4), np.uint8); base.over(back)
    im = up(base.a, k)
    hc, ax, ay = hero_cell(pose_at(seg, t), k * HSC)
    im.alpha_composite(hc, (int(round(FX * k - ax)), int(round(FY * k - ay))))
    top = Layer(); top.over(front); top.over(decor); im.alpha_composite(up(top.a, k))
    if debug: overlay(im, seg, t, k, hit_now, info)
    return im

# ---------------------------------------------------------------- debug overlay (thin 1-screen-px lines)
def hires_geo(sh, k):
    yy, xx = np.mgrid[0:H * k, 0:W * k].astype(np.float32)
    return sh.geo((xx + .5) / k - FX, (yy + .5) / k - FY)
_HG = {}
def edges(m):
    e = np.zeros_like(m)
    for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]: e |= ~np.roll(np.roll(m, dy, 0), dx, 1)
    return m & e
FS = None
def overlay(im, seg, t, k, hit_now, info):
    global FS
    a = np.array(im)
    full = np.zeros((H * k, W * k), bool); cur = np.zeros_like(full)
    for name, a0, a1 in seg['strokes']:
        sh = SH[name]
        if (name, k) not in _HG: _HG[(name, k)] = hires_geo(sh, k)
        g = _HG[(name, k)]; full |= g['inside']; S = state(a0, a1, t)
        if S and S['active']: cur |= g['inside'] & (g['s'] <= S['head'])
    a[edges(full)] = (255, 210, 60, 255)                  # yellow = full hitbox of this hit (inactive part)
    a[edges(cur)] = (255, 50, 50, 255)                    # red = live hit area this tick
    im.paste(Image.fromarray(a, 'RGBA'))
    dr = ImageDraw.Draw(im)
    fx, fy = FX * k, FY * k
    def circ(cx, cy, r, col): dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=1)
    # reach reference (GK_REACH from the body origin), dotted
    reach = GK_REACH[{'H1': 0, 'H2': 1, 'V': 2, 'X': 2}[seg['id']]]
    ox, oy = fx + O[0] * k, fy + O[1] * k
    for i in range(0, 360, 6):
        an = math.radians(i); x = ox + math.cos(an) * reach * k; y = oy + math.sin(an) * reach * k * GROUND_SQ
        dr.point((x, y), fill=(120, 124, 140))
    circ(fx, fy, 5 * k, (70, 255, 120))                   # hurt: touch() r+5 / moveCol r5 at the feet
    circ(fx, fy - 8 * k, 5 * k, (60, 200, 230))           # hurt vs shots: (hero.y-8), s.r+5
    dr.line([fx - 2, fy - 4 * k, fx + 2, fy - 4 * k], fill=(255, 80, 255)); dr.line([fx, fy - 4 * k - 2, fx, fy - 4 * k + 2], fill=(255, 80, 255))
    for yy in range(int(fy - 30 * k), int(fy), 4): dr.point((fx - 8 * k, yy), fill=(110, 110, 120)); dr.point((fx + 8 * k, yy), fill=(110, 110, 120))
    for xx in range(int(fx - 8 * k), int(fx + 8 * k), 4): dr.point((xx, fy - 30 * k), fill=(110, 110, 120))
    ox_, oy_ = (ox, oy) if seg['id'] != 'V' else (fx + SH['V'].c[0] * k, fy + SH['V'].c[1] * k)
    if seg['id'] == 'X': ox_, oy_ = fx + XC[0] * k, fy + XC[1] * k
    dr.line([ox_ - 3, oy_, ox_ + 3, oy_], fill=(255, 255, 255)); dr.line([ox_, oy_ - 3, ox_, oy_ + 3], fill=(255, 255, 255))
    if FS is None: FS = font(11, False)
    dr.fontmode = '1'
    on = any(i['active'] for i in info)
    dr.text((4, 2), '%s t=%02d %s' % (seg['id'], t, 'HIT ON' if on else 'off'), font=FS, fill=(255, 70, 70) if on else (170, 170, 170))

# ---------------------------------------------------------------- io helpers
def font(sz, bold=True):
    for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc' % ('Bold' if bold else 'Regular'), '/home/box/.fonts/NotoSansKR.ttf']:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz, index=1) if p.endswith('.ttc') else ImageFont.truetype(p, sz)
            except Exception: pass
    return ImageFont.load_default()
def save_gif(frames, delays, path):
    frames = [f.convert('RGB') for f in frames]
    allc = np.unique(np.concatenate([np.array(f).reshape(-1, 3) for f in frames]), axis=0)
    if len(allc) <= 256:
        pal = Image.new('P', (1, 1)); pal.putpalette(list(allc.flatten()) + [0] * (768 - allc.size))
    else:
        big = Image.new('RGB', (frames[0].width, frames[0].height * len(frames)))
        for i, f in enumerate(frames): big.paste(f, (0, i * f.height))
        pal = big.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    ps = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    ps[0].save(path, save_all=True, append_images=ps[1:], duration=delays, loop=0, disposal=1, optimize=False)
    return len(allc)

def timeline():
    seq, dl = [], []
    for seg in SEGS:
        ts = list(range(0, seg['T'] + 1, STEP))
        for t in ts: seq.append((seg, t)); dl.append(33)
        dl[-1] = 260
    dl[-1] = 500
    return seq, dl

def key_tick(seg):           # frame with the full live hitbox (end of sweep, still active)
    a0, a1 = seg['strokes'][-1][1], seg['strokes'][-1][2]; t = a0
    while t < a1 and state(a0, a1, t)['head'] < 1: t += 1
    return t

# ---------------------------------------------------------------- spec
def build_spec():
    ref = 'main clone /tmp/tlg_main (github main @9bd16684, 2026-10-24 16:46:59 KST)'
    sp = dict(
        _doc='Hitbox spec for the v3 slash trail designs. All lengths in field (logical) px of the 384x216 screen; x3 display = 1 px -> 3 screen px. '
             'Origin = hero feet (hero.x, hero.y); +x = facing direction (east; mirror x for west), +y = screen down. '
             'Active ticks are 60fps game ticks from attack start. The trail body is clipped to the hitbox: filled fan/band = hit area; bright rim = outer reach. '
             'Live hit area at tick t (active) = part of the shape with sweep fraction <= head(t), head(t) = 1-(1-clamp((t-a0+1)/sweep_ticks))^2.',
        source=ref,
        game_numbers_found={
            'screen': {'logical': [384, 216], 'scale': 'integer k = floor(min(CW/384, CH/216)) (world.js L1006); x3 = 1152x648', 'src': 'test128/world.js L17, L1006'},
            'hero_display': {'H128FIG_field_px': 30, 'atlas_fig_px': 117, 'draw_scale': 'k*30/117 (k=3 -> 0.769)', 'atlas_figH': 124,
                             'displayed_fig_px': round(124 * HSC, 1), 'src': 'test128/world.js L1128, L1187; assets/anim/hero8.json figH'},
            'hero_hurt': {'melee_touch': 'hypot(hero-mob) < r + 5 (feet, no y-squash)', 'shots': 'hypot(hero.x-s.x, hero.y-8-s.y) < s.r + 5',
                          'hazards': 'probe point (hero.x, hero.y-4) (inHaz)', 'collision': 'moveCol radius 5',
                          'note': 'no rectangle hurtbox exists in code; the hero is a 5 px circle at the feet (+ the y-8 circle for shots)',
                          'src': 'test128/world.js L526, L871, L863, L499, L726/L804'},
            'attack_reach_field_px': {'GK_REACH': GK_REACH, 'GK_ARC_deg_code': [130, 143, 156], 'GK_span_deg_art': [140, 140, 170],
                                      'GK_atlas_px': 'R 52/54/72, T 18/18/26, sq .5/.75/1, rot 0/35/0, fwd 22, y 78/90/74; GK_K = 30/117',
                                      'hit_rule_now': 'gkTouch: mob body points (feet..head x left/mid/right) inside the flying arc band |dd| < T/2 + 6 atlas px',
                                      'src': 'test128/world.js L1193, L1206, L1214, L1216-1217, L1231, L1235-1237'},
            'attack_timing': {'ATK': '.26 s, active .05-.16 s (ticks 3-10)', 'ATK3': '.38 s, active .07-.24 s (ticks 4-14)', 'src': 'test128/world.js L45-46'},
            'town_demo_build_differs': {'SWING': 'range 29 px, arc 150, hit3 arc 100 x1.15 (33.4 px)', 'ATK': 'same timings',
                                         'src': '/workspace/town-demo/world.js L21, L39-40 (older field build, no GK)'},
            'town_hit_table': {'H8HB': 'r right 190/148/174 town px, arcs 150/170/160 (town index.html L1790; x0.3 LSC -> ~57/44/52 logical)'},
            'research': {'recommendation': 'body-centred sweep, radius = reach x 0.7 (hit rate 29% -> 69%), filled fan = hit area',
                         'src': 'share/2026-10-24_slash_shape/README.md'},
        },
        used=dict(
            radius='R = GK_REACH x 0.7 = %.1f / %.1f / %.1f px (hit1/2/3). Code has no sweep radius (it flies a small arc out to the reach), '
                   'so the research recommendation was applied.' % (R1, R2, R3),
            origin='body centre = feet + (0, %d): GK side origin (-78+27 atlas px) x 30/117 = -13.1' % BODY_DY,
            squash='ground-plane y squash 0.8 (world.js L809 hit test ddy/.8)',
            arcs='140 / 140 / 170 deg (research & GK art span); code GK_ARC 130/143/156 is stored but not used by gkTouch',
            hero='in-game hero8 atlas (PixelLab v3 char fb140a07), hit1/2/3_right frames, drawn at 30/117 (x3 -> 0.769, smoothed, alpha cut 110); '
                 'baked white crescents of hit3 frames stripped; hit1/hit2 frames 7_182, 7_183 (baked grey/white smear) replaced by pose 7_181. dark_v3prop (east 124 px fig) is the same character but not the in-game frame set.'),
        hits={},
    )
    for seg in SEGS:
        e = dict(label=seg['ko'], direction={'H1': 'horizontal', 'H2': 'horizontal (reverse)', 'V': 'vertical', 'X': 'X (two diagonals)'}[seg['id']],
                 hit=seg['hit'], strokes=[])
        for name, a0, a1 in seg['strokes']:
            sh = SH[name]; d = sh.spec(); sw = max(2.0, 0.6 * (a1 - a0))
            d.update(active_ticks=[a0, a1], sweep_ticks=round(sw, 2), visual_fade_ticks=[a1 + 1, a1 + FADE_T],
                     preview_frames='1 GIF frame = %d ticks; frame index = tick // %d' % (STEP, STEP))
            g = sh.g; xs = PX[g['inside']]; ys = PY[g['inside']]
            d['native_bbox_from_feet'] = [float(xs.min() - .5), float(ys.min() - .5), float(xs.max() + .5), float(ys.max() + .5)]
            d['area_px'] = int(g['inside'].sum())
            e['strokes'].append(d)
        if seg['id'] == 'X':
            u = SH['XA'].g['inside'] | SH['XB'].g['inside']
            dd = np.hypot(PX[u] - O[0], PY[u] - O[1])
            e['union'] = dict(reach_from_body_centre=round(float(dd.max()), 2), reach_limit=round(R3, 2), band_width=XW, band_length=round(XL, 2),
                              cross_point_from_feet=list(XC), tilt_from_vertical_deg=35, forward_reach_from_feet=float(PX[u].max() + .5),
                              area_px=int(u.sum()), note='X is a design proposal (no X attack in code); uses the hit3 reach 37 -> R 25.9')
        sp['hits'][seg['id']] = e
    return sp

# ---------------------------------------------------------------- main
def main():
    seq, dl = timeline(); out = {}
    normal, debug = {}, {}
    for st in STYLES:
        normal[st.n] = [compose(st, seg, t) for seg, t in seq]
        debug[st.n] = [compose(st, seg, t, debug=True) for seg, t in seq]
        out['style_%d_%s_hitbox.gif' % (st.n, st.key)] = save_gif(normal[st.n], dl, os.path.join(HERE, 'style_%d_%s_hitbox.gif' % (st.n, st.key)))
        out['style_%d_%s_hitbox_debug.gif' % (st.n, st.key)] = save_gif(debug[st.n], dl, os.path.join(HERE, 'style_%d_%s_hitbox_debug.gif' % (st.n, st.key)))
        # native transparent sheet: rows H1/H2/V/X, columns = ticks 0..T step 2; trail only (back+front+decor), 1 px = 1 field px
        cols = max(len(range(0, sg['T'] + 1, STEP)) for sg in SEGS)
        sheet = Image.new('RGBA', (W * cols, H * len(SEGS)))
        for r, seg in enumerate(SEGS):
            for c, t in enumerate(range(0, seg['T'] + 1, STEP)):
                b, f, d, _, _ = layers(st, seg, t); L = Layer(); L.over(b); L.over(f); L.over(d)
                sheet.paste(Image.fromarray(L.a, 'RGBA'), (c * W, r * H))
        sheet.save(os.path.join(HERE, 'style_%d_%s_sheet_native.png' % (st.n, st.key)))
    # hitbox masks (native, 1 px = 1 field px): rows H1/H2/V/X; white = hitbox, red dot = feet
    hm = Image.new('RGBA', (W * len(SEGS), H)); dr = ImageDraw.Draw(hm)
    for i, seg in enumerate(SEGS):
        m = np.zeros((H, W), bool)
        for name, _, _ in seg['strokes']: m |= SH[name].g['inside']
        a = np.zeros((H, W, 4), np.uint8); a[m] = (255, 255, 255, 255); a[FY, FX] = (255, 0, 0, 255)
        hm.paste(Image.fromarray(a, 'RGBA'), (i * W, 0))
    hm.save(os.path.join(HERE, 'hitbox_masks_native.png'))
    # all-in-one: 3x2 styles, each cell = normal | debug at x2 (screen-size budget) -> < 3 MB
    sc = 2; cw, ch, lab = W * K3, H * K3, 26
    f1 = font(16); f2 = font(11, False); allf = []
    for i, (seg, t) in enumerate(seq):
        im = Image.new('RGB', (cw * 2 * 3 + 20, (ch + lab) * 2 + 4), hx('#0c0d10')[:3]); dr = ImageDraw.Draw(im); dr.fontmode = '1'
        for j, st in enumerate(STYLES):
            x, y = (j % 3) * (cw * 2 + 10), (j // 3) * (ch + lab + 4)
            im.paste(normal[st.n][i].convert('RGB'), (x, y + lab)); im.paste(debug[st.n][i].convert('RGB'), (x + cw, y + lab))
            dr.text((x + 6, y + 4), '%d. %s' % (st.n, st.ko), font=f1, fill=(214, 206, 188))
            dr.text((x + cw * 2 - 150, y + 8), seg['ko'], font=f2, fill=(150, 140, 120))
        allf.append(im)
    out['slash_hitbox_all.gif'] = save_gif(allf, dl, os.path.join(HERE, 'slash_hitbox_all.gif'))
    # board: per style row: 4 key frames normal + 4 debug, x3
    labw, head, gap = 250, 96, 24; rowh = ch + 16
    Wb = labw + cw * 4 + gap + cw * 4 + 16
    board = Image.new('RGB', (Wb, head + rowh * 6 + 8), hx('#0c0d10')[:3]); dr = ImageDraw.Draw(board); dr.fontmode = '1'
    dr.text((16, 10), '사멸의 궤적 — 히트박스 일치 검기 v3 (게임 원본 크기 x3, 주인공 30px)', font=font(24), fill=(222, 214, 196))
    dr.text((16, 44), '반지름 = 사거리 x 0.7 (32/30/37 -> %.1f/%.1f/%.1f px) · 판정 = 채워진 부채꼴/띠 · 밝은 테두리 = 최대 사거리 · 빨강 = 지금 판정, 노랑 = 전체 판정, 초록/하늘 = 주인공 피격 원(r5)' % (R1, R2, R3), font=font(13, False), fill=(150, 144, 132))
    names = [sg['ko'] for sg in SEGS]
    fs = font(13, False)
    for i, nm in enumerate(names):
        dr.text((labw + i * cw + 4, head - 20), nm, font=fs, fill=(160, 150, 120))
        dr.text((labw + cw * 4 + gap + i * cw + 4, head - 20), nm + ' · debug', font=fs, fill=(160, 120, 120))
    idx = {}
    for i, (seg, t) in enumerate(seq):
        if t == key_tick(seg) - key_tick(seg) % STEP + (STEP if key_tick(seg) % STEP else 0): idx.setdefault(seg['id'], i)
    for r, st in enumerate(STYLES):
        y = head + r * rowh
        dr.text((16, y + 14), '%d. %s' % (st.n, st.ko), font=font(24), fill=(226, 218, 200)); dr.text((18, y + 48), st.en, font=font(14), fill=(150, 144, 132))
        cl = [c for kk, c in st.pal.items() if not kk.startswith('fan')][:10]
        for j, c in enumerate(cl):
            xx = 18 + (j % 5) * 44; yy = y + 80 + (j // 5) * 46
            dr.rectangle([xx, yy, xx + 36, yy + 26], fill=hx(c)[:3], outline=(70, 70, 76)); dr.text((xx, yy + 28), c, font=font(10, False), fill=(120, 116, 110))
        for i, seg in enumerate(SEGS):
            k_ = idx[seg['id']]
            board.paste(normal[st.n][k_].convert('RGB'), (labw + i * cw, y)); board.paste(debug[st.n][k_].convert('RGB'), (labw + cw * 4 + gap + i * cw, y))
    board.save(os.path.join(HERE, 'slash_hitbox_board.png'))
    json.dump(build_spec(), open(os.path.join(HERE, 'hitbox_spec.json'), 'w'), ensure_ascii=False, indent=1)
    print('colours:', out); print('key frames:', {k: (seq[v][1]) for k, v in idx.items()})

if __name__ == '__main__':
    main()
