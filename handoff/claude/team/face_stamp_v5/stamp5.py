# 얼굴 이식 v5 (사장님 10-27 「중간에 얼굴이 너무 색깔이 틀려지는 거 고쳐라, 이 얼굴(정6)로 통일」)
# v4 와 다른 점: ① 판은 정6 얼굴 그대로(6색으로 줄이지 않음) ② 모든 장(안 찍은 장 포함)의 머리 둘레 살색(목·귀·턱 조각까지)을
#   정6 얼굴 살색으로 바꿈: 그 장 살색 밝기를 정6 밝기에 맞춘 뒤, 밝기가 가장 가까운 정6 살색 하나로 → 장마다 얼굴색이 튀지 않음
import json, sys, numpy as np
from PIL import Image
from scipy import ndimage
from common import load, skinmask
D, FIX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
meta = json.load(open(D + '/meta.json'))['anims']
def area(a): return ndimage.binary_fill_holes(ndimage.binary_closing(skinmask(a), iterations=1))
def skin_all(a, rows=46):
    f = a.astype(float) / 255; r, g, b, al = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b); s = (mx - mn) / np.maximum(mx, 1e-6)
    m = (al > .78) & (r > g) & (g >= b - .02) & (mx > .42) & (s > .1) & (s < .5) & (r - g > .05)
    ys = np.nonzero((al > .16).any(1))[0]
    if not len(ys): return m
    m[:ys.min()] = False; m[ys.min() + rows:] = False
    lab, n = ndimage.label(m); keep = np.zeros_like(m)
    for k in range(1, n + 1):
        c = lab == k
        if c.sum() >= 2: keep |= c
    return keep
L = lambda c: c[..., 0] * .3 + c[..., 1] * .59 + c[..., 2] * .11
plates = {}
for dn, fn in [('down', 'front_fixed_full.png'), ('right', 'side_fixed_full.png')]:
    a = load(f'{FIX}/{fn}'); m = area(a); ys, xs = np.nonzero(m)
    plates[dn] = (a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(), m[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
ref = load(f'{FIX}/front_fixed_full.png'); rs = skinmask(ref)
PAL = np.unique(ref[rs][:, :3].astype(int), axis=0); PL = L(PAL.astype(float)); REF_L = L(ref[rs][:, :3].astype(float)).mean()
def lock(px):
    l = L(px.astype(float)); l = l * (REF_L / max(l.mean(), 1))
    return PAL[np.abs(l[:, None] - PL[None]).argmin(1)]
table, skipped = {}, []
for n, frs in meta.items():
    dn = 'down' if n.endswith('_down') else ('right' if n.endswith('_right') else ('up' if n.endswith('_up') else None))
    if dn is None or n.startswith(('death', 'cast')): continue
    for fn, ax, ay, t in frs:
        a = load(f'{D}/{fn}'); out = a.copy(); rec = {'ok': False}; put_full = np.zeros(a.shape[:2], bool)
        if dn in plates:
            Q, Mq = plates[dn]; h, w = Mq.shape; tm = area(a)
            if tm.sum() >= 12:
                ty, tx = [int(v) for v in np.argwhere(tm).mean(0)]; cy, cx = [int(v) for v in np.argwhere(Mq).mean(0)]; best = (-1, 0, 0)
                for dy in range(-8, 9):
                    for dx in range(-8, 9):
                        y0, x0 = ty - cy + dy, tx - cx + dx
                        if y0 < 0 or x0 < 0 or y0 + h > a.shape[0] or x0 + w > a.shape[1]: continue
                        t2 = tm[y0:y0 + h, x0:x0 + w]; iou = (t2 & Mq).sum() / max((t2 | Mq).sum() + tm.sum() - t2.sum(), 1)
                        if iou > best[0]: best = (iou, y0, x0)
                iou, y0, x0 = best; rec = {'iou': round(float(iou), 2), 'dx': int(x0), 'dy': int(y0), 'ok': bool(iou >= .5)}
                if iou >= .5:
                    put = Mq & ndimage.binary_dilation(tm, iterations=1)[y0:y0 + h, x0:x0 + w] & (a[y0:y0 + h, x0:x0 + w, 3] > 0)
                    out[y0:y0 + h, x0:x0 + w][put] = Q[put]; put_full[y0:y0 + h, x0:x0 + w] = put
        sk = skin_all(a) & ~put_full          # 판이 안 덮은 살색(목·귀·턱·안 찍은 장 얼굴) → 정6 살색으로
        if sk.any(): out[sk, :3] = lock(out[sk, :3]).astype(np.uint8)
        rec['locked'] = int(sk.sum())
        if dn in plates and not rec['ok']: skipped.append(fn)
        Image.fromarray(out).save(f'{OUT}/{fn}'); table[fn] = rec
json.dump({'skin_palette': PAL.tolist(), 'frames': table}, open(OUT + '/face_table.json', 'w'), indent=0)
print('정6 살색', len(PAL), '가지 / 이식', sum(v['ok'] for v in table.values()), '/', len(table), '/ 판 없이 살색만 맞춘 장:', skipped)
