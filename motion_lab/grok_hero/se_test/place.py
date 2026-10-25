# tw8_<k>/000~007 → <k>/ : 동작 하나에 한 번만 이동(발바닥 189, 몸 가운데 128). 장마다 크기·위치 안 맞춤(교과서 부록 A-9)
# 달리기는 가장 낮은 장의 발을 189에. 숫자(키·머리 오르내림·몸 좌우) 출력
import sys,glob,os,json,numpy as np
from PIL import Image
from pxscale import pxscale
def bodyx(im):
    a=np.array(im)[...,3]>0;ys,xs=np.nonzero(a[60:150]);return float(xs.mean())
R={}
SC={'walk_ne':.96,'run_s':1.0,'run_n':.78,'run_ne2':.86,'run_se2':.87}   # 10-25 겹쳐 보기(ratio/overlay.png)로 다시: ↘달리기 ×0.87, 뒷면 ×0.92 더; 정면은 얼굴 폭(15px = 정면 걷기)에 맞춰 1.0 (팀장 10-25)   # 그림 도구가 정면·뒷면 달리기를 크게 그림 → 걷기 머리 크기에 맞춰 동작 하나에 한 배율(눈으로 비교 sc.png)
TOP={'run_s2':24+3}   # 걷기 ↓ 머리 위끝 24, 걷기 ↑ 29
for k in sys.argv[1:]:
    ims=[Image.open(f).convert('RGBA') for f in sorted(glob.glob(f'tw8_{k}/*.png'))[:8]]
    if k in SC: ims=[(lambda c,im2:(c.paste(im2,(0,256-im2.height),im2),c)[1])(Image.new('RGBA',(256,256)),pxscale(im,SC[k])) for im in ims]
    dx=round(128-np.median([bodyx(i) for i in ims]));dy=189-max(i.getbbox()[3] for i in ims)
    if k in TOP:   # 정면·뒷면 달리기: 카메라 쪽으로 나온 발은 그림에서 더 아래 → 가장 낮은 발을 땅에 대면 몸이 떠서 커 보임(10-25). 머리 위끝을 같은 방향 걷기 + 몸 숙임 3px 에 맞춤
        dy=TOP[k]-int(np.median([i.getbbox()[1] for i in ims]))
    os.makedirs(k,exist_ok=True);tops=[];bx=[];hs=[]
    for i,im in enumerate(ims):
        c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy),im);c.save(f'{k}/{i:03d}.png');b=c.getbbox();tops.append(b[1]);hs.append(b[3]-b[1]);bx.append(round(bodyx(c),1))
    R[k]=dict(dx=dx,dy=dy,h=[min(hs),max(hs)],head_bob=max(tops)-min(tops),sway=round(max(bx)-min(bx),1))
    print(k,R[k])
json.dump(R,open('place.json','w'),indent=1)
