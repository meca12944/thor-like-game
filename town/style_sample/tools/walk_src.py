"""Load 2x4 walk sheets (src/fem_walk/<name>_<view>.jpg) -> 8 RGBA float frames; auto landmarks + overlay check."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import *
from PIL import Image, ImageDraw
S = '/workspace/town-demo/style_sample/'
def load_grid(path, rows=2, per=4):
    rgb, fg = keyed(path)
    r = fg.any(1); ys = np.where(r)[0]
    bands = np.split(ys, np.where(np.diff(ys) > 8)[0] + 1)
    bands = [b for b in bands if len(b) > 40]
    assert len(bands) == rows, (path, [len(b) for b in bands])
    out = []
    for b in bands:
        sub = np.zeros_like(fg); sub[b[0]:b[-1] + 1] = fg[b[0]:b[-1] + 1]
        for sg in split_frames(sub, per):
            if sg[0] == 'ids': lab = sg[2]; m = np.isin(lab, sg[1]) & sub
            else: a, c = sg; m = np.zeros_like(fg); m[:, a:c] = sub[:, a:c]
            yy, xx = np.where(m); y0, y1, x0, x1 = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
            f = np.zeros((y1 - y0, x1 - x0, 4), np.float32); f[..., :3] = rgb[y0:y1, x0:x1]; f[..., 3] = m[y0:y1, x0:x1]
            out.append(f)
    return out
def auto(f, view):
    m = body(f); H0 = f.shape[0]; c, s = crown_sole(m, minrun=max(8, H0 // 20))
    ch = chin_auto(f, m, c, s) if view != 'back' else None
    sp = split_auto(m, c, s) if view != 'side' else None
    return c, ch, sp, s
if __name__ == '__main__':
    names = sys.argv[1].split(','); view = sys.argv[2]; tiles = []; res = {}
    for n in names:
        fr = load_grid(S + f'src/fem_walk/{n}_{view}.jpg'); lm = [auto(f, view) for f in fr]; res[n] = lm
        print(n, [f.shape[:2] for f in fr][:2], lm)
        for i in (0, 4):
            f = fr[i]; im = Image.fromarray(np.dstack([f[..., :3] * f[..., 3:] + 60 * (1 - f[..., 3:]), ]).astype(np.uint8)).convert('RGB')
            k = 2; im = im.resize((im.width * k, im.height * k), Image.NEAREST); d = ImageDraw.Draw(im)
            c, ch, sp, s = lm[i]
            for y, col in ((c, 'yellow'), (ch, 'red'), (sp, 'cyan'), (s, 'lime')):
                if y is not None: d.line([(0, y * k), (im.width, y * k)], fill=col)
            d.text((2, 2), f'{n}{i}', fill='white'); tiles.append(im)
    W = sum(t.width + 4 for t in tiles); Hh = max(t.height for t in tiles)
    out = Image.new('RGB', (W, Hh), 'black'); x = 0
    for t in tiles: out.paste(t, (x, 0)); x += t.width + 4
    p = S + f'work/walk_ov_{view}_{len(names)}.png'; out.save(p); print(p, out.size)
    json.dump({k: v for k, v in res.items()}, open(S + f'work/walk_auto_{view}.json', 'w'))
