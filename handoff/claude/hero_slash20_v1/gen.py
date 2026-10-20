# 20 basic-weapon sword-arc variants (procedural, pixel style) on the standing hero, 3 hits each, 5x4 grid video
import sys,os,math,random,numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'slash');import fx2
F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
IDLE=Image.open('/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/east/000.png').convert('RGBA')
BAY=fx2.BAY
def arc(R,span,T,head,tail,rot,rev,sq,st):
    S=int(2*R+2*T+30);o=np.zeros((S,S,4));vis,k,w,d,Y,X=fx2.field(R,span,T*st.get('tk',1),head,tail,rot,rev,sq,S);ad=np.abs(d)
    if st.get('jag'):d=d+np.sin(np.arctan2(Y-S/2,X-S/2)*40)*w*.25;ad=np.abs(d)
    core,mid,glow=st['c'];dith=(k>BAY[Y%4,X%4]*.9) if st.get('dith') else np.ones_like(vis)
    if st.get('glow',1):g=vis&(ad<w/2+st.get('gw',5))&dith;o[g,:3]=glow;o[g,3]=np.maximum(o[g,3],(st.get('ga',90)*k+20)[g])
    if st.get('out'):m=vis&(ad<w/2+1.5)&dith;o[m,:3]=st['out'];o[m,3]=255
    b=vis&(ad<w/2)&dith
    if st.get('grad',1):col=np.array(mid)[None,None,:]*(1-k[...,None])+np.array(core)[None,None,:]*k[...,None];o[b,:3]=col[b]
    else:o[b,:3]=mid
    o[b,3]=st.get('ba',230)
    if st.get('hollow'):h=vis&(ad<w/2-2);o[h,3]=0
    c=vis&(ad<w/5)&(k>.25)&dith;o[c,:3]=core;o[c,3]=255
    if st.get('edge',1):e=vis&(d>w/2-1.5)&(d<w/2)&(k>.4);o[e,:3]=core;o[e,3]=255
    return Image.fromarray(o.clip(0,255).astype(np.uint8))
