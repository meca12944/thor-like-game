"""Hero-matched proportions for every character sprite (768x432 grid).
Landmarks per frame: crown (top), chin (bottom of the face = start of the neck), split (top of the gap between
the legs = crotch for trousers / skirt hem for skirts), sole (baseline), shoulder width (widest body row in the
band just under the chin).  Source landmarks are auto-detected then checked on overlays (manual overrides
in OVR).  Each frame is remapped piecewise (head / torso / legs) so its landmarks land EXACTLY on the hero
FRONT idle landmarks, built at 8x the final size and box-downsampled 8:1 so landmark rows fall on pixel
boundaries; then palette / cleanup / outline like make_sprites.py.  Final sprites are measured again from
their pixels (not assumed) by measure_final()."""
import json, sys, os, csv, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
sys.path.insert(0, '/workspace/town-demo/tools/anim'); sys.path.insert(0, os.path.dirname(__file__))
from key import keyed, split_frames
import make_sprites as MS
SS = 8

def load_frames(path, n=3):
    rgb, fg = keyed(path); out = []
    for sg in split_frames(fg, n):
        if sg[0] == 'ids': m = np.isin(sg[2], sg[1])
        else:
            a, b = sg; m = np.zeros_like(fg); m[:, a:b] = fg[:, a:b]
        ys, xs = np.where(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        f = np.zeros((y1 - y0, x1 - x0, 4), np.float32); f[..., :3] = rgb[y0:y1, x0:x1]; f[..., 3] = m[y0:y1, x0:x1]
        out.append(f)
    return out

def steel(f):
    r, g, b = f[..., 0], f[..., 1], f[..., 2]; mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
    return (mx > 150) & (mx - mn < 45)
def skin(f):
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    return (f[..., 3] > .5) & (r > 120) & (r - b > 35) & (r > g + 8) & (g > 60) & (r - g < 110)

def body(f, props=None):
    """opaque body mask without weapons: drops steel and (optionally) given column ranges (staffs/spears)"""
    m = (f[..., 3] > .5) & (~steel(f) if props == 'hero' else True)
    lab, n = ndi.label(m)
    if n > 1: sz = ndi.sum(m, lab, range(1, n + 1)); m = lab == (np.argmax(sz) + 1)
    return m

def crown_sole(m, minrun=25):
    """crown = first row with an opaque run >= minrun px (skips thin staff / spear tips), sole = last opaque row"""
    rows = np.where(m.sum(1) >= 2)[0]; sole = int(rows[-1])
    for y in rows:
        xx = np.where(m[y])[0]; runs = np.split(xx, np.where(np.diff(xx) > 1)[0] + 1)
        if max(len(r) for r in runs) >= minrun: return int(y), sole
    return int(rows[0]), sole

def chin_auto(f, m, crown, sole):
    """neck start: skin-run width (around the face centre) drops below 55% of the face width"""
    H = sole - crown + 1; sk = skin(f) & m
    band = sk[crown:crown + int(H * .45)]
    if band.sum() < 20: return None
    ys, xs = np.where(band[: int(H * .25)]) if band[: int(H * .25)].sum() > 10 else np.where(band)
    cx = np.median(xs); w = []
    for y in range(band.shape[0]):
        row = band[y]; xx = np.where(row)[0]
        if not len(xx): w.append(0); continue
        j = np.argmin(abs(xx - cx)); a = b = xx[j]
        while a - 1 >= 0 and row[a - 1]: a -= 1
        while b + 1 < len(row) and row[b + 1]: b += 1
        w.append(b - a + 1 if abs(xx[j] - cx) < 0.06 * H else 0)
    w = ndi.median_filter(np.array(w, float), 3); top = int(np.argmax(w > 0)); fmax = 0
    for y in range(top, len(w)):
        fmax = max(fmax, w[y])
        if y - top > 0.06 * H and w[y] < .55 * fmax: return crown + y
    return None

def split_auto(m, crown, sole):
    """top of the gap between the legs at the feet centre column"""
    H = sole - crown + 1; low = m[sole - int(H * .12): sole + 1]
    ys, xs = np.where(low); 
    if not len(xs): return None
    # feet: two clusters -> gap centre
    cols = low.any(0); xx = np.where(cols)[0]
    gaps = [(xx[i], xx[i + 1]) for i in range(len(xx) - 1) if xx[i + 1] - xx[i] > 1]
    if not gaps: return None
    g = max(gaps, key=lambda t: t[1] - t[0]); cx = (g[0] + g[1]) // 2
    y = sole
    while y > crown and not m[y, cx - 0: cx + 1].any(): y -= 1
    return y + 1  # first row of the gap

def shoulder(m, chin, crown, sole, frac=(.03, .14)):
    H = sole - crown + 1; best = 0
    for y in range(chin + int(H * frac[0]), chin + int(H * frac[1]) + 1):
        xx = np.where(m[y])[0]
        if len(xx): best = max(best, xx[-1] - xx[0] + 1)
    return best

def remap(f, src, dst, Hd, head_cx=None, wscale=None, phase=0.0):
    """src/dst: (crown, chin, split, sole) rows; output height Hd (+margin) rows; widths scaled by
    the head factor in the head band ramping to wscale below the shoulders"""
    c0, c1, c2, c3 = src; d0, d1, d2, d3 = dst
    kh = (d1 - d0) / (c1 - c0); wscale = wscale or (d3 - d0) / (c3 - c0)
    W = int(f.shape[1] * max(kh, wscale)) + 8
    yo = np.arange(Hd, dtype=np.float32) + .5
    sy = np.where(yo < d1, c0 + (yo - d0) / kh,
         np.where(yo < d2, c1 + (yo - d1) * (c2 - c1) / (d2 - d1), c2 + (yo - d2) * (c3 - c2) / (d3 - d2)))
    ramp = np.clip((yo - d1) / ((d2 - d1) * .35), 0, 1); sx = kh + (wscale - kh) * ramp
    m = f[..., 3] > .5; cx = head_cx if head_cx is not None else np.where(m[c0:c1])[1].mean()
    X = np.arange(W, dtype=np.float32) + .5; ocx = W / 2 + phase
    SY = np.repeat(sy[:, None], W, 1); SX = cx + (X[None, :] - ocx) / sx[:, None]
    pm = f.copy(); pm[..., :3] *= pm[..., 3:4]
    out = np.dstack([ndi.map_coordinates(pm[..., c], [SY - .5, SX - .5], order=1, cval=0) for c in range(4)])
    out[..., :3] /= np.maximum(out[..., 3:4], 1e-3)
    return out

def to_final(hi, ncol_pal=None):
    """8:1 box downsample -> binary alpha; returns float rgba"""
    H, W = hi.shape[:2]; H8, W8 = H // SS * SS, W // SS * SS; hi = hi[:H8, :W8]
    pm = hi.copy(); pm[..., :3] *= pm[..., 3:4]
    pm = pm.reshape(H8 // SS, SS, W8 // SS, SS, 4).mean((1, 3))
    a = pm[..., 3]; rgb = pm[..., :3] / np.maximum(a[..., None], 1e-3)
    blur = np.dstack([ndi.uniform_filter(rgb[..., c] * (a > .3), 3) / np.maximum(ndi.uniform_filter((a > .3).astype(float), 3), 1e-3) for c in range(3)])
    rgb = np.clip(rgb + .5 * (rgb - blur), 0, 255)
    return np.dstack([rgb, (a > .5).astype(np.float32)])

def finish(frames, ncol):
    q, pal = MS.palette_quant(frames, ncol)
    return [MS.outline(MS.clean(f)) for f in q]

def trim(f):
    a = f[..., 3] > 0; ys, xs = np.where(a); return f[:, xs.min():xs.max() + 1] if len(xs) else f

def measure_final(f, view, ref_chin_frac=None):
    m = (f[..., 3] > 0) & ~steel(f); lab, n = ndi.label(m)
    if n > 1: sz = ndi.sum(m, lab, range(1, n + 1)); m = lab == (np.argmax(sz) + 1)
    rows = np.where(m.sum(1) >= 2)[0]; crown, sole = int(rows[0]), int(rows[-1])
    chin = chin_auto(f, m, crown, sole) if view != 'back' else None
    split = split_auto(m, crown, sole) if view != 'side' else None
    sh = shoulder(m, chin if chin else crown + round((sole - crown + 1) * (ref_chin_frac or .25)), crown, sole)
    return dict(crown=crown, chin=chin, split=split, sole=sole, H=sole - crown + 1,
                head=(chin - crown) if chin else None, legs=(sole + 1 - split) if split else None, shoulder=int(sh))
