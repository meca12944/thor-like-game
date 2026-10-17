"""Run the style sample in headless Chromium: FPS/frame-time measurement + screenshot + walking GIF frames."""
import asyncio, json, os, sys, shutil
from playwright.async_api import async_playwright
U = 'http://127.0.0.1:27413/index.html'; O = '/workspace/town-demo/style_sample/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-gpu-rasterization','--ignore-gpu-blocklist'])
        res = {}
        for (w, h) in [(1920, 1080), (1280, 720)]:
            for stress in (0, 40):
                pg = await b.new_page(viewport={'width': w, 'height': h})
                await pg.goto(U + f'?fps=1&stress={stress}')
                await pg.wait_for_function('window.__ss&&__ss.ready'); await pg.wait_for_timeout(1500)
                await pg.evaluate('__ss.startRec()'); await pg.wait_for_timeout(10000)
                r = await pg.evaluate('__ss.stopRec()'); res[f'{w}x{h}_stress{stress}'] = r; print(w, h, stress, r, flush=True)
                if w == 1920 and stress == 0: await pg.screenshot(path=O + 'work/fps_overlay_1920.png')
                await pg.close()
        json.dump(res, open(O + 'fps_measure.json', 'w'), indent=1)
        # clean screenshot + gif frames (deterministic, manual stepping)
        pg = await b.new_page(viewport={'width': 1920, 'height': 1080})
        await pg.goto(U); await pg.wait_for_function('window.__ss&&__ss.ready')
        await pg.evaluate('__ss.setManual(true);__ss.advance(1.2)'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=O + 'work/shot_1920.png')
        fr = O + 'work/gif/'; shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
        await pg.set_viewport_size({'width': 960, 'height': 540}); await pg.evaluate('__ss.setManual(true)')
        for i in range(int(12.6 * 15)):          # ~ one full loop at 15 fps capture
            await pg.evaluate('__ss.advance(1/15)'); await pg.wait_for_timeout(30)
            await pg.screenshot(path=fr + '%04d.png' % i)
        await b.close()
asyncio.run(main())
