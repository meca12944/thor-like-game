"""castle_far: the royal castle far view = the illustrator's hand-drawn picture + its 16-frame loop (owner 10-25
「일러스트 작가랑 손그림풍 성 원화 새로 그려서 써라」「그림이 움직이게 해달라」). Replaces the code-drawn castle_fortress.py (now in tools/hd/_archive_old_felt).

Source (not in the repo, ~40 MB): the delivery folder (castle_art/: castle_far_back.png / castle_far_front.png 2560x1440 RGBA no sky,
window_glow_mask_gray.png, anim/fx_glow, anim/fx_smoke, anim/fx_crows 16 frames 8 fps). castle_far_src/ keeps the README + metadata.
Game files (test128/assets/world/castle_far/):
  castle_far.webp        the whole castle (back layer), 1920x1080
  castle_far_front.webp  the outer wall band only (y >= 1345 in the 2560 picture), drawn on top with a touch of extra parallax
  castle_glow_4x4.webp   lit windows (flicker), 16 frames, 4x4 cells, cropped to the window box, 0.75 scale (= the base picture)
  castle_fx_4x4.webp     smoke + ash + crows, 16 frames, 4x4 cells, cropped to their box, 0.5 scale
world.js drawBackdrop draws base -> glow cell -> fx cell -> front at the same fit/scale; frame = floor(t * fps) % 16.
usage: python3 tools/hd/fields/castle_far.py [src dir]   (rebuilds the webp files and patches the backdrop in maps/felt.json + maps/prologue_grave.json)"""
import os, sys, json
from PIL import Image
import numpy as np
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..')
OUT = 'assets/world/castle_far/'
SW, SH = 2560, 1440          # source picture size
BASE_S = .75                 # 2560 -> 1920
TIP, FOOT = 17, 1439         # first / last opaque row in the source
BAND = 1345                  # the outer wall band starts here (front layer)
HIDE = 1372                  # source row that sits on the near horizon: the band below it hides behind Felt's wall / the field's lip
X0, X1 = 20, 2537            # silhouette columns
N, FPS = 16, 8

def rel(p): return os.path.join(ROOT, p)

def bbox_union(paths):
    bb = None
    for p in paths:
        b = Image.open(p).getchannel('A').point(lambda v: 255 if v > 2 else 0).getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    return bb

