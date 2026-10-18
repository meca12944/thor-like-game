"""test128 hero v3 smoke test: 4 dirs x (walk, run, 3-hit combo, dash, cast S1-S3, hurt) + console errors + screenshots."""
import asyncio, json, subprocess, sys, os, time
from playwright.async_api import async_playwright
D='/workspace/town-demo'; PORT=18953
BASE=sys.argv[1] if len(sys.argv)>1 else f'http://127.0.0.1:{PORT}/index128.html'
SHOT='/workspace/review/test128_v3'; os.makedirs(SHOT,exist_ok=True)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL) if len(sys.argv)<=1 else None; time.sleep(1)
    R={}; errs=[]; bad=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg=await b.new_page(viewport={'width':1920,'height':1080})
        pg.on('pageerror',lambda e:errs.append('pageerror: '+str(e))); pg.on('console',lambda m:errs.append('console.error: '+m.text) if m.type=='error' else None)
        pg.on('response',lambda r:bad.append(f'{r.status} {r.url}') if r.status>=400 else None)
        await pg.goto(BASE+('&' if '?' in BASE else '?')+'nosave=1'); await pg.wait_for_function('window.__game&&window.__game.ready',timeout=90000)
        R['v3']=await pg.evaluate("()=>{const g=__game;return !!(g.H8&&g.H8.v3)&&g.H8.sheets.every((s,i)=>g.IMG['h8_'+i]&&g.IMG['h8_'+i].naturalWidth>0)}")
        await pg.wait_for_timeout(5500)
        await pg.evaluate("()=>{const g=__game;g.setManual(true);g.slimes.forEach(m=>{m.x+=4000;m.dead=true;m.respawn=1e9;});const h=g.hero;h.x=900;h.y=560;h.vx=h.vy=0;}")
        adv="""(n)=>{const out=[];for(let i=0;i<n;i++){__game.advance(1/60);const h=__game.hero,c=__game.heroCell8();out.push({sheet:c?c.h8:null,cell:c?c.c.join(','):null,fx:c?!!(c.fxf||c.fxb):false,atk:h.atk?h.atk.i:-1,dash:!!h.dash,sk:h.sk?h.sk.id:null,hurt:h.hurtT>0,run:!!h.run,face:h.face});}return out}"""
        SH=await pg.evaluate("()=>__game.H8.sheets.map(s=>s.split('_').pop().split('.')[0])")
        raf="()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))"
        from PIL import Image, ImageChops
        import io
        async def shot(name):
            await pg.evaluate(raf); a=Image.open(io.BytesIO(await pg.screenshot())).convert('RGB')
            hx,hy=await pg.evaluate("()=>{const h=__game.hero,g=__game;const k=g.VIEW.logicalW/1280;let cx=0,cy=0;try{cx=camX;cy=camY}catch(e){};return [(h.x-cx)*k,(h.y-cy)*k]}")
            a.crop((int(hx)-280,int(hy)-330,int(hx)+280,int(hy)+130)).save(f'{SHOT}/{name}.png')
        KEY={'right':'ArrowRight','left':'ArrowLeft','down':'ArrowDown','up':'ArrowUp'}
        for d,k in KEY.items():
            r={}
            await pg.evaluate("()=>{const h=__game.hero;h.x=900;h.y=560;h.vx=h.vy=0}")
            await pg.keyboard.down(k); f=await pg.evaluate(adv,30); await shot(f'{d}_1_walk'); await pg.keyboard.up(k); await pg.evaluate(adv,20)
            r['walk']=dict(sheets=sorted(set(SH[x['sheet']] for x in f[5:] if x['sheet'] is not None)),cells=len(set(x['cell'] for x in f[5:])),face=f[-1]['face'])
            await pg.evaluate("()=>{const h=__game.hero;h.x=900;h.y=560;h.vx=h.vy=0}")
            await pg.keyboard.down(k);await pg.keyboard.up(k);await pg.wait_for_timeout(60);await pg.keyboard.down(k); f=await pg.evaluate(adv,30); await shot(f'{d}_2_run'); await pg.keyboard.up(k); await pg.evaluate(adv,40)
            r['run']=dict(run=any(x['run'] for x in f),sheets=sorted(set(SH[x['sheet']] for x in f[10:] if x['sheet'] is not None)))
            await pg.evaluate(f"()=>{{const h=__game.hero;h.x=900;h.y=560;h.vx=h.vy=0;h.face='{d}';h.f8='{d}';h.cool=0}}")
            seq=[]; shots={}
            for t in range(110):
                if t in (0,12,32): await pg.keyboard.press('KeyJ')
                seq+=await pg.evaluate(adv,1)
                a=seq[-1]['atk']
                if a>=0 and a not in shots and len([x for x in seq if x['atk']==a])==(7 if a==0 else 9 if a==1 else 14): shots[a]=1; await shot(f'{d}_3_hit{a+1}')
            busy=[x for x in seq if x['atk']>=0]
            r['combo']=dict(hits=sorted(set(x['atk'] for x in busy)),ticks=len(busy),fx_frames=sum(x['fx'] for x in busy),sheets=sorted(set(SH[x['sheet']] for x in busy)))
            await pg.evaluate(f"()=>{{const h=__game.hero;h.x=900;h.y=560;h.vx=h.vy=0;h.face='{d}';h.f8='{d}';h.dashCd=0}}")
            await pg.keyboard.press('ShiftLeft'); f=await pg.evaluate(adv,6); await shot(f'{d}_4_dash'); f+=await pg.evaluate(adv,30)
            r['dash']=dict(ticks=sum(x['dash'] for x in f),sheets=sorted(set(SH[x['sheet']] for x in f if x['dash'])))
            r['cast']={}
            for s in (1,2,3):
                await pg.evaluate(f"()=>{{const h=__game.hero;h.x=900;h.y=560;h.vx=h.vy=0;h.face='{d}';h.f8='{d}';try{{__game.gauge=1}}catch(e){{}};for(const k in __game.cool)__game.cool[k]=0;}}")
                await pg.evaluate(f"()=>__game.useSkill('fire',{{slot:{s-1}}})"); f=await pg.evaluate(adv,24); await shot(f'{d}_5_cast{s}'); f+=await pg.evaluate(adv,150)
                r['cast'][s]=dict(variant=await pg.evaluate('()=>__game.hero.lastSlot'),sk=sorted(set(x['sk'] for x in f if x['sk'])),fx=sum(x['fx'] for x in f),sheets=sorted(set(SH[x['sheet']] for x in f if x['sk'] and x['sheet'] is not None)))
            await pg.evaluate(f"()=>{{const g=__game,h=g.hero;h.x=900;h.y=560;h.vx=h.vy=0;h.face='{d}';h.f8='{d}';h.inv=0;h.deadT=0;h.hp=Math.max(h.hp,80);g.hurtHero(-1,0,1)}}")
            f=await pg.evaluate(adv,5); await shot(f'{d}_6_hurt'); f+=await pg.evaluate(adv,40)
            r['hurt']=dict(ticks=sum(x['hurt'] for x in f),sheets=sorted(set(SH[x['sheet']] for x in f if x['hurt'])))
            R[d]=r; print(d,json.dumps(r,ensure_ascii=False))
        await b.close()
    if srv: srv.terminate()
    R['errors']=errs[:20]; R['bad_responses']=bad[:20]
    json.dump(R,open(f'{SHOT}/result.json','w'),ensure_ascii=False,indent=1); print('v3',R['v3'],'errors',errs[:10],'bad',bad[:10])
asyncio.run(main())
