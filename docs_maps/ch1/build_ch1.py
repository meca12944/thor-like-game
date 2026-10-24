#!/usr/bin/env python3
"""1장 지도 설계도 데이터 만들기 → ch1_map.json (팀장, 2026-10-24).
  python3 docs_maps/ch1/build_ch1.py && python3 tools/mapplan/draw.py docs_maps/ch1/ch1_map.json
몹 무리 자리는 「격자 + 흔들기」로 고르게 뿌리고, 마을·무덤가·NPC 둘레와 절벽은 비운다.
"""
import json, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
R = random.Random(1024)

W, H = 640, 470
Z = [  # id, 이름, 종류, x, y, w, h, 메모
    ('cliff_n', '북쪽 절벽', 'field', 180, 20, 260, 100, '석화 나무·히든 정예. 바람과 낙석'),
    ('field_c', '잿빛 들판 중앙', 'field', 180, 120, 260, 210, '부서진 마차·정예 껍데기·탈영병 유해'),
    ('field_e', '동쪽 들판 · 가도 들머리', 'field', 440, 70, 190, 260, '2장 철혈의 가도로 가는 길, 펠트 정문 바로 밖'),
    ('field_s', '남쪽 들판 · 무명 무덤가', 'field', 180, 330, 230, 130, '프롤로그 시작점'),
    ('felt', '펠트 마을', 'town', 420, 300, 150, 120, '생존자 거점 (지금 게임 펠트를 2.5배로)'),
    ('ws_1f', '폐공방 1층 작업실', 'dungeon', 20, 40, 140, 100, '리네트 구출 · 대형 재봉틀'),
    ('ws_b1', '폐공방 지하 1층 고문실', 'dungeon', 20, 160, 140, 100, '영혼이 꿰매진 인형 제단'),
    ('ws_b2', '폐공방 지하 2층 고치 저장고', 'dungeon', 20, 280, 140, 100, '고치 어미 · 빈 고치(붉은 목도리)'),
    ('ws_boss', '실타래의 베틀방', 'boss', 30, 395, 120, 65, '보스 아라크네 (지금 28x20 → 120x65)'),
]
zones = [dict(id=i, name=n, kind=k, x=x, y=y, w=w, h=h, note=t) for i, n, k, x, y, w, h, t in Z]
zb = {z['id']: z for z in zones}

