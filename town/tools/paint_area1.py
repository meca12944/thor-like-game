"""Area-1 painted backgrounds (768x432 base grid: 1 tile = 16 logical px = 32 buffer px).
Bakes the static ground of every area-1 map from its tile grid (the collision source of truth), so the art always matches collision:
  grass / forest floor / dirt road / sand / tall grass / water with banks + north-bank drop / stepping stones / plank bridges /
  3-4 view cliffs (rock face + grass lip + stone steps) / dungeon flagstones, moss, cracks, 1.5-tile wall faces, wall tops, pits, spike beds,
  stairs, boss rune floor, ambient occlusion and contact shadows.
Tall things (trees, rocks, pillars, ruins, doors, torches, chests, mobs, hero) are drawn by world.js as y-sorted sprites from
assets/world/paint/props.png (tools/paint_props.py) so the hero walks behind canopies.
Textures: assets_src/world/paint/tex_*.jpg (generated, painted).  Output: assets/world/paint/<map>_bg.webp
Run: python3 tools/paint_area1.py [map ...]"""
import os, sys, json, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SRC = R + 'assets_src/world/paint/'; OUT = R + 'assets/world/paint/'
S = 32
rng = np.random.default_rng(7)
def H(x, y, s=0): return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) & 0xffffffff
def load(n): return np.asarray(Image.open(SRC + n + '.jpg').convert('RGB')).astype(np.float32) / 255
def seamless(n, P, both=True, crop=None):
    a = load(n); h, w, _ = a.shape
    if crop: a = a[crop[1]:crop[3], crop[0]:crop[2]]; h, w, _ = a.shape
    if both:
        m = min(h, w); a = a[(h - m) // 2:(h - m) // 2 + m, (w - m) // 2:(w - m) // 2 + m]
        a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((P, P), Image.LANCZOS)).astype(np.float32) / 255
        b = np.roll(np.roll(a, P // 2, 0), P // 2, 1)
        t = np.sin(np.linspace(0, math.pi, P)) ** 2; wgt = np.outer(t, t)[..., None]
        return a * wgt + b * (1 - wgt)
    PH = round(h * P / w)
    a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((P, PH), Image.LANCZOS)).astype(np.float32) / 255
    b = np.roll(a, P // 2, 1); t = (np.sin(np.linspace(0, math.pi, P)) ** 2)[None, :, None]
    return a * t + b * (1 - t)
def tile_to(t, h, w, ox=0, oy=0):
    th, tw = t.shape[:2]
    ys = (np.arange(h) + oy) % th; xs = (np.arange(w) + ox) % tw
    return t[ys][:, xs]
def noise(h, w, scale, seed):
    r = np.random.default_rng(seed); gh, gw = h // scale + 3, w // scale + 3
    z = ndi.zoom(r.random((gh, gw)), scale, order=3)[:h, :w]
    return (z - z.mean()) / (z.std() + 1e-6)
def fbm(h, w, seed, scales=(256, 96, 32, 12), amps=(1, .55, .3, .15)):
    return sum(a * noise(h, w, s, seed + i) for i, (s, a) in enumerate(zip(scales, amps))) / sum(amps)
def up(m):  # cell mask -> pixel mask (nearest)
    return np.kron(m.astype(np.float32), np.ones((S, S), np.float32))
def soft(m, sigma, nz, amp=.2, width=.12, bias=0.):
    b = ndi.gaussian_filter(up(m), sigma)
    return np.clip((b - .5 + bias + nz * amp) / width + .5, 0, 1)
def blend(base, top, a):
    a = a[..., None] if a.ndim == 2 else a
    return base * (1 - a) + top * a
def grade(img, mul):  # multiply by per-pixel scalar or rgb
    return img * (mul[..., None] if mul.ndim == 2 else mul)
def save(img, mid):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    im.save(OUT + mid + '_bg.webp', quality=86, method=6)
    print(mid, im.size, os.path.getsize(OUT + mid + '_bg.webp') // 1024, 'KB')
    return im
PROPS = Image.open(OUT + 'props.png').convert('RGBA'); PMETA = json.load(open(OUT + 'props.json'))['rects']
def prop(name, scale=1.):
    x, y, w, h, ax, ay = PMETA[name]; im = PROPS.crop((x, y, x + w, y + h))
    if scale != 1: im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    return im, ax * scale, ay * scale
def paste(canvas, name, px, py, scale=1., flip=False, alpha=1.):
    im, ax, ay = prop(name, scale)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = im.size[0] - ax
    if alpha < 1: a = np.asarray(im).copy(); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); im = Image.fromarray(a)
    canvas.alpha_composite(im, (int(round(px - ax)), int(round(py - ay))))

# =============================================================================== fields
def paint_field(j):
    w, h = j['w'], j['h']; Hp, Wp = h * S, w * S
    G = [row.ljust(w, '#')[:w] for row in j['ground']]
    C = np.array([list(r) for r in G])
    cells = lambda chars: np.isin(C, list(chars))
    tex = {k: seamless('tex_' + k, P) for k, P in [('grass', 512), ('dirt', 448), ('forest', 448), ('water', 384), ('sand', 320)]}
    n1, n2, n3 = fbm(Hp, Wp, 1), fbm(Hp, Wp, 2), fbm(Hp, Wp, 3, scales=(48, 16, 6), amps=(1, .6, .3))
    # 1. meadow: grass with large tonal variation (sunny yellow-green patches / cooler shade)
    img = tile_to(tex['grass'], Hp, Wp)
    warm = np.array([1.08, 1.04, .82]); cool = np.array([.82, .92, .9])
    t = np.clip(n1 * .5 + .5, 0, 1)[..., None]
    img = img * (warm * t + cool * (1 - t)) * (1 + .06 * n2[..., None])
    # 2. forest floor under woods (and slightly beyond), deep forest darker
    trees = cells('TPY')
    fm = soft(trees, 16, n2, .3, .3, -.05)
    img = blend(img, tile_to(tex['forest'], Hp, Wp, 37, 91) * 1.05, fm * .92)
    deep = ndi.binary_erosion(trees, iterations=2, border_value=1)
    img = grade(img, 1 - .35 * ndi.gaussian_filter(up(deep), 22))
    # 3. sand (beach / island)
    sand = cells('_')
    sm = soft(sand, 11, n3, .4, .22)
    img = blend(img, tile_to(tex['sand'], Hp, Wp) * np.array([1.02, 1, .95]), sm)
    # 4. dirt road with darker trodden centre and a soft worn rim
    road = cells('=OXzS')
    rm = soft(road, 12, n3 * .7 + n2 * .3, .45, .22)
    dirt = tile_to(tex['dirt'], Hp, Wp, 11, 29) * (1 + .07 * n2[..., None])
    ctr = ndi.gaussian_filter(up(ndi.binary_erosion(road, iterations=1)), 10)
    dirt = grade(dirt, 1 - .10 * ctr)
    rim = np.clip(1 - np.abs(rm - .5) * 2.4, 0, 1)
    img = grade(img, 1 - .16 * rim * (1 - rm))
    img = blend(img, dirt, rm)
    # 5. tall grass: dark lush base + painted blades (below), slightly raised look
    tg = cells('"'); tm = soft(tg, 11, n3, .4, .25)
    img = grade(img, 1 - .18 * tm)
    # 6. ambient occlusion around solid objects (trees, rocks, cliffs)
    sol = cells('TPRrusfOWLXZ#')
    ao = ndi.gaussian_filter(up(sol), 10)
    img = grade(img, 1 - .22 * ao * (1 - up(sol)))
    # 7. water: bank band, depth, north-bank drop, shore highlight
    water = cells('~b:') 
    wm = soft(water, 10, n3, .25, .1, -.03)                     # slightly inside the tiles -> banks read on the land side
    bank = np.clip(ndi.gaussian_filter(up(water), 9) * 2.2, 0, 1) * (1 - wm)
    wetsand = tile_to(tex['sand'], Hp, Wp, 70, 13) * np.array([.72, .70, .62])
    img = blend(img, wetsand, np.clip(bank * 1.15, 0, 1) * .85)
    dist = ndi.distance_transform_edt(wm > .5)
    depth = np.clip(dist / 40, 0, 1)
    wt = tile_to(tex['water'], Hp, Wp) * (1 - .38 * depth[..., None]) * np.array([.92, 1.0, 1.02])
    img = blend(img, wt, wm)
    # north bank drop: water pixels just below land (3/4 view shows the earth bank face)
    land_above = np.roll(wm < .5, 10, axis=0) & (wm > .5); land_above[:10] = False
    dropband = np.zeros((Hp, Wp), np.float32)
    for k in range(1, 12): dropband = np.maximum(dropband, (np.roll(wm < .5, k, 0) & (wm > .5)) * (1 - k / 12))
    dropband[:12] = 0
    img = blend(img, np.array([.27, .22, .16]) * (1 + .15 * n3[..., None]), dropband * .85)
    edge = np.clip(1 - np.abs(wm - .55) * 7, 0, 1)
    img = img + edge[..., None] * np.array([.18, .22, .2]) * .6
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(pil)
    # 8. tall grass blades
    r2 = np.random.default_rng(5)
    ys, xs = np.nonzero(tg)
    for cy, cx in sorted(zip(ys, xs)):
        for _ in range(26):
            bx = cx * S + r2.random() * S; by = cy * S + r2.random() * S + 6; L = 7 + r2.random() * 9; lean = (r2.random() - .5) * 6
            g0 = 70 + int(r2.random() * 50)
            d.line([(bx, by), (bx + lean, by - L)], fill=(30, g0, 28, 255), width=2)
            d.line([(bx + lean * .6, by - L * .6), (bx + lean, by - L)], fill=(120, 175 + int(r2.random() * 40), 70, 255), width=1)
    # 9. small tufts (',') and flowers (''')
    for cy, cx in zip(*np.nonzero(cells(','))):
        for _ in range(3):
            bx = cx * S + 4 + r2.random() * 24; by = cy * S + 8 + r2.random() * 20
            for k in range(5):
                a = -math.pi / 2 + (k - 2) * .35; L = 4 + r2.random() * 4
                d.line([(bx, by), (bx + math.cos(a) * L, by + math.sin(a) * L)], fill=(52, 110, 38, 255) if k % 2 else (130, 180, 70, 255), width=1)
    for cy, cx in zip(*np.nonzero(cells("'"))):
        nm = ['flowers_blue', 'flowers_yellow'][H(cx, cy, 4) % 2]
        paste(pil, nm, cx * S + 8 + H(cx, cy, 5) % 16, cy * S + 22 + H(cx, cy, 6) % 8, .62 + (H(cx, cy, 7) % 20) / 100, flip=H(cx, cy, 8) % 2 == 1)
    for cy, cx in zip(*np.nonzero(cells('m'))): paste(pil, 'mushrooms', cx * S + 16, cy * S + 26, .9)
    for cy, cx in zip(*np.nonzero(cells('n'))): paste(pil, 'fern', cx * S + 16, cy * S + 28, .85, flip=H(cx, cy, 2) % 2 == 1)
    # 10. stepping stones
    for cy, cx in zip(*np.nonzero(cells(':'))):
        x0, y0 = cx * S + 16, cy * S + 17
        d.ellipse([x0 - 13, y0 - 7, x0 + 13, y0 + 11], fill=(20, 40, 45, 160))
        d.ellipse([x0 - 13, y0 - 10, x0 + 13, y0 + 8], fill=(118, 118, 108, 255)); d.ellipse([x0 - 10, y0 - 9, x0 + 8, y0 + 2], fill=(160, 158, 142, 255))
        d.arc([x0 - 13, y0 - 10, x0 + 13, y0 + 8], 20, 160, fill=(60, 62, 58, 255), width=2)
    # 11. plank bridges (components of 'b' not covered by a barrier)
    covered = set()
    for o in j.get('objects', []):
        if o['type'] == 'barrier':
            for yy in range(o['y'], o['y'] + o['h']):
                for xx in range(o['x'], o['x'] + o['w']): covered.add((xx, yy))
    bmask = cells('b').copy()
    for (xx, yy) in covered:
        if 0 <= yy < h and 0 <= xx < w: bmask[yy, xx] = False
    lab, nb = ndi.label(bmask)
    for i, sl in enumerate(ndi.find_objects(lab)):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        draw_bridge(pil, x0 * S, y0 * S, (x1 - x0) * S, (y1 - y0) * S)
    img = np.asarray(pil.convert('RGB')).astype(np.float32) / 255
    # 12. cliffs (3/4: rock face on the lowest 2 rows of each cliff column, grassy plateau above, steps)
    cl = cells('#'); st = cells('S')
    if cl.any() or st.any():
        img = paint_cliffs(img, C, cl | st, st, tex, n2, n3)
    return img

def draw_bridge(pil, X, Y, Wd, Hd):
    d = ImageDraw.Draw(pil); r = np.random.default_rng(X * 7 + Y)
    d.rectangle([X - 4, Y + 4, X + Wd + 4, Y + Hd + 8], fill=(15, 30, 32, 110))            # shadow on the water
    pw = 9
    for px in range(X - 4, X + Wd + 4, pw):                                                   # planks run across the travel direction (north-south)
        c = 120 + int(r.random() * 40); jy = int(r.random() * 3)
        d.rectangle([px, Y + 3 + jy, px + pw - 2, Y + Hd - 3 + jy], fill=(c, int(c * .68), int(c * .4), 255))
        d.line([(px, Y + 3 + jy), (px, Y + Hd - 3 + jy)], fill=(70, 44, 24, 255), width=1)
        d.line([(px + 2, Y + 5 + jy), (px + 2, Y + Hd - 6 + jy)], fill=(min(255, c + 40), int(c * .8), int(c * .5), 255), width=1)
    for yy in (Y + 2, Y + Hd - 6):                                                             # side beams + rails
        d.rectangle([X - 6, yy, X + Wd + 6, yy + 5], fill=(92, 58, 30, 255)); d.line([(X - 6, yy), (X + Wd + 6, yy)], fill=(150, 104, 60, 255), width=1)
    for px in range(X - 6, X + Wd + 8, 24):
        for yy in (Y - 6, Y + Hd - 14):
            d.rectangle([px, yy, px + 5, yy + 14], fill=(78, 50, 26, 255)); d.rectangle([px, yy, px + 5, yy + 2], fill=(140, 96, 54, 255))
    d.line([(X - 6, Y - 4), (X + Wd + 8, Y - 4)], fill=(176, 150, 100, 255), width=2)
    d.line([(X - 6, Y + Hd - 12), (X + Wd + 8, Y + Hd - 12)], fill=(176, 150, 100, 255), width=2)

def paint_cliffs(img, C, cl, st, tex, n2, n3):
    h, w = C.shape; Hp, Wp = h * S, w * S
    face_t = seamless('tex_cliff', 384, both=False)
    ft = tile_to(face_t, max(face_t.shape[0], 64), Wp)
    out = img.copy()
    # plateau top: lighter, warmer grass (elevated), with dark rim where it drops
    top = np.zeros((h, w), bool); face = np.zeros((h, w), np.int8)
    for y in range(h):
        for x in range(w):
            if not cl[y, x]: continue
            below1 = y + 1 >= h or not cl[y + 1, x]; below2 = y + 2 >= h or not cl[y + 2, x]
            if below1: face[y, x] = 2       # lower face row
            elif below2: face[y, x] = 1     # upper face row
            else: top[y, x] = True
    tm = up(top)
    grass_hi = tile_to(tex['grass'], Hp, Wp, 200, 120) * np.array([1.1, 1.08, .85])
    out = blend(out, grass_hi * (1 + .05 * n2[..., None]), tm)
    # faces
    fm = up(face > 0)
    rowpos = np.zeros((Hp, Wp), np.float32)   # 0 at the top of the face band -> 1 at its bottom
    for y in range(h):
        for x in range(w):
            if face[y, x] == 1: rowpos[y * S:(y + 1) * S, x * S:(x + 1) * S] = np.linspace(0, .5, S)[:, None]
            if face[y, x] == 2:
                above = y - 1 >= 0 and face[y - 1, x] == 1
                rowpos[y * S:(y + 1) * S, x * S:(x + 1) * S] = (np.linspace(.5, 1, S) if above else np.linspace(0, 1, S))[:, None]
    fy = (rowpos * 63).astype(int); fx = np.arange(Wp)[None, :].repeat(Hp, 0)
    rock = ft[np.clip(fy + (np.arange(Hp)[:, None] // 64) * 0, 0, ft.shape[0] - 1), fx % ft.shape[1]]
    shade = (1.05 - .45 * rowpos)[..., None] * (1 + .08 * n3[..., None])
    out = blend(out, rock * shade, fm)
    # grass lip at the top of each face band (jagged overhang)
    lip = np.zeros((Hp, Wp), np.float32)
    for y in range(h):
        for x in range(w):
            if face[y, x] > 0 and (y == 0 or face[y - 1, x] == 0):
                for px in range(x * S, (x + 1) * S):
                    L = 6 + int(4 + 3 * math.sin(px * .37) + 2 * math.sin(px * 1.3) + (H(px, y, 3) % 4))
                    lip[y * S:y * S + L, px] = 1
    out = blend(out, grass_hi * .92, lip)
    out = grade(out, 1 - .35 * np.clip(ndi.gaussian_filter(lip, 2) - lip, 0, 1) * 3)
    # side shading where a face meets open ground left/right, and a contact shadow below the face
    for y in range(h):
        for x in range(w):
            if face[y, x] > 0:
                if x > 0 and not cl[y, x - 1]: out[y * S:(y + 1) * S, x * S:x * S + 5] *= np.linspace(.55, 1, 5)[None, :, None]
                if x + 1 < w and not cl[y, x + 1]: out[y * S:(y + 1) * S, (x + 1) * S - 5:(x + 1) * S] *= np.linspace(1, .55, 5)[None, :, None]
            if face[y, x] == 2 and y + 1 < h and not cl[y + 1, x]:
                out[(y + 1) * S:(y + 1) * S + 10, x * S:(x + 1) * S] *= np.linspace(.6, 1, 10)[:, None, None]
    # stone steps
    pil = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(pil)
    ys, xs = np.nonzero(st)
    if len(xs):
        x0, x1, y0, y1 = xs.min() * S, (xs.max() + 1) * S, ys.min() * S, (ys.max() + 1) * S
        d.rectangle([x0 - 3, y0, x1 + 3, y1], fill=(70, 66, 58))
        n = (y1 - y0) // 9
        for i in range(n):
            yy = y0 + i * 9; c = 128 + i * 6
            d.rectangle([x0, yy, x1, yy + 8], fill=(c, c - 4, c - 14)); d.line([(x0, yy + 8), (x1, yy + 8)], fill=(58, 54, 48), width=2)
            d.line([(x0, yy), (x1, yy)], fill=(min(255, c + 40), min(255, c + 36), min(255, c + 24)), width=1)
        d.rectangle([x0 - 6, y0, x0 - 1, y1], fill=(96, 90, 80)); d.rectangle([x1 + 1, y0, x1 + 6, y1], fill=(96, 90, 80))
    return np.asarray(pil).astype(np.float32) / 255

# =============================================================================== dungeon / boss
def paint_dungeon(j, boss=False):
    w, h = j['w'], j['h']; Hp, Wp = h * S, w * S
    G = [row.ljust(w, '#')[:w] for row in j['ground']]
    C = np.array([list(r) for r in G])
    legend = j['legend']
    def isw(ch):
        L = legend.get(ch, 'wall'); g = L if isinstance(L, str) else L.get('ground', 'floor')
        return g.startswith('wall')
    wall = np.vectorize(isw)(C)
    floor = ~wall
    fl = seamless('tex_dfloor', 448)
    n2, n3 = fbm(Hp, Wp, 12), fbm(Hp, Wp, 13, scales=(40, 14, 5), amps=(1, .6, .3))
    img = np.zeros((Hp, Wp, 3), np.float32) + np.array([.035, .04, .05])
    flo = tile_to(fl, Hp, Wp) * np.array([.92, 1.0, .95]) * (1 + .08 * n2[..., None])
    fmask = up(floor)
    img = blend(img, flo, fmask)
    # moss ',' patches and cracks '%'
    moss = soft(np.isin(C, [',']), 9, n3, .35, .35, -.08) * fmask
    mt = tile_to(seamless('tex_forest', 384), Hp, Wp) * np.array([.75, 1.0, .7])
    img = blend(img, mt, moss * .75)
    if boss:   # rune circle fitted to the arena interior
        ys, xs = np.nonzero(floor); x0, x1, y0, y1 = xs.min() * S, (xs.max() + 1) * S, ys.min() * S, (ys.max() + 1) * S
        bf = Image.open(SRC + 'tex_bossfloor.jpg').convert('RGB')
        bw = x1 - x0 + 120; bh = round(bw * bf.size[1] / bf.size[0])
        bf = np.asarray(bf.resize((bw, bh), Image.LANCZOS)).astype(np.float32) / 255
        cx, cy = (x0 + x1) // 2, int(j['boss']['y'] * S + 2.2 * S)
        canvas = img.copy(); yy0 = cy - bh // 2; xx0 = cx - bw // 2
        sy0, sx0 = max(0, -yy0), max(0, -xx0); ey, ex = min(bh, Hp - yy0), min(bw, Wp - xx0)
        canvas[yy0 + sy0:yy0 + ey, xx0 + sx0:xx0 + ex] = bf[sy0:ey, sx0:ex]
        rad = np.hypot((np.arange(Wp)[None, :] - cx) / (bw * .5), (np.arange(Hp)[:, None] - cy) / (bh * .5))
        a = np.clip((1.02 - rad) / .12, 0, 1) * fmask
        img = blend(img, canvas * 1.08, a)
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(pil)
    r2 = np.random.default_rng(3)
    for cy, cx in zip(*np.nonzero(np.isin(C, ['%']))):
        for _ in range(2):
            x, y = cx * S + r2.random() * S, cy * S + r2.random() * S
            pts = [(x, y)]
            for k in range(5): x += (r2.random() - .5) * 12; y += (r2.random() - .5) * 12; pts.append((x, y))
            d.line(pts, fill=(18, 20, 22, 255), width=2)
    img = np.asarray(pil.convert('RGB')).astype(np.float32) / 255
    # walls: face where floor is directly below (1 tile, +0.5 tile up into a wall above), dark tops elsewhere
    wt = seamless('tex_dwall', 448, both=False, crop=(0, 0, 1280, 335))
    frieze = seamless('tex_dwall', 448, both=False, crop=(0, 340, 1280, 405))
    face = np.zeros((h, w), bool)
    for y in range(h):
        for x in range(w):
            if wall[y, x] and y + 1 < h and floor[y + 1, x]: face[y, x] = True
    topc = tile_to(fl, Hp, Wp, 100, 50) * np.array([.11, .12, .14])
    tmask = up(wall & ~face)
    img = blend(img, topc * (1 + .1 * n3[..., None]), tmask)
    fh = int(S * 1.5)
    for y in range(h):
        for x in range(w):
            if not face[y, x]: continue
            ext = 16 if (y - 1 >= 0 and wall[y - 1, x] and not face[y - 1, x]) else 0
            yA, yB = (y + 1) * S - (S + ext), (y + 1) * S
            seg = tile_to(wt, yB - yA, S, x * S, 0 if ext else 16)
            g = np.linspace(.62, 1.0, yB - yA)[:, None, None] * (.9 if boss else .8)
            img[yA:yB, x * S:(x + 1) * S] = seg * g
            if boss:
                fr = tile_to(frieze, 12, S, x * S, 0); img[yA + 4:yA + 16, x * S:(x + 1) * S] = fr * .95
            img[yB - 3:yB, x * S:(x + 1) * S] *= .45                                              # base shadow line
            img[yA:yA + 2, x * S:(x + 1) * S] = img[yA:yA + 2, x * S:(x + 1) * S] * .6 + np.array([.36, .4, .3]) * .4   # top edge highlight
    # wall-top rims next to floor (left/right/top), soft floor shadows
    rimc = np.array([.36, .40, .32])
    for y in range(h):
        for x in range(w):
            if not wall[y, x] or face[y, x]: continue
            X0, Y0 = x * S, y * S
            if x > 0 and floor[y, x - 1]: img[Y0:Y0 + S, X0:X0 + 3] = rimc
            if x + 1 < w and floor[y, x + 1]: img[Y0:Y0 + S, X0 + S - 3:X0 + S] = rimc
            if y > 0 and floor[y - 1, x]: img[Y0:Y0 + 3, X0:X0 + S] = rimc
    ao = ndi.gaussian_filter(up(wall), 7)
    img = grade(img, 1 - .45 * ao * fmask)
    # baked statics: pits, spike beds, stairs, torch glow
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(pil)
    for cy, cx in zip(*np.nonzero(C == 'o')):
        X, Y = cx * S, cy * S
        d.rounded_rectangle([X + 1, Y + 1, X + S - 2, Y + S - 2], 6, fill=(54, 50, 44, 255))
        d.rounded_rectangle([X + 3, Y + 3, X + S - 4, Y + S - 4], 5, fill=(6, 6, 9, 255))
        d.rectangle([X + 4, Y + 4, X + S - 5, Y + 9], fill=(30, 26, 22, 255))
    for cy, cx in zip(*np.nonzero(C == '^')):
        X, Y = cx * S, cy * S
        d.rectangle([X + 2, Y + 2, X + S - 3, Y + S - 3], fill=(44, 46, 50, 255), outline=(20, 20, 24, 255))
        for i in range(3):
            for k in range(3): d.ellipse([X + 6 + i * 8, Y + 6 + k * 8, X + 9 + i * 8, Y + 9 + k * 8], fill=(14, 14, 16, 255))
    for ch, nm in (('U', 'stairs_up'), ('V', 'stairs_down')):
        for cy, cx in zip(*np.nonzero(C == ch)): paste(pil, nm, cx * S + 16, cy * S + 31, .9)
    glow = Image.new('RGBA', pil.size); gd = ImageDraw.Draw(glow)
    for cy, cx in zip(*np.nonzero(C == 't')):
        X, Y = cx * S + 16, cy * S + 10
        for r_ in range(44, 4, -4): gd.ellipse([X - r_, Y - r_ * .8, X + r_, Y + r_ * .8], fill=(255, 150, 60, int(10 * (1 - r_ / 48))))
    pil = Image.alpha_composite(pil, glow)
    return np.asarray(pil.convert('RGB')).astype(np.float32) / 255

def main():
    ids = sys.argv[1:] or ['field00', 'field01', 'dungeon01_b1', 'dungeon01_b2', 'boss01']
    for mid in ids:
        j = json.load(open(R + 'maps/' + mid + '.json'))
        img = paint_field(j) if j['type'] == 'field' else paint_dungeon(j, boss=j['type'] == 'boss')
        save(img, mid)
if __name__ == '__main__': main()
