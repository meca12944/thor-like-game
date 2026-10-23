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
    n=0
    for face in ['ArrowRight','ArrowDown']:
        pg.evaluate("(k)=>{const W=__world;W.killAll&&W.killAll();W.setHeroTile(13,6,'right');W.advance(.2);W.key(k,true);W.advance(.05);W.key(k,false);W.advance(.4)}",face)
        for t in range(75):
            if t in (2,22,44):pg.evaluate("()=>__world.tap('KeyJ')")
            r=pg.evaluate("()=>{const W=__world,h=W.hero;W.killAll&&W.killAll();W.advance(1/60);const S=W.S,v=S.view,c=document.querySelector('canvas'),R=c.getBoundingClientRect(),q=R.width/c.width;return [R.left+(v.ox+(h.x-S.camI[0])*v.k)*q,R.top+(v.oy+(h.y-S.camI[1])*v.k)*q]}")
            x0=min(max(0,r[0]-200),880);y0=min(max(0,r[1]-170),470)
            pg.screenshot(path=f'{O}/{n:04d}.png',clip={'x':x0,'y':y0,'width':400,'height':250});n+=1
    b.close()
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','20','-i',f'{O}/%04d.png','-pix_fmt','yuv420p','-vf','scale=800:500:flags=neighbor',O+'.mp4'])
print('errors',errs[:3],n)
