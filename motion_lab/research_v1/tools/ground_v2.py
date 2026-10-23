"""새 그림 땅 맞추기: 그림마다 위아래로 떠다니는 것(그린 도구의 흔들림)을 없애고, 사람 움직임을 다시 넣음
 걷기: 디딘 발은 늘 땅에, 다리 벌어질 때 허리 위만 살짝 내려감
 달리기: 디딘 장은 땅에, 다리 가장 벌어진 장(공중)에서 몸 전체 3칸 뜸 (교과서: 4칸 이하)"""
import os,numpy as np
from PIL import Image
from fix import *
def ld(n):return [np.array(Image.open(f'out/hero8/{n}/{i:03d}.png')) for i in range(8)]
def phase(fr,front):
    if front:f=np.abs(footdiff(fr));return f/max(1,f.max())
    return spread(fr)
def walk(n,Gy,front=False,B=3.0):
    fr=ld(n);g=[np.roll(a,Gy-boot_bot(a),0) for a in fr];s=phase(g,front)
    bob=[int(round(B*(v-.5))) for v in s];return [warp(a,dy=b) for a,b in zip(g,bob)],bob
def run(n,Gy,front=False,A=3):
    fr=ld(n);g=[np.roll(a,Gy-boot_bot(a),0) for a in fr];s=phase(g,front)
    up=[-int(round(A*v)) for v in s];return [np.roll(a,u,0) for a,u in zip(g,up)],up
R={}
R['walk_right_v2']=walk('walk_right_v2',190)
R['walk_down_v2']=walk('walk_down_v2',189,front=True)
R['walk_up_v2']=walk('walk_up_v2',189)
R['run_down_v2']=run('run_down_v2',189,front=True)
R['run_up_v2']=run('run_up_v2',189)
for n,(fr,v) in R.items():
    os.makedirs(f'out/hero8/{n}g',exist_ok=True)
    for i,a in enumerate(fr):Image.fromarray(a).save(f'out/hero8/{n}g/{i:03d}.png')
    print(n,'움직임',v,'발',[boot_bot(a) for a in fr],'머리',list(map(int,head_y(fr))))
