"""File SFX (assets/sfx/fx): all load after the audio unlock (no 404), every SFX.ev hook callable, voice cap holds, no console errors.
Run: python3 town/tools/test_sfx.py   (serves the repo root on :18947)"""
import asyncio, json, subprocess, sys, os, glob
from playwright.async_api import async_playwright
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PORT = 18947
async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=os.path.dirname(D), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1); errs = []; bad = []; R = {}
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg = await b.new_page()
            pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
            pg.on('response', lambda r: r.status >= 400 and bad.append(f'{r.status} {r.url}'))
            await pg.goto(f'http://127.0.0.1:{PORT}/town/index.html?nosave=1'); await pg.wait_for_function("window.__game", timeout=20000)
            R['lazy_before_unlock'] = await pg.evaluate("__game.SFX.stat.req") == 0
            await pg.mouse.click(640, 360); await pg.keyboard.press('KeyZ'); await pg.wait_for_timeout(5000)
            st = await pg.evaluate("__game.SFX.stat"); n = len(glob.glob(D + '/assets/sfx/fx/*.ogg'))
            R['all_loaded'] = (st['ok'] == n and not st['fail'], st['ok'], n, st['fail'])
            R['hooks'] = await pg.evaluate("""(()=>{const E=__game.SFX.ev,bad=[];for(const k in E){try{E[k]('sword',0)}catch(e){bad.push(k+':'+e.message)}}return bad})()"""); R['hooks'] = (R['hooks'] == [], R['hooks'])
            R['voice_cap'] = await pg.evaluate("""(()=>{for(let i=0;i<40;i++){__game.SFX.play('footstep');__game.SFX.play('hit_normal');}return __game.SFX.stat.voices})()""") <= 12
            await b.close()
    finally: srv.terminate()
    R['no_404'] = (not bad, bad); R['noErrors'] = (not errs, errs)
    print(json.dumps(R, ensure_ascii=False)); ok = all((v[0] if isinstance(v, tuple) else v) for v in R.values()); print('PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
asyncio.run(main())
