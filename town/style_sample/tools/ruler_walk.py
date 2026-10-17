import sys, os, numpy as np, time
sys.path.insert(0, os.path.dirname(__file__))
from walk_src import load_grid, S
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
names = sys.argv[1].split(','); view = sys.argv[2]; fi = int(sys.argv[3]) if len(sys.argv) > 3 else 0
k = 3; tiles = []
for n in names:
    f = load_grid(S + f'src/fem_walk/{n}_{view}.jpg')[fi]; H = f.shape[0]
    rgb = (f[..., :3] * f[..., 3:] + np.array([60, 80, 60]) * (1 - f[..., 3:])).astype(np.uint8)
    for (a, b) in ((0, int(H * .30)), (int(H * .40), int(H * .72))):
        crop = Image.fromarray(rgb[a:b]).resize(((rgb.shape[1]) * k, (b - a) * k), Image.NEAREST)
        t = Image.new('RGB', (crop.width + 40, crop.height + 16), (20, 20, 20)); t.paste(crop, (40, 16)); d = ImageDraw.Draw(t)
        for y in range(a - a % 5 + 5, b, 5):
            yy = 16 + (y - a) * k; d.line([(36 if y % 10 == 0 else 38, yy), (t.width, yy)] if y % 10 == 0 else [(30, yy), (40, yy)], fill=(200, 200, 200) if y % 10 == 0 else (120, 120, 120))
            if y % 10 == 0: d.text((0, yy - 7), str(y), font=F, fill='yellow')
        d.text((44, 0), f'{n} {view} f{fi} H{H}', font=F, fill='white'); tiles.append(t)
W = sum(t.width + 6 for t in tiles); Hh = max(t.height for t in tiles)
out = Image.new('RGB', (W, Hh), 'black'); x = 0
for t in tiles: out.paste(t, (x, 0)); x += t.width + 6
p = S + f'work/rw_{view}_{names[0]}_{int(time.time())}.png'; out.save(p); print(p, out.size)
