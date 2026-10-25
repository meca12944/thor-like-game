"""Felt v5 (owner 10-25 「전체 맵 집 마을을 새로 디자인 · 기존꺼 쓰지말고 · 지도에 맞게 성벽 웅장하게」).
Everything in this town is drawn in code from scratch (inkart.py brush/ink/watercolour core): the capital's colossal north wall with the
ruined old gate (felt_v4_wall.py), every building (felt_v4_house.py), every small prop (felt_v4_props.py) and the ground (here).
No art file from the old felt/ folder is used. Object data (NPCs, doors, texts, quests hooks) comes from felt_v4_objects.json.
Layout (150x120 tiles): north band = capital wall + gatehouse (exit '1장 정문' through the arch), west gate + Gas's post (from the field),
Luca's campfire at the centre (save), NW chief Bart / NE inn + herb hut + chapel / SW Linette's atelier + Rom's forge (outskirts) /
SE junk street (used weapons + tools) / Ben's wagon east / Toby's shack south / Arachne's workshop entrance in the SE corner.
Usage: python3 build_felt5.py  -> maps/felt.json + assets/world/felt5/*"""
import json, os, sys, math, random, copy, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import inkart, felt_v4_wall as WL, felt_v4_house as HS, felt_v4_props as PR
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
FA = 'assets/world/felt5/'; W, H = 150, 120; T = 16; D = 2; AT = 32; HD = 1.5; G = int(T * HD)
WALL_Y = WL.WALL_Y; GATE_X = WL.GATE_X; SEED = 5
rnd = random.Random(SEED)
def rel(p): return os.path.join(ROOT, p)
SRC = json.load(open(os.path.join(HERE, 'felt_v4_objects.json')))
OB = {o.get('id'): o for o in SRC['objects'] if o.get('id')}
_saved = {}
def save(im, name, webp=False):
    p = FA + name + ('.webp' if webp else '.png')
    if webp: im.save(rel(p), 'WEBP', quality=90, method=6)
    else: im.save(rel(p), optimize=True)
    _saved[name] = im.size; return p
grid = np.full((H, W), '.', dtype='<U1')
road = np.zeros((H, W), bool); lane = np.zeros((H, W), bool)
props = []; under = []; objs = []; spawns = {}; lights = []; fires = []; flick = []; smoke = []; shadows = []
def prop(img, x, y, ax, ay, **k):
    q = {'img': img, 'x': round(x, 3), 'y': round(y, 3), 'ax': round(ax, 1), 'ay': round(ay, 1), 'D': D, 'fade': 0, 'shadow': 0}; q.update(k); props.append(q); return q
def solid(x0, y0, x1, y1, ch='X'):
    grid[max(0, y0):min(H, y1), max(0, x0):min(W, x1)] = ch
# ---------------------------------------------------------------- roads / lanes
def paint(mask, pts, w):
    yy, xx = np.mgrid[0:H, 0:W]
    for (a, b), (c, d) in zip(pts[:-1], pts[1:]):
        L = max(1e-6, math.hypot(c - a, d - b)); t = np.clip(((xx + .5 - a) * (c - a) + (yy + .5 - b) * (d - b)) / L ** 2, 0, 1)
        mask |= np.hypot(xx + .5 - (a + t * (c - a)), yy + .5 - (b + t * (d - b))) <= w / 2
CAMP = (75.5, 71.0)
paint(road, [(GATE_X, 28), (GATE_X, 64)], 5)                                 # the avenue from the old gate to the camp
paint(road, [(60, 31.5), (91, 31.5)], 5)                                    # gate plaza
paint(road, [(0, 70.5), (14, 70.5), (40, 70), (66, 71)], 4)                # west gate street
paint(road, [(85, 71), (112, 71.5), (136, 74), (141, 82), (139, 92)], 4)   # east street to Ben's wagon
paint(road, [(GATE_X, 79), (GATE_X, 92), (80, 104), (79, 119)], 3.5)       # south road (out of town, the outer district)
yy_, xx_ = np.mgrid[0:H, 0:W]; camp = np.hypot((xx_ + .5 - CAMP[0]) / 1.15, yy_ + .5 - CAMP[1]) < 8.5
paint(lane, [(10, 31), (60, 31)], 2.5); paint(lane, [(91, 31), (143, 31)], 2.5)   # the wall-foot track
paint(lane, [(68, 66), (52, 58), (41, 55.5)], 2.5); paint(lane, [(56, 51), (52, 58)], 2)
paint(lane, [(83, 66), (96, 59), (101, 56)], 2.5); paint(lane, [(101, 57), (112, 55), (121, 53)], 2.2); paint(lane, [(121, 53), (128, 49), (134, 45.5)], 2.2)
paint(lane, [(134, 45.5), (134, 36), (110, 33)], 2)
paint(lane, [(68, 76), (56, 88), (49, 99.5)], 2.5); paint(lane, [(49, 99.5), (42, 108), (38, 117)], 2)
paint(lane, [(18, 71), (17, 90), (16, 109.5)], 2.5)                          # forge lane
paint(lane, [(83, 77), (96, 92), (100, 100.5)], 2.5); paint(lane, [(100, 100.5), (114, 98.5), (124, 101), (131, 108), (134, 114.5)], 2.5)
paint(lane, [(8, 66), (8, 70)], 2); paint(lane, [(24, 52), (34, 55.5)], 2)
lane &= ~road
# ---------------------------------------------------------------- north band (capital wall + gate)
print('wall...')
band = WL.build_band(); bim = band.finish(cut=band.meta['cut']); pc, ox, oy = band.meta['portc_pic']; bim.alpha_composite(pc.finish(), (ox, oy))
# the royal castle far behind the wall (owner 10-25 「성 뒷편 뷰를 우리 인트로 영상처럼 높은 성으로」): a screen-pinned far backdrop (castle_backdrop.py),
# drawn by world.js drawBackdrop only in the sky behind the wall (clipY); it shows through the deep breaches in normal play and whole from the gate vista.
import castle_backdrop as CB
BPT = 20; BW, BH, BCX, BBASE, BHC, BWC = 180, 42, 90, 38, 30, 22
bdi, bdm = CB.compose(BW, BH, BPT, BCX, BBASE, BHC, BWC, seed=11, city_t=(0, 3.2))
bdp = FA + 'castle_backdrop.webp'; bdi.save(rel(bdp), 'WEBP', quality=88, method=6)
backdrop = {'img': bdp, 'D': BPT / 16, 'ppt': BPT, 'ax': BCX * BPT, 'ay': (BBASE - BHC) * BPT, 'x': 75, 'px': .92, 'fy': .03, 'clipY': WALL_Y - 1.5,
            'sky': '#4a4440', 'floor': '#b9ae9e', 'side': '#9a9086', 'glows': bdm['glows'], 'smoke': bdm['smoke'][:7],
            'shaft': [BCX * BPT, (BBASE - BHC * .62) * BPT, BWC * 1.3 * BPT, BHC * .45 * BPT],
            'fog': [[(BBASE - BHC * .55) * BPT, 2.4 * BPT, .35, 5], [(BBASE - 7) * BPT, 4 * BPT, .5, 9], [(BBASE - 3.5) * BPT, 5 * BPT, .7, 14], [(BBASE - 1) * BPT, 6 * BPT, .8, 20]]}
