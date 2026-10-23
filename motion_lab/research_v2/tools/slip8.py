# 8방향 발 미끄러짐: 장마다 땅에 닿은 발(아래쪽 14줄)을 이동 반대 방향으로 옮겨 다음 장과 가장 잘 겹치는 거리 = 그 장에서 발이 뒤로 간 거리.
# 한 바퀴 합 vs 게임이 한 바퀴에 가는 거리(걷기 walkCyc*32/84, 달리기 runCyc*46/119 들판px x 117/30) -> 미끄러짐 배수 (1이 딱 맞음, 크면 얼음 위)
import sys,os,json,numpy as np
from scipy import ndimage
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from measure8 import load,body
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
V={'right':(1,0),'dr':(.707,.707),'down':(0,1),'up':(.707,-.707),'n':(0,-1)}
def feetmask(a,rows=14):
    m=body(a);ys=np.nonzero(m.any(1))[0];b=ys.max();o=np.zeros_like(m);o[b-rows+1:b+1]=m[b-rows+1:b+1];return o
def travel(fr,d):
    vx,vy=d;out=[]
    for i in range(len(fr)):
        a=feetmask(fr[i]);b=feetmask(fr[(i+1)%len(fr)],22);best=(0,0)
        for s in range(0,40):
            sh=ndimage.shift(a.astype(float),(-vy*s,-vx*s),order=0)>.5
            sc=(sh&b).sum()/max(1,a.sum())
            if sc>best[0]+1e-6:best=(sc,s)
        out.append(best[1])
    return out
if __name__=='__main__':
    s=open(R+'/test128/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e]);G=H['gait']
    cyc={'walk':G['walkCyc']*32/84*117/30,'run':G['runCyc']*46/119*117/30}
    for b in ['walk','run']:
        for d,v in V.items():
            k=f'{b}_{d}'
            try:fr=load(k)
            except Exception:continue
            t=travel(fr,v);print(f'{k:9s} 장마다',t,f'합 {sum(t)} / 게임 {cyc[b]:.0f} -> 미끄러짐 {cyc[b]/max(1,sum(t)):.2f}배')
