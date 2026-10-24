# 정면 1·3타 몸 그림에 남은 검기 자국 지우기 (검기는 코드로 그림). 대상 frames/<칸>/000.png, 원본은 000_raw.png로 둠
# ① 밝은 청백 띠(파랑 강함) → 주변 몸 색으로 메움  ② 몸 밖 가는 줄(두께 2px 이하, 회청색) → 지움
import sys,os,numpy as np
from PIL import Image
from scipy import ndimage
R=os.path.dirname(os.path.abspath(__file__))
for k in sys.argv[1:]:
    p=f'{R}/frames/{k}/000.png';raw=f'{R}/frames/{k}/000_raw.png'
    if not os.path.exists(raw): Image.open(p).save(raw)
    A=np.array(Image.open(raw).convert('RGBA')).astype(int);r,g,b,a=[A[...,i] for i in range(4)];mean=(r+g+b)/3;on=a>0
    blue=on&(b>r+20)&(g>r+5)&(mean>60);blue|=on&(mean>150)&ndimage.binary_dilation(blue,iterations=3)
    thick=ndimage.binary_opening(on,iterations=2)
    thin=on&~ndimage.binary_dilation(thick,iterations=1)&(mean>45)&~(r>g+12)   # 몸 밖 가는 회청 줄 (갈색 장화·피부는 남김)
    body=ndimage.binary_dilation(thick&~blue,iterations=1)
    gone=(blue|thin)&~(body&~blue)   # 몸 밖 → 지움
    fill=blue&body                     # 몸 위 → 주변 색
    B=A.copy();B[gone]=0
    keep=on&~blue&~gone
    for _ in range(6):
        if not fill.any(): break
        acc=np.zeros(A.shape[:2]+(4,));cnt=np.zeros(A.shape[:2])
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                acc+=np.roll(np.roll(B*keep[...,None],dy,0),dx,1);cnt+=np.roll(np.roll(keep,dy,0),dx,1)
        ok=fill&(cnt>0);B[ok]=(acc[ok]/cnt[ok][:,None]).astype(int);B[ok,3]=255;keep|=ok;fill&=~ok
    L,n=ndimage.label(B[...,3]>0);big=np.argmax(np.bincount(L.ravel())[1:])+1;sz=np.bincount(L.ravel());B[(L!=big)&(sz[L]<30)]=0
    Image.fromarray(B.astype('uint8')).save(p);print(k,'지움',int(gone.sum()),'메움',int((blue&body).sum()))
