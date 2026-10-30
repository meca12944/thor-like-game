# 정면 얼굴 "한 장"을 모든 장에 통째로 찍기: 얼굴 살색(구멍 채움) + 둘레 2칸(눈썹·턱선·볼 옆 머리) + 이마 위 앞머리 8줄 = 판 하나.
# 판 안의 칸은 장과 상관없이 모두 판 그대로 → 8장 얼굴이 칸까지 똑같음. 자리만 장마다 (dx, dy).
import sys, glob, os, json, numpy as np
from PIL import Image
from scipy import ndimage
ref, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
def skin(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (a[..., 3] > 0) & (r > g) & (g > b) & (r - b > 45) & (r > 120)
R = np.asarray(Image.open(ref).convert('RGBA')).astype(int)
X0, Y0, X1, Y1 = 76, 26, 126, 88
plate = R[Y0:Y1, X0:X1]
sk = skin(plate); sk[56:] = False
face = ndimage.binary_fill_holes(ndimage.binary_closing(sk, iterations=2))
pm = ndimage.binary_dilation(face, iterations=2)
ys, xs = np.nonzero(face); top = ys.min()
for y in range(max(0, top - 8), top):                     # 앞머리: 얼굴 너비만큼 이마 위 8줄
    pm[y, xs.min() - 1:xs.max() + 2] = True
pm &= plate[..., 3] > 0
h, w = pm.shape; os.makedirs(out, exist_ok=True); table = {}
pal = np.unique(plate[sk][:, :3], axis=0); PL = pal @ [.299, .587, .114]
for f in sorted(glob.glob(src + '/*.png')):
    A = np.asarray(Image.open(f).convert('RGBA')).astype(int); O = A.copy()
    tm = skin(A); tm[90:] = False; tz = ndimage.binary_fill_holes(ndimage.binary_closing(tm, iterations=2))
    best = (-1, 0, 0)
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            t2 = tz[Y0 + dy:Y0 + dy + h, X0 + dx:X0 + dx + w]
            iou = (t2 & face).sum() / max((t2 | face).sum(), 1)
            if iou > best[0]: best = (iou, dx, dy)
    iou, dx, dy = best; y0, x0 = Y0 + dy, X0 + dx
    O[y0:y0 + h, x0:x0 + w][pm] = plate[pm]
    full = np.zeros(A.shape[:2], bool); full[y0:y0 + h, x0:x0 + w] = pm
    rest = skin(O) & ~full; rest[:y0 + top] = False; rest[100:] = False            # 판 밖 목 살색 → 판 살색
    if rest.any():
        l = O[rest][:, :3] @ [.299, .587, .114]; O[rest, :3] = pal[np.abs(l[:, None] - PL[None]).argmin(1)]
    Image.fromarray(O.astype(np.uint8)).save(f'{out}/{os.path.basename(f)}')
    table[os.path.basename(f)] = {'iou': round(float(iou), 2), 'dx': dx, 'dy': dy}
    print(os.path.basename(f), table[os.path.basename(f)])
json.dump({'plate_box': [X0, Y0, X1, Y1], 'frames': table}, open(out + '/face_table.json', 'w'), indent=1)
Image.fromarray(np.where(pm[..., None], plate, 0).astype(np.uint8)).save(out + '/_plate.png')
