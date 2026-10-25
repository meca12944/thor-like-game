"""Wang (corner) autotile compositor for PixelLab create-tileset outputs.
Terrain levels per *vertex*: 0=water 1=base 2=path (3+ = extra, e.g. second base).
Each map uses a 'P' set (lower=base, upper=path) and a 'W' set (lower=water, upper=base).
Ground is rendered at 32px per 16px cell (hd.D=2)."""
import json, os, random
import numpy as np
from PIL import Image
TS = 32
def load_set(d):
    t = json.load(open(os.path.join(d, 'tiles.json')))
    out = {}
    for e in t:
        c = e['corners']; key = tuple(1 if c[k] == 'upper' else 0 for k in ('NW', 'NE', 'SW', 'SE'))
        f = e['f'] if os.path.isabs(e['f']) and os.path.exists(e['f']) else os.path.join(d, os.path.basename(e['f']))
        out[key] = np.array(Image.open(f).convert('RGB')).astype(np.float32)
    return out
def d4(a, i):
    a = np.rot90(a, i % 4)
    return a[:, ::-1] if i >= 4 else a
def unify_base(W, P):
    """replace base-coloured pixels of the W transition tiles with the P base texture, so the
    shoreline tiles sit seamlessly next to plain base tiles."""
    base = P[(0, 0, 0, 0)]; wb = W[(1, 1, 1, 1)]; ww = W[(0, 0, 0, 0)]
    def cent(a, k=6):
        px = a.reshape(-1, 3); rnd = np.random.RandomState(1); c = px[rnd.choice(len(px), k, replace=False)]
        for _ in range(10):
            lab = ((px[:, None] - c[None]) ** 2).sum(-1).argmin(1)
            c = np.array([px[lab == j].mean(0) if (lab == j).any() else c[j] for j in range(k)])
        return c
    cb, cw = cent(wb), cent(ww)
    out = {}
    for key, a in W.items():
        if key in ((0, 0, 0, 0),):
            out[key] = a; continue
        if key == (1, 1, 1, 1):
            out[key] = base.copy(); continue
        px = a.reshape(-1, 3)
        db = ((px[:, None] - cb[None]) ** 2).sum(-1).min(1); dw = ((px[:, None] - cw[None]) ** 2).sum(-1).min(1)
        m = (db < dw * 0.8).reshape(TS, TS)
        # erode by 1 px so the painted bank line stays
        e = m.copy(); e[1:] &= m[:-1]; e[:-1] &= m[1:]; e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
        b = a.copy(); b[e] = base[e]
        # soft 1px blend ring
        ring = m & ~e; b[ring] = a[ring] * 0.5 + base[ring] * 0.5
        out[key] = b
    return out
def vnoise(h, w, cell, seed):
    r = np.random.RandomState(seed)
    gh, gw = h // cell + 2, w // cell + 2
    g = r.rand(gh, gw)
    ys = np.arange(h) / cell; xs = np.arange(w) / cell
    y0 = ys.astype(int); x0 = xs.astype(int); fy = ys - y0; fx = xs - x0
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    top = a + (b - a) * fx[None]; bot = c + (d - c) * fx[None]
    return top + (bot - top) * fy[:, None]
def grade(img, sat=0.78, warm=(1.04, 1.0, 0.92), gain=0.96):
    a = img.astype(np.float32)
    l = (a * [0.3, 0.59, 0.11]).sum(-1, keepdims=True)
    a = l + (a - l) * sat
    a = a * np.array(warm) * gain
    return np.clip(a, 0, 255)
def compose(V, P, W=None, seed=1, extra=None, mottle=0.08, gr=None):
    """V: (h+1, w+1) int array of vertex levels. extra: {level:(set, lower_level)} for other pairs"""
    H, Wd = V.shape[0] - 1, V.shape[1] - 1
    out = np.zeros((H * TS, Wd * TS, 3), np.float32)
    rnd = random.Random(seed)
    for y in range(H):
        for x in range(Wd):
            c = (V[y, x], V[y, x + 1], V[y + 1, x], V[y + 1, x + 1])
            s = set(c); lo = min(s); hi = max(s)
            if 0 in s and 2 in s:  # never: clamp path to base
                c = tuple(1 if v == 2 else v for v in c); s = set(c); hi = max(s)
            if lo == hi:
                src = {0: (W, (0, 0, 0, 0)), 1: (P, (0, 0, 0, 0)), 2: (P, (1, 1, 1, 1))}.get(lo)
                if lo >= 3: src = (extra[lo][0], (1, 1, 1, 1))
                if src[0] is None: src = (P, (0, 0, 0, 0))
                tile = d4(src[0][src[1]], rnd.randrange(8))
            else:
                if lo >= 1 and hi >= 3: st = extra[hi][0]; base = extra[hi][1]
                elif lo == 0: st = W; base = 0
                else: st = P; base = 1
                key = tuple(0 if v <= base else 1 for v in c)
                tile = st[key]
            out[y * TS:(y + 1) * TS, x * TS:(x + 1) * TS] = tile
    n = vnoise(out.shape[0], out.shape[1], 96, seed) * 0.65 + vnoise(out.shape[0], out.shape[1], 29, seed + 7) * 0.35
    out *= (1 - mottle + 2 * mottle * n)[..., None]
    if gr is not False: out = grade(out, **(gr or {}))
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
