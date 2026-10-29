# 핵심 자세 2장 + 사이 장 → 달리기 8장 (교본 부록 A-5). 키는 핵심 자세 평균에 맞춤(pxscale, 발 기준), 지나가는 장은 살짝 올림, 공중은 4px까지.
import sys, glob, os, math
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pxscale import pxscale
d, out = sys.argv[1], sys.argv[2]; RISE = 2; GROUND = 246; AIR = 4
RL = sorted(glob.glob(f'tw_{d}_RL/*.png')); LR = sorted(glob.glob(f'tw_{d}_LR/*.png'))
seq = [RL[0], RL[1], RL[2], RL[3], LR[0], LR[1], LR[2], LR[3]]
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
    im.save(f'{out}/{i:03d}.png'); print(d, i, os.path.basename(os.path.dirname(f)) + '/' + os.path.basename(f), 'h', hh, '->', bb(im)[3] - bb(im)[1], 'bottom', bb(im)[3])
