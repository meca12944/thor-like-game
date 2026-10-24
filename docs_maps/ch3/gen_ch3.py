#!/usr/bin/env python3
"""3장 지도 설계도 만들기 → ch3_map.json (스토리 담당, 사장님 10-24 「전체 챕터 지도」). 고칠 때는 이 파일을 고치고 다시 돌린다."""
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


# ---------- 구역 (팀 제안: 크기·자리). 층마다 따로 구역 (README: 던전 층 = 구역 하나) ----------
zone('lobby', '대서고 1층 로비', 'dungeon', 0, 0, 250, 230, '무너진 대리석 기둥·책장 — 헬레나')
zone('f2', '대서고 2층 중앙 열람실', 'dungeon', 260, 0, 250, 230, '사슬 금서 보관함, 깨진 스테인드글라스 천장')
zone('f3', '대서고 3층 서가 회랑', 'dungeon', 520, 0, 240, 230, '부서진 난간, 숨겨진 책장')
zone('boss', '3층 보스방 · 셀레네의 서고', 'boss', 560, 250, 170, 150, '보스 「지식의 괴물」 맹목의 셀레네')
zone('b1', '지하 금지된 서고', 'dungeon', 0, 250, 250, 200, '시간 왜곡 금서, 연금술 화로')
zone('secret', '금지된 서고 비밀방', 'hidden', 270, 300, 110, 90, '해독한 암호 금서의 주문으로 엶')

areas = [
    dict(kind='ruin', poly=[[60, 120], [130, 110], [150, 190], [70, 200]]),     # 무너진 기둥·책장 (헬레나)
    dict(kind='books', poly=[[10, 20], [240, 20], [240, 40], [10, 40]]),
    dict(kind='books', poly=[[170, 60], [240, 60], [240, 170], [170, 170]]),
    dict(kind='books', poly=[[280, 20], [340, 20], [340, 210], [280, 210]]),
    dict(kind='books', poly=[[440, 20], [500, 20], [500, 210], [440, 210]]),
    dict(kind='ruin', poly=[[360, 90], [420, 90], [420, 140], [360, 140]]),     # 스테인드글라스 빛 모이는 곳
    dict(kind='books', poly=[[530, 20], [750, 20], [750, 50], [530, 50]]),
    dict(kind='pit', poly=[[700, 120], [758, 110], [758, 225], [705, 225]]),    # 부서진 난간 아래 낭떠러지
    dict(kind='books', poly=[[540, 90], [640, 90], [640, 120], [540, 120]]),
    dict(kind='books', poly=[[20, 280], [230, 280], [230, 300], [20, 300]]),
    dict(kind='fire', poly=[[170, 380], [220, 375], [225, 420], [175, 425]]),   # 연금술 화로
    dict(kind='books', poly=[[590, 280], [700, 280], [700, 300], [590, 300]]),
]
paths = [
    dict(kind='corridor', w=4, pts=[[0, 210], [125, 210], [125, 60], [245, 60]]),
    dict(kind='corridor', w=3, pts=[[265, 60], [390, 60], [390, 200], [505, 200]]),
    dict(kind='corridor', w=3, pts=[[525, 200], [600, 160], [690, 160], [690, 225]]),
    dict(kind='corridor', w=2, pts=[[40, 225], [40, 330], [240, 340]]),
]
links = [
    dict(**{'from': 'ch2', 'to': 'lobby', 'kind': 'gate', 'at': [1, 210], 'label': '← 2장 왕도 성문'}),
    dict(**{'from': 'lobby', 'to': 'f2', 'kind': 'stairs', 'at': [248, 60], 'label': '중앙 계단'}),
    dict(**{'from': 'f2', 'to': 'f3', 'kind': 'stairs', 'at': [508, 200], 'label': '나선 계단'}),
    dict(**{'from': 'f3', 'to': 'boss', 'kind': 'door', 'at': [690, 228], 'label': '보스 문'}),
    dict(**{'from': 'lobby', 'to': 'b1', 'kind': 'stairs', 'at': [40, 228], 'label': '지하 계단'}),
    dict(**{'from': 'b1', 'to': 'secret', 'kind': 'secret', 'at': [252, 340], 'label': '비밀방 (암호 금서 주문)'}),
    dict(**{'from': 'f3', 'to': 'lobby', 'kind': 'shortcut', 'at': [600, 228], 'label': '무너진 책장 사다리 (3층→1층, 안에서 내림)'}),
    dict(**{'from': 'b1', 'to': 'ch2', 'kind': 'shortcut', 'at': [5, 440], 'label': '배수 통로 → 2장 하수도 (안에서 엶)'}),
    dict(**{'from': 'boss', 'to': 'ch4', 'kind': 'gate', 'at': [728, 330], 'label': '→ 4장'}),
]
mk('save', '쉼터: 로비 입구', 'lobby', .06, .85, '팀 제안')
mk('save', '쉼터: 열람실 계단참', 'f2', .08, .3, '팀 제안')
mk('save', '쉼터: 3층 서가 입구', 'f3', .05, .85, '팀 제안')
mk('save', '쉼터: 보스 문 앞', 'f3', .65, .95, '팀 제안', '보스 문 앞 필수')
mk('save', '쉼터: 지하 서고', 'b1', .15, .3, '팀 제안')
mk('save', '쉼터: 비밀방', 'secret', .2, .7, '팀 제안')
mk('save', '쉼터: 보스방 뒤 (처치 후)', 'boss', .9, .85, '팀 제안')

