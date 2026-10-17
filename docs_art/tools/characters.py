# full-body character profile normalizer (same canvas/body/baseline as outfits_v3)
# usage: characters.py <batch_name> "<title>" id=src:name:title:hf[:special] ...
#  special: comma list of fit | clampw | hat=<px in source> (headwear height to exclude)
#  hf = height factor vs adult BODY (1.0 adult, ~0.62 child, monsters can be >1 / fit)
import numpy as np, cv2, os, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove, new_session
OUT='/workspace/thor-like-game/docs_art/characters'; os.makedirs(OUT,exist_ok=True)
BODY=1200; CW,CH=900,1320; TOP=60; BASE=TOP+BODY
batch=sys.argv[1]; btitle=sys.argv[2]
specs=[]
for a in sys.argv[3:]:
    cid,rest=a.split('=',1); p=rest.split(':'); specs.append((cid,p[0],p[1],p[2],float(p[3]),p[4] if len(p)>4 else ''))
sess=new_session('isnet-anime')
def make_alpha(img):
    rm=np.array(remove(Image.fromarray(img),session=sess,only_mask=True,post_process_mask=True)).astype(np.float32)/255
    c=np.concatenate([img[:15,:15].reshape(-1,3),img[:15,-15:].reshape(-1,3),img[-15:,:15].reshape(-1,3),img[-15:,-15:].reshape(-1,3)])
    bgc=np.median(c,0).astype(np.float32)
    dist=np.abs(img.astype(np.float32)-bgc).max(2)
    cand=(dist<40).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(cand,8)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))
    bg=np.zeros(cand.shape,bool)
    for i in range(1,n):
        m=lab==i
        if i in border or (st[i,4]>30 and rm[m].mean()<0.5): bg|=m
    near=cv2.dilate(bg.astype(np.uint8),np.ones((5,5),np.uint8))>0
    a=np.ones(cand.shape,np.float32); soft=np.clip((dist-10)/80.0,0,1)
    a[near]=soft[near]; a[bg]=np.clip((dist[bg]-22)/80,0,1)
    a=cv2.GaussianBlur(a,(3,3),0)
    n2,l2,s2,_=cv2.connectedComponentsWithStats((a>0.1).astype(np.uint8),8)
    for i in range(1,n2):
        if s2[i,4]<300: a[l2==i]=0
    return a,bgc
idx_p=f'{OUT}/index.json'
idx=json.load(open(idx_p)) if os.path.exists(idx_p) else dict(size=[CW,CH],body_height=BODY,top=TOP,baseline=BASE,chars={},batches={})
for cid,src,name,title,hf,sp in specs:
    if os.environ.get('LINEUP'): break
    img=np.array(Image.open(f'/workspace/art_work/gen/{src}.jpg').convert('RGB'))
    a,bgc=make_alpha(img)
    a3=np.clip(a,1e-3,1)[...,None]; dec=np.clip((img-bgc*(1-a3))/a3,0,255)
    edge=((a>0.02)&(a<0.98))[...,None]; img=np.where(edge,dec,img).astype(np.uint8)
    on=a>0.5; ys,xs=np.nonzero(on); feet=ys.max(); top_all=ys.min(); h=feet-top_all
    band=on[int(top_all+.25*h):int(top_all+.55*h)]; cx=int(np.median(np.nonzero(band)[1]))
    col=on[:,max(0,cx-45):cx+45]; head=np.nonzero(col.any(1))[0].min()
    if 'fit' in sp:   # monsters: fit whole silhouette into canvas
        x0,x1=xs.min(),xs.max(); s=min((BODY*hf)/(feet-top_all),(CW-40)/(x1-x0)); cx=(x0+x1)//2
    else:
        hat=next((float(t[4:]) for t in sp.split(',') if t.startswith('hat=')),0.0)
        s=BODY*hf/(feet-head-hat)       # headwear excluded from head-to-feet measure
        s=min(s,(BASE-4)/(feet-head))   # never clip headwear at canvas top
        x0,x1=xs.min(),xs.max(); s=min(s,(CW-20)/max(1,2*max(cx-x0,x1-cx))) if 'clampw' in sp else s
    rgba=Image.fromarray(np.dstack([img,(a*255).astype(np.uint8)]),'RGBA')
    big=rgba.resize((round(rgba.width*s),round(rgba.height*s)),Image.LANCZOS)
    r,g,b,al=big.split(); rgb=Image.merge('RGB',(r,g,b)).filter(ImageFilter.UnsharpMask(1.4,50,2)); big=Image.merge('RGBA',(*rgb.split(),al))
    canvas=Image.new('RGBA',(CW,CH),(0,0,0,0)); canvas.paste(big,(round(CW/2-cx*s),round(BASE-feet*s)),big)
    canvas.save(f'{OUT}/{cid}.png',optimize=True)
    idx['chars'][cid]=dict(name=name,title=title,label=(f'「{title}」 {name}' if title else name),file=f'{cid}.png',batch=batch,height_factor=hf)
    print(cid,'scale',round(s,2),'cut' if (round(CW/2-cx*s)>0 or True) else '')
ids=[s[0] for s in specs]; idx['batches'][batch]=dict(title=btitle,ids=ids,lineup=f'batch_{batch}.png')
json.dump(idx,open(idx_p,'w'),ensure_ascii=False,indent=1)
# lineup
sc=0.5; tw=int(CW*sc*0.9); W=tw*len(ids)+80; H=int(CH*sc)+165
L=Image.new('RGBA',(W,H),(32,34,40,255)); d=ImageDraw.Draw(L)
font=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',26); small=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',18); tiny=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',15)
y0=60
for yy in [y0+TOP*sc,y0+BASE*sc]: d.line([(20,yy),(W-20,yy)],fill=(90,95,110,255),width=2)
d.text((20,15),f'characters / batch {batch} — {btitle} · 같은 캔버스·몸 높이·기준선 (outfits_v3 규격)',font=small,fill=(220,220,230,255))
for i,cid in enumerate(ids):
    m=idx['chars'][cid]; im=Image.open(f'{OUT}/{cid}.png').resize((int(CW*sc),int(CH*sc)),Image.LANCZOS)
    L.alpha_composite(im,(40+i*tw+tw//2-im.width//2,y0)); tx=40+i*tw+tw//2
    if m['title']: d.text((tx,y0+CH*sc+6),f'「{m["title"]}」',font=small,fill=(200,180,130,255),anchor='ma')
    d.text((tx,y0+CH*sc+32),m['name'],font=font,fill='white',anchor='ma'); d.text((tx,y0+CH*sc+70),cid,font=tiny,fill=(150,155,170,255),anchor='ma')
L.save(f'{OUT}/batch_{batch}.png',optimize=True); print('lineup',f'{OUT}/batch_{batch}.png')
