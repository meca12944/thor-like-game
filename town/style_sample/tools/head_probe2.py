import json, sys, numpy as np
sys.path.insert(0, '/workspace/town-demo/style_sample/tools')
from hero_measure import frames, RAW
from head_probe import body_mask
from scipy import ndimage as ndi
def skin(rgba):
    r, g, b = [rgba[..., i].astype(int) for i in range(3)]
    return (rgba[..., 3] > 0) & (r > 140) & (r - b > 45) & (r > g + 10) & (g > 80) & (r - g < 90)
def head2(rgba):
    m = body_mask(rgba); ys = np.where(m.sum(1) >= 3)[0]; top = int(ys[0]); bot = int(ys[-1]); H = bot - top + 1
    cx = np.where(m[top:top + 12])[1].mean()
    sk = ndi.binary_opening(skin(rgba), iterations=1)
    lab, n = ndi.label(sk); best = None
    for i, o in enumerate(ndi.find_objects(lab)):
        if o is None: continue
        t, bb = o[0].start, o[0].stop; x = (o[1].start + o[1].stop) / 2; sz = (lab[o] == i + 1).sum()
        if t - top < H * .3 and sz > 60 and abs(x - cx) < 70:
            sc = sz - abs(x - cx) * 5
            if best is None or sc > best[0]: best = (sc, bb, x)
    chin = best[1] if best else None
    return dict(top=top, chin=chin, headH=(chin - top) if chin else None, H=H, bot=bot)
if __name__ == '__main__':
    C = json.load(open('/workspace/town-demo/tools/anim/hero_anim.src.json'))
    for k, s in C['sheets'].items():
        if sys.argv[1:] and k not in sys.argv[1:]: continue
        fr = frames(RAW + s['file'] + '.jpg', s['n']); hs = [head2(f) for f in fr]
        print(k, 'headH', [h['headH'] for h in hs], 'H', [h['H'] for h in hs])
