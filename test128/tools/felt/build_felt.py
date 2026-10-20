"""Builds test128/maps/felt.json (chapter 1 town 「펠트」) + assets/world/felt_bg.png from the painted concept felt_2.
python3 tools/felt/build_felt.py <felt_2 png (1536x864)> [overlay.png]
Walkable area = everything outside the BLOCK polygons, authored in concept-image pixels (1536x864, 32 px = 1 tile).
Collision is approximate: tune BLOCK below, re-run, check the overlay."""
import sys, os, json
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
SRC = sys.argv[1]; OV = sys.argv[2] if len(sys.argv) > 2 else None
W, H, T = 48, 27, 32  # tiles, concept px per tile

# solid areas (concept px polygons): buildings, ruins, the raised east yard, rocks, the sky. Everything else is walkable.
BLOCK = [
 [(0, 0), (1536, 0), (1536, 200), (0, 200)],                                              # sky / far ruins
 [(0, 200), (470, 200), (470, 300), (420, 330), (420, 395), (300, 415), (240, 440), (130, 465), (0, 490)],  # NW shop row (weapon / tool shops)
 [(420, 255), (560, 255), (560, 385), (420, 385)],                                        # orange-awning stall in front of the NW row
 [(425, 85), (490, 85), (490, 235), (425, 235)],                                          # guard watchtower
 [(500, 200), (920, 200), (920, 310), (500, 310)],                                        # smithy + royal-wall ruins
 [(920, 200), (1160, 200), (1160, 260), (960, 330), (920, 330)],                          # ruins left of the chapel lane
 [(1060, 200), (1536, 200), (1536, 430), (1200, 420), (1160, 380)],                       # raised east yard + fences
 [(950, 230), (1120, 230), (1200, 330), (1200, 440), (950, 440)],                         # inn (2 floors)
 [(1120, 380), (1250, 380), (1250, 500), (1120, 500)],                                    # house right of the inn
 [(1230, 410), (1400, 410), (1400, 580), (1230, 580)],                                    # herb hut
 [(1400, 420), (1536, 420), (1536, 700), (1400, 700)],                                    # east house (web-covered)
 [(280, 450), (500, 450), (540, 590), (540, 690), (280, 690)],                            # chief Bart's house + its stall
 [(0, 560), (230, 560), (240, 700), (230, 864), (0, 864)],                                # SW house
 [(230, 760), (380, 720), (470, 864), (230, 864)],                                        # SW rocks
 [(510, 600), (760, 600), (760, 830), (510, 830)],                                        # south-centre house
 [(780, 490), (1060, 490), (1060, 690), (780, 690)],                                      # Linette's atelier (royal-tailor ruin)
 [(1110, 640), (1380, 640), (1380, 840), (1110, 840)],                                    # Ben's stall
 [(1380, 700), (1536, 760), (1536, 864), (1300, 864)],                                    # SE webs / rocks
 [(860, 800), (1110, 800), (1110, 864), (960, 864)],                                      # south rocks (right of the south road)
]
# walkable strokes cut back out of BLOCK (lanes the polygons above cover)
CARVE = [
 ([(600, 330), (540, 290), (480, 250)], 56),                        # lane up to the guard watchtower
 ([(930, 340), (960, 280), (1000, 220), (1010, 200)], 60),          # lane up to the chapel
 ([(1240, 610), (1400, 660), (1536, 710)], 60),                     # east road -> Arachne's ruin
 ([(720, 540), (765, 620), (790, 730)], 64),                         # plaza -> south road (between the south house and the atelier)
]
FOUNTAIN = ((690, 478), (82, 52))     # solid ellipse in the plaza

def grid():
    m = Image.new('L', (W * T, H * T), 255); d = ImageDraw.Draw(m)
    for poly in BLOCK: d.polygon(poly, fill=0)
    for pts, w in CARVE:
        d.line(pts, fill=255, width=w)
        for x, y in pts: d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=255)
    (cx, cy), (rx, ry) = FOUNTAIN; d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=0)
    px = m.load(); rows = []
    for ty in range(H):
        r = ''
        for tx in range(W):
            n = sum(px[tx * T + i, ty * T + j] > 0 for i in range(4, T, 8) for j in range(4, T, 8))
            edge = tx in (0, W - 1) or ty in (0, H - 1)
            r += '.' if n >= 9 and not edge else '#'
        rows.append(r)
    for x in range(26, 30): rows[H - 1] = rows[H - 1][:x] + '.' + rows[H - 1][x + 1:]   # south exit gap
    return rows

