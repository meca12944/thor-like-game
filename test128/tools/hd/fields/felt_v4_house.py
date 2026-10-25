"""felt v5 (build_felt_v4): parametric village buildings drawn in code — timber/stone/plank faces, gable/front-gable/thatch roofs,
burn damage, windows, doors (known rect for the engine's door-leaf animation), chimneys, hanging signs. No external art."""
import math, random
import numpy as np
from inkart import Pic, PAL, C, tone, mix, masonry, crack, moss_post, soot_post, ivy, fbm
T = 32
def _roof_courses(p, poly, y0, y1, xl, xr, col, r, kind='slate', step=7):
    p.fill(poly, col, wob=.6, line=1.5)
    y = y1 - 3; row = 0
    while y > y0 + 2:
        if kind == 'thatch':
            for x in np.arange(xl + r.uniform(0, 3), xr, 2.6):
                if r.random() < .55: p.stroke([(x, y), (x + r.uniform(-1, 1), y - step * r.uniform(.8, 1.4))], .55, 120, .2)
            p.stroke([(xl + 2, y + 1), (xr - 2, y + 1)], .6, 90, 1.2)
        else:
            p.stroke([(xl + 2, y), (xr - 2, y)], .75, 150, .7)
            x = xl + (row % 2) * step * .8 + r.uniform(0, 2)
            while x < xr - 3:
                if r.random() < .8: p.stroke([(x, y), (x, y - step + 1)], .6, 120, .2)
                if r.random() < .22:
                    f = r.uniform(.82, 1.12); p.fill([(x + .6, y - step + 1.2), (x + step * 1.6 - .6, y - step + 1.2), (x + step * 1.6 - .6, y - .6), (x + .6, y - .6)], tone(col, f), wob=.2, line=0)
                x += step * 1.6
        y -= step; row += 1
def window(p, x, y, w, h, kind='lit', r=None, frame='wood_d'):
    r = r or random.Random(0)
    p.fill([(x - 3, y - 3), (x + w + 3, y - 3), (x + w + 3, y + h + 3), (x - 3, y + h + 3)], frame, wob=.3, line=1.1)
    if kind == 'lit':
        p.rect(x, y, x + w, y + h * .45, 'void', wob=.2, line=.8); p.rect(x, y + h * .45, x + w, y + h, mix('void', 'glow', .55), wob=.2, line=.8)
    else: p.rect(x, y, x + w, y + h, 'void', wob=.2, line=.8)
    p.stroke([(x + w / 2, y), (x + w / 2, y + h)], 1.0, 220, .2); p.stroke([(x, y + h / 2), (x + w, y + h / 2)], 1.0, 220, .2)
    if kind == 'board':
        for k in range(2):
            yy = y + h * (.3 + .4 * k); p.fill([(x - 4, yy - 2.5 + k * 3), (x + w + 4, yy - 3.5 - k * 2), (x + w + 4, yy + 1.5 - k * 2), (x - 4, yy + 2.5 + k * 3)], tone('wood', r.uniform(.9, 1.1)), wob=.2, line=.9)
    if kind == 'shutter':
        p.fill([(x - 3 - w * .5, y - 1), (x - 3, y - 1), (x - 3, y + h + 1), (x - 3 - w * .5, y + h + 3)], 'wood', wob=.3, line=1.0)
    p.fill([(x - 4, y + h + 3), (x + w + 4, y + h + 3), (x + w + 4, y + h + 6), (x - 4, y + h + 6)], 'stone_l', wob=.2, line=.9)
    p.shade([(x - 3, y + h + 6), (x + w + 3, y + h + 6), (x + w + 3, y + h + 9), (x - 3, y + h + 9)], .3, 0)
