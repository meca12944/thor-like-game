from PIL import Image, ImageDraw
import numpy as np, cv2, json, os
N=16; FPS=8
os.makedirs('anim/frames',exist_ok=True)
for d in ('fx_glow','fx_smoke','fx_crows'): os.makedirs(f'anim/{d}',exist_ok=True)
C=np.array(Image.open('castle_far.png')).astype(np.float32)
H,W=C.shape[:2]
gm=np.array(Image.open('window_glow_mask_gray.png')).astype(np.float32)/255
wins=json.load(open('windows.json'))['windows']
rng=np.random.default_rng(7)
TAU=2*np.pi
# per-window flicker params (integer harmonics => periodic in N)
wid=np.zeros((H,W),np.int32)-1
for w in wins: 
    sl=(slice(w['y'],w['y']+w['h']),slice(w['x'],w['x']+w['w'])); wid[sl]=np.where(gm[sl]>0,w['id'],wid[sl])
fp=[(rng.integers(1,4),rng.uniform(0,TAU),rng.integers(2,6),rng.uniform(0,TAU),rng.uniform(.10,.22)) for _ in wins]
def flick(i,t):
    k1,p1,k2,p2,amp=fp[i]; u=t/N
    return 1+amp*(0.6*np.sin(TAU*k1*u+p1)+0.4*np.sin(TAU*k2*u+p2))
