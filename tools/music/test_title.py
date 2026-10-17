#!/usr/bin/env python3
"""[title] Headless check of town/title.js + title BGM: overlay shown (?titlescreen=1), game ignores keys while it is up,
title theme starts on the first key, 이어하기 disabled without a save, settings volume, 새 게임 -> overlay gone and
title theme fades into the town music, game takes input afterwards, ~60 fps on the title screen, no console errors.
Under automation without ?titlescreen=1 the title screen is skipped (existing tests stay unaffected) - also checked."""
import asyncio, subprocess, sys, os, time
from playwright.async_api import async_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PORT = 18978
U = f'http://localhost:{PORT}/town/index.html'

async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '-d', ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1); ok = True
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
            pg = await b.new_page(viewport={'width': 1280, 'height': 720})
            errs = []
            pg.on('console', lambda m: errs.append('console.' + m.type + ': ' + m.text) if m.type == 'error' else None)
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
            pg.on('requestfailed', lambda r: errs.append('FAIL ' + r.url))
            # 1) skipped under automation by default
            await pg.goto(U)
            await pg.wait_for_timeout(800)
            assert await pg.evaluate("!document.getElementById('ttl') && __titleScreen.skipped"), 'title must be skipped for plain automated runs'
            print('plain automated run: title skipped')
            # 2) forced title screen
            await pg.evaluate("localStorage.removeItem('townDemo.quicksave')")
            await pg.goto(U + '?titlescreen=1')
            for _ in range(100):
                if await pg.evaluate('!!(window.__game&&window.__game.ready)'): break
                await pg.wait_for_timeout(100)
            assert await pg.evaluate("!!document.getElementById('ttl') && __titleScreen.active"), 'overlay visible'
            assert not (await pg.evaluate('BGM.state'))['started'], 'no audio before input'
            fps = await pg.evaluate("""()=>new Promise(r=>{let n=0,t0=performance.now();function f(t){n++;if(t-t0<2000)requestAnimationFrame(f);else r(n*1000/(t-t0));}requestAnimationFrame(f);})""")
            print('fps on title screen: %.1f' % fps)
            await pg.evaluate('__game.setManual&&__game.setManual(true)')
            hx0 = await pg.evaluate('[__game.hero.x,__game.hero.y]')
            await pg.keyboard.down('d'); await pg.wait_for_timeout(100); held = await pg.evaluate('JSON.stringify(__game.keys)'); await pg.evaluate('__game.advance&&__game.advance(.3)'); await pg.keyboard.up('d')
            hx1 = await pg.evaluate('[__game.hero.x,__game.hero.y]')
            print('held keys seen by game during title:', held)
            assert hx0 == hx1, 'hero must not move while the title screen is up %s %s' % (hx0, hx1)
            assert await pg.evaluate("__titleScreen.stage") == 'menu', 'any key -> menu'
            for _ in range(60):
                s = await pg.evaluate('BGM.state')
                if s['current'] == 'title': break
                await pg.wait_for_timeout(200)
            print('after first key:', s); assert s['current'] == 'title', 'title theme plays'
            items = await pg.evaluate("[...document.querySelectorAll('#ttl li')].map(l=>l.textContent+(l.classList.contains('off')?' [off]':''))")
            print('menu:', items); assert any('이어하기' in t and '[off]' in t for t in items), '이어하기 disabled without save'
            # settings: volume
            await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('Enter')   # 새 게임 -> (skip 이어하기) 설정
            assert await pg.evaluate("__titleScreen.stage") == 'settings'
            v0 = (await pg.evaluate('BGM.state'))['vol']; await pg.keyboard.press('ArrowLeft'); v1 = (await pg.evaluate('BGM.state'))['vol']
            await pg.keyboard.press('ArrowRight'); print('settings volume', v0, '->', v1); assert v1 < v0
            await pg.screenshot(path='/tmp/title_test.png')
            await pg.evaluate("()=>{const g=__game,b=g.boar,h=g.hero;b.x=h.x<640?1200:80;b.y=h.y<450?690:200;b.hp=b.maxHp;b.t=99}")  # champion far away -> town music
            await pg.keyboard.press('Escape'); await pg.keyboard.press('ArrowUp'); await pg.keyboard.press('Enter')  # 새 게임
            await pg.wait_for_timeout(300)
            assert not await pg.evaluate("__titleScreen.active"), 'game started'
            for _ in range(60):
                s = await pg.evaluate('BGM.state')
                if s['current'] == 'town_a_fountain': break
                await pg.wait_for_timeout(200)
            print('after 새 게임:', s); assert s['current'] == 'town_a_fountain'
            await pg.wait_for_timeout(1200)
            assert not await pg.evaluate("!!document.getElementById('ttl')"), 'overlay removed'
            await pg.evaluate('__game.setManual&&__game.setManual(true)')
            hx0 = await pg.evaluate('[__game.hero.x,__game.hero.y]')
            await pg.keyboard.down('d'); await pg.wait_for_timeout(100); held = await pg.evaluate('JSON.stringify(__game.keys)'); await pg.evaluate('__game.advance&&__game.advance(.3)'); await pg.keyboard.up('d')
            hx1 = await pg.evaluate('[__game.hero.x,__game.hero.y]')
            print('held keys seen by game after start:', held)
            print('hero moved after start:', hx0, '->', hx1); assert hx1 != hx0
            print('console errors:', errs or 'none'); ok = not errs and fps > 50
            await b.close()
    finally:
        srv.terminate()
    print('PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)

asyncio.run(main())
