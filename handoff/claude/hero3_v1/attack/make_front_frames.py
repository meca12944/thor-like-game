# 정면 공격 3타 → 게임 그림 폴더 (사장님 11-01 「옆모습이랑 똑같이 맞춰」 → 「게임에 연결해」)
# 그록 정면 콤보 w_all(1타 내려베기 · 되돌려베기 · 내려찍기) + 그록 2타 다시(후보2 c2 13~21 + 메인 m 28~48)에서 게임에 쓰는 장만 골라
# game144/atk_front 에 256칸(발 = 128,246)으로 두고, 장마다 손 자리·칼 각도·몸 뒤·칼 길이 배율(s)을 grip.json 에. 틱 표 = game144/atk_anims_front.json
#  틱: 옆과 똑같이 1타 30 · 2타 30 · 3타 45틱, 칼이 맞는 장 시작 8 · 8 · 11틱 (1타 = w 30장, 2타 = c2 21장(칼끝이 카메라), 3타 = w 198장)
#  칼 길이 배율 s: 칼끝이 카메라를 가리키는 장 0.15, 오른쪽으로 펼쳐지는 장은 분홍 칼날 길이 ÷ 끝 자세 칼날(원근). 땅에 꽂힌 것처럼 안 보이게 칼끝을 발 4칸 위에서 멈추는 건 게임(drawHandSword)이 장착 칼 길이로 함
# 쓰는 법: python3 make_front_frames.py <fc(w_all: body/, grip.json)> <fc2(2타 다시: body2/, grip2.json)> <game144 폴더>
import json, os, sys, shutil
import numpy as np, cv2
from PIL import Image
FC, F2, OUT = [a.rstrip('/') + '/' for a in sys.argv[1:4]]
S1 = [(6, 1), (10, 1), (14, 1), (18, 1), (22, 2), (26, 1), (28, 1)] + [(30, 1)] \
     + [(31, 1), (32, 1), (33, 1), (34, 1), (35, 1), (36, 1), (38, 2), (40, 2), (42, 2), (44, 2), (46, 7)]
S2 = [('c2_013', 3), ('c2_014', 1), ('c2_015', 1), ('c2_016', 1), ('c2_017', 2)] + [('c2_021', 1)] \
     + [(f'm_{k:03d}', 1) for k in (29, 31, 32, 33, 34, 36, 38, 42, 48)] \
     + [(k, 1) for k in (109, 113, 117, 121, 125, 129, 133)] + [(137, 1), (140, 1), (144, 3)]
S3 = [(156, 1), (168, 1), (172, 1), (176, 1), (180, 1), (182, 3), (192, 1), (194, 1), (196, 1)] + [(198, 1)] \
     + [(k, 2) for k in (200, 202, 204, 206, 208, 212, 216, 220, 224, 228, 232, 236, 240, 246)] + [(252, 5)]
ANIM = {'hit1': S1, 'hit2': S2, 'hit3': S3}
TOT = {'hit1': (30, 30), 'hit2': (30, 'c2_021'), 'hit3': (45, 198)}
HIT = {'hit1': 8, 'hit2': 8, 'hit3': 11}
for k, L in ANIM.items():
    assert sum(n for _, n in L) == TOT[k][0], k
    t = 0
    for f, n in L:
        if f == TOT[k][1]: break
        t += n
    assert t == HIT[k], (k, t)
# w_all 칼 자리: 칼이 흐려 거의 안 보이는 장(칼날 40칸 밑)은 앞뒤 멀쩡한 장 사이로 이음 (front_render.py 와 같음)
FR = json.load(open(FC + 'grip.json'))['frames']
ok = [f['blade'] >= 40 for f in FR]
for k, f in enumerate(FR):
    if ok[k]: continue
    p = max([i for i in range(k) if ok[i]], default=None); n = min([i for i in range(k + 1, len(FR)) if ok[i]], default=None)
    if p is None or n is None: continue
    t = (k - p) / (n - p); da = (FR[n]['ang'] - FR[p]['ang'] + 180) % 360 - 180
    f['ang'] = FR[p]['ang'] + da * t; f['guard'] = [FR[p]['guard'][i] * (1 - t) + FR[n]['guard'][i] * t for i in range(2)]; f['behind'] = False
G2 = json.load(open(F2 + 'grip2.json'))['frames']
def src(key):
    if isinstance(key, str):
        s_, n = key.split('_'); r = G2[f'{s_}_{int(n)}']; return Image.open(F2 + f'body2/{key}.png'), r, r.get('s', 1.0), True
    return Image.open(FC + f'body/{key:03d}.png'), FR[key], 1.0, key < 198
def clean(im):
    """몸 덩어리와 떨어진 조각 = 그록 분홍 칼이 흐려 남은 흙색 자국 → 지움 (내려찍기 흙먼지 198장부터는 그대로)"""
    a = np.array(im.convert('RGBA')); n_, lab, st, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    if n_ > 2: main = 1 + int(np.argmax(st[1:, 4])); a[(lab != main) & (lab > 0), 3] = 0
    return Image.fromarray(a)
need = []
for L in ANIM.values():
    for f, _ in L:
        if f not in need: need.append(f)
od = OUT + 'atk_front'; shutil.rmtree(od, ignore_errors=True); os.makedirs(od); grip = {}
for j, key in enumerate(need):
    im, r, s, cl = src(key)
    if cl: im = clean(im)
    im = im.convert('RGBA').crop((22, 22, 278, 278))   # 300판(발 150,268) → 256판(발 128,246)
    nm = f'{j:03d}.png'; im.save(os.path.join(od, nm))
    grip[nm] = {'src': str(key), 'guard': [round(r['guard'][0] - 22, 1), round(r['guard'][1] - 22, 1)], 'ang': round(float(r['ang']), 1), 'behind': bool(r['behind']), 's': round(float(s), 3)}
json.dump(grip, open(os.path.join(od, 'grip.json'), 'w'), ensure_ascii=False, indent=0)
anims = {k: [['atk_front', need.index(f), n] for f, n in L] for k, L in ANIM.items()}
json.dump(anims, open(OUT + 'atk_anims_front.json', 'w'), ensure_ascii=False, indent=0)
print('장', len(need), {k: sum(x[2] for x in v) for k, v in anims.items()})
