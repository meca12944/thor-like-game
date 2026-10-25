# 그록 얼굴 판 칸 맞추기 (팀장 10-25: 그록은 1배를 못 그림 → 「게임 1px = 10×10 칸」으로 받아 우리가 1배로)
# 1) 칸 크기·시작점 찾기: 가로·세로 색 변화가 몰리는 줄의 간격(기본 10 근처 8~12 탐색) 2) 칸마다 가운데 60%의 중간값 색 3) 정해진 색표(hex)에서 가장 가까운 색, 투명 칸은 투명
# usage: snap.py <그록.png> <out.png> [--pal hex,hex,...] [--n 6] [--cell 10]
import sys,numpy as np
from PIL import Image
def arg(k,d=None): return sys.argv[sys.argv.index(k)+1] if k in sys.argv else d
src,out=sys.argv[1],sys.argv[2];im=Image.open(src).convert('RGBA');A=np.array(im).astype(float)
def edges(axis):
    d=np.abs(np.diff(A[...,:3],axis=axis)).sum(2)+np.abs(np.diff(A[...,3],axis=axis))*2;return d.sum(1-axis)
def grid(prof,c0):
    best=(-1,None)
    for c in np.arange(c0-2,c0+2.01,0.05):
        for o in np.arange(0,c,0.5):
            idx=np.round(np.arange(o,len(prof),c)).astype(int);idx=idx[(idx>0)&(idx<len(prof))]
            s=prof[idx-1].mean()
            if s>best[0]: best=(s,(c,o))
    return best[1]
c0=float(arg('--cell',10))
cx,ox=grid(edges(1),c0);cy,oy=grid(edges(0),c0)
W=int((A.shape[1]-ox)//cx);H=int((A.shape[0]-oy)//cy);O=np.zeros((H,W,4),np.uint8)
for j in range(H):
    for i in range(W):
        x0,x1=ox+i*cx,ox+(i+1)*cx;y0,y1=oy+j*cy,oy+(j+1)*cy;m=.2
        blk=A[int(y0+m*cy):int(y1-m*cy)+1,int(x0+m*cx):int(x1-m*cx)+1].reshape(-1,4)
        if blk[:,3].mean()<128: continue
        O[j,i,:3]=np.median(blk[blk[:,3]>=128][:,:3],0);O[j,i,3]=255
pal=arg('--pal')
if pal: P=np.array([[int(h[k:k+2],16) for k in (0,2,4)] for h in pal.replace('#','').split(',')],float)
else:
    from scipy.cluster.vq import kmeans2
    px=O[O[...,3]>0][:,:3].astype(float);P,_=kmeans2(px,int(arg('--n',6)),seed=1,minit='++')
on=O[...,3]>0;d=((O[...,:3][on][:,None,:].astype(float)-P[None])**2).sum(2);O[...,:3][on]=P[d.argmin(1)].astype(np.uint8)
Image.fromarray(O).save(out);print('칸',round(cx,2),round(cy,2),'시작',ox,oy,'→',W,'x',H,'색',len(P))
