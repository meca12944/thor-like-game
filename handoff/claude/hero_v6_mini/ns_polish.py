"""Front/back cycle polish (MOTION_NS_KEYPOSE_ko.md step 6, Linette polish.py rule):
1) one uniform vertical shift per clip so the lowest foot of the clip sits at y 192 (front foot a little below the 189 root, as drawn);
2) runs: airborne lift capped at 4 px (a frame whose lowest pixel is above 188 is moved down to 188). Walks keep the drawn ground.
python3 ns_polish.py -> ns/final_<motion>/000..007.png"""
import os, glob, json
from PIL import Image
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ns'); log = {}
for m in ['walk_south', 'walk_north', 'run_south', 'run_north']:
    F = sorted(glob.glob(f'{D}/cycle_{m}/*.png')); ims = [Image.open(f).convert('RGBA') for f in F]
    bots = [im.getbbox()[3] for im in ims]; shift = 192 - max(bots); out = f'{D}/final_{m}'; os.makedirs(out, exist_ok=True); dys = []
    for i, im in enumerate(ims):
        dy = shift; b = bots[i] + dy
        if m.startswith('run') and b < 188: dy += 188 - b
        c = Image.new('RGBA', (256, 256)); c.paste(im, (0, dy), im); c.save(f'{out}/{i:03d}.png'); dys.append(dy)
    log[m] = {'shift': shift, 'dy': dys, 'bottom': [c + d for c, d in zip(bots, dys)]}
    print(m, log[m])
json.dump(log, open(f'{D}/polish_log.json', 'w'), indent=1)
