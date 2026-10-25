"""Organic HD field generator (option A): noise forest/rock border, Catmull-Rom road, river/lake/sea/lava,
2-3 landmarks, Wang-autotiled PixelLab ground (D=3, 32px tiles = 2/3 cell), props + legend decos.
Usage: python3 build.py [field03 ...]   (writes maps/<id>.json + assets/world/fields_hd/<id>_ground.png)"""
import json, os, sys, math, random
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wang, props
ROOT = props.ROOT; HERE = os.path.dirname(os.path.abspath(__file__)); SETS = os.path.join(HERE, 'sets')
D = 3; CELL = 48
OUT = 'assets/world/fields_hd'
SOLID = ['#', 'T', 'P', 'R', 'r', 'u', 'L', '~']
B = {
 'field_felt': dict(P='p_ffelt', W='w_ffelt', entr='north', water='river', hop=True, seed=11,
   T=['ash_tree_a', 'ash_tree_b', 'dead_tree'], Pt=['burnt_pine_a', 'burnt_pine_b'], R=['boulder'], r=['stone_low'], u=['ash_bush', 'bush_b'],
   s=['stump', 'pale_mushrooms'], w=['dry_reeds'], tmix=.6, lms=[('ring', 'ruin_pillar', '무너진 석주 고리'), ('bridge',), ('group', ['mausoleum', 'thread_stake'], '잿빛 묘소')],
   tuft=['#5b5646', '#6b6450', '#4a473b'], fx={'particles': 'ash', 'birds': 3}, gr={'sat': .74}),
 'field02': dict(P='p_f02', W='w_f02', water='lake', seed=21, T=['stalag'], Pt=['stalag'], R=['boulder'], r=['crystal'], u=['crystal'], s=['rubble'], w=[],
   tmix=.5, rockband=True, lms=[('single', 'lm_cave', 0, '거대 자수정'), ('cluster', 'crystal', '수정 군락'), ('single', 'lm_cave', 3, '부서진 수정 제단')],
   tuft=None, fx={'particles': 'motes'}, gr={'sat': .7, 'gain': .92}, wlift=(26, 24, 36)),
 'field03': dict(P='p_f03', W='w_f03', water='lake', seed=31, T=['desert_rock'], Pt=['sandruin'], R=['desert_rock'], r=['desert_rock'], u=['desert_rock'], s=[], w=[],
   tmix=.75, rockband=True, palms=True, lms=[('single', 'lm_desert', 0, '모래에 묻힌 거상'), ('oasis', 'palm', '오아시스'), ('row', 'sandruin', '무너진 열주')],
   tuft=['#8a7a52', '#9a8960'], tuftp=.08, fx={'particles': 'dust', 'birds': 2}, gr={'sat': .78}),
 'field04': dict(P='p_f04', W='w_f03', water='lake', lake_r=3.2, seed=41, T=['sandruin'], Pt=['desert_rock'], R=['desert_rock'], r=['desert_rock'], u=['desert_rock'], s=[], w=[],
   tmix=.5, rockband=True, palms=True, lms=[('single', 'lm_pyramid', 1, '모래 피라미드'), ('row', 'sandruin', '파라오의 길'), ('single', 'lm_desert', 3, '잠든 왕의 머리')],
   tuft=['#8a7a52'], tuftp=.05, fx={'particles': 'dust'}, gr={'sat': .76}),
 'field05': dict(P='p_f05', W='w_f05', water='sea', seed=51, T=['palm'], Pt=['coastpine'], R=['desert_rock'], r=['coral'], u=['coral'], s=['rubble'], w=[],
   tmix=.55, lms=[('single', 'lm_wreck', 0, '좌초한 범선'), ('cluster', 'coral', '마른 산호초'), ('single', 'lm_wreck', 2, '부서진 뱃머리')],
   tuft=['#8c8a62', '#7a7a58'], tuftp=.06, fx={'particles': None, 'birds': 3}, gr={'sat': .7, 'gain': .95}, wdesat=.6),
 'field06': dict(P='p_f06', W='w_f06', water='sea', seed=61, T=['coastpine'], Pt=['oak'], R=['boulder'], r=['stone_low'], u=['bush_b'], s=['stump'], w=['dry_reeds'],
   tmix=.6, lms=[('single', 'lm_lighthouse', 0, '꺼진 등대'), ('ring', 'ruin_pillar', '바람의 석주'), ('single', 'lm_wreck', 1, '절벽 아래 난파선')],
   tuft=['#5e6a4c', '#6c7656', '#4f5a40'], fx={'birds': 4, 'butterflies': 3}, gr={'sat': .58, 'gain': .9}, wdesat=.3),
 'field07': dict(P='p_f07', W='w_f07', water='lava', seed=71, T=['dead_tree'], Pt=['burnt_pine_a', 'burnt_pine_b'], R=['basalt'], r=['basalt'], u=['basalt'], s=['rubble'], w=[],
   tmix=.4, rockband=True, lms=[('single', 'lm_vfort', 0, '화산 요새 잔해'), ('cluster', 'basalt', '현무암 기둥'), ('single', 'lm_vfort', 2, '불탄 망루')],
   tuft=None, fx={'particles': 'embers'}, gr={'sat': .72, 'gain': .92}),
 'field08': dict(P='p_f08', W='w_f08', water='lake', seed=81, T=['pine_snow'], Pt=['pine_snow'], R=['snowrock'], r=['snowrock'], u=['snowrock'], s=['stump'], w=[],
   tmix=.5, lms=[('single', 'lm_frosttower', 0, '뇌전 첨탑'), ('ring', 'ruin_pillar', '얼어붙은 석주'), ('single', 'lm_frosttower', 3, '눈 덮인 감시탑')],
   tuft=None, fx={'particles': 'snow'}, gr={'sat': .75}),
 'field09': dict(P='p_f09', W='w_f09', water='river', seed=91, T=['dead_tree', 'ash_tree_b'], Pt=['temple'], R=['boulder'], r=['rubble'], u=['ash_bush'], s=['pale_mushrooms'], w=['dry_reeds'],
   tmix=.7, lms=[('single', 'lm_temple', 0, '어둠 신전 입구'), ('row', 'temple', '부러진 신전 기둥'), ('group', ['mausoleum', 'rubble'], '이름 없는 묘')],
   tuft=['#4e4652', '#5a5160'], fx={'particles': 'motes', 'birds': 2}, gr={'sat': .7, 'gain': .92}, wlift=(18, 16, 22)),
}
CAT = None
def cat(): 
    global CAT
    if CAT is None: CAT = props.catalog(build=False)
    return CAT
