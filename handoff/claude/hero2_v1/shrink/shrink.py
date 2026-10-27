# 머리·얼굴 비율 줄이기 (도트 유지: 새 색 없이 줄·칸을 빼서 줄임, 눈·눈썹·코·입 줄은 안 뺌)
# 쓰는 법: shrink.py 원본 결과 비율 턱줄 [얼굴위 얼굴왼 얼굴오른]
import sys, numpy as np
from PIL import Image
src, dst, k, chin = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
A = np.asarray(Image.open(src).convert('RGBA')).astype(int)
r, g, b, al = A[..., 0], A[..., 1], A[..., 2], A[..., 3] > 0
skin = al & (r > g) & (g > b) & (r - b > 40) & (r > 110)
top = np.nonzero(al.any(1))[0].min()
ft, fl, fr = [int(v) for v in sys.argv[5:8]]
lum = A[..., :3].sum(-1)
med = np.median(lum[ft:chin + 1, fl:fr + 1][skin[ft:chin + 1, fl:fr + 1]])
feat = np.zeros_like(al); feat[ft:chin + 1, fl:fr + 1] = (lum[ft:chin + 1, fl:fr + 1] < med * .72) | ((b > r + 8) & (b > 45))[ft:chin + 1, fl:fr + 1]
feat &= al
from scipy import ndimage
sl = np.zeros_like(skin); sr = np.zeros_like(skin)
for d in (1, 2, 3):
    sl[:, d:] |= skin[:, :-d]; sr[:, :-d] |= skin[:, d:]
feat &= sl & sr          # 살색 사이에 있는 진한 칸만 = 눈·눈썹·코·입
prot_r = set(np.nonzero(feat.any(1))[0].tolist()); prot_c = set(np.nonzero(feat.any(0))[0].tolist())
def pick(lo, hi, n, prot, taken):
    out = []
    for i in range(n):
        t = int(round(lo + (i + .5) * (hi - lo) / max(n, 1)))
        for d in range(0, hi - lo + 1):
            ok = False
            for c in (t + d, t - d):
                if lo <= c <= hi and c not in prot and all(abs(c - o) > 1 for o in out + taken):
                    out.append(c); ok = True; break
            if ok: break
    return out
H = chin - top + 1; nR = round(H * (1 - k)); nRf = round((chin - ft + 1) * (1 - k))
drop_r = pick(ft + 1, chin - 2, nRf, prot_r, [])
drop_r += pick(top + 1, ft - 1, nR - len(drop_r), set(), drop_r)
hx = np.nonzero(al[top:chin + 1].any(0))[0]; x0, x1 = hx.min(), hx.max(); Wd = x1 - x0 + 1
nC = round(Wd * (1 - k)); nCf = round((fr - fl + 1) * (1 - k))
drop_c = pick(fl + 1, fr - 1, nCf, prot_c, [])
rest = nC - len(drop_c); drop_c += pick(x0 + 1, fl - 1, (rest + 1) // 2, set(), drop_c) + pick(fr + 1, x1 - 1, rest // 2, set(), drop_c)
cx = (fl + fr) // 2
B = A.copy(); B[top:chin + 1] = 0
keep_r = [y for y in range(top, chin + 1) if y not in drop_r]
keep_c = [x for x in range(x0, x1 + 1) if x not in drop_c]
newx = {}
for i, x in enumerate([x for x in keep_c if x >= cx]): newx[x] = cx + i
for i, x in enumerate([x for x in keep_c if x < cx][::-1]): newx[x] = cx - 1 - i
for j, y in enumerate(keep_r[::-1]):
    for x, nx in newx.items(): B[chin - j, nx] = A[y, x]
for i in range(1, 9):   # 턱 아래 8줄: 옆 머리카락 이음새를 가로로만 서서히 원래 크기로
    y = chin + i; kk = (1 - k) * (1 - i / 9); row = A[y]; nr = np.zeros_like(row)
    for x in range(A.shape[1]):
        sx = int(round(cx + (x - cx) / (1 - kk)))
        if 0 <= sx < A.shape[1]: nr[x] = row[sx]
    keepface = (x := None)
    nr[fl:fr + 1] = row[fl:fr + 1]  # 목은 그대로
    B[y] = nr
Image.fromarray(B.astype(np.uint8)).save(dst)
print(src.split('/')[-1], 'H', H, '->', len(keep_r), 'W', Wd, '->', len(keep_c), 'face', chin - ft + 1, '->', chin - ft + 1 - sum(1 for y in drop_r if y >= ft), 'x', fr - fl + 1, '->', fr - fl + 1 - sum(1 for x in drop_c if fl <= x <= fr), 'rows', sorted(drop_r), 'cols', sorted(drop_c))
