"""Felt v4 = the Grok composition built from the town-art room's final D=3 parts (owner 10-23 「그록 그림 대표」 + credits approved).
Parts: handoff/claude/felt_grok_build/final/ (the town-art room) -> copied to assets/world/felt/ (fixed here, 0 credits):
  fountain water darkened (canon = dry cracked fountain), the "o305" text on the weapon-shop sign wiped, the baked-in villager in front of the
  general store hidden behind a well. Places = grok_foot x 0.56 world px (the parts are drawn at 0.7 x Grok size, so the gaps shrink with them).
Ground = code (palette.json colours): packed-dirt roads traced from the key art as polylines, a cobbled plaza ring, dark earth with dead
  grass, a fenced grave lawn. Solid = each picture's bottom opaque width. Doors / marks / NPCs / clues / waystones / signs follow felt.json
  (other rooms' data, now in maps/src/felt.json: edit THAT, then rebuild). Writes maps/felt.json + maps/ch1.json (felt + field_felt joined
  at the south gate). NPC spots: the near rule (2번방) with the spots tuned for this layout (NEAR below wins over src).
python3 tools/hd/build_felt.py [parts dir]   (default: the art room's handoff folder)"""
import os, sys, json, copy, math, random
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'handoff', 'claude', 'felt_grok_build', 'final')
OUT = os.path.join(ROOT, 'assets', 'world', 'felt'); os.makedirs(OUT, exist_ok=True)
S, T, D, GD = 0.56, 16, 3, 3                      # world px per Grok px, tile, part D, ground D (= parts: one pixel size everywhere)
PJ = json.load(open(os.path.join(SRC, 'parts.json')))['parts']
FF = json.load(open(os.path.join(ROOT, 'maps', 'field_felt.json'))); _top = [x for x, c in enumerate(FF['ground'][0]) if c in ".'=,"]
W, H = max(54, int(860 * S // T) - (_top[0] + _top[-1]) // 2 + FF['w']), 35                                     # 1536 x 864 Grok px x 0.56 = 860 x 484 world px (+ 2 rows below the south stalls + 3 rows of seam outside the south gate)
g2w = lambda gx, gy: (gx * S, gy * S)              # Grok px -> world px
rnd = random.Random(7)

# ---------- parts (copy + 0-credit fixes) ----------
def load(pid): return Image.open(os.path.join(SRC, PJ[pid]['img'])).convert('RGBA')
IM = {pid: load(pid) for pid in PJ}
def dry_fountain(im):   # (unused since the art room's statue fountain is dry)                               # blue water -> dark still water / cracked basin (colours from palette base24 + accent #2f4a52)
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

# ---------- placement ----------
SC = json.load(open(os.path.join(SRC, 'scene_suggest.json')))['scene']   # the town-art room's entrance scene + district accents (Grok px)
SC = [['sign_post', 990, 818] if e[0] == 'sign_post' else e for e in SC]   # 이정표 비켜 세움 (남문 간판과 겹침, art room)
SEAM = [('dead_tree', 700, 975), ('dead_tree', 1040, 985), ('bush_b', 790, 960), ('bush_b', 935, 965), ('bush_b', 610, 1000), ('bush_b', 1150, 995),
        ('stone_low', 650, 925), ('stone_low', 1085, 930), ('bush_b', 480, 990), ('stone_low', 1250, 990)]   # 남문 바깥 이음매 (art room 30131c70): town ground runs 3 rows past the gate, dry scrub on it, field trees start below
EXTRA = [tuple(e) for e in SC] + SEAM + [  # + mine (Grok px): plaza lamps / bench, market, inn, herbs, web quarter, castle rubble
 ('tombs', 1450, 305), ('fence_iron', 1215, 335), ('fence_iron', 1300, 340), ('candelabra', 1000, 215), ('cocoons', 1500, 640),
 ('lamp', 600, 452), ('lamp', 785, 452), ('lamp', 600, 575), ('lamp', 790, 575), ('lamp', 175, 560),
 ('bench', 742, 585), ('crates', 575, 405), ('barrels', 395, 425), ('cart', 850, 430),
 ('barrels', 965, 478), ('herb_rack', 1175, 668), ('rubble', 1385, 725), ('rubble', 545, 255), ('rubble', 880, 262), ('crates', 1105, 850)]
props, solid = [], [[False] * W for _ in range(H)]
for x in range(W): solid[0][x] = solid[H - 1][x] = True
for y in range(H): solid[y][0] = solid[y][W - 1] = True
for y in range(int(175 * S // T)): solid[y] = [True] * W           # far backdrop above the castle line
GX = int(860 * S // T)                                               # south road column
for y in range(H - 4, H):                                            # seam outside the gate: only the road walks on to the ash field
    for x in range(W): solid[y][x] = abs(x - GX) > 1
def bottom_span(im):                               # opaque columns in the bottom 12 % of the picture
    al = np.asarray(im)[..., 3]; h = al.shape[0]; rows = al[int(h * .88):]; cols = np.where(rows.max(0) > 0)[0]
    return (cols[0], cols[-1]) if len(cols) else (0, al.shape[1] - 1)
def place(pid, gx, gy, n=''):
    p = PJ[pid]; im = IM[pid]; wx, wy = g2w(gx, gy); c0, c1 = bottom_span(im); kind = p.get('kind', 'prop')
    x0, x1 = wx + (c0 - p['ax']) / D, wx + (c1 - p['ax']) / D; inset = (x1 - x0) * (.1 if kind == 'building' else .2)
    depth = min(p['h'] / D * .32, 44) if kind == 'building' else min(p['h'] / D * .3, 10)
    if pid in ('castle_l', 'castle_r'): depth = 60
    if pid == 'fountain': depth = p['w'] / D * .36                 # basin only (the king statue stands tall above it)
    sx0, sx1, sy1, sy0 = int((x0 + inset) // T), int((x1 - inset) // T), int((wy - 3) // T), int((wy - depth) // T)
    if pid in ('lamp', 'sign_post', 'brazier', 'candelabra'): sx0 = sx1 = int(wx // T); sy0 = sy1 = int((wy - 1) // T)
    if pid == 'string_lights': sx0, sx1 = int((wx - 30) // T), int((wx + 30) // T); sy0 = sy1 = -9              # walk under the lanterns (posts only)
    if pid == 'south_gate': sy0 = sy1 = int((wy - 3) // T); sx0, sx1 = int((wx - 53) // T), int((wx + 53) // T)  # posts + side fences; the opening is cut below
    for y in range(max(0, sy0), min(H, sy1 + 1)):
        for x in range(max(0, sx0), min(W, sx1 + 1)): solid[y][x] = not (pid == 'south_gate' and abs((x + .5) * T - wx) < 24)
    if pid == 'string_lights':
        for x in (sx0, sx1): solid[int((wy - 1) // T)][x] = True
    big = kind == 'building' and pid != 'fountain'
    props.append({'id': pid + n, 'role': p.get('role', ''), 'img': f'assets/world/felt/{p["img"]}', 'x': wx / T, 'y': wy / T, 'ax': p['ax'], 'ay': p['ay'],
                  'solid': None if pid in ('south_gate', 'string_lights') else [sx0, sy0, sx1, sy1], 'fade': 1 if big or pid in ('watchtower', 'mausoleum', 'south_gate', 'string_lights') else 0, 'shadow': 0 if big else 1})
for pid, p in PJ.items():
    if 'grok_foot' in p: place(pid, *p['grok_foot'])
ss = PJ['shop_sign']; place('well', ss['grok_foot'][0] - 92 / D / S, ss['grok_foot'][1] + 4, '_shop')   # covers the villager baked into the store art
for i, (pid, gx, gy) in enumerate(EXTRA): place(pid, gx, gy, f'_{i}')
P = {q['id']: q for q in props}
for f in os.listdir(OUT):                                           # the folder holds exactly the pictures this map uses
    if f != 'ground.png': os.remove(os.path.join(OUT, f))
for pid, im in IM.items():
    if any(q['img'].endswith('/' + PJ[pid]['img']) for q in props): im.save(os.path.join(OUT, PJ[pid]['img']), optimize=True)

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
 ([(620, 540), (470, 610), (300, 690), (170, 790)], 46), ([(700, 560), (760, 650), (840, 760), (860, 864), (860, 1010)], 56),
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
e = n1 * .6 + n2 * .3 + n3 * .1; t = np.clip((e - .25) / .5, 0, 1)[..., None]; img[:] = cols['d2'] * (1 - t) + cols['d3'] * t   # soft mottling (low contrast, continuous)
tuft = (vnoise(1.5, 9) > .7) & (vnoise(10, 10) > .62); img[tuft] = cols['g1'] * .6 + cols['d2'] * .4
img[yard] = np.where((n3[yard] > .45)[:, None], cols['g1'], np.where((n2[yard] > .5)[:, None], cols['g1'] * .8 + cols['d3'] * .2, cols['d3']))
# roads: packed dirt, darker rim, ruts and pebbles
road = dr < 0; rim = (dr >= 0) & (dr < 3)
rv = n2 * .7 + n3 * .3; t = np.clip((rv[road] - .25) / .55, 0, 1)[:, None]; img[road] = cols['r2'] * (1 - t) + cols['r3'] * t   # soft packed dirt
img[rim] = cols['r0']; peb = road & (n3 > .8) & (vnoise(1.2, 4) > .7); img[peb] = cols['r5']; img[road & (vnoise(1.5, 5) > .86)] = cols['d4']
# plaza: cobble ring (stone cells by jittered grid), mortar in between, inner basin ring stones
cell = 4.0; jx, jy = vnoise(4, 6) * 1.6, vnoise(4, 7) * 1.6
cx, cy = (wxp + jx) / cell, (wyp + (np.floor((wxp + jx) / cell) % 2) * cell / 2 + jy) / cell
fx, fy = cx - np.floor(cx), cy - np.floor(cy); mort = (fx < .16) | (fy < .2); shade = vnoise(cell, 8)
plaza = pr < 1 + (n2 - .5) * .12
stone = sel([shade < .35, shade < .6, shade < .82], [cols['s1'], cols['s2'], cols['s3']], cols['s4'])
img[plaza] = np.where(mort[plaza][:, None], cols['s0'], stone[plaza]); img[plaza & (pr > .9) & (pr < .97)] = cols['s0']
# edges: darker toward the map border (no hard frame), backdrop band darker still
edge = np.minimum.reduce([wxp, wyp, W * T - wxp, H * T - wyp + 400])   # no dark band at the bottom: the ash field joins there; img *= np.clip(.55 + edge / 60, .55, 1)[..., None]
img[wyp < 175 * S] *= .7
# snap to the town palette (base24 + accents)
pal = np.array([hx(c) for c in (PAL['base24'] + PAL['accent8'] if PAL else [v for v in ('#201810',)])])
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - .47)[(yy % 4).astype(int), (xx % 4).astype(int)][..., None]   # ordered dither: fine 1-pixel grain instead of big blotches
img = img + BAYER * 12
flat = img.reshape(-1, 3); idx = np.empty(len(flat), int)
for i in range(0, len(flat), 1 << 18): idx[i:i + (1 << 18)] = np.argmin(((flat[i:i + (1 << 18), None, :] - pal[None]) ** 2).sum(2), 1)
Image.fromarray(pal[idx].reshape(GH, GW, 3).astype(np.uint8)).save(os.path.join(OUT, 'ground.png'), optimize=True)

# ---------- game objects (doors / NPCs / marks follow the new buildings) ----------
F = json.load(open(os.path.join(ROOT, 'maps', 'src', 'felt.json')))   # doors / NPCs / lines / clues = other rooms' data
def foot(pid, dx=0, dy=0): p = P[pid]; return [int(p['x']) + dx, int(p['y'] - .01) + dy]
rows = [['#' if solid[y][x] else '.' for x in range(W)] for y in range(H)]
DOOR = {'f_door_chief': 's_house', 'f_door_smith': 'se_house', 'f_door_herb': 'e_row', 'f_door_inn': 'inn', 'f_door_chapel': 'chapel',
        'f_door_atelier': 'linette', 'f_arachne_gate': 'web_arch', 'f_door_guard': 'watchtower', 'f_door_weapon': 'west_a', 'f_door_tool': 'shop_sign'}
EX = [int(860 * S // T), H - 1]                       # [17] south exit (3 tiles wide) -> 잿빛 들판
objs = []
for o in F['objects']:
    o = copy.deepcopy(o); t, i = o['type'], o.get('id')
    if t == 'door' and i in DOOR: o['x'], o['y'] = foot(DOOR[i])
    if i == 'f_arachne_gate': o.update(to='arachne', spawn='felt', scene='door:arachne', text='거미줄로 뒤덮인 폐공방 입구. 안쪽 깊은 곳에서 철사 긁는 소리가 난다.')   # 제1던전
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
        'f_toby': ['f_mark_fountain', 2, 4], 'f_gas': ['f_mark_gate', -2, -5]}
if not any(o['type'] == 'mark' for o in objs):
    objs += [{'type': 'mark', 'id': 'f_mark_fountain', 'x': foot('fountain', 0, -2)[0], 'y': foot('fountain', 0, -2)[1]},
             {'type': 'mark', 'id': 'f_mark_stall', 'x': foot('red_stall')[0], 'y': foot('red_stall')[1]}, {'type': 'mark', 'id': 'f_mark_gate', 'x': EX[0], 'y': EX[1] - 1}]
by = {o.get('id'): o for o in objs}
for o in objs:
    if o['type'] == 'npc':
        n = NEAR.get(o['id']) or o.get('near')
        if n and n[0] in by: o['near'] = n; r = by[n[0]]; o['x'], o['y'] = min(W - 2, max(1, r['x'] + n[1])), min(H - 2, max(1, r['y'] + n[2]))
for x in range(EX[0] - 1, EX[0] + 2): rows[H - 1][x] = '.'
fx_, fy_ = foot('fountain', 0, 1); objs.append({'type': 'waystone', 'id': 'ws_felt_plaza', 'x': fx_, 'y': fy_, 'name': '광장 분수', 'walk': True})
for o in objs:
    if o['type'] == 'door': rows[o['y'] + 1][o['x']] = '.'
    if o['type'] in ('npc', 'waystone', 'clue', 'sign'): rows[int(o['y'])][int(o['x'])] = '.'
# district lights (TOWN_LAYOUT 3) and threads toward the Arachne gate (4)
def lp(pid, dx, dy, r, col, a): x, y = P[pid]['x'] + dx, P[pid]['y'] + dy; return [x, y, r, col, a]
LIGHTS = [lp(next(q['id'] for q in props if q['id'].startswith('brazier')), 0, -.6, 60, '#ff8a3a', 1), lp('se_house', -1, -2, 56, '#ff7a2a', 1), lp('s_house', 0, -1, 40, '#ffb060', .6),
 lp('west_a', 0, -1, 44, '#ffc070', .8), lp('west_b', 0, -1, 44, '#ffc070', .8), lp('stall_n', 0, -1, 40, '#ffcc80', .7), lp('shop_sign', 0, -1, 40, '#ffc070', .6),
 lp('castle_l', 0, -1, 50, '#ff5a2a', .7), lp('castle_r', 0, -1, 50, '#ff5a2a', .7), lp('linette', 0, 0, 44, '#ffd0a0', .6),
 lp('chapel', 0, 0, 44, '#b080ff', .8), lp('mausoleum', -2, 0, 50, '#9a70e0', .6), lp('inn', 0, -1, 50, '#ffb060', .8),
 lp('e_row', 0, -1, 44, '#cfe0d8', .5), lp('web_arch', 0, -1, 56, '#c8d8ff', .7), lp('red_stall', 0, -1, 36, '#ffb070', .6), lp('fountain', 0, -1, 50, '#9fd8ff', .35)]
LIGHTS += [[q['x'], q['y'] - 1.4, 26, '#ffc070', .7] for q in props if q['id'].startswith('lamp_')]
LIGHTS += [[q['x'], q['y'] - .5, 22, '#ff6a2a', .9] for q in props if q['id'].startswith('ember_rubble')]           # 불씨 잔해 (art room)
LIGHTS += [[q['x'], q['y'] - 2.2, 22, '#c090ff', .7] for q in props if q['id'].startswith('candelabra')]
LIGHTS += [[q['x'], q['y'] - 2.2, 40, '#ffc880', .7] for q in props if q['id'].startswith('string_lights')]
# smoke (code, not baked): Rom's forge chimney (art room: se_house picture x~120, y~20) + the burned castle
se = P['se_house']; SMOKE = [[se['x'] + (120 - se['ax']) / D / T, se['y'] - (se['ay'] - 20) / D / T, 1]]
for c in ('castle_l', 'castle_r'): q = P[c]; SMOKE.append([q['x'] + .5, q['y'] - 5, 1.6])
ax0, ay0 = P['fountain']['x'] + 3, P['fountain']['y'] - 1; ax1, ay1 = P['web_arch']['x'] - 2, P['web_arch']['y'] - 1.5; WEBS = []
for i in range(14):
    t = (i / 13) ** .7; x = ax0 + (ax1 - ax0) * t; y = ay0 + (ay1 - ay0) * t; n = 1 + int(t * 3)
    for j in range(n): dx = (j - n / 2) * 1.1; WEBS.append([x + dx, y - 2 - (j % 2), x + dx + 1.2 + t, y - .2, .5 + t, .25 + .5 * t])
m = {k: F[k] for k in ('type', 'area', 'region', 'title', 'bgm', 'battleBgm', 'tileset', 'tile') if k in F}
m.update(id='felt', name='펠트', w=W, h=H, legend={'.': 'dirt', '#': 'cliff'}, solid=['#'], ground=[''.join(r) for r in rows], objects=objs,
         spawns={'default': [EX[0] + .5, EX[1] - 7.5, 'up'], 'world': [EX[0] + .5, EX[1] - 7.5, 'up'], 'field': [EX[0] + .5, EX[1] - 1.5, 'up'], 'arachne': [foot('web_arch')[0] + .5, foot('web_arch')[1] + 1.6, 'down']},   # start inside the south gate (forge, chief's house, statue ahead)
         hd={'D': GD, 'ground': 'assets/world/felt/ground.png', 'props': [dict(q, D=D) for q in props], 'lights': LIGHTS, 'webs': WEBS, 'smoke': SMOKE, 'grade': 'dusk'},
         note='GENERATED by tools/hd/build_felt.py from the town-art room parts + maps/src/felt.json (doors / NPCs / clues) - do not hand-edit')
json.dump(m, open(os.path.join(ROOT, 'maps', 'felt.json'), 'w'), ensure_ascii=False, indent=1)
FF = json.load(open(os.path.join(ROOT, 'maps', 'field_felt.json')))
top = [x for x, c in enumerate(FF['ground'][0]) if c in ".'=,"]; fxo = EX[0] - (top[0] + top[-1]) // 2
json.dump({'id': 'ch1', 'note': '1장 = 펠트 + 잿빛 들판 이어 붙인 지도 (세미 오픈월드). GENERATED by tools/hd/build_felt.py (field_felt sits under the south gate); field_felt.json is edited as it is',
           'compose': [{'map': 'felt', 'x': 0, 'y': 0}, {'map': 'field_felt', 'x': fxo, 'y': H}], 'region': 'ch1', 'area': 1}, open(os.path.join(ROOT, 'maps', 'ch1.json'), 'w'), ensure_ascii=False, indent=1)
print('ok felt', W, 'x', H, len(props), 'props', len(objs), 'objects; field_felt at x', fxo)
print('\n'.join(rows[y] if isinstance(rows[y], str) else ''.join(rows[y]) for y in range(H)))