def door(p, cx, yb, w, h, arch=False, col='wood', frame='stone_l', r=None):
    r = r or random.Random(0); x0, x1 = cx - w / 2, cx + w / 2; yt = yb - h
    fr = [(x0 - 5, yb), (x0 - 5, yt - 4), (x1 + 5, yt - 4), (x1 + 5, yb)]
    if arch: fr = [(x0 - 5, yb), (x0 - 5, yt + w * .3)] + [(cx + (w / 2 + 5) * math.cos(a), yt + w * .3 - (w / 2 + 5) * .9 * math.sin(a)) for a in np.linspace(math.pi, 0, 12)] + [(x1 + 5, yt + w * .3), (x1 + 5, yb)]
    p.fill(fr, frame, wob=.3, line=1.3)
    lf = [(x0, yb), (x0, yt + (w * .3 if arch else 0))] + ([(cx + w / 2 * math.cos(a), yt + w * .3 - w / 2 * .9 * math.sin(a)) for a in np.linspace(math.pi, 0, 12)] if arch else [(x1, yt)]) + [(x1, yt + (w * .3 if arch else 0)), (x1, yb)]
    p.fill(lf, col, wob=.25, line=1.2)
    for k in range(1, 4): xx = x0 + w * k / 4; p.stroke([(xx, yt + (w * .32 if arch else 3)), (xx, yb - 1)], .7, 170, .2)
    for yy in (yt + h * .25, yt + h * .7): p.fill([(x0 + 1, yy), (x1 - 1, yy), (x1 - 1, yy + 2.5), (x0 + 1, yy + 2.5)], 'iron', wob=.1, line=.6)
    p.ell(x1 - w * .22, yt + h * .55, 1.8, 1.8, 'iron_l', n=8, wob=0, line=.8)
    p.shade([(x0, yt), (x1, yt), (x1, yt + 5), (x0, yt + 5)], .45, 0)
    p.fill([(x0 - 8, yb - 1), (x1 + 8, yb - 1), (x1 + 10, yb + 5), (x0 - 10, yb + 5)], 'stone_l', wob=.4, line=1.1)   # door step
    return dict(cx=cx, by=yb, w=w, h=h)
def hanging_sign(p, x, y, glyph, side=1, r=None):
    r = r or random.Random(0)
    p.stroke([(x, y), (x + side * 22, y)], 1.6, 230, .2); p.stroke([(x, y + 7), (x + side * 10, y)], 1.0, 200, .2)
    bx = x + side * 14; p.stroke([(bx - 7, y), (bx - 7, y + 5)], .7); p.stroke([(bx + 7, y), (bx + 7, y + 5)], .7)
    p.fill([(bx - 11, y + 5), (bx + 11, y + 5), (bx + 11, y + 21), (bx - 11, y + 21)], 'wood_l', wob=.5, line=1.2)
    g = glyph; X, Y = bx, y + 13
    if g == 'mug': p.rect(X - 4, Y - 5, X + 3, Y + 5, 'cloth_o', wob=.3, line=1); p.stroke([(X + 3, Y - 3), (X + 6, Y - 1), (X + 6, Y + 2), (X + 3, Y + 3)], .9)
    elif g == 'spool': p.rect(X - 5, Y - 6, X + 5, Y - 4, 'wood', line=.8); p.rect(X - 3, Y - 4, X + 3, Y + 4, 'cloth_r', line=.8); p.rect(X - 5, Y + 4, X + 5, Y + 6, 'wood', line=.8); p.stroke([(X + 3, Y), (X + 8, Y + 3)], .6)
    elif g == 'sword': p.fill([(X - 1, Y - 7), (X + 1, Y - 7), (X + 1, Y + 3), (X, Y + 5), (X - 1, Y + 3)], 'iron_l', wob=.1, line=.8); p.stroke([(X - 4, Y + 3), (X + 4, Y + 3)], 1.2)
    elif g == 'anvil': p.fill([(X - 7, Y - 3), (X + 6, Y - 3), (X + 3, Y), (X + 3, Y + 3), (X + 5, Y + 5), (X - 5, Y + 5), (X - 3, Y + 3), (X - 3, Y)], 'iron', wob=.2, line=.9)
    elif g == 'leaf': p.fill([(X - 6, Y + 4), (X - 2, Y - 4), (X + 5, Y - 6), (X + 3, Y + 1)], 'herb', wob=.3, line=.9); p.stroke([(X - 6, Y + 5), (X + 4, Y - 5)], .6)
    elif g == 'bag': p.fill([(X - 5, Y + 5), (X - 6, Y - 1), (X - 2, Y - 4), (X + 2, Y - 4), (X + 6, Y - 1), (X + 5, Y + 5)], 'cloth', wob=.3, line=.9); p.stroke([(X - 3, Y - 4), (X + 3, Y - 4)], 1.0)
    elif g == 'key': p.ell(X - 3, Y, 3, 3, 'wood_d', n=8, line=.9); p.stroke([(X, Y), (X + 6, Y)], 1.0); p.stroke([(X + 5, Y), (X + 5, Y + 3)], .8)
