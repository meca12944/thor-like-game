"""Style-sample sprite pipeline: generated hi-res pixel-art sheet (#FF00FF bg) -> clean in-game pixel sprite
at the NEW logical grid (768x432, 32px tiles). Steps: key magenta -> split frames -> common scale (ref frame
height = target) -> area downsample -> binary alpha -> shared palette quantize -> remove stray pixels ->
1px dark selective outline. Output: strip PNG + json (cells with foot anchor)."""
import json, sys, numpy as np
from PIL import Image
from scipy import ndimage

def key(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # magenta-ness: high R & B, low G
    mag = np.minimum(r, b) - g
    alpha = (mag < 70).astype(np.float32)            # binary key: dark-magenta fringe counts as background
    # despill remaining fg: min(R,B) may not exceed G by more than 30
    spill = np.clip(np.minimum(r, b) - g - 30, 0, None)
    a[..., 0] -= spill; a[..., 2] -= spill
    alpha = ndimage.binary_opening(alpha > 0, iterations=1).astype(np.float32)
    return np.dstack([np.clip(a, 0, 255), alpha])

def frames(k, minw=20):
    al = k[..., 3] > 0.5
    lab, n = ndimage.label(ndimage.binary_dilation(al, iterations=6))
    boxes = []
    for sl in ndimage.find_objects(lab):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if h > 80 and w > minw: boxes.append(sl)
    boxes.sort(key=lambda s: s[1].start)
    out = []
    for sl in boxes:
        sub = k[sl].copy(); m = lab[sl] == lab[sl][al[sl]].max() if False else None
        ys, xs = np.where(sub[..., 3] > 0.5)
        out.append(sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    return out

SHARP = 0.6
def down(fr, s):
    h, w = fr.shape[:2]; W = max(1, round(w * s)); H = max(1, round(h * s))
    pm = fr.copy(); pm[..., :3] *= pm[..., 3:4]
    im = Image.fromarray(pm.astype(np.float32)[..., 0]).mode  # dummy
    chans = [np.asarray(Image.fromarray(pm[..., c].astype(np.float32), 'F').resize((W, H), Image.BOX)) for c in range(4)]
    o = np.dstack(chans); a = o[..., 3]
    rgb = o[..., :3] / np.maximum(a[..., None], 1e-3)
    rgb = np.clip(rgb, 0, 255)
    # light unsharp on the small sprite so eyes / gold trim survive the downscale
    blur = np.dstack([ndimage.uniform_filter(rgb[..., c] * (a > .3), 3) / np.maximum(ndimage.uniform_filter((a > .3).astype(float), 3), 1e-3) for c in range(3)])
    rgb = np.clip(rgb + SHARP * (rgb - blur), 0, 255)
    return np.dstack([rgb, (a > 0.5).astype(np.float32)])

def palette_quant(sprites, ncol):
    px = np.concatenate([s[..., :3][s[..., 3] > 0] for s in sprites]).astype(np.uint8)
    sample = Image.fromarray(px[None, :, :])
    pal_img = sample.quantize(colors=ncol, method=Image.MEDIANCUT, dither=Image.NONE)
    pal = np.array(pal_img.getpalette()[:ncol * 3]).reshape(-1, 3).astype(np.float32)
    out = []
    for s in sprites:
        rgb = s[..., :3]; d = ((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1)
        q = pal[d.argmin(-1)]
        out.append(np.dstack([q, s[..., 3]]))
    return out, pal

def clean(s):
    a = s[..., 3] > 0
    nb = ndimage.convolve(a.astype(int), np.ones((3, 3), int), mode='constant') - a
    a = a & (nb >= 2)                          # drop isolated / whisker pixels
    holes = (~a) & (ndimage.convolve(a.astype(int), np.array([[0,1,0],[1,0,1],[0,1,0]]), mode='constant') >= 4)
    rgb = s[..., :3].copy()
    if holes.any():                            # fill 1px pinholes with neighbour avg
        for y, x in zip(*np.where(holes)):
            ys, xs = slice(max(0,y-1), y+2), slice(max(0,x-1), x+2)
            m = a[ys, xs]; rgb[y, x] = rgb[ys, xs][m].mean(0)
        a = a | holes
    return np.dstack([rgb, a.astype(np.float32)])

def outline(s, outc=(28, 20, 26)):
    a = s[..., 3] > 0
    edge = a & ~ndimage.binary_erosion(a, structure=np.array([[0,1,0],[1,1,1],[0,1,0]]), border_value=0)
    rgb = s[..., :3].copy()
    lum = rgb @ np.array([.299, .587, .114])
    e = edge & (lum > 60)
    rgb[e] = rgb[e] * 0.35 + np.array(outc) * 0.65   # selective (hue-keeping) outline
    return np.dstack([rgb, s[..., 3]])

def reproportion(fr, chin, crotch, heads=7.9, legs=0.50):
    """Piecewise remap of a hi-res frame (fractions of height: chin, crotch measured on the source) so the
    figure becomes `heads` heads tall with legs = `legs` of height. Head shrinks uniformly about the head
    centre, the horizontal shrink ramps back to 1 over the shoulders so hair/neck have no seam."""
    H, W = fr.shape[:2]
    th, tl = 1 / heads, legs; tt = 1 - th - tl
    kh = th / chin
    al = fr[..., 3] > 0.5; ys, xs = np.where(al[: int(chin * H)]); cx = xs.mean()
    yo = np.arange(H) / H
    src = np.where(yo < th, yo / th * chin,
          np.where(yo < th + tt, chin + (yo - th) / tt * (crotch - chin), crotch + (yo - th - tt) / tl * (1 - crotch)))
    ramp = np.clip((yo - th) / 0.12, 0, 1); sx = kh + (1 - kh) * ramp          # horizontal scale per output row
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    sy = src[Y.astype(int)] * H; sxx = cx + (X - cx) / sx[Y.astype(int)]
    out = np.dstack([ndimage.map_coordinates(fr[..., c], [sy, sxx], order=1, cval=0) for c in range(4)])
    return out

def build(name, sheets, target_h, ncol, outdir):
    """sheets: list of (key, path, ref_index, mirror_ok)"""
    allf = {}
    for k, p, ref, *rest in sheets:
        fr = frames(key(p))
        if rest and rest[0]: fr = [reproportion(f, *rest[0]) for f in fr]
        s = target_h / fr[ref].shape[0]
        allf[k] = [down(f, s) for f in fr]
    keys = list(allf); flat = [f for k in keys for f in allf[k]]
    q, pal = palette_quant(flat, ncol)
    q = [outline(clean(f)) for f in q]
    # pack strip: rows per anim
    cells = {}; rows = []; i = 0
    for k in keys:
        rowf = q[i:i + len(allf[k])]; i += len(allf[k]); rows.append((k, rowf))
    W = max(sum(f.shape[1] + 2 for f in r) for _, r in rows); H = sum(max(f.shape[0] for f in r) + 2 for _, r in rows)
    sheet = np.zeros((H, W, 4), np.uint8); y = 0
    for k, r in rows:
        x = 0; rh = max(f.shape[0] for f in r); cells[k] = []
        for f in r:
            h, w = f.shape[:2]; oy = y + rh - h
            sheet[oy:oy + h, x:x + w, :3] = f[..., :3].astype(np.uint8)
            sheet[oy:oy + h, x:x + w, 3] = (f[..., 3] * 255).astype(np.uint8)
            cells[k].append([x, oy, w, h, w // 2, h - 1]); x += w + 2
        y += rh + 2
    Image.fromarray(sheet, 'RGBA').save(f'{outdir}/{name}.png')
    json.dump({'cells': cells, 'targetH': target_h, 'colors': ncol}, open(f'{outdir}/{name}.json', 'w'))
    print(name, sheet.shape, {k: [c[2:4] for c in v] for k, v in cells.items()})

if __name__ == '__main__':
    R = '/workspace/town-demo/src/hero/anim_keyed/'; O = '/workspace/town-demo/style_sample/assets'
    import os; os.makedirs(O, exist_ok=True)
    build('hero_hd', [('down', R + 'walk_down_k4.png', 1), ('right', R + 'walk_right_k6.png', 2), ('up', R + 'walk_up_k4.png', 1)], 56, 40, O)
    build('fem_hd', [('down', '/workspace/town-demo/style_sample/src/fem_walk_down_raw.jpg', 1, (0.149, 0.548))], 68, 48, O)
