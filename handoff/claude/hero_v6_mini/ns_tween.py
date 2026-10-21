"""In-betweens between the two key poses (MOTION_NS_KEYPOSE_ko.md step 4): animate-with-text-v3, first_frame + last_frame, 4 frames (=4 gen, 5 images).
R->L and L->R per motion, same seed 7. Output ns/tw_<motion>_<RL|LR>/000.png.. Skips existing.
python3 ns_tween.py [motion ...]"""
import os, sys, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(D, 'ns')
ACT = {
 'walk_south': 'natural human walk toward the viewer: the back leg swings forward past the standing leg, knee bends as it passes, body rises slightly at the passing moment, gentle opposite arm swing, sword pointing down, front view the whole time, no effects',
 'walk_north': 'natural human walk away from the viewer, back view the whole time: the back leg swings forward past the standing leg, knee bends as it passes, body rises slightly at the passing moment, gentle opposite arm swing, sword pointing down, no effects',
 'run_south': 'natural human run toward the viewer, front view the whole time: the pushing leg swings through and its knee drives up while the other leg comes down and pushes off, brief moment with both feet off the ground, arms at his sides, sword held low pointing down, no effects',
 'run_north': 'natural human run away from the viewer, back view the whole time: the kicked-up heel swings through and that knee drives forward while the other leg pushes off and its heel kicks up showing the sole, arms at his sides, sword held low pointing down, no effects',
}
def one(motion, pair):
    out = os.path.join(O, f'tw_{motion}_{pair}'); 
    if os.path.isdir(out) and os.listdir(out): return motion, pair, 'skip'
    a, b = (('R', 'L') if pair == 'RL' else ('L', 'R'))
    img = lambda k: {'type': 'base64', 'base64': pl.b64(os.path.join(O, f'key_{motion}_{k}.png')), 'format': 'png'}
    r = pl.submit('/animate-with-text-v3', {'first_frame': img(a), 'last_frame': img(b), 'action': ACT[motion], 'frame_count': 4, 'seed': int(os.environ.get('TW_SEED', 7)), 'no_background': True})
    jid = r.get('background_job_id') or (r.get('background_job_ids') or [None])[0]
    if not jid: return motion, pair, 'submit failed ' + str(r)[:200]
    open(os.path.join(O, f'jobid_tw_{motion}_{pair}.txt'), 'w').write(jid)
    j = pl.wait(jid, every=6, limit=1800); rec = pl.log(f'tw_{motion}_{pair}', '/animate-with-text-v3', j); ims = pl.images(j)
    os.makedirs(out, exist_ok=True)
    for i, b_ in enumerate(ims): open(os.path.join(out, f'{i:03d}.png'), 'wb').write(b_)
    return motion, pair, rec['status'], rec['n'], len(ims)
motions = sys.argv[1:] or list(ACT)
with ThreadPoolExecutor(8) as ex:
    for res in ex.map(lambda mp: one(*mp), [(m, p) for m in motions for p in ('RL', 'LR')]): print(*res, flush=True)
print('TOTAL hero_v6 usage', pl.total(), flush=True)
