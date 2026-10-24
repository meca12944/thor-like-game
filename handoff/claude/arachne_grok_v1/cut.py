# 그록 아라크네 그림 → 배경·그림자 지우기 + 원래 도트 크기(약 2.5px)로 줄이기. usage: cut.py
# 회색 배경/바닥 그림자 = 무채색(채널 차 < 12) + 밝기 38 이상, 테두리에서 이어진 것만 지움 (검은 머리카락은 밝기 < 35라 남음)
import numpy as np, os
from PIL import Image
from scipy import ndimage
C = os.path.dirname(os.path.abspath(__file__))
PX = 2.5   # 그록 그림 한 도트 ≈ 2.5px
def clean(rgb):
    a = rgb.astype(int); mx, mn = a.max(2), a.min(2)
    bgish = (mx - mn < 12) & (mx > 38)
    lab, _ = ndimage.label(bgish); edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bg = np.isin(lab, list(edge))
    bg = ndimage.binary_opening(~bg, iterations=1); bg = ~bg          # 1px 가시 지우기
    return bg
def cut(src, boxes, names, out):
    im = Image.open(src).convert('RGB'); a = np.asarray(im)
    bg = clean(a)
    for (x0, y0, x1, y1), n in zip(boxes, names):
        sub = a[y0:y1, x0:x1]; m = ~bg[y0:y1, x0:x1]
        lab, k = ndimage.label(m); 
        if k: sizes = ndimage.sum(m, lab, range(1, k + 1)); keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 400]); m = keep
        ys, xs = np.where(m); sub = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        rgba = np.dstack([sub, (m * 255).astype(np.uint8)])
        big = Image.fromarray(rgba, 'RGBA'); big.save(f'{C}/clean/{n}_full.png')
        w, h = round(big.width / PX), round(big.height / PX)
        rgb = big.convert('RGB').resize((w, h), Image.BOX); al = Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.BOX)
        al = al.point(lambda v: 255 if v >= 128 else 0)
        sm = rgb.quantize(48, method=Image.MEDIANCUT).convert('RGB'); sm.putalpha(al); sm.save(f'{out}/{n}.png'); print(n, big.size, '->', sm.size)
cut(f'{C}/raw/arachne_4view.jpg', [(10, 130, 315, 560), (320, 130, 632, 560), (655, 130, 952, 560), (966, 130, 1275, 560)], ['front', 'side_r', 'back', 'side_l'], f'{C}/clean')
