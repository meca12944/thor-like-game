# 실험: 게임 크기(144)에서 얼굴을 또렷하게 — ① 그냥 줄임 ② 색 줄이기(팔레트 고정 24색) ③ ②+얼굴 손질(눈 진하게 2×2 + 반짝임 1점, 턱선 1px 어둡게, 피부 3단)
import sys,numpy as np
sys.path.insert(0,'../se_test');sys.path.insert(0,'../ratio')
from PIL import Image,ImageDraw,ImageFont
from pxscale import pxscale
from scipy import ndimage
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
def to144(f):
    im=Image.open(f).convert('RGBA');b=im.getbbox();s=144/164;c=pxscale(im.crop(b),s);o=Image.new('RGBA',(256,256));o.paste(c,(round(128+(b[0]-128)*s),round(189+(b[1]-189)*s)),c);return o
def pal(im,n=24):
    a=im.getchannel('A');q=im.convert('RGB').quantize(n,method=Image.Quantize.MEDIANCUT).convert('RGBA');q.putalpha(a);return q
def clean(im):
    A=np.array(im).astype(int);r,g,b,al=[A[...,i] for i in range(4)];L=A[...,:3].mean(2)
    sk=(al>0)&(r>110)&(r-g>15)&(g-b>0);top=np.nonzero(al.any(1))[0].min();sk[top+45:]=0
    lab,n=ndimage.label(sk);sz=np.bincount(lab.ravel());sz[0]=0;face=lab==sz.argmax()
    ys,xs=np.nonzero(face);y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    fill=ndimage.binary_fill_holes(face)|face;hole=fill&~face   # 얼굴 안 어두운 칸 = 눈·입
    sk_c=A[...,:3][face];mid=np.median(sk_c,0);lite=np.clip(mid*1.12,0,255);dark=mid*0.78
    B=A.copy()
    # 피부 3단: 위쪽 밝게, 가장자리 어둡게
    edge=face&~ndimage.binary_erosion(face)
    B[face,:3]=mid;B[face&(np.arange(256)[:,None]<y0+(y1-y0)*0.45),:3]=lite;B[edge,:3]=dark
    # 눈: 얼굴 위 40~60% 높이의 어두운 구멍 → 아주 어둡게 + 위 왼쪽 1점 반짝임
    eyes=hole&(np.arange(256)[:,None]>y0+(y1-y0)*0.25)&(np.arange(256)[:,None]<y0+(y1-y0)*0.6)
    el,en=ndimage.label(eyes)
    for i in range(1,en+1):
        ey,ex=np.nonzero(el==i)
        if len(ey)<2: continue
        B[el==i,:3]=[28,20,24];B[ey.min(),ex.min(),:3]=[235,235,240]
    # 입: 아래쪽 구멍 → 진한 살색 1줄
    mouth=hole&(np.arange(256)[:,None]>=y0+(y1-y0)*0.6);B[mouth,:3]=mid*0.6
    # 턱선: 얼굴 아래 바로 밑 1px 어둡게
    below=ndimage.binary_dilation(face)&~face&(np.arange(256)[:,None]>y0+(y1-y0)*0.5)&(al>0);B[below,:3]=np.minimum(B[below,:3],[50,32,28])
    return Image.fromarray(B.astype('uint8'))
srcs=[('정면','../frames/walk_down/000.png'),('↘','../se_test/walk_se/000.png'),('옆','../se_test/walk_r2/000.png')]
Z=8;C=30;W=Image.new('RGB',(3*(C*Z+8),len(srcs)*(C*Z+30)),(70,74,80));d=ImageDraw.Draw(W)
from measure_ratio import meas
for r,(n,f) in enumerate(srcs):
    a=to144(f);vs=[('① 그냥 144',a),('② 색 24개',pal(a)),('③ ②+얼굴 손질',clean(pal(a)))]
    a.save(f'/tmp/_a.png');m=meas('/tmp/_a.png');x0,y0,x1,y1,_=m['face'];cx,cy=(x0+x1)//2,(y0+y1)//2
    for c,(t,im) in enumerate(vs):
        cr=im.crop((cx-C//2,cy-C//2,cx+C//2,cy+C//2));bg=Image.new('RGBA',cr.size,(70,74,80,255));bg.alpha_composite(cr)
        W.paste(bg.convert('RGB').resize((C*Z,C*Z),Image.NEAREST),(c*(C*Z+8),r*(C*Z+30)+26));d.text((c*(C*Z+8)+4,r*(C*Z+30)+4),f'{n} {t}',font=F,fill=(255,255,255))
W.save('clean_test.png')
