"""Women: idle (4-frame breathing) + walk (8 frames) x 4 directions on the hero FRONT idle landmarks.
Per frame: crown/sole detected; chin/split from manually read rows on frame 0 of each sheet (WLM), scaled per frame.
dst rows (final px, 1 px top margin M): crown M+b | chin 13+M+b | split 36+M+b | sole 57  (b = walk bob)."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from proportions import *
from build_fem import SRC, src_lm, gap_top, NAMES
from walk_src import load_grid
from chars import CH
S = '/workspace/town-demo/style_sample/'
M = 1; TH = 56; TCH = 13; TSP = 36; HH = TH + M; CW = 64; OUTP = S + 'assets/walk_{}.png'
def set_size(h, cw):
    global TH, TCH, TSP, HH, CW
    TH = h; TCH = round(h * 13 / 56); TSP = round(h * 36 / 56); HH = h + M; CW = cw
# manual (chin, split) rows on walk frame 0, read on work/rw_* rulers (None = derive from front fractions)
WLM = {
 'g_tool':   {'front': (70, 196)}, 'a_tailor': {'front': (76, 178)}, 'h_mystic': {'front': (72, 180)},
 'g_dancer': {'front': (75, 188)}, 'f_diver':  {'front': (75, 190)}, 'e_tailor': {'front': (70, 172)},
 'c_priest': {'front': (78, 190)}, 'd_yuna':   {'front': (70, 170)},
}
BOB = [0, 1, 0, -1, 0, 1, 0, -1]
BREATH = [0, 0, 1, 1]
WK = {}
def head_cx(f, c, ch):
    m = body(f); y = int(c + .6 * (ch - c)); xx = np.where(m[y])[0]
    runs = np.split(xx, np.where(np.diff(xx) > 1)[0] + 1); r = max(runs, key=len); return (r[0] + r[-1] + 1) / 2
def render(f, s, b, ph=0, wk=1.0):
    d = (M + b, (TCH + M + b), (TSP + M + b), HH)
    ws = (d[3] - d[0]) * SS / (s[3] - s[0]) * wk
    hi = remap(f, s, tuple(v * SS for v in d), HH * SS, head_cx=head_cx(f, s[0], s[1]), phase=ph, wscale=ws)
    lo = to_final(hi); W = lo.shape[1]; cx = W // 2
    out = np.zeros((HH, CW, 4), np.float32); a = max(0, cx - CW // 2); o = CW // 2 - (cx - a)
    seg = lo[:, a:a + CW - o]; out[:, o:o + seg.shape[1]] = seg; return out
def walk_lm(name, view, fr):
    c0, s0 = crown_sole(body(fr[0]), minrun=max(8, fr[0].shape[0] // 20))
    w = WLM[name].get(view)
    fc, fs = crown_sole(body(load_grid(S + f'src/fem_walk/{name}_front.jpg')[0]), minrun=15)
    fch, fsp = WLM[name]['front']
    k = (s0 - c0) / (fs - fc)
    ch = w[0] if w and w[0] is not None else c0 + (fch - fc) * k
    sp = w[1] if w and w[1] is not None else c0 + (fsp - fc) * k
    out = []
    for f in fr:
        c, s = crown_sole(body(f), minrun=max(8, f.shape[0] // 20)); kk = (s - c) / (s0 - c0)
        out.append((c, c + (ch - c0) * kk, c + (sp - c0) * kk, s + 1))
    return out
def build(name, views=('front', 'side', 'back')):
    p = dict(CH)[name]; idle = dict(zip(['front', 'side', 'back'], load_frames(p, 3)))
    seq = {}; flat = []
    for v in views:
        s = src_lm(name, v); f = idle[v]; best = None
        for ph in range(SS):
            fr0 = render(f, s, 0, ph); sp = gap_top(fr0[..., 3] > 0) if v != 'side' else TSP + M
            sc = abs((sp if sp is not None else 99) - (TSP + M))
            if best is None or sc < best[0]: best = (sc, ph)
            if sc == 0: break
        ids = [render(f, s, b, best[1]) for b in BREATH]
        wp = S + f'src/fem_walk/{name}_{v}.jpg'
        if os.path.exists(wp):
            if v == 'front':
                fr = load_grid(wp); keys = list(range(8))
            else:
                fr = load_grid(wp, 1, 4); keys = [0, 0, 1, 1, 2, 2, 3, 3]
            lms = walk_lm(name, v, fr)
            # width: match the idle sprite of the same view on the head band (stable across poses; arms swing out of it)
            def wid(g):
                a = g[..., 3] > 0; r = []
                for y in range(M + TCH // 3, M + TCH - 1):
                    xx = np.where(a[y])[0]
                    if not len(xx): continue
                    runs = np.split(xx, np.where(np.diff(xx) > 1)[0] + 1); c = CW // 2
                    run = min(runs, key=lambda q: 0 if q[0] <= c <= q[-1] else min(abs(q[0] - c), abs(q[-1] - c)))
                    r.append(len(run))   # contiguous run under the head centre (ignores staff / spear shafts)
                return np.median(r) if r else 1
            wk = float(np.clip(wid(ids[0]) / wid(render(fr[0], lms[0], 0)), .85, 1.2))
            WK[(name, v)] = round(float(wk), 3)
            ws = [render(fr[keys[i]], lms[keys[i]], BOB[i], 0, wk) for i in range(8)]
        else: ws = [ids[0]] * 8
        seq[v] = (len(flat), len(ids), len(ws)); flat += ids + ws
    fin = finish(flat, 48)
    out = {}
    for v, (a, ni, nw) in seq.items(): out[v] = dict(idle=fin[a:a + ni], walk=fin[a + ni:a + ni + nw])
    return out
def sheet(name, d):
    rows = [('down', d['front'], False), ('left', d['side'], True), ('right', d['side'], False), ('up', d['back'], False)]
    sh = np.zeros((HH * 4, CW * 12, 4), np.uint8)
    for r, (_, v, mir) in enumerate(rows):
        for c, f in enumerate(v['idle'] + v['walk']):
            g = f[:, ::-1] if mir else f
            sh[r * HH:(r + 1) * HH, c * CW:(c + 1) * CW, :3] = g[..., :3]; sh[r * HH:(r + 1) * HH, c * CW:(c + 1) * CW, 3] = g[..., 3] * 255
    Image.fromarray(sh, 'RGBA').save(OUTP.format(name))
    return dict(cw=CW, ch=HH, ax=CW // 2, ay=HH - 1, rows=['down', 'left', 'right', 'up'], idle=[0, 4], walk=[4, 8])
if __name__ == '__main__':
    names = sys.argv[1].split(','); meta = {}
    mp = S + 'assets/walk_meta.json'
    if os.path.exists(mp): meta = json.load(open(mp))
    for n in names:
        d = build(n); meta[n] = sheet(n, d); print(n, 'ok', {k[1]: v for k, v in WK.items() if k[0] == n})
    json.dump(meta, open(mp, 'w'), indent=0)
