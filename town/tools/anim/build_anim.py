"""Build a character animation atlas + JSON from generated sprite strips.
   python3 tools/anim/build_anim.py hero
 in : tools/anim/<char>_anim.src.json, src/<char>/anim_raw/*.jpg
 out: src/<char>/anim_keyed/*.png (exact #FF00FF bg), assets/anim/<char>.png (+ _magenta.png), assets/anim/<char>.json
 Frames are scaled so the reference pose is heroH logical px tall, downsampled (box filter), palette-snapped,
 alpha-thresholded, and anchored at the feet (baseline) / body centre-of-mass so frames don't jitter."""
import json, sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from key import keyed, split_frames
from scipy import ndimage as ndi
ROOT = '/workspace/town-demo/'
char = sys.argv[1] if len(sys.argv) > 1 else 'hero'
C = json.load(open(ROOT + f'tools/anim/{char}_anim.src.json'))
RAW = ROOT + f'src/{char}/anim_raw/'; KEY = ROOT + f'src/{char}/anim_keyed/'; os.makedirs(KEY, exist_ok=True)

def body_mask(rgba):
    a = rgba[..., 3] > 0; r, g, b = [rgba[..., i].astype(int) for i in range(3)]
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
    steel = (mx > 140) & (mx - mn < 40)            # blade / white smear
    cyan = (b > 150) & (g > 150) & (r < 200) & (b - r > 40)
    return a & ~steel & ~cyan

def frames_of(path, n):
    rgb, fg = keyed(path)
    o = rgb.copy(); o[~fg] = [255, 0, 255]
    Image.fromarray(o).save(KEY + os.path.basename(path).replace('.jpg', '.png'))
    segs = split_frames(fg, n); out = []
    for sg in segs:
        if sg[0] == 'ids': m = np.isin(sg[2], sg[1])
        else:
            a, b = sg; m = np.zeros_like(fg); m[:, a:b] = fg[:, a:b]
        ys, xs = np.where(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8); rgba[..., :3] = rgb[y0:y1, x0:x1]; rgba[..., 3] = m[y0:y1, x0:x1] * 255
        out.append(rgba)
    if len(out) != n: print('WARN', path, 'found', len(out), 'frames, expected', n)
    return out

def downscale(rgba, s):
    H, W = rgba.shape[:2]; nw, nh = max(1, round(W * s)), max(1, round(H * s))
    a = rgba[..., 3:4].astype(float) / 255; pm = np.concatenate([rgba[..., :3] * a, a * 255], -1).astype(np.float32)
    ch = [np.asarray(Image.fromarray(pm[..., i]).resize((nw, nh), Image.BOX)) for i in range(4)]
    al = ch[3] / 255; rgb = np.stack(ch[:3], -1) / np.maximum(al[..., None], 1e-3)
    out = np.zeros((nh, nw, 4), np.uint8); out[..., :3] = np.clip(rgb, 0, 255); out[..., 3] = (al > .45) * 255
    return out

def anchor(rgba):
    bm = body_mask(rgba); a = rgba[..., 3] > 0
    use = bm if bm.sum() > 20 else a
    rc = use.sum(1); rows = [i for i in range(len(rc)) if rc[i] >= 2]
    base = max(rows) if rows else rgba.shape[0] - 1
    ys, xs = np.where(use); cx = xs.mean()
    # feet centre if the lowest 12% is clearly feet (more stable for standing/walking)
    return float(cx), int(base)

SH = {}
for k, s in C['sheets'].items():
    fr = frames_of(RAW + s['file'] + '.jpg', s['n'])
    ref = fr[s['ref']]; bm = body_mask(ref); ys = np.where(bm.any(1))[0]; h = ys.max() - ys.min() + 1
    sc = C['heroH'] * s.get('refFactor', 1) / h
    SH[k] = [downscale(f, sc) for f in fr]

