# 얼굴 "한 장"을 모든 장에 통째로 찍기(정면·옆, 옆은 상자 인자): 얼굴 살색(구멍 채움) + 둘레 2칸(눈썹·턱선·볼 옆 머리) + 이마 위 앞머리 8줄 = 판 하나.
# 판 안의 칸은 장과 상관없이 모두 판 그대로 → 8장 얼굴이 칸까지 똑같음. 자리만 장마다 (dx, dy).
import sys, glob, os, json, numpy as np
from PIL import Image
from scipy import ndimage
ref, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
HT = int(sys.argv[4]) if len(sys.argv) > 4 else 144     # 게임 그림 키 (판 자리·줄 수는 키 218 기준 숫자를 발 기준 (128, 246)에서 같은 비율로)
SC = HT / 218
X = lambda x: round(128 + (x - 128) * SC); Y = lambda y: round(246 - (246 - y) * SC); N = lambda n: max(1, round(n * SC))
def skin(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (a[..., 3] > 0) & (r > g) & (g > b) & (r - b > 45) & (r > 120)
R = np.asarray(Image.open(ref).convert('RGBA')).astype(int)
BX = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else [76, 26, 126, 88]   # 얼굴 판 상자(키 218 기준). 정면 76,26,126,88 · 옆 118,26,152,88
X0, Y0, X1, Y1 = X(BX[0]), Y(BX[1]), X(BX[2]), Y(BX[3])
plate = R[Y0:Y1, X0:X1]
sk = skin(plate); sk[N(56):] = False
face = ndimage.binary_fill_holes(ndimage.binary_closing(sk, iterations=2))
pm = ndimage.binary_dilation(face, iterations=N(2))
ys, xs = np.nonzero(face); top = ys.min()
for y in range(max(0, top - N(8)), top):                  # 앞머리: 얼굴 너비만큼 이마 위 8줄(키 218 기준)
    pm[y, xs.min() - 1:xs.max() + 2] = True
pm &= plate[..., 3] > 0
h, w = pm.shape; os.makedirs(out, exist_ok=True); table = {}
pal = np.unique(plate[sk][:, :3], axis=0); PL = pal @ [.299, .587, .114]
ANG = [int(v) for v in sys.argv[6].split(',')] if len(sys.argv) > 6 else [0]   # 판 기울기 찾기(도, 옆 달리기처럼 몸을 숙일 때 예: -14,-12,…,4). 기본 0 = 똑바로
def turn(m, a):   # 판(색·얼굴·찍을 칸)을 a도 기울임 (칸 그대로 NEAREST)
    if a == 0: return m
    return np.asarray(Image.fromarray(m.astype(np.uint8)).rotate(a, Image.NEAREST, expand=True))
plates = []
for a in ANG:
    P = turn(plate, a) if a else plate
    F = turn(face * 255, a) > 127 if a else face; M = turn(pm * 255, a) > 127 if a else pm
    plates.append((a, P, F, M))
for f in sorted(glob.glob(src + '/*.png')):
    A = np.asarray(Image.open(f).convert('RGBA')).astype(int); O = A.copy()
    tm = skin(A); tm[Y(100):] = False; tz = ndimage.binary_fill_holes(ndimage.binary_closing(tm, iterations=2))
    # 얼굴 = 가장 위에 있는 살색 덩어리(앞에 든 주먹 살색은 뺌)
    lab, nl = ndimage.label(tz)
    if nl:
        ys_, xs_ = np.nonzero(lab); k = lab[ys_.min(), xs_[ys_ == ys_.min()][0]]; tz = lab == k
    ty_, tx_ = np.nonzero(tz)
    best = (-1, 0, 0, 0)
    for a, P, F, M in plates:
        h2, w2 = F.shape; fy, fx = np.nonzero(F)
        # 얼굴 살색 가운데를 먼저 맞추고(영상은 머리 자리가 장마다 다름), 그 둘레 ±4칸(키 218 기준)에서 겹침이 가장 큰 자리
        cy = int(round(ty_.mean() - fy.mean())) if len(ty_) else Y0; cx = int(round(tx_.mean() - fx.mean())) if len(ty_) else X0
        R4 = N(4)
        for y0 in range(cy - R4, cy + R4 + 1):
            for x0 in range(cx - R4, cx + R4 + 1):
                if y0 < 0 or x0 < 0 or y0 + h2 > 256 or x0 + w2 > 256: continue
                t2 = tz[y0:y0 + h2, x0:x0 + w2]
                iou = (t2 & F).sum() / max((t2 | F).sum(), 1)
                if iou > best[0]: best = (iou, x0, y0, a)
    iou, x0, y0, a = best; P, F, M = [q for q in plates if q[0] == a][0][1:]
    h2, w2 = M.shape
    O[y0:y0 + h2, x0:x0 + w2][M] = P[M]
    full = np.zeros(A.shape[:2], bool); full[y0:y0 + h2, x0:x0 + w2] = M
    rest = skin(O) & ~full; rest[:y0 + top] = False; rest[Y(100):] = False            # 판 밖 목 살색 → 판 살색
    if rest.any():
        l = O[rest][:, :3] @ [.299, .587, .114]; O[rest, :3] = pal[np.abs(l[:, None] - PL[None]).argmin(1)]
    Image.fromarray(O.astype(np.uint8)).save(f'{out}/{os.path.basename(f)}')
    table[os.path.basename(f)] = {'iou': round(float(iou), 2), 'x': x0, 'y': y0, 'deg': a}
    print(os.path.basename(f), table[os.path.basename(f)])
json.dump({'plate_box': [X0, Y0, X1, Y1], 'frames': table}, open(out + '/face_table.json', 'w'), indent=1)
Image.fromarray(np.where(pm[..., None], plate, 0).astype(np.uint8)).save(out + '/_plate.png')
