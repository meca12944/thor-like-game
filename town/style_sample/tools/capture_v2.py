import asyncio, json
from playwright.async_api import async_playwright
U = 'http://127.0.0.1:27413/index.html'; O = '/workspace/town-demo/style_sample/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-gpu-rasterization', '--ignore-gpu-blocklist']); res = {}
        errs = []
        for stress in (0, 40):
            pg = await b.new_page(viewport={'width': 1920, 'height': 1080}); pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U + f'?fps=1&stress={stress}'); await pg.wait_for_function('window.__ss&&__ss.ready'); await pg.wait_for_timeout(1500)
            await pg.evaluate('__ss.startRec()'); await pg.wait_for_timeout(8000)
            r = await pg.evaluate('__ss.stopRec()'); res[f'1920x1080_stress{stress}'] = r; print(stress, r, flush=True)
            if stress == 0: await pg.screenshot(path=O + 'work/fps_overlay_v2.png')
            await pg.close()
        json.dump(res, open(O + 'fps_measure_v2.json', 'w'), indent=1)
        pg = await b.new_page(viewport={'width': 1920, 'height': 1080}); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('window.__ss&&__ss.ready')
        await pg.evaluate('__ss.setManual(true);__ss.advance(2.0)'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=O + 'sample_scene_v2.png'); print('errors', errs)
        await b.close()
asyncio.run(main())