mk('npc', '헬레나 (짓눌린 근위대)', 'lobby', .4, .7, '정본 6장 3장', '기둥·책장에 하반신이 깔린 여기사. 검병 3개 → 근위대의 꺾인 창검, 재가 됨')
mk('quest', '근위대의 꺾인 창검 (헬레나)', 'lobby', .47, .78, '근위대의 꺾인 창검 · 부러진 근위대의 창', '꺾인 맹세의 검병 + 부서진 맹세의 칼자루 + 부러진 검병')
mk('elite', '타락한 근위대 (1층)', 'lobby', .75, .3, '꺾인 맹세의 검병', '헬레나의 옛 부하')
mk('elite', '타락한 근위대 (2층)', 'f2', .7, .75, '부서진 맹세의 칼자루', '헬레나의 옛 부하')
mk('elite', '타락한 근위대 (3층)', 'f3', .4, .6, '부러진 검병', '헬레나의 옛 부하')
mk('chest', '사슬 금서 보관함', 'f2', .5, .5, '맹세의 흑연검', '2층 중앙 열람실, 검은 잉크가 검 모양으로 굳음')
mk('item', '스테인드글라스 아래 독서대', 'f2', .5, .2, '거울 파편 반지 · 굳어버린 안경테', '깨진 천장으로 빛이 모이는 곳')
mk('item', '추락한 학자의 유해 (부서진 난간 끝)', 'f3', .9, .8, '망자의 눈물 반지 · 시간의 양피지', '3층 보스방 직전. 시간의 양피지 = 셀레네 연구 일지 해독(아이템배치 표)')
mk('landmark', '숨겨진 책장', 'f3', .3, .2, '정본 6장 3장')
mk('hidden_elite', '잉크를 삼킨 고서 (미믹)', 'f3', .32, .3, '시간이 굳은 핏방울 (2/3)', '숨겨진 책장 뒤 → 5장 수장고 석관')
mk('boss', '맹목의 셀레네 「지식의 괴물」', 'boss', .5, .5, '대서고의 양피지 망토', '1페이즈 잉크 안개·쿨타임 늘리는 투사체 / 2페이즈 금서 날개 공중 체공·마모 폭주')
mk('chest', '비밀방 서가', 'secret', .6, .4, '공허의 소용돌이 반지 · 잊혀진 양피지', '1장 베르디가 해독한 2장 암호화된 금서의 주문')
mk('landmark', '연금술 화로', 'b1', .78, .66, '정본 6장 6장 히든 무기 연계', '6장 클로비스 태엽 핵(진짜 심장)을 여기서 녹이면 초침을 부수는 대검')
mk('quest', '태엽 핵 소각 → 초침을 부수는 대검', 'b1', .7, .78, '초침을 부수는 대검', '6장 뒤 다시 찾아옴 (2장 그레이 해체 공구 필요)')
mk('shortcut', '책장 사다리 레버', 'f3', .45, .97, '팀 제안')
mk('shortcut', '배수 통로 철창', 'b1', .03, .95, '팀 제안', '2장 하수도와 이어짐')

