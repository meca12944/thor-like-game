# 손에 드는 칼 그림 (사장님 10-31 「칼이 아이템이 바뀌면 주인공이 들고 있는 칼도 바꿔야」 「칼 크기 조금만 줄이자」)
# 도감 아이콘(test128/assets/icons/grok/<id>_128.webp, 칼이 45° — 손잡이 왼쪽 아래·칼끝 오른쪽 위)을 4배로 키워 45° 돌려 세우고(칼끝 위),
# 주인공 키(144칸) × 길이 비율로 미리곱 LANCZOS 한 번 줄임(투명 가장자리 단단히). 한 번만 줄이기: 키우기·돌리기는 큰 판에서, 줄이기는 마지막 한 번.
# 쓰는 법: python3 make_hand.py <아이콘 폴더> <출력 폴더> [전체 배율=0.85]
import sys, os, numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; SC = float(sys.argv[3]) if len(sys.argv) > 3 else .85
H = 144
# 길이 = 주인공 키 대비 (처음 가안 값 × SC). 장검 0.55, 대검 0.72, 세검 0.6, 창검 0.95, 목검 0.5 …
LEN = {'w_loop_long': .55, 'w_ara_spine': .6, 'w_iron_broken': .62, 'w_oath_ink': .58, 'w_noble_rapier': .6, 'w_heretic_great': .72, 'w_husk_mirror': .62,
       'w_guard_spear': .95, 'w_alch_mercury': .58, 'w_hand_breaker': .72, 'w_king_great': .72, 'w_first_loop': .58, 'w_true_death': .6, 'w_cradle_wood': .5, 'w_executioner': .7}
os.makedirs(out, exist_ok=True)
for w, k in LEN.items():
    im = Image.open(f'{src}/{w}_128.webp').convert('RGBA')
    big = im.resize((512, 512), Image.LANCZOS).rotate(45, Image.BICUBIC, expand=True); big = big.crop(big.getbbox())
    L = round(H * k * SC); s = L / big.height
    a = np.asarray(big).astype(np.float32); al = a[..., 3:4] / 255; pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
    w2 = max(1, round(big.width * s)); ch = [np.asarray(Image.fromarray(pm[..., c], 'F').resize((w2, L), Image.LANCZOS)) for c in range(4)]
    A = np.clip(ch[3], 0, 255); rgb = np.stack([np.clip(ch[c] / np.maximum(A, 1e-3) * 255, 0, 255) for c in range(3)], 2)
    o = Image.fromarray(np.concatenate([rgb, ((A > 100) * 255)[..., None]], 2).astype(np.uint8), 'RGBA'); o = o.crop(o.getbbox())
    o.save(f'{out}/{w}_hand.png'); print(w, '길이', o.height, '폭', o.width)
