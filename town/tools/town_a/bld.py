# [town_a] procedural front-facing 3/4 buildings (art px, A=0.6 px / world px)
import numpy as np, math
from px import *

def blotch(h, w, seed, scale=6, amt=1.0):
    r = np.random.default_rng(seed)
    small = r.random((max(2, h//scale+2), max(2, w//scale+2)))
    im = Image.fromarray((small*255).astype(np.uint8)).resize((w+scale*2, h+scale*2), Image.BICUBIC)
    return (np.asarray(im)[scale:scale+h, scale:scale+w].astype(np.float32)/255 - .5)*amt

def stone_courses(c, x0, y0, x1, y1, pal, seed, rowh=(6, 8), sw=(9, 16), mortar=None):
    R = rng(seed); mortar = mortar or dk(pal[1], .9); c.rect(x0, y0, x1, y1, mortar)
    y = y0
    while y < y1:
        h = R.randint(*rowh); x = x0 - R.randint(0, 8)
        while x < x1:
            w = R.randint(*sw); sx0, sx1 = max(x0, x+1), min(x1, x+w); sy1 = min(y1, y+h)
            if sx1 - sx0 >= 2:
                base = pal[R.choice([2, 3, 3, 3, 4])]
                c.rect(sx0, y+1, sx1, sy1, base)
                c.hline(sx0, sx1, y+1, dk(base, 1.18)); c.vline(sx0, y+1, sy1, dk(base, 1.1))
                c.hline(sx0, sx1, sy1-1, dk(base, .72)); c.vline(sx1-1, y+1, sy1, dk(base, .8))
                if R.random() < .25: c.put(R.randint(sx0+1, max(sx0+1, sx1-2)), R.randint(y+2, max(y+2, sy1-2)), dk(base, .85))
                if R.random() < .12:  # moss
                    for k in range(R.randint(2, 5)): c.put(R.randint(sx0, sx1-1), sy1-1-R.randint(0, 1), P['leaf'][R.randint(2, 4)])
            x += w
        y += h

def planks(c, x0, y0, x1, y1, pal, seed, pw=5, vertical=True):
    R = rng(seed)
    if vertical:
        x = x0
        while x < x1:
            w = pw + R.randint(-1, 1); col = pal[R.choice([2, 3, 3, 4])]
            c.rect(x, y0, min(x1, x+w), y1, col); c.vline(x, y0, y1, dk(pal[1], .9)); c.vline(x+1, y0, y1, dk(col, 1.12))
            for k in range(R.randint(0, 2)):
                yy = R.randint(y0, max(y0, y1-3)); c.rect(x+2, yy, x+3, yy+2, dk(col, .82))
            x += w
    else:
        y = y0
        while y < y1:
            h = pw + R.randint(-1, 1); col = pal[R.choice([2, 3, 3, 4])]
            c.rect(x0, y, x1, min(y1, y+h), col); c.hline(x0, x1, y, dk(pal[1], .85)); c.hline(x0, x1, y+1, dk(col, 1.12))
            y += h

def shingles(c, mask, x0, y0, y1, pal, seed, sw=9, rh=7, moss=.008):
    """fill mask (bool HxW) with horizontal shingle courses; lighter near the ridge"""
    R = rng(seed); H, W = mask.shape; tint = np.random.default_rng(seed)
    ys, xs = np.nonzero(mask)
    if len(ys) == 0: return
    span = max(1, y1 - y0)
    var = {}
    for y, x in zip(ys, xs):
        r = (y - y0) // rh; ry = (y - y0) % rh; off = (r % 2) * (sw // 2)
        k = (x - x0 + off) // sw; kx = (x - x0 + off) % sw
        t = (y - y0) / span
        idx = 4 - int(t * 2.2)
        key = (r, k)
        if key not in var: var[key] = R.choice([0, 0, 0, 0, 1, -1]) if R.random() > moss else 9
        v = var[key]
        if v == 9: col = P['leaf'][2 + (ry > 2)] if (kx + ry) % 3 else pal[max(0, idx - 1)]
        else:
            ii = max(0, min(5, idx + v))
            if ry == rh - 1: ii = max(0, ii - 2)
            elif ry == 0: ii = min(5, ii + 1)
            elif kx == 0: ii = max(0, ii - 2)
            elif kx == 1 or ry == 1: ii = min(5, ii + 1)
            elif ry >= rh - 3: ii = max(0, ii - 1)
            col = pal[ii]
        c.a[y, x] = col

def roof_hip(c, x0, x1, y0, y1, pal, seed, inset=None, ridge=True, kind='hip'):
    inset = (y1 - y0) * .55 if inset is None else inset
    if kind == 'gable': inset = 0
    pts = [(x0, y1), (x1, y1), (x1 - inset, y0), (x0 + inset, y0)]
    im = Image.new('L', (c.w, c.h), 0); ImageDraw.Draw(im).polygon(pts, fill=255); m = np.asarray(im) > 0
    shingles(c, m, x0, y0, y1, pal, seed)
    # ridge cap
    if ridge:
        c.rect(x0 + inset, y0, x1 - inset + 1, y0 + 3, pal[5]); c.hline(x0 + inset, x1 - inset + 1, y0 + 3, pal[1])
        c.hline(x0 + inset, x1 - inset + 1, y0, dk(pal[5], 1.08))
    if inset > 0:  # hip ridges along the slanted edges
        n = int(y1 - y0)
        for i in range(n):
            t = i / max(1, n); y = int(y0 + i)
            xl = int(x0 + inset - inset * t); xr = int(x1 - inset + inset * t)
            for dx, ci in ((0, 1), (1, 5), (2, 4)): c.put(xl + dx, y, pal[ci]); c.put(xr - dx, y, pal[ci])
    else:  # gable ends: bargeboards
        for x in (x0, x1 - 2):
            c.rect(x, y0, x + 2, y1, P['wood_d'][3]); c.vline(x, y0, y1, P['wood_d'][1])
    # eave fascia
    c.rect(x0, y1 - 2, x1, y1, pal[1]); c.hline(x0, x1, y1 - 1, pal[0])
    return m

def gable_front(c, gx, gw, ywt, ya, pal, wallpal, seed, T=9, E=5, window=True, timber=True):
    """front-facing gable: triangle wall + V-shaped roof strips. ywt = wall top (eave line), ya = apex y"""
    outer = [(gx - gw - E, ywt + 2), (gx + gw + E, ywt + 2), (gx, ya)]
    im = Image.new('L', (c.w, c.h), 0); ImageDraw.Draw(im).polygon(outer, fill=255); mo = np.asarray(im) > 0
    # roof strips coloured by distance from the outer slope edge, tile courses across the slope
    ys, xs = np.nonzero(mo)
    L = math.hypot(gw + E, ywt + 2 - ya); ux, uy = (gw + E) / L, (ywt + 2 - ya) / L
    for y, x in zip(ys, xs):
        side = -1 if x < gx else 1
        dxp = (x - gx) * side; dyp = y - ya
        d = dyp * ux - dxp * uy  # distance below the slope line
        along = dxp * ux + dyp * uy
        if d < 1.2: col = pal[1]
        elif d < 2.6: col = pal[5]
        else:
            ii = 3 if (int(along) // 5) % 2 == 0 else 4
            if int(along) % 5 == 0: ii = 1
            if d > T - 2: ii = max(0, ii - 1)
            col = pal[ii]
        c.a[y, x] = col
    inner = [(gx - gw, ywt + 3), (gx + gw, ywt + 3), (gx, ya + T * 1.25)]
    im = Image.new('L', (c.w, c.h), 0); ImageDraw.Draw(im).polygon(inner, fill=255); mi = np.asarray(im) > 0
    b = blotch(c.h, c.w, seed + 7, 5, 1.2)
    ys, xs = np.nonzero(mi)
    for y, x in zip(ys, xs): c.a[y, x] = wallpal[3 + (b[y, x] > .25) - (b[y, x] < -.3)]
    # shadow under the gable roof
    sh = mi & ~np.roll(mi, 3, axis=0)
    c.shade(sh, .78)
    if timber:
        tc = P['timber']
        c.rect(gx - gw + 2, ywt - 1, gx + gw - 1, ywt + 2, tc[3]); c.hline(gx - gw + 2, gx + gw - 1, ywt - 1, tc[4])
        c.rect(gx - 1, int(ya + T * 1.25), gx + 2, ywt, tc[3]); c.vline(gx - 1, int(ya + T * 1.25), ywt, tc[4])
    if window:
        wy = int(ya + (ywt - ya) * .5); ww = max(8, int(gw * .45)); wh = max(8, int((ywt - ya) * .3))
        draw_window(c, gx - ww // 2, wy, ww, wh, seed, box=False, mullion=True)

def draw_window(c, x, y, w, h, seed, box=True, shutters=None, mullion=True, arch=False, frame=None):
    R = rng(seed); tc = frame or P['timber']; g = P['glass']
    c.rect(x - 2, y - 2, x + w + 2, y + h + 2, tc[2]); c.hline(x - 2, x + w + 2, y - 2, tc[4]); c.vline(x - 2, y - 2, y + h + 2, tc[3])
    for yy in range(y, y + h):
        t = (yy - y) / max(1, h - 1); col = lerpc(g[1], g[3], t); c.hline(x, x + w, yy, col)
    for k in range(0, w + h, 1):  # diagonal reflection streak
        xx, yy = x + k - 3, y + h - 1 - k
        if x <= xx < x + w - 1 and y <= yy < y + h: c.put(xx, yy, g[5]); c.put(xx + 1, yy, g[4])
    c.put(x, y, g[0]); c.hline(x, x + w, y, g[0])
    if mullion:
        c.vline(x + w // 2, y, y + h, tc[4]); c.hline(x, x + w, y + h // 2, tc[4])
    if arch:
        for i in range(w + 4):
            dx = (i - (w + 4) / 2) / ((w + 4) / 2); top = int(y - 2 - 4 * math.sqrt(max(0, 1 - dx * dx)))
            for yy in range(top, y - 1): c.put(x - 2 + i, yy, tc[2])
    c.rect(x - 3, y + h + 1, x + w + 3, y + h + 3, P['stone'][4]); c.hline(x - 3, x + w + 3, y + h + 2, P['stone'][2])
    if shutters:
        sp = shutters; sw = max(3, w // 2 - 1)
        for sx in (x - 2 - sw, x + w + 2):
            c.rect(sx, y - 1, sx + sw, y + h + 1, sp[3]); c.vline(sx, y - 1, y + h + 1, sp[1]); c.vline(sx + sw - 1, y - 1, y + h + 1, sp[2])
            for yy in range(y + 1, y + h, 3): c.hline(sx + 1, sx + sw - 1, yy, sp[2])
    if box:
        by = y + h + 3; c.rect(x - 2, by, x + w + 2, by + 4, P['wood'][3]); c.hline(x - 2, x + w + 2, by + 3, P['wood'][1]); c.hline(x - 2, x + w + 2, by, P['wood'][4])
        fl = [hexc('#e8607e'), hexc('#f4a6c4'), hexc('#f6e27a'), hexc('#ffffff'), hexc('#b67ad8'), hexc('#ff8a4a')]
        for xx in range(x - 2, x + w + 2):
            for k in range(R.randint(1, 3)):
                c.put(xx, by - k, P['leaf'][R.randint(2, 5)])
            if R.random() < .45: c.put(xx, by - R.randint(1, 3), R.choice(fl))

def draw_door(c, x, yb, w, h, seed, style='arch', pal=None, frame='stone', steps=2, double=False):
    pal = pal or P['wood']; R = rng(seed)
    fr = P['stone'] if frame == 'stone' else P['timber']
    top = yb - h
    # frame
    c.rect(x - 3, top, x + w + 3, yb, fr[3]); c.vline(x - 3, top, yb, fr[4]); c.vline(x + w + 2, top, yb, fr[1])
    if style == 'arch':
        for i in range(-3, w + 3):
            dx = (i + .5 - w / 2) / (w / 2 + 3); a = int(round((w / 2 + 3) * .55 * math.sqrt(max(0, 1 - dx * dx))))
            for yy in range(top - a, top): c.put(x + i, yy, fr[3] if yy > top - a else fr[5])
    planks(c, x, top, x + w, yb, pal, seed, pw=4)
    if style == 'arch':
        for i in range(0, w):
            dx = (i + .5 - w / 2) / (w / 2); a = int(round((w / 2) * .55 * math.sqrt(max(0, 1 - dx * dx))))
            col = pal[3] if (i % 4) else pal[1]
            for yy in range(top - a, top): c.put(x + i, yy, col)
            c.put(x + i, top - a, pal[1])
    c.rect(x, top, x + w, top + 2, dk(pal[2], .7))
    if double: c.vline(x + w // 2, top, yb, pal[0])
    for hy in (top + 4, yb - 6):
        c.rect(x, hy, x + w, hy + 2, P['iron'][2]); c.hline(x, x + w, hy, P['iron'][4])
    hx = x + w - 4 if not double else x + w // 2 - 3
    c.rect(hx, top + h // 2, hx + 2, top + h // 2 + 3, P['gold'][4]); c.put(hx, top + h // 2, P['gold'][5])
    if double:
        c.rect(hx + 4, top + h // 2, hx + 6, top + h // 2 + 3, P['gold'][4])
    # steps
    for i in range(steps):
        sx0, sx1 = x - 4 - i * 3, x + w + 4 + i * 3; sy = yb + i * 3
        c.rect(sx0, sy, sx1, sy + 3, P['stone'][4 - i]); c.hline(sx0, sx1, sy, P['stone'][5]); c.hline(sx0, sx1, sy + 2, P['stone'][2])
    return (x, top, w, h)

def draw_awning(c, x0, x1, y, depth, cols, seed):
    sw = 6
    for xx in range(x0, x1):
        k = ((xx - x0) // sw) % 2; pal = cols[k]
        bump = 2 if ((xx - x0) % sw) in (1, 2, 3, 4) else 1
        for yy in range(y, y + depth + bump):
            t = (yy - y) / max(1, depth)
            ii = 2 + int(t * 2.5)
            col = pal[min(5, ii)]
            if yy >= y + depth + bump - 1: col = pal[1]
            c.put(xx, yy, col)
        c.put(xx, y, cols[0][1])
    c.hline(x0, x1, y, P['iron'][2])

def hang_sign(c, ax, ay, bw, bh, seed, side=1, pal=None):
    """iron bracket from the wall at (ax,ay) reaching out by side*(bw+4); board hangs below. returns board rect"""
    pal = pal or P['wood']; ir = P['iron']
    bx = ax + (4 if side > 0 else -4 - bw)
    c.rect(min(ax, ax + side * (bw + 6)), ay, max(ax, ax + side * (bw + 6)) + 1, ay + 2, ir[2]); c.hline(min(ax, ax + side * (bw + 6)), max(ax, ax + side * (bw + 6)) + 1, ay, ir[4])
    c.rect(ax - 1 if side > 0 else ax - 1, ay - 3, ax + 2, ay + 6, ir[2])
    for k in range(5): c.put(ax + side * k, ay + 2 + k, ir[3])  # brace
    for cx in (bx + 3, bx + bw - 4):
        for yy in range(ay + 2, ay + 6): c.put(cx, yy, ir[4] if yy % 2 else ir[2])
    by = ay + 6
    c.rect(bx, by, bx + bw, by + bh, pal[1]); c.rect(bx + 1, by + 1, bx + bw - 1, by + bh - 1, pal[4])
    c.rect(bx + 2, by + 2, bx + bw - 2, by + bh - 2, pal[3]); c.hline(bx + 2, bx + bw - 2, by + 2, pal[5])
    return (bx, by, bw, bh)

def chimney(c, x, ytop, ybot, w=14, seed=0):
    stone_courses(c, x, ytop, x + w, ybot, P['stone'], seed, rowh=(3, 4), sw=(4, 7))
    c.rect(x - 1, ytop - 3, x + w + 1, ytop, P['stone'][4]); c.hline(x - 1, x + w + 1, ytop - 3, P['stone'][5])
    c.rect(x + 2, ytop - 3, x + w - 2, ytop - 2, P['iron'][0])

def wall_plaster(c, x0, y0, x1, y1, pal, seed, timber=True, posts=(), braces=True, beam_mid=None):
    b = blotch(y1 - y0, x1 - x0, seed, 7, 1.4); nz = np.random.default_rng(seed).random((y1 - y0, x1 - x0))
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            v = b[yy - y0, xx - x0] + (nz[yy - y0, xx - x0] - .5) * .5
            c.a[yy, xx] = pal[3 + (v > .32) - (v < -.35)]
    if timber:
        tc = P['timber']
        def post(px_):
            c.rect(px_, y0, px_ + 3, y1, tc[3]); c.vline(px_, y0, y1, tc[4]); c.vline(px_ + 2, y0, y1, tc[2])
        for p_ in (x0, x1 - 3) + tuple(posts): post(p_)
        c.rect(x0, y0, x1, y0 + 3, tc[3]); c.hline(x0, x1, y0 + 2, tc[2])
        if beam_mid: c.rect(x0, beam_mid, x1, beam_mid + 3, tc[3]); c.hline(x0, x1, beam_mid, tc[4])
        if braces:
            xs = sorted((x0,) + tuple(posts) + (x1 - 3,))
            for i in range(len(xs) - 1):
                a_, b_ = xs[i] + 3, xs[i + 1]
                if b_ - a_ < 14: continue
                yb_ = y1 if beam_mid is None else beam_mid
                L = min(b_ - a_, yb_ - y0 - 3) * .55
                for t in range(int(L)):
                    for d in range(3):
                        c.put(a_ + t + d, yb_ - 1 - t, tc[3 if d else 4]); c.put(b_ - 1 - t - d, yb_ - 1 - t, tc[3 if d else 4])

def building(spec):
    """spec keys: W,H (wall), RH (roof), roof pal, kind hip|gable, wall plaster|stone|wood|logs, door dict, windows list,
    gables list [(gx_rel, gw, rise)], chimneys [x_rel], awning (x0,x1,y_rel,cols), sign (side,bw,bh,y_rel), extras callable."""
    S = dict(E=6, padL=0, padR=0, topPad=18, foot=10, F=10)
    S.update(spec)
    W, H, RH, E = S['W'], S['H'], S['RH'], S['E']
    padL, padR, top = S['padL'], S['padR'], S['topPad']
    cw = W + 2 * E + padL + padR; ch = top + RH + H + S['foot']
    c = Canvas(cw, ch)
    wx0 = padL + E; wx1 = wx0 + W; ywt = top + RH; yb = ywt + H
    seed = S.get('seed', 1)
    # wall
    wall = S.get('wall', 'plaster')
    wp = P[S.get('wallpal', 'plaster')]
    F = S['F']
    if wall == 'plaster': wall_plaster(c, wx0, ywt, wx1, yb - F, wp, seed, True, S.get('posts', ()), S.get('braces', True), S.get('beam_mid'))
    elif wall == 'plaster_plain': wall_plaster(c, wx0, ywt, wx1, yb - F, wp, seed, False)
    elif wall == 'stone': stone_courses(c, wx0, ywt, wx1, yb - F, P[S.get('stonepal', 'stone')], seed, rowh=(6, 8), sw=(9, 15))
    elif wall == 'wood': planks(c, wx0, ywt, wx1, yb - F, P[S.get('woodpal', 'wood')], seed, pw=5)
    elif wall == 'logs':
        y = ywt
        while y < yb - F:
            for yy in range(y, min(yb - F, y + 6)):
                k = yy - y; col = P['wood'][[1, 3, 4, 4, 3, 2][k]]; c.hline(wx0, wx1, yy, col)
            c.put(wx0, y + 2, P['wood'][5]); c.put(wx1 - 1, y + 2, P['wood'][5]); y += 6
    # foundation
    stone_courses(c, wx0 - 1, yb - F, wx1 + 1, yb, P['stone'], seed + 3, rowh=(4, 6), sw=(7, 12))
    c.hline(wx0 - 1, wx1 + 1, yb - 1, P['stone'][1])
    meta = dict(doors=[], signs=[], wall=(wx0, ywt, wx1, yb), base=yb, w=cw, h=ch)
    # roof
    rk = S.get('kind', 'hip'); rp = P[S.get('roof', 'roof_red')]
    rx0, rx1 = wx0 - E, wx1 + E; ry0 = top; ry1 = ywt + 2
    roof_hip(c, rx0, rx1, ry0, ry1, rp, seed + 11, inset=S.get('inset'), kind=rk)
    # eave shadow on the wall
    m = np.zeros((ch, cw), bool); m[ry1:ry1 + 4, wx0:wx1] = True; c.shade(m, .72); m[:] = False; m[ry1 + 4:ry1 + 6, wx0:wx1] = True; c.shade(m, .88)
    for (gxr, gw, rise) in S.get('gables', []):
        gable_front(c, wx0 + gxr, gw, ywt, ywt - rise, rp, wp, seed + 23 + gxr, window=S.get('gable_window', True))
    for cxr in S.get('chimneys', []):
        cy = top + int(RH * .25)
        chimney(c, wx0 + cxr, cy - 22, cy + 12, seed=seed + cxr)
    for i, wd in enumerate(S.get('windows', [])):
        x, y, w, h = wd[:4]; o = wd[4] if len(wd) > 4 else {}
        draw_window(c, wx0 + x, ywt + y, w, h, seed + 40 + i, box=o.get('box', True), shutters=P[o['sh']] if 'sh' in o else None, arch=o.get('arch', False))
    if 'awning' in S:
        a0, a1, ay, cols = S['awning']
        draw_awning(c, wx0 + a0, wx0 + a1, ywt + ay, 10, [P[cols[0]], P[cols[1]]], seed)
        m[:] = False; m[ywt + ay + 11:ywt + ay + 14, wx0 + a0:wx0 + a1] = True; c.shade(m, .7)
    for d in S.get('doors', [d for d in [S.get('door')] if d]):
        r = draw_door(c, wx0 + d['x'], yb, d.get('w', 16), d.get('h', 30), seed + 5, d.get('style', 'arch'), P[d.get('pal', 'wood')], d.get('frame', 'stone'), d.get('steps', 2), d.get('double', False))
        meta['doors'].append(dict(id=d.get('id'), x=r[0] + r[2] / 2, y=yb, w=r[2]))
    if 'sign' in S:
        side, bw, bh, syr, sxr = S['sign']
        ax = (wx1 if side > 0 else wx0) if sxr is None else wx0 + sxr
        r = hang_sign(c, ax, ywt + syr, bw, bh, seed, side)
        meta['signs'].append(r)
    if 'extras' in S: S['extras'](c, dict(wx0=wx0, wx1=wx1, ywt=ywt, yb=yb, top=top, seed=seed, meta=meta))
    c.outline()
    # ground-contact AO
    m[:] = False; m[yb - 2:yb, wx0 - 1:wx1 + 1] = True; c.shade(m, .7)
    return c, meta
