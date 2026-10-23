import asyncio, json, collections
from playwright.async_api import async_playwright
B='https://meca12944.github.io/thor-like-game/test128/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        c=await b.new_context(viewport={'width':1600,'height':900}); pg=await c.new_page(); cdp=await c.new_cdp_session(pg)
        for q in ['?start=field00&notitle&nc=53']:
            await pg.goto(B+q,wait_until='load'); await pg.wait_for_function('window.__game&&window.__game.ready'); await pg.wait_for_timeout(4000)
            await pg.mouse.click(800,450)
            await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval',{'interval':200}); await cdp.send('Profiler.start')
            await pg.keyboard.down('ArrowRight'); await pg.wait_for_timeout(2500); await pg.keyboard.up('ArrowRight'); await pg.keyboard.down('ArrowLeft'); await pg.wait_for_timeout(2500); await pg.keyboard.up('ArrowLeft')
            prof=(await cdp.send('Profiler.stop'))['profile']
            nodes={n['id']:n for n in prof['nodes']}; cnt=collections.Counter(prof['samples']); dt=prof['endTime']-prof['startTime']
            par={}
            for n in prof['nodes']:
                for ch in n.get('children',[]): par[ch]=n['id']
            per=collections.Counter()
            def nm(i):
                n=nodes[i]['callFrame']; return (n['functionName'] or '(anon)')+' @'+n['url'].split('/')[-1].split('?')[0]+':'+str(n['lineNumber']+1)
            for nid,c_ in cnt.items():
                if nodes[nid]['callFrame']['functionName']!='drawImage': continue
                chain=[];i=par.get(nid)
                while i and len(chain)<3: chain.append(nm(i)); i=par.get(i)
                per[' <- '.join(chain)]+=c_
            tot=sum(cnt.values())
            print('==',q,'samples',tot)
            for k,v in per.most_common(16): print(f'  {100*v/tot:5.1f}%  {k[:110]}')
        await b.close()
asyncio.run(main())
