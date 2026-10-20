# Felt (ch.1) mob attack patterns: 3 per mob = 1 melee + 2 projectile patterns that always fire in the 4 directions (up/down/left/right).
# Melee uses the existing attack strip (atk/<id>.png; the spider lunges with its idle pose). Projectiles and hit flashes are drawn in code,
# not baked into sprites. Writes the pattern spec (patterns.json) and a preview video.
# usage: patterns.py <art/mobs/felt dir> <out.mp4> <tmp frame dir>
import sys,os,json,math,subprocess
from PIL import Image,ImageDraw,ImageFont
D,OUT,TMP=sys.argv[1:4];os.makedirs(TMP,exist_ok=True)
DIRS=[(1,0),(0,1),(-1,0),(0,-1)]   # right, down, left, up
# per pattern: windup/total in frames at 60fps, speed px/s (game pixels at sprite scale 1), waves = list of (frame offset), proj = code-drawn type
PAT={
 'c1_01_silmamul':[
  {'key':'melee','name':'실 휘감기','type':'melee','windup':12,'hit_frame':4,'range':70,'dmg':1.0},
  {'key':'needle_cross','name':'바늘 사방 사격','type':'proj','proj':'needle','dirs':4,'waves':[0],'speed':380,'windup':24,'dmg':0.6},
  {'key':'thread_ball','name':'실타래 탄 (맞으면 1초 묶임)','type':'proj','proj':'threadball','dirs':4,'waves':[0],'speed':170,'windup':30,'dmg':0.5,'on_hit':'bind_1s'}],
 'c1_02_thread_puppet':[
  {'key':'melee','name':'가위 베기','type':'melee','windup':12,'hit_frame':4,'range':80,'dmg':1.2},
  {'key':'blade_boomerang','name':'가위날 투척 (되돌아옴)','type':'proj','proj':'blade','dirs':4,'waves':[0],'speed':260,'windup':26,'dmg':0.8,'return':True},
  {'key':'pin_burst','name':'시침핀 3연사','type':'proj','proj':'pin','dirs':4,'waves':[0,8,16],'speed':340,'windup':20,'dmg':0.4}],
 'c1_03_needle_spider':[
  {'key':'melee','name':'바늘 다리 찍기','type':'melee','windup':12,'hit_frame':4,'range':60,'dmg':1.0,'lunge':True},
  {'key':'web_cross','name':'거미줄 탄 (감속 장판)','type':'proj','proj':'web','dirs':4,'waves':[0],'speed':210,'windup':24,'dmg':0.4,'on_end':'slow_zone_2s'},
  {'key':'venom_double','name':'독침 2파','type':'proj','proj':'venom','dirs':4,'waves':[0,24],'speed':320,'windup':20,'dmg':0.5,'on_hit':'poison_3s'}],
 'c1_04_unrotting_hound':[
  {'key':'melee','name':'달려들어 물기','type':'melee','windup':12,'hit_frame':4,'range':90,'dmg':1.3},
  {'key':'miasma_orb','name':'독기 구체','type':'proj','proj':'orb','dirs':4,'waves':[0],'speed':200,'windup':30,'dmg':0.7},
  {'key':'stone_shards','name':'돌껍질 파편 2파','type':'proj','proj':'shard','dirs':4,'waves':[0,14],'speed':300,'windup':22,'dmg':0.5}]}
json.dump({'note':'dirs 4 = right/down/left/up. frames at 60fps. projectiles drawn in code (proj type). speed in px/s at sprite scale 1.','patterns':PAT},
          open(f'{D}/patterns.json','w'),ensure_ascii=False,indent=1)

M={m['id']:m for m in json.load(open(f'{D}/manifest.json'))};A={a['id']:a for a in json.load(open(f'{D}/atk_manifest.json'))}
IDS=list(PAT);SC=0.55;Q=3;CW,CH=480,420;HEAD=44;VW,VH=CW*2,CH*2+HEAD
font=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',20);fbig=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',22)
def sc(im,s):return im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.NEAREST)
def frames_of(mid):
    m,a=M[mid],A[mid];idl=Image.open(f'{D}/sheets/{mid}.png');atk=Image.open(f'{D}/atk/{mid}.png')
    I=[(idl.crop((i*m['w'],0,(i+1)*m['w'],m['h'])),m['h']-12) for i in range(m['n'])]
    T=[(atk.crop((i*a['w'],0,(i+1)*a['w'],a['h'])),a['foot']) for i in range(a['n'])]
    return I,T,a['ticks']
# ---- code-drawn projectiles (drawn on a 1/3-res layer, upscaled x3 nearest for a pixel look)
def ang_pts(cx,cy,d,pts):
    c,s=d;return [(cx+x*c-y*s,cy+x*s+y*c) for x,y in pts]
