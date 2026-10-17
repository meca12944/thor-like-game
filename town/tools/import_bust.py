"""Import upper-body bust portraits into the game.
Source  : docs_art/bust/<id>/<expr>.png   (illustrator deliverable: transparent PNG 1024x1280, see docs_art/bust/README.md)
Target  : town/assets/bust/<id>/<expr>.webp (default) or .png, + town/assets/bust/index.json (read by town/tachie.js)
usage   : python3 town/tools/import_bust.py [--src DIR] [--format webp|png] [--quality 90] [--keep]
  --src     extra/temporary source tree with the same <id>/<expr>.png layout (e.g. temp busts from make_bust_temp.py).
            Real art in docs_art/bust always wins over --src for the same id/expr.
  --format  webp (lossy RGB q=--quality, lossless-quality alpha; ~10x smaller) or png (optimized, lossless).
  --keep    do not delete stale files in town/assets/bust.
Ids/expressions: hero a_tailor h_mystic g_dancer f_diver e_tailor c_priest d_yuna x neutral smile angry sad surprised blush.
Missing expressions fall back to neutral at runtime."""
import argparse, json, os, sys
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ART = os.path.join(R, 'docs_art', 'bust'); OUT = os.path.join(R, 'town', 'assets', 'bust')
SIZE = (1024, 1280)
NAMES = {'hero': '필멸자', 'a_tailor': '리네트', 'h_mystic': '베일라', 'g_dancer': '자이라', 'f_diver': '마렌', 'e_tailor': '로자린드', 'c_priest': '이벨린', 'd_yuna': '유나'}
EX = ['neutral', 'smile', 'angry', 'sad', 'surprised', 'blush']
ALIAS = {'normal': 'neutral', 'happy': 'smile', 'mad': 'angry', 'cry': 'sad', 'shock': 'surprised', 'shy': 'blush'}

def load(p):
    im = Image.open(p).convert('RGBA')
    if im.size != SIZE:  # fit (keep aspect), anchored bottom-center, transparent padding
        print('  warn: %s is %dx%d, fitting into %dx%d' % (os.path.relpath(p, R), *im.size, *SIZE))
        s = min(SIZE[0] / im.width, SIZE[1] / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        c = Image.new('RGBA', SIZE, (0, 0, 0, 0)); c.paste(im, ((SIZE[0] - im.width) // 2, SIZE[1] - im.height)); im = c
    return im

def main():
    a = argparse.ArgumentParser(); a.add_argument('--src'); a.add_argument('--format', default='webp', choices=['webp', 'png'])
    a.add_argument('--quality', type=int, default=90); a.add_argument('--keep', action='store_true'); o = a.parse_args()
    idx = {'version': 1, 'size': list(SIZE), 'expressions': EX, 'alias': ALIAS, 'chars': {}}
    written = set(); tot = 0
    for cid, nm in NAMES.items():
        ex = {}; srcs = {}
        for e in EX:
            cands = [(os.path.join(ART, cid, e + '.png'), 'art')] + ([(os.path.join(o.src, cid, e + '.png'), 'temp')] if o.src else [])
            p, kind = next(((p, k) for p, k in cands if os.path.exists(p)), (None, None))
            if not p: continue
            os.makedirs(os.path.join(OUT, cid), exist_ok=True)
            fn = '%s/%s.%s' % (cid, e, o.format); dst = os.path.join(OUT, fn); im = load(p)
            if o.format == 'webp': im.save(dst, 'WEBP', quality=o.quality, alpha_quality=100, method=6)
            else: im.save(dst, 'PNG', optimize=True, compress_level=9)
            ex[e] = fn; srcs[e] = kind; written.add(dst); tot += os.path.getsize(dst)
        if ex:
            if 'neutral' not in ex: print('  warn: %s has no neutral (fallback uses first expression)' % cid)
            idx['chars'][cid] = {'name': nm, 'side': 'left' if cid == 'hero' else 'right', 'expr': ex, 'source': srcs}
    if not idx['chars']: sys.exit('no bust images found in %s%s' % (ART, ' or ' + o.src if o.src else ''))
    if not o.keep:
        for d, _, fs in os.walk(OUT):
            for f in fs:
                p = os.path.join(d, f)
                if f != 'index.json' and p not in written: os.remove(p); print('  removed stale', os.path.relpath(p, R))
    json.dump(idx, open(os.path.join(OUT, 'index.json'), 'w'), ensure_ascii=False, indent=1)
    n = sum(len(c['expr']) for c in idx['chars'].values()); art = sum(v == 'art' for c in idx['chars'].values() for v in c['source'].values())
    print('ok: %d images (%d real art, %d temp) -> %s, %.1f MB' % (n, art, n - art, os.path.relpath(OUT, R), tot / 1e6))

if __name__ == '__main__': main()
