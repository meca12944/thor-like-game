"""Felt v4 = the Grok composition built from the town-art room's final D=3 parts (owner 10-23 「그록 그림 대표」 + credits approved).
Parts: handoff/claude/felt_grok_build/final/ (the town-art room) -> copied to assets/world/felt/ (fixed here, 0 credits):
  fountain pool wet again (owner 10-24 펠트 업그레이드: 물이 도는 분수; ripples / falling water = code in felt_live.js), the "o305" text on the weapon-shop sign wiped, the baked-in villager in front of the
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
W0, H = max(54, int(860 * S // T) - (_top[0] + _top[-1]) // 2 + FF['w']), 35                                     # 1536 x 864 Grok px x 0.56 = 860 x 484 world px (+ 2 rows below the south stalls + 3 rows of seam outside the south gate)
WALL, W = W0 - 1, W0 + 13                           # owner 10-24 펠트 업그레이드 2단계: the old east border = the town wall (palisade); 13 columns outside it = 쪽문 -> ruined path -> 아라크네 폐공방
GATE_ROWS, ROPE_ROW = (23, 24), 25                  # 동쪽 쪽문: rows 23-24 open, row 25 = 가스's rope barrier (the plank says 「출입 금지」, passable beside it)
g2w = lambda gx, gy: (gx * S, gy * S)              # Grok px -> world px
t2g = lambda tx, ty: (tx * T / S, ty * T / S)      # tile -> Grok px
rnd = random.Random(7)

# ---------- parts (copy + 0-credit fixes) ----------
def load(pid): return Image.open(os.path.join(SRC, PJ[pid]['img'])).convert('RGBA')
IM = {pid: load(pid) for pid in PJ}
def wet_fountain(im):   # owner 10-24 「분수 물」: the art room's dry, cracked basin -> still dark-teal water (shade kept from the picture); jets / ripples move in code (felt_live.js)
    a = np.asarray(im).astype(float); h, w = a.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]; L = (.3 * r + .59 * g + .11 * b) / 255
    pool = (((xx - 146) / 119.) ** 2 + ((yy - 250) / 46.) ** 2 < 1) & (al > 0)                       # basin (picture px), the pedestal cut out
    ped = (((xx - 148) / 54.) ** 2 + ((yy - 236) / 27.) ** 2 < 1) | ((yy < 236) & (np.abs(xx - 148) < 54))
    dark, light = np.array([22, 44, 54.]), np.array([96, 140, 150.]); t = np.clip((L - .12) / .45, 0, 1)[..., None]
    a[..., :3] = np.where((pool & ~ped)[..., None], dark * (1 - t) + light * t, a[..., :3]); return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
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
IM['fountain'] = wet_fountain(IM['fountain'])
for pid in IM:
    if PJ[pid].get('kind') == 'building' and pid not in ('linette', 'bl_house'): IM[pid] = ragged(IM[pid]); IM['west_a'] = wipe_sign(IM['west_a'])

# ---------- placement ----------
PJ['web_arch']['grok_foot'] = list(t2g(WALL + 7.1, 24.7))      # 아라크네 폐공방 입구: outside the east wall (was inside at tile 51.4, 24.7)
SC = json.load(open(os.path.join(SRC, 'scene_suggest.json')))['scene']   # the town-art room's entrance scene + district accents (Grok px)
SC = [['sign_post', 990, 818] if e[0] == 'sign_post' else e for e in SC]   # 이정표 비켜 세움 (남문 간판과 겹침, art room)
SEAM = [('dead_tree', 700, 975), ('dead_tree', 1040, 985), ('bush_b', 790, 960), ('bush_b', 935, 965), ('bush_b', 610, 1000), ('bush_b', 1150, 995),
        ('stone_low', 650, 925), ('stone_low', 1085, 930), ('bush_b', 480, 990), ('stone_low', 1250, 990)]   # 남문 바깥 이음매 (art room 30131c70): town ground runs 3 rows past the gate, dry scrub on it, field trees start below
_coc = iter([t2g(68.6, 26.95), t2g(68.4, 21.9)])                    # the cocoons follow the workshop out of town
EXTRA = [tuple(e) for e in SC] + SEAM + [  # + mine (Grok px): plaza lamps / bench, market, inn, herbs, web quarter, castle rubble
 ('tombs', 1450, 305), ('fence_iron', 1215, 335), ('fence_iron', 1300, 340), ('candelabra', 1000, 215), ('cocoons', 1500, 640),
 ('lamp', 600, 452), ('lamp', 785, 452), ('lamp', 600, 575), ('lamp', 790, 575), ('lamp', 175, 560),
 ('bench', 742, 585), ('crates', 575, 405), ('barrels', 395, 425), ('cart', 850, 430),
 ('barrels', 965, 478), ('herb_rack', 1175, 668), ('rubble', 1385, 725), ('rubble', 545, 255), ('rubble', 880, 262), ('crates', 1105, 850)]
EXTRA = [('cocoons', *next(_coc)) if e[0] == 'cocoons' and e[1] > 1300 else e for e in EXTRA]
OUTSIDE = [  # tile coords: burnt ruins between the side gate and the workshop (no bones / carcasses in the village area)
 ('burnt_pine_a', 60.6, 9.6), ('burnt_pine_b', 64.2, 8.6), ('dead_tree', 68.6, 10.6), ('burnt_pine_a', 70.2, 14.2), ('ruin_pillar', 61.6, 13.2), ('stone_low', 66.2, 15.6),
 ('boulder', 69.2, 18.8), ('ash_bush', 60.6, 18.4), ('stump', 63.6, 19.4), ('ember_rubble', 62.4, 21.4), ('thread_stake', 60.9, 22.9), ('thread_stake', 62.9, 26.9),
 ('rubble', 60.3, 27.6), ('d_web_sheet', 67.8, 24.2), ('ruin_pillar', 69.0, 23.6), ('dead_tree', 69.6, 28.4), ('burnt_pine_b', 66.8, 30.4), ('stone_low', 63.6, 29.8),
 ('boulder', 60.6, 30.6), ('burnt_pine_a', 60.6, 33.9), ('dead_tree', 64.0, 33.4), ('burnt_pine_b', 67.6, 34.7), ('burnt_pine_a', 70.4, 33.6),
 ('burnt_pine_b', 62.2, 5.9), ('burnt_pine_a', 67.0, 5.6), ('burnt_pine_b', 70.6, 6.6)]
EXTRA += [(pid, *t2g(x, y)) for pid, x, y in OUTSIDE]
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
    if pid in ('stall_n', 'red_stall'): sy0 -= 3  # stall roof blocks the path (1장 점검, kept from main)
    for y in range(max(0, sy0), min(H, sy1 + 1)):
        for x in range(max(0, sx0), min(W, sx1 + 1)): solid[y][x] = not (pid == 'south_gate' and abs((x + .5) * T - wx) < 24)
    if pid == 'string_lights':
        for x in (sx0, sx1): solid[int((wy - 1) // T)][x] = True
    big = kind == 'building' and pid != 'fountain'
    props.append({'id': pid + n, 'role': p.get('role', ''), 'img': f'assets/world/felt/{p["img"]}', 'x': wx / T, 'y': wy / T, 'ax': p['ax'], 'ay': p['ay'],
                  'solid': None if pid in ('south_gate', 'string_lights') else [sx0, sy0, sx1, sy1], 'fade': 1 if big or pid in ('watchtower', 'mausoleum', 'south_gate', 'string_lights', 'fountain') else 0, 'shadow': 0 if big else 1})
for pid, p in PJ.items():
    if 'grok_foot' in p: place(pid, *p['grok_foot'])
ss = PJ['shop_sign']; place('well', ss['grok_foot'][0] - 92 / D / S, ss['grok_foot'][1] + 4, '_shop')   # covers the villager baked into the store art
for i, (pid, gx, gy) in enumerate(EXTRA): place(pid, gx, gy, f'_{i}')
def palisade_ns():                                                   # a N-S run of the south gate's own pointed stakes (one tile = 2 stakes, the nearer one drawn last)
    sg = IM['south_gate']; al = np.asarray(sg)[..., 3]; cols_ = np.where(al[150:].max(0) > 0)[0]; x0 = cols_[0]
    stake = sg.crop((x0, 0, x0 + 18, sg.height)); stake = stake.crop(stake.getbbox()); stake = stake.crop((0, 0, stake.width, 66)).resize((24, 66), Image.NEAREST)   # the pointed top only, so a segment stays about a tile tall
    out = Image.new('RGBA', (32, 90), (0, 0, 0, 0))
    dk = np.asarray(stake).copy(); dk[..., :3] = (dk[..., :3] * .7).astype(np.uint8); out.alpha_composite(Image.fromarray(dk, 'RGBA'), (8, 0)); out.alpha_composite(stake, (1, 24)); return out
PAL_NS = palisade_ns(); IM['palisade_ns'] = PAL_NS; PJ['palisade_ns'] = {'img': 'palisade_ns.png'}
for y in range(6, H - 4):                                            # the town wall (palisade) on the old east border, 쪽문 = GATE_ROWS
    solid[y][WALL] = y not in GATE_ROWS
    if y not in GATE_ROWS + (ROPE_ROW,): props.append({'id': f'wall_e_{y}', 'role': 'wall', 'img': 'assets/world/felt/palisade_ns.png', 'x': WALL + .5, 'y': y + 1., 'ax': 16, 'ay': PAL_NS.height, 'solid': None, 'fade': 1, 'shadow': 0})
P = {q['id']: q for q in props}
# ---------- art slots (maps/src/felt_slots.json = the ONE table; illustrator art docs_art/felt_props, 1d91e38a) ----------
SLOTS = json.load(open(os.path.join(ROOT, 'maps', 'src', 'felt_slots.json')))['slots']
ART, SLOT_OUT = os.path.join(ROOT, '..', 'docs_art', 'felt_props'), os.path.join(ROOT, 'assets', 'world', 'felt_slots'); os.makedirs(SLOT_OUT, exist_ok=True)
for f in os.listdir(SLOT_OUT): os.remove(os.path.join(SLOT_OUT, f))
for sl in SLOTS:
    for f in (sl['file'] if isinstance(sl['file'], list) else [sl['file']]): Image.open(os.path.join(ART, f)).save(os.path.join(SLOT_OUT, f), optimize=True)
SIM = lambda f: Image.open(os.path.join(SLOT_OUT, f)).convert('RGBA')
DECALS = []                                                          # [img, foot x, foot y] centre-anchored, baked into ground.png after the palette snap
for sl in SLOTS:
    if sl.get('anchor') == 'center':
        if 'under' in sl or 'fill' in sl: continue                   # shadow strips: below, once the building feet are known; fill = ash floor tiles (code ground)
        DECALS.append([sl['file'], sl['x'], sl['y']])
        continue
    im = SIM(sl['file']); nf = sl.get('frames', 1); fw = im.width // nf
    if 'at' in sl: b = P[sl['at']]; x, y, ax, ay = b['x'], b['y'] + 1e-4, sl['ax'], sl['ay']
    else: x, y, ax, ay = sl['x'], sl['y'], sl.get('ax', fw / 2), sl.get('ay', im.height)
    if sl.get('mount'):                                              # hangs on a building wall / eaves: sort just after that building
        hosts = [q for q in props if PJ.get(q['id'], {}).get('kind') == 'building' and q['y'] > y and q['x'] - q['ax'] / D / T <= x <= q['x'] + (PJ[q['id']]['w'] - q['ax']) / D / T and q['y'] - q['ay'] / D / T <= y - .2]
        if hosts: ny = min(hosts, key=lambda q: q['y'])['y'] + .01; ay += (ny - y) * T * D; y = ny
    q = {'id': 'slot_' + sl['id'], 'role': 'slot', 'img': 'assets/world/felt_slots/' + sl['file'], 'x': x, 'y': y, 'ax': ax, 'ay': ay, 'solid': sl.get('solid'), 'fade': sl.get('fade', 0), 'shadow': 0}
    for k in ('frames', 'seq', 'show'):
        if k in sl: q[k] = sl[k]
    props.append(q)
    if sl.get('solid'):
        x0, y0, x1, y1 = sl['solid']
        for yy_ in range(y0, y1 + 1):
            for xx_ in range(x0, x1 + 1): solid[yy_][xx_] = True
SHADOWS = [P[pid] for sl in SLOTS if 'under' in sl for pid in sl['under'] if pid in P]
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
 ([(1040, 250), (1180, 280)], 30), ([(470, 235), (600, 228), (800, 240), (990, 230)], 34),
 ([(1430, 700), (1580, 690), (1700, 702), (1790, 716), (P['web_arch']['x'] * T / S, P['web_arch']['y'] * T / S + 10)], 34)]   # 쪽문 -> 폐공방: the short ruined path
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
img[road | rim] *= 1.17                                                    # owner 10-24: paths 15-20 % brighter (the roads read from the dirt)
# plaza: cobble ring (stone cells by jittered grid), mortar in between, inner basin ring stones
cell = 4.0; jx, jy = vnoise(4, 6) * 1.6, vnoise(4, 7) * 1.6
cx, cy = (wxp + jx) / cell, (wyp + (np.floor((wxp + jx) / cell) % 2) * cell / 2 + jy) / cell
fx, fy = cx - np.floor(cx), cy - np.floor(cy); mort = (fx < .16) | (fy < .2); shade = vnoise(cell, 8)
plaza = pr < 1 + (n2 - .5) * .12
stone = sel([shade < .35, shade < .6, shade < .82], [cols['s1'], cols['s2'], cols['s3']], cols['s4'])
img[plaza] = np.where(mort[plaza][:, None], cols['s0'], stone[plaza]); img[plaza & (pr > .9) & (pr < .97)] = cols['s0']; img[plaza] *= 1.12
# edges: darker toward the map border (no hard frame), backdrop band darker still
edge = np.minimum.reduce([wxp, wyp, W * T - wxp, H * T - wyp + 400])   # no dark band at the bottom: the ash field joins there; img *= np.clip(.55 + edge / 60, .55, 1)[..., None]
outside = (wxp > (WALL + .5) * T + (n1 - .5) * 10) & (wyp >= 175 * S)     # past the wall: the illustrator's seamless ash floor tiles (ash_ground_tile_a / b), the ruined path on top, darker
ashn = np.hypot((wxp - 53.2 * T) / (4.6 * T), (wyp - 10.2 * T) / (2.6 * T)) < 1 + (n1 - .5) * .5 + (n3 - .5) * .25   # 북쪽 잿더미 지구 (inside the wall)
AT = [np.asarray(Image.open(os.path.join(ROOT, '..', 'docs_art', 'felt_props', f)).convert('RGB')).astype(float) for f in ('ash_ground_tile_a.png', 'ash_ground_tile_b.png')]
tx_, ty_ = (xx // (T * GD)).astype(int), (yy // (T * GD)).astype(int); pick = (np.sin(tx_ * 12.9898 + ty_ * 78.233) * 43758.5453 % 1) < .5
tex = np.where(pick[..., None], AT[0][(yy % 48).astype(int), (xx % 48).astype(int)], AT[1][(yy % 48).astype(int), (xx % 48).astype(int)])
ash = (outside | ashn) & (dr >= 2 + (n3 - .5) * 3); img[ash] = tex[ash]; img[outside & (dr < 2)] *= .8
img[wyp < 175 * S] *= .84                                                  # backdrop band: gentler (owner 10-24, was .7)
# snap to the town palette (base24 + accents)
pal = np.array([hx(c) for c in (PAL['base24'] + PAL['accent8'] if PAL else [v for v in ('#201810',)])])
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - .47)[(yy % 4).astype(int), (xx % 4).astype(int)][..., None]   # ordered dither: fine 1-pixel grain instead of big blotches
img = img + BAYER * 12
flat = img.reshape(-1, 3); idx = np.empty(len(flat), int)
for i in range(0, len(flat), 1 << 18): idx[i:i + (1 << 18)] = np.argmin(((flat[i:i + (1 << 18), None, :] - pal[None]) ** 2).sum(2), 1)
gim = Image.fromarray(pal[idx].reshape(GH, GW, 3).astype(np.uint8)).convert('RGBA')
for f, x, y in DECALS:                                               # decals / ash floor tiles: centre anchor, ground layer, asset px = ground px (both D=3)
    d = SIM(f); gim.alpha_composite(d, (int(round(x * T * GD - d.width / 2)), int(round(y * T * GD - d.height / 2))))
sh = SIM('shadow_strip.png')
for q in SHADOWS:                                                    # dithered shadow band along each building's front (the foot line), tiled
    c0, c1 = bottom_span(IM[q['id']]); x0 = int(round(q['x'] * T * GD - q['ax'] + c0)); x1 = int(round(q['x'] * T * GD - q['ax'] + c1)); y0 = int(round(q['y'] * T * GD - 6))
    for x in range(x0, x1 - sh.width // 2, sh.width): gim.alpha_composite(sh.crop((0, 0, min(sh.width, x1 - x), sh.height)), (x, y0))
gim.convert('RGB').save(os.path.join(OUT, 'ground.png'), optimize=True)

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
    elif t == 'npc': o['x'], o['y'] = int(o['x'] * W0 / 56), int(o['y'] * H / 38)    # no near rule -> scaled spot (fixed below)
    objs.append(o)
NEAR = {'f_rom': ['f_door_smith', -1, 1], 'f_sera': ['f_door_herb', 0, 1], 'f_ben': ['f_mark_stall', 0, 1],
        'f_linette': ['f_door_atelier', -4, 1], 'f_luca': ['f_mark_fountain', 5, 1],  # Luca: at the ration tent's front (the canopy, walkable)
  # -4: the door's own tile is inside the building picture, she needs open ground to pace. 바르트·마르타·오스왈드는 집 안에만 있다
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
WEBS = []                                                                     # threads thicken from the fountain to the side gate, then on to the workshop
LEGS = [((P['fountain']['x'] + 3, P['fountain']['y'] - 1), (WALL - .5, GATE_ROWS[0] + .5), 10, 0, .55), ((WALL + 1.5, GATE_ROWS[0] + .5), (P['web_arch']['x'] - 2, P['web_arch']['y'] - 1.5), 4, .55, .8)]
for (ax0, ay0), (ax1, ay1), N, t0, t1 in LEGS:
    for i in range(N):
        u = i / (N - 1); t = t0 + (t1 - t0) * u; x = ax0 + (ax1 - ax0) * u; y = ay0 + (ay1 - ay0) * u; n = 1 + int(t * 3)
        for j in range(n): dx = (j - n / 2) * 1.1; WEBS.append([x + dx, y - 2 - (j % 2), x + dx + 1.2 + t, y - .2, .5 + t, .25 + .5 * t])
# ---------- live layer (felt_live.js, owner 10-24 펠트 업그레이드): code-drawn water, flicker, signs; nothing baked ----------
fo = P['fountain']
FOUNTAIN = {'x': fo['x'], 'y': fo['y'], 'ax': fo['ax'], 'ay': fo['ay'], 'D': D, 'pool': [146, 250, 119, 46], 'ped': [148, 236, 54, 27],   # picture px (fountain.png)
            'jets': [[88, 200, 255], [98, 208, 263], [147, 213, 277], [190, 207, 267], [202, 200, 250]]}                             # [x, top, bottom] of each falling stream
FLICK = [lp(next(q['id'] for q in props if q['id'].startswith('brazier')), 0, -.6, 34, '#ff9a40', 1), lp('se_house', -1, -2, 30, '#ff8a3a', 1)]   # 5-8 live flames (brazier, forge, plaza lamps, chapel candles)
FLICK += [[q['x'], q['y'] - 1.4, 16, '#ffc070', .8] for q in props if q['id'].startswith('lamp_') and 20 <= q['x'] <= 28]
FLICK += [[q['x'], q['y'] - 2.2, 14, '#ffd090', .8] for q in props if q['id'].startswith('candelabra')]
def door(i): return next(o for o in objs if o.get('id') == i)
SIGNS = [[door(i)['x'] + dx, door(i)['y'] + dy, icon] for i, dx, dy, icon in (                                                  # code planks only where no illustrator sign exists yet
    ('f_door_inn', 1.8, -1.2, 'mug'), ('f_door_smith', 1.8, -1.0, 'anvil'), ('f_door_atelier', 2.2, -1.0, 'needle'))]           # weapon / tool / herb / south gate = art (felt_slots.json)
objs.append({'type': 'sign', 'id': 'f_sign_gate_night', 'x': 27, 'y': 28, 'text': '「해 지면 문 닫음」\n— 펠트 경비대', 'live': 1})        # under sign_gate_sunset.png
objs.append({'type': 'sign', 'id': 'f_sign_side_gate', 'x': WALL - 1, 'y': ROPE_ROW, 'text': '「출입 금지」\n— 가스', 'live': 1})       # 동쪽 쪽문, beside the rope
LIVE = {'fountain': dict(FOUNTAIN, art=1), 'flick': FLICK, 'signs': SIGNS}                                                      # art = fountain_water_strip.png draws the water (code ripples off, sound kept)
def nearest_floor(x, y, avoid=()):
    best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            X, Y = x + dx, y + dy
            if (X, Y) in avoid: continue
            if 1 <= X < W - 1 and 1 <= Y < H - 1 and not solid[Y][X]:
                rank = abs(dx) + abs(dy) + (0 if dy >= 0 else 2)
                if best is None or rank < best[0]: best = (rank, X, Y)
    return [best[1], best[2]] if best else [x, y]
npc_tiles = set()
for o in objs:
    if o.get('type') == 'npc':
        for dy in range(-1, 2):
            for dx in range(-1, 2): npc_tiles.add((int(o['x']) + dx, int(o['y']) + dy))
def props_named(prefix):
    return [q for q in props if q['id'] == prefix or q['id'].startswith(prefix + '_')]
SPOT = {}
if props_named('cart'): SPOT['f_hid_cart'] = nearest_floor(int(props_named('cart')[0]['x']), int(props_named('cart')[0]['y']) + 1, npc_tiles)
if props_named('tombs'):
    gq = max(props_named('tombs'), key=lambda q: q['x']); SPOT['f_hid_grave'] = nearest_floor(int(gq['x']) - 1, int(gq['y']) + 1, npc_tiles)
if props_named('crates'):
    cq = min(props_named('crates'), key=lambda q: q['x']); SPOT['f_chest_plaza'] = nearest_floor(int(cq['x']) + 1, int(cq['y']) + 1, npc_tiles)
for o in objs:
    if o.get('id') in SPOT: o['x'], o['y'] = SPOT[o['id']]
SPAWNS = {'default': [EX[0] + .5, EX[1] - 7.5, 'up'], 'world': [EX[0] + .5, EX[1] - 7.5, 'up'], 'field': [EX[0] + .5, EX[1] - 1.5, 'up'], 'arachne': [foot('web_arch')[0] + .5, foot('web_arch')[1] + 1.6, 'down']}
for o in objs:
    if o.get('type') == 'door' and o.get('out'): SPAWNS[o['out']] = [o['x'] + .5, o['y'] + 1.5, 'up']  # step back out on the tile in front of that door
props.sort(key=lambda q: q['y'])                                     # painter's order by foot (stable); slots / wall pieces join the town's own pictures
m = {k: F[k] for k in ('type', 'area', 'region', 'title', 'bgm', 'battleBgm', 'tileset', 'tile') if k in F}
m.update(id='felt', name='펠트', viewZoom=1.3, w=W, h=H,   # viewZoom: owner 10-24 「카메라 1.3배」
         legend={'.': 'dirt', '#': 'cliff'}, solid=['#'], ground=[''.join(r) for r in rows], objects=objs,
         spawns=SPAWNS,   # start inside the south gate (forge, chief's house, statue ahead); out-spawns = walk back out of an interior
         hd={'D': GD, 'ground': 'assets/world/felt/ground.png', 'props': [dict(q, D=D) for q in props], 'lights': LIGHTS, 'webs': WEBS, 'smoke': SMOKE, 'grade': 'dusk', 'live': LIVE},
         note='GENERATED by tools/hd/build_felt.py from the town-art room parts + maps/src/felt.json (doors / NPCs / clues) - do not hand-edit')
json.dump(m, open(os.path.join(ROOT, 'maps', 'felt.json'), 'w'), ensure_ascii=False, indent=1)
FF = json.load(open(os.path.join(ROOT, 'maps', 'field_felt.json')))
top = [x for x, c in enumerate(FF['ground'][0]) if c in ".'=,"]; fxo = EX[0] - (top[0] + top[-1]) // 2
# east filler (owner 10-24 펠트 업그레이드 2단계): felt is wider than the field now -> a strip of the field's own forest under felt's outside-the-wall columns (no void)
EX0, EW = fxo + FF['w'], W - (fxo + FF['w']); rf = random.Random(5)
FG = Image.open(os.path.join(ROOT, FF['hd']['ground'])); fgD = FF['hd']['D']; cw = EW * T * fgD
eg = Image.new('RGB', (cw, FF['h'] * T * fgD))
for x in range(0, cw, 4 * T * fgD): eg.paste(FG.crop((FG.width - 4 * T * fgD, 0, FG.width, FG.height)), (x, 0))
os.makedirs(os.path.join(ROOT, 'assets', 'world', 'felt_east'), exist_ok=True); eg.save(os.path.join(ROOT, 'assets', 'world', 'felt_east', 'ground.png'), optimize=True)
json.dump({'id': 'felt_east', 'type': 'field', 'name': FF.get('name'), 'title': FF.get('title'), 'bgm': FF.get('bgm'), 'battleBgm': FF.get('battleBgm'), 'tileset': FF.get('tileset'), 'tile': FF.get('tile'),
           'w': EW, 'h': FF['h'], 'legend': {k: FF['legend'][k] for k in ('T', 'P', '#')}, 'solid': FF.get('solid', []), 'grade': FF.get('grade'), 'objects': [], 'spawns': {},
           'ground': [''.join(rf.choice('TTTP') for _ in range(EW)) for _ in range(FF['h'])],
           'hd': {'D': fgD, 'ground': 'assets/world/felt_east/ground.png', 'decoArt': FF['hd']['decoArt'], 'props': [], 'grade': FF['hd'].get('grade')},
           'note': 'GENERATED by tools/hd/build_felt.py: forest filler east of field_felt, under felt\'s outside-the-wall strip (ch1 only)'}, open(os.path.join(ROOT, 'maps', 'felt_east.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({'id': 'ch1', 'note': '1장 = 펠트 + 잿빛 들판 이어 붙인 지도 (세미 오픈월드). GENERATED by tools/hd/build_felt.py (field_felt sits under the south gate, felt_east = forest filler east of it); field_felt.json is edited as it is',
           'compose': [{'map': 'felt', 'x': 0, 'y': 0}, {'map': 'field_felt', 'x': fxo, 'y': H}] + ([{'map': 'felt_east', 'x': EX0, 'y': H}] if EW > 0 else []), 'region': 'ch1', 'area': 1}, open(os.path.join(ROOT, 'maps', 'ch1.json'), 'w'), ensure_ascii=False, indent=1)
print('ok felt', W, 'x', H, len(props), 'props', len(objs), 'objects; field_felt at x', fxo)
print('\n'.join(rows[y] if isinstance(rows[y], str) else ''.join(rows[y]) for y in range(H)))
