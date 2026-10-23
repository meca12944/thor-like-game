"""HD map test (owner 10-23 「펠트 마을을 최고 퀄리티로」, with the town-art room): a small square built at the hero's pixel density
(D = 3 art px per world px) to prove the game path for the "hd" map block (world.js): one big ground picture + separate,
y-sorted buildings/props (hero walks behind them, they turn see-through) + code light pools.
Parts = the town-art room's PixelLab trial parts (handoff/claude/felt_hd on claude/linette-8dir), copied to parts_src/.
python3 tools/hd/build_hd_test.py  -> maps/felt_hd_test.json + assets/world/hd_test/*.png   (?go=felt_hd_test)"""
import os, json, random
from collections import deque
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
OUT = os.path.join(ROOT, 'assets', 'world', 'hd_test'); os.makedirs(OUT, exist_ok=True)
D, TW, TH, T = 3, 26, 18, 16; W, H = TW * T * D, TH * T * D; R = random.Random(7)

def cut(path):  # PixelLab parts can come on a flat grey card: flood-fill it away from the corners, crop
    im = Image.open(path).convert('RGBA'); a = np.array(im).astype(int); h, w = a.shape[:2]
    if a[0, 0, 3] > 0:
        seen = np.zeros((h, w), bool); q = deque([(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]); bg = a[0, 0, :3]
        while q:
            y, x = q.popleft()
            if y < 0 or x < 0 or y >= h or x >= w or seen[y, x]: continue
            if np.abs(a[y, x, :3] - bg).sum() > 24 and a[y, x, 3] > 0: continue
            seen[y, x] = True; q.extend([(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)])
        a[seen, 3] = 0
    im = Image.fromarray(a.astype(np.uint8), 'RGBA'); return im.crop(im.getbbox())

# ---- ground at D=3: Voronoi cobbles (plaza), a winding dirt lane, ash grass round the edges (fixed palette, no smoothing)
PAL = {'mortar': (34, 28, 30), 'st': [(84, 76, 78), (96, 88, 88), (74, 68, 72), (108, 98, 94)], 'hi': (126, 116, 110), 'lo': (52, 46, 50),
       'dirt': [(78, 64, 54), (70, 58, 50), (86, 72, 60)], 'grass': [(70, 74, 62), (60, 66, 56), (80, 82, 68)]}
yy, xx = np.mgrid[0:H, 0:W]
pts = np.array([(x + R.uniform(-4, 4), y + R.uniform(-4, 4)) for y in range(0, H + 12, 11) for x in range(0 if (y // 11) % 2 == 0 else 5, W + 12, 11)])
d, i = cKDTree(pts).query(np.stack([xx.ravel(), yy.ravel()], 1), k=2); d = d.reshape(H, W, 2); i = i[:, 0].reshape(H, W)
g = np.array(PAL['st'])[i % 4].astype(np.uint8)
edge = (d[:, :, 1] - d[:, :, 0]) < 1.5; g[edge] = PAL['mortar']
near = (d[:, :, 1] - d[:, :, 0]) < 3.0; ctr = pts[i]; up = (yy - ctr[:, :, 1]) + (xx - ctr[:, :, 0]) < 0
g[near & ~edge & up] = PAL['hi']; g[near & ~edge & ~up] = PAL['lo']
lane = np.abs((yy - H * .62) - (xx - W * .5) * .12) < 34 + 9 * np.sin(xx / 41.0)
g[lane] = np.array(PAL['dirt'])[(xx * 7 + yy * 13) % 3][lane]
rim = (yy < 30 + 12 * np.sin(xx / 47.0)) | (yy > H - 70 - 16 * np.sin(xx / 53.0)) | (xx < 36 + 10 * np.sin(yy / 31.0)) | (xx > W - 36 - 10 * np.sin(yy / 29.0))
g[rim] = np.array(PAL['grass'])[((xx // 2) * 3 + (yy // 2) * 5) % 3][rim]
Image.fromarray(g, 'RGB').save(os.path.join(OUT, 'ground.png'), optimize=True)

# ---- props: foot point in map tiles; solid = footprint rows just above the foot
SPEC = [  # file, foot x, foot y (tiles), footprint depth in tiles (0 = walk-through), fade
 ('chapel', 5.0, 7.2, 3, 1), ('atelier_v2', 13.0, 7.0, 3, 1), ('house_v2', 21.0, 7.2, 3, 1), ('burned_v2', 5.0, 15.2, 3, 1),
 ('crates', 17.6, 8.6, 1, 0), ('cart', 9.5, 10.6, 1, 0), ('lamp', 10.5, 8.0, 1, 0), ('lamp', 16.5, 11.6, 1, 0), ('brazier', 20.0, 12.4, 1, 0)]
props = []; solids = set()
for n, (f, fx, fy, depth, fade) in enumerate(SPEC):
    im = cut(os.path.join(HERE, 'parts_src', f + '.png')); name = f'{f}.png'; im.save(os.path.join(OUT, name), optimize=True)
    wt = im.width / (T * D); p = {'id': f'{f}_{n}', 'img': f'assets/world/hd_test/{name}', 'x': fx, 'y': fy, 'ax': im.width / 2, 'ay': im.height, 'fade': fade, 'shadow': 1}
    if depth:
        x0, x1 = int(round(fx - wt * .42)), int(round(fx + wt * .42)) - (1 if depth == 1 else 0); y1 = int(fy - .01); y0 = y1 - depth + 1
        if depth == 1: x0 = x1 = int(fx)
        p['solid'] = [x0, y0, x1, y1]
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): solids.add((x, y))
    props.append(p)
lights = [[10.5, 6.4, 60, '#ffb060', .8], [16.5, 10.0, 60, '#ffb060', .8], [20.0, 11.6, 70, '#ff8a3a', 1], [5.0, 6.4, 40, '#ffd27a', .6], [13, 5.6, 40, '#ffc070', .5]]
rows = [''.join('#' if x in (0, TW - 1) or y in (0, TH - 1) else '.' for x in range(TW)) for y in range(TH)]
m = {'id': 'felt_hd_test', 'type': 'field', 'area': 1, 'region': 'ch1', 'name': '펠트 HD 시험 광장', 'title': {'kicker': '시험', 'name': '펠트 HD 시험', 'sub': '점 크기 3배 · 따로 세운 건물'},
     'bgm': 'town_ruin', 'battleBgm': 'battle_champion', 'tileset': 'field', 'tile': T, 'w': TW, 'h': TH, 'legend': {'.': 'dirt', '#': 'cliff'}, 'solid': ['#'],
     'spawns': {'default': [13.5, 14.5, 'up']}, 'objects': [{'type': 'sign', 'x': 13, 'y': 12, 'text': '점 크기 3배 시험 광장.\n건물 뒤로 걸어가 보세요 — 건물이 반투명해집니다.'}],
     'ground': rows, 'hd': {'D': D, 'ground': 'assets/world/hd_test/ground.png', 'props': props, 'lights': lights, 'grade': 'dusk'},
     'note': 'GENERATED by tools/hd/build_hd_test.py'}
json.dump(m, open(os.path.join(ROOT, 'maps', 'felt_hd_test.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', W, H, len(props), 'props', len(solids), 'solid tiles')
