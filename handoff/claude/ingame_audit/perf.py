import asyncio, json, sys
from playwright.async_api import async_playwright
B='https://meca12944.github.io/thor-like-game/test128/'
FPS_JS="""()=>new Promise(res=>{const ts=[];let last=performance.now();function f(t){ts.push(t-last);last=t;if(ts.length<240)requestAnimationFrame(f);else{ts.shift();ts.sort((a,b)=>a-b);const avg=ts.reduce((a,b)=>a+b)/ts.length;res({fps:+(1000/avg).toFixed(1),p95:+ts[Math.floor(ts.length*.95)].toFixed(1),worst:+ts[ts.length-1].toFixed(1)});}}requestAnimationFrame(f);})"""
async def run(q, thr):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium',args=['--enable-gpu-rasterization','--ignore-gpu-blocklist'])
        c=await b.new_context(viewport={'width':1600,'height':900},device_scale_factor=1); pg=await c.new_page()
        cdp=await c.new_cdp_session(pg); await cdp.send('Network.enable'); await cdp.send('Network.setCacheDisabled',{'cacheDisabled':True})
        if thr>1: await cdp.send('Emulation.setCPUThrottlingRate',{'rate':thr})
        tot={'n':0,'bytes':0,'big':[]}
        def fin(e):
            tot['n']+=1; tot['bytes']+=e.get('encodedDataLength',0)
        urls={}
        cdp.on('Network.responseReceived',lambda e: urls.__setitem__(e['requestId'],e['response']['url']))
        def fin2(e):
            fin(e); u=urls.get(e['requestId'],''); 
            if e.get('encodedDataLength',0)>300000: tot['big'].append((round(e['encodedDataLength']/1e6,2),u.split('/test128/')[-1][:70]))
        cdp.on('Network.loadingFinished',fin2)
        t0=asyncio.get_event_loop().time()
        await pg.goto(B+q,wait_until='load',timeout=180000)
        await pg.wait_for_function('window.__game&&window.__game.ready',timeout=180000)
        tr=round(asyncio.get_event_loop().time()-t0,1)
        await pg.wait_for_timeout(3000)
        await pg.mouse.click(800,450)
        await pg.keyboard.down('ArrowRight')
        f=await pg.evaluate(FPS_JS)
        await pg.keyboard.up('ArrowRight')
        mem=await pg.evaluate("()=>performance.memory?Math.round(performance.memory.usedJSHeapSize/1e6):null")
        print(json.dumps({'page':q,'cpu_x':thr,'ready_s':tr,'requests':tot['n'],'MB':round(tot['bytes']/1e6,1),'fps':f,'heapMB':mem,'big':sorted(tot['big'],reverse=True)[:8]},ensure_ascii=False))
        await b.close()
async def main():
    for q in ['?notitle&nc=51','?start=field00&notitle&nc=51','?start=felt&notitle&nc=51']:
        for thr in (1,4): await run(q,thr)
asyncio.run(main())
