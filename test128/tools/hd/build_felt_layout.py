"""Felt composition board (owner 10-23 「그록 그림을 대표로 — 먼저 인게임에 넣어보고 구도를 잡아봐」, with the town-art room).
The Grok key art (tools/hd/keyart/grok_felt.png = Drive 1장_펠트_마을_추천.png) is laid in the game as the hd ground, and every building is
cut out of the same picture as a separate y-sorted prop, so the hero walks in the key art's own composition: around the fountain plaza,
behind houses (they turn see-through), up to the burned castle. The key art is a 3/4 oblique view like the game, so picture positions map
straight to the map with one scale S (world px per picture px). 0 credits. Placeholder art — the real D=3 parts come later in this layout.
python3 tools/hd/build_felt_layout.py [S]   -> maps/felt_layout.json + assets/world/felt_layout/*.png   (?go=felt_layout)"""
import os, sys, json
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
OUT = os.path.join(ROOT, 'assets', 'world', 'felt_layout'); os.makedirs(OUT, exist_ok=True)
S = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8      # world px per picture px: villagers ~20 px, doors ~ hero height
T = 16; D = 1 / S                                            # hd D = picture px per world px
key = Image.open(os.path.join(HERE, 'keyart', 'grok_felt.png')).convert('RGB'); KW, KH = key.size
TW, TH = int(KW * S // T), int(KH * S // T)
key.crop((0, 0, int(TW * T / S), int(TH * T / S))).save(os.path.join(OUT, 'ground.png'), optimize=True)
# buildings in the key art: name (canon role guess, to confirm with the town-art room), box x0 y0 x1 y1, foot y (picture px)
B = [  # canon names = the town-art room's match table (handoff/claude/felt_grok_layout/match.json on claude/linette-8dir, numbers in [])
 ('watchtower', '[4] 경비 초소 감시탑', 420, 82, 492, 222, 220),
 ('castle', '[2] 불탄 왕성 폐허', 500, 40, 905, 215, 213),
 ('linette', '[3] 리네트의 공방', 600, 190, 800, 274, 272),
 ('chapel', '[5] 예배당 종탑', 985, 40, 1095, 195, 193),
 ('west_a', '[14] 중고 무기점', 95, 165, 270, 430, 428),
 ('west_b', '[15] 시장 거리', 250, 155, 450, 375, 372),
 ('stall_n', '[15] 시장 노점', 430, 262, 575, 392, 390),
 ('west_edge', '[15] 시장 거리', 0, 180, 115, 440, 438),
 ('inn', '[7] 마르타의 여관', 930, 215, 1165, 440, 438),
 ('yard_fence', '[6] 예배당 뒤 묘지', 1170, 300, 1536, 410, 405),
 ('shop_sign', '[13] 잡화점', 285, 425, 525, 600, 598),
 ('sw_house', '[16] 주민 빈집', 55, 495, 255, 730, 728),
 ('bl_house', '주민 집', 0, 640, 140, 864, 862),
 ('s_house', '[12] 이장 바르트의 집', 505, 590, 745, 815, 812),
 ('se_house', '[11] 롬의 대장간', 830, 500, 1030, 735, 732),
 ('e_row', '[8] 세라의 약초 오두막', 1150, 430, 1410, 650, 648),
 ('web_arch', '[9] 아라크네의 폐공방', 1400, 430, 1536, 705, 702),
 ('red_stall', '[10] 벤의 노점', 1140, 640, 1385, 830, 828),
 ('fountain', '[1] 금 간 분수', 600, 400, 765, 505, 500),
]
# NPCs stand where the match table puts them (picture px, in front of their place); sprites / lines come from felt.json
NPCAT = {'f_luca': (640, 540), 'f_toby': (735, 545), 'f_linette': (705, 300), 'f_gas': (470, 245), 'f_oswald': (1040, 222), 'f_martha': (1050, 470),
         'f_sera': (1270, 675), 'f_ben': (1225, 812), 'f_rom': (930, 760), 'f_bart': (630, 812)}
solid = [[False] * TW for _ in range(TH)]
for x in range(TW): solid[0][x] = solid[TH - 1][x] = True
for y in range(TH): solid[y][0] = solid[y][TW - 1] = True
top = int(190 * S // T)                                    # sky / far backdrop above the town = not walkable
for y in range(top): solid[y] = [True] * TW
props = []
for n, (pid, role, x0, y0, x1, y1, fy) in enumerate(B):
    im = key.crop((x0, y0, x1, y1)).convert('RGBA'); f = f'{pid}.png'; im.save(os.path.join(OUT, f), optimize=True)
    depth = min(70, (y1 - y0) * .35) if pid != 'fountain' else 70
    sx0, sx1 = int((x0 + (x1 - x0) * .1) * S // T), int((x1 - (x1 - x0) * .1) * S // T); sy1 = int((fy - 4) * S // T); sy0 = int((fy - depth) * S // T)
    for y in range(max(0, sy0), min(TH, sy1 + 1)):
        for x in range(max(0, sx0), min(TW, sx1 + 1)): solid[y][x] = True
    props.append({'id': pid, 'role': role, 'img': f'assets/world/felt_layout/{f}', 'x': (x0 + x1) / 2 * S / T, 'y': fy * S / T,
                  'ax': (x1 - x0) / 2, 'ay': fy - y0, 'solid': [sx0, sy0, sx1, sy1], 'fade': 1 if pid != 'fountain' else 0, 'shadow': 0})
felt = json.load(open(os.path.join(ROOT, 'maps', 'felt.json')))
npcs = []
for o in felt['objects']:
    if o.get('type') == 'npc' and o['id'] in NPCAT:
        q = dict(o); px, py = NPCAT[o['id']]; q['x'], q['y'] = int(px * S // T), int(py * S // T); solid[q['y']][q['x']] = False; npcs.append(q)
rows = [''.join('#' if solid[y][x] else '.' for x in range(TW)) for y in range(TH)]
spawn = [860 * S / T, (820 * S) / T, 'up']   # [17] 남쪽 출구 → 잿빛 들판
m = {'id': 'felt_layout', 'type': 'field', 'area': 1, 'region': 'ch1', 'name': '펠트 — 구도 잡기 판', 'title': {'kicker': '1장 · 구도 시험', 'name': '펠트', 'sub': '그록 대표 그림 그대로'},
     'bgm': 'town_ruin', 'battleBgm': 'battle_champion', 'tileset': 'field', 'tile': T, 'w': TW, 'h': TH, 'legend': {'.': 'dirt', '#': 'cliff'}, 'solid': ['#'],
     'spawns': {'default': spawn}, 'objects': npcs + [{'type': 'sign', 'x': round(spawn[0]) + 2, 'y': int(spawn[1]) - 1, 'text': '구도 잡기 판 — 그록 대표 그림을 그대로 깔았다.\n건물 뒤로 지나가 보세요 (반투명).'}],
     'ground': rows, 'hd': {'D': D, 'ground': 'assets/world/felt_layout/ground.png', 'props': props, 'lights': [], 'grade': None},
     'note': f'GENERATED by tools/hd/build_felt_layout.py (S={S}); placeholder art cut from the Grok key art'}
json.dump(m, open(os.path.join(ROOT, 'maps', 'felt_layout.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', TW, 'x', TH, 'tiles', len(props), 'props, D', round(D, 3))
