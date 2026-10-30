# 정답 게임 얼굴을 판으로 장마다 찍기 (판 크기 그대로, 살색 겹침이 가장 큰 자리, 그 장 살색 안쪽+1칸만 → 앞머리는 그 장 그대로)
import sys, glob, os, json, numpy as np
from PIL import Image
from scipy import ndimage
ref, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
def skin(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (a[..., 3] > 0) & (r > g) & (g > b) & (r - b > 45) & (r > 120)
R = np.asarray(Image.open(ref).convert('RGBA')).astype(int)
X0, Y0, X1, Y1 = 80, 34, 122, 84                       # 정면 머리 둘레
plate = R[Y0:Y1, X0:X1]
pm = ndimage.binary_fill_holes(ndimage.binary_closing(skin(plate), iterations=2))   # 눈·입 구멍까지 = 얼굴 판
pal = np.unique(plate[skin(plate)][:, :3], axis=0); PL = pal @ [.299, .587, .114]
h, w = pm.shape; os.makedirs(out, exist_ok=True); table = {}
for f in sorted(glob.glob(src + '/*.png')):
    A = np.asarray(Image.open(f).convert('RGBA')).astype(int); O = A.copy()
    tm = skin(A); tm[90:] = False
    best = (-1, 0, 0)
    for dy in range(-10, 11):
        for dx in range(-10, 11):
            y0, x0 = Y0 + dy, X0 + dx
            t2 = tm[y0:y0 + h, x0:x0 + w]
            iou = (t2 & pm).sum() / max((t2 | pm).sum(), 1)
            if iou > best[0]: best = (iou, dx, dy)
    iou, dx, dy = best; y0, x0 = Y0 + dy, X0 + dx
    tz = ndimage.binary_fill_holes(ndimage.binary_closing(tm, iterations=2))
    put = pm & ndimage.binary_dilation(tz, iterations=1)[y0:y0 + h, x0:x0 + w]
    if iou >= .45: O[y0:y0 + h, x0:x0 + w][put] = plate[put]
    rest = skin(O) & ~np.pad(put, ((y0, 256 - y0 - h), (x0, 256 - x0 - w))); rest[90:] = False    # 목·귀 살색 → 판 살색
    if rest.any():
        l = O[rest][:, :3] @ [.299, .587, .114]; O[rest, :3] = pal[np.abs(l[:, None] - PL[None]).argmin(1)]
    Image.fromarray(O.astype(np.uint8)).save(f'{out}/{os.path.basename(f)}')
    table[os.path.basename(f)] = {'iou': round(float(iou), 2), 'dx': dx, 'dy': dy, 'ok': bool(iou >= .45)}
    print(os.path.basename(f), table[os.path.basename(f)])
json.dump(table, open(out + '/face_table.json', 'w'), indent=1)
