# 공격 자세(몸만) 조립: 걷기와 같은 방향 배율 그대로(clips.json walk_<방향>.scale), 발바닥 = 189, 두 발 가운데 = 128 → frames/atk<1~3>_<방향>/000.png + attack_feet.json
import os,json,numpy as np
from PIL import Image
from pxscale import pxscale
R=os.path.dirname(os.path.abspath(__file__));C=json.load(open(f'{R}/clips.json'));OUT={}
for d in ('down','right','up','left'):
    s=C[f'walk_{d}']['scale']
    for i in (1,2,3):
        im=pxscale(Image.open(f'{R}/attack/body/hit{i}_{d}.png'),s);a=np.array(im)[...,3]>40;ys,xs=np.nonzero(a);bot=ys.max()
        fx=xs[ys>=bot-6];feet=(fx.min()+fx.max())/2     # 두 발 바깥쪽 끝의 가운데
        dx=int(round(128-feet));dy=189-int(bot);c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy),im)
        os.makedirs(f'{R}/frames/atk{i}_{d}',exist_ok=True);c.save(f'{R}/frames/atk{i}_{d}/000.png')
        OUT[f'atk{i}_{d}']=dict(scale=s,feet_src=[round(float(feet/s),1),int(bot/s)],dx=dx,dy=dy)
json.dump(OUT,open(f'{R}/attack_feet.json','w'),indent=1);print(OUT)
