"""Front/back walk+run KEY POSES for hero_v6 (handoff/claude/MOTION_NS_KEYPOSE_ko.md section 2-3, Linette prompts adapted to him + a sword).
edit-images-v2 edit_with_text, 10 gen each, same seed 7 for R and L. Output ns/key_<motion>_<R|L>.png. Skips existing files.
python3 ns_keys.py [motion ...]   motions: walk_south walk_north run_south run_north"""
import os, sys, base64
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(D, 'ns'); os.makedirs(O, exist_ok=True)
TAIL = ' Keep the exact same character design, colors, outfit, size and the long sword in his right hand pointing down, full body, no effects.'
P = {
 'walk_south': "Natural human walking pose toward the viewer, mid-stride contact: his {A} leg (on the {a} side of the image) steps forward toward the viewer with the heel touching the ground, that foot slightly lower in the image and slightly bigger; his {B} leg is behind him, knee slightly bent, standing on the toes. Feet about hip width apart, not crossed. Hips level, torso upright, a slight natural arm swing, the sword still pointing down.",
 'walk_north': "Natural human walking pose walking AWAY from the viewer, back view, seen from behind, we see his back and the back of his head, mid-stride contact: his {A} leg (on the {a} side of the image) steps forward away from the viewer, heel touching the ground, that foot slightly higher in the image; his {B} leg is behind him nearer the viewer, knee slightly bent, heel lifted so we see the sole of the boot. Feet about hip width apart, not crossed. Hips level, slight natural arm swing, the sword pointing down.",
 'run_south': "Natural human RUNNING pose toward the viewer, front view facing the viewer, face visible: his {A} knee ({a} side of the image) drives up and forward toward the viewer, thigh raised, foot off the ground under the knee; his {B} leg pushes off behind, nearly straight, only the toes touching the ground. Torso leaning slightly forward, both arms at his sides slightly pulled back, the sword held low pointing down. Not crossed, human proportions.",
 'run_north': "Natural human RUNNING pose running AWAY from the viewer, back view, seen from behind: his {A} knee ({a} side of the image) drives up and forward away from the viewer; his {B} leg behind him nearer the viewer is bent with the heel kicked up high so we see the sole of the boot. Torso leaning slightly forward, both arms at his sides slightly pulled back, the sword held low pointing down. Not crossed, human proportions.",
}
def side(motion, leg):   # his RIGHT leg = image left on the front view, image right on the back view
    front = motion.endswith('south')
    return ('left' if front else 'right') if leg == 'RIGHT' else ('right' if front else 'left')
def one(motion, key):
    out = os.path.join(O, f'key_{motion}_{key}.png')
    if os.path.exists(out): return motion, key, 'skip'
    A, B = ('RIGHT', 'LEFT') if key == 'R' else ('LEFT', 'RIGHT')
    desc = P[motion].format(A=A, B=B, a=side(motion, A)) + TAIL
    src = os.path.join(D, 'rot', 's4', 'south.png' if motion.endswith('south') else 'north.png')
    body = {'method': 'edit_with_text', 'edit_images': [{'image': {'type': 'base64', 'base64': pl.b64(src), 'format': 'png'}, 'width': 256, 'height': 256}],
            'image_size': {'width': 256, 'height': 256}, 'description': desc, 'seed': 7, 'no_background': True}
    r = pl.submit('/edit-images-v2', body)
    if not r.get('background_job_id'): return motion, key, 'submit failed ' + str(r)[:200]
    j = pl.wait(r['background_job_id'], every=6, limit=1800); rec = pl.log(f'key_{motion}_{key}', '/edit-images-v2', j); ims = pl.images(j)
    if ims: open(out, 'wb').write(ims[0])
    return motion, key, rec['status'], rec['n']
motions = sys.argv[1:] or list(P)
with ThreadPoolExecutor(8) as ex:
    for res in ex.map(lambda mk: one(*mk), [(m, k) for m in motions for k in 'RL']): print(*res, flush=True)
print('TOTAL hero_v6 usage', pl.total(), flush=True)
