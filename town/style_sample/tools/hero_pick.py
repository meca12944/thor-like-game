import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import load_frames
from PIL import Image, ImageDraw, ImageFont
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 14)
M = json.load(open('/workspace/town-demo/style_sample/work/hero_sheet_meas.json')); RAW = '/workspace/town-demo/src/hero/anim_raw/'
idl = load_frames(RAW + 'idle3.jpg', 3); hw = {0: 99., 1: 103., 2: 99.}
def vw(fn): return 'back' if '_up' in fn else ('side' if ('right' in fn or 'spin' in fn or fn.startswith('hurt')) else 'front')
def img(f, s):
    t = Image.fromarray(np.dstack([f[..., :3], f[..., 3] * 255]).astype(np.uint8), 'RGBA'); return t.resize((max(1, int(t.width * s)), max(1, int(t.height * s))), Image.LANCZOS)
keys = sys.argv[2].split(','); S = 0.5
rows = []
for k in keys:
    s = M[k]; v = vw(s['file']); vi = {'front': 0, 'side': 1, 'back': 2}[v]
    fr = load_frames(RAW + s['file'] + '.jpg', s['n'])[s['ref']]
    eh = 91 / s['head_med'] if s['head_med'] and v != 'back' else None; ew = hw[vi] / s['headW_med']
    cands = [('idle', idl[vi], 1.0), ('A head %.2f' % eh if eh else 'A -', fr, eh or 0), ('B width %.2f' % ew, fr, ew)]
    r = Image.new('RGB', (900, 230), (60, 80, 60)); d = ImageDraw.Draw(r); x = 10
    for lab, f, sc in cands:
        if sc:
            t = img(f, sc * S); r.paste(t, (x, 225 - t.height), t)
        d.text((x, 2), f'{k} {lab}', fill='white', font=FT); x += 300
    for yy in (225 - int(388 * S), ): d.line((0, yy, 900, yy), fill=(255, 255, 0))
    rows.append(r)
out = Image.new('RGB', (900, 235 * len(rows))); 
for i, r in enumerate(rows): out.paste(r, (0, i * 235))
out.save(f'/workspace/town-demo/style_sample/work/pick_{sys.argv[1]}.png')
