# hit3 v2 (owner 2026-10-20: 3타 검흔 반달 작게 + 칼 앞에, 칼과 겹치지 않게).
# ↘/↗: rebuilt from the clean diagonal key frames exactly as dg/showcase.py c3_attack does (cdiag3 -> oneblade/face fix -> polish),
#      then the side crescent (pressed to 3/4) is scaled S about the chest and placed GAP px past the blade tip -> blade untouched.
# →: in-game frames; crescent pulled out (all/trail.py, blade cut), holes filled, same scale + placement. ← ↙ ↖ = mirrors.
import sys,json,numpy as np
from PIL import Image
from scipy import ndimage
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
sys.path.insert(0,P+'dg');sys.path.insert(0,P+'fix');sys.path.insert(0,P+'all');sys.path.insert(0,'/home/user/thor-like-game/tools/anim')
import polish as PL,skin_match as SM;from trail import trail;from oneblade import fix as oneblade
S=float(sys.argv[2]) if len(sys.argv)>2 else 1.0;GAP=5;THIN=float(sys.argv[3]) if len(sys.argv)>3 else 0.4;CH=(128,129)
G='/home/user/thor-like-game/test128/assets/';A=json.load(open(G+'anim/hero8.json'))
def clean(im):
    a=np.array(im.convert('RGBA'));r,g,b,al=[a[...,i].astype(int) for i in range(4)];mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    m=(al>0)&(mx-mn<14)&(mn>70);core=ndimage.binary_erosion(m,iterations=2);lab,n=ndimage.label(core)
    for i in range(1,n+1):
        c=lab==i
        if c.sum()>40:a[ndimage.binary_dilation(c,iterations=3)&m]=0
    return Image.fromarray(a)
def light(a):
    r,g,b=[a[...,i].astype(int) for i in range(3)];mn=np.minimum(np.minimum(r,g),b);mx=np.maximum(np.maximum(r,g),b)
    return (a[...,3]>0)&(mn>110)&((mx-mn)<70)
def thin(cres,keep):
    """crescent thinner: per 3-degree ray from the chest keep only the outer (leading) part of its span"""
    a=np.array(cres);m=a[...,3]>0
    if not m.any():return cres
    ys,xs=np.nonzero(m);dx,dy=xs-CH[0],ys-CH[1];r=np.hypot(dx,dy);ang=np.round(np.degrees(np.arctan2(dy,dx))/3).astype(int)
    out=a.copy();out[m]=0
    for k in np.unique(ang):
        s_=ang==k;rr=r[s_];lo,hi=rr.min(),rr.max();sel=rr>=hi-(hi-lo)*keep
        out[ys[s_][sel],xs[s_][sel]]=a[ys[s_][sel],xs[s_][sel]]
    return Image.fromarray(out)
TINT=(160,222,255);TALPHA=0.62   # owner 2026-10-20: trail = slightly transparent light sky blue
def tint(cres):
    a=np.array(cres).astype(float);m=a[...,3]>0;lum=a[...,:3].mean(-1)/255.0
    for i in range(3):a[...,i]=np.where(m,TINT[i]*(0.75+0.25*lum),a[...,i])
    a[...,3]=np.where(m,a[...,3]*TALPHA,0);return Image.fromarray(a.clip(0,255).astype(np.uint8))
def place(base,cres,d,behind=False):
    cres=thin(cres,1-THIN) if THIN>0 else cres
    cres=tint(cres)
    """scale cres about the chest, move it along d until its inner edge is GAP px past the blade tip of base; 256 canvas in/out"""
    PADc=128;W=256+2*PADc
    B=Image.new('RGBA',(W,W));B.paste(base,(PADc,PADc));C=Image.new('RGBA',(W,W));C.paste(cres,(PADc,PADc))
    cx,cy=CH[0]+PADc,CH[1]+PADc;D=np.array(d,float);D/=np.linalg.norm(D);N=np.array([-D[1],D[0]])
    yy,xx=np.nonzero(light(np.array(B)));Pp=np.stack([xx-cx,yy-cy],1);band=(np.abs(Pp@N)<26)&(Pp@D>0)
    tipR=float((Pp[band]@D).max()) if band.any() else 0
    sm=C.resize((round(W*S),round(W*S)),Image.NEAREST);ox,oy=round(cx-cx*S),round(cy-cy*S)
    L0=Image.new('RGBA',(W,W));L0.paste(sm,(ox,oy));qy,qx=np.nonzero(np.array(L0)[...,3]>0)
    if len(qx)==0:return base,0,tipR
    Q=np.stack([qx-cx,qy-cy],1);near=np.abs(Q@N)<26;inner=float((Q[near]@D).min()) if near.any() else float((Q@D).min())
    k=max(0.0,tipR+GAP-inner);L=Image.new('RGBA',(W,W));L.paste(sm,(ox+round(D[0]*k),oy+round(D[1]*k)))
    if behind:L.alpha_composite(B);out=L
    else:out=B.copy();out.alpha_composite(L)
    return out,round(k),round(tipR)
