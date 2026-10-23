"""잿빛 들판 (field_felt) hd ground = the felt_v4 way (code ground, D=2), so the field matches the town's pixel size and palette.
Split with the town-art room (10-23): they paint the deco parts (trees, pines, rocks, ...) at D=3; this script paints the ground and adds the
hd block to maps/field_felt.json (the map stays the other rooms' data: tiles, mobs, objects are untouched, only "hd" is (re)written).
- tile classes from the legend: grass / tall grass / dirt road / water / bridge / stones / cliff / sand; edges domain-warped so they are organic
- colours = the town palette (palette.json) passed through the game's 'ash' grade, then snapped to it (one 32-colour ash set)
- the top rows ease from the town's warm earth to ash, so the south-gate seam is a fade, not a line
- scorch marks baked into the ground; threads between trees = hd webs (code, they sway); water ripples = hd water tiles (code)
python3 tools/hd/build_field_felt_hd.py [palette.json]"""
import os, sys, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
OUT = os.path.join(ROOT, 'assets', 'world', 'field_felt_hd'); os.makedirs(OUT, exist_ok=True)
MP = os.path.join(ROOT, 'maps', 'field_felt.json'); M = json.load(open(MP))
PALF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'handoff', 'claude', 'felt_grok_layout', 'palette.json')
PARTS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, '..', 'handoff', 'claude', 'felt_grok_build', 'final')
# tile deco -> the art room's D=3 parts (parts.json "field_legend": legend char -> part ids); tiles keep their rules, only the picture changes
# (world.js buildMap / drawPropsHi). Not decos: b (bridge planks under the hero), " (reeds on half the tall-grass tiles), clue:<id> (a prop on it)
PAL = json.load(open(PALF)); hx = lambda s: np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], float)
W, H, T, GD = M['w'], M['h'], M['tile'], 3                       # ground D = the parts' D (one pixel size)
GW, GH = W * T * GD, H * T * GD
yy, xx = np.mgrid[0:GH, 0:GW].astype(float); wxp, wyp = xx / GD, yy / GD
def vnoise(scale, seed):
    r = np.random.default_rng(seed); gw, gh = int(W * T / scale) + 3, int(H * T / scale) + 3; g = r.random((gh, gw))
    fx, fy = wxp / scale, wyp / scale; ix, iy = fx.astype(int), fy.astype(int); tx, ty = fx - ix, fy - iy; tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b, c, d = g[iy, ix], g[iy, ix + 1], g[iy + 1, ix], g[iy + 1, ix + 1]; return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty
def ash(c, k=.9):                                  # = world.js GRADE.ash
    r, g, b = c[..., 0], c[..., 1], c[..., 2]; L = (r * .3 + g * .59 + b * .11) * .82; t = np.stack([L * .9 + 12, L * .84 + 9, L * .88 + 14], -1)
    k = np.asarray(k)[..., None] if np.ndim(k) else k; return c + (t - c) * k
# ---- tile classes (legend ground; deco cells stand on their ground) ----
CL = {'grass': 0, 'grass_tuft': 0, 'grass_flowers': 0, 'tallgrass': 1, 'dirt': 2, 'water': 3, 'bridge_h': 4, 'stones': 5, 'cliff': 6, 'sand': 7}
def cls(ch):
    L = M['legend'].get(ch, 'grass'); g = L if isinstance(L, str) else L.get('ground', 'grass'); return CL.get(g, 0)
