"""inkart: code-drawn art in a Japanese hand-drawn look (felt v5, owner 10-25 「기존 것 쓰지 말고 새로 디자인」).
ink outlines with brush-pressure width + wobble, flat cel fills (2-3 tones), watercolour wash / edge pooling / bleed,
desaturated sepia palette. No external art is read: every picture is drawn from polygons and noise here.
Layers: col (RGB fills) + al (alpha) + shd (cel shadow amount) + lit (highlight) + ink (2x supersampled) + post (numpy callbacks)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
INK = np.array([36, 29, 26.])
PAL = dict(paper=(204, 191, 168), stone_l=(162, 152, 136), stone=(130, 121, 108), stone_d=(94, 87, 78), stone_dd=(62, 57, 52), void=(30, 26, 25),
           wood_l=(142, 114, 86), wood=(110, 86, 64), wood_d=(76, 60, 46), char=(50, 44, 40),
           plaster=(182, 170, 148), plaster_d=(146, 135, 118), roof=(96, 88, 84), roof_l=(122, 112, 104), roof_d=(66, 60, 58),
           tile_r=(128, 92, 78), tile_rd=(96, 70, 60), thatch=(150, 132, 96), thatch_d=(110, 96, 70),
           moss=(108, 112, 80), moss_d=(82, 88, 64), soot=(46, 42, 40), cloth_r=(132, 66, 56), cloth_o=(156, 124, 78), cloth=(176, 162, 136), cloth_b=(92, 100, 108),
           iron=(72, 70, 72), iron_l=(110, 106, 104), ember=(200, 112, 60), glow=(214, 168, 104), herb=(110, 118, 78), sky=(120, 118, 124))
def C(c): return tuple(int(v) for v in (PAL[c] if isinstance(c, str) else c))
def mix(a, b, t): a, b = C(a), C(b); return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
def tone(c, f): c = C(c); return tuple(int(max(0, min(255, v * f))) for v in c)
def vnoise(h, w, scale, seed):
    r = np.random.RandomState(seed % (2 ** 31)); lh, lw = max(2, int(h / scale) + 3), max(2, int(w / scale) + 3)
    im = Image.fromarray((r.rand(lh, lw) * 255).astype(np.uint8)).resize((int((lw - 1) * scale) + 2, int((lh - 1) * scale) + 2), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w] / 255.
def fbm(h, w, scale, seed, oct=3):
    a = np.zeros((h, w), np.float32); s = 0; amp = 1.
    for i in range(oct): a += vnoise(h, w, max(1.5, scale / 2 ** i), seed + i * 7) * amp; s += amp; amp *= .5
    return a / s
class Pic:
    def __init__(s, w, h, seed=0, ss=2):
        s.w, s.h, s.ss, s.seed = int(w), int(h), ss, seed; s.r = random.Random(seed)
        s.col = Image.new('RGB', (s.w, s.h), (0, 0, 0)); s.cd = ImageDraw.Draw(s.col)
        s.al = Image.new('L', (s.w, s.h), 0); s.ad = ImageDraw.Draw(s.al)
        s.shd = Image.new('L', (s.w, s.h), 0); s.sd = ImageDraw.Draw(s.shd)
        s.lit = Image.new('L', (s.w, s.h), 0); s.ld = ImageDraw.Draw(s.lit)
        s.ink = Image.new('L', (s.w * ss, s.h * ss), 0); s.idr = ImageDraw.Draw(s.ink)
        s.post = []; s.meta = {}
    # ---- geometry helpers ----
    def wob(s, pts, amp=.6, step=7, closed=True):
        if amp <= 0 or len(pts) < 2: return [tuple(p) for p in pts]
        P = list(pts) + ([pts[0]] if closed else []); out = []; ph = s.r.random() * 100
        for i in range(len(P) - 1):
            (x0, y0), (x1, y1) = P[i], P[i + 1]; L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / step))
            nx, ny = (-(y1 - y0) / (L + 1e-6), (x1 - x0) / (L + 1e-6))
            for k in range(n):
                t = k / n; j = 0 if k == 0 else amp * (math.sin(ph + (i * 7 + k) * 1.7) * .6 + (s.r.random() - .5) * .8)
                out.append((x0 + (x1 - x0) * t + nx * j, y0 + (y1 - y0) * t + ny * j))
        if not closed: out.append(tuple(P[-1]))
        return out
    def fill(s, pts, col, wob=.5, line=1.1, la=235, alpha=255, step=7):
        p = s.wob(pts, wob, step)
        if len(p) < 3: return p
        s.cd.polygon(p, fill=C(col)); s.ad.polygon(p, fill=alpha)
        if line: s.line(p, line, True, la)
        return p
    def rect(s, x0, y0, x1, y1, col, **k): return s.fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col, **k)
    def ell(s, cx, cy, rx, ry, col, n=None, **k):
        n = n or max(10, int((rx + ry) / 2)); return s.fill([(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)], col, **k)
    def line(s, pts, w=1.1, closed=False, a=235, taper=True):
        S = s.ss; P = list(pts) + ([pts[0]] if closed else []); n = len(P)
        for i in range(n - 1):
            t = i / max(1, n - 2); pr = .65 + .55 * math.sin(math.pi * t) if taper and not closed else .8 + .4 * s.r.random()
            ww = max(1, int(round(w * pr * S)))
            s.idr.line([(P[i][0] * S, P[i][1] * S), (P[i + 1][0] * S, P[i + 1][1] * S)], fill=a, width=ww)
            if ww > 2: r_ = ww / 2 - .5; s.idr.ellipse([P[i + 1][0] * S - r_, P[i + 1][1] * S - r_, P[i + 1][0] * S + r_, P[i + 1][1] * S + r_], fill=a)
    def stroke(s, pts, w=1.0, a=220, amp=.5): s.line(s.wob(pts, amp, 6, closed=False), w, False, a)
    def shade(s, pts, amt=.35, wob=.4):
        p = s.wob(pts, wob) if wob else pts; s.sd.polygon(p, fill=int(255 * amt))
    def light(s, pts, amt=.2, wob=.4):
        p = s.wob(pts, wob) if wob else pts; s.ld.polygon(p, fill=int(255 * amt))
    def hatch(s, pts, sp=4.0, ang=60, w=.6, a=120, jit=.6):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; x0, y0, x1, y1 = int(min(xs)) - 2, int(min(ys)) - 2, int(max(xs)) + 3, int(max(ys)) + 3
        S = s.ss; bw, bh = (x1 - x0) * S, (y1 - y0) * S
        if bw <= 0 or bh <= 0: return
        L = Image.new('L', (bw, bh), 0); d = ImageDraw.Draw(L); M = Image.new('L', (bw, bh), 0); ImageDraw.Draw(M).polygon([((x - x0) * S, (y - y0) * S) for x, y in pts], fill=255)
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang)); R = (bw + bh)
        k = -R
        while k < R:
            o = k + (s.r.random() - .5) * jit * S * 2; cx, cy = bw / 2 + o * -sa, bh / 2 + o * ca
            d.line([(cx - ca * R, cy - sa * R), (cx + ca * R, cy + sa * R)], fill=a, width=max(1, int(w * S))); k += sp * S
        L = Image.fromarray(np.minimum(np.asarray(L), np.asarray(M)))
        reg = s.ink.crop((x0 * S, y0 * S, x0 * S + bw, y0 * S + bh)); s.ink.paste(Image.fromarray(np.maximum(np.asarray(reg), np.asarray(L))), (x0 * S, y0 * S))
    def dots(s, x0, y0, x1, y1, n, col, r=(.6, 1.6), alpha=255):
        for _ in range(int(n)):
            x = s.r.uniform(x0, x1); y = s.r.uniform(y0, y1); rr = s.r.uniform(*r); s.cd.ellipse([x - rr, y - rr * .8, x + rr, y + rr * .8], fill=C(col))
    # ---- finish: watercolour + ink ----
    def finish(s, cut=None, wash=.10, pool=.22, grain=.045, bleed=.35, desat=.22, sepia=.22, shadow=.62, far=0.0, edge_dark=.0):
        col = np.asarray(s.col, np.float32).copy(); a = np.asarray(s.al, np.float32) / 255.
        for fn in s.post: fn(s, col, a)
        sh = np.asarray(s.shd, np.float32) / 255.; li = np.asarray(s.lit, np.float32) / 255.
        sh = ndimage.gaussian_filter(sh, .7); li = ndimage.gaussian_filter(li, .7)
        col = col * (1 - shadow * sh[..., None]) * np.array([1.0, .99, 1.03]) ** sh[..., None]
        col = col + (np.array([236, 222, 196.]) - col) * li[..., None] * .5
        h, w = a.shape
        lum = col @ np.array([.3, .59, .11]); gx = ndimage.sobel(lum, 1); gy = ndimage.sobel(lum, 0); g = np.hypot(gx, gy)
        g = ndimage.gaussian_filter(np.clip(g / 90., 0, 1), 1.4)
        col *= (1 - pool * g)[..., None]                                                     # pigment pools at the colour edges
        W1 = fbm(h, w, 60, s.seed + 3); W2 = vnoise(h, w, 3, s.seed + 5)
        col *= (1 - wash + 2 * wash * W1)[..., None] * (1 - grain + 2 * grain * W2)[..., None]  # uneven wash + paper grain
        if bleed:
            pm = col * a[..., None]; bl = ndimage.gaussian_filter(pm, (1.6, 1.6, 0)); ba = ndimage.gaussian_filter(a, 1.6)
            bc = bl / np.maximum(ba, 1e-3)[..., None]; col = col * (1 - bleed) + bc * bleed
        lum = (col @ np.array([.3, .59, .11]))[..., None]; col = col * (1 - desat) + lum * desat
        col = col * (1 - sepia) + lum * np.array([1.08, .98, .84]) * sepia
        if edge_dark:
            ed = ndimage.distance_transform_edt(a > .5); col *= (1 - edge_dark * np.clip(1 - ed / 6, 0, 1))[..., None]
        ink = np.asarray(s.ink.resize((w, h), Image.LANCZOS), np.float32) / 255.
        ink = np.clip(ink * 1.15, 0, 1)
        ic = INK if not far else INK * (1 - far) + np.array(PAL['sky']) * far
        ink_ = ink * (1 - far * .5)
        col = col * (1 - ink_[..., None]) + ic * ink_[..., None]
        a = np.maximum(a, ink_ * .95); a = np.where(a < .12, 0, np.clip(a * 1.05, 0, 1))
        if cut is not None: a = np.where(cut, 0, a)
        out = np.dstack([np.clip(col, 0, 255), a * 255]).astype(np.uint8)
        return Image.fromarray(out, 'RGBA')
# ---------- reusable painters ----------
def masonry(p, x0, y0, x1, y1, top=None, rowh=15, col='stone', var=.16, la=120, lw=.85, holes=.03, seed=0, wmin=1.1, wmax=2.6, bottom_dark=.0, skip=None):
    """stone courses on a face. top(x)->y of the broken upper edge (None = flat). returns list of (x,y) hole centers"""
    r = random.Random(seed); holesL = []; y = y1; row = 0
    while y > y0 - .5:
        ya = max(y0, y - rowh * r.uniform(.85, 1.15)); x = x0 - r.uniform(0, rowh * wmax * .7)
        while x < x1:
            bw = rowh * r.uniform(wmin, wmax); xa, xb = max(x0, x), min(x1, x + bw)
            if xb - xa > 2:
                tx = top((xa + xb) / 2) if top else y0
                if ya >= tx - rowh * .3 and not (skip and skip((xa + xb) / 2, (ya + y) / 2)):
                    yt = max(ya, tx); f = 1 + (r.random() - .5) * 2 * var
                    if bottom_dark: f *= 1 - bottom_dark * max(0, (y - y0) / max(1, y1 - y0) - .5)
                    pts = [(xa + .5, yt + .4), (xb - .5, yt + .4 + r.uniform(-.6, .6)), (xb - .4, y - .4), (xa + .4, y - .4)]
                    if r.random() < holes and yt > y0 + rowh:
                        p.fill(pts, 'void', wob=.6, line=lw * 1.2, la=la + 40); holesL.append(((xa + xb) / 2, (yt + y) / 2))
                    else:
                        c = tone(col, f); p.fill(pts, c, wob=.45, line=0, step=6)
                        if r.random() < .8: p.stroke([(xa + .5, y - .6), (xb - .5, y - .6 + r.uniform(-.6, .6))], lw * r.uniform(.7, 1.3), la, .5)   # bed joint
                        if r.random() < .55: p.stroke([(xa + .4, yt + .6), (xa + .4, y - .6)], lw * .8, int(la * .8), .3)                    # head joint
                        if r.random() < .12: p.line(p.wob(pts, .5, 6), lw, True, la)                                                 # a stone drawn whole
                        if r.random() < .35: p.shade([(xa, y - 3.0), (xb, y - 3.0), (xb, y), (xa, y)], .3, 0)   # each stone a little darker at its foot
                        if r.random() < .3: p.light([(xa + 1, yt + .5), (xb - 1, yt + .5), (xb - 1, yt + 2.2), (xa + 1, yt + 2.2)], .3, 0)
            x += bw
        if ya <= y0: break
        y = ya; row += 1
    return holesL
def crack(p, x, y, length, seed, w=1.2, down=True, a=230):
    r = random.Random(seed); pts = [(x, y)]; ang = math.pi / 2 if down else r.uniform(0, math.pi * 2)
    for i in range(int(length / 5)):
        ang += r.uniform(-.7, .7); ang = ang * .8 + (math.pi / 2) * .2 if down else ang
        x += math.cos(ang) * 5; y += math.sin(ang) * 5; pts.append((x, y))
        if r.random() < .12 and length > 30: crack(p, x, y, length * .4, seed + i * 13, w * .7, down, a)
    p.line(pts, w, False, a)
def moss_post(region_fn, amount=.6, col='moss', scale=9, seed=0, thr=.55):
    """post-process: moss patches where region_fn(yy,xx)->weight 0..1"""
    def fn(p, c, a):
        h, w = a.shape; yy, xx = np.mgrid[0:h, 0:w]; wgt = region_fn(yy, xx)
        n = fbm(h, w, scale, seed + p.seed); m = np.clip((n + wgt * .5 - thr) / .1, 0, 1) * amount * (a > .5) * np.clip(wgt * 3, 0, 1)
        mc = np.array(C(col), np.float32); md = np.array(C('moss_d'), np.float32); sel = vnoise(h, w, 3, seed + 9)[..., None]
        c[:] = c * (1 - m[..., None]) + (mc * (1 - sel * .6) + md * sel * .6) * m[..., None]
    return fn
def soot_post(region_fn, amount=.55, seed=0):
    def fn(p, c, a):
        h, w = a.shape; yy, xx = np.mgrid[0:h, 0:w]; wgt = region_fn(yy, xx)
        n = fbm(h, w, 14, seed + p.seed + 31); st = vnoise(h, w, 1, seed + 2)
        streak = ndimage.uniform_filter1d(vnoise(1, w, 2.5, seed + 4).repeat(h, 0), 1)
        m = np.clip(wgt * (.55 + .7 * n) * (.6 + .6 * streak), 0, 1) * amount
        c[:] = c * (1 - m[..., None]) + np.array(C('soot'), np.float32) * m[..., None]
    return fn
def ivy(p, x, y, length, seed, col='moss_d'):
    r = random.Random(seed); pts = [(x, y)]
    for i in range(int(length / 4)):
        x += r.uniform(-1.4, 1.4); y += 4; pts.append((x, y))
        if r.random() < .55: lx = x + r.uniform(-3, 3); ly = y + r.uniform(-2, 2); p.ell(lx, ly, r.uniform(1.4, 2.6), r.uniform(1.0, 1.8), tone(col, r.uniform(.85, 1.15)), n=7, wob=.3, line=.5, la=160)
    p.line(pts, .7, False, 180)