tp, tox, toy = WL.tunnel(); tim = tp.finish(); tpath = save(tim, 'gate_tunnel')
tunnel_q = {'id': 'gate_tunnel', 'img': tpath, 'x': round(tox / AT, 3), 'y': WALL_Y - 3.5, 'ax': 0, 'ay': round((WALL_Y - 3.5) * AT - toy, 1), 'D': D, 'fade': 0, 'shadow': 0}
SL = 25; band_q = []
for i, x0 in enumerate(range(0, 150, SL)):
    sl = bim.crop((x0 * AT, 0, (x0 + SL) * AT, bim.height)); bb = sl.getbbox()
    if not bb: continue
    sl = sl.crop((0, bb[1], sl.width, bim.height)); path = save(sl, f'wall_{i}')
    band_q.append({'id': f'wall_{i}', 'img': path, 'x': x0, 'y': WALL_Y + .5, 'ax': 0, 'ay': (WALL_Y + .5) * AT - bb[1], 'D': D, 'fade': 0, 'shadow': 0})
solid(0, 0, W, WALL_Y + 1, '#')
for cx, w, top in WL.TOWERS: solid(int(cx - w / 2), WALL_Y, int(math.ceil(cx + w / 2)), int(WALL_Y + 2.5) + 1, '#')
for a, b in (WL.GH['tl'], WL.GH['tr']): solid(int(a), WALL_Y, int(math.ceil(b)), int(WALL_Y + 3.5) + 1, '#')
for x in range(72, 79):
    for y in range(24, WALL_Y + 1): grid[y, x] = '='
road[24:WALL_Y + 1, 72:79] = True
# rubble mounds at the collapsed runs (solid), dark at the wall foot
for k, (a, b, lo) in enumerate(WL.COLLAPSE):
    for j, xx in enumerate(np.arange(a + .5, b, 3.4)):
        ww = rnd.uniform(3.4, 4.6); p, ax, ay = PR.rubble(300 + k * 20 + j, ww, rnd.uniform(1.6, 2.4)); im = p.finish(); path = save(im, f'rubble_wall_{k}_{j}')
        y = WALL_Y + rnd.uniform(1.6, 2.6); prop(path, xx + ww / 2 - .5, y, ax, ay, id=f'rubble_wall_{k}_{j}')
        solid(int(xx), WALL_Y, int(xx + ww), int(y) + 1, '#')
# ---------------------------------------------------------------- side walls (west + east edges)
print('side walls...')
def side(x0, x1, y0, y1, hfn, seed, inner, tag):
    for j, (im, xtl, yb, ax, ay) in enumerate(WL.side_wall_chunks(x0, x1, y0, y1, hfn, seed, 3.0, inner)):
        path = save(im, f'{tag}_{j}'); prop(path, x0, yb, ax, ay, id=f'{tag}_{j}')
    solid(int(x0), int(y0), int(math.ceil(x1)), int(math.ceil(y1)), '#')
side(0, 4, WALL_Y + 1, 63, lambda y: 7.5 - (2.5 if 44 < y < 52 else 0), 71, 'right', 'wwall_n')
side(0, 4, 78, 118, lambda y: 6.5 - max(0, (y - 96)) * .18, 72, 'right', 'wwall_s')
side(146, 150, WALL_Y + 1, 79, lambda y: 7.0 - (3 if 54 < y < 63 else 0), 73, 'left', 'ewall_n')
side(146, 150, 87, 118, lambda y: 5.0 - max(0, y - 100) * .15, 74, 'left', 'ewall_s')
# west gate: two broken towers flanking the street (reuse the wall's tower painter on a small canvas)
def gate_tower(cx, foot, seed, tag, top_):
    p = inkart.Pic(int(7 * AT), int((foot - top_ + 3) * AT), seed)
    WL_T, WL_WY = WL.T, WL.WALL_Y
    # local tower: draw on a canvas whose y0 = top_-2 tiles
    oy = (top_ - 2) * AT; Wt = 5.2
    import types
    def L(y): return (y - (top_ - 2)) * AT
    xl, xr = (3.5 - Wt / 2) * AT, (3.5 + Wt / 2) * AT; fb = L(foot); ft = L(top_)
    jt = [(x, ft + rnd.uniform(-6, 6) + (rnd.random() < .35) * rnd.uniform(8, 30)) for x in np.linspace(xl, xr, 9)]
    p.fill([(xl - 6, fb)] + [(xl - 4, ft + 20)] + jt + [(xr + 4, ft + 20), (xr + 6, fb)], 'stone', wob=.5, line=1.6)
    inkart.masonry(p, xl - 6, ft - 30, xr + 6, fb, top=lambda x: float(np.interp(x, [q[0] for q in jt], [q[1] for q in jt])), rowh=15, col='stone', holes=.03, seed=seed, bottom_dark=.25)
    for k in range(3): WL.slit(p, 3.5, top_ + 2 + k * 2.6 - (top_ - 2), top_ + 3.2 + k * 2.6 - (top_ - 2))
    p.shade([(xr - 1.4 * AT, ft), (xr + 6, ft), (xr + 6, fb), (xr - 1.4 * AT, fb)], .38, .5)
    p.post.append(inkart.moss_post(lambda yy, xx: np.clip((yy - (fb - 3 * AT)) / (3 * AT), 0, 1), .7, 'moss', 8, seed, .58))
    p.post.append(inkart.soot_post(lambda yy, xx: np.clip(1 - (yy - ft) / (fb - ft), 0, 1) * .8, .5, seed))
    inkart.crack(p, xl + 2 * AT, ft + 30, 90, seed, 1.3)
    p.fill([(xl - 10, fb + 2), (xr + 10, fb + 2), (xr + 6, fb - 10), (xl - 6, fb - 10)], 'stone_d', wob=.5, line=1.2)
    im = p.finish(); path = save(im, tag); prop(path, cx, foot, 3.5 * AT, fb, id=tag)
    solid(int(cx - 2.6), int(foot - 3), int(math.ceil(cx + 2.6)), int(foot) + 0, '#')
