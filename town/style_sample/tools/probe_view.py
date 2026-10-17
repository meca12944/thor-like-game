import json, sys, numpy as np
sys.path.insert(0, '/workspace/town-demo/style_sample/tools')
from hero_measure import frames, RAW
from head_probe2 import head2
from PIL import Image, ImageDraw
C = json.load(open('/workspace/town-demo/tools/anim/hero_anim.src.json'))
ks = sys.argv[2:]; out = sys.argv[1]; tiles = []
for k in ks:
    s = C['sheets'][k]; fr = frames(RAW + s['file'] + '.jpg', s['n'])
    for i in ([s['ref']] if len(ks) > 4 else range(len(fr))):
        f = fr[i]; h = head2(f); im = Image.new('RGB', (f.shape[1] + 40, 420), (60, 80, 60)); t = Image.fromarray(f, 'RGBA')
        im.paste(t, (20, 10), t); d = ImageDraw.Draw(im)
        for y, c in ((h['top'], (255, 255, 0)), (h['chin'], (255, 0, 0))):
            if y is not None: d.line((0, 10 + y, im.width, 10 + y), fill=c)
        d.text((2, 400), f'{k}{i} {h["headH"]}', fill='white'); tiles.append(im)
W = sum(t.width for t in tiles); img = Image.new('RGB', (W, 420)); x = 0
for t in tiles: img.paste(t, (x, 0)); x += t.width
img.save(out)
