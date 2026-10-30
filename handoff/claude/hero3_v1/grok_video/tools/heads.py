# 얼굴 찍기 전·후 머리 크게: python3 heads.py <찍기 전 폴더> <찍은 뒤 폴더> <장 수> <출력 png>
import sys, numpy as np
from PIL import Image, ImageDraw
a_dir, b_dir, n, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
Z = 6; W = 34; per = 9; rows = (n + per - 1) // per
o = Image.new('RGB', (per * W * Z, rows * (2 * W * Z + 24)), (46, 48, 56)); d = ImageDraw.Draw(o)
for i in range(n):
    a = Image.open(f'{b_dir}/{i:03d}.png'); al = np.asarray(a)[..., 3]; bb = a.getbbox(); top = bb[1]
    xs = np.nonzero(al[top:top + 30].any(0))[0]; xr = xs.max()
    box = (xr - W + 3, top, xr + 3, top + W)
    for r, dd in enumerate([a_dir, b_dir]):
        im = Image.open(f'{dd}/{i:03d}.png').crop(box).resize((W * Z, W * Z), Image.NEAREST)
        o.paste(im, ((i % per) * W * Z, (i // per) * (2 * W * Z + 24) + 24 + r * W * Z), im)
    d.text(((i % per) * W * Z + 4, (i // per) * (2 * W * Z + 24) + 4), str(i), fill=(255, 255, 0))
o.save(out)