gate_tower(3.2, 66.5, 81, 'wgate_tower_n', 55.5); gate_tower(3.2, 79.0, 82, 'wgate_tower_s', 68.0)
for y in range(67, 75):
    for x in range(0, 6): grid[y, x] = '.'
solid(0, 63, 4, 64, '#'); solid(0, 76, 4, 79, '#')
# ---------------------------------------------------------------- buildings
print('houses...')
B = []
def building(key, x0, foot, spec, door=None, smoke_k=1.0, light=None, fade=1):
    p, m = HS.house(seed=zlib.crc32(key.encode()) % 997, **spec); im = p.finish(); path = save(im, 'h_' + key)
    q = prop(path, x0, foot, m['ax'], m['ay'], id=key, fade=fade, shadow=0)
    Wt, dpt = spec['W'], spec['d']; solid(x0, foot - dpt, x0 + Wt, foot, 'H')
    shadows.append((x0, foot - dpt, x0 + Wt, foot, spec.get('hf', 3)))
    if m.get('chimney'): cx_, ch = m['chimney']; smoke.append([round(x0 + cx_, 2), round(foot - ch / 1.0 * 1 - .2, 2), 1.0 * smoke_k])
    if door and m['door'] is not None:
        d = m['door']; dx = int(x0 + (d['cx'] - m['ax']) / AT); dy = foot - 1
        q['door'] = {'id': door['id'], 'cx': round(d['cx'], 1), 'by': round(d['by'], 1), 'w': round(d['w'], 1), 'h': round(d['h'], 1), 'col': [92, 66, 40]}
        o = {'type': 'door', 'id': door['id'], 'x': dx, 'y': dy, 'name': door['name']}
        for k in ('to', 'out', 'text', 'scene'):
            if door.get(k): o[k] = door[k]
        if door.get('to') and door.get('out'): o['spawn'] = 'door'; spawns[door['out']] = [dx + .5, dy + 1.9, 'down']
        elif door.get('to'): o['spawn'] = door.get('spawn', 'default')
        objs.append(o); grid[dy, dx] = 'H'
        for yy in range(foot, min(H, foot + 2)):
            if grid[yy, dx] not in '=': grid[yy, dx] = '.'
        lane[foot:foot + 2, dx] |= ~road[foot:foot + 2, dx]
        lights.append([dx + .5, foot - .9, 44, '#ffb060', .75])     # the doorway's warm spill
    B.append((key, x0, foot, spec, q)); return q
def D_(i): return OB[i]
building('chief', 34, 55, dict(W=13, d=6, hf=5.2, roof='gable', mat='timber', stories=2, door_at=6.5, wins=[(2.5, 3.1, 'lit'), (4.5, 3.1, 'shutter'), (9, 3.1, 'lit'), (11, 3.1, 'board'), (2.5, .9, 'lit'), (10.5, .9, 'lit')], chim=10.5, dmg=.25, sign=('key', 7.6 * 32 + 38, 2.7)), D_('f_door_chief'))
building('empty', 52, 50, dict(W=9, d=5, hf=3.2, roof='gable', mat='plank', roofcol='tile_r', door_at=3, wins=[(6.5, 1, 'board')], dmg=.8), D_('f_door_empty'))
building('inn', 92, 56, dict(W=17, d=7, hf=5.6, roof='gable', mat='timber', stories=2, door_at=8.5, door_w=1.6, wins=[(2.5, 3.4, 'lit'), (5.5, 3.4, 'lit'), (11.5, 3.4, 'lit'), (14.5, 3.4, 'shutter'), (2.5, 1, 'lit'), (5.5, 1, 'lit'), (12, 1, 'lit'), (14.8, 1, 'lit')], chim=3.5, dmg=.15, sign=('mug', 9.8 * 32 + 38, 2.8), extras=('balcony',)), D_('f_door_inn'), smoke_k=1.2)
building('herb', 116, 52, dict(W=8, d=5, hf=2.8, roof='thatch', roofcol='thatch', mat='timber', door_at=4, wins=[(1.8, .9, 'lit'), (6.4, .9, 'shutter')], extras=('herbs',), chim=6.6, dmg=.1, sign=('leaf', 5.1 * 32 + 38, 2.3)), D_('f_door_herb'), smoke_k=.7)
building('chapel', 128, 45, dict(W=11, d=6, hf=4.0, roof='front', mat='stone', door_at=5.5, arch_door=True, door_w=1.5, door_h=2.3, wins=[(2.3, 1.3, 'lit', 1.0, 1.6), (8.7, 1.3, 'lit', 1.0, 1.6)], dmg=.3), D_('f_door_chapel'))
building('atelier', 43, 99, dict(W=11, d=5, hf=3.6, roof='gable', mat='timber', roofcol='roof', door_at=5, wins=[(2, 1, 'lit'), (8.3, 1, 'lit', 1.6, 1.15)], chim=8.8, dmg=.15, sign=('spool', 6.2 * 32 + 38, 2.5)), D_('f_door_atelier'), smoke_k=.8)
building('weapon', 95, 100, dict(W=10, d=5, hf=3.6, roof='gable', mat='stone', roofcol='roof_d', door_at=4, wins=[(7.5, 1.0, 'lit', 1.6, 1.1)], dmg=.35, sign=('sword', 5.2 * 32 + 38, 2.5), extras=(('awn', 6, 9.5),)), D_('f_door_weapon'))
building('tool', 110, 98, dict(W=10, d=5, hf=3.4, roof='gable', mat='plank', roofcol='tile_r', door_at=4.5, wins=[(1.8, 1, 'lit'), (7.8, 1, 'lit', 1.4, 1.1)], dmg=.4, sign=('bag', 5.7 * 32 + 38, 2.4), extras=(('awn', 6.3, 9.6),), chim=1.6), D_('f_door_tool'), smoke_k=.6)
building('forge', 9, 109, dict(W=12, d=6, hf=3.8, roof='gable', mat='stone', roofcol='roof_d', door_at=4, wins=[(8.5, 1.0, 'lit', 2.4, 1.3)], chim=9.5, dmg=.3, sign=('anvil', 5.2 * 32 + 38, 2.6)), D_('f_door_smith'), smoke_k=1.6)
building('guard', 5, 66, dict(W=6, d=4, hf=2.9, roof='gable', mat='plank', roofcol='roof', door_at=3.5, door_w=1.2, wins=[(1.4, 1, 'board')], dmg=.4), D_('f_door_guard'))
building('toby', 32, 117, dict(W=6, d=3, hf=2.3, roof='gable', mat='plank', roofcol='thatch_d', wins=[(4.3, .8, 'shutter', .8, .8)], dmg=.2), None)
# Arachne's workshop entrance: a sunken stone portal (SE corner, "마을 오른쪽 아래, 숲길 끝")
building('arachne_gate', 131, 114, dict(W=7, d=4, hf=3.2, roof='front', mat='stone', roofcol='stone_d', door_at=3.5, door_w=1.8, door_h=2.4, arch_door=True, wins=[], dmg=.7), D_('f_arachne_gate'))
ag = [o for o in objs if o['id'] == 'f_arachne_gate'][0]; spawns['arachne'] = [ag['x'] + .5, ag['y'] + 2.2, 'down']
# decor houses (no door) + burnt shells
building('house_nw2', 22, 47, dict(W=9, d=5, hf=3.4, roof='gable', mat='timber', roofcol='tile_r', wins=[(2, 1, 'board'), (6.5, 1, 'dark')], chim=7, dmg=.6), None)
building('house_ne2', 103, 46, dict(W=9, d=5, hf=3.0, roof='gable', mat='plank', wins=[(2.4, 1, 'board'), (6.5, 1, 'shutter')], dmg=.7), None)
building('house_e3', 122, 66, dict(W=9, d=5, hf=3.2, roof='thatch', roofcol='thatch_d', mat='timber', wins=[(2, .9, 'dark'), (6.6, .9, 'lit')], dmg=.4, chim=2), None, smoke_k=.5)
building('house_s2', 60, 98, dict(W=9, d=5, hf=3.2, roof='gable', mat='timber', roofcol='roof', wins=[(2.2, 1, 'shutter'), (6.6, 1, 'board')], dmg=.5), None)
building('house_se3', 122, 88, dict(W=8, d=4, hf=2.8, roof='gable', mat='plank', roofcol='tile_r', wins=[(4, .9, 'board')], dmg=.6), None)
building('house_w2', 25, 80, dict(W=9, d=5, hf=3.2, roof='gable', mat='timber', roofcol='roof_d', wins=[(2.2, 1, 'dark'), (6.5, 1, 'board')], dmg=.55, chim=7), None)
for k, (x0, foot, Wt) in enumerate([(55, 61, 10), (85, 46, 10), (44, 64, 8), (106, 66, 9), (25, 95, 8), (88, 112, 9), (60, 113, 10), (108, 83, 9), (37, 86, 8)]):
    building(f'ruin_{k}', x0, foot, dict(W=Wt, d=5, hf=3.4, ruin=True), None, fade=1)
    if k % 3 == 0: smoke.append([x0 + Wt / 2, foot - 2.6, .8])
