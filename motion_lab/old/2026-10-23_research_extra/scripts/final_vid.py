import json,numpy as np
from PIL import Image
from fix import load,R,track
from render2 import grid
C=json.load(open(R+'hero8/clips.json'))
def ld(n):return [np.array(Image.open(f'out/hero8/{n}/{i:03d}.png')) for i in range(8)]
def ticks(n,total):return [int((i+1)*total/n)-int(i*total/n) for i in range(n)]
NEWS={'walk_right':'walk_right_v2g','walk_down':'walk_down_v2g','walk_up':'walk_up_v3g','run_right':'run_right_v2','run_down':'run_down_v2g','run_up':'run_up_v2B'}
d=[x for x in track(ld('walk_right_v2g')) if x];wcyc=round(np.mean(d)*8/5.33);print('걷기 디딘 발/장',round(np.mean(d),1),'추천 한 바퀴 틱',wcyc,'(지금 43)')
WV=5.33;RV=10.1;k=1/np.sqrt(2)
V={'walk_right':(WV,0),'walk_down':(0,WV*.8),'walk_up':(WV*k,-WV*k*.8),'run_right':(RV,0),'run_down':(0,RV*.8),'run_up':(RV*k,-RV*k*.8)}
OLDC={'walk':43,'run':34};NEWC={'walk':wcyc,'run':26}
NM={'walk_right':'옆 걷기','walk_down':'정면 걷기','walk_up':'대각선 위 걷기','run_right':'옆 달리기','run_down':'정면 달리기','run_up':'대각선 위 달리기'}
rows=[]
for kk,n in NEWS.items():
    m=kk.split('_')[0];old=load('hero8',kk);new=ld(n);vx,vy=V[kk]
    rows.append((NM[kk],[dict(frames=old,ticks=ticks(len(old),OLDC[m]),vx=vx,vy=vy,label='전'),dict(frames=new,ticks=ticks(8,NEWC[m]),vx=vx,vy=vy,label='후')]))
grid('hero_move_v3a.mp4',rows[:3],secs=6,W=300,title='주인공 걷기 (게임 속도) 왼쪽=전, 오른쪽=후')
grid('hero_move_v3b.mp4',rows[3:],secs=6,W=300,title='주인공 달리기 (게임 속도) 왼쪽=전, 오른쪽=후')
for r in rows:
    for L in r[1]:L['ticks']=[t*3 for t in L['ticks']];L['vx']=L['vx']/3;L['vy']=L['vy']/3
grid('hero_move_v3_slow.mp4',rows,secs=8,W=300,title='3배 느리게 (왼쪽=전, 오른쪽=후)')
