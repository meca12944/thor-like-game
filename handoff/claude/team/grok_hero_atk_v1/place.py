# 모션연구방 규칙대로 놓기 (motion_lab/grok_hero/assemble_attack.py 와 같음): 크기 = 그 방향 걷기 배율(clips.json walk_<방향>.scale),
# 발바닥 = 189, 두 발 가운데 = 128, 256x256 칸. 발 자리는 모션방 attack_feet 의 원본 시트 좌표를 그대로 씀 (서로 같은 점).
import json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from pxscale import pxscale
C = json.load(open('clips.json')); ROWS = {'down': 75, 'right': 540, 'up': 1010, 'left': 1480}; COLS = [0, 341, 683]
FEET = {'down': [[166, 444], [454, 444], [786, 444]], 'right': [[146, 904], [454, 904], [767, 904]], 'up': [[135, 1374], [430, 1374], [768, 1374]], 'left': [[193, 1843], [570, 1843], [937, 1843]]}  # 모션방 f29e82ee 정정판 (2타: 몸 덩어리만으로 다시 잼)
# 공격 시트의 주인공이 걷기 시트보다 크게 그려져 있음: 정면 선 키 = 걷기 167px(시트) / 공격 1타 285px(시트) -> 0.586 (걷기 배율 그대로면 머리가 256 칸 위로 잘림)
ATK_K = 167 / 286  # = 0.584, 모션방과 같은 값
os.makedirs('placed', exist_ok=True); out = {}
for d in FEET:
    s = C[f'walk_{d}']['scale'] * ATK_K
    for i in range(3):
        im = Image.open(f'cells/{d}_{i + 1}_rgba.png'); fx, fy = FEET[d][i][0] - COLS[i], FEET[d][i][1] - ROWS[d]  # feet in my cell
        im = pxscale(im, s); dx, dy = round(128 - fx * s), round(189 - fy * s)
        c = Image.new('RGBA', (256, 256)); c.paste(im, (dx, dy), im); c.save(f'placed/atk{i + 1}_{d}.png'); out[f'atk{i + 1}_{d}'] = dict(scale=s, feet_cell=[fx, fy], dx=dx, dy=dy)
json.dump(out, open('placed/place.json', 'w'), indent=1); print(len(out), 'placed')