# ---------------------------------------------------------------- small props
print('props...')
_cache = {}
def sp(fn, key, x, y, solid_wh=(1, 1), **k):
    if key not in _cache:
        p, ax, ay = fn(); _cache[key] = (save(p.finish(), 'p_' + key), ax, ay)
    path, ax, ay = _cache[key]; q = prop(path, x, y, ax, ay, id='p_' + key, **k)
    if solid_wh:
        w_, h_ = solid_wh; x0 = int(round(x - w_ / 2)); y0 = int(math.ceil(y)) - h_
        for yy in range(y0, y0 + h_):
            for xx in range(x0, x0 + w_):
                if 0 <= yy < H and 0 <= xx < W and grid[yy, xx] == '.' and not road[yy, xx] and not lane[yy, xx]: grid[yy, xx] = 'X'
    return q
def free_at(x, y, r=0):
    for yy in range(int(y) - r, int(y) + 1):
        for xx in range(int(x) - r, int(x) + r + 1):
            if not (0 <= yy < H and 0 <= xx < W) or grid[yy, xx] != '.' or road[yy, xx] or lane[yy, xx]: return False
    return True
def brz(x, y): sp(lambda: PR.brazier(1), 'brazier', x, y); lights.append([x, y - 1.0, 64, '#ff8a3a', 1]); flick.append([x, y - 1.0, 34, '#ff8a3a', 1]); fires.append([x, y - 1.15, .9])
def torch(x, y): sp(lambda: PR.torch_post(2), 'torch', x, y); lights.append([x, y - 1.9, 46, '#ff9a48', .85]); flick.append([x, y - 1.9, 24, '#ff9a48', .8]); fires.append([x, y - 2.05, .5])
def lamp(x, y): sp(lambda: PR.lantern_post(3), 'lamp', x, y); lights.append([x + .4, y - 2.2, 52, '#ffb060', .8]); fires.append([x + .45, y - 2.25, .3])
# gate plaza: braziers, banners, founder statues, chest
for x in (66.5, 84.5): brz(x, 34.6)
for x in (62, 70, 81, 89): sp(lambda: PR.banner(11, 'cloth_r', 4.2, .55), 'banner_r', x, 33.4, sway=.6)
for x in (56, 95): sp(lambda: PR.statue(4), 'statue', x, 34.8, (2, 1))
for x, y in ((58.5, 36.5), (93.5, 37), (53, 30.2), (98, 30.6)): sp(lambda: PR.column(5, 3.0), 'column', x, y, (2, 1))
for y in (40, 48, 56): lamp(72.6, y); lamp(78.4, y + 4)
# camp (Luca's campfire, the save point)
sp(lambda: PR.campring(6), 'campring', CAMP[0], CAMP[1] + .9, (3, 2))
for k, (x, y, col) in enumerate([(66.5, 66.8, 'cloth'), (85.5, 66.5, 'cloth_b'), (67.5, 77.2, 'cloth_r'), (84.2, 77.6, 'cloth')]):
    sp(lambda c=col, k=k: PR.tent(20 + k, c), f'tent_{k}', x, y, (3, 2))
