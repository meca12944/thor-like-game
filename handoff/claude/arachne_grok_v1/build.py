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
# ---- 게임 띠 전부 (그록 그림 + 핵심 자세 4장, 사이 장은 게임 코드의 웅크림·늘임·흔들림이 맡음; 장 순서는 world_mobs.js anim.map)
def cell(path, flip=False, bottom=249, up=0):
    im = islands(Image.open(path).convert('RGBA')); bb = im.getbbox(); im = im.crop(bb)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    c = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    x = 128 - im.width // 2 if flip or path.endswith(('_0.png', '_1.png', '_2.png', '_3.png')) else bb[0]   # 시트 그림은 가운데, PixelLab 장은 제자리
    c.alpha_composite(im, (x, bottom - up - im.height)); return c
def save(name, cells):
    s = Image.new('RGBA', (256 * len(cells), 256), (0, 0, 0, 0))
    for i, c in enumerate(cells): s.alpha_composite(c, (256 * i, 0))
    s.save(f'{OUT}/c1_boss_arachne_{name}.png'); print(name, len(cells))
if 'all' in sys.argv:
    K = C + '/key/'; I = C + '/clean/side_r_cov.png'
    idle, stab, cast, crouch, pull = cell(I), cell(K + 'stab_key.png'), cell(K + 'cast_key.png'), cell(K + 'crouch_key.png'), cell(K + 'pull_key.png')
    c0, c1, c2 = [cell(f'{C}/clean/m2_{i}.png', flip=True) for i in range(3)]   # 2페이즈 엎드린 거미형 (그록 2줄, 왼쪽 보기 → 뒤집음)
    save('walk', [Image.open(f'{C}/tw/walk/{i:03d}.png').convert('RGBA') for i in range(8)]); save('walk', [islands(Image.open(f'{C}/tw/walk/{i:03d}.png').convert('RGBA')) for i in range(8)])
    save('attack', [idle, stab]); save('pounce', [crouch, cell(I, up=12), cell(I, up=24), stab]); save('hurt', [idle, pull]); save('death', [idle, pull, c1])
    save('roar', [idle, cast]); save('rage', [c0, c2]); save('ragewalk', [c0, c1, c2]); save('prison', [idle, cast]); save('rain', [idle, cast]); save('shoot', [idle, cast])
