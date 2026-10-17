"""Hero frame proportion measurement (source sheets). Scale proxy = the HAIR blob (rigid, present in every
view/pose, never covered by the sword): crown = top of hair, hair height / width / sqrt(area).
Head height (crown->chin) is estimated as hair_h * k measured on the idle frame (front views have face below
hair; back views hair covers the head)."""
import json, sys, os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, '/workspace/town-demo/tools/anim')
from key import keyed, split_frames
RAW = '/workspace/town-demo/src/hero/anim_raw/'

def frames(path, n):
    rgb, fg = keyed(path); out = []
    for sg in split_frames(fg, n):
        if sg[0] == 'ids': m = np.isin(sg[2], sg[1])
        else:
            a, b = sg; m = np.zeros_like(fg); m[:, a:b] = fg[:, a:b]
        ys, xs = np.where(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8); rgba[..., :3] = rgb[y0:y1, x0:x1]; rgba[..., 3] = m[y0:y1, x0:x1] * 255
        out.append(rgba)
    return out

def hair(rgba):
    a = rgba[..., 3] > 0; r, g, b = [rgba[..., i].astype(int) for i in range(3)]
    mx = np.maximum(np.maximum(r, g), b)
    dark = a & (mx < 95) & (b >= r - 4) & (b >= g - 4)     # navy-black hair (boots/belt are brown: r > b)
    dark = ndi.binary_closing(dark, iterations=2) & a
    lab, n = ndi.label(dark)
    if n == 0: return None
    sz = ndi.sum(dark, lab, range(1, n + 1)); objs = ndi.find_objects(lab)
    # hair = biggest dark blob whose top is in the upper 45% of the figure
    H = rgba.shape[0]; best = None
    for i, o in enumerate(objs):
        if o[0].start < H * .45 and sz[i] > 30 and (best is None or sz[i] > sz[best]): best = i
    if best is None: return None
    o = objs[best]
    return dict(top=o[0].start, h=o[0].stop - o[0].start, w=o[1].stop - o[1].start, area=float(sz[best]), cx=(o[1].start + o[1].stop) / 2)

if __name__ == '__main__':
    C = json.load(open('/workspace/town-demo/tools/anim/hero_anim.src.json'))
    for k, s in list(C['sheets'].items())[:int(sys.argv[1]) if len(sys.argv) > 1 else 99]:
        fr = frames(RAW + s['file'] + '.jpg', s['n'])
        hs = [hair(f) for f in fr]
        print(k, s['file'], 'refH', fr[s['ref']].shape[0], 'hair sqrtA', [round(h['area'] ** .5, 1) if h else None for h in hs], 'hairW', [h['w'] if h else None for h in hs])