sp(lambda: PR.memorial(7), 'memorial', 89.5, 70.0, (5, 1))
sp(lambda: PR.board(8), 'board', 81.5, 64.6, (2, 1))
sp(lambda: PR.well(9), 'well', 63.5, 73.4, (3, 2))
for x, y in ((71.5, 74.5), (80, 74.6)): sp(lambda: PR.bench(10), 'bench', x, y, (2, 1))
for x, y in ((69.5, 64.4), (82, 77.4)): sp(lambda: PR.woodpile(12), 'woodpile', x, y, (2, 1))
for x, y in ((64.3, 69.2), (86.8, 73.6), (70.4, 79.4), (81.4, 79.6)): torch(x, y)
for x, y in ((88.6, 67.2), (62.2, 76.6)): sp(lambda: PR.sacks(13), 'sacks', x, y, (2, 1))
sp(lambda: PR.laundry(14, 4.0), 'laundry', 75.5, 81.6, None)
# west gate + Gas's post
for x, y in ((6.6, 66.4), (6.6, 75.4)): brz(x, y)
sp(lambda: PR.signpost(15), 'signpost', 13.5, 74.0, (1, 1))
for x, y in ((11.6, 66.4), (2.8, 81.6)): sp(lambda: PR.crate(16), 'crate', x, y)
sp(lambda: PR.barrel(17), 'barrel', 12.7, 66.6); sp(lambda: PR.banner(18, 'cloth_b', 3.6, .7), 'banner_b', 9.6, 74.6, (1, 1), sway=.6)
# NW chief block
for x, y in ((48, 55.6), (32.6, 55.4)): sp(lambda: PR.barrel(17), 'barrel', x, y)
sp(lambda: PR.woodpile(19), 'woodpile2', 49.5, 52.4, (2, 1)); sp(lambda: PR.cart(20), 'cart', 29.5, 58.6, (3, 1))
lamp(46.5, 58.2); torch(33.2, 57.6)
sp(lambda: PR.laundry(21, 4.4), 'laundry2', 64.5, 52.6, None)
# NE inn block
for x, y in ((90.2, 58.2), (110.6, 58.4)): sp(lambda: PR.table(22), 'table', x, y, (3, 1))
for x, y in ((89, 56.5), (91.4, 56.6), (110, 56.3)): sp(lambda: PR.barrel(17), 'barrel', x, y)
lamp(97.4, 59.6); lamp(106, 58.8); torch(115.4, 54.6)
sp(lambda: PR.rack(23, 'herb'), 'herbrack', 126.5, 54.8, (3, 1)); sp(lambda: PR.sacks(13), 'sacks', 114.5, 54.6, (2, 1))
# chapel + graves
for k, (x, y) in enumerate([(140.5, 38.5), (143, 38.8), (140.8, 41.5), (143.4, 41.9), (140.2, 44.6), (143.2, 45), (126.5, 39.6), (124.4, 42.2)]):
    sp(lambda k=k: PR.grave(30 + k, k % 3), f'grave_{k % 6}', x, y)
torch(126.6, 46.8); torch(140.4, 46.8)
lights.append([133.5, 44.0, 56, '#ffc070', .7])
# SW atelier + forge
sp(lambda: PR.laundry(24, 3.6), 'laundry3', 57.5, 101.6, None); sp(lambda: PR.crate(16), 'crate', 41.6, 100.6); sp(lambda: PR.sacks(13), 'sacks', 55.2, 99.6, (2, 1))
lamp(53.5, 102.8)
sp(lambda: PR.anvil(25), 'anvil', 23.5, 108.6); sp(lambda: PR.grindstone(26), 'grind', 27.4, 108.4); sp(lambda: PR.woodpile(27), 'woodpile3', 7.5, 112.4, (2, 1))
sp(lambda: PR.haystack(28), 'haystack', 29.5, 103.6, (2, 1)); sp(lambda: PR.rack(29, 'weapon'), 'wrack', 25.5, 104.2, (3, 1))
brz(21.4, 106.2); lights.append([18.9, 107.6, 90, '#ff7a2a', 1]); fires.append([18.9, 107.9, 1.3, 'forge']); flick.append([18.9, 107.6, 44, '#ff7a2a', 1])
# SE junk street
sp(lambda: PR.rack(31, 'weapon'), 'wrack', 106.5, 101.4, (3, 1)); sp(lambda: PR.cart(32), 'cart2', 121.5, 102.2, (3, 1))
for x, y in ((93.4, 100.6), (108.6, 101.8), (120.6, 98.6)): sp(lambda: PR.crate(16), 'crate', x, y)
for x, y in ((94.6, 101.4), (122.2, 98.4)): sp(lambda: PR.barrel(17), 'barrel', x, y)
lamp(103.6, 103.4); lamp(117.4, 102.2); sp(lambda: PR.banner(33, 'cloth_o', 3.4, .6), 'banner_o', 109.2, 103.2, (1, 1), sway=.6)
# Ben's wagon (east end)
sp(lambda: PR.wagon(34), 'wagon', 141.5, 93.6, (5, 2)); sp(lambda: PR.crate(16), 'crate', 137.6, 92.6); sp(lambda: PR.sacks(13), 'sacks', 144.2, 96.4, (2, 1))
brz(136.2, 98.6)
# Toby's shack (south): a small hideout, safe and cosy
sp(lambda: PR.crate(35, .8), 'crate_s', 39.4, 117.4); sp(lambda: PR.banner(36, 'cloth_b', 2.2, .3), 'flag_toby', 31.3, 117.6, (1, 1), sway=.8); lamp(41.8, 115.2)
# Arachne's entrance: thread stakes, webs, dead wood
for x, y in ((128.4, 115.6), (140.2, 115.2), (127.5, 110.2)): sp(lambda: PR.stakes(37, 3.0), 'stakes', x, y, (3, 1))
torch(129.6, 112.6)
# ---------------------------------------------------------------- objects (from felt_v4_objects.json)
def nearest_free(x, y, need_floor=True):
    for r in range(0, 6):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                X, Y = x + dx, y + dy
                if 0 <= X < W and 0 <= Y < H and grid[Y, X] in '.=': return X, Y
    raise SystemExit(f'no free cell near {x},{y}')
def put(o, x, y, adjust=True):
    o = copy.deepcopy(o); o.pop('near', None)
    if adjust and o['type'] not in ('door',): x, y = nearest_free(x, y)
    o['x'] = x; o['y'] = y; objs.append(o); return o
