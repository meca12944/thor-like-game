# 옆모습 발 재기: 장마다 앞발·뒷발 바닥 줄, 땅(244~246)에 닿은 x → 처음 닿는 장 = 발 닿는 장, 닿은 x가 장마다 뒤로 가는 칸 = 러닝머신 빠르기
# 쓰는 법: python3 feet.py <장 폴더>
# 옆모습: 장마다 앞쪽(오른쪽) 발과 뒤쪽 발의 가장 낮은 줄 → 땅(246)에 처음 닿는 장 = 발 닿는 장
import sys, glob, numpy as np
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + '/0*.png'))
for i, f in enumerate(fs):
    a = np.asarray(Image.open(f))[..., 3] > 0; ys, xs = np.nonzero(a)
    low = a[200:]; yy, xx = np.nonzero(low); cx = np.median(xx)
    r = low[:, int(cx):]; l = low[:, :int(cx)]
    br = 200 + np.nonzero(r.any(1))[0].max() if r.any() else -1; bl = 200 + np.nonzero(l.any(1))[0].max() if l.any() else -1
    # 땅에 닿은 칸들의 x (가장 낮은 2줄)
    g = np.nonzero(a[244:247].any(0))[0]
    print(i, '앞발 바닥', br, '뒷발 바닥', bl, '땅 닿은 x', (g.min(), g.max()) if len(g) else None)
