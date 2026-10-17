import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import *
from ruler import ruled, R
from chars import CH, V
for name, p in CH:
    if sys.argv[1:] and name not in sys.argv[1:]: continue
    fr = dict(zip(V, load_frames(p, 3)))
    def headcrop(v):
        f = fr[v]; r = R[name][v]; H = r['sole'] - r['crown']
        m = f[..., 3] > .5; c0 = r['crown']; band = m[c0:c0 + int(H * .25)]; xs = np.where(band)[1]
        cx = int(np.median(xs)); x0 = max(0, cx - 70); g = f[:, x0:cx + 70]
        return ruled(g, max(0, c0 - 10), c0 + int(H * .26), 2)
    def splitcrop(v):
        f = fr[v]; r = R[name][v]; s = r['split'] or int(r['sole'] * .58); m = f[..., 3] > .5
        xs = np.where(m[s + 20])[0] if (s + 20) < m.shape[0] else np.array([f.shape[1] // 2]); cx = int((xs.min() + xs.max()) / 2) if len(xs) else f.shape[1] // 2
        g = f[:, max(0, cx - 60):cx + 60]; return ruled(g, max(0, s - 50), s + 40, 2)
    P = [headcrop('front'), headcrop('side'), splitcrop('front'), splitcrop('back')]
    W = P[0].width + P[1].width + 20; Hh = max(P[0].height, P[1].height) + max(P[2].height, P[3].height) + 20
    img = Image.new('RGB', (max(W, P[2].width + P[3].width + 20), Hh), (0, 0, 0))
    img.paste(P[0], (0, 0)); img.paste(P[1], (P[0].width + 20, 0)); y = max(P[0].height, P[1].height) + 20
    img.paste(P[2], (0, y)); img.paste(P[3], (P[2].width + 20, y)); img.save(f'/workspace/town-demo/style_sample/work/r2_{name}.png'); print(name, img.size)
