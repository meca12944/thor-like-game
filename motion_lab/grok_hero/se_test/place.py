# tw8_<k>/000~007 → <k>/ : 동작 하나에 한 번만 이동(발바닥 189, 몸 가운데 128). 장마다 크기·위치 안 맞춤(교과서 부록 A-9)
# 달리기는 가장 낮은 장의 발을 189에. 숫자(키·머리 오르내림·몸 좌우) 출력
import sys,glob,os,json,numpy as np
from PIL import Image
def bodyx(im):
    a=np.array(im)[...,3]>0;ys,xs=np.nonzero(a[60:150]);return float(xs.mean())
R={}
for k in sys.argv[1:]:
    ims=[Image.open(f).convert('RGBA') for f in sorted(glob.glob(f'tw8_{k}/*.png'))[:8]]
    dx=round(128-np.median([bodyx(i) for i in ims]));dy=189-max(i.getbbox()[3] for i in ims);os.makedirs(k,exist_ok=True);tops=[];bx=[];hs=[]
    for i,im in enumerate(ims):
        c=Image.new('RGBA',(256,256));c.paste(im,(dx,dy),im);c.save(f'{k}/{i:03d}.png');b=c.getbbox();tops.append(b[1]);hs.append(b[3]-b[1]);bx.append(round(bodyx(c),1))
    R[k]=dict(dx=dx,dy=dy,h=[min(hs),max(hs)],head_bob=max(tops)-min(tops),sway=round(max(bx)-min(bx),1))
    print(k,R[k])
json.dump(R,open('place.json','w'),indent=1)
