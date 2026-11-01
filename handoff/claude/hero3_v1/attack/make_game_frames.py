# 공격 장 → 게임 그림 폴더 (사장님 11-01 「좋아 올려」)
# 옆 공격 3타(그록 v9 1~2타 + 3타 이어 찍기) + 달리다 찌르기(v3 + 빼기 다시)에서 게임에 쓰는 장만 골라 game144/atk_side · thrust_side 에 256칸(발 = 128,246)으로 두고,
# 장마다 손 자리(코등이)·칼 각도(화면, 0 = 오른쪽, -90 = 위)를 grip.json 에 적음. 틱 표(게임 공격 길이 30/30/45·26틱, 치는 장 시작 8/8/11·4틱)도 여기서 정함.
# 쓰는 법: python3 make_game_frames.py <공격 작업 폴더(grip.json, body/)> <찌르기 작업 폴더(grip4.json, body4/)> <game144 폴더>
import json, os, sys, shutil
from PIL import Image
SRC = {'atk_side': (sys.argv[1], 'grip.json', 'body'), 'thrust_side': (sys.argv[2], 'grip4.json', 'body4')}
OUT = sys.argv[3]
# (영상, 장, 틱) — 치는 장(칼이 앞을 지나는 장)이 틱 합 8/8/11/4 자리에서 시작
#  1타: 머리 위 → 앞 → 뒤 아래로 내려벰(19·20장에 칼이 앞), 2타: 뒤 → 아래 → 앞 위로 올려벰(51·52장), 3타: 머리 위 뒤로 크게 들어 한 발 내딛으며 내려침(62·63장)
#  찌르기: 달리며 칼 내밂 → 다 뻗음(80장) → 짧게 버팀 → 빼기 다시(그록, 90장에서 바로 당김)
ANIM = {
 'hit1': ('atk_side', [('fv',4,2),('fv',9,2),('fv',13,2),('fv',16,1),('fv',17,1), ('fv',19,2),('fv',20,2),('fv',21,2),('fv',22,2),('fv',23,2),('fv',24,2),('fv',25,3),('fv',27,3),('fv',30,2),('fv',35,2)]),
 'hit2': ('atk_side', [('fv',38,2),('fv',43,2),('fv',45,1),('fv',47,1),('fv',48,1),('fv',49,1), ('fv',51,2),('fv',52,2),('fv',53,2),('fv',54,2),('fv',55,2),('fv',56,2),('fv',57,3),('fv',59,3),('fv',62,4)]),
 'hit3': ('atk_side', [('f3',30,2),('f3',40,2),('f3',49,2),('f3',54,2),('f3',57,1),('f3',59,1),('f3',60,1), ('f3',61,2),('f3',62,2),('f3',63,2),('f3',64,2),('f3',65,2),('f3',66,3),('f3',68,3),('f3',70,4),('f3',75,5),('f3',90,5),('f3',110,4)]),
 'thrust': ('thrust_side', [('f',75,1),('f',77,1),('f',78,1),('f',79,1), ('f',80,2),('f',81,2),('f',82,2),('f',86,2),('f',90,2), ('fc',5,2),('fc',9,2),('fc',12,2),('fc',16,2),('fc',21,2),('fc',26,2)]),
}
TOT = {'hit1': (30, 8), 'hit2': (30, 8), 'hit3': (45, 11), 'thrust': (26, 4)}
for k, (g, L) in ANIM.items():
    t = [x[2] for x in L]; tot, hit = TOT[k]; assert sum(t) == tot, (k, sum(t)); acc = 0
    for x in L:
        if acc >= hit: break
        acc += x[2]
    assert acc == hit, (k, acc)
meta = {}
for g, (D, gj, bd) in SRC.items():
    J = json.load(open(os.path.join(D, gj)))['frames']; idx = {(f['src'], f['k']): i for i, f in enumerate(J)}
    need = []
    for k, (gg, L) in ANIM.items():
        if gg != g: continue
        for s, n, _ in L:
            if (s, n) not in need: need.append((s, n))
    od = os.path.join(OUT, g); shutil.rmtree(od, ignore_errors=True); os.makedirs(od)
    grip = {}
    for j, key in enumerate(need):
        i = idx[key]; im = Image.open(os.path.join(D, bd, f'{i:03d}.png')).convert('RGBA').crop((22, 22, 278, 278))   # 300판(발 150,268) → 256판(발 128,246)
        nm = f'{j:03d}.png'; im.save(os.path.join(od, nm))
        f = J[i]; grip[nm] = {'src': key[0], 'k': key[1], 'guard': [round(f['guard'][0] - 22, 1), round(f['guard'][1] - 22, 1)], 'ang': round(f['ang'], 1), 'behind': bool(f['behind'])}
    json.dump(grip, open(os.path.join(od, 'grip.json'), 'w'), ensure_ascii=False, indent=0)
    meta[g] = need
anims = {k: [[g, meta[g].index((s, n)), t] for s, n, t in L] for k, (g, L) in ANIM.items()}
json.dump(anims, open(os.path.join(OUT, 'atk_anims.json'), 'w'), ensure_ascii=False, indent=0)
print({g: len(v) for g, v in meta.items()}, {k: sum(x[2] for x in v) for k, v in anims.items()})
