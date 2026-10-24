"""Clean procedural cobble / flagstone road layer (no PixelLab): consistent stone size, rounded worn stones,
dirt mortar, concentric rings on a plaza, stones thinning out at the edges so the road melts into the dirt.
All sizes are in ground-image pixels (48 px per 16 px map cell for hd.D=3)."""
import numpy as np
from scipy import ndimage
def h2(a, b, s=0.0):
    v = np.sin(a * 12.9898 + b * 78.233 + s * 37.719) * 43758.5453
    return v - np.floor(v)
def _sdf(cx, cy, hx, hy, r):
    qx = np.abs(cx) - (hx - r); qy = np.abs(cy) - (hy - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
def bricks(H, W, rh=16, sw=21, jit=6, seed=1):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    row = np.floor(yy / rh); off = h2(row, 3.1, seed) * sw
    xs = xx + off; k = np.floor(xs / sw)
    def J(kk): return (h2(row, kk, seed + 1) - .5) * jit
    left = k * sw + J(k); m = xs < left; k = np.where(m, k - 1, k); left = k * sw + J(k)
    right = (k + 1) * sw + J(k + 1); w = right - left
    u = xs - left; v = yy - row * rh
    sid = row * 1013 + k
    ctr_x = left + w / 2 - off; ctr_y = row * rh + rh / 2
    return u - w / 2, v - rh / 2, w / 2 - 1.1, np.full_like(w, rh / 2 - 1.1), sid, ctr_x, ctr_y
def rings(H, W, c, rh=16, sw=21, seed=2):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = xx - c[0]; dy = (yy - c[1]); r = np.hypot(dx, dy); th = np.arctan2(dy, dx) + np.pi
    ring = np.floor(r / rh); rm = (ring + .5) * rh
    n = np.maximum(6, np.round(2 * np.pi * rm / sw)); ph = h2(ring, 5.3, seed)
    t = th / (2 * np.pi) * n + ph; seg = np.floor(t)
    arc = 2 * np.pi * rm / n
    u = (t - seg - .5) * arc; v = r - rm
    sid = 50000 + ring * 997 + seg
    ta = (seg + .5 - ph) / n * 2 * np.pi - np.pi
    return u, v, arc / 2 - 1.1, np.full_like(u, rh / 2 - 1.1), sid, c[0] + rm * np.cos(ta), c[1] + rm * np.sin(ta)
def render(base, road, plaza=None, plaza_r=0, seed=3, stone=(124, 114, 100), lane=None):
    """base: HxWx3 float ground. road: HxW float coverage 0..1 (cobble). lane: coverage of packed-dirt lanes.
    plaza: (cx, cy) px centre, plaza_r px radius (ring pattern inside). returns new image"""
    H, W = road.shape; img = base.astype(np.float32).copy()
    if lane is not None:  # packed earth lanes: smooth, a bit lighter and warmer, soft edge
        lm = np.clip((lane - .25) / .5, 0, 1)[..., None]
        packed = ndimage.uniform_filter(base, size=(9, 9, 1)) * np.array([1.07, 1.04, .99]) + 2
        img = img * (1 - lm * .7) + packed * lm * .7
    cx, cy, hx, hy, sid, sx, sy = bricks(H, W, seed=seed)
    if plaza is not None:
        P = rings(H, W, plaza, seed=seed + 1)
        yy, xx = np.mgrid[0:H, 0:W]; inside = np.hypot(xx - plaza[0], yy - plaza[1]) < plaza_r
        cx, cy, hx, hy, sid, sx, sy = [np.where(inside, p, b) for p, b in zip(P, (cx, cy, hx, hy, sid, sx, sy))]
    d = _sdf(cx, cy, hx, hy, 4.2)
    # coverage at the stone centre -> whole stones drop out at the road edge (worn edge)
    rc = road[np.clip(sy.astype(int), 0, H - 1), np.clip(sx.astype(int), 0, W - 1)]
    rn = h2(sid, 1.7, seed); keep = rc + (rn - .5) * .42 > .5
    sunk = np.clip((rc - .5) / .3, 0, 1)            # edge stones are half buried
    # packed earth under and around the road
    bm = np.clip((road - .15) / .5, 0, 1)[..., None]
    earth = ndimage.uniform_filter(base, size=(7, 7, 1)) * np.array([1.08, 1.05, .99])
    img = img * (1 - bm * .7) + earth * bm * .7
    # stone colour: one flat tone per stone, small variation, soft rim darkening, light from the top
    var = .93 + .14 * h2(sid, 9.1, seed); warm = (h2(sid, 4.4, seed) - .5) * .06
    col = np.stack([stone[0] * var * (1 + warm), stone[1] * var, stone[2] * var * (1 - warm)], -1)
    rim = np.clip(-d / 3.0, 0, 1)
    shade = .76 + .24 * rim
    top = (cy < 0) & (d > -3.2) & (d < 0); bot = (cy > 0) & (d > -2.6) & (d < 0)
    shade = shade + top * .09 - bot * .07
    col = col * shade[..., None]
    a = (d < 0) & keep
    alpha = np.where(a, .55 + .45 * sunk, 0.0)[..., None]
    col = col * (.82 + .18 * sunk[..., None]) + earth * (1 - (.82 + .18 * sunk[..., None])) * 0
    img = img * (1 - alpha) + col * alpha
    # mortar: darker earth in the joints inside the road
    jm = ((d >= 0) & (road > .45))[..., None] * .35
    img = img * (1 - jm) + img * .52 * jm
    return np.clip(img, 0, 255)