NPCS = [  # id, tile x, tile y, name, role, art (placeholder sprites from towns A/C/F), idle line
 ('f_bart',    14, 23, '바르트', '이장',      'a_chief',     '30년 전 그 불길을 아직도 기억하네. 하늘까지 붉었지…… 왕도는 하룻밤 사이에 재가 됐어.'),
 ('f_rom',     20, 11, '롬',     '대장장이',  'a_smith',     '괴물한테 칼을 팔 생각은 없어. …돈은 있나? 그럼 얘기가 달라지지.'),
 ('f_sera',    39, 19, '세라',   '약초꾼',    'a_herb',      '요즘 약초를 말리다 보면…… 잎사귀가 꿈틀거리는 것 같아. 내가 피곤한 거겠지?'),
 ('f_gas',     16,  9, '가스',   '경비대장',  'a_guard',     '밤만 되면 어디선가 실 잣는 소리가 들려. 철사를 긁는 것 같은…… 외지인, 해 지면 돌아다니지 마.'),
 ('f_martha',  34, 15, '마르타', '여관 주인', 'c_innkeeper', '외지인은 안 받아. …하룻밤만이야. 문제 일으키면 바로 내쫓을 거다.'),
 ('f_toby',    21, 18, '토비',   '아이',      'a_kid',       '펠릭스가 공방 쪽으로 공 주우러 갔는데 안 돌아와요…… 아저씨, 혹시 못 봤어요?'),
 ('f_oswald',  31,  7, '오스왈드','수도사',   'c_priest',    '오늘 밤에도 기도회가 열립니다. 이 땅의 독을 씻어 낼 것은 오직 기도뿐이오.'),
 ('f_ben',     33, 24, '벤',     '떠돌이 상인','f_merchant', '이 장부, 분명 30년 전 거라는데 글씨가 하나도 안 바랬어. 이상하지 않아?'),
 ('f_luca',    18, 16, '루카',   '시인',      'a_bard',      '「불탄 왕도에 실이 내리고……」 아, 또 이런 가사가 나오네. 요즘은 밝은 노래가 안 써져.'),
 ('f_linette', 29, 22, '리네트', '재봉사',    'a_tailor',    '여긴 왕실 의상실이 있던 자리예요. 언젠가 여기서 영웅의 망토를 만들 거예요!'),
]
DOORS = [  # id, tile x, tile y, name, extra
 ('f_door_weapon', 6, 14, '중고 무기점', {'shop': 'f_weapon'}),
 ('f_door_tool',  11, 12, '잡화점', {'shop': 'f_tool'}),
 ('f_door_smith', 22,  9, '롬의 대장간', {'text': '롬의 대장간 — 모루 강화는 준비 중이다. (placeholder)'}),
 ('f_door_chief', 13, 21, '이장 바르트의 집', {'text': '이장 바르트의 집 — 실내는 준비 중이다. (placeholder)'}),
 ('f_door_herb',  39, 17, '세라의 약초 오두막', {'text': '세라의 약초 오두막 — 실내는 준비 중이다. (placeholder)'}),
 ('f_door_guard', 15,  8, '경비 초소', {'text': '경비 초소와 감시탑 — 실내는 준비 중이다. (placeholder)'}),
 ('f_door_inn',   32, 13, '마르타의 여관', {'heal': 1, 'text': '마르타의 여관 — 하룻밤 쉬었다. 체력이 모두 회복됐다.'}),
 ('f_door_chapel',31,  6, '낡은 예배당', {'text': '낡은 예배당 — 기도회는 밤에만 열린다. 실내는 준비 중이다. (placeholder)'}),
 ('f_door_atelier',27, 21, '리네트의 공방', {'text': '리네트의 공방 (왕실 의상실 폐허) — 실내는 준비 중이다. (placeholder)'}),
]

