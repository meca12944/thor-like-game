# 아라크네 v2 (팀장 계획 「웅장한 보스전」, 모션 담당, 10-24): 포효·분노 서기·분노 걷기·실 감옥 예고·고치 비 예고·쓰러짐+실 풀림. 256칸, 다리 끝 y249, 옆모습 오른쪽.
import json,numpy as np
from PIL import Image
L=lambda d,i:Image.open(f'{d}/{i:03d}.png').convert('RGBA')
C={
 'roar':([L('t_idle_roar',i) for i in range(5)]+[L('t_roar_idle',i) for i in range(5)],[5,5,6,6,10,40,8,8,10,10],{'release':4}),
 'rage':([L('t_rage_idle',i) for i in range(4)],[6,6,6,6],{}),
 'ragewalk':([L('t_rage_walk',i) for i in range(8)],[4]*8,{}),
 'prison':([L('t_idle_prison',i) for i in range(5)]+[L('t_prison_idle',i) for i in (1,2,3,4)],[5,5,6,6,12,6,6,6,6],{'release':4}),
 'rain':([L('t_idle_rain',i) for i in range(5)]+[L('t_rain_idle',i) for i in (1,2,3,4)],[5,5,6,6,12,6,6,6,6],{'release':4}),
 'death':([L('t_idle_dead',i) for i in range(9)]+[L('t_dead_unravel',i) for i in (1,2,3,4)],[6,6,6,6,5,5,4,4,20,8,8,10,40],{}),
}
bot=lambda im:int(np.nonzero((np.array(im)[...,3]>40).any(1))[0].max())
out={}
for k,(fr,ticks,extra) in C.items():
    fr=[Image.fromarray(np.roll(np.array(f),249-bot(f),0)) for f in fr]   # 그림 도구가 띄워 그린 장을 땅에(다리 끝 249)
    S=Image.new('RGBA',(256*len(fr),256))
    for i,f in enumerate(fr):S.paste(f,(i*256,0))
    S.save(f'c1_boss_arachne_{k}.png');out[k]=dict(n=len(fr),ticks=ticks,**extra)
json.dump(out,open('anim2.json','w'),ensure_ascii=False);print(json.dumps(out,ensure_ascii=False))
