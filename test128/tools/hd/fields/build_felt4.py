"""Felt v4 (owner 10-25: rebuild FELT on Claude's ch1 draft, docs_maps/ch1/ch1_zone_felt.png + ch1_map.json zone 'felt').
- 150x120 tiles. No castle / moat inside the town: a colossal ruined OLD CITY GATE ARCH + broken curtain walls fill the north band,
  the king's castle + inner wall only as a far, fogged parallax strip behind it.
- draft layout (local = draft abs - (440, 330), y squeezed under the north band): west gate (펠트 서문) + Gas's post (arrival from the field),
  north gate '1장 정문' (exit), Luca's campfire in the centre (save point, tall smoke column), four blocks NW 이장 / NE 여관 / SW 리네트 /
  SE 고물상 거리 (중고 무기점 + 잡화점), Ben's wagon on the east edge, Toby's shack in the south.
- outskirts additions kept from v3 (flagged): 롬's forge (wide yard), chapel + graves, 세라's herb hut, the Arachne gate, the empty house.
- light / fire / smoke / ash / mist are drawn in code (draft art rule), not baked into art.
- ground at 24 px per cell (hd D=1.5): 3600x2880, under the phone canvas limit; every prop carries its own D.
Usage: python3 build_felt4.py -> maps/felt.json (+ assets/world/felt/{ground4,g4_*}.png)"""
import json, os, sys, math, random, copy, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wang, props, cobble
from build import crom, disk, bfs, SETS
import build_felt2 as F2
ROOT = props.ROOT; FA = F2.FA; FF = F2.FF; T = 16
W, H = 150, 120; SEED = 11; HD = 1.5; G = int(T * HD)      # ground px per cell
WALL_Y = 26; GATE_X = 75.5
ORIG = F2.ORIG; DOORS = F2.DOORS
def P(name):  # parts.json art; falls back to the field_felt_hd copy when the felt/ file is missing (ruin_pillar)
    v = F2.P(name)
    if not os.path.exists(rel(v['img'])) and name in props.OLD:
        o = props.OLD[name]; v = dict(v, img=o[0], ax=o[1], ay=o[2])
    return v
GI = '/tmp/plwork/out/gi'
def rel(p): return os.path.join(ROOT, p)
def art(path):
    im = Image.open(rel(path)); ax, ay = props.anchor(im); return {'img': path, 'ax': ax, 'ay': ay, 'w': im.width, 'h': im.height}
def save_art(a, name):
    d = FA + name + '.png'; Image.fromarray(a.astype(np.uint8)).save(rel(d), optimize=True); return d
def char_ruin(src, name, cut, seed):
    """a burnt-out shell of a town house: charred, desaturated, roof gone above a jagged line"""
    im = Image.open(rel(src)).convert('RGBA'); a = np.array(im).astype(float); h, w = a.shape[:2]; r = np.random.RandomState(seed)
    a = props._grade(a, .4, (1.0, .96, .92), .72)
    soot = ndimage.gaussian_filter(r.rand(h, w), 3); soot = (soot - soot.min()) / (np.ptp(soot) + 1e-6)
    yy = np.mgrid[0:h, 0:w][0] / h; k = np.clip(1.2 - yy * 1.1 + (soot - .5), .25, 1)[..., None]
    a[..., :3] *= (1 - .4 * k)
    xs = np.arange(w); line = cut * h + ndimage.gaussian_filter1d(r.rand(w) * h * .22, 4) + 18 * np.sin(xs / 23 + seed)
    for x in range(w): a[:int(max(0, line[x])), x, 3] = 0
    edge = np.zeros((h, w), bool)
    for x in range(w):
        y0 = int(max(0, line[x])); edge[y0:y0 + 6, x] = True
    a[edge & (a[..., 3] > 0), :3] *= .6
    a[..., 3] = np.where(a[..., 3] < 40, 0, 255)
    return art(save_art(np.clip(a, 0, 255), name))