W=(255,255,255);V=[
 ('청백 섬광(현재)',dict(c=(W,(90,190,255),(40,110,255)))),
 ('순백 초승달',dict(c=(W,(225,235,245),(170,190,220)),ga=60)),
 ('은빛 강철',dict(c=(W,(170,180,195),(90,100,120)),out=(40,45,60))),
 ('황금 참격',dict(c=((255,250,210),(255,200,70),(220,120,20)))),
 ('진홍 혈풍',dict(c=((255,220,220),(230,50,60),(140,10,30)))),
 ('자색 그림자',dict(c=((240,210,255),(150,80,230),(70,20,140)))),
 ('비취 바람',dict(c=((230,255,240),(80,220,150),(20,130,90)))),
 ('얇은 실선',dict(c=(W,(180,230,255),(80,160,255)),tk=.45,gw=3)),
 ('굵은 초승달',dict(c=(W,(120,200,255),(40,110,255)),tk=1.7)),
 ('픽셀 셀 참격',dict(c=(W,(140,220,255),(60,120,230)),out=(20,30,80),dith=1,glow=0)),
 ('도트 부서짐',dict(c=(W,(150,210,255),(60,120,255)),dith=1)),
 ('외곽선만',dict(c=(W,(150,220,255),(60,140,255)),hollow=1,tk=1.4)),
 ('톱날 검기',dict(c=(W,(200,230,255),(90,150,255)),jag=1)),
 ('이중 궤적',dict(c=(W,(110,200,255),(40,110,255)),echo=2)),
 ('삼중 부채',dict(c=(W,(110,200,255),(40,110,255)),echo=3)),
 ('잔상 연속',dict(c=(W,(130,210,255),(50,120,255)),ghost=1)),
 ('X자 교차',dict(c=(W,(130,210,255),(50,120,255)),cross=1)),
 ('충격파 링',dict(c=(W,(130,210,255),(50,120,255)),ring=1)),
 ('먹선 붓터치',dict(c=((60,60,70),(25,25,35),(120,120,140)),out=None,ga=50,edge=0)),
 ('불꽃 베기',dict(c=((255,255,200),(255,150,40),(220,40,10)),jag=1,sparkc=(255,200,80))),
]
SL=[(52,140,18,0,112,0,.5),(54,140,18,35,100,1,.75),(72,170,26,0,116,0,1)]   # R span T rot y rev squash
LIFE=13
def draw(spr,s,st,OX,OY):
    a=s['age'];R,span,T,rot,y,rev,sq=SL[s['n']];x=116+22+a*4
    for e in range(st.get('echo',1)):
        h=min(1,(a+1)/2.5)-e*.12;tl=(0 if a<4 else min(1,(a-4)/7))+e*.1
        if h<=tl or h<=0:continue
        rr=R*(1+.025*a)*(1+.16*e*(-1)**e);im=arc(rr,span*(1-.08*e),T*(1 if a<6 else max(.35,1-(a-6)/7))*(1-.3*e),h,tl,rot+e*6,rev,sq,st)
        spr.alpha_composite(im,(int(OX+x-im.width/2),int(OY+y-im.height/2)))
        if st.get('cross') and a>=1:
            im2=arc(rr,span,T*.8,min(1,a/2.5),tl,rot+180+0,1-rev,sq,st).transpose(Image.FLIP_LEFT_RIGHT);spr.alpha_composite(im2,(int(OX+x+8-im2.width/2),int(OY+y-im2.height/2)))
    if st.get('ghost') and a>0:
        for g in (1,2):
            if a-g<0:continue
            im=arc(R*(1+.025*(a-g)),span,T*.8,min(1,(a-g+1)/2.5),0 if a-g<4 else min(1,(a-g-4)/7),rot,rev,sq,st);im.putalpha(im.getchannel('A').point(lambda v:int(v*(.4/g))))
            spr.alpha_composite(im,(int(OX+x-g*8-im.width/2),int(OY+y-im.height/2)))
    lay=Image.new('RGBA',spr.size);hx,hy=OX+x+R,OY+y;d=ImageDraw.Draw(lay)
    if st.get('ring') and a<10:r=6+a*6;al=int(255*(1-a/10));d.ellipse([hx-r*.5,hy-r,hx+r*.5,hy+r],outline=(200,240,255,al),width=2)
    fx2.star(lay,hx,hy,a,s['n']==2)
    if a>=1:
        col=st.get('sparkc')
        if col:
            rnd=random.Random(s['n']);px=lay.load()
            for i in range(10):
                g=rnd.uniform(-1.3,1.3);L=a*rnd.uniform(2,5);xx=int(hx+math.cos(g)*L);yy=int(hy+math.sin(g)*L)
                if 0<=xx<lay.width-1 and 0<=yy<lay.height:px[xx,yy]=(*col,max(0,255-a*28));px[xx+1,yy]=(*col,max(0,255-a*28))
        else:fx2.sparks(lay,hx,hy,8,a,s['n'])
    spr.alpha_composite(lay)
def timeline():
    T=[[] for _ in range(6)]
    for n in range(3):
        for a in range(LIFE+(3 if n<2 else 10)):T.append([{'n':n,'age':a}] if a<LIFE else [])
    return T
def panel(st,act,lab):
    spr=Image.new('RGBA',(440,300),(66,96,58,255));OX,OY=40,30;spr.alpha_composite(IDLE,(OX,OY))
    for s in act:draw(spr,s,st,OX,OY)
    p=spr.crop((110,40,410,294)).resize((240,203),Image.NEAREST);ImageDraw.Draw(p).text((6,4),lab,font=F,fill='white');return p
if __name__=='__main__':
    OUT=sys.argv[1];os.makedirs(OUT,exist_ok=True);TL=timeline();n=0
    for slow in (1,1,2):
        for f,act in enumerate(TL):
            fr=Image.new('RGB',(1200,812))
            for i,(nm,st) in enumerate(V):fr.paste(panel(st,act,f'{i+1}. {nm}').convert('RGB'),((i%5)*240,(i//5)*203))
            for q in range(slow):fr.save(f'{OUT}/{n:05d}.png');n+=1
    print(n)
