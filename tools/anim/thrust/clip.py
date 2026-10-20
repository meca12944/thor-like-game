# thrust clip mp4: columns = given frame lists ("i:ticks,..."; recovery = played back in reverse after the hold). usage: clip.py <frames dir> <out.mp4> "<label>=<seq>" ...
import sys,os,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont,ImageOps
d,out=sys.argv[1:3];FT=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',22)
cols=[]
for a in sys.argv[3:]:
    lab,sq=a.split('=');mir=lab.endswith('<');s=[]
    for t in sq.split(','):
        i,k=t.split(':');im=Image.open(f'{d}/{int(i):03d}.png').convert('RGBA');s.append((ImageOps.mirror(im) if mir else im,int(k)))
    s.append((s[0][0],24));cols.append((lab.rstrip('<'),s))
C=(0,50,256,206);W,H=C[2]-C[0],C[3]-C[1];S=2
fd=os.path.dirname(out)+'/clipf';shutil.rmtree(fd,True);os.makedirs(fd);f=0
def at(s,t):
    t%=sum(k for _,k in s)
    for im,k in s:
        if t<k: return im
        t-=k
T=max(sum(k for _,k in s) for _,s in cols)
for slow in (1,1,1,4,4):
    for t in range(T):
        im=Image.new('RGB',(W*S*len(cols),H*S+40),(58,62,70));g=ImageDraw.Draw(im)
        for c,(lab,s) in enumerate(cols):
            fr=at(s,t).crop(C).resize((W*S,H*S),Image.NEAREST);im.paste(fr,(c*W*S,40),fr);g.text((c*W*S+10,8),lab,fill=(255,255,255),font=FT)
        if slow>1: g.text((W*S*len(cols)-140,8),'1/4 느리게',fill=(255,180,180),font=FT)
        for r in range(slow): im.save(f'{fd}/{f:05d}.png');f+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{fd}/%05d.png','-vf','fps=30,pad=ceil(iw/2)*2:ceil(ih/2)*2','-pix_fmt','yuv420p','-c:v','libx264','-crf','20',out],check=True);shutil.rmtree(fd);print('ok',out)
