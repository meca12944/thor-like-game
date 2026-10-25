# 눈으로 크기 맞추기: 같은 방향 걷기 장의 윗몸(정수리~허리) 테두리(하늘색)를 달리기 장 위에 겹침. 배율 후보마다 한 칸. 머리 위끝·머리 가운데 맞춤
import sys,glob,numpy as np
sys.path.insert(0,'../se_test')
from PIL import Image,ImageDraw,ImageFont
from pxscale import pxscale
from scipy import ndimage
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
G='..'
PAIRS=[('run_se3','../se_test/run_se3','../se_test/walk_se'),('run_r3','../se_test/run_r3','../se_test/walk_r2')]
SC=[1.10,1.0,0.92,0.85]
def headbox(im):
    a=np.array(im)[...,3]>0;t=int(np.nonzero(a.any(1))[0].min());xs=np.nonzero(a[t:t+12].any(0))[0];return t,(xs.min()+xs.max())/2
Z=3;CW=110;CH=110
W=Image.new('RGB',(len(SC)*CW*Z,len(PAIRS)*(CH*Z+20)),(70,74,80));d=ImageDraw.Draw(W)
for r,(n,rp,wp) in enumerate(PAIRS):
    run=Image.open(sorted(glob.glob(rp+'/*.png'))[0]).convert('RGBA');walk=Image.open(sorted(glob.glob(wp+'/*.png'))[0]).convert('RGBA')
    tr,cr=headbox(run);tw,cw=headbox(walk)
    wa=np.array(walk)[...,3]>0;wa[tw+75:]=0;edge=wa&~ndimage.binary_erosion(wa)
    for c,s in enumerate(SC):
        # 달리기를 s배 (걷기 크기 기준으로 보이게) → 머리 위끝·가운데 맞춤
        rb=run.getbbox();rs=pxscale(run.crop(rb),s);can=Image.new('RGBA',(256,256),(70,74,80,255))
        ox=round(cw-(cr-rb[0])*s);oy=round(tw-(tr-rb[1])*s);can.alpha_composite(rs,(ox,oy)) if ox>=0 and oy>=0 else can.paste(rs,(ox,oy),rs)
        A=np.array(can);A[edge]=[90,230,255,255];can=Image.fromarray(A)
        crop=can.crop((int(cw)-CW//2,tw-8,int(cw)+CW//2,tw-8+CH)).resize((CW*Z,CH*Z),Image.NEAREST)
        W.paste(crop.convert('RGB'),(c*CW*Z,r*(CH*Z+20)+20));d.text((c*CW*Z+4,r*(CH*Z+20)+2),f'{n} ×{s}',font=F,fill=(255,255,255))
W.save('overlay.png');print(W.size)