def chimney(p, x, ytop, ybot, w=14, r=None):
    p.fill([(x, ybot), (x, ytop), (x + w, ytop), (x + w, ybot)], 'stone', wob=.4, line=1.2)
    masonry(p, x, ytop, x + w, ybot, rowh=6, col='stone', la=110, lw=.6, holes=0, seed=int(x + ytop), wmin=.9, wmax=1.6)
    p.fill([(x - 3, ytop - 3), (x + w + 3, ytop - 3), (x + w + 3, ytop + 2), (x - 3, ytop + 2)], 'stone_l', wob=.3, line=1.1)
    p.rect(x + 3, ytop - 5, x + w - 3, ytop - 2, 'void', wob=.2, line=.8)
    p.shade([(x + w * .6, ytop + 2), (x + w, ytop + 2), (x + w, ybot), (x + w * .6, ybot)], .3, 0)
def house(W, d, hf, seed=0, roof='gable', mat='timber', roofcol='roof', door_at=None, door_w=1.35, door_h=2.05, wins=None, chim=None, dmg=.3, sign=None,
          stories=1, extras=(), arch_door=False, ruin=False):
    """W: face width (tiles); d: depth (tiles, solid footprint rows); hf: face height (tiles). returns (Image, meta)"""
    r = random.Random(seed); m = 1.2; ov = .45
    rh = (d * .55 + .9) if roof in ('gable', 'thatch') else (d * .36 + .5) if roof == 'front' else 0
    gab = W * .42 if roof == 'front' else 0
    top_pad = 2.2 + (1.5 if chim is not None else 0) + gab
    Wp = int((W + 2 * m) * T); Hp = int((hf + rh + top_pad + .45) * T); p = Pic(Wp, Hp, seed)
    xl, xr = m * T, (m + W) * T; yb = Hp - .45 * T; ft = yb - hf * T
    meta = dict(ax=xl, ay=yb, W=W, d=d)
    if ruin: return ruin_house(p, W, d, hf, r, xl, xr, yb, ft, meta, seed)
    # --- roof behind the face (front-gable roof planes go back/up from the gable edges)
    if roof == 'front':
        apx = (xl + xr) / 2; apy = ft - gab * T; rd = rh * T
        L = [(xl - ov * T, ft + .15 * T), (apx, apy - .25 * T), (apx, apy - .25 * T - rd), (xl - ov * T, ft + .15 * T - rd)]
        R = [(xr + ov * T, ft + .15 * T), (apx, apy - .25 * T), (apx, apy - .25 * T - rd), (xr + ov * T, ft + .15 * T - rd)]
        for poly, f in ((L, 1.08), (R, .82)):
            p.fill(poly, tone(roofcol, f), wob=.5, line=1.4)
            for k in range(1, 9):
                t = k / 9; a = (poly[0][0] + (poly[1][0] - poly[0][0]) * t, poly[0][1] + (poly[1][1] - poly[0][1]) * t); p.stroke([a, (a[0], a[1] - rd)], .6, 130, .3)
            for k in range(1, 6):
                t = k / 6; p.stroke([(poly[0][0], poly[0][1] - rd * t), (poly[1][0], poly[1][1] - rd * t)], .6, 110, .4)
        p.fill([(apx - 3, apy - .25 * T + 2), (apx + 3, apy - .25 * T + 2), (apx + 3, apy - .25 * T - rd), (apx - 3, apy - .25 * T - rd)], tone(roofcol, .7), wob=.2, line=1.0)
    # --- face
    if roof == 'front':
        fpoly = [(xl, yb), (xl, ft), ((xl + xr) / 2, ft - gab * T), (xr, ft), (xr, yb)]
    else: fpoly = [(xl, yb), (xl, ft - .2 * T), (xr, ft - .2 * T), (xr, yb)]
    base = {'timber': 'plaster', 'stone': 'stone', 'plank': 'wood', 'plaster': 'plaster'}[mat]
    p.fill(fpoly, base, wob=.5, line=1.6)
    ytop_face = ft - gab * T
    if mat == 'stone':
        masonry(p, xl, ytop_face, xr, yb, rowh=10, col='stone', var=.15, holes=.01, seed=seed + 1, wmin=1.0, wmax=2.2,
                top=(lambda x: ft - gab * T * (1 - abs(x - (xl + xr) / 2) / ((xr - xl) / 2))) if gab else None)
    elif mat == 'plank':
        for x in np.arange(xl + 5, xr - 2, 6.5): p.stroke([(x + r.uniform(-.5, .5), ft + 2), (x + r.uniform(-.5, .5), yb - 2)], .7, 150, .4)
        for k in range(int((xr - xl) / 6.5)):
            if r.random() < .3: x = xl + k * 6.5; p.fill([(x + 1, ft), (x + 6, ft), (x + 6, yb), (x + 1, yb)], tone('wood', r.uniform(.8, 1.15)), wob=.2, line=0)
    else:
        p.post.append(lambda pp, c, a, x0=int(xl), x1=int(xr), y0=int(ytop_face), y1=int(yb): None)
        base_h = .7 * T
        p.fill([(xl, yb), (xl, yb - base_h), (xr, yb - base_h), (xr, yb)], 'stone', wob=.4, line=1.2)
        masonry(p, xl, yb - base_h, xr, yb, rowh=8, col='stone', var=.15, holes=0, seed=seed + 2)
        if mat == 'timber':
            bw = 4.5; ys = [ft - .1 * T, yb - base_h] + ([ft + (yb - base_h - ft) * .48] if stories > 1 else [])
            for yy in ys: p.fill([(xl - 2, yy - bw / 2), (xr + 2, yy - bw / 2), (xr + 2, yy + bw / 2), (xl - 2, yy + bw / 2)], 'wood_d', wob=.3, line=1.0)
            nv = max(2, int(W / 2.3)); xsv = [xl + (xr - xl) * k / nv for k in range(nv + 1)]
            for k, xx in enumerate(xsv):
                xx = min(max(xx, xl + 2), xr - 2); p.fill([(xx - 2.2, ft), (xx + 2.2, ft), (xx + 2.2, yb - base_h), (xx - 2.2, yb - base_h)], 'wood_d', wob=.2, line=.9)
            levels = sorted(ys)
            for k in range(nv):
                for a_, b_ in zip(levels[:-1], levels[1:]):
                    if r.random() < .35:
                        xa, xb = xsv[k] + 2, xsv[k + 1] - 2
                        if r.random() < .5: p.fill([(xa, b_ - 2), (xa + 4, b_ - 2), (xb, a_ + 2), (xb - 4, a_ + 2)], 'wood_d', wob=.2, line=.8)
                        else: p.fill([(xb, b_ - 2), (xb - 4, b_ - 2), (xa, a_ + 2), (xa + 4, a_ + 2)], 'wood_d', wob=.2, line=.8)
            if gab: p.fill([((xl + xr) / 2 - 2, ft - gab * T + 4), ((xl + xr) / 2 + 2, ft - gab * T + 4), ((xl + xr) / 2 + 2, ft), ((xl + xr) / 2 - 2, ft)], 'wood_d', wob=.2, line=.8)
        # plaster stains / flaked patches showing lath
        for k in range(int(W * .6)):
            x = r.uniform(xl + 6, xr - 14); y = r.uniform(ft + 6, yb - base_h - 10)
            if r.random() < .5: p.fill([(x, y), (x + r.uniform(5, 10), y + r.uniform(-2, 2)), (x + r.uniform(4, 9), y + r.uniform(4, 8)), (x + r.uniform(-1, 2), y + r.uniform(4, 7))], 'plaster_d', wob=.6, line=.6, la=120)
    # --- openings
    meta['door'] = None
    if door_at is not None:
        dcx = xl + door_at * T; meta['door'] = door(p, dcx, yb, door_w * T, door_h * T, arch=arch_door, frame='stone_l' if mat != 'plank' else 'wood_d', r=r)
        meta['door_tx'] = door_at
    for wn in (wins or []):
        wx, wy, kind = wn[0], wn[1], (wn[2] if len(wn) > 2 else 'lit'); ww_ = (wn[3] if len(wn) > 3 else 1.0) * T; wh_ = (wn[4] if len(wn) > 4 else 1.15) * T
        window(p, xl + wx * T - ww_ / 2, yb - wy * T - wh_, ww_, wh_, kind, r)
    # --- roof in front (side-gable / thatch): its front slope above the face
    if roof in ('gable', 'thatch'):
        eave = ft + .25 * T; ridge = ft - rh * T
        poly = [(xl - ov * T, eave), (xr + ov * T, eave), (xr + .25 * T, ridge), (xl - .25 * T, ridge)]
        p.fill([(xl - .2 * T, ridge + 2), (xr + .2 * T, ridge + 2), (xr + .05 * T, ridge - .45 * T), (xl - .05 * T, ridge - .45 * T)], tone(roofcol, .68), wob=.5, line=1.2)   # back slope sliver
        _roof_courses(p, poly, ridge, eave, xl - ov * T, xr + ov * T, roofcol, r, 'thatch' if roof == 'thatch' else 'slate', 7 if roof != 'thatch' else 6)
        p.fill([(xl - .3 * T, ridge - 2), (xr + .3 * T, ridge - 2), (xr + .3 * T, ridge + 3), (xl - .3 * T, ridge + 3)], tone(roofcol, .75), wob=.4, line=1.2)  # ridge cap
        p.light([(xl, ridge + 4), (xr, ridge + 4), (xr + ov * T * .5, ridge + (eave - ridge) * .45), (xl - ov * T * .5, ridge + (eave - ridge) * .45)], .14, .5)
        p.shade([(xl - ov * T, eave - 5), (xr + ov * T, eave - 5), (xr + ov * T, eave), (xl - ov * T, eave)], .35, .3)
        p.shade([(xl, eave), (xr, eave), (xr, eave + .32 * T), (xl, eave + .32 * T)], .42, .4)   # eave shadow on the face
        if roof == 'thatch':
            for x in np.arange(xl - ov * T, xr + ov * T, 3): p.stroke([(x, eave - 3), (x + r.uniform(-1, 1), eave + r.uniform(1, 4))], .6, 150, .2)
        # burn holes + patches
        nh = int(dmg * 3 + r.random() * dmg * 2)
        for k in range(nh):
            hx = r.uniform(xl + T, xr - 2 * T); hy = r.uniform(ridge + 10, eave - 14); hw = r.uniform(.9, 2.0) * T; hh = r.uniform(.5, .9) * T
            pts = [(hx + hw / 2 + hw / 2 * math.cos(a) * r.uniform(.7, 1.1), hy + hh / 2 * math.sin(a) * r.uniform(.7, 1.1)) for a in np.linspace(0, 2 * math.pi, 11, endpoint=False)]
            p.fill(pts, 'void', wob=.8, line=1.3)
            for j in range(3): xx = hx + hw * (j + .5) / 3; p.fill([(xx - 1.8, hy - hh / 2), (xx + 1.8, hy - hh / 2), (xx + 2.5, hy + hh / 2), (xx - 1.0, hy + hh / 2)], 'char', wob=.3, line=.8)
            p.post.append(soot_post(lambda yy, xx, hx=hx, hy=hy, hw=hw: np.clip(1 - np.hypot((xx - hx - hw / 2) / (hw * .9), (yy - hy) / (hw * .6)), 0, 1), .6, int(hx)))
        if r.random() < .7:
            px_ = r.uniform(xl, xr - 1.5 * T); py_ = r.uniform(ridge + 8, eave - 16)
            p.fill([(px_, py_), (px_ + 1.3 * T, py_ + 1), (px_ + 1.3 * T, py_ + .55 * T), (px_, py_ + .5 * T)], tone('wood', r.uniform(.9, 1.1)), wob=.3, line=1.0)
            for k in range(1, 4): p.stroke([(px_ + k * .33 * T, py_ + 1), (px_ + k * .33 * T, py_ + .5 * T)], .6, 150)
        p.post.append(moss_post(lambda yy, xx, e=eave, rg=ridge: np.clip((yy - rg) / (e - rg + 1), 0, 1) * ((yy < e) & (yy > rg)) * .6, .5, 'moss', 7, seed + 7, .62))
        meta['ridge'] = ridge; meta['eave'] = eave
    if chim is not None:
        cx_ = xl + chim * T; ctop = (meta.get('ridge', ft - gab * T) - 1.3 * T)
        chimney(p, cx_ - 11, ctop, meta.get('ridge', ft) + (meta.get('eave', ft) - meta.get('ridge', ft)) * .5, 22, r)
        meta['chimney'] = (chim, (yb - ctop) / T)
    # --- extras
    if 'balcony' in extras:
        by_ = ft + (yb - .7 * T - ft) * .48
        p.fill([(xl + .6 * T, by_ + 3), (xr - .6 * T, by_ + 3), (xr - .4 * T, by_ + 9), (xl + .4 * T, by_ + 9)], 'wood', wob=.3, line=1.1)
        for x in np.arange(xl + .7 * T, xr - .6 * T, 6): p.stroke([(x, by_ - 12), (x, by_ + 3)], .9, 200, .2)
        p.stroke([(xl + .6 * T, by_ - 12), (xr - .6 * T, by_ - 12)], 1.6, 230, .4)
        for x in (xl + 2.5 * T, xr - 3.2 * T): p.fill([(x, by_ - 10), (x + .7 * T, by_ - 11), (x + .8 * T, by_ + 6), (x - .1 * T, by_ + 6)], r.choice(['cloth_r', 'cloth', 'cloth_b']), wob=.6, line=.9)  # laundry on the rail
    if 'awning' in extras:
        ax0 = xl + extras_awn(extras)[0] * T; ax1 = xl + extras_awn(extras)[1] * T; ay0 = yb - 2.45 * T
        n = int((ax1 - ax0) / 9)
        for k in range(n):
            xa = ax0 + k * (ax1 - ax0) / n; xb = ax0 + (k + 1) * (ax1 - ax0) / n
            p.fill([(xa, ay0), (xb, ay0), (xb + 2, ay0 + .62 * T), (xa + 2, ay0 + .62 * T + (k % 2) * 2)], 'cloth_r' if k % 2 else 'cloth', wob=.4, line=1.0)
        p.shade([(ax0, ay0 + .62 * T), (ax1, ay0 + .62 * T), (ax1, ay0 + .62 * T + 7), (ax0, ay0 + .62 * T + 7)], .4, .3)
        for x in (ax0 + 2, ax1 - 2): p.stroke([(x, ay0 + .6 * T), (x, yb)], 1.4, 230, .3)
    if 'herbs' in extras:
        for x in np.arange(xl + .5 * T, xr - .4 * T, .55 * T):
            if r.random() < .75:
                yy = meta.get('eave', ft) + .35 * T; p.stroke([(x, yy - 3), (x, yy + 3)], .6, 180)
                p.fill([(x - 3, yy + 3), (x + 3, yy + 3), (x + 1.5, yy + 13), (x - 1.5, yy + 13)], r.choice(['herb', 'moss', 'thatch_d']), wob=.5, line=.7)
    if sign: hanging_sign(p, sign[1], yb - sign[2] * T, sign[0], sign[3] if len(sign) > 3 else 1, r)
    # weathering on the face: soot above openings, damp at the foot
    p.post.append(soot_post(lambda yy, xx: ((yy > ytop_face) & (yy < yb)) * np.clip(1 - (yy - ft) / (hf * T * .7), 0, 1) * dmg * .9, .5, seed + 3))
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - (yb - .9 * T)) / (.9 * T), 0, 1) * (yy < yb), .55, 'moss', 6, seed + 5, .6))
    p.shade([(xr - .7 * T, ytop_face), (xr, ytop_face), (xr, yb), (xr - .7 * T, yb)], .18, .3)
    p.stroke([(xl - 4, yb + 1), (xr + 4, yb + 1)], 1.8, 235, .6)
    return p, meta
