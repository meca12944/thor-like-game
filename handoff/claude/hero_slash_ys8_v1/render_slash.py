# stationary body + flying white crescent (original hit3 art) 3-hit combo, side view
import sys,random,numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'newatk');import linette_fx as LF,render3dir as R
CW=Image.open('slash/cw_148.png').convert('RGBA')
def cx(im):
    a=np.array(im).astype(int);mn=a[...,:3].min(-1);mx=a[...,:3].max(-1)
    body=(a[...,3]>0)&~((mn>115)&(mx-mn<60));ys,xs=np.nonzero(body[120:200]);return xs.mean()
IDLE=Image.open(R.IDLE['side']).convert('RGBA');C0=cx(IDLE);import os;NOMOVE=os.environ.get('NOMOVE')=='1'
def still(im):
    d=round(C0-cx(im));o=Image.new('RGBA',im.size);o.alpha_composite(im,(max(d,0),0),(max(-d,0),0));return o
# per hit: strike frame, scale, rotation(deg ccw), spawn y (sprite px), speed px/tick, hit-stop, shake
SL={'hit1':(9,.75,0,112,7,3,1.2),'hit2':(6,.85,40,95,7,3,1.5),'hit3':(10,1.15,-35,125,8,6,3)}
def crescent(spr,s,OX,OY):
    a=s['age'];sc=s['sc']*(1+.02*a);k=CW.resize((max(1,round(CW.width*sc)),max(1,round(CW.height*sc))),Image.NEAREST).rotate(s['rot'],Image.NEAREST,expand=True)
    al=1 if a<6 else max(0,1-(a-6)/5);
    if al<1:k.putalpha(Image.eval(k.getchannel('A'),lambda v:int(v*al)))
    x=s['x']+a*s['v'];spr.alpha_composite(k,(int(OX+x-k.width/2),int(OY+s['y']-k.height/2)))
def timeline():
    out=[];act=[];shake=0;rnd=random.Random(3)
    for _ in range(14):out.append((IDLE,[],0,0))
    for c in ('hit1','hit2','hit3'):
        sf,sc,rot,y,v,stop,sh=SL[c]
        for f,t in R.PLAN[c]:
            im=IDLE if NOMOVE else still(R.frame('side',c,f));strike=f==sf
            if strike:tip,_=R.blade(im);act.append({'x':(C0+42+CW.width*sc*.55) if NOMOVE else max(tip[0],C0+30)+CW.width*sc*.35,'y':y,'sc':sc,'rot':rot,'v':v,'age':0});shake=max(shake,sh)
            for k in range(t+(stop if strike else 0)):
                out.append((im,[dict(a) for a in act],shake,rnd.random()))
                if not(strike and k<stop):
                    for a in act:a['age']+=1
                act=[a for a in act if a['age']<11];shake=shake*.8 if shake>.3 else 0
    for _ in range(24):out.append((IDLE,[],0,0))
    return out
def render(s,lab):
    im,act,sh,r=s;fr=Image.new('RGBA',(480,380),(66,96,58,255));OX,OY=40,30;spr=Image.new('RGBA',(400,300));spr.alpha_composite(im,(OX,OY))
    for a in act:crescent(spr,a,OX,OY)
    d=round((r*2-1)*sh);fr.alpha_composite(spr.resize((600,450),Image.NEAREST),(-80+d*3//2,-40));ImageDraw.Draw(fr).text((10,8),lab,font=LF.F,fill='white');return fr
if __name__=='__main__':
    import os;OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True)
    A=R.timeline('side');B=timeline();n=0
    for slow in (1,1,3):
        for i in range(max(len(A),len(B))):
            sl=' · 1/3 슬로우' if slow>1 else ''
            fa=LF.render(A[min(i,len(A)-1)],lab='현재 새 공격'+sl);fb=render(B[min(i,len(B)-1)],('모션 없이 검흔만' if NOMOVE else '제자리 + 검흔 날리기')+sl)
            fr=Image.new('RGB',(960,380));fr.paste(fa.convert('RGB'),(0,0));fr.paste(fb.convert('RGB'),(480,0))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
