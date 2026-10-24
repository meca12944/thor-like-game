"""제1던전 「아라크네의 폐공방」 (1장, owner 10-23 「제1던전까지」; split with the town-art room = parts, monster room = champions / boss).
One joined map like the temple: 지하 1층 「실 공방」 (48x30) on top, a sloping passage, 지하 2층 「고치 저장고」 (48x30) below; the boss room
「재단사의 방」 (28x20) behind the sealed door is its own map. Tiles are carved here from rooms + corridors (no hand-typed rows), the hd layer
(code ground: worn flagstones, plank floors in the workrooms, wall tops + a 1-tile stone front with thread strands; the art room's D=3 parts) is
painted on top. Felt's f_arachne_gate becomes the way in (maps/src/felt.json keeps the text; build_felt.py adds the link + an 'arachne' spawn).
python3 tools/hd/build_arachne.py [parts dir]   -> maps/arachne.json, maps/arachne_boss.json, assets/world/arachne/*   test: ?go=arachne"""
import os, sys, json, shutil
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'handoff', 'claude', 'felt_grok_build', 'final')
OUT = os.path.join(ROOT, 'assets', 'world', 'arachne'); os.makedirs(OUT, exist_ok=True)
PJ = json.load(open(os.path.join(SRC, 'parts.json')))['parts']
PAL = json.load(open(os.path.join(SRC, '..', '..', 'felt_grok_layout', 'palette.json')))
T, D, GD = 16, 3, 3
LEG = {'#': 'wall', '.': 'floor', ',': 'floor_moss', '%': 'floor_crack', 'o': {'ground': 'floor', 'hop': True}, 'U': {'ground': 'floor', 'obj': 'stairs_up'},
       'B': {'ground': 'floor', 'obj': 'boss_door'}, 'C': {'ground': 'floor', 'obj': 'chest'}, 'p': {'ground': 'floor', 'deco': 'pillar', 'solid': True}}

class Grid:
    def __init__(s, w, h): s.w, s.h = w, h; s.g = [['#'] * w for _ in range(h)]
    def room(s, x, y, w, h, c='.'):
        for j in range(y, y + h):
            for i in range(x, x + w): s.g[j][i] = c
    def put(s, x, y, c): s.g[y][x] = c
    def rows(s): return [''.join(r) for r in s.g]

