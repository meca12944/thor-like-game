# 얼굴 이식 v4 (사장님 10-27 「해결 방법대로 다 하고 주인공 몸에 이식까지」)
# 해결 1) 얼굴판은 게임 크기 그대로 한 장씩 (정면 = 정6 손 보정, 옆 = 옆7 원래 + 정면 살색), 장마다 자리(dx, dy)만 표로 → 배율·돌리기 없음
# 해결 2) 크기 그대로 찍고, 판은 그 장 살색(+1칸) 안에만 → 앞머리·옆머리는 그 장 그대로(머리카락 움직임 유지)
# 해결 4) 살색 6색 고정: 그 장 얼굴 둘레 살색을 정면 판의 살색 6가지 중 가장 가까운 색으로
# 고개가 크게 돈 장(겹침 0.5 미만)은 찍지 않고 목록에 남김 → 「숙인 머리판」이 필요한 장
import json, sys, numpy as np
from PIL import Image
from scipy import ndimage
from common import load, skinmask
D, FIX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
meta = json.load(open(D + '/meta.json'))['anims']
def area(a): return ndimage.binary_fill_holes(ndimage.binary_closing(skinmask(a), iterations=1))
plates = {}
for dn, fn in [('down', 'front_fixed_full.png'), ('right', 'side_fixed_full.png')]:
    a = load(f'{FIX}/{fn}'); m = area(a); ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    plates[dn] = (a[y0:y1, x0:x1].copy(), m[y0:y1, x0:x1])
# 살색 6색 = 정면 판 살색을 6가지로 묶음
P, M = plates['down']; sk = skinmask(P) & M
pal = np.array(Image.fromarray(P[sk][None, :, :3].astype(np.uint8)).quantize(6, method=Image.Quantize.MEDIANCUT).convert('RGB')).reshape(-1, 3)
PAL = np.unique(pal, axis=0).astype(int)
def lock(rgb):
    d = ((rgb[:, None, :] - PAL[None]) ** 2).sum(2); return PAL[d.argmin(1)]
for dn in plates:  # 판도 6색으로
    Q, Mq = plates[dn]; s = skinmask(Q) & Mq; Q[s, :3] = lock(Q[s, :3].astype(int))
table, skipped = {}, []
for n, frs in meta.items():
    dn = 'down' if n.endswith('_down') else ('right' if n.endswith('_right') else None)
    if dn is None or n.startswith(('death', 'cast')): continue
    Q, Mq = plates[dn]; h, w = Mq.shape
    for fn, ax, ay, t in frs:
        a = load(f'{D}/{fn}'); out = a.copy(); tm = area(a); rec = {'ok': False}
        if tm.sum() >= 12:
            ty, tx = [int(v) for v in np.argwhere(tm).mean(0)]; cy, cx = [int(v) for v in np.argwhere(Mq).mean(0)]
            best = (-1, 0, 0)
            for dy in range(-8, 9):
                for dx in range(-8, 9):
                    y0, x0 = ty - cy + dy, tx - cx + dx
                    if y0 < 0 or x0 < 0 or y0 + h > a.shape[0] or x0 + w > a.shape[1]: continue
                    t2 = tm[y0:y0 + h, x0:x0 + w]; iou = (t2 & Mq).sum() / max((t2 | Mq).sum() + tm.sum() - t2.sum(), 1)
                    if iou > best[0]: best = (iou, y0, x0)
            iou, y0, x0 = best; rec = {'iou': round(float(iou), 2), 'dx': int(x0), 'dy': int(y0), 'ok': bool(iou >= .5)}
            if iou >= .5:
                put = Mq & ndimage.binary_dilation(tm, iterations=1)[y0:y0 + h, x0:x0 + w] & (a[y0:y0 + h, x0:x0 + w, 3] > 0)
                out[y0:y0 + h, x0:x0 + w][put] = Q[put]
                # 판 밖 얼굴 둘레 살색도 6색으로 (장마다 살색 같게)
                band = np.zeros(tm.shape, bool); band[max(0, y0 - 4):y0 + h + 4, max(0, x0 - 4):x0 + w + 4] = True
                s2 = skinmask(out) & band; out[s2, :3] = lock(out[s2, :3].astype(int)).astype(np.uint8)
        if not rec['ok']: skipped.append(fn)
        Image.fromarray(out).save(f'{OUT}/{fn}'); table[fn] = rec
json.dump({'palette6': PAL.tolist(), 'frames': table}, open(OUT + '/face_table.json', 'w'), indent=0)
print('살색 6색', PAL.tolist()); print('이식', sum(v['ok'] for v in table.values()), '/', len(table)); print('숙인 머리판 필요(안 찍음):', skipped)
