"""Remove the coat tails from the hero_v6 rotation: edit-images-v2 (edit_with_text) on the unique directions in one call so they stay consistent.
Output -> rot/nocoat/<dir>.png"""
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(D, 'rot', 's2'); OUT = os.path.join(D, 'rot', 'nocoat'); os.makedirs(OUT, exist_ok=True)
DIRS = sys.argv[1:] or ['south', 'south-east', 'east', 'north-east', 'north']
DESC = ('Shorten the long navy coat into a waist-length fitted jacket that ends at the belt: remove all coat tails and the long front and back flaps below the belt. '
        'Below the belt show black fitted trousers, steel knee guards and the same brown knee boots. Keep everything else exactly the same: '
        'face, messy short black hair, gold pauldrons, gold trim on the jacket, belts and pouch, gloves, the sword in the right hand, pose, size and position.')
body = {'method': 'edit_with_text', 'description': DESC, 'image_size': {'width': 256, 'height': 256}, 'no_background': True, 'seed': 77,
        'edit_images': [{'image': {'type': 'base64', 'base64': pl.b64(os.path.join(SRC, f'{d}.png')), 'format': 'png'}, 'width': 256, 'height': 256} for d in DIRS]}
r = pl.submit('/edit-images-v2', body); print({k: (str(v)[:300]) for k, v in r.items() if k != 'last_response'})
if not r.get('background_job_id'): sys.exit(1)
j = pl.wait(r['background_job_id'], every=6); rec = pl.log('edit_nocoat_' + '+'.join(DIRS), '/edit-images-v2', j); print(rec)
ims = pl.images(j); print('images', len(ims))
for d, b in zip(DIRS, ims): open(os.path.join(OUT, f'{d}.png'), 'wb').write(b)
