import os
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://127.0.0.1:8931/linette.html');pg.wait_for_timeout(3000)
    for k in ['ArrowRight','ArrowDown','ArrowUp','ArrowLeft']:
        pg.keyboard.down(k);pg.wait_for_timeout(800);pg.keyboard.up(k)
    pg.keyboard.down('Shift');pg.keyboard.down('ArrowRight');pg.wait_for_timeout(900);pg.screenshot(path='sbx.png');pg.keyboard.up('ArrowRight');pg.keyboard.up('Shift')
    print('errors',errs[:5]);b.close()
