"""castle_fortress: the royal castle as one tall code-drawn picture with NO sky (owner 10-25 16:51 「하늘은 그리지 말고 화면에 성 전체가 꽉 차게」).
Form study (not a copy) of the owner's reference capture: a huge gothic fortress front — thick round and square towers with corbelled
crenellated crowns, close rows of pointed-arch windows and buttresses with pinnacles, stacked building masses stepping up to a central keep
(the needle spires of our intro video crown it), a gate arch on the west, the east side broken and fallen.
Style = inkart (ink outlines, flat cels, watercolour bleed, desaturated sepia). The background stays TRANSPARENT: world.js fills behind it
with one flat dark fog tone, the silhouette reads by its own light/shade, ink and ember-lit windows.
compose(...) -> (RGBA Image, meta{glows, smoke, tip, base, bbox})."""
import math, random
import numpy as np
from PIL import Image
from scipy import ndimage
from inkart import Pic, fbm, vnoise, tone, mix

ST = (104, 97, 92)      # stone (front)
ROOF = (62, 57, 58)
VOID = (30, 26, 27)
EMBER = (226, 128, 60)

class OPic(Pic):
    """Pic whose fills hide what was drawn before them (ink, cel shade, light) — needed for a big picture of overlapping masses; ink scaled up (LW)."""
    LW = 1.0
    def fill(s, pts, col, wob=.5, line=1.1, la=235, alpha=255, step=7):
        p = s.wob(pts, wob, step)
        if len(p) < 3: return p
        S = s.ss; s.idr.polygon([(x * S, y * S) for x, y in p], fill=0); s.sd.polygon(p, fill=0); s.ld.polygon(p, fill=0)
        s.cd.polygon(p, fill=tuple(int(v) for v in col)); s.ad.polygon(p, fill=alpha)
        if line: s.line(p, line, True, la)
        return p
    def line(s, pts, w=1.1, closed=False, a=235, taper=True): Pic.line(s, pts, w * s.LW, closed, a, taper)

