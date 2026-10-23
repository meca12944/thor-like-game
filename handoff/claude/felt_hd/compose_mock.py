"""Felt HD mock: one plaza slice (24x14 tiles) built at the hero's pixel density (D=3 px per world px) to compare with the current in-game Felt.
Ground = code (Voronoi cobbles + dirt + ash grass, fixed palette, dither), buildings/props = PixelLab parts (low top-down, chapel palette),
light = code (dusk grade, dithered shadows, lamp/brazier glow). 0 credits. python3 compose_mock.py -> mock_d3.png"""
import sys, json, math, random
import numpy as np
from PIL import Image
sys.path.insert(0, '../linette_final_v1'); from pxscale import pxscale
D, TW, TH = 3, 24, 14; W, H = TW * 16 * D, TH * 16 * D; R = random.Random(7)
# ---- ground: Voronoi cobbles on a plaza, a dirt lane, ash grass at the bottom edge
PAL = {'mortar': (34, 28, 30), 'st': [(84, 76, 78), (96, 88, 88), (74, 68, 72), (108, 98, 94)], 'hi': (128, 118, 112), 'lo': (52, 46, 50),
       'dirt': [(78, 64, 54), (70, 58, 50), (86, 72, 60)], 'grass': [(70, 74, 62), (60, 66, 56), (80, 82, 68)]}
yy, xx = np.mgrid[0:H, 0:W]
pts = np.array([(x + R.uniform(-5, 5), y + R.uniform(-5, 5)) for y in range(0, H + 14, 13) for x in range(0 if (y // 13) % 2 == 0 else 6, W + 14, 13)])
from scipy.spatial import cKDTree
t = cKDTree(pts); d, i = t.query(np.stack([xx.ravel(), yy.ravel()], 1), k=2); d = d.reshape(H, W, 2); i = i[:, 0].reshape(H, W)
g = np.zeros((H, W, 3), np.uint8); st = np.array(PAL['st'])[i % 4]; g[:] = st
edge = (d[:, :, 1] - d[:, :, 0]) < 1.6; g[edge] = PAL['mortar']
# bevel: top-left of each stone lighter, bottom-right darker (pixels near the edge)
near = (d[:, :, 1] - d[:, :, 0]) < 3.2; ctr = pts[i]; up = (yy - ctr[:, :, 1]) + (xx - ctr[:, :, 0]) < 0
g[near & ~edge & up] = PAL['hi']; g[near & ~edge & ~up] = PAL['lo']
# dirt lane (diagonal band) and ash grass along the bottom
lane = np.abs((yy - H * .55) - (xx - W * .5) * .18) < 40 + 10 * np.sin(xx / 37.0)
dn = np.array(PAL['dirt'])[(xx * 7 + yy * 13) % 3]; g[lane] = dn[lane]
grass = yy > H - 60 - 18 * np.sin(xx / 53.0); gn = np.array(PAL['grass'])[((xx // 2) * 3 + (yy // 2) * 5) % 3]; g[grass] = gn[grass]
img = Image.fromarray(g, 'RGB').convert('RGBA')
def cut(path):  # PixelLab parts come on a flat grey card: flood-fill it away from the corners
    im = Image.open(path).convert('RGBA'); a = np.array(im).astype(int); h, w = a.shape[:2]
    from collections import deque
    seen = np.zeros((h, w), bool); q = deque([(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]); bg = a[0, 0, :3]
    while q:
        y, x = q.popleft()
        if y < 0 or x < 0 or y >= h or x >= w or seen[y, x]: continue
        if np.abs(a[y, x, :3] - bg).sum() > 24 and a[y, x, 3] > 0: continue
        seen[y, x] = True; q.extend([(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)])
    a[seen, 3] = 0; return Image.fromarray(a.astype(np.uint8), 'RGBA').crop(Image.fromarray(a.astype(np.uint8), 'RGBA').getbbox())
def shadow(cx, by, w):  # dithered contact shadow under a footprint
    s = np.array(img); rx, ry = w * .55, max(8, w * .12)
    for y in range(int(by - ry), int(by + ry)):
        for x in range(int(cx - rx + ry * .6), int(cx + rx + ry * .6)):
            if 0 <= x < W and 0 <= y < H and ((x - cx - ry * .6) / rx) ** 2 + ((y - by) / ry) ** 2 <= 1 and ((x + y) % 2 == 0 or ((x - cx) / rx) ** 2 < .5):
                s[y, x, :3] = (s[y, x, :3] * .55).astype(np.uint8)
    return Image.fromarray(s, 'RGBA')
items = []  # (path, foot x, foot y)
P = 'parts/'
for f, x, y in [('chapel.png', 190, 300), ('atelier_v2.png', 600, 290), ('house_v2.png', 960, 300), ('burned_v2.png', 170, 640), ('crates.png', 820, 360), ('cart.png', 420, 420),
                ('lamp.png', 470, 330), ('lamp.png', 760, 470), ('brazier.png', 905, 520)]:
    items.append((cut(P + f), x, y))
for im, x, y in sorted(items, key=lambda t: t[2]):
    img = shadow(x, y - 4, im.width * .8); img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height)))
# ---- characters at their own density, scaled to D (hero atlas 117 px figure = 30 world px)
s = open('../../../test128/index.html').read(); k = s.index('/*H8*/const H8='); H8, _ = json.JSONDecoder().raw_decode(s[s.index('{', k):])
f0 = H8['anims']['idle_down'][0]; cx, cy, cw, ch, ax, ay = H8['cells'][f0[0]][f0[1]][:6]
hs = Image.open('../../../test128/assets/' + H8['sheets'][f0[0]].split('?')[0]).convert('RGBA').crop((cx, cy, cx + cw, cy + ch)); hs = pxscale(hs, D * 30 / 117)
def place(sp, x, y, ax, ay, sc):
    global img; img = shadow(x, y, sp.width * .7); img.alpha_composite(sp, (int(x - ax * sc), int(y - ay * sc)))
place(hs, 600, 520, ax, ay, D * 30 / 117)
for nm, x, y in [('toby', 300, 470), ('ben', 680, 330)]:
    try:
        j = json.load(open(f'../../../test128/assets/npcs/felt/felt_{nm}.json')); c = j['cells'][0][0]; sh = Image.open('../../../test128/assets/npcs/felt/' + j['sheets'][0]).convert('RGBA').crop((c[0], c[1], c[0] + c[2], c[1] + c[3]))
        sc = D * 30 / 117; place(pxscale(sh, sc), x, y, c[4], c[5], sc)
    except Exception as e: print('npc', nm, e)
# ---- dusk grade + warm light pools (dithered) + ash
a = np.array(img).astype(float); a[:, :, :3] *= np.array([.86, .82, .9]); a[:, :, :3] += np.array([6, 2, 10])
for lx, ly, r in [(470, 200, 120), (760, 340, 120), (905, 470, 110), (600, 230, 90)]:
    dd = np.hypot(xx - lx, (yy - ly) * 1.3); w = np.clip(1 - dd / r, 0, 1) ** 1.6; dith = ((xx + yy) % 2) * .06
    a[:, :, 0] += (w + dith * (w > 0)) * 70; a[:, :, 1] += (w + dith * (w > 0)) * 42; a[:, :, 2] += w * 10
a = np.clip(a, 0, 255).astype(np.uint8); out = Image.fromarray(a.copy(), 'RGBA').copy()
px = out.load()
for n in range(260): x, y = R.randrange(W), R.randrange(H); px[x, y] = (200, 194, 206, 255) if n % 6 else (255, 170, 110, 255)
out.save('mock_d3.png'); print('ok', out.size)