def press(tr,sg):
    ax=128.0;return tr.transform((256,256),Image.AFFINE,(1/0.71,0,ax-ax/0.71,-sg*0.41/0.71,1,sg*0.41*ax/0.71),resample=Image.NEAREST)
def frames_diag(v):
    T=[e[2] for e in A['anims']['hit3_right']];fr=[clean(Image.open(P+f'cdiag3/hit3_{v}/{i:02d}.png').convert('RGBA')) for i in range(8)]
    if v=='se':
        ref=SM.ref_ramp(Image.open(P+'q34/rot_south-east.png'));fr=[SM.fix_face3(oneblade(im)[0],ref) for im in fr]
    pol=PL.polish(list(zip(fr,T)),f'hit3_{v}',v,set(range(8)));sg=1 if v=='se' else -1;out=[]
    for i,(im,t) in enumerate(pol):
        tr,cn=trail(Image.open(P+f'all/hit3_right/k{i}.png'),420,2)
        if cn:
            im,k,tp=place(im,press(tr,sg),(1,.3*sg),behind=(v=='ne'));print(v,i,'tip',tp,'push',k)
        else:
            c=Image.new('RGBA',(512,512));c.paste(im,(128,128));im=c
        out.append((im,t))
    return out
def frames_side():
    out=[]
    for i,e in enumerate(A['anims']['hit3_right']):
        x,y,w,h,ax,ay=A['cells'][e[0]][e[1]];sh=Image.open(G+A['sheets'][e[0]]).convert('RGBA');im=Image.new('RGBA',(256,256));im.paste(sh.crop((x,y,x+w,y+h)),(128-ax,189-ay))
        tr,cn=trail(im,150,2)
        if cn and i>=4:
            a=np.array(im);m=np.array(tr)[...,3]>0;a[m]=0;body=a[...,3]>0;holes=ndimage.binary_fill_holes(body)&~body
            if holes.any():
                idx=ndimage.distance_transform_edt(~body,return_distances=False,return_indices=True);a[holes]=a[idx[0][holes],idx[1][holes]]
            im,k,tp=place(Image.fromarray(a),tr,(1,0));print('side',i,'tip',tp,'push',k)
        else:
            c=Image.new('RGBA',(512,512));c.paste(im,(128,128));im=c
        out.append((im,e[2]))
    return out
if __name__=='__main__':
    src=sys.argv[1];d=json.load(open(src+'/hero_sbx.json'))
    if 'hero_sbx_h3s.webp' in d['sheets']:
        i=d['sheets'].index('hero_sbx_h3s.webp');d['sheets'].pop(i);d['cells'].pop(i)
    for k in [k for k in d['anims'] if k.startswith('hit3s_')]:del d['anims'][k]
    clips={'right':frames_side(),'down':frames_diag('se'),'up':frames_diag('ne')}
    MIR={'right':'left','down':'downl','up':'upl'};new=[];idx={}
    for dr,fr in clips.items():
        NL=[];ML=[]
        for im,t in fr:
            for flip,lst in ((False,NL),(True,ML)):
                j=im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im;bb=j.getbbox();new.append((j.crop(bb),256-bb[0],317-bb[1]));lst.append((len(new)-1,t))   # 512 canvas: feet root (256,317)
        idx[dr]=NL;idx[MIR[dr]]=ML
    W=2048;x=y=rowh=0;pos=[]
    for im,ax,ay in new:
        if x+im.width>W:x=0;y+=rowh+1;rowh=0
        pos.append((x,y));x+=im.width+1;rowh=max(rowh,im.height)
    sh=Image.new('RGBA',(W,y+rowh))
    for (im,_,_),p in zip(new,pos):sh.paste(im,p)
    name='hero_sbx_h3s.webp';d['sheets'].append(name);d['cells'].append([[px,py,im.width,im.height,int(ax),int(ay)] for (im,ax,ay),(px,py) in zip(new,pos)]);si=len(d['sheets'])-1
    sh.save(src+'/'+name,'WEBP',lossless=True)
    for dr,L in idx.items():d['anims'][f'hit3s_{dr}']=[[si,c,t] for c,t in L]
    json.dump(d,open(src+'/hero_sbx.json','w'),separators=(',',':'));print('ok',sh.size)
