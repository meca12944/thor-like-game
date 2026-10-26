# 찍은 낱장(proj/bake) → 동작마다 아틀라스 한 장 (줄 = 방향 down/right/up/left, 한 방향에 cols칸씩) + atlas.json
import json, math, os, sys
from PIL import Image

proj = sys.argv[1]
src, dst = os.path.join(proj, 'bake'), os.path.join(proj, 'atlas')
os.makedirs(dst, exist_ok=True)
meta = json.load(open(os.path.join(src, 'bake.json')))
DIRS = ['down', 'right', 'up', 'left']
ox0, oy0 = meta['origin']
out = {'fps': meta['fps'], 'px': meta['px'], 'cam_size': meta['cam_size'], 'anims': {}}
total = 0
for n, a in meta['anims'].items():
    nf = a['frames']
    ims = {(d, f): Image.open(os.path.join(src, f'{n}_{d}_{f:03d}.png')).convert('RGBA') for d in DIRS for f in range(nf)}
    box = None
    for im in ims.values():
        b = im.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    x0, y0 = max(box[0] - 3, 0), max(box[1] - 3, 0)
    x1, y1 = min(box[2] + 3, meta['px']), min(box[3] + 3, meta['px'])
    edge = box[0] <= 0 or box[1] <= 0 or box[2] >= meta['px'] or box[3] >= meta['px']
    w, h = x1 - x0, y1 - y0
    cols = min(nf, max(1, 8192 // w))
    rpd = math.ceil(nf / cols)
    sheet = Image.new('RGBA', (cols * w, 4 * rpd * h))
    for di, d in enumerate(DIRS):
        for f in range(nf):
            sheet.paste(ims[(d, f)].crop((x0, y0, x1, y1)), ((f % cols) * w, (di * rpd + f // cols) * h))
    sheet.save(os.path.join(dst, n + '.png'), optimize=True)
    total += os.path.getsize(os.path.join(dst, n + '.png'))
    out['anims'][n] = {'frames': nf, 'cols': cols, 'rows_per_dir': rpd, 'w': w, 'h': h, 'ox': ox0 - x0, 'oy': oy0 - y0,
                       'tips': {d: [[t[0] - x0, t[1] - y0, t[2] - x0, t[3] - y0] for t in a['tips'][d]] for d in DIRS}}
    print(f'{n:28s} {nf:3d}장 칸 {w}x{h} 판 {sheet.size} {"!! 가장자리 잘림" if edge else ""}')
json.dump(out, open(os.path.join(dst, 'atlas.json'), 'w'))
print('합계', round(total / 1e6, 1), 'MB')
