#!/usr/bin/env python3
"""v2: slash-direction variants (가로 / 세로 / X자) for all 6 dark trail styles.
Reuses ../make.py (v1, read-only: its source is loaded and patched in memory, the file is not modified).
Run: python3 make_dirs.py
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(HERE, '..', 'make.py')
src = open(V1, encoding='utf-8').read()
src = src.replace("if __name__ == '__main__':\n    main()", "")
src = src.replace("STYLES = [Ashen(), Abyss(), BloodInk(), Steel(), Wraith(), Gilt()]", "")
PATCH = [
    # angle unwrap around the arc mid-angle (arcs may cross +-180)
    ("    s = (th - a['a0']) / (a['a1'] - a['a0'])\n",
     "    mid = (a['a0'] + a['a1']) / 2; th = mid + np.mod(th - mid + 180, 360) - 180\n    s = (th - a['a0']) / (a['a1'] - a['a0'])\n"),
    # per-arc fan inner radius / afterimage start radius
    ("    if F['head'] is None or F['fade'] >= 0.7: return\n    v, cut = visible(G, F); r = G['r']\n",
     "    if F['head'] is None or F['fade'] >= 0.7: return\n    r0 = G['a'].get('fan_r0', r0)\n    v, cut = visible(G, F); r = G['r']\n"),
    ("p0, p1 = pt(k, s, R * 0.30), pt(k, s, R - 5)", "p0, p1 = pt(k, s, R * ARCS[k].get('ai_r0', 0.30)), pt(k, s, R - 5)"),
    # particles: any track length
    ("born = next((j for j in range(1, 8) if", "born = next((j for j in range(len(FRAMES)) if"),
    # hold frames: no speed lines / sparkle / afterimages
    ("def afterimages(k, F, st, back):\n    if F['head'] is None or F['fade'] > 0: return",
     "def afterimages(k, F, st, back):\n    if F['head'] is None or F['fade'] > 0 or F.get('hold'): return"),
    ("def speedlines(k, F, st, L):\n    if F['head'] is None or F['fade'] > 0: return",
     "def speedlines(k, F, st, L):\n    if F['head'] is None or F['fade'] > 0 or F.get('hold'): return"),
    ("def sparkle(k, F, st, L):\n    if F['head'] is None or F['fade'] > 0: return",
     "def sparkle(k, F, st, L):\n    if F['head'] is None or F['fade'] > 0 or F.get('hold'): return"),
]
for a, b in PATCH:
    assert a in src, a[:60]
    src = src.replace(a, b)
mk = {'__file__': V1, '__name__': 'v1make'}
exec(compile(src, V1, 'exec'), mk)
N, R, Layer, hx, XX, YY = mk['N'], mk['R'], mk['Layer'], mk['hx'], mk['XX'], mk['YY']

# ---------------------------------------------------------------- arcs
def chord_arc(p0, p1, bulge_sign, sq=0.36, extra=None):
    """near-straight diagonal slash p0 -> p1: an R=70 arc whose bulge is flattened (squash along the bulge axis).
    q-space: chord along qx, bulge along +qy (theta = 90), arc theta 90+a -> 90-a."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy); al = math.degrees(math.asin(min(L / 2 / R, 1)))
    rot = math.degrees(math.atan2(dy, dx)); a0, a1 = 90 + al, 90 - al
    if bulge_sign < 0: rot += 180; a0, a1 = 90 - al, 90 + al
    t = math.radians(rot); bx, by = -math.sin(t), math.cos(t)          # bulge direction
    off = R * math.cos(math.radians(al)) * sq
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    a = dict(c=(mx - bx * off, my - by * off), R=R, sq=sq, rot=rot, a0=a0, a1=a1)
    a.update(extra or {}); return a

