import sys,json,os
from playwright.sync_api import sync_playwright
url='http://127.0.0.1:8931/index.html';mode=sys.argv[1] if len(sys.argv)>1 else 'walk'
out=f'game/{mode}';os.makedirs(out,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(url);pg.wait_for_function('window.__world&&window.__game',timeout=60000);pg.wait_for_timeout(1500)
    pg.evaluate("()=>{__world.setManual(true);__world.go('field01','world')}")
    for i in range(12):pg.evaluate("()=>__world.advance(.5)")
    best=None
    for ty in range(6,30,2):
        for tx in range(4,30,3):
            r=pg.evaluate("([x,y])=>{const W=__world;W.setHeroTile(x,y,'right');W.advance(.05);const x0=W.hero.x;W.key('ArrowRight',true);W.advance(1.2);W.key('ArrowRight',false);W.advance(.5);return W.hero.x-x0}",[tx,ty])
            if r>90:best=(tx,ty);break
        if best:break
    print('open spot',best)
    pg.evaluate("([x,y])=>{const W=__world;W.setHeroTile(x,y,'right');W.killAll&&W.killAll();W.advance(.5)}",list(best))
    if mode=='run':
        pg.evaluate("()=>{const W=__world;W.key('ArrowRight',true);W.advance(1/60);W.key('ArrowRight',false);W.advance(2/60);W.key('ArrowRight',true)}")
    else:pg.evaluate("()=>__world.key('ArrowRight',true)")
    pg.evaluate("()=>__world.advance(.5)")
    rec=[]
    for i in range(48):
        pg.evaluate("()=>{__world.hero.hp=__world.hero.maxHp;__world.advance(1/60)}")
        h=pg.evaluate("()=>{const h=__world.hero;return {x:h.x,y:h.y,gp:h.gp,run:!!h.run,moving:h.moving}}")
        pg.screenshot(path=f'{out}/{i:03d}.png');rec.append(h)
    json.dump({'rec':rec,'errors':errs},open(f'{out}/rec.json','w'))
    print('errors',errs[:3]);print(rec[0],rec[-1])
    b.close()
