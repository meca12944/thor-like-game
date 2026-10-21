"""Close the run loop: v3 interpolation from the last frame back to the first (custom_start_frame + end_frame), frame_count 4.
python3 seam.py <post dir> <out dir>  -> <out>/seam_000..003.png (raw); usage logged."""
import os, sys, json, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
CID = json.load(open(os.path.join(D, 'rot', 'pick.json')))['character_id']
fr = sorted(f for f in os.listdir(SRC) if f.endswith('.png'))
b64 = lambda f: {'type': 'base64', 'base64': pl.b64(os.path.join(SRC, f)), 'format': 'png'}
body = {'character_id': CID, 'mode': 'v3', 'action_description': 'continue the same running stride smoothly from the start pose to the end pose, '
        'sword held low in the right hand, STRICT SIDE VIEW, same character, no effects', 'frame_count': 4, 'directions': ['east'],
        'custom_start_frame': b64(fr[-1]), 'end_frame': b64(fr[0]), 'keep_first_frame': False, 'animation_name': 'run_v6_seam', 'seed': 605}
r = pl.submit('/characters/animations', body); print({k: str(v)[:200] for k, v in r.items()}, flush=True)
jid = r['background_job_ids'][0]; open(os.path.join(OUT, 'job_id.txt'), 'w').write(jid)
j = pl.wait(jid, every=8, limit=1800); rec = pl.log('run_east_seam', '/characters/animations', j); print(rec, flush=True)
urls = ((j.get('last_response') or {}).get('storage_urls') or {}).get('frames') or []
for i, u in enumerate(urls):
    open(os.path.join(OUT, f'seam_{i:03d}.png'), 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120).read())
print('saved', len(urls))
