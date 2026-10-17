#!/usr/bin/env python3
"""[town_a] builds town A (시작 마을) : ground chunks, y-sorted overlays, interiors, collision grids, doors/signs/chests/NPC spots
-> town/assets/town_a/*  and town/assets/level.json ("ta" block).  usage: python3 build_town_a.py [TOWN_DIR]"""
import sys, os, json, math, base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px import *
from bld import building, stone_courses, planks
import props as PR
import interiors as IN
from ground import Ground, fbm, C

TOWN = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(TOWN, 'assets', 'town_a'); os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(('.png', '.jpg')): os.remove(os.path.join(OUT, f))
CELL = 8
ROOM_OUT = dict(id='out', name='시작 마을', x0=-1300, y0=-1050, x1=2500, y1=790)

IMGS = {}          # key -> filename (shared sprite images)
OV = []            # overlays {img,x,y,w,h,sortY}
BLK = []           # collision shapes in world coords: ('rect',x0,y0,x1,y1) ('ell',cx,cy,rx,ry) ('poly',[pts])
SHADOWS = []       # ground shadows: ('ell',cx,cy,rx,ry,k) / ('poly',pts,k)
DOORS, SIGNS, CHESTS, SPOTS, LABELS = [], [], [], [], []
ROOMS = [ROOM_OUT]

def save_img(key, cv):
    if key in IMGS: return IMGS[key]
    fn = key + '.png'; cv.img().save(os.path.join(OUT, fn), optimize=True); IMGS[key] = dict(src=fn, w=cv.w, h=cv.h); return IMGS[key]

def place(key, item, x, y, block=True, sort_off=0, shadow=True, room='out'):
    """item from props: (Canvas, (ax,ay) foot anchor, ellipse rel art px). x,y = world foot."""
    cv, (ax, ay), el = item
    save_img(key, cv)
    ox, oy = x - ax / A, y - ay / A
    OV.append(dict(img=key, x=round(ox, 1), y=round(oy, 1), w=round(cv.w / A, 1), h=round(cv.h / A, 1), sortY=round(y + sort_off, 1)))
    if block and el:
        ex, ey, rx, ry = el; BLK.append(('ell', ox + ex / A, oy + ey / A, max(6, rx / A), max(5, ry / A)))
    if shadow and el:
        ex, ey, rx, ry = el; SHADOWS.append(('ell', ox + ex / A + 6, oy + ey / A + 2, rx / A * 1.25 + 6, ry / A * 1.6 + 5, .66))
    return ox, oy

def place_tree(kind, seed, scale, x, y):
    item = PR.tree(kind, seed, scale)
    cv = item[0]
    key = f'tree_{kind}_{seed}_{int(scale*100)}'
    place(key, item, x, y, shadow=False)
    w = cv.w / A
    SHADOWS.append(('ell', x + 14, y - 4, w * .42, w * .17, .55))

def place_building(key, spec, X, Y, doors=(), sign=None, depth=None, label=None):
    cv, meta = building(spec); save_img(key, cv)
    wx0, ywt, wx1, yb = meta['wall']
    ox, oy = X - wx0 / A, Y - yb / A
    OV.append(dict(img=key, x=round(ox, 1), y=round(oy, 1), w=round(cv.w / A, 1), h=round(cv.h / A, 1), sortY=Y))
    Wd = (wx1 - wx0) / A
    D = depth or (yb - spec.get('topPad', 18)) / A * .72
    BLK.append(('rect', X + 2, Y - D, X + Wd - 2, Y - 3))
    SHADOWS.append(('poly', [(X + Wd, Y - D * .9), (X + Wd + 46, Y - D * .75), (X + Wd + 46, Y + 10), (X + 6, Y + 14), (X + 6, Y)], .6))
    out = dict(x0=X, x1=X + Wd, y=Y, top=oy, D=D, doors=[])
    for i, d in enumerate(meta['doors']):
        dx = ox + d['x'] / A; dw = d['w'] / A
        out['doors'].append((dx, dw))
        BLK.append(('cut', dx - dw / 2 - 2, Y - 14, dx + dw / 2 + 2, Y))   # door recess (still solid wall above)
    if sign and meta['signs']:
        bx, by, bw, bh = meta['signs'][0]
        SIGNS.append(dict(x=round(ox + bx / A, 1), y=round(oy + by / A, 1), w=round(bw / A, 1), h=round(bh / A, 1), text=sign))
    if label: LABELS.append(dict(x=X + Wd / 2, y=Y - D / 2, text=label))
    return out

# ---------------------------------------------------------------- layout (world px; hero ≈ 93 px tall)
T = {}
# west: dojo + 바렌's house + duel clearing
T['dojo'] = place_building('b_dojo', dict(W=300, H=100, RH=86, roof='roof_teal', kind='gable', wall='wood', woodpal='wood', seed=31,
    door=dict(x=126, w=48, h=64, style='square', frame='timber', double=True, steps=2),
    windows=[(30, 30, 30, 24, {'box': False}), (240, 30, 30, 24, {'box': False})], padR=0, padL=0,
    sign=(1, 0, 0, 0, None)), -420, 440, label='바렌 도장')
T['baren'] = place_building('b_baren', dict(W=190, H=84, RH=76, roof='roof_brown', kind='hip', seed=32,
    door=dict(x=80, w=30, h=58), windows=[(22, 22, 24, 22, {'sh': 'cloth_blue'}), (144, 22, 24, 22, {'sh': 'cloth_blue'})], chimneys=[30]), -400, 90, label='사범의 집')
T['smith'] = place_building('b_smith', dict(W=260, H=100, RH=82, roof='roof_slate', kind='gable', wall='stone', seed=33, padL=60,
    door=dict(x=34, w=44, h=62, style='square', frame='timber', double=True), chimneys=[200],
    windows=[(120, 30, 28, 22, {}), (190, 30, 28, 22, {'box': False})], sign=(-1, 54, 26, 12, None)), 0, 240, sign='대장간', label='대장간')
T['hero'] = place_building('b_hero', dict(W=180, H=84, RH=78, roof='roof_red', kind='hip', gables=[(90, 34, 70)], seed=34,
    door=dict(x=76, w=28, h=58), windows=[(20, 24, 22, 20, {'sh': 'cloth_green'}), (138, 24, 22, 20, {'sh': 'cloth_green'})]), 110, -385, label='필멸자의 집')
