# paste the idle (standing) face onto edited down-attack frames, aligned by head top/centre; writes pasted png + ring mask for inpaint-v3
import sys,glob,numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user/605da03e-2542-5329-b23f-a50876f99780/scratchpad/face');from locate import find,HB
from PIL import Image
IDLE='/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/south/000.png'
FB=(112,73,135,98)   # face box in the idle frame (bangs edge .. chin)
def head(a):
    op=a[...,3]>200;dark=op&(a[...,:3].max(-1)<90)&(a[...,2]>=a[...,0]-10)   # hair = dark navy
    ys,xs=np.nonzero(dark[:150]);top=ys.min()
    band=(ys<top+28);return top,int(np.median(xs[band]))
idle=np.array(Image.open(IDLE).convert('RGBA'));it,ic=head(idle)
face=idle[FB[1]:FB[3],FB[0]:FB[2]]
for src,out in zip(sys.argv[1::2],sys.argv[2::2]):
    a=np.array(Image.open(src).convert('RGBA'));sc,hx,hy=find(a)
    x0=FB[0]-HB[0]+hx;y0=FB[1]-HB[1]+hy;t,c=hy,hx
    b=a.copy();b[y0:y0+face.shape[0],x0:x0+face.shape[1]]=face
    Image.fromarray(b).save(out+'_paste.png')
    m=np.zeros(a.shape[:2],np.uint8);m[y0-5:y0+face.shape[0]+5,x0-5:x0+face.shape[1]+5]=255;m[y0+5:y0+face.shape[0]-6,x0+5:x0+face.shape[1]-5]=0
    Image.fromarray(m).convert('RGB').save(out+'_mask.png');print(out,'head',t,c,'paste at',x0,y0)
