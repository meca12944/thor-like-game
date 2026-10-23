import os
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_CHROME']);pg=b.new_page(viewport={'width':1280,'height':720});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://127.0.0.1:8931/index.html');pg.wait_for_timeout(4000)
    for k in ['ArrowRight','ArrowDown','ArrowUp','ArrowLeft']:
        pg.keyboard.down(k);pg.wait_for_timeout(700);pg.screenshot(path=f'town_{k}.png');pg.keyboard.up(k)
    pg.keyboard.press('ArrowRight');pg.wait_for_timeout(60);pg.keyboard.down('ArrowRight');pg.wait_for_timeout(700);pg.screenshot(path='town_run.png');pg.keyboard.up('ArrowRight')
    print('errors',errs[:5]);b.close()