# ---------------- joined map: 지하 1층 (rows 0-29) + 지하 2층 (rows 30-59) ----------------
W, H = 48, 60; G = Grid(W, H); props, objs, spawns_mob, chests = [], [], [], {}
def P(pid, x, y, **k): props.append(dict(part=pid, x=x, y=y, **k))     # x, y = foot point in tiles
def mob(m, x, y): spawns_mob.append({'type': 'spawn', 'mob': m, 'x': x, 'y': y, 'respawn': 0})
# 지하 1층 「실 공방」
G.room(2, 2, 10, 7); G.put(6, 3, 'U')                                   # 입구 계단방 (felt)
G.room(12, 5, 6, 2)                                                     # → 재단실
G.room(18, 2, 13, 8, '.')                                               # 재단실
G.room(23, 10, 2, 3)                                                    # → 베틀방
G.room(13, 13, 23, 10)                                                  # 베틀방 (champion)
G.room(6, 17, 7, 2)                                                     # → 마네킹 창고
G.room(2, 13, 10, 13)                                                   # 마네킹 창고
G.room(36, 17, 4, 2)                                                    # → 비탈방
G.room(38, 12, 8, 16)                                                   # 비탈 위
G.room(41, 28, 3, 6)                                                    # 비탈 통로 (실 커튼) → 지하 2층
# 지하 2층 「고치 저장고」
G.room(4, 34, 40, 12)                                                   # 고치 홀 (champion)
G.room(10, 46, 2, 2); G.room(35, 46, 2, 2)                              # → 실패 탑 방, → 보스 앞방
G.room(3, 48, 15, 9)                                                    # 실패 탑 방
G.room(27, 48, 17, 10)                                                  # 보스 앞방 (비석)
G.put(35, 57, 'B')                                                      # 봉인된 문 → 재단사의 방
G.room(33, 3, 4, 5)                                                     # 숨은 방 (재단실 동쪽 벽 뒤): 금 간 벽 (31,5)을 조사하면 무너진다
G.put(32, 5, '.')
SECRET = [(31, 5)]
G.put(35, 6, 'C'); chests['35,6'] = {'id': 'ar_secret', 'loot': [['heart_piece', 1], ['potion', 1]]}
for x, y in ((16, 38), (24, 38), (32, 38), (16, 42), (24, 42), (32, 42)): G.put(x, y, 'p')   # 고치 홀 기둥 (막힘, 필살기 그늘 X — 보스방만)
for x in range(19, 30): G.put(x, 40, 'o') if x not in (24,) else None                       # 갈라진 바닥 틈 (구멍), 가운데 한 칸 다리
G.put(4, 7, 'C'); chests['4,7'] = {'id': 'ar_c1', 'loot': [['potion', 1]]}
G.put(3, 24, 'C'); chests['3,24'] = {'id': 'ar_c2', 'loot': [['potion', 1], ['bomb', 1]]}
G.put(4, 55, 'C'); chests['4,55'] = {'id': 'ar_c3', 'loot': [['potion', 2]]}
# props (the art room's parts; foot point in tiles)
P('d_stair_arch', 6.5, 3.4, under=0); P('d_waystone', 9.5, 6.95)
P('d_cut_table', 21.5, 5); P('d_cut_table', 27.5, 5); P('d_wardrobe', 30, 3.2); P('d_mannequin', 19, 3.2); P('d_mannequin', 29, 8.5); P('d_web_sheet', 25, 2.9)
P('d_loom_a', 16.5, 15.5); P('d_loom_b', 32.5, 15.5); P('d_spool_rack', 24, 14.2); P('d_thread_pillar', 14.5, 21.5); P('d_thread_pillar', 34.5, 21.5); P('d_bones', 20, 21)
P('d_mannequins', 7, 15); P('d_mannequin', 3.5, 20); P('d_mannequin', 10, 23); P('d_bones', 7, 25); P('d_web_sheet', 11, 13.9)
P('d_web_sheet', 45, 12.9); P('d_bones', 39.5, 26)
P('d_cocoon_wall', 10, 34.9); P('d_cocoon_wall', 38, 34.9); P('d_cocoon_l', 6, 44); P('d_cocoon_l', 42, 37); P('d_cocoon_m', 20, 36.5); P('d_cocoon_m', 28, 37.5)
P('d_cocoon_s', 12, 41); P('d_cocoon_s', 36, 44); P('d_cocoon_m', 30, 44.5); P('d_bones', 9, 38)
P('d_spool_tower', 10.5, 52); P('d_cocoon_s', 4.5, 50); P('d_cocoon_l', 15.5, 55); P('d_web_sheet', 16, 48.9)
P('d_waystone', 31.5, 52.95); P('d_door_arch', 35.5, 57.95); P('d_cocoon_s', 42, 50); P('d_bones', 41, 56)
# objects
objs += [{'type': 'waystone', 'id': 'ws_arachne_in', 'x': 9, 'y': 6, 'name': '폐공방 입구 비석', 'art': 'hd'},
         {'type': 'waystone', 'id': 'ws_arachne_boss', 'x': 31, 'y': 52, 'name': '재단사의 방 앞 비석', 'art': 'hd'},
         {'type': 'champion', 'id': 'champ_c1_loom', 'mob': 'champ_c1_loom', 'x': 24, 'y': 18, 'loot': [['potion', 2], ['bomb', 2]]},
         {'type': 'champion', 'id': 'champ_c1_cocoon', 'mob': 'champ_c1_cocoon', 'x': 24, 'y': 44, 'loot': [['potion', 2], ['antidote', 1]]},
         {'type': 'secret_wall', 'id': 'ar_secret_wall', 'x': 31, 'y': 5, 'flag': 'arachne_secret', 'name': '금 간 벽이 무너졌다 — 숨겨진 방!', 'textDone': '무너진 벽 너머로 좁은 방이 보인다.'},
         {'type': 'sign', 'x': 10, 'y': 3, 'walk': True, 'text': '폐공방 지하 1층 「실 공방」.\n안쪽 베틀방에서 실 끊기는 소리가 난다.'},
         {'type': 'sign', 'x': 42, 'y': 30, 'walk': True, 'text': '실 커튼 너머로 내려가는 비탈길.\n아래층은 고치 저장고다.'},
         {'type': 'clue', 'id': 'ar_note_order', 'x': 20, 'y': 8, 'name': '주문 장부', 'flag': 'ar_note_order', 'textIdle': '재단대 밑에 두꺼운 장부가 떨어져 있다.',
          'text': '왕실 의상실 주문 장부. 마지막 장:\n「왕도 화재의 밤 — 수의 열두 벌. 치수: 사람이 아님.」\n주문자 서명란에 낯익은 문양이 찍혀 있다.\n필멸자: (무심코 가슴께를 누른다) ……', 'textDone': '불탄 밤의 주문 장부. 서명란의 문양이 마음에 걸린다.',
          'textMore': [['quest:q_felt_ledger', '필멸자: 벤의 장부에 있던 서명, 그리고 이 주문자 서명란…\n필멸자: 내 가슴의 문양과 똑같다.\n필멸자: 30년 전 왕도가 불타던 그 밤, 내가 여기 있었다는 건가.']]},   # 제미나이 1장 연결 3
         {'type': 'clue', 'id': 'ar_note_cloth', 'x': 17, 'y': 17, 'name': '베틀에 걸린 천', 'flag': 'ar_note_cloth', 'textIdle': '베틀에 짜다 만 천이 걸려 있다.',
          'text': '천을 짜던 실이 아니다. 사람 머리카락이다.\n무늬 사이로 누군가의 얼굴이 입을 벌리고 있다.\n필멸자: ……여기서 짠 건 옷이 아니었군.', 'textDone': '머리카락으로 짠 천. 얼굴 무늬가 아직 입을 벌리고 있다.'},
         {'type': 'clue', 'id': 'ar_note_mannequin', 'x': 4, 'y': 16, 'name': '꿰맨 마네킹', 'flag': 'ar_note_mannequin', 'textIdle': '이 마네킹만 유난히 사람 같다.',
          'text': '마네킹의 이음매에서 미지근한 것이 배어 나온다.\n안에 든 건 짚이 아니다.\n필멸자: ……보지 마라. 다음으로 간다.', 'textDone': '꿰맨 자리가 아직 미지근하다.'},
         {'type': 'clue', 'id': 'ar_note_cocoon', 'x': 7, 'y': 36, 'name': '작은 고치', 'flag': 'ar_note_cocoon', 'textIdle': '바닥에 떨어진 고치가 꿈틀댄다.',
          'text': '고치 속에서 손톱으로 긁는 소리가 난다.\n칼끝을 대자 소리가 뚝 멈춘다.\n필멸자: ……늦었다.', 'textDone': '이제 아무 소리도 나지 않는다.'},
         {'type': 'clue', 'id': 'ar_note_wall', 'x': 41, 'y': 50, 'name': '벽에 새긴 글', 'flag': 'ar_note_wall', 'textIdle': '벽에 무언가 빽빽하게 긁혀 있다.',
          'text': '「영혼은 실이다. 끊기면 다시 꿰매면 된다.」\n그 아래 수십 번 덧새긴 이름 하나: 「아라크네」.\n자기 이름을 잊지 않으려 한 것처럼.', 'textDone': '덧새긴 이름 「아라크네」.'},
         {'type': 'clue', 'id': 'ar_note_last', 'x': 34, 'y': 4, 'name': '아라크네의 마지막 기록', 'flag': 'ar_note_last', 'textIdle': '수놓인 천 조각이 벽에 걸려 있다.', 'cg': 'cg/cg_arachne_past.png',
          'text': '「다 끝내면, 쉬어도 되겠지.」', 'textDone': '「다 끝내면, 쉬어도 되겠지.」'},
         {'type': 'clue', 'id': 'ar_clue_felix', 'x': 12, 'y': 54, 'name': '펠릭스의 목도리', 'flag': 'felt_felix_items', 'textIdle': '고치 사이에 무언가 굴러다닌다.', 'cg': 'cg/cg_felix_scarf.png',
          'text': '……(말없이 챙긴다)', 'textDone': '펠릭스의 공과 목도리를 챙겼다.'}]   # 토비 퀘스트 「사라진 아이의 실타래」
