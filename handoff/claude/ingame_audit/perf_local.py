import asyncio, json, subprocess, sys, time
from playwright.async_api import async_playwright
PORT=int(sys.argv[1]); D=sys.argv[2]
FPS_JS=open('perf.py').read().split('FPS_JS="""')[1].split('"""')[0]
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    out={}
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        for q in ['?start=field00&notitle','?start=felt&notitle','?notitle']:
            r=[]
            for thr in (1,4):
                c=await b.new_context(viewport={'width':1600,'height':900}); pg=await c.new_page(); cdp=await c.new_cdp_session(pg)
                if thr>1: await cdp.send('Emulation.setCPUThrottlingRate',{'rate':thr})
                await pg.goto(f'http://127.0.0.1:{PORT}/index.html'+q); await pg.wait_for_function('window.__game&&window.__game.ready',timeout=120000); await pg.wait_for_timeout(3000)
                await pg.mouse.click(800,450); await pg.keyboard.down('ArrowRight'); f=await pg.evaluate(FPS_JS); await pg.keyboard.up('ArrowRight'); r.append((thr,f)); await c.close()
            out[q]=r
        await b.close()
    srv.terminate(); print(json.dumps(out))
asyncio.run(main())
