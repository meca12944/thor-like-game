# 누빔 멧돼지 게임 띠 (256칸, 발 y249, 오른쪽 보기). 걷기 = PixelLab 8장을 배율 1개·이동 1번으로 기준(옆 서기 키 120)에 맞춤 (모션 교과서 9). 공격 = 그록 자세 + anim.map.
import os, numpy as np
from PIL import Image
from scipy import ndimage
C = os.path.dirname(os.path.abspath(__file__)); OUT = C + '/strips'; os.makedirs(OUT, exist_ok=True)
def islands(im):
    a = np.array(im); m = a[..., 3] > 0; lab, k = ndimage.label(m, np.ones((3, 3)))
    if k <= 1: return im
    sz = ndimage.sum(m, lab, range(1, k + 1)); big = lab == np.argmax(sz) + 1; near = ndimage.binary_dilation(big, iterations=6)
    keep = np.isin(lab, [i for i in range(1, k + 1) if (near & (lab == i)).any()]); a[~keep] = 0; return Image.fromarray(a)
def save(name, cells):
    s = Image.new('RGBA', (256 * len(cells), 256), (0, 0, 0, 0))
    for i, c in enumerate(cells): s.alpha_composite(c, (256 * i, 0))
    s.save(f'{OUT}/c1_quilted_boar_{name}.png'); print(name, len(cells))
base = lambda n: Image.open(f'{C}/base/{n}.png').convert('RGBA')
# walk: one scale (frame 0 height -> side_stand height) and one shift (lowest foot of the clip -> 249)
fr = [islands(Image.open(f'{C}/tw/walk/{i:03d}.png').convert('RGBA')) for i in range(8)]
h0 = fr[0].getbbox(); s = (base('side_stand').getbbox()[3] - base('side_stand').getbbox()[1]) / (h0[3] - h0[1])
fr = [f.resize((round(256 * s), round(256 * s)), Image.LANCZOS) for f in fr]
bot = max(f.getbbox()[3] for f in fr); cx = (fr[0].getbbox()[0] + fr[0].getbbox()[2]) / 2
cells = []
for f in fr: c = Image.new('RGBA', (256, 256), (0, 0, 0, 0)); c.alpha_composite(f, (round(128 - cx), 249 - bot)); cells.append(c)
save('walk', cells); print('walk scale', round(s, 3))
save('attack', [base('side_stand'), base('crouch'), base('charge')])
