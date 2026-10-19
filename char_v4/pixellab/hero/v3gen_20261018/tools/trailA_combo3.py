#!/usr/bin/env python3
"""Trail A: trail_w1_a45 style (thin white->lavender crescent, peak 0.45) composited over the no-effect combo frames.
Tip tracked per frame from blade pixels (light, low-saturation, largest blade component); arc interpolated in polar coords
around the shoulder so the head sits on the tip and follows tip radius (full blade length). Slash frames only (fast tip motion);
afterwards the trail thins and scatters on its own layer for 2 frames. Writes fx layers + composited frames."""
import os, json, numpy as np
from PIL import Image
from scipy import ndimage as nd
O=os.environ.get('C3','/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/combo3_v1'); A=O+'/trailA'
D=['south','east','north','west']; PEAK=0.45
WHITE=np.array([255,255,255.]);LAV=np.array([222,204,245.]);PUR=np.array([168,130,215.])
def load(h,d): p=f'{O}/hit{h}/{d}'; return [np.array(Image.open(f'{p}/{f}').convert('RGBA')) for f in sorted(os.listdir(p)) if f.endswith('.png')]
def shoulder(a):
    ys,xs=np.nonzero(a[...,3]>0); y0,y1=ys.min(),ys.max(); band=(ys>y0+0.22*(y1-y0))&(ys<y0+0.45*(y1-y0))
    return np.array([xs[band].mean(), ys[band].mean()])
def blade(a,sh):
    rgb=a[...,:3].astype(int); mx=rgb.max(-1); mn=rgb.min(-1)
    m=(a[...,3]>0)&(mx>140)&(mx-mn<45)&(rgb[...,2]>=rgb[...,0]-5)
    lab,n=nd.label(nd.binary_dilation(m,iterations=1),structure=np.ones((3,3)))
    if n==0: return None
    best=None
    for i in range(1,n+1):
        ys,xs=np.nonzero((lab==i)&m)
        if len(xs)<6: continue
        pts=np.stack([xs,ys],1).astype(float); dd=np.hypot(*(pts-sh).T)
        ext=np.ptp(pts,0).max()
        score=ext*(1+dd.max()/100)
        if best is None or score>best[0]: best=(score,pts[dd.argmax()],pts[dd.argmin()],ext)
    return None if best is None or best[3]<14 else best
def stroke(H,W,pts,width,alpha_head):
    """pts: polyline head(first)->tail. tapered flag stroke: thick at head, thin tail."""
    yy,xx=np.mgrid[0:H,0:W]; field=np.zeros((H,W)); core=np.zeros((H,W))
    n=len(pts)
    for k in range(n-1):
        p,q=pts[k],pts[k+1]; t0,t1=k/(n-1),(k+1)/(n-1)
        v=q-p; L2=max((v**2).sum(),1e-6)
        t=np.clip(((xx-p[0])*v[0]+(yy-p[1])*v[1])/L2,0,1)
        dist=np.hypot(xx-(p[0]+t*v[0]),yy-(p[1]+t*v[1]))
        s=t0+(t1-t0)*t; w=width*(1-s)**0.9+0.4
        inside=np.clip((w-dist)/1.0+0.5,0,1)*(1-s)**0.6
        field=np.maximum(field,inside); core=np.maximum(core,np.clip((w*0.45-dist)/1.0+0.5,0,1)*(1-s))
    col=PUR[None,None]*(1-field[...,None])+LAV[None,None]*field[...,None]
    col=col*(1-core[...,None])+WHITE*core[...,None]
    al=PEAK*255*alpha_head*field*(0.45+0.55*core)
    out=np.zeros((H,W,4),np.uint8); out[...,:3]=np.clip(col,0,255); out[...,3]=np.round(al)
    out[out[...,3]<6]=0; return out
