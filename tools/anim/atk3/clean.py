# remove PixelLab grey smudges: grey (desaturated, mid/light) blobs that are not the long thin blade. usage: clean.py <in dir> <out dir>
import sys,os,numpy as np
from PIL import Image
from scipy import ndimage
src,dst=sys.argv[1:3];os.makedirs(dst,exist_ok=True)
for f in sorted(os.listdir(src)):
    a=np.array(Image.open(f'{src}/{f}').convert('RGBA'));rgb=a[...,:3].astype(int)
    m=(a[...,3]>0)&((rgb.max(-1)-rgb.min(-1))<16)&(rgb.mean(-1)>70)
    lab,n=ndimage.label(m,structure=np.ones((3,3)));cut=0;blades=[]
    for i in range(1,n+1):
        ys,xs=np.nonzero(lab==i)
        if len(ys)<25: continue
        ev=np.linalg.eigvalsh(np.cov(np.vstack([xs,ys])))
        if ev[1]/max(ev[0],0.25)>12: blades.append((ev[1],i,len(ys)));continue   # long thin = blade
        a[lab==i,3]=0;cut+=len(ys)
    blades.sort()
    for _,i,k in blades[:-1]:                          # only one sword: keep the longest blade, drop stray blade bits
        if _<0.5*blades[-1][0]: a[lab==i,3]=0;cut+=k
    # drop specks left floating after the cut
    al=a[...,3]>0;l2,n2=ndimage.label(al,structure=np.ones((3,3)))
    if n2>1:
        sz=ndimage.sum(al,l2,range(1,n2+1));big=np.argmax(sz)+1
        for i in range(1,n2+1):
            if i!=big and sz[i-1]<40: a[l2==i,3]=0
    Image.fromarray(a).save(f'{dst}/{f}')
    if cut: print(f,'cut',cut)
