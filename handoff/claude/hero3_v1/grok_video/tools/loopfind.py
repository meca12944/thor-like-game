# 한 바퀴 찾기: 실루엣(초록 아닌 칸) 차이로 주기 → 장 i와 i+주기 차이가 가장 작은 시작 장 (교본 0부 5-5)
import sys, glob, numpy as np
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + '/*.png')); skip = int(sys.argv[2]) if len(sys.argv) > 2 else 18
M = []
for f in fs:
    a = np.asarray(Image.open(f).convert('RGB').resize((240, 240), Image.BILINEAR)).astype(int)
    M.append((a[..., 1] - np.maximum(a[..., 0], a[..., 2])) < 70)
M = np.array(M); n = len(M)
def d(i, j): return (M[i] ^ M[j]).sum() / max((M[i] | M[j]).sum(), 1)
res = []
for P in range(8, 50):
    v = [d(i, i + P) for i in range(skip, n - P)]
    res.append((P, float(np.mean(v))))
mins = [r for k, r in enumerate(res) if 0 < k < len(res) - 1 and r[1] < res[k - 1][1] and r[1] < res[k + 1][1]]
print('주기 후보(평균 차이):', [(P, round(v, 3)) for P, v in sorted(mins, key=lambda r: r[1])[:5]])
P = int(sys.argv[3]) if len(sys.argv) > 3 else sorted(mins, key=lambda r: r[1])[0][0]
st = sorted(range(skip, n - P), key=lambda i: d(i, i + P))[:5]
print('주기', P, '좋은 시작 장(이음매 차이):', [(i, round(d(i, i + P), 3)) for i in st])
