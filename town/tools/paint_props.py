"""Area-1 painted prop atlas: key out the #FF00FF-ish background of the generated prop sheets (assets_src/world/paint/props_*.jpg),
split into connected objects, scale each to its in-game size (buffer px = 2x logical px, 768x432 base grid) and pack
assets/world/paint/props.png + props.json  {name: [x, y, w, h, ax, ay]}  (ax, ay = anchor = feet/base point inside the cell, buffer px).
Run: python3 tools/paint_props.py   (from town/ or anywhere)"""
import os, json, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SRC = R + 'assets_src/world/paint/'; OUT = R + 'assets/world/paint/'
# (sheet, [names in reading order (row by row, left to right)], {name: target width in buffer px})
SHEETS = {
 'props_forest': ['oak_a', 'oak_b', 'pine', 'bush', 'bush_flower', 'boulder', 'rocks', 'stump', 'log', 'mushrooms', 'flowers_blue', 'flowers_yellow', 'fern'],
 'props_ruins': ['temple_gate', 'arch', 'ruin_wall', 'pillar_broken', 'pillar_fallen', 'tablet', 'bridge_v', 'fence', 'signpost', 'boulder_cracked'],
 'props_dungeon': ['sconce', 'brazier', 'crystal', 'pillar_d', 'stairs_down', 'stairs_up', 'rubble', 'statue', 'door', 'portcullis', 'doorway', 'door_sealed'],
}
SIZE = {'oak_a': 150, 'oak_b': 150, 'pine': 104, 'bush': 54, 'bush_flower': 54, 'boulder': 60, 'rocks': 46, 'stump': 46, 'log': 72, 'mushrooms': 30,
        'flowers_blue': 36, 'flowers_yellow': 34, 'fern': 40,
        'temple_gate': 236, 'arch': 150, 'ruin_wall': 96, 'pillar_broken': 46, 'pillar_fallen': 74, 'tablet': 48, 'bridge_v': 96, 'fence': 64, 'signpost': 40, 'boulder_cracked': 72,
        'sconce': 26, 'brazier': 50, 'crystal': 44, 'pillar_d': 40, 'stairs_down': 60, 'stairs_up': 60, 'rubble': 64, 'statue': 64,
        'door': 62, 'portcullis': 62, 'doorway': 62, 'door_sealed': 62}
DIL = {'props_dungeon': 4}
def key_sheet(name, names):
    im = np.asarray(Image.open(SRC + name + '.jpg').convert('RGB')).astype(np.float32)
    h, w, _ = im.shape
    corners = np.concatenate([im[:12, :12].reshape(-1, 3), im[:12, -12:].reshape(-1, 3), im[-12:, :12].reshape(-1, 3), im[-12:, -12:].reshape(-1, 3)])
    bg = np.median(corners, 0)
    d = np.sqrt(((im - bg) ** 2).sum(2))
    # magenta-ness: high R and B, low G
    mag = np.minimum(im[..., 0], im[..., 2]) - im[..., 1]
    a = np.clip((d - 40) / 60, 0, 1) * np.clip((150 - mag) / 70, 0, 1) ** 0.5
    a = np.where(d < 30, 0, a)
    solid = a > .5
    solid = ndi.binary_opening(solid, iterations=1)
    grp = ndi.binary_dilation(solid, iterations=DIL.get(name, 9))
    lab, n = ndi.label(grp)
    objs = ndi.find_objects(lab)
    items = []
    for i, sl in enumerate(objs):
        area = (lab[sl] == i + 1).sum()
        if area < 600: continue
        items.append((sl, i + 1))
    # reading order: cluster rows by centre y
    items.sort(key=lambda it: (it[0][0].start + it[0][0].stop) / 2)
    rows = []; 
    for it in items:
        cy = (it[0][0].start + it[0][0].stop) / 2
        if rows and abs(cy - rows[-1][0]) < h * .12: rows[-1][1].append(it)
        else: rows.append([cy, [it]])
    ordered = [it for r in rows for it in sorted(r[1], key=lambda it: it[0][1].start)]
    print(name, 'found', len(ordered), 'expected', len(names))
    out = {}
    for nm, (sl, li) in zip(names, ordered):
        m = (lab[sl] == li) & ndi.binary_erosion(a[sl] > .35, iterations=2)
        alpha = a[sl] * m
        rgb = im[sl].copy()
        # despill: pull magenta fringe toward neighbours (reduce R/B excess over G at soft edges)
        edge = ndi.binary_dilation(alpha < .98, iterations=3)
        ex = np.maximum(0, np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1] - 10)
        rgb[..., 0] -= ex * edge; rgb[..., 2] -= ex * edge
        ys, xs = np.nonzero(alpha > .05)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([np.clip(rgb[y0:y1, x0:x1], 0, 255), alpha[y0:y1, x0:x1] * 255]).astype(np.uint8)
        out[nm] = Image.fromarray(rgba, 'RGBA')
    return out
def scale(img, tw):
    w, h = img.size; th = max(1, round(h * tw / w))
    # premultiplied downscale (no dark/magenta halos), then a light unsharp for crisp pixel edges
    a = np.asarray(img).astype(np.float32) / 255
    pm = np.dstack([a[..., :3] * a[..., 3:4], a[..., 3:4]])
    pim = Image.fromarray((pm * 255).astype(np.uint8), 'RGBA').resize((tw, th), Image.LANCZOS)
    p = np.asarray(pim).astype(np.float32) / 255
    al = p[..., 3:4]; rgb = np.where(al > 1e-3, p[..., :3] / np.maximum(al, 1e-3), 0)
    al = np.where(al < .12, 0, np.clip((al - .12) / .7, 0, 1))  # harden the alpha edge (sprite look)
    o = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), al]) * 255).astype(np.uint8), 'RGBA')
    return o.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
def main():
    sprites = {}
    for sh, names in SHEETS.items():
        for nm, im in key_sheet(sh, names).items(): sprites[nm] = scale(im, SIZE[nm])
    # simple shelf packing
    W = 1024; x = y = rowh = 0; rects = {}
    order = sorted(sprites, key=lambda k: -sprites[k].size[1])
    for nm in order:
        w, h = sprites[nm].size
        if x + w + 2 > W: x = 0; y += rowh + 2; rowh = 0
        rects[nm] = [x, y, w, h]; x += w + 2; rowh = max(rowh, h)
    H = y + rowh
    atlas = Image.new('RGBA', (W, H))
    meta = {}
    for nm, (x, y, w, h) in rects.items():
        atlas.paste(sprites[nm], (x, y))
        a = np.asarray(sprites[nm])[..., 3]; ys = np.nonzero(a.max(1) > 40)[0]
        meta[nm] = [x, y, w, h, w // 2, int(ys.max()) if len(ys) else h - 1]   # anchor = bottom-centre of the opaque part
    atlas.save(OUT + 'props.png', optimize=True)
    json.dump({'note': 'area-1 painted props (tools/paint_props.py). rect = [x, y, w, h, anchorX, anchorY] in buffer px (2x logical).', 'scale': 2, 'rects': meta},
              open(OUT + 'props.json', 'w'), separators=(',', ':'))
    print('atlas', atlas.size, len(meta))
if __name__ == '__main__': main()
