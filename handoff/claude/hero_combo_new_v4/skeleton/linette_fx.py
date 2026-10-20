# Linette weapon effects (test128/linette.html, PR #21) applied to the new hero combo, rendered to frames.
# strike frame per hit -> layered lance trail at the blade tip along the blade (trailOne port), hit-stop 4/5/9 ticks (sprite and
# trail age frozen), screen shake 1.5/2/4 px decaying x0.82 per frame, hit 3: heavy trail + shockwave ring (16 ticks) + white flash (4).
import random
from PIL import Image,ImageDraw,ImageFont
P='newatk/';F=ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf',16)
T={'hit1':[3,3,3,2,2,1,1,1,1,3,2,2,2,2,2],'hit2':[2,2,2,2,2,2,2,2,2,2,2,2,2,2,3],'hit3':[2,2,2,2,2,1,1,1,1,1,2,3,3,3,4]}
STRIKE={'hit1':(9,(241,117),(0.99,-0.12),False,False),'hit2':(5,(185,42),(0.39,-0.92),True,False),'hit3':(10,(244,140),(1.0,-0.06),True,True)}
HIT={'hit1':(4,1.5),'hit2':(5,2),'hit3':(9,4)};NOFX={'hit2'}
def lance(d,cx,cy,dx,dy,nx,ny,back,ahead,w,col):
    d.polygon([(cx-dx*back,cy-dy*back),(cx+nx*w/2,cy+ny*w/2),(cx+dx*ahead,cy+dy*ahead),(cx-nx*w/2,cy-ny*w/2)],fill=col)
def trail(layer,tip,dr,age,big,heavy):
    life=20 if heavy else 16 if big else 12
    if age<0 or age>=life:return
    d=ImageDraw.Draw(layer,'RGBA');g=min(1,(age+1)/2);a=1-age/life;dx,dy=dr;nx,ny=-dy,dx;tx,ty=tip
    ahead=(92 if heavy else 70 if big else 52)*g;back=40 if heavy else 34 if big else 26;W=16 if heavy else 12 if big else 9;cx=tx+dx*ahead*.35;cy=ty+dy*ahead*.35
    if heavy:lance(d,cx,cy,dx,dy,nx,ny,back+ahead*.45,ahead*.75,W*1.6,(60,150,255,int(255*.31*a)))
    lance(d,cx,cy,dx,dy,nx,ny,back+ahead*.35,ahead*.65,W,(90,210,255,int(255*.47*a)))
    lance(d,cx,cy,dx,dy,nx,ny,back*.8+ahead*.3,ahead*.6,W*.45,(210,250,255,int(255*.86*a)))
    lance(d,cx,cy,dx,dy,nx,ny,back*.6+ahead*.25,ahead*.55,max(1.5,W*.18),(255,255,255,int(255*a)))
    for o,l in ([(.9,.6),(-.9,.5),(1.6,.35),(-1.6,.3)] if big else [(.9,.55),(-.9,.45)]):
        sx=cx+nx*o*W-dx*back*.6;sy=cy+ny*o*W-dy*back*.6;L=(back+ahead)*l;d.line([(sx,sy),(sx+dx*L,sy+dy*L)],fill=(200,245,255,int(255*.67*a)),width=1)
    if age<4:
        ex=tx+dx*ahead*.95;ey=ty+dy*ahead*.95;r=5 if big else 4;d.rectangle([ex-r,ey,ex+r,ey],fill=(255,255,255,int(255*a)));d.rectangle([ex,ey-r,ex,ey+r],fill=(255,255,255,int(255*a)))
def timeline(fx):
    """list of per-tick states: (sprite, [(trail args)], shake, waves, flash)"""
    out=[];idle=Image.open('/home/user/thor-like-game/char_v4/pixellab/hero/v3gen_20261018/moves_v1/idle/east/000.png').convert('RGBA')
    for _ in range(12):out.append((idle,None,0))
    active=[];shake=0;waves=[];flash=0;rnd=random.Random(1)
    for clip in ('hit1','hit2','hit3'):
        sf,tip,dr,big,heavy=STRIKE[clip];stop,sk=HIT[clip]
        if clip in NOFX:sf=-1   # owner 2026-10-20: no effect on hit 2
        for i,t in enumerate(T[clip]):
            im=Image.open(f'{P}clean/{clip}_{i:02d}.png')
            ticks=t+(stop if (fx and i==sf) else 0)
            for k in range(ticks):
                if fx and i==sf and k==0:
                    active.append({'tip':tip,'dr':dr,'big':big,'heavy':heavy,'age':0});shake=max(shake,sk)
                    if heavy:waves.append({'x':tip[0]+dr[0]*60,'y':189-6,'a':0});flash=4
                frozen=fx and i==sf and k<stop
                out.append((im,[dict(x) for x in active],(shake,rnd.random(),rnd.random()),[dict(w) for w in waves],flash))
                if not frozen:
                    for a in active:a['age']+=1
                for w in waves:w['a']+=1
                waves=[w for w in waves if w['a']<16];active=[a for a in active if a['age']<20]
                shake=shake*0.82 if shake>0.3 else 0;flash=max(0,flash-1)
    for _ in range(20):out.append((Image.open(f'{P}clean/hit3_14.png'),[],(0,0,0),[],0))
    return out
def render(state,W=480,H=380,lab=''):
    im,trs,sh,waves,flash=(state+(None,None,None))[:5] if len(state)==3 else state
    fr=Image.new('RGBA',(W,H),(66,96,58,255));layer=Image.new('RGBA',(256,256))
    sx=sy=0
    if sh and sh[0]:sx=round((sh[1]*2-1)*sh[0]);sy=round((sh[2]*2-1)*sh[0])
    OX,OY=40,30;spr=Image.new('RGBA',(400,300));spr.alpha_composite(im,(OX,OY))
    for w in (waves or []):
        a=1-w['a']/16;r=10+w['a']*7;ImageDraw.Draw(spr,'RGBA').ellipse([OX+w['x']-r,OY+w['y']-r*.45,OX+w['x']+r,OY+w['y']+r*.45],outline=(200,240,255,int(255*.8*a)),width=max(1,round(3*a+1)))
    for t in (trs or []):trail(spr,(t['tip'][0]+OX,t['tip'][1]+OY),t['dr'],t['age'],t['big'],t['heavy'])
    big=spr.resize((600,450),Image.NEAREST);fr.alpha_composite(big,(-80+sx*3//2,-40+sy*3//2))
    if flash:fr.alpha_composite(Image.new('RGBA',(W,H),(255,255,255,int(255*flash*0.05))))
    ImageDraw.Draw(fr).text((10,8),lab,font=F,fill='white');return fr
if __name__=='__main__':
    A=timeline(False);B=timeline(True);n=0
    for slow in (1,1,3):
        L=max(len(A),len(B))
        for i in range(L):
            a=A[min(i,len(A)-1)];b=B[min(i,len(B)-1)]
            fa=render(a if len(a)==5 else (a[0],None,(0,0,0),[],0),lab='새 공격 · 효과 없음'+(' · 1/3 슬로우' if slow>1 else ''))
            fb=render(b if len(b)==5 else (b[0],None,(0,0,0),[],0),lab='새 공격 + 리네트 무기 효과'+(' · 1/3 슬로우' if slow>1 else ''))
            fr=Image.new("RGB",(960,380));fr.paste(fa.convert('RGB'),(0,0));fr.paste(fb.convert('RGB'),(480,0))
            for k in range(slow):fr.save(f'{P}fx/{n:05d}.png');n+=1
    print('frames',n)
