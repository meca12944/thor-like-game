"""Felt town v3 (owner review 10-24): organic lived-in DQ-style village.
- curving / branching roads of varying width, round cobble plaza around a bigger fountain
- buildings ~1.33x bigger (D=2.25), grouped in rows/clusters with yards, gardens, wells, carts, lanterns, trees, grass
- a grand intact castle (PixelLab) behind the moat, wooden bridge + banner-lined approach road
- clean procedural cobble (tools/hd/fields/cobble.py) melting into packed earth and grass
Usage: python3 build_felt3.py -> maps/felt.json (+ assets/world/felt/{castle_grand,ground3,f3_*}.png)"""
import json, os, sys, math, random, copy, glob, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wang, props, cobble
from build import crom, disk, bfs, SETS
import build_felt2 as F2
ROOT = props.ROOT; FA = F2.FA; FF = F2.FF; T = 16
W, H = 88, 68; SEED = 7; G = 48              # ground px per cell
ORIG = F2.ORIG; P = F2.P; DOORS = F2.DOORS
GI = '/tmp/plwork/out/gi'
def rel(p): return os.path.join(ROOT, p)
def prep_assets():
    A = {}
    src = f'{GI}/castle_grand_b_0.png'; dst = FA + 'castle_grand.png'
    if os.path.exists(src):
        im = Image.open(src).convert('RGBA'); im = im.crop(im.getbbox()); a = np.array(im).astype(int)
        a[..., 3] = np.where(a[..., 3] < 40, 0, 255); a = props._grade(a, .86, (1.03, 1.0, .95), .93)
        Image.fromarray(a.astype(np.uint8)).save(rel(dst), optimize=True)
    im = Image.open(rel(dst)); A['castle'] = {'img': dst, 'ax': im.width // 2, 'ay': im.height - 2, 'w': im.width, 'h': im.height}
    for pre in ('f3_garden', 'f3_flowers', 'f3_hay', 'f3_goods', 'f3_banner'):
        A[pre] = []
        for i in range(4):
            s = f'{GI}/{pre}_{i}.png'; d = f'{FA}{pre}_{i}.png'
            if os.path.exists(s):
                v = props.prep(s, '_tmp', sat=.82, warm=(1.03, 1.0, .95), gain=.95); shutil.move(rel(v['img']), rel(d))
            im = Image.open(rel(d)); ax, ay = props.anchor(im)
            A[pre].append({'img': d, 'ax': ax, 'ay': ay, 'w': im.width, 'h': im.height})
    for n in ('laundry_line', 'sign_weapon_sword', 'sign_tool_hammer_bag', 'sign_herb_leaf'):
        s = os.path.join(ROOT, '..', 'docs_art/felt_props', n + '.png'); d = FA + 'f3_' + n + '.png'
        if os.path.exists(s): shutil.copy(s, rel(d))
        im = Image.open(rel(d)); ax, ay = props.anchor(im); A[n] = {'img': d, 'ax': ax, 'ay': ay, 'w': im.width, 'h': im.height}
    cat = json.load(open(rel('assets/world/fields_hd/catalog.json'))); A['oak'] = cat['oak'] + cat['oak1']
    return A
# (key, art, x, foot y, D)
BUILD = [
 ('atelier', 'linette', 14, 29, 2.25), ('tool', 'bl_house', 28, 28, 2.25), ('inn', 'inn', 63, 30, 2.25), ('chapel', 'chapel', 78, 27, 1.4),
 ('chief', 's_house', 11, 46, 2.25), ('weapon', 'west_b', 26, 46, 2.25), ('herb', 'e_row', 73, 46, 2.25),
 ('stall', 'red_stall', 60, 45, 3), ('stall2', 'stall_n', 52, 44, 3),
 ('forge', 'se_house', 12, 63, 2.25), ('empty', 'sw_house', 31, 62, 2.25), ('guard', 'watchtower', 53, 61, 1.5), ('arachne', 'web_arch', 79, 62, 2.5),
 ('fountain', 'fountain', 44.5, 36, 2.25),
]
DOORART = {'atelier': (238, 265, 46, 70), 'tool': (106, 218, 40, 75), 'weapon': (92, 388, 40, 72), 'chief': (136, 300, 54, 100), 'forge': (60, 300, 44, 82),
           'inn': (176, 343, 48, 80), 'herb': (110, 300, 44, 75), 'chapel': (62, 200, 40, 55), 'empty': (175, 345, 44, 90)}
PLAZA = (44.5, 33.5, 7.0)
def main():
    A = prep_assets(); rnd = random.Random(SEED)
    yy, xx = np.mgrid[0:H, 0:W]
    de = np.minimum(np.minimum(xx, W - 1 - xx), H - 1 - yy).astype(float)
    S = de < 1.6 + 2.6 * wang.vnoise(H, W, 6, SEED)                    # forest border
    S |= (yy < 22) & ((xx < 25 + 3 * wang.vnoise(H, W, 4, SEED + 2)) | (xx > 63 - 3 * wang.vnoise(H, W, 4, SEED + 3)))
    S |= (yy < 18)
    C = np.zeros((H, W), bool); water = np.zeros((H, W), bool); Hs = np.zeros((H, W), bool)
    road = np.zeros((H, W), bool); clear = np.zeros((H, W), bool); lanec = np.zeros((H, W), bool)
    RD = Image.new('L', (W * G, H * G), 0); LD = Image.new('L', (W * G, H * G), 0); dR = ImageDraw.Draw(RD); dL = ImageDraw.Draw(LD)
    def lay(pts, r, kind='road', c=None):
        rr = r if isinstance(r, (list, tuple)) else [r] * len(pts)
        sp = crom(pts); n = len(sp)
        for i, p in enumerate(sp):
            f = i / max(1, n - 1) * (len(rr) - 1); j = min(int(f), len(rr) - 2) if len(rr) > 1 else 0
            ri = rr[j] + (rr[j + 1] - rr[j]) * (f - j) if len(rr) > 1 else rr[0]
            if not (0 <= p[0] < W and 0 <= p[1] < H + 1): continue
            disk(road if kind == 'road' else lanec, p[0], p[1], ri); disk(clear, p[0], p[1], (c or ri + 1.2))
            dd = dR if kind == 'road' else dL; R = ri * G
            dd.ellipse([p[0] * G - R, p[1] * G - R, p[0] * G + R, p[1] * G + R], fill=255)
    # ---- castle (north), moat, bridge ----
    cas = A['castle']; CD = 1.3; cx0 = 44.5; cfy = 17.6
    props_ = [{'id': 'castle_grand', 'img': cas['img'], 'x': cx0, 'y': cfy, 'ax': cas['ax'], 'ay': cas['ay'], 'D': CD, 'fade': 0, 'shadow': 0}]
    hw = cas['w'] / CD / T / 2
    C[:17, int(cx0 - hw + .6):int(cx0 + hw - .4)] = True
    for x in range(20, 70):
        yc = 19.9 + .45 * math.sin(x / 4.3)
        for y in range(18, 23):
            if abs(y + .5 - yc) <= 1.25 and not (43 <= x <= 45): water[y, x] = True
    for y in range(18, 23):
        for x in (43, 44, 45): water[y, x] = True
    props_.append({'id': 'bridge', 'img': props.OLD['bridge_3'][0], 'x': 44.5, 'y': 22.4, 'ax': 60, 'ay': 143, 'D': 2.4, 'under': 1, 'fade': 0, 'shadow': 0})
    bridge = [(x, y) for x in (43, 44, 45) for y in range(18, 23)]
    # ---- roads (cobble, varying width) + packed-earth lanes ----
    lay([(44.5, 17.2), (44.5, 22.5), (44.6, 25), (44.5, 27.5)], [1.25, 1.5, 1.7, 2.0])                       # castle approach
    lay([(44.5, 40), (43.6, 44), (42.8, 48), (44.6, 53), (45.2, 57), (44.3, 61), (44.5, 68.5)], [2.0, 1.6, 1.5, 1.4, 1.6, 1.8, 2.0])  # south road
    lay([(38, 31.5), (33, 32.5), (27, 30.9), (20, 32.4), (13, 31.0), (6, 32.8), (2.5, 34.0)], [1.8, 1.3, 1.05, 1.45, 1.0, 1.1, .8])  # west road
    lay([(51, 31.5), (56, 32.6), (62, 33.4), (69, 32.0), (75, 31.2), (80, 30.4)], [1.8, 1.25, 1.5, 1.05, 1.2, .9])  # east road
    lay([(43, 48.4), (36, 50.4), (28, 48.7), (20, 50.5), (13, 49.0), (7.5, 50.6)], [1.6, 1.1, 1.35, 1.0, 1.15, .9])  # south-west street
    lay([(46, 47.5), (52, 49.3), (59, 47.9), (66, 50.0), (72, 49.1), (77, 49.6)], [1.6, 1.15, 1.4, 1.0, 1.15, .95])   # south-east street
    lay([(50, 38.8), (53.5, 41.5), (56, 44.6), (58, 47.5)], [1.3, 1.1, 1.0, 1.0])                              # market lane
    disk(road, PLAZA[0], PLAZA[1], PLAZA[2]); disk(clear, PLAZA[0], PLAZA[1], PLAZA[2] + 1.5)
    R = PLAZA[2] * G; dR.ellipse([PLAZA[0] * G - R, PLAZA[1] * G - R, PLAZA[0] * G + R, PLAZA[1] * G + R], fill=255)
    lay([(7.5, 50.6), (7.2, 55), (9.5, 59.5), (11.5, 63.6)], .9, 'lane')                                        # forge lane (outskirts)
    lay([(75, 31.0), (77, 28.2)], .8, 'lane')                                                                     # chapel
    lay([(77, 49.2), (78.4, 54), (79, 58.5), (79, 63.4)], [1.0, .9, .9, .9], 'lane')                                # arachne trail
    lay([(46, 59.5), (50, 61.6), (53, 62.0)], .8, 'lane')                                                         # guard post
    lay([(31, 50), (31, 56), (31, 62.6)], .8, 'lane')                                                             # empty house
    lay([(20, 31.8), (22, 27.4), (24, 25.5)], .7, 'lane')                                                          # yard path
    # ---- buildings ----
    doors = []; spawns = {}
    for key, art, x, y, Dq in BUILD:
        v = P(art); wc = v['w'] / Dq / T
        dep = {'fountain': 3, 'guard': 2, 'stall2': 2, 'stall': 3, 'arachne': 3, 'chapel': 4}.get(key, 5 if v['w'] > 300 else 4)
        x0 = int(round(x - wc * .43)); x1 = int(round(x + wc * .43))
        Hs[y - dep:y, x0:x1] = True
        q = {'id': art, 'img': v['img'], 'x': x, 'y': y, 'ax': v['ax'], 'ay': v['ay'], 'D': Dq, 'fade': 1, 'shadow': 0}
        if key in DOORART:
            cx, by, dw, dh = DOORART[key]; dx = int(math.floor(x + (cx - v['ax']) / Dq / T)); dy = y - 1
            d = DOORS[key]; doors.append((key, dx, dy, d))
            im = np.array(Image.open(rel(v['img'])).convert('RGB')).astype(float)
            reg = im[int(by - dh * .9):int(by - dh * .1), int(cx - dw * .3):int(cx + dw * .3)].reshape(-1, 3)
            q['door'] = {'id': d['id'], 'cx': cx, 'by': by, 'w': dw, 'h': dh, 'col': [int(c) for c in np.median(reg, 0)]}
        props_.append(q)
    for key, dx, dy, d in doors:   # short connector from each door to the nearest street / lane
        m = road | lanec; dist, ind = ndimage.distance_transform_edt(~m, return_indices=True)
        ty_, tx_ = ind[0][dy + 2, dx], ind[1][dy + 2, dx]
        kind = 'lane' if key in ('forge', 'chapel', 'empty') else 'road'
        lay([(dx + .5, dy + 1.2), (dx + .5, dy + 2.0), ((dx + tx_) / 2 + .5, (dy + 2 + ty_) / 2 + .5), (tx_ + .5, ty_ + .5)], .85 if kind == 'road' else .75, kind, 1.4)
    S &= ~clear; S &= ~water; C &= ~water
    # ---- small props ----
    small = []
    def sp(art, x, y, solid=True, D=3, flip=False, v=None, **kw):
        v = v or P(art)
        q = dict({'id': f'{os.path.basename(v["img"])[:-4]}_{len(small)}', 'img': v['img'], 'x': x, 'y': y, 'ax': v['ax'], 'ay': v['ay'], 'D': D, 'fade': 0, 'shadow': 1, 'flip': flip}, **kw)
        small.append(q)
        if solid: Hs[int(y - .6), int(x)] = True
        return q
    def tree(x, y, kind=None, D=2.25):
        k = kind or rnd.choice(['oak', 'oak', 'oak', 'ash_tree_a', 'ash_tree_b'])
        if k == 'oak': v = rnd.choice(A['oak'])
        else: o = props.OLD[k]; v = {'img': o[0], 'ax': o[1], 'ay': o[2]}
        sp(None, x, y, True, D if k == 'oak' else 3, flip=rnd.random() < .5, v=v, sway=1)
    pick = lambda k, i=None: A[k][rnd.randrange(len(A[k])) if i is None else i]
    # castle approach: banners, braziers at the bridge head
    for x in (40.6, 48.4): sp(None, x, 17.7, True, 2.4, v=pick('f3_banner', 0), sway=.6)
    for x in (41.4, 47.6): sp(None, x, 25.3, True, 2.4, v=pick('f3_banner', 2), sway=.6)
    for x in (39.6, 49.4): sp('brazier', x, 23.4)
    for x, y in ((38.6, 28.8), (50.4, 28.8), (38.6, 38.6), (50.4, 38.6)): sp('brazier', x, y)
    # plaza: benches, flower beds, goods, stalls' wares, notice board, string lights
    sp('bench', 40.0, 30.2); sp('bench', 49.0, 30.2, flip=True)
    for x, y in ((37.6, 33.6), (51.4, 33.6)): sp(None, x, y, True, 2.6, v=pick('f3_flowers', 0 if x < 44 else 1))
    sp(None, 55.6, 41.8, True, 2.6, v=pick('f3_goods', 0)); sp(None, 63.6, 42.6, True, 2.6, v=pick('f3_goods', 2)); sp(None, 49.6, 45.6, True, 2.6, v=pick('f3_goods', 3))
    sp('string_lights', 56.2, 39.6, False, fade=1, shadow=0)
    # lamps along the streets
    for x, y in ((42.4, 44.5), (46.8, 52.5), (42.2, 58.5), (47.0, 64.5), (33, 29.6), (22, 29.9), (8.5, 30.4), (56, 29.9), (69, 30.2), (76.8, 33.0),
                 (36, 47.7), (22, 47.8), (14, 51.4), (53, 50.5), (66, 51.0), (73, 47.9), (80.6, 52.5), (9.3, 57)):
        sp('lamp', x, y)
    # NW yard (atelier + tool shop): garden, laundry, flowers, well, hay
    sp(None, 21.2, 24.2, True, 2.6, v=pick('f3_garden', 0)); sp(None, 21.6, 26.6, True, 2.6, v=pick('f3_garden', 1))
    sp(None, 6.6, 27.8, False, 2.6, v=A['laundry_line'], sway=.8, shadow=0)
    sp(None, 33.6, 26.2, True, 2.6, v=pick('f3_flowers', 2)); sp('barrels', 32.8, 28.2); sp('crates', 23.6, 28.4); sp(None, 8.2, 25.6, True, 2.6, v=pick('f3_hay', 0))
    sp(None, 30.8, 23.6, False, 3, v=A['sign_tool_hammer_bag'], shadow=0)
    # west row (chief + weapon): yard between, hay, cart, garden
    sp(None, 18.6, 42.6, True, 2.6, v=pick('f3_garden', 2)); sp(None, 18.6, 45.4, True, 2.6, v=pick('f3_flowers', 3))
    sp('cart', 33.4, 44.4); sp(None, 34.6, 47.2, True, 2.6, v=pick('f3_hay', 1)); sp('barrels', 21.6, 47.4); sp('woodpile', 4.6, 44.6)
    sp(None, 22.4, 44.0, False, 3, v=A['sign_weapon_sword'], shadow=0)
    # east: inn yard, herb garden
    sp('barrels', 56.6, 29.6); sp('crates', 69.4, 29.4); sp(None, 70.4, 27.0, True, 2.6, v=pick('f3_hay', 3))
    sp('herb_rack', 77.8, 46.4); sp(None, 67.6, 44.8, True, 2.6, v=pick('f3_garden', 3)); sp(None, 67.2, 41.8, True, 2.6, v=pick('f3_flowers', 1))
    sp(None, 69.6, 43.6, False, 3, v=A['sign_herb_leaf'], shadow=0)
    # chapel + graveyard (NE)
    sp('candelabra', 74.6, 27.0); sp('mausoleum', 84.0, 25.4); sp('tombs', 82.6, 30.6); sp('tombs', 74.0, 24.0, flip=True)
    # south: forge outskirts, empty house, guard post, farm patch, arachne
    sp('anvil', 18.6, 63.4); sp('woodpile', 4.8, 62.2); sp('barrels', 19.6, 61.0); sp(None, 21.0, 58.8, True, 2.6, v=pick('f3_hay', 2))
    sp('crates', 36.4, 61.4); sp('cart', 26.2, 57.2)
    for i, (x, y) in enumerate(((58, 55.2), (61.6, 55.4), (65.2, 55.0), (58.4, 58.4), (62.0, 58.6), (65.6, 58.2))): sp(None, x, y, True, 2.6, v=pick('f3_garden', i % 4))
    sp(None, 68.8, 57.0, True, 2.6, v=pick('f3_hay', 0))
    for x, y in ((82.6, 57.2), (75.4, 58.6), (83.4, 62.6)):
        o = props.OLD['thread_stake']; sp(None, x, y, True, 3, v={'img': o[0], 'ax': o[1], 'ay': o[2]})
    sp('cocoons', 82.4, 60.2); sp('cocoons', 75.6, 61.4, flip=True)
    # trees: groves between the clusters (+ along the edges), grass in the gaps
    groves = [(36, 24, 3), (53, 25, 3), (4, 38, 2), (17, 38, 2), (34, 38, 3), (55, 36.5, 2), (68.5, 38, 2), (81, 38, 3), (39, 55, 3), (50, 56, 2),
              (24, 53.5, 2), (4, 54, 2), (71, 54, 2), (84, 46, 2), (60, 63, 3), (37, 65, 2), (25, 65, 2), (16, 54, 1), (70.5, 63.5, 2)]
    for gx, gy, n in groves:
        for i in range(n):
            for _ in range(20):
                x = gx + rnd.uniform(-2.2, 2.2); y = gy + rnd.uniform(-1.4, 1.4); cx_, cy_ = int(x), int(y - .6)
                if 0 < cx_ < W - 1 and 0 < cy_ < H - 1 and not (road | lanec | Hs | water)[cy_ - 1:cy_ + 2, cx_ - 1:cx_ + 2].any():
                    tree(x, y); break
    # ---- grid ----
    grid = np.full((H, W), '.', dtype='<U1')
    grid[road | lanec] = '='; grid[water] = '~'; grid[S] = '#'; grid[C] = 'X'; grid[Hs] = 'H'
    for x, y in bridge: grid[y, x] = '='
    objs = []; DO = {o.get('id'): o for o in ORIG['objects'] if o['type'] == 'door'}
    for key, dx, dy, d in doors:
        grid[dy, dx] = 'H'; grid[dy + 1, dx] = '='
        o = {'type': 'door', 'id': d['id'], 'x': dx, 'y': dy, 'name': d['name']}
        if d.get('to'): o.update(to=d['to'], spawn='door', out=d['out']); spawns[d['out']] = [dx + .5, dy + 1.9, 'down']
        if d.get('text'): o['text'] = d['text']
        old = DO.get(d['id'])
        if old and old.get('scene'): o['scene'] = old['scene']
        objs.append(o)
    ag = (79, 61); objs.append(dict(DO['f_arachne_gate'], x=ag[0], y=ag[1])); grid[ag[1], ag[0]] = 'H'; grid[ag[1] + 1, ag[0]] = '='; spawns['arachne'] = [ag[0] + .5, ag[1] + 2.2, 'down']
    objs.append(dict(DO['f_door_guard'], x=53, y=60)); grid[60, 53] = 'H'; grid[61, 53] = '='
    ex = 42; objs.append({'type': 'exit', 'x': ex, 'y': H - 1, 'w': 5, 'h': 1, 'to': 'field_felt', 'spawn': 'felt', 'label': '↓ 잿빛 들판'})
    grid[H - 4:, 42:47] = '='
    spawns.update({'default': [44.5, 52.5, 'up'], 'world': [44.5, 52.5, 'up'], 'field': [44.5, H - 2.5, 'up']})
    floor = np.isin(grid, ['.', '='])
    nb = ndimage.binary_dilation(floor, structure=np.ones((3, 3)))
    for y in range(H):
        for x in range(W):
            if grid[y, x] != '#': continue
            r = rnd.random()
            if nb[y, x]: grid[y, x] = rnd.choice('TTTPP') if r < .7 else ('R' if r < .8 else '#')
            elif r < .55: grid[y, x] = rnd.choice('TTP')
    # ---- NPCs / objects ----
    OB = {o.get('id'): o for o in ORIG['objects']}
    def put(o, x, y):
        o = copy.deepcopy(o); o['x'] = x; o['y'] = y; o.pop('near', None); objs.append(o)
        if o['type'] != 'door' and grid[y, x] not in '.=': raise SystemExit(f'object {o.get("id")} on {grid[y, x]} at {x},{y}')
        return o
    put(OB['f_gas'], 48, 58); put(OB['f_toby'], 48, 37); put(OB['f_luca'], 40, 37)
    put(OB['f_linette'], 18, 31); put(OB['f_ben'], 60, 47)
    put(OB['ws_felt_plaza'], 50, 31); put(OB['ws_arachne'], 76, 63)
    put(OB['f_chest_plaza'], 35, 27); put(OB['f_clue_bell'], 76, 29)
    put(OB['f_hid_grave'], 84, 28); put(OB['f_hid_cart'], 33, 46)
    put(OB['f_mark_fountain'], 44, 38); put(OB['f_mark_stall'], 60, 46); put(OB['f_mark_gate'], 44, 64)
    sign = [o for o in ORIG['objects'] if o['type'] == 'sign'][0]
    s = put(sign, 46, 63)
    s['text'] = '펠트\n↑ 광장 · 펠트 왕성   ← 잡화점 · 리네트 공방 · 무기점 · 이장 집 · 대장간(외곽)\n→ 여관 · 약초 오두막 · 예배당   ↘ 아라크네의 폐공방'
    put({'type': 'door', 'id': 'f_well_wish', 'name': '소원 우물', 'wish': 1, 'fortunes': ['대길 — 잃어버린 것이 돌아온다.', '길 — 오늘 산 칼은 잘 든다.', '소길 — 따뜻한 스튜 한 그릇의 운.', '평 — 실 잣는 소리에 귀 기울이지 말 것.', '흉 — 해 지기 전에 돌아갈 것.']}, 38, 42)
    grid[42, 38] = 'H'
    sp('well', 38.5, 43.0, False)
    put({'type': 'sign', 'text': '〔펠트 게시판〕\n· 왕성 출입은 허가받은 자만 — 근위대\n· 해자 갈대 구함, 값 쳐 드림 — 약초꾼 세라\n· 밤에는 여관 문을 잠급니다 — 마르타\n· 들판의 굳은 사슴을 본 자는 경비 초소로'}, 52, 35)
    put({'type': 'clue', 'id': 'f_clue_gate', 'name': '왕성 정문', 'flag': 'felt_look_gate', 'text': '굳게 닫힌 펠트 왕성의 정문. 쇠창살 너머로 횃불이 흔들리고, 성벽 위로 근위병의 그림자가 오간다.\n「허가 없는 자, 들이지 말 것.」 문 옆 놋쇠판에 그렇게 새겨져 있다.', 'textDone': '정문은 굳게 닫혀 있다. 허가 없이는 들어갈 수 없다.'}, 44, 17)
    put({'type': 'clue', 'id': 'f_clue_moat', 'name': '해자의 녹슨 투구', 'flag': 'felt_look_moat', 'text': '해자 가장자리에 녹슨 근위대 투구가 걸려 있다. 안쪽에 이름이 긁혀 있다 — 「가스」.\n…경비대장의 옛 투구일까.', 'textDone': '녹슨 투구. 안쪽의 이름은 「가스」.', 'loot': [['potion', 1]]}, 30, 22)
    put({'type': 'hidden', 'id': 'f_hid_moat', 'loot': [['riceball', 1]], 'find': '해자 갈대 사이에서 찾았다!'}, 58, 22)
    put({'type': 'hidden', 'id': 'f_hid_tower', 'loot': [['potion', 1]], 'find': '초소 뒤 돌 틈에서 찾았다!'}, 55, 59)
    put({'type': 'hidden', 'id': 'f_hid_forge', 'loot': [['riceball', 1]], 'find': '장작더미 뒤에서 찾았다!'}, 5, 60)
    put({'type': 'landmark', 'id': 'lm_felt_castle', 'name': '펠트 왕성'}, 44, 19)
    put({'type': 'landmark', 'id': 'lm_felt_fountain', 'name': '광장 분수'}, 44, 39)
    put({'type': 'landmark', 'id': 'lm_felt_grave', 'name': '예배당 묘지'}, 80, 29)
    # ---- reachability ----
    SOL = set('#TPRCHX~')
    free = np.vectorize(lambda c: c not in SOL)(grid); sx, sy = 44, 52
    reach = bfs(free, sx, sy); grid[free & ~reach] = '#'; free2 = free & reach
    for o in objs:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'door'): free2[o['y'], o['x']] = False
    r2 = bfs(free2, sx, sy); lost = int((free & reach & ~r2).sum()); bad = []
    for o in objs:
        x, y = o['x'], o['y']
        if o['type'] in ('door', 'npc', 'chest', 'sign', 'waystone', 'clue'):
            if not any(0 <= y + b < H and 0 <= x + a < W and r2[y + b, x + a] for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))): bad.append(o.get('id') or o['type'])
        elif o['type'] in ('hidden', 'mark', 'landmark') and not r2[y, x] and not any(r2[y + b, x + a] for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))): bad.append(o.get('id'))
    for k, (x, y, _) in spawns.items():
        if not r2[int(y), int(x)]: bad.append('spawn:' + k)
    if not r2[H - 1, ex + 2]: bad.append('exit')
    print(f'felt: reach {int(r2.sum())} cells, lost {lost}, unreachable {bad}')
    # ---- ground: Wang dirt/water + muted grass patches + packed lanes + clean cobble ----
    Pw = wang.load_set(os.path.join(SETS, 'p_felt')); Ww = wang.load_set(os.path.join(SETS, 'w_felt')); Ww = wang.unify_base(Ww, Pw)
    tw, th = W * 3 // 2, H * 3 // 2
    wi = ndimage.gaussian_filter((grid == '~').astype(float), .95)
    vy, vx = np.mgrid[0:th + 1, 0:tw + 1] / 1.5 - .5
    ws = ndimage.map_coordinates(wi, [vy, vx], order=1, mode='nearest')
    V = np.ones((th + 1, tw + 1), int); V[ws > .48] = 0
    img = np.array(wang.compose(V, Pw, Ww, seed=SEED, mottle=.10, gr={'sat': .72, 'gain': .95})).astype(np.float32)
    img = img * .55 + ndimage.uniform_filter(img, size=(5, 5, 1)) * .45            # calmer dirt (less pixel noise)
    gh, gw = img.shape[:2]
    def up(a, o=1): return np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((gw, gh), Image.BILINEAR)).astype(np.float32) / 255.
    # grass: tiled grass texture, graded to a dusty olive, in noisy patches away from streets / houses
    Gs = wang.load_set(os.path.join(SETS, 't_grass_dirt')); gt = Gs[(1, 1, 1, 1)]
    grass = np.zeros_like(img); r_ = random.Random(SEED + 9)
    for y in range(0, gh, 32):
        for x in range(0, gw, 32): grass[y:y + 32, x:x + 32] = wang.d4(gt, r_.randrange(8))[:min(32, gh - y), :min(32, gw - x)]
    grass = wang.grade(grass, sat=.5, warm=(.98, 1.03, .86), gain=.8)
    grass = grass * .45 + ndimage.uniform_filter(grass, size=(7, 7, 1)) * .55
    gm = wang.vnoise(gh, gw, 170, SEED + 11) * .7 + wang.vnoise(gh, gw, 47, SEED + 12) * .3
    near = ndimage.distance_transform_edt(~((road | lanec | Hs | water | C) & ~np.isin(grid, ['T', 'P']))) 
    away = up(np.clip((near - 1.0) / 2.5, 0, 1))
    fine = wang.vnoise(gh, gw, 6, SEED + 13)
    gmask = ((gm * .9 + away * .5 + (fine - .5) * .16) > .72).astype(np.float32)
    gmask = np.maximum(gmask, (up(np.isin(grid, ['#', 'T', 'P', 'R']).astype(float)) * (gm > .45)).astype(np.float32) * .0)
    rimg = ndimage.binary_dilation(gmask > .5, iterations=2) & ~(gmask > .5)
    img = img * (1 - gmask[..., None]) + grass * gmask[..., None]
    img[rimg] *= .86
    # streets
    rf = np.array(RD.filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(14))).astype(np.float32) / 255.
    rf = np.clip(rf + (wang.vnoise(gh, gw, 40, SEED + 20) - .5) * .34 + (wang.vnoise(gh, gw, 11, SEED + 22) - .5) * .12, 0, 1)
    lf = np.array(LD.filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(7))).astype(np.float32) / 255.
    lf = np.clip(lf + (wang.vnoise(gh, gw, 30, SEED + 21) - .5) * .25, 0, 1)
    img = cobble.render(img, rf, plaza=(PLAZA[0] * G, PLAZA[1] * G), plaza_r=PLAZA[2] * G - 6, seed=SEED, lane=lf, stone=(100, 92, 81))
    bandm = ndimage.gaussian_filter(np.isin(grid, ['#', 'T', 'P', 'R', 'C', 'X']).astype(float), 1.0)
    img *= 1.28 * (1 - .42 * up(bandm))[..., None] * np.array([1, 1, 1.03])
    wm = up(ndimage.gaussian_filter((V == 0).astype(float), .8)) if False else None
    gimg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    gp = FA + 'ground3.png'; gimg.save(rel(gp), optimize=True)
    # ---- hd block ----
    def arts(keys): return [{'img': FF + k + '.png', 'ax': props.OLD[k][1], 'ay': props.OLD[k][2]} for k in keys]
    oakA = [{'img': v['img'], 'ax': v['ax'], 'ay': v['ay'], 'D': 2.25, 'sway': 1} for v in A['oak'][:4]]
    decoArt = {'T': arts(['ash_tree_a', 'ash_tree_b']) + oakA, 'P': arts(['burnt_pine_a', 'burnt_pine_b']), 'R': arts(['boulder']),
               'u': arts(['ash_bush', 'bush_b']), 'w': arts(['dry_reeds']), 's': arts(['stump', 'stone_low', 'stump', 'pale_mushrooms', 'stone_low']),
               'C': arts(['burnt_pine_a', 'burnt_pine_b', 'dead_tree'])}
    for d in decoArt['T'] + decoArt['P']: d['sway'] = 1
    decoArt['w'][0]['sway'] = 3; decoArt['u'][0]['sway'] = .5; decoArt['u'][1]['sway'] = .5
    dw = ndimage.distance_transform_edt(grid != '~'); taken = {(o['x'], o['y']) for o in objs}
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if grid[y, x] != '.' or (x, y) in taken: continue
            if dw[y, x] <= 1.5 and rnd.random() < .25: grid[y, x] = 'w'
            elif dw[y, x] > 2 and not np.isin(grid[y-1:y+2, x-1:x+2], ['=', 'H']).any() and rnd.random() < .03: grid[y, x] = rnd.choice('su')
    free = np.vectorize(lambda c: c not in SOL | {'u'})(grid); free2 = free.copy()
    for o in objs:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'door'): free2[o['y'], o['x']] = False
    r3 = bfs(free2, sx, sy); print('  after scatter reach', int(r3.sum()), 'lost', int((r2 & ~r3).sum()))
    wruns = []
    for y in range(H):
        x = 0
        while x < W:
            if grid[y, x] == '~' or (y, x) in {(b, a) for a, b in bridge}:
                x0 = x
                while x < W and (grid[y, x] == '~' or (x, y) in bridge): x += 1
                wruns.append([y, x0, x - 1])
            x += 1
    gcell = np.array(Image.fromarray((gmask * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)) > 100
    tufts = []
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if grid[y, x] != '.': continue
            pr = .55 if gcell[y, x] else .12
            for _ in range(2 if gcell[y, x] else 1):
                if rnd.random() < pr: tufts.append([round(x + rnd.random(), 2), round(y + .3 + rnd.random() * .7, 2), rnd.randrange(3) if gcell[y, x] else (3 if rnd.random() < .3 else rnd.randrange(3))])
    allp = props_ + small
    lights = []; fires = []
    for q in small:
        n = os.path.basename(q['img'])[:-4]
        if n == 'brazier': lights.append([q['x'], q['y'] - .9, 62, '#ff8a3a', 1]); fires.append([q['x'], q['y'] - 1.05, 1.0])
        if n == 'lamp': lights.append([q['x'], q['y'] - 1.2, 50, '#ffb060', .85]); fires.append([q['x'], q['y'] - 1.25, .45])
        if n == 'candelabra': lights.append([q['x'], q['y'] - 1.6, 30, '#ffc070', .7]); fires.append([q['x'], q['y'] - 2.05, .3])
    # castle windows: warm glow where the art has lit windows
    ca = np.array(Image.open(rel(cas['img'])).convert('RGBA')).astype(int)
    lit = (ca[..., 0] > 170) & (ca[..., 1] > 90) & (ca[..., 2] < 110) & (ca[..., 0] - ca[..., 2] > 90) & (ca[..., 3] > 0)
    lab, n = ndimage.label(ndimage.binary_dilation(lit, iterations=3)); pts = ndimage.center_of_mass(lit, lab, range(1, n + 1))
    sz = ndimage.sum(lit, lab, range(1, n + 1)); pts = [p for p, s in sorted(zip(pts, sz), key=lambda t: -t[1])[:18]]
    for py, px in pts:
        lights.append([round(cx0 + (px - cas['ax']) / CD / T, 2), round(cfy - (cas['ay'] - py) / CD / T, 2), 26, '#ffb860', .75])
    gate = [cx0, cfy - .8]; lights.append([gate[0], gate[1], 60, '#ff9a40', .9])
    for q in props_:
        if q['id'] == 'se_house':
            fxp = q['x'] + (210 - q['ax']) / q['D'] / T; fyp = q['y'] - (q['ay'] - 262) / q['D'] / T
            lights.append([fxp, fyp, 80, '#ff7a2a', 1]); fires.append([fxp, fyp, 1.5, 'forge'])
        if q['id'] == 'inn': lights.append([q['x'] - 2, q['y'] - 2, 64, '#ffb060', .85])
    smoke = []
    for q in props_:
        off = {'se_house': (-1.6, -6.9), 's_house': (-.2, -6.4), 'bl_house': (1.9, -4.6), 'inn': (2.2, -7.6)}.get(q['id'])
        if off: smoke.append([q['x'] + off[0] * 3 / q['D'], q['y'] + off[1] * 3 / q['D'], 1])
    fount = None
    for q in props_:
        if q['id'] == 'fountain':
            fount = {'x': q['x'], 'y': q['y'], 'ax': q['ax'], 'ay': q['ay'], 'D': q['D'], 'streams': [[86, 214, 262], [102, 222, 270], [124, 228, 276], [170, 228, 276], [192, 222, 270], [206, 214, 262]],
                     'pool': [146, 262, 112, 42], 'rim': [146, 206, 62, 14]}
    hd = {'D': 3, 'ground': gp, 'props': allp, 'decoArt': decoArt, 'lights': lights, 'smoke': smoke, 'grade': 'dusk', 'water': wruns, 'tufts': tufts,
          'fires': fires, 'fountains': [fount], 'fx': {'particles': 'ash', 'birds': 3, 'butterflies': 3, 'tuft': ['#5b5a44', '#6a6a4c', '#4a4b38'], 'water': 'moat'},
          'webs': [[78.2, 57.6, 80.6, 59.2, .5, .3], [77.0, 59.5, 79.5, 60.2, .6, .3], [80.0, 56.5, 81.8, 58.6, .4, .25]]}
    legend = {'.': 'dirt', '=': 'dirt', '~': 'water', '#': 'cliff', 'X': 'cliff', 'C': {'ground': 'cliff', 'deco': 'pine'}, 'H': {'ground': 'dirt', 'solid': True},
              'T': {'ground': 'dirt', 'deco': 'tree'}, 'P': {'ground': 'dirt', 'deco': 'pine'}, 'R': {'ground': 'dirt', 'deco': 'boulder'},
              'u': {'ground': 'dirt', 'deco': 'bush'}, 's': {'ground': 'dirt', 'deco': 'stump', 'solid': False}, 'w': {'ground': 'dirt', 'deco': 'mushrooms', 'solid': False}}
    out = {k: ORIG[k] for k in ('type', 'area', 'title', 'bgm', 'battleBgm', 'tileset', 'tile', 'id', 'name')}
    cur = json.load(open(rel('maps/felt.json')))
    out['title'] = dict(out['title'], sub='잿빛 왕성 아래의 마을')
    out.update({'region': ORIG['region'], 'w': W, 'h': H, 'legend': legend, 'solid': ['#', 'C', 'X', 'H', 'T', 'P', 'R', 'u', '~'],
                'ground': [''.join(r) for r in grid], 'objects': objs, 'spawns': spawns, 'hd': hd,
                'note': 'GENERATED by tools/hd/fields/build_felt3.py (organic village v3: castle north, moat + bridge, clustered rows, round plaza) - do not hand-edit'})
    if 'mapPos' in cur: out['mapPos'] = cur['mapPos']
    json.dump(out, open(rel('maps/felt.json'), 'w'), ensure_ascii=False, indent=1)
    return out
if __name__ == '__main__':
    main()
