#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont
A='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/atk1_v1'
D=['south','south-east','east','north-east','north','north-west','west','south-west']
fr={d:[Image.open(f'{A}/{d}/{f}').convert('RGBA') for f in sorted(os.listdir(f'{A}/{d}')) if f.endswith('.png')] for d in D}
W,H=fr['south'][0].size; n=max(len(v) for v in fr.values()); S=2; L=18; G=(128,128,128,255)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
except Exception: font=ImageFont.load_default()
# crop box: union bbox over everything, padded
bb=None
for v in fr.values():
    for im in v:
        b=im.getbbox()
        if b: bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
p=6; bb=(max(0,bb[0]-p),max(0,bb[1]-p),min(W,bb[2]+p),min(H,bb[3]+p)); cw,ch=bb[2]-bb[0],bb[3]-bb[1]
gifs=[]
for i in range(n):
    c=Image.new('RGBA',(4*cw*S,2*(ch*S+L)),G); dr=ImageDraw.Draw(c)
    for k,d in enumerate(D):
        im=fr[d][min(i,len(fr[d])-1)].crop(bb).resize((cw*S,ch*S),Image.NEAREST)
        x,y=(k%4)*cw*S,(k//4)*(ch*S+L); dr.text((x+4,y+2),d,fill=(255,255,255,255),font=font)
        c.alpha_composite(im,(x,y+L))
    gifs.append(c.convert('RGB'))
gifs[0].save(f'{A}/atk1_8dir.gif',save_all=True,append_images=gifs[1:],duration=90,loop=0,disposal=2)
# contact sheet: one row per direction, 1x full canvas crop
LW=90; sh=Image.new('RGBA',(LW+n*cw,8*ch),G); dr=ImageDraw.Draw(sh)
for r,d in enumerate(D):
    dr.text((4,r*ch+ch//2-7),d,fill=(255,255,255,255),font=font)
    for i,im in enumerate(fr[d]): sh.alpha_composite(im.crop(bb),(LW+i*cw,r*ch))
sh.save(f'{A}/atk1_8dir_frames.png'); print('ok',n,bb)
