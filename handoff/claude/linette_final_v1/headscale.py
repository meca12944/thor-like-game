# owner 10-22 "가만히 서있는 얼굴 크기와 뛰는 얼굴 크기가 틀리다": find the scale that makes each clip's FACE match the idle face of the same view.
# Face window = from the ribbon top down 30 rows, ribbon x -8..+20 (toward the face); best scale/shift by mean colour difference.
import glob,sys,numpy as np
from PIL import Image
sys.path.insert(0,'.');from pxscale import pxscale
def ribbon(a):
    al=a[:,:,3]>0;b=al&(a[:,:,2]>a[:,:,0]+40)&(a[:,:,2]>120);ys,xs=np.nonzero(b);t=ys.min();k=ys<t+8;return t,int(np.median(xs[k]))
def win(a,t,x,sgn):
    x0,x1=(x-8,x+20) if sgn>0 else (x-20,x+8);w=a[t-2:t+30,x0:x1].astype(float);m=w[:,:,3:4]/255;return w[:,:,:3]*m,m
def score(A,B):return np.abs(A[0]-B[0]).mean()+40*np.abs(A[1]-B[1]).mean()
def best(ref,f,sgn):
    ra=np.array(ref.convert('RGBA')).astype(int);rt,rx=ribbon(ra);R=win(ra,rt,rx,sgn);out=None
    im=Image.open(f).convert('RGBA')
    for s in np.arange(0.76,1.12,0.02):
        a=np.array(pxscale(im,s) if abs(s-1)>1e-3 else im).astype(int)
        try:t,x=ribbon(a)
        except Exception:continue
        for dy in range(-3,4):
            for dx in range(-3,4):
                try:sc=score(R,win(a,t+dy,x+dx,sgn))
                except Exception:continue
                if out is None or sc<out[0]:out=(sc,round(float(s),2))
    return out
if __name__=='__main__':
    for m,d,ref in [(sys.argv[1],sys.argv[2],sys.argv[3])]:
        fs=sorted(glob.glob(f'frames_polished/{m}/{d}/*.png'));R=Image.open(ref)
        r=[best(R,f,1 if d in('right','down','up','south','north') else -1)[1] for f in fs];print(m,d,r,'median',sorted(r)[len(r)//2])
