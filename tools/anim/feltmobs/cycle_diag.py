# Diagonal walk cycle (2번방 final method): one key pose + one same->same 8-frame animate-with-text-v3 cycle (frames 0-7).
# One scale per clip from frame 0 (body height = the side walk's), pxscale (no nearest-neighbour), x shifted once by frame 0's body
# centre, every frame's feet on the ground line (y 250). usage: cycle_diag.py <cycle prefix> <side walk strip> <out strip>
import sys,numpy as np
from PIL import Image
from assemble_lib import clean
from pxscale import pxscale
pre,side,out=sys.argv[1:4]
sd=Image.open(side);sh=np.mean([sd.crop((i*256,0,i*256+256,256)).getbbox()[3]-sd.crop((i*256,0,i*256+256,256)).getbbox()[1] for i in range(8)])
fr=[clean(Image.open(f'{pre}_{i:02d}.png')) for i in range(8)];b0=fr[0].getbbox();s=sh/(b0[3]-b0[1]);cx0=(b0[0]+b0[2])/2*s
st=Image.new('RGBA',(256*8,256))
for i,im in enumerate(fr):
    big=pxscale(im,s);b=big.getbbox();crop=big.crop(b);x=round(128-cx0+b[0]);st.paste(crop,(i*256+x,250-crop.height),crop)
st.save(out);print(out,'scale',round(s,3),'side h',round(sh))
