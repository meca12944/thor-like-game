#!/usr/bin/env python3
"""1장 잿빛 들판 중앙 (ch1_field_c, 260x210) — 그록 1장 그림으로 조립 (팀장 10-26 「조립표 순서대로 중앙」).

설계도: docs_maps/ch1/ch1_map.json 구역 field_c (전체 180,120 → 이 맵 0,0). 조립표: docs_maps/ch1/CH1_ASSEMBLY_PLAN_ko.md (팀장 결정: 수도교 동서, 틈 2칸).
- 무너진 수도교: 동서 한 줄 (상판 y108~122), 서쪽 토막 x0~118 (끝 = 무너진 끝 L), 틈 2칸, 동쪽 토막 x120~260 (끝 R). 아치 밑으로 지나감, 기둥 밑동만 막힘.
  (상판 위를 걷는 높은 길은 엔진 level 이 생긴 뒤)
- 꺼진 지반 (6,84) 75x70: 테두리는 걷고 안쪽 어둠 = 막힘. 수도교 서쪽 토막이 그 위를 지나감. 부서진 승강기 = 지름길② 자리(아직 조사만).
- 붉은 실의 첨탑 = 폐공방 건물(사람 크기라 42/34 배) — 문으로 들어가면 지금 폐공방(arachne).
- 옛 싸움터·쓰러진 탑·잿더미 언덕 + 화면마다 표지물(ch1_kit.fill_landmarks) + 길가 흔적.
- 동쪽 끝 = 동쪽 들판(ch1_field_e)과 이어짐. 북쪽(절벽 오르막)·남쪽(무덤가 쪽 들판)은 아직 표지판.
효과(잿가루 폭포·지반 안개·실 흔들림)는 코드 → 효과 담당 목록 handoff/claude/ch1_center/README_ko.md.
usage: python3 tools/hd/fields/build_ch1_center.py   (test128 에서)
"""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch1_kit import Field, G1, G2, TS, HS, T128

F = Field('ch1_field_c', 260, 210, 180, 120, 'assets/world/ch1_center', 1026)
W, H = F.W, F.H
F.ground_ash()

# ---- 길 ----
R_MAIN = [(259, 160), (212, 151), (176, 138), (161.5, 127), (161.5, 104), (150, 93), (112, 82), (62, 77), (22, 75)]   # 동쪽 들판 → 아치 밑 → 폐공방 문
R_SOUTH = [(212, 151), (165, 172), (128, 194), (121, 209)]                                                         # 갈림길 → 남쪽(무덤가 쪽)
R_FALLS = [(161.5, 127), (140, 131), (124, 132)]                                                                    # 잿가루 폭포 아래 쉼터
F.road(R_MAIN, 3.2); F.road(R_SOUTH, 2.6); F.road(R_FALLS, 2.2)

# ---- 꺼진 지반 (설계도 186,204 → 6,84) ----
PX, PY = 6, 84
pp, pim = F.img(f'{G1}/06_sunken_pit/06_pit_rim_back.png', 'sunken_pit')
F.under('sunken_pit', pp, PX, PY)
F.alpha_mask(pim, PX, PY, '~', thr=.5, dark=70)
F.big.append((PX, PY, 75, 70))

# ---- 무너진 수도교 (동서, 상판 위 y 108) ----
AQ = f'{G1}/04_aqueduct'; TOP = 108
def aq(name, x, k):
    p, im = F.img(f'{AQ}/04_aqueduct_{name}_full_ref.png', 'aqueduct_' + name)
    h = im.height / TS; F.prop(f'aq_{k}', p, x, TOP + h, ax=0, ay=im.height, shadow=0)
    F.alpha_mask(im, int(x), TOP, 'X', thr=.55, keep=lambda tx, ty: ty < int(h) - 2)   # 기둥 밑동 2줄만 막힘 (아치 밑은 지나감)
    return im.width / TS
x = 0
for k in range(4): x += aq('repeat', x, k)
x += aq('end_L', x, 4)                       # 서쪽 토막의 무너진 끝
GAP0 = x; x += 2                             # 틈 2칸 (팀장 10-25) — 잿가루 폭포가 떨어지는 자리
GAP1 = x; x += aq('end_R', x, 5)
k = 6
while x < W: x += aq('repeat', x, k); k += 1
F.big.append((0, TOP, W, 14))

