# 정면 공격 장의 흐린 푸른 검기 줄 2차 지우기 (팀장 10-25): 옷(짙은 남색, 밝기<55)보다 밝은 청회색(b>r+18, b>g+4, 밝기 55~200) 칸
# 몸 밖(투명과 닿은 가는 줄)은 지우고, 몸 안은 주변 옷 색 평균으로 메움. 대상: final_stampedB2/atk*_down 모든 장
import glob,numpy as np
from PIL import Image
from scipy import ndimage
for f in sorted(glob.glob('final_stampedB2/atk*_down/*.png')):
    A=np.array(Image.open(f).convert('RGBA')).astype(int);c=A[...,:3];m=c.mean(2);on=A[...,3]>0
    bl=on&(c[...,2]>c[...,0]+18)&(c[...,2]>c[...,1]+4)&(m>55)&(m<200)
    bl=ndimage.binary_dilation(bl,iterations=1)&on&(c[...,2]>c[...,0]+8)
    out=ndimage.binary_dilation(~on,iterations=2)&bl;A[out]=0;fill=bl&~out
    keep=on&~bl
    for _ in range(6):
        if not fill.any(): break
        acc=np.zeros(A.shape[:2]+(4,));cnt=np.zeros(A.shape[:2])
        for dy in (-1,0,1):
            for dx in (-1,0,1): acc+=np.roll(np.roll(A*keep[...,None],dy,0),dx,1);cnt+=np.roll(np.roll(keep,dy,0),dx,1)
        ok=fill&(cnt>0);A[ok]=(acc[ok]/cnt[ok][:,None]).astype(int);A[ok,3]=255;keep|=ok;fill&=~ok
    L,n=ndimage.label(A[...,3]>0);sz=np.bincount(L.ravel());sz[0]=0;A[(L!=sz.argmax())&(sz[L]<25)]=0
    Image.fromarray(A.astype('uint8')).save(f);print(f,'지움',int(out.sum()),'메움',int(bl.sum()-out.sum()))