for m, x, y in (('c1_thread_puppet', 21, 6), ('c1_thread_puppet', 28, 7), ('c1_needle_spider', 6, 19), ('c1_thread_puppet', 8, 22), ('c1_needle_spider', 41, 20),
                ('c1_silmamul', 18, 19), ('c1_needle_spider', 30, 20),
                ('c1_needle_spider', 10, 37), ('c1_silmamul', 36, 37), ('c1_needle_spider', 14, 44), ('c1_silmamul', 40, 43), ('c1_thread_puppet', 8, 52), ('c1_needle_spider', 14, 51)):
    mob(m, x, y)
AREAS = [{'id': 'ar_b1', 'name': '아라크네의 폐공방 · 지하 1층', 'sub': '실 공방', 'x': 0, 'y': 0, 'w': W, 'h': 30},
         {'id': 'ar_b2', 'name': '아라크네의 폐공방 · 지하 2층', 'sub': '고치 저장고', 'x': 0, 'y': 30, 'w': W, 'h': 30}]

# ---------------- 재단사의 방 (boss) ----------------
BG = Grid(28, 20); BG.room(3, 3, 22, 15)
for (x, y) in ((3, 3), (4, 3), (3, 4), (24, 3), (23, 3), (24, 4), (3, 17), (4, 17), (3, 16), (24, 17), (23, 17), (24, 16)): BG.put(x, y, '#')   # rounded corners
for x, y in ((8, 7), (19, 7), (8, 14), (19, 14)): BG.put(x, y, 'p')                          # 4 pillars = the 필살기 shade
BG.put(14, 17, 'U')
BPROPS = [dict(part='d_boss_loom', x=14, y=4.2), dict(part='d_cocoon_throne', x=14, y=6.5), dict(part='d_cocoon_l', x=5, y=6), dict(part='d_cocoon_l', x=23, y=6),
          dict(part='d_bones', x=6, y=15), dict(part='d_bones', x=22, y=15.5), dict(part='d_bones', x=11, y=11), dict(part='d_bones', x=17.5, y=12.5),
          dict(part='d_cocoon_s', x=10, y=5.5), dict(part='d_cocoon_s', x=18.5, y=5.5), dict(part='d_web_sheet', x=5.5, y=4.9), dict(part='d_web_sheet', x=22.5, y=4.9)]

