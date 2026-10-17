"""test128 hero8 smoke test: 8-dir walk, run, 3-hit combo, dash v2, cast, hurt + console errors + screenshots.
Run: python3 tools/test/test_hero8.py [base_url]   (default: serves /workspace/town-demo on :18951 and loads index128.html)"""
import asyncio, json, subprocess, sys, os, time
from playwright.async_api import async_playwright
D='/workspace/town-demo'; PORT=18952
BASE=sys.argv[1] if len(sys.argv)>1 else f'http://127.0.0.1:{PORT}/index128.html'
SHOT=os.environ.get('SHOTS','/workspace/town-demo/shots_hero8'); os.makedirs(SHOT,exist_ok=True)
SHEET=['walk','run','atk','dash','hurt','cast']
async def main():
    srv=None
    if len(sys.argv)<=1 and os.system(f"curl -sf -o /dev/null http://127.0.0.1:{PORT}/index128.html")!=0: srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    R={}; errs=[]; bad=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':1920,'height':1080})
        pg.on('pageerror',lambda e:errs.append('pageerror: '+str(e)))
        pg.on('console',lambda m:errs.append('console.'+m.type+': '+m.text) if m.type=='error' else None)
        pg.on('response',lambda r:bad.append(f'{r.status} {r.url}') if r.status>=400 else None)
        sep='&' if '?' in BASE else '?'
        await pg.goto(BASE+sep+'nosave=1'); await pg.wait_for_function('window.__game&&window.__game.ready',timeout=60000)
        R['h8_loaded']=await pg.evaluate("()=>{const g=__game;return !!g.H8&&g.H8.sheets.every((s,i)=>g.IMG['h8_'+i]&&g.IMG['h8_'+i].naturalWidth>0)}")
        await pg.wait_for_timeout(5500) # let the 5 s controls overlay fade
        await pg.screenshot(path=f'{SHOT}/01_idle_town.png')
        await pg.evaluate("()=>{const g=__game;g.setManual(true);window.__sl=g.slimes.map(m=>[m.x,m.y]);g.slimes.forEach(m=>{m.x+=4000;});const h=g.hero;h.x=640;h.y=470;h.face='right';h.f8='right';h.vx=h.vy=0;}")
        adv="""(n)=>{const out=[];for(let i=0;i<n;i++){__game.advance(1/60);const h=__game.hero,c=__game.heroCell8();out.push({sheet:c?c.h8:null,cell:c?c.c.join(','):null,atk:h.atk?h.atk.i:-1,dash:!!h.dash,sk:h.sk?h.sk.id:null,hurt:h.hurtT>0,run:!!h.run,x:+h.x.toFixed(1),y:+h.y.toFixed(1)});}
            const h=__game.hero;return {f8:__game.face8(),face:h.face,x:h.x,y:h.y,frames:out}}"""
        KEYS={'right':['ArrowRight'],'downright':['ArrowDown','ArrowRight'],'down':['ArrowDown'],'downleft':['ArrowDown','ArrowLeft'],
              'left':['ArrowLeft'],'upleft':['ArrowUp','ArrowLeft'],'up':['ArrowUp'],'upright':['ArrowUp','ArrowRight']}
        dirs={}
        for d,ks in KEYS.items():
            await pg.evaluate("()=>{const h=__game.hero;h.x=330;h.y=540;h.vx=h.vy=0}");await pg.wait_for_timeout(350)
            for k in ks: await pg.keyboard.down(k)
            r=await pg.evaluate(adv,40)
            for k in ks: await pg.keyboard.up(k)
            await pg.evaluate(adv,20)
            cells=len(set(f['cell'] for f in r['frames'][10:]))
            dirs[d]={'f8':r['f8'],'sheet':SHEET[r['frames'][-1]['sheet']],'distinct_walk_cells':cells,'moved':[round(r['frames'][-1]['x']-330),round(r['frames'][-1]['y']-540)]}
        R['walk_8dir']=dirs; R['walk_8dir_ok']=all(v['f8']==d and v['sheet']=='walk' and v['distinct_walk_cells']>=5 for d,v in dirs.items())
        # downright walk screenshot (mid-stride)
        await pg.evaluate("()=>{const h=__game.hero;h.x=360;h.y=500;h.vx=h.vy=0}");await pg.wait_for_timeout(350)
        await pg.keyboard.down('ArrowDown');await pg.keyboard.down('ArrowRight');await pg.evaluate(adv,17)
        await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))");await pg.screenshot(path=f'{SHOT}/02_walk_downright.png')
        await pg.keyboard.up('ArrowDown');await pg.keyboard.up('ArrowRight');await pg.evaluate(adv,20)
        # run: double tap right + hold
        await pg.evaluate("()=>{const h=__game.hero;h.x=400;h.y=470;h.vx=h.vy=0}")
        await pg.keyboard.down('ArrowRight');await pg.keyboard.up('ArrowRight');await pg.wait_for_timeout(80);await pg.keyboard.down('ArrowRight')
        r=await pg.evaluate(adv,40);await pg.keyboard.up('ArrowRight');await pg.evaluate(adv,30)
        R['run']={'run':r['frames'][-1]['run'],'sheet':SHEET[r['frames'][-1]['sheet']],'distinct_cells':len(set(f['cell'] for f in r['frames'][15:]))}
        R['run_ok']=R['run']['run'] and R['run']['sheet']=='run'
        # combo: J x3 (mashed) facing upright
        await pg.evaluate("()=>{const h=__game.hero;h.x=640;h.y=470;h.vx=h.vy=0;h.face='up';h.f8='upright';}")
        seq=[]
        for i in range(3):
            await pg.keyboard.press('KeyJ'); r=await pg.evaluate(adv,4); seq+=r['frames']
        r=await pg.evaluate(adv,50); seq+=r['frames']
        busy=[f for f in seq if f['atk']>=0]; hits=sorted(set(f['atk'] for f in busy))
        R['combo']={'hits':hits,'attack_ticks':len(busy),'sheets':sorted(set(SHEET[f['sheet']] for f in busy)),'f8':r['f8']}
        R['combo_ok']=hits==[0,1,2] and 34<=len(busy)<=38 and R['combo']['sheets']==['atk']
        # combo screenshot mid hit 3 facing downleft, with a slime in front
        await pg.evaluate("()=>{const g=__game,h=g.hero;h.x=640;h.y=470;h.face='left';h.f8='downleft';const m=g.slimes[0];m.x=575;m.y=530;}")
        await pg.keyboard.press('KeyJ');await pg.evaluate(adv,4);await pg.keyboard.press('KeyJ');await pg.evaluate(adv,4);await pg.keyboard.press('KeyJ');await pg.evaluate(adv,8)
        await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))");await pg.screenshot(path=f'{SHOT}/03_combo_hit3_downleft.png')
        await pg.evaluate(adv,40);await pg.evaluate("()=>{__game.slimes[0].x+=4000}")
        # dash v2 to the right (no input = facing), Shift
        await pg.evaluate("()=>{const h=__game.hero;h.x=500;h.y=470;h.vx=h.vy=0;h.face='right';h.f8='right';h.dashCd=0}")
        await pg.keyboard.press('ShiftLeft'); r=await pg.evaluate(adv,8)
        await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))");await pg.screenshot(path=f'{SHOT}/04_dash_right.png')
        r2=await pg.evaluate(adv,30); fr=r['frames']+r2['frames']; dt=[f for f in fr if f['dash']]
        R['dash']={'ticks':len(dt),'travel_world_px':round(dt[-1]['x']-500,1) if dt else 0,'travel_at_8_ticks':round(r['frames'][-1]['x']-500,1),'sheet':sorted(set(SHEET[f['sheet']] for f in dt))}
        R['dash_ok']=16<=len(dt)<=18 and 90<=R['dash']['travel_world_px']<=110
        # diagonal dash (hold up+left)
        await pg.evaluate("()=>{const h=__game.hero;h.x=700;h.y=520;h.vx=h.vy=0;h.dashCd=0}")
        await pg.keyboard.down('ArrowUp');await pg.keyboard.down('ArrowLeft');await pg.keyboard.press('ShiftLeft');r=await pg.evaluate(adv,20);await pg.keyboard.up('ArrowUp');await pg.keyboard.up('ArrowLeft');await pg.evaluate(adv,20)
        R['dash_diag_f8']=r['f8']
        # cast: skill key 1
        await pg.evaluate("()=>{const h=__game.hero;h.x=640;h.y=470;h.vx=h.vy=0;h.face='down';h.f8='down';}")
        await pg.keyboard.press('Digit1'); r=await pg.evaluate(adv,14)
        sk=[f for f in r['frames'] if f['sk']]
        await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))");await pg.screenshot(path=f'{SHOT}/05_cast_down.png')
        await pg.evaluate(adv,120)
        R['cast']={'skill':sk[0]['sk'] if sk else None,'sheets':sorted(set(SHEET[f['sheet']] for f in sk if f['sheet'] is not None))}
        R['cast_ok']=bool(sk) and R['cast']['sheets']==['cast']
        # hurt: real slime contact (restore slimes next to the hero) + direct hit fallback
        await pg.evaluate("()=>{const g=__game,h=g.hero;h.x=640;h.y=470;h.inv=0;h.face='right';h.f8='downright';g.slimes.forEach((m,i)=>{m.x=window.__sl[i][0];m.y=window.__sl[i][1];});}")
        got=None
        for _ in range(4):
            await pg.evaluate("()=>{const g=__game,h=g.hero,m=g.slimes.find(m=>!m.dead);if(m){m.x=h.x+30;m.y=h.y;}}")
            r=await pg.evaluate(adv,90); hu=[f for f in r['frames'] if f['hurt']]
            if hu: got=('monster',hu); break
        if not got:
            await pg.evaluate("()=>{__game.hero.inv=0;__game.hurtHeroForTest(1,0,5)}"); r=await pg.evaluate(adv,25); got=('direct',[f for f in r['frames'] if f['hurt']])
        R['hurt']={'source':got[0],'ticks':len(got[1]),'sheets':sorted(set(SHEET[f['sheet']] for f in got[1] if f['sheet'] is not None))}
        R['hurt_ok']=len(got[1])>0 and R['hurt']['sheets']==['hurt']
        await pg.evaluate(adv,40);await pg.evaluate("()=>{const g=__game,h=g.hero;g.slimes.forEach(m=>{m.x+=4000});h.x=330;h.y=560;h.face='left';h.f8='downleft';h.inv=0;h.hp=h.maxHp;g.hurtHeroForTest(1,0,1);h.hp=h.maxHp;}"); await pg.evaluate(adv,8)
        await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))");await pg.screenshot(path=f'{SHOT}/06_hurt.png')
        # back to real-time play for a few seconds (monsters + rendering) to catch runtime errors
        await pg.evaluate("()=>__game.setManual(false)")
        await pg.keyboard.down('ArrowLeft');await pg.wait_for_timeout(700);await pg.keyboard.up('ArrowLeft')
        for k in ['KeyJ','KeyJ','KeyJ','ShiftLeft','Digit1','KeyJ']: await pg.keyboard.press(k);await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{SHOT}/07_realtime.png')
        # field00: the world module draws the same hero8 frames (walk diag, combo, dash)
        await pg.evaluate("()=>{__world.go('field00','town');}"); await pg.wait_for_timeout(2500)
        await pg.evaluate("()=>__world.setManual(true)")
        wv="(n)=>{__world.advance(n/60);const h=__world.hero;return {scene:__world.scene,f8:h.f8,face:h.face,roll:!!h.roll,atk:h.atk?h.atk.i:-1}}"
        await pg.evaluate("()=>{__world.key('ArrowDown',true);__world.key('ArrowLeft',true)}"); w1=await pg.evaluate(wv,30)
        await pg.evaluate("()=>{__world.key('ArrowDown',false);__world.key('ArrowLeft',false)}"); await pg.evaluate(wv,10)
        await pg.evaluate("()=>__world.tap('ShiftLeft')"); w2=await pg.evaluate(wv,6)
        await pg.screenshot(path=f'{SHOT}/08_field_dash.png'); await pg.evaluate(wv,30)
        await pg.evaluate("()=>__world.tap('KeyJ')"); w3=await pg.evaluate(wv,8)
        await pg.screenshot(path=f'{SHOT}/09_field_attack.png'); await pg.evaluate(wv,40)
        R['field']={'walk':w1,'dash':w2,'atk':w3}
        R['field_ok']=w1['scene']!='town' and w1['f8']=='downleft' and w2['roll'] and w3['atk']==0
        await pg.evaluate("()=>__world.setManual(false)"); await pg.wait_for_timeout(1500)
        R['errors']=errs; R['http_errors']=bad
        await b.close()
    if srv: srv.terminate()
    print(json.dumps(R,ensure_ascii=False,indent=1))
    ok=all(R[k] for k in R if k.endswith('_ok')) and R['h8_loaded'] and not errs
    print('ALL OK' if ok else 'FAIL')
asyncio.run(main())
