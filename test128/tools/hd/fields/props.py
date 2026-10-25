"""Prop catalog for the HD fields: crop + mild grade + foot anchor for the generated PixelLab props,
plus the existing D=3 felt parts. Output: assets/world/fields_hd/<name>.png and a catalog dict."""
import os, glob, json
import numpy as np
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.environ.get('PL_OUT', '/tmp/plwork/out/gi')
OUT = 'assets/world/fields_hd'
def _grade(a, sat=.8, warm=(1.03, 1.0, .94), gain=.97):
    rgb = a[..., :3].astype(np.float32); l = (rgb * [.3, .59, .11]).sum(-1, keepdims=True)
    rgb = (l + (rgb - l) * sat) * np.array(warm) * gain
    a = a.copy(); a[..., :3] = np.clip(rgb, 0, 255); return a
def anchor(im):
    a = np.array(im)[..., 3] > 40; ys, xs = np.nonzero(a)
    if not len(ys): return im.width // 2, im.height
    cnt = a.sum(1); thr = cnt.max() * .22; rows = np.nonzero(cnt > thr)[0]; base = rows.max()
    y0 = max(ys.min(), base - max(4, (base - ys.min()) // 7)); sub = a[y0:base + 1]
    xs2 = np.nonzero(sub)[1]; ax = int(round(xs2.mean())) if len(xs2) else im.width // 2
    return ax, int(base - 1)
def prep(src, name, sat=.8, warm=(1.03, 1.0, .94), gain=.97, regrade=True):
    im = Image.open(src).convert('RGBA'); bb = im.getbbox(); im = im.crop(bb)
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] < 40, 0, 255)  # hard alpha: crisp pixel edges
    if regrade: a = _grade(a, sat, warm, gain)
    im = Image.fromarray(a.astype(np.uint8)); os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    rel = f'{OUT}/{name}.png'; im.save(os.path.join(ROOT, rel), optimize=True)
    ax, ay = anchor(im); return {'img': rel, 'ax': ax, 'ay': ay, 'w': im.width, 'h': im.height}
# existing felt / field_felt parts (already graded, anchors from the earlier builds)
OLD = {
 'ash_tree_a': ('assets/world/field_felt_hd/ash_tree_a.png', 66, 181), 'ash_tree_b': ('assets/world/field_felt_hd/ash_tree_b.png', 66, 164),
 'dead_tree': ('assets/world/field_felt_hd/dead_tree.png', 64, 175), 'burnt_pine_a': ('assets/world/field_felt_hd/burnt_pine_a.png', 29, 192),
 'burnt_pine_b': ('assets/world/field_felt_hd/burnt_pine_b.png', 47, 200), 'bush_b': ('assets/world/field_felt_hd/bush_b.png', 46, 53),
 'ash_bush': ('assets/world/field_felt_hd/ash_bush.png', 45, 54), 'boulder': ('assets/world/field_felt_hd/boulder.png', 41, 87),
 'stone_low': ('assets/world/field_felt_hd/stone_low.png', 70, 43), 'stump': ('assets/world/field_felt_hd/stump.png', 25, 46),
 'pale_mushrooms': ('assets/world/field_felt_hd/pale_mushrooms.png', 32, 55), 'ruin_pillar': ('assets/world/field_felt_hd/ruin_pillar.png', 38, 143),
 'thread_stake': ('assets/world/field_felt_hd/thread_stake.png', 8, 116), 'dry_reeds': ('assets/world/field_felt_hd/dry_reeds.png', 37, 74),
 'bridge_3': ('assets/world/field_felt_hd/bridge_3.png', 60, 143), 'rubble': ('assets/world/felt/rubble.png', 27, 32),
 'mausoleum': ('assets/world/felt/mausoleum.png', 47, 141), 'tombs': ('assets/world/felt/tombs.png', 70, 112),
}
GEN = {  # generated sets: name -> (glob prefix, grade kwargs)
 'oak': ('pr_oak4', {}), 'oak1': ('pr_oak', {}), 'crystal': ('pr_crystal', {'sat': .7}), 'stalag': ('pr_stalag', {}),
 'palm': ('pr_palm', {}), 'desert_rock': ('pr_desert', {}), 'sandruin': ('pr_sandruin', {'sat': .75}),
 'coral': ('pr_coral', {'sat': .5, 'warm': (1.0, 1.0, .98), 'gain': .9}), 'coastpine': ('pr_coastpine', {}),
 'basalt': ('pr_basalt', {'sat': .85}), 'snowrock': ('pr_snowrock', {'sat': .7}), 'temple': ('pr_temple', {}),
 'pine_snow': ('pr_pine_snow', {}),
 'lm_cave': ('lm_cave', {'sat': .6}), 'lm_desert': ('lm_desert', {}), 'lm_pyramid': ('lm_pyramid', {}), 'lm_wreck': ('lm_wreck', {}),
 'lm_lighthouse': ('lm_lighthouse', {}), 'lm_vfort': ('lm_vfort', {}), 'lm_frosttower': ('lm_frosttower', {'sat': .7}), 'lm_temple': ('lm_temple', {}),
}
def catalog(build=True):
    C = {}
    for k, (p, ax, ay) in OLD.items():
        im = Image.open(os.path.join(ROOT, p)); C[k] = [{'img': p, 'ax': ax, 'ay': ay, 'w': im.width, 'h': im.height}]
    cache = os.path.join(ROOT, OUT, 'catalog.json')
    old = json.load(open(cache)) if os.path.exists(cache) else {}
    for k, (pre, kw) in GEN.items():
        fs = sorted(f for f in glob.glob(f'{SRC}/{pre}_[0-9].png'))
        if build and fs: C[k] = [prep(f, f'{k}_{i}', **kw) for i, f in enumerate(fs)]
        elif k in old: C[k] = old[k]
    json.dump({k: v for k, v in C.items() if k in GEN}, open(cache, 'w'), indent=0)
    return C
if __name__ == '__main__':
    C = catalog(); print({k: len(v) for k, v in C.items()})
