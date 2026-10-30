# 주인공 v3 (그록 작은그림 작화, 키 218) → 게임 H8 아틀라스 (사장님 10-30 「일단 이거 전부 메인에 올려라, 플레이 가능하게」)
# 쓰는 법: python3 hero3_atlas.py <index.html> <v3 폴더(handoff/claude/hero3_v1)> <출력 webp>
# - 그린 것: 서기 3방향(정면·옆·뒷면, 얼굴 = A하프 스무스), 달리기 정면·뒷면 13장(그록 영상, 같은 박자·같은 발 닿는 장 0·6.5)
# - 아직 안 그린 동작(옆 달리기, 걷기, 회피대시, 점프, 공격, 맞기, 쓰러짐, 시전 …)은 그 방향 서기 장을 같은 틱으로(이동·효과·판정은 코드 그대로)
# - 걷기 = 달리기 장(걷기 영상 전까지). 옆 걷기·달리기 = 옆 서기(옆 달리기 영상 전까지)
import sys, re, json, glob, os
from PIL import Image
html, V3, out = sys.argv[1:4]
s = open(html, encoding='utf-8').read()
i = s.index('/*H8*/'); j = s.index('{', i); d = 0
for k in range(j, len(s)):
    if s[k] == '{': d += 1
    elif s[k] == '}':
        d -= 1
        if d == 0: break
H = json.loads(s[j:k + 1])
frames = {}
frames['stand_down'] = [f'{V3}/ref/down_face.png']; frames['stand_right'] = [f'{V3}/ref/right_face.png']; frames['stand_up'] = [f'{V3}/ref/up.png']
frames['run_down'] = sorted(glob.glob(f'{V3}/grok_video/run13_face/0*.png')); frames['run_up'] = sorted(glob.glob(f'{V3}/grok_video/run13_back/0*.png'))
assert len(frames['run_down']) == 13 and len(frames['run_up']) == 13
# 장 자르기(빈 곳), 발 기준 = (128, 246) 판 기준
cells, crops, idx = [], [], {}
for nm, fl in frames.items():
    idx[nm] = []
    for f in fl:
        im = Image.open(f).convert('RGBA'); bb = im.getbbox(); c = im.crop(bb)
        crops.append(c); idx[nm].append(len(crops) - 1); cells.append([0, 0, c.width, c.height, 128 - bb[0], 246 - bb[1]])
# 줄 맞춰 깔기 (가로 2048)
W = 2048; x = y = rowh = 0
for n, c in enumerate(crops):
    if x + c.width > W: x = 0; y += rowh + 1; rowh = 0
    cells[n][0], cells[n][1] = x, y; x += c.width + 1; rowh = max(rowh, c.height)
sheet = Image.new('RGBA', (W, y + rowh))
for n, c in enumerate(crops): sheet.paste(c, (cells[n][0], cells[n][1]))
sheet.save(out, 'WEBP', lossless=True, method=6)
stand = {'down': idx['stand_down'][0], 'up': idx['stand_up'][0], 'right': idx['stand_right'][0], 'left': idx['stand_right'][0]}
old = H['anims']; new = {}
for key, L in old.items():
    dr = key.rsplit('_', 1)[1]; nm = key.rsplit('_', 1)[0]
    if nm in ('run', 'walk') and dr in ('down', 'up'):
        new[key] = [[0, c, 3] for c in idx['run_' + dr]]
    elif nm == 'idle':
        new[key] = [[0, stand[dr], 60]]
    else:   # 아직 안 그린 동작: 그 방향 서기 장, 틱·시전 효과 칸은 그대로
        new[key] = [[0, stand.get(dr, stand['right'])] + e[2:] for e in L]
for dr in ('down', 'up'):
    for nm in ('run', 'walk'):
        new.setdefault(f'{nm}_{dr}', [[0, c, 3] for c in idx['run_' + dr]])
H['anims'] = new
H['cells'] = [cells, H['cells'][1]]
H['sheets'] = ['anim/hero3_0.webp', H['sheets'][1]]
H['figH'] = 218
H['grip'] = {}
H['gait'] = {'walkCyc': 123, 'runCyc': 150}   # 옛 82/96 × 1.5(키 1.5배) → 달리기 한 바퀴 ≈ 0.5초 = 그록 영상 박자
for kk in [q for q in list(H) if q.startswith("_") and q != "_doc"]: del H[kk]
H['_doc'] = ('주인공 v3 (10-30 사장님 「일단 이거 전부 메인에 올려라, 플레이 가능하게」): 그록 작은그림 작화, 키 218(옛 144의 1.5배), 얼굴 = A하프 스무스. '
             'sheets 0 = v3 그림(서기 3방향 + 달리기 정면·뒷면 13장, 그록 영상 → 도트, 발 닿는 장 0·6.5), 1 = 시전 마법진(옛 그대로). '
             '아직 안 그린 동작(옆 달리기·걷기·회피대시·점프·공격·맞기·쓰러짐·시전)은 그 방향 서기 장(틱 그대로). 걷기 = 달리기 장. '
             '만든 과정 handoff/claude/hero3_v1 · 교본 0부 2(얼굴)·5(그록 영상). 도구 tools/anim/hero3_atlas.py')
js = json.dumps(H, ensure_ascii=False, separators=(',', ':'))
s2 = s[:j] + js + s[k + 1:]
open(html, 'w', encoding='utf-8').write(s2)
print('장', len(cells), '시트', sheet.size, round(os.path.getsize(out) / 1e3), 'KB', '동작', len(new))
