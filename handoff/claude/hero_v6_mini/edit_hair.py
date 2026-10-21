"""v7 details on the old-proportion front (ref/v7k_south_s41.png), edit-image-pixen, 2 seeds -> ref/v7_south_s<seed>.png"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, 'ref')
DESC = ('Keep everything else exactly the same: face, body, head size, proportions, pose, position, outfit, colours and sword. '
        'Only change the hair: soft short dark hair with long bangs falling over the forehead and sweeping to the side, '
        'slightly messy, close to the head, no tall spikes, no volume on top, hair just covering the ears and the nape.')
assert len(DESC) <= 500, len(DESC)
def one(seed):
    r = pl.submit('/edit-image-pixen', {'image': {'type': 'base64', 'base64': pl.b64(os.path.join(R, 'v7k_south_s41.png')), 'format': 'png'}, 'description': DESC, 'seed': seed, 'no_background': True})
    if not r.get('background_job_id'): return seed, str(r)[:300]
    j = pl.wait(r['background_job_id'], every=4); rec = pl.log(f'pixen_hair_s{seed}', '/edit-image-pixen', j); ims = pl.images(j)
    if ims: open(os.path.join(R, f'hair_south_s{seed}.png'), 'wb').write(ims[0])
    return seed, rec['status'], rec['n'], len(ims)
with ThreadPoolExecutor(2) as ex:
    for res in ex.map(one, [51, 52]): print(res, flush=True)
