# owner 10-22 "얼굴이 틀리다": some in-between frames of the side walk/run lose the eye. Paste frame 0's eye (5x5) onto every other frame at the
# spot found by matching frame 0's face (ribbon top .. chin, face side) against the frame (best shift by colour difference) - head moves a few px per frame.
import sys,glob,numpy as np
from PIL import Image
D=sys.argv[1];fs=sorted(glob.glob(D+'/*.png'));A0=np.array(Image.open(fs[0]).convert('RGBA'));a0=A0.astype(int)
def rib(a):b=(a[:,:,3]>0)&(a[:,:,2]>a[:,:,0]+40)&(a[:,:,2]>120);ys,xs=np.nonzero(b);t=ys.min();return t,int(np.median(xs[ys<t+8]))
t0,x0=rib(a0);EY,EX=[int(v) for v in sys.argv[2:4]]   # eye centre in frame 0 (absolute px)
W=a0[t0+6:t0+32,x0-2:x0+24]
for f in fs[1:]:
    A=np.array(Image.open(f).convert('RGBA'));a=A.astype(int);t,x=rib(a);best=None
    for dy in range(-6,7):
        for dx in range(-6,7):
            y1,x1=t0+6+(t-t0)+dy,x0-2+(x-x0)+dx;R=a[y1:y1+W.shape[0],x1:x1+W.shape[1]]
            if R.shape!=W.shape:continue
            sc=np.abs(R[:,:,:3]*(R[:,:,3:]>0)-W[:,:,:3]*(W[:,:,3:]>0)).mean()
            if best is None or sc<best[0]:best=(sc,(t-t0)+dy,(x-x0)+dx)
    _,oy,ox=best;y,xx=EY+oy,EX+ox;P=A0[EY-2:EY+3,EX-2:EX+3];reg=A[y-2:y+3,xx-2:xx+3];m=(P[:,:,3]>0)&(reg[:,:,3]>0);reg[m]=P[m];Image.fromarray(A).save(f);print(f,'shift',oy,ox)
