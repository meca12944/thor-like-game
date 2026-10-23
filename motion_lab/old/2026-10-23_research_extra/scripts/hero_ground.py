"""주인공 땅 맞추기: 뜬 걷기는 땅에 내리고, 착지 뒤 땅에 묻힌 장은 올림. 걷기는 내린 뒤 사람처럼 오르내림을 다시 넣음"""
import json,numpy as np
from fix import *
C=json.load(open(R+'hero8/clips.json'))
def shift(a,dy):return np.roll(a,dy,0) if dy else a
def ground_walk(k,Gy,B=3.0):
    fr=load('hero8',k);fb=[feet_bot(a) for a in fr];n=len(fr)
    dy=[Gy-b for b in fb];g=[shift(a,d) for a,d in zip(fr,dy)]
    # 딛는 순간(다리 가장 벌어짐) 살짝 낮게, 다리 모일 때 살짝 높게 — 발은 땅에 둔 채 허리 위만
    s=spread(g);bob=[int(round(B*(v-.5))) for v in s]
    out=[warp(a,dy=b) for a,b in zip(g,bob)]
    return fr,out,dict(발=fb,내림=dy,오르내림=bob)
def lift_landing(k,Gy):
    fr=load('hero8',k);fb=[feet_bot(a) for a in fr];dy=[min(0,Gy-b) for b in fb]
    return fr,[shift(a,d) for a,d in zip(fr,dy)],dict(발=fb,올림=dy)
NEW={}
def stretch(a,up):
    # 머리~허리는 그대로 위로, 허리~발(망토 아랫단·다리)을 그만큼 늘림 — 발은 땅에 그대로
    m=a[...,3]>40;ys=np.nonzero(m.any(1))[0];top,bot=ys.min(),feet_bot(a);hip=int(top+(bot-top)*.45)
    out=np.zeros_like(a)
    for y in range(256):
        if y<=hip-up:sy=y+up
        elif y<=bot:sy=int(round(hip+(y-(hip-up))*(bot-hip)/(bot-hip+up)))
        else:sy=y
        if 0<=sy<256:out[y]=a[sy]
    return out
def walk_up_fix():
    # 대각선 위 걷기: 칼끝이 땅에 맞춰져 몸 전체가 17칸 떠 있었음 -> 동작 전체를 한 번에 내림(중간값), 그 뒤 땅에 묻힌 장만 올림
    fr=load('hero8','walk_up');fb=[feet_bot(a) for a in fr];base=189-int(np.median(fb))
    g=[shift(a,base) for a in fr];dy=[min(0,189-feet_bot(a)) for a in g];out=[stretch(shift(a,d),14) for a,d in zip(g,dy)]   # 다리가 짧게 그려져 서기보다 22칸 작음 -> 동작 전체 다리 14칸 늘림(한 번만)
    return fr,out,dict(발=fb,전체내림=base,묻힌장올림=dy,다리늘림=14)
def walk_down_fix(B=3.0):
    fr=load('hero8','walk_down');fb=[feet_bot(a) for a in fr];n=len(fr)
    g=[shift(a,189-b) for a,b in zip(fr,fb)]
    f=footdiff(g);c=int(np.argmax(np.abs(f)))
    bob=[int(round(B/2*np.cos(4*np.pi*(i-c-0.5)/n)+0.01)) for i in range(n)]
    return fr,[warp(a,dy=b) for a,b in zip(g,bob)],dict(발=fb,내림=[189-b for b in fb],딛는장=c,오르내림=bob)
NEW['walk_up']=walk_up_fix();NEW['walk_down']=walk_down_fix();NEW['walk_right']=ground_walk('walk_right',190)
for k,Gy in [('jump_up',189),('jump_right',190)]:NEW[k]=lift_landing(k,Gy)
if __name__=='__main__':
    for k,(fr,out,info) in NEW.items():
        print(k,info,'머리',list(map(int,head_y(fr))),'->',list(map(int,head_y(out))),'새 발',[feet_bot(a) for a in out])
