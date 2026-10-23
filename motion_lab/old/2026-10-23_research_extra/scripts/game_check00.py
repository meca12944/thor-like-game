# 들판에서 걷기·달리기(옆·아래·위·대각선)·점프를 찍어 MP4로. 게임 코드는 안 바꿈(입력만)
import os,json,subprocess,sys
from playwright.sync_api import sync_playwright
O=sys.argv[1];os.makedirs(O,exist_ok=True)
for f in os.listdir(O):os.remove(O+'/'+f)
n=0;errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720})
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://127.0.0.1:8931/index.html');pg.wait_for_function('window.__world&&window.__game',timeout=60000);pg.wait_for_timeout(2500)
    pg.evaluate("()=>{__world.setManual(true);__world.go('field00','world')}")
    for i in range(12):pg.evaluate("()=>__world.advance(.5)")
    SPOT=None
    for ty in range(6,30,2):
        for tx in range(6,40,2):
            r=pg.evaluate("([x,y])=>{const W=__world;W.setHeroTile(x,y,'right');W.advance(.05);const x0=W.hero.x,y0=W.hero.y;let ok=1;for(const k of ['ArrowRight','ArrowLeft','ArrowDown','ArrowUp']){W.setHeroTile(x,y,'right');W.advance(.02);const a=[W.hero.x,W.hero.y];W.key(k,true);W.advance(1);W.key(k,false);W.advance(.3);if(Math.hypot(W.hero.x-a[0],W.hero.y-a[1])<60)ok=0;}return ok}",[tx,ty])
            if r:SPOT=[tx,ty];break
        if SPOT:break
    print('spot',SPOT,'pet',pg.evaluate('()=>!!__world.S.pet'))
    def shot(k=1):
        global n
        for _ in range(k):
            pg.evaluate("()=>{__world.hero.hp=__world.hero.maxHp;__world.killAll&&__world.killAll();__world.advance(2/60)}");p_=pg.evaluate("()=>{const W=__world,S=W.S,v=S.view,h=W.hero,c=document.querySelector('canvas'),r=c.getBoundingClientRect(),q=r.width/c.width;return [r.left+(v.ox+(h.x-S.camI[0])*v.k)*q,r.top+(v.oy+(h.y-S.camI[1])*v.k)*q]}")
            x0=min(max(0,p_[0]-240),1280-480);y0=min(max(0,p_[1]-230),720-300)
            pg.screenshot(path=f'{O}/{n:04d}.png',clip={'x':x0,'y':y0,'width':480,'height':300});n+=1
    def hold(keys,secs,run=False):
        if run:
            pg.evaluate("(k)=>{const W=__world;const d={ArrowRight:'right',ArrowLeft:'left',ArrowUp:'up',ArrowDown:'down'}[k];W.dirTap(d);W.dirTap(d)}",keys[0])
        for k in keys:pg.evaluate("(k)=>__world.key(k,true)",k)
        shot(int(secs*30));print(keys,'run' if run else 'walk',pg.evaluate('()=>[Math.round(__world.hero.x),Math.round(__world.hero.y),!!__world.hero.run,__world.hero.f8||__world.hero.face]'))
        for k in keys:pg.evaluate("(k)=>__world.key(k,false)",k)
        shot(10)
    for keys,run in [(['ArrowRight'],0),(['ArrowLeft'],0),(['ArrowDown'],0),(['ArrowUp'],0),(['ArrowRight'],1),(['ArrowLeft'],1),(['ArrowDown'],1),(['ArrowUp'],1)]:
        pg.evaluate("([x,y])=>{const W=__world;W.setHeroTile(x,y,'right');if(W.S.pet){W.S.pet.x=W.hero.x-14;W.S.pet.y=W.hero.y+4;}W.advance(.6)}",SPOT);hold(keys,2.0,run)
    pg.evaluate("()=>__world.tap('Space')");shot(40)
    b.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{O}/%04d.png','-pix_fmt','yuv420p','-vf','scale=960:600:flags=neighbor',O+'.mp4'])
print('errors',errs[:5],'frames',n)
