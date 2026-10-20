# comparison mp4: top = current game (hero8 atlas), bottom = new frames. columns → ← ↘ ↗ (left = mirror of right, ↙/↖ in game = mirror).
# usage: compare.py <hit n> <new_e dir> <new_se dir> <new_ne dir> <ticks csv> <out.mp4>
import json,sys,subprocess,os,shutil
from PIL import Image,ImageDraw,ImageFont,ImageOps
n,de,dse,dne,tk,out=sys.argv[1:7];TK=[int(t) for t in tk.split(',')]
A='test128/assets/';H=json.load(open(A+'anim/hero8.json'));FT=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',22)
SH={}
def cell(s,c):
    if s not in SH: SH[s]=Image.open(A+H['sheets'][s]).convert('RGBA')
    x,y,w,h,ax,ay=H['cells'][s][c];im=Image.new('RGBA',(256,256));im.paste(SH[s].crop((x,y,x+w,y+h)),(128-ax,189-ay));return im
old=[[(cell(e[0],e[1]),e[2]) for e in H['anims'][f'hit{n}_{d}']] for d in ('right','left')]  # the game has no diagonal attack yet: only → ← are compared
ld=lambda d:[Image.open(f'{d}/{i:03d}.png').convert('RGBA') for i in range(len(TK))]
E,SE,NE=ld(de),ld(dse),ld(dne)
new=[list(zip(E,TK)),list(zip([ImageOps.mirror(i) for i in E],TK)),list(zip(SE,TK)),list(zip(NE,TK))]
def at(seq,t,pause=20):
    L=sum(k for _,k in seq);t%=L+pause
    for im,k in seq:
        if t<k: return im
        t-=k
    return seq[0][0]
C=(36,52,220,212);W,Hh=C[2]-C[0],C[3]-C[1];S=2
fd=os.path.dirname(out)+'/cmpf';shutil.rmtree(fd,True);os.makedirs(fd)
lab=['→','← (반전)','↘ (↙=반전)','↗ (↖=반전)']
T=max(sum(k for _,k in s)+20 for s in old+new);f=0
for slow in (1,1,1,3,3):
    for t in range(T):
        for r in range(slow):
            im=Image.new('RGB',(W*S*4,Hh*S*2+40),(58,62,70));g=ImageDraw.Draw(im)
            for c in range(4):
                for row,src in enumerate((old,new)):
                    if c>=len(src): continue
                    fr=at(src[c],t).crop(C).resize((W*S,Hh*S),Image.NEAREST);im.paste(fr,(c*W*S,40+row*Hh*S),fr)
                g.text((c*W*S+10,8),lab[c],fill=(255,255,255),font=FT)
            g.text((8,40+4),'지금 게임',fill=(255,220,120),font=FT);g.text((8,40+Hh*S+4),f'새 {n}타',fill=(120,230,140),font=FT)
            if slow>1: g.text((W*S*4-140,8),'1/3 느리게',fill=(255,180,180),font=FT)
            im.save(f'{fd}/{f:05d}.png');f+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{fd}/%05d.png','-vf','fps=30,pad=ceil(iw/2)*2:ceil(ih/2)*2','-pix_fmt','yuv420p','-c:v','libx264','-crf','20',out],check=True);shutil.rmtree(fd);print('ok',out,f)
