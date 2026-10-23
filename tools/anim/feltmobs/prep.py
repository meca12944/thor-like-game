# Split each PixelLab 2-pose image (idle left / attack right) and place both on 256x256 canvases with shared feet line and back edge,
# ready for /v2/animate-with-text-v3 (first_frame / last_frame). usage: prep.py <felt dir> <out dir>
import sys,os,numpy as np
from PIL import Image
from scipy import ndimage
D,O=sys.argv[1:3];os.makedirs(O,exist_ok=True)
for n in ['thread_wraith','thread_puppet','needle_spider','stone_hound']:
    a=np.array(Image.open(f'{D}/{n}.png').convert('RGBA'));al=a[...,3]>=128;a[...,3]=np.where(al,255,0)
    w=a.shape[1];col=al.sum(0);lo,hi=int(w*.4),int(w*.6);cut=lo+int(np.argmin(col[lo:hi]))
    def box(m):
        lab,k=ndimage.label(m,structure=np.ones((3,3)));sz=ndimage.sum(m,lab,range(1,k+1));keep=np.isin(lab,[i+1 for i in range(k) if sz[i]>12])
        ys,xs=np.nonzero(keep);return xs.min(),ys.min(),xs.max()+1,ys.max()+1
    L=al.copy();L[:,cut:]=False;R=al.copy();R[:,:cut]=False
    ix0,iy0,ix1,iy1=box(L);ax0,ay0,ax1,ay1=box(R)
    idle=a[iy0:iy1,ix0:ix1];atk=a[ay0:ay1,ax0:ax1]
    s=min(1,236/max(idle.shape[0],atk.shape[0]),250/max(idle.shape[1],atk.shape[1]))
    left=max(3,min(128-int(idle.shape[1]*s/2),253-int(atk.shape[1]*s)))
    for tag,im in (('idle',idle),('atk',atk)):
        p=Image.fromarray(im);p=p.resize((round(p.width*s),round(p.height*s)),Image.NEAREST)
        c=Image.new('RGBA',(256,256),(0,0,0,0));c.alpha_composite(p,(left,250-p.height));c.save(f'{O}/{n}_{tag}.png')
    print(n,'scale',round(s,2),'idle',idle.shape[:2],'atk',atk.shape[:2])
