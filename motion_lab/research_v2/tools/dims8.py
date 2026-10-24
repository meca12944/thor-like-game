# 8방향 몸 크기 표: 동작마다 (중앙값) 키 = 머리 위~발, 몸통 폭 = 키의 35~60% 높이 띠에서 칼 뺀 몸 폭, 전체 폭(망토·칼 포함)
import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from measure8 import load,body
def dims(a):
    m=body(a);ys=np.nonzero(m.any(1))[0];t,b=ys.min(),ys.max();h=b-t
    band=m[t+int(h*.35):t+int(h*.6)];w=np.median([np.ptp(np.nonzero(r)[0]) for r in band if r.any()])
    full=np.ptp(np.nonzero((a[...,3]>40).any(0))[0]);return h,w,full
if __name__=='__main__':
    D=['right','dr','down','up','n']
    print('동작      '+' '.join(f'{d:>16s}' for d in D))
    for b in ['idle','walk','run','dash','jump']:
        row=[]
        for d in D:
            try:v=np.median(np.array([dims(a) for a in load(f'{b}_{d}')]),0);row.append(f'키{v[0]:4.0f} 몸{v[1]:3.0f} 폭{v[2]:3.0f}')
            except Exception:row.append(f'{"-":>16s}')
        print(f'{b:8s} '+' '.join(row))
