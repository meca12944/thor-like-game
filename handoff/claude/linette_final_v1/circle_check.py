# Circle check (owner 10-21): every idle/walk/run clip drawn with the same reference circle around Linette, so size differences
# and parts sticking out are easy to spot. usage: circle_check.py <frames_polished> <out.png>
import sys,glob
import numpy as np
from PIL import Image,ImageDraw
P,out=sys.argv[1],sys.argv[2];CX,CY,R=128,128,64   # circle: centre at mid-body, radius ~ half her height
rows=[(m,d) for m in ('idle','walk','run') for d in ('right','down','south','up','north') if glob.glob(f'{P}/{m}/{d}/*.png')]
cell=150;W=Image.new('RGBA',(8*cell+90,len(rows)*cell),(52,70,52,255));dr=ImageDraw.Draw(W)
def upper(im):
    a=np.array(im).astype(int);al=a[:,:,3]>0
    by=np.where(al&(a[:,:,2]>a[:,:,0]+40)&(a[:,:,2]>120))[0];ry=np.where(al&(a[:,:,0]>150)&(a[:,:,1]<70)&(a[:,:,2]<80))[0]
    return ry.max()-by.min() if len(by) and len(ry) else 0
for r,(m,d) in enumerate(rows):
    fs=sorted(glob.glob(f'{P}/{m}/{d}/*.png'))[:8];us=[]
    for i,f in enumerate(fs):
        im=Image.open(f).convert('RGBA');us.append(upper(im));c=im.crop((CX-75,CY-75,CX+75,CY+75))
        W.alpha_composite(c,(90+i*cell,r*cell))
        x0,y0=90+i*cell+75,r*cell+75;dr.ellipse((x0-R,y0-R,x0+R,y0+R),outline=(255,80,80,255),width=1)
        dr.line((x0-70,y0+61,x0+70,y0+61),fill=(255,220,90,160))   # ground line
    dr.text((4,r*cell+60),f'{m}\n{d}\nup {int(np.median(us))}',fill=(255,255,255,255))
W.save(out);print(out)