areas = [
    {'kind': 'citywall', 'poly': [[0, 462], [640, 462], [640, 470], [0, 470]]},  # 왕도 외성벽 (남쪽 끝, 너머는 없음)
    {'kind': 'cliff', 'poly': [[180, 20], [440, 20], [440, 34], [380, 44], [300, 38], [230, 46], [180, 40]]},
    {'kind': 'cliff', 'poly': [[250, 70], [292, 62], [300, 88], [262, 96]]},
    {'kind': 'ash', 'poly': [[200, 150], [260, 140], [280, 190], [220, 210]]},
    {'kind': 'ash', 'poly': [[330, 230], [400, 220], [420, 280], [350, 300]]},
    {'kind': 'ruin', 'poly': [[296, 196], [326, 196], [326, 214], [296, 214]]},   # 부서진 마차 자리
    {'kind': 'grave', 'poly': [[270, 400], [330, 396], [336, 440], [266, 444]]},  # 무명 무덤가
    {'kind': 'forest', 'poly': [[190, 340], [230, 336], [236, 380], [192, 388]]},  # 마른 나무
    {'kind': 'water', 'poly': [[520, 120], [600, 110], [610, 150], [530, 160]]},   # 검은 웅덩이
    {'kind': 'wall', 'poly': [[420, 300], [570, 300], [570, 304], [420, 304]]},    # 펠트 북쪽 담
    {'kind': 'building', 'poly': [[440, 320], [480, 320], [480, 345], [440, 345]]},
    {'kind': 'building', 'poly': [[500, 320], [545, 320], [545, 345], [500, 345]]},
    {'kind': 'building', 'poly': [[440, 370], [480, 370], [480, 400], [440, 400]]},
    {'kind': 'building', 'poly': [[510, 372], [555, 372], [555, 404], [510, 404]]},
    {'kind': 'web', 'poly': [[30, 300], [80, 290], [90, 330], [40, 340]]},
    {'kind': 'web', 'poly': [[100, 330], [150, 320], [150, 370], [110, 372]]},
    {'kind': 'web', 'poly': [[40, 405], [140, 405], [140, 450], [40, 450]]},
]
paths = [
    {'kind': 'road', 'w': 3, 'pts': [[300, 425], [330, 400], [380, 380], [425, 360]]},                 # 무덤가 → 펠트 서문
    {'kind': 'road', 'w': 3, 'pts': [[495, 300], [480, 270], [420, 240], [330, 205]]},                 # 펠트 정문 → 마차
    {'kind': 'road', 'w': 3, 'pts': [[330, 205], [280, 160], [200, 110], [160, 90]]},                  # 마차 → 폐공방 정문
    {'kind': 'road', 'w': 3, 'pts': [[480, 270], [520, 200], [560, 120], [600, 90], [628, 76]]},       # → 2장 가도
    {'kind': 'road', 'w': 2, 'pts': [[330, 205], [330, 140], [320, 90], [300, 60]]},                   # → 북쪽 절벽
    {'kind': 'corridor', 'w': 4, 'pts': [[90, 140], [90, 160]]}, {'kind': 'corridor', 'w': 4, 'pts': [[90, 260], [90, 280]]},
    {'kind': 'corridor', 'w': 4, 'pts': [[90, 380], [90, 395]]},
]
links = [
    {'from': 'field_s', 'to': 'felt', 'kind': 'gate', 'at': [421, 360], 'label': '펠트 서문'},
    {'from': 'felt', 'to': 'field_e', 'kind': 'gate', 'at': [495, 301], 'label': '1장 정문 (베르디)'},
    {'from': 'field_s', 'to': 'field_c', 'kind': 'gate', 'at': [300, 331], 'label': '들판 남쪽 길'},
    {'from': 'field_c', 'to': 'cliff_n', 'kind': 'gate', 'at': [320, 121], 'label': '절벽 오르막'},
    {'from': 'field_c', 'to': 'field_e', 'kind': 'gate', 'at': [440, 220], 'label': ''},
    {'from': 'field_c', 'to': 'ws_1f', 'kind': 'door', 'at': [160, 90], 'label': '폐공방 정문'},
    {'from': 'ws_1f', 'to': 'ws_b1', 'kind': 'stairs', 'at': [90, 140], 'label': '계단'},
    {'from': 'ws_b1', 'to': 'ws_b2', 'kind': 'stairs', 'at': [90, 260], 'label': '계단'},
    {'from': 'ws_b2', 'to': 'ws_boss', 'kind': 'door', 'at': [90, 382], 'label': '베틀방 문'},
    {'from': 'ws_boss', 'to': 'field_s', 'kind': 'shortcut', 'at': [150, 430], 'label': '지름길① 보스 뒤 뒷문 → 무덤가 (안에서 열림)'},
    {'from': 'ws_b1', 'to': 'field_c', 'kind': 'shortcut', 'at': [160, 210], 'label': '지름길② 고문실 하수 구멍 → 들판 (안에서 열림)'},
    {'from': 'cliff_n', 'to': 'field_e', 'kind': 'shortcut', 'at': [440, 70], 'label': '지름길③ 밧줄 다리 (내리기)'},
    {'from': 'field_e', 'to': 'ch2', 'kind': 'gate', 'at': [629, 76], 'label': '→ 2장 철혈의 가도'},
    {'from': 'field_e', 'to': 'ch2', 'kind': 'lift', 'at': [600, 280], 'label': '1~2장 리프트 (2장 카일라가 엶)'},
]

M = []
def mk(t, name, zone, x, y, ref='', note=''):
    M.append(dict(type=t, name=name, zone=zone, x=x, y=y, ref=ref, note=note))

