import sys,os,random
from PIL import Image,ImageDraw
sys.path.insert(0,'newatk');sys.path.insert(0,'slash');import linette_fx as LF,render3dir as R,fx2
IDLE=Image.open(R.IDLE['side']).convert('RGBA');C0=116
# strike frame, R, span, T, rot, y, stop, shake, v, rev, sq
SL={'hit1':(9,52,140,18,0,112,4,1.5,4,0,.5),'hit2':(6,54,140,18,35,100,4,2,4,1,.75),'hit3':(10,72,170,26,0,116,8,4,3,0,1)}
LIFE=13;ARC={'A':fx2.arcA,'B':fx2.arcB,'C':fx2.arcC}
def draw(spr,s,OX,OY,st):
    a=s['age'];head=min(1,(a+1)/2.5);tail=0 if a<4 else min(1,(a-4)/7)
    x=s['x']+a*s['v']
    if tail<head:
        T=s['T']*(1 if a<6 else max(.35,1-(a-6)/7));im=ARC[st](s['R']*(1+.025*a),s['span'],T,head,tail,s['rot'],s['rev'],s['sq'])
        if st=='C' and a>0:   # afterimage one step back
            g=ARC['A'](s['R']*(1+.025*(a-1)),s['span'],T*.8,min(1,a/2.5),tail,s['rot'],s['rev'],s['sq']);g.putalpha(g.getchannel('A').point(lambda v:v*.35))
            spr.alpha_composite(g,(int(OX+x-s['v']*2-g.width/2),int(OY+s['y']-g.height/2)))
        spr.alpha_composite(im,(int(OX+x-im.width/2),int(OY+s['y']-im.height/2)))
    lay=Image.new('RGBA',spr.size);hx,hy=OX+x+s['R']*.95,OY+s['y']
    if st=='A':fx2.lines(lay,OX+x+s['R']*.4,hy,a,7 if s['big'] else 4,s['seed'])
    fx2.star(lay,hx,hy,a,s['big']);
    if a>=1:fx2.sparks(lay,hx,hy,14 if s['big'] else 8,a,s['seed'])
    spr.alpha_composite(lay)
def timeline():
    out=[];act=[];shake=0;rnd=random.Random(3);fl=0
    for _ in range(14):out.append((IDLE,[],0,0,0))
    for c in ('hit1','hit2','hit3'):
        sf,Rr,span,T,rot,y,stop,sh,v,rev,sq=SL[c]
        for f,t in R.PLAN[c]:
            strike=f==sf
            if strike:act.append(dict(x=C0+22,y=y,R=Rr,span=span,T=T,rot=rot,v=v,rev=rev,sq=sq,big=c=='hit3',seed=len(out),age=0));shake=max(shake,sh);fl=4 if c=='hit3' else 2
            for k in range(t+(stop if strike else 0)):
                out.append((IDLE,[dict(a) for a in act],shake,rnd.random(),fl))
                if not(strike and k<stop):
                    for a in act:a['age']+=1
                act=[a for a in act if a['age']<LIFE];shake=shake*.8 if shake>.3 else 0;fl=max(0,fl-1)
    for _ in range(24):out.append((IDLE,[],0,0,0))
    return out
def render(s,lab,st):
    im,act,sh,r,fl=s;fr=Image.new('RGBA',(480,380),(66,96,58,255));OX,OY=40,30;spr=Image.new('RGBA',(400,300));spr.alpha_composite(im,(OX,OY))
    for a in act:draw(spr,a,OX,OY,st)
    d=round((r*2-1)*sh);fr.alpha_composite(spr.resize((600,450),Image.NEAREST),(-80+d*3//2,-40+round((r-.5)*sh)))
    if fl:fr.alpha_composite(Image.new('RGBA',fr.size,(220,240,255,int(255*fl*.05))))
    ImageDraw.Draw(fr).text((10,8),lab,font=LF.F,fill='white');return fr
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);B=timeline();n=0
    NM={'A':'A 청백 섬광','B':'B 픽셀 참격','C':'C 삼중 잔광'}
    for slow in (1,1,3):
        for i in range(len(B)):
            fr=Image.new('RGB',(1440,380))
            for j,st in enumerate('ABC'):fr.paste(render(B[i],NM[st]+(' · 1/3 슬로우' if slow>1 else ''),st).convert('RGB'),(j*480,0))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
