# Linette-style trail for the cleaned hero 3-hit (no effect in the sprite; the engine draws it): at the strike frame find the blade tip
# and blade direction (like linette_final_v1/thrust_fx.py), then draw the lance streak ahead of the tip (port of linette fx.py).
# usage: linette_trail.py <clean dir> <out.mp4>   (also writes <clean dir>/trail.json = engine data)
import json,sys,os,shutil,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
D,out=sys.argv[1:3];CL=json.load(open(D+'/clips.json'))
HIT={'hit1':5,'hit2':6,'hit3':9}                                  # strike tick (game H8.combo)
HINT={'right':(1,0),'left':(-1,0),'down':(1,.45),'downl':(-1,.45),'up':(1,-.45),'upl':(-1,-.45)}
def strike_frame(T,tick):
    c=0
    for i,t in enumerate(T):
        if c+t>tick: return i
        c+=t
    return len(T)-1
TR={}
for k,T in CL.items():
    h,d=k.split('_');f0=strike_frame(T,HIT[h]);fv=np.array(HINT[d],float);fv/=np.hypot(*fv);best=None
    for fi in range(f0,min(len(T),f0+4)):                         # strike frame .. +3: take the one whose blade reaches furthest along the facing
        a=np.array(Image.open(f'{D}/{k}/{fi:02d}.png'));r,g,b,al=[a[...,i].astype(int) for i in range(4)];mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
        light=(al>0)&(mn>120)&(mx-mn<60);ys,xs=np.nonzero(light if light.sum()>10 else al>0);proj=(xs-128)*fv[0]+(ys-130)*fv[1];i=proj.argmax()
        if best is None or proj[i]>best[0]+4: best=(proj[i],fi,np.array([xs[i],ys[i]],float),light)
    _,fi,tip,light=best
    ay,ax=np.nonzero(light);near=np.hypot(ax-tip[0],ay-tip[1])<34
    if near.sum()>4:
        P=np.stack([ax[near],ay[near]],1).astype(float);P-=P.mean(0);v=np.linalg.svd(P,full_matrices=False)[2][0];v=v if v@fv>0 else -v
        if v@fv<.9: v=fv                                          # blade far off the facing (mid-swing) or unreadable: trail along the facing
    else: v=fv
    tick=sum(T[:fi]) if fi>f0 else HIT[h]
    TR[k]={'frame':fi,'tick':tick,'tip':[round(float(tip[0])-128,1),round(float(tip[1])-189,1)],'dir':[round(float(v[0]),3),round(float(v[1]),3)],'big':h!='hit1','heavy':h=='hit3'}
json.dump(TR,open(D+'/trail.json','w'),indent=0)
def lance(g,cx,cy,dx,dy,nx,ny,back,ahead,w,col): g.polygon([(cx-dx*back,cy-dy*back),(cx+nx*w/2,cy+ny*w/2),(cx+dx*ahead,cy+dy*ahead),(cx-nx*w/2,cy-ny*w/2)],fill=col)
def trail(base,x,y,m,age):
    big,heavy=m['big'],m['heavy'];life=20 if heavy else 16 if big else 12
    if age<0 or age>=life: return
    grow=min(1,(age+1)/2);a=1-age/life;dx,dy=m['dir'];nx,ny=-dy,dx;tx,ty=x+m['tip'][0],y+m['tip'][1]
    ahead=(92 if heavy else 70 if big else 52)*grow;back=40 if heavy else 34 if big else 26;W=16 if heavy else 12 if big else 9
    cx,cy=tx+dx*ahead*.35,ty+dy*ahead*.35;lay=Image.new('RGBA',base.size);g=ImageDraw.Draw(lay)
    if heavy: lance(g,cx,cy,dx,dy,nx,ny,back+ahead*.45,ahead*.75,W*1.6,(60,150,255,int(80*a)))
    lance(g,cx,cy,dx,dy,nx,ny,back+ahead*.35,ahead*.65,W,(90,210,255,int(120*a)))
    lance(g,cx,cy,dx,dy,nx,ny,back*.8+ahead*.3,ahead*.6,W*.45,(210,250,255,int(220*a)))
    lance(g,cx,cy,dx,dy,nx,ny,back*.6+ahead*.25,ahead*.55,max(1.5,W*.18),(255,255,255,int(255*a)))
    for o,l in (((W*.9,.6),(-W*.9,.5),(W*1.6,.35),(-W*1.6,.3)) if big else ((W*.9,.55),(-W*.9,.45))):
        sx,sy=cx+nx*o-dx*back*.6,cy+ny*o-dy*back*.6;L=(back+ahead)*l;g.line((sx,sy,sx+dx*L,sy+dy*L),fill=(200,245,255,int(170*a)),width=1)
    if age<4:
        ex,ey=tx+dx*ahead*.95,ty+dy*ahead*.95;r=5 if big else 4;g.line((ex-r,ey,ex+r,ey),fill=(255,255,255,int(255*a)));g.line((ex,ey-r,ex,ey+r),fill=(255,255,255,int(255*a)))
    base.alpha_composite(lay)
# video: columns → ← ↘ ↙ ↗ ↖, 1->2->3 back to back, real speed x2 then 1/3 speed
COLS=[('right','→'),('left','←'),('down','↘'),('downl','↙'),('up','↗'),('upl','↖')];FT=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',20)
FR={k:[Image.open(f'{D}/{k}/{i:02d}.png').convert('RGBA') for i in range(len(T))] for k,T in CL.items()}
def seq(d):
    s=[]
    for h in ('hit1','hit2','hit3'):
        k=f'{h}_{d}';t0=0
        for i,t in enumerate(CL[k]):
            for j in range(t): s.append((k,i,t0));t0+=1
    s+= [(f'hit3_{d}',len(CL[f'hit3_{d}'])-1,99)]*24;return s
C=(0,30,360,226);W,H=C[2]-C[0],C[3]-C[1];S=2
fd=os.path.dirname(os.path.abspath(out))+'/lt_f';shutil.rmtree(fd,True);os.makedirs(fd);n=0;SQ={d:seq(d) for d,_ in COLS};T=len(SQ['right'])
for slow in (1,1,3):
    for t in range(T):
        im=Image.new('RGB',(W*S*3,(H*S+30)*2),(58,62,70));dr=ImageDraw.Draw(im)
        for c,(d,lab) in enumerate(COLS):
            k,i,tt=SQ[d][min(t,len(SQ[d])-1)];base=Image.new('RGBA',(360,256));base.alpha_composite(FR[k][i],(52,0))
            m=TR[k];trail(base,180,189,m,tt-m['tick'])
            fr=base.crop(C).resize((W*S,H*S),Image.NEAREST);x0,y0=(c%3)*W*S,(c//3)*(H*S+30)
            im.paste(fr,(x0,y0+30),fr);dr.text((x0+8,y0+4),lab+('  1/3 느리게' if slow>1 and c==0 else ''),fill=(255,255,255),font=FT)
        for r in range(slow): im.save(f'{fd}/{n:05d}.png');n+=1
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','60','-i',f'{fd}/%05d.png','-vf','fps=30,pad=ceil(iw/2)*2:ceil(ih/2)*2','-pix_fmt','yuv420p','-c:v','libx264','-crf','20',out],check=True);shutil.rmtree(fd)
print('ok',out,{k:(v['frame'],v['dir']) for k,v in TR.items() if k.endswith(('right','down','up'))})