class F:
    def __init__(s, p, P, r, glows, smokes, dark=1.0):
        s.p, s.P, s.r, s.glows, s.smokes, s.k = p, P, r, glows, smokes, dark
    def c(s, col, f=1.0): return tone(col, f * s.k)
    # pointed (gothic) arch window
    def arch(s, x, y, w, h, lit=False, col=None, line=.7):
        P = s.P; ys = y + w * .9; pts = [(x - w / 2, y + h)]
        for i in range(7):
            a = i / 6; pts.append((x - w / 2 * (1 - a) ** 1.25, ys - (ys - y) * math.sin(a * math.pi / 2)))
        for i in range(5, -1, -1):
            a = i / 6; pts.append((x + w / 2 * (1 - a) ** 1.25, ys - (ys - y) * math.sin(a * math.pi / 2)))
        pts.append((x + w / 2, y + h))
        c = EMBER if lit else (col or VOID)
        s.p.fill(pts, c, wob=.15, line=line, la=200)
        if lit: s.glows.append([x, y + h * .55, max(w, h * .5) * 1.4])
        elif h > 3 * P and w > 1.2 * P: s.p.stroke([(x, ys), (x, y + h)], .5, 120, .1)   # mullion
    def crenels(s, x0, x1, y, col, mw=None, mh=None, line=.8):
        P = s.P; mw = mw or 1.3 * P; mh = mh or 1.4 * P; n = max(2, int((x1 - x0) / (mw * 1.8)))
        step = (x1 - x0) / n
        for i in range(n):
            mx = x0 + i * step + (step - mw) / 2; s.p.rect(mx, y - mh, mx + mw, y + .2 * P, col, wob=.15, line=line, la=200)
    def crown(s, cx, w, y, col, broken=False):
        y = y - .6 * s.P
        """corbelled machicolation band + merlons (the thick tower tops of the reference)."""
        P = s.P; ow = w * 1.22; h = 3.2 * P
        if broken:
            pts = [(cx - ow / 2, y + h)]; n = 8
            for i in range(n + 1): pts.append((cx - ow / 2 + ow * i / n, y + s.r.uniform(-.6, 2.2) * P))
            pts.append((cx + ow / 2, y + h)); s.p.fill(pts, col, wob=.3, line=1.0, la=210); return
        s.p.fill([(cx - w / 2, y + h + 2.2 * P), (cx - ow / 2, y + h), (cx - ow / 2, y), (cx + ow / 2, y), (cx + ow / 2, y + h), (cx + w / 2, y + h + 2.2 * P)], col, wob=.2, line=1.0, la=215)
        s.p.shade([(cx - ow / 2, y + h), (cx + ow / 2, y + h), (cx + w / 2, y + h + 2.2 * P), (cx - w / 2, y + h + 2.2 * P)], .6, .1)
        n = max(3, int(ow / (1.7 * P)))
        for i in range(n + 1):                                               # corbels
            x = cx - ow / 2 + ow * i / n; s.p.stroke([(x, y + h), (x, y + h + 1.4 * P)], .55, 140, .1)
        s.p.shade([(cx + ow * .18, y), (cx + ow / 2, y), (cx + ow / 2, y + h), (cx + w / 2, y + h + 2.2 * P), (cx + w * .18, y + h + 2.2 * P)], .4, .15)
        s.p.stroke([(cx - ow / 2, y + h * .45), (cx + ow / 2, y + h * .45)], .5, 110, .1)
        s.crenels(cx - ow / 2, cx + ow / 2, y, col)
    def spire(s, cx, w, y, h, col=ROOF):
        P = s.P; tip = (cx, y - h)
        s.p.fill([(cx - w / 2, y + .3 * P), (cx - w * .16, y - h * .5), tip, (cx + w * .16, y - h * .5), (cx + w / 2, y + .3 * P)], s.c(col), wob=.2, line=1.0, la=225)
        s.p.shade([tip, (cx + w / 2, y + .3 * P), (cx + w * .04, y + .3 * P)], .45, .1)
        for k in range(1, 4):                                                # ribbed bands
            yk = y - h * k * .22; hw = w / 2 * (1 - k * .22) ** 1.4
            s.p.stroke([(cx - hw, yk), (cx + hw, yk)], .6, 150, .1)
        return tip
    def tower(s, cx, w, top, base, round_=True, roof='crown', col=None, win=True, lit=.12, broken=False, turret=False):
        P, r = s.P, s.r; col = col or s.c(ST, r.uniform(.94, 1.06))
        s.p.fill([(cx - w / 2, base), (cx - w / 2, top), (cx + w / 2, top), (cx + w / 2, base)], col, wob=.3, line=1.15, la=220)
        if round_:                                                           # cylinder: dark right third, lit left strip, curved courses
            s.p.shade([(cx + w * .08, top), (cx + w / 2, top), (cx + w / 2, base), (cx + w * .08, base)], .5, .2)
            s.p.shade([(cx + w * .36, top), (cx + w / 2, top), (cx + w / 2, base), (cx + w * .36, base)], .3, .2)
            s.p.light([(cx - w * .44, top), (cx - w * .24, top), (cx - w * .24, base), (cx - w * .44, base)], .3, .2)
            yy = top + 3.2 * P
            while yy < base - P:
                s.p.stroke([(cx - w / 2 + w * j / 8, yy + (1 - ((j / 8) * 2 - 1) ** 2) * .5 * P) for j in range(9)], .45, 95, .1); yy += r.uniform(2.6, 3.6) * P
        else:
            s.p.shade([(cx + w * .2, top), (cx + w / 2, top), (cx + w / 2, base), (cx + w * .2, base)], .52, .2)
            s.p.light([(cx - w / 2, top), (cx - w * .3, top), (cx - w * .3, base), (cx - w / 2, base)], .25, .2)
            for sx in (-1, 1): s.p.stroke([(cx + sx * w * .38, top + 2 * P), (cx + sx * w * .38, base)], .55, 120, .1)   # corner buttress lines
            yy = top + 4 * P
            while yy < base - P: s.p.stroke([(cx - w / 2, yy), (cx + w / 2, yy)], .5, 100, .1); yy += r.uniform(3.4, 4.6) * P
        if win:
            wy = top + 5.2 * P; ww = min(w * .2, 1.5 * P); cols = [0] if w < 7 * P else [-w * .22, w * .22] if w < 11 * P else [-w * .28, 0, w * .28]
            while wy < base - 5 * P:
                for ox in cols:
                    if r.random() < .82: s.arch(cx + ox, wy, ww, ww * 2.6, lit=r.random() < lit)
                wy += r.uniform(5.5, 7.5) * P
        if roof == 'crown': s.crown(cx, w, top - 2.6 * P, col, broken)
        tip = None
        if roof == 'spire' or turret:
            if roof == 'crown' and not broken: tip = s.spire(cx + (r.choice([-1, 1]) * w * .22 if turret == 'side' else 0), w * (.42 if turret else .9), top - 2.6 * P, w * (1.8 if turret else 2.8))
            elif roof == 'spire': s.crenels(cx - w / 2, cx + w / 2, top, col, mw=w / 9); tip = s.spire(cx, w * .9, top - 1.2 * P, w * 3.2)
        if r.random() < .3 and not broken: s.smokes.append([cx + r.uniform(-.3, .3) * w, top])
        return tip
    def block(s, x0, x1, top, base, col=None, rows=2, bays=None, lit=.08, buttress=True, gable=False):
        """a hall mass: crenellated parapet, buttresses with pinnacles, rows of tall pointed windows."""
        P, r = s.P, s.r; col = col or s.c(ST, r.uniform(.92, 1.02)); w = x1 - x0
        s.p.fill([(x0, base), (x0, top), (x1, top), (x1, base)], col, wob=.3, line=1.1, la=215)
        s.p.shade([(x0, top), (x1, top), (x1, top + 2.2 * P), (x0, top + 2.2 * P)], .35, .1)               # parapet shadow
        if gable:                                                                                            # steep roof behind the parapet
            s.p.fill([(x0 + w * .06, top - .2 * P), (x0 + w * .5, top - w * .42), (x1 - w * .06, top - .2 * P)], s.c(ROOF), wob=.3, line=1.0, la=215)
            s.p.shade([(x0 + w * .5, top - w * .42), (x1 - w * .06, top - .2 * P), (x0 + w * .5, top - .2 * P)], .4, .1)
            for k in range(1, 4): s.p.stroke([(x0 + w * .5 - w * .44 * k / 4, top - w * .42 * (1 - k / 4)), (x0 + w * .5 + w * .44 * k / 4, top - w * .42 * (1 - k / 4))], .5, 110, .1)
        s.crenels(x0, x1, top, col, mw=1.1 * P, mh=1.2 * P)
        nb = bays or max(2, int(w / (5.2 * P))); bw = w / nb
        h = base - top; rh = h / (rows + .4)
        for i in range(nb):
            bx = x0 + (i + .5) * bw
            for j in range(rows):
                wy = top + 3 * P + j * rh; wh = rh * .62
                if wy + wh > base - 1.5 * P: break
                if r.random() < .9: s.arch(bx, wy, min(bw * .42, 2.2 * P), wh, lit=r.random() < lit)
            if buttress and i > 0:
                x = x0 + i * bw
                s.p.fill([(x - .7 * P, base), (x - .7 * P, top - 1.2 * P), (x, top - 4.2 * P), (x + .7 * P, top - 1.2 * P), (x + .7 * P, base)], tone(col, 1.06), wob=.15, line=.8, la=200)
                s.p.shade([(x, top - 4 * P), (x + .7 * P, top - 1.2 * P), (x + .7 * P, base), (x, base)], .4, .1)
        for k in range(rows):                                                 # string courses
            yk = top + 2.4 * P + k * rh; s.p.stroke([(x0, yk), (x1, yk)], .55, 110, .2)

