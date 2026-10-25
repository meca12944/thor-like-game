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
    global PX
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
if 'motion' not in __import__('sys').argv: cut(f'{C}/raw/arachne_4view.jpg', [(10, 130, 315, 560), (320, 130, 632, 560), (655, 130, 952, 560), (966, 130, 1275, 560)], ['front', 'side_r', 'back', 'side_l'], f'{C}/clean')
# 동작 시트 3줄 x 4칸 (1줄 위에서 본 기어오기, 2줄 엎드려 기기→피 토하기, 3줄 젖히기→일어서 웃기; 3줄엔 주인공 크기 비교 인물이 있어 가장 큰 덩어리만 남김)
if __name__ == '__main__' and 'motion' in __import__('sys').argv:
    rows = [(0, 255), (255, 425), (420, 705)]
    boxes, names = [], []
    for r, (y0, y1) in enumerate(rows):
        for c in range(4): boxes.append((c * 320, y0, c * 320 + 320, y1)); names.append(f'm{r + 1}_{c}')
    import numpy as np
    from scipy import ndimage
    def biggest(path):
        im = Image.open(path); a = np.array(im); m = a[..., 3] > 0; lab, k = ndimage.label(m, np.ones((3, 3)))
        if k > 1:
            sz = ndimage.sum(m, lab, range(1, k + 1)); big = lab == np.argmax(sz) + 1; near = ndimage.binary_dilation(big, iterations=4)
            keep = np.isin(lab, [i for i in range(1, k + 1) if (near & (lab == i)).any()]); a[~keep] = 0; Image.fromarray(a).crop(Image.fromarray(a).getbbox()).save(path)
    PX = 2.5 * 266 / 382   # 동작 시트는 4면보다 작게 그려짐 (3줄 서 있는 키 266px vs 4면 382px) → 같은 크기로
    cut(f'{C}/raw/arachne_motion.jpg', boxes, names, f'{C}/clean')
    for n in names: biggest(f'{C}/clean/{n}.png')
