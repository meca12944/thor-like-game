"""Milestone GIF: town gate -> 바람길 (guide line + minimap, quest giver !) -> map screen -> 시작의 숲 road -> 고대 숲 신전 entrance.
Uses the in-game route (WorldNav.path) as the autopilot.  Output: world_milestone.gif   Run: python3 tools/record_world_gif.py"""
import asyncio, os, shutil, subprocess, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(__file__))
import test_world as TW
D = TW.D; OUT = D + 'world_milestone.gif'; FR = '/tmp/wld/gif/'
async def main():
    srv = TW.ensure_server(); await asyncio.sleep(.5)
    shutil.rmtree(FR, ignore_errors=True); os.makedirs(FR)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 768, 'height': 432})
        await pg.goto(TW.U + '?worldreset')
        for i in range(150):
            if await pg.evaluate('!!(window.__game&&__game.ready&&window.__world&&__world.ready&&window.WorldNav&&WorldNav.booted)'): break
            await pg.wait_for_timeout(100)
        ev = pg.evaluate
        await ev("()=>{localStorage.removeItem('thor.world.v1');__world.reset();const h=document.getElementById('hint');if(h)h.style.display='none'}")
        await ev(TW.WALK)
        n = [0]
        async def shot(k=1):
            for _ in range(k):
                await pg.screenshot(path=FR + '%04d.png' % n[0]); n[0] += 1
        # town, at the south gate
        await ev("()=>{__game.setManual(true);const h=__game.hero;h.x=680;h.y=650;h.face='down';h.vx=h.vy=0;__game.advance(.1)}")
        await pg.wait_for_timeout(150); await shot(6)
        await ev("()=>{const h=__game.hero;h.y=700;h._px=h.x;h._py=h.y}")
        for i in range(80):   # fade out -> area card -> fade in (real time scale)
            await ev("()=>__world.advance(.1)"); await pg.wait_for_timeout(15); await shot()
            if await ev("()=>__world.scene==='map'&&!__world.trans"): break
        await ev("()=>{__world.god=true;WorldNav.setMini(0)}")
        async def follow(sec, step=12, until=None):
            for i in range(int(sec * 60 / step)):
                r = await ev("(k)=>{const W=__world,N=WorldNav,P=N.path,T=W.map.T;const ks=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'];for(let f=0;f<k;f++){if(W.trans){ks.forEach(c=>W.key(c,false));W.advance(1/60);continue;}"
                             "if(P.searching||!P.n){W.advance(1/60);continue;}const j=Math.min(P.n-1,P.i0+1),gx=(P.x[j]+.5)*T,gy=(P.y[j]+.5)*T,h=W.hero,dx=gx-h.x,dy=gy-h.y;"
                             "if(j===P.n-1&&Math.abs(dx)<3&&Math.abs(dy)<3){ks.forEach(c=>W.key(c,false));return 'arrived';}"
                             "W.key('ArrowRight',dx>2);W.key('ArrowLeft',dx<-2);W.key('ArrowDown',dy>2);W.key('ArrowUp',dy<-2);W.advance(1/60);}return W.trans?'trans':W.map.id}", step)
                await pg.wait_for_timeout(10); await shot()
                if r == 'arrived' or (until and r == until): return r
                if r == 'trans':   # let the scene load (async fetch) and play the card at 1x
                    for j in range(60):
                        await ev("()=>__world.advance(.1)"); await pg.wait_for_timeout(15); await shot()
                        if await ev("()=>!__world.trans"): break
                    if until: return 'changed'
            return 'timeout'
        await follow(6)                                         # guide line -> the quest giver (!)
        await ev("()=>{__world.hero.face='up';__world.tap('KeyL');__world.advance(.05)}"); await shot(10)
        await ev("()=>{__world.tap('KeyL');__world.advance(.6)}"); await shot(4)
        await ev("()=>{__world.tap('KeyM');__world.advance(.05)}")   # map screen: explored area, objective star, route, world inset
        for i in range(14): await ev("()=>{__world.key('ArrowRight',true);__world.advance(.1)}"); await shot()
        await ev("()=>__world.key('ArrowRight',false)"); await shot(6)
        await ev("()=>{__world.tap('KeyM');__world.advance(.05)}")
        await follow(20, until='changed')                      # road -> east exit -> 시작의 숲 (card)
        await ev("()=>{for(let i=0;i<6;i++){if((WorldNav.currentDest()||{}).kind==='dungeon')break;__world.tap('KeyG');__world.advance(.02)}__world.advance(.2)}")
        await shot(8)
        await ev("()=>{__world.tap('KeyV');__world.advance(.05)}")   # large minimap for a moment
        await follow(2.5)
        await ev("()=>{__world.tap('KeyV');__world.advance(.02);__world.tap('KeyV');__world.advance(.02)}")  # (large -> off -> small)
        await follow(30, until='changed')                      # -> 고대 숲 신전 entrance -> B1 card
        await shot(6)
        await b.close()
    if srv: srv.terminate()
    pal = '/tmp/wld/gif_pal.png'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', FR + '%04d.png', '-vf', 'scale=640:-1:flags=lanczos,palettegen=max_colors=160:stats_mode=diff', pal], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', FR + '%04d.png', '-i', pal, '-lavfi', 'scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle', OUT], check=True)
    print('frames', n[0], OUT, os.path.getsize(OUT) // 1024, 'KB')
asyncio.run(main())