def extras_awn(extras):
    for e in extras:
        if isinstance(e, tuple) and e[0] == 'awn': return e[1], e[2]
    return 1, 4
def ruin_house(p, W, d, hf, r, xl, xr, yb, ft, meta, seed):
    """burnt shell: back wall beyond, side stubs, broken front wall, fallen charred beams."""
    back_b = yb - d * .55 * T; back_t = back_b - hf * .9 * T
    jb = [(x, back_t + r.uniform(-4, 4) + (r.random() < .3) * r.uniform(5, hf * T * .5)) for x in np.linspace(xl, xr, int(W * 1.4) + 2)]
    p.fill([(xl, back_b)] + jb + [(xr, back_b)], tone('stone', .85), wob=.5, line=1.4)
    masonry(p, xl, back_t - 10, xr, back_b, top=lambda x: float(np.interp(x, [q[0] for q in jb], [q[1] for q in jb])), rowh=10, col=tone('stone', .85), holes=.04, seed=seed + 1)
    p.fill([(xl, back_b), (xr, back_b), (xr, yb), (xl, yb)], 'char', wob=.4, line=1.0)     # floor of ash
    p.dots(xl + 4, back_b + 3, xr - 4, yb - 3, W * 6, 'stone_d', (1, 3))
    for k in range(3):
        x = r.uniform(xl + T, xr - 2 * T); p.fill([(x, back_b + r.uniform(0, 10)), (x + 4, back_b + r.uniform(0, 10)), (x + r.uniform(20, 50), yb - 6), (x + r.uniform(16, 46), yb - 4)], 'char', wob=.3, line=1.1)
    for side in (xl, xr - .55 * T):
        hs = r.uniform(.4, .9) * hf * T; p.fill([(side, yb), (side, back_b - hs * .6), (side + .55 * T, back_b - hs * .6 + 6), (side + .55 * T, yb)], 'stone', wob=.5, line=1.3)
    jf = [(x, yb - r.uniform(.25, .75) * hf * T * (1 if r.random() > .3 else .3)) for x in np.linspace(xl, xr, int(W * 1.2) + 2)]
    gap = r.uniform(.35, .6)
    p.fill([(xl, yb)] + [q for q in jf if q[0] < xl + (xr - xl) * gap - T * .7] + [(xl + (xr - xl) * gap - T * .7, yb)], 'stone', wob=.5, line=1.4)
    p.fill([(xl + (xr - xl) * gap + T * .7, yb)] + [q for q in jf if q[0] > xl + (xr - xl) * gap + T * .7] + [(xr, yb)], 'stone', wob=.5, line=1.4)
    for poly_x0, poly_x1 in ((xl, xl + (xr - xl) * gap - T * .7), (xl + (xr - xl) * gap + T * .7, xr)):
        masonry(p, poly_x0, yb - hf * T * .8, poly_x1, yb, top=lambda x: float(np.interp(x, [q[0] for q in jf], [q[1] for q in jf])), rowh=10, col='stone', holes=.03, seed=seed + int(poly_x0))
    p.post.append(soot_post(lambda yy, xx: np.clip(1 - (yy - back_t) / (hf * T * 1.3), 0, 1), .75, seed))
    p.post.append(moss_post(lambda yy, xx: np.clip((yy - (yb - .7 * T)) / (.7 * T), 0, 1), .5, 'moss', 6, seed + 5, .6))
    meta['door'] = None; meta['ruin'] = True
    return p, meta
