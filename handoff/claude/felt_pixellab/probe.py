import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
bal = lambda: pl.req('GET', '/balance')['subscription']['generations']
STYLE = 'dark fantasy slum, soot-stained, worn, muted browns and greys, late afternoon light, 16-bit JRPG pixel art'
b0 = bal()
r = pl.submit('/map-objects', {'description': 'old wooden barrel with iron hoops, ' + STYLE, 'image_size': {'width': 64, 'height': 64}, 'view': 'high top-down', 'seed': 11})
print('map-object submit', {k: v for k, v in r.items() if k != 'last_response'})
j = pl.wait(r['background_job_id']); rec = pl.log('prop_barrel', '/map-objects', j); ims = pl.images(j)
for i, b in enumerate(ims): open(f'out/props/barrel_{i}.png', 'wb').write(b)
b1 = bal(); print('map-object', rec, 'balance diff', round(b0 - b1, 3), 'imgs', len(ims))
r = pl.submit('/create-tileset', {'lower_description': 'packed dark dirt road with ash and pebbles', 'upper_description': 'worn grey cobblestone plaza', 'tile_size': {'width': 16, 'height': 16}, 'view': 'high top-down', 'transition_size': 0.0, 'seed': 21})
print('tileset submit', {k: v for k, v in r.items() if k not in ('last_response',)})
jid = r.get('background_job_id') or r.get('id')
j = pl.wait(jid) if r.get('background_job_id') else r
json.dump({k: v for k, v in j.items()}, open('out/tiles/probe_tileset_job.json', 'w'))
rec = pl.log('tiles_dirt_cobble', '/create-tileset', j); b2 = bal()
print('tileset', rec, 'balance diff', round(b1 - b2, 3), 'keys', list((j.get('last_response') or j).keys())[:12])
