# 걸음 박자 재기: 장마다 다리 벌어짐(허리 아래 몸 폭, 칼 뺌) + 앞뒤 발(정면·뒷면은 왼발/오른발 중 아래쪽에 있는 발)
import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from measure8 import load,body
def legs(a):
    m=body(a);ys=np.nonzero(m.any(1))[0];t,b=ys.min(),ys.max();h=b-t;band=m[b-int(h*.18):b+1];xs=np.nonzero(band)[1]
    spread=xs.max()-xs.min()
    cx=128;L=m[:, :cx];R=m[:,cx:];lb=np.nonzero(L.any(1))[0].max() if L.any() else 0;rb=np.nonzero(R.any(1))[0].max() if R.any() else 0
    return spread,int(lb)-int(rb)
if __name__=='__main__':
    for b in ['walk','run']:
        for d in ['right','dr','down','up','n']:
            k=f'{b}_{d}'
            try:fr=load(k)
            except Exception:continue
            v=[legs(a) for a in fr];print(f'{k:9s} 벌어짐',[x[0] for x in v],' 왼-오른발 높이',[x[1] for x in v])