put(OB['f_gas'], 10, 70); put(OB['f_toby'], 40, 116); put(OB['f_luca'], 78, 72)
put(OB['f_linette'], 51, 101); put(OB['f_ben'], 138, 96)
put(OB['ws_felt_plaza'], 72, 69); put(OB['ws_arachne'], 136, 115)
put(OB['f_chest_plaza'], 58, 33); put(OB['f_clue_bell'], 131, 46)
put(OB['f_hid_grave'], 145, 37); put(OB['f_hid_cart'], 145, 99)
put(OB['f_mark_fountain'], 75, 75); put(OB['f_mark_stall'], 139, 97); put(OB['f_mark_gate'], 7, 71)
sg = [o for o in SRC['objects'] if o['type'] == 'sign']
s1 = put(sg[0], 13, 75); s1['text'] = '펠트 서문\n→ 루카의 모닥불(쉼터) · 이장 집 · 여관 · 리네트 공방\n↑ 무너진 옛 성문 (1장 정문)   ↘ 고물상 거리 (중고 무기점 · 잡화점)\n↙ 롬의 대장간 (외곽)   ↘↘ 아라크네의 폐공방 (숲길 끝)'
wish = put(OB['f_well_wish'], 63, 72, adjust=False); grid[72, 63] = 'H'
bd = [o for o in sg if '게시판' in o.get('text', '')]
put(bd[0] if bd else sg[-1], 81, 65)
for i, (x, y) in [('f_clue_gate', (79, 30)), ('f_clue_moat', (40, 31)), ('f_hid_moat', (110, 30)), ('f_hid_tower', (5, 61)), ('f_hid_forge', (6, 111))]:
    o = OB.get(i)
    if o:
        if i == 'f_clue_gate': o = dict(o, text='왕도의 옛 성문. 성벽은 하늘을 가릴 만큼 높고, 거인도 드나들었을 법한 아치는 반쯤 무너졌다.\n그을린 돌에 새겨진 문장은 이제 읽을 수 없다. 아치 아래 어두운 통로 끝에 성 밖 들판의 빛이 보인다.')
        if i == 'f_clue_moat': o = dict(o, name='무너진 성벽 잔해의 녹슨 투구')
        put(o, x, y, adjust=(o['type'] != 'clue'))
for i, (x, y) in [('lm_felt_castle', (75, 32)), ('lm_felt_fountain', (75, 76)), ('lm_felt_grave', (138, 47))]:
    if i in OB: put(OB[i], x, y)
put(dict(OB['felt_gate'], zoom=.22, pan=25, hold=1, r=3.5, sub='왕도의 성벽 — 펠트는 그 그늘 아래에 있다'), 75, 38)
# clue tiles placed inside rubble keep their tile; make sure a neighbour is floor
for o in objs:
    if o['type'] == 'clue' and grid[o['y'], o['x']] not in '.=':
        if grid[o['y'] + 1, o['x']] not in '.=': grid[o['y'] + 1, o['x']] = '.'
# exits + spawns
objs.append({'type': 'exit', 'x': 72, 'y': 24, 'w': 7, 'h': 1, 'to': 'field_felt', 'spawn': 'felt', 'label': '↑ 1장 정문'})
objs.append({'type': 'exit', 'x': 0, 'y': 68, 'w': 1, 'h': 5, 'to': 'field_felt', 'spawn': 'felt', 'label': '← 펠트 서문 · 잿빛 들판'})
spawns.update({'default': [75.5, 80.0, 'up'], 'world': [75.5, 80.0, 'up'], 'field': [3.6, 70.5, 'right'], 'gate': [GATE_X, WALL_Y + 1.8, 'down']})
# campfire / smoke / ash fx
cf = [CAMP[0], CAMP[1] + .5]
lights += [[cf[0], cf[1], 170, '#ff8a3a', 1.0], [cf[0], cf[1], 70, '#ffc070', .6]]; flick.append([cf[0], cf[1], 64, '#ff9a40', .9])
fires += [[cf[0], cf[1] - .1, 1.5], [cf[0] - .4, cf[1] + .2, .9, 'embers']]; smoke.append([cf[0], cf[1] - .6, 1.6, 5])
for k, (a, b, lo) in enumerate(WL.COLLAPSE): fires.append([(a + b) / 2, WALL_Y + 1.5, .7, 'embers']); smoke.append([(a + b) / 2 + 1, WALL_Y + .5, 1.0, 2])
# ---------------------------------------------------------------- outskirts: dead trees, bushes, rubble (deco letters), south-edge silhouettes
print('deco + reach...')
deco = {'T': [], 'R': [], 'u': [], 's': [], 'P': []}
for k in range(5): p, ax, ay = PR.deadtree(50 + k, rnd.uniform(4.2, 5.6)); deco['T'].append({'img': save(p.finish(), f'd_tree_{k}'), 'ax': ax, 'ay': ay, 'D': D, 'sway': .4})
for k in range(4): p, ax, ay = PR.rubble(60 + k, rnd.uniform(1.2, 1.8), rnd.uniform(.7, 1.1)); deco['R'].append({'img': save(p.finish(), f'd_rubble_{k}'), 'ax': ax, 'ay': ay, 'D': D})
for k in range(3): p, ax, ay = PR.bush(70 + k, rnd.choice(['moss_d', 'thatch_d', 'moss']), rnd.uniform(.8, 1.0)); deco['u'].append({'img': save(p.finish(), f'd_bush_{k}'), 'ax': ax, 'ay': ay, 'D': D})
for k in range(2): p, ax, ay = PR.stump(80 + k); deco['s'].append({'img': save(p.finish(), f'd_stump_{k}'), 'ax': ax, 'ay': ay, 'D': D})
p, ax, ay = PR.column(90, 2.4); deco['P'].append({'img': save(p.finish(), 'd_column'), 'ax': ax, 'ay': ay, 'D': D})
# groves: outskirts
for gx, gy, n in [(14, 40, 7), (26, 36, 5), (8, 90, 6), (12, 98, 4), (140, 60, 5), (134, 82, 4), (100, 116, 6), (122, 117, 6), (60, 118, 5), (22, 118, 6), (144, 106, 5), (114, 40, 4), (50, 40, 4), (96, 40, 3), (128, 58, 3), (30, 66, 3), (62, 86, 3), (88, 88, 3), (106, 76, 3)]:
    for i in range(n):
        for _ in range(25):
            x = int(gx + rnd.uniform(-4, 4)); y = int(gy + rnd.uniform(-3, 3))
            if 0 < x < W - 1 and WALL_Y + 4 < y < H and free_at(x, y, 1): grid[y, x] = rnd.choice('TTTR'); break
for _ in range(500):
    x = rnd.randrange(5, W - 5); y = rnd.randrange(WALL_Y + 4, H - 1)
    if free_at(x, y, 1) and not camp[y, x]:
        grid[y, x] = rnd.choice('uuRsP' if rnd.random() < .6 else 'us')
