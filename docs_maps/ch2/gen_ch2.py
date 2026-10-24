#!/usr/bin/env python3
"""2장 지도 설계도 만들기 → ch2_map.json (스토리 담당, 사장님 10-24 「전체 챕터 지도」). 고칠 때는 이 파일을 고치고 다시 돌린다."""
import json, os
Z = {}
zones = []
def zone(id, name, kind, x, y, w, h, note=''):
    z = dict(id=id, name=name, kind=kind, x=x, y=y, w=w, h=h, note=note); zones.append(z); Z[id] = z
markers = []
def mk(t, name, zid, rx, ry, ref='', note=''):  # rx, ry = 구역 안 0~1 비율
    z = Z[zid]; markers.append(dict(type=t, name=name, zone=zid, x=int(z['x'] + rx * (z['w'] - 1)), y=int(z['y'] + ry * (z['h'] - 1)), ref=ref, note=note))
def mobs(zid, kinds=(), step=50, skip=()):  # 몹 무리: step 타일 격자마다 하나 (팀 제안), skip = 비울 칸 (rx,ry 중심 근처)
    z = Z[zid]; i = 0
    for gy in range(z['y'] + step // 2, z['y'] + z['h'], step):
        for gx in range(z['x'] + step // 2, z['x'] + z['w'], step):
            rx, ry = (gx - z['x']) / z['w'], (gy - z['y']) / z['h']
            if any(abs(rx - a) < .12 and abs(ry - b) < .14 for a, b in skip): continue
            k = kinds[i % len(kinds)]; i += 1
            j = ((gx * 7 + gy * 13) % 11) - 5
            markers.append(dict(type='mob', name=k[0], zone=zid, x=min(z['x'] + z['w'] - 2, max(z['x'] + 1, gx + j)), y=min(z['y'] + z['h'] - 2, max(z['y'] + 1, gy - j)), ref='팀 제안', note=k[1]))

# ---------- 구역 (팀 제안: 크기·자리) ----------
zone('road_w', '철혈의 가도 · 외곽', 'field', 0, 60, 250, 200, '1장에서 들어오는 성곽 길. 전사자 시체, 성벽 위 바르바라')
zone('road_m', '철혈의 가도 · 바리케이드', 'field', 250, 60, 250, 200, '가도 중앙 바리케이드, 중장갑 정예병')
zone('gate', '성문 앞 광장', 'boss', 500, 90, 140, 140, '보스 「불멸의 수문장」 단테 경')
zone('armory', '숨겨진 무기고', 'hidden', 500, 0, 140, 80, '바르바라가 여는 성문 우회로')
zone('forge', '무쇠 공방', 'town', 270, 270, 120, 90, '가도 측면 불타는 대장간 — 카일라')
zone('sw_entry', '하수도 · 첫 수문', 'dungeon', 10, 300, 240, 140, '하수도 진입로, 첫 수문 옆 백골 더미')
zone('sw_slum', '하수도 · 배수관 판자촌', 'town', 260, 380, 120, 90, '그레이의 정보상 판자촌 (쉼터 거점)')
zone('sw_mid', '하수도 · 중간 통로와 중앙 저수조', 'dungeon', 390, 370, 200, 140, '벽에 굳은 로크, 수은 폐수 저수조')
zone('sw_dead', '하수도 · 막다른 배수로', 'dungeon', 10, 450, 240, 140, '돌로 굳은 부부 유골')
zone('sw_deep', '하수도 · 맹독 폐수 최심부', 'dungeon', 600, 360, 170, 230, '투명 즉사 함정, 목 잘린 거대 기사상')

# ---------- 지형 ----------
areas = [
    dict(kind='wall', poly=[[0, 60], [500, 60], [500, 68], [0, 68]]),                 # 북쪽 성곽 (바르바라가 서 있는 성벽)
    dict(kind='wall', poly=[[0, 252], [270, 252], [270, 260], [0, 260]]),
    dict(kind='ruin', poly=[[360, 120], [392, 112], [400, 210], [366, 216]]),         # 바리케이드
    dict(kind='ash', poly=[[30, 90], [120, 80], [140, 150], [60, 170]]),
    dict(kind='ruin', poly=[[150, 190], [210, 180], [220, 240], [160, 245]]),          # 무너진 망루
    dict(kind='fire', poly=[[290, 285], [340, 282], [345, 320], [292, 325]]),          # 불타는 대장간 화덕
    dict(kind='wall', poly=[[500, 90], [508, 90], [508, 230], [500, 230]]),            # 성문 앞 담 (가운데가 문)
    dict(kind='water', poly=[[20, 360], [240, 350], [240, 380], [20, 390]]),
    dict(kind='mercury', poly=[[440, 420], [540, 410], [560, 480], [450, 490]]),       # 중앙 수은 저수조
    dict(kind='poison', poly=[[610, 380], [760, 380], [760, 580], [610, 580]]),        # 맹독 폐수
    dict(kind='poison', poly=[[30, 480], [200, 470], [210, 520], [40, 530]]),
]
paths = [
    dict(kind='road', w=4, pts=[[0, 160], [120, 158], [250, 165], [380, 160], [500, 160]]),
    dict(kind='road', w=2, pts=[[330, 200], [330, 270]]),                              # 가도 → 무쇠 공방
    dict(kind='bridge', w=2, pts=[[640, 160], [700, 160]]),
    dict(kind='sewer', w=3, pts=[[30, 330], [240, 340], [260, 420], [390, 420], [590, 440], [600, 470]]),
    dict(kind='sewer', w=2, pts=[[130, 440], [130, 460], [200, 520]]),
    dict(kind='corridor', w=2, pts=[[610, 470], [680, 420], [740, 500], [690, 570]]),
]
links = [
    dict(**{'from': 'ch1', 'to': 'road_w', 'kind': 'gate', 'at': [1, 160], 'label': '← 1장 동쪽 끝 (1장 좌표 629,76) · 정문 베르디'}),
    dict(**{'from': 'road_w', 'to': 'road_m', 'kind': 'gate', 'at': [250, 160], 'label': '무너진 초소'}),
    dict(**{'from': 'road_m', 'to': 'gate', 'kind': 'gate', 'at': [500, 160], 'label': '보스 문'}),
    dict(**{'from': 'road_m', 'to': 'forge', 'kind': 'door', 'at': [330, 268], 'label': '공방 길'}),
    dict(**{'from': 'forge', 'to': 'ch1', 'kind': 'shortcut', 'at': [385, 300], 'label': '1↔2장 리프트 (카일라) = 1장 (600,280)'}),
    dict(**{'from': 'road_m', 'to': 'armory', 'kind': 'secret', 'at': [490, 62], 'label': '무기고 문 (바르바라)'}),
    dict(**{'from': 'armory', 'to': 'gate', 'kind': 'shortcut', 'at': [600, 79], 'label': '성문 우회로'}),
    dict(**{'from': 'gate', 'to': 'ch3', 'kind': 'gate', 'at': [639, 160], 'label': '왕도 성문 → 3장 (성문 기어 손잡이)'}),
    dict(**{'from': 'road_w', 'to': 'sw_entry', 'kind': 'stairs', 'at': [120, 255], 'label': '하수구 맨홀'}),
    dict(**{'from': 'sw_entry', 'to': 'sw_slum', 'kind': 'door', 'at': [252, 400], 'label': '배수관'}),
    dict(**{'from': 'sw_slum', 'to': 'sw_mid', 'kind': 'door', 'at': [385, 420], 'label': '중간 통로'}),
    dict(**{'from': 'sw_entry', 'to': 'sw_dead', 'kind': 'door', 'at': [130, 445], 'label': '갈라진 배수로'}),
    dict(**{'from': 'sw_mid', 'to': 'sw_deep', 'kind': 'door', 'at': [595, 450], 'label': '맹독 구역 (렌즈 반지 필요)'}),
    dict(**{'from': 'sw_mid', 'to': 'road_m', 'kind': 'shortcut', 'at': [470, 372], 'label': '사다리 지름길 (안에서 엶)'}),
    dict(**{'from': 'sw_mid', 'to': 'ch4', 'kind': 'secret', 'at': [560, 508], 'label': '귀족가 직행 샛길 → 4장 (해독한 금서)'}),
]

# ---------- 인물·아이템·보스 (정본) ----------
mk('save', '쉼터: 가도 입구 모닥불', 'road_w', .05, .55, '팀 제안')
mk('save', '쉼터: 바리케이드 뒤', 'road_m', .55, .75, '팀 제안')
mk('save', '쉼터: 보스 문 앞', 'road_m', .95, .55, '팀 제안', '보스 문 앞 필수')
mk('save', '쉼터: 공방 화덕', 'forge', .7, .6, '팀 제안')
mk('save', '쉼터: 무기고 안', 'armory', .2, .7, '팀 제안')
mk('save', '쉼터: 수문 옆', 'sw_entry', .2, .3, '팀 제안')
mk('save', '쉼터: 판자촌 (그레이 옆)', 'sw_slum', .3, .5, '팀 제안')
mk('save', '쉼터: 저수조 둑', 'sw_mid', .1, .2, '팀 제안')
mk('save', '쉼터: 배수로 입구', 'sw_dead', .55, .1, '팀 제안')
mk('save', '쉼터: 최심부 입구', 'sw_deep', .05, .45, '팀 제안')

mk('npc', '바르바라 (유령 기사단장)', 'road_w', .55, .06, '정본 6장 2장-1)', '외곽 성벽 위, 푸른 인광 반유령. 군번줄+녹은 펜던트 → 무기고 열고 성불')
mk('item', '녹슨 군번줄 (전사자 시체)', 'road_w', .3, .7, '녹슨 군번줄', '가도 외곽 전사자 시체')
mk('item', '녹은 펜던트 (전사자 시체)', 'road_w', .8, .3, '녹은 펜던트', '가도 전사자 시체')
mk('landmark', '바리케이드', 'road_m', .48, .5, '정본 6장 2장-1)')
mk('elite', '중장갑 정예병', 'road_m', .62, .45, '파열된 철갑 반지 · 부러진 검의 날', '바리케이드 뒤편')
mk('npc', '카일라 (무쇠 공방 견습공)', 'forge', .4, .45, '정본 6장 2장-1)', '왕실 특수 천 → 마모 저항 방어구, 리프트 숏컷 개방')
mk('item', '카일라의 덧대기 키트', 'forge', .25, .7, '카일라의 덧대기 키트', '제작에 씀 (카일라 소지)')
mk('item', '낡은 무쇠 망치', 'forge', .5, .75, '낡은 무쇠 망치', '제작에 씀 (카일라 소지)')
mk('quest', '마모 저항 방어구 제작', 'forge', .6, .35, '마모 저항 방어구', '리네트의 왕실 특수 천 전달')
mk('chest', '무기 거치대', 'armory', .6, .4, '처형인의 무쇠 반지 · 잿빛 장비 수리 망치', '바르바라가 연 무기고 안')
mk('boss', '단테 경 「불멸의 수문장」', 'gate', .55, .5, '철혈의 부러진 대검 · 철혈기사의 무쇠망토 · 성문 기어 손잡이', '1페이즈 철갑 수호자 / 2페이즈(50%) 철갑 파쇄·폭주 2배')
mk('quest', '대검 → 1장 베르디 (형의 안식)', 'gate', .85, .2, '가문의 마지막 맹세 · 피 묻은 기록관의 안경(기록관의 렌즈 반지) · 영구 스태미나 20%', '대검을 1장 정문 베르디에게 가져가면 받음 (1장 지도)')

mk('item', '첫 수문 옆 백골 더미', 'sw_entry', .35, .2, '석화된 해골 반지 · 석회화된 유골')
mk('npc', '그레이 (하수도 상인)', 'sw_slum', .55, .45, '정본 6장 2장-2)', '베르디에게 몰래 식량을 보냄')
mk('shop', '그레이의 가게', 'sw_slum', .7, .7, '닳지 않는 잿빛유물 · 암호화된 금서 · 타임키퍼의 해체 공구 · 녹슨 해체톱', '금서 → 1장 베르디 해독 → 3장 비밀방 / 4장 샛길. 해체 공구 → 6장 클로비스')
mk('npc', '로크 (연금술 탈영병)', 'sw_mid', .3, .15, '정본 6장 2장-2)', '통로 벽에 반쯤 석화. 수은 필터(6장) 또는 수은 정화통 → 석상이 되고 물약병')
mk('item', '석화된 연금술사의 물약병', 'sw_mid', .32, .26, '석화된 연금술사의 물약병', '로크가 굳은 뒤 발치')
mk('item', '중앙 저수조 바닥', 'sw_mid', .5, .65, '멍든 수은 반지 · 검은 이끼 물약 · 잿빛 이끼')
mk('item', '부부 유골', 'sw_dead', .9, .85, '닳아버린 결혼반지', '막다른 배수로 끝, 서로 껴안고 굳음')
mk('item', '수은 정화통', 'sw_deep', .25, .3, '수은 정화통', '하수도 심부 — 로크에게 (6장 수은 필터 대신)')
for i, (rx, ry) in enumerate([(.2, .55), (.45, .4), (.55, .65), (.75, .5), (.4, .8), (.7, .25)]):
    mk('trap', f'투명 즉사 함정 {i + 1}', 'sw_deep', rx, ry, '렌즈 반지로 보임')
mk('landmark', '목 잘린 거대 기사상', 'sw_deep', .55, .93, '정본 6장 2장-2)')
mk('item', '망각된 집행관의 참수검', 'sw_deep', .6, .9, '망각된 집행관의 참수검', '기사상에 꽂힌 검 (참수 연출 없음)')
mk('shortcut', '리프트 레버 (카일라가 엶)', 'forge', .9, .3, '1↔2장 직통 안전 숏컷')
mk('shortcut', '사다리 지름길 레버', 'sw_mid', .4, .02, '팀 제안', '하수도 ↔ 가도 바리케이드')

# ---------- 몹 무리 (팀 제안 — 정본: 「갑옷과 육신이 들러붙은 기사들이 배회」, 하수도 「생물들이 석회화」) ----------
mobs('road_w', step=45, kinds=[('굳은 기사 무리', '갑옷과 몸이 들러붙은 기사 3'), ('굳은 기사 무리', '갑옷 기사 2 + 방패 1'), ('굳은 기사 무리', '갑옷 기사 4')], skip=[(.05, .55), (.55, .06)])
mobs('road_m', step=45, kinds=[('굳은 기사 무리', '갑옷 기사 3'), ('굳은 기사 무리', '창 기사 2 + 갑옷 기사 2'), ('굳은 기사 무리', '갑옷 기사 3')], skip=[(.48, .5), (.95, .55), (.55, .75)])
mobs('sw_entry', [('석회화된 하수 생물', '석회 쥐 떼 4'), ('석회화된 하수 생물', '굳어 가는 하수 벌레 3')], step=60, skip=[(.2, .3)])
mobs('sw_mid', [('석회화된 하수 생물', '수은 먹은 생물 3'), ('석회화된 하수 생물', '석회 쥐 떼 4')], step=60, skip=[(.3, .15), (.1, .2)])
mobs('sw_dead', [('석회화된 하수 생물', '석회 쥐 떼 3')], step=60, skip=[(.55, .1)])
mobs('sw_deep', [('석회화된 하수 생물', '맹독 생물 2')], step=70, skip=[(.05, .45), (.6, .9)])
mobs('armory', [('굳은 기사 무리', '무기고 경비 2')], step=70, skip=[(.2, .7), (.6, .4)])

grok = [
    dict(kind='bg', name='철혈의 가도 바닥·성곽 타일', size='16px 타일 세트', desc='잿가루 덮인 돌 포장길, 녹슨 갑옷 조각, 높은 성곽 벽 (위로 걸을 수 있는 성벽 길)'),
    dict(kind='bg', name='하수도 타일', size='16px 타일 세트', desc='오물 배수로, 석회로 하얗게 굳은 벽, 푸른 수은 웅덩이, 맹독 녹색 폐수'),
    dict(kind='prop', name='바리케이드', size='약 4x6 타일', desc='부서진 수레·창·방패를 쌓은 길막이'),
    dict(kind='prop', name='거대 성문', size='약 8x10 타일', desc='녹슨 판금 성문, 기어 손잡이 구멍'),
    dict(kind='prop', name='무쇠 공방 (불타는 대장간)', size='약 12x10 타일', desc='화덕 불, 모루, 리프트 승강기'),
    dict(kind='prop', name='배수관 판자촌', size='약 14x10 타일', desc='오물 배수관 위 판자 집, 그레이 가게'),
    dict(kind='prop', name='목 잘린 거대 기사상', size='약 4x6 타일', desc='맹독 폐수 한가운데, 머리 없는 기사상에 검이 꽂힘 (잘리는 장면 없음)'),
    dict(kind='prop', name='전사자 시체·백골 더미·부부 유골', size='각 1~2 타일', desc='루팅 표시용'),
    dict(kind='mob', name='굳은 기사', size='주인공 크기', desc='갑옷과 몸이 들러붙어 굳은 기사 (가도 잡몹)'),
    dict(kind='mob', name='중장갑 정예병', size='주인공 1.5배', desc='바리케이드 지키는 두꺼운 판금 정예'),
    dict(kind='mob', name='석회화된 하수 생물', size='작음', desc='쥐·벌레가 석회로 굳어 가는 하수도 잡몹'),
    dict(kind='npc', name='카일라', size='주인공 크기', desc='구릿빛 피부, 가죽 팔토시·에이프런, 묶은 머리, 어깨에 큰 망치'),
    dict(kind='npc', name='바르바라', size='주인공 크기', desc='반투명 잿빛 환영, 부서진 투구 사이 푸른 인광, 가슴 갑옷에 구멍'),
    dict(kind='npc', name='그레이', size='주인공 크기', desc='쥐 모피 누더기 외투, 두건, 등에 톱·갈고리'),
    dict(kind='npc', name='로크', size='주인공 크기', desc='부푼 배, 석회암처럼 굳는 피부, 고장 난 방독면'),
    dict(kind='boss', name='단테 경', size='주인공 3배', desc='녹슨 거대 판금 갑옷, 틈새에서 잿가루·쇳가루 폭포, 반으로 부러진 대검 / 2페이즈 갑옷 파쇄'),
]
m = dict(chapter='ch2', title='철혈의 가도 & 하수도 (녹슨 맹세와 오물)', w=780, h=600, zones=zones, areas=areas, paths=paths, links=links, markers=markers, grok=grok)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ch2_map.json')
json.dump(m, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(out, len(markers), 'markers')
