# 머리 가운데 x: 머리 꼭대기 10줄 가운데(정수리, 휘날리는 머리카락 영향 적음) + 얼굴(피부) 가운데
import sys,os,numpy as np
from scipy import ndimage
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from measure8 import load,body,skin
def headx(a,n=10):
    m=body(a);ys=np.nonzero(m.any(1))[0];t=ys.min();row=m[t:t+n];xs=np.nonzero(row)[1]
    # 꼭대기 줄들 중 가장 큰 덩어리(정수리)만
    lab,k=ndimage.label(row);
    if k>1:
        sz=ndimage.sum(row,lab,range(1,k+1));big=lab==(np.argmax(sz)+1);xs=np.nonzero(big)[1]
    return xs.mean(),t
def facex(a):
    m=body(a);t=np.nonzero(m.any(1))[0].min();s=skin(a);s[t+45:]=False;s[:t]=False
    lab,k=ndimage.label(s)
    if not k:return np.nan
    sz=ndimage.sum(s,lab,range(1,k+1));b=lab==(np.argmax(sz)+1);return np.nonzero(b)[1].mean()
if __name__=='__main__':
    for d in ['right','down','dr','up']:
        out=[]
        for b in ['idle','walk','run','dash','jump','hurt']:
            p=os.path.join(os.path.dirname(__file__),'../../hero8/frames',f'{b}_{d}')
            if not os.path.isdir(p):continue
            fr=load(f'{b}_{d}');h=np.array([headx(a) for a in fr]);f=np.array([facex(a) for a in fr])
            out.append(f"{b}:정수리{np.median(h[:,0])-128:+.0f} 얼굴{np.nanmedian(f)-128:+.0f} 위{np.median(h[:,1]):.0f}")
        print(d,' | '.join(out))
