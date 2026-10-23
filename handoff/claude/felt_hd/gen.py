"""Felt HD test parts: PixelLab map-objects at ~3 px per world px (the hero is ~3.9; the old parts were 1).
python3 gen.py  (key from env PIXELLAB_API_KEY only; spend logged to ../felt_pixellab/usage.jsonl)"""
import os, sys, json, base64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'felt_pixellab'))
import pl
from specs import STYLE
B = 'building, front door facing the viewer (south), highly detailed, '
ASSETS = [
 ('atelier', (400, 360), B + "ruined royal tailor workshop of carved pale stone with a broken gilded arch, colorful faded cloth drapes patching the cracked walls and roof, a dress mannequin and bolts of cloth by the door, grey spider threads in the corners"),
 ('chapel',  (300, 400), B + "old ruined stone chapel with a square bell tower and a rusted bell, part of the roof collapsed, candle light in the arched door, soot stains"),
 ('burned',  (300, 260), "burned-out ruined two-room stone house seen from high top-down, roofless, charred black beams, rubble and ash inside, highly detailed"),
 ('fountain',(220, 170), "cracked old round stone fountain of the burned royal capital, broken statue on top, thin trickle of dark water, moss and soot, highly detailed"),
 ('lamp',    (64, 170),  "old iron street lamp post with a dim warm lantern, bent, highly detailed"),
 ('crates',  (110, 100), "stack of old wooden crates and a barrel, soot stained, highly detailed"),
 ('cart',    (150, 120), "broken wooden hand cart with cloth bundles, one wheel off, highly detailed"),
 ('deadtree',(180, 270), "dead leafless gnarled tree with charred bark, grey spider threads hanging from branches, highly detailed"),
 ('brazier', (80, 120),  "iron fire brazier on a tripod with a small flame and embers, highly detailed"),
]
for aid, (w, h), desc in ASSETS:
    out = f'parts/{aid}.png'
    if os.path.exists(out): continue
    r = pl.submit('/map-objects', {'description': desc + ', ' + STYLE, 'image_size': {'width': w, 'height': h}, 'view': 'high top-down', 'seed': int(os.environ.get('SEED', 7))})
    if '_http' in r: print(aid, r); continue
    j = pl.wait(r['background_job_id'], every=5); pl.log(f'hd_{aid}', '/map-objects', j)
    ims = pl.images(j)
    if ims: open(out, 'wb').write(ims[0]); print(aid, 'ok')
    else: print(aid, 'no image', str(j)[:200])
print('spent total (felt log)', pl.spent())