def crom(pts, step=.04):
    P = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.array, P[i - 1:i + 3])
        for t in np.arange(0, 1, step):
            t2, t3 = t * t, t * t * t
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(np.array(pts[-1])); return out
def disk(mask, x, y, r):
    h, w = mask.shape; x0, x1 = max(0, int(x - r - 1)), min(w, int(x + r + 2)); y0, y1 = max(0, int(y - r - 1)), min(h, int(y + r + 2))
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            if (xx + .5 - x) ** 2 + (yy + .5 - y) ** 2 <= r * r: mask[yy, xx] = True
def bfs(free, sx, sy):
    h, w = free.shape; seen = np.zeros_like(free); q = [(sx, sy)]; seen[sy, sx] = True
    while q:
        x, y = q.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            X, Y = x + dx, y + dy
            if 0 <= X < w and 0 <= Y < h and free[Y, X] and not seen[Y, X]: seen[Y, X] = True; q.append((X, Y))
    return seen
def pdims(v, Dq):  # prop footprint in cells
    return v['w'] / Dq / 16, v['h'] / Dq / 16
def gen(mid, cfg, orig):
    w, h = 56, 36; seed = cfg['seed']; rnd = random.Random(seed); C = cat()
    yy, xx = np.mgrid[0:h, 0:w]
    de = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)).astype(float)
    band = 1.7 + 3.3 * wang.vnoise(h, w, 6, seed)
    S = de < band
    water = np.zeros((h, w), bool); road = np.zeros((h, w), bool); clear = np.zeros((h, w), bool); bridge = np.zeros((h, w), bool)
    north = cfg.get('entr') == 'north'
    if north:
        ex = w // 2; ent = (ex, 0); spawn = [ex + .5, 2.5, 'down']
        for y in range(9):
            half = 3.2 + max(0, y - 3) * .3
            for x in range(w):
                if abs(x + .5 - (ex + .5)) <= half: clear[y, x] = True
    else:
        ey = h // 2; ent = (0, ey); spawn = [2.5, ey + .5, 'right']
        for x in range(9):
            half = 3.2 + max(0, x - 3) * .3
            for y in range(h):
                if abs(y + .5 - ey) <= half: clear[y, x] = True
    wt = cfg['water']; Lx = w - 11; Ly = rnd.randint(int(h * .3), int(h * .62))
    if wt == 'sea': Lx = w - 20
    xr0 = int(w * (.66 if north else .5)); yb = rnd.randint(int(h * .38), int(h * .62))
    if north:
        pts = [(ex + .5, -1), (ex + .5, 5), (ex - 1.5, h * .32), (ex + 1, yb - 1.5), (xr0 - 4, yb + .5), (xr0 + 4, yb + .5), (w - 6, yb - 2), (w - 3.5, yb - 2.5)]
    elif wt == 'river':
        pts = [(-1, ey), (5, ey), (w * .24, ey + rnd.uniform(-4, 4)), (xr0 - 4, yb + .5), (xr0 + 4, yb + .5), (w * .78, (yb + Ly) / 2 + rnd.uniform(-2, 2)), (Lx + .5, Ly + 2.2)]
    else:
        pts = [(-1, ey), (5, ey), (w * .3, ey + rnd.uniform(-5, 5)), (w * .55, ey + rnd.uniform(-5, 5)), (w * .78 if wt != 'sea' else w * .62, Ly + rnd.uniform(-3, 3)), (Lx + .5, Ly + 2.2)]
    path = crom(pts)
    for p in path:
        if 0 <= p[0] < w and 0 <= p[1] < h: disk(road, p[0], p[1], 1.3); disk(clear, p[0], p[1], 2.8)
    nzc = wang.vnoise(h + 8, 8, 5, seed + 5)[:, 3]
    if wt == 'river':
        for y in range(h):
            off = 4.5 * math.sin((y - yb) / 5.5) * min(1, abs(y - yb) / 4) + 3 * (nzc[y] - .5)
            hw = 1.2 if abs(y - yb) <= 2 else 1.25 + .4 * nzc[y + 3]
            for x in range(w):
                if abs(x + .5 - (xr0 + .5 + off)) <= hw: water[y, x] = True
        for y in range(yb - 1, yb + 2):
            for x in range(w):
                if water[y, x]: bridge[y, x] = True
    elif wt == 'sea':
        cx = w - 12 + 11 * (wang.vnoise(h + 8, 8, 6, seed + 6)[:h, 3] - .55) + 3 * (wang.vnoise(h + 8, 8, 2, seed + 8)[:h, 5] - .5)
        for y in range(h): water[y, :] = xx[y] > cx[y]
        S &= ~(xx > w - 18)
        S |= (de < band) & (xx > w - 18) & ((yy < 2.5 + 2 * wang.vnoise(h, w, 5, seed + 9)) | (yy > h - 3.5 - 2 * wang.vnoise(h, w, 5, seed + 9)))
    if wt in ('lake', 'lava'):
        n = 2 if wt == 'lava' else 1; r0 = cfg.get('lake_r', 3.4 if wt == 'lava' else 4.6)
        dist_road = ndimage.distance_transform_edt(~road)
        for k in range(n):
            for _ in range(400):
                cx, cy = rnd.uniform(10, w - 10), rnd.uniform(8, h - 8)
                if dist_road[int(cy), int(cx)] < r0 + 3 or abs(cx - Lx) + abs(cy - Ly) < 14 or (cx < 14 and not north): continue
                if water[max(0, int(cy - r0 - 4)):int(cy + r0 + 4), max(0, int(cx - r0 - 4)):int(cx + r0 + 4)].any(): continue
                break
            ang = np.arctan2(yy + .5 - cy, xx + .5 - cx); rr = np.hypot(xx + .5 - cx, (yy + .5 - cy) * 1.25)
            wob = .78 + .22 * np.sin(ang * 3 + seed + k) + .12 * np.sin(ang * 5 + k * 2)
            water |= rr < r0 * wob * 1.25
    if wt != 'river': water &= ~clear; water &= ~road
    S &= ~clear; S &= ~water
    # interior clumps of trees/rocks
    n2 = wang.vnoise(h, w, 5, seed + 3)
    dw = ndimage.distance_transform_edt(~water); dr = ndimage.distance_transform_edt(~road)
    clump = (n2 > .7) & (de > band + 2.5) & ~clear & (dw > 2.5) & (dr > 3)
    S |= clump
    return dict(w=w, h=h, S=S, water=water, road=road, bridge=bridge, clear=clear, spawn=spawn, ent=ent, north=north,
                L0=(Lx, Ly), end=pts[-1], yb=yb, xr0=xr0, de=de, band=band, rnd=rnd)
