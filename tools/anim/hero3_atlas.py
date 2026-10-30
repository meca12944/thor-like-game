# 주인공 v3 (그록 작은그림 작화, 키 144) → 게임 H8 아틀라스 (사장님 10-30 「일단 이거 전부 메인에 올려라, 플레이 가능하게」 → 「주인공이 왜 이리 거대해, 작아져야지」 → 키 218 → 144)
# 쓰는 법: python3 hero3_atlas.py <index.html> <v3 폴더(handoff/claude/hero3_v1)> <출력 webp>
# - 그린 것(hero3_v1/game144/, 키 144): 서기 3방향(정면·옆·뒷면, 얼굴 = A를 게임 키에 맞춰 한 번 줄임), 달리기 정면·뒷면 13장(그록 영상, 같은 박자·같은 발 닿는 장 0·6.5),
#   옆 달리기 17장(그록 영상, 발 닿는 장 0·9, 걸음 거리는 옆만 따로 = gaitMul: 디딘 발이 땅에 붙게)
# - 아직 안 그린 동작(옆 달리기, 걷기, 회피대시, 점프, 공격, 맞기, 쓰러짐, 시전 …)은 그 방향 서기 장을 같은 틱으로(이동·효과·판정은 코드 그대로)
# - 걷기(평소 이동) = 달리기 장(가볍게 뛰기 영상 전까지, 사장님 10-30 「가볍게 뛰기 영상」)
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
G = f'{V3}/game144'
frames['stand_down'] = [f'{G}/down_face.png']; frames['stand_right'] = [f'{G}/right_face.png']; frames['stand_up'] = [f'{G}/up.png']
frames['run_down'] = sorted(glob.glob(f'{G}/run13_face/0*.png')); frames['run_up'] = sorted(glob.glob(f'{G}/run13_back/0*.png'))
frames['run_right'] = sorted(glob.glob(f'{G}/run_side_face/0*.png'))
# 돌기 장 (사장님 10-30 「잔상이 아니라 부드럽게 전환되도록」, 그록 뒤돌기 영상 2개): 돌 때만 씀(바라보기는 4방향 그대로). 왼쪽 쪽은 뒤집기, 반대로 돌기는 거꾸로 — world.js TURN_CLIP
for tk in ('turn_rd', 'turn_dl', 'turn_ur'): frames[tk] = sorted(glob.glob(f'{G}/{tk}/0*.png'))   # (k는 위 JSON 끝 자리라 쓰면 안 됨)
assert all(len(frames[k]) >= 8 for k in ('run_down', 'run_up', 'run_right'))   # 바닥에서 달리기(ground.py)로 높이 뜬 장을 빼서 정면 10·뒷면 13·옆 14장
# 몸통 가운데 줄 맞추기 (교본 1부 1-0 「모든 방향을 같은 몸 가운데 줄로」, 사장님 10-30 「부드럽게 전환」): 동작 하나에 한 번,
# 그 동작 장들의 몸통(키의 30~50% 줄) 가운데 평균을 발 기준 x(128)에 둠. 서기 원본은 몸이 왼쪽으로 23~27칸 비켜 있어 출발·멈춤·돌기 때마다 몸이 옆으로 미끄러졌음.
import numpy as np
def torso_x(im):
    a = np.asarray(im)[..., 3] > 0; ys = np.nonzero(a.any(1))[0]; t, b = ys.min(), ys.max(); xs = []
    for fr in (.3, .35, .4, .45, .5):
        r = np.nonzero(a[int(t + (b - t) * fr)])[0]
        if len(r): xs.append((r.min() + r.max()) / 2)
    return float(np.median(xs))
