"""Front/back cycle polish v2 (replaces the per-frame lift cap of ns_polish.py, which made the body hop by up to 6 px out of rhythm):
the feet of a front/back view are drawn at different depths (front foot lower), so the BODY is the reference, not the lowest pixel.
1) one uniform shift per clip so the lowest foot of the clip sits at y 192;
2) head height follows a smooth rhythm: per frame, measure the head top; target = clip mean + a two-bump curve (one rise per step,
   walk 1 px, run 2 px, highest at the passing frames 2 and 6 of 8); move each frame by (target - measured), at most 6 px.
python3 ns_polish2.py [motion ...] -> ns/final_<motion>/ (+ polish2.json)"""
import os, sys, glob, json, math
from PIL import Image
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ns'); log = {}
for m in sys.argv[1:] or ['walk_south', 'walk_north', 'run_south', 'run_north']:
    ims = [Image.open(f).convert('RGBA') for f in sorted(glob.glob(f'{D}/cycle_{m}/*.png'))]; n = len(ims)
    shift = 192 - max(im.getbbox()[3] for im in ims); tops = [im.getbbox()[1] + shift for im in ims]
    amp = 2 if m.startswith('run') else 1; mean = sum(tops) / n
    tgt = [mean - amp * abs(math.sin(2 * math.pi * (i - 0) / n)) for i in range(n)]   # rises at frames 2 and 6 (passing), lowest at the keys 0 and 4
    out = f'{D}/final_{m}'; os.makedirs(out, exist_ok=True); dys = []
    for i, im in enumerate(ims):
        d = max(-6, min(6, round(tgt[i] - tops[i]))); dy = shift + d
        c = Image.new('RGBA', (256, 256)); c.paste(im, (0, dy), im); c.save(f'{out}/{i:03d}.png'); dys.append(dy)
    log[m] = {'shift': shift, 'dy': dys, 'head_top': [im.getbbox()[1] + dy for im, dy in zip(ims, dys)]}
    print(m, log[m])
json.dump(log, open(f'{D}/polish2.json', 'w'), indent=1)
