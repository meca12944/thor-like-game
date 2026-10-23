# head size = blue ribbon top -> top of the red bikini top (first red row), median per clip; also full-height, head-to-skirt
import glob,sys,numpy as np
from PIL import Image
def m(f):
    a=np.array(Image.open(f).convert('RGBA')).astype(int);al=a[:,:,3]>0
    by=np.where(al&(a[:,:,2]>a[:,:,0]+40)&(a[:,:,2]>120))[0];red=al&(a[:,:,0]>150)&(a[:,:,1]<70)&(a[:,:,2]<80);ry=np.where(red)[0]
    if not len(by) or not len(ry):return None
    return ry.min()-by.min(),ry.max()-by.min()
D=sys.argv[1] if len(sys.argv)>1 else 'frames_polished'
for mo in ('idle','walk','run','cast'):
    for d in ('right','down','up','south','north'):
        fs=sorted(glob.glob(f'{D}/{mo}/{d}/*.png'));v=[x for x in map(m,fs) if x]
        if v:h=sorted(x[0] for x in v);u=sorted(x[1] for x in v);print(mo,d,'head',h[len(h)//2],'upper',u[len(u)//2])
