#!/usr/bin/env python3
"""copy selected candidates into botw_basic_v1/hit*/<dir>/; west = horizontal mirror of the chosen east (owner allowed; sword ends up in left hand)."""
import os,shutil,json
from PIL import Image
R='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/botw_basic_v1'
SEL=json.load(open(R+'/selection.json'))['selection']
for h,m in SEL.items():
    for d,src in m.items():
        dst=f'{R}/{h}/{d}'; shutil.rmtree(dst,ignore_errors=True); os.makedirs(dst)
        if src.startswith('MIRROR:'):
            s=f'{R}/_cand/'+src[7:]
            for f in sorted(os.listdir(s)): Image.open(f'{s}/{f}').transpose(Image.FLIP_LEFT_RIGHT).save(f'{dst}/{f}')
        else:
            for f in sorted(os.listdir(f'{R}/_cand/{src}')): shutil.copy(f'{R}/_cand/{src}/{f}',dst)
print('assembled')
