"""Generate every Felt exterior asset (2 seeds each) + the grass<->dirt tileset. Skips files that already exist.
FELT_CAP (default 200) stops new submissions once usage.jsonl reaches it."""
import os, sys, json, base64
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
from specs import ASSETS, STYLE
D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, 'out', 'assets'); os.makedirs(OUT, exist_ok=True)
SEEDS = [101, 202]

def one(a, seed):
    aid, (w, h), desc = a; path = os.path.join(OUT, f'{aid}_s{seed}.png')
    if os.path.exists(path): return aid, seed, 'skip'
    r = pl.submit('/map-objects', {'description': desc + ', ' + STYLE, 'image_size': {'width': w, 'height': h}, 'view': 'high top-down', 'seed': seed})
    if not r.get('background_job_id'): return aid, seed, 'submit failed ' + str(r)[:200]
    j = pl.wait(r['background_job_id'], every=5); rec = pl.log(f'{aid}_s{seed}', '/map-objects', j)
    ims = pl.images(j)
    if ims: open(path, 'wb').write(ims[0])
    return aid, seed, rec['status']

def tileset():
    path = os.path.join(D, 'out', 'tiles', 'grass_dirt.json')
    if os.path.exists(path): return 'skip'
    t1 = json.load(open(os.path.join(D, 'out', 'tiles', 'dirt_cobble.json')))['tileset']['tiles']
    dirt = next(t for t in t1 if all(v == 'lower' for v in t['corners'].values()))
    r = pl.submit('/create-tileset', {'lower_description': 'dead ashen grass with dry weeds and soot', 'upper_description': 'packed dark dirt road with ash and pebbles',
        'upper_reference_image': {'type': 'base64', 'base64': dirt['image']['base64'], 'format': 'png'},
        'tile_size': {'width': 16, 'height': 16}, 'view': 'high top-down', 'transition_size': 0.0, 'seed': 22})
    j = pl.wait(r['background_job_id'], every=6); pl.log('tiles_grass_dirt', '/create-tileset', j)
    t = pl.req('GET', f"/tilesets/{r['tileset_id']}"); json.dump(t, open(path, 'w')); return j.get('status')

jobs = [(a, s) for a in ASSETS for s in SEEDS]
with ThreadPoolExecutor(6) as ex:
    ft = ex.submit(tileset)
    for res in ex.map(lambda x: one(*x), jobs): print(*res, flush=True)
    print('tileset', ft.result(), flush=True)
print('TOTAL usage', pl.total(), flush=True)
