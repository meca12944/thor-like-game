#!/usr/bin/env python3
"""Headless check of town/bgm.js: no console errors, starts after first input, town -> champion -> victory -> town, dive, keys."""
import asyncio, subprocess, sys, os, time
from playwright.async_api import async_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PORT = 18977
URL = f'http://localhost:{PORT}/town/index.html'

async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '-d', ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    ok = True
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
            pg = await b.new_page(viewport={'width': 1280, 'height': 720})
            errs = []
            pg.on('console', lambda m: errs.append('console.' + m.type + ': ' + m.text) if m.type == 'error' else None)
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
            pg.on('requestfailed', lambda r: errs.append('FAIL ' + r.url))
            await pg.goto(URL)
            for _ in range(100):
                if await pg.evaluate('!!(window.__game&&window.__game.ready)'): break
                await pg.wait_for_timeout(100)
            st = lambda: pg.evaluate('BGM.state')
            s0 = await st(); print('before input:', s0)
            assert not s0['started'], 'must not start before input'
            await pg.evaluate("()=>{const g=__game;const b=g.boar;b.x=g.hero.x+900;b.y=g.hero.y;b.hp=b.maxHp;b.t=99}")
            await pg.keyboard.press('ArrowRight')
            async def wait_track(tid, ms=12000):
                for _ in range(ms // 200):
                    s = await st()
                    if s['current'] == tid: return s
                    await pg.wait_for_timeout(200)
                raise AssertionError('expected %s, state %s' % (tid, await st()))
            async def keep_boar_far():
                await pg.evaluate("()=>{const g=__game,b=g.boar;b.x=Math.min(1400,g.hero.x+900);b.y=g.hero.y;b.hp=b.maxHp;}")
            await keep_boar_far()
            s = await wait_track('town_a_fountain'); print('town:', s)
            await pg.evaluate("()=>{const g=__game,b=g.boar;b.dead=false;b.x=g.hero.x+150;b.y=g.hero.y;b.hp=b.maxHp-1;}")
            s = await wait_track('battle_champion'); print('champion fight:', s)
            await pg.evaluate("()=>{const g=__game,b=g.boar;b.dead=true;b.respawn=999;}")
            s = await wait_track('jingle_victory'); print('victory jingle:', s)
            s = await wait_track('town_a_fountain', 15000); print('back to town:', s)
            await pg.keyboard.press('b'); await pg.wait_for_timeout(300); m1 = await st()
            await pg.keyboard.press('b'); await pg.wait_for_timeout(300); m2 = await st()
            assert m1['muted'] and not m2['muted'], 'B toggles mute'
            await pg.keyboard.press('Minus'); await pg.wait_for_timeout(200); v = await st(); print('volume after -:', v['vol'])
            await pg.keyboard.press('Equal')
            await pg.keyboard.press('n'); s = await wait_track('area01_forest'); print('jukebox 1:', s['current'])
            await pg.keyboard.press('n'); s = await wait_track('area02_cave'); print('jukebox 2:', s['current'])
            await pg.screenshot(path='/tmp/bgm_test.png')
            # every track decodes
            n = await pg.evaluate("""async()=>{const m=await (await fetch('../audio/bgm/bgm.json')).json();const ac=new OfflineAudioContext(2,44100,44100);let n=0;
              for(const id in m){const ab=await (await fetch('../audio/bgm/'+m[id].file)).arrayBuffer();const buf=await ac.decodeAudioData(ab);
              if(Math.abs(buf.duration-m[id].duration)>0.05)throw new Error(id+' duration '+buf.duration);n++;}return n}""")
            print('decoded tracks:', n)
            print('console errors:', errs or 'none')
            ok = not errs
            await b.close()
    finally:
        srv.terminate()
    print('PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)

asyncio.run(main())
