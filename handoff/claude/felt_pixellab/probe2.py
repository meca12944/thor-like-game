import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
STYLE = 'dark fantasy slum, soot-stained, worn, muted browns and greys, late afternoon light, 16-bit JRPG pixel art'
r = pl.submit('/map-objects', {'description': 'small poor weapon shop building made of soot-stained stone and old timber, sagging dark slate roof, wooden door at the front, a hanging sign with a crossed swords icon (no text), rack of rusty used swords and shields beside the door, ' + STYLE,
    'image_size': {'width': 192, 'height': 192}, 'view': 'high top-down', 'seed': 31})
j = pl.wait(r['background_job_id'], every=4); print(pl.log('bld_weapon_probe', '/map-objects', j))
for b in pl.images(j): open('out/bld/weapon_probe.png', 'wb').write(b)
r = pl.submit('/create-tileset', {'lower_description': 'packed dark dirt road with ash and pebbles', 'upper_description': 'worn grey cobblestone plaza', 'tile_size': {'width': 16, 'height': 16}, 'view': 'high top-down', 'transition_size': 0.0, 'seed': 21})
print('tileset submit', {k: v for k, v in r.items() if k != 'last_response'})
jid = r.get('background_job_id')
j = pl.wait(jid, every=6) if jid else r
json.dump(j, open('out/tiles/dirt_cobble_job.json', 'w'))
print(pl.log('tiles_dirt_cobble', '/create-tileset', j), list((j.get('last_response') or {}).keys())[:15])
