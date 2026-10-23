"""Generate the plaza parts + one pro tileset (cobble <-> dirt, ragged meandering border). Skips existing files. FELT_CAP stops it."""
import os, sys, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
from specs_plaza import ASSETS, STYLE
D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, 'out', 'plaza'); os.makedirs(OUT, exist_ok=True)

def one(aid, size, desc, seed, extra):
    path = os.path.join(OUT, f'{aid}_s{seed}.png')
    if os.path.exists(path): return aid, seed, 'skip'
    body = dict({'description': desc + ', ' + STYLE, 'image_size': {'width': size[0], 'height': size[1]}, 'view': 'high top-down', 'seed': seed}, **extra)
    r = pl.submit('/map-objects', body)
    if not r.get('background_job_id'): return aid, seed, 'submit failed ' + str(r)[:200]
    j = pl.wait(r['background_job_id'], every=5); rec = pl.log(f'plaza:{aid}_s{seed}', '/map-objects', j)
    ims = pl.images(j)
    if ims: open(path, 'wb').write(ims[0])
    return aid, seed, rec['status'], rec['n']

def tileset():
    path = os.path.join(OUT, 'tiles_cobble_pro.json')
    if os.path.exists(path): return 'skip'
    r = pl.submit('/create-tileset', {'mode': 'pro', 'lower_description': 'packed dark earth with ash, pebbles and dry weeds',
        'upper_description': 'old worn grey-brown cobblestone plaza with cracked and missing stones', 'tile_size': {'width': 16, 'height': 16},
        'view': 'high top-down', 'transition_size': 0.0, 'raggedness': 0.6, 'boundary_amplitude': 0.25, 'seed': 33})
    if not r.get('background_job_id'): return 'submit failed ' + str(r)[:300]
    j = pl.wait(r['background_job_id'], every=6); rec = pl.log('plaza:tiles_cobble_pro', '/create-tileset', j)
    t = pl.req('GET', f"/tilesets/{r['tileset_id']}"); json.dump(t, open(path, 'w')); return j.get('status'), rec['n']

jobs = [(a, s, d, seed, ex) for a, s, d, seeds, ex in ASSETS for seed in seeds]
with ThreadPoolExecutor(6) as ex:
    ft = ex.submit(tileset)
    for res in ex.map(lambda x: one(*x), jobs): print(*res, flush=True)
    print('tileset', ft.result(), flush=True)
print('TOTAL usage (all Felt work)', pl.total(), flush=True)
