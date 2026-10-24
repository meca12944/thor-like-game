# 아라크네 그록판 띠 그림 만들기: 떨어진 작은 조각(그림 도구가 넣은 글자 등) 지우기 → 256칸 띠. usage: build.py walk
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage
C = os.path.dirname(os.path.abspath(__file__)); OUT = C + '/strips'; os.makedirs(OUT, exist_ok=True)
def islands(im):  # 가장 큰 덩어리와 그 근처(8칸 안)만 남김
    a = np.array(im); m = a[..., 3] > 0; lab, k = ndimage.label(m, np.ones((3, 3)))
    if k <= 1: return im
    sz = ndimage.sum(m, lab, range(1, k + 1)); big = lab == (np.argmax(sz) + 1); near = ndimage.binary_dilation(big, iterations=8)
    keep = np.isin(lab, [i for i in range(1, k + 1) if (near & (lab == i)).any() and sz[i - 1] > 3]) | big
    a[~keep] = 0; return Image.fromarray(a)
def strip(name, frames):
    s = Image.new('RGBA', (256 * len(frames), 256), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.alpha_composite(islands(Image.open(f).convert('RGBA')), (256 * i, 0))
    s.save(f'{OUT}/c1_boss_arachne_g_{name}.png'); print(name, len(frames))
if 'walk' in sys.argv: strip('walk', [f'{C}/tw/walk/{i:03d}.png' for i in range(8)])
if 'idle' in sys.argv:
    for n in ('side_r_cov', 'front_cov', 'back_256'): strip('idle_' + n.split('_')[0], [f'{C}/clean/{n}.png'])
