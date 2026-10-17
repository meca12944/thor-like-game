"""Headless balance check (town/BALANCE_TODO.md applied): numeric HP, combo 10/10/14, area-1 HP/dmg, roll i-frames 0.18s / cd 0.40s,
attack tokens, telegraph floors per difficulty, every damaging hazard rollable, potion cap + % heal + 4s cooldown, MP regen, difficulty menu.
Run: python3 tools/test_balance.py  (serves /workspace/town-demo on :18941 if nothing is listening)"""
import asyncio, json, socket, subprocess, sys, os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'; PORT=18941; U='http://127.0.0.1:%d/index.html'%PORT
def ensure_server():
    s=socket.socket()
    try: s.connect(('127.0.0.1',PORT)); s.close(); return None
    except OSError: return subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
async def main():
    srv=ensure_server(); await asyncio.sleep(.6); errs=[]; R={}; ok={}
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720})
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(U+'?worldreset&nosave=1'); await pg.wait_for_function('window.__game&&window.__game.ready&&window.__world&&__world.ready')
        ev=pg.evaluate
        R['town']=await ev("""()=>{const g=__game;g.setDifficulty(1);const sl=g.slimes.find(s=>!s.dead&&s.kind!=='boar');g.FEEL.critChance=0;
          const o={hp:[g.hero.hp,g.hero.maxHp],slime:sl.maxHp,boar:g.boar.maxHp,atk:g.ATK_DMG,perfect:g.FEEL.perfectTicks,ifr:g.FEEL.dashIframes,cd:g.FEEL.dashCdTicks};
          g.gauge=0;const t0=g.mp;return o}""")
        ok['town numeric HP 50 / slime 40 / boar 320 / combo 10,10,14']=R['town']['hp']==[50,50] and R['town']['slime']==40 and R['town']['boar']==320 and R['town']['atk']==[10,10,14]
        ok['town roll 11 i-frame ticks / 24 cd ticks, perfect 7']=R['town']['ifr']==11 and R['town']['cd']==24 and R['town']['perfect']==7
        R['mp']=await ev("""async()=>{const g=__game;g.gauge=0;await new Promise(r=>setTimeout(r,2000));return g.mp}""")
        ok['MP passive 0.25/s (x6 idle) — not the old 0.6+']=0.3<R['mp']<3.5
        # --- world
        await ev("()=>{__world.go('field01','west')}")
        await ev("async()=>{const W=__world;for(let i=0;i<120&&(W.trans||!W.map||W.map.id!=='field01');i++){W.advance(1/20);await new Promise(r=>setTimeout(r,5));}}")
        R['field']=await ev("""()=>{const W=__world,o={};o.scene=W.map&&W.map.id;o.hp=[W.hero.hp,W.hero.maxHp];o.roll=W.ROLL;
          o.mobs={};for(const m of W.mobs)o.mobs[m.kind]=m.maxHp;return o}""")
        exp={'mushroom':50,'rabbit':40,'wasp':50,'boar':60,'scarecrow':55,'slime':40,'squirrel':40,'sprout':60,'champ_boar':320,'champ_wasp':320}
        ok['world mob HP = BALANCE_TODO targets']=all(R['field']['mobs'].get(k,v)==v for k,v in exp.items())
        ok['world ROLL dur .22 / iframe .18 / cd .4']=R['field']['roll']['iframe']==0.18 and R['field']['roll']['cd']==0.4 and R['field']['roll']['dur']==0.22
        R['dmg']=await ev("""()=>{const W=__world,h=W.hero,o={};W.god=false;W.S.mobs.forEach(m=>m.spawnT=99);h.hp=h.maxHp;h.inv=0;h.roll=null;W.hurt(5);o.afterMob=h.hp;
          h.inv=0;h.roll={t:0.10,dx:1,dy:0};o.inIframe=W.hurt(9);h.roll={t:0.19,dx:1,dy:0};h.inv=0;o.afterIframe=W.hurt(9);h.roll=null;o.hp=h.hp;
          // golem ult damage = 52% of max HP, raw
          h.hp=h.maxHp;h.inv=0;const fake={x:h.x+200,y:h.y};const z={shape:'all',kind:'ult',dmg:Math.ceil(h.maxHp*0.52),raw:true};o.ultDmg=z.dmg;W.hurt(z.dmg,null,true);o.afterUlt=h.hp;h.hp=h.maxHp;return o}""")
        ok['mob hit 5 HP (10%)']=R['dmg']['afterMob']==45
        ok['roll i-frames block at 0.10s, not at 0.19s']=R['dmg']['inIframe'] is False and R['dmg']['afterIframe'] is True
        ok['boss 필살 52% survivable from full HP']=R['dmg']['afterUlt']==24
        # tokens: 6 slimes next to the hero -> never more than 2 melee attackers at once
        R['tok']=await ev("""()=>{const W=__world,h=W.hero;W.god=true;W.S.mobs.forEach(m=>{m.dead=true});W.S.tokens=[];
          for(let i=0;i<6;i++){const a=i/6*6.283;const s=W.spawn('slime',h.x+Math.cos(a)*40,h.y+Math.sin(a)*30);s.spawnT=0;s.t=2;}
          let mx=0,starts=0;for(let f=0;f<600;f++){W.advance(1/60);const n=W.S.mobs.filter(m=>!m.dead&&m.kind==='slime'&&(m.st==='prep'||m.st==='jump')).length;mx=Math.max(mx,n);}
          return {maxConcurrent:mx}}""")
        ok['attack tokens: <=2 melee attackers at once']=0<R['tok']['maxConcurrent']<=2
        # rollability + telegraph floors on every difficulty
        R['diff']={}
        for i,name in enumerate(['easy','normal','hard','nightmare']):
            R['diff'][name]=await ev("""(i)=>{const g=__game,W=__world;g.setDifficulty(i);const d=g.diff;W.S.hazards.length=0;W.S.mobs.forEach(m=>m.dead=true);
              const h=W.hero;const kinds=['mushroom','rabbit','wasp','boar','scarecrow','slime','squirrel','sprout','champ_boar','champ_wasp'];
              for(const k of kinds){const m=W.spawn(k,h.x+30,h.y+10);m.spawnT=0;m.t=5;m.cd=0;m.aggro=true;m.hitT=1;}
              let minLine=9,minAoe=9,maxAct=0;for(let f=0;f<900;f++){W.advance(1/60);for(const z of W.S.hazards){if(z._seen)continue;z._seen=1;
                if(z.shape==='line')minLine=Math.min(minLine,z.warn);else if(z.dmg)minAoe=Math.min(minAoe,z.warn);if(z.dmg&&!z.linger&&z.kind!=='poison')maxAct=Math.max(maxAct,z.act);}}
              return {id:d.id,minLine:+minLine.toFixed(3),minAoe:+minAoe.toFixed(3),floor:d.telegraph_floor,maxAct,iframe:+(W.ROLL.iframe+d.iframe_bonus).toFixed(3)}}""",i)
        for name,v in R['diff'].items():
            ok[f'{name}: telegraphs >= floor & roll window (i-frames - hit window) >= 0.08s']=v['minLine']>=v['floor']['charge_line']-1e-6 and v['minAoe']>=v['floor']['aoe']-1e-6 and v['maxAct']<=v['iframe']-0.08+1e-6
        await ev("()=>__game.setDifficulty(1)")
        # potions in the world: 30% heal, 4s cd
        R['pot']=await ev("""()=>{const W=__world,g=__game,h=W.hero;g.potionCd=0;g.potions=3;h.hp=20;W.tap('KeyE');W.advance(0.05);const a=h.hp;W.tap('KeyE');W.advance(0.05);const b=h.hp;W.advance(4.1);W.tap('KeyE');W.advance(0.05);return [a,b,h.hp,g.potions]}""")
        ok['world potion +15 (30%), 4s cooldown']=R['pot'][0]==35 and R['pot'][1]==35 and R['pot'][2]==50
        R['cap']=await ev("()=>{const g=__game;g.potions=0;let n=0;for(let i=0;i<9;i++)if(g.invAdd('potion',1))n++;return g.potionTotal()}")
        ok['potion cap 5 (normal)']=R['cap']==5
        await b.close()
    if srv: srv.terminate()
    print(json.dumps(R,ensure_ascii=False,indent=1))
    allok=True
    for k,v in ok.items(): print(('PASS ' if v else 'FAIL ')+k); allok&=bool(v)
    print('PASS no errors' if not errs else 'FAIL errors: '+str(errs[:3])); allok&=not errs
    sys.exit(0 if allok else 1)
asyncio.run(main())