def place_lms(G, cfg, mid):
    """landmarks: footprint must sit on floor (not road/water); clear border cells inside the margin."""
    w, h = G['w'], G['h']; S, water, road = G['S'], G['water'], G['road']; rnd = G['rnd']; C = cat()
    props_, objs, Lsolid, lmpos = [], [], np.zeros((h, w), bool), []
    dw = ndimage.distance_transform_edt(~water); dr = ndimage.distance_transform_edt(~road)
    ex, ey = G['ent']
    def ok(x, y, fw, fh, strict=True):
        x0, x1, y0, y1 = int(x - fw / 2 - 1), int(math.ceil(x + fw / 2 + 1)), int(y - fh - .5), int(y + 2)
        if x0 < 1 or y0 < 1 or x1 > w - 1 or y1 > h - 1: return False
        if (water[y0:y1, x0:x1].any() or road[y0:y1 - 1, x0:x1].any()): return False
        if abs(x - ex) + abs(y - ey) < 12: return False
        if any(abs(x - a) + abs(y - b) < 11 for a, b in lmpos): return False
        if strict and S[y0:y1, x0:x1].mean() > .35: return False
        return True
    def carve(x, y, fw, fh):
        x0, x1, y0, y1 = int(x - fw / 2 - 1), int(math.ceil(x + fw / 2 + 1)), int(y - fh - .5), int(y + 3)
        S[max(0, y0):y1, max(0, x0):x1] = False
    def find(fw, fh, near=None, pref=None):
        best = None
        for _ in range(3000):
            x, y = rnd.uniform(4, w - 4), rnd.uniform(5, h - 3)
            if not ok(x, y, fw, fh): continue
            s = rnd.random()
            if near == 'water': s += -abs(dw[int(y), int(x)] - 3.5) * 2
            if near == 'road': s += -abs(dr[int(y), int(x)] - 3.5)
            if best is None or s > best[0]: best = (s, x, y)
        return best[1:] if best else None
    lms = list(cfg['lms'])
    if cfg['water'] == 'river' and not any(L[0] == 'bridge' for L in lms): lms.append(('autobridge',))
    for i, L in enumerate(lms):
        kind = L[0]; lid = f'lm_{mid}_{i}' if not (mid == 'field_felt' and kind == 'bridge') else 'lm_bridge00'
        if kind == 'bridge' or (kind == 'autobridge'):
            bx = [x for x in range(w) if G['bridge'][G['yb'], x]]
            if not bx: continue
            cx = (min(bx) + max(bx) + 1) / 2
            props_.append({'img': C['bridge_3'][0]['img'], 'ax': 60, 'ay': 143, 'flip': False, 'id': 'bridge', 'x': round(cx, 2), 'y': G['yb'] + 2, 'under': 1})
            if kind == 'bridge': objs.append({'type': 'landmark', 'id': lid, 'x': int(cx), 'y': G['yb'] - 2, 'name': '개울 다리'})
            lmpos.append((cx, G['yb'])); continue
        if kind == 'single':
            v = C[L[1]][L[2] % len(C[L[1]])]; Dq = 1.5; fw, fh = pdims(v, Dq); fw0 = v['w'] / Dq / 16
            if i == 0: x, y = G['L0'][0] + .5, G['L0'][1] + 1.0
            else:
                p = find(fw * .9, fh * .5, 'water' if i == 1 else 'road'); 
                if not p: print('  no spot for', L); continue
                x, y = p
            carve(x, y, fw, fh * .55)
            sw, sh = max(1, fw * .62), max(1, fh * .32)
            props_.append({'img': v['img'], 'ax': v['ax'], 'ay': v['ay'], 'D': Dq, 'x': round(x, 2), 'y': round(y, 2), 'shadow': 1, 'id': lid})
            Lsolid[int(y - sh):int(math.ceil(y)), int(x - sw / 2):int(math.ceil(x + sw / 2))] = True
            objs.append({'type': 'landmark', 'id': lid, 'x': int(x), 'y': int(y), 'name': L[3]}); lmpos.append((x, y)); continue
        # composite landmarks
        key = L[1]; name = L[-1]
        if kind == 'oasis':
            if G.get('lake') is None: continue
            lx, ly = G['lake']; vs = C['palm']; ang0 = rnd.random() * 6
            for j in range(6):
                a = ang0 + j * 1.05 + rnd.uniform(-.25, .25); r = 5.6 + rnd.uniform(0, 1.2)
                x, y = lx + math.cos(a) * r, ly + math.sin(a) * r * .8
                cx_, cy_ = int(x), int(y)
                if not (2 <= cx_ < w - 2 and 2 <= cy_ < h - 2) or water[cy_, cx_] or road[cy_, cx_]: continue
                v = vs[j % len(vs)]; props_.append({'img': v['img'], 'ax': v['ax'], 'ay': v['ay'], 'x': cx_ + .5, 'y': cy_ + .9, 'shadow': 1, 'flip': j % 2 == 0})
                Lsolid[cy_, cx_] = True; S[cy_, cx_] = False
            objs.append({'type': 'landmark', 'id': lid, 'x': int(lx), 'y': int(ly), 'name': name}); lmpos.append((lx, ly)); continue
        p = find(7, 5, 'road')
        if not p: print('  no spot for', L); continue
        x, y = p; carve(x, y, 7, 5); pieces = []
        if kind == 'ring':
            for j in range(6):
                if j == 4: continue  # one fallen gap
                a = j * math.pi / 3 + .3; pieces.append((key, x + math.cos(a) * 2.6, y - 1 + math.sin(a) * 1.9))
            pieces.append(('rubble', x + math.cos(4 * math.pi / 3 + .3) * 2.6, y - 1 + math.sin(4 * math.pi / 3 + .3) * 1.9))
        elif kind == 'row':
            for j in range(4): pieces.append((key, x - 3.6 + j * 2.4, y - 2.2)); pieces.append((key, x - 3.6 + j * 2.4, y + .6)) if j % 3 != 1 else None
        elif kind == 'cluster':
            for j in range(6): a = rnd.uniform(0, 6.28); r = rnd.uniform(.6, 2.6); pieces.append((key, x + math.cos(a) * r * 1.2, y - 1 + math.sin(a) * r * .8))
        elif kind == 'group':
            pieces.append((key[0], x, y - 1.2)); pieces.append((key[1], x - 2.6, y + .6)); pieces.append((key[1], x + 2.6, y + .4))
        used = set()
        for j, (k_, px, py) in enumerate(sorted(pieces, key=lambda t: t[2])):
            cx_, cy_ = int(px), int(py)
            if (cx_, cy_) in used or not (1 <= cx_ < w - 1 and 1 <= cy_ < h - 1): continue
            used.add((cx_, cy_)); vs = C[k_]; v = vs[j % len(vs)]
            props_.append({'img': v['img'], 'ax': v['ax'], 'ay': v['ay'], 'x': cx_ + .5, 'y': cy_ + .9, 'shadow': 1, 'flip': j % 2 == 1})
            fw = max(1, int(round(v['w'] / 3 / 16 * .6)))
            Lsolid[cy_, max(0, cx_ - fw // 2):cx_ - fw // 2 + fw] = True
        objs.append({'type': 'landmark', 'id': lid, 'x': int(x), 'y': int(y), 'name': name}); lmpos.append((x, y))
    return props_, objs, Lsolid, lmpos
def build(mid):
    cfg = B[mid]; orig = json.load(open(os.path.join(HERE, 'orig', mid + '.json'))); C = cat()
    G = gen(mid, cfg, orig); w, h = G['w'], G['h']; S, water, road, bridge = G['S'], G['water'], G['road'], G['bridge']
    if cfg['water'] in ('lake', 'lava'):
        lab, n = ndimage.label(water); 
        if n: cy, cx = ndimage.center_of_mass(water, lab, 1 + int(np.argmax(ndimage.sum(water, lab, range(1, n + 1))))); G['lake'] = (cx + .5, cy + .5)
    pr, lobjs, Lsolid, lmpos = place_lms(G, cfg, mid)
    rnd = G['rnd']
    grid = np.full((h, w), '.', dtype='<U1')
    grid[road] = '='; grid[water] = '~'; grid[bridge] = 'b'; grid[S] = '#'; grid[Lsolid] = 'L'
    free = ~np.isin(grid, ['#', 'L', '~'])
    sx, sy = int(G['spawn'][0]), int(G['spawn'][1])
    reach = bfs(free, sx, sy)
    grid[free & ~reach] = '#'
    # decorate band edges with trees / rocks
    floor = np.isin(grid, ['.', '=', 'b'])
    nb = ndimage.binary_dilation(floor, structure=np.ones((3, 3)))
    rock = cfg.get('rockband')
    for y in range(h):
        for x in range(w):
            if grid[y, x] != '#': continue
            edge = nb[y, x]; r = rnd.random()
            if edge:
                if r < .62: grid[y, x] = 'T' if rnd.random() < cfg['tmix'] else 'P'
                elif r < .8: grid[y, x] = 'R'
            elif r < (.45 if not rock else .3): grid[y, x] = 'T' if rnd.random() < cfg['tmix'] else 'P'
            elif rock and r < .55: grid[y, x] = 'R'
    # floor scatter (single obstacles, never two solids touching -> cannot cut paths)
    dw = ndimage.distance_transform_edt(grid != '~'); dr = ndimage.distance_transform_edt(grid != '=')
    nearent = np.zeros((h, w), bool); disk(nearent, sx + .5, sy + .5, 6)
    nearlm = ndimage.binary_dilation(Lsolid, iterations=2)
    ssolid = np.zeros((h, w), bool)
    for y in range(2, h - 2):
        for x in range(2, w - 2):
            if grid[y, x] != '.' or nearent[y, x] or nearlm[y, x]: continue
            win = grid[y - 1:y + 2, x - 1:x + 2]
            if not np.isin(win, ['.', 'w', 's']).all() or ssolid[y - 1:y + 2, x - 1:x + 2].any(): 
                if cfg['w'] and dw[y, x] <= 1.5 and rnd.random() < .18: grid[y, x] = 'w'
                continue
            r = rnd.random()
            if cfg['w'] and dw[y, x] <= 1.5 and r < .18: grid[y, x] = 'w'
            elif dr[y, x] < 2: continue
            elif r < .03: grid[y, x] = 'u'; ssolid[y, x] = True
            elif r < .05: grid[y, x] = 'r'; ssolid[y, x] = True
            elif r < .062: grid[y, x] = 'T'; ssolid[y, x] = True
            elif r < .09 and cfg['s']: grid[y, x] = 's'
    # final reachability (scatter may never cut anything, but verify)
    free = ~np.isin(grid, SOLID + ['L'])
    if cfg.get('hop'): free |= grid == '~'
    reach = bfs(free, sx, sy)
    if not cfg.get('hop'): grid[free & ~reach] = '#'
    free = ~np.isin(grid, SOLID + ['L']); reach = bfs(free, sx, sy) if not cfg.get('hop') else bfs(free | (grid == '~'), sx, sy)
    floor_cells = [(x, y) for y in range(h) for x in range(w) if grid[y, x] in '.=s' and reach[y, x]]
    # objects: exit, sign, mobs, specials
    objs = []
    if G['north']:
        ex = w // 2; objs.append({'type': 'exit', 'x': ex - 3, 'y': 0, 'w': 7, 'h': 1, 'to': 'felt', 'spawn': 'field', 'label': '펠트 마을'})
    else:
        ey = h // 2; ex0 = [o for o in orig['objects'] if o['type'] == 'exit'][0]
        objs.append(dict(ex0, x=0, y=ey - 3, w=1, h=6))
    taken = set()
    def spot(cond, far=(), mind=4, tries=4000):
        for _ in range(tries):
            x, y = rnd.choice(floor_cells)
            if (x, y) in taken or grid[y, x] == '=' or not cond(x, y): continue
            if any(abs(x - a) + abs(y - b) < mind for a, b in far): continue
            taken.add((x, y)); return x, y
    for o in orig['objects']:
        if o['type'] == 'sign' and ('월드맵' in o.get('text', '') or '펠트 마을' in o.get('text', '')):
            if G['north']: objs.append(dict(o, x=w // 2 - 3, y=7)); 
            else: objs.append(dict(o, x=4, y=h // 2 - 4))
            grid[objs[-1]['y'], objs[-1]['x']] = '.'
    objs += lobjs
    mobs = [o for o in orig['objects'] if o['type'] == 'spawn']; placed = []
    for o in mobs:
        p = spot(lambda x, y: abs(x - sx) + abs(y - sy) > 12 and all(abs(x - a) + abs(y - b) > 3 for a, b in lmpos), placed, 5)
        if p: objs.append(dict(o, x=p[0], y=p[1])); placed.append(p)
    keep = [o for o in orig['objects'] if o['type'] in ('waystone', 'chest', 'champion', 'clue') or (o['type'] == 'sign' and o not in [x for x in objs])]
    for o in keep:
        if o['type'] == 'sign' and ('월드맵' in o.get('text', '') or '펠트 마을' in o.get('text', '')): continue
        if o['type'] == 'sign' and '왕도' in o.get('text', ''):
            p = spot(lambda x, y: abs(x - G['end'][0]) + abs(y - G['end'][1]) < 4 and dr[y, x] < 2.5, placed, 1)
        elif o['type'] == 'waystone': p = spot(lambda x, y: 5 < abs(x - sx) + abs(y - sy) < 14 and dr[y, x] < 3, placed, 3)
        elif o['type'] == 'champion': p = spot(lambda x, y: abs(x - sx) + abs(y - sy) > 30, placed, 4)
        elif o['type'] == 'chest': p = spot(lambda x, y: (dw[y, x] < 4 or G['de'][y, x] < G['band'][y, x] + 3) and abs(x - sx) + abs(y - sy) > 20, placed, 4)
        elif o['type'] == 'clue': p = spot(lambda x, y: 12 < abs(x - sx) + abs(y - sy) < 30 and dr[y, x] > 3, placed, 4)
        else: p = spot(lambda x, y: dr[y, x] < 2.5 and abs(x - sx) + abs(y - sy) > 25, placed, 4)
        if p: objs.append(dict(o, x=p[0], y=p[1])); placed.append(p)
        else: print('  !! no spot for', o.get('id') or o['type'])
    # solid objects must not block a 1-wide corridor: verify reachability after blocking them
    free2 = free.copy()
    for o in objs:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'door'): free2[o['y'], o['x']] = False
    r2 = bfs(free2 | ((grid == '~') if cfg.get('hop') else False), sx, sy)
    lost = int((reach & free2 & ~r2).sum())
    # ---- ground image (Wang) ----
    P = wang.load_set(os.path.join(SETS, cfg['P'])); W = wang.load_set(os.path.join(SETS, cfg['W'])); W = wang.unify_base(W, P)
    tw, th = w * 3 // 2, h * 3 // 2
    wi = ndimage.gaussian_filter(np.isin(grid, ['~', 'b']).astype(float), .95)
    pi = ndimage.gaussian_filter(((grid == '=')).astype(float), .85)
    vy, vx = np.mgrid[0:th + 1, 0:tw + 1] / 1.5 - .5
    ws = ndimage.map_coordinates(wi, [vy, vx], order=1, mode='nearest'); ps = ndimage.map_coordinates(pi, [vy, vx], order=1, mode='nearest')
    nz = (wang.vnoise(th + 1, tw + 1, 3, seed=cfg['seed'] + 40) - .5) * .32 + (wang.vnoise(th + 1, tw + 1, 7, seed=cfg['seed'] + 41) - .5) * .2
    V = np.ones((th + 1, tw + 1), int); V[ws + nz > .48] = 0; V[(ps + nz > .4) & (ws < .12)] = 2
    img = np.array(wang.compose(V, P, W, seed=cfg['seed'], mottle=cfg.get('mottle', .13), gr=cfg.get('gr'))).astype(np.float32)
    band = ndimage.gaussian_filter(np.isin(grid, ['#', 'T', 'P', 'R']).astype(float), 1.0)
    bm = np.array(Image.fromarray((band * 255).astype(np.uint8)).resize((img.shape[1], img.shape[0]), Image.BILINEAR)) / 255.
    img *= (1 - .42 * bm)[..., None] * np.array([1, 1, 1.04])
    if cfg.get('wlift'):
        wm = np.array(Image.fromarray((ndimage.gaussian_filter((ws < .48 - nz).astype(float) * 0 + (V == 0).astype(float), .8) * 255).astype(np.uint8)).resize((img.shape[1], img.shape[0]), Image.BILINEAR)) / 255.
        img += wm[..., None] * np.array(cfg['wlift'])
    if cfg.get('wdesat'):
        wm = np.array(Image.fromarray((ndimage.gaussian_filter((V == 0).astype(float), .8) * 255).astype(np.uint8)).resize((img.shape[1], img.shape[0]), Image.BILINEAR)) / 255. * cfg['wdesat']
        lum = (img * [.3, .59, .11]).sum(-1, keepdims=True) * np.array([1.0, 1.02, 1.04]); img = img * (1 - wm[..., None]) + lum * wm[..., None] * .92
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    gimg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    gp = f'{OUT}/{mid}_ground.png'; gimg.save(os.path.join(ROOT, gp), optimize=True)
    # ---- decoArt / legend ----
    def arts(keys): return [{'img': v['img'], 'ax': v['ax'], 'ay': v['ay']} for k in keys for v in C[k]]
    base = orig['legend'].get('.', 'grass'); base = base if isinstance(base, str) else base['ground']
    pathg = {'field_felt': 'dirt', 'field02': 'stones', 'field07': 'stones'}.get(mid, 'stones')
    legend = {'.': base, '=': pathg, '~': {'ground': 'water', 'hop': True} if cfg.get('hop') else ('lava' if cfg['water'] == 'lava' else 'water'),
              'b': 'bridge_h', '#': 'cliff', 'L': base,
              'T': {'ground': base, 'deco': 'tree'}, 'P': {'ground': base, 'deco': 'pine'}, 'R': {'ground': base, 'deco': 'boulder'},
              'r': {'ground': base, 'deco': 'rocks'}, 'u': {'ground': base, 'deco': 'bush'}, 's': {'ground': base, 'deco': 'mushrooms', 'solid': False},
              'w': {'ground': base, 'deco': 'mushrooms', 'solid': False}}
    decoArt = {'T': arts(cfg['T']), 'P': arts(cfg['Pt']), 'R': arts(cfg['R']), 'r': arts(cfg['r']), 'u': arts(cfg['u'])}
    if cfg['s']: decoArt['s'] = arts(cfg['s'])
    if cfg['w']: decoArt['w'] = arts(cfg['w'])
    else: legend['w'] = base
    solid = ['#', 'T', 'P', 'R', 'r', 'u', 'L'] + ([] if cfg.get('hop') else ['~'])
    # water shimmer runs + tufts
    wruns = []
    for y in range(h):
        x = 0
        while x < w:
            if grid[y, x] == '~':
                x0 = x
                while x < w and grid[y, x] == '~': x += 1
                wruns.append([y, x0, x - 1])
            x += 1
    tufts = []
    if cfg.get('tuft'):
        p = cfg.get('tuftp', .22)
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if grid[y, x] == '.' and rnd.random() < p: tufts.append([round(x + rnd.random(), 2), round(y + .3 + rnd.random() * .7, 2), rnd.randrange(3)])
    fx = dict(cfg.get('fx') or {}); fx['tuft'] = cfg.get('tuft'); fx['water'] = cfg['water']
    hd = {'D': D, 'ground': gp, 'decoArt': decoArt, 'props': pr, 'water': wruns, 'tufts': tufts, 'fx': fx}
    if mid == 'field_felt': hd['grade'] = None
    out = {k: orig[k] for k in orig if k not in ('ground', 'legend', 'objects', 'hd', 'solid', 'spawns', 'w', 'h')}
    sp = {'default': G['spawn'], ('felt' if G['north'] else 'world'): G['spawn']}
    out.update({'w': w, 'h': h, 'ground': [''.join(r) for r in grid], 'legend': legend, 'solid': solid, 'objects': objs, 'spawns': sp, 'hd': hd})
    json.dump(out, open(os.path.join(ROOT, 'maps', mid + '.json'), 'w'), ensure_ascii=False, indent=1)
    nfree = int(free.sum()); print(f'{mid}: reach {int(reach.sum())}/{nfree} floor cells, mobs {len([o for o in objs if o["type"]=="spawn"])}/{len(mobs)}, lms {len(lobjs)}, objlost {lost}, props {len(pr)}')
    return out
def build00():
    """field00 keeps its hand-made 120x40 layout (objects/quests are tied to it); only reskinned:
    Wang ground, HD trees/rocks, cliff blocks broken up with boulders, tufts for tall grass."""
    mid = 'field00'; orig = json.load(open(os.path.join(HERE, 'orig', mid + '.json'))); C = cat(); rnd = random.Random(7)
    w, h = orig['w'], orig['h']; grid = np.array([list(r) for r in orig['ground']])
    floor = ~np.isin(grid, ['#', 'T', 'P', '~', 'R', 'O', 'r', 'u', 's', 'f', 'c'])
    nb = ndimage.binary_dilation(floor, structure=np.ones((3, 3)))
    for y in range(h):
        for x in range(w):
            if grid[y, x] != '#': continue
            r = rnd.random()
            if nb[y, x] and r < .45: grid[y, x] = 'R'
            elif not nb[y, x] and r < .4: grid[y, x] = 'T'
    P = wang.load_set(os.path.join(SETS, 't_grass_dirt')); W = wang.unify_base(wang.load_set(os.path.join(SETS, 'w_f00')), P)
    tw, th = w * 3 // 2, h * 3 // 2
    wi = ndimage.gaussian_filter(np.isin(grid, ['~', 'b']).astype(float), .9)
    pi = ndimage.gaussian_filter(np.isin(grid, ['=', ':', '_']).astype(float), .8)
    vy, vx = np.mgrid[0:th + 1, 0:tw + 1] / 1.5 - .5
    ws = ndimage.map_coordinates(wi, [vy, vx], order=1, mode='nearest'); ps = ndimage.map_coordinates(pi, [vy, vx], order=1, mode='nearest')
    nz = (wang.vnoise(th + 1, tw + 1, 3, seed=47) - .5) * .32 + (wang.vnoise(th + 1, tw + 1, 7, seed=48) - .5) * .2
    V = np.ones((th + 1, tw + 1), int); V[ws + nz > .45] = 0; V[(ps + nz > .4) & (ws < .12)] = 2
    img = np.array(wang.compose(V, P, W, seed=7, mottle=.13, gr={'sat': .6, 'gain': .9})).astype(np.float32)
    band = ndimage.gaussian_filter(np.isin(grid, ['#', 'T', 'P', 'R']).astype(float), 1.0)
    bm = np.array(Image.fromarray((band * 255).astype(np.uint8)).resize((img.shape[1], img.shape[0]), Image.BILINEAR)) / 255.
    img *= (1 - .42 * bm)[..., None] * np.array([1, 1, 1.04])
    gimg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    gp = f'{OUT}/{mid}_ground.png'; gimg.save(os.path.join(ROOT, gp), optimize=True)
    def arts(keys): return [{'img': v['img'], 'ax': v['ax'], 'ay': v['ay']} for k in keys for v in C[k]]
    decoArt = {'T': arts(['oak', 'oak1']), 'Y': arts(['oak1']), 'P': arts(['coastpine']), 'R': arts(['boulder']), 'r': arts(['stone_low']),
               'u': arts(['bush_b']), 's': arts(['stump']), 'm': arts(['pale_mushrooms']),
               'f': [{'img': 'assets/world/field_felt_hd/fence_tile.png', 'ax': 24, 'ay': 42, 'flip': False}],
               'O': [{'img': 'assets/world/field_felt_hd/ruin_pillar.png', 'ax': 38, 'ay': 143, 'flip': False}],
               'c': [{'img': 'assets/world/field_felt_hd/thread_stake.png', 'ax': 8, 'ay': 116, 'flip': False}]}
    tufts = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            c = grid[y, x]; n = {'"': 3, ',': 1, "'": 1, '.': 1 if rnd.random() < .12 else 0}.get(c, 0)
            for _ in range(n): tufts.append([round(x + rnd.random(), 2), round(y + .3 + rnd.random() * .7, 2), 3 if c == "'" and rnd.random() < .6 else rnd.randrange(3)])
    wruns = []
    for y in range(h):
        x = 0
        while x < w:
            if grid[y, x] == '~':
                x0 = x
                while x < w and grid[y, x] == '~': x += 1
                wruns.append([y, x0, x - 1])
            x += 1
    legend = dict(orig['legend']); legend['R'] = {'ground': 'grass', 'deco': 'boulder'}
    out = dict(orig); out['ground'] = [''.join(r) for r in grid]; out['legend'] = legend
    out['hd'] = {'D': D, 'ground': gp, 'decoArt': decoArt, 'props': [], 'water': wruns, 'tufts': tufts,
                 'fx': {'tuft': ['#5e6a4c', '#6c7656', '#4f5a40'], 'birds': 4, 'butterflies': 4, 'water': 'river'}}
    free = ~np.isin(grid, orig['solid'] + ['R'])
    sx, sy = [int(v) for v in orig['spawns']['default'][:2]]; r = bfs(free, sx, sy)
    json.dump(out, open(os.path.join(ROOT, 'maps', mid + '.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'{mid}: reach {int(r.sum())}/{int(free.sum())} (layout unchanged, reskin)')
if __name__ == '__main__':
    for m in (sys.argv[1:] or ['field00'] + [k for k in B]): build00() if m == 'field00' else build(m)