# ---- smoke: vertically tileable noise, rising one full period per loop
P=256
def tile_noise(w,h,scale,seed):
    r=np.random.default_rng(seed).random((h//scale,w//scale)).astype(np.float32)
    r=np.tile(r,(3,3)); r=cv2.resize(r,(w*3,h*3),interpolation=cv2.INTER_CUBIC)
    return r[h:2*h,w:2*w]
noise=0.6*tile_noise(512,P,32,1)+0.4*tile_noise(512,P,16,2)
sources=[(1925,540,1.0),(2205,760,0.8),(1262,40,0.55),(840,300,0.5)]  # broken east tops + spires
def smoke_layer(t):
    A=np.zeros((H,W),np.float32)
    off=int(round(P*t/N))
    for k,(sx,sy,s) in enumerate(sources):
        h=int(420*s); w=int(240*s)+60
        y0=max(0,sy-h); x0=sx-w//2
        yy=np.arange(y0,sy)[:,None]; xx=np.arange(x0,x0+w)[None,:]
        hrel=(sy-yy)/h                          # 0 at source,1 at top
        width=(0.15+0.85*hrel)*w/2
        drift=40*s*hrel**1.5                    # leans east (wind)
        prof=np.clip(1-np.abs(xx-sx-drift)/np.maximum(width,1),0,1)
        n=noise[((yy+off+k*61)%P), (xx-x0+k*97)%512]
        a=prof*np.clip((n-0.30)*2.4,0,1)*np.clip(hrel*14,0,1)*(1-hrel)**1.1*s*(1+0.8*(1-hrel)**3)
        xs=slice(max(x0,0),min(x0+w,W)); ax=slice(xs.start-x0,xs.stop-x0)
        A[y0:sy,xs]=np.maximum(A[y0:sy,xs],a[:,ax])
    # cel-style flat steps instead of airbrush
    A=np.where(A>0.45,0.34,np.where(A>0.22,0.2,np.where(A>0.08,0.09,0)))
    A=cv2.GaussianBlur(A,(5,5),1.2)
    return A
# ---- ash particles near spires (periodic paths)
ash=[(rng.uniform(1100,2300),rng.uniform(80,700),rng.uniform(0,1),rng.uniform(60,160),rng.integers(1,3),rng.uniform(0,TAU)) for _ in range(70)]
# ---- crows: fly off from towers, each phase-offset, fade at both ends of its cycle
crows=[]
for i in range(7):
    sx,sy=[(1925,520),(2150,700),(1262,120),(760,330),(1660,280),(1925,520),(560,420)][i]
    ang=rng.uniform(-2.6,-0.5); dist=rng.uniform(260,520)
    crows.append((sx,sy,np.cos(ang)*dist,np.sin(ang)*dist*0.6,rng.uniform(0,1),rng.uniform(0.8,1.3),rng.uniform(0,TAU)))
def draw_crow(d,x,y,sz,flap,a):
    col=(24,17,13,int(255*a))
    wy=-flap*sz*0.9
    pts=[(x-sz*1.6,y+wy*0.6),(x-sz*0.8,y+wy),(x,y),(x+sz*0.8,y+wy),(x+sz*1.6,y+wy*0.6)]
    d.line(pts,fill=col,width=max(2,int(sz*0.35)),joint='curve')
    d.ellipse((x-sz*0.3,y-sz*0.2,x+sz*0.3,y+sz*0.25),fill=col)
def crow_layer(t):
    S=2; im=Image.new('RGBA',(W*S//2,H*S//2))  # draw at full res (S/2=1); AA via supersample below
    big=Image.new('RGBA',(W*2,H*2)); d=ImageDraw.Draw(big)
    for (sx,sy,dx,dy,ph,sz,fph) in crows:
        u=(ph+t/N)%1
        a=min(1,u/0.12)*min(1,(1-u)/0.15)
        if a<=0: continue
        x=sx+dx*u; y=sy+dy*u-25*np.sin(np.pi*u)
        flap=np.sin(TAU*4*t/N+fph)
        s=(11+7*u)*sz
        draw_crow(d,x*2,y*2,s*2,flap,a)
    return np.array(big.resize((W,H),Image.LANCZOS)).astype(np.float32)/255
def over(dst,rgb,a):
    da=dst[...,3:4]/255; a=a[...,None]
    oa=a+da*(1-a)
    out=(rgb*a+dst[...,:3]*da*(1-a))/np.maximum(oa,1e-6)
    return np.dstack([out,oa*255])
glowcol=np.array([255,170,80],np.float32)
frames=[]
for t in range(N):
    F=C.copy()
    # window flicker: scale window pixels only
    fac=np.ones((H,W),np.float32)
    for w in wins:
        m=wid==w['id']; fac[m]=flick(w['id'],t)
    k=gm*(fac-1)  # signed
    F[...,:3]=np.clip(F[...,:3]+k[...,None]*(glowcol*0.9 - F[...,:3]*0.2)*1.6,0,255)
    gl=np.zeros((H,W,4),np.float32); gl[...,:3]=F[...,:3]; gl[...,3]=np.where(gm>0,C[...,3],0)
    Image.fromarray(gl.round().astype(np.uint8),'RGBA').save(f'anim/fx_glow/glow_{t:02d}.png',optimize=True)
    # smoke + ash
    SA=smoke_layer(t)
    ashA=np.zeros((H,W),np.float32)
    for (ax,ay,ph,L,kk,pp) in ash:
        u=(ph+kk*t/N)%1
        x=ax+8*np.sin(TAU*u+pp)+30*u; y=ay-L*u
        a=np.sin(np.pi*u)*0.8
        xi,yi=int(x),int(y)
        if 1<=xi<W-2 and 1<=yi<H-2: cv2.circle(ashA,(xi,yi),2 if kk==1 else 1,a,-1,lineType=cv2.LINE_AA)
    smokeRGB=np.empty((H,W,3),np.float32); smokeRGB[:]=(92,82,72)
    ashRGB=np.empty((H,W,3),np.float32); ashRGB[:]=(128,112,96)
    L=np.zeros((H,W,4),np.float32); L=over(L,smokeRGB,SA); L=over(L,ashRGB,ashA)
    Image.fromarray(L.round().astype(np.uint8),'RGBA').save(f'anim/fx_smoke/smoke_{t:02d}.png',optimize=True)
    F=over(F,smokeRGB,SA); F=over(F,ashRGB,ashA)
    CR=crow_layer(t)
    Image.fromarray((CR*255).round().astype(np.uint8),'RGBA').save(f'anim/fx_crows/crows_{t:02d}.png',optimize=True)
    F=over(F,CR[...,:3]*255,CR[...,3])
    F[F[...,3]<1]=0
    fr=Image.fromarray(F.round().astype(np.uint8),'RGBA'); fr.save(f'anim/frames/castle_anim_{t:02d}.png',optimize=True)
    frames.append(fr); print('frame',t,flush=True)
# spritesheet 4x4 at half res
cw,ch=W//2,H//2
sheet=Image.new('RGBA',(cw*4,ch*4))
for i,f in enumerate(frames): sheet.paste(f.resize((cw,ch),Image.LANCZOS),((i%4)*cw,(i//4)*ch))
sheet.save('anim/castle_anim_spritesheet_4x4_1280x720.png',optimize=True)
# gif preview over dark sepia
y=np.linspace(0,1,H)[:,None,None]; sky=(np.array([28,22,18])*(1-y)+np.array([70,55,42])*y)*np.ones((1,W,1))
sky=Image.fromarray(np.dstack([sky,np.full((H,W),255)]).astype(np.uint8),'RGBA')
g=[Image.alpha_composite(sky,f).convert('RGB').resize((1280,720),Image.LANCZOS) for f in frames]
g[0].save('anim/preview_dark_sepia.gif',save_all=True,append_images=g[1:],duration=1000//FPS,loop=0,optimize=False)
json.dump(dict(frames=N,fps=FPS,frame_size=[W,H],loop='seamless: frame N == frame 0 (all motion uses t/N periodic functions)',
  sheet=dict(file='castle_anim_spritesheet_4x4_1280x720.png',cols=4,rows=4,cell=[cw,ch],order='row-major'),
  layers=dict(frames='frames/castle_anim_XX.png (castle+all fx, composited)',fx_glow='fx_glow/glow_XX.png (lit window pixels only, flickered)',
  fx_smoke='fx_smoke/smoke_XX.png (smoke wisps + ash)',fx_crows='fx_crows/crows_XX.png')),open('anim/anim.json','w'),indent=1)