grid = np.array([[cls(c) for c in row] for row in M['ground']])
n1, n2, n3 = vnoise(18, 1), vnoise(6, 2), vnoise(2.5, 3)
wx_, wy_ = wxp + (vnoise(9, 11) - .5) * 9, wyp + (vnoise(9, 12) - .5) * 9   # domain warp -> ragged class edges
gx, gy = np.clip((wx_ // T).astype(int), 0, W - 1), np.clip((wy_ // T).astype(int), 0, H - 1)
C = grid[gy, gx]; C[grid[np.clip((wyp // T).astype(int), 0, H - 1), np.clip((wxp // T).astype(int), 0, W - 1)] == 4] = 4   # the bridge keeps square ends
cols = {k: hx(v) for k, v in dict(d1='#2e2318', d2='#38291b', d3='#42301f', d4='#4f3721', r0='#5b4127', r1='#6b4b2c', r2='#76583a', r3='#876442', r4='#9d744c',
        r5='#ac8863', s0='#312b26', s1='#4b4138', s2='#5d4c3c', s3='#675d53', s4='#877360', g1='#4d5a2c', g2='#3e362e', w0='#2f4a52', w1='#3a4f6b', w2='#4f7f86', sa='#c0a98d').items()}
def sel(conds, cs, other): return np.select([c[..., None] for c in conds], cs, other)
img = np.zeros((GH, GW, 3))
# grass: mottled dead grass, short blades (vertical 2-px strokes)
gv = n1 * .55 + n2 * .3 + n3 * .15
t = np.clip((gv - .3) / .4, 0, 1)[..., None]; img[:] = cols['g2'] * (1 - t) + (cols['g1'] * .7 + cols['d3'] * .3) * t   # soft mottling (low contrast, continuous)
bv = vnoise(1.1, 4); blade = (bv > .8) & (np.roll(bv, 1, 0) <= .8) & (n1 > .4); img[blade] = img[blade] * 1.18   # sparse short blades
# tall grass: denser, lighter, longer blades
tg = C == 1; sway = np.floor((xx + np.floor(vnoise(4, 5) * 3)) / 2) % 3 == 0          # tall grass: thin vertical stalks in clumps, lit tips
tb = sway & (vnoise(2.2, 15) > .42) & tg; img[tg] = cols['d3'] * .6 + cols['g1'] * .4; img[tb] = cols['g1']; img[tb & ~np.roll(tb, 2, 0)] = cols['r3'] * .7 + cols['g1'] * .3
# dirt road
rd = C == 2; rv = n2 * .7 + n3 * .3; t = np.clip((rv[rd] - .25) / .55, 0, 1)[:, None]; img[rd] = cols['r2'] * (1 - t) + cols['r3'] * t   # soft packed dirt
img[rd & (vnoise(1.2, 6) > .82)] = cols['r5']
# sand: pale, fine speckle
sd = C == 7; img[sd] = sel([n3[sd] < .5], [cols['sa'] * .85], cols['sa']); img[sd & (vnoise(1, 7) > .85)] = cols['r4']
# stones: cobbles
st = C == 5; cell = 3.5; jx = vnoise(3, 8) * 1.4; cx = (wxp + jx) / cell; cy = (wyp + (np.floor(cx) % 2) * cell / 2) / cell
fx, fy = cx - np.floor(cx), cy - np.floor(cy); mort = (fx < .18) | (fy < .22); sh = vnoise(cell, 9)
stone = sel([sh < .4, sh < .7], [cols['s1'], cols['s2']], cols['s3']); img[st] = np.where(mort[st][:, None], cols['s0'], stone[st])
# cliff: dark rock, lighter top lip, cracks
cf = C == 6; img[cf] = sel([n2[cf] < .5], [cols['s0']], cols['s1']); up = np.roll(C, 3, 0) != 6; img[cf & up] = cols['s3']; img[cf & (vnoise(1.4, 10) > .86)] = cols['d1']
# water: dark blue-grey, darker banks, a few still highlights (ripples move in code)
wt = (C == 3) | (C == 4); near = np.zeros_like(wt)
for d in (2, 3): near |= ~np.roll(wt, d, 0) | ~np.roll(wt, -d, 0) | ~np.roll(wt, d, 1) | ~np.roll(wt, -d, 1)
img[wt] = sel([n1[wt] < .5], [cols['w0']], cols['w1'] * .8 + cols['w0'] * .2); img[wt & near] = cols['w0'] * .6; img[wt & ~near & (vnoise(1.6, 13) > .86)] = cols['w2']
bank = ~wt & (np.roll(wt, -2, 0) | np.roll(wt, 2, 1) | np.roll(wt, -2, 1)); img[bank] = cols['d1']
# bridge (horizontal planks over the water)
br = C == 4; pl = ((wxp // 3) % 2 == 0); img[br] = np.where(pl[br][:, None], cols['r1'], cols['r2']); img[br & ((wxp % 3) < .6)] = cols['d1']
img[br & ((wyp % T) < 1.5)] = cols['d1']
# scorch marks (burned king's road outskirts), dithered
rng = np.random.default_rng(21)
for _ in range(40):
    sx, sy = rng.random() * W * T, rng.random() * H * T; tx, ty = int(sx // T), int(sy // T)
    if grid[ty, tx] in (3, 4, 6): continue
    rx = 8 + rng.random() * 20; q = ((wxp - sx) / rx) ** 2 + ((wyp - sy) / (rx * .45)) ** 2
    img[(q < .35)] = cols['d1'] * .7; img[(q >= .35) & (q < 1) & (((xx + yy) % 2) == 0)] = cols['d1']
# ash grade: town warm at the top rows (south-gate seam) -> full ash by row 5
k = np.clip((wyp - 8) / (5 * T), .15, .9); img = ash(img, k)
edge = np.minimum(wxp, W * T - wxp); img *= np.clip(.7 + edge / 80, .7, 1)[..., None]
pal = np.array([hx(c) for c in PAL['base24'] + PAL['accent8']]); pal = np.concatenate([pal, ash(pal)])   # town colours + their ash twins
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - .47)[(yy % 4).astype(int), (xx % 4).astype(int)][..., None]   # ordered dither: fine 1-pixel grain instead of big blotches
img = img + BAYER * 14
flat = img.reshape(-1, 3); out = np.empty(len(flat), int)
for i in range(0, len(flat), 1 << 18): out[i:i + (1 << 18)] = np.argmin(((flat[i:i + (1 << 18), None, :] - pal[None]) ** 2).sum(2), 1)
Image.fromarray(pal[out].reshape(GH, GW, 3).clip(0, 255).astype(np.uint8)).save(os.path.join(OUT, 'ground.png'), optimize=True)
# ---- code layers: water tiles (ripples), threads between nearby trees (sway) ----
WATER = []                                          # runs [y, x0, x1] of water tiles
for y in range(H):
    for x in range(W):
        if grid[y, x] == 3 and (x == 0 or grid[y, x - 1] != 3): x1 = x
        if grid[y, x] == 3 and (x == W - 1 or grid[y, x + 1] != 3): WATER.append([y, x1, x])
trees = [(x, y) for y in range(H) for x in range(W) if M['ground'][y][x] in 'TP' and 2 < y < H - 3]
rng = np.random.default_rng(5); WEBS = []
for _ in range(22):
    a = trees[rng.integers(len(trees))]; b = min((t for t in trees if t != a and 2 <= abs(t[0] - a[0]) <= 5 and abs(t[1] - a[1]) <= 2), key=lambda t: rng.random(), default=None)
    if b: WEBS.append([a[0] + .5, a[1] - .4, b[0] + .5, b[1] - .3, .8 + rng.random() * .6, .35 + rng.random() * .25])
import shutil
PJA = json.load(open(os.path.join(PARTS, 'parts.json'))); PJ = PJA['parts']; ART, PROPS = {}, []
def part(i):                                                    # copy one part (town parts reused out here get the field's ash)
    p = dict(PJ[i]); im = Image.open(os.path.join(PARTS, p['img'])).convert('RGBA')
    if not p.get('zone', '').startswith('field'):
        a = np.asarray(im).astype(float); a[..., :3] = ash(a[..., :3], .55); im = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    im.save(os.path.join(OUT, p['img'])); return {'img': f'assets/world/field_felt_hd/{p["img"]}', 'ax': p['ax'], 'ay': p['ay'], **({'flip': False} if p.get('flip') is False else {})}
h = lambda x, y, n=0: (np.sin(x * 127.1 + y * 311.7 + n * 74.7) * 43758.5453) % 1
for ch, ids in PJA.get('field_legend', {}).items():
    ids = [i for i in ids if i in PJ]
    if not ids: continue
    if ch == 'b':                                                  # bridge: one picture over the whole block of bridge tiles, flat under the hero
        v = part(ids[0]); bt = [(x, y) for y in range(H) for x in range(W) if M['ground'][y][x] == 'b']
        if bt: PROPS.append(dict(v, id='bridge', x=(min(x for x, _ in bt) + max(x for x, _ in bt) + 1) / 2, y=max(y for _, y in bt) + 1, under=1))
    elif ch == '"':                                                # reeds: half the tall-grass tiles (art room: all of them is too thick)
        vs = [part(i) for i in ids]
        for y in range(H):
            for x in range(W):
                if M['ground'][y][x] == '"' and h(x, y) < .5:
                    v = vs[int(h(x, y, 1) * len(vs))]; PROPS.append(dict(v, id=f'reed_{x}_{y}', x=float(x + .5 + (h(x, y, 2) - .5) * .4), y=float(y + 1 - h(x, y, 3) * .3), flip=bool(v.get('flip', True) and h(x, y, 4) < .5), shadow=0))
    elif ch.startswith('clue:'):                                   # a picture on a clue spot (굳은 사슴 사체)
        o = next((o for o in M['objects'] if o.get('id') == ch[5:]), None)
        if o: PROPS.append(dict(part(ids[0]), id=ch[5:], x=o['x'] + .5, y=o['y'] + .9, shadow=1))
    else: ART[ch] = [part(i) for i in ids]
M['hd'] = {'D': GD, 'decoArt': ART, 'ground': 'assets/world/field_felt_hd/ground.png', 'props': PROPS, 'water': WATER, 'webs': WEBS, 'grade': None}
txt = json.dumps(M, ensure_ascii=False, indent=1) + '\n'; open(MP, 'w').write(txt)   # serialise first: a failure never truncates the map
print('ok field_felt hd ground', GW, 'x', GH, len(WATER), 'water runs', len(WEBS), 'threads')
