"""One-thing fix on a key pose with edit-image-pixen (1 gen per seed; it follows a single small change better than edit-images-v2).
python3 ns_pixfix.py <motion> <R|L> "<description>" seed [seed ...] -> ns/pix_<motion>_<k>_s<seed>.png"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); m, k, desc = sys.argv[1:4]; seeds = [int(s) for s in sys.argv[4:]]
assert len(desc) <= 500, len(desc)
src = os.path.join(D, 'ns', f'key_{m}_{k}_bad.png')
def one(seed):
    r = pl.submit('/edit-image-pixen', {'image': {'type': 'base64', 'base64': pl.b64(src), 'format': 'png'}, 'description': desc, 'seed': seed, 'no_background': True})
    if not r.get('background_job_id'): return seed, str(r)[:200]
    j = pl.wait(r['background_job_id'], every=4); rec = pl.log(f'pixfix_{m}_{k}_s{seed}', '/edit-image-pixen', j); ims = pl.images(j)
    if ims: open(os.path.join(D, 'ns', f'pix_{m}_{k}_s{seed}.png'), 'wb').write(ims[0])
    return seed, rec['status'], rec['n']
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(one, seeds): print(m, k, *r, flush=True)
