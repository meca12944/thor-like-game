"""castle_tone: one stone for Felt's capital wall and the royal castle behind it (owner 10-25 「뒷 벽이랑 성벽이랑, 뒤에 왕도하고 일체화」).
The illustrator's castle (castle_far.webp) is the reference: a warm sepia stone, flat 2-3 tone cel fills, heavy black ink, vertical black rain/soot drips
under every ledge. regrade() maps a code-drawn picture onto it: luminance by quantile matching (to the castle's lower half = the part that meets the wall),
colour by the castle's own luminance -> colour ramp, then a soft cel posterise; drips() paints the castle's drip streaks under the ledges / slits / merlons.
Used by build_felt5.py (wall band, gate tunnel, side walls, wall rubble) and castle_city.py (the capital skyline round the castle)."""
import os, math
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..')
REF = 'assets/world/castle_far/castle_far.webp'
INKC = np.array([10, 8, 5.], np.float32)
LUM = np.array([.3, .59, .11], np.float32)
_ref = None
def ref():
    """(ramp 256x3: castle colour per luminance, target quantiles q -> luminance) from the castle's lower half (rows >= 55 % of its height)"""
    global _ref
    if _ref is not None: return _ref
    a = np.asarray(Image.open(os.path.join(ROOT, REF)).convert('RGBA'), np.float32); h = a.shape[0]
    m = a[..., 3] > 250; px = a[m][:, :3]; L = px @ LUM
    ramp = np.zeros((256, 3), np.float32); cnt = np.zeros(256)
    idx = np.clip(L.astype(int), 0, 255); np.add.at(ramp, idx, px); np.add.at(cnt, idx, 1)
    ok = cnt > 30; ramp[ok] /= cnt[ok, None]; xs = np.arange(256)
    hue = np.where(ok[:, None], ramp / np.maximum(xs[:, None], 1), np.nan)                     # colour / luminance (the sepia tint), smooth it, keep it past the ends
    for c in range(3):
        v = hue[:, c]; g = ~np.isnan(v); hue[:, c] = np.interp(xs, xs[g], v[g])
    hue = ndimage.gaussian_filter1d(hue, 6, axis=0); hue[:12] = hue[12]
    ramp = np.clip(hue * xs[:, None], 0, 255)
    lo = a[int(h * .55):]; ml = lo[..., 3] > 250; Ll = lo[ml][:, :3] @ LUM
    q = np.linspace(0, 1, 257); tq = np.percentile(Ll, q * 100)
    _ref = (ramp, q, tq); return _ref
class Tone:
    """fit on one picture (its own quantiles), apply to that picture and to every piece that must share the same stone"""
    def __init__(s, im, mix=.8, lift=1.22, cel=.5, flat=3.0, detail=.22, ink=.85, big=22, keep=.32):
        a = np.asarray(im.convert('RGBA'), np.float32); m = a[..., 3] > 200; L = a[m][:, :3] @ LUM
        ramp, q, tq = ref(); s.ramp = ramp; s.sq = np.percentile(L, q * 100); s.tq = np.clip(tq * lift, 0, 255); s.q = q; s.mix = mix; s.cel = cel; s.flat = flat; s.detail = detail; s.ink = ink; s.big = big; s.keep = keep
        if flat: L = s.base(np.asarray(im.convert('RGBA'), np.float32))[m]; s.sq = np.percentile(L, q * 100)
    def base(s, a):
        """the flat stone tone: the drawn picture's watercolour blotches (5-30 px) are pressed flat toward the big shading (tower sides, alcoves, arch)"""
        L = a[..., :3] @ LUM; al = (a[..., 3] > 0).astype(np.float32)
        def blur(v, sg): return ndimage.gaussian_filter(v * al, sg) / np.maximum(ndimage.gaussian_filter(al, sg), 1e-3)
        Ls = blur(L, s.flat); Lb = blur(L, s.big)
        return Lb + (Ls - Lb) * s.keep
    def lut(s):
        xs = np.arange(256, dtype=np.float32); qq = np.interp(xs, s.sq + np.arange(len(s.sq)) * 1e-4, s.q); Lt = np.interp(qq, s.q, s.tq)
        Lt = Lt * s.mix + xs * (1 - s.mix) * .9
        if s.cel:   # soft posterise toward the castle's flat cel tones (shadow / mid / lit)
            lv = np.array([8, 34, 62, 96, 128, 156, 186.]); k = np.abs(Lt[:, None] - lv[None]).argmin(1); Lt = Lt + (lv[k] - Lt) * s.cel
        return np.clip(Lt, 0, 255)
    def apply(s, im, keep_warm=True):
        a = np.asarray(im.convert('RGBA'), np.float32).copy(); rgb = a[..., :3]; L = rgb @ LUM
        Ls = s.base(a) if s.flat else L     # flat cel fills: the tone comes from the smoothed stone,
        Lt = np.interp(Ls, np.arange(256), s.lut()) + (L - Ls) * s.detail                    # only a little of the fine brush grain is kept
        Lc = np.clip(Lt, 0, 255); out = s.ramp[Lc.astype(int)] * (Lc / np.maximum(np.floor(Lc), 1))[..., None]
        if keep_warm:   # fire light, banners, embers keep their colour (only re-lit to the new luminance)
            sat = (rgb.max(2) - rgb.min(2)) / np.maximum(rgb.max(2), 1); w = np.clip((sat - .28) / .2, 0, 1)[..., None]
            out = out * (1 - w) + rgb * (Lt / np.maximum(L, 1))[..., None] * w
        if s.ink:   # the castle's black ink on the drawn lines (mortar, edges, cracks): found on the source, well under its neighbourhood
            loc = ndimage.uniform_filter(L, 9); k = np.clip((loc - L - 10) / 26, 0, 1); k = np.maximum(k, ndimage.grey_dilation(k, size=(2, 2)) * .8) * s.ink;   # a touch heavier, like the castle's pen
            out = out * (1 - k[..., None]) + INKC * k[..., None]
        a[..., :3] = np.clip(out, 0, 255); return Image.fromarray(a.astype(np.uint8), 'RGBA')
