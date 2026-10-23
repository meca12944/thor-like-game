# 발바닥 가운데 x: 그림에서 가장 아래 8줄(칼 뺌)의 가운데. 한 바퀴 평균 = 몸무게가 실리는 곳(그림자 자리)
import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from measure8 import load,body
def feet(a,n=8):
    m=body(a);ys=np.nonzero(m.any(1))[0];bot=ys.max();ys2,xs=np.nonzero(m[bot-n+1:bot+1]);return xs.mean()
if __name__=='__main__':
    for d in ['right','down','dr','up']:
        print(d,' '.join(f"{b}:{np.mean([feet(a) for a in load(f'{b}_{d}')])-128:+.1f}" for b in ['idle','walk','run','dash','jump']))
