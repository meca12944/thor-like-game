# 주인공 8방향 크기·위치 재기: 동작마다 머리 위, 발, 머리 가운데 x, 몸통 가운데 x, 머리~턱(피부 아래끝), 어깨 폭
import json,os,sys,numpy as np
from PIL import Image
from scipy import ndimage
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
F=R+'/motion_lab/hero8/frames'
def load(k):return [np.array(Image.open(f'{F}/{k}/{f}').convert('RGBA')) for f in sorted(os.listdir(f'{F}/{k}'))]
def body(a):
    A=a[...,3]>40;c=a[...,:3].astype(int);sw=(c.min(2)>150)&(c.max(2)-c.min(2)<40)   # 칼날(밝은 회색) 빼기
    m=A&~ndimage.binary_dilation(sw,iterations=1);return m
def skin(a):
    r,g,b=[a[...,i].astype(int) for i in range(3)];m=(a[...,3]>200)&(r>150)&(g>95)&(b>70)&(r>g+15)&(g>b)&(r<250)
    return m
def meas(a):
    m=body(a);ys,xs=np.nonzero(m);top,bot=ys.min(),ys.max();h=bot-top
    head=m[top:top+18];hx=np.nonzero(head)[1].mean()
    tor=m[top+int(h*.25):top+int(h*.55)];tx=np.nonzero(tor)[1].mean()
    sk=skin(a);sk[top+40:]=False;chin=np.nonzero(sk.any(1))[0].max() if sk.any() else np.nan
    return top,bot,hx,tx,chin-top
if __name__=='__main__':
    print(f"{'동작':12s} 머리위  발  키   머리x 몸통x 머리~턱")
    for b in ['idle','walk','run','dash','jump']:
        for d in ['right','down','dr','up']:
            k=f'{b}_{d}'
            if not os.path.isdir(f'{F}/{k}'):continue
            M=np.array([meas(a) for a in load(k)],float)
            md=np.nanmedian(M,0);print(f'{k:12s} {md[0]:5.0f} {md[1]:4.0f} {md[1]-md[0]:4.0f}  {md[2]:5.1f} {md[3]:5.1f} {md[4]:5.0f}   머리위 {M[:,0].min():.0f}~{M[:,0].max():.0f}')
