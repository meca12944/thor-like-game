"""v7 details on the old-proportion front (ref/oldprop_south_s22.png), edit-image-pixen, 2 seeds -> ref/v7_south_s<seed>.png"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, 'ref')
DESC = ('Keep body, head size, proportions, pose and position. Gold knee guards instead of steel. Brown leather bracers on both forearms over black gloves. '
        'Ornate gold pauldrons. Thin gold embroidery down the centre of the navy high-collar jacket, jacket ends at the hips, no coat tails. '
        'Dark brown-black messy hair. Brown knee-high boots with buckles.')
assert len(DESC) <= 500, len(DESC)
def one(seed):
    r = pl.submit('/edit-image-pixen', {'image': {'type': 'base64', 'base64': pl.b64(os.path.join(R, 'oldprop_south_s22.png')), 'format': 'png'}, 'description': DESC, 'seed': seed, 'no_background': True})
    if not r.get('background_job_id'): return seed, str(r)[:300]
    j = pl.wait(r['background_job_id'], every=4); rec = pl.log(f'pixen_v7_s{seed}', '/edit-image-pixen', j); ims = pl.images(j)
    if ims: open(os.path.join(R, f'v7_south_s{seed}.png'), 'wb').write(ims[0])
    return seed, rec['status'], rec['n'], len(ims)
with ThreadPoolExecutor(2) as ex:
    for res in ex.map(one, [31, 32]): print(res, flush=True)