def rot(d,a):
    c,s=math.cos(a),math.sin(a);return (d[0]*c-d[1]*s,d[0]*s+d[1]*c)
def draw_proj(g,kind,x,y,d,t,age):
    if kind=='needle':
        g.line(ang_pts(x,y,d,[(-7,0),(5,0)]),fill=(30,30,36),width=3);g.line(ang_pts(x,y,d,[(-6,0),(5,0)]),fill=(220,224,232),width=1)
        g.point(ang_pts(x,y,d,[(-5,0)]),fill=(30,30,36))
        for k in range(1,4):g.point(ang_pts(x,y,d,[(-7-3*k,0)]),fill=(160,160,170))
    elif kind=='threadball':
        g.ellipse((x-5,y-5,x+5,y+5),fill=(200,198,190),outline=(40,38,40))
        for k in range(3):a=age*0.3+k*2.1;g.arc((x-4,y-4,x+4,y+4),math.degrees(a),math.degrees(a)+120,fill=(120,116,112))
        tail=[ang_pts(x,y,d,[(-6-2*k,2*math.sin(age*0.4+k*0.9))])[0] for k in range(10)];g.line(tail,fill=(190,186,178),width=1)
    elif kind=='blade':
        p=rot((1,0),age*0.5);g.polygon(ang_pts(x,y,p,[(-8,0),(0,-2),(8,0),(0,2)]),fill=(170,90,50),outline=(50,25,15))
        g.polygon(ang_pts(x,y,rot(p,math.pi/2),[(-8,0),(0,-2),(8,0),(0,2)]),fill=(150,75,40),outline=(50,25,15))
        g.ellipse((x-1,y-1,x+1,y+1),fill=(230,200,140))
    elif kind=='pin':
        g.line(ang_pts(x,y,d,[(-5,0),(4,0)]),fill=(30,30,36),width=3);g.line(ang_pts(x,y,d,[(-5,0),(4,0)]),fill=(210,214,220),width=1)
        hx,hy=ang_pts(x,y,d,[(-6,0)])[0];g.ellipse((hx-2,hy-2,hx+2,hy+2),fill=(200,30,40),outline=(60,10,14))
    elif kind=='web':
        g.ellipse((x-6,y-6,x+6,y+6),fill=(235,235,240,180),outline=(90,90,100))
        for k in range(6):a=k*math.pi/3+age*0.05;g.line((x,y,x+6*math.cos(a),y+6*math.sin(a)),fill=(150,150,160))
        g.ellipse((x-3,y-3,x+3,y+3),outline=(150,150,160))
    elif kind=='venom':
        g.line(ang_pts(x,y,d,[(-6,0),(4,0)]),fill=(20,40,20),width=3);g.line(ang_pts(x,y,d,[(-5,0),(4,0)]),fill=(150,230,90),width=1)
        for k in range(1,3):tx,ty=ang_pts(x,y,d,[(-7-4*k,0)])[0];g.point((tx,ty),fill=(100,200,60))
    elif kind=='orb':
        r=5+math.sin(age*0.3);g.ellipse((x-r-3,y-r-3,x+r+3,y+r+3),fill=(120,40,170,90));g.ellipse((x-r,y-r,x+r,y+r),fill=(150,60,210),outline=(50,10,70))
        g.ellipse((x-2,y-2-1,x+2,y+2-1),fill=(230,190,255))
    elif kind=='shard':
        p=rot((1,0),age*0.4);g.polygon(ang_pts(x,y,p,[(-5,-3),(6,0),(-3,4)]),fill=(130,126,120),outline=(40,38,36))
        g.line(ang_pts(x,y,p,[(-2,-1),(3,0)]),fill=(160,90,200))
def draw_zone(g,x,y,age):   # web slow zone left where a web shot ends
    al=max(0,200-age*2);g.ellipse((x-12,y-7,x+12,y+7),outline=(200,200,210,al));g.line((x-12,y,x+12,y),fill=(200,200,210,al));g.line((x,y-7,x,y+7),fill=(200,200,210,al))
def flash(g,x,y,age,col):   # release flash ring
    r=4+age*1.5;al=max(0,220-age*28);g.ellipse((x-r,y-r,x+r,y+r),outline=col+(al,),width=2)
def slash(g,x,y,age,flip=False):  # melee hit arc
    al=max(0,240-age*30);r=14
    g.arc((x-r,y-r,x+r,y+r),-70,70,fill=(255,250,230,al),width=3)