def main():
    rows = grid()
    # door tiles must be solid (the engine makes npc / door / sign tiles solid anyway); make sure every npc stands next to a walkable tile
    walk = lambda x, y: 0 <= x < W and 0 <= y < H and rows[y][x] == '.'
    for n in NPCS:
        if not walk(n[1], n[2]): print('WARN npc not on road', n[0], n[1], n[2])
    for dd in DOORS:
        if not any(walk(dd[1] + a, dd[2] + b) for a, b in ((0, 1), (1, 0), (-1, 0), (0, -1))): print('WARN door not reachable', dd[0])
    objs = [
     {'type': 'exit', 'x': 26, 'y': 26, 'w': 4, 'h': 1, 'to': 'world', 'spawn': 'townA', 'label': '↓ 차가운 대지 · 월드맵'},
     {'type': 'door', 'id': 'f_arachne_gate', 'x': 47, 'y': 22, 'name': '아라크네의 폐공방',
      'text': '거미줄로 뒤덮인 폐허가 마을 울타리 너머로 이어진다. 안쪽에서 철사 긁는 소리가 난다.\n(1장 보스 던전 — 준비 중)'},
     {'type': 'sign', 'x': 24, 'y': 11, 'text': '펠트\n← 무기점 · 잡화점   ↑ 대장간 · 예배당   → 여관 · 약초 오두막   ↓ 남쪽 길'},
    ]
    for i, x, y, name, extra in DOORS: objs.append(dict({'type': 'door', 'id': i, 'x': x, 'y': y, 'name': name}, **extra))
    for i, x, y, name, role, art, idle in NPCS:
        objs.append({'type': 'npc', 'id': i, 'x': x, 'y': y, 'name': name, 'role': role, 'main': 1 if i in ('f_linette', 'f_bart') else 0, 'idle': idle, 'art': art})
    j = {'id': 'felt', 'type': 'town', 'area': 1, 'region': 'felt', 'name': '펠트',
         'title': {'kicker': 'CHAPTER 1', 'name': '펠트', 'sub': '불탄 왕도 외곽의 빈민가'},
         'bgm': 'town_ruin', 'battleBgm': 'field_battle', 'tileset': 'field', 'tile': 16, 'w': W, 'h': H,
         'bg': 'assets/world/felt_bg.png',
         'note': 'generated by tools/felt/build_felt.py from the felt_2 concept — do not hand-edit; collision is approximate. NPC art = placeholders from towns A/C/F.',
         'legend': {'.': 'dirt', '#': {'ground': 'dirt', 'solid': True}}, 'solid': ['#'],
         'spawns': {'default': [27.5, 24.5, 'up'], 'world': [27.5, 24.5, 'up']},
         'objects': objs, 'ground': rows}
    json.dump(j, open(os.path.join(ROOT, 'maps', 'felt.json'), 'w'), ensure_ascii=False, indent=1)
    src = Image.open(SRC).convert('RGB')
    src.resize((1280, 720), Image.LANCZOS).save(os.path.join(ROOT, 'assets', 'world', 'felt_bg.png'), optimize=True)
    if OV:
        ov = src.copy(); d = ImageDraw.Draw(ov, 'RGBA')
        for ty, r in enumerate(rows):
            for tx, c in enumerate(r):
                if c == '#': d.rectangle([tx * T, ty * T, tx * T + T - 1, ty * T + T - 1], fill=(255, 0, 0, 80))
        for o in objs:
            col = {'npc': (60, 160, 255, 230), 'door': (255, 220, 0, 230), 'exit': (0, 255, 120, 200), 'sign': (255, 255, 255, 230)}[o['type']]
            d.rectangle([o['x'] * T, o['y'] * T, (o['x'] + o.get('w', 1)) * T - 1, (o['y'] + o.get('h', 1)) * T - 1], fill=col)
        ov.save(OV)
    print('ok', sum(r.count('.') for r in rows), 'walkable tiles')
main()
