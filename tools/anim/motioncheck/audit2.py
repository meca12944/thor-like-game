# Deep motion audit (hero8 atlas, motions in use since the attack became 검기-only): per clip
#  seam   = jump from the last frame back to the first vs the average frame-to-frame change (loops only; >1.8 = visible hitch)
#  jit    = head-top wobble that is not smooth (idle should breathe smoothly)
#  size   = figure height vs the same motion facing other ways
#  bright = mean colour vs the other directions
#  stride = how far the planted foot slides per cycle vs how far the game moves the hero in that cycle (foot sliding)
import sys,json,numpy as np
from PIL import Image
G=sys.argv[1]
s=open(f'{G}/index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);A=json.JSONDecoder().raw_decode(s[j:])[0]
IM={};C=A['cells']
def cell(f):
    if f[0] not in IM:IM[f[0]]=np.array(Image.open(f'{G}/assets/'+A['sheets'][f[0]]).convert('RGBA')).astype(int)
    x,y,w,h,ax,ay=C[f[0]][f[1]];return IM[f[0]][y:y+h,x:x+w],ax,ay
def canvas(f,W=200,H=170):
    a,ax,ay=cell(f);o=np.zeros((H,W,4),int);ox,oy=W//2-ax,H-10-ay;h,w=a.shape[:2]
    ys,xs=max(0,oy),max(0,ox);o[ys:oy+h,xs:ox+w]=a[ys-oy:H-oy if oy+h>H else h,xs-ox:W-ox if ox+w>W else w][:o[ys:oy+h,xs:ox+w].shape[0],:o[ys:oy+h,xs:ox+w].shape[1]];return o
def diff(a,b):m=(a[...,3]>0)|(b[...,3]>0);return (np.abs(a[...,:3]-b[...,:3]).sum(2)*m).sum()/max(1,m.sum())
DIRS=['down','up','right','left'];MOT=['idle','walk','run','dash','jump','rjump','hurt','death','hold','cast_s1']
rows=[];sizes={};bri={}
for mo in MOT:
    for d in DIRS:
        L=A['anims'].get(f'{mo}_{d}')
        if not L:continue
        fr=[canvas(f) for f in L];al=[f[...,3]>0 for f in fr]
        top=[np.nonzero(a.any(1))[0].min() for a in al];hgt=[160-t for t in top]
        sizes.setdefault(mo,{})[d]=np.median(hgt);bri.setdefault(mo,{})[d]=np.mean([f[...,:3][a].mean() for f,a in zip(fr,al)])
        note=[]
        if mo in('idle','walk','run') and len(fr)>2:
            dd=[diff(fr[k],fr[k+1]) for k in range(len(fr)-1)];seam=diff(fr[-1],fr[0])/max(1e-3,np.mean(dd))
            if seam>1.8:note.append(f'반복 이음새 튐 x{seam:.1f}')
            big=[k for k,v in enumerate(dd) if v>2.2*np.median(dd)]
            if big:note.append('갑자기 바뀌는 장: '+','.join(f'{k+1}→{k+2}' for k in big))
        if mo=='idle':
            t=np.array(top,float);sm=np.convolve(np.r_[t[-1],t,t[0]],[1/3]*3,'valid');j=np.abs(t-sm).max()
            if j>1.5:note.append(f'머리 떨림 {j:.1f}px')
        rows.append((mo,d,len(L),sum(f[2] for f in L),note))
for mo in sizes:
    v=sizes[mo];m=np.median(list(v.values()))
    for d,h in v.items():
        if abs(h-m)>6:[r[4].append(f'키가 다른 방향보다 {h-m:+.0f}px') for r in rows if r[0]==mo and r[1]==d]
    b=bri[mo];mb=np.median(list(b.values()))
    for d,x in b.items():
        if abs(x-mb)>8:[r[4].append(f'색 밝기 {x-mb:+.0f}') for r in rows if r[0]==mo and r[1]==d]
for mo,d,n,t,note in rows:print(f'{mo:8s} {d:5s} {n:2d}장 {t:3d}틱  '+(' · '.join(note) if note else '-'))