XE = (158, 116); XF = (112, 116); HC = 54   # chord centres; both slashes bulge clockwise (pinwheel), cross lands ~(172,116) east / (128,116) front
XOPT = dict(fan_r0=0.55, ai_r0=0.45, blade_r0=0.40)
ARCS = {
    'H':  dict(c=(128, 128), R=R, sq=0.55, rot=0.0, a0=-70.0, a1=70.0),                       # 가로 140
    'V':  dict(c=(140, 120), R=R, sq=0.50, rot=90.0, a0=172.0, a1=352.0, fan_r0=0.22),        # 세로 180, tall
    'X1': chord_arc((XE[0] - 30, XE[1] - HC), (XE[0] + 30, XE[1] + HC), -1, extra=XOPT),      # TL -> BR
    'X2': chord_arc((XE[0] + 30, XE[1] - HC), (XE[0] - 30, XE[1] + HC), -1, extra=XOPT),      # TR -> BL
    'F1': chord_arc((XF[0] - 34, XF[1] - HC), (XF[0] + 34, XF[1] + HC), -1, extra=XOPT),      # front view
    'F2': chord_arc((XF[0] + 34, XF[1] - HC), (XF[0] - 34, XF[1] + HC), -1, extra=XOPT),
}
mk['ARCS'].clear(); mk['ARCS'].update(ARCS); mk['GEO'].clear()
BEHIND = {'V': (0.22, 96)}          # wind-up part of the overhead cleave passes behind the head

# ---------------------------------------------------------------- timelines
def F(head, tail=0.0, fade=0.0, blade=None, hold=False, off=False):
    return dict(head=head, tail=tail, fade=fade, blade=(head if blade is None else blade), hold=hold, off=off)
OFF = F(None, off=True)
SWING = [F(None, blade=-0.06), F(0.35), F(0.72), F(1.0), F(1.0, .22, .25, 1.04), F(1.0, .48, .5, 1.06),
         F(1.0, .72, .75, 1.07), F(1.0, .96, .95, 1.07)]
SWING_D = [100, 33, 33, 33, 50, 50, 50, 150]
HOLD = lambda: F(1.0, 0, 0.02, 1.0, hold=True)
X1T = [F(None, blade=-0.06), F(0.45), F(1.0), HOLD(), HOLD(), HOLD(), HOLD(), HOLD(),
       F(1.0, .2, .3, 1.0), F(1.0, .45, .55, 1.0), F(1.0, .7, .8, 1.0), F(1.0, .95, .95, 1.0)]
X2T = [OFF, OFF, OFF, F(None, blade=-0.06), F(0.5), F(1.0), HOLD(), HOLD(),
       F(1.0, .2, .3, 1.0), F(1.0, .45, .55, 1.0), F(1.0, .7, .8, 1.0), F(1.0, .95, .95, 1.0)]
X_D = [100, 33, 33, 50, 33, 33, 50, 117, 50, 50, 50, 150]     # 2nd slash starts 116 ms after the 1st
FLASH = {5: 3, 6: 2, 7: 1}                                      # cross-point burst size per X frame
for t in X2T: t['blade'] = t['blade'] if t['blade'] is not None else None
for t in X1T[3:]: t['blade'] = None if not t.get('hold') and t['fade'] > 0 else t['blade']
for t in X1T[3:]: t['blade'] = None                             # the blade is now doing slash 2
for t in X2T[8:]: t['blade'] = None

def NOBLADE(tr): return [dict(t, noblade=True) for t in tr]
SEQS = [  # name, label, hero, tracks [(arc, track)], delays, flash arcs
    ('H', '가로 베기', 'east', [('H', SWING)], SWING_D, None),
    ('V', '세로 베기', 'east', [('V', SWING)], SWING_D, None),
    ('X', 'X자 베기', 'east', [('X1', X1T), ('X2', X2T)], X_D, ('X1', 'X2')),
    ('XF', 'X자 (정면)', 'south', [('F1', NOBLADE(X1T)), ('F2', NOBLADE(X2T))], X_D, ('F1', 'F2')),   # front: sprite keeps its own sword, no ghost blade
]

# ---------------------------------------------------------------- per-style flash colours (bright, mid, dark)
FLASHC = {1: ('bone_h', 'emb_h', 'emb'), 2: ('shard_h', 'rim_h', 'rim'), 3: ('sheen', 'body', 'edge'),
          4: ('glint', 'hi', 'body'), 5: ('core', 'core_g', 'smoke_l'), 6: ('g_tip', 'g_h', 'emb')}

