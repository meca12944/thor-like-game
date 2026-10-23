"""Keep the OLD mini proportions: edit the old front sprite (ref/old_front_256.png) into the v6 design with edit-image-pixen. 2 seeds."""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, 'ref')
DESC = ('Same body, head size, proportions, pose and position. Messy short spiky black hair, no long hair. Remove the cape. '
        'Dark navy high-collar jacket ending at the hips, thin gold trim, gold pauldrons on both shoulders, brown belt with pouch, '
        'black fingerless gloves, black trousers, steel knee guards, brown knee boots. Long steel sword held lowered in the right hand.')
def one(seed):
    r = pl.submit('/edit-image-pixen', {'image': {'type': 'base64', 'base64': pl.b64(os.path.join(R, 'old_front_256.png')), 'format': 'png'}, 'description': DESC, 'seed': seed, 'no_background': True})
    if not r.get('background_job_id'): return seed, str(r)[:300]
    j = pl.wait(r['background_job_id'], every=4); rec = pl.log(f'pixen_oldprop_s{seed}', '/edit-image-pixen', j); ims = pl.images(j)
    if ims: open(os.path.join(R, f'oldprop_south_s{seed}.png'), 'wb').write(ims[0])
    return seed, rec['status'], rec['n'], len(ims)
with ThreadPoolExecutor(2) as ex:
    for res in ex.map(one, [21, 22]): print(res, flush=True)
