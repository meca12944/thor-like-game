import numpy as np, colorsys
from PIL import Image
from scipy import ndimage
def load(f): return np.array(Image.open(f).convert('RGBA'))
def skinmask(a, rows=34):
    """new grok hero: darker skin (~160,125,105), leather is more saturated -> HSV gate"""
    f = a.astype(float) / 255; r, g, b, al = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b); s = (mx - mn) / np.maximum(mx, 1e-6)
    m = (al > .78) & (r > g) & (g >= b - .02) & (mx > .5) & (s > .12) & (s < .48) & (r - g > .06)
    ys = np.nonzero((al > .16).any(1))[0]; top = ys.min(); m[:top] = False; m[top + rows:] = False
    lab, n = ndimage.label(m)
    if not n: return m
    k = np.argmax(ndimage.sum(m, lab, range(1, n + 1))) + 1; return lab == k
def face(a):
    m = skinmask(a); ys, xs = np.nonzero(m)
    return (int(ys.mean()), int(xs.mean()), len(ys)) if len(ys) > 15 else None
def crop(a, f, S=26): cy, cx = f[0], f[1]; return Image.fromarray(a).crop((cx - S // 2, cy - S // 2 - 2, cx + S // 2, cy + S // 2 - 2))