T['chief'] = place_building('b_chief', dict(W=330, H=130, RH=96, roof='roof_red', kind='hip', gables=[(84, 42, 86), (246, 42, 86)], seed=35, beam_mid=60,
    posts=(110, 220), door=dict(x=150, w=32, h=62), chimneys=[160],
    windows=[(24, 18, 24, 26, {'sh': 'cloth_red'}), (282, 18, 24, 26, {'sh': 'cloth_red'}), (24, 76, 24, 24, {}), (282, 76, 24, 24, {}), (120, 76, 22, 22, {}), (190, 76, 22, 22, {})]), 600, -420, label='촌장 오스왈드의 집')
T['granny'] = place_building('b_granny', dict(W=230, H=90, RH=82, roof='roof_brown', kind='gable', wall='stone', stonepal='stone_w', seed=36,
    door=dict(x=40, w=28, h=58, style='arch'), windows=[(110, 26, 24, 22, {'sh': 'cloth_purple'}), (176, 26, 24, 22, {})], chimneys=[190]), 1320, -340, label='엘스베트의 집')
T['herb'] = place_building('b_herb', dict(W=180, H=80, RH=82, roof='roof_thatch', kind='hip', wall='logs', seed=37,
    door=dict(x=70, w=28, h=56, frame='timber', style='square'), windows=[(20, 24, 22, 18, {}), (136, 24, 22, 18, {})]), -1160, -380, label='세레스의 약초 오두막')
T['farm'] = place_building('b_farm', dict(W=230, H=88, RH=82, roof='roof_thatch', kind='gable', wall='wood', seed=38,
    door=dict(x=90, w=30, h=58, frame='timber', style='square'), windows=[(24, 26, 24, 20, {'sh': 'cloth_red'}), (176, 26, 24, 20, {'sh': 'cloth_red'})], chimneys=[40]), -1200, 190, label='하로의 농가')
T['tool'] = place_building('b_tool', dict(W=260, H=96, RH=92, roof='roof_green', kind='hip', gables=[(150, 46, 84)], seed=39, padR=60,
    door=dict(x=134, w=32, h=60), windows=[(30, 30, 30, 24, {'box': True}), (206, 30, 26, 22, {'sh': 'cloth_green'})],
    awning=(14, 90, 14, ('cloth_green', 'cloth_cream')), sign=(1, 64, 28, 14, None)), 1300, 300, sign='도구상점', label='도구상점 「보따리」')
T['tailor'] = place_building('b_tailor', dict(W=250, H=96, RH=92, roof='roof_teal', kind='hip', gables=[(96, 44, 84)], seed=40, wallpal='plaster_w', padL=60,
    door=dict(x=82, w=30, h=60), windows=[(24, 30, 26, 24, {'sh': 'cloth_purple'}), (150, 30, 30, 24, {}), (200, 30, 30, 24, {})],
    awning=(140, 240, 14, ('cloth_red', 'cloth_cream')), sign=(1, 64, 28, 14, None)), 1880, 300, sign='재봉소', label='리네트 재봉소')
T['hs1'] = place_building('b_house1', dict(W=210, H=86, RH=80, roof='roof_red', kind='hip', seed=41, door=dict(x=90, w=28, h=58),
    windows=[(24, 24, 24, 22, {'sh': 'cloth_blue'}), (162, 24, 24, 22, {'sh': 'cloth_blue'})], chimneys=[160]), 1330, 680)
T['hs2'] = place_building('b_house2', dict(W=240, H=90, RH=84, roof='roof_brown', kind='gable', seed=42, wallpal='plaster_w', door=dict(x=40, w=28, h=58),
    gables=[(170, 40, 76)], windows=[(110, 26, 24, 22, {}), (190, 26, 24, 22, {'sh': 'cloth_green'})]), 1860, 680)
T['booth'] = place_building('b_booth', dict(W=80, H=72, RH=50, roof='roof_red', kind='hip', wall='wood', seed=43, F=6,
    windows=[(24, 18, 30, 18, {'box': False})]), 860, 660, depth=70, label='경비 초소')

