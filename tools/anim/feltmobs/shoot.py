# PixelLab "shoot" body motion per Felt mob (one per mob, shared by both 4-way projectile patterns) -> cleaned strips + manifest,
# and a preview: each mob plays pattern 2 then pattern 3 from patterns.json, projectiles drawn in code (projfx) and fired on the release frame.
# usage: shoot.py <anim dir> <felt dir> <out.mp4> <tmp dir>
import sys,os,glob,json,math,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
from projfx import *
from assemble_lib import clean
A,D,MP4,TMP=sys.argv[1:5];O=f'{D}/pl';os.makedirs(TMP,exist_ok=True)
MOBS=[('thread_wraith','c1_01_silmamul'),('thread_puppet','c1_02_thread_puppet'),('needle_spider','c1_03_needle_spider'),('stone_hound','c1_04_unrotting_hound')]
DROP={'thread_wraith':[2,3]}                  # frames where a glow got baked in (effects are drawn in code)
RELEASE={'thread_wraith':4,'thread_puppet':5,'needle_spider':4,'stone_hound':4}   # source frame index where projectiles leave
BACK={'thread_puppet':[3,1,0]}                # ends with arms out: settle back to idle
RECOLOR={'stone_hound'}                       # colours drift lighter over the clip: match each frame to frame 0
def match(fr,ref):
    a=np.array(fr).astype(float);r=np.array(ref).astype(float);m=a[...,3]>0;mr=r[...,3]>0
    for c in range(3):
        mu,sd=a[...,c][m].mean(),a[...,c][m].std()+1e-6;mu0,sd0=r[...,c][mr].mean(),r[...,c][mr].std()
        a[...,c]=np.where(m,(a[...,c]-mu)/sd*sd0+mu0,a[...,c])
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
PAT=json.load(open(f'{D}/patterns.json'))['patterns'];MAN=json.load(open(f'{O}/manifest.json'))
for src,mid in MOBS:
    fs=sorted(glob.glob(f'{A}/{src}_shoot_*.png'));idx=[i for i in range(len(fs)) if i not in DROP.get(src,[])]
    fr=[clean(Image.open(fs[i])) for i in idx]
    if src in RECOLOR:fr=[fr[0]]+[match(f,fr[0]) for f in fr[1:]]
    rel=idx.index(RELEASE[src]);fr+= [fr[i] for i in BACK.get(src,[])]
    ticks=[5]*rel+[10]+[5]*(len(fr)-rel-1)
    st=Image.new('RGBA',(256*len(fr),256))
    for i,f in enumerate(fr):st.paste(f,(i*256,0))
    st.save(f'{O}/{mid}_shoot.png');MAN[mid]['shoot']={'n':len(fr),'w':256,'h':256,'foot':250,'ticks':ticks,'release':rel,'origin_y':150}
json.dump(MAN,open(f'{O}/manifest.json','w'),ensure_ascii=False,indent=1)
# ---- preview: 2x2 arenas, mob in the centre, pattern 2 then pattern 3
font=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',20);fbig=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',22)
SC=0.6;Q=3;CW,CH=480,420;HEAD=44;VW,VH=CW*2,CH*2+HEAD;DIRS=[(1,0),(0,1),(-1,0),(0,-1)]
def cells(mid,k):
    st=Image.open(f'{O}/{mid}_{k}.png');n=MAN[mid][k]['n'];return [st.crop((i*256,0,(i+1)*256,256)).resize((round(256*SC),)*2,Image.NEAREST) for i in range(n)]
TL={}
for src,mid in MOBS:
    S=cells(mid,'shoot');W=cells(mid,'walk');m=MAN[mid]['shoot'];spr=[];ev=[]
    for p in [q for q in PAT[mid] if q['type']=='proj']:
        t0=len(spr);spr+= [(W[0],None)]*20;ev.append(('label',t0,p))
        for i,t in enumerate(m['ticks']):
            if i==m['release']:
                for w in p['waves']:ev.append(('fire',len(spr)+w,p))
            spr+= [(S[i],None)]*t
        spr+= [(W[0],None)]*(70+max(p['waves']))
    TL[mid]=(spr,ev)
N=max(len(v[0]) for v in TL.values())
for f in range(N):
    img=Image.new('RGBA',(VW,VH),(34,30,38,255));d=ImageDraw.Draw(img);d.text((12,10),'1장 펠트 몹 — 사방 투사체 공격 (몸 동작 PixelLab · 투사체 코드)',font=fbig,fill=(255,200,120))
    for k,(src,mid) in enumerate(MOBS):
        spr,ev=TL[mid];ff=f%len(spr);cx0,cy0=(k%2)*CW,(k//2)*CH+HEAD;d.rectangle((cx0+4,cy0+4,cx0+CW-4,cy0+CH-4),outline=(70,62,76))
        im,_=spr[ff];side=round(256*SC);ox,oy=cx0+CW//2-side//2,cy0+CH//2-round(150*SC)
        img.alpha_composite(im,(ox,oy));bx,by=cx0+CW//2,oy+round(150*SC)
        L=Image.new('RGBA',(CW//Q,CH//Q),(0,0,0,0));g=ImageDraw.Draw(L);lab=None
        for e,t,p in ev:
            if e=='label' and t<=ff:lab=p
            age=ff-t
            if e!='fire' or age<0:continue
            ex,ey=(bx-cx0)/Q,(by-cy0)/Q
            if age<8:flash(g,ex,ey,age,(255,255,255))
            v=p['speed']/60*SC/Q;R=min(CW,CH)/2/Q-8
            for dd in DIRS:
                dist=age*v
                if p.get('return'):
                    if age*v/R*1.2>math.pi:continue
                    dist=R*math.sin(age*v/R*1.2)
                elif dist>R:
                    if p.get('on_end') and dist-R<v*100:draw_zone(g,ex+dd[0]*R,ey+dd[1]*R,int((dist-R)/v))
                    continue
                draw_proj(g,p['proj'],ex+dd[0]*(dist+8),ey+dd[1]*(dist+8),dd,f,age)
        img.alpha_composite(L.resize((CW,CH),Image.NEAREST),(cx0,cy0))
        d.text((cx0+12,cy0+8),MAN[mid]['name'],font=fbig,fill=(235,225,210))
        if lab:d.text((cx0+12,cy0+CH-34),f'{PAT[mid].index(lab)+1}. {lab["name"]}',font=font,fill=(160,210,255))
    img.convert('RGB').save(f'{TMP}/{f:05d}.png')
subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','60','-i',f'{TMP}/%05d.png','-vf',f'loop=1:size={N}','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',MP4],check=True);print(N,'frames')