def cross_point(k1, k2):
    best = None
    for s1 in np.linspace(0, 1, 201):
        p = mk['pt'](k1, s1, R - 3)
        for s2 in np.linspace(0, 1, 201):
            q = mk['pt'](k2, s2, R - 3); d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
            if best is None or d < best[0]: best = (d, (p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    return best[1], best[2]
CROSS = {('X1', 'X2'): cross_point('X1', 'X2'), ('F1', 'F2'): cross_point('F1', 'F2')}

def burst(L, st, x, y, size):
    P = st.pal; cb, cm, cd = (P[c] for c in FLASHC[st.n])
    if st.n == 2: cb, cm, cd = P['shard_h'], P['rim_h'], P['rim']
    ray = {3: 11, 2: 7, 1: 3}[size]
    for dx, dy, ln in ((1, 0, ray), (-1, 0, ray), (0, 1, ray), (0, -1, ray), (1, 1, ray * 0.6), (-1, 1, ray * 0.6), (1, -1, ray * 0.6), (-1, -1, ray * 0.6)):
        n = int(ln)
        for i in range(n + 1):
            c = cb if i < n * 0.4 else cm if i < n * 0.75 else cd
            L.px(x + dx * i, y + dy * i, c)
    if size >= 2:   # ring
        rr = {3: 5.5, 2: 8.5}[size]; ring = np.abs(np.hypot(XX - x, YY - y) - rr) < 0.55
        L.paint(ring & ~L.mask(), cd if size == 2 else cm)
    if size == 3:
        core = np.hypot(XX - x, YY - y) <= 2.3
        L.paint(core, P['void'] if st.n == 2 else cb)          # abyss: a black pinhole at the cross
        if st.n == 2: L.paint(mk['edge_in'](core), cb)

# ---------------------------------------------------------------- render
GROUND = mk['GROUND']
HEROES = {'east': mk['HSPR']}
sh = np.array(Image.open(os.path.join(HERE, '..', '..', 'dark_v3prop', 'south.png')).convert('RGBA'))
HS = Layer(); HS.a = sh; HEROES['south'] = HS

def draw_blade(k, Fr, L, behind):
    s = Fr['blade']
    if s is None or Fr.get('noblade'): return
    a = ARCS[k]; r0 = a.get('blade_r0', 0.26); pt = mk['pt']
    p0 = pt(k, s, R * r0); p1 = pt(k, s, R - 6); B = BLADE = mk['BLADE']
    Bl = Layer(); Bl.line(p0, p1, B['m'], 2); Bl.line(p0, pt(k, s, R * r0 + 6), B['d'], 2)
    Bl.px(*p1, B['h']); Bl.px(*pt(k, s, R - 9), B['h']); Bl.outline(B['o'], diag=False)
    (behind if p1[1] < a['c'][1] - 6 and k in ('H',) else L).over(Bl)

def render(st, seq, fi, transparent=False):
    name, _, hero, tracks, delays, fl = seq
    times = list(np.cumsum([0] + delays[:-1]) / 1000.0)
    back, front = Layer(), Layer()
    for k, tr in tracks:
        Fr = tr[fi]
        if Fr.get('off'): continue
        mk['FRAMES'][:] = tr; mk['TIMES'][:] = times
        b2, f2 = Layer(), Layer()
        st.render(k, fi, b2, f2)
        if k in BEHIND:
            s0, ymax = BEHIND[k]; mv = (f2.a[..., 3] > 0) & (mk['geo'](k)['s'] < s0) & (YY < ymax)
            b2.a[mv] = f2.a[mv]; f2.a[mv] = 0
        draw_blade(k, Fr, f2, b2)
        back.over(b2); front.over(f2)
    if fl and fi in FLASH:
        x, y = CROSS[fl]; burst(front, st, x, y, FLASH[fi])
    if transparent:
        o = Layer(); o.over(back); o.over(front); return o.a
    out = Layer(); out.a = GROUND.a.copy(); out.over(back); out.over(HEROES[hero]); out.over(front)
    return out.a

STYLES = [mk[c]() for c in ('Ashen', 'Abyss', 'BloodInk', 'Steel', 'Wraith', 'Gilt')]
crop, save_gif, font = mk['crop'], mk['save_gif'], mk['font']

def main():
    R_ = {}
    for st in STYLES:
        for si, seq in enumerate(SEQS):
            for fi in range(len(seq[4])): R_[(st.n, si, fi)] = render(st, seq, fi)
    allseq = [(si, fi) for si, seq in enumerate(SEQS) for fi in range(len(seq[4]))]
    dl = []
    for si, seq in enumerate(SEQS): dl += list(seq[4])
    dl[-1] = 400
    lab = {'H': '가로', 'V': '세로', 'X': 'X자', 'XF': 'X자 정면'}
    info = {}
    f1 = font(20); f2 = font(13, False); fs = font(16)
    for st in STYLES:
        frs = []
        for si, fi in allseq:
            im = crop(R_[(st.n, si, fi)], 3); d = ImageDraw.Draw(im); d.fontmode = '1'
            d.text((8, 6), '%s %s' % (st.ko, lab[SEQS[si][0]]), font=fs, fill=(150, 144, 132)); frs.append(im)
        p = os.path.join(HERE, 'style_%d_%s_dirs.gif' % (st.n, st.key)); info[st.n] = save_gif(frs, dl, p)
        # native transparent sheet: rows H, V, X(east), X(front); 12 columns
        sheet = Image.new('RGBA', (N * 12, N * 4))
        for si, seq in enumerate(SEQS):
            for fi in range(len(seq[4])):
                sheet.paste(Image.fromarray(render(st, seq, fi, True), 'RGBA'), (fi * N, si * N))
        sheet.save(os.path.join(HERE, 'style_%d_%s_dirs_sheet_native.png' % (st.n, st.key)))
    # combined 3x2 grid
    sc = 2; cw = (mk['CROP'][2] - mk['CROP'][0]) * sc; ch = (mk['CROP'][3] - mk['CROP'][1]) * sc; lb = 34
    allf = []
    for si, fi in allseq:
        im = Image.new('RGB', (cw * 3, (ch + lb) * 2), hx('#0c0d10')[:3]); d = ImageDraw.Draw(im); d.fontmode = '1'
        for i, st in enumerate(STYLES):
            x, y = (i % 3) * cw, (i // 3) * (ch + lb)
            im.paste(crop(R_[(st.n, si, fi)], sc), (x, y + lb))
            t = '%d. %s' % (st.n, st.ko); d.text((x + 10, y + 6), t, font=f1, fill=(214, 206, 188))
            d.text((x + 20 + d.textlength(t, font=f1), y + 12), st.en, font=f2, fill=(130, 126, 118))
            d.text((x + cw - 90, y + 8), SEQS[si][1], font=font(16), fill=(170, 150, 110))
        allf.append(im)
    info['all'] = save_gif(allf, dl, os.path.join(HERE, 'slash_dirs_all.gif'))
    # board: per row  가로(swipe, full) | 세로(swipe, full) | X(1st slash, cross burst, full X) | X front (full)
    COLS = [(0, 2, '가로 · 휘두름'), (0, 3, '가로 · 완성'), (1, 2, '세로 · 휘두름'), (1, 3, '세로 · 완성'),
            (2, 2, 'X자 · 1타'), (2, 5, 'X자 · 교차 섬광'), (2, 7, 'X자 · 완성 (최대)'), (3, 7, 'X자 · 정면 완성')]
    sc = 2; labw = 330; head = 74; rowh = ch + 30; gaps = {2: 24, 4: 24, 7: 24}
    xs = []; x = labw
    for i in range(len(COLS)):
        x += gaps.get(i, 0); xs.append(x); x += cw
    W = x + 16
    board = Image.new('RGB', (W, head + rowh * 6 + 10), hx('#0c0d10')[:3]); d = ImageDraw.Draw(board)
    d.text((20, 14), '사멸의 궤적 — 검흔 방향 베리에이션 v2 (가로 · 세로 · X자) — 6 styles × 3 directions', font=font(26), fill=(222, 214, 196))
    for i, (_, _, nm) in enumerate(COLS): d.text((xs[i] + 6, head - 24), nm, font=font(17), fill=(170, 160, 130))
    fL = font(30); fE = font(16); fM = font(13, False)
    for r, st in enumerate(STYLES):
        y = head + r * rowh
        d.rectangle([8, y, W - 8, y + rowh - 6], outline=(40, 42, 50))
        d.text((22, y + 18), '%d. %s' % (st.n, st.ko), font=fL, fill=(226, 218, 200))
        d.text((24, y + 62), st.en, font=fE, fill=(150, 144, 132))
        cols = [c for kk, c in st.pal.items() if not kk.startswith('fan')][:12]
        for j, c in enumerate(cols):
            xx = 24 + (j % 6) * 46; yy = y + 100 + (j // 6) * 54
            d.rectangle([xx, yy, xx + 38, yy + 30], fill=hx(c)[:3], outline=(70, 70, 76))
            d.text((xx, yy + 33), c, font=font(11, False), fill=(120, 116, 110))
        for i, (si, fi, _) in enumerate(COLS): board.paste(crop(R_[(st.n, si, fi)], sc), (xs[i], y + 12))
    board.save(os.path.join(HERE, 'slash_dirs_board.png'))
    print('unique colours:', info)

if __name__ == '__main__':
    main()