# ---- 붉은 실의 첨탑 = 폐공방 (설계도 폐공방 정문 160,90 쪽 → 들판 북서쪽) ----
SP, sim = F.img(f'{G1}/09_red_thread_spire/09_thread_spire_full_ref.png', 'thread_spire')
SD = round(1 / HS, 3); SW_, SH_ = sim.width / TS / SD, sim.height / TS / SD; SX, SBASE = 24, 74
F.prop('thread_spire', SP, SX, SBASE, D=SD, shadow=0)
F.alpha_mask(sim, int(SX - SW_ / 2), int(SBASE - SH_), 'X', thr=.5, D=SD, keep=lambda tx, ty: ty < int(SH_ * .8) or ty >= int(SH_) - 1)
F.big.append((int(SX - SW_ / 2), int(SBASE - 20), int(SW_), 20))
F.rect(11, SBASE - 1, 16, SBASE, '.')        # 문 앞
F.objs.append({'type': 'exit', 'x': 11, 'y': SBASE - 1, 'w': 5, 'h': 1, 'to': 'arachne', 'spawn': 'felt', 'label': '폐공방'})

# ---- 북쪽 = 북쪽 절벽으로 오르는 비탈(막힘) + 그 너머 먼 왕성 · 남·서·동 끝 ----
F.rect(0, 0, W, 10, '#'); F.rect(0, 0, 1, H, '#'); F.rect(W - 1, 0, W, H, '#'); F.rect(0, H - 2, W, H, '#')
F.rect(W - 1, 150, W, 171, '.'); F.rect(118, H - 2, 125, H, '#')
edge = Image.new('L', (F.GW, 13 * TS)); de = ImageDraw.Draw(edge)
for yy in range(13 * TS): de.line([(0, yy), (F.GW, yy)], fill=int(255 * max(0, min(1, (13 * TS - yy) / (5 * TS))) ** 1.5 * .8))
F.ground.paste(Image.new('RGBA', (F.GW, 13 * TS), (28, 24, 22, 255)), (0, 0), edge)
R = F.rocks()
for i, xx in enumerate(range(3, W - 2, 9)):
    if not (SX - SW_ / 2 - 2 < xx < SX + SW_ / 2 + 2): F.prop(f'edge_{i}', R[2 if i % 3 else 0][0], xx + F.rnd.uniform(-1.5, 1.5), 11.2 + F.rnd.uniform(0, 1.2), shadow=0)

# ---- 작은 경관 (조립표 자리) ----
F.small('12b_old_battlefield_spears', 190, 166)                 # 창이 꽂힌 옛 싸움터 (수도교 그늘 남동)
F.small('12a_collapsed_tower', 96, 30)                          # 쓰러진 탑 몸통
F.small('12d_ash_mound_hill', 54, 26); F.small('12d_ash_mound_hill', 200, 186, fl=True)   # 큰 잿더미 두 곳
F.scatter_rocks(24, 16, 200)
F.fill_landmarks(14, 204)
F.roadside(14, 204)
F.tufts_mounds(12, 204)
F.footprints()
F.save_ground()

# ---- 물체 ----
O = F.objs
O.append({'type': 'exit', 'x': W - 1, 'y': 150, 'w': 1, 'h': 21, 'to': 'ch1_field_e', 'spawn': 'west', 'label': '→ 동쪽 들판 · 1장 정문'})
O.append({'type': 'waystone', 'id': 'ws_ash_falls', 'x': 124, 'y': 134, 'name': '잿가루 폭포 아래 모닥불', 'art': 'camp'})
O.append({'type': 'waystone', 'id': 'ws_mound_camp', 'x': 168, 'y': 90, 'name': '잿더미 쉼터 모닥불', 'art': 'camp'})
O.append({'type': 'vista', 'id': 'cc_aqueduct', 'x': 128, 'y': 140, 'r': 3.5, 'zoom': 0.42, 'dir': 270, 'pan': 18, 'hold': 1, 'name': '무너진 수도교', 'sub': '물 대신 재가 흐르는 다리'})
O.append({'type': 'vista', 'id': 'cc_spire', 'x': 46, 'y': 82, 'r': 3.5, 'zoom': 0.4, 'dir': 270, 'pan': 16, 'hold': 1, 'name': '붉은 실의 첨탑', 'sub': '폐공방 지붕에서 하늘로 묶인 실'})
O.append({'type': 'vista', 'id': 'cc_pit', 'x': 88, 'y': 104, 'r': 3, 'zoom': 0.45, 'dir': 180, 'pan': 22, 'hold': 1, 'name': '꺼진 지반', 'sub': '땅 밑으로 가라앉은 옛 거리'})
O.append({'type': 'clue', 'id': 'cc_remains', 'x': 200, 'y': 150, 'name': '쓰러진 탈영병', 'flag': 'cc_look_remains', 'loot': [['k_void_drop', 1]],
          'text': '빈 망토와 가죽 팔토시. 성벽 쪽으로 손을 뻗은 채 굳어 있다.\n손끝 아래 바닥에 검붉은 방울 하나가 굳지 않고 떨린다. …주워 들었다.', 'textDone': '성벽 쪽으로 손을 뻗은 빈 망토.'})
