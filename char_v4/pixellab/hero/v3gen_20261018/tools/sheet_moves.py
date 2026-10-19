#!/usr/bin/env python3
import os, sys
from PIL import Image, ImageDraw, ImageFont
A='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/moves_v1'
m=sys.argv[1]; MS={'run':70,'dash':80,'jump':80,'walk':90}.get(m,90)
D=[d for d in ['south','north','east','west'] if os.path.isdir(f'{A}/{m}/{d}')]
fr={d:[Image.open(f'{A}/{m}/{d}/{f}').convert('RGBA') for f in sorted(os.listdir(f'{A}/{m}/{d}')) if f.endswith('.png')] for d in D}
W,H=fr[D[0]][0].size; n=max(len(v) for v in fr.values()); S=2; L=18; G=(128,128,128,255)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
except Exception: font=ImageFont.load_default()
bb=None
for v in fr.values():
    for im in v:
        b=im.getbbox()
        if b: bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
p=6; bb=(max(0,bb[0]-p),max(0,bb[1]-p),min(W,bb[2]+p),min(H,bb[3]+p)); cw,ch=bb[2]-bb[0],bb[3]-bb[1]
gifs=[]
for i in range(n):
    c=Image.new('RGBA',(len(D)*cw*S,ch*S+L),G); dr=ImageDraw.Draw(c)
    for k,d in enumerate(D):
        im=fr[d][min(i,len(fr[d])-1)].crop(bb).resize((cw*S,ch*S),Image.NEAREST)
        x=k*cw*S; dr.text((x+4,2),d,fill=(255,255,255,255),font=font); c.alpha_composite(im,(x,L))
    gifs.append(c.convert('RGB'))
gifs[0].save(f'{A}/{m}_4dir.gif',save_all=True,append_images=gifs[1:],duration=MS,loop=0,disposal=2)
LW=60; sh=Image.new('RGBA',(LW+n*cw,len(D)*ch),G); dr=ImageDraw.Draw(sh)
for r,d in enumerate(D):
    dr.text((4,r*ch+ch//2-7),d,fill=(255,255,255,255),font=font)
    for i,im in enumerate(fr[d]): sh.alpha_composite(im.crop(bb),(LW+i*cw,r*ch))
sh.save(f'{A}/{m}_4dir_frames.png'); print('ok',m,D,n,bb)
