"""Area-1 field layouts (바람길 field00 + 시작의 숲 field01) for the painted art pass.
Builds the tile grid (collision source of truth) from shapes, keeps every gameplay anchor the rest of the game relies on
(town gate edge 24-30 / y0, east-west edge y17-21, NPC 퀸트 30,8, waystones, champions, temple gate 45-47 / y4),
writes ground/legend/solid/objects/paint into maps/field00.json and maps/field01.json and checks reachability.
Run: python3 tools/area1_layout.py   (then tools/paint_area1.py bakes the painted ground)"""
import os, json, math
from collections import deque
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
def H(x, y, s=0): return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) & 0xffffffff
def rnd(x, y, s=0): return (H(x, y, s) % 10007) / 10007
LEGEND = {".": "grass", ",": "grass_tuft", "'": "grass_flowers", "=": "dirt", "~": "water", "b": "bridge_h", ":": "stones", "#": "cliff", "\"": "tallgrass", "_": "sand",
  "S": "steps",
  "T": {"ground": "grass", "deco": "tree"}, "P": {"ground": "grass", "deco": "pine"}, "Y": {"ground": "grass", "deco": "tree", "solid": False},
  "R": {"ground": "grass", "deco": "boulder"}, "r": {"ground": "grass", "deco": "rocks"}, "u": {"ground": "grass", "deco": "bush"}, "s": {"ground": "grass", "deco": "stump"},
  "m": {"ground": "grass", "deco": "mushrooms", "solid": False}, "f": {"ground": "grass", "deco": "fence"}, "O": {"ground": "dirt", "deco": "pillar_broken"},
  "c": {"ground": "grass", "deco": "crystal"}, "W": {"ground": "grass", "deco": "ruin_wall"}, "L": {"ground": "grass", "deco": "log"},
  "n": {"ground": "grass", "deco": "fern", "solid": False}, "X": {"ground": "dirt", "deco": "rubble"}, "Z": {"ground": "grass"}, "z": {"ground": "dirt"}}
