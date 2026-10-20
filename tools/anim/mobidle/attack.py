# Attack motions for the 47 monsters: idle pose -> wind-up (squash + lean back) -> snap into the sheet's attack pose (lunge + stretch,
# small shake while held, effects included as drawn) -> settle back to idle. Field monsters (no attack pose) do a body slam with the idle
# pose. Attack pose is placed over the idle one by matching the feet line and the back edge of the body. 12 frames, ticks per frame in
# the manifest. usage: attack.py <sheet dir> <INDEX.md> <out dir>   (reuses idle.py's keying / picking)
import sys,os,json,numpy as np
from PIL import Image
from scipy import ndimage
sys.argv_saved=sys.argv;src,index,out=sys.argv[1:4]
import importlib.util
spec=importlib.util.spec_from_file_location('idle',os.path.join(os.path.dirname(os.path.abspath(__file__)),'idle_lib.py'));L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
os.makedirs(out+'/atk',exist_ok=True)
def crop(rgba,mask):
    ys,xs=np.nonzero(mask);a=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1].copy();a[...,3]=np.where(mask[ys.min():ys.max()+1,xs.min():xs.max()+1],255,0);return a,(xs.min(),ys.min())
def body_mask_right(mask,x0,x1,y0,y1):
    sub=mask[y0:y1,x0:x1].copy();w=x1-x0;c=sub.sum(0);lo,hi=int(w*.38),int(w*.62);cut=lo+int(np.argmin(c[lo:hi]));sub[:,:cut]=False
    lab,n=ndimage.label(sub,structure=np.ones((3,3)));keep=np.zeros_like(sub)
    if n==0:return None,None
    sz=ndimage.sum(sub,lab,range(1,n+1));big=int(np.argmax(sz))+1
    for i in range(n):
        if sz[i]>15:keep|=lab==i+1
    full=np.zeros_like(mask);full[y0:y1,x0:x1]=keep;bm=np.zeros_like(mask);bm[y0:y1,x0:x1]=lab==big;return full,bm
def scale(a,sx,sy):
    h,w=a.shape[:2];nh,nw=max(1,round(h*sy)),max(1,round(w*sx));ry=np.clip((np.arange(nh)*h/nh).astype(int),0,h-1);rx=np.clip((np.arange(nw)*w/nw).astype(int),0,w-1);return a[ry][:,rx]
def paste(c,a,x,y):   # x = left, y = bottom (feet)
    h,w=a.shape[:2];top=y-h
    for yy in range(h):
        Y=top+yy
        if not 0<=Y<c.shape[0]:continue
        row=a[yy];m=row[:,3]>0;xs=np.arange(w)+x;ok=m&(xs>=0)&(xs<c.shape[1]);c[Y,xs[ok]]=row[ok]
TICKS=[6,3,3,2,3,3,3,3,2,3,4,6]
def build(idle,atk,atk_dx,atk_dbot):
    ih,iw=idle.shape[:2]
    if atk is None: ah,aw=ih,iw
    else: ah,aw=atk.shape[:2]
    P=24;W=max(iw,atk_dx+aw)+2*P+30;H=max(ih,ah-atk_dbot,ih+12)+2*P;foot=H-P;fr=[]
    def F(img,sx=1,sy=1,dx=0,jit=0):
        c=np.zeros((H,W,4),np.uint8);a=scale(img,sx,sy);base=P+(0 if img is idle else atk_dx);paste(c,a,base+dx+round((img.shape[1]-a.shape[1])/2)+jit,foot+(0 if img is idle else atk_dbot));return c
    fr.append(F(idle))                                   # 0 rest
    fr.append(F(idle,1.04,.95,-3));fr.append(F(idle,1.07,.91,-6))   # 1-2 wind-up: squash and lean back
    if atk is None:                                       # body slam
        fr+= [F(idle,.92,1.08,10),F(idle,.9,1.1,18),F(idle,.95,1.04,20,1),F(idle,1,1,19,-1),F(idle,1.03,.97,16),F(idle,1.02,.98,10),F(idle,1,1,5),F(idle,1.01,.99,2),F(idle)]
    else:
        fr+= [F(atk,.95,1.06,6),F(atk,1,1,4),F(atk,1,1,4,1),F(atk,1,1,4,-1),F(atk,1,1,3),F(atk,1,1,1),F(idle,1.03,.97,2),F(idle,1.01,.99,1),F(idle)]
    return fr,W,H,foot
MON=[];sheet=None;import re
for line in open(index,encoding='utf-8'):
    m=re.match(r'## (mobs_\d+)\.jpg',line)
    if m:sheet=m.group(1);continue
    m=re.match(r'\| (\d) .*?\| `([^`]+)` \| ([^|]+)\|',line)
    if m and sheet:MON.append((sheet,int(m.group(1)),m.group(2),m.group(3).strip()))
MAN=[]
def save(mid,name,fr,W,H,foot,has):
    strip=Image.new('RGBA',(W*len(fr),H))
    for i,f in enumerate(fr):strip.paste(Image.fromarray(f),(i*W,0))
    strip.save(f'{out}/atk/{mid}.png');MAN.append({'id':mid,'name':name,'w':int(W),'h':int(H),'foot':int(foot),'n':len(fr),'ticks':TICKS,'hit':4,'pose':bool(has)})
for sheet,cell,mid,name in MON:
    im=Image.open(f'{src}/{sheet}.jpg');rgba,mask=L.key(im);Wd,Hd=im.size;c=(cell-1)%3;r=(cell-1)//3;x0,x1,y0,y1=int(c*Wd/3),int((c+1)*Wd/3),int(r*Hd/2),int((r+1)*Hd/2)
    got=L.pick(mask,x0,x1,y0,y1);keep,bb,_=got;m2=np.zeros_like(mask);m2[bb[1]:bb[3],bb[0]:bb[2]]=keep[bb[1]-y0:bb[3]-y0,bb[0]-x0:bb[2]-x0]
    idle,(ix,iy)=crop(rgba,m2);ibot=iy+idle.shape[0]
    am,bm=body_mask_right(mask,x0,x1,y0,y1)
    if am is None or not am.any(): fr,W,H,foot=build(idle,None,0,0);save(mid,name,fr,W,H,foot,False);continue
    atk,(ax,ay)=crop(rgba,am);bys,bxs=np.nonzero(bm)
    # align: body back edge (left of the main body) on the idle's left edge, body feet on the idle feet
    dx=(ax-bxs.min());dbot=(ay+atk.shape[0])-(bys.max()+1)
    fr,W,H,foot=build(idle,atk,dx,dbot);save(mid,name,fr,W,H,foot,True)
fp=f'{src}/mobs_field.jpg'
if os.path.exists(fp):
    im=Image.open(fp);rgba,mask=L.key(im);lab,n=ndimage.label(mask,structure=np.ones((3,3)));sz=ndimage.sum(mask,lab,range(1,n+1))
    big=sorted([i for i in range(n) if sz[i]>2000],key=lambda i:ndimage.center_of_mass(mask,lab,i+1)[1])[:5]
    for (mid,name),i in zip(L.FIELD,big):
        idle,_=crop(rgba,lab==i+1);fr,W,H,foot=build(idle,None,0,0);save(mid,name,fr,W,H,foot,False)
json.dump(MAN,open(out+'/atk_manifest.json','w'),ensure_ascii=False,indent=0);print(len(MAN),'attacks',sum(m['pose'] for m in MAN),'with pose')
