# [town_a] procedural painted ground (art px, A=0.6): grass, cobble (voronoi), dirt, sand, soil beds, water
import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from px import hexc, A

def vnoise(h, w, scale, seed):
    r = np.random.default_rng(seed); s = r.random((h // scale + 3, w // scale + 3)).astype(np.float32)
    im = Image.fromarray(s, 'F').resize(((w // scale + 3) * scale, (h // scale + 3) * scale), Image.BICUBIC)
    return np.asarray(im)[scale:scale + h, scale:scale + w]

def fbm(h, w, seed, scales=(64, 24, 8), amps=(.55, .3, .15)):
    out = np.zeros((h, w), np.float32)
    for i, (s, a) in enumerate(zip(scales, amps)): out += vnoise(h, w, s, seed + i * 17) * a
    return out

def C(h): return np.array(hexc(h)[:3], np.float32)

def pal_map(v, cols):
    """v in [0,1] -> blend across colour list"""
    cols = np.array([C(c) for c in cols]); n = len(cols) - 1
    t = np.clip(v, 0, 1) * n; i = np.clip(t.astype(int), 0, n - 1); f = (t - i)[..., None]
    return cols[i] * (1 - f) + cols[i + 1] * f

class Ground:
    def __init__(s, x0, y0, x1, y1, seed=7):
        s.wx0, s.wy0 = x0, y0; s.W = int((x1 - x0) * A); s.H = int((y1 - y0) * A); s.seed = seed
        s.rgb = np.zeros((s.H, s.W, 3), np.float32)
    def P(s, x, y): return ((x - s.wx0) * A, (y - s.wy0) * A)
    def mask(s, draw_fn, blur=0, rough=0, seed=0):
        im = Image.new('L', (s.W, s.H), 0); d = ImageDraw.Draw(im); draw_fn(d, s.P); m = np.asarray(im).astype(np.float32) / 255
        if blur: m = ndi.gaussian_filter(m, blur)
        if rough:
            n = fbm(s.H, s.W, s.seed + seed + 99, (12, 5, 2), (.5, .3, .2))
            m = np.clip((m - .5 + (n - .5) * rough) * 6 + .5, 0, 1)
        return m
    def grass(s):
        H, W = s.H, s.W; n = fbm(H, W, s.seed, (90, 30, 9), (.5, .32, .18)); f = np.random.default_rng(s.seed).random((H, W)).astype(np.float32)
        base = pal_map(n * 1.25 - .1, ['#3f6a2c', '#4e7c34', '#5e8c3c', '#6c9a44', '#7aa64c', '#8ab456'])
        base += ((f - .5) * 14)[..., None]
        # tufts: short vertical dark/light strokes
        r = np.random.default_rng(s.seed + 1)
        k = int(W * H / 22)
        xs, ys = r.integers(1, W - 1, k), r.integers(3, H - 1, k)
        for i in range(k):
            x, y = xs[i], ys[i]
            if f[y, x] < .5:
                base[y - 2:y, x] *= .78; base[y, x] *= .85
            else:
                base[y - 1, x] = base[y - 1, x] * .6 + C('#a6c866') * .4
        s.rgb[:] = base
        s.grassn = n
    def flowers(s, m, density=.004, cols=('#f4a6c4', '#ffffff', '#f6e27a', '#e8607e', '#b67ad8'), seed=3):
        r = np.random.default_rng(seed); ys, xs = np.nonzero(m > .5); k = int(len(ys) * density)
        if not k: return
        idx = r.choice(len(ys), k)
        for i in idx:
            y, x = ys[i], xs[i]; c = C(cols[r.integers(0, len(cols))])
            s.rgb[y, x] = c; 
            if x + 1 < s.W: s.rgb[y, x + 1] = c * .8
            if y + 1 < s.H: s.rgb[y + 1, x] = C('#2e5222')
    def layer(s, m, tex):
        m3 = m[..., None]; s.rgb[:] = s.rgb * (1 - m3) + tex * m3
    def edge_dark(s, m, k=.72, w=2.0):
        """darken just outside/inside a mask border (gives painted outlines to paths)"""
        e = np.clip(ndi.gaussian_filter(m, w) - m, 0, 1) * 2.2
        s.rgb *= (1 - e * (1 - k))[..., None]
    def cobble(s, warm=False, size=17, seed=11):
        H, W = s.H, s.W; r = np.random.default_rng(seed)
        gx, gy = np.meshgrid(np.arange(0, W + size, size), np.arange(0, H + size, size))
        pts = np.stack([gx.ravel() + r.uniform(-.38, .38, gx.size) * size + (gy.ravel() // size % 2) * size * .5,
                        gy.ravel() + r.uniform(-.38, .38, gy.size) * size * .8], 1)
        tree = cKDTree(pts); yy, xx = np.mgrid[0:H, 0:W]
        q = np.stack([xx.ravel(), yy.ravel()], 1).astype(np.float32)
        d, i = tree.query(q, k=2, workers=-1)
        d1 = d[:, 0].reshape(H, W); d2 = d[:, 1].reshape(H, W); ii = i[:, 0].reshape(H, W)
        border = d2 - d1
        tone = r.random(len(pts)).astype(np.float32)[ii]
        cols = ['#6f6a5e', '#857e6e', '#9a927e', '#aca38c', '#bdb49a'] if not warm else ['#7a6a52', '#917e60', '#a6926e', '#b8a47c', '#c9b68e']
        base = pal_map(.25 + tone * .6, cols)
        # light from top-left inside each stone
        cx = pts[ii.ravel(), 0].reshape(H, W); cy = pts[ii.ravel(), 1].reshape(H, W)
        lit = -((xx - cx) * .6 + (yy - cy) * .8) / size
        base *= (1 + np.clip(lit, -.6, .6) * .22)[..., None]
        base += ((r.random((H, W)) - .5) * 10)[..., None]
        gap = border < 1.6
        moss = (fbm(H, W, seed + 5, (40, 12), (.6, .4)) > .62) & gap
        base[gap] = C('#4a4436') if not warm else C('#55462f')
        base[moss] = C('#4f6b30')
        soft = (border >= 1.6) & (border < 2.8); base[soft] *= .86
        return base
    def dirt(s, seed=21, cols=('#6e5232', '#7f6040', '#8f6e4a', '#9e7c54', '#ad8a60')):
        H, W = s.H, s.W; n = fbm(H, W, seed, (40, 14, 4), (.45, .35, .2)); r = np.random.default_rng(seed)
        base = pal_map(n, list(cols)); base += ((r.random((H, W)) - .5) * 16)[..., None]
        k = int(W * H / 140)
        for x, y in zip(r.integers(1, W - 2, k), r.integers(1, H - 2, k)):
            base[y, x] = C('#c0a47a'); base[y + 1, x] = C('#5a4028')
        return base
    def sand(s, seed=31):
        return s.dirt(seed, ('#a89068', '#b8a076', '#c6ae84', '#d2bc92', '#dcc8a0'))
    def soil_rows(s, m, horizontal=True, period=9, seed=41):
        H, W = s.H, s.W; yy, xx = np.mgrid[0:H, 0:W]
        ph = (yy if horizontal else xx) % period
        base = s.dirt(seed, ('#4a3222', '#573c28', '#64462e', '#704f34', '#7c5a3c'))
        base[ph < 3] *= .72
        base[ph == 3] *= 1.15
        s.layer(m, base); return ph
    def crops(s, m, kind, seed=51, period=9):
        r = np.random.default_rng(seed); H, W = s.H, s.W
        ys, xs = np.nonzero(m > .6)
        if not len(ys): return
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        if kind == 'carrot':
            for y in range(y0 + 5, y1, period):
                for x in range(x0 + 2, x1, 6):
                    if m[y, x] < .6: continue
                    xx = x + r.integers(-1, 2)
                    for (dx, dy, c) in ((0, 0, '#3e7a2c'), (-1, -1, '#5a9a3a'), (1, -1, '#5a9a3a'), (0, -2, '#76b44a'), (-2, -2, '#4a8a32'), (2, -2, '#4a8a32'), (0, 1, '#e07a2a')):
                        if 0 <= y + dy < H and 0 <= xx + dx < W: s.rgb[y + dy, xx + dx] = C(c)
        else:
            for y in range(y0 + 6, y1, 14):
                for x in range(x0 + 4, x1, 13):
                    if m[y, x] < .6 or r.random() < .15: continue
                    cx, cy = x + r.integers(-2, 3), y + r.integers(-2, 3); rx, ry = 5 + r.integers(0, 2), 4
                    for yy in range(-ry, ry + 1):
                        for xx in range(-rx, rx + 1):
                            if (xx / rx) ** 2 + (yy / ry) ** 2 <= 1 and 0 <= cy + yy < H and 0 <= cx + xx < W:
                                v = .5 - xx / rx * .3 - yy / ry * .35 + (.15 if xx % 3 == 0 else 0)
                                s.rgb[cy + yy, cx + xx] = pal_map(np.array(v), ['#8a3a10', '#c05a1a', '#e07a2a', '#f4a048'])
                    s.rgb[cy - ry - 1, cx] = C('#4a6a22'); s.rgb[cy - ry - 2, cx + 1] = C('#4a6a22')
                    for k in range(6):
                        lx, ly = cx + r.integers(-9, 10), cy + r.integers(-6, 6)
                        if 0 <= ly < H and 0 <= lx < W and s.rgb[ly, lx, 0] < 120: s.rgb[ly, lx] = C('#3e7a2c' if k % 2 else '#5a9a3a')
    def water(s, cx, cy, rx, ry, seed=61, rim=True):
        H, W = s.H, s.W; px, py = s.P(cx, cy); rxa, rya = rx * A, ry * A
        yy, xx = np.mgrid[0:H, 0:W]; e = ((xx - px) / rxa) ** 2 + ((yy - py) / rya) ** 2
        n = fbm(H, W, seed, (16, 6), (.6, .4))
        m = e < 1 + (n - .5) * .25
        depth = np.clip(1 - e, 0, 1)
        col = pal_map(.85 - depth * .75 + (n - .5) * .1, ['#1c4a60', '#26607a', '#357a92', '#4a94a8', '#6aaebc'])
        # shimmer lines
        sh = ((yy + (np.sin(xx * .15) * 2).astype(int)) % 11 == 0) & (n > .55)
        col[sh] = C('#a8dce6')
        s.rgb[m] = col[m]
        if rim:
            ring = (e >= 1 + (n - .5) * .25) & (e < 1.32 + (n - .5) * .25)
            st = s.cobble(seed=seed + 3, size=9)
            s.rgb[ring] = st[ring] * .95
            inner = (e < 1 + (n - .5) * .25) & (e > .86); s.rgb[inner] *= .75
        return m
    def shadow(s, draw_fn, k=.62, blur=3.5):
        m = s.mask(draw_fn, blur=blur); s.rgb *= (1 - m * (1 - k))[..., None]
    def save_chunks(s, outdir, prefix, cw=640, ch=560, q=88):
        out = []; im = Image.fromarray(np.clip(s.rgb, 0, 255).astype(np.uint8), 'RGB')
        for y in range(0, s.H, ch):
            for x in range(0, s.W, cw):
                c = im.crop((x, y, min(s.W, x + cw), min(s.H, y + ch))); nm = f'{prefix}_{x // cw}_{y // ch}.jpg'
                c.save(f'{outdir}/{nm}', quality=q, optimize=True)
                out.append(dict(src=nm, x=round(s.wx0 + x / A, 2), y=round(s.wy0 + y / A, 2), w=round(c.width / A, 2), h=round(c.height / A, 2)))
        return out, im
