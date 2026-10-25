from PIL import Image
import numpy as np
c=Image.open('castle_far.png')
W,H=c.size
def bgsolid(col): return Image.new('RGBA',(W,H),col)
# dark sepia sky gradient (flat bands for preview only)
y=np.linspace(0,1,H)[:,None,None]
top=np.array([28,22,18]);bot=np.array([70,55,42])
sky=(top*(1-y)+bot*y)*np.ones((1,W,1))
sky=Image.fromarray(np.dstack([sky,np.full((H,W),255)]).astype(np.uint8),'RGBA')
Image.alpha_composite(sky,c).convert('RGB').save('preview_dark_sepia.png')
for n,col in [('white',(255,255,255,255)),('black',(0,0,0,255)),('magenta',(255,0,255,255))]:
    Image.alpha_composite(bgsolid(col),c).convert('RGB').save(f'/tmp/chk_{n}.png')
# crops for fringe check
for n in ['white','black','magenta']:
    im=Image.open(f'/tmp/chk_{n}.png')
    im.crop((1150,0,1450,300)).resize((600,600),Image.NEAREST).save(f'/tmp/crop_{n}_spire.png')
    im.crop((2200,600,2560,900)).resize((720,600),Image.NEAREST).save(f'/tmp/crop_{n}_east.png')
a=np.array(c).astype(int)
op=a[...,3]>0
g=a[...,1]-np.maximum(a[...,0],a[...,2])
print('green-dominant visible px:',int(((g>10)&op).sum()),'of',int(op.sum()))
print('rows with alpha at bottom row fraction:',(a[-1,:,3]>128).mean(),'top row:',(a[0,:,3]>0).sum(),'left col:',(a[:,0,3]>0).sum(),'right col:',(a[:,-1,3]>0).sum())
ys,xs=np.where(a[...,3]>128);print('bbox',xs.min(),xs.max(),ys.min(),ys.max())
