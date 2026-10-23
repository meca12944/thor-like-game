import json,numpy as np
from fix import load,R
from render2 import grid
from hero_ground import NEW,C
def seq(idle,walk,ti,tw,reps=2):
    # 서 있다가(2번) 걷기 시작(3번) -> 바꿀 때 몸이 튀는지 보기
    f=[];t=[]
    for _ in range(reps):f+=idle;t+=ti
    for _ in range(3):f+=walk;t+=tw
    return f,t
iu=load('hero8','idle_up');ti=C['idle_up']['ticks'];tw=C['walk_up']['ticks']
f0,t0=seq(iu,load('hero8','walk_up'),ti,tw);f1,t1=seq(iu,NEW['walk_up'][1],ti,tw)
NM={'walk_down':'정면 걷기','walk_right':'옆 걷기','jump_up':'대각선 위 점프(높이 빼고 그림만)','jump_right':'옆 점프(높이 빼고 그림만)'}
V={'walk_down':(0,1.5),'walk_right':(1.9,0),'jump_up':(0,0),'jump_right':(0,0)}
rows=[('대각선 위: 서기→걷기',[dict(frames=f0,ticks=t0,label='전'),dict(frames=f1,ticks=t1,label='후')])]
rows+=[(NM[k],[dict(frames=NEW[k][0],ticks=C[k]['ticks']+[30],vx=V[k][0],vy=V[k][1],label='전'),dict(frames=NEW[k][1],ticks=C[k]['ticks']+[30],vx=V[k][0],vy=V[k][1],label='후')]) for k in ['walk_down','walk_right','jump_up','jump_right']]
for r in rows[1:]:
    for L in r[1]:L['frames']=list(L['frames'])+[L['frames'][-1]]
grid('hero_ground_v1.mp4',rows,secs=8,title='주인공 발·땅 맞추기 (왼쪽=전, 오른쪽=후, 동그라미=그림자 자리)')
