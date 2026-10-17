import json, sys, numpy as np
sys.path.insert(0, '/workspace/town-demo/style_sample/tools'); sys.path.insert(0, '/workspace/town-demo/tools/anim')
from hero_measure import frames, RAW
from scipy import ndimage as ndi
def body_mask(rgba):
    a = rgba[..., 3] > 0; r, g, b = [rgba[..., i].astype(int) for i in range(3)]
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
    steel = (mx > 140) & (mx - mn < 40); cyan = (b > 150) & (g > 150) & (r < 200) & (b - r > 40)
    m = a & ~steel & ~cyan
    lab, n = ndi.label(m)
    if n > 1:
        sz = ndi.sum(m, lab, range(1, n + 1)); m = lab == (np.argmax(sz) + 1)
    return m
def head(rgba):
    m = body_mask(rgba); ys = np.where(m.sum(1) >= 3)[0]; top = ys[0]; bot = ys[-1]
    # head centre column: mean x of the top 15 rows
    cx = np.where(m[top:top + 15])[1].mean()
    hw = None
    prof = []
    for y in range(top, bot):
        row = m[y]; 
        # contiguous run containing (nearest to) cx
        xs = np.where(row)[0]
        if len(xs) == 0: prof.append(0); continue
        j = np.argmin(abs(xs - cx)); x0 = x1 = xs[j]
        while x0 - 1 >= 0 and row[x0 - 1]: x0 -= 1
        while x1 + 1 < len(row) and row[x1 + 1]: x1 += 1
        prof.append(x1 - x0 + 1)
    prof = np.array(prof, float); prof = ndi.uniform_filter1d(prof, 5)
    hmax = prof[:int(len(prof) * .35)].max(); ymax = int(prof[:int(len(prof) * .35)].argmax())
    # neck: first local min after the head max where width < 0.75 * head width
    for y in range(ymax, int(len(prof) * .6)):
        if prof[y] < .72 * hmax and prof[y] <= prof[y - 1] and prof[y] <= prof[min(len(prof) - 1, y + 1)]:
            return dict(top=int(top), neck=int(y), headH=int(y), headW=float(hmax), H=int(bot - top + 1))
    return dict(top=int(top), neck=None, headH=None, headW=float(hmax), H=int(bot - top + 1))
if __name__ == '__main__':
    C = json.load(open('/workspace/town-demo/tools/anim/hero_anim.src.json'))
    for k, s in C['sheets'].items():
        if sys.argv[1:] and k not in sys.argv[1:]: continue
        fr = frames(RAW + s['file'] + '.jpg', s['n']); hs = [head(f) for f in fr]
        print(k, 'headH', [h['headH'] for h in hs], 'headW', [round(h['headW']) for h in hs], 'H', [h['H'] for h in hs])
