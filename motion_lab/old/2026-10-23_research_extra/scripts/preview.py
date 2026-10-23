import os
from playwright.sync_api import sync_playwright
U='https://raw.githack.com/meca12944/thor-like-game/claude/motion-lab/test128/index.html?go=field00'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME'],args=['--ignore-certificate-errors']);pg=b.new_page(viewport={'width':1280,'height':720});errs=[];bad=[]
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('response',lambda r:bad.append((r.status,r.url[-60:])) if r.status>=400 else None)
    pg.goto(U,timeout=90000);pg.wait_for_timeout(12000)
    pg.keyboard.down('ArrowRight');pg.wait_for_timeout(900);pg.screenshot(path='preview.png');pg.keyboard.up('ArrowRight')
    print('errors',errs[:3],'bad',bad[:5],'scene',pg.evaluate("()=>window.__world&&[__world.scene,__world.map&&__world.map.id]"))
    b.close()
