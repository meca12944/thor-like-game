import json,os,numpy as np
from PIL import Image
from fix import load,R
from render2 import grid
import death
def outl(ch,k):
    d=f'out/{ch}/{k}';return [np.array(Image.open(f'{d}/{f}')) for f in sorted(os.listdir(d)) if f.endswith('.png')]
def row(ch,k,name,vx,vy):
    C=json.load(open(R+ch+'/clips.json'));N=json.load(open(f'out/{ch}/clips_changed.json'))
    return (name,[dict(frames=load(ch,k),ticks=C[k]['ticks'],vx=vx,vy=vy,label='전'),dict(frames=outl(ch,k),ticks=N[k]['ticks'],vx=vx,vy=vy,label='후')])
# 달리기 속도: 발 추적으로 잰 값(리네트 옆 4.0 = 게임 값과 같음)
#grid('linette_run_v1.mp4',[row('linette','run_right','옆 달리기',4.0,0),row('linette','run_down','대각선 아래 달리기',2.83,2.26),row('linette','run_up','대각선 위 달리기',2.83,-2.26)],secs=6,title='리네트 달리기: 왼쪽=전, 오른쪽=후')
grid('hero_v1.mp4',[row('hero8','run_right','옆 달리기',4.85,0),row('hero8','idle_right','서기',0,0)]+[r for r in death.rows if r[0].startswith('주인공')],secs=6,title='주인공: 왼쪽=전, 오른쪽=후')
grid('linette_death_v1.mp4',[r for r in death.rows if r[0].startswith('리네트')],secs=5,title='리네트 쓰러지기: 왼쪽=같은 박자, 오른쪽=중력 박자')
