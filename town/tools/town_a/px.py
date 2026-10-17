# [town_a] procedural pixel-art primitives (art scale A = 0.6 px per world px = the 768x432 grid)
import numpy as np, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
A = 0.6
def hexc(h):
    h = h.lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), 255)
def ramp(*hs): return [hexc(h) for h in hs]
P = dict(
 roof_red=ramp('#5a2218','#7a3020','#9a3e28','#b44e32','#c9653f','#dc8458'),
 roof_slate=ramp('#262b38','#353c4d','#475064','#5b667c','#717e96','#909cb2'),
 roof_brown=ramp('#40291a','#583822','#73492b','#8d5c35','#a87244','#c08b58'),
 roof_green=ramp('#22382a','#2e4a36','#3c5e44','#4d7553','#638e66','#80aa80'),
 roof_teal=ramp('#1c3438','#27474c','#335c60','#437477','#588e8e','#78aaa6'),
 roof_thatch=ramp('#5a4220','#74572a','#8f6e36','#a98744','#c2a055','#d8bb70'),
 plaster=ramp('#9c8c6e','#b4a483','#c9b996','#dacbab','#e8dcc0','#f3ead6'),
 plaster_w=ramp('#a39b8c','#bcb4a4','#d0c8b8','#e0d9cb','#ece6da','#f6f2ea'),
 timber=ramp('#22160e','#33221490'[:7],'#4a3020','#5f3f28','#765034','#8c6440'),
 stone=ramp('#3e3c3a','#55524e','#6d6963','#86817a','#a09a90','#bab4a8'),
 stone_w=ramp('#4a4640','#635e56','#7c766c','#958e82','#aea698','#c6beae'),
 wood=ramp('#3a2414','#52331c','#6b4426','#855631','#a06b3e','#ba8550'),
 wood_d=ramp('#24160c','#342014','#462c1a','#5a3922','#6e482c','#845a38'),
 glass=ramp('#141c2c','#1f2c44','#2f4462','#466282','#6a8cae','#a8c8e0'),
 leaf=ramp('#13261a','#1d3a22','#2a5129','#3b6a31','#52843c','#71a04a','#94bd5e'),
 iron=ramp('#16161a','#26262c','#3a3a42','#55555e','#767680','#9a9aa4'),
 cloth_red=ramp('#5a1418','#7e1e22','#a42c2c','#c84438','#e0664c','#f29070'),
 cloth_blue=ramp('#16224a','#203268','#2c4688','#3c5ea4','#5a7ec0','#86a6d8'),
 cloth_green=ramp('#1c3a1c','#285226','#366c32','#4a8840','#64a452','#8cc070'),
 cloth_cream=ramp('#8c7c5c','#a89874','#c4b48e','#dacca8','#ece0c2','#faf2de'),
 cloth_purple=ramp('#2e1840','#42225a','#5a3078','#764296','#9460b2','#b488cc'),
 gold=ramp('#5a3a08','#7e5410','#a8741a','#d09a28','#ecc048','#fde488'),
 water=ramp('#16364a','#1e4a62','#2a627c','#3a7c96','#5a9cb2','#8cc4d4','#c8ecf4'),
 dirt=ramp('#4a3420','#5e442a','#745636','#8a6a44','#a08054','#b89a6c'),
 sand=ramp('#7a6646','#94805a','#ad986c','#c4b080','#d6c494','#e6d6aa'),
 hay=ramp('#6a5018','#8a6a20','#ab872c','#c8a43c','#dcbe54','#ecd67a'),
)
OUT = hexc('#1e140e')
def rng(seed): return random.Random(seed)
class Canvas:
    def __init__(s, w, h):
        s.w, s.h = int(w), int(h); s.a = np.zeros((s.h, s.w, 4), np.uint8)
    def put(s, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h: s.a[y, x] = c
    def rect(s, x0, y0, x1, y1, c):  # inclusive-exclusive
        x0, y0, x1, y1 = max(0,int(x0)), max(0,int(y0)), min(s.w,int(x1)), min(s.h,int(y1))
        if x1 > x0 and y1 > y0: s.a[y0:y1, x0:x1] = c
    def hline(s, x0, x1, y, c): s.rect(x0, y, x1, y+1, c)
    def vline(s, x, y0, y1, c): s.rect(x, y0, x+1, y1, c)
    def poly(s, pts, c):
        im = Image.new('L', (s.w, s.h), 0); ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
        m = np.asarray(im) > 0; s.a[m] = c; return m
    def ellipse(s, cx, cy, rx, ry, c):
        im = Image.new('L', (s.w, s.h), 0); ImageDraw.Draw(im).ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=255)
        m = np.asarray(im) > 0; s.a[m] = c; return m
    def blit(s, o, x, y):
        x, y = int(x), int(y); src = o.a if isinstance(o, Canvas) else o
        h, w = src.shape[:2]; X0, Y0 = max(0, x), max(0, y); X1, Y1 = min(s.w, x+w), min(s.h, y+h)
        if X1 <= X0 or Y1 <= Y0: return
        sub = src[Y0-y:Y1-y, X0-x:X1-x]; dst = s.a[Y0:Y1, X0:X1]
        al = sub[..., 3:4].astype(np.float32)/255
        da = dst[..., 3:4].astype(np.float32)/255
        oa = al + da*(1-al)
        rgb = (sub[..., :3]*al + dst[..., :3]*da*(1-al)) / np.maximum(oa, 1e-6)
        dst[..., :3] = rgb.astype(np.uint8); dst[..., 3:4] = (oa*255).astype(np.uint8)
    def shade(s, mask, k):  # multiply rgb in mask by k (k<1 darker)
        m = mask & (s.a[..., 3] > 0)
        s.a[..., :3][m] = np.clip(s.a[..., :3][m].astype(np.float32)*k, 0, 255).astype(np.uint8)
    def noise(s, amt, seed=1, mask=None):
        r = np.random.default_rng(seed).integers(-amt, amt+1, (s.h, s.w, 1))
        m = (s.a[..., 3] > 0) if mask is None else (mask & (s.a[..., 3] > 0))
        v = np.clip(s.a[..., :3].astype(int) + r, 0, 255).astype(np.uint8)
        s.a[..., :3][m] = v[m]
    def outline(s, c=OUT, inner=True):
        al = s.a[..., 3] > 0
        pad = np.pad(al, 1)
        edge = al & ~(pad[:-2,1:-1] & pad[2:,1:-1] & pad[1:-1,:-2] & pad[1:-1,2:])
        if inner:
            v = s.a[edge].astype(np.float32); v[:, :3] = v[:, :3]*0.45 + np.array(c[:3])*0.55; s.a[edge] = v.astype(np.uint8)
        return edge
    def img(s): return Image.fromarray(s.a, 'RGBA')
def lerpc(c1, c2, t): return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3)) + (255,)
def dk(c, k): return tuple(int(min(255, max(0, v*k))) for v in c[:3]) + (c[3] if len(c) > 3 else 255,)
FONT_B = '/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf'
FONT_S = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
def font(sz, serif=False):
    return ImageFont.truetype(FONT_S if serif else FONT_B, sz, index=1 if serif else 0) if serif else ImageFont.truetype(FONT_B, sz)
