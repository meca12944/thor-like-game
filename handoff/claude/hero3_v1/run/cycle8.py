# 핵심 자세 2장 + 사이 장 → 달리기 8장 (교본 부록 A-5). 키는 핵심 자세 평균에 맞춤(pxscale, 발 기준), 지나가는 장은 살짝 올림, 공중은 4px까지.
import sys, glob, os, math
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pxscale import pxscale
d, out = sys.argv[1], sys.argv[2]; RISE = 2; GROUND = 246; AIR = 4
# v2(정면): 핵심 자세 4장 R·P1·L·P2(P = 두 다리가 엉덩이 밑에 모인 지나가는 자세) + 사이 장 4묶음의 가운데 1장씩
# v3(정면, 깊이): 디딤 CR(오른발 앞·아래·크게) · 지나감 PA · 디딤 CL · 지나감 PB(=PA 뒤집어 고침) + 사이 장 가운데 1장씩
# v4(정면, 깊이, 발 앞 보기): 디딤 CR → 사이(PB2 쪽, 발 앞) → 지나감 PB2 → 사이 → 디딤 CL2 → 사이(= 2번째 사이 장 좌우 뒤집기) → 지나감 PA → 사이
seq = ['key_s_CR.png', 't5_PBCR/001.png', 'key_s_PB2_s.png', 't5_CLPB/001.png', 'key_s_CL2.png', 'pbcr1_mirror.png', 'key_s_PA_s.png', 't5_CRPA/001.png']
RL = [seq[0]]; LR = [seq[4]]
def bb(im): return im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
keyH = sum(bb(Image.open(f).convert('RGBA'))[3] - bb(Image.open(f).convert('RGBA'))[1] for f in (RL[0], LR[0])) / 2
os.makedirs(out, exist_ok=True)
for i, f in enumerate(seq):
    im = Image.open(f).convert('RGBA'); b = bb(im); hh = b[3] - b[1]; ph = i % 4
    target = keyH + (RISE * math.sin(math.pi * ph / 4) if ph else 0)
    if abs(target - hh) > 0.5:
        s = target / hh; im2 = pxscale(im, s); cx = (b[0] + b[2]) / 2; fy = b[3]
        c = Image.new('RGBA', (256, 256)); c.alpha_composite(im2, (round(cx - cx * s), round(fy - fy * s))) if False else c.paste(im2, (round(cx - cx * s), round(fy - fy * s)), im2); im = c
    b2 = bb(im)
    if b2[3] < GROUND - AIR:                       # 공중 4px까지 (깡충 방지)
        c = Image.new('RGBA', (256, 256)); c.paste(im, (0, GROUND - AIR - b2[3]), im); im = c
    if b2[3] > GROUND: c = Image.new('RGBA', (256, 256)); c.paste(im, (0, GROUND - b2[3]), im); im = c
    import numpy as np                            # 머리(맨 위 40줄) 가운데를 출발 그림 머리 가운데에 맞춤 → 장마다 옆으로 미끄러지지 않게
    def headx(im):     # 정면 = 얼굴 살색 가운데, 뒷면 = 어깨 띠(머리끝+45~75줄) 가운데 (날리는 머리카락·망토에 안 끌리게)
        a = np.asarray(im).astype(int); al = a[..., 3] > 8; t = np.nonzero(al.any(1))[0].min()
        if d == 's':
            r, g, b = a[..., 0], a[..., 1], a[..., 2]; m = al & (r > g) & (g > b) & (r - b > 45) & (r > 120); m[90:] = False
            return np.nonzero(m)[1].mean()
        ys, xs = np.nonzero(al[t + 45:t + 75]); return xs.mean()
    if not hasattr(sys, '_hx'): sys._hx = headx(Image.open('start_' + d + '.png').convert('RGBA'))
    dx = round(sys._hx - headx(im))
    if dx: c = Image.new('RGBA', (256, 256)); c.paste(im, (dx, 0), im); im = c
    im.save(f'{out}/{i:03d}.png'); print(d, i, os.path.basename(os.path.dirname(f)) + '/' + os.path.basename(f), 'h', hh, '->', bb(im)[3] - bb(im)[1], 'bottom', bb(im)[3], 'dx', dx)
