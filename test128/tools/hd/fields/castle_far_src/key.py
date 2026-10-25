from PIL import Image, ImageFilter
import numpy as np, cv2
src=Image.open('src/gen_castle_try3.jpg').convert('RGB')
W,H=2560,1440
up=src.resize((W,H),Image.LANCZOS)
up=up.filter(ImageFilter.UnsharpMask(radius=1.6,percent=60,threshold=2))
a=np.array(up).astype(np.float32)
r,g,b=a[...,0],a[...,1],a[...,2]
gn=g-np.maximum(r,b)          # greenness
# alpha: gn<=25 opaque, gn>=90 transparent
al=np.clip((90-gn)/(90-25),0,1)
# clean: morphological to kill specks & fill pinholes in solid castle
m=(al>0.5).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(m,8)
keep=np.zeros(n,bool); keep[1:]=st[1:,cv2.CC_STAT_AREA]>400
al=al*keep[lab]
# fill small transparent holes (<60px) inside castle
inv=(al<0.5).astype(np.uint8)
n2,lab2,st2,_=cv2.connectedComponentsWithStats(inv,4)
small=np.zeros(n2,bool); small[1:]=st2[1:,cv2.CC_STAT_AREA]<60
al=np.where(small[lab2],1.0,al)
# slight edge AA: blur alpha within 1px band
alb=cv2.GaussianBlur(al,(3,3),0.7)
edge=(cv2.dilate((al>0.5).astype(np.uint8),np.ones((3,3)))-cv2.erode((al>0.5).astype(np.uint8),np.ones((3,3))))>0
al=np.where(edge,alb,al)
# despill
lim=np.maximum(r,b)*1.0
g2=np.minimum(g,lim+4)
# on semi-transparent edges, un-premultiply against green bg
bg=np.array([0,174,8],np.float32)
rgb=np.stack([r,g2,b],-1)
semi=(al>0.02)&(al<0.98)
est=(a-bg*(1-al[...,None]))/np.maximum(al[...,None],0.02)
est[...,1]=np.minimum(est[...,1],np.maximum(est[...,0],est[...,2])+4)
rgb=np.where(semi[...,None],np.clip(est,0,255),rgb)
# gentle sepia grade: pull toward warm monochrome, keep orange windows
lum=0.3*rgb[...,0]+0.59*rgb[...,1]+0.11*rgb[...,2]
sep=np.stack([lum*1.07,lum*0.97,lum*0.84],-1)
sat=(np.max(rgb,-1)-np.min(rgb,-1))
orange=(rgb[...,0]-rgb[...,2]>55)&(rgb[...,0]>120)
k=np.where(orange,0.15,0.45)[...,None]
rgb=np.clip(rgb*(1-k)+sep*k,0,255)
al[al<0.03]=0
rgb[al==0]=0
out=np.dstack([rgb,al*255]).round().astype(np.uint8)
Image.fromarray(out,'RGBA').save('castle_far.png',optimize=True)
np.save('/tmp/orange_mask.npy',orange&(al>0.9))
print('done',out.shape, (al==0).mean(), ((al>0)&(al<1)).mean())