# 장 자르기(빈 곳), 발 기준 = (128, 246) 판 기준 + 동작마다 몸통 가운데로 옮김(sx)
cells, crops, idx, shift = [], [], {}, {}
for nm, fl in frames.items():
    idx[nm] = []; ims = [Image.open(f).convert('RGBA') for f in fl]
    sx = round(float(np.mean([torso_x(im) for im in ims])) - 128); shift[nm] = sx
    for im in ims:
        if nm.startswith('turn_'): sx = round(torso_x(im) - 128)   # 돌기 장은 장마다(한 장 1틱, 앞뒤 두 동작에 다 이어져야 해서): 몸이 제자리에서 돎
        bb = im.getbbox(); c = im.crop(bb)
        crops.append(c); idx[nm].append(len(crops) - 1); cells.append([0, 0, c.width, c.height, 128 + sx - bb[0], 246 - bb[1]])
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
    if nm in ('run', 'walk') and dr in ('down', 'up', 'right', 'left'):
        new[key] = [[0, c, 3] for c in idx['run_' + ('right' if dr == 'left' else dr)]]
    elif nm == 'idle':
        new[key] = [[0, stand[dr], 60]]
    else:   # 아직 안 그린 동작: 그 방향 서기 장, 틱·시전 효과 칸은 그대로
        new[key] = [[0, stand.get(dr, stand['right'])] + e[2:] for e in L]
for tk in ('turn_rd', 'turn_dl', 'turn_ur'):
    new[tk] = [[0, c, 1] for c in idx[tk]]
for dr in ('down', 'up', 'right', 'left'):
    for nm in ('run', 'walk'):
        new.setdefault(f'{nm}_{dr}', [[0, c, 3] for c in idx['run_' + ('right' if dr == 'left' else dr)]])
H['anims'] = new
H['cells'] = [cells, H['cells'][1]]
H['sheets'] = ['anim/hero3_0.webp', H['sheets'][1]]
bb = Image.open(frames['stand_down'][0]).getbbox(); H['figH'] = bb[3] - bb[1]   # 서기 키 (144)
H['grip'] = {}
H['bodyAligned'] = True   # 동작마다 몸통 맞춤을 했다는 표시 → world.js h8Pop(튐 맞추기) 끔
H['gait'] = {'walkCyc': 123, 'runCyc': 150}   # 달리기 한 바퀴 ≈ 0.5초 = 그록 영상 박자(걸음 0.26초). 키를 줄여도 그대로(사장님 「발걸음 똑같이」, 빠르기 같음)
# 옆 달리기: 영상에서 디딘 발이 장마다 14.6칸 뒤로 = 게임 달리기(108/초 = 15.5칸/장)와 거의 같음 → 한 바퀴 거리 = 17장 × 14.6 = 248칸 = runCyc 187 꼴 → 배수 150/187
SIDE = round(150 / 187, 3)
H['gaitMul'] = {k: SIDE for k in ('run_right', 'run_left', 'walk_right', 'walk_left')}
for kk in [q for q in list(H) if q.startswith("_") and q != "_doc"]: del H[kk]
H['_doc'] = ('주인공 v3 (10-30 사장님 「일단 이거 전부 메인에 올려라, 플레이 가능하게」 → 「작아져야지」): 그록 작은그림 작화, 키 144(옛 주인공과 같은 화면 키), 얼굴 = A를 키에 맞춰 한 번 줄임. '
             'sheets 0 = v3 그림(서기 3방향 + 달리기 정면·뒷면 13장(발 닿는 장 0·6.5) + 옆 17장(발 닿는 장 0·9, gaitMul로 옆만 걸음 거리 187), 그록 영상 → 도트), 1 = 시전 마법진(옛 그대로). '
             '아직 안 그린 동작(회피대시·점프·공격·맞기·쓰러짐·시전)은 그 방향 서기 장(틱 그대로). 걷기(평소 이동) = 달리기 장(가볍게 뛰기 영상 전까지). '
             'turn_rd(옆→정면)·turn_dl(정면→옆←)·turn_ur(뒷면→옆) = 돌 때만 쓰는 돌기 장(그록 뒤돌기 영상, world.js TURN_CLIP). '
             '만든 과정 handoff/claude/hero3_v1(game144) · 교본 0부 2(얼굴)·5(그록 영상). 도구 tools/anim/hero3_atlas.py')
js = json.dumps(H, ensure_ascii=False, separators=(',', ':'))
s2 = s[:j] + js + s[k + 1:]
open(html, 'w', encoding='utf-8').write(s2)
print('장', len(cells), '시트', sheet.size, round(os.path.getsize(out) / 1e3), 'KB', '동작', len(new), '몸통 맞춤(칸)', shift)
