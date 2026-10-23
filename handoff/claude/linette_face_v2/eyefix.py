# owner 10-22: the 8-frame cycles drop the eye on some middle frames -> copy frame 0's eye patch onto frames without an eye,
# placed relative to the ribbon top (y) and the face front edge (rightmost skin pixel on the eye row). usage: eyefix.py <dir>
import sys,glob,numpy as np
from PIL import Image
def info(a):
    a=a.astype(int)   # eye = blue iris pixels (blue clearly above green) 12-24 rows under the ribbon top, within 10px of the face front
    al=a[:,:,3]>0;blue=al&(a[:,:,2]>a[:,:,0]+40)&(a[:,:,2]>120);ys,_=np.nonzero(blue);t=ys.min();eye=[]
    for y in range(t+12,t+25):
        xs=np.where(al[y])[0];fx=xs.max()
        for x in range(fx-10,fx):
            r,g,b=a[y,x,:3]
            if a[y,x,3]>0 and b>g+25 and b>=r-10:eye.append((y,x))
    return t,eye
def front(a,y):return max(np.where(a[yy,:,3]>0)[0].max() for yy in range(y,y+6))   # nose tip = face front just under the eye
D=sys.argv[1];fs=sorted(glob.glob(D+'/*.png'));a0=np.array(Image.open(fs[0]).convert('RGBA'));t0,e0=info(a0)
ey=int(round(np.mean([p[0] for p in e0])));ex=int(round(np.mean([p[1] for p in e0])));f0=front(a0,ey);patch=a0[ey-2:ey+3,ex-2:ex+3].copy();dy,dx=ey-t0,ex-f0
for f in fs[1:]:
    a=np.array(Image.open(f).convert('RGBA'));t,e=info(a)
    if len(e)>=len(e0):continue   # frame already shows an eye as clear as the key
    y=t+dy;x=front(a,y)+dx;reg=a[y-2:y+3,x-2:x+3];m=(patch[:,:,3]>0)&(reg[:,:,3]>0);reg[m]=patch[m];Image.fromarray(a).save(f);print('eye ->',f)
