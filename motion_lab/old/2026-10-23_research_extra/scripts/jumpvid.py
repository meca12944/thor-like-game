import json,sys,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
R='/home/user/thor-like-game/test128/'
s=open(R+'index.html').read();i=s.index('/*H8*/const H8=');j=s.index('{',i);e=s.index(';/*/H8*/');H=json.loads(s[j:e])
F=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',14);SH={}
def img(h8,c,fl):
    p=H['sheets'][h8]
    if p not in SH:SH[p]=Image.open(R+'assets/'+p).convert('RGBA')
    x,y,w,hh,ax,ay=c;t=SH[p].crop((x,y,x+w,y+hh))
    if fl:t=t.transpose(Image.FLIP_LEFT_RIGHT);ax=w-ax
    return t,ax,ay
def seg(L):
    s=[k for k,x in enumerate(L) if x['j']];a=max(0,s[0]-6);return L[a:s[-1]+12]
def video(out,pairs,slow=2,W=300,Hh=240,S=2,title=''):
    n=max(len(seg(L)) for _,L in pairs)
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W*len(pairs)*S}x{(Hh+24)*S}','-r',str(60//slow),'-i','-','-pix_fmt','yuv420p','-vcodec','libx264','-crf','18',out],stdin=subprocess.PIPE)
    for rep in range(3):
        for k in range(n+20):
            im=Image.new('RGB',(W*len(pairs),Hh+24),(40,44,40));d=ImageDraw.Draw(im);d.text((6,3),title,fill=(255,255,255),font=F)
            for c,(lab,L) in enumerate(pairs):
                Sg=seg(L);x=Sg[min(k,len(Sg)-1)];ox=c*W;d.rectangle([ox,24,ox+W-2,24+Hh],fill=(70,84,70));gy=24+Hh-30
                d.line([ox,gy,ox+W,gy],fill=(110,95,70));d.ellipse([ox+W//2-18,gy-4,ox+W//2+18,gy+4],fill=(55,66,55))
                if x['c']:
                    t,ax,ay=img(x['h8'],x['c'],x['fl']);im.paste(t,(ox+W//2-ax,int(gy-x['z']*1.5)-ay),t)
                d.text((ox+6,28),lab,fill=(255,240,120),font=F)
            p.stdin.write(im.resize((im.width*S,im.height*S),Image.NEAREST).tobytes())
    p.stdin.close();p.wait()
if __name__=='__main__':
    video('jump_v1.mp4',[('전',json.load(open('jlog_old.json'))),('후',json.load(open('jlog_new.json')))],title='주인공 제자리 점프 (2배 느리게)')
