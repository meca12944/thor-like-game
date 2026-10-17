# normalize full-body outfit designs: same body height, same baseline, transparent
import numpy as np, cv2, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove, new_session
OUT='/workspace/thor-like-game/docs_art/outfits_v3'; os.makedirs(OUT,exist_ok=True)
PICK=[('hero','r07','필멸자 (주인공)'),('a_tailor','v3_a_tailor','나비'),('h_mystic','r13','운'),('g_dancer','r12','방울'),
      ('f_diver','r10','숨비'),('e_tailor','r04','루비'),('c_priest','r11','설화'),('d_yuna','r06','유나 (현대복)')]
BODY=1200; CW,CH=900,1320; TOP=60; BASE=TOP+BODY
sess=new_session('isnet-anime')
def make_alpha(img,cid=''):
    rm=np.array(remove(Image.fromarray(img),session=sess,only_mask=True,post_process_mask=True)).astype(np.float32)/255
    if cid=='c_priest':
        return cv2.GaussianBlur(rm,(3,3),0)
    dist=255-img.min(2).astype(np.float32)
    cand=(dist<48).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(cand,8)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))
    bg=np.zeros(cand.shape,bool)
    for i in range(1,n):
        m=lab==i
        if i in border or rm[m].mean()<0.5: bg|=m
    near=cv2.dilate(bg.astype(np.uint8),np.ones((5,5),np.uint8))>0
    a=np.ones(cand.shape,np.float32); soft=np.clip((dist-12)/90.0,0,1)
    a[near]=soft[near]; a[bg]=np.clip((dist[bg]-25)/90,0,1)
    a=cv2.GaussianBlur(a,(3,3),0)
    # drop tiny specks
    n2,l2,s2,_=cv2.connectedComponentsWithStats((a>0.1).astype(np.uint8),8)
    for i in range(1,n2):
        if s2[i,4]<400: a[l2==i]=0
    return a
meta={}
for cid,src,name in PICK:
    img=np.array(Image.open(f'gen/{src}.jpg').convert('RGB'))
    a=make_alpha(img,cid)
    a3=np.clip(a,1e-3,1)[...,None]; dec=np.clip((img-255*(1-a3))/a3,0,255)
    edge=((a>0.02)&(a<0.98))[...,None]; img=np.where(edge,dec,img).astype(np.uint8)
    on=a>0.5; ys,xs=np.nonzero(on)
    feet=ys.max()
    # body centre: median x of opaque pixels in torso band (25-55% of figure)
    top_all=ys.min(); h=feet-top_all
    band=on[int(top_all+.25*h):int(top_all+.55*h)]; bx=np.nonzero(band)[1]; cx=int(np.median(bx))
    # head top: topmost opaque pixel within +-45px of body centre column
    col=on[:,max(0,cx-45):cx+45]; head=np.nonzero(col.any(1))[0].min()
    s=BODY/(feet-head)
    rgba=Image.fromarray(np.dstack([img,(a*255).astype(np.uint8)]),'RGBA')
    big=rgba.resize((round(rgba.width*s),round(rgba.height*s)),Image.LANCZOS)
    r,g,b,al=big.split(); rgb=Image.merge('RGB',(r,g,b)).filter(ImageFilter.UnsharpMask(1.4,50,2)); big=Image.merge('RGBA',(*rgb.split(),al))
    canvas=Image.new('RGBA',(CW,CH),(0,0,0,0))
    canvas.alpha_composite(big,(round(CW/2-cx*s),round(BASE-feet*s)) if False else (0,0)) if False else None
    ox=round(CW/2-cx*s); oy=round(BASE-feet*s)
    canvas.paste(big,(ox,oy),big)
    canvas.save(f'{OUT}/{cid}.png',optimize=True)
    meta[cid]=dict(name=name,src_scale=round(s,3),clipped=bool(ox>0 or ox+big.width<CW) and False)
    print(cid,'scale',round(s,2),'head',head,'feet',feet,'cx',cx)
# lineup
sc=0.5; tw=int(CW*sc*0.9); W=tw*len(PICK)+80; H=int(CH*sc)+150
L=Image.new('RGBA',(W,H),(32,34,40,255)); d=ImageDraw.Draw(L)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',26); small=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',18)
except Exception:
    import glob; f=[p for p in glob.glob('/usr/share/fonts/**/*CJK*',recursive=True)]+glob.glob('/usr/share/fonts/**/*Nanum*',recursive=True)
    font=ImageFont.truetype(f[0],26) if f else ImageFont.load_default(); small=ImageFont.truetype(f[0],18) if f else font
y0=60
for yy,lab in [(y0+TOP*sc,'head'),(y0+BASE*sc,'baseline')]:
    d.line([(20,yy),(W-20,yy)],fill=(90,95,110,255),width=2)
d.text((20,15),'outfits_v3 — hero + 7 heroines (same body height / baseline)',font=small,fill=(220,220,230,255))
for i,(cid,src,name) in enumerate(PICK):
    im=Image.open(f'{OUT}/{cid}.png'); im=im.resize((int(CW*sc),int(CH*sc)),Image.LANCZOS)
    x=40+i*tw+tw//2-im.width//2; L.alpha_composite(im,(x,y0))
    tx=40+i*tw+tw//2
    d.text((tx,y0+CH*sc+8),name,font=font,fill='white',anchor='ma'); d.text((tx,y0+CH*sc+44),cid,font=small,fill=(170,175,190,255),anchor='ma')
L.save(f'{OUT}/lineup.png',optimize=True)
json.dump(dict(size=[CW,CH],body_height=BODY,top=TOP,baseline=BASE,chars=meta),open(f'{OUT}/index.json','w'),ensure_ascii=False,indent=1)