O.append({'type': 'clue', 'id': 'cc_remains2', 'x': 88, 'y': 160, 'name': '쓰러진 탈영병', 'flag': 'cc_look_remains2',
          'text': '구덩이 가장자리에 엎드린 빈 망토. 장갑 한 짝만 남았다.', 'textDone': '구덩이 가장자리의 빈 망토.'})
O.append({'type': 'clue', 'id': 'cc_lift', 'x': 56, 'y': 85, 'name': '부서진 승강기', 'flag': 'cc_look_lift',
          'text': '구덩이 위에 걸린 부서진 승강기 발판. 사슬이 아래 어둠 속으로 이어진다.\n…아래에서 누가 사슬을 올려 주면 내려갈 수 있을 것 같다.', 'textDone': '어둠 속으로 이어진 사슬.'})
O.append({'type': 'clue', 'id': 'cc_falls', 'x': 120, 'y': 124, 'name': '수도교의 끊긴 틈', 'flag': 'cc_look_falls',
          'text': '끊긴 수도교 틈으로 물 대신 잿가루가 쏟아진다.\n폭포 뒤 벽에 어두운 굴이 보이는 것 같다.', 'textDone': '잿가루가 쏟아지는 틈.'})
O.append({'type': 'sign', 'x': 140, 'y': 11, 'text': '북쪽 절벽으로 오르는 비탈. 무너진 돌에 길이 막혀 있다.'})
O.append({'type': 'sign', 'x': 121, 'y': 206, 'text': '남쪽 들판으로 가는 길. 무너진 담에 막혀 있다.'})
O.append({'type': 'hint', 'id': 'cc_h_arch', 'x': 161, 'y': 132, 'r': 3, 'text': '수도교 아치 밑으로 지나갈 수 있다'})
F.mobs('field_c', skip=lambda x, y: x > 236 and 140 < y < 180)

prol = json.load(open(os.path.join(T128, 'maps/prologue_grave.json')))
bd = dict(prol['hd']['backdrop']); bd['x'] = 140; bd['clipY'] = 10.6; bd.pop('front', None)
mp = F.write({
    'name': '잿빛 들판 — 중앙', 'title': {'kicker': '1장 · 펠트', 'name': '잿빛 들판', 'sub': '무너진 수도교와 꺼진 지반, 붉은 실의 첨탑'},
    'bgm': 'area01_forest', 'battleBgm': 'battle_champion', 'grade': 'ash', 'fog': .24, 'ash': 1, 'wind': [5, 1],
    'camZones': [{'x0': 0, 'y0': 10, 'x1': W, 'y1': 30, 'zoom': 0.8, 'look': -7.5, 'f': 8}],
    'spawns': {'default': [256.5, 160.5, 'left'], 'east': [256.5, 160.5, 'left']},
    'hd': {'backdrop': bd, 'fires': [[124.5, 134.4, 1.1], [168.5, 90.4, 1.0]], 'smoke': [[124.5, 134.0, 1.0], [168.5, 90.0, 0.9]],
           'flick': [[124.5, 134.4, 48, '#ff8a3a', 1], [168.5, 90.4, 44, '#ff8a3a', 1]]},
    'note': '1장 들판 중앙 (build_ch1_center.py + ch1_kit.py 가 만든다). 설계도 field_c = 전체 180,120.',
})
print('ok', W, H, 'gap', round(GAP0, 1), round(GAP1, 1), 'mobs', sum(1 for o in O if o['type'] == 'spawn'), 'props', len(F.props), 'under', len(F.unders))