# ---------- 몹 무리 (팀 제안 — 정본: 「소리 내는 자를 사냥하는 눈먼 사서들과 검은 잉크 괴물들」) ----------
K = [('눈먼 사서', '소리에 달려드는 사서 2'), ('검은 잉크 괴물', '잉크 덩어리 3'), ('눈먼 사서', '사서 3 + 잉크 1')]
mobs('lobby', K, step=50, skip=[(.06, .85), (.4, .7), (.47, .78), (.75, .3)])
mobs('f2', K, step=50, skip=[(.08, .3), (.5, .5), (.5, .2), (.7, .75)])
mobs('f3', K, step=50, skip=[(.05, .85), (.65, .95), (.9, .8), (.3, .2), (.4, .6)])
mobs('b1', K, step=55, skip=[(.15, .3), (.78, .66), (.7, .78)])

grok = [
    dict(kind='bg', name='대서고 바닥·서가 타일', size='16px 타일 세트', desc='먼지 낀 대리석 바닥, 끝없는 책장, 바닥에 흘러 굳은 검은 잉크'),
    dict(kind='bg', name='지하 금지된 서고 타일', size='16px 타일 세트', desc='사슬로 묶인 금서, 촛불, 어두운 석조'),
    dict(kind='prop', name='무너진 대리석 기둥 + 책장 더미', size='약 6x5 타일', desc='헬레나가 깔린 자리'),
    dict(kind='prop', name='사슬 금서 보관함', size='약 3x3 타일', desc='사슬 감긴 철제 함, 안에 잉크 굳은 검'),
    dict(kind='prop', name='깨진 스테인드글라스 천장 빛 + 독서대', size='약 4x4 타일', desc='위에서 빛줄기가 모이는 독서대'),
    dict(kind='prop', name='부서진 난간', size='약 6x2 타일', desc='3층 낭떠러지 쪽 난간'),
    dict(kind='prop', name='연금술 화로', size='약 4x4 타일', desc='지하 서고 구석의 큰 화로'),
    dict(kind='mob', name='눈먼 사서', size='주인공 크기', desc='눈을 가린 사서, 소리에 반응해 달려듦'),
    dict(kind='mob', name='검은 잉크 괴물', size='작음~주인공 크기', desc='흘러 다니는 검은 잉크 덩어리'),
    dict(kind='mob', name='타락한 근위대', size='주인공 1.2배', desc='헬레나의 옛 부하, 부서진 근위대 갑옷 (층마다 1명, 검병 조각 지님)'),
    dict(kind='mob', name='잉크를 삼킨 고서 (미믹)', size='주인공 1.5배', desc='책장 뒤에 숨은 거대한 책 괴물'),
    dict(kind='npc', name='헬레나', size='주인공 크기', desc='하반신이 기둥·책장에 깔림, 상반신은 거의 하얀 뼈, 쥔 창과 근위대 투구는 원형'),
    dict(kind='boss', name='맹목의 셀레네', size='주인공 3배', desc='불탄 금서·양피지·굳은 잉크가 소용돌이친 짐승, 얼굴 자리는 텅 빈 공백 / 2페이즈 불타는 금서 날개'),
]
m = dict(chapter='ch3', title='침묵의 대서고 (눈먼 지식의 감옥)', w=760, h=460, zones=zones, areas=areas, paths=paths, links=links, markers=markers, grok=grok)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ch3_map.json')
json.dump(m, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(out, len(markers), 'markers')