SOLID = ["~", "#", "T", "P", "R", "r", "u", "s", "f", "O", "c", "W", "L", "X", "Z", "z"]
class G:
    def __init__(s, w, h): s.w, s.h = w, h; s.g = [['.'] * w for _ in range(h)]
    def ok(s, x, y): return 0 <= x < s.w and 0 <= y < s.h
    def get(s, x, y): return s.g[y][x] if s.ok(x, y) else '#'
    def set(s, x, y, c):
        if s.ok(x, y): s.g[y][x] = c
    def rect(s, x0, y0, x1, y1, c, only=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if only is None or s.get(x, y) in only: s.set(x, y, c)
    def line(s, pts, width, c, only=None):   # thick polyline (round brush)
        r = width / 2
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = max(1, int(math.hypot(bx - ax, by - ay) * 3))
            for i in range(L + 1):
                px, py = ax + (bx - ax) * i / L, ay + (by - ay) * i / L
                for y in range(int(py - r) - 1, int(py + r) + 2):
                    for x in range(int(px - r) - 1, int(px + r) + 2):
                        if (x + .5 - px) ** 2 + (y + .5 - py) ** 2 <= r * r and (only is None or s.get(x, y) in only): s.set(x, y, c)
    def ellipse(s, cx, cy, rx, ry, c, only=None):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1 and (only is None or s.get(x, y) in only): s.set(x, y, c)
    def trees(s, x, y):  # oak / pine mix
        s.set(x, y, 'P' if rnd(x, y, 7) < .3 else 'T')
    def border(s, depth, keep=()):
        for y in range(s.h):
            for x in range(s.w):
                d = min(x, y, s.w - 1 - x, s.h - 1 - y)
                lim = depth + (1 if rnd(x // 2, y // 2, 3) < .45 else 0) + (1 if rnd(x // 3, y // 3, 5) < .2 else 0)
                if d < lim and not any(x0 <= x <= x1 and y0 <= y <= y1 for (x0, y0, x1, y1) in keep): s.trees(x, y)
    def scatter(s, c, prob, only='.', seed=1, avoid_near=None):
        for y in range(1, s.h - 1):
            for x in range(1, s.w - 1):
                if s.get(x, y) in only and rnd(x, y, seed) < prob:
                    if avoid_near and any(s.get(x + dx, y + dy) in avoid_near for dx in (-1, 0, 1) for dy in (-1, 0, 1)): continue
                    s.set(x, y, c)
    def rows(s): return [''.join(r) for r in s.g]
def walk(rows, start, solid, extra_solid=()):
    h, w = len(rows), len(rows[0]); seen = {start}; q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and rows[ny][nx] not in solid and (nx, ny) not in extra_solid:
                seen.add((nx, ny)); q.append((nx, ny))
    return seen
ROAD_ONLY = set('.,\'"TPRrusmnL_')   # what a road may overwrite

# =====================================================================================  field00  바람길
def field00():
    g = G(56, 36)
    g.border(2, keep=[(23, 0, 31, 3), (53, 16, 55, 22), (30, 33, 34, 35)])
    # thicker woods: SW grove, south-east wood, north-west behind the hill
    for (cx, cy, rx, ry) in [(8, 27, 5, 4.5), (38, 26, 3, 2.6), (20, 31, 4, 2.5), (52, 28, 3, 6), (51, 9, 2.5, 3.5)]:
        g.ellipse(cx, cy, rx, ry, 'T')
    # ---- wind hill plateau (raised ruins) : top x2..16 y2..9, cliff face rows 10-11, east side col 17
    g.rect(2, 2, 16, 9, '.')
    g.rect(1, 10, 17, 11, '#'); g.rect(17, 6, 17, 11, '#'); g.rect(2, 1, 16, 1, 'T')
    g.rect(8, 10, 9, 11, 'S')                                    # stone steps cut into the cliff
    g.rect(4, 4, 12, 8, '=')                                     # ruined plaza
    for (x, y) in [(4, 4), (12, 4), (4, 8), (12, 8)]: g.set(x, y, 'O')
    g.set(6, 3, 'Z'); g.set(10, 3, 'Z')                          # arch legs (paint prop 'arch')
    for x in (2, 3): g.set(x, 7, 'W')
    g.set(14, 3, 'W'); g.set(15, 3, 'W'); g.set(15, 8, 'r'); g.set(2, 3, 'R')
    # ---- hidden path behind the canopies: town road -> plateau north-east corner (rows 2-3), trees south of it (rows 4-5)
    g.rect(17, 2, 23, 3, '.'); g.rect(18, 4, 23, 5, 'T'); g.rect(17, 4, 17, 5, 'T'); g.rect(18, 0, 23, 1, 'T')
    for x in range(18, 24): g.trees(x, 4); g.trees(x, 5)
    # ---- town road (gate x24-30 at y0) down to the crossroads
    g.rect(24, 0, 30, 2, '.')
    g.line([(27.5, 0), (27.5, 11)], 3, '=', ROAD_ONLY)
    g.ellipse(27.5, 14, 4.6, 2.8, '=', ROAD_ONLY)                # crossroads plaza
    # west road to the steps
    g.line([(23.5, 14), (14, 14.5), (9, 13.5), (9, 12)], 2.6, '=', ROAD_ONLY)
    # pond + stream (north-east), sand beach
    g.ellipse(44, 6, 5, 3.2, '_', set('.,\'TP'))
    g.ellipse(44, 6, 4.3, 2.6, '~')
    g.line([(44, 8), (43.2, 13), (44.5, 18), (45.2, 24), (45, 30), (46, 36)], 2.6, '~', set('.,\'TP_"=u'))
    # east road -> bridge -> exit (y17-21)
    g.line([(30, 15.5), (36, 18.5), (48, 19), (56, 19)], 3, '=', set('.,\'TP_"u~'))
    for y in range(g.h):
        for x in range(g.w):
            if g.get(x, y) == '=' and any(g.get(x + dx, y) == '~' for dx in (-2, -1, 1, 2)) and 40 <= x <= 48: pass
    # bridge: road cells that were water
    br = [(x, y) for y in range(16, 22) for x in range(40, 49)]
    road_rows = {}
    for (x, y) in br:
        if g.get(x, y) == '=': road_rows.setdefault(y, []).append(x)
    # redo: stream cells inside the road band become bridge planks
    g2 = G(56, 36); g2.line([(30, 15.5), (36, 18.5), (48, 19), (56, 19)], 3, 'R')
    stream = G(56, 36); stream.line([(44, 8), (43.2, 13), (44.5, 18), (45.2, 24), (45, 30), (46, 36)], 2.6, '~')
    for y in range(g.h):
        for x in range(g.w):
            if g2.get(x, y) == 'R' and stream.get(x, y) == '~': g.set(x, y, 'b')
    # south road -> rockfall (2지역 blocked)
    g.line([(27.5, 16), (30, 23), (32, 29), (32, 36)], 2.6, '=', set('.,\'TP"u'))
    g.rect(30, 32, 34, 35, 'X', set('=.,\'TP'))
    g.rect(29, 33, 35, 35, 'T', set('.,\''))
    # return-later nook west of the south road (cracked boulder, 대지의 수정)
    g.rect(25, 28, 28, 31, 'T', set('.,\'"'))
    g.rect(26, 29, 27, 30, '.'); g.set(28, 29, '.')            # 28,29 = barrier tile (cracked boulder object)
    for (x, y) in [(25, 28), (25, 29), (25, 30), (25, 31), (26, 28), (27, 28), (28, 28), (26, 31), (27, 31), (28, 31), (28, 30), (24, 29), (24, 30)]: g.trees(x, y)
    # tall grass, groves interior clearing, details
    g.rect(14, 20, 19, 23, '"', set('.,\'')); g.rect(47, 11, 51, 14, '"', set('.,\''))
    g.ellipse(8, 27, 2, 1.6, '.', set('TP'))                     # clearing inside the SW grove
    g.line([(12.5, 27), (8, 27)], 1.2, '.', set('TP'))           # its entrance
    g.scatter('u', .012, '.', 11, avoid_near='=~b'); g.scatter('r', .008, '.', 12, avoid_near='=~bS'); g.scatter('s', .004, '.', 13, avoid_near='=~b')
    g.scatter('m', .02, '.', 14); g.scatter("'", .06, '.', 15); g.scatter(',', .10, '.', 16); g.scatter('n', .012, '.', 17)
    for (x, y, c) in [(23, 12, 'R'), (21, 17, 'L'), (36, 9, 'R'), (12, 17, 'R'), (38, 13, 'u'), (34, 22, 'r'), (16, 26, 'L'), (49, 24, 'R')]:
        if g.get(x, y) in '.,\'n': g.set(x, y, c)
    g.rect(17, 2, 23, 3, '.'); g.set(20, 3, ','); g.set(22, 2, "'"); g.set(24, 2, "'"); g.set(24, 3, "'")
    # keep anchor tiles open
    for (x, y) in [(27, 2), (30, 9), (29, 8), (31, 8), (30, 8), (8, 7), (6, 9), (8, 5), (25, 11), (25, 12), (53, 19), (54, 17), (54, 18), (54, 19), (54, 20), (54, 21), (55, 17), (55, 18), (55, 19), (55, 20), (55, 21)]:
        if g.get(x, y) not in '=b': g.set(x, y, '.')
    for y in range(17, 22): g.set(55, y, '=' if 18 <= y <= 20 else '.'); g.set(54, y, '=' if 18 <= y <= 20 else '.')
    rows = g.rows()
    objs = [
     {"type": "exit", "x": 24, "y": 0, "w": 7, "h": 1, "to": "town", "spawn": "gate", "label": "시작 마을"},
     {"type": "exit", "x": 55, "y": 17, "w": 1, "h": 5, "to": "field01", "spawn": "west", "label": "시작의 숲"},
     {"type": "sign", "x": 25, "y": 11, "text": "↑ 시작 마을    ← 바람의 언덕\n→ 시작의 숲 · 고대 숲 신전    ↓ 수정 동굴 (낙석으로 막힘)"},
     {"type": "sign", "x": 34, "y": 29, "text": "낙석으로 길이 막혀 있다. 수정 동굴(2지역)은 아직 갈 수 없다."},
     {"type": "waystone", "id": "ws_windhill", "x": 8, "y": 6, "name": "바람의 언덕 비석"},
     {"type": "chest", "id": "f00_chest_hill", "x": 6, "y": 8, "loot": [["potion", 1], ["m_hardwood", 1]], "note": "ruins on the wind hill (stone steps below the cliff)"},
     {"type": "chest", "id": "f00_chest_canopy", "x": 20, "y": 2, "loot": [["spirit_drop", 1], ["potion", 1]], "note": "hidden: path behind the tree canopies from the town road to the hill (rows 2-3)"},
     {"type": "barrier", "id": "f00_rock_quake", "x": 28, "y": 29, "w": 1, "h": 1, "need": "boss01", "sprite": "boulder_cracked", "verb": "대지의 수정으로 바위를 부쉈다!",
      "text": "금이 간 큰 바위가 길을 막고 있다.\n땅을 울리는 힘(대지의 수정)이 있다면 부술 수 있을 것 같다…"},
     {"type": "chest", "id": "f00_chest_quake", "x": 26, "y": 29, "loot": [["heart_piece", 1], ["m_a1_shared", 2]], "note": "return later: needs 대지의 수정 (boss01 flag)"},
     {"type": "npc", "id": "npc_bori", "x": 30, "y": 8, "sprite": "npc_bard", "name": "순례자 퀸트", "title": "「바람길의 순례자」", "quests": ["q_forest_chiefs", "q_temple_golem"], "idle": "바람이 좋은 날이군. 숲 쪽 길은 이 길을 따라 동쪽이야."},
     {"type": "landmark", "id": "lm_bridge00", "x": 44, "y": 19, "name": "개울 다리"},
     {"type": "landmark", "id": "lm_windhill", "x": 8, "y": 4, "name": "바람의 언덕 유적"},
    ]
    mobs = [("rabbit", 20, 8), ("rabbit", 38, 22), ("mushroom", 15, 18), ("slime", 40, 14), ("slime", 22, 25), ("squirrel", 49, 23), ("mushroom", 8, 27), ("rabbit", 50, 16)]
    paint = {"props": [{"s": "arch", "x": 8.5, "y": 4.0}, {"s": "tablet", "x": 13.5, "y": 6.3}, {"s": "signpost", "x": 22.6, "y": 13.0}],
             "lights": [[8, 5, 1.2], [20, 2, .9], [12, 25, 1], [36, 21, 1], [50, 26, .9]], "leaves": 10}
    return g, rows, objs, mobs, paint, {"default": [27.5, 2.5, "down"], "town": [27.5, 2.5, "down"], "east": [53.5, 19.5, "left"]}

# =====================================================================================  field01  시작의 숲
def field01():
    g = G(64, 40)
    g.border(2, keep=[(0, 16, 3, 22), (29, 0, 35, 2), (31, 37, 36, 39)])
    # temple plateau: cliff x35..61 rows 2..5 (face rows 4-5), trees standing on top (rows 2-3)
    g.rect(35, 2, 61, 5, '#')
    g.rect(44, 4, 48, 5, '=')                                    # gorge to the temple gate (exit 45-47 / y4)
    g.set(44, 4, '#'); g.set(48, 4, '#')
    # stream (north edge -> pond with an island -> south edge)
    g.line([(31.5, 0), (32.5, 6), (32.5, 15), (30.8, 21), (31.2, 26)], 3, '~')
    g.ellipse(31.5, 29.6, 5.2, 3.9, '~')
    g.line([(32, 33), (33.5, 40)], 3, '~')
    g.ellipse(32, 30, 1.7, 1.25, '_')                            # island
    g.rect(26, 30, 29, 30, ':')                                  # stepping stones from the west bank
    g.rect(24, 29, 26, 31, '.', set('TP'))
    # road: west edge -> bridge -> junction -> temple / boar clearing
    road = [(0, 19), (8, 18.5), (15, 16.5), (22, 14.5), (29, 14), (36, 14), (44, 13.5)]
    g.line(road, 3, '=', set('.,\'TP"u'))
    g.line([(44, 13.5), (46, 11), (46, 6), (46, 4)], 3, '=', set('.,\'TP"u'))
    g.line([(42, 15), (42, 21), (45, 23)], 2.4, '=', set('.,\'TP"u'))
    g2 = G(64, 40); g2.line(road, 3, 'R')
    for y in range(g.h):
        for x in range(g.w):
            if g2.get(x, y) == 'R' and g.get(x, y) == '~': g.set(x, y, 'b')
    # boar clearing (open dirt/grass) + south-east wood with the return-later nook
    g.ellipse(49, 25.5, 6.5, 4.2, '.', set('TP"u'))
    g.ellipse(49, 25.5, 4, 2.4, '=', set('.,\''))
    g.rect(55, 29, 61, 36, 'T', set('.,\'"'))
    g.rect(57, 31, 59, 34, '.'); g.set(56, 32, '.')              # nook; 56,32 = cracked boulder barrier
    g.line([(52, 28), (54, 31), (55.5, 32.5)], 1.6, '.', set('.,\'TP"'))
    # wasp meadow (north-west), tall grass
    g.ellipse(15, 7, 7, 4, '.', set('TP'))
    g.rect(19, 4, 23, 7, '"', set('.,\''))
    g.rect(53, 12, 58, 16, '"', set('.,\'')); g.rect(4, 24, 9, 26, '"', set('.,\'')); g.rect(16, 30, 21, 33, '"', set('.,\''))
    # broken rope bridge (return later: 수정 실) -> secluded nook west of the stream (x24..29, y5..10)
    g.rect(23, 2, 30, 11, 'T', set('.,\'"'))
    g.rect(25, 6, 30, 9, '.')
    g.rect(30, 7, 34, 8, 'b')                                     # bridge cells over the stream (barrier object keeps them solid)
    g.rect(35, 7, 36, 8, '.')
    # glade with the odd tree (walk-through 'Y'), as before
    g.rect(4, 28, 13, 35, 'T'); g.rect(5, 29, 12, 34, '.'); g.set(9, 28, 'Y')
    g.rect(14, 28, 14, 35, 'P', set('.,\''))
    # groves for route variety
    for (cx, cy, rx, ry) in [(9, 8.5, 3, 2.5), (25, 18.5, 2.4, 3), (37, 21, 2.2, 2.4), (52, 9, 2.6, 2.2), (24, 35, 3, 2), (45, 34, 4, 2.5), (5, 13, 2, 2.4)]:
        g.ellipse(cx, cy, rx, ry, 'T', set('.,\'"'))
    for (cx, cy, rx, ry) in [(9, 8.5, 1, .8)]: g.ellipse(cx, cy, rx, ry, '.')
    g.scatter('u', .012, '.', 21, avoid_near='=~b:'); g.scatter('r', .007, '.', 22, avoid_near='=~b:'); g.scatter('s', .004, '.', 23, avoid_near='=~b:')
    g.scatter('m', .025, '.', 24); g.scatter("'", .06, '.', 25); g.scatter(',', .10, '.', 26); g.scatter('n', .015, '.', 27)
    for (x, y, c) in [(12, 13, 'R'), (35, 18, 'R'), (50, 18, 'R'), (20, 25, 'L'), (39, 9, 'r'), (58, 21, 'u'), (28, 23, 'R'), (54, 6, 'L'), (60, 11, 'R')]:
        if g.get(x, y) in '.,\'n': g.set(x, y, c)
    # anchors kept open (tests / quests / spawns)
    for (x, y) in [(46, 24), (49, 26), (15, 10), (15, 7), (15, 8), (15, 9), (22, 15), (42, 10), (42, 9), (43, 8), (59, 7), (59, 8), (9, 31), (29, 16), (29, 17), (27, 12), (4, 16), (42, 22), (56, 14),
                   (46, 7), (46, 6), (25, 7), (27, 7), (58, 33)]:
        if g.get(x, y) not in '=b:_': g.set(x, y, '.')
    for x in range(22, 28): g.set(x, 15, '=' if g.get(x, 15) == '=' else '.')
    for y in range(17, 22): g.set(0, y, '=' if 18 <= y <= 20 else '.'); g.set(1, y, '=' if 18 <= y <= 20 else '.')
    for (x0, x1, y) in [(43, 49, 6), (43, 49, 7), (43, 49, 8)]:
        for x in range(x0, x1 + 1):
            if g.get(x, y) in 'TPRrus': g.set(x, y, '.')
    rows = g.rows()
    objs = [
     {"type": "exit", "x": 0, "y": 17, "w": 1, "h": 5, "to": "field00", "spawn": "east", "label": "바람길 (시작 마을)"},
     {"type": "waystone", "id": "ws_temple", "x": 42, "y": 9, "name": "신전 앞 비석"},
     {"type": "landmark", "id": "lm_bridge01", "x": 32, "y": 14, "name": "쉼터 다리"},
     {"type": "landmark", "id": "lm_island", "x": 32, "y": 29, "name": "개울 웅덩이의 섬"},
     {"type": "exit", "x": 45, "y": 4, "w": 3, "h": 1, "to": "dungeon01_b1", "spawn": "default", "label": "고대 숲 신전"},
     {"type": "sign", "x": 4, "y": 16, "text": "← 바람길 · 시작 마을   /   시작의 숲 · 고대 숲 신전 →\n(Shift: 구르기 — 구르는 동안은 무적)"},
     {"type": "sign", "x": 27, "y": 12, "text": "쉼터 다리. 개울 아래쪽 웅덩이 가운데 작은 섬이 보인다…"},
     {"type": "sign", "x": 43, "y": 8, "text": "고대 숲 신전.\n「숲의 두 우두머리가 쓰러질 때, 골렘의 방이 열리리라.」"},
     {"type": "sign", "x": 41, "y": 20, "text": "경고: 이 앞 공터에 거대 왕멧돼지 「돌엄니」 출몰!"},
     {"type": "chest", "id": "f01_chest_glade", "x": 9, "y": 31, "loot": [["potion", 2], ["m_hardwood", 2]], "note": "secret: walk through the odd pale tree (Y) at the top of the ring glade"},
     {"type": "chest", "id": "f01_chest_island", "x": 32, "y": 30, "loot": [["heart_piece", 1]], "note": "secret: stepping stones (:) from the west bank of the pond"},
     {"type": "chest", "id": "f01_chest_cliff", "x": 59, "y": 7, "loot": [["potion", 1], ["m_a1_shared", 3]], "note": "under the temple cliff, east of the gorge"},
     {"type": "hidden", "id": "f01_grass_item", "x": 56, "y": 14, "loot": [["spirit_drop", 1]], "note": "interact in the tall grass where it glints"},
     {"type": "barrier", "id": "f01_bridge_thread", "x": 30, "y": 7, "w": 5, "h": 2, "need": "boss02", "sprite": "bridge_broken", "verb": "수정 실을 기둥에 걸어 끊어진 다리를 건널 수 있게 됐다!",
      "text": "끊어진 밧줄 다리. 건너편 기둥에 줄을 걸 수 있다면…\n(수정 동굴의 힘 「수정 실」이 필요하다)"},
     {"type": "chest", "id": "f01_chest_thread", "x": 26, "y": 7, "loot": [["heart_piece", 1], ["spirit_drop", 1]], "note": "return later: needs 수정 실 (area-2 boss flag boss02)"},
     {"type": "barrier", "id": "f01_rock_quake", "x": 56, "y": 32, "w": 1, "h": 1, "need": "boss01", "sprite": "boulder_cracked", "verb": "대지의 수정으로 바위를 부쉈다!",
      "text": "금이 간 큰 바위. 안쪽에서 반짝이는 것이 보인다.\n땅을 울리는 힘(대지의 수정)이 있다면…"},
     {"type": "chest", "id": "f01_chest_quake", "x": 58, "y": 33, "loot": [["m_a1_shared", 4], ["bomb", 2], ["potion", 1]], "note": "return later: needs 대지의 수정 (boss01 flag)"},
     {"type": "heal", "x": 29, "y": 16, "note": "bench/rest spot: interact to restore HP"},
     {"type": "champion", "id": "champ_boar", "mob": "champ_boar", "x": 49, "y": 26},
     {"type": "champion", "id": "champ_wasp", "mob": "champ_wasp", "x": 15, "y": 7},
    ]
    mobs = [("rabbit", 8, 21), ("mushroom", 12, 23), ("rabbit", 17, 19), ("mushroom", 6, 11), ("wasp", 22, 10), ("squirrel", 24, 13), ("slime", 20, 27), ("slime", 37, 10),
            ("wasp", 37, 17), ("squirrel", 39, 12), ("boar", 52, 16), ("scarecrow", 56, 19), ("sprout", 44, 18), ("boar", 55, 27), ("sprout", 37, 26), ("scarecrow", 28, 36)]
    top = [{"s": ("pine" if rnd(x, 2, 9) < .35 else ("oak_a" if x % 2 else "oak_b")), "x": x + .5 + (rnd(x, 3, 4) - .5) * .8, "y": 3.2 + rnd(x, 1, 5) * .5} for x in range(36, 61, 2) if not 42 <= x <= 50]
    paint = {"props": top + [{"s": "temple_gate", "x": 46.5, "y": 5.05}, {"s": "pillar_broken", "x": 41.2, "y": 6.6, "solid": False}, {"s": "ruin_wall", "x": 50.5, "y": 6.3}],
             "lights": [[9, 31, 1.2], [15, 7, 1], [36, 20, .9], [52, 10, .9], [46, 9, 1.1], [20, 33, .8], [26, 7, 1], [58, 32, .8], [49, 25, 1]], "leaves": 16}
    return g, rows, objs, mobs, paint, {"default": [2.5, 19.5, "right"], "west": [2.5, 19.5, "right"], "world": [2.5, 19.5, "right"], "dungeon": [46.5, 7, "down"]}

def nearest_open(rows, x, y, solid):
    best = None
    for r in range(0, 6):
        for yy in range(y - r, y + r + 1):
            for xx in range(x - r, x + r + 1):
                if 0 <= yy < len(rows) and 0 <= xx < len(rows[0]) and rows[yy][xx] not in solid and rows[yy][xx] not in '=b':
                    d = abs(xx - x) + abs(yy - y)
                    if best is None or d < best[0]: best = (d, xx, yy)
        if best: return best[1], best[2]
    return x, y
def build(mid, fn, respawn):
    g, rows, objs, mobs, paint, spawns = fn()
    # tree canopies are ~4.5 tiles tall: trees just south of a chest / barrier would hide it -> swap them for low props (same collision)
    rows = [list(r) for r in rows]
    for o in objs:
        if o['type'] not in ('chest', 'barrier') or o.get('id') == 'f00_chest_canopy': continue
        for yy in range(o['y'] + 1, o['y'] + o.get('h', 1) + 3):
            for xx in range(o['x'] - 2, o['x'] + o.get('w', 1) + 2):
                if 0 <= yy < len(rows) and 0 <= xx < len(rows[0]) and rows[yy][xx] in 'TP': rows[yy][xx] = 'uursuR'[int(rnd(xx, yy, 77) * 6)]
    rows = [''.join(r) for r in rows]
    # paint props marked solid (temple gate, ruin wall) block their footprint
    p = R + 'maps/' + mid + '.json'; j = json.load(open(p))
    solid = set(SOLID)
    objsolid = {(o['x'], o['y']) for o in objs if o['type'] in ('chest', 'sign', 'heal', 'waystone', 'npc')}
    for o in objs:
        if o['type'] == 'barrier':
            for yy in range(o['y'], o['y'] + o['h']):
                for xx in range(o['x'], o['x'] + o['w']): objsolid.add((xx, yy))
    out = []
    for (k, x, y) in mobs:
        x2, y2 = nearest_open(rows, x, y, solid | {'"'})
        out.append({"type": "spawn", "mob": k, "x": x2, "y": y2, "respawn": respawn})
    j.update({"legend": LEGEND, "solid": SOLID, "ground": rows, "objects": objs + out, "spawns": spawns})
    j["paint"] = dict(paint, bg='world/paint/' + mid + '_bg.webp')
    json.dump(j, open(p, 'w'), ensure_ascii=False, indent=1)
    # ---- reachability check from the default spawn (barriers closed, then open)
    sp = spawns['default']; start = (int(sp[0]), int(sp[1]))
    closed = walk(rows, start, solid, objsolid - {(o['x'], o['y']) for o in objs if o['type'] in ()})
    barrier_cells = {c for o in objs if o['type'] == 'barrier' for c in [(xx, yy) for yy in range(o['y'], o['y'] + o['h']) for xx in range(o['x'], o['x'] + o['w'])]}
    opened = walk(rows, start, solid, objsolid - barrier_cells)
    for o in objs + out:
        if o['type'] in ('chest', 'sign', 'waystone', 'npc', 'heal'):
            adj = [(o['x'] + dx, o['y'] + dy) for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))]
            a, b = any(c in closed for c in adj), any(c in opened for c in adj)
            print(mid, o['type'], o.get('id', o.get('text', '')[:12]), (o['x'], o['y']), 'reach' if a else ('LATER' if b else 'UNREACHABLE'))
        elif o['type'] in ('spawn', 'champion', 'landmark'):
            if (o['x'], o['y']) not in closed: print(mid, 'WARN not reachable', o)
        elif o['type'] == 'exit':
            cells = [(xx, yy) for yy in range(o['y'], o['y'] + o['h']) for xx in range(o['x'], o['x'] + o['w'])]
            print(mid, 'exit', o['to'], 'reach' if any(c in closed for c in cells) else 'UNREACHABLE')
    print('\n'.join(rows))
if __name__ == '__main__':
    build('field00', field00, 30); build('field01', field01, 25)
