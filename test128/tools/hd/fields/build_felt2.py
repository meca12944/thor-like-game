"""Felt town rebuild (option A): standalone map (no ch1 compose), Dragon-Quest-scale wide layout, huge 3-part castle on the
north edge behind a moat, natural forest edges (no fence ring), Wang ground (p_felt/w_felt), every door with an interior.
Usage: python3 build_felt2.py   -> maps/felt.json, maps/felt_int_{weapon,tool,herb,forge}.json, assets/world/felt/castle_*.png"""
import json, os, sys, math, random, copy
import numpy as np
from PIL import Image, ImageEnhance
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wang, props
from build import crom, disk, bfs, SETS
ROOT = props.ROOT; HERE = os.path.dirname(os.path.abspath(__file__))
FA = 'assets/world/felt/'; FF = 'assets/world/field_felt_hd/'
W, H = 80, 62; T = 16; SEED = 5
PARTS = json.load(open(os.path.join(ROOT, '..', 'handoff/claude/felt_grok_build/final/parts.json')))['parts'] if os.path.exists(os.path.join(ROOT, '..', 'handoff/claude/felt_grok_build/final/parts.json')) else None
ORIG = json.load(open(os.path.join(HERE, 'orig', 'felt.json')))
def P(name):  # art + anchor
    q = PARTS[name]; return {'img': FA + q['img'], 'ax': q['ax'], 'ay': q['ay'], 'w': q['w'], 'h': q['h']}
def norm(a, m, target=64.0):  # one brightness / warmth for the three castle parts
    rgb = a[..., :3].astype(float); l = (rgb[m] * [.3, .59, .11]).sum(-1).mean()
    g = rgb * (target / l); lum = (g * [.3, .59, .11]).sum(-1, keepdims=True); g = lum + (g - lum) * .85
    a = a.copy(); a[..., :3] = np.clip(g * [1.04, 1.0, .93], 0, 255); return a
def castle_assets():
    out = {}
    for n in ('castle_l', 'castle_r'):
        a = np.array(Image.open(os.path.join(ROOT, FA + n + '.png')).convert('RGBA')).astype(int)
        lum = a[..., :3].mean(-1); pale = (lum > 150) & (a[..., 3] > 0); tr = a[..., 3] == 0
        lab, _ = ndimage.label(pale | tr); keep = set(np.unique(lab[tr])) - {0}
        sky = np.isin(lab, list(keep)) & pale; sky[int(a.shape[0] * .6):] = False; a[sky, 3] = 0
        m = a[..., 3] > 0; a = norm(a, m)
        Image.fromarray(a.astype(np.uint8)).save(os.path.join(ROOT, FA + n + '_cut.png'), optimize=True)
        out[n] = {'img': FA + n + '_cut.png', 'ax': 171, 'ay': 285, 'w': 342, 'h': 286}
    src = '/tmp/plwork/out/gi/castle_keep_0.png'; dst = os.path.join(ROOT, FA + 'castle_keep.png')
    if os.path.exists(src):
        im = Image.open(src).convert('RGBA'); im = im.crop(im.getbbox()); a = np.array(im)
        a[..., 3] = np.where(a[..., 3] < 40, 0, 255); a = props._grade(a, .85, (1.03, 1.0, .95), .95); a = norm(a.astype(int), a[..., 3] > 0)
        Image.fromarray(a.astype(np.uint8)).save(dst, optimize=True)
    im = Image.open(dst); ax, ay = props.anchor(im)
    out['castle_keep'] = {'img': FA + 'castle_keep.png', 'ax': ax, 'ay': ay, 'w': im.width, 'h': im.height}
    return out
