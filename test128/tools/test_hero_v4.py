"""test128 hero v4 in-game check: 4 dirs x idle / walk / run / dash(+afterimages) / 3-hit combo / guard / cast / hurt / death.
Console errors + bad responses -> result.json; per motion a 4-direction GIF + PNG strip in v3gen_20261018/ingame_test/.
usage: python3 test_hero_v4.py <dir served as web root containing test128/>"""
import asyncio, json, subprocess, sys, os, time, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
ROOT=sys.argv[1] if len(sys.argv)>1 else '/tmp/tlg_v4'; PORT=18962
BASE=f'http://127.0.0.1:{PORT}/test128/index.html'
OUT='/workspace/town-demo/char_v4/pixellab/hero/v3gen_20261018/ingame_test'; os.makedirs(OUT,exist_ok=True)
DIRS=['down','up','right','left']; KEY={'down':'ArrowDown','up':'ArrowUp','right':'ArrowRight','left':'ArrowLeft'}
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    R={}; errs=[]; bad=[]; G={}
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg=await b.new_page(viewport={'width':1920,'height':1080})
        pg.on('pageerror',lambda e:errs.append('pageerror: '+str(e))); pg.on('console',lambda m:errs.append('console.error: '+m.text) if m.type=='error' else None)
        pg.on('response',lambda r:bad.append(f'{r.status} {r.url}') if r.status>=400 else None)
        await pg.goto(BASE+'?nosave=1'); await pg.wait_for_function('window.__game&&window.__game.ready',timeout=90000)
        R['v4']=await pg.evaluate("()=>{const g=__game;return !!(g.H8&&g.H8.v4)&&g.H8.sheets.every((s,i)=>g.IMG['h8_'+i]&&g.IMG['h8_'+i].naturalWidth>0)}")
        SH=await pg.evaluate("()=>__game.H8.sheets.map(s=>s.split('_').pop().split('.')[0])")
        await pg.wait_for_timeout(5500)
        await pg.evaluate("()=>{const g=__game;g.setManual(true);g.slimes.forEach(m=>{m.x+=4000;m.dead=true;m.respawn=1e9;});const h=g.hero;h.x=900;h.y=560;h.vx=h.vy=0;}")
        st="""()=>{const h=__game.hero,c=__game.heroCell8();return {sheet:c?c.h8:null,key:c?c.h8+':'+c.c.join(','):null,fl:c?c.fl:null,fx:c?!!(c.fxf||c.fxb):false,atk:h.atk?h.atk.i:-1,dash:!!h.dash,gh:(h.gh||[]).length,hurt:h.hurtT>0,dead:h.deadT>0,sk:h.sk?h.sk.id:null,run:!!h.run,face:h.face,pose:h.pose?h.pose.n:null}}"""
        raf="()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))"
        async def adv(n):
            out=[]
            for _ in range(n): await pg.evaluate("()=>__game.advance(1/60)"); out.append(await pg.evaluate(st))
            return out
        async def grab():
            await pg.evaluate(raf); a=Image.open(io.BytesIO(await pg.screenshot())).convert('RGB')
            hx,hy=await pg.evaluate("()=>{const h=__game.hero,g=__game;const k=g.VIEW.logicalW/1280;let cx=0,cy=0;try{cx=camX;cy=camY}catch(e){};return [(h.x-cx)*k,(h.y-cy)*k]}")
            return a.crop((int(hx)-240,int(hy)-250,int(hx)+240,int(hy)+70))
        async def reset(d,x=900):
            await pg.evaluate(f"()=>{{const h=__game.hero;h.x={x};h.y=560;h.vx=h.vy=0;h.face='{d}';h.f8='{d}';h.cool=0;h.dashCd=0;h.atk=null;h.dash=null;h.gh=null;h.inv=0;h.hurtT=0;h.deadT=0;h.rec=null;h.castRec=null;h.pose=null;h.run=false;h.hp=Math.max(h.hp,h.maxHp)}}"); await adv(20)
        def cells(S,f=lambda x:True): return len(set(x['key'] for x in S if f(x)))
        for d in DIRS:
            k=KEY[d]; r={}; G[d]={}
            await reset(d); fr=[]; S=[]
            for i in range(16): S+=await adv(4); fr.append(await grab())
            G[d]['idle']=(fr,66); r['idle']=dict(cells=cells(S),sheets=sorted(set(SH[x['sheet']] for x in S)))
            sx={'left':1200,'right':600}.get(d,900)
            await reset(d,sx); await pg.keyboard.down(k); fr=[]; S=[]
            for i in range(20): S+=await adv(3); fr.append(await grab())
            await pg.keyboard.up(k); G[d]['walk']=(fr,50); r['walk']=dict(cells=cells(S[6:]),face=S[-1]['face'],fl=S[-1]['fl'],sheets=sorted(set(SH[x['sheet']] for x in S[6:])))
            await reset(d,sx); await pg.keyboard.down(k); await pg.keyboard.up(k); await adv(2); await pg.keyboard.down(k); fr=[]; S=[]
            for i in range(20): S+=await adv(2); fr.append(await grab())
            await pg.keyboard.up(k); G[d]['run']=(fr,33); r['run']=dict(run=any(x['run'] for x in S),cells=cells(S[6:]),sheets=sorted(set(SH[x['sheet']] for x in S[6:])))
            await reset(d,sx); await pg.keyboard.press('ShiftLeft'); fr=[]; S=[]
            for i in range(18): S+=await adv(2); fr.append(await grab())
            G[d]['dash']=(fr,66); r['dash']=dict(ticks=sum(x['dash'] for x in S),max_ghosts=max(x['gh'] for x in S),ghosts_end=S[-1]['gh'],ghost_ticks_after=sum(1 for x in S if not x['dash'] and x['gh']),cells=cells(S,lambda x:x['dash']))
            await reset(d); fr=[]; S=[]
            for t in range(72):
                if t in (0,10,26): await pg.keyboard.press('KeyJ')
                S+=await adv(1)
                if t%2==0: fr.append(await grab())
            G[d]['combo']=(fr,33); busy=[x for x in S if x['atk']>=0]
            r['combo']=dict(hits=sorted(set(x['atk'] for x in busy)),ticks=len(busy),fx=sum(x['fx'] for x in busy),cells=cells(busy))
            await reset(d); ok=await pg.evaluate("()=>__game.heroPose('guard')"); fr=[]; S=[]
            for i in range(16): S+=await adv(3); fr.append(await grab())
            G[d]['guard']=(fr,50); r['guard']=dict(ok=ok,ticks=sum(1 for x in S if x['pose']=='guard'),cells=cells(S,lambda x:x['pose']=='guard'))
            await reset(d); ok=await pg.evaluate("()=>__game.heroPose('jump')"); fr=[]; S=[]
            for i in range(14): S+=await adv(3); fr.append(await grab())
            G[d]['jump']=(fr,50); r['jump']=dict(ok=ok,cells=cells(S,lambda x:x['pose']=='jump'))
            await reset(d); await pg.evaluate("()=>{try{__game.gauge=1}catch(e){};for(const k in __game.cool)__game.cool[k]=0;__game.useSkill('fire',{slot:0})}"); fr=[]; S=[]
            for i in range(26): S+=await adv(3); fr.append(await grab())
            G[d]['cast']=(fr,50); r['cast']=dict(sk=sorted(set(x['sk'] for x in S if x['sk'])),fx=sum(x['fx'] for x in S),cells=cells(S,lambda x:x['sk']),sheets=sorted(set(SH[x['sheet']] for x in S if x['sk'] and x['sheet'] is not None)))
            await reset(d); await pg.evaluate("()=>{const g=__game,h=g.hero;h.hp=Math.max(h.hp,80);g.hurtHeroForTest(-1,0,1)}"); fr=[]; S=[]
            for i in range(14): S+=await adv(2); fr.append(await grab())
            G[d]['hurt']=(fr,50); r['hurt']=dict(ticks=sum(x['hurt'] for x in S),cells=cells(S,lambda x:x['hurt']),sheets=sorted(set(SH[x['sheet']] for x in S if x['hurt'])))
            await reset(d); await pg.evaluate("()=>{const g=__game,h=g.hero;h.inv=0;h.hp=1;g.hurtHeroForTest(-1,0,999)}"); fr=[]; S=[]
            for i in range(20): S+=await adv(6); fr.append(await grab())
            G[d]['death']=(fr,100); r['death']=dict(dead_ticks=6*sum(x['dead'] for x in S),cells=cells(S,lambda x:x['dead']),sheets=sorted(set(SH[x['sheet']] for x in S if x['dead'] and x['sheet'] is not None)))
            R[d]=r; print(d,json.dumps(r))
        await b.close()
    srv.terminate()
    R['errors']=errs[:20]; R['bad_responses']=bad[:20]
    for m in G['down']:
        n=min(len(G[d][m][0]) for d in G); W,H=G['down'][m][0][0].size; fr=[]
        for i in range(n):
            im=Image.new('RGB',(W*4,H)); dr=ImageDraw.Draw(im)
            for j,d in enumerate(DIRS): im.paste(G[d][m][0][i],(j*W,0)); dr.text((j*W+8,8),f'{m} {d}',fill='yellow')
            fr.append(im)
        fr[0].save(f'{OUT}/{m}_4dir.gif',save_all=True,append_images=fr[1:],duration=G['down'][m][1],loop=0)
        sel=fr[::max(1,n//5)][:5]; s=Image.new('RGB',(sel[0].width//2,sel[0].height*len(sel)//2))
        for i,f in enumerate(sel): s.paste(f.resize((f.width//2,f.height//2),Image.NEAREST),(0,i*f.height//2))
        s.save(f'{OUT}/{m}_4dir_strip.png')
    json.dump(R,open(f'{OUT}/result.json','w'),indent=1); print('v4',R['v4'],'errors',errs[:10],'bad',bad[:10])
asyncio.run(main())
