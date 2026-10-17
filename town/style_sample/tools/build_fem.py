"""Build hero + 8 women (front/side/back idle) on the hero FRONT idle landmarks; measure; CSV + sheets."""
import sys, os, json, csv, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import *
from chars import CH, V
# source landmarks (crown, chin, split, sole) read on magnified rulers (work/r2_*.png, r3_split.png);
# None = derived (back chin from front fraction, side split from front fraction)
SRC = {
 'hero':     {'front': (1, 92, 248, 388), 'side': (0, 92, None, 388), 'back': (0, None, 248, 386)},
 'g_tool':   {'front': (1, 117, 358, 581), 'side': (0, 116, None, 575), 'back': (3, None, 355, 576)},
 'a_tailor': {'front': (2, 128, 362, 604), 'side': (4, 127, None, 605), 'back': (3, None, 355, 598)},
 'h_mystic': {'front': (0, 110, 325, 557), 'side': (1, 107, None, 551), 'back': (1, None, 324, 553)},
 'g_dancer': {'front': (3, 112, 385, 625), 'side': (2, 110, None, 618), 'back': (2, None, 385, 619)},
 'f_diver':  {'front': (3, 108, 367, 608), 'side': (3, 103, None, 600), 'back': (3, None, 376, 598)},
 'e_tailor': {'front': (2, 113, 359, 656), 'side': (0, 112, None, 651), 'back': (0, None, 357, 652)},
 'c_priest': {'front': (0, 113, 358, 631), 'side': (1, 110, None, 627), 'back': (1, None, 363, 628)},
 'd_yuna':   {'front': (1, 118, 369, 642), 'side': (1, 114, None, 634), 'back': (0, None, 369, 635)},
}
NAMES = {'hero': '주인공', 'g_tool': '사프란 (샘플 NPC)', 'a_tailor': '나비', 'h_mystic': '운', 'g_dancer': '방울', 'f_diver': '숨비', 'e_tailor': '루비', 'c_priest': '설화', 'd_yuna': '유나 (현대복)'}
# target = hero FRONT idle, final px (rows): crown 0 | chin 13 | split 36 | sole bottom edge 56
T = dict(H=56, chin=13, split=36)
OUT = '/workspace/town-demo/style_sample/'
def src_lm(name, v):
    c0, c1, c2, c3 = SRC[name][v]; f0, f1, f2, f3 = SRC[name]['front']; k = (c3 - c0) / (f3 - f0)
    if c1 is None: c1 = c0 + (f1 - f0) * k
    if c2 is None: c2 = c0 + (f2 - f0) * k
    return (c0, c1, c2, c3 + 1)
PH = {}
def gap_top(a):
    rows = np.where(a.sum(1) >= 2)[0]; sole = rows[-1]; feet = a[sole - 4:sole + 1]; xx = np.where(feet.any(0))[0]
    gaps = [(xx[i], xx[i + 1]) for i in range(len(xx) - 1) if xx[i + 1] - xx[i] > 1]
    if not gaps: return None
    g = max(gaps, key=lambda t: t[1] - t[0]); gx = (g[0] + g[1]) // 2; y = sole
    while y > 0 and not a[y, gx]: y -= 1
    return y + 1
def build():
    res = {}
    for name, p in CH:
        fr = dict(zip(V, load_frames(p, 3))); hi = []
        for v in V:
            s = src_lm(name, v); d = (0, T['chin'] * SS, T['split'] * SS, T['H'] * SS)
            f = fr[v]; m = f[..., 3] > .5; hc = np.where(m[int(s[0]):int(s[1])])[1].mean()
            # crop vertically to the crown..sole span first so dst row 0 == crown edge
            best = None
            for ph in range(SS):   # horizontal sampling phase: keep the leg gap open at the split row
                lo = to_final(remap(f, s, d, T['H'] * SS, head_cx=hc, phase=ph))
                sp = gap_top(lo[..., 3] > 0) if v != 'side' else T['split']
                sc = abs((sp if sp is not None else 99) - T['split'])
                if best is None or sc < best[0]: best = (sc, lo, ph)
                if sc == 0: break
            hi.append(best[1]); PH[(name, v)] = best[2]
        fin = finish(hi, 40 if name == 'hero' else 44)
        res[name] = {v: trim(f) for v, f in zip(V, fin)}
    return res
def save(res):
    meta = {}
    for name, d in res.items():
        W = sum(f.shape[1] + 4 for f in d.values()); Hh = max(f.shape[0] for f in d.values())
        sh = np.zeros((Hh, W, 4), np.uint8); x = 0; cells = {}
        for v, f in d.items():
            h, w = f.shape[:2]; sh[Hh - h:, x:x + w, :3] = f[..., :3]; sh[Hh - h:, x:x + w, 3] = f[..., 3] * 255
            cells[v] = [x, Hh - h, w, h, w // 2, h - 1]; x += w + 4
        Image.fromarray(sh, 'RGBA').save(OUT + f'assets/idle_{name}.png'); meta[name] = cells
    json.dump(meta, open(OUT + 'assets/idle_cells.json', 'w'), indent=0)
if __name__ == '__main__':
    r = build(); save(r)
    import pickle; pickle.dump(r, open('/tmp/fem_res.pkl', 'wb'))
    for n, d in r.items(): print(n, {v: f.shape[:2] for v, f in d.items()})
    print('phase', PH)
