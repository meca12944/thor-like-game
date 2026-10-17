import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import *
from chars import CH, V
res = {}; tiles = []
for name, p in CH:
    fr = load_frames(p, 3); res[name] = {}
    for v, f in zip(V, fr):
        m = body(f, 'hero' if name == 'hero' else None); c0, c3 = crown_sole(m, 25 if name != 'hero' else 3); c1 = chin_auto(f, m, c0, c3) if v != 'back' else None; c2 = split_auto(m, c0, c3) if v != 'side' else None
        res[name][v] = dict(crown=c0, chin=c1, split=c2, sole=c3, w=f.shape[1])
        im = Image.new('RGB', (f.shape[1] + 20, 500), (60, 80, 60)); t = Image.fromarray(np.dstack([f[..., :3], f[..., 3] * 255]).astype(np.uint8), 'RGBA')
        im.paste(t, (10, 10), t); d = ImageDraw.Draw(im)
        for y, c in ((c0, (255, 255, 0)), (c1, (255, 0, 0)), (c2, (0, 200, 255)), (c3, (255, 255, 255))):
            if y is not None: d.line((0, 10 + y, im.width, 10 + y), fill=c)
        d.text((2, 485), f'{name} {v} {c0}/{c1}/{c2}/{c3}', fill='white'); tiles.append(im)
json.dump(res, open('/workspace/town-demo/style_sample/work/src_landmarks.json', 'w'), indent=0)
for part in range(3):
    T = tiles[part * 9:(part + 1) * 9]; W = sum(t.width for t in T); img = Image.new('RGB', (W, 500)); x = 0
    for t in T: img.paste(t, (x, 0)); x += t.width
    img.save(f'/workspace/town-demo/style_sample/work/probe_src_{part}.png')
for k, v in res.items(): print(k, {kk: (vv['crown'], vv['chin'], vv['split'], vv['sole']) for kk, vv in v.items()})
