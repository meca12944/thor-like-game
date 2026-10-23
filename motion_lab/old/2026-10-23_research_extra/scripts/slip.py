import sys,numpy as np
from measure import load
from foot import clusters
Y0,Y1=184,191
def prof(a):return (a[Y0:Y1,:,3]>40)
def stance(fr):
    """per frame pair: backward displacement of the planted foot (px), best overlap score"""
    n=len(fr);res=[]
    for i in range(n):
        a,b=prof(fr[i]),prof(fr[(i+1)%n]);best=(0,None,None)
        for (x0,x1) in [c for c in clusters(fr[i]) if c[1]-c[0]>=8]:
            m=np.zeros_like(a);m[:,x0:x1+1]=a[:,x0:x1+1]
            for s in range(-35,6):
                sh=np.roll(m,s,1);inter=(sh&b).sum();sc=inter/max(1,m.sum())
                if sc>best[0]:best=(sc,-s,(x0,x1))
        res.append(best)
    return res
if __name__=='__main__':
    for arg in sys.argv[1:]:
        c,k=arg.split(':');r=stance(load(c,k))
        d=[x[1] for x in r];print(f'{c[:3]} {k:12s} disp',d,'score',[round(x[0],2) for x in r],'sum',sum(x or 0 for x in d))
