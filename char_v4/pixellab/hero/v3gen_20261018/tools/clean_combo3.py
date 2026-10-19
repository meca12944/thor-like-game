#!/usr/bin/env python3
"""Remove floating spark specks (opaque components < 60 px not touching the main sprite) from generated combo frames.
Originals kept in combo3_v1/_gen_raw/hitN/dir/. Only generated (not atk1-copied) dirs are passed in."""
import os, sys, shutil, numpy as np
from PIL import Image
from scipy import ndimage as nd
O=os.environ.get('C3','/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/combo3_v1')
for hd in sys.argv[1:]:
    src=f'{O}/{hd}'; raw=f'{O}/_gen_raw/{hd}'
    if not os.path.isdir(raw): shutil.copytree(src,raw)
    tot=0
    for f in sorted(os.listdir(raw)):
        a=np.array(Image.open(f'{raw}/{f}').convert('RGBA')); lab,n=nd.label(a[...,3]>0,structure=np.ones((3,3)))
        if n>1:
            sz=nd.sum(np.ones(lab.shape),lab,range(1,n+1))
            for i,s in enumerate(sz,1):
                if s<60: a[lab==i]=0; tot+=int(s)
        Image.fromarray(a).save(f'{src}/{f}')
    print(hd,'removed px',tot)
