# 필멸자 기본 외형: 갈색 머리 → 검은 머리 팔레트 스왑 (머리 영역 + 갈색 계열만)
import json, colorsys, os, shutil, sys
import numpy as np
from PIL import Image
A=os.path.join(os.path.dirname(__file__),'..','assets'); O=os.path.join(A,'..','assets_orig_hair')
S=json.load(open(os.path.join(A,'sprites.json')))
HERO=[k for k in S if k.startswith(('hero_','cb_','sk_'))]
def hairmask(a):
    rgb=a[...,:3]/255.0; mx=rgb.max(-1); mn=rgb.min(-1); v=mx; s=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
    h=np.zeros_like(mx); d=np.maximum(mx-mn,1e-6)
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60
    return (a[...,3]>0)&(h>=12)&(h<=42)&(s>0.30)&(v>0.08)&(v<0.66)
def black(a,m):
    rgb=a[...,:3].astype(float); lum=(0.3*rgb[...,0]+0.59*rgb[...,1]+0.11*rgb[...,2])/255
    t=np.clip((lum-0.08)/0.5,0,1)   # 어두운 곳 #121216 → 밝은 곳 #4c4c5c (푸른빛 도는 흑발 하이라이트)
    lo=np.array([18,18,22]); hi=np.array([76,76,92])
    out=lo+(hi-lo)*t[...,None]
    a[...,:3][m]=out[m].astype(np.uint8); return a
for k in HERO:
    sp=S[k]; src=os.path.join(A,sp['src']); orig=os.path.join(O,sp['src'])
    if not os.path.exists(orig): shutil.copy(src,orig)
    im=np.array(Image.open(orig).convert('RGBA')); H,W=im.shape[:2]
    win=np.zeros((H,W),bool); HM=hairmask(im)
    rgb=im[...,:3]/255.0; mx=rgb.max(-1); mn=rgb.min(-1); d=np.maximum(mx-mn,1e-6); r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
    HUE=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60; VAL=mx
    big=k.startswith('hero_walk')   # 걷기 시트는 얼굴이 밝아서 넓게 잡아도 안전
    n=sp['n']; anchors=sp.get('srcAnchor'); bh=sp.get('bodyH',[165]*n)
    for i in range(n):
        ax=i*sp['w']+sp['ax']; ay=sp['ay']
        bH=bh[i] if 'bodyH' in sp and i<len(bh) else min(165,ay*0.98)
        y0=int(max(0,ay-bH*1.08)); y1=int(max(0,ay-bH*0.60)); x0=int(max(0,ax-bH*0.42)); x1=int(min(W,ax+bH*0.42))
        hm=HM[y0:y1,x0:x1]; rows=np.where(hm.sum(1)>=3)[0]
        if not len(rows): continue
        top=y0+rows[0]
        za=int(top+bH*(0.115 if not big else 0.20)); zb=int(top+bH*(0.21 if not big else 0.30))
        win[y0:za,x0:x1]=True
        sub=np.zeros((H,W),bool); sub[za:zb,x0:x1]=True
        win|=sub&(HUE>=24)|sub&(VAL<0.42)
    m=HM&win
    im=black(im,m); Image.fromarray(im).save(src); print(k,int(m.sum()))
