"""Phase A/B animations for hero_v6 (characters/animations, mode v3, 1 job per direction). Key from env only.
python3 anim.py <anim> [dir ...]   e.g. python3 anim.py run east     (dirs: south, south-east, east, north-east, north)
Frames -> anim/<anim>/<dir>/000.png ...; usage -> usage.jsonl. HERO_CAP stops new jobs."""
import os, sys, json, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pl
D = os.path.dirname(os.path.abspath(__file__)); P = json.load(open(os.path.join(D, 'plan.json')))
CID = json.load(open(os.path.join(D, 'rot', 'pick.json')))['character_id']
COMMON = ('Same character as the rotation: messy spiky dark hair, navy hip-length jacket with gold trim, ornate gold pauldrons, brown bracers, gold knee guards, '
          'long sword in the right hand. Face, outfit and proportions identical every frame. No cape and no coat tails, '
          'nothing flaps. Bold outlines, no flickering pixels. NO glow, sparks, dust or effects. Keep facing the same direction the whole time.')
SIDE = ' STRICT SIDE VIEW every frame, the chest never turns toward the camera.'
BACK = ' BACK VIEW every frame, the face is never shown, sword and arms stay visible.'
name = sys.argv[1]; spec = P['phaseA'].get(name) or P['phaseB'][name]
dirs = sys.argv[2:] or [P['dirs'][d] for d in spec['dirs']]
seed = int(os.environ.get('ANIM_SEED') or {'idle': 601, 'walk': 602, 'run': 603}.get(name, 610))
jobs = {}; gid = None
for d in dirs:
    extra = SIDE if d == 'east' else BACK if d == 'north' else ''
    body = {'character_id': CID, 'mode': 'v3', 'action_description': spec.get('action', name) + '. ' + COMMON + extra,
            'frame_count': spec['frames'], 'directions': [d], 'animation_name': f'{name}_v6', 'keep_first_frame': False, 'seed': seed}
    if gid: body['animation_group_id'] = gid
    r = pl.submit('/characters/animations', body)
    if not r.get('background_job_ids'): print('submit failed', d, str(r)[:300]); continue
    gid = gid or r.get('animation_group_id'); jobs[d] = r['background_job_ids'][0]; print('submitted', name, d, flush=True)
for d, jid in jobs.items():
    j = pl.wait(jid, every=8, limit=1800); rec = pl.log(f'{name}_{d}', '/characters/animations', j)
    o = os.path.join(D, 'anim', name, d); os.makedirs(o, exist_ok=True)
    urls = ((j.get('last_response') or {}).get('storage_urls') or {}).get('frames') or []
    for i, u in enumerate(urls):
        open(os.path.join(o, f'{i:03d}.png'), 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120).read())
    print('done', name, d, rec['status'], rec['n'], len(urls), 'frames', flush=True)
print('TOTAL hero_v6 usage', pl.total())
