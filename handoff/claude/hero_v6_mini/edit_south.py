"""Remove the coat tails on the south reference with edit-image-pixen (1 gen each), 2 seeds -> ref/nocoat_south_s<seed>.png"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, 'ref')
DESC = ('Shorten the long navy coat into a waist-length fitted jacket that ends at the belt: remove all coat tails and long flaps below the belt. '
        'Below the belt show black fitted trousers, steel knee guards and the same brown knee boots. Keep everything else the same: face, messy short black hair, '
        'gold pauldrons, gold trim, belts and pouch, gloves, the sword in the right hand, pose, size and position.')
def one(seed):
    r = pl.submit('/edit-image-pixen', {'image': {'type': 'base64', 'base64': pl.b64(os.path.join(R, 'south_ref_256.png')), 'format': 'png'},
                                         'description': DESC, 'seed': seed, 'no_background': True})
    if not r.get('background_job_id'): return seed, str(r)[:300]
    j = pl.wait(r['background_job_id'], every=4); rec = pl.log(f'pixen_nocoat_s{seed}', '/edit-image-pixen', j); ims = pl.images(j)
    if ims: open(os.path.join(R, f'nocoat_south_s{seed}.png'), 'wb').write(ims[0])
    return seed, rec['status'], rec['n'], len(ims)
with ThreadPoolExecutor(2) as ex:
    for res in ex.map(one, [11, 12]): print(res, flush=True)
