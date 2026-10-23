"""쓰러지기: 같은 박자(6) -> 비틀(느림) · 떨어짐(중력처럼 점점 빨라짐) · 쿵(땅에 닿는 장은 짧게) · 털썩 멈춤(길게)"""
import json,numpy as np
from fix import load,R,head_y
from render2 import grid
def gravity_ticks(fr,total,F=16):
    """stagger slowly, then fall like a dropped object (frame times from sqrt of how far the head has dropped), short impact, long lie-still"""
    h=np.array([float(head_y([a])[0]) for a in fr]);n=len(fr)
    hit=int(np.argmax(h>=h.max()-3));dr=h-h[0];s=max(1,int(np.argmax(dr>=0.2*dr[hit]))-1)
    T=np.sqrt(np.clip(h[s:hit+1]-h[s],0,None)/(h[hit]-h[s]))*F;fall=np.maximum(2,np.round(np.diff(T)))
    rest=total-fall.sum()-3;st=np.linspace(1.3,0.8,s);after=np.linspace(1,2,n-hit-1)
    tot_w=st.sum()+after.sum();k=rest/tot_w
    t=np.r_[np.minimum(10,np.round(st*k)),fall,[3],np.round(after*k)].astype(int);t[-1]+=total-t.sum()
    return [int(x) for x in t],list(map(int,h)),hit
rows=[]
for ch,ks in [('linette',['death_right','death_south','death_north']),('hero8',['death_right'])]:
    C=json.load(open(R+ch+'/clips.json'))
    for k in ks:
        fr=load(ch,k);t0=C[k]['ticks'];t1,h,hit=gravity_ticks(fr,sum(t0));print(ch,k,'머리',h,'땅',hit,'박자',t0,'->',t1)
        rows.append((('리네트 ' if ch=='linette' else '주인공 ')+{'death_right':'옆 쓰러지기','death_south':'정면 쓰러지기','death_north':'뒷면 쓰러지기'}[k],[dict(frames=fr+[fr[-1]],ticks=t0+[60],label='전'),dict(frames=fr+[fr[-1]],ticks=t1+[60],label='후')]))
