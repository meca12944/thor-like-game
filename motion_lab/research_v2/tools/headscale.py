# 머리 크기 = 머리 위 → 금색 어깨받이 위 (모든 방향·동작에 보이는 표시점). 동작·방향끼리 몸 크기 비교에 씀
import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from measure8 import load,body
def pauld(a):
    A=a[...,3]>40;r,g,b=[a[...,i].astype(int) for i in range(3)]
    gold=A&(r>85)&(g>55)&(b<70)&(r-b>45)&(g-b>20)
    m=body(a);top=np.nonzero(m.any(1))[0].min()
    rows=gold.sum(1);rows[:top+22]=0;ys=np.nonzero(rows>=3)[0]
    return top,(ys.min() if len(ys) else np.nan)
if __name__=='__main__':
    for b in ['idle','walk','run','dash','jump']:
        out=[]
        for d in ['right','down','dr','up']:
            k=f'{b}_{d}'
            if not os.path.isdir(os.path.join(os.path.dirname(__file__),'../../hero8/frames',k)):continue
            v=np.array([pauld(a) for a in load(k)],float);hd=v[:,1]-v[:,0]
            out.append(f'{d}:{np.nanmedian(hd):.0f}({np.nanmin(hd):.0f}~{np.nanmax(hd):.0f})')
        print(b,'  '.join(out))
