"""Pixel measurement of the FINAL sprites (assets/idle_<id>.png) - nothing taken from the transform.
crown = first row with >=2 opaque px in the head column band; sole = last opaque row (baseline);
chin = last face row (skin-width taper -> neck), front/side only (back: face hidden);
split = first transparent row of the leg gap above the feet (front/back; side: legs overlap);
shoulder = width of the contiguous opaque run through the body centre, max over rows chin+3..chin+6."""
import sys, os, json, csv, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import skin
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
O = '/workspace/town-demo/style_sample/'
C = json.load(open(O + 'assets/idle_cells.json'))
OVR = json.load(open(O + 'work/final_chin_override.json')) if os.path.exists(O + 'work/final_chin_override.json') else {}
def run_at(row, cx):
    xx = np.where(row)[0]
    if not len(xx): return 0, None, None
    j = np.argmin(abs(xx - cx)); a = b = xx[j]
    while a - 1 >= 0 and row[a - 1]: a -= 1
    while b + 1 < len(row) and row[b + 1]: b += 1
    return b - a + 1, a, b
def measure(f, view, key):
    a = f[..., 3] > 0; H, W = a.shape
    rows = np.where(a.sum(1) >= 2)[0]; crown, sole = int(rows[0]), int(rows[-1])
    feet = a[sole - 4:sole + 1]; fx = np.where(feet.any(0))[0]; cx = (fx.min() + fx.max()) / 2
    # chin
    chin = None
    if view != 'back':
        sk = skin(np.dstack([f[..., :3], a.astype(float)]))
        w = [run_at(sk[y], cx if view == 'front' else np.where(sk[y])[0].mean() if sk[y].any() else cx)[0] for y in range(crown, crown + 22)]
        top = next((i for i, v in enumerate(w) if v >= 2), None); fm = 0
        if top is not None:
            for i in range(top, len(w)):
                fm = max(fm, w[i])
                if i - top >= 4 and w[i] < .6 * fm: chin = crown + i - 1; break   # last face row
    if key in OVR: chin = OVR[key]
    split = None
    if view != 'side':
        gx = None; cols = feet.any(0); xx = np.where(cols)[0]
        gaps = [(xx[i], xx[i + 1]) for i in range(len(xx) - 1) if xx[i + 1] - xx[i] > 1]
        if gaps:
            g = max(gaps, key=lambda t: t[1] - t[0]); gx = (g[0] + g[1]) // 2; y = sole
            while y > crown and not a[y, gx]: y -= 1
            split = y + 1
    ref = chin if chin is not None else crown + 12
    sh = max(run_at(a[y], cx)[0] for y in range(ref + 3, ref + 7))
    head = (chin - crown + 1) if chin is not None else None
    return dict(crown=crown, chin=chin, split=split, sole=sole, H=sole - crown + 1, head=head,
                heads=round((sole - crown + 1) / head, 2) if head else None,
                legs=(sole + 1 - split) if split else None, leg_ratio=round((sole + 1 - split) / (sole - crown + 1), 3) if split else None,
                shoulder=int(sh), baseline_row=sole)
if __name__ == '__main__':
    out = []; ov = []
    for name, cells in C.items():
        sh = np.asarray(Image.open(O + f'assets/idle_{name}.png')).astype(float); sh[..., 3] /= 255
        for v, (x, y, w, h, ax, ay) in cells.items():
            f = sh[y:y + h, x:x + w]; m = measure(f, v, f'{name}.{v}'); m.update(id=name, view=v); out.append(m); ov.append((f, m))
    json.dump(out, open('/tmp/fem_meas.json', 'w'))
    for m in out: print(m['id'], m['view'], 'crown', m['crown'], 'chin', m['chin'], 'split', m['split'], 'sole', m['sole'], 'H', m['H'], 'head', m['head'], 'legs', m['legs'], 'sh', m['shoulder'])
    # overlay x6 with landmark lines for visual check
    S = 6; tiles = []
    for f, m in ov:
        rgba = np.dstack([f[..., :3], f[..., 3] * 255]).astype(np.uint8); t = Image.fromarray(rgba, 'RGBA')
        bg = Image.new('RGBA', t.size, (84, 108, 74, 255)); bg.alpha_composite(t); im = bg.convert('RGB').resize((t.width * S, t.height * S), Image.NEAREST)
        c = Image.new('RGB', (im.width + 8, im.height + 30), (20, 20, 20)); c.paste(im, (4, 0)); d = ImageDraw.Draw(c)
        for yy, col in ((m['chin'], (255, 0, 0)), (m['split'], (0, 200, 255))):
            if yy is not None: d.line((0, (yy + 1) * S if col == (255, 0, 0) else yy * S, c.width, (yy + 1) * S if col == (255, 0, 0) else yy * S), fill=col)
        d.text((2, im.height + 4), f"{m['id'][:8]} {m['view'][0]}", fill='white'); tiles.append(c)
    for part in range(3):
        T = tiles[part * 9:(part + 1) * 9]; W = sum(t.width for t in T); img = Image.new('RGB', (W, T[0].height)); x = 0
        for t in T: img.paste(t, (x, 0)); x += t.width
        img.save(O + f'work/meas_ov_{part}.png')
