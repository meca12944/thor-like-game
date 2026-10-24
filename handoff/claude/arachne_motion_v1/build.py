# 아라크네 보스 동작 띠 그림 (모션연구방 10-24, 몬스터제작방 부탁): 베기 빈틈 / 덮치기 / 맞기 / 쓰러짐. 256칸, 발 기준 y≈249(원래 띠와 같게)
import os,json,numpy as np
from PIL import Image
L=lambda d,i:Image.open(f'{d}/{i:03d}.png').convert('RGBA')
F=lambda p:Image.open(p).convert('RGBA')
atk=[F(f'atk{i}.png') for i in range(7)]
C={
 'attack':(atk+[L('t_hit_rec',1),L('t_hit_rec',2),L('t_hit_rec',4),L('t_rec_idle',1),L('t_rec_idle',4)],[6,5,5,4,4,4,9,6,8,14,6,5],{'hit':6}),
 'pounce':([L('t_idle_crouch',i) for i in range(5)]+[L('t_crouch_leap',i) for i in (1,2,3,4)]+[L('t_leap_idle',i) for i in (1,2,3,4)],[5,5,5,5,8,4,4,4,4,4,6,6,6],{'hit':9}),
 'hurt':([L('t_idle_hurt',i) for i in (0,1,3,4,3,1)],[2,3,4,6,4,4],{}),
 'death':([L('t_idle_dead',i) for i in range(9)],[6,6,6,6,5,5,4,4,30],{}),
}
def bot(im):
    a=np.array(im)[...,3]>40;return int(np.nonzero(a.any(1))[0].max())
out={}
# 땅: 그림 도구가 그린 자세 장은 15~25칸 떠 있음(다리 끝이 땅에 안 닿음) -> 땅을 디딘 장은 다리 끝을 땅(249)에 붙임.
# 공중 장은 그대로 두지 않고 덮치기 포물선을 그림으로 줌(웅크림 마지막 장과 같은 이동 + 위로 10/22/22/10칸). 원래 띠의 뛰어 베기 장(공격 6)은 그대로.
AIR={'attack':{6:None},'pounce':{5:10,6:22,7:22,8:10}}
for k,(fr,ticks,extra) in C.items():
    o=[];last=0
    for i,f in enumerate(fr):
        a=AIR.get(k,{})
        if i in a and a[i] is None:dy=0
        elif i in a:dy=last-a[i]
        else:dy=249-bot(f);last=dy
        o.append(Image.fromarray(np.roll(np.array(f),dy,0)))
    fr=o;S=Image.new('RGBA',(256*len(fr),256))
    for i,f in enumerate(fr):S.paste(f,(i*256,0))
    S.save(f'c1_boss_arachne_{k}.png');out[k]=dict(n=len(fr),ticks=ticks,**extra);print(k,'발',[bot(f) for f in fr])
json.dump(out,open('anim.json','w'),ensure_ascii=False)
print(json.dumps(out,ensure_ascii=False))
