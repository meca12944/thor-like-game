"""All-motion check sheet + video: idle/walk/run x 5 directions (s, se, e, ne, n; left = mirror).
python3 make_sheet.py -> hero_v6_all_sheet.png, hero_v6_all_motions.mp4 (each clip plays at its timing.json ticks, 60 ticks/s)"""
import os, glob, json, subprocess, tempfile
from PIL import Image, ImageDraw
DIRS = ['s', 'se', 'e', 'ne', 'n']
SRC = {'idle': {'s': 'anim/idle/south_pp', 'se': 'anim/idle/south-east_pp', 'e': 'anim/idle/east_pp', 'ne': 'anim/idle/north-east_pp', 'n': 'anim/idle/north_pp'},
       'walk': {'s': 'ns/final_walk_south', 'se': 'anim/walk/south-east_final', 'e': 'anim/walk/east_final', 'ne': 'anim/walk/north-east_final', 'n': 'ns/final_walk_north'},
       'run': {'s': 'ns/final_run_south', 'se': 'anim/run/south-east_final', 'e': 'anim/run/east_final', 'ne': 'anim/run/north-east_final', 'n': 'ns/final_run_north'}}
CW = 160; BG = (60, 70, 60, 255)
def clip(d):
    fs = sorted(glob.glob(d + '/*.png')); t = json.load(open(d + '/timing.json')) if os.path.exists(d + '/timing.json') else {}
    if 'source_frames' in t: fs = [fs[i] for i in t['source_frames']]
    tk = t.get('ticks', [6] * len(fs)); return [Image.open(f).convert('RGBA').crop((48, 56, 208, 216)) for f in fs], tk
C = {(m, d): clip(p) for m, r in SRC.items() for d, p in r.items()}
# sheet: one row per motion x direction, frames left to right
rows = [(k, v[0]) for k, v in C.items()]; W = max(len(f) for _, f in rows) * CW + 90
sh = Image.new('RGBA', (W, CW * len(rows)), BG); dr = ImageDraw.Draw(sh)
for r, ((m, d), fr) in enumerate(rows):
    dr.text((4, r * CW + 70), f'{m} {d}', fill='white')
    for i, f in enumerate(fr): sh.alpha_composite(f, (90 + i * CW, r * CW))
sh.save('hero_v6_all_sheet.png')
# video: grid motions x directions, 4 s, 60 ticks/s -> 30 fps (2 ticks per video frame)
tmp = tempfile.mkdtemp(); V = Image.new('RGBA', (CW * 5, CW * 3))
for vf in range(120):
    t = vf * 2; g = Image.new('RGBA', V.size, BG)
    for r, m in enumerate(SRC):
        for c, d in enumerate(DIRS):
            fr, tk = C[(m, d)]; tt = t % sum(tk); i = 0
            while tt >= tk[i]: tt -= tk[i]; i += 1
            g.alpha_composite(fr[i], (c * CW, r * CW))
    g.convert('RGB').resize((CW * 10, CW * 6), Image.NEAREST).save(f'{tmp}/{vf:04d}.png')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', f'{tmp}/%04d.png', '-pix_fmt', 'yuv420p', 'hero_v6_all_motions.mp4'], check=True)
print('ok', sh.size)
