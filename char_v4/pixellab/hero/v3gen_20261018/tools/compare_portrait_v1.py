#!/usr/bin/env python3
import glob,os
from PIL import Image,ImageDraw,ImageFont
O='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018'; D=f'{O}/portrait_v1'
S=3
try: F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
except Exception: F=ImageFont.load_default()
cells=[('OLD hero.png (128x128)',Image.open('/workspace/town-demo/assets/portraits/hero.png'))]
for p in sorted(glob.glob(f'{D}/bust_*.png')):
    cells.append(('NEW '+os.path.basename(p)[5:-4],Image.open(p)))
sp=Image.open(f'{O}/v1_1x_descA/south.png'); sp=sp.crop(sp.getbbox())
cells.append(('south.png (src sprite)',sp))
W=128*S; H=max(max(c.height*S for _,c in cells),W); pad=16; top=34
canvas=Image.new('RGBA',(len(cells)*(W+pad)+pad,H+top+pad),(128,128,128,255))
d=ImageDraw.Draw(canvas)
for i,(lab,im) in enumerate(cells):
    im=im.convert('RGBA'); im=im.resize((im.width*S,im.height*S),Image.NEAREST)
    x=pad+i*(W+pad); d.rectangle([x-1,top-1,x+W,top+H],outline=(90,90,90,255))
    canvas.alpha_composite(im,(x+(W-im.width)//2,top+(H-im.height)//2))
    d.text((x,8),lab,fill=(255,255,255,255),font=F)
canvas.convert('RGB').save(f'{D}/portrait_compare.png'); print(canvas.size)