# building: key, art, center x, foot y, D, door (art cx, bottom, w, h) or None, door object
BUILD = [
 ('atelier', 'linette', 14, 27, 3, (238, 265, 46, 70)),
 ('tool', 'bl_house', 27, 28, 3, (106, 218, 40, 75)),
 ('weapon', 'west_b', 26, 46, 3, (92, 388, 40, 72)),
 ('chief', 's_house', 13, 47, 3, (136, 300, 54, 100)),
 ('forge', 'se_house', 14, 58, 3, (60, 300, 44, 82)),
 ('inn', 'inn', 56, 30, 3, (176, 343, 48, 80)),
 ('herb', 'e_row', 68, 37, 3, (110, 300, 44, 75)),
 ('chapel', 'chapel', 70, 24, 1.5, (62, 200, 40, 55)),
 ('empty', 'sw_house', 29, 57, 3, (175, 345, 44, 90)),
 ('arachne', 'web_arch', 71, 52, 3, None),
 ('guard', 'watchtower', 47, 57, 1.5, None),
 ('stall', 'red_stall', 52, 45, 3, None),
 ('stall2', 'stall_n', 60, 46, 3, None),
 ('fountain', 'fountain', 40, 33, 3, None),
]
DOORS = {  # door object per building (ids / links kept from the old map)
 'atelier': dict(id='f_door_atelier', name='리네트의 공방', to='felt_int_atelier', out='atelier_out'),
 'tool': dict(id='f_door_tool', name='잡화점', to='felt_int_tool', out='tool_out'),
 'weapon': dict(id='f_door_weapon', name='중고 무기점', to='felt_int_weapon', out='weapon_out'),
 'chief': dict(id='f_door_chief', name='이장 바르트의 집', to='felt_int_chief', out='chief_out'),
 'forge': dict(id='f_door_smith', name='롬의 대장간', to='felt_int_forge', out='forge_out'),
 'inn': dict(id='f_door_inn', name='마르타의 여관', to='felt_int_inn', out='inn_out'),
 'herb': dict(id='f_door_herb', name='세라의 약초 오두막', to='felt_int_herb', out='herb_out'),
 'chapel': dict(id='f_door_chapel', name='낡은 예배당', to='felt_int_chapel', out='chapel_out'),
 'empty': dict(id='f_door_empty', name='빈집', text='판자로 막힌 빈집이다. 문틈으로 탄내가 새어 나온다.\n…안에는 아무도 없다.'),
}
def main():
    rnd = random.Random(SEED); cas = castle_assets()
    yy, xx = np.mgrid[0:H, 0:W]
    de = np.minimum(np.minimum(xx, W - 1 - xx), H - 1 - yy).astype(float)
    band = 1.8 + 3.0 * wang.vnoise(H, W, 6, SEED)
    S = de < band                         # forest border (sides + south)
    C = np.zeros((H, W), bool)            # castle mass (north)
    water = np.zeros((H, W), bool); road = np.zeros((H, W), bool); clear = np.zeros((H, W), bool); Hs = np.zeros((H, W), bool)
    # castle: three parts on the north edge, keep in front (D=1.5 = exact 2x)
    castle = [('castle_l', 27, 13), ('castle_r', 53, 13), ('castle_keep', 40, 15)]
    props_ = []
    for n, x, y in castle:
        v = cas[n]; wc = v['w'] / 1.5 / T
        C[:y, int(x - wc * .5 + .5):int(x + wc * .5 - .5)] = True
        props_.append({'id': n, 'img': v['img'], 'x': x, 'y': y, 'ax': v['ax'], 'ay': v['ay'], 'D': 1.5, 'fade': 0, 'shadow': 0})
    C[:13, 18:63] = True; C[13:15, 32:48] = True
    # sides of the castle: forest
    S |= (yy < 20) & ((xx < 19 + 3 * wang.vnoise(H, W, 4, SEED + 2)) | (xx > 61 - 3 * wang.vnoise(H, W, 4, SEED + 3)))
    # moat in front of the castle, earth causeway in the middle
    for x in range(12, 69):
        yc = 17.2 + .9 * math.sin(x / 6.0) + .6 * (wang.vnoise(4, W, 5, SEED + 4)[1, x] - .5)
        hw = 1.15 if abs(x - 40) > 8 else .9
        for y in range(14, 21):
            if abs(y + .5 - yc) <= hw and not (37 <= x <= 43): water[y, x] = True
    # roads (Catmull-Rom), plaza ring
    def lay(pts, r=1.25, c=2.2):
        for p in crom(pts):
            if 0 <= p[0] < W and 0 <= p[1] < H: disk(road, p[0], p[1], r); disk(clear, p[0], p[1], c)
    lay([(40.5, 63), (40.5, 56), (40, 47), (40.5, 39), (40.5, 36)], 1.4)
    lay([(40.5, 27), (40.3, 22), (40.5, 17.5), (40.5, 16)], 1.3)
    lay([(3, 36.5), (12, 35.8), (22, 36.6), (31, 36), (36, 36.2)])
    lay([(45, 36.2), (52, 37), (60, 36.4), (68, 38.5), (77, 38)])
    disk(road, 40.5, 31.5, 6.6); disk(clear, 40.5, 31.5, 8)
    # buildings
    doors = []; spawns = {}
    for key, art, x, y, Dq, dr in BUILD:
        v = P(art); wc = v['w'] / Dq / T; dep = {'fountain': 3, 'guard': 2, 'stall2': 2, 'arachne': 3}.get(key, 4 if v['w'] > 300 else 3)
        x0 = int(round(x - wc * .44)); x1 = int(round(x + wc * .44))
        Hs[y - dep:y, x0:x1] = True
        q = {'id': art, 'img': v['img'], 'x': x, 'y': y, 'ax': v['ax'], 'ay': v['ay'], 'D': Dq, 'fade': 1, 'shadow': 0}
        if dr:
            cx, by, dw, dh = dr; dx = int(math.floor(x + (cx - v['ax']) / Dq / T)); dy = y - 1
            d = DOORS[key]; doors.append((key, dx, dy, d))
            im = np.array(Image.open(os.path.join(ROOT, v['img'])).convert('RGB')).astype(float)
            reg = im[int(by - dh * .9):int(by - dh * .1), int(cx - dw * .3):int(cx + dw * .3)].reshape(-1, 3)
            col = [int(c) for c in np.median(reg, 0)]
            q['door'] = {'id': d['id'], 'cx': cx, 'by': by, 'w': dw, 'h': dh, 'col': col}
            lay([(dx + .5, y + .4), (dx + .5, y + 1.6)], .8, 1.6)
        props_.append(q)
    # short paths from the doors to the nearest road (L-shaped, curved)
    rmask = road.copy()
    for key, dx, dy, d in doors:
        d2 = ndimage.distance_transform_edt(~rmask, return_indices=True)[1]
        ty_, tx_ = d2[0][dy + 2, dx], d2[1][dy + 2, dx]
        lay([(dx + .5, dy + 1.5), (dx + .5, (dy + 1.5 + ty_ + .5) / 2), ((dx + tx_) / 2 + .5, ty_ + .5), (tx_ + .5, ty_ + .5)], .85, 1.6)
    # arachne approach + guard post path
    lay([(68, 38.5), (70.5, 45), (71, 53)], 1.0); lay([(42, 52), (46, 58.6)], .9)
    S &= ~clear; S &= ~water; C &= ~water
    # small props
    small = []
    def sp(art, x, y, solid=True, D=3, flip=False, **kw):
        v = P(art); q = dict({'id': art + f'_{len(small)}', 'img': v['img'], 'x': x, 'y': y, 'ax': v['ax'], 'ay': v['ay'], 'D': D, 'fade': 0, 'shadow': 1, 'flip': flip}, **kw)
        small.append(q)
        if solid: Hs[int(y - .6), int(x)] = True
        return q
    for x, y, k in ((19.2, 13.6, 'ash_tree_a'), (17.6, 11.2, 'burnt_pine_b'), (20.6, 9.0, 'dead_tree'), (60.8, 13.6, 'ash_tree_b'), (62.4, 11.0, 'burnt_pine_a'), (59.8, 8.6, 'dead_tree'),
                    (33.6, 13.9, 'burnt_pine_a'), (46.6, 13.8, 'burnt_pine_b')):
        o = props.OLD[k]; small.append({'id': k + f'_c{len(small)}', 'img': o[0], 'x': x, 'y': y, 'ax': o[1], 'ay': o[2], 'D': 3, 'fade': 0, 'shadow': 1, 'sway': 1})
    for x, y in ((34.2, 24.4), (46.8, 24.4)):
        o = props.OLD['ruin_pillar']; small.append({'id': f'pillar_{x}', 'img': o[0], 'x': x, 'y': y, 'ax': o[1], 'ay': o[2], 'D': 3, 'fade': 0, 'shadow': 1}); Hs[int(y - .6), int(x)] = True
    for x, y in ((74.6, 47.2), (66.6, 47.6), (75.4, 53.4)):
        o = props.OLD['thread_stake']; small.append({'id': f'stake_{x}', 'img': o[0], 'x': x, 'y': y, 'ax': o[1], 'ay': o[2], 'D': 3, 'fade': 0, 'shadow': 1}); Hs[int(y - .6), int(x)] = True
    sp('ember_rubble', 40.5, 16.3); Hs[15, 36:45] = True; sp('rubble', 36.6, 15.8, False); sp('rubble', 44.3, 16.0, False, flip=True)
    for x, y in ((37.2, 21.2), (43.8, 21.2), (34.4, 29.4), (46.6, 29.4), (35.2, 35.4), (45.8, 35.4)): sp('brazier', x, y)
    for x, y in ((40 - 3.1, 44.5), (40 + 3.1, 44.5), (40 - 3, 52.5), (40 + 3.2, 52.5), (21, 37.6), (31, 34.6), (50, 34.7), (61, 39.3), (16.4, 30.3), (57.6, 33.3), (66.5, 26.8), (29.4, 49.6), (16.4, 49.8)): sp('lamp', x, y)
    sp('well', 33.5, 42); sp('bench', 36.2, 26.6, flip=False); sp('bench', 45.0, 26.6, flip=True)
    sp('cart', 31.4, 38.9); sp('barrels', 30.2, 31.2); sp('crates', 22.5, 30.5); sp('barrels', 59.4, 30.4); sp('crates', 47.3, 41.2)
    sp('anvil', 18.4, 58.5); sp('woodpile', 8.5, 57.6); sp('barrels', 19.6, 56.3)
    sp('herb_rack', 72.3, 38.0); sp('string_lights', 56, 41.3, False, fade=1, shadow=0)
    sp('candelabra', 72.6, 24.8); sp('mausoleum', 75.8, 22.6); sp('tombs', 74.9, 28.4); sp('tombs', 64.6, 27.8, flip=True)
    sp('cocoons', 74.4, 50.6); sp('cocoons', 67.8, 49.8, flip=True); sp('crates', 9.2, 28.6); sp('barrels', 22.4, 46.6)
    for q in small:
        if q['img'].endswith(('tombs.png', 'mausoleum.png')): Hs[int(q['y'] - 1.4):int(q['y']), int(q['x'] - 1):int(q['x'] + 1)] = True
    # grid
    grid = np.full((H, W), '.', dtype='<U1')
    grid[road] = '='; grid[water] = '~'; grid[S] = '#'; grid[C] = 'X'; grid[Hs] = 'H'
    for x in range(W):
        if grid[0, x] == 'X' and x % 2 == 0: grid[0, x] = 'C'
        if grid[1, x] == 'X' and x % 3 == 1: grid[1, x] = 'C'
    # doors & exits
    objs = []; DO = {o.get('id'): o for o in ORIG['objects'] if o['type'] == 'door'}
    for key, dx, dy, d in doors:
        grid[dy, dx] = 'H'; grid[dy + 1, dx] = '=' if grid[dy + 1, dx] != '=' else '='
        o = {'type': 'door', 'id': d['id'], 'x': dx, 'y': dy, 'name': d['name']}
        if d.get('to'): o.update(to=d['to'], spawn='door', out=d['out']); spawns[d['out']] = [dx + .5, dy + 1.9, 'down']
        if d.get('text'): o['text'] = d['text']
        old = DO.get(d['id'])
        if old and old.get('scene'): o['scene'] = old['scene']
        objs.append(o)
    # Arachne gate (the arch itself), guard post (not enterable: its door stays shut)
    objs.append(dict(DO['f_arachne_gate'], x=71, y=51)); grid[51, 71] = 'H'; spawns['arachne'] = [71.5, 53.2, 'down']
    objs.append(dict(DO['f_door_guard'], x=47, y=56)); grid[56, 47] = 'H'
    # free floor below doors
    for o in objs:
        if o['type'] == 'door' and grid[o['y'] + 1, o['x']] in '#CH': grid[o['y'] + 1, o['x']] = '='
    exitx = 38; objs.append({'type': 'exit', 'x': exitx, 'y': H - 1, 'w': 5, 'h': 1, 'to': 'field_felt', 'spawn': 'felt', 'label': '↓ 잿빛 들판'})
    grid[H - 4:, 38:43] = '='
    spawns.update({'default': [40.5, 50.5, 'up'], 'world': [40.5, 50.5, 'up'], 'field': [40.5, H - 2.5, 'up']})
    # decorate the forest border
    floor = np.isin(grid, ['.', '='])
    nb = ndimage.binary_dilation(floor, structure=np.ones((3, 3)))
    for y in range(H):
        for x in range(W):
            if grid[y, x] != '#': continue
            r = rnd.random()
            if nb[y, x]: grid[y, x] = rnd.choice('TTTPP') if r < .66 else ('R' if r < .82 else '#')
            elif r < .5: grid[y, x] = rnd.choice('TTP')
    # NPCs / objects from the old map, re-placed
    OB = {o.get('id'): o for o in ORIG['objects']}
    def put(o, x, y):
        o = copy.deepcopy(o); o['x'] = x; o['y'] = y; o.pop('near', None); objs.append(o)
        if o['type'] != 'door' and grid[y, x] not in '.=': raise SystemExit(f'object {o.get("id")} on {grid[y, x]} at {x},{y}')
        return o
    put(OB['f_gas'], 44, 54); put(OB['f_toby'], 45, 33); put(OB['f_luca'], 36, 33)
    put(OB['f_linette'], 18, 29); put(OB['f_ben'], 52, 47)
    put(OB['ws_felt_plaza'], 47, 31); put(OB['ws_arachne'], 68, 54)
    put(OB['f_chest_plaza'], 29, 31); put(OB['f_clue_bell'], 66, 25)
    put(OB['f_hid_grave'], 76, 26); put(OB['f_hid_cart'], 32, 40)
    put(OB['f_mark_fountain'], 40, 35); put(OB['f_mark_stall'], 52, 46); put(OB['f_mark_gate'], 40, 59)
    sign = OB.get(None)
    for o in ORIG['objects']:
        if o['type'] == 'sign': sign = o
    s = put(sign, 43, 58)
    s['text'] = '펠트\n↑ 광장 · 불탄 왕성   ← 무기점 · 잡화점 · 이장 집 · 대장간\n→ 여관 · 약초 오두막 · 예배당   ↘ 아라크네의 폐공방'
    # new: minigame (소원 우물), side-quest hooks, hidden collectibles, landmarks
    put({'type': 'door', 'id': 'f_well_wish', 'name': '소원 우물', 'wish': 1, 'fortunes': ['대길 — 잃어버린 것이 돌아온다.', '길 — 오늘 산 칼은 잘 든다.', '소길 — 따뜻한 스튜 한 그릇의 운.', '평 — 실 잣는 소리에 귀 기울이지 말 것.', '흉 — 해 지기 전에 돌아갈 것.']}, 33, 41)
    grid[41, 33] = 'H'
    put({'type': 'sign', 'text': '〔펠트 게시판〕\n· 왕성 잔해 출입 금지 — 경비대장 가스\n· 해자 갈대 구함, 값 쳐 드림 — 약초꾼 세라\n· 밤에는 여관 문을 잠급니다 — 마르타\n· 들판의 굳은 사슴을 본 자는 경비 초소로'}, 50, 31)
    put({'type': 'clue', 'id': 'f_clue_gate', 'x': 0, 'y': 0, 'name': '무너진 성문', 'flag': 'felt_look_gate', 'text': '불탄 왕성의 정문. 돌무더기와 숯이 된 들보가 문을 완전히 막았다.\n돌 틈에 낀 실 한 가닥이 바람에 떨린다. 안쪽에서 무언가가 당긴다.', 'textDone': '돌무더기에 막혀 들어갈 수 없다.'}, 40, 17)
    put({'type': 'clue', 'id': 'f_clue_moat', 'x': 0, 'y': 0, 'name': '해자의 녹슨 투구', 'flag': 'felt_look_moat', 'text': '해자 가장자리에 녹슨 근위대 투구가 걸려 있다. 안쪽에 이름이 긁혀 있다 — 「가스」.\n…경비대장의 옛 투구일까.', 'textDone': '녹슨 투구. 안쪽의 이름은 「가스」.', 'loot': [['potion', 1]]}, 25, 20)
    put({'type': 'hidden', 'id': 'f_hid_moat', 'loot': [['riceball', 1]], 'find': '해자 갈대 사이에서 찾았다!'}, 56, 20)
    put({'type': 'hidden', 'id': 'f_hid_tower', 'loot': [['potion', 1]], 'find': '초소 뒤 돌 틈에서 찾았다!'}, 49, 57)
    put({'type': 'hidden', 'id': 'f_hid_forge', 'loot': [['riceball', 1]], 'find': '장작더미 뒤에서 찾았다!'}, 7, 55)
    put({'type': 'landmark', 'id': 'lm_felt_castle', 'name': '불탄 왕성'}, 40, 19)
    put({'type': 'landmark', 'id': 'lm_felt_fountain', 'name': '금 간 분수'}, 40, 36)
    put({'type': 'landmark', 'id': 'lm_felt_grave', 'name': '예배당 묘지'}, 74, 25)
    # reachability
    SOL = set('#TPRCHX~')
    free = np.vectorize(lambda c: c not in SOL)(grid)
    sx, sy = 40, 50; reach = bfs(free, sx, sy)
    grid[free & ~reach] = '#'
    free2 = free & reach
    for o in objs:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'door'): free2[o['y'], o['x']] = False
    r2 = bfs(free2, sx, sy); lost = int((free & reach & ~r2).sum())
    bad = []
    for o in objs:
        x, y = o['x'], o['y']
        if o['type'] in ('door', 'npc', 'chest', 'sign', 'waystone', 'clue'):
            if not any(0 <= y + b < H and 0 <= x + a < W and r2[y + b, x + a] for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))): bad.append(o.get('id') or o['type'])
        elif o['type'] in ('hidden', 'mark', 'landmark') and not r2[y, x] and not any(r2[y + b, x + a] for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))): bad.append(o.get('id'))
    for k, (x, y, _) in spawns.items():
        if not r2[int(y), int(x)]: bad.append('spawn:' + k)
    ex = [o for o in objs if o['type'] == 'exit'][0]
    if not r2[ex['y'], ex['x'] + 2]: bad.append('exit')
    print(f'felt: reach {int(r2.sum())} cells, lost {lost}, unreachable {bad}')
    # ---- Wang ground ----
    Pw = wang.load_set(os.path.join(SETS, 'p_felt')); Ww = wang.load_set(os.path.join(SETS, 'w_felt')); Ww = wang.unify_base(Ww, Pw)
    tw, th = W * 3 // 2, H * 3 // 2
    wi = ndimage.gaussian_filter((grid == '~').astype(float), .95); pi = ndimage.gaussian_filter((grid == '=').astype(float) + .6 * (grid == 'H') * ndimage.binary_dilation(grid == '=', iterations=1), .85)
    vy, vx = np.mgrid[0:th + 1, 0:tw + 1] / 1.5 - .5
    ws = ndimage.map_coordinates(wi, [vy, vx], order=1, mode='nearest'); ps = ndimage.map_coordinates(pi, [vy, vx], order=1, mode='nearest')
    nz = (wang.vnoise(th + 1, tw + 1, 3, seed=SEED + 40) - .5) * .3 + (wang.vnoise(th + 1, tw + 1, 7, seed=SEED + 41) - .5) * .18
    V = np.ones((th + 1, tw + 1), int); V[ws + nz > .48] = 0; V[(ps + nz > .4) & (ws < .12)] = 2
    img = np.array(wang.compose(V, Pw, Ww, seed=SEED, mottle=.12, gr={'sat': .72, 'gain': .95})).astype(np.float32)
    bandm = ndimage.gaussian_filter(np.isin(grid, ['#', 'T', 'P', 'R', 'C', 'X']).astype(float), 1.0)
    bm = np.array(Image.fromarray((bandm * 255).astype(np.uint8)).resize((img.shape[1], img.shape[0]), Image.BILINEAR)) / 255.
    img *= 1.32 * (1 - .42 * bm)[..., None] * np.array([1, 1, 1.03])
    wm = np.array(Image.fromarray((ndimage.gaussian_filter((V == 0).astype(float), .8) * 255).astype(np.uint8)).resize((img.shape[1], img.shape[0]), Image.BILINEAR)) / 255.
    img += wm[..., None] * np.array([14, 14, 18])
    gimg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    gp = FA + 'ground2.png'; gimg.save(os.path.join(ROOT, gp), optimize=True)
    # ---- hd block ----
    def arts(keys): return [{'img': FF + k + '.png', 'ax': props.OLD[k][1], 'ay': props.OLD[k][2]} for k in keys]
    decoArt = {'T': arts(['ash_tree_a', 'ash_tree_b', 'dead_tree']), 'P': arts(['burnt_pine_a', 'burnt_pine_b']), 'R': arts(['boulder']),
               'u': arts(['ash_bush', 'bush_b']), 'w': arts(['dry_reeds']), 's': arts(['stump', 'stone_low', 'stump', 'pale_mushrooms', 'stone_low']),
               'C': arts(['burnt_pine_a', 'burnt_pine_b', 'dead_tree'])}
    for d in decoArt['T'] + decoArt['P']: d['sway'] = 1
    decoArt['w'][0]['sway'] = 3; decoArt['u'][0]['sway'] = .5; decoArt['u'][1]['sway'] = .5
    # reeds along the moat, a few bushes / trees inside town
    dw = ndimage.distance_transform_edt(grid != '~'); taken = {(o['x'], o['y']) for o in objs}
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if grid[y, x] != '.' or (x, y) in taken: continue
            if dw[y, x] <= 1.5 and rnd.random() < .2: grid[y, x] = 'w'
            elif dw[y, x] > 2 and grid[y-1:y+2, x-1:x+2].tolist().count('=') == 0 and rnd.random() < .022: grid[y, x] = 's'
    for x, y in ((6, 33), (21, 40), (33, 47), (47, 48), (61, 49), (63, 31), (18, 22), (30, 22), (50, 24), (8, 42), (75, 33), (57, 55), (24, 52), (34, 54)):
        if grid[y, x] == '.' and grid[y - 1:y + 2, x - 1:x + 2].tolist().count('H') == 0: grid[y, x] = rnd.choice('Tu')
    free = np.vectorize(lambda c: c not in SOL | {'u'})(grid); free2 = free.copy()
    for o in objs:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'door'): free2[o['y'], o['x']] = False
    r3 = bfs(free2, sx, sy); print('  after scatter reach', int(r3.sum()), 'lost', int((r2 & ~r3).sum()))
    wruns = []
    for y in range(H):
        x = 0
        while x < W:
            if grid[y, x] == '~':
                x0 = x
                while x < W and grid[y, x] == '~': x += 1
                wruns.append([y, x0, x - 1])
            x += 1
    tufts = [[round(x + rnd.random(), 2), round(y + .3 + rnd.random() * .7, 2), rnd.randrange(4) if rnd.random() < .12 else rnd.randrange(3)]
             for y in range(1, H - 1) for x in range(1, W - 1) if grid[y, x] == '.' and rnd.random() < .2]
    for t in tufts:
        if t[2] == 3 and rnd.random() < .5: t[2] = 1
    allp = props_ + small
    lights = []; fires = []
    for q in small:
        n = os.path.basename(q['img'])[:-4]
        if n == 'brazier': lights.append([q['x'], q['y'] - .9, 62, '#ff8a3a', 1]); fires.append([q['x'], q['y'] - 1.05, 1.0])
        if n == 'lamp': lights.append([q['x'], q['y'] - 1.2, 46, '#ffb060', .8]); fires.append([q['x'], q['y'] - 1.25, .45])
        if n == 'candelabra': lights.append([q['x'], q['y'] - 1.6, 30, '#ffc070', .7]); fires.append([q['x'], q['y'] - 2.05, .3])
    # forge glow (outdoor furnace under the awning of the smithy), inn windows, embers in the castle rubble
    fx_ = {'forge': None}
    for q in props_:
        if q['id'] == 'se_house':
            fxp = q['x'] + (210 - q['ax']) / 3 / T; fyp = q['y'] - (q['ay'] - 262) / 3 / T
            lights.append([fxp, fyp, 70, '#ff7a2a', 1]); fires.append([fxp, fyp, 1.3, 'forge']); fx_['forge'] = [fxp, fyp]
        if q['id'] == 'inn': lights.append([q['x'] - 1.5, q['y'] - 1.5, 54, '#ffb060', .8])
    lights.append([40.5, 15.6, 50, '#ff6a2a', .8]); fires.append([40.5, 15.9, .6, 'embers'])
    smoke = []
    for q in props_:
        off = {'se_house': (-1.6, -6.9), 's_house': (-.2, -6.4), 'bl_house': (1.9, -4.6), 'inn': (2.2, -7.6)}.get(q['id'])
        if off: smoke.append([q['x'] + off[0], q['y'] + off[1], 1])
    smoke += [[30.5, 4.0, 1.8], [47.5, 3.5, 1.6], [61.0, 4.5, 1.5]]
    fount = None
    for q in props_:
        if q['id'] == 'fountain':
            fount = {'x': q['x'], 'y': q['y'], 'ax': q['ax'], 'ay': q['ay'], 'D': 3, 'streams': [[86, 214, 262], [102, 222, 270], [124, 228, 276], [170, 228, 276], [192, 222, 270], [206, 214, 262]],
                     'pool': [146, 262, 112, 42], 'rim': [146, 206, 62, 14]}
    hd = {'D': 3, 'ground': gp, 'props': allp, 'decoArt': decoArt, 'lights': lights, 'smoke': smoke, 'grade': 'dusk', 'water': wruns, 'tufts': tufts,
          'fires': fires, 'fountains': [fount], 'fx': {'particles': 'ash', 'birds': 2, 'butterflies': 2, 'tuft': ['#5b5646', '#6b6450', '#4a473b'], 'water': 'moat'},
          'webs': [[70.2, 47.6, 72.6, 49.2, .5, .3], [69.0, 49.5, 71.5, 50.2, .6, .3], [72.0, 46.5, 73.8, 48.6, .4, .25]]}
    legend = {'.': 'dirt', '=': 'dirt', '~': 'water', '#': 'cliff', 'X': 'cliff', 'C': {'ground': 'cliff', 'deco': 'pine'}, 'H': {'ground': 'dirt', 'solid': True},
              'T': {'ground': 'dirt', 'deco': 'tree'}, 'P': {'ground': 'dirt', 'deco': 'pine'}, 'R': {'ground': 'dirt', 'deco': 'boulder'},
              'u': {'ground': 'dirt', 'deco': 'bush'}, 's': {'ground': 'dirt', 'deco': 'stump', 'solid': False}, 'w': {'ground': 'dirt', 'deco': 'mushrooms', 'solid': False}}
    out = {k: ORIG[k] for k in ('type', 'area', 'title', 'bgm', 'battleBgm', 'tileset', 'tile', 'id', 'name')}
    out.update({'region': ORIG['region'], 'w': W, 'h': H, 'legend': legend, 'solid': ['#', 'C', 'X', 'H', 'T', 'P', 'R', 'u', '~'],
                'ground': [''.join(r) for r in grid], 'objects': objs, 'spawns': spawns, 'hd': hd,
                'note': 'GENERATED by tools/hd/fields/build_felt2.py (standalone town: castle north, moat, wide DQ layout, every door has an interior) - do not hand-edit'})
    json.dump(out, open(os.path.join(ROOT, 'maps/felt.json'), 'w'), ensure_ascii=False, indent=1)
    return out
if __name__ == '__main__':
    main()
