"""Copy the confirmed clips into one game-ready layout: final/<motion>/<direction>/000.png.. + timing.json,
final/rot/<8 directions>.png, final/manifest.json. 256 canvas, feet root (128, 189); west / south-west / north-west = mirror of east / south-east / north-east.
python3 export_final.py"""
import os, glob, json, shutil
from make_sheet_src import SRC
NAME = {'s': 'south', 'se': 'south-east', 'e': 'east', 'ne': 'north-east', 'n': 'north'}
shutil.rmtree('final', ignore_errors=True); man = {'canvas': 256, 'foot_root': [128, 189], 'mirror': {'west': 'east', 'south-west': 'south-east', 'north-west': 'north-east'}, 'clips': {}}
for m, r in SRC.items():
    for d, p in r.items():
        o = f'final/{m}/{NAME[d]}'; os.makedirs(o)
        fs = sorted(glob.glob(p + '/*.png')); t = json.load(open(p + '/timing.json'))
        if 'source_frames' in t: fs = [fs[i] for i in t['source_frames']]   # idle ping-pong expanded to plain frames
        for i, f in enumerate(fs): shutil.copy(f, f'{o}/{i:03d}.png')
        tk = t['ticks']; json.dump({'ticks': tk, 'cycle_ticks': sum(tk), 'source': p}, open(o + '/timing.json', 'w'))
        man['clips'][f'{m}/{NAME[d]}'] = {'frames': len(fs), 'cycle_ticks': sum(tk)}
shutil.copytree('rot/s4', 'final/rot', ignore=shutil.ignore_patterns('*.json'))
json.dump(man, open('final/manifest.json', 'w'), indent=1); print(len(man['clips']), 'clips')
