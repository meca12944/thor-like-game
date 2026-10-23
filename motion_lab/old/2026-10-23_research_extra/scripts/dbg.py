import os
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720})
    pg.goto('http://127.0.0.1:8931/index.html');pg.wait_for_function('window.__world&&window.__game',timeout=60000);pg.wait_for_timeout(1500)
    f="()=>{const W=__world;return [W.scene,!!W.trans,W.map&&W.map.id,W.hero.x,W.hero.y,W.ready]}"
    print(pg.evaluate(f))
    pg.evaluate("()=>{__world.setManual(true);__world.go('field01','world')}")
    for i in range(12):pg.evaluate("()=>__world.advance(.5)");print(pg.evaluate(f))
    pg.evaluate("()=>__world.key('ArrowRight',true)")
    for i in range(3):pg.evaluate("()=>__world.advance(.3)");print(pg.evaluate(f))
    pg.screenshot(path='dbg.png');b.close()