grid[H - 2:, :][np.isin(grid[H - 2:, :], ['.'])] = 'T'
grid[road & np.isin(grid, ['.'])] = '='; grid[lane & np.isin(grid, ['.'])] = '='
# ---------------------------------------------------------------- reachability
sys.path.insert(0, HERE); from build import bfs
SOL = set('#TPRCHXu')
def reach_of(gr):
    free = np.vectorize(lambda c: c not in SOL)(gr)
    for o in objs:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'door'): free[o['y'], o['x']] = False
    return free, bfs(free, 75, 80)
for it in range(8):
    free, r2 = reach_of(grid)
    lost = free & ~r2
    deco_lost = ndimage.binary_dilation(lost, iterations=1) & np.isin(grid, list('uRsPT')) & (np.arange(H)[:, None] > WALL_Y + 3)
    if not lost.any() or not deco_lost.any(): break
    grid[deco_lost] = '.'
free, r2 = reach_of(grid); lostn = int((free & ~r2).sum())
grid[free & ~r2 & (grid == '.')] = 'u' if False else grid[free & ~r2 & (grid == '.')]
bad = []
for o in objs:
    x, y = o['x'], o['y']
    nb = any(0 <= y + b < H and 0 <= x + a < W and r2[y + b, x + a] for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)))
    if o['type'] in ('door', 'npc', 'chest', 'sign', 'waystone', 'clue') and not nb: bad.append(o.get('id') or o['type'])
    elif o['type'] in ('hidden', 'mark', 'landmark', 'vista') and not (r2[y, x] or nb): bad.append(o.get('id'))
    elif o['type'] == 'exit' and not any(r2[y + b, x + a] for a in range(o['w']) for b in range(o['h'])): bad.append('exit:' + o['label'])
for k, (x, y, _) in spawns.items():
    if not r2[int(y), int(x)]: bad.append('spawn:' + k)
print(f'felt5: reach {int(r2.sum())} cells, isolated floor {lostn}, unreachable {bad}')
if bad: raise SystemExit('unreachable: ' + str(bad))
# ---------------------------------------------------------------- ground (painted in code)
print('ground...')
gh, gw = H * G, W * G
def sn(scale, seed):
    return inkart.vnoise(gh, gw, scale, seed)
def up(a, blur=0):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((gw, gh), Image.BILINEAR)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255.
n1 = sn(300, 1) * .55 + sn(90, 2) * .3 + sn(22, 3) * .15
earth_a = np.array([112, 101, 86.]); earth_b = np.array([88, 80, 70.])
img = earth_a * (1 - n1[..., None]) + earth_b * n1[..., None]
grain = sn(3, 4) - .5; img += grain[..., None] * 14
# dead grass / moss patches away from roads
rl = (road | lane).astype(float); away = up(np.clip(ndimage.distance_transform_edt(~(road | lane)) / 4, 0, 1))
gv = sn(220, 5) * .6 + sn(60, 6) * .4 + away * .25
gm = np.clip((gv - .66) / .12, 0, 1)
grass_c = np.array([96, 94, 66.]) * (1 + (sn(4, 7)[..., None] - .5) * .35)
img = img * (1 - gm[..., None] * .85) + grass_c * gm[..., None] * .85
# ash drifts
ash = np.clip((sn(260, 8) * .7 + sn(70, 9) * .3 - .62) / .2, 0, 1) * .3
img = img * (1 - ash[..., None]) + np.array([150, 145, 138.]) * ash[..., None]
# scorch around ruins and burnt houses
sc = np.zeros((H, W))
for key, x0, foot, spec, q in B:
    if spec.get('ruin') or spec.get('dmg', 0) > .5: sc[max(0, foot - 7):min(H, foot + 3), max(0, x0 - 2):min(W, x0 + spec['W'] + 2)] = 1
sc[WALL_Y:WALL_Y + 6, 30:50] = 1; sc[WALL_Y:WALL_Y + 6, 101:120] = 1
scorch = up(ndimage.gaussian_filter(sc, 1.6)) * np.clip(.35 + sn(40, 10), 0, 1)
img *= (1 - .5 * scorch)[..., None]
# packed lanes + camp clearing
lm = up(ndimage.gaussian_filter((lane | camp).astype(float), .9)); lm = np.clip((lm - .25) / .45 + (sn(30, 11) - .5) * .5, 0, 1)
packed = np.array([140, 126, 104.]) * (1 + (sn(6, 12)[..., None] - .5) * .18)
img = img * (1 - lm[..., None] * .8) + packed * lm[..., None] * .8
# cobble roads: voronoi stones
rm = up(ndimage.gaussian_filter(road.astype(float), .7)); rmask = np.clip((rm - .35) / .3 + (sn(40, 13) - .5) * .9 * (rm < .97), 0, 1) > .5
ys, xs = np.nonzero(rmask)
sx = np.arange(0, gw, 11.0); sy = np.arange(0, gh, 9.0)
SX, SY = np.meshgrid(sx, sy); rr = np.random.RandomState(14)
SX = SX + (np.arange(SX.shape[0])[:, None] % 2) * 5.5 + rr.uniform(-3, 3, SX.shape); SY = SY + rr.uniform(-2.5, 2.5, SY.shape)
seeds = np.stack([SX.ravel(), SY.ravel()], 1); tree = cKDTree(seeds)
dd, ii = tree.query(np.stack([xs, ys], 1).astype(np.float32), k=2, workers=-1)
edge = dd[:, 1] - dd[:, 0]; ctone = rr.uniform(.82, 1.12, len(seeds))[ii[:, 0]]; cwarm = rr.uniform(-6, 6, len(seeds))[ii[:, 0]]
stone = np.array([132, 124, 112.])
sc_col = stone[None, :] * ctone[:, None] + np.array([1, .4, -.6])[None, :] * cwarm[:, None]
sc_col *= (1 - .18 * np.clip(dd[:, 0] / 7, 0, 1))[:, None]                     # domed: darker toward the stone rim
joint = np.clip(1 - edge / 1.8, 0, 1)[:, None]
sc_col = sc_col * (1 - joint * .55) + np.array([52, 46, 40.]) * joint * .55
img[ys, xs] = sc_col
verge = up(ndimage.gaussian_filter((ndimage.binary_dilation(road, iterations=1) & ~road).astype(float), .7)) * (~rmask)
img *= (1 - .25 * verge)[..., None]
# building + wall cast shadows (light from upper left: shadows fall to the lower right)
shm = Image.new('L', (gw, gh), 0); sd = ImageDraw.Draw(shm)
for x0, y0, x1, y1, hf in shadows:
    sd.polygon([(x1 * G, y0 * G), (x1 * G + hf * .45 * G, y0 * G + hf * .25 * G), (x1 * G + hf * .45 * G, y1 * G + .55 * G), (x0 * G + .6 * G, y1 * G + .55 * G), (x0 * G, y1 * G)], fill=150)
