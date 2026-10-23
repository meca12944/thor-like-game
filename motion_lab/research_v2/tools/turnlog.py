# 게임(들판)에서 주인공을 8방향으로 걷기·달리기·멈추기·방향 바꾸기 시키며 틱마다 그림 칸을 기록 -> 머리 튐(방향 바꿀 때 머리가 순간이동한 칸 수)을 잼
#   python3 turnlog.py <주소> <out.json> [frames_dir]
import os,sys,json
from playwright.sync_api import sync_playwright
URL,OUT=sys.argv[1],sys.argv[2];FR=sys.argv[3] if len(sys.argv)>3 else None
K={'R':['ArrowRight'],'L':['ArrowLeft'],'U':['ArrowUp'],'D':['ArrowDown'],'DR':['ArrowDown','ArrowRight'],'DL':['ArrowDown','ArrowLeft'],'UR':['ArrowUp','ArrowRight'],'UL':['ArrowUp','ArrowLeft'],'-':[]}
# (방향, 틱, 달리기)
SEQ=[('-',20,0),('R',40,0),('-',20,0),('R',40,1),('-',20,0),('L',30,1),('R',30,1),('-',20,0),('D',40,1),('U',30,1),('-',20,0),
     ('R',20,1),('DR',20,1),('D',20,1),('DL',20,1),('L',20,1),('UL',20,1),('U',20,1),('UR',20,1),('R',20,1),('-',20,0),
     ('R',20,0),('DR',20,0),('D',20,0),('DL',20,0),('L',20,0),('UL',20,0),('U',20,0),('UR',20,0),('R',20,0),('-',20,0),
     ('DR',30,1),('-',20,0),('DL',30,1),('-',20,0),('D',30,0),('-',20,0)]
log=[];errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720})
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_function('window.__world&&window.__game&&window.__world.ready',timeout=60000);pg.wait_for_timeout(1500)
    pg.evaluate("()=>{__world.setManual(true);__world.go('field01','world')}")
    for i in range(10):pg.evaluate("()=>__world.advance(.5)")
    pg.evaluate("()=>{const W=__world;W.killAll&&W.killAll();W.setHeroTile(13,10,'right');W.advance(.3)}")
    held=[];n=0
    for d,ticks,run in SEQ:
        keys=K[d]
        for k in held:
            if k not in keys:pg.evaluate("(k)=>__world.key(k,false)",k)
        if run and keys and not pg.evaluate("()=>!!__world.hero.run"):
            pg.evaluate("(k)=>{const d={ArrowRight:'right',ArrowLeft:'left',ArrowUp:'up',ArrowDown:'down'}[k];__world.dirTap(d);__world.dirTap(d)}",keys[-1])
        for k in keys:pg.evaluate("(k)=>__world.key(k,true)",k)
        held=keys
        for t in range(ticks):
            r=pg.evaluate("()=>{const W=__world;W.hero.hp=W.hero.maxHp;W.killAll&&W.killAll();W.advance(1/60);const h=W.hero;return [h.x,h.y,h.face,h.f8,!!h.run,!!h.moving,W.cell8()]}")
            log.append({'seg':f'{d}{"run" if run else ""}','x':r[0],'y':r[1],'face':r[2],'f8':r[3],'run':r[4],'mov':r[5],'cell':r[6]})
            if FR and n%2==0:
                p_=pg.evaluate("()=>{const W=__world,S=W.S,v=S.view,h=W.hero,c=document.querySelector('canvas'),r=c.getBoundingClientRect(),q=r.width/c.width;return [r.left+(v.ox+(h.x-S.camI[0])*v.k)*q,r.top+(v.oy+(h.y-S.camI[1])*v.k)*q]}")
                os.makedirs(FR,exist_ok=True);x0=min(max(0,p_[0]-160),1280-320);y0=min(max(0,p_[1]-200),720-260)
                pg.screenshot(path=f'{FR}/{n//2:04d}.png',clip={'x':x0,'y':y0,'width':320,'height':260})
            n+=1
    b.close()
json.dump({'log':log,'errs':errs},open(OUT,'w'));print('ticks',len(log),'errors',errs[:3])