# 프롤로그 · 남쪽 들판
mk('start', '눈뜨는 자리 (코어 푸른빛)', 'field_s', 300, 420, '정본 6장 프롤로그, 0절 들판 남쪽')
mk('item', '배낭 유해: 닳은 등불·평범한 회복 물약', 'field_s', 312, 428, '정본 프롤로그')
mk('save', '무덤가 모닥불', 'field_s', 286, 410, '', '팀 제안')
# 펠트 마을
mk('npc', '경비대장 가스 (초소)', 'felt', 428, 356, '정본 1장-1)', '서문 초소. 보스 뒤: 나무 의수·부서진 투구만 남음')
mk('npc', '이장 바르트', 'felt', 460, 332, '정본 1장-1)')
mk('shop', '여관 마르타 (들판 괴물 처치 뒤 거래)', 'felt', 520, 332, '정본 1장-1)', '잿빛 정화제·투척 나이프')
mk('save', '루카의 모닥불', 'felt', 495, 360, '정본 1장-1)')
mk('npc', '맹인 시인 루카', 'felt', 500, 364, '정본 1장-1)', '공허의 핏방울 → 비파·징검다리 반지')
mk('shop', '떠돌이 상인 벤 (짐마차)', 'felt', 560, 390, '정본 1장-1)', '수색가 반지·특수 숫돌·잿빛 화염병')
mk('npc', '소년 토비 (판잣집)', 'felt', 456, 410, '정본 1장-1)', '아동 보호: 둘레 몹 없음')
mk('shop', '고물 수리점', 'felt', 530, 385, '정본 0절', '수리 도구·소모품 조금')
mk('npc', '리네트 (구출 뒤 동행, 보스 뒤 천·바늘 상자)', 'felt', 470, 385, '정본 0절')
# 들판
mk('npc', '베르디 (돌기둥, 1장 정문)', 'felt', 500, 306, '정본 0절', '2장 단테 대검 → 기록관 안경 / 금서 해독')
mk('elite', '방황하는 껍데기 (정예)', 'field_c', 312, 205, '정본 1장-2)', '부서진 마차 둘레 → 잿가루 낀 철환')
mk('item', '탈영병 유해: 가죽 팔토시·닳아빠진 장갑', 'field_c', 380, 270, '정본 1장-2)')
mk('item', '공허의 핏방울 (바닥, 검붉은 방울)', 'field_c', 384, 274, '정본 0절')
mk('item', '탈영병 유해 2', 'field_c', 230, 260, '정본 1장-2) "곳곳에"')
mk('item', '탈영병 유해 3', 'field_e', 520, 230, '정본 1장-2) "곳곳에"')
mk('save', '부서진 마차 모닥불', 'field_c', 340, 215, '', '팀 제안')
mk('hidden_elite', '석화 나무 아래 히든 정예 → 시간이 굳은 핏방울 1/3', 'cliff_n', 274, 80, '정본 1장-2)')
mk('landmark', '석화된 거대 나무', 'cliff_n', 270, 74)
mk('save', '절벽 길 모닥불', 'cliff_n', 360, 100, '', '팀 제안')
mk('save', '가도 들머리 모닥불', 'field_e', 560, 150, '', '팀 제안')
mk('elite', '썩지 않는 들개 우두머리 (지금 게임 챔피언)', 'field_e', 560, 90, '', '팀 제안: 지금 있는 챔피언 재사용')
# 폐공방
mk('save', '공방 문간 모닥불', 'ws_1f', 140, 60, '', '팀 제안')
mk('quest', '뒤집힌 옷장: 리네트 구출 (cg_linette_meet)', 'ws_1f', 40, 60, '정본 1장-3), 0절 동행')
mk('chest', '대형 재봉틀 뒤 잠긴 철제 상자: 피 묻은 바늘 반지', 'ws_1f', 100, 110, '정본 1장-3)')
mk('item', '숨겨진 제단: 영혼이 꿰매진 인형', 'ws_b1', 40, 240, '정본 1장-3)', '비밀벽 뒤')
mk('save', '고문실 모닥불', 'ws_b1', 140, 180, '', '팀 제안')
mk('midboss', '고치 어미 → 붉은 실타래 반지', 'ws_b2', 90, 360, '정본 1장-3)', '보스방 직전 길막')
mk('item', '빈 거미 고치: 붉은 목도리 (토비)', 'ws_b2', 140, 300, '정본 1장-1)')
mk('save', '베틀방 문 앞 모닥불', 'ws_b2', 110, 372, '', '보스 문 앞 필수')
mk('boss', '아라크네 → 붉은 척추검·실크 망토·붉은 마지막 기록 실타래', 'ws_boss', 90, 430, '정본 1장-3)')

