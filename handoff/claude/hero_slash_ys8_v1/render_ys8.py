import sys,os,random,numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'newatk');sys.path.insert(0,'slash');import linette_fx as LF,render3dir as R,ys8
IDLE=Image.open(R.IDLE['side']).convert('RGBA');C0=116
# hit: strike frame, R, span, T, rot, y, hitstop, shake, travel px/tick, sparks
SL={'hit1':(9,40,130,13,0,112,3,1.2,3,6,0,.55),'hit2':(6,42,130,13,30,104,3,1.5,3,6,1,.8),'hit3':(10,56,160,18,0,118,6,3,2,12,0,1)}
LIFE=12
def draw(spr,s,OX,OY):
    a=s['age'];Rr,span,T,rot=s['R'],s['span'],s['T'],s['rot']
    head=min(1,(a+1)/3);tail=0 if a<4 else min(1,(a-4)/6)        # sweep in over 3 ticks, then tail chases head
    if tail>=head:return
    sc=1+.03*a;im=ys8.arc(Rr*sc,span,T*(1 if a<6 else max(.3,1-(a-6)/6)),head,tail,rot,rev=s['rev'],sq=s['sq'])
    x=s['x']+a*s['v'];spr.alpha_composite(im,(int(OX+x-im.width/2),int(OY+s['y']-im.height/2)))
    if a>=1:
        lay=Image.new('RGBA',spr.size);ys8.sparks(lay,OX+x+Rr,OY+s['y'],s['sp'],a,s['seed']);spr.alpha_composite(lay)
def timeline():
    out=[];act=[];shake=0;rnd=random.Random(3);fl=0
    for _ in range(14):out.append((IDLE,[],0,0,0))
    for c in ('hit1','hit2','hit3'):
        sf,Rr,span,T,rot,y,stop,sh,v,sp,rev,sq=SL[c]
        for f,t in R.PLAN[c]:
            strike=f==sf
            if strike:act.append(dict(rev=rev,sq=sq,x=C0+26,y=y,R=Rr,span=span,T=T,rot=rot,v=v,sp=sp,seed=len(out),age=0));shake=max(shake,sh);fl=3 if c=='hit3' else 0
            for k in range(t+(stop if strike else 0)):
                out.append((IDLE,[dict(a) for a in act],shake,rnd.random(),fl))
                if not(strike and k<stop):
                    for a in act:a['age']+=1
                act=[a for a in act if a['age']<LIFE];shake=shake*.8 if shake>.3 else 0;fl=max(0,fl-1)
    for _ in range(24):out.append((IDLE,[],0,0,0))
    return out
def render(s,lab):
    im,act,sh,r,fl=s;fr=Image.new('RGBA',(480,380),(66,96,58,255));OX,OY=40,30;spr=Image.new('RGBA',(400,300));spr.alpha_composite(im,(OX,OY))
    for a in act:draw(spr,a,OX,OY)
    d=round((r*2-1)*sh);fr.alpha_composite(spr.resize((600,450),Image.NEAREST),(-80+d*3//2,-40))
    if fl:fr.alpha_composite(Image.new('RGBA',fr.size,(220,240,255,int(255*fl*.05))))
    ImageDraw.Draw(fr).text((10,8),lab,font=LF.F,fill='white');return fr
if __name__=='__main__':
    import render_slash as RS
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);A=RS.timeline();B=timeline();n=0
    for slow in (1,1,3):
        for i in range(max(len(A),len(B))):
            sl=' · 1/3 슬로우' if slow>1 else ''
            fa=RS.render(A[min(i,len(A)-1)],'이전 검흔'+sl);fb=render(B[min(i,len(B)-1)],'이스8 스타일 검흔'+sl)
            fr=Image.new('RGB',(960,380));fr.paste(fa.convert('RGB'),(0,0));fr.paste(fb.convert('RGB'),(480,0))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
