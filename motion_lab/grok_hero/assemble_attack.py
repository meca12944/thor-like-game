# 공격 자세(몸만) 조립: 걷기와 같은 방향 배율(clips.json walk_<방향>.scale) × K, K = 정면 걷기 키 / 정면 1타 키 (그록 공격 시트가 걷기 시트보다 크게 그려짐, 검흔 담당 10-24 지적), 발바닥 = 189, 두 발 가운데 = 128 → frames/atk<1~3>_<방향>/000.png + attack_feet.json
import os,json,numpy as np
from scipy import ndimage
from PIL import Image
from pxscale import pxscale
R=os.path.dirname(os.path.abspath(__file__));C=json.load(open(f'{R}/clips.json'));OUT={}
hh=lambda im:(lambda ys:ys.max()-ys.min())(np.nonzero(np.array(im)[...,3]>40)[0])
import glob;K=float(np.median([hh(Image.open(f)) for f in glob.glob(f'{R}/cut/walk_down/*.png')]))/hh(Image.open(f'{R}/attack/body/hit1_down.png'));print('K',round(K,3))
for d in ('down','right','up','left'):
    s=C[f'walk_{d}']['scale']*K
    for i in (1,2,3):
        im=Image.open(f'{R}/attack/body/hit{i}_{d}.png').convert('RGBA');A=np.array(im);L,n=ndimage.label(ndimage.binary_dilation(A[...,3]>40,iterations=6))
        big=np.argmax(np.bincount(L.ravel())[1:])+1;A[L!=big]=0;im=Image.fromarray(A)   # 칸을 3등분으로 잘라 옆 칸 사람 조각이 섞임 → 몸(가장 큰 덩어리)에 붙은 것만
        im=pxscale(im,s);a=np.array(im)[...,3]>40;ys,xs=np.nonzero(a);bot=ys.max()
        fx=xs[ys>=bot-6];feet=(fx.min()+fx.max())/2     # 두 발 바깥쪽 끝의 가운데
        dx=int(round(128-feet));dy=189-int(bot);c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy),im)
        os.makedirs(f'{R}/frames/atk{i}_{d}',exist_ok=True);c.save(f'{R}/frames/atk{i}_{d}/000.png')
        OUT[f'atk{i}_{d}']=dict(scale=s,feet_src=[round(float(feet/s),1),int(bot/s)],dx=dx,dy=dy)
json.dump(OUT,open(f'{R}/attack_feet.json','w'),indent=1);print(OUT)