# palette: shared 48-colour palette for crisp pixels
allpx = np.concatenate([f[f[..., 3] > 0][:, :3] for v in SH.values() for f in v])
pal_img = Image.fromarray(allpx[None, :, :].astype(np.uint8)).quantize(48, method=Image.Quantize.MEDIANCUT)
def snap(f):
    q = Image.fromarray(f[..., :3]).quantize(palette=pal_img, dither=Image.Dither.NONE).convert('RGB')
    o = f.copy(); o[..., :3] = np.asarray(q); return o
for k in SH: SH[k] = [snap(f) for f in SH[k]]

def bob(f, px):  # drop the upper body by px (seam at the belt, ~45% of height) -> breathing / walk bob
    if not px: return f
    a = f[..., 3] > 0; ys = np.where(a.any(1))[0]; top, bot = ys.min(), ys.max(); cut = int(top + (bot - top) * .45)
    o = f.copy(); up = f[top:cut].copy(); o[top:cut + px] = 0
    o[top + px:cut + px][up[..., 3] > 0] = up[up[..., 3] > 0]
    # refill the seam rows from the original lower part
    low = f[cut:cut + px]; m = (o[cut:cut + px, :, 3] == 0) & (low[..., 3] > 0); o[cut:cut + px][m] = low[m]
    return o

uniq = {}; cells = []
def cell(sheet, idx, opt):
    fl = bool(opt.get('flip')); key = (sheet, idx, opt.get('bob', 0), fl)
    if key in uniq: return uniq[key]
    src = SH[sheet][idx][:, ::-1].copy() if fl else SH[sheet][idx]   # flip: mirrored frame (front/back views: same swing from the other side)
    f = bob(src, opt.get('bob', 0)); ax, ay = anchor(src)
    cells.append(dict(img=f, ax=ax, ay=ay)); uniq[key] = len(cells) - 1; return uniq[key]

anims = {}
for name, A in C['anims'].items():
    if isinstance(A, str): continue
    fl = []
    for e in A['frames']:
        opt = e[3] if len(e) > 3 else {}
        fl.append([cell(e[0], e[1], opt), e[2], opt.get('dx', 0), opt.get('dy', 0)])
    anims[name] = dict(loop=A['loop'], frames=fl, ticks=sum(f[1] for f in fl))
for name, A in C['anims'].items():
    if isinstance(A, str): anims[name] = dict(anims[A], alias=A)

# pack (shelf)
PAD = 1; W = 512; x = y = rowh = 0; rects = []
for c in cells:
    h, w = c['img'].shape[:2]
    if x + w + PAD > W: x = 0; y += rowh + PAD; rowh = 0
    rects.append((x, y, w, h)); x += w + PAD; rowh = max(rowh, h)
H = y + rowh
atlas = np.zeros((H, W, 4), np.uint8)
for c, (x, y, w, h) in zip(cells, rects): atlas[y:y + h, x:x + w] = c['img']
os.makedirs(ROOT + 'assets/anim', exist_ok=True)
Image.fromarray(atlas).save(ROOT + f'assets/anim/{char}.png')
mag = atlas.copy(); mag[atlas[..., 3] == 0] = [255, 0, 255, 255]; Image.fromarray(mag).save(ROOT + f'assets/anim/{char}_magenta.png')
out = dict(_doc='GENERATED by tools/anim/build_anim.py from tools/anim/%s_anim.src.json - edit the src json, not this. cells: [x,y,w,h,ax,ay] in logical px (ax,ay = foot anchor). anim frames: [cell, ticks@60fps, dx, dy].' % char,
           src=f'anim/{char}.png', logicalScale=C['logicalScale'], heroH=C['heroH'],
           cells=[[*r, round(c['ax'], 1), c['ay']] for c, r in zip(cells, rects)], anims=anims,
           weapons=C.get('weapons', {}), itemWeaponType=C.get('itemWeaponType', {}), titleCombo=C.get('titleCombo', {}))
json.dump(out, open(ROOT + f'assets/anim/{char}.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('cells', len(cells), 'atlas', W, H, 'anims', len(anims))