sd.rectangle([0, WALL_Y * G, gw, (WALL_Y + 2.2) * G], fill=170)
for q in props:
    if q.get('id', '').startswith(('p_tent', 'p_well', 'p_wagon', 'p_memorial')): sd.ellipse([(q['x'] - 1.6) * G, (q['y'] - .5) * G, (q['x'] + 2.2) * G, (q['y'] + .4) * G], fill=120)
shm = np.asarray(shm.filter(ImageFilter.GaussianBlur(G * .35)), np.float32) / 255.
img *= (1 - .42 * shm)[..., None]
# the north band: sky above the wall (seen above the parapet and through the breaches)
yy2 = np.arange(gh, dtype=np.float32)[:, None] / G
skyw = np.clip((WALL_Y - 2 - yy2) / 3, 0, 1)
skyc = np.array([206, 198, 186.]) * (1 - np.clip(yy2 / 26, 0, 1))[..., None] + np.array([150, 144, 138.]) * np.clip(yy2 / 26, 0, 1)[..., None]
skyc = skyc + (sn(160, 15)[..., None] - .5) * 18
img = img * (1 - skyw[..., None]) + np.broadcast_to(skyc, img.shape) * skyw[..., None]
# paper / watercolour finish: soft bleed, pooled edges, sepia grade, light vignette at the map edges
blur = np.asarray(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32)
img = img * .7 + blur * .3
lum = img.mean(2, keepdims=True); img = img * .8 + lum * .2
img = img * np.array([1.03, 1.0, .93]) + (sn(2, 16)[..., None] - .5) * 8
_xx = np.broadcast_to(np.arange(gw)[None, :], (gh, gw)); _yy = np.broadcast_to(np.arange(gh)[:, None], (gh, gw))
ex = np.minimum.reduce([_xx / G, (gw - _xx) / G, _yy / G * 9, (gh - _yy) / G])
img *= (.82 + .18 * np.clip(ex / 6, 0, 1))[..., None]
gimg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
gp = save(gimg, 'ground', webp=True)
# ---------------------------------------------------------------- tufts + hd + json
gcell = np.asarray(Image.fromarray((gm * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)) > 90
tufts = []
for y in range(WALL_Y + 3, H - 1):
    for x in range(1, W - 1):
        if grid[y, x] != '.': continue
        if rnd.random() < (.45 if gcell[y, x] else .12): tufts.append([round(x + rnd.random(), 2), round(y + .3 + rnd.random() * .7, 2), 3 if rnd.random() < .2 else rnd.randrange(3)])
allp = [tunnel_q] + sorted(props + band_q, key=lambda q: q['y'])
webs = [[129.4, 111.2, 131.6, 112.6, .5, .3], [136.0, 111.0, 138.4, 112.2, .6, .3], [127.2, 113.8, 129.0, 115.6, .4, .25], [139.2, 113.5, 141.0, 115.0, .5, .3]]
hd = {'D': HD, 'ground': gp, 'backdrop': backdrop, 'props': allp, 'decoArt': deco, 'lights': lights, 'smoke': smoke, 'grade': 'dusk', 'gradeCol': 'rgb(214,203,192)', 'flick': flick,
      'tufts': tufts, 'fires': fires, 'fx': {'particles': 'ash', 'birds': 5, 'mist': 6, 'tuft': ['#57534a', '#625d50', '#4a463d']}, 'webs': webs}
legend = {'.': 'dirt', '=': 'dirt', '#': 'cliff', 'X': {'ground': 'dirt', 'solid': True}, 'H': {'ground': 'dirt', 'solid': True},
          'T': {'ground': 'dirt', 'deco': 'tree'}, 'P': {'ground': 'dirt', 'deco': 'pine'}, 'R': {'ground': 'dirt', 'deco': 'boulder'},
          'u': {'ground': 'dirt', 'deco': 'bush'}, 's': {'ground': 'dirt', 'deco': 'stump', 'solid': False}, 'w': {'ground': 'dirt', 'deco': 'mushrooms', 'solid': False}}
out = {k: SRC[k] for k in ('type', 'area', 'title', 'bgm', 'battleBgm', 'tileset', 'tile', 'id', 'name') if k in SRC}
out['title'] = dict(out.get('title', {}), sub='왕도의 거대한 성벽 그늘 아래, 불타 버린 외곽 마을')
out.update({'region': SRC.get('region'), 'viewZoom': 1.3, 'grade': 'ash', 'fog': .22, 'ash': 60, 'wind': [5, 1], 'w': W, 'h': H, 'legend': legend, 'skyTop': 20,
            'camZones': [{'x0': 6, 'y0': 28, 'x1': 144, 'y1': 32, 'zoom': .9, 'look': -3.5, 'f': 6}],
            'solid': ['#', 'C', 'X', 'H', 'T', 'P', 'R', 'u', '~'], 'ground': [''.join(r) for r in grid], 'objects': objs, 'spawns': spawns, 'hd': hd,
            'note': 'GENERATED by tools/hd/fields/build_felt5.py (felt v5: everything drawn in code, assets/world/felt5) - do not hand-edit'})
if 'mapPos' in SRC: out['mapPos'] = SRC['mapPos']
json.dump(out, open(rel('maps/felt.json'), 'w'), ensure_ascii=False, indent=1)
import re
qt = open(rel('maps/quests.json'), encoding='utf-8').read()
qt2 = re.sub(r'\{"map": "felt", "x": \d+, "y": \d+, "label": "아라크네의 폐공방"', '{"map": "felt", "x": %d, "y": %d, "label": "아라크네의 폐공방"' % (ag['x'], ag['y']), qt)
if qt2 != qt: open(rel('maps/quests.json'), 'w', encoding='utf-8').write(qt2)
print('arachne gate at', ag['x'], ag['y'], '| props', len(allp), '| files', len(_saved))
json.dump({'grid': [''.join(r) for r in grid]}, open('/tmp/v5/grid.json', 'w'))
