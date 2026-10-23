"""잿빛 들판 D=3 미리보기 (바닥은 임시 단색+잡음, 3번방이 코드로 제대로). field_preview.png"""
import json, sys, numpy as np
from PIL import Image
M = json.load(open(sys.argv[1])); P = json.load(open('final/parts.json')); L = P['field_legend']; P = P['parts']
G = M['ground']; T = 48; x0, y0, cw, ch = 0, 0, 40, 23
GC = {'.': (78, 74, 58), ',': (74, 70, 54), "'": (80, 74, 60), '=': (98, 80, 60), '~': (44, 58, 62), ':': (88, 84, 76), '#': (40, 34, 28), '"': (82, 76, 56), '_': (110, 96, 76), 'b': (44, 58, 62)}
rng = np.random.default_rng(3)
H, W = ch * T, cw * T
g = np.zeros((H // 3, W // 3, 3))
for y in range(ch):
    for x in range(cw):
        c = G[y0 + y][x0 + x]; g[y * 16:(y + 1) * 16, x * 16:(x + 1) * 16] = GC.get(c, GC['.'])
g += rng.normal(0, 4, g.shape)
bg = Image.fromarray(g.clip(0, 255).astype(np.uint8)).resize((W, H), Image.NEAREST).convert('RGBA')
items = []
for y in range(ch):
    for x in range(cw):
        c = G[y0 + y][x0 + x]
        if c in L:
            ids = L[c]; pid = ids[(x * 7 + y * 13) % len(ids)]
            jx, jy = rng.integers(-10, 11), rng.integers(-6, 7)
            items.append(((y + 1) * T + jy, (x + .5) * T + jx, pid))
for fy, fx, pid in sorted(items):
    p = P[pid]; im = Image.open('final/' + p['img']).convert('RGBA')
    bg.alpha_composite(im, (int(fx - p['ax']), int(fy - p['ay'])))
bg.crop((0, 0, 1920, 1080)).save('field_preview.png')
