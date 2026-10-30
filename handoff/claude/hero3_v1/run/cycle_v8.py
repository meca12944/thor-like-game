# 정면 달리기 16장: 핵심 4장(디딤 CR·지나감 PB·디딤 CL·지나감 PA) 사이마다 사이 장 3장. 나쁜 사이 장(주먹이 가운데로)은 반대쪽 묶음의 좋은 장을 좌우 뒤집어 씀.
# 키는 출발 그림 키에 맞춤(pxscale, 발 기준), 지나가는 장에서 몸 +2px, 공중 4px까지, 정면 = 얼굴 가운데로 제자리.
import sys, os, math, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pxscale import pxscale
out = sys.argv[1]; GROUND = 246; AIR = 4; RISE = 2
SEQ = [('hero3_CR.png', 0), ('t7_CRPB/002.png', 0), ('hero_PB2.png', 0), ('t7_PBCL/002.png', 0),
       ('hero3_CL.png', 0), ('t7_CLPA/002.png', 0), ('hero_PA2.png', 0), ('t7_PACR/002.png', 0)]
def bb(im): return im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
def facex(im):
    a = np.asarray(im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (a[..., 3] > 0) & (r > g) & (g > b) & (r - b > 45) & (r > 120); m[90:] = False
    return np.nonzero(m)[1].mean()
start = Image.open('start_s.png').convert('RGBA'); keyH = bb(start)[3] - bb(start)[1]; hx = facex(start)
os.makedirs(out, exist_ok=True)
for i, (f, mir) in enumerate(SEQ):
    im = Image.open(f).convert('RGBA')
    if mir: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    b = bb(im); hh = b[3] - b[1]
    target = keyH + RISE * math.sin(math.pi * (i % 4) / 4)
    if abs(target - hh) > 0.5:
        s = target / hh; im2 = pxscale(im, s); cx = (b[0] + b[2]) / 2; fy = b[3]
        c = Image.new('RGBA', (256, 256)); c.paste(im2, (round(cx - cx * s), round(fy - fy * s)), im2); im = c
    b2 = bb(im); dy = 0
    if b2[3] < GROUND - AIR: dy = GROUND - AIR - b2[3]
    if b2[3] > GROUND: dy = GROUND - b2[3]
    dx = round(hx - facex(im))
    if dx or dy: c = Image.new('RGBA', (256, 256)); c.paste(im, (dx, dy), im); im = c
    im.save(f'{out}/{i:03d}.png'); print(i, f, '뒤집음' if mir else '', 'h', hh, '->', bb(im)[3] - bb(im)[1], 'dx', dx)
