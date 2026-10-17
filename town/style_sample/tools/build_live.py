"""Bake the approved v2 (hero-matched) women for the LIVE game's 384x216 grid: 28 logical px tall (= live hero),
head 7 px (4.0 heads), leg split row 18, 1 px top margin for the walk bob.  Same pipeline as build_walk.py (56 px sample).
Output: town/assets/npcs/v2/<id>.png (rows down/left/right/up x [idle 4 | walk 8]) + meta.json."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import build_walk as BW
from proportions import finish, SS
from PIL import Image
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/npcs/v2/'); os.makedirs(R, exist_ok=True)
BW.set_size(28, 32); BW.OUTP = R + '{}.png'
meta = {}
for n in sys.argv[1].split(','):
    d = BW.build(n); meta[n] = BW.sheet(n, d); print(n, 'ok', {k[1]: v for k, v in BW.WK.items() if k[0] == n})
# 미소 (a_tool, town A shopkeeper): only a front still exists -> reproportion it (crown 17 | chin 58 | skirt hem 170 | sole 299,
# read on work/a_tool_ruler.png); standing NPC: 4-frame breathing idle in every row, walk = idle.
im = np.asarray(Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/npcs/a_tool.png')).convert('RGBA')).astype(np.float32)
f = im.copy(); f[..., 3] = (im[..., 3] > 128).astype(np.float32)
s = (17, 58, 170, 300)
ids = [BW.render(f, s, b) for b in BW.BREATH]; fin = finish(ids, 40)
fr = {'idle': fin, 'walk': [fin[0]] * 8}
meta['a_tool'] = BW.sheet('a_tool', {'front': fr, 'side': fr, 'back': fr}); meta['a_tool']['static'] = True
old = json.load(open(R + 'meta.json')) if os.path.exists(R + 'meta.json') else {}
old.update(meta); json.dump(old, open(R + 'meta.json', 'w'), indent=0)
