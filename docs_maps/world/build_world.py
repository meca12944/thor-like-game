#!/usr/bin/env python3
"""세계 지도: 거대한 성 안의 왕도 (사장님 10-24 「거대한 성, 그 안 왕도에서 벌어지는 일이다」).
챕터 = 왕도 안의 구역. 바깥 세상은 없다. 가운데 왕성(7장), 그 위 하늘의 틈새(8장).
  python3 docs_maps/world/build_world.py && python3 tools/mapplan/draw.py docs_maps/world/world_map.json
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 2400
Z = [  # 챕터 구역 (팀 제안 배치, 크기는 각 장 지도 크기에 맞춰 나중에 고침)
    ('ch1', '1장 잿빛 들판·펠트·폐공방 (남쪽 외곽)', 'field', 880, 1880, 640, 470, '외성벽 안 가장 바깥, 불타 버린 구역이 벌판이 됨'),
    ('ch2', '2장 철혈의 가도 (내성문 가는 길)', 'field', 920, 1380, 560, 470, '외곽 → 내성문, 성곽 길'),
    ('ch2s', '2장 왕도 지하 하수도 (땅 밑)', 'hidden', 300, 1460, 560, 420, '왕도 아래를 거미줄처럼, 3·6장 폐수가 흘러듦'),
    ('ch3', '3장 침묵의 대서고 (서쪽 구역)', 'dungeon', 140, 700, 640, 600, ''),
    ('ch4', '4장 잿더미 연회장·귀족가 (동쪽 구역)', 'town', 1620, 700, 640, 600, ''),
    ('ch5', '5장 대성당·지하 수장고 (북쪽 구역)', 'dungeon', 880, 100, 640, 520, ''),
    ('ch6', '6장 연금술 심장부·시계탑 (동남 내성)', 'dungeon', 1560, 1380, 600, 470, '시간을 붙잡는 기관'),
    ('ch7', '7장 왕성 옥좌의 방 (한가운데)', 'boss', 900, 700, 600, 600, '왕가의 열쇠로 여는 황금 문'),
    ('ch8', '8장 공허의 틈새 (왕성 위 하늘)', 'sky', 1000, 790, 400, 140, '옥좌 뒤 제단 → 왕도 상공 핏빛 하늘'),
]
zones = [dict(id=i, name=n, kind=k, x=x, y=y, w=w, h=h, note=t) for i, n, k, x, y, w, h, t in Z]
# ch8 은 ch7 위 하늘이라 겹쳐도 됨 → 검사에서 빼기 위해 그림용 따로
sky = zones.pop()
areas = [
    {'kind': 'citywall', 'poly': [[40, 40], [2360, 40], [2360, 60], [40, 60]]}, {'kind': 'citywall', 'poly': [[40, 2340], [2360, 2340], [2360, 2360], [40, 2360]]},
    {'kind': 'citywall', 'poly': [[40, 40], [60, 40], [60, 2360], [40, 2360]]}, {'kind': 'citywall', 'poly': [[2340, 40], [2360, 40], [2360, 2360], [2340, 2360]]},
    {'kind': 'citywall', 'poly': [[860, 660], [1540, 660], [1540, 672], [860, 672]]}, {'kind': 'citywall', 'poly': [[860, 1328], [1540, 1328], [1540, 1340], [860, 1340]]},
    {'kind': 'citywall', 'poly': [[860, 660], [872, 660], [872, 1340], [860, 1340]]}, {'kind': 'citywall', 'poly': [[1528, 660], [1540, 660], [1540, 1340], [1528, 1340]]},
    {'kind': 'void', 'poly': [[sky['x'], sky['y']], [sky['x'] + sky['w'], sky['y']], [sky['x'] + sky['w'], sky['y'] + sky['h']], [sky['x'], sky['y'] + sky['h']]]},
]
links = [
    {'from': 'ch1', 'to': 'ch2', 'kind': 'gate', 'at': [1200, 1870], 'label': '외곽 → 가도'},
    {'from': 'ch1', 'to': 'ch2', 'kind': 'lift', 'at': [1480, 1870], 'label': '1~2장 리프트'},
    {'from': 'ch2', 'to': 'ch2s', 'kind': 'stairs', 'at': [905, 1640], 'label': '하수도 입구'},
    {'from': 'ch2', 'to': 'ch7', 'kind': 'gate', 'at': [1200, 1334], 'label': '내성문 (단테 경)'},
    {'from': 'ch2s', 'to': 'ch3', 'kind': 'secret', 'at': [460, 1320], 'label': '하수도 → 대서고 지하'},
    {'from': 'ch1', 'to': 'ch4', 'kind': 'secret', 'at': [1700, 1320], 'label': '금서 해독 샛길 (베르디)'},
    {'from': 'ch7', 'to': 'ch5', 'kind': 'gate', 'at': [1200, 640], 'label': ''},
    {'from': 'ch7', 'to': 'ch3', 'kind': 'gate', 'at': [840, 1000], 'label': ''},
    {'from': 'ch7', 'to': 'ch4', 'kind': 'gate', 'at': [1580, 1000], 'label': ''},
    {'from': 'ch4', 'to': 'ch6', 'kind': 'gate', 'at': [1860, 1340], 'label': ''},
    {'from': 'ch6', 'to': 'ch3', 'kind': 'oneway', 'at': [800, 1340], 'label': '태엽 핵 → 3장 화로'},
    {'from': 'ch7', 'to': 'ch8', 'kind': 'stairs', 'at': [1200, 940], 'label': '옥좌 뒤 제단 → 하늘'},
]
M = [dict(type='landmark', name='외성벽 (왕도 끝, 바깥 세상 없음)', zone='', x=1200, y=50),
     dict(type='landmark', name='왕성 (모든 구역에서 보이는 중심)', zone='ch7', x=1200, y=1150),
     dict(type='start', name='무명 무덤가', zone='ch1', x=1180, y=2300)]
out = dict(chapter='world', title='거대한 성 안의 왕도 (전체 세계 지도, 배치는 팀 제안)', w=W, h=H, zones=zones, areas=areas,
           paths=[], links=links, markers=M, grok=[], sky=sky)
json.dump(out, open(os.path.join(HERE, 'world_map.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