def compose(W, H, seed=31, front_gate=True, east_broken=True, haze=(150, 140, 130), fog_base=.10):
    """W x H picture px. The castle fills the frame: needle tip at ~1% from the top, the wall foot at the bottom edge, towers to the side edges."""
    P = H / 100.; cx = W / 2; r = random.Random(seed); glows, smokes = [], []
    U = lambda u: cx + u * P                                                 # horizontal units from the centre (W/2/P ~ 100 at 2:1)
    hu = W / 2 / P
    layers = []; OPic.LW = max(1.0, P / 7.)
    # ---------------- back: keep + needle spires (hazed) ----------------
    p = OPic(W, H, seed); f = F(p, P, r, glows, smokes, 1.08)
    tips = []
    f.block(U(-30), U(30), 34 * P, 70 * P, rows=3, bays=10, lit=.1)
    for u, w, t in ((-40, 9, 22), (40, 9, 24), (-24, 7, 16), (24, 7, 18)):
        f.tower(U(u), w * P, t * P, 72 * P, round_=True, roof='crown', turret=True, lit=.1)
    f.tower(U(0), 13 * P, 26 * P, 70 * P, round_=False, roof='crown', lit=.14)             # the keep
    tips.append(f.spire(U(0), 9 * P, 22.8 * P, 21.6 * P))                                  # the central needle (frame top)
    for s_ in (-1, 1): f.tower(U(s_ * 10.5), 5 * P, 30 * P, 50 * P, round_=True, roof='spire', lit=.0, win=False)
    for u in (-58, -50, 50, 60):
        f.tower(U(u), 6.5 * P, r.uniform(28, 34) * P, 74 * P, round_=r.random() < .6, roof=r.choice(['crown', 'spire']), lit=.06)
    layers.append((p, .26))
    # ---------------- mid: the great stepped masses + thick crowned towers ----------------
    p = OPic(W, H, seed + 1); f = F(p, P, r, glows, smokes, .9)
    f.block(U(-hu * .9), U(-34), 46 * P, 86 * P, rows=3, lit=.08, gable=False)
    f.block(U(34), U(hu * .92), 44 * P, 86 * P, rows=3, lit=.08)
    f.block(U(-36), U(36), 48 * P, 86 * P, rows=3, bays=12, lit=.1)
    for u0, u1, t in ((-66, -52, 44), (54, 68, 42), (-34, -22, 44), (24, 34, 45)): f.block(U(u0), U(u1), t * P, 60 * P, rows=1, gable=True, buttress=False, lit=.1)
    for u, w, t, rd in ((-74, 12, 30, True), (-46, 15, 26, True), (46, 14, 25, True), (76, 11, 33, False), (-90, 9, 40, False), (92, 9, 42, True), (-18, 10, 36, True), (20, 10, 38, False)):
        brk = east_broken and u == 76
        f.tower(U(u), w * P, t * P, 88 * P, round_=rd, roof='crown', broken=brk, lit=.12, turret=('side' if r.random() < .4 and not brk else False))
    layers.append((p, .12))
    # ---------------- front: curtain wall, gate (west), buttressed hall front, broken east end ----------------
    p = OPic(W, H, seed + 2); f = F(p, P, r, glows, smokes, .74)
    wt = 74 if front_gate else 80
    f.block(U(-hu), U(hu), wt * P, 101 * P, rows=1, bays=26, lit=.05, buttress=True)
    for u, w in ((-hu + 4, 10), (-52, 9), (-22, 8), (14, 8), (44, 9), (hu - 4, 10)):
        f.tower(U(u), w * P, (wt - 9) * P, 101 * P, round_=(abs(u) < 60), roof='crown', lit=.06, win=True)
    if front_gate:                                                          # the gate arch between two square towers (west, like the reference)
        gx = U(-68); gw = 7 * P
        for s_ in (-1, 1): f.tower(gx + s_ * (gw + 3.4 * P), 6.4 * P, 58 * P, 101 * P, round_=False, roof='crown', lit=.1)
        pts = [(gx - gw, 101 * P), (gx - gw, 84 * P)] + [(gx - gw * math.cos(a), 84 * P - gw * 1.25 * math.sin(a)) for a in np.linspace(0, math.pi, 15)] + [(gx + gw, 101 * P)]
        p.fill([(gx - gw - 1.6 * P, 101 * P), (gx - gw - 1.6 * P, 66 * P), (gx + gw + 1.6 * P, 66 * P), (gx + gw + 1.6 * P, 101 * P)], f.c(ST, 1.04), wob=.3, line=1.1, la=215)
        f.crenels(gx - gw - 1.6 * P, gx + gw + 1.6 * P, 66 * P, f.c(ST, 1.04))
        p.fill(pts, VOID, wob=.2, line=1.3, la=235)
        for k in range(1, 7): p.stroke([(gx - gw + 2 * gw * k / 7, 76 * P), (gx - gw + 2 * gw * k / 7, 101 * P)], .7, 150, .1)   # portcullis bars
        for k in range(3): p.stroke([(gx - gw, (86 + k * 5) * P), (gx + gw, (86 + k * 5) * P)], .6, 140, .1)
        glows.append([gx, 97 * P, 6 * P])
    if east_broken:                                                         # the east end fallen: jagged breach + rubble cone
        ex = U(hu * .72); jag = [(ex - 14 * P, 101 * P), (ex - 14 * P, 76 * P), (ex - 12.5 * P, 71 * P)]
        for i in range(9): jag.append((ex - 12 * P + i * 3 * P, (73 + r.uniform(-2, 13)) * P))
        jag += [(ex + 14 * P, 70 * P), (ex + 15.5 * P, 75 * P), (ex + 15.5 * P, 101 * P)]
        p.fill(jag, (40, 35, 35), wob=.6, line=1.3, la=230)
        for k in range(5): xk = ex - 10 * P + k * 5 * P; p.fill([(xk, 101 * P), (xk + .5 * P, (84 + r.uniform(0, 6)) * P), (xk + 2 * P, (85 + r.uniform(0, 6)) * P), (xk + 2.4 * P, 101 * P)], (60, 54, 52), wob=.3, line=.9, la=200)   # snapped beams / inner walls
        p.fill([(ex - 16 * P, 101 * P), (ex - 6 * P, 92 * P), (ex + 3 * P, 90 * P), (ex + 14 * P, 95 * P), (ex + 22 * P, 101 * P)], (96, 90, 86), wob=1.2, line=1.0, la=200)
        for k in range(30):
            x = ex + r.uniform(-14, 20) * P; y = r.uniform(92, 100) * P; p.stroke([(x, y), (x + r.uniform(1, 2.6) * P, y + r.uniform(-.5, .8) * P)], .8, 170)
    layers.append((p, 0.0))
    # ---------------- composite (transparent background) ----------------
    out = np.zeros((H, W, 4), np.float32)
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H; fn = fbm(H, W, 90, seed + 4, 3)
    for i, (pic, hz) in enumerate(layers):
        im = np.asarray(pic.finish(far=hz, bleed=.3, sepia=.3, desat=.28, wash=.12), np.float32)
        col, a = im[..., :3], im[..., 3:4] / 255.
        h = hz + fog_base * np.clip((yy - .55) / .45, 0, 1) * (.6 + .4 * fn)               # haze: deeper layers + the lower part (ground fog), kept light
        col = col * (1 - h[..., None]) + np.array(haze, np.float32) * h[..., None]
        out[..., :3] = out[..., :3] * (1 - a) + col * a; out[..., 3:] = out[..., 3:] + (1 - out[..., 3:]) * a
    grain = vnoise(H, W, 2.5, seed + 30); out[..., :3] *= (.965 + .07 * grain)[..., None]
    al = out[..., 3] > .05; ys, xs = np.where(al)
    meta = dict(glows=[[round(g[0], 1), round(g[1], 1), round(g[2], 1)] for g in glows], smoke=[[round(s_[0], 1), round(s_[1], 1)] for s_ in sorted(smokes, key=lambda s_: s_[1])[:7]],
                tip=[float(tips[0][0]), float(tips[0][1])], bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())])
    img = np.dstack([np.clip(out[..., :3], 0, 255), np.clip(out[..., 3] * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(img, 'RGBA'), meta

if __name__ == '__main__':
    import sys, time
    t = time.time(); im, meta = compose(2400, 1200, front_gate='nogate' not in sys.argv)
    bg = Image.new('RGBA', im.size, (44, 40, 38, 255)); bg.alpha_composite(im); bg.convert('RGB').save('/tmp/v7/fortress_test.png')
    print(im.size, meta['bbox'], meta['tip'], len(meta['glows']), round(time.time() - t, 1))
