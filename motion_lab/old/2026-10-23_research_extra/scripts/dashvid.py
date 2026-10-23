import json,numpy as np,subprocess
from PIL import Image,ImageDraw,ImageFont
R='/home/user/thor-like-game/test128/'
s=open(R+'index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e]);L=json.load(open(R+'assets/anim/linette8.json'))
F=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',13);SH={}
def fr(A,k):
    o=[]
    for e in A['anims'][k]:
        p=A['sheets'][e[0]]
        if p not in SH:SH[p]=Image.open(R+'assets/'+p).convert('RGBA')
        x,y,w,h,ax,ay=A['cells'][e[0]][e[1]];c=Image.new('RGBA',(256,256));t=SH[p].crop((x,y,x+w,y+h));c.paste(t,(128-ax,189-ay),t);o.append(c)
    return o
def at(ticks,t):
    for i,x in enumerate(ticks):
        if t<x:return i
        t-=x
    return len(ticks)-1
def video(out,lanes,secs,W=620,Hh=190,S=2,title=''):
    """lanes: dict(frames,ticks,kind:'dash'|'hurt',dist,label,dur). 한 번 하고 쉬고 반복(1.2초마다)"""
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*S}x{(Hh*len(lanes)+22)*S}','-r','60','-i','-','-pix_fmt','yuv420p','-vcodec','libx264','-crf','18',out],stdin=subprocess.PIPE)
    for T in range(secs*60):
        im=Image.new('RGB',(W,Hh*len(lanes)+22),(40,44,40));d=ImageDraw.Draw(im);d.text((6,3),title,fill=(255,255,255),font=F)
        for r,Ln in enumerate(lanes):
            oy=22+r*Hh;d.rectangle([0,oy,W,oy+Hh-2],fill=(70,84,70))
            for gx in range(0,W,24):d.line([gx,oy+150,gx,oy+Hh-2],fill=(80,96,80))
            t=T%72;tot=sum(Ln['ticks']);i=at(Ln['ticks'],t) if t<tot else None
            x=150
            if Ln['kind']=='dash':
                u=min(1,t/Ln['dur']);x=150+Ln['dist']*(1-(1-u)**3)
            else:
                x=200-(12 if t>=0 else 0)
            img=Ln['frames'][i] if i is not None else Ln['idle']
            d.ellipse([x-16,oy+146,x+16,oy+154],fill=(55,66,55))
            if Ln['kind']=='dash' and i is not None and t<Ln['dur']:
                for g in range(1,5):   # 잔상
                    tg=t-g*2
                    if tg<0:break
                    ug=tg/Ln['dur'];xg=150+Ln['dist']*(1-(1-ug)**3);gi=Ln['frames'][at(Ln['ticks'],tg)].copy();a=np.array(gi);a[...,3]=(a[...,3]*0.35*(1-g/5)).astype(np.uint8);gi=Image.fromarray(a);im.paste(gi,(int(xg)-128,oy+150-189),gi)
            if Ln['kind']=='hurt' and t<4:img=Image.fromarray(np.where(np.array(img)[...,3:]>0,np.minimum(255,np.array(img).astype(int)+[90,40,40,0]),np.array(img)).astype(np.uint8))
            im.paste(img,(int(x)-128,oy+150-189),img);d.text((6,oy+4),Ln['label'],fill=(255,240,120),font=F)
        p.stdin.write(im.resize((W*S,im.height*S),Image.NEAREST).tobytes())
    p.stdin.close();p.wait()
