# 걷기·달리기 4방향 조립 (교과서 9절): 동작(클립)마다 크기 한 번(pxscale, 「머리→장화 윗선」 길이를 지금 주인공 같은 동작과 같게), 위치 한 번(발바닥 = 189, 몸 가운데 = 128). 장마다 따로 맞추지 않음.
#  → frames/<동작>_<방향>/NNN.png (256 캔버스), clips.json (배율·이동)
import os,json,numpy as np
INFO=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'cut','info.json')))
from PIL import Image
from pxscale import pxscale
from measure import meas
R=os.path.dirname(os.path.abspath(__file__));H8='/home/user/thor-like-game/motion_lab/hero8/frames'
TGT={}
for mo in ('walk','run'):
    for d in ('down','right','up'):TGT[f'{mo}_{d}']=np.median([meas(Image.open(f'{H8}/{mo}_{d}/{f}'))['boot_top'] for f in sorted(os.listdir(f'{H8}/{mo}_{d}'))])
TGT['walk_left']=TGT['walk_right'];TGT['run_left']=TGT['run_right']
C={}
for k in sorted(os.listdir(f'{R}/cut')):
    if not os.path.isdir(f'{R}/cut/{k}'):continue
    fr=[Image.open(f'{R}/cut/{k}/{f}') for f in sorted(os.listdir(f'{R}/cut/{k}'))]
    s=float(TGT[k]/np.median([meas(f)['boot_top'] for f in fr]))
    sc=[pxscale(f,s) for f in fr]
    # 가로 기준: 시트의 칸 가운데(그림 가운데 6개를 고른 간격 직선에 맞춘 값). 장마다 그 칸 기준점 하나만 쓰고, 그 안에서 몸이 움직인 만큼은 그대로 둠
    x0=[INFO[f'{k}_{i}']['src'][0] for i in range(len(fr))];gx=[]
    for i,f in enumerate(fr):a=np.array(f)[...,3]>40;ys,xs=np.nonzero(a);gx.append(x0[i]+xs.mean())
    b,a0=np.polyfit(np.arange(len(fr)),gx,1);anc=[a0+b*i for i in range(len(fr))]
    feet=[]
    for im in sc:a=np.array(im)[...,3]>40;feet.append(np.nonzero(a)[0].max())
    dy=189-int(round(np.median(feet)))
    os.makedirs(f'{R}/frames/{k}',exist_ok=True);dxs=[]
    for i,im in enumerate(sc):
        dx=int(round(128-(anc[i]-x0[i])*s));dxs.append(dx)
        c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy),im);c.save(f'{R}/frames/{k}/{i:03d}.png')
    C[k]=dict(scale=round(s,3),dy=dy,dx=dxs,cell=round(float(b),1),frames=len(fr),ticks=[6 if k.startswith('walk') else 4]*len(fr))
json.dump(C,open(f'{R}/clips.json','w'),indent=1);print(json.dumps(C))
