import os,sys,subprocess
from playwright.sync_api import sync_playwright
O=sys.argv[1];os.makedirs(O,exist_ok=True)
for f in os.listdir(O):os.remove(O+'/'+f)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://127.0.0.1:8931/index.html');pg.wait_for_function('window.__world&&window.__game',timeout=60000);pg.wait_for_timeout(2500)
    pg.evaluate("()=>{__world.setManual(true);__world.go('field01','world')}")
    for i in range(12):pg.evaluate("()=>__world.advance(.5)")
    pg.evaluate("()=>{const W=__world;W.killAll&&W.killAll();W.setHeroTile(13,6,'right');W.advance(.2);W.key('ArrowRight',true);W.advance(.1);W.key('ArrowRight',false);W.advance(.3)}")
    n=0;log=[]
    for rnd in range(3):
        pg.evaluate("()=>{const W=__world,h=W.hero;W.killAll&&W.killAll();h.inv=0;W.spawn('boar',h.x-26,h.y);W.advance(1/60)}")
        for t in range(90):
            r=pg.evaluate("()=>{const W=__world,h=W.hero;if(h.hp<h.maxHp*.5)h.hp=h.maxHp;W.advance(1/60);const S=W.S,v=S.view,c=document.querySelector('canvas'),R=c.getBoundingClientRect(),q=R.width/c.width;return [h.face,Math.round(h.x*10)/10,Math.round(h.inv*100)/100,R.left+(v.ox+(h.x-S.camI[0])*v.k)*q,R.top+(v.oy+(h.y-S.camI[1])*v.k)*q]}")
            log.append(r[:3])
            x0=min(max(0,r[3]-240),800);y0=min(max(0,r[4]-200),420)
            pg.screenshot(path=f'{O}/{n:04d}.png',clip={'x':x0,'y':y0,'width':480,'height':300});n+=1
        pg.evaluate("()=>{const W=__world;W.killAll&&W.killAll();W.hero.face='right';W.hero.f8='right';W.advance(.6)}")
    b.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','20','-i',f'{O}/%04d.png','-pix_fmt','yuv420p','-vf','scale=960:600:flags=neighbor',O+'.mp4'])
hit=[i for i in range(1,len(log)) if log[i][2]>log[i-1][2]+.5]
for h in hit[:3]:print('맞은 장',h,log[h-1:h+9])
print('errors',errs[:3])