# ---- timeline per mob: melee, rest, proj A, rest, proj B, rest
def timeline(mid):
    I,T,ticks=frames_of(mid);ev=[];spr=[]
    def idle(n,start=0):
        for f in range(n):spr.append(('i',(start+f)//8%len(I)))
    for p in PAT[mid]:
        t0=len(spr)
        if p['type']=='melee':
            if p.get('lunge'):
                seq=[(0,1,1),(-3,1.05,.94),(-6,1.08,.9),(12,.92,1.08),(20,.9,1.1),(22,.95,1.04),(20,1,1),(16,1.03,.97),(10,1.02,.98),(5,1,1),(2,1,1),(0,1,1)]
                for k,(dx,sx,sy) in enumerate(seq):spr+= [('l',(dx,sx,sy))]*ticks[k]
            else:
                for k,t in enumerate(ticks):spr+= [('a',k)]*t
            hit=t0+sum(ticks[:p['hit_frame']]);ev.append(('slash',hit,p))
        else:
            for f in range(p['windup']):spr.append(('w',f/p['windup']))
            for w in p['waves']:ev.append(('fire',t0+p['windup']+w,p))
            last=max(p['waves']);spr+= [('r',f) for f in range(10)]
            idle(last)
        ev.append(('label',t0,p));idle(70)
    return I,T,spr,ev
TL={mid:timeline(mid) for mid in IDS};N=max(len(v[2]) for v in TL.values())
for f in range(N):
    img=Image.new('RGBA',(VW,VH),(34,30,38,255));d=ImageDraw.Draw(img)
    d.text((12,10),'1장 펠트 몹 공격 패턴 — 근접 1 + 사방 투사체 2',font=fbig,fill=(255,200,120))
    for k,mid in enumerate(IDS):
        I,T,spr,ev=TL[mid];cx0,cy0=(k%2)*CW,(k//2)*CH+HEAD;ox,oy=cx0+CW//2,cy0+CH//2+70   # foot point
        d.rectangle((cx0+4,cy0+4,cx0+CW-4,cy0+CH-4),outline=(70,62,76))
        ff=min(f,len(spr)-1);kind,v=spr[ff];dx=0
        if kind=='i':im,foot=I[v]
        elif kind=='a':im,foot=T[v]
        elif kind=='l':im,foot=I[0];dx,sx,sy=v;im=im.resize((round(im.width*sx),round(im.height*sy)),Image.NEAREST);foot=round(foot*sy)
        elif kind=='w':im,foot=I[0];q=v;im=im.resize((round(im.width*(1+.08*q)),round(im.height*(1-.1*q))),Image.NEAREST);foot=round(foot*(1-.1*q))
        else:im,foot=I[0];q=max(0,1-v/10);im=im.resize((round(im.width*(1-.05*q)),round(im.height*(1+.08*q))),Image.NEAREST);foot=round(foot*(1+.08*q))
        s=sc(im,SC);sfoot=round(foot*SC);mw=round(M[mid]['w']*SC)
        img.alpha_composite(s,(ox-mw//2+round(dx*SC*2),oy-sfoot))
        bx,by=ox,oy-round(M[mid]['h']*SC*0.38)   # body centre = projectile origin
        L=Image.new('RGBA',(CW//Q,CH//Q),(0,0,0,0));g=ImageDraw.Draw(L)
        lab=None
        for e,t,p in ev:
            if e=='label' and t<=ff:lab=p
            age=f-t
            if age<0:continue
            if e=='slash' and age<9:slash(g,(bx-cx0+70)//Q,(by-cy0)//Q,age)
            if e=='fire':
                ex,ey=(bx-cx0)/Q,(by-cy0)/Q
                if age<8:flash(g,ex,ey,age,(255,255,255))
                v=p['speed']/60*SC/Q;R=min(CW,CH)/2/Q-8
                for dd in DIRS:
                    dist=age*v
                    if p.get('return'):dist=R*math.sin(min(math.pi,age*v/R*1.2))
                    if p.get('return') and age*v/R*1.2>math.pi:continue
                    if not p.get('return') and dist>R:
                        if p.get('on_end') and dist-R<v*100:draw_zone(g,ex+dd[0]*R,ey+dd[1]*R,int((dist-R)/v))
                        continue
                    draw_proj(g,p['proj'],ex+dd[0]*(dist+6),ey+dd[1]*(dist+6),dd,f,age)
        img.alpha_composite(L.resize((CW,CH),Image.NEAREST),(cx0,cy0))
        d.text((cx0+12,cy0+8),M[mid]['name'].split(' (')[0],font=fbig,fill=(235,225,210))
        if lab:
            i=PAT[mid].index(lab)+1;tag='근접' if lab['type']=='melee' else '사방 투사체'
            d.text((cx0+12,cy0+CH-34),f'{i}. {lab["name"]}  [{tag}]',font=font,fill=(255,215,150) if lab['type']=='melee' else (160,210,255))
    img.convert('RGB').save(f'{TMP}/{f:05d}.png')
subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate','60','-i',f'{TMP}/%05d.png','-vf',f'loop=1:size={N}','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',OUT],check=True)
print(N,'frames')