def sheet(frames, box, s, pad=4):
    x0, y0, x1, y1 = box; x0 = max(0, x0 - pad); y0 = max(0, y0 - pad); x1 = min(SW, x1 + pad); y1 = min(SH, y1 + pad)
    cw, ch = int(round((x1 - x0) * s)), int(round((y1 - y0) * s))
    sh = Image.new('RGBA', (cw * 4, ch * 4))
    for i, f in enumerate(frames): sh.paste(f.crop((x0, y0, x1, y1)).resize((cw, ch), Image.LANCZOS), ((i % 4) * cw, (i // 4) * ch))
    a = np.array(sh); a[a[..., 3] < 3] = 0                    # clean near-zero alpha (smaller file, no grey fringe)
    return Image.fromarray(a), {'sx': x0, 'sy': y0, 'sw': x1 - x0, 'sh': y1 - y0, 'cw': cw, 'ch': ch, 'cols': 4, 'n': N}

def build(src):
    os.makedirs(rel(OUT), exist_ok=True)
    back = Image.open(src + '/castle_far_back.png').convert('RGBA')
    back.resize((int(SW * BASE_S), int(SH * BASE_S)), Image.LANCZOS).save(rel(OUT + 'castle_far.webp'), 'WEBP', quality=88, method=6, alpha_quality=90)
    front = Image.open(src + '/castle_far_front.png').convert('RGBA').crop((0, BAND - 2, SW, SH))
    front.resize((int(SW * BASE_S), int(front.height * BASE_S)), Image.LANCZOS).save(rel(OUT + 'castle_far_front.webp'), 'WEBP', quality=88, method=6, alpha_quality=90)
    A = src + '/anim/'
    gm = np.array(Image.open(src + '/window_glow_mask_gray.png').convert('L')) > 0
    glow = []
    for t in range(N):                                            # lit window pixels only (the flicker); everything else transparent
        g = np.array(Image.open(A + 'fx_glow/glow_%02d.png' % t).convert('RGBA')); g[~gm] = 0; glow.append(Image.fromarray(g))
    fx = []
    for t in range(N):
        f = Image.open(A + 'fx_smoke/smoke_%02d.png' % t).convert('RGBA'); f.alpha_composite(Image.open(A + 'fx_crows/crows_%02d.png' % t).convert('RGBA')); fx.append(f)
    gb = Image.fromarray((gm * 255).astype(np.uint8)).getbbox()
    fb = None
    for f in fx:
        b = f.getchannel('A').point(lambda v: 255 if v > 2 else 0).getbbox()
        if b: fb = b if fb is None else (min(fb[0], b[0]), min(fb[1], b[1]), max(fb[2], b[2]), max(fb[3], b[3]))
    gs, gmeta = sheet(glow, gb, BASE_S); gs.save(rel(OUT + 'castle_glow_4x4.webp'), 'WEBP', quality=90, method=6, alpha_quality=95)
    fs, fmeta = sheet(fx, fb, .5); fs.save(rel(OUT + 'castle_fx_4x4.webp'), 'WEBP', quality=86, method=6, alpha_quality=85)
    meta = {'glow': gmeta, 'fx': fmeta}
    json.dump(meta, open(rel(OUT + 'castle_far.json'), 'w'), indent=1)
    return meta

def backdrop(kind, meta=None):
    """the hd.backdrop entry (picture px = the 2560x1440 source; world.js scales by b.iw / image width)."""
    meta = meta or json.load(open(rel(OUT + 'castle_far.json')))
    BG = '#24201e'
    b = {'img': OUT + 'castle_far.webp', 'iw': SW, 'ih': SH, 'D': 1, 'ppt': 16, 'ax': (X0 + X1) / 2, 'ay': HIDE, 'cy0': TIP, 'bw': X1 - X0 + 1,
         'front': {'img': OUT + 'castle_far_front.webp', 'y': BAND - 2, 'px': .03},
         'anim': {'fps': FPS, 'n': N, 'layers': [dict(meta['glow'], img=OUT + 'castle_glow_4x4.webp'), dict(meta['fx'], img=OUT + 'castle_fx_4x4.webp')]},
         'sky': BG, 'floor': BG, 'side': BG, 'edge': .07,
         # 살아 있는 성 (사장님 10-25, 팀 회의 교본 6-6): 핵 심장 박동 빛 · 굳은 기사의 잿빛 횃불 순찰 [x0, x1, 속도, 위상, 성곽y?] · 먼 종 [x, y, 색, 반지름, 주기초] — 그림 좌표(2560)
         'alive': {'core': [1259, 92, '#6cc4ff', 90], 'torch': [[160, 760, 34, 0], [700, 1250, 26, .4], [1180, 1660, 30, .7], [1900, 2380, 22, .2], [620, 1080, 24, .3, 1146], [1100, 1560, 20, .6, 1182], [240, 560, 18, .1, 1188]],
                   'ty': 1352, 'bell': [1300, 1060, '#ffe2b0', 60, 26]}}
    if kind == 'felt':      # behind the capital wall: shows through the breaches, the whole castle from the gate vista
        b.update({'x': 75, 'px': .92, 'fit': [.02, 14, .9, .97, 1.04, .33], 'clipY': 26.5, 'fog': [[SH * .80, SH * .12, .07, 5], [SH * .90, SH * .12, .10, 9]]})
    else:                   # 무명 무덤가: past the end of the road / from the crest, over the field's lip
        b.update({'x': 46, 'px': .95, 'fit': [.02, 13.05, .25, .97, 1.04], 'clipY': 12.7, 'lift': .4, 'fog': [[SH * .84, SH * .10, .08, 5], [SH * .92, SH * .09, .11, -4]]})
    return b

def patch_maps(meta):
    for f, kind in (('maps/felt.json', 'felt'), ('maps/prologue_grave.json', 'pg')):
        p = rel(f); j = json.load(open(p)); h = j['hd'] if 'hd' in j else j['hds'][0]
        old = h.get('backdrop') or {}; nb = backdrop(kind, meta)
        for k in ('x', 'px', 'fit', 'clipY'): nb[k] = old.get(k, nb[k])   # keep the map's own placement (set by its build script)
        h['backdrop'] = nb; json.dump(j, open(p, 'w'), ensure_ascii=False, indent=1); print('patched', f)

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else '/workspace/map_review/castle_art'
    m = build(src); print(json.dumps(m)); patch_maps(m)
    for n in sorted(os.listdir(rel(OUT))): print(n, os.path.getsize(rel(OUT + n)))
