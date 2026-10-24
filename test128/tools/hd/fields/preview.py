"""quick offline overview of an HD field: ground + decoArt + props sorted by foot y (python, no browser)."""
import json, os, sys, hashlib
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
def render(mid, out, scale=.5):
    m = json.load(open(f'{ROOT}/maps/{mid}.json')); h = m['hd']; D = h['D']; cs = 16 * D
    g = Image.open(f'{ROOT}/{h["ground"]}').convert('RGBA'); items = []; cache = {}
    def im(p):
        if p not in cache: cache[p] = Image.open(f'{ROOT}/{p}').convert('RGBA')
        return cache[p]
    for y, row in enumerate(m['ground']):
        for x, ch in enumerate(row):
            A = h['decoArt'].get(ch)
            if not A: continue
            hs = int(hashlib.md5(f'{x},{y}'.encode()).hexdigest(), 16)
            v = A[hs % len(A)]; items.append(((y + 1) * cs, v, (x + .5) * cs, (y + 1) * cs - 3, 1, (hs >> 8) & 1))
    for q in h.get('props', []):
        s = D / q.get('D', D); items.append((q['y'] * cs - (9e9 if q.get('under') else 0), q, q['x'] * cs, q['y'] * cs, s, q.get('flip', False)))
    for _, v, fx, fy, s, fl in sorted(items, key=lambda t: t[0]):
        i = im(v['img'])
        if s != 1: i = i.resize((int(i.width * s), int(i.height * s)), Image.NEAREST)
        if fl: i = i.transpose(Image.FLIP_LEFT_RIGHT); ax = i.width - v['ax'] * s
        else: ax = v['ax'] * s
        g.alpha_composite(i, (int(fx - ax), int(fy - v['ay'] * s))) if fx - ax >= 0 and fy - v['ay'] * s >= 0 else g.paste(i, (int(fx - ax), int(fy - v['ay'] * s)), i)
    g = g.resize((int(g.width * scale), int(g.height * scale)), Image.LANCZOS).convert('RGB'); g.save(out, quality=85); return g.size
if __name__ == '__main__':
    for mid in sys.argv[1:]: print(render(mid, f'/tmp/work/pv_{mid}_{os.getpid()}.jpg'))
