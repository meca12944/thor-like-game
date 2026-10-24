# 그록 공격 시트(1타 세로·2타 가로·3타 반원 × 정면·오른쪽·뒤·왼쪽) 자르기: 몸만 남기고 파란 검기(그림에 구운 효과)는 fx/ 로 따로 (검기는 코드로 그림)
import os,numpy as np
from PIL import Image
from scipy import ndimage
from cut import bgimage,cut
R=os.path.dirname(os.path.abspath(__file__));SRC=os.path.join(R,'../../docs_art/grok_hero_20261024/hero_attack3_4dir.jpg')
a=np.array(Image.open(SRC).convert('RGB')).astype(int);H,W=a.shape[:2]
r,g,b=a[...,0],a[...,1],a[...,2];blue=(b>r+35)&(g>r+15)&(a.mean(2)>90)   # 청백 검기
blue=ndimage.binary_dilation(blue,iterations=2);blue|=(a.mean(2)>170)&ndimage.binary_dilation(blue,iterations=8)   # 검기 흰 심지까지
clean=a.copy();BG=bgimage(np.where(blue[...,None],np.median(a.reshape(-1,3),0),a))
clean[blue]=BG[blue].astype(int)   # 검기 자리는 배경으로 메운 뒤 몸만 자름
ROWS=[('down',125,480),('right',600,1000),('up',1065,1470),('left',1535,1945)];HITS=['hit1','hit2','hit3']   # 줄 이름 글씨(정면·오른쪽…)는 빼고;HITS=['hit1','hit2','hit3']
for d,y0,y1 in ROWS:
    for ci,hn in enumerate(HITS):
        x0,x1=int(ci*W/3),int((ci+1)*W/3);o,_=cut(clean[y0:y1,x0:x1],BG[y0:y1,x0:x1])
        fx=np.zeros_like(o);fx[...,:3]=a[y0:y1,x0:x1].clip(0,255);fx[...,3]=blue[y0:y1,x0:x1]*255
        os.makedirs(f'{R}/attack/body',exist_ok=True);os.makedirs(f'{R}/attack/fx',exist_ok=True)
        Image.fromarray(o).save(f'{R}/attack/body/{hn}_{d}.png');Image.fromarray(fx).save(f'{R}/attack/fx/{hn}_{d}.png')
print('ok')
