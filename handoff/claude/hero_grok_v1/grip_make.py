# 칼 손 자리 1차 (눈으로 찍음, 2.5배 격자 표에서 읽음 ±5px): 게임 동작 이름 → 그림 폴더, [dx, dy] 발(128,189) 기준 + 각도 규칙
import json, math, numpy as np, os
from PIL import Image, ImageDraw
def sinus(n, c, a, ph=0): return [(c[0] + a[0] * math.cos(2 * math.pi * i / n + ph), c[1] + a[1] * math.cos(2 * math.pi * i / n + ph)) for i in range(n)]
P = {  # (게임 이름, 폴더, 손 점들)
 'walk_down': ('walk_down', [(-23,-63),(-22,-63),(-23,-63),(-19,-63),(-19,-63),(-19,-63),(-23,-63),(-26,-63)]),
 'walk_dr':   ('walk_dr',   [(0,-63),(2,-63),(10,-65),(16,-67),(20,-66),(22,-67),(10,-65),(2,-67)]),
 'walk_right':('walk_right', sinus(8, (17,-72), (30,-4), -math.pi / 8)),
 'walk_up':   ('walk_ur',   [(34,-69),(38,-69),(40,-77),(40,-77),(38,-73),(40,-69),(36,-77),(34,-69)]),
 'walk_n':    ('walk_up',   [(29,-69),(30,-61),(32,-61),(34,-65),(32,-61),(30,-59)]),
 'run_down':  ('run_down',  sinus(8, (-27,-75), (4,3))),
 'run_dr':    ('run_dr',    sinus(8, (6,-76), (10,6))),
 'run_right': ('run_right', [(52,-99),(48,-99),(56,-97),(48,-87),(32,-79),(28,-79),(32,-73),(48,-87)]),
 'run_up':    ('run_ur',    [(32,-107),(38,-107),(44,-97),(40,-81),(30,-79),(20,-79),(40,-81),(46,-97)]),
 'run_n':     ('run_up',    [(28,-99),(26,-87),(30,-101),(28,-101),(22,-103),(26,-85),(30,-81),(28,-73)]),
}
BASE = {'walk': {'right': 25, 'dr': 50, 'down': 112, 'up': 18, 'n': 70}, 'run': {'right': 155, 'dr': 135, 'down': 100, 'up': 160, 'n': 80}}
out = {'_doc': '검흔·효과방 10-25 1차: 칼 손(오른손) 자리 [dx, dy, deg] — 발(128,189) 기준 art px, deg 캔버스(0=오른쪽, 90=아래), 왼쪽은 게임이 뒤집음. 손 = 눈으로 찍음(±5px, 게임에서 약 1px). 각도 = 걷기 앞-아래 20~30°(옆모습은 손 흔들림 따라 ±10°), 달리기 = 칼을 뒤로 끌기. 확인 표 grip_check.png.'}
rows = []
for name, (fold, pts) in P.items():
    mv, dr = name.split('_'); fr = sorted(f for f in os.listdir(fold) if f.endswith('.png')); assert len(fr) == len(pts), (name, len(fr), len(pts))
    mx = np.mean([p[0] for p in pts]); sp = max(1, max(abs(p[0] - mx) for p in pts)); side = dr in ('right', 'dr', 'up')
    g = [[round(x, 1), round(y, 1), int(round(BASE[mv][dr] - ((x - mx) / sp * 10 if side and mv == 'walk' else 0)))] for x, y in pts]
    out[name] = g; rows.append((name, fold, fr, g))
json.dump(out, open('grip.json', 'w'), ensure_ascii=False, indent=1)
S = 1.6; cw, chh = int(150 * S), int(150 * S); sh = Image.new('RGBA', (8 * cw, len(rows) * chh), (150, 150, 160, 255)); dw = ImageDraw.Draw(sh)
for j, (name, fold, fr, g) in enumerate(rows):
    for i, f in enumerate(fr):
        a = Image.open(f'{fold}/{f}').convert('RGBA').crop((53, 54, 203, 204)).resize((cw, chh), Image.NEAREST); sh.alpha_composite(a, (i * cw, j * chh))
        x = i * cw + (128 - 53 + g[i][0]) * S; y = j * chh + (189 - 54 + g[i][1]) * S; t = math.radians(g[i][2]); L = 21 * 144 / 117 * S * 1.6
        dw.line([(x, y), (x + math.cos(t) * L, y + math.sin(t) * L)], fill=(235, 240, 250, 255), width=3); dw.ellipse([x - 4, y - 4, x + 4, y + 4], outline=(0, 255, 200, 255), width=2)
    dw.text((3, j * chh + 3), name, fill=(255, 255, 0, 255))
sh.save('grip_check.png'); print({k: len(v) for k, v in out.items() if k[0] != '_'})
