"""새 옆 달리기(넓은 보폭) 조립: 크기·위치·땅은 동작 전체에 한 번만"""
import os,json,numpy as np
from PIL import Image
from fix import *
from pxscale import pxscale
new=[Image.open(f'pl/cyc_run_r/{i:03d}.png').convert('RGBA') for i in range(8)]
old=load('hero8','run_right')
def bodyh(fr):return np.median([feet_bot(a)-int(head_y([a])[0]) for a in fr])
s=bodyh(old)/bodyh([np.array(x) for x in new])
sc=[np.array(pxscale(im,s)) for im in new]
# 256 캔버스로: 발 기준점 (128,189) 기준으로 비율대로 줄인 그림을 다시 놓기
def place(a,dx,dy):
    o=np.zeros((256,256,4),np.uint8);h,w=a.shape[:2]
    ox,oy=int(round(128-128*s))+dx,int(round(189-189*s))+dy
    ys,xs=slice(max(0,oy),min(256,oy+h)),slice(max(0,ox),min(256,ox+w))
    o[ys,xs]=a[ys.start-oy:ys.stop-oy,xs.start-ox:xs.stop-ox];return o
fr=[place(a,0,0) for a in sc]
dy=189-max(feet_bot(a) for a in fr)                                   # 가장 낮은 장(땅 디딤)을 땅선에
dx=int(round(np.median(stats(old)[:,2])-np.median(stats(fr)[:,2])))  # 몸 가운데를 옛 달리기와 같게
fr=[place(a,dx,dy) for a in sc]
print('배율',round(s,3),'이동',dx,dy,'발',[feet_bot(a) for a in fr],'머리',list(map(int,head_y(fr))),'track',track(fr))
os.makedirs('out/hero8/run_right_v2',exist_ok=True)
for i,a in enumerate(fr):Image.fromarray(a).save(f'out/hero8/run_right_v2/{i:03d}.png')
