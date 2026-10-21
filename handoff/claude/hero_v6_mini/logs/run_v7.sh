#!/bin/sh
# rotation (seed 4) from the v7 old-proportion reference, then the side run check
. ~/.config/pixellab/env
HERO_REF=south_ref_256_v7.png python3 rotate.py 4 > rotate_s4.log 2>&1 || exit 1
python3 - <<'PY'
import json, sys, urllib.request; sys.path.insert(0, '.'); import pl
j = json.load(open('rot/s4/job.json')); cid = j['character_id']; c = pl.req('GET', f'/characters/{cid}')
for d, u in c['rotation_urls'].items():
    open(f'rot/s4/{d}.png', 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read())
json.dump({'character_id': cid, 'seed': 4, 'ref': 'south_ref_256_v7.png'}, open('rot/pick.json', 'w'))
print('rotation saved', list(c['rotation_urls']))
PY
rm -rf anim/run/east
python3 anim.py run east > anim_run_east_v7.log 2>&1
python3 check_run.py anim/run/east 4 2.2 run_east_v7 > check_run_east_v7.txt 2>&1
echo ALLDONE
