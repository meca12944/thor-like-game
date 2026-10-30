# 그록 영상이 슬쩍 확대·축소됐는지: 한 바퀴 장의 윗몸(머리~가슴, 서기 키의 30%)을 첫 장(서기)과 겹쳐 가장 잘 맞는 배율
import sys, numpy as np
from PIL import Image
def mask(f):
    a = np.asarray(Image.open(f).convert('RGB')).astype(int); return (a[..., 1] - np.maximum(a[..., 0], a[..., 2])) < 70
def top(k, Hs):
    ys, xs = np.nonzero(k); t = ys.min(); band = k[t:t + int(Hs * .30)]
    yy, xx = np.nonzero(band); cx = xx.mean()
    return band, cx
d, st, P = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
K0 = mask(f'{d}/frames/0001.png'); ys = np.nonzero(K0.any(1))[0]; Hs = ys.max() - ys.min()
B0, c0 = top(K0, Hs)
def iou_at(k, z):
    im = Image.fromarray((k * 255).astype(np.uint8)); w, h = im.size
    kk = np.asarray(im.resize((round(w * z), round(h * z)), Image.BILINEAR)) > 127
    B, c = top(kk, Hs); W = max(B.shape[1], B0.shape[1]) + 200
    a = np.zeros((B0.shape[0], W), bool); b = np.zeros_like(a)
    a[:, 100 + 0:100 + B0.shape[1]] = B0
    off = int(round(c0 - c)); bb = B[:B0.shape[0]]
    x0 = 100 + off
    b[:bb.shape[0], max(0, x0):x0 + bb.shape[1]] = bb[:, max(0, -x0):]
    return (a & b).sum() / max((a | b).sum(), 1)
fr = [mask(f'{d}/frames/{i + 1:04d}.png') for i in range(st, st + P, max(1, P // 8))]
res = [(round(z, 2), float(np.mean([iou_at(k, z) for k in fr]))) for z in np.arange(.86, 1.05, .01)]
best = max(res, key=lambda r: r[1])
print(d, '가장 잘 맞는 배율', best[0], '겹침', round(best[1], 3), '(1.00일 때', round(dict(res)[1.0], 3), ')')
