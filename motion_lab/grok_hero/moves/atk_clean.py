# 공격 사이 장 손질: 그림 도구가 넣은 검기(파란 빛·흰 줄)를 지우고, 몸이 조각났거나 효과가 많이 덮은 장은 뺌 (교과서 1-00 #8)
import glob,os,json,numpy as np
from PIL import Image
from scipy import ndimage
M=json.load(open('moves.json'))
def fx(A):
    c=A[...,:3].astype(int);a=A[...,3]>0;r,g,b=c[...,0],c[...,1],c[...,2]
    cyan=a&(b>r+35)&(b>90);white=a&(c.min(2)>170)&(c.max(2)-c.min(2)<50)
    return cyan|ndimage.binary_dilation(cyan,iterations=1)&a&(c.mean(2)>110)|white
for d in ('down','right','up'):
    for i in (1,2,3):
        k=f'atk{i}_{d}';fs=sorted(glob.glob(f'{k}/*.png'));pose=np.array(Image.open(fs[-1]).convert('RGBA'));ph=np.ptp(np.nonzero(pose[...,3].any(1))[0]);keep=[]
        for f in fs[:-1]:
            A=np.array(Image.open(f).convert('RGBA'));m=fx(A);ratio=m.sum()/max(1,(A[...,3]>0).sum());A[m]=0
            L,n=ndimage.label(ndimage.binary_dilation(A[...,3]>40,iterations=2));sz=np.bincount(L.ravel());sz[0]=0;big=sz.argmax();A[L!=big]=0
            h=np.ptp(np.nonzero(A[...,3].any(1))[0]) if A[...,3].any() else 0
            good=ratio<.08 and h>.8*ph and h<1.2*ph
            if good: Image.fromarray(A).save(f);keep.append(f)
            else: os.remove(f)
        for j,f in enumerate(keep+[fs[-1]]):
            if f!=f'{k}/{j:03d}.png': os.rename(f,f'{k}/{j:03d}.png')
        n=len(keep);M[k]['frames']=n+1;M[k]['ticks']=[1]*n+[9-n];print(k,'사이 장',n,'남김')
json.dump(M,open('moves.json','w'),indent=1)