def arc(sh,t_prev,t_cur,d,steps=18):
    a0=np.arctan2(*(t_prev-sh)[::-1]); a1=np.arctan2(*(t_cur-sh)[::-1]); da=(a1-a0+np.pi)%(2*np.pi)-np.pi
    if abs(da)>2.0:  # cross-body sweep: pick the bulge per SWORD_ARC_RULES (front=smile/below, back & side=over the top)
        alt=da-np.sign(da)*2*np.pi; mid=lambda x: np.sin(a0+x/2)  # +y is down
        want_down=(d=='south')
        da=max([da,alt],key=lambda x: mid(x) if want_down else -mid(x))
    r0,r1=np.hypot(*(t_prev-sh)),np.hypot(*(t_cur-sh))
    s=np.linspace(0,1,steps); ang=a1-da*s; r=r1+(r0-r1)*s
    return np.stack([sh[0]+r*np.cos(ang),sh[1]+r*np.sin(ang)],1)  # head (current tip) -> tail (previous)
rng=np.random.default_rng(45); meta={}
for d in D:
  for h in (1,2,3):
    fr=load(h,d); H,W=fr[0].shape[:2]; sh=[shoulder(a) for a in fr]; bl=[blade(a,s) for a,s in zip(fr,sh)]
    tips=[None if b is None else b[1] for b in bl]
    # angular speed of tip around shoulder
    spd=[0.0]*len(fr)
    for i in range(1,len(fr)):
        if tips[i] is None or tips[i-1] is None: continue
        a0=np.arctan2(*(tips[i-1]-sh[i])[::-1]); a1=np.arctan2(*(tips[i]-sh[i])[::-1])
        spd[i]=abs((a1-a0+np.pi)%(2*np.pi)-np.pi)*np.hypot(*(tips[i]-sh[i]))  # px of arc
    # slash frames: top-2 fastest with arc >= 18 px (contiguous preferred)
    order=sorted(range(1,len(fr)),key=lambda i:-spd[i]); sl=[i for i in order[:2] if spd[i]>=18] or [i for i in order[:1] if spd[i]>=5]
    sl=[i for i in sl if not sl or abs(i-max(sl,key=lambda k:spd[k]))<=2]
    layers=[np.zeros((H,W,4),np.uint8) for _ in fr]; trails={}
    for i in sorted(sl):
        pts=arc(sh[i],tips[i-1],tips[i],d); trails[i]=pts
        layers[i]=np.maximum(layers[i],stroke(H,W,pts,2.6,1.0))
    # scatter/fade for 2 frames after the last slash frame, on its own layer
    if sl:
        last=max(sl); pts=trails[last]
        for k,(fade,keep) in enumerate([(0.55,0.6),(0.25,0.3)],1):
            j=last+k
            if j>=len(fr): break
            seg=stroke(H,W,pts,1.6,fade); m=seg[...,3]>0
            # break into drifting dashes: random holes + small outward drift
            holes=nd.binary_dilation(rng.random((H,W))>keep,iterations=1); seg[m&holes]=0
            c=sh[last]; dx=int(round(np.sign(pts[0][0]-c[0])*k)); dy=int(round(np.sign(pts[0][1]-c[1])*k))
            seg=np.roll(np.roll(seg,dy,0),dx,1)
            layers[j]=np.maximum(layers[j],seg)
    fd=f'{A}/fx/hit{h}/{d}'; od=f'{A}/hit{h}/{d}'; os.makedirs(fd,exist_ok=True); os.makedirs(od,exist_ok=True)
    for i,(a,L) in enumerate(zip(fr,layers)):
        Image.fromarray(L).save(f'{fd}/fx_{i:03d}.png')
        base=Image.fromarray(a); fx=Image.fromarray(L); base.alpha_composite(fx); base.save(f'{od}/{i:03d}.png')
    meta[f'hit{h}/{d}']={'slash_frames':sorted(sl),'arc_px':[round(s,1) for s in spd],'tips':[None if t is None else [int(t[0]),int(t[1])] for t in tips]}
    print(d,h,'slash',sorted(sl),[round(s) for s in spd])
json.dump(meta,open(A+'/trailA_meta.json','w'),indent=1)
