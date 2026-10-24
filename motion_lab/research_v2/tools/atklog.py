# 게임(들판)에서 주인공이 오른쪽·왼쪽을 보고 1·2·3타 연속 공격 -> 틱마다 화면 (때리기 몸동작 전·후 비교)
import os,sys,json
from playwright.sync_api import sync_playwright
URL,FR=sys.argv[1],sys.argv[2];os.makedirs(FR,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_function('window.__world&&window.__world.ready',timeout=60000);pg.wait_for_timeout(1500)
    pg.evaluate("()=>{const W=__world;W.setManual(true);W.killAll&&W.killAll();W.hero.x=488;W.hero.y=470;W.advance(.3)}")
    n=0
    def shot(k):
        global n
        for _ in range(k):
            pg.evaluate("()=>{const W=__world;W.hero.hp=W.hero.maxHp;W.killAll&&W.killAll();W.advance(1/60)}")
            q=pg.evaluate("()=>{const W=__world,S=W.S,v=S.view,h=W.hero,c=document.querySelector('canvas'),r=c.getBoundingClientRect(),s=r.width/c.width;return [r.left+(v.ox+(h.x-S.camI[0])*v.k)*s,r.top+(v.oy+(h.y-S.camI[1])*v.k)*s]}")
            x0=min(max(0,q[0]-160),1280-320);y0=min(max(0,q[1]-190),720-260)
            pg.screenshot(path=f'{FR}/{n:04d}.png',clip={'x':x0,'y':y0,'width':320,'height':260});n+=1
    for face,key in [('right','ArrowRight'),('left','ArrowLeft')]:
        pg.evaluate("(k)=>{__world.key(k,true);__world.advance(.1);__world.key(k,false);__world.advance(.3)}",key);shot(10)
        for hit in range(3):
            pg.evaluate("()=>__world.key('KeyJ',true)");shot(2);pg.evaluate("()=>__world.key('KeyJ',false)");shot(18 if hit<2 else 30)
        shot(15)
    b.close();print('frames',n,'errs',errs[:3])
