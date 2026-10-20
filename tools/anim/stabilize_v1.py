# hero sprite stabilisation (owner 2026-10-20: "주인공이 흔들린다 진동 받는 것처럼" after the 2x zoom).
# The body (gold trim centroid in the torso band) wandered 1-6 px between frames - e.g. idle -3,-2,-3,-2 = a 1 px flicker that
# reads as vibration once each pixel is 2 screen px. Per clip: idle -> torso x locked to the clip median; walk/run -> torso x
# follows a circular 5-frame average. Only the anchor ax moves (new cell entries, pixels untouched; feet stay on the ground).
# walk_down frame 5 (drawn ~6 px taller) is replaced by its neighbour.
import json,numpy as np
from PIL import Image
T='/home/user/thor-like-game/test128/'
d=json.load(open(T+'assets/anim/hero8.json'));sh={}
def arr(s):
    if s not in sh:sh[s]=np.array(Image.open(T+'assets/'+d['sheets'][s]).convert('RGBA'))
    return sh[s]
def gx(e):
    x,y,w,h,ax,ay=d['cells'][e[0]][e[1]];a=arr(e[0])[y:y+h,x:x+w];al=a[...,3]>0;r,g,b=[a[...,i].astype(int) for i in range(3)]
    gold=al&(r>150)&(g>90)&(b<90)&(r>g);band=np.zeros(al.shape,bool);band[max(0,ay-100):max(0,ay-40)]=True
    ys,xs=np.nonzero(gold&band)
    if len(xs)<5:return None
    m=np.median(xs);xs=xs[np.abs(xs-m)<25];return float(xs.mean())-ax
if 'walk_down' in d['anims'] and len(d['anims']['walk_down'])==12:
    L=d['anims']['walk_down'];L[5]=[L[4][0],L[4][1],L[5][2]]
log={}
for n in ['idle','walk','run']:
    for dr in ['right','left','down','up']:
        k=f'{n}_{dr}'
        if k not in d['anims']:continue
        L=d['anims'][k];X=[gx(e) for e in L]
        if any(v is None for v in X):continue
        N=len(X)
        tgt=[float(np.median(X))]*N if n=='idle' else [float(np.mean([X[(i+j)%N] for j in range(-2,3)])) for i in range(N)]
        sh_=[int(round(X[i]-tgt[i])) for i in range(N)];log[k]=sh_
        for i,e in enumerate(L):
            if sh_[i]==0:continue
            c=list(d['cells'][e[0]][e[1]]);c[4]=c[4]+sh_[i];d['cells'][e[0]].append(c);L[i]=[e[0],len(d['cells'][e[0]])-1]+e[2:]
d['src']['stabilize_v1']='idle/walk/run torso-x stabilised by anchor shift (tools/anim/stabilize_v1.py)'
js=json.dumps(d,separators=(',',':'),ensure_ascii=False);open(T+'assets/anim/hero8.json','w').write(js)
s=open(T+'index.html',encoding='utf-8').read();a=s.index("/*H8*/const H8=");b=s.index(";/*/H8*/");pre=s[a:b];k=pre.index('?null:')+6;s=s[:a]+pre[:k]+js+s[b:]
open(T+'index.html','w',encoding='utf-8').write(s)
for k,v in log.items():print(k,v)
