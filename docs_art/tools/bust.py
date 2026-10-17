# usage: bust.py <char_id> <cx> <fx> <fy> <rx> <ry>   (coords in 1280x720 gen space)
# reads gen/<char>_{neutral,smile,angry,sad,surprised,blush}.jpg
import sys, numpy as np, cv2, os
from PIL import Image, ImageFilter
from rembg import remove, new_session
cid=sys.argv[1]; cx,fx,fy,rx,ry=map(int,sys.argv[2:7])
EX=['neutral','smile','angry','sad','surprised','blush']
OUT=f'/workspace/thor-like-game/docs_art/bust/{cid}'; os.makedirs(OUT,exist_ok=True)
base=np.array(Image.open(f'gen/{cid}_neutral.jpg').convert('RGB'))
H,W=base.shape[:2]
sess=new_session('isnet-anime')
rm=np.array(remove(Image.fromarray(base),session=sess,only_mask=True,post_process_mask=True)).astype(np.float32)/255
def make_alpha(img):
    dist=255-img.min(2).astype(np.float32)
    cand=(dist<48).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(cand,8)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))
    bg=np.zeros(cand.shape,bool)
    for i in range(1,n):
        if i in border: bg|=lab==i
        else:
            m=lab==i
            if rm[m].mean()<0.5: bg|=m   # enclosed white gap that rembg calls background
    near=cv2.dilate(bg.astype(np.uint8),np.ones((5,5),np.uint8))>0
    a=np.ones(cand.shape,np.float32)
    soft=np.clip((dist-12)/90.0,0,1)
    a[near]=soft[near]; a[bg]=np.clip((dist[bg]-25)/90,0,1)
    return cv2.GaussianBlur(a,(3,3),0)
alpha=make_alpha(base)
if os.environ.get('UNION_RM'):
    core=cv2.erode((rm>0.5).astype(np.uint8),np.ones((5,5),np.uint8)).astype(np.float32)
    alpha=np.maximum(alpha,cv2.GaussianBlur(core,(5,5),0))
    dist0=255-base.min(2).astype(np.float32)
    pw=(dist0<10).astype(np.uint8)
    n,l,st,_=cv2.connectedComponentsWithStats(pw,8)
    kill=np.zeros(pw.shape,np.uint8)
    for i in range(1,n):
        if st[i,4]<40: continue
        x,y,w,h=st[i,:4]; sub=(l[max(0,y-6):y+h+6,max(0,x-6):x+w+6]==i).astype(np.uint8)
        ring=cv2.dilate(sub,np.ones((9,9),np.uint8))-sub
        dd=dist0[max(0,y-6):y+h+6,max(0,x-6):x+w+6][ring>0]
        if dd.size and (dd>100).mean()>0.35: kill[l==i]=1
    kill[(yy0:=0):0]=0
    kill=cv2.dilate(kill,np.ones((3,3),np.uint8))
    alpha=np.where(kill>0,np.minimum(alpha,np.clip((dist0-4)/30,0,1)),alpha)
    alpha=cv2.GaussianBlur(alpha.astype(np.float32),(3,3),0)
yy,xx=np.mgrid[0:H,0:W]
d=((xx-fx)/rx)**2+((yy-fy)/ry)**2
mask=np.clip((1.0-d)/0.35,0,1)  # feathered ellipse
mask=cv2.GaussianBlur(mask.astype(np.float32),(0,0),6)[...,None]
gb=cv2.cvtColor(base,cv2.COLOR_RGB2GRAY).astype(np.float32)
for e in EX:
    if e=='neutral': img=base.copy()
    else:
        im=np.array(Image.open(f'gen/{cid}_{e}.jpg').convert('RGB').resize((W,H)))
        gi=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY).astype(np.float32)
        warp=np.eye(2,3,dtype=np.float32)
        try:
            _,warp=cv2.findTransformECC(gb,gi,warp,cv2.MOTION_TRANSLATION,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,100,1e-5))
        except cv2.error: pass
        im=cv2.warpAffine(im,warp,(W,H),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)
        print(e,'shift',warp[:,2].round(1))
        img=(im*mask+base*(1-mask)).astype(np.uint8)
    a3=np.clip(alpha,1e-3,1)[...,None]
    dec=np.clip((img.astype(np.float32)-255*(1-a3))/a3,0,255)
    edge=((alpha>0.02)&(alpha<0.98))[...,None]
    img=np.where(edge,dec,img).astype(np.uint8)
    rgba=np.dstack([img,(alpha*255).astype(np.uint8)])
    w=int(H*0.8); x0=max(0,min(W-w,cx-w//2))
    crop=Image.fromarray(rgba,'RGBA').crop((x0,0,x0+w,H))
    # premultiply-safe resize
    out=crop.resize((1024,1280),Image.LANCZOS)
    r,g,b,a=out.split(); rgb=Image.merge('RGB',(r,g,b)).filter(ImageFilter.UnsharpMask(1.6,60,2))
    out=Image.merge('RGBA',(*rgb.split(),a))
    out.save(f'{OUT}/{e}.png',optimize=True)
print('ok',OUT)
