"""Labelled overview of town A (dev deliverable): python3 overview.py <town dir> <raw overview png> <out png>
Reads assets/level.json (ta) for buildings, NPCs, chests, toys, dive spots, doors and the south exit."""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
TOWN, RAW, OUTP = sys.argv[1:4]
FB = '/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf'
t = json.load(open(os.path.join(TOWN, 'assets', 'level.json')))['ta']; o = t['rooms'][0]
im = Image.open(RAW).convert('RGB'); S = im.width / (o['x1'] - o['x0'])
P = lambda x, y: ((x - o['x0']) * S, (y - o['y0']) * S)
LEG = 430; can = Image.new('RGB', (im.width + LEG, max(im.height + 60, 1240)), (24, 22, 30)); can.paste(im, (0, 60))
d = ImageDraw.Draw(can); F = lambda s: ImageFont.truetype(FB, s)
def Q(x, y): a, b = P(x, y); return a, b + 60
def tag(x, y, text, fill=(255, 236, 160), size=22, bg=(20, 16, 24)):
    f = F(size); w = d.textlength(text, font=f); a, b = Q(x, y)
    d.rounded_rectangle([a - w / 2 - 6, b - size / 2 - 5, a + w / 2 + 6, b + size / 2 + 5], 6, fill=bg + (0,) if False else bg, outline=(232, 214, 176), width=2)
    d.text((a - w / 2, b - size / 2 - 1), text, font=f, fill=fill)
def dot(x, y, col, label, r=13):
    a, b = Q(x, y); d.ellipse([a - r, b - r, a + r, b + r], fill=col, outline=(0, 0, 0), width=3)
    f = F(17); w = d.textlength(label, font=f); d.text((a - w / 2, b - 10), label, font=f, fill=(0, 0, 0) if sum(col) > 400 else (255, 255, 255))
d.text((16, 14), '필멸자 — 시작 마을 A  (월드 3800 × 1840 px · 실내 9칸 · 문 14 · 상자 7 · NPC 10 + 챔피언 바렌)', font=F(28), fill=(255, 224, 138))
for L in t['labels']: tag(L['x'], L['y'], L['text'])
NPCN = {'a_chief': '오스왈드(촌장)', 'a_granny': '엘스베트(분수지기)', 'a_kid': '토비', 'a_guard': '베른(경비)', 'a_farmer': '하로(농부)', 'a_herb': '세레스(약초)', 'a_bard': '라우렌(음유시인)', 'sm_A': '바렌(사범·챔피언)'}
leg = []
for i, (k, v) in enumerate(t['npcs'].items()):
    p = v[0] if isinstance(v[0], list) else v; n = 'N%d' % (i + 1); dot(p[0], p[1], (120, 200, 255), str(i + 1)); leg.append(('npc', str(i + 1), NPCN.get(k, k)))
inside = {'a_tool': '미라벨 — 도구상점 안', 'a_smith': '브란트 — 대장간 안', 'a_tailor': '리네트 — 재봉소 안'}
for k, v in inside.items(): leg.append(('npc', '실내', v))
IT = json.load(open(os.path.join(TOWN, 'assets', 'icons', 'items_demo.json')))['items']
NM = lambda i: (IT.get(i) or {}).get('n', i)
NEED = {'oath8': '8번째 맹세(후반)', 'earth_crystal': '구역1 보스 처치 후', 'bomb': '폭탄/광석 곡괭이'}
KIND = {'easy': '쉬움', 'hidden': '숨김', 'later': '재방문'}
for i, c in enumerate(t['chests']):
    lab = 'C%d' % (i + 1)
    if c['room'] == 'out': dot(c['x'], c['y'], (255, 200, 60) if c['kind'] != 'later' else (230, 90, 90), str(i + 1))
    items = ', '.join('%s×%d' % (NM(a), b) for a, b in c['items']); need = (' · 조건: ' + NEED.get(c['need'], c['need'])) if c.get('need') else ''
    leg.append(('chest', str(i + 1), '%s [%s] %s%s' % (c['hint'], KIND.get(c['kind'], c['kind']), items, need)))
for s in t['spots']: dot(s['x'], s['y'], (170, 255, 140), 'T'); 
leg.append(('toy', 'T', 'A3 토비의 나무 장난감 ×3 (대장간 뒤 · 촌장 집 울타리 · 분수 꽃밭) → 토비: 하트 조각'))
for (x, y, n) in [(777, 398, '분수 잠수: 생명의 진주 + 요람의 장부 조각(A6)'), (450, 168, '이끼 낀 우물 잠수'), (868, 572, '빗물 웅덩이'), (1030, -250, '촌장 집 연못')]:
    dot(x, y, (90, 230, 255), 'D', 11)
leg.append(('dive', 'D', '잠수 지점: 분수(A6 요람의 장부 조각) · 이끼 낀 우물 · 빗물 웅덩이 · 촌장 집 연못'))
G = t['gate']; a, b = Q((G['x0'] + G['x1']) / 2, G['y'] + 60)
d.polygon([(a - 26, b - 30), (a + 26, b - 30), (a, b + 6)], fill=(127, 216, 255), outline=(0, 0, 0))
tag((G['x0'] + G['x1']) / 2, G['y'] + 20, '▼ 남문 → 바람길 → 시작의 숲 (구역 1)', fill=(190, 240, 255), size=22)
tag(-120, 690, '연습 슬라임 · 멧돼지 챔피언 (바렌의 수련장)', fill=(255, 190, 190), size=18)
for dd in t['doors']:
    if dd.get('kind') == 'trap' or not dd.get('locked'): continue
    a, b = Q(dd['x'], dd['y']); d.text((a - 9, b - 30), '🔒' if False else 'X', font=F(20), fill=(255, 110, 110))
x0 = im.width + 18; y = 70; d.text((x0, y), '범례', font=F(26), fill=(255, 224, 138)); y += 40
COL = {'npc': (120, 200, 255), 'chest': (255, 200, 60), 'toy': (170, 255, 140), 'dive': (90, 230, 255)}
import textwrap
for kind, k, text in leg:
    d.ellipse([x0, y + 2, x0 + 22, y + 24], fill=COL[kind], outline=(0, 0, 0), width=2)
    d.text((x0 + 30, y), k, font=F(16), fill=(255, 255, 255))
    for j, line in enumerate(textwrap.wrap(text, 26)):
        d.text((x0 + 70, y + j * 21), line, font=F(16), fill=(230, 226, 214))
    y += 21 * max(1, len(textwrap.wrap(text, 26))) + 8
y += 10
for line in ['X = 잠긴 문 (메시지 표시)', '실내: 도구상점 · 대장간(+지하 창고) · 재봉소', '  바렌 도장 · 사범의 집 · 필멸자의 집', '  촌장 집(+지하 창고)', '문: 정면에서 위로 걸어 들어감 / 아래로 나감']:
    d.text((x0, y), line, font=F(16), fill=(200, 210, 240)); y += 22
can.save(OUTP); print(OUTP, can.size)
