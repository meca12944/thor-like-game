import os,sys,json,subprocess
P='/tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/'
os.environ['ATKDIR']='a5';exec(open(P+'dg/showcase.py').read().split('SCRIPT=')[0])
import skin as SK
from PIL import Image,ImageDraw
def lance(im,tip,age,life=10,big=False):  # thrust streak ahead of the blade tip (Linette fx.py idea), fades over `life` ticks
    if age<0 or age>=life: return im
    o=Image.new('RGBA',im.size);d=ImageDraw.Draw(o);a=1-age/life;g=min(1,(age+1)/2);x,y=tip;L=(70 if big else 54)*g;W=(10 if big else 7)
    for k,(w,col) in enumerate([(W,(90,210,255,int(120*a))),(W*.5,(210,250,255,int(220*a))),(max(1.5,W*.2),(255,255,255,int(255*a)))]):
        d.polygon([(x-20,y),(x+L*.35,y-w/2),(x+L,y),(x+L*.35,y+w/2)],fill=col)
    im=im.copy();im.alpha_composite(o);return im
def thrust_clip(h):
    T=[e[2] for e in A['anims'][h+'_right']];fr=[Image.open(P+f'jit/{h}_th/{i:02d}.png').convert('RGBA') for i in range(8)]
    fr=[SK.fix_face(im,f'{h}_th',i)[0] for i,im in enumerate(fr)]
    pol=PL.polish(list(zip(fr,T)),f'{h}_th','side',{2,3,4,5,6});out=[];age=0
    tp=trail3.tip(pol[3][0])
    for i,(im,t) in enumerate(pol):
        for k in range(t):
            if 3<=i<=5 and tp: out.append(lance(im,(tp[0],tp[1]),age,big=(h=='hit2')));age+=1
            else: out.append(im)
    return out
def old_clip(h): return [im for im,t in clip(h,'right') for _ in range(t)]
os.makedirs(P+'th/vid',exist_ok=True);[os.remove(P+'th/vid/'+f) for f in os.listdir(P+'th/vid')];k=0
for rep in range(3):
    for h in ['hit1','hit2']:
        A1,B1=old_clip(h),thrust_clip(h)
        for t in range(max(len(A1),len(B1))+10):
            for _ in range(3):
                cv=Image.new('RGB',(512,256),(86,124,70));d=ImageDraw.Draw(cv)
                for j,S in enumerate([A1,B1]): im=S[min(t,len(S)-1)];cv.paste(im,(j*256,0),im)
                d.text((6,6),f'{h} now',fill=(255,255,0));d.text((262,6),f'{h} thrust (new)',fill=(255,255,0))
                cv.resize((1024,512),Image.NEAREST).save(P+f'th/vid/{k:04d}.png');k+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',P+'th/vid/%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',P+'thrust_compare.mp4'],check=True)
W=Image.new('RGB',(256*8,512),(58,74,52))
for r,h in enumerate(['hit1','hit2']):
    S=thrust_clip(h);T=[e[2] for e in A['anims'][h+'_right']];c=0
    for i,t in enumerate(T): W.paste(S[c],(i*256,r*256),S[c]);c+=t
W.save(P+'t69.png');print(k)
