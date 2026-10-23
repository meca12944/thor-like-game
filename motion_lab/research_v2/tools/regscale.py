# 같은 방향 서기 그림과 비교해서 "몸 크기 배율" 찾기: 머리~가슴 부분을 0.80~1.20배로 바꿔 가며 가장 잘 겹치는 배율
import sys,os,numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from measure8 import load,body
def feat(a):
    m=body(a).astype(float);g=a[...,:3].astype(float).mean(2)/255*m
    return np.stack([m,ndimage.sobel(g,0),ndimage.sobel(g,1)],-1)
def crop_ref(a,frac=.42):
    m=body(a);ys,xs=np.nonzero(m);top=ys.min();h=ys.max()-top
    y1=top+int(h*frac);x0,x1=xs[(ys<y1)].min(),xs[(ys<y1)].max()
    return top,y1,x0,x1
def best_scale(ref,a,ss=np.arange(.80,1.205,.01)):
    t,y1,x0,x1=crop_ref(ref);R=feat(ref)[t:y1,x0:x1];best=(-9,1)
    ma=body(a);ta=np.nonzero(ma.any(1))[0].min()
    for s in ss:
        im=Image.fromarray(a);w=round(256*s);b=np.array(im.resize((w,w),Image.BILINEAR));F=feat(b)
        tb=np.nonzero(body(b).any(1))[0].min()
        for dy in range(-4,5,2):
            yy=tb+dy
            for dx in range(-30,31,3):
                xx=round(x0*s)+dx+round(128*s-128)*0
                xx=x0+dx+round((w-256)/2)
                if yy<0 or xx<0 or yy+R.shape[0]>w or xx+R.shape[1]>w:continue
                P=F[yy:yy+R.shape[0],xx:xx+R.shape[1]]
                sc=(R*P).sum()/np.sqrt((R*R).sum()*(P*P).sum()+1e-9)
                if sc>best[0]:best=(sc,s)
    return best[1],best[0]
if __name__=='__main__':
    for d in ['right','down','dr','up']:
        ref=load(f'idle_{d}')[0]
        for b in ['walk','run']:
            fr=load(f'{b}_{d}');v=[best_scale(ref,a) for a in fr[::2]]
            print(f'{b}_{d}','배율',[round(x[0],2) for x in v],'맞음',[round(x[1],2) for x in v])
