from PIL import Image
import numpy as np, cv2, json
c=np.array(Image.open('castle_far.png')).astype(np.int32)
H,W=c.shape[:2]; al=c[...,3]
# ---- windows
r,g,b=c[...,0],c[...,1],c[...,2]
o=((r-g>38)&(r-b>70)&(r>110)&(al>230)).astype(np.uint8)
o=cv2.morphologyEx(o,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(o,8)
wins=[];mask=np.zeros((H,W),np.float32)
for i in range(1,n):
    x,y,w,h,A=st[i]
    if A<12 or w>60 or h>90: continue
    wins.append(dict(id=len(wins),x=int(x),y=int(y),w=int(w),h=int(h),cx=round(float(cen[i][0]),1),cy=round(float(cen[i][1]),1),area=int(A)))
    mask[lab==i]=1
# soft glow-mask: window pixels weighted by orange strength
strength=np.clip((r-g-25)/50,0,1)
gm=np.clip(mask*(0.35+0.65*strength),0,1)
gm=cv2.GaussianBlur(gm,(3,3),0.6)*(al/255)
gmu=(gm*255).astype(np.uint8)
Image.fromarray(np.dstack([np.full((H,W),255,np.uint8)]*3+[gmu]),'RGBA').save('window_glow_mask.png')
Image.fromarray(gmu,'L').save('window_glow_mask_gray.png')
json.dump(dict(canvas=[W,H],count=len(wins),note='bbox in castle_far.png pixel coords (2560x1440); lit-window pixels only',windows=wins),open('windows.json','w'),indent=1)
print('windows',len(wins))

# ---- front/back split: front = lower rampart band (hard cut at y=CUT, solid wall face)
CUT=1345
cimg=Image.open('castle_far.png')
ca=np.array(cimg)
front=ca.copy(); front[:CUT]=0
back=ca.copy()   # full castle; area under front kept so parallax never opens holes
edge=(np.arange(ca.shape[0])[:,None]>=CUT)&(ca[...,3]<255)
back[edge]=0
Image.fromarray(front,'RGBA').save('castle_far_front.png',optimize=True)
Image.fromarray(back,'RGBA').save('castle_far_back.png',optimize=True)
Image.fromarray(np.zeros_like(ca),'RGBA').save('banners.png',optimize=True)
st=Image.alpha_composite(Image.alpha_composite(Image.open('castle_far_back.png'),Image.open('castle_far_front.png')),Image.open('banners.png'))
d=np.abs(np.array(st).astype(int)-ca.astype(int))
d[ca[...,3]==0,:3]=0
print('stack max diff',d.max(),'alpha diff',d[...,3].max())
