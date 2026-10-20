# Clean PixelLab walk/attack frames (drop small detached bits away from the body), save strips + manifest, and render a preview:
# each mob walks right, attacks, walks back left (mirrored), attacks. usage: assemble.py <anim dir> <out dir> <out.mp4> <tmp dir>
import sys,os,glob,json,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
A,O,MP4,TMP=sys.argv[1:5];os.makedirs(O,exist_ok=True);os.makedirs(TMP,exist_ok=True)
MOBS=[('thread_wraith','c1_01_silmamul','실마물'),('thread_puppet','c1_02_thread_puppet','실 꼭두각시'),('needle_spider','c1_03_needle_spider','바늘 거미'),('stone_hound','c1_04_unrotting_hound','썩지 않는 들개')]
DROP={'needle_spider_attack':[6]}          # frame with a baked-in slash arc (effects are drawn in code)
from assemble_lib import clean
MAN={}
for src,mid,name in MOBS:
    for k in ('walk','attack'):
        fs=sorted(glob.glob(f'{A}/{src}_{k}_*.png'));fr=[clean(Image.open(f)) for i,f in enumerate(fs) if i not in DROP.get(f'{src}_{k}',[])]
        if k=='walk':fr=fr[:8];ticks=[7]*8
        else:fr=fr+[fr[3],fr[1]];ticks=[6,4,4,3,3,3]+[3]*(len(fr)-8)+[8,4]   # wind-up .. strike (held), quick settle back
        ticks=(ticks+[3]*len(fr))[:len(fr)]
        st=Image.new('RGBA',(256*len(fr),256))
        for i,f in enumerate(fr):st.paste(f,(i*256,0))
        st.save(f'{O}/{mid}_{k}.png');MAN.setdefault(mid,{'name':name})[k]={'n':len(fr),'w':256,'h':256,'foot':250,'ticks':ticks,**({'hit':len(fr)-3} if k=='attack' else {})}
json.dump(MAN,open(f'{O}/manifest.json','w'),ensure_ascii=False,indent=1)
# ---- preview
font=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',22);SC=0.7;CW,CH=480,300;HEAD=44;VW,VH=CW*2,CH*2+HEAD
def strip(mid,k):
    st=Image.open(f'{O}/{mid}_{k}.png');m=MAN[mid][k];return [st.crop((i*256,0,(i+1)*256,256)).resize((round(256*SC),)*2,Image.NEAREST) for i in range(m['n'])],m['ticks']
SEQ={}
for _,mid,_ in MOBS:
    W,wt=strip(mid,'walk');T,tt=strip(mid,'attack');seq=[];x=0;span=CW-round(256*SC)-20;speed=1.3
    for flip in (False,True):
        f=0
        while True:
            i=(f//wt[0])%len(W);seq.append((W[i],flip,x,None));x+=-speed if flip else speed;f+=1
            if (not flip and x>=span) or (flip and x<=0):break
        for i,t in enumerate(tt):
            for q in range(t):seq.append((T[i],flip,x,i==MAN[mid]['attack']['hit'] and q==0))
        for q in range(20):seq.append((W[0],flip,x,None))
    SEQ[mid]=seq
N=max(len(s) for s in SEQ.values());HIT={mid:[] for mid in SEQ}
for f in range(N):
    img=Image.new('RGBA',(VW,VH),(34,30,38,255));d=ImageDraw.Draw(img);d.text((12,10),'1장 펠트 몹 — 이동 · 공격 (PixelLab)',font=font,fill=(255,200,120))
    for k,(_,mid,name) in enumerate(MOBS):
        cx,cy=(k%2)*CW,(k//2)*CH+HEAD;d.rectangle((cx+4,cy+4,cx+CW-4,cy+CH-4),outline=(70,62,76));d.line((cx+10,cy+CH-22,cx+CW-10,cy+CH-22),fill=(60,54,64))
        im,flip,x,hit=SEQ[mid][f%len(SEQ[mid])]
        if flip:im=im.transpose(Image.FLIP_LEFT_RIGHT)
        px=cx+10+round(x);py=cy+CH-22-round(250*SC);img.alpha_composite(im,(px,py))
        if hit:HIT[mid].append((f,px+(30 if flip else round(256*SC)-30),py+round(150*SC),flip))
        for (t0,hx,hy,fl) in HIT[mid]:
            age=f-t0
            if 0<=age<10:   # code-drawn hit arc
                al=max(0,255-age*26);r=18+age*2;g=Image.new('RGBA',(VW,VH));gd=ImageDraw.Draw(g)
                gd.arc((hx-r,hy-r,hx+r,hy+r),(110 if fl else -70),(250 if fl else 70),fill=(255,248,225,al),width=4);img.alpha_composite(g)
        d.text((cx+12,cy+8),name,font=font,fill=(235,225,210))
    img.convert('RGB').save(f'{TMP}/{f:05d}.png')
subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','60','-i',f'{TMP}/%05d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',MP4],check=True);print(N,'frames')