# fountain (procedural, centre 777,415 = engine POOL/PILLAR) ---------------------------------
def fountain():
    w, h = 190, 170; c = Canvas(w, h); cx, cy = w // 2, 112
    st = P['stone']
    c.ellipse(cx, cy + 6, 86, 40, st[2])                    # front face
    for x in range(cx - 86, cx + 86):
        for y in range(cy, cy + 14):
            if ((x - cx) / 86) ** 2 + ((y - 6 - cy) / 40) ** 2 < 1 and ((x - cx) / 86) ** 2 + ((y - cy) / 40) ** 2 >= 1:
                c.put(x, y, st[2] if (x // 9 + (y > cy + 7)) % 2 else st[3])
    c.ellipse(cx, cy, 86, 40, st[4]); c.ellipse(cx, cy, 80, 36, st[3])
    m = c.ellipse(cx, cy, 72, 31, P['water'][2])
    yy, xx = np.mgrid[0:h, 0:w]
    rr = np.sqrt(((xx - cx) / 72) ** 2 + ((yy - cy) / 31) ** 2)
    ring = m & ((rr * 9).astype(int) % 3 == 0); c.a[ring] = P['water'][3]
    hl = m & (yy < cy - 22); c.a[hl] = P['water'][1]
    for k in range(14):
        a = k / 14 * math.tau; c.put(cx + int(math.cos(a) * 60), cy + int(math.sin(a) * 24), P['water'][6])
    # pillar + bowls
    c.rect(cx - 8, cy - 70, cx + 8, cy + 2, st[3]); c.vline(cx - 8, cy - 70, cy + 2, st[5]); c.vline(cx + 7, cy - 70, cy + 2, st[1])
    c.ellipse(cx, cy - 40, 30, 10, st[2]); c.ellipse(cx, cy - 42, 28, 8, st[4]); c.ellipse(cx, cy - 42, 23, 6, P['water'][3])
    c.ellipse(cx, cy - 72, 16, 6, st[2]); c.ellipse(cx, cy - 73, 15, 5, st[4]); c.ellipse(cx, cy - 73, 11, 3, P['water'][4])
    c.rect(cx - 3, cy - 92, cx + 3, cy - 74, P['water'][5]); c.rect(cx - 1, cy - 98, cx + 1, cy - 92, P['water'][6])
    for side in (-1, 1):
        for t in range(26):
            x = cx + side * (8 + t); y = int(cy - 72 + t * t * .05 + t * .2); c.put(x, y, P['water'][6]); c.put(x, y + 1, P['water'][5])
            x2 = cx + side * (24 + t * 1.4); y2 = int(cy - 40 + t * t * .07 + t * .3)
            if y2 < cy - 4: c.put(int(x2), y2, P['water'][6]); c.put(int(x2), y2 + 1, P['water'][5])
    c.outline()
    return c, (cx, cy + 28), None
place('fountain', fountain(), 777, 415 + 17, block=False, sort_off=-14, shadow=False)
BLK.append(('ell', 777, 418, 138, 66))

# trees -----------------------------------------------------------------------------------------
import random
R = random.Random(5)
def belt(x0, x1, y0, y1, n, kinds=('oak', 'oak', 'pine', 'round'), scale=(1.0, 1.35)):
    for i in range(n):
        x = R.uniform(x0, x1); y = R.uniform(y0, y1); k = R.choice(kinds)
        place_tree(k, R.randint(1, 6), round(R.uniform(*scale), 2), x, y)
belt(-1300, 2500, -1050, -900, 34)                 # north forest
belt(-1300, -1180, -900, 700, 16)                  # west edge
belt(2380, 2500, -900, 700, 16)                    # east edge
BLK += [('rect', -1300, -1050, 2500, -905), ('rect', -1300, -1050, -1200, 790), ('rect', 2400, -1050, 2500, 790)]
# accents
for (k, s, sc, x, y) in [('oak', 2, 1.3, -900, -200), ('oak', 3, 1.2, -560, -150), ('pine', 4, 1.1, -640, 260), ('oak', 1, 1.25, -1290, 330),
                         ('oak', 5, 1.1, -480, -40), ('round', 6, 1.1, -1000, -90), ('oak', 4, 1.0, 40, -560), ('pine', 2, 1.2, 520, -620),
                         ('oak', 6, 1.4, 1790, -560), ('oak', 1, 1.1, 1220, -620), ('pine', 3, 1.0, 2250, -420), ('oak', 2, 1.2, 2330, -150),
                         ('oak', 3, 1.3, 2330, 200), ('pine', 5, 1.1, 2330, 520), ('oak', 4, 1.0, 1255, 720 - 140), ('round', 1, .9, 520, 40),
                         ('oak', 5, 1.15, 1150, -700), ('pine', 6, 1.2, 330, -700), ('oak', 2, 1.0, -260, -500), ('oak', 6, 1.1, -760, -560),
                         ('round', 3, 1.0, 2100, -520), ('oak', 1, 1.0, 1600, -760), ('pine', 1, 1.05, -380, -760)]:
    place_tree(k, s, sc, x, y)
for i, (x, y) in enumerate([(470, 255), (1080, 690), (440, 680), (-460, 690), (200, 690), (1230, 470), (2280, 450), (1690, 430), (600, -60),
                            (980, -95), (1250, -95), (-1100, -20), (-900, 660), (-1150, 690), (2200, -180), (1750, 50), (1290, 60)]):
    place('bush_%d' % (i % 4), PR.tree('bush', 10 + i % 4, 1.0), x, y)

# fences / walls ----------------------------------------------------------------------------------
def fence_piece(n_posts, kind='rail', vertical=False):
    if vertical:
        c = Canvas(12, 40); w = P['wood']; c.rect(4, 0, 9, 40, w[2]); c.vline(4, 0, 40, w[4])
        if kind == 'picket': c.rect(3, 0, 10, 40, hexc('#e6e0d0')); c.vline(3, 0, 40, hexc('#ffffff'))
        c.outline(); return c
    L = n_posts * 22; c = Canvas(L + 6, 30); w = P['wood']
    if kind == 'picket':
        for x in range(0, L, 7): c.rect(x + 2, 4, x + 7, 28, hexc('#e6e0d0')); c.poly([(x + 2, 4), (x + 4, 0), (x + 7, 4)], hexc('#f4f0e6')); c.vline(x + 6, 4, 28, hexc('#b8b0a0'))
        c.rect(0, 10, L + 4, 12, hexc('#c8c0b0')); c.rect(0, 20, L + 4, 22, hexc('#c8c0b0'))
    else:
        for y in (8, 17): c.rect(0, y, L + 6, y + 3, w[3]); c.hline(0, L + 6, y, w[5])
        for k in range(n_posts + 1): x = k * 22; c.rect(x, 2, x + 5, 29, w[2]); c.vline(x, 2, 29, w[4]); c.hline(x, x + 5, 2, w[5])
    c.outline(); return c
def fence_h(x0, x1, y, kind='rail'):
    x = x0
    while x < x1 - 20:
        seg = min(x1 - x, 220); n = max(1, int(seg * A / 22)); cv = fence_piece(n, kind); key = f'fence_{kind}_{n}'
        save_img(key, cv); OV.append(dict(img=key, x=round(x, 1), y=round(y - cv.h / A, 1), w=round(cv.w / A, 1), h=round(cv.h / A, 1), sortY=y))
        x += n * 22 / A
    BLK.append(('rect', x0, y - 10, x1, y + 2))
def fence_v(x, y0, y1, kind='rail'):
    cv = fence_piece(0, kind, True); key = f'fencev_{kind}'; save_img(key, cv)
    y = y0
    while y < y1:
        OV.append(dict(img=key, x=round(x - 10, 1), y=round(y, 1), w=round(cv.w / A, 1), h=round(cv.h / A, 1), sortY=round(y + cv.h / A, 1))); y += cv.h / A - 4
    BLK.append(('rect', x - 6, y0, x + 6, y1))
fence_h(80, 400, 455)                               # training yard north fence
fence_v(-445, 455, 690)                             # training yard west fence
fence_v(1200, 700, 745)                             # palisade step joint
fence_h(-1240, -800, 262); fence_h(-700, -500, 262) # fields north (gap = farm lane)
fence_v(-500, 262, 480); fence_h(-1240, -760, 485, 'rail')
fence_h(580, 760, -110, 'picket'); fence_h(860, 1170, -110, 'picket')   # chief's yard (gap at the stairs)
fence_v(580, -420, -110, 'picket'); fence_v(1170, -420, -110, 'picket')
fence_h(1760, 2340, -330, 'picket'); fence_v(2340, -330, -60, 'picket')  # tailor back yard

# south palisade + gate
def palisade(L):
    c = Canvas(int(L * A), 70); w = P['wood']; R2 = random.Random(int(L))
    for x in range(0, c.w, 8):
        hh = 60 + R2.randint(-3, 3); c.rect(x, 70 - hh, x + 7, 70, w[3 if (x // 8) % 2 else 2]); c.vline(x, 70 - hh, 70, w[4]); c.vline(x + 6, 70 - hh, 70, w[1])
        c.poly([(x, 70 - hh), (x + 3, 70 - hh - 5), (x + 7, 70 - hh)], w[4])
    for y in (24, 50): c.rect(0, y, c.w, y + 3, P['wood_d'][2])
    c.outline(); return c
for (a, b, yb) in ((-1300, 545, 735), (815, 1200, 735), (1200, 2500, 785)):   # east part steps south: walkway in front of the two houses
    x = a
    while x < b:
        L = min(400, b - x); cv = palisade(L); key = 'palisade_%d' % int(L); save_img(key, cv)
        OV.append(dict(img=key, x=x, y=round(yb - cv.h / A, 1), w=round(cv.w / A, 1), h=round(cv.h / A, 1), sortY=yb)); x += L
    BLK.append(('rect', a, yb - 43, b, 790))
BLK.append(('rect', 1192, 692, 1208, 790))
place('gate_l', PR.gate_pillar(1), 540, 740); place('gate_r', PR.gate_pillar(2), 822, 740)
def gate_arch():
    c = Canvas(int(330 * A), 40); w = P['wood']
    c.rect(0, 10, c.w, 30, w[3]); c.hline(0, c.w, 10, w[5]); c.hline(0, c.w, 29, w[1]); c.poly([(0, 10), (c.w // 2, 0), (c.w, 10)], P['roof_red'][3])
    c.rect(c.w // 2 - 50, 13, c.w // 2 + 50, 28, w[4]); c.outline(); return c
cv = gate_arch(); save_img('gate_arch', cv); OV.append(dict(img='gate_arch', x=516, y=520, w=round(cv.w / A, 1), h=round(cv.h / A, 1), sortY=760))
SIGNS.append(dict(x=681 - 83, y=520 + 13 / A, w=166, h=15 / A, text='남문 · 바람길'))

# terrace (north hill retaining wall) + stairs
def retaining(L, H=46):
    c = Canvas(int(L * A), int(H * A) + 6)
    stone_courses(c, 0, 6, c.w, c.h, P['stone_w'], int(L), rowh=(6, 8), sw=(9, 15))
    c.rect(0, 0, c.w, 6, P['leaf'][4]); 
    for x in range(0, c.w, 3): c.put(x, 6 + (x * 7) % 3, P['leaf'][3])
    c.outline(); return c
TER = [(-560, 520, -240), (560, 720, -90), (840, 1250, -90)]
for (a, b, y) in TER:
    x = a
    while x < b:
        L = min(300, b - x); cv = retaining(L); key = 'ter_%d' % int(L); save_img(key, cv)
        OV.append(dict(img=key, x=x, y=round(y - cv.h / A, 1), w=round(cv.w / A, 1), h=round(cv.h / A, 1), sortY=y)); x += L
    BLK.append(('rect', a, y - 46, b, y - 4))
BLK.append(('poly', [(520, -286), (560, -136), (560, -94), (520, -244)]))   # diagonal corner
# west stairs gap at x -470..-410? (handled by not walling) -> wall starts at -560 but leave gap
BLK = [b for b in BLK]
BLK.append(('cutrect', -500, -290, -420, -238))

# props -------------------------------------------------------------------------------------------
place('well_mossy', PR.well(3, True), 492, 150)            # DIVE 'barrel' spot (450,168) -> 대장간 옆 이끼 낀 우물
place('barrel_rain', PR.barrel(2, True), 552, 150)
place('anvil', PR.anvil(), 92, 290); place('woodpile', PR.woodpile(), 360, 282); place('barrel1', PR.barrel(4), 400, 268)
place('crate1', PR.crate(1), 1262, 330); place('sacks', PR.sacks(), 1268, 380); place('barrel2', PR.barrel(5), 1790, 330); place('crate2', PR.crate(2), 2310, 335)
for (x, y) in [(565, 268), (995, 262), (470, 560 + 120), (1070, 690)]: place('lamp', PR.lamp(), x, y)
for (x, y) in [(1660, 350), (2380, 470), (1180, 340)]: place('lamp', PR.lamp(), x, y)
place('bench', PR.bench(1), 1000 + 70, 250); place('bench_moss', PR.bench(7, True), 360, 430)
place('notice', PR.notice_board(2), 1150, 252)
place('signpost', PR.signpost(1, ((1, 0), (-1, 1))), 905, 630)
place('bell', PR.bell_tower(), 1240, 250)
place('cart', PR.cart(), -700, 210); place('woodpile2', PR.woodpile(2), -1235, 205); place('trough', PR.trough(), -60, 668)
place('dummy1', PR.dummy(1), -340, 540); place('dummy2', PR.dummy(2), -220, 600); place('dummy3', PR.dummy(3), -340, 650)
place('target', PR.target(), -80, 660); place('rack', PR.weapon_rack(), 30, 470)
place('scare1', PR.scarecrow(1), -900, 380); place('scare2', PR.scarecrow(2), -640, 590); place('hay', PR.haystack(3), -590, 640)
place('scare3', PR.scarecrow(3, False), -1100, 600)
place('laundry', PR.laundry(4, 190), 2030, -150, block=False)
for (x, y) in [(-1000, -330), (-940, -350), (-1190, -330), (-1120, -320)]: place('pot_%d' % (x % 4), PR.flowerpot(x % 7), x, y)
place('crate3', PR.crate(3), 970, 690 - 70); place('barrel3', PR.barrel(6), 1000, 690 - 70)
place('stall', PR.stall(2, ('cloth_blue', 'cloth_cream')), 1580, 470)
for (x, y) in [(-700, 60), (-760, 120)]: pass
place('rock_big1', PR.rock(1, True), -1000, 80); place('rock2', PR.rock(2), -820, -40); place('rock3', PR.rock(3), 2200, 120); place('rock_big2', PR.rock(4, True), 1700, -720)
place('pot_g1', PR.flowerpot(2), 1290, -330); place('pot_g2', PR.flowerpot(5), 1500, -320)
# stone wall behind 엘스베트's house (까치둥지 담장)
def low_wall(L):
    c = Canvas(int(L * A), 40); stone_courses(c, 0, 4, c.w, 40, P['stone_w'], 9, rowh=(6, 7), sw=(8, 13)); c.rect(0, 0, c.w, 5, P['stone_w'][4]); c.outline(); return c
cv = low_wall(560); save_img('lowwall', cv); OV.append(dict(img='lowwall', x=1260, y=round(-760 - cv.h / A, 1), w=round(cv.w / A, 1), h=round(cv.h / A, 1), sortY=-760))
BLK.append(('rect', 1260, -800, 1820, -760))
def nest():
    c = Canvas(30, 16); 
    for k in range(80):
        R2 = random.Random(k); x = R2.randint(1, 28); y = R2.randint(4, 15)
        if ((x - 15) / 14) ** 2 + ((y - 10) / 6) ** 2 < 1: c.put(x, y, P['wood'][R2.randint(1, 4)])
    c.ellipse(15, 7, 3, 2, P['gold'][5]); c.outline(); return c, (15, 15), None
place('nest', nest(), 1560, -830 + 40, block=False, sort_off=10, shadow=False)

# chests (interactables) ----------------------------------------------------------------------------
def chest(id_, x, y, kind, items, need=None, hint='', room='out', show=True, gold=False, msg=None):
    if show:
        it = PR.chest(1, 'gold' if gold else 'wood'); place('chest_gold' if gold else 'chest', it, x, y, shadow=True)
        OV[-1]['tag'] = id_
        save_img('chest_open', PR.chest(1, 'wood', True)[0])
    CHESTS.append(dict(id=id_, x=x, y=y, kind=kind, items=items, need=need, hint=hint, room=room, msg=msg))
chest('a_chest_tailor_yard', 2150, -130, 'easy', [['potion', 1], ['herb_red', 2]], hint='리네트 재봉소 뒤뜰 · 빨랫줄 옆 바구니')
CHESTS[-1]['basket'] = True
OV.pop(); place('basket', PR.basket(), 2150, -130); OV[-1]['tag'] = 'a_chest_tailor_yard'
chest('a_chest_scarecrow', -615, 612, 'easy', [['spd_s', 1], ['m_hardwood', 2]], hint='하로의 밭 · 허수아비 옆 건초 더미')
chest('a_chest_gate_supply', 985, 618, 'easy', [['torch', 2], ['antidote', 1]], hint='남문 경비 초소 뒤편 보급 상자')
chest('a_hidden_bench', 360, 445, 'hidden', [['feather', 1]], hint='광장 서쪽 가장자리 이끼 낀 벤치 밑 (반짝임)', show=False)
chest('a_chest_tak', 1205, 548, 'later', [['hs_tak', 1]], need='oath8', gold=True, show=False, hint='분수 옆 연못 · 금빛 사슬 상자',
      msg='금빛 사슬이 단단히 감겨 있다. 「여덟 개의 맹세가 모이면 열린다」')
chest('a_chest_granny_roof', 1745, -700, 'later', [['potion_m', 2]], need='earth_crystal', hint='엘스베트 집 뒤 · 까치둥지 담장 아래 움푹 꺼진 골목',
      msg='담장 위 까치둥지에서 무언가 반짝인다. 땅이 움푹 꺼져 손이 닿지 않는다… (대지의 수정이 있으면 발판을 세울 수 있을 것 같다)', show=False)
# A3 toys (토비의 보물지도)
for i, (x, y, where) in enumerate([(250, -150, '대장간 뒤'), (600, -180, '촌장 집 울타리'), (900, 505, '분수 꽃밭')]):
    SPOTS.append(dict(id='a3_toy_%d' % (i + 1), x=x, y=y, r=46, kind='toy', where=where))

# ---------------------------------------------------------------- doors & interiors
INT_X = 4400
def add_room(id_, name, room, ox, oy):
    rw, rh = room.rw, room.rh
    save_img('int_' + id_, room.c)
    r = dict(id=id_, name=name, x0=ox, y0=oy, x1=round(ox + rw / A, 1), y1=round(oy + rh / A, 1), dark=True, bgimg='int_' + id_)
    r['blocks'] = [[round(ox + b[0] / A, 1), round(oy + b[1] / A, 1), round(ox + b[2] / A, 1), round(oy + b[3] / A, 1)] for b in room.blocks]
    ROOMS.append(r)
    dx, dy = room.door
    r['exit'] = dict(x=round(ox + dx / A, 1), y=round(oy + dy / A, 1), w=round(IN.GAP / A, 1))
    r['spots'] = {k: [round(ox + v[0] / A, 1), round(oy + v[1] / A, 1)] for k, v in room.spots.items()}
    return r
def link(bkey, id_, label, room_r, idx=0, locked=None):
    if locked:
        dx, dw = T[bkey]['doors'][idx]; DOORS.append(dict(id=id_, x=round(dx, 1), y=T[bkey]['y'], w=round(dw, 1), locked=locked, label=label)); return
    dx, dw = T[bkey]['doors'][idx]
    DOORS.append(dict(id=id_, x=round(dx, 1), y=T[bkey]['y'], w=round(dw, 1), to=room_r['id'], label=label,
                      inside=[room_r['exit']['x'], room_r['exit']['y'] - 70]))
    room_r['back'] = [round(dx, 1), T[bkey]['y'] + 40]
slot = [0]
def next_origin(rw, rh):
    x = INT_X + slot[0] * 1400; slot[0] += 1; return x, 0

# tool shop
r = IN.Room(500, 320, 'plaster', 'wood', 11)
r.put(IN.shelf(100, 84, 'bottles', 1), 90, 98); r.put(IN.shelf(100, 84, 'jars', 2), 200, 98); r.put(IN.shelf(90, 84, 'bottles', 3), 420, 98)
r.window(300); r.put(IN.counter(150), 250, 176); r.spots['keeper'] = (250, 140)
r.put(PR.barrel(1), 60, 280); r.put(PR.crate(2), 440, 286); r.put(PR.sacks(1), 400, 290); r.put(IN.rug(110, 44, 'cloth_green'), 250, 270, block=False)
x0, y0 = next_origin(0, 0); R_tool = add_room('tool', '도구상점 「보따리」', r, x0, y0); link('tool', 'd_tool', '도구상점 「보따리」', R_tool)
# smithy
r = IN.Room(520, 330, 'stone', 'stone', 12)
r.put(IN.forge(100), 110, 100); r.put(PR.anvil(), 200, 180); r.put(IN.shelf(90, 80, 'weapons', 4), 330, 92); r.put(PR.weapon_rack(), 440, 100)
r.put(PR.barrel(3, True), 60, 200); r.put(PR.woodpile(3), 470, 260); r.spots['keeper'] = (240, 170)
r.put(IN.trapdoor(), 90, 300, block=False); r.spots['trap'] = (90, 285)
x0, y0 = next_origin(0, 0); R_smith = add_room('smith', '대장간', r, x0, y0); link('smith', 'd_smith', '대장간', R_smith)
# tailor
r = IN.Room(500, 320, 'plaster', 'wood', 13)
r.put(IN.shelf(100, 84, 'cloth', 5), 90, 98); r.put(IN.shelf(100, 84, 'cloth', 6), 410, 98); r.window(230)
r.put(IN.mannequin('cloth_purple'), 190, 170); r.put(IN.mannequin('cloth_red'), 320, 170); r.put(IN.mirror(), 460, 180)
r.put(IN.table(70, 2), 120, 250); r.put(IN.rug(120, 46, 'cloth_purple'), 250, 280, block=False); r.spots['keeper'] = (250, 200)
x0, y0 = next_origin(0, 0); R_tailor = add_room('tailor', '리네트 재봉소', r, x0, y0); link('tailor', 'd_tailor', '리네트 재봉소', R_tailor)
# dojo
r = IN.Room(620, 360, 'wood', 'dojo', 14)
for x in (120, 200, 420, 500): r.put(IN.scroll_banner(), x, 70, block=False)
r.put(PR.weapon_rack(), 60, 110); r.put(PR.weapon_rack(), 560, 110); r.put(IN.mat(240, 130), 310, 290, block=False); r.put(PR.dummy(4), 310, 150)
r.spots['scroll'] = (310, 100)
x0, y0 = next_origin(0, 0); R_dojo = add_room('dojo', '바렌 도장', r, x0, y0); link('dojo', 'd_dojo', '바렌 도장', R_dojo)
# hero's house (lodging)
r = IN.Room(420, 290, 'plaster', 'wood', 15)
r.put(IN.bed(1, 'cloth_green'), 60, 170); r.put(IN.table(56, 3), 300, 200); r.put(IN.chair(), 260, 205); r.put(IN.fireplace(64), 200, 100)
r.put(IN.cradle(), 370, 150); r.spots['cradle'] = (370, 140); r.window(320, 28, 30); r.put(IN.rug(100, 40, 'cloth_blue'), 210, 260, block=False)
x0, y0 = next_origin(0, 0); R_hero = add_room('hero', '필멸자의 집', r, x0, y0); link('hero', 'd_hero', '필멸자의 집', R_hero)
# chief
r = IN.Room(560, 340, 'plaster', 'wood', 16)
r.put(IN.shelf(110, 86, 'books', 7), 90, 100); r.put(IN.fireplace(76), 290, 100); r.put(IN.shelf(110, 86, 'books', 8), 480, 100)
r.put(IN.table(90, 4), 300, 220); r.put(IN.chair(), 240, 228); r.put(IN.chair(), 360, 228); r.put(IN.rug(160, 60, 'cloth_red'), 300, 300, block=False)
r.put(IN.trapdoor(), 480, 300, block=False); r.spots['trap'] = (480, 285)
x0, y0 = next_origin(0, 0); R_chief = add_room('chief', '촌장 오스왈드의 집', r, x0, y0); link('chief', 'd_chief', '촌장 오스왈드의 집', R_chief)
# 바렌's house
r = IN.Room(420, 290, 'wood', 'wood', 17)
r.put(IN.bed(2, 'cloth_blue'), 360, 170); r.put(IN.table(56, 5), 160, 200); r.put(IN.chair(), 120, 205); r.put(PR.weapon_rack(), 230, 100)
r.put(IN.shelf(80, 80, 'books', 9), 70, 96); r.spots['letter'] = (160, 190)
x0, y0 = next_origin(0, 0); R_baren = add_room('baren', '사범의 집', r, x0, y0); link('baren', 'd_baren', '사범의 집', R_baren)
# cellars (trapdoors)
r = IN.Room(400, 270, 'cellar', 'dirt', 18)
r.put(PR.barrel(7), 60, 150); r.put(PR.crate(4), 340, 160); r.put(IN.strongbox(), 200, 140); r.spots['taxbox'] = (200, 128)
r.put(IN.shelf(80, 80, 'jars', 10), 120, 96)
x0, y0 = next_origin(0, 0); R_cc = add_room('chief_cellar', '촌장 집 지하실', r, x0, y0)
r = IN.Room(400, 270, 'cellar', 'dirt', 19)
r.put(PR.crate(5), 70, 160); r.put(PR.barrel(8), 340, 150); r.put(PR.sacks(2), 300, 230)
r.c.blit(IN.cracked_wall_patch()[0], 170, IN.BW - 70); r.spots['crack'] = (200, IN.BW + 14)
x0, y0 = next_origin(0, 0); R_fc = add_room('forge_cellar', '대장간 지하 창고', r, x0, y0)
for (src, dst) in ((R_smith, R_fc), (R_chief, R_cc)):
    tp = src['spots']['trap']
    DOORS.append(dict(id='trap_' + dst['id'], room=src['id'], x=tp[0], y=tp[1], w=50, kind='trap', to=dst['id'], label=dst['name'],
                      inside=[dst['exit']['x'], dst['exit']['y'] - 70]))
    dst['back'] = [tp[0], tp[1] + 60]; dst['ladder'] = True
CHESTS.append(dict(id='a_chest_forge_cellar', x=R_fc['spots']['crack'][0], y=R_fc['spots']['crack'][1], kind='later', items=[['m_iron_ingot', 3], ['charm_luck', 1]],
                   need='bomb', room='forge_cellar', hint='대장간 지하 창고 · 금 간 벽 뒤',
                   msg='벽에 금이 가 있다. 안쪽이 비어 있는 소리가 난다… (폭탄이나 투척 곡괭이로 부술 수 있을 것 같다)'))
# locked doors
link('granny', 'd_granny', '엘스베트의 집', None, locked='엘스베트는 분수 곁에 있다. 집은 비어 있다.')
link('herb', 'd_herb', '세레스의 약초 오두막', None, locked='쓴 약초 냄새가 난다. 세레스는 밖에 있다.')
link('farm', 'd_farm', '하로의 농가', None, locked='하로는 밭에 나가 있다.')
link('hs1', 'd_hs1', '민가', None, locked='문이 잠겨 있다.'); link('hs2', 'd_hs2', '민가', None, locked='문이 잠겨 있다.')

# ---------------------------------------------------------------- ground (outdoor room)
G = Ground(ROOM_OUT['x0'], ROOM_OUT['y0'], ROOM_OUT['x1'], ROOM_OUT['y1'])
G.grass()
mead = G.mask(lambda d, P_: [d.ellipse([*P_(-1250, -880), *P_(2450, -600)], fill=255), d.ellipse([*P_(-1200, -700), *P_(-600, 140)], fill=255),
                            d.ellipse([*P_(1700, -900), *P_(2450, -300)], fill=255)], blur=20)
G.flowers(mead, .006, seed=4); G.flowers(np.ones_like(mead), .0007, seed=5)
def path(pts, w):
    def f(d, P_):
        q = [P_(*p) for p in pts]; d.line(q, fill=255, width=int(w * A), joint='curve')
        for p in q: d.ellipse([p[0] - w * A / 2, p[1] - w * A / 2, p[0] + w * A / 2, p[1] + w * A / 2], fill=255)
    return f
dirt_m = np.zeros((G.H, G.W), np.float32)
for pts, w in [([(560, 560), (300, 560), (-430, 560), (-520, 420), (-520, 180), (-560, 60)], 80),             # yard -> west lane
               ([(-520, 300), (-800, 300), (-900, 250)], 70), ([(-560, 60), (-800, 40), (-1000, -120), (-1000, -330)], 64),   # farm / herb hut
               ([(-520, 180), (-470, -100), (-460, -280), (-300, -340), (0, -350), (190, -360)], 64),              # west stairs -> hero house
               ([(780, -90), (780, -300), (790, -420)], 70), ([(250, -330), (600, -260), (780, -250)], 56),
               ([(1170, -250), (1320, -280), (1380, -340)], 60), ([(1250, -90), (1500, -200), (1720, -330), (1745, -700)], 56),
               ([(1790, 330), (1790, 60), (1950, -100), (2150, -120)], 60),                                 # alley -> tailor back yard
               ([(-215, 445), (-215, 520)], 60), ([(-210, 90), (-210, 160), (-470, 160)], 50), ([(250, -150), (450, -150)], 40),
               ([(680, 690), (680, 790)], 200)]:
    dirt_m = np.maximum(dirt_m, G.mask(path(pts, w), rough=1.4, seed=len(pts)))
G.layer(dirt_m, G.dirt()); G.edge_dark(dirt_m, .8)
sand_m = G.mask(lambda d, P_: [d.rounded_rectangle([*P_(-440, 455), *P_(610, 692)], radius=int(60 * A), fill=255),
                               d.ellipse([*P_(-900, -80), *P_(-560, 200)], fill=255)], rough=1.2, seed=3)
G.layer(sand_m, G.sand()); G.edge_dark(sand_m, .8)
cob_m = G.mask(lambda d, P_: [d.rounded_rectangle([*P_(420, 230), *P_(1265, 700)], radius=int(120 * A), fill=255),
                              d.rectangle([*P_(1200, 315), *P_(2390, 470)], fill=255), d.rectangle([*P_(700, -95), *P_(860, 260)], fill=255),
                              d.rectangle([*P_(-10, 238), *P_(470, 330)], fill=255), d.rectangle([*P_(560, 640), *P_(800, 790)], fill=255),
                              d.rounded_rectangle([*P_(700, -260), *P_(870, -90)], radius=10, fill=255)], rough=.8, seed=9)
G.layer(cob_m, G.cobble(warm=True)); G.edge_dark(cob_m, .7, 1.5)
# fields
car = G.mask(lambda d, P_: d.rectangle([*P_(-1230, 290), *P_(-520, 460)], fill=255), rough=.6, seed=13)
G.soil_rows(car); G.crops(car, 'carrot')
pum = G.mask(lambda d, P_: d.rectangle([*P_(-1170, 510), *P_(-700, 680)], fill=255), rough=.6, seed=14)
G.soil_rows(pum, period=14, seed=44); G.crops(pum, 'pumpkin')
herbs = G.mask(lambda d, P_: [d.rectangle([*P_(-1230, -300), *P_(-1070, -220)], fill=255), d.rectangle([*P_(-900, -300), *P_(-780, -220)], fill=255)], rough=.6, seed=15)
G.soil_rows(herbs, period=8, seed=45); G.flowers(herbs, .05, ('#8a60c8', '#e0e0f0', '#5ab040', '#f0d050'), seed=8)
# flower beds: fountain ring + chief yard + granny
fl = G.mask(lambda d, P_: d.ellipse([*P_(777 - 200, 418 - 112), *P_(777 + 200, 418 + 112)], fill=255), blur=2) - \
     G.mask(lambda d, P_: d.ellipse([*P_(777 - 150, 418 - 78), *P_(777 + 150, 418 + 78)], fill=255), blur=2)
fl = np.clip(fl, 0, 1)
bed = np.zeros((G.H, G.W, 3), np.float32); bed[:] = C('#2e5a26'); bn = fbm(G.H, G.W, 77, (6, 3), (.6, .4)); bed *= (0.8 + bn * .45)[..., None]
G.layer(fl, bed); G.flowers(fl, .22, seed=9)
fl2 = G.mask(lambda d, P_: [d.rectangle([*P_(600, -150), *P_(740, -120)], fill=255), d.rectangle([*P_(900, -150), *P_(1150, -120)], fill=255),
                            d.rectangle([*P_(1330, -320), *P_(1440, -296)], fill=255), d.rectangle([*P_(470, -330), *P_(560, -300)], fill=255)], blur=1.5)
G.layer(fl2, bed); G.flowers(fl2, .25, seed=10)
# water
G.water(1120, 590, 112, 62, seed=61)
G.water(1030, -250, 72, 36, seed=62)
BLK += [('ell', 1120, 590, 118, 66), ('ell', 1030, -250, 78, 40)]
# chest visible under the pond water (a_chest_tak lies at the bottom, gold chains)
# shadows of everything
for sh in SHADOWS:
    if sh[0] == 'ell': G.shadow(lambda d, P_, s=sh: d.ellipse([*P_(s[1] - s[3], s[2] - s[4]), *P_(s[1] + s[3], s[2] + s[4])], fill=255), k=sh[5], blur=3)
    else: G.shadow(lambda d, P_, s=sh: d.polygon([P_(*p) for p in s[1]], fill=255), k=sh[2], blur=5)
# terrace top: slightly lighter hill grass + wall shadow below the wall
for (a, b, y) in TER:
    G.shadow(lambda d, P_, a=a, b=b, y=y: d.rectangle([*P_(a, y - 2), *P_(b + 20, y + 16)], fill=255), k=.6, blur=3)
# stairs decals (main + west)
def stairs_img(w, h, n):
    c = Canvas(int(w * A), int(h * A)); st = P['stone']
    for i in range(n):
        y0 = int(i * c.h / n); y1 = int((i + 1) * c.h / n); c.rect(0, y0, c.w, y1, st[4 - i % 2]); c.hline(0, c.w, y0, st[5]); c.hline(0, c.w, y1 - 1, st[1])
    c.rect(0, 0, 3, c.h, st[2]); c.rect(c.w - 3, 0, c.w, c.h, st[2]); return c
im = Image.fromarray(np.clip(G.rgb, 0, 255).astype(np.uint8))
def decal(cv, wx, wy):
    px_, py_ = G.P(wx, wy); i2 = cv.img(); im.paste(i2, (int(px_), int(py_)), i2)
decal(stairs_img(120, 56, 5), 720, -140); decal(stairs_img(80, 56, 5), -500, -290)
decal(PR.grate()[0], 777 - 33, 262 - 18)
decal(stairs_img(50, 20, 2), 470, -300) if False else None
# the gold-chained chest seen through the clear pond water
gc = PR.chest(1, 'gold')[0].img(); gc = Image.blend(gc, Image.new('RGBA', gc.size, (40, 110, 140, 255)), .35); gc.putalpha(PR.chest(1, 'gold')[0].img().split()[3])
px_, py_ = G.P(1185, 560); im.paste(gc, (int(px_), int(py_)), gc)
G.rgb = np.asarray(im).astype(np.float32)
ground_chunks, ground_im = G.save_chunks(OUT, 'g_out')
ROOM_OUT['bg'] = ground_chunks

# ---------------------------------------------------------------- collision grids
def grid_for(room, shapes):
    gw = int(math.ceil((room['x1'] - room['x0']) / CELL)); gh = int(math.ceil((room['y1'] - room['y0']) / CELL))
    m = Image.new('L', (gw, gh), 0); d = ImageDraw.Draw(m); cut = Image.new('L', (gw, gh), 0); dc = ImageDraw.Draw(cut)
    def P_(x, y): return ((x - room['x0']) / CELL, (y - room['y0']) / CELL)
    for s in shapes:
        if s[0] == 'rect': d.rectangle([*P_(s[1], s[2]), *P_(s[3], s[4])], fill=255)
        elif s[0] == 'ell': d.ellipse([*P_(s[1] - s[3], s[2] - s[4]), *P_(s[1] + s[3], s[2] + s[4])], fill=255)
        elif s[0] == 'poly': d.polygon([P_(*p) for p in s[1]], fill=255)
        elif s[0] == 'cutrect': dc.rectangle([*P_(s[1], s[2]), *P_(s[3], s[4])], fill=255)
    a = (np.asarray(m) > 0) & ~(np.asarray(cut) > 0)
    bits = np.packbits(a.ravel())
    return dict(cell=CELL, w=gw, h=gh, b64=base64.b64encode(bits.tobytes()).decode()), a
ROOM_OUT['grid'], gridA = grid_for(ROOM_OUT, BLK)
for r in ROOMS[1:]:
    r['grid'], _ = grid_for(r, [('rect', *b) for b in r['blocks']]); del r['blocks']

# ---------------------------------------------------------------- minimap (whole outdoor map at 0.12 px/world)
MS = 0.12
def compose_outdoor(scale, labels=False):
    W_ = int((ROOM_OUT['x1'] - ROOM_OUT['x0']) * scale); H_ = int((ROOM_OUT['y1'] - ROOM_OUT['y0']) * scale)
    base = ground_im.resize((W_, H_), Image.LANCZOS).convert('RGBA')
    cache = {}
    for o in sorted(OV, key=lambda o: o['sortY']):
        key = (o['img'], round(o['w'] * scale), round(o['h'] * scale))
        if key not in cache:
            src = Image.open(os.path.join(OUT, IMGS[o['img']]['src'])).convert('RGBA')
            cache[key] = src.resize((max(1, key[1]), max(1, key[2])), Image.LANCZOS)
        base.alpha_composite(cache[key], (int((o['x'] - ROOM_OUT['x0']) * scale), int((o['y'] - ROOM_OUT['y0']) * scale)))
    return base
mini = compose_outdoor(MS); mini.convert('RGB').save(os.path.join(OUT, 'minimap.jpg'), quality=86)
OVD = os.environ.get('TA_OVERVIEW_DIR', '/tmp/ta')   # dev-only overview renders (not shipped)
os.makedirs(OVD, exist_ok=True)
compose_outdoor(0.6).convert('RGB').save(os.path.join(OVD, 'overview_raw.png'))

# ---------------------------------------------------------------- level.json
DIVE_EXTRA = [dict(id='pond', name='촌장 집 연못', x=1030, y=-250, r=96, item='hipotion', theme='mud', hidden=True)]
lvl = dict(world=[1280, 720], bounds=[ROOM_OUT['x0'], ROOM_OUT['y0'], 99999, 99999], blocks=[], overlays=[], overlayImgs=[],
           ta=dict(v=1, scale=A, imgs=IMGS, rooms=ROOMS, overlays=OV, doors=DOORS, signs=SIGNS, chests=CHESTS, spots=SPOTS, labels=LABELS,
                   minimap=dict(src='minimap.jpg', s=MS), gate=dict(x0=560, x1=800, y=690), slimeZone=[-380, 490, 560, 672],
                   npcs=dict(a_chief=[720, -175], a_granny=[690, 292], a_kid=[[960, 470], [960, 560]], a_guard=[872, 612], a_farmer=[-860, 490],
                             a_herb=[-990, -315], a_bard=[1250, 640], sm_A=[-120, 505]),
                   talk=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npc_lines.json'))),
                   inside=dict(a_tool=R_tool['spots']['keeper'], a_smith=R_smith['spots']['keeper'], a_tailor=R_tailor['spots']['keeper'])))
json.dump(lvl, open(os.path.join(TOWN, 'assets', 'level.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print('rooms', len(ROOMS), 'overlays', len(OV), 'imgs', len(IMGS), 'doors', len(DOORS), 'chests', len(CHESTS), 'assets %.1f MB' % (tot / 1e6))
