# flame-only key frames (S1 cyan) on the 256 hero canvas (feet root 128,189), from 2번 room's render3.py flame(); input for PixelLab restyle
import sys,math,random,numpy as np
sys.argv=['x'];exec(open('render3.py').read().split("if __name__=='__main__':")[0])
from PIL import Image,ImageDraw
seq=d['anims']['cast_s1_down'];full=seq[2];cimg,cax,cay=cell(full[3],full[4])
a=np.asarray(cimg)[...,3];ys,xs=np.nonzero(a>0)
cx=(xs.min()+xs.max())/2-cax;cy=(ys.min()+ys.max())/2-cay;rx=(xs.max()-xs.min())/2;ry=(ys.max()-ys.min())/2
print('ring',cx,cy,rx,ry)
TS=[LAP0+round(LAP*k/8) for k in range(1,9)]+[LAP0+LAP+p for p in (2,8,16,28)]
import os;os.makedirs('kf',exist_ok=True)
for n,t in enumerate(TS):
    rng=random.Random(t*131)
    parts=flame(t,'s1',cx,cy,rx,ry,rng);im=Image.new('RGBA',(256,256));g=ImageDraw.Draw(im,'RGBA')
    for x,y,w,h,col,fr in parts:
        X=round(128+x);Y=round(189+y);g.rectangle((X,Y,X+w-1,Y+h-1),fill=col)
    im.save(f'kf/{n:03d}.png')
print(TS)