def prep_assets():
    A = {}
    def gi(n, out, sat=.8, warm=(1.0, .98, .95), gain=.95):
        s = f'{GI}/{n}.png'; d = FA + out + '.png'
        if os.path.exists(s) and Image.open(s).width > 8:
            im = Image.open(s).convert('RGBA'); im = im.crop(im.getbbox()); a = np.array(im).astype(float)
            a[..., 3] = np.where(a[..., 3] < 40, 0, 255); a = props._grade(a, sat, warm, gain); Image.fromarray(a.astype(np.uint8)).save(rel(d), optimize=True)
        return art(d) if os.path.exists(rel(d)) else None
    A['arch'] = gi('gate_arch_0', 'g4_gate_arch', .78, (1.0, .98, .96), .92)
    A['wall'] = gi('gate_wall_0', 'g4_gate_wall', .78, (1.0, .98, .96), .9)
    A['dtree'] = [v for v in (gi(f'r5_deadtree_{i}', f'g4_deadtree_{i}', .7) for i in range(4)) if v]
    A['debris'] = [v for v in (gi(f'r5_debris_{i}', f'g4_debris_{i}', .75) for i in range(4)) if v]
    A['shack'] = gi('r5_shack_1', 'g4_shack', .8)
    A['firepit'] = gi('r5_firepit_1', 'g4_firepit', .8)
    # far king's castle + inner wall: the old castle painting, fogged to a cold silhouette, wall segments repeated out to 2x screen width
    s = f'{GI}/castle_grand_b_0.png'; d = FA + 'g4_far_castle.png'
    if os.path.exists(s):
        c = Image.open(s).convert('RGBA'); c = c.crop(c.getbbox()); cw, ch = c.size
        seg = c.crop((int(cw * .62), int(ch * .42), int(cw * .84), ch))                    # a plain wall run between towers
        Wd = 2600; strip = Image.new('RGBA', (Wd, ch), (0, 0, 0, 0))
        x = 0
        while x < Wd:
            strip.alpha_composite(seg, (x, ch - seg.height)); x += seg.width - 2
        strip.alpha_composite(c, ((Wd - cw) // 2, 0))
        a = np.array(strip).astype(float); fog = np.array([96, 94, 104.])
        l = (a[..., :3] * [.3, .59, .11]).sum(-1, keepdims=True); rgb = l * .75 + 10
        yy = np.mgrid[0:a.shape[0], 0:a.shape[1]][0][..., None] / a.shape[0]
        mix = .4 + .3 * yy                                                                  # foot fades into the mist
        a[..., :3] = rgb * (1 - mix) + fog * mix; a[..., 3] = np.where(a[..., 3] < 40, 0, 255)
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(rel(d), optimize=True)
    A['far'] = art(d) if os.path.exists(rel(d)) else None
    A['ruins'] = [char_ruin(FA + 'west_a.png', 'g4_ruin_a', .38, 1), char_ruin(FA + 'sw_house.png', 'g4_ruin_b', .45, 2),
                  char_ruin(FA + 's_house.png', 'g4_ruin_c', .5, 3), char_ruin(FA + 'e_row.png', 'g4_ruin_d', .42, 4)]
    A['g2'] = {n: art(FA + n + '.png') for n in ('g2_refugee_tent_a', 'g2_refugee_tent_b', 'g2_refugee_tent_d', 'g2_refugee_tent_crest_a', 'g2_ration_tent',
               'g2_memorial_wall_day', 'g2_burnt_stump_a', 'g2_burnt_stump_b', 'g2_burnt_stump_c', 'g2_charred_cart_b', 'g2_rope_barrier', 'g2_sign_gate_sunset',
               'g2_thread_clump_1', 'g2_thread_clump_3', 'g2_thread_pile_1', 'g2_thread_pile_2', 'g2_ash_decal_a', 'g2_ash_decal_b', 'g2_ash_decal_c')}
    A['g2']['g2_laundry_line_strip'] = {'img': FA + 'g2_laundry_line_strip.png', 'ax': 53.5, 'ay': 82, 'strip': [4, 180, 1]}
    A['g2']['g2_ribbon_tree_strip'] = {'img': FA + 'g2_ribbon_tree_strip.png', 'ax': 113.0, 'ay': 203, 'strip': [4, 200, 0]}
    for n in ('f3_banner_0', 'f3_banner_2', 'f3_hay_1', 'f3_goods_0', 'f3_goods_2', 'f3_garden_2', 'f3_sign_weapon_sword', 'f3_sign_tool_hammer_bag', 'f3_sign_herb_leaf'):
        A[n] = art(FA + n + '.png')
    return A
# (key, art, x, foot y, D) — draft blocks: NW 이장 (40,32)->(40,50) · NE 여관 (100,32)->(100,51) · SW 리네트 (50,85)->(47,95) · SE 고물 수리점 (110,85)->(101..116,95)
BUILD = [
 ('chief', 's_house', 40, 50, 2.25), ('empty', 'sw_house', 57, 47, 2.25),
 ('inn', 'inn', 100, 51, 2.25), ('herb', 'e_row', 119, 49, 2.25),
 ('atelier', 'linette', 47, 95, 2.25),
 ('weapon', 'west_b', 101, 97, 2.25), ('tool', 'bl_house', 116, 94, 2.25),
 ('forge', 'se_house', 19, 106, 2.25), ('chapel', 'chapel', 136, 40, 1.4),
 ('guard', 'watchtower', 8, 64, 1.5), ('arachne', 'web_arch', 12, 47, 2.5), ('stall2', 'stall_n', 139, 92, 3),
]
DOORART = {'atelier': (238, 265, 46, 70), 'tool': (106, 218, 40, 75), 'weapon': (92, 388, 40, 72), 'chief': (136, 300, 54, 100), 'forge': (60, 300, 44, 82),
           'inn': (176, 343, 48, 80), 'herb': (110, 300, 44, 75), 'chapel': (62, 200, 40, 55), 'empty': (175, 345, 44, 90)}
RUINS = [(27, 41, 0), (24, 56, 1), (68, 46, 3), (88, 42, 2), (129, 62, 0), (112, 65, 3), (25, 86, 2), (63, 104, 1), (90, 111, 0), (131, 80, 1), (140, 108, 3), (58, 84, 0)]
CAMP = (75.5, 71.0)
def main():
    A = prep_assets(); rnd = random.Random(SEED)
    yy, xx = np.mgrid[0:H, 0:W]
    de = np.minimum(np.minimum(xx, W - 1 - xx), H - 1 - yy).astype(float)
    S = de < 1.8 + 3.0 * wang.vnoise(H, W, 7, SEED)                   # ruin / dead-wood border (no fence)
    S[66:75, :9] = False                                               # west gate gap
    X = np.zeros((H, W), bool); X[:WALL_Y, :] = True                 # north band: the old gate + walls (scenery, solid)
    Hs = np.zeros((H, W), bool); road = np.zeros((H, W), bool); clear = np.zeros((H, W), bool); lanec = np.zeros((H, W), bool)
    RD = Image.new('L', (W * G, H * G), 0); LD = Image.new('L', (W * G, H * G), 0); dR = ImageDraw.Draw(RD); dL = ImageDraw.Draw(LD)
    def lay(pts, r, kind='road', c=None):
        rr = r if isinstance(r, (list, tuple)) else [r] * len(pts)
        sp_ = crom(pts); n = len(sp_)
        for i, p in enumerate(sp_):
            f = i / max(1, n - 1) * (len(rr) - 1); j = min(int(f), len(rr) - 2) if len(rr) > 1 else 0
            ri = rr[j] + (rr[j + 1] - rr[j]) * (f - j) if len(rr) > 1 else rr[0]
            if not (-1 <= p[0] < W + 1 and 0 <= p[1] < H + 1): continue
            disk(road if kind == 'road' else lanec, p[0], p[1], ri); disk(clear, p[0], p[1], (c or ri + 1.2))
            dd = dR if kind == 'road' else dL; R = ri * G * (1.12 if kind == 'road' else 1.0)
            dd.ellipse([p[0] * G - R, p[1] * G - R, p[0] * G + R, p[1] * G + R], fill=255)
    # ---- roads: broken cobble (the old capital streets) + packed-earth paths, all bending ----
    lay([(GATE_X, 24), (75, 29), (72.6, 35), (74.8, 42), (78.2, 50), (76.4, 57), (74.6, 64)], [2.4, 2.4, 1.7, 1.4, 1.6, 1.3, 1.6])          # 1장 정문 -> campfire
    lay([(-1, 70.5), (6, 70.8), (14, 69.2), (22, 71.6), (32, 73.2), (42, 70.4), (52, 72.4), (61, 70.6), (68, 71.2)], [1.9, 1.9, 1.5, 1.3, 1.45, 1.2, 1.4, 1.25, 1.5])  # 서문 -> campfire
    lay([(83, 71.2), (92, 73.4), (103, 71.0), (114, 74.2), (125, 72.0), (133, 76.0), (138.5, 83), (139.5, 89)], [1.5, 1.3, 1.45, 1.2, 1.35, 1.15, 1.1, 1.0])  # east -> Ben
    lay([(75.6, 77.5), (77.6, 84), (73.4, 91.5), (70.2, 99), (62, 105.6), (50, 109.6), (41, 112.4)], [1.5, 1.3, 1.4, 1.2, 1.25, 1.1, 1.0])  # south -> Toby
    lay([(34, 72.6), (35.6, 65), (40.8, 58.4), (42.6, 53.5)], [1.2, 1.0, 1.1, 1.0])                                                          # NW block
    lay([(77.8, 51), (86, 55.2), (95, 54.6), (104, 56.4), (113, 54.2), (121, 53.4)], [1.2, 1.0, 1.15, 1.0, 1.05, .95])                         # NE block
    lay([(103, 71.5), (106.4, 79), (107.6, 87), (110, 98.5)], [1.15, 1.0, 1.1, 1.0])                                                          # SE block
    lay([(73.4, 91.5), (63, 95.6), (54, 99.4)], [1.1, 1.0, .95])                                                                              # SW block
    lay([(58, 71.8), (59, 63), (57.5, 52)], [.9, .85, .85], 'lane')                                                                           # empty house
    lay([(22, 72), (25.4, 81), (23.2, 91), (24.6, 100), (27, 107)], [.95, .9, .9, .9, .9], 'lane')                                              # forge (outskirts)
    lay([(121, 53.4), (128, 48.6), (134, 44.2)], [.9, .85, .8], 'lane')                                                                       # chapel (outskirts)
    lay([(14, 69.2), (13.4, 61), (12.4, 52.5)], [.9, .85, .8], 'lane')                                                                        # arachne gate
    lay([(41, 112.4), (37.4, 114.6)], .9, 'lane')
    disk(lanec, CAMP[0], CAMP[1], 7.2); disk(clear, CAMP[0], CAMP[1], 8.5)
    R = 7.2 * G; dL.ellipse([CAMP[0] * G - R, CAMP[1] * G - R, CAMP[0] * G + R, CAMP[1] * G + R], fill=255)
    for x0, y0, x1 in ((62, 27, 89),):                                                                                                         # gate apron (rubble-strewn)
        disk(road, GATE_X, 28.5, 5.5); disk(clear, GATE_X, 28.5, 7)
        dR.ellipse([(GATE_X - 5.5) * G, (28.5 - 4.2) * G, (GATE_X + 5.5) * G, (28.5 + 4.2) * G], fill=255)
    # ---- buildings ----
    props_ = []; doors = []; spawns = {}
    for key, an, x, y, Dq in BUILD:
        v = P(an); wc = v['w'] / Dq / T
        dep = {'guard': 2, 'stall2': 2, 'arachne': 3, 'chapel': 4}.get(key, 5 if v['w'] > 300 else 4)
        x0 = int(round(x - wc * .43)); x1 = int(round(x + wc * .43)); Hs[y - dep:y, x0:x1] = True
        q = {'id': an, 'img': v['img'], 'x': x, 'y': y, 'ax': v['ax'], 'ay': v['ay'], 'D': Dq, 'fade': 1, 'shadow': 0}
        if key in DOORART:
            cx, by, dw, dh = DOORART[key]; dx = int(math.floor(x + (cx - v['ax']) / Dq / T)); dy = y - 1
            d = DOORS[key]; doors.append((key, dx, dy, d))
            im = np.array(Image.open(rel(v['img'])).convert('RGB')).astype(float)
            reg = im[int(by - dh * .9):int(by - dh * .1), int(cx - dw * .3):int(cx + dw * .3)].reshape(-1, 3)
            q['door'] = {'id': d['id'], 'cx': cx, 'by': by, 'w': dw, 'h': dh, 'col': [int(c) for c in np.median(reg, 0)]}
        props_.append(q)
    for x, y, i in RUINS:                                                                                                                      # burnt-out shells
        v = A['ruins'][i]; Dq = 2.25; wc = v['w'] / Dq / T; x0 = int(round(x - wc * .43)); x1 = int(round(x + wc * .43)); Hs[y - 4:y, x0:x1] = True
        props_.append({'id': f'ruin_{x}_{y}', 'img': v['img'], 'x': x, 'y': y, 'ax': v['ax'], 'ay': v['ay'], 'D': Dq, 'fade': 1, 'shadow': 0, 'flip': (x + y) % 2 == 1})
    for key, dx, dy, d in doors:
        m = road | lanec; dist, ind = ndimage.distance_transform_edt(~m, return_indices=True)
        ty_, tx_ = ind[0][dy + 2, dx], ind[1][dy + 2, dx]
        kind = 'lane' if key in ('forge', 'chapel', 'empty', 'herb') else 'road'
        lay([(dx + .5, dy + 1.2), (dx + .5, dy + 2.0), ((dx + tx_) / 2 + .5, (dy + 2 + ty_) / 2 + .5), (tx_ + .5, ty_ + .5)], .85 if kind == 'road' else .75, kind, 1.4)
    S &= ~clear
    # ---- north band: far castle strip (parallax), the gate arch, broken walls on both sides ----
    back = []
    if A['far']:
        f = A['far']; back.append({'id': 'far_castle', 'img': f['img'], 'x': GATE_X, 'y': 15.0, 'ax': f['w'] // 2, 'ay': f['h'] - 1, 'D': 1.6, 'fade': 0, 'shadow': 0, 'par': .35})
    AD = 1.1; arch = A['arch']; awt = arch['w'] / AD / T if arch else 0
    if A['wall']:
        wv = A['wall']; WD = 1.1; ww = wv['w'] / WD / T; xs = []
        x = GATE_X - awt * .42 - ww * .42
        while x + ww / 2 > 0: xs.append(x); x -= ww * .82
        x = GATE_X + awt * .42 + ww * .42
        while x - ww / 2 < W: xs.append(x); x += ww * .82
        for i, x in enumerate(sorted(xs, key=lambda t: -abs(t - GATE_X))):
            back.append({'id': f'gate_wall_{i}', 'img': wv['img'], 'x': round(x, 2), 'y': WALL_Y - .4 + (i % 2) * .6, 'ax': wv['ax'], 'ay': wv['ay'], 'D': WD, 'fade': 0, 'shadow': 0, 'flip': x > GATE_X})
    if arch:
        back.append({'id': 'gate_arch', 'img': arch['img'], 'x': GATE_X + ARCH_DX, 'y': WALL_Y + .6, 'ax': arch['ax'], 'ay': arch['ay'], 'D': AD, 'fade': 0, 'shadow': 0})
    # ---- small props ----
    small = []
    def sp(an, x, y, solid=True, D=3, flip=False, v=None, **kw):
        v = v or P(an)
        q = dict({'id': f'{os.path.basename(v["img"])[:-4]}_{len(small)}', 'img': v['img'], 'x': round(x, 2), 'y': round(y, 2), 'ax': v['ax'], 'ay': v['ay'], 'D': D, 'fade': 0, 'shadow': 1, 'flip': flip}, **kw)
        if v.get('strip'): q['strip'] = v['strip']; q['shadow'] = 0
        small.append(q)
        if solid: Hs[int(y - .6), int(x)] = True
        return q
    g2 = A['g2']
    def tree(x, y):
        k = rnd.random()
        if A['dtree'] and k < .5: v = rnd.choice(A['dtree']); sp(None, x, y, True, 2.4, flip=rnd.random() < .5, v=v, sway=.4)
        else:
            o = props.OLD[rnd.choice(['dead_tree', 'burnt_pine_a', 'burnt_pine_b', 'ash_tree_b'])]; sp(None, x, y, True, 3, flip=rnd.random() < .5, v={'img': o[0], 'ax': o[1], 'ay': o[2]}, sway=.6)
    def deb(x, y, D=2.6):
        if A['debris'] and rnd.random() < .6: sp(None, x, y, True, D, flip=rnd.random() < .5, v=rnd.choice(A['debris']))
        else: sp(rnd.choice(['rubble', 'ember_rubble', 'stone_low', 'ruin_pillar']), x, y, True, 3, flip=rnd.random() < .5)
    # gate apron: rubble heaps at the wall foot, torn banners, two braziers, chained-off breach
    for x, y in ((63.5, 28.2), (68.2, 27.4), (83.0, 27.6), (87.6, 28.4), (58.2, 27.6), (93.0, 27.5), (50, 27.6), (101, 27.8), (40, 27.4), (112, 27.6), (28, 28), (124, 27.6), (16, 27.8), (136, 28)):
        deb(x, y)
    for x in (70.0, 81.0): sp('brazier', x, 30.6)
    sp(None, 66.6, 31.6, True, 2.4, v=A['f3_banner_0'], sway=.6); sp(None, 84.4, 31.6, True, 2.4, v=A['f3_banner_2'], sway=.6, flip=True)
    sp(None, 92.0, 30.8, True, 3, v=g2['g2_rope_barrier'])
    # west gate (펠트 서문): two broken pillars, braziers, Gas's watchtower, sign
    sp('ruin_pillar', 4.6, 67.0); sp('ruin_pillar', 4.6, 75.2); sp('brazier', 6.6, 67.4); sp('brazier', 6.6, 75.4)
    deb(2.4, 65.4); deb(2.6, 77.0); sp('barrels', 11.6, 65.6); sp('crates', 4.4, 62.4)
    # Luca's campfire + survivors' camp around it
    if A['firepit']: sp(None, CAMP[0], CAMP[1] + .9, True, 2.2, v=A['firepit'], shadow=0)
    for x, y, n in ((66.6, 64.6, 'g2_refugee_tent_a'), (85.4, 64.2, 'g2_refugee_tent_b'), (65.0, 78.6, 'g2_refugee_tent_d'), (86.6, 79.4, 'g2_refugee_tent_crest_a')):
        sp(None, x, y, True, 2.6, v=g2[n], fade=1)
    sp(None, 81.6, 59.6, True, 2.8, v=g2['g2_ration_tent'], fade=1); Hs[58:60, 80:84] = True
    sp(None, 62.0, 60.6, True, 2.8, v=g2['g2_memorial_wall_day'], fade=1); Hs[59:61, 60:64] = True
    sp(None, 90.6, 73.0, False, 3, v=g2['g2_laundry_line_strip'])
    sp(None, 70.4, 83.6, True, 3, v=g2['g2_ribbon_tree_strip'], fade=1)
    sp('bench', 71.4, 74.2); sp('bench', 80.0, 74.4, flip=True); sp('woodpile', 82.6, 68.0); sp('crates', 68.4, 67.6); sp('barrels', 88.6, 67.6)
    sp(None, 79.4, 81.0, True, 2.6, v=A['f3_hay_1'])
    # NW / NE blocks
    sp('cart', 48.6, 53.6); sp('woodpile', 33.0, 52.6); sp('barrels', 47.4, 47.0); sp(None, 31.4, 47.6, True, 2.6, v=A['f3_garden_2'])
    sp('barrels', 93.4, 50.6); sp('crates', 106.6, 52.0); sp('herb_rack', 124.4, 50.2); sp(None, 115.6, 52.2, False, 3, v=A['f3_sign_herb_leaf'], shadow=0)
    # SE 고물상 거리: junk heaps, charred cart, signs
    sp(None, 96.6, 99.8, False, 3, v=A['f3_sign_weapon_sword'], shadow=0); sp(None, 112.0, 96.8, False, 3, v=A['f3_sign_tool_hammer_bag'], shadow=0)
    sp(None, 121.4, 96.4, True, 2.6, v=g2['g2_charred_cart_b']); sp('crates', 107.2, 93.2); sp('barrels', 120.6, 91.6); deb(124.6, 99.6); sp(None, 105.6, 100.6, True, 2.6, v=A['f3_goods_2'])
    # SW: Linette's yard
    sp('crates', 53.6, 92.6); sp(None, 40.4, 96.6, True, 2.6, v=A['f3_goods_0'])
    # forge yard (outskirts, wide): anvil, quench barrels, woodpile, ore heap
    sp('anvil', 27.6, 106.4); sp('anvil', 29.8, 103.6, flip=True); sp('woodpile', 11.6, 104.2); sp('barrels', 31.6, 108.2); sp('crates', 12.2, 108.4); deb(33.6, 102.0, 2.8)
    # Ben's wagon (east edge)
    sp('cart', 143.0, 95.6, True, 2.2); sp(None, 135.6, 95.2, True, 2.6, v=A['f3_goods_2']); sp('barrels', 142.6, 90.2)
    # Toby's shack (south, quiet)
    if A['shack']: sp(None, 36.0, 113.0, True, 2.1, v=A['shack'], fade=1); Hs[110:113, 34:39] = True
    sp('woodpile', 31.6, 113.4); sp('crates', 40.8, 110.6)
    # chapel + graves (NE outskirts)
    sp('candelabra', 133.0, 41.4); sp('mausoleum', 143.2, 40.0); sp('tombs', 140.6, 45.6); sp('tombs', 131.4, 36.6, flip=True); sp('tombs', 142.6, 35.4)
    # arachne gate: thread stakes, thread clumps
    for x, y in ((9.0, 52.0), (16.4, 50.6), (8.0, 44.0)):
        o = props.OLD['thread_stake']; sp(None, x, y, True, 3, v={'img': o[0], 'ax': o[1], 'ay': o[2]})
    for x, y, n in ((15.0, 54.6, 'g2_thread_clump_1'), (10.0, 55.4, 'g2_thread_pile_1'), (17.6, 46.6, 'g2_thread_clump_3'), (7.6, 49.6, 'g2_thread_pile_2')):
        sp(None, x, y, False, 3, v=g2[n], shadow=0)
    # burnt stumps / ash decals / debris sprinkled through the burnt district
    for _ in range(26):
        for _t in range(30):
            x = rnd.uniform(8, W - 8); y = rnd.uniform(WALL_Y + 4, H - 6); cx_, cy_ = int(x), int(y - .6)
            if not (road | lanec | Hs | S)[cy_ - 1:cy_ + 2, cx_ - 1:cx_ + 2].any() and math.hypot(x - CAMP[0], y - CAMP[1]) > 10:
                if rnd.random() < .5: sp(None, x, y, True, 2.6, v=g2[rnd.choice(['g2_burnt_stump_a', 'g2_burnt_stump_b', 'g2_burnt_stump_c'])])
                else: deb(x, y)
                break
    under = []
    for _ in range(40):
        x = rnd.uniform(6, W - 6); y = rnd.uniform(WALL_Y + 3, H - 4); v = g2[rnd.choice(['g2_ash_decal_a', 'g2_ash_decal_b', 'g2_ash_decal_c'])]
        if math.hypot(x - CAMP[0], y - CAMP[1]) > 9 and not (road | lanec)[max(0, int(y) - 2):int(y) + 2, max(0, int(x) - 2):int(x) + 3].any():
            under.append({'id': f'ash_{len(under)}', 'img': v['img'], 'x': round(x, 2), 'y': round(y, 2), 'ax': v['ax'], 'ay': v['ay'], 'D': rnd.choice([2.2, 2.6, 3]), 'under': 1, 'fade': 0, 'shadow': 0, 'flip': rnd.random() < .5})
    # dead-wood groves between the blocks
    groves = [(20, 33, 3), (52, 34, 2), (100, 34, 3), (120, 34, 2), (30, 62, 2), (50, 60, 2), (92, 62, 2), (118, 80, 2), (86, 92, 2), (60, 114, 3), (100, 114, 2),
              (126, 112, 2), (10, 88, 2), (138, 66, 2), (140, 52, 2), (34, 92, 2), (66, 92, 1), (96, 84, 1), (46, 82, 2), (128, 92, 1)]
    for gx, gy, n in groves:
        for i in range(n):
            for _ in range(20):
                x = gx + rnd.uniform(-2.4, 2.4); y = gy + rnd.uniform(-1.5, 1.5); cx_, cy_ = int(x), int(y - .6)
                if 0 < cx_ < W - 1 and WALL_Y < cy_ < H - 1 and not (road | lanec | Hs)[cy_ - 1:cy_ + 2, cx_ - 1:cx_ + 2].any():
                    tree(x, y); break
    # ---- grid ----
    grid = np.full((H, W), '.', dtype='<U1')
    grid[road | lanec] = '='; grid[S] = '#'; grid[X] = 'X'; grid[Hs] = 'H'
    for x in range(int(GATE_X - 2.5), int(GATE_X + 2.5)):
        for y in range(WALL_Y - 2, WALL_Y): grid[y, x] = '='                                                    # the gate passage (into the arch shadow)
    objs = []; DO = {o.get('id'): o for o in ORIG['objects'] if o['type'] == 'door'}
    for key, dx, dy, d in doors:
        grid[dy, dx] = 'H'; grid[dy + 1, dx] = '='
        o = {'type': 'door', 'id': d['id'], 'x': dx, 'y': dy, 'name': d['name']}
        if d.get('to'): o.update(to=d['to'], spawn='door', out=d['out']); spawns[d['out']] = [dx + .5, dy + 1.9, 'down']
        if d.get('text'): o['text'] = d['text']
        old = DO.get(d['id'])
        if old and old.get('scene'): o['scene'] = old['scene']
        objs.append(o)
    ag = (12, 46); objs.append(dict(DO['f_arachne_gate'], x=ag[0], y=ag[1])); grid[ag[1], ag[0]] = 'H'; grid[ag[1] + 1, ag[0]] = '='; spawns['arachne'] = [ag[0] + .5, ag[1] + 2.2, 'down']
    objs.append(dict(DO['f_door_guard'], x=8, y=63)); grid[63, 8] = 'H'; grid[64, 8] = '='
    gx0 = int(GATE_X - 2.5)
    objs.append({'type': 'exit', 'x': gx0, 'y': WALL_Y - 2, 'w': 5, 'h': 1, 'to': 'field_felt', 'spawn': 'felt', 'label': '↑ 1장 정문'})
    objs.append({'type': 'exit', 'x': 0, 'y': 68, 'w': 1, 'h': 5, 'to': 'field_felt', 'spawn': 'felt', 'label': '← 펠트 서문 · 잿빛 들판'})
    grid[67:74, 0:3] = '='
    spawns.update({'default': [75.5, 78.6, 'up'], 'world': [75.5, 78.6, 'up'], 'field': [3.6, 70.5, 'right'], 'gate': [GATE_X, WALL_Y + 1.6, 'down']})
    floor = np.isin(grid, ['.', '='])
    nb = ndimage.binary_dilation(floor, structure=np.ones((3, 3)))
    for y in range(H):
        for x in range(W):
            if grid[y, x] != '#': continue
            r = rnd.random()
            if nb[y, x]: grid[y, x] = rnd.choice('TTPRR') if r < .75 else '#'
            elif r < .5: grid[y, x] = rnd.choice('TPR')
    # ---- NPCs / objects ----
    OB = {o.get('id'): o for o in ORIG['objects']}
    def put(o, x, y):
        o = copy.deepcopy(o); o['x'] = x; o['y'] = y; o.pop('near', None); objs.append(o)
        if o['type'] != 'door' and grid[y, x] not in '.=': raise SystemExit(f'object {o.get("id")} on {grid[y, x]} at {x},{y}')
        return o
    put(OB['f_gas'], 10, 69); put(OB['f_toby'], 38, 115); put(OB['f_luca'], 79, 73)
    put(OB['f_linette'], 52, 98); put(OB['f_ben'], 137, 96)
    put(OB['ws_felt_plaza'], 70, 69); put(OB['ws_arachne'], 15, 50)
    put(OB['f_chest_plaza'], 60, 30); put(OB['f_clue_bell'], 132, 43)
    put(OB['f_hid_grave'], 144, 37); put(OB['f_hid_cart'], 144, 97)
    put(OB['f_mark_fountain'], 75, 75); put(OB['f_mark_stall'], 138, 95); put(OB['f_mark_gate'], 7, 71)
    sign = [o for o in ORIG['objects'] if o['type'] == 'sign'][0]
    s = put(sign, 13, 73)
    s['text'] = '펠트 서문\n→ 루카의 모닥불(쉼터) · 이장 집 · 여관 · 리네트 공방\n↑ 무너진 옛 성문 (1장 정문)   ↘ 고물상 거리 (중고 무기점 · 잡화점)\n↙ 롬의 대장간 (외곽)   ↖ 아라크네의 폐공방'
    put({'type': 'door', 'id': 'f_well_wish', 'name': '소원 우물', 'wish': 1, 'fortunes': ['대길 — 잃어버린 것이 돌아온다.', '길 — 오늘 산 칼은 잘 든다.', '소길 — 따뜻한 스튜 한 그릇의 운.', '평 — 실 잣는 소리에 귀 기울이지 말 것.', '흉 — 해 지기 전에 돌아갈 것.']}, 64, 72)
    grid[72, 64] = 'H'; sp('well', 64.5, 73.0, False)
    put({'type': 'sign', 'text': '〔펠트 게시판〕\n· 옛 성문 밖은 해 지기 전까지만 — 경비대\n· 약초 캐 오실 분 구함, 값 쳐 드림 — 약초꾼 세라\n· 밤에는 여관 문을 잠급니다 — 마르타\n· 들판의 굳은 사슴을 본 자는 서문 초소로'}, 85, 68)
    put({'type': 'clue', 'id': 'f_clue_gate', 'name': '무너진 옛 성문', 'flag': 'felt_look_gate', 'text': '왕도의 옛 성문. 거인도 드나들었을 법한 아치가 반쯤 무너진 채 펠트에 그늘을 드리운다.\n그을린 돌에 새겨진 문장은 이제 읽을 수 없다. 아치 아래로 성 밖 길이 이어진다.', 'textDone': '무너진 옛 성문. 아치 아래로 지나가면 성 밖 길이다.'}, 79, 29)
    put({'type': 'clue', 'id': 'f_clue_moat', 'name': '성문 잔해의 녹슨 투구', 'flag': 'felt_look_moat', 'text': '성문 잔해 사이에 녹슨 경비대 투구가 끼어 있다. 안쪽에 이름이 긁혀 있다 — 「가스」.\n…경비대장의 옛 투구일까.', 'textDone': '녹슨 투구. 안쪽의 이름은 「가스」.', 'loot': [['potion', 1]]}, 54, 29)
    put({'type': 'hidden', 'id': 'f_hid_moat', 'loot': [['riceball', 1]], 'find': '성문 잔해 틈에서 찾았다!'}, 96, 29)
    put({'type': 'hidden', 'id': 'f_hid_tower', 'loot': [['potion', 1]], 'find': '초소 뒤 돌 틈에서 찾았다!'}, 11, 62)
    put({'type': 'hidden', 'id': 'f_hid_forge', 'loot': [['riceball', 1]], 'find': '장작더미 뒤에서 찾았다!'}, 10, 106)
    put({'type': 'landmark', 'id': 'lm_felt_castle', 'name': '무너진 옛 성문'}, 75, 30)
    put({'type': 'landmark', 'id': 'lm_felt_fountain', 'name': '루카의 모닥불'}, 75, 76)
    put({'type': 'landmark', 'id': 'lm_felt_grave', 'name': '예배당 묘지'}, 137, 44)
    put({'type': 'vista', 'id': 'felt_gate', 'r': 3, 'zoom': .72, 'dir': 270, 'pan': 5, 'name': '무너진 옛 성문', 'sub': '펠트는 그 그늘 아래에 있다'}, 75, 33)
    # ---- reachability ----
    SOL = set('#TPRCHX~')
    free = np.vectorize(lambda c: c not in SOL)(grid); sx, sy = 75, 78
    reach = bfs(free, sx, sy); grid[free & ~reach] = '#'; free2 = free & reach
    for o in objs:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'door'): free2[o['y'], o['x']] = False
    r2 = bfs(free2, sx, sy); lost = int((free & reach & ~r2).sum()); bad = []
    for o in objs:
        x, y = o['x'], o['y']
        if o['type'] in ('door', 'npc', 'chest', 'sign', 'waystone', 'clue'):
            if not any(0 <= y + b < H and 0 <= x + a < W and r2[y + b, x + a] for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))): bad.append(o.get('id') or o['type'])
        elif o['type'] in ('hidden', 'mark', 'landmark', 'vista') and not r2[y, x] and not any(r2[y + b, x + a] for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))): bad.append(o.get('id'))
        elif o['type'] == 'exit' and not any(r2[y + b, x + a] for a in range(o['w']) for b in range(o['h'])): bad.append('exit:' + o['label'])
    for k, (x, y, _) in spawns.items():
        if not r2[int(y), int(x)]: bad.append('spawn:' + k)
    print(f'felt: reach {int(r2.sum())} cells, lost {lost}, unreachable {bad}')
    # ---- ground: ashen dirt, dead grass, scorch, broken cobble, packed paths; a misty void above the walls ----
    Pw = wang.load_set(os.path.join(SETS, 'p_felt'))
    tw, th = (W * 3 + 3) // 4, (H * 3 + 3) // 4
    V = np.ones((th + 1, tw + 1), int)
    img = np.array(wang.compose(V, Pw, None, seed=SEED, mottle=.10, gr={'sat': .5, 'gain': .92})).astype(np.float32)[:H * G, :W * G]
    img = img * .3 + ndimage.uniform_filter(img, size=(9, 9, 1)) * .7
    gh, gw = img.shape[:2]
    def up(a): return np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((gw, gh), Image.BILINEAR)).astype(np.float32) / 255.
    def sn(scale, seed):                                                                                  # smooth fbm-ish noise 0..1 (no square cells)
        r = np.random.RandomState(seed); lh, lw = int(gh / scale * 4) + 4, int(gw / scale * 4) + 4
        lo = ndimage.gaussian_filter(r.rand(lh, lw), 2.0); lo = (lo - np.percentile(lo, 2)) / (np.percentile(lo, 98) - np.percentile(lo, 2) + 1e-6)
        return np.array(Image.fromarray(np.clip(lo * 255, 0, 255).astype(np.uint8)).resize((gw + int(gw / (lw - 4) * 4), gh + int(gh / (lh - 4) * 4)), Image.BICUBIC)).astype(np.float32)[:gh, :gw] / 255.
    tone = sn(520, SEED + 40) * .6 + sn(180, SEED + 41) * .4
    img *= (.91 + .16 * tone)[..., None]
    Gs = wang.load_set(os.path.join(SETS, 't_grass_dirt')); gt = Gs[(1, 1, 1, 1)]
    grass = np.zeros_like(img); r_ = random.Random(SEED + 9)
    for y in range(0, gh, 32):
        for x in range(0, gw, 32): grass[y:y + 32, x:x + 32] = wang.d4(gt, r_.randrange(8))[:min(32, gh - y), :min(32, gw - x)]
    grass = wang.grade(grass, sat=.36, warm=(1.03, 1.0, .82), gain=.78)                       # dead, dry grass
    grass = grass * .5 + ndimage.uniform_filter(grass, size=(3, 3, 1)) * .5
    near = ndimage.distance_transform_edt(~((road | lanec | Hs) & ~np.isin(grid, ['T', 'P'])))
    away = up(np.clip((near - 1.0) / 4.0, 0, 1))
    gv = sn(260, SEED + 11) * .65 + sn(70, SEED + 12) * .35 + away * .3 + (wang.vnoise(gh, gw, 3, SEED + 13) - .5) * .12
    gmask = np.clip((gv - .78) / .1, 0, 1)
    img = img * (1 - gmask[..., None]) + grass * gmask[..., None]
    av = sn(300, SEED + 30) * .7 + sn(90, SEED + 31) * .3
    ash = np.clip((av - .62) / .25, 0, 1) * .18
    img = img * (1 - ash[..., None]) + np.array([138, 133, 128.]) * ash[..., None]                # pale ash drifts
    sc = np.zeros((H, W))
    for x, y, _ in RUINS: sc[max(0, y - 6):y + 3, max(0, x - 6):x + 7] = 1
    scorch = up(ndimage.gaussian_filter(sc, 1.8)) * np.clip(.4 + sn(60, SEED + 32), 0, 1)
    img *= (1 - .45 * scorch)[..., None]
    rf = np.array(RD.filter(ImageFilter.GaussianBlur(5))).astype(np.float32) / 255.
    rf = np.clip(rf * 1.2 + (sn(90, SEED + 20) - .5) * .7 + (wang.vnoise(gh, gw, 5, SEED + 22) - .5) * .18, 0, 1)   # broken: dirt shows through in patches
    lf = np.array(LD.filter(ImageFilter.GaussianBlur(4))).astype(np.float32) / 255.
    lf = np.clip(lf + (sn(60, SEED + 21) - .5) * .25, 0, 1)
    ob = cobble.bricks
    cobble.bricks = lambda H_, W_, rh=16, sw=21, jit=6, seed=1: ob(H_, W_, 8, 11, 3, seed)
    lm = np.clip((lf - .2) / .45, 0, 1)[..., None] * .88                                          # packed earth paths + the camp clearing: trodden, paler, warmer
    packed = ndimage.uniform_filter(img, size=(11, 11, 1)) * np.array([1.24, 1.17, 1.05]) + 8 + (wang.vnoise(gh, gw, 3, SEED + 50) - .5)[..., None] * 14
    img = img * (1 - lm) + packed * lm
    img = cobble.render(img, rf, None, 0, seed=SEED, lane=None, stone=(100, 94, 88)); cobble.bricks = ob
    bandm = ndimage.gaussian_filter(np.isin(grid, ['#', 'T', 'P', 'R', 'C']).astype(float), 1.0)
    img *= 1.22 * (1 - .4 * up(bandm))[..., None]
    # the north band: dark rubble at the wall foot, a cold misty void above the walls (behind the far castle)
    yy2 = np.arange(gh, dtype=np.float32)[:, None] / G
    void = np.clip((WALL_Y - 4 - yy2) / 10, 0, 1)
    sky = np.array([92, 90, 100.]) * (1 - np.clip(yy2 / 18, 0, 1))[..., None] + np.array([58, 56, 62.]) * np.clip(yy2 / 18, 0, 1)[..., None]
    img = img * (1 - void[..., None]) + np.broadcast_to(sky, img.shape) * void[..., None]
    footd = np.clip(1 - np.abs(yy2 - WALL_Y) / 3, 0, 1); img *= (1 - .35 * footd)[..., None]
    gimg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    gp = FA + 'ground4.png'; gimg.save(rel(gp), optimize=True)
    # ---- hd block ----
    def arts(keys, D=3): return [{'img': props.OLD[k][0], 'ax': props.OLD[k][1], 'ay': props.OLD[k][2], 'D': D} for k in keys]
    decoArt = {'T': arts(['dead_tree', 'burnt_pine_a', 'burnt_pine_b', 'ash_tree_b']), 'P': arts(['burnt_pine_a', 'burnt_pine_b', 'dead_tree']),
               'R': arts(['boulder', 'rubble', 'stone_low', 'ruin_pillar']), 'u': arts(['ash_bush']), 'w': arts(['dry_reeds']), 's': arts(['stump', 'stone_low', 'stump', 'stone_low'])}
    if A['dtree']: decoArt['T'] += [dict(v, D=2.4) for v in A['dtree']]
    if A['debris']: decoArt['R'] += [dict(v, D=2.6) for v in A['debris']]
    for d in decoArt['T'] + decoArt['P']: d['sway'] = .5
    taken = {(o['x'], o['y']) for o in objs}
    for y in range(WALL_Y + 1, H - 1):
        for x in range(1, W - 1):
            if grid[y, x] != '.' or (x, y) in taken: continue
            if not np.isin(grid[y-1:y+2, x-1:x+2], ['=', 'H']).any() and rnd.random() < .025: grid[y, x] = rnd.choice('su')
    free = np.vectorize(lambda c: c not in SOL | {'u'})(grid); free2 = free.copy()
    for o in objs:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'door'): free2[o['y'], o['x']] = False
    for _it in range(6):
        r3 = bfs(free2, sx, sy); lostm = r2 & ~r3
        if not lostm.any(): break
        fixm = ndimage.binary_dilation(lostm, iterations=2) & (grid == 'u'); grid[fixm] = '.'; free2[fixm] = True
    print('  after scatter reach', int(r3.sum()), 'lost', int((r2 & ~r3).sum()))
    gcell = np.array(Image.fromarray((gmask * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)) > 100
    tufts = []
    for y in range(WALL_Y + 1, H - 1):
        for x in range(1, W - 1):
            if grid[y, x] != '.': continue
            if rnd.random() < (.4 if gcell[y, x] else .06): tufts.append([round(x + rnd.random(), 2), round(y + .3 + rnd.random() * .7, 2), 3 if rnd.random() < .2 else rnd.randrange(3)])
    small.sort(key=lambda q: q['y']); props_.sort(key=lambda q: q['y'])
    allp = back + sorted(props_ + small, key=lambda q: q['y']) + under
    lights = []; fires = []; flick = []
    for q in small:
        n = os.path.basename(q['img'])[:-4]
        if n == 'brazier': L = [q['x'], q['y'] - .9, 60, '#ff8a3a', 1]; lights.append(L); flick.append([q['x'], q['y'] - .9, 34, '#ff8a3a', 1]); fires.append([q['x'], q['y'] - 1.05, 1.0])
        if n == 'lamp': lights.append([q['x'], q['y'] - 1.2, 46, '#ffb060', .8]); fires.append([q['x'], q['y'] - 1.25, .45])
        if n == 'candelabra': lights.append([q['x'], q['y'] - 1.6, 30, '#ffc070', .7]); fires.append([q['x'], q['y'] - 2.05, .3])
    cf = [CAMP[0], CAMP[1] + .2]
    lights += [[cf[0], cf[1], 170, '#ff8a3a', 1.0], [cf[0], cf[1], 70, '#ffc070', .6]]; flick.append([cf[0], cf[1], 64, '#ff9a40', .9])
    fires += [[cf[0], cf[1] - .1, 1.5], [cf[0] - .4, cf[1] + .2, .9, 'embers']]
    smoke = [[cf[0], cf[1] - .6, 1.6, 5]]                                                         # the campfire's smoke column: seen from far off
    for q in props_:
        if q['id'] == 'se_house':
            fxp = q['x'] + (210 - q['ax']) / q['D'] / T; fyp = q['y'] - (q['ay'] - 262) / q['D'] / T
            lights.append([fxp, fyp, 80, '#ff7a2a', 1]); fires.append([fxp, fyp, 1.5, 'forge']); flick.append([fxp, fyp, 40, '#ff7a2a', 1])
        if q['id'] == 'inn': lights.append([q['x'] - 2, q['y'] - 2, 60, '#ffb060', .8])
        off = {'se_house': (-1.6, -6.9), 's_house': (-.2, -6.4), 'bl_house': (1.9, -4.6), 'inn': (2.2, -7.6)}.get(q['id'])
        if off: smoke.append([q['x'] + off[0] * 3 / q['D'], q['y'] + off[1] * 3 / q['D'], 1])
        if q['id'].startswith('ruin_') and (q['x'] + q['y']) % 3 == 0: smoke.append([q['x'] + .5, q['y'] - 2.5, .8])   # still smouldering
    for q in small:
        if 'ember_rubble' in q['img']: fires.append([q['x'], q['y'] - .4, .7, 'embers'])
    hd = {'D': HD, 'ground': gp, 'props': allp, 'decoArt': decoArt, 'lights': lights, 'smoke': smoke, 'grade': 'dusk', 'gradeCol': 'rgb(214,203,192)', 'flick': flick, 'tufts': tufts,
          'fires': fires, 'fx': {'particles': 'ash', 'birds': 4, 'mist': 10, 'tuft': ['#57534a', '#625d50', '#4a463d']},
          'webs': [[8.2, 50.6, 10.8, 52.2, .5, .3], [14.0, 49.5, 16.5, 50.2, .6, .3], [7.0, 45.5, 9.0, 47.6, .4, .25]]}
    legend = {'.': 'dirt', '=': 'dirt', '#': 'cliff', 'X': 'cliff', 'H': {'ground': 'dirt', 'solid': True},
              'T': {'ground': 'dirt', 'deco': 'tree'}, 'P': {'ground': 'dirt', 'deco': 'pine'}, 'R': {'ground': 'dirt', 'deco': 'boulder'},
              'u': {'ground': 'dirt', 'deco': 'bush'}, 's': {'ground': 'dirt', 'deco': 'stump', 'solid': False}, 'w': {'ground': 'dirt', 'deco': 'mushrooms', 'solid': False}}
    out = {k: ORIG[k] for k in ('type', 'area', 'title', 'bgm', 'battleBgm', 'tileset', 'tile', 'id', 'name')}
    cur = json.load(open(rel('maps/felt.json')))
    out['title'] = dict(out['title'], sub='무너진 옛 성문 그늘 아래, 생존자의 마을')
    out.update({'region': ORIG['region'], 'viewZoom': 1.3, 'grade': 'ash', 'fog': .34, 'ash': 60, 'wind': [5, 1], 'w': W, 'h': H, 'legend': legend,
                'solid': ['#', 'C', 'X', 'H', 'T', 'P', 'R', 'u', '~'], 'ground': [''.join(r) for r in grid], 'objects': objs, 'spawns': spawns, 'hd': hd,
                'note': 'GENERATED by tools/hd/fields/build_felt4.py (ch1 draft layout: old gate arch north, campfire centre, four blocks) - do not hand-edit'})
    if 'mapPos' in cur: out['mapPos'] = cur['mapPos']
    json.dump(out, open(rel('maps/felt.json'), 'w'), ensure_ascii=False, indent=1)
    return out
ARCH_DX = 0.0
if __name__ == '__main__':
    main()