def ink_boost(im, amt=.7, thr=22, off=14):
    """the castle's black ink: dark thin lines (well under their neighbourhood) go near-black"""
    a = np.asarray(im, np.float32).copy(); L = a[..., :3] @ LUM; loc = ndimage.uniform_filter(L, 7)
    k = np.clip((loc - L - off) / thr, 0, 1) * amt * (a[..., 3] > 0); a[..., :3] = a[..., :3] * (1 - k[..., None]) + INKC * k[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
def drips(im, seed, dens=1.0, lmin=14, lmax=120, wmax=3.2, a0=.75, ledge=None, region=None, scale=1.0):
    """vertical black drip streaks hanging from ledges (strong dark -> light edges going down), tapered, clipped to the stone"""
    a = np.asarray(im, np.float32).copy(); h, w = a.shape[:2]; al = a[..., 3] / 255.; L = a[..., :3] @ LUM
    r = np.random.RandomState(seed)
    if ledge is None:
        gy = ndimage.sobel(ndimage.gaussian_filter(L, 1.0), 0)                         # bright under dark = the underside of a ledge / sill / merlon gap
        ledge = (gy > 60) & (al > .9)
        if region is not None: ledge &= region
    ys, xs = np.nonzero(ledge)
    if not len(ys): return im
    n = int(len(ys) * .012 * dens); pick = r.choice(len(ys), min(n, len(ys)), replace=False)
    D = np.zeros((h, w), np.float32)
    for i in pick:
        x0, y0 = xs[i], ys[i]; ln = r.uniform(lmin, lmax) * scale * (1.6 if r.rand() < .15 else 1); ww = r.uniform(.8, wmax) * scale; aa = r.uniform(.35, 1) * a0
        y1 = min(h, int(y0 + ln)); yy = np.arange(y0, y1); t = (yy - y0) / max(1, ln)
        wob = np.cumsum(r.normal(0, .12, len(yy))); xc = x0 + wob
        for j, y in enumerate(yy):
            hw = ww * (1 - t[j] * .7) / 2; xa, xb = int(math.floor(xc[j] - hw)), int(math.ceil(xc[j] + hw))
            if xb < 0 or xa >= w: continue
            v = aa * (1 - t[j] ** 1.6)
            D[y, max(0, xa):min(w, xb + 1)] = np.maximum(D[y, max(0, xa):min(w, xb + 1)], v)
    D = ndimage.gaussian_filter(D, (.6, .45)) * (al > .5)
    a[..., :3] = a[..., :3] * (1 - D[..., None]) + INKC * D[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
def clean_finish(p, cut=None, soot=False, moss=False, **k):
    """finish an inkart Pic the castle's way: no blotchy watercolour soot / moss washes (the castle's grime is its drip streaks), little paper wash / pooling"""
    p.post = [f for f in p.post if (soot or 'soot_post' not in f.__qualname__) and (moss or 'moss_post' not in f.__qualname__)]
    kw = dict(wash=.03, pool=.10, grain=.02, bleed=.25, desat=.22, sepia=.22); kw.update(k)
    return p.finish(cut=cut, **kw)
