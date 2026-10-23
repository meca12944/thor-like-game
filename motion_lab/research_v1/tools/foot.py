import sys,numpy as np
from measure import load
def clusters(a,y0=183,y1=190):
    m=(a[y0:y1,:,3]>40).any(0);xs=np.nonzero(m)[0];out=[];
    if not len(xs):return out
    s=xs[0];p=xs[0]
    for x in xs[1:]:
        if x>p+2:out.append((s,p));s=x
        p=x
    out.append((s,p));return [c for c in out if c[1]-c[0]>=3]
if __name__=='__main__':
 for arg in sys.argv[1:]:
     c,k=arg.split(':');fr=load(c,k);print(c[:3],k)
     for i,a in enumerate(fr):
         ys=np.nonzero((a[...,3]>40).any(1))[0]
         print(f'  {i}: bot{ys.max()} ground', clusters(a))
