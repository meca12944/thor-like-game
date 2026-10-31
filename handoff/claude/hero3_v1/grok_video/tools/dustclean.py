# 그록이 그린 흙먼지 지우기 (회피대시 정면·뒷면 영상, 「no dust」라고 해도 발 옆에 먼지를 그림): 효과는 그림에 굽지 않고 코드로(CLAUDE.md)
# 발 근처(아래 35줄)에서 밝은 황토색(밝기 70↑, 빨강 > 파랑+30) 칸이 있는 중간 밝기(45↑) 덩어리 = 먼지 → 지움. 그다음 몸과 떨어진 작은 덩어리도 지움. 장화는 아주 어두워(밝기 50↓) 안 지워짐.
# 쓰는 법: python3 dustclean.py <장 폴더> <출력 폴더>
import sys, os, glob, numpy as np
from PIL import Image
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob(src + '/0*.png')):
    a = np.asarray(Image.open(f).convert('RGBA')).copy(); op = a[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]; bot = ys.max(); reg = np.zeros_like(op); reg[max(0, bot - 35):] = True
    r, g, b = [a[..., i].astype(int) for i in range(3)]; L = r * .299 + g * .587 + b * .114
    light = op & reg & (L > 70) & (r > b + 30); mid = op & reg & (L > 45)
    lab, n = ndimage.label(mid); hit = np.unique(lab[light]); dust = np.isin(lab, hit[hit > 0])
    a[dust, 3] = 0; op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lab, range(1, n + 1)); keep = np.argmax(sz) + 1
        a[(lab != keep) & op, 3] = 0
    Image.fromarray(a).save(f'{out}/{os.path.basename(f)}')
    print(os.path.basename(f), '먼지', int(dust.sum()), '떨어진 덩어리', int(n - 1))
