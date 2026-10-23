"""v7 details on the old-proportion front (ref/v7_south_s31.png), edit-image-pixen, 2 seeds -> ref/v7_south_s<seed>.png"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, 'ref')
DESC = ('Keep everything exactly the same: body, head, proportions, pose, position, colours, jacket, pauldrons, bracers, boots and sword. '
        'Only add a small rounded gold knee guard on each knee, over the black trousers, just above the boots.')
assert len(DESC) <= 500, len(DESC)
def one(seed):
    r = pl.submit('/edit-image-pixen', {'image': {'type': 'base64', 'base64': pl.b64(os.path.join(R, 'v7_south_s31.png')), 'format': 'png'}, 'description': DESC, 'seed': seed, 'no_background': True})
    if not r.get('background_job_id'): return seed, str(r)[:300]
    j = pl.wait(r['background_job_id'], every=4); rec = pl.log(f'pixen_v7knee_s{seed}', '/edit-image-pixen', j); ims = pl.images(j)
    if ims: open(os.path.join(R, f'v7k_south_s{seed}.png'), 'wb').write(ims[0])
    return seed, rec['status'], rec['n'], len(ims)
with ThreadPoolExecutor(2) as ex:
    for res in ex.map(one, [41, 42]): print(res, flush=True)
