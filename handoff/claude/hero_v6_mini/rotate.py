"""Phase 0: 8-direction rotation of hero_v6 from ref/south_ref_256.png (create-character-v3, reference mode). ~8 generations."""
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, 'rot'); os.makedirs(OUT, exist_ok=True)
DESC = os.environ.get('HERO_DESC') or ('young swordsman, messy spiky dark hair, navy high-collar jacket ending at the hips with gold embroidery down the centre, '
        'ornate gold pauldrons on both shoulders, brown leather bracers over black fingerless gloves, brown belt with a pouch, black trousers, '
        'small gold knee guards, brown buckled knee boots, long steel sword held lowered in the right hand. No cape, no coat tails. '
        'Same character, colours and proportions as the reference in every direction.')
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
body = {'description': DESC, 'reference_image': {'type': 'base64', 'base64': pl.b64(os.path.join(D, 'ref', os.environ.get('HERO_REF', 'south_ref_256.png'))), 'format': 'png'},
        'n_directions': 8, 'view': 'low top-down', 'seed': seed, 'no_background': True, 'name': 'hero_v6'}
r = pl.submit('/create-character-v3', body); print({k: v for k, v in r.items() if k != 'last_response'})
j = pl.wait(r['background_job_id'], every=6); rec = pl.log(f'rotate_s{seed}', '/create-character-v3', j); print(rec)
o = os.path.join(OUT, f's{seed}'); os.makedirs(o, exist_ok=True)
json.dump({'character_id': r.get('character_id'), 'job': {k: v for k, v in j.items() if k != 'last_response'}}, open(os.path.join(o, 'job.json'), 'w'), indent=1)
for i, im in enumerate((j.get('last_response') or {}).get('images') or []):
    nm = im.get('direction') or str(i); open(os.path.join(o, f'{nm}.png'), 'wb').write(base64.b64decode(im['base64']))
print('saved', os.listdir(o))