# 몹 무리 (격자 + 흔들기). 비울 곳: 마을, 무덤가 둘레, 토비, 모닥불 둘레
NOGO = [(300, 420, 22), (515, 330, 14), (440, 330, 8)] + [(k['x'], k['y'], 10) for k in M if k['type'] == 'save']
FIELD_MIX = ['썩지 않는 들개 3', '썩지 않는 들개 4', '실마물 2 + 들개 2', '실 꼭두각시 3', '실마물 3', '바늘 거미 4']
DUNGEON_MIX = ['바늘 거미 4', '실 꼭두각시 3', '실마물 3', '바늘 거미 3 + 실 꼭두각시 1', '새끼 거미 6 + 바늘 거미 1']
def scatter(zid, step, mix):
    z = zb[zid]
    for gy in range(z['y'] + step // 2, z['y'] + z['h'], step):
        for gx in range(z['x'] + step // 2, z['x'] + z['w'], step):
            x = min(z['x'] + z['w'] - 3, max(z['x'] + 3, gx + R.randint(-step // 3, step // 3)))
            y = min(z['y'] + z['h'] - 3, max(z['y'] + 3, gy + R.randint(-step // 3, step // 3)))
            if any((x - a) ** 2 + (y - b) ** 2 < r * r for a, b, r in NOGO): continue
            if zid == 'cliff_n' and y < 46: continue
            mk('mob', R.choice(mix), zid, x, y, '', '팀 제안')
for zid in ('cliff_n', 'field_c', 'field_e', 'field_s'): scatter(zid, 46, FIELD_MIX)
for zid in ('ws_1f', 'ws_b1', 'ws_b2'): scatter(zid, 44, DUNGEON_MIX)

grok = [
    {'kind': 'bg', 'name': '잿빛 들판 바닥 세트', 'size': '16px 타일 + 큰 장식', 'desc': '재가 눈처럼 쌓인 땅, 마른 풀, 발자국 남는 잿더미'},
    {'kind': 'bg', 'name': '북쪽 절벽 끝', 'size': '구역 260x100', 'desc': '깎아지른 절벽 끝, 바람에 날리는 재, 낙석'},
    {'kind': 'prop', 'name': '석화된 거대 나무', 'size': '약 10x14 타일', 'desc': '돌이 된 거대한 나무, 밑동에 히든 정예가 숨는 그늘'},
    {'kind': 'prop', 'name': '부서진 마차', 'size': '약 8x5 타일', 'desc': '들판 한가운데 뒤집힌 마차, 정예 껍데기의 영역'},
    {'kind': 'prop', 'name': '탈영병 유해 3종', 'size': '약 2x1 타일', 'desc': '쓰러진 병사 유해 (팔토시·장갑), 1개는 옆에 검붉은 방울'},
    {'kind': 'prop', 'name': '무명 무덤가 + 배낭 유해', 'size': '약 12x8 타일', 'desc': '이름 없는 무덤들, 이전 루프의 가죽 배낭 유해'},
    {'kind': 'prop', 'name': '1장 정문 + 돌기둥 베르디', 'size': '약 6x5 타일', 'desc': '들판으로 나가는 정문, 다리가 돌기둥과 굳은 기록관'},
    {'kind': 'prop', 'name': '밧줄 다리 / 리프트 / 하수 구멍 / 보스 뒷문', 'size': '각 3~6 타일', 'desc': '지름길 4종'},
    {'kind': 'bg', 'name': '폐공방 1층·지하1·지하2 바닥/벽', 'size': '16px 타일', 'desc': '붉은 인체 조직 실이 엉킨 재봉 공방, 고문실, 고치 저장고'},
    {'kind': 'prop', 'name': '뒤집힌 옷장 / 대형 재봉틀 / 숨겨진 제단 / 빈 고치', 'size': '각 2~6 타일', 'desc': '1장 이야기 소품'},
    {'kind': 'mob', 'name': '방황하는 껍데기 (정예)', 'size': '약 2x3 타일', 'desc': '몬스터 담당 기획서 기준'},
    {'kind': 'mob', 'name': '북쪽 절벽 히든 정예', 'size': '약 2x3 타일', 'desc': '정본에 모습 없음 → 몬스터 담당이 기획 후 그록에 부탁'},
    {'kind': 'npc', 'name': '바르트·마르타·벤·가스·루카·토비 새 외형', 'size': '캐릭터', 'desc': '정본 2장 1) 외형 그대로'},
    {'kind': 'boss', 'name': '아라크네 새 외형', 'size': '보스', 'desc': '사람 상체 + 기계 팔 + 실크 거미 하체 + 핏빛 드레스'},
]
DX, DY = 20, 30   # 펠트 구역을 들판과 안 겹치게 옮김
for k in M:
    if k['zone'] == 'felt': k['x'] += DX; k['y'] += DY
for a in areas:
    if a['kind'] in ('building', 'wall'): a['poly'] = [[x + DX, y + DY] for x, y in a['poly']]
zb['felt']['x'] += DX; zb['felt']['y'] += DY
for l in links:
    if 'felt' in (l['from'], l['to']): l['at'] = [l['at'][0] + DX, l['at'][1] + DY]
paths[0]['pts'][-1] = [445, 390]; paths[1]['pts'][0] = [515, 331]
out = dict(chapter='ch1', title='프롤로그 + 1장 잿빛 들판 · 펠트 · 폐공방', w=W, h=H, zones=zones, areas=areas, paths=paths,
           links=links, markers=M, grok=grok)
json.dump(out, open(os.path.join(HERE, 'ch1_map.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('markers', len(M), 'mobs', sum(k['type'] == 'mob' for k in M))
