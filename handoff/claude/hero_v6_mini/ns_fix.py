"""Fix one key pose (MOTION_NS_KEYPOSE_ko.md step 3): edit-images-v2 on the bad key itself, 'keep this exact pose, only change ...'. 10 gen.
python3 ns_fix.py <motion> <R|L> "<description>" [seed]  -> overwrites ns/key_<motion>_<k>.png (old kept as _bad.png)"""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); m, k, desc = sys.argv[1:4]; seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
f = os.path.join(D, 'ns', f'key_{m}_{k}.png'); bad = f.replace('.png', '_bad.png')
if not os.path.exists(bad): shutil.copy(f, bad)
body = {'method': 'edit_with_text', 'edit_images': [{'image': {'type': 'base64', 'base64': pl.b64(bad), 'format': 'png'}, 'width': 256, 'height': 256}],
        'image_size': {'width': 256, 'height': 256}, 'description': desc, 'seed': seed, 'no_background': True}
r = pl.submit('/edit-images-v2', body); j = pl.wait(r['background_job_id'], every=6, limit=1800)
rec = pl.log(f'fix_{m}_{k}', '/edit-images-v2', j); ims = pl.images(j)
if ims: open(f, 'wb').write(ims[0])
print(rec, len(ims))