# ---------------- hd: code ground + parts ----------------
pal = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in PAL['base24'] + PAL['accent8']], float)
def hx(c): return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], float)
def paint(rows, name, seed):
    h, w = len(rows), len(rows[0]); GW, GH = w * T * GD, h * T * GD
    yy, xx = np.mgrid[0:GH, 0:GW].astype(float); wx, wy = xx / GD, yy / GD
    rng = np.random.default_rng(seed)
    def vn(scale, sd):
        r = np.random.default_rng(sd); g = r.random((int(h * T / scale) + 3, int(w * T / scale) + 3)); fx, fy = wx / scale, wy / scale; ix, iy = fx.astype(int), fy.astype(int); tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty); a, b, c, d = g[iy, ix], g[iy, ix + 1], g[iy + 1, ix], g[iy + 1, ix + 1]; return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty
    grid = np.array([[c for c in r] for r in rows]); tile = grid[np.clip((wy // T).astype(int), 0, h - 1), np.clip((wx // T).astype(int), 0, w - 1)]
    wall = tile == '#'; pit = tile == 'o'; floor = ~wall & ~pit
    below = np.vstack([grid[1:], np.full((1, w), '#')]); front_t = (grid == '#') & (below != '#')          # wall tiles with floor under them: the visible stone face
    front = front_t[np.clip((wy // T).astype(int), 0, h - 1), np.clip((wx // T).astype(int), 0, w - 1)]
    img = np.zeros((GH, GW, 3)); n1, n2, n3 = vn(14, seed), vn(5, seed + 1), vn(2, seed + 2)
    # flagstones: offset rows of 8x6 world px slabs, mortar, wear
    sx = (wx + (np.floor(wy / 6) % 2) * 4) / 8; sy = wy / 6; fx, fy = sx - np.floor(sx), sy - np.floor(sy); mort = (fx < .08) | (fy < .1); sh = vn(6, seed + 3)
    t = np.clip((n1 * .6 + sh * .4 - .25) / .5, 0, 1)[..., None]; stone = hx('#3e362e') * (1 - t) + hx('#5d4c3c') * t
    img[:] = stone; img[mort] = hx('#241f1a')
    # plank floor in the workrooms (재단실, 베틀방): boards of 4 world px, seams, knots
    plank_box = np.zeros((h, w), bool)
    for (x, y, ww, hh) in PLANK.get(name, []): plank_box[y:y + hh, x:x + ww] = True
    pb = plank_box[np.clip((wy // T).astype(int), 0, h - 1), np.clip((wx // T).astype(int), 0, w - 1)] & floor
    bt = np.clip((n2 * .7 + n3 * .3 - .2) / .6, 0, 1)[..., None]; boards = hx('#42301f') * (1 - bt) + hx('#5b4127') * bt
    img[pb] = boards[pb]; img[pb & ((wy % 4) < .5)] = hx('#2e1a09'); img[pb & ((wx + np.floor(wy / 4) * 13) % 37 < .5)] = hx('#2e1a09')
    # thread tangles / dust on the floor
    th = floor & (vn(1.2, seed + 4) > .83) & (n1 > .55); img[th] = hx('#877360')
    # pits: black with a lighter lip
    img[pit] = hx('#0e0703'); lip = pit & ~np.roll(pit, 3, 0); img[lip] = hx('#241f1a')
    # walls: dark rock tops, the front face = stone courses + hanging thread strands
    img[wall] = hx('#17110c') * (.8 + .4 * n2[wall][:, None]); fy2 = wy % T
    course = front & ((fy2 % 5) < .7); img[front] = hx('#312b26') * (.8 + .4 * n3[front][:, None]); img[course] = hx('#201810')
    lipw = front & (fy2 < 1.4); img[lipw] = hx('#4b4138')
    strand = front & ((np.floor(wx * GD) % 23) == (np.floor(n1 * 40) % 23)) & (fy2 > 2); img[strand] = hx('#c0a98d') * .7
    for (cx, cy) in (SECRET if name == 'arachne' else []):                          # 숨은 방 힌트: the wall face is cracked (zigzag), a draught of dust at its foot
        X0, Y0 = cx * T, cy * T; zz = (np.abs(wx - (X0 + 8 + 3 * np.sin((wy - Y0) * .8))) < .7) & (wy > Y0 + 2) & (wy < Y0 + T) & (wx > X0) & (wx < X0 + T)
        img[zz] = hx('#0e0703'); img[(np.abs(wx - (X0 + 5 + 2 * np.sin((wy - Y0) * 1.3))) < .5) & (wy > Y0 + 7) & (wy < Y0 + T) & (wx > X0)] = hx('#17110c')
        dust = (wy > Y0 + T) & (wy < Y0 + T + 3) & (wx > X0 + 2) & (wx < X0 + T - 2) & (vn(1, seed + 9) > .6); img[dust] = hx('#877360')
    # floor shade under the wall face (contact shadow)
    above_front = np.vstack([np.zeros((1, w), bool), front_t[:-1]])[np.clip((wy // T).astype(int), 0, h - 1), np.clip((wx // T).astype(int), 0, w - 1)]
    sh2 = floor & above_front & ((wy % T) < 5); img[sh2] *= .6
    BY = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - .47)[(yy % 4).astype(int), (xx % 4).astype(int)][..., None]
    img = img + BY * 12; flat = img.reshape(-1, 3); out = np.empty(len(flat), int)
    for i in range(0, len(flat), 1 << 18): out[i:i + (1 << 18)] = np.argmin(((flat[i:i + (1 << 18), None, :] - pal[None]) ** 2).sum(2), 1)
    Image.fromarray(pal[out].reshape(GH, GW, 3).clip(0, 255).astype(np.uint8)).save(os.path.join(OUT, f'{name}_ground.png'), optimize=True)
PLANK = {'arachne': [(18, 2, 13, 8), (13, 13, 23, 10)], 'arachne_boss': []}
used = set()
def hdprops(lst):
    out = []
    for i, q in enumerate(lst):
        p = PJ[q['part']]; used.add(q['part']); big = p['h'] > 140
        o = {'id': f"{q['part']}_{i}", 'img': f"assets/world/arachne/{p['img']}", 'x': q['x'], 'y': q['y'], 'ax': p['ax'], 'ay': p['ay'], 'D': D, 'fade': 1 if big else 0, 'shadow': 0 if q['part'] in ('d_cocoon_wall', 'd_wall_arch') else 1}
        if q.get('solid'): fx, fy = int(q['x']), int(q['y'] - .01); o['solid'] = [fx, fy, fx, fy]
        out.append(o)
    return out
for name, rows in (('arachne', G.rows()), ('arachne_boss', BG.rows())): paint(rows, name, 11 if name == 'arachne' else 23)
# solid tiles under the big parts (looms, racks, tables, wardrobes, towers, the throne)
SOLIDP = {'d_loom_a': 2, 'd_loom_b': 2, 'd_spool_rack': 2, 'd_cut_table': 1, 'd_wardrobe': 1, 'd_mannequins': 2, 'd_spool_tower': 1, 'd_cocoon_l': 1, 'd_cocoon_throne': 3, 'd_boss_loom': 4, 'd_thread_pillar': 0}
def solidify(grid, lst):
    for q in lst:
        r = SOLIDP.get(q['part']);
        if r is None: continue
        y = int(q['y'] - .01)
        for x in range(int(q['x']) - r, int(q['x']) + r + 1 if r else int(q['x']) + 1):
            if grid.g[y][x] == '.': grid.g[y][x] = '#'
solidify(G, props); solidify(BG, BPROPS)
used.add('d_thread_pillar'); PILLAR = {'p': [{'img': 'assets/world/arachne/' + PJ['d_thread_pillar']['img'], 'ax': PJ['d_thread_pillar']['ax'], 'ay': PJ['d_thread_pillar']['ay'], 'flip': False}]}
LIGHTS = [[9, 6.5, 40, '#c8d8ff', .7], [24, 16, 60, '#ffb070', .5], [31, 52.5, 46, '#c8d8ff', .8], [24, 40, 70, '#b080ff', .45], [42, 30, 40, '#cfe0d8', .5]]
m = {'id': 'arachne', 'type': 'dungeon', 'region': 'ch1', 'area': 1, 'mapPos': [0, 0], 'name': '아라크네의 폐공방',
     'title': {'kicker': '1장 · 던전', 'name': '아라크네의 폐공방', 'sub': '실과 고치의 지하'}, 'bgm': 'area01_temple_user01', 'battleBgm': 'battle_champion',
     'tileset': 'dungeon', 'tile': T, 'dark': .55, 'w': W, 'h': H, 'legend': LEG, 'solid': ['#'], 'ground': G.rows(),
     'spawns': {'default': [6.5, 5.5, 'down'], 'felt': [6.5, 5.5, 'down'], 'boss': [35.5, 55.5, 'up']},
     'links': {'stairs_up': {'to': 'felt', 'spawn': 'arachne'}, 'boss_door': {'to': 'arachne_boss', 'spawn': 'default', 'needFlags': ['champ_c1_loom', 'champ_c1_cocoon'],
               'lockedText': '실로 꿰매 봉인된 문. 「베틀방과 고치 홀의 두 파수꾼을 쓰러뜨려라.」',
               'openText': '재단사의 방 봉인이 풀린다', 'doneText': '두 파수꾼을 쓰러뜨렸다! 지하 2층 끝, 실로 꿰맨 문이 풀린다.'}},
     'chests': chests, 'areas': AREAS, 'objects': objs + spawns_mob,
     'hd': {'D': GD, 'ground': 'assets/world/arachne/arachne_ground.png', 'props': hdprops(props), 'lights': LIGHTS, 'decoArt': PILLAR},
     'note': 'GENERATED by tools/hd/build_arachne.py — edit the script'}
open(os.path.join(ROOT, 'maps', 'arachne.json'), 'w').write(json.dumps(m, ensure_ascii=False, indent=1) + '\n')
b = {'id': 'arachne_boss', 'type': 'boss', 'region': 'ch1', 'area': 1, 'mapPos': [0, 0], 'name': '재단사의 방',
     'title': {'kicker': 'BOSS', 'name': '실타래의 재단사 아라크네', 'sub': '영혼을 실에 꿰매는 자'}, 'bgm': 'battle_boss', 'bgm2': 'battle_boss_phase2', 'dark': .4,
     'tileset': 'dungeon', 'tile': T, 'w': 28, 'h': 20, 'legend': LEG, 'solid': ['#'], 'ground': BG.rows(), 'spawns': {'default': [14.5, 15.5, 'up']},
     'links': {'stairs_up': {'to': 'arachne', 'spawn': 'boss'}},
     'boss': {'id': 'arachne', 'kind': 'arachne', 'name': '아라크네', 'x': 14.5, 'y': 9, 'flag': 'boss_arachne', 'intro': 1.8, 'reward': [['heart_piece', 1]], 'exit': {'to': 'felt', 'spawn': 'arachne'}, 'splash': 'assets/boss/arachne_splash.png', 'sub': '영혼을 실에 꿰매는 자'},
     'objects': [], 'hd': {'D': GD, 'ground': 'assets/world/arachne/arachne_boss_ground.png', 'props': hdprops(BPROPS), 'decoArt': PILLAR,
            'phase2': {'threads': [[3, 4, 8.5, 7.5, 1.2], [24.5, 4, 19.5, 7.5, 1.2], [3, 16.5, 8.5, 14.5, 1], [24.5, 16.5, 19.5, 14.5, 1], [8.5, 7.5, 19.5, 7.5, 2], [8.5, 14.5, 19.5, 14.5, 2],
                                   [8.5, 7.5, 8.5, 14.5, 1.5], [19.5, 7.5, 19.5, 14.5, 1.5], [3, 10, 8.5, 11, 1], [24.5, 10, 19.5, 11, 1]],
                       'cocoons': [[6, 9], [11, 7], [17, 7], [22, 9], [10.5, 12.5], [17.5, 12.5]]}, 'lights': [[14, 6, 90, '#b080ff', .6], [14, 14, 70, '#c8d8ff', .35]]},
     'note': 'GENERATED by tools/hd/build_arachne.py — edit the script'}
open(os.path.join(ROOT, 'maps', 'arachne_boss.json'), 'w').write(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
for f in os.listdir(OUT):
    if not f.endswith('_ground.png'): os.remove(os.path.join(OUT, f))
for pid in used: shutil.copy(os.path.join(SRC, PJ[pid]['img']), os.path.join(OUT, PJ[pid]['img']))
print('ok arachne', W, 'x', H, len(m['hd']['props']), 'props', len(spawns_mob), 'mobs; boss room 28 x 20')
print('\n'.join(G.rows())); print(); print('\n'.join(BG.rows()))
