#!/usr/bin/env python3
"""before/after compare sheet: cmp_trail_front.py <cand_dir> <dir> <out.png>"""
import os,sys
from PIL import Image,ImageDraw
G='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; c,d,out=sys.argv[1:4]; S=200
fs=sorted(f for f in os.listdir(c) if f.endswith('.png'))
sh=Image.new('RGBA',(len(fs)*S,2*S),(128,128,128,255)); dr=ImageDraw.Draw(sh)
for k,f in enumerate(fs):
    h=f.split('_')[0]; i=f.split('_')[1]
    sh.alpha_composite(Image.open(f'{G}/combo3_final/{h}/{d}/{i}').convert('RGBA').crop((20,30,236,246)).resize((S,S)),(k*S,0))
    sh.alpha_composite(Image.open(f'{c}/{f}').convert('RGBA').crop((20,30,236,246)).resize((S,S)),(k*S,S))
    dr.text((k*S+3,3),'before '+f,fill=(255,255,0,255)); dr.text((k*S+3,S+3),'after',fill=(0,255,255,255))
sh.save(out)
