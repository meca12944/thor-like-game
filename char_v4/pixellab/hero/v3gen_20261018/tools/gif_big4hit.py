#!/usr/bin/env python3
"""big4hit GIFs: big4hit_hit{1..4}.gif (4 dirs side by side, 2x, gray) and big4hit_all.gif (1->2->3->4 chained per direction).
Hitstop: the frame with the most smear (cyan/white) pixels in each clip is held longer."""
import os
from PIL import Image,ImageDraw,ImageFont
R='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/big4hit_v1'; D=['south','east','west','north']; G=(128,128,128,255); S=2; L=20
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
except Exception: font=ImageFont.load_default()
def load(h,d):
    p=f'{R}/hit{h}/{d}'; return [Image.open(f'{p}/{f}').convert('RGBA') for f in sorted(os.listdir(p)) if f.endswith('.png')]
F={(h,d):load(h,d) for h in (1,2,3,4) for d in D}
def smear(im):
    n=0
    for r,g,b,a in im.getdata():
        if a>128 and b>180 and g>170 and (b-r>40 or (r>225 and g>225 and b>225)): n+=1
    return n
IMP={k:max(range(len(v)),key=lambda i:smear(v[i])) for k,v in F.items()}
bb=None
for v in F.values():
    for im in v:
        b=im.getbbox(); bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
bb=(max(0,bb[0]-4),max(0,bb[1]-4),min(256,bb[2]+4),min(256,bb[3]+4)); cw,ch=bb[2]-bb[0],bb[3]-bb[1]
def canvas(): return Image.new('RGBA',(4*cw*S,ch*S+L),G)
def frame(items):
    c=canvas(); dr=ImageDraw.Draw(c)
    for k,(d,h,i) in enumerate(items):
        dr.text((k*cw*S+4,2),f'{d}  hit{h}  f{i}',fill=(255,255,255,255),font=font)
        c.alpha_composite(F[(h,d)][i].crop(bb).resize((cw*S,ch*S),Image.NEAREST),(k*cw*S,L))
    return c.convert('RGB')
def dur(h,i,n):
    imps=sorted(IMP[(h,d)] for d in D); imp=imps[1]
    return 200 if i==n-1 else (170 if i==imp else 80)
for h in (1,2,3,4):
    n=min(len(F[(h,d)]) for d in D)
    fr=[frame([(d,h,i) for d in D]) for i in range(n)]; du=[dur(h,i,n) for i in range(n)]
    fr[0].save(f'{R}/big4hit_hit{h}.gif',save_all=True,append_images=fr[1:],duration=du,loop=0)
fr=[];du=[]
for h in (1,2,3,4):
    n=min(len(F[(h,d)]) for d in D)
    for i in range(n): fr.append(frame([(d,h,i) for d in D])); du.append(dur(h,i,n) if i<n-1 else 120)
du[-1]=500
fr[0].save(f'{R}/big4hit_all.gif',save_all=True,append_images=fr[1:],duration=du,loop=0)
print('ok bbox',bb,'impact',IMP)
