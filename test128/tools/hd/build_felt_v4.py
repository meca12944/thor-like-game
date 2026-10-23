"""Felt v4 = the Grok composition built from the town-art room's final D=3 parts (owner 10-23 「그록 그림 대표」 + credits approved).
Parts: handoff/claude/felt_grok_build/final/ (claude/linette-8dir 8be3cd86) -> copied to assets/world/felt_v4/ (fixed here, 0 credits):
  fountain water darkened (canon = dry cracked fountain), the "o305" text on the weapon-shop sign wiped, the baked-in villager in front of the
  general store hidden behind a well. Places = grok_foot x 0.56 world px (the parts are drawn at 0.7 x Grok size, so the gaps shrink with them).
Ground = code (palette.json colours): packed-dirt roads traced from the key art as polylines, a cobbled plaza ring, dark earth with dead
  grass, a fenced grave lawn. Solid = each picture's bottom opaque width. Doors / marks / NPCs / clues / waystones / signs follow felt.json
  (other rooms' data) exactly like v3. Writes maps/felt_v4.json + maps/ch1_v4.json (felt_v4 + field_felt joined at the south exit).
python3 tools/hd/build_felt_v4.py [parts dir]   (default: the art room's handoff folder)   test: ?go=ch1_v4"""
import os, sys, json, copy, math, random
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'handoff', 'claude', 'felt_grok_build', 'final')
OUT = os.path.join(ROOT, 'assets', 'world', 'felt_v4'); os.makedirs(OUT, exist_ok=True)
S, T, D, GD = 0.56, 16, 3, 2                      # world px per Grok px, tile, part D, ground D
PJ = json.load(open(os.path.join(SRC, 'parts.json')))['parts']
FF = json.load(open(os.path.join(ROOT, 'maps', 'field_felt.json'))); _top = [x for x, c in enumerate(FF['ground'][0]) if c in ".'=,"]
W, H = max(54, int(860 * S // T) - (_top[0] + _top[-1]) // 2 + FF['w']), 32                                     # 1536 x 864 Grok px x 0.56 = 860 x 484 world px (+ 2 rows below the south stalls)
g2w = lambda gx, gy: (gx * S, gy * S)              # Grok px -> world px
rnd = random.Random(7)

# ---------- parts (copy + 0-credit fixes) ----------
def load(pid): return Image.open(os.path.join(SRC, PJ[pid]['img'])).convert('RGBA')
IM = {pid: load(pid) for pid in PJ}
def dry_fountain(im):                              # blue water -> dark still water / cracked basin (colours from palette base24 + accent #2f4a52)
    a = np.asarray(im).astype(float); r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    blue = (b > r + 18) & (b > g - 4) & (al > 0); L = (.3 * r + .59 * g + .11 * b) / 255
    dark = np.array([23, 17, 12.]); teal = np.array([47, 74, 82.]); mud = np.array([62, 54, 46.])
    t = np.clip((L - .25) / .6, 0, 1)[..., None]; col = dark * (1 - t) + np.where(t > .55, mud, teal) * t
    a[..., :3] = np.where(blue[..., None], col, a[..., :3]); return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
def wipe_sign(im, box=(73, 116, 123, 137)):         # "o305" -> blank wooden plate
    a = np.asarray(im).copy(); x0, y0, x1, y1 = box; p = a[y0:y1, x0:x1, :3].astype(int); L = p.sum(2)
    base = np.median(p[L < np.percentile(L, 45)], 0).astype(np.uint8); hi = L > np.percentile(L, 45)
    sub = a[y0:y1, x0:x1]; sub[hi, :3] = base; a[y0:y1, x0:x1] = sub; return Image.fromarray(a, 'RGBA')
def ragged(im, r=14):                               # cut sides (opaque right up to the picture edge) -> torn, dithered edge, no hard rectangle
    a = np.asarray(im).copy(); al = a[..., 3].astype(float); h, w = al.shape; op = al > 0
    rng = np.random.default_rng(w * 7 + h); nz = rng.random((h // 3 + 1, w // 3 + 1)).repeat(3, 0).repeat(3, 1)[:h, :w]   # 1 world px blocks
    yy, xx = np.mgrid[0:h, 0:w]; dist = np.full((h, w), 1e9)
    for side, d in (('l', xx), ('r', w - 1 - xx), ('t', yy), ('b', h - 1 - yy)):
        edge = {'l': op[:, 0], 'r': op[:, -1], 't': op[0], 'b': op[-1]}[side]
        if edge.mean() > .12: dist = np.minimum(dist, d)
    keep = np.clip(dist / r + (nz - .5) * .9, 0, 1) > .35
    a[..., 3] = np.where(keep, a[..., 3], 0); return Image.fromarray(a, 'RGBA')
IM['fountain'] = dry_fountain(IM['fountain'])
for pid in IM:
    if PJ[pid].get('kind') == 'building' and pid not in ('linette', 'bl_house'): IM[pid] = ragged(IM[pid]); IM['west_a'] = wipe_sign(IM['west_a'])
for pid, im in IM.items(): im.save(os.path.join(OUT, PJ[pid]['img']), optimize=True)

# ---------- placement ----------
EXTRA = [  # props with no Grok spot: (part, Grok x, y) - district accents from TOWN_LAYOUT_ko.md 3)
 ('tombs', 1300, 292), ('tombs', 1450, 305), ('fence_iron', 1215, 335), ('fence_iron', 1300, 340),          # NE chapel yard
 ('lamp', 600, 452), ('lamp', 785, 452), ('lamp', 600, 575), ('lamp', 790, 575), ('lamp', 300, 470), ('lamp', 175, 560),  # plaza + W market
 ('bench', 742, 585), ('crates', 575, 405), ('barrels', 395, 425), ('cart', 850, 430),                    # plaza / market
 ('barrels', 965, 478), ('herb_rack', 1175, 668), ('rubble', 1385, 725), ('rubble', 1500, 640),            # inn / herbs / web quarter
 ('anvil', 900, 760), ('woodpile', 1025, 745), ('sign_post', 815, 705), ('brazier', 1000, 812),          # S entrance (forge, Gas' brazier)
 ('rubble', 545, 255), ('rubble', 880, 262), ('crates', 1105, 850)]
props, solid = [], [[False] * W for _ in range(H)]
for x in range(W): solid[0][x] = solid[H - 1][x] = True
for y in range(H): solid[y][0] = solid[y][W - 1] = True
for y in range(int(175 * S // T)): solid[y] = [True] * W           # far backdrop above the castle line
def bottom_span(im):                               # opaque columns in the bottom 12 % of the picture
    al = np.asarray(im)[..., 3]; h = al.shape[0]; rows = al[int(h * .88):]; cols = np.where(rows.max(0) > 0)[0]
    return (cols[0], cols[-1]) if len(cols) else (0, al.shape[1] - 1)
def place(pid, gx, gy, n=''):
    p = PJ[pid]; im = IM[pid]; wx, wy = g2w(gx, gy); c0, c1 = bottom_span(im); kind = p.get('kind', 'prop')
    x0, x1 = wx + (c0 - p['ax']) / D, wx + (c1 - p['ax']) / D; inset = (x1 - x0) * (.1 if kind == 'building' else .2)
    depth = min(p['h'] / D * .32, 44) if kind == 'building' else min(p['h'] / D * .3, 10)
    if pid in ('castle_l', 'castle_r'): depth = 60
    if pid == 'fountain': depth = p['h'] / D * .55
    sx0, sx1, sy1, sy0 = int((x0 + inset) // T), int((x1 - inset) // T), int((wy - 3) // T), int((wy - depth) // T)
    if pid in ('lamp', 'sign_post', 'brazier'): sx0 = sx1 = int(wx // T); sy0 = sy1 = int((wy - 1) // T)
    for y in range(max(0, sy0), min(H, sy1 + 1)):
        for x in range(max(0, sx0), min(W, sx1 + 1)): solid[y][x] = True
    big = kind == 'building' and pid != 'fountain'
    props.append({'id': pid + n, 'role': p.get('role', ''), 'img': f'assets/world/felt_v4/{p["img"]}', 'x': wx / T, 'y': wy / T, 'ax': p['ax'], 'ay': p['ay'],
                  'solid': [sx0, sy0, sx1, sy1], 'fade': 1 if big or pid in ('watchtower', 'mausoleum') else 0, 'shadow': 0 if big else 1})
for pid, p in PJ.items():
    if 'grok_foot' in p: place(pid, *p['grok_foot'])
ss = PJ['shop_sign']; place('well', ss['grok_foot'][0] - 92 / D / S, ss['grok_foot'][1] + 4, '_shop')   # covers the villager baked into the store art
for i, (pid, gx, gy) in enumerate(EXTRA): place(pid, gx, gy, f'_{i}')
P = {q['id']: q for q in props}

# ---------- code ground (D=2) ----------
GW, GH = W * T * GD, H * T * GD
PAL = json.load(open(os.path.join(SRC, '..', '..', 'felt_grok_layout', 'palette.json'))) if os.path.exists(os.path.join(SRC, '..', '..', 'felt_grok_layout', 'palette.json')) else None
hx = lambda s: np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], float)
yy, xx = np.mgrid[0:GH, 0:GW].astype(float); wxp, wyp = xx / GD, yy / GD      # world px of every ground pixel
def vnoise(scale, seed):                           # smooth value noise in world px
    r = np.random.default_rng(seed); gw, gh = int(W * T / scale) + 3, int(H * T / scale) + 3; g = r.random((gh, gw))
    fx, fy = wxp / scale, wyp / scale; ix, iy = fx.astype(int), fy.astype(int); tx, ty = fx - ix, fy - iy; tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b, c, d = g[iy, ix], g[iy, ix + 1], g[iy + 1, ix], g[iy + 1, ix + 1]; return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty
def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; t = np.clip(((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy), 0, 1); return np.hypot(px - ax - t * dx, py - ay - t * dy)
ROADS = [  # Grok px polylines, width (the key art's road web: plaza hub, radial roads + ring, south exit)
 ([(692, 470), (620, 390), (540, 300), (470, 235)], 46), ([(700, 420), (760, 330), (790, 255)], 40), ([(760, 430), (880, 330), (990, 230)], 44),
 ([(800, 480), (960, 470), (1110, 530), (1270, 600), (1430, 700)], 54), ([(600, 470), (440, 430), (280, 470), (120, 510), (0, 520)], 50),
 ([(620, 540), (470, 610), (300, 690), (170, 790)], 46), ([(700, 560), (760, 650), (840, 760), (860, 864)], 56),
 ([(250, 780), (500, 800), (840, 790), (1100, 760), (1300, 720)], 42), ([(840, 560), (1000, 640), (1120, 700)], 40),
 ([(1040, 250), (1180, 280)], 30), ([(470, 235), (600, 228), (800, 240), (990, 230)], 34)]
dr = np.full((GH, GW), 1e9)
for pts, w in ROADS:
    for (a, b) in zip(pts, pts[1:]):
        (ax, ay), (bx, by) = g2w(*a), g2w(*b); dr = np.minimum(dr, seg_dist(wxp, wyp, ax, ay, bx, by) - w * S / 2)
n1, n2, n3 = vnoise(18, 1), vnoise(6, 2), vnoise(2.5, 3)
dr = dr + (n1 - .5) * 10 + (n2 - .5) * 4                                   # ragged road edges
pcx, pcy = g2w(692, 478); pr = np.hypot((wxp - pcx) / (150 * S), (wyp - pcy) / (95 * S))   # plaza ellipse (1 = rim)
yard = np.hypot((wxp - 1330 * S) / (210 * S), (wyp - 255 * S) / (70 * S)) < 1 + (n1 - .5) * .3
cols = {k: hx(v) for k, v in dict(d0='#201810', d1='#2e2318', d2='#38291b', d3='#42301f', d4='#4f3721', r0='#5b4127', r1='#6b4b2c', r2='#76583a',
        r3='#876442', r4='#9d744c', r5='#ac8863', s0='#312b26', s1='#4b4138', s2='#5d4c3c', s3='#675d53', s4='#877360', g0='#2e2318', g1='#4d5a2c', g2='#3e362e').items()}
img = np.zeros((GH, GW, 3))
def sel(conds, cs, other): return np.select([c[..., None] for c in conds], cs, other)
# earth: dark dirt mottled, dead grass tufts
e = n1 * .6 + n2 * .3 + n3 * .1; img[:] = sel([e < .35, e < .5, e < .65], [cols['d1'], cols['d2'], cols['d3']], cols['d4'])
tuft = (vnoise(1.5, 9) > .7) & (vnoise(10, 10) > .62); img[tuft] = cols['g1'] * .6 + cols['d2'] * .4
img[yard] = np.where((n3[yard] > .5)[:, None], cols['g1'] * .75, cols['g1'] * .45 + cols['d2'] * .55)
# roads: packed dirt, darker rim, ruts and pebbles
road = dr < 0; rim = (dr >= 0) & (dr < 3)
rv = n2 * .7 + n3 * .3; img[road] = sel([rv[road] < .35, rv[road] < .55, rv[road] < .75], [cols['r1'], cols['r2'], cols['r3']], cols['r4'])
img[rim] = cols['r0']; peb = road & (n3 > .8) & (vnoise(1.2, 4) > .7); img[peb] = cols['r5']; img[road & (vnoise(1.5, 5) > .86)] = cols['d4']
# plaza: cobble ring (stone cells by jittered grid), mortar in between, inner basin ring stones
cell = 4.0; jx, jy = vnoise(4, 6) * 1.6, vnoise(4, 7) * 1.6
cx, cy = (wxp + jx) / cell, (wyp + (np.floor((wxp + jx) / cell) % 2) * cell / 2 + jy) / cell
fx, fy = cx - np.floor(cx), cy - np.floor(cy); mort = (fx < .16) | (fy < .2); shade = vnoise(cell, 8)
plaza = pr < 1 + (n2 - .5) * .12
stone = sel([shade < .35, shade < .6, shade < .82], [cols['s1'], cols['s2'], cols['s3']], cols['s4'])
img[plaza] = np.where(mort[plaza][:, None], cols['s0'], stone[plaza]); img[plaza & (pr > .9) & (pr < .97)] = cols['s0']
# edges: darker toward the map border (no hard frame), backdrop band darker still
edge = np.minimum.reduce([wxp, wyp, W * T - wxp, H * T - wyp]); img *= np.clip(.55 + edge / 60, .55, 1)[..., None]
img[wyp < 175 * S] *= .7
# snap to the town palette (base24 + accents)
pal = np.array([hx(c) for c in (PAL['base24'] + PAL['accent8'] if PAL else [v for v in ('#201810',)])])
flat = img.reshape(-1, 3); idx = np.argmin(((flat[:, None, :] - pal[None]) ** 2).sum(2), 1)
Image.fromarray(pal[idx].reshape(GH, GW, 3).astype(np.uint8)).save(os.path.join(OUT, 'ground.png'), optimize=True)

# ---------- game objects (doors / NPCs / marks follow the new buildings) ----------
F = json.load(open(os.path.join(ROOT, 'maps', 'felt.json')))
def foot(pid, dx=0, dy=0): p = P[pid]; return [int(p['x']) + dx, int(p['y'] - .01) + dy]
rows = [['#' if solid[y][x] else '.' for x in range(W)] for y in range(H)]
DOOR = {'f_door_chief': 's_house', 'f_door_smith': 'se_house', 'f_door_herb': 'e_row', 'f_door_inn': 'inn', 'f_door_chapel': 'chapel',
        'f_door_atelier': 'linette', 'f_arachne_gate': 'web_arch', 'f_door_guard': 'watchtower', 'f_door_weapon': 'west_a', 'f_door_tool': 'shop_sign'}
EX = [int(860 * S // T), H - 1]                       # [17] south exit (3 tiles wide) -> 잿빛 들판
objs = []
for o in F['objects']:
    o = copy.deepcopy(o); t, i = o['type'], o.get('id')
    if t == 'door' and i in DOOR: o['x'], o['y'] = foot(DOOR[i])
    elif t == 'exit': o.update(x=EX[0] - 1, y=EX[1], w=3, h=1)
    elif t == 'waystone': o['x'], o['y'] = foot('web_arch', -4, 1)                        # 폐공방 앞 비석
    elif t == 'clue' and i == 'f_clue_felix': o['x'], o['y'] = foot('web_arch', -2, 2)
    elif t == 'clue' and i == 'f_clue_bell': o['x'], o['y'] = foot('chapel', 2, 0)
    elif t == 'sign': o['x'], o['y'] = EX[0] + 2, EX[1] - 3
    elif t == 'mark':
        o['x'], o['y'] = {'f_mark_fountain': foot('fountain', 0, -2), 'f_mark_stall': foot('red_stall'), 'f_mark_gate': [EX[0], EX[1] - 1]}.get(i, [o['x'], o['y']])
    elif t == 'npc': o['x'], o['y'] = int(o['x'] * W / 56), int(o['y'] * H / 38)    # no near rule -> scaled spot (fixed below)
    objs.append(o)
NEAR = {'f_rom': ['f_door_smith', -1, 1], 'f_bart': ['f_door_chief', -3, 1], 'f_oswald': ['f_door_chapel', 0, 1], 'f_martha': ['f_door_inn', 0, 1],
        'f_sera': ['f_door_herb', 0, 1], 'f_ben': ['f_mark_stall', -4, 0], 'f_linette': ['f_door_atelier', -2, 1], 'f_luca': ['f_mark_fountain', 5, 1],
        'f_toby': ['f_mark_fountain', 2, 4], 'f_gas': ['f_mark_gate', -1, -3]}
if not any(o['type'] == 'mark' for o in objs):
    objs += [{'type': 'mark', 'id': 'f_mark_fountain', 'x': foot('fountain', 0, -2)[0], 'y': foot('fountain', 0, -2)[1]},
             {'type': 'mark', 'id': 'f_mark_stall', 'x': foot('red_stall')[0], 'y': foot('red_stall')[1]}, {'type': 'mark', 'id': 'f_mark_gate', 'x': EX[0], 'y': EX[1] - 1}]
by = {o.get('id'): o for o in objs}
for o in objs:
    if o['type'] == 'npc':
        n = o.get('near') or NEAR.get(o['id'])
        if n and n[0] in by: o['near'] = n; r = by[n[0]]; o['x'], o['y'] = min(W - 2, max(1, r['x'] + n[1])), min(H - 2, max(1, r['y'] + n[2]))
for x in range(EX[0] - 1, EX[0] + 2): rows[H - 1][x] = '.'
fx_, fy_ = foot('fountain', 0, 1); objs.append({'type': 'waystone', 'id': 'ws_felt_plaza', 'x': fx_, 'y': fy_, 'name': '광장 분수', 'walk': True})
for o in objs:
    if o['type'] == 'door': rows[o['y'] + 1][o['x']] = '.'
    if o['type'] in ('npc', 'waystone', 'clue', 'sign'): rows[int(o['y'])][int(o['x'])] = '.'
# district lights (TOWN_LAYOUT 3) and threads toward the Arachne gate (4)
def lp(pid, dx, dy, r, col, a): x, y = P[pid]['x'] + dx, P[pid]['y'] + dy; return [x, y, r, col, a]
LIGHTS = [lp('brazier_21', 0, -.6, 60, '#ff8a3a', 1), lp('se_house', -1, -2, 56, '#ff7a2a', 1), lp('s_house', 0, -1, 40, '#ffb060', .6),
 lp('west_a', 0, -1, 44, '#ffc070', .8), lp('west_b', 0, -1, 44, '#ffc070', .8), lp('stall_n', 0, -1, 40, '#ffcc80', .7), lp('shop_sign', 0, -1, 40, '#ffc070', .6),
 lp('castle_l', 0, -1, 50, '#ff5a2a', .7), lp('castle_r', 0, -1, 50, '#ff5a2a', .7), lp('linette', 0, 0, 44, '#ffd0a0', .6),
 lp('chapel', 0, 0, 44, '#b080ff', .8), lp('mausoleum', -2, 0, 50, '#9a70e0', .6), lp('inn', 0, -1, 50, '#ffb060', .8),
 lp('e_row', 0, -1, 44, '#cfe0d8', .5), lp('web_arch', 0, -1, 56, '#c8d8ff', .7), lp('red_stall', 0, -1, 36, '#ffb070', .6), lp('fountain', 0, -1, 50, '#9fd8ff', .35)]
LIGHTS += [[q['x'], q['y'] - 1.4, 26, '#ffc070', .7] for q in props if q['id'].startswith('lamp_')]
ax0, ay0 = P['fountain']['x'] + 3, P['fountain']['y'] - 1; ax1, ay1 = P['web_arch']['x'] - 2, P['web_arch']['y'] - 1.5; WEBS = []
for i in range(14):
    t = (i / 13) ** .7; x = ax0 + (ax1 - ax0) * t; y = ay0 + (ay1 - ay0) * t; n = 1 + int(t * 3)
    for j in range(n): dx = (j - n / 2) * 1.1; WEBS.append([x + dx, y - 2 - (j % 2), x + dx + 1.2 + t, y - .2, .5 + t, .25 + .5 * t])
m = {k: F[k] for k in ('type', 'area', 'region', 'title', 'bgm', 'battleBgm', 'tileset', 'tile') if k in F}
m.update(id='felt_v4', name='펠트', w=W, h=H, legend={'.': 'dirt', '#': 'cliff'}, solid=['#'], ground=[''.join(r) for r in rows], objects=objs,
         spawns={'default': [EX[0] + .5, EX[1] - 1.5, 'up'], 'world': [EX[0] + .5, EX[1] - 1.5, 'up'], 'field': [EX[0] + .5, EX[1] - 1.5, 'up']},
         hd={'D': GD, 'ground': 'assets/world/felt_v4/ground.png', 'props': [dict(q, D=D) for q in props], 'lights': LIGHTS, 'webs': WEBS, 'grade': 'dusk'},
         viewZoom=0.85, note='GENERATED by tools/hd/build_felt_v4.py from the town-art room parts + felt.json (doors / NPCs / clues)')
json.dump(m, open(os.path.join(ROOT, 'maps', 'felt_v4.json'), 'w'), ensure_ascii=False, indent=1)
FF = json.load(open(os.path.join(ROOT, 'maps', 'field_felt.json')))
top = [x for x, c in enumerate(FF['ground'][0]) if c in ".'=,"]; fxo = EX[0] - (top[0] + top[-1]) // 2
json.dump({'id': 'ch1_v4', 'note': 'test: Felt v4 (town-art room D=3 parts) + 잿빛 들판', 'region': 'ch1', 'area': 1, 'dropExits': ['felt'],
           'compose': [{'map': 'felt_v4', 'x': 0, 'y': 0}, {'map': 'field_felt', 'x': fxo, 'y': H}]}, open(os.path.join(ROOT, 'maps', 'ch1_v4.json'), 'w'), ensure_ascii=False, indent=1)
print('ok felt_v4', W, 'x', H, len(props), 'props', len(objs), 'objects; field_felt at x', fxo)
print('\n'.join(rows[y] if isinstance(rows[y], str) else ''.join(rows[y]) for y in range(H)))
