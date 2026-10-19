#!/usr/bin/env python3
"""candidate review sheets: sheet_cand.py <cand_root> <out_prefix> [rows_per_sheet]; rows = hit*/<dir>_s<seed>"""
import os,sys
from PIL import Image,ImageDraw
R,P=sys.argv[1],sys.argv[2]; K=int(sys.argv[3]) if len(sys.argv)>3 else 4; S=128
rows=[(h,x) for h in sorted(os.listdir(R)) for x in sorted(os.listdir(f'{R}/{h}'))]
sh=Image.new('RGBA',(110+8*S,len(rows)*S),(128,128,128,255)); dr=ImageDraw.Draw(sh)
for r,(h,x) in enumerate(rows):
    dr.text((4,r*S+60),f'{h}\n{x}',fill=(255,255,255,255))
    fs=sorted(f for f in os.listdir(f'{R}/{h}/{x}') if f.endswith('.png'))
    for i,f in enumerate(fs[:8]):
        sh.alpha_composite(Image.open(f'{R}/{h}/{x}/{f}').convert('RGBA').crop((32,40,224,232)).resize((S,S),Image.NEAREST),(110+i*S,r*S))
for k in range(0,len(rows),K): sh.crop((0,k*S,sh.width,min(sh.height,(k+K)*S))).save(f'{P}_{k//K}.png')
print(len(rows),'rows')
