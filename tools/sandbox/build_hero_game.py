# Sandbox hero = the game's hero, always (owner 10-23 "샌드박스에 주인공은 항상 최신 업데이트된 주인공으로").
# Reads the live hero atlas (/*H8*/ JSON in test128/index.html + test128/assets/anim/hero8_*.webp) and writes a sandbox-format
# atlas (hero_game.json + hero_game_N.webp) with the sandbox's clip names. Left / ↙ / ↖ = the game's mirrored right / down / up art
# (same rule as the game: facing up/down -> front / back art, diagonals too). Run it whenever the hero changes, then republish the sandbox.
#   python3 tools/sandbox/build_hero_game.py <out_dir>
import json, os, sys
from PIL import Image, ImageOps
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'); G = os.path.join(R, 'test128'); OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
s = open(f'{G}/index.html').read(); i = s.index('/*H8*/const H8='); j = s.index('{', i); H8, _ = json.JSONDecoder().raw_decode(s[j:])
SH = [Image.open(f'{G}/assets/' + p).convert('RGBA') for p in H8['sheets']]; AN = H8['anims']
def src(base, d):  # sandbox direction -> (game clip, mirrored)
    side = {'right': ('right', False), 'left': ('right', True), 's': ('down', False), 'n': ('up', False), 'down': ('down', False), 'downl': ('down', True), 'up': ('up', False), 'upl': ('up', True)}[d]
    k = f'{base}_{side[0]}'
    return (k, side[1]) if k in AN else (f'{base}_right', d in ('left', 'downl', 'upl'))
want = {}
for base in ('idle', 'walk', 'run', 'dash', 'jump'):
    for d in ('right', 'left', 's', 'n', 'down', 'downl', 'up', 'upl'): want[f'{base}_{d}'] = src(base, d)
hurt = 'hurtys' if 'hurtys_right' in AN else 'hurt'; cast = 'cast_s1' if 'cast_s1_right' in AN else 'cast'
for nm, base in (('hurt', hurt), ('death', 'death'), ('rjump', 'rjump'), ('cast', cast)):
    want[f'{nm}_right'] = (f'{base}_right', False); want[f'{nm}_left'] = (f'{base}_right', True)
cells, anims, cache = [], {}, {}; sheet = Image.new('RGBA', (2048, 4096)); X = Y = rowH = 0
for name, (k, mir) in want.items():
    if k not in AN: continue
    fr = []
    for f in AN[k]:
        key = (f[0], f[1], mir)
        if key not in cache:
            x, y, w, h, ax, ay = H8['cells'][f[0]][f[1]][:6]; im = SH[f[0]].crop((x, y, x + w, y + h))
            if mir: im = ImageOps.mirror(im); ax = w - ax
            if X + w > 2048: X = 0; Y += rowH + 1; rowH = 0
            sheet.paste(im, (X, Y)); cells.append([X, Y, w, h, ax, ay]); cache[key] = len(cells) - 1; X += w + 1; rowH = max(rowH, h)
        fr.append([0, cache[key], f[2]])
    anims[name] = fr
sheet = sheet.crop((0, 0, 2048, Y + rowH + 1)); os.makedirs(OUT, exist_ok=True); sheet.save(f'{OUT}/hero_game_0.webp', lossless=True, quality=100)
json.dump({'_doc': 'built by tools/sandbox/build_hero_game.py from the game hero atlas (test128/index.html /*H8*/)', 'sheets': ['hero_game_0.webp'], 'cells': [cells], 'anims': anims}, open(f'{OUT}/hero_game.json', 'w'), separators=(',', ':'))
print(len(anims), 'clips', len(cells), 'cells', sheet.size)
