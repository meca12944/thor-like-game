# Hidden-dive-spot decal: a small rain puddle baked from the background's own cobble pixels
# (darkened + teal-tinted, blocky 3px grain, sky-glint pixels) so it reads as ordinary scenery.
import json, numpy as np
from PIL import Image
A='/workspace/town-demo/assets/'
bg=np.asarray(Image.open('/workspace/town-demo/src/bg_town.jpg').convert('RGB')).astype(np.float32)
CX,CY=868,572; W,H=96,44; G=2          # centre in world px, decal box, pixel grain
x0,y0=CX-W//2,CY-H//2; c=bg[y0:y0+H,x0:x0+W].copy()
yy,xx=np.mgrid[0:H,0:W]; yy=(yy//G)*G+G/2; xx=(xx//G)*G+G/2
def e(cx,cy,rx,ry): return ((xx-cx)/rx)**2+((yy-cy)/ry)**2
ang=np.arctan2((yy-22)/12,(xx-48)/28); wob=1+.18*np.sin(ang*3+1)+.1*np.sin(ang*5+2)
r=e(48,22,28,12)/wob**2; r2=e(30,27,12,6)
m=(r<1)|(r2<1); edge=m&~((r<.62)|(r2<.5)); wet=~m&((r<1.7)|(r2<1.9))
lum=c.mean(2,keepdims=True)
water=c*.5+np.array([30,70,82])*.5*(.7+lum/255*.5)   # keeps the mortar-line pattern faintly visible
water[edge]=c[edge]*.62+np.array([20,50,60])*.38
water[wet]=c[wet]*.8
rng=np.random.default_rng(3)
gl=m&~edge&(yy<16)&(rng.random((H,W))<.0)  # placeholder
out=np.zeros((H,W,4),np.uint8); out[...,:3]=np.clip(water,0,255); out[...,3]=(m|wet)*255
for gx,gy in [(40,16),(56,15),(30,25)]:            # sky glints
    out[gy:gy+2,gx:gx+4,:3]=[132,178,184]
Image.fromarray(out,'RGBA').save(A+'decal_puddle.png')
M=json.load(open(A+'sprites.json'))
M['decal_puddle']=dict(src='decal_puddle.png',w=W,h=H,n=1,ax=W//2,ay=H//2)
json.dump(M,open(A+'sprites.json','w'),indent=1)
big=Image.fromarray(np.clip(bg,0,255).astype(np.uint8)).convert('RGBA');big.alpha_composite(Image.open(A+'decal_puddle.png'),(x0,y0))
big.crop((CX-110,CY-60,CX+110,CY+60)).resize((660,360),Image.NEAREST).save('/tmp/puddle_prev2.png')
