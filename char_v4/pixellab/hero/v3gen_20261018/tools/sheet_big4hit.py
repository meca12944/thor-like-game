#!/usr/bin/env python3
"""contact sheet of a candidate tag: rows hit x dir, 8 frames, 1x on gray. usage: sheet_big4hit.py <root> <out.png>"""
import os,sys
from PIL import Image,ImageDraw
root,out=sys.argv[1],sys.argv[2]; D=['south','east','west','north']; S=160
rows=[(h,d) for h in (1,2,3,4) for d in D if os.path.isdir(f'{root}/hit{h}/{d}')]
n=max(len([f for f in os.listdir(f'{root}/hit{h}/{d}') if f.endswith('.png')]) for h,d in rows)
sh=Image.new('RGBA',(60+n*S,len(rows)*S),(128,128,128,255)); dr=ImageDraw.Draw(sh)
for r,(h,d) in enumerate(rows):
    dr.text((4,r*S+70),f'h{h}\n{d}',fill=(255,255,255,255))
    fs=sorted(f for f in os.listdir(f'{root}/hit{h}/{d}') if f.endswith('.png'))
    for i,f in enumerate(fs):
        im=Image.open(f'{root}/hit{h}/{d}/{f}').convert('RGBA').crop((32,40,224,232)).resize((S,S),Image.NEAREST)
        sh.alpha_composite(im,(60+i*S,r*S))
    dr.line([(0,r*S),(sh.width,r*S)],fill=(90,90,90,255))
sh.save(out); print(out,sh.size)
