# 그록 일러스트(81f8303f) 01·02·06 → 머리만 키워(원본에서) → 게임 크기·우리 색 → 아틀라스 새 칸 + 맞기 ↓→ 3장·대시 ↗ 가운데 장 (팀장 10-26 허락, 크레딧 0)
import sys,json;sys.path.insert(0,sys.argv[2])
from h8lib import load,save
from PIL import Image
import numpy as np
R=sys.argv[1];s,j,k,H=load(R);base=H['sheets'].index('anim/hero_grok_0.webp')
SP=f'{R}/test128/assets/anim/hero_grok_0.webp';S=Image.open(SP).convert('RGBA');C=H['cells'][base]
G=sys.argv[2]+'/g81/'
# 색: 지금 주인공 걷기 64색 + 밝기 순위 맞춤
px=[]
def cellim(c): x,y,w,h,ax,ay=C[c];return S.crop((x,y,x+w,y+h))
for n in ['walk_down','walk_right','walk_dr','walk_up']:
    for f in H['anims'][n]: a=np.array(cellim(f[1]));px.append(a[a[...,3]>40][:,:3])
P=np.concatenate(px).astype(float);q=Image.fromarray(P.reshape(-1,1,3).astype('uint8')).quantize(colors=64,method=Image.Quantize.MEDIANCUT)
pal=np.array(q.getpalette()[:192]).reshape(-1,3).astype(float);lumP=np.sort(P@[.3,.59,.11])
def remap(gi):
    a=np.array(gi).astype(float);m=a[...,3]>110;c=a[m][:,:3];l=c@[.3,.59,.11];r=np.argsort(np.argsort(l))/max(1,len(l)-1);tl=np.interp(r,np.linspace(0,1,len(lumP)),lumP);c=np.clip(c*((tl+1)/(l+1))[:,None],0,255)
    d=((c[:,None,:]-pal[None,:,:])**2).sum(-1);a[m,:3]=pal[d.argmin(1)];a[...,3]=np.where(m,255,0);return Image.fromarray(a.astype('uint8'))
ref=Image.open(G+'03_atk1.png').getbbox();SC=144/(ref[3]-ref[1])
def make(name,head,wx=1.0,neck=.19):
    im=Image.open(G+name+'.png').convert('RGBA');im=im.crop(im.getbbox());W,Hh=im.size;a=np.array(im)[...,3]
    ny=int(Hh*neck);xs=np.where(a[ny]>110)[0];cx=int(xs.mean())
    hd=im.crop((0,0,W,ny));hw,hh=int(W*head),int(ny*head);hd=hd.resize((hw,hh),Image.LANCZOS)
    pad=hh-ny;out=Image.new('RGBA',(max(W,hw)+2*abs(hw-W),Hh+pad));ox=(out.width-W)//2;out.paste(im,(ox,pad),im)
    out.alpha_composite(hd,(ox+cx-int(cx*head),0))
    out=out.crop(out.getbbox());out=out.resize((round(out.width*SC*wx),round(out.height*SC)),Image.LANCZOS);return remap(out)   # wx = 가로만 넓힘(7등신 → 5.5등신 몸 폭)
_sl={'x':0,'y':None,'rh':0}
def slot(w,h):
    global S
    if _sl['y'] is None: _sl['y']=S.height+2
    if _sl['x']+w>S.width: _sl['x']=0;_sl['y']+=_sl['rh']+2;_sl['rh']=0
    need=_sl['y']+h+2
    if need>S.height: T=Image.new('RGBA',(S.width,need));T.paste(S,(0,0));S=T
    x,y=_sl['x'],_sl['y'];_sl['x']+=w+2;_sl['rh']=max(_sl['rh'],h);return x,y
def addcell(im):
    b=im.getbbox();im=im.crop(b);a=np.array(im)[...,3];w,h=im.size
    fy=[y for y in range(h-int(h*.08),h)];fx=np.where(a[fy].max(0)>110)[0];ax=int((fx.min()+fx.max())/2)   # 발 가운데
    x,y=slot(w,h);S.paste(im,(x,y));C.append([x,y,w,h,ax,h]);return len(C)-1
PAR={'01_hit_down':(1.25,1.12),'02_hit_right':(1.18,1.0),'06_dash_ur':(1.35,1.15)}   # (머리 배율, 가로 배율): 이웃 장과 머리 폭·어깨 폭 ±5%
c01=addcell(make('01_hit_down',*PAR['01_hit_down']));c02=addcell(make('02_hit_right',*PAR['02_hit_right']));c06=addcell(make('06_dash_ur',*PAR['06_dash_ur']))
log={}
for n,c in [('hurt_down',c01),('hurt_right',c02)]:
    L=H['anims'][n];cur=L[0][1];H['anims'][n]=[[base,cur,2],[base,c,8],[base,cur,10]];log[n]=H['anims'][n]
L=H['anims']['dash_up'];L[2][1]=c06;log['dash_up']=L
H['_grok81_note']='10-26 그록 일러스트 01·02·06(81f8303f): 머리·가로 배율 %s(원본에서)·0.143배·우리 64색, 맞기 ↓→ [지금 2 · 그록 8 · 지금 10], 대시 ↗ 가운데 장'%PAR
S.save(SP,lossless=True);save(R,s,j,k,H);print(json.dumps(log))
