# 얼굴 도장 다시 시험 (사장님 10-27 「도장처럼 찍어 넣는 게 퀄리티 잘 나오는지 확인, 다시 시작」)
# 기준 = 지금 게임 걷기 첫 장 얼굴(정면 walk_down_00, 옆 walk_right_00). 모든 동작 장에 찍음:
#  자리 = 살색 모양 겹치기(±8px 찾기), 겹침 0.5 미만이면 안 찍음(고개가 돌았거나 가려짐)
#  바꾸는 칸 = 기준 얼굴 살색(구멍 채움) ∩ 그 장 살색(구멍 채움, +1px) — 앞머리·옆머리는 그 장 그대로
#  밝기 = 그 장 원래 살색 평균에 맞춤
import json, sys, numpy as np
from PIL import Image
from scipy import ndimage
from common import load, skinmask
D, OUT = sys.argv[1], sys.argv[2]
meta = json.load(open(D + '/meta.json'))['anims']
def area(a): return ndimage.binary_fill_holes(ndimage.binary_closing(skinmask(a), iterations=1))
REF = {'down': 'walk_down_00.png', 'right': 'walk_right_00.png'}
refs = {}
for dn, fn in REF.items():
    a = load(f'{D}/{fn}'); m = area(a); ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    refs[dn] = (a[y0:y1, x0:x1].copy(), m[y0:y1, x0:x1], (y0, x0))
res = {}
for n, frs in meta.items():
    dn = 'down' if n.endswith('_down') else ('right' if n.endswith('_right') else None)
    if dn is None or n.startswith('death') or n.startswith('cast'): continue
    P, M, (ry, rx) = refs[dn]; h, w = M.shape
    for fn, ax, ay, t in frs:
        a = load(f'{D}/{fn}'); tm = area(a); out = a.copy(); info = {'ok': False}
        if tm.sum() >= 12:
            ty, tx = [int(v) for v in np.argwhere(tm).mean(0)]
            cy, cx = [int(v) for v in np.argwhere(M).mean(0)]
            best = (-1, 0, 0)
            for dy in range(-8, 9):
                for dx in range(-8, 9):
                    y0, x0 = ty - cy + dy, tx - cx + dx
                    if y0 < 0 or x0 < 0 or y0 + h > a.shape[0] or x0 + w > a.shape[1]: continue
                    t2 = tm[y0:y0 + h, x0:x0 + w]; inter = (t2 & M).sum(); uni = (t2 | M).sum() + (tm.sum() - t2.sum())
                    iou = inter / max(uni, 1)
                    if iou > best[0]: best = (iou, y0, x0)
            iou, y0, x0 = best
            info = {'iou': round(float(iou), 2), 'ok': bool(iou >= 0.5)}
            if iou >= 0.5:
                grow = ndimage.binary_dilation(tm, iterations=1)
                put = M & grow[y0:y0 + h, x0:x0 + w] & (a[y0:y0 + h, x0:x0 + w, 3] > 0)
                Q = P.copy(); sk = skinmask(a)
                if sk.any():
                    tgt = a[sk][:, :3].astype(float).mean(0); ps = put & (Q[..., :3].astype(float).mean(2) > 90)
                    if ps.any():
                        src = Q[ps][:, :3].astype(float).mean(0); Q[ps, :3] = np.clip(Q[ps, :3] * (tgt / np.maximum(src, 1)), 0, 255).astype(np.uint8)
                out[y0:y0 + h, x0:x0 + w][put] = Q[put]
        Image.fromarray(out).save(f'{OUT}/{fn}'); res[fn] = info
json.dump(res, open(OUT + '/stamp.json', 'w'), indent=0)
ok = sum(v['ok'] for v in res.values()); print('찍음', ok, '/', len(res))
for k, v in res.items():
    if not v['ok']: print('  안 찍음', k, v.get('iou'))
