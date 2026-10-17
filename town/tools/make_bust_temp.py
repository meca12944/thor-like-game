"""TEMPORARY bust portraits until the illustrator's art (docs_art/bust/<id>/<expr>.png) arrives.
Crops the full-body standing art (town/assets/tachie/<id>_<expr>.png, 750x2150) to the upper body
(head to just below the waist) and scales it into the 1024x1280 bust canvas, then runs import_bust.py.
usage: python3 town/tools/make_bust_temp.py [--mode render|crop] [--out /tmp/bust_temp] [--no-import]
  render (default): re-renders the same procedural vector art (tools/tachie/view.html) with exactly that crop window
                    at 1.82x device scale -> crisp 1024x1280 (no raster upscaling). Falls back to crop if Chromium fails.
  crop            : crops the existing 750x2150 PNGs and upscales with Lanczos (no browser needed, slightly softer)."""
import argparse, os, subprocess, sys
from PIL import Image
T = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(T))
FULL = os.path.join(R, 'town', 'assets', 'tachie')
IDS = ['hero', 'a_tailor', 'h_mystic', 'g_dancer', 'f_diver', 'e_tailor', 'c_priest', 'd_yuna']
EX = ['neutral', 'smile', 'angry', 'sad', 'surprised', 'blush']
W, H = 1024, 1280
# crop window in full-body pixel space (750x2150): top of hair (hero y=21) to just below the waist (~y 900), 4:5
CY0, CH = 10, 890; CW = CH * W / H; CX0 = (750 - CW) / 2
FS = 1.25  # full-body PNG px per view.html CSS px (render.py ran at device scale 1.25)

def crop(out):
    for cid in IDS:
        for e in EX:
            p = os.path.join(FULL, '%s_%s.png' % (cid, e))
            if not os.path.exists(p): continue
            im = Image.open(p).convert('RGBA').crop((round(CX0), CY0, round(CX0 + CW), CY0 + CH)).resize((W, H), Image.LANCZOS)
            os.makedirs(os.path.join(out, cid), exist_ok=True); im.save(os.path.join(out, cid, e + '.png'))
        print('crop', cid)

def render(out):
    from playwright.sync_api import sync_playwright
    clip = {'x': CX0 / FS, 'y': CY0 / FS, 'width': CW / FS, 'height': CH / FS}; dsf = H / clip['height']
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 600, 'height': 1720}, device_scale_factor=dsf)
        for cid in IDS:
            for e in EX:
                pg.goto('file://%s/tachie/view.html?c=%s&e=%s' % (T, cid, e)); pg.wait_for_function('document.title=="ok"')
                os.makedirs(os.path.join(out, cid), exist_ok=True); dst = os.path.join(out, cid, e + '.png')
                pg.screenshot(path=dst, omit_background=True, clip=clip)
                im = Image.open(dst)
                if im.size != (W, H): im.convert('RGBA').resize((W, H), Image.LANCZOS).save(dst)
            print('render', cid)
        b.close()

if __name__ == '__main__':
    a = argparse.ArgumentParser(); a.add_argument('--mode', default='render', choices=['render', 'crop'])
    a.add_argument('--out', default='/tmp/bust_temp'); a.add_argument('--no-import', action='store_true'); o = a.parse_args()
    if o.mode == 'render':
        try: render(o.out)
        except Exception as ex: print('render failed (%s); falling back to crop' % ex); crop(o.out)
    else: crop(o.out)
    if not o.no_import: subprocess.check_call([sys.executable, os.path.join(T, 'import_bust.py'), '--src', o.out])
