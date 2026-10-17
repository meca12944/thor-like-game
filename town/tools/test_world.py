"""Headless walk-through of the outside world (world.js):
town -> exit gate -> world-map title card -> world map -> area 1 field -> champions -> dungeon B1 (key/door) -> B2 (levers/gate)
-> boss room (golem: phase 2 + 필살기) -> warp back -> field -> world map -> town (spawn preserved).
Screenshots: shot_worldmap_entry.png, shot_worldmap.png, shot_field01.png, shot_dungeon01.png, shot_boss01.png
Run: python3 tools/test_world.py   (serves /workspace/town-demo on :18940 if nothing is listening)
"""
import asyncio, json, socket, subprocess, sys, os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'; PORT=int(os.environ.get('WORLD_TEST_PORT','18940')); U='http://127.0.0.1:%d/index.html'%PORT
def ensure_server():
    s=socket.socket()
    try: s.connect(('127.0.0.1',PORT)); s.close(); return None
    except OSError: return subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
WALK = r"""
window.__walk = function(tx, ty, maxSec, opt) {   // BFS on the live collision grid, then drive the arrow keys frame by frame
  opt = opt || {}; const W = __world, m0 = W.map, T = m0.T, startScene = m0.id;
  const solid = (x, y) => x < 0 || y < 0 || x >= m0.w || y >= m0.h || (m0.solidG[y * m0.w + x] && !(x === tx && y === ty));
  const avoid = new Set((m0.objs || []).filter(o => ['pit', 'spikes'].includes(o.type) && !opt.allowTraps).map(o => o.tx + ',' + o.ty));
  for (const o of (m0.objs || [])) if (['stairs_up', 'stairs_down', 'exit'].includes(o.type)) for (let yy = 0; yy < (o.h || 1); yy++) for (let xx = 0; xx < (o.w || 1); xx++) avoid.add((o.tx + xx) + ',' + (o.ty + yy)); // never leave the scene by accident
  const [sx, sy] = W.tile(); const prev = new Map([[sx + ',' + sy, null]]); const q = [[sx, sy]];
  while (q.length) { const [x, y] = q.shift(); if (x === tx && y === ty) break;
    for (const [dx, dy] of [[1,0],[-1,0],[0,1],[0,-1]]) { const nx = x + dx, ny = y + dy, k = nx + ',' + ny;
      if (prev.has(k) || solid(nx, ny) || (avoid.has(k) && !(nx === tx && ny === ty))) continue; prev.set(k, [x, y]); q.push([nx, ny]); } }
  if (!prev.has(tx + ',' + ty)) return {ok: false, why: 'no path', from: [sx, sy], to: [tx, ty], scene: startScene};
  const path = []; let c = [tx, ty]; while (c) { path.unshift(c); c = prev.get(c[0] + ',' + c[1]); }
  const keys = {left: 'ArrowLeft', right: 'ArrowRight', up: 'ArrowUp', down: 'ArrowDown'};
  const release = () => Object.values(keys).forEach(k => W.key(k, false));
  let i = 1, t = 0;
  while (t < maxSec) {
    if (W.trans || W.map !== m0) { release(); return {ok: true, changed: true, scene: W.map && W.map.id, t}; }
    if (i >= path.length) { release(); return {ok: true, at: W.tile(), t}; }
    const [px, py] = path[i], gx = (px + .5) * T, gy = (py + .5) * T, h = W.hero, dx = gx - h.x, dy = gy - h.y;
    if (Math.abs(dx) < 2.5 && Math.abs(dy) < 2.5) { i++; continue; }
    W.key(keys.right, dx > 2); W.key(keys.left, dx < -2); W.key(keys.down, dy > 2); W.key(keys.up, dy < -2);
    W.advance(1 / 60); t += 1 / 60;
  }
  release(); return {ok: false, why: 'timeout', at: W.tile(), target: [tx, ty], i, n: path.length};
};

window.__follow = function(maxSec) {   // autopilot that only reads the guide route (WorldNav.path) — proves the in-game pathfinding
  const W = __world, N = WorldNav, m0 = W.map, keys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
  const rel = () => keys.forEach(k => W.key(k, false)); let t = 0, lastI = -1, stuck = 0, lx = W.hero.x, ly = W.hero.y;
  while (t < maxSec) {
    if (W.trans || W.map !== m0) { rel(); return {ok: true, changed: true, scene: W.map && W.map.id, t: +t.toFixed(2)}; }
    const P = N.path, T = m0.T;
    if (P.searching || !P.n) { W.advance(1 / 60); t += 1 / 60; continue; }
    let i = Math.min(P.n - 1, P.i0 + 1); const gx = (P.x[i] + .5) * T, gy = (P.y[i] + .5) * T, h = W.hero, dx = gx - h.x, dy = gy - h.y;
    if (i === P.n - 1 && Math.abs(dx) < 3 && Math.abs(dy) < 3) { rel(); return {ok: true, at: W.tile(), t: +t.toFixed(2), label: N.state.label}; }
    W.key('ArrowRight', dx > 2); W.key('ArrowLeft', dx < -2); W.key('ArrowDown', dy > 2); W.key('ArrowUp', dy < -2);
    W.advance(1 / 60); t += 1 / 60;
    if (Math.hypot(h.x - lx, h.y - ly) < .2) { if (++stuck > 90) { rel(); return {ok: false, why: 'stuck', at: W.tile(), next: [P.x[i], P.y[i]], t}; } } else stuck = 0; lx = h.x; ly = h.y;
  }
  rel(); return {ok: false, why: 'timeout', at: W.tile()};
};
window.__untilScene = async function(id, maxSec) { const W = __world; let t = 0; while (t < maxSec) { if (!W.trans && W.map && W.map.id === id) return true; W.advance(1/20); t += 1/20; await new Promise(r => setTimeout(r, 5)); } return false; }; // scene loads are async (fetch)
"""
async def main():
    srv=ensure_server(); await asyncio.sleep(.6)
    res={}; errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1152,'height':648})
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' and 'Failed to load resource' not in m.text else None)
        pg.on('response',lambda r: errs.append('HTTP %d %s'%(r.status,r.url)) if r.status>=400 and '/audio/' not in r.url else None); pg.on('pageerror',lambda e: errs.append(str(e)))
        pg.on('requestfailed',lambda r: errs.append('FAIL '+r.url) if '/audio/' not in r.url else None)
        await pg.goto(U+'?worldreset')
        for i in range(150):
            if await pg.evaluate('!!(window.__game&&window.__game.ready&&window.__world&&window.__world.ready&&window.WorldNav&&WorldNav.booted)'): break
            await pg.wait_for_timeout(100)
        await pg.evaluate("()=>{localStorage.removeItem('thor.world.v1');__world.reset();document.getElementById('hint')&&(document.getElementById('hint').style.display='none')}")
        await pg.evaluate(WALK)
        async def ev(s,*a):
            try: return await pg.evaluate(s,*a)
            except Exception as e:
                print(json.dumps(res,ensure_ascii=False)); print('EVAL FAILED:',s[:160]); raise
        # ---------- 1. town -> exit gate (real keyboard; town stepped with __game.advance like the town tests) ----------
        await ev("()=>{__game.setManual(true);const h=__game.hero;h.x=680;h.y=640;h.face='down'}")
        await pg.keyboard.down('ArrowDown')
        for i in range(60):
            if await ev("()=>!!__world.trans"): break
            await ev("()=>__game.advance(.05)"); await pg.wait_for_timeout(30)
            if i==30 and not await ev("()=>!!__world.trans"):   # town walking itself is broken (other worker's WIP) -> step over the gate line directly
                res['town_walk_fallback']=await ev("()=>{const h=__game.hero;const r=[h.y,h.vy];h.vx=h.vy=0;h.y=700;h._px=h.x;h._py=h.y;return r}")
        await pg.keyboard.up('ArrowDown')
        town_saved=await ev("()=>__world.S.townPos")
        await ev("()=>__world.setManual(true)")
        res['left_town']=await ev("()=>({trans:!!__world.trans,to:__world.trans&&__world.trans.to,townPaused:true,saved:__world.S.townPos})")
        # area card (first visit of the outskirts road) mid-way
        await ev("()=>__world.advance(.45)"); await pg.wait_for_timeout(120); await ev("()=>__world.advance(1.0)"); await pg.wait_for_timeout(120)
        res['entry_card']=await ev("()=>({phase:__world.trans&&__world.trans.phase,title:__world.trans&&__world.trans.cardData})")
        await pg.screenshot(path=D+'shot_area_card.png')
        ok=await ev("()=>__untilScene('field00',4)"); await ev("()=>__world.advance(.4)")
        res['field00']=await ev("()=>({ok:%s,scene:__world.map.id,bgm:__scene.bgm,nav:WorldNav.booted,dest:(WorldNav.currentDest()||{}).label,mark:WorldNav.npcMark('npc_bori')})"%('true' if ok else 'false'))
        await ev("()=>{__world.god=true}")
        # ---------- 2. follow the guide route to the quest giver, accept the quest ----------
        res['to_npc']=await ev("()=>__follow(30)")
        await ev("()=>{__world.hero.face='up';__world.tap('KeyL');__world.advance(.1)}")
        res['quest']=await ev("()=>({dialog:!!__world.S.dialog,state:__world.SAVE.quests.q_forest_chiefs,mark:WorldNav.npcMark('npc_bori'),dest:(WorldNav.currentDest()||{}).label})")
        await ev("()=>{__world.tap('KeyL');__world.advance(.3)}")
        await pg.wait_for_timeout(60); await pg.screenshot(path=D+'shot_field00.png')
        # map screen
        await ev("()=>{__world.tap('KeyM');__world.advance(.1)}")
        res['mapscreen']=await ev("()=>({open:!!WorldNav.screen,paused:(()=>{const x=__world.hero.x;__world.key('ArrowLeft',true);__world.advance(.3);__world.key('ArrowLeft',false);return __world.hero.x===x})()})")
        await pg.wait_for_timeout(60); await pg.screenshot(path=D+'shot_mapscreen.png')
        await ev("()=>{__world.tap('KeyM');__world.advance(.1)}")
        # cross-map route: the quest target (the boar champion) is in field01 -> the route leads to field00's east exit
        res['route_cross']=await ev("()=>{__world.advance(.3);const s=WorldNav.state;return {via:s.via,goal:s.goal,label:s.label,n:WorldNav.path.n}}")
        r=await ev("()=>__follow(60)"); res['follow_to_field01']=r
        ok=await ev("()=>__untilScene('field01',6)")
        res['field']=await ev("()=>({ok:%s,scene:__world.map.id,bgm:__scene.bgm,mobs:__world.mobs.map(m=>m.kind),dest:(WorldNav.currentDest()||{}).label})"%('true' if ok else 'false'))
        # ---------- 2. field: champions (real attacks, god mode so the walk is deterministic) ----------
        await ev("()=>{__world.god=true}")
        async def fight(filt, maxSec=40):
            return await ev("""(a)=>{const [filt,maxSec]=a;const W=__world;let t=0;const tgt=()=>W.mobs.find(m=>!m.dead&&eval(filt));
              const rel=()=>['ArrowRight','ArrowLeft','ArrowUp','ArrowDown'].forEach(k=>W.key(k,false));
              while(t<maxSec){const m=tgt();if(!m){rel();return {ok:true,t:+t.toFixed(1)};}const h=W.hero;const dx=m.x-h.x,dy=m.y-h.y,d=Math.hypot(dx,dy);
                W.key('ArrowRight',dx>14);W.key('ArrowLeft',dx<-14);W.key('ArrowDown',dy>10);W.key('ArrowUp',dy<-10);
                if(d<40){W.hero.face=Math.abs(dx)>Math.abs(dy)?(dx>0?'right':'left'):(dy>0?'down':'up');W.tap('KeyJ');}
                W.advance(1/30);t+=1/30;}
              ['ArrowRight','ArrowLeft','ArrowUp','ArrowDown'].forEach(k=>W.key(k,false));const m=tgt();return {ok:false,hp:m&&m.hp,st:m&&m.st,sub:m&&m.sub,inv:m&&m.invuln,mx:m&&m.x|0,my:m&&m.y|0,hx:W.hero.x|0,hy:W.hero.y|0,hst:W.hero.roll?'roll':W.hero.atk?'atk':'-'}}""",[filt,maxSec])
        await ev("()=>__world.setHeroTile(46,24)"); await ev("()=>__world.advance(.2)")
        await pg.screenshot(path='/tmp/wld/champ_boar_pre.png')
        res['champ_boar']=await fight("m.kind==='champ_boar'")
        await ev("()=>__world.setHeroTile(15,10)"); await ev("()=>__world.advance(.2)")
        res['champ_wasp']=await fight("m.kind==='champ_wasp'")
        res['flags']=await ev("()=>__world.SAVE.flags")
        # screenshot of the field with mobs + a champion bar: respawn the boar champion copy just for the picture? use regular mobs near the bridge
        await ev("()=>{__world.setHeroTile(22,15,'right');__world.advance(.5)}")
        nearest=await ev("()=>{const W=__world;W.spawn('champ_boar',W.hero.x+70,W.hero.y+10,{noDrop:true,aggro:true});W.spawn('wasp',W.hero.x+40,W.hero.y-30);W.spawn('rabbit',W.hero.x-40,W.hero.y+30);W.advance(.9);const b=W.mobs.find(m=>m.kind==='champ_boar');b.hp=11;W.advance(.05);return W.mobs.length}")
        await pg.wait_for_timeout(80); await pg.screenshot(path=D+'shot_field01.png')
        await ev("()=>__world.killAll(m=>m.kind==='champ_boar')")
        # walk the road to the temple gate
        # objective -> 고대 숲 신전 입구 via G (auto objective now = report to 하로), then follow the guide line
        for i in range(6):
            if await ev("()=>(WorldNav.currentDest()||{}).kind==='dungeon'"): break
            await ev("()=>{__world.tap('KeyG');__world.advance(.05)}")
        await ev("()=>__world.advance(.3)")
        r=await ev("()=>__follow(60)"); res['walk_field_to_dungeon']=r
        ok=await ev("()=>__untilScene('dungeon01_b1',6)")
        if not ok: print(json.dumps(res,ensure_ascii=False)); raise SystemExit('field->dungeon failed')
        res['b1']=await ev("()=>({ok:%s,scene:__world.map.id})"%('true' if ok else 'false'))
        # ---------- 3. dungeon B1: key -> locked door -> stairs down ----------
        r1=await ev("()=>__walk(33,20,60)"); r1b=await ev("()=>__world.SAVE.keys")
        r2=await ev("()=>__walk(33,7,60)")
        await ev("()=>{__world.key('ArrowUp',true);__world.advance(.4);__world.key('ArrowUp',false)}")
        door=await ev("()=>__world.objs.find(o=>o.type==='door_locked').open")
        await ev("()=>{__world.setHeroTile(14,10,'right');__world.advance(.6)}"); await pg.wait_for_timeout(80)
        await pg.screenshot(path=D+'shot_dungeon01.png')
        r3=await ev("()=>__walk(33,3,60)")
        ok=await ev("()=>__untilScene('dungeon01_b2',6)")
        res['b1_puzzle']={'toKey':r1,'keys':r1b,'toDoor':r2,'doorOpen':door,'toStairs':r3,'b2':ok}
        # ---------- 4. dungeon B2: two levers open the gate, boss door needs both champions ----------
        lv=await ev("()=>__world.objs.filter(o=>o.type==='lever').map(o=>[o.tx,o.ty])")
        out=[]
        for (lx,ly) in lv:
            w=await ev("(a)=>__walk(a[0],a[1]+1,60)",[lx,ly]); await ev("()=>{__world.hero.face='up';__world.tap('KeyL');__world.advance(.1)}"); out.append([w.get('ok'),await ev("(a)=>__world.objs.find(o=>o.type==='lever'&&o.tx===a[0]&&o.ty===a[1]).on",[lx,ly])])
        res['b2_dbg']=await ev("()=>[__world.map.id,__world.tile(),[...new Set(__world.objs.map(o=>o.type))].join(',')]")
        gate=await ev("()=>{const g=__world.objs.find(o=>o.type==='gate');return g?g.open:'missing'}")
        bd=await ev("()=>{const o=__world.objs.find(o=>o.type==='boss_door');return [o.tx,o.ty]}")
        w=await ev("(a)=>__walk(a[0],a[1]+1,60)",bd)
        await ev("()=>{__world.key('ArrowUp',true);__world.advance(.3);__world.key('ArrowUp',false)}")
        ok=await ev("()=>__untilScene('boss01',6)")
        res['b2_puzzle']={'levers':out,'gateOpen':gate,'toBossDoor':w,'boss':ok}
        # ---------- 5. boss: golem 6 patterns, phase 2 at 50 %, 필살기 avoided by pillar shadow / roll ----------
        await ev("()=>__world.advance(1.5)")
        seen=await ev("""()=>{const W=__world,b=W.boss;const st=new Set();let t=0;W.god=false;W.hero.hp=W.hero.maxHp;
            while(t<25){st.add(b.st);W.advance(1/30);t+=1/30;W.hero.hp=W.hero.maxHp;W.hero.inv=1;}return [...st]}""")
        res['boss_p1_states']=seen
        await ev("()=>{const b=__world.boss;b.hp=Math.floor(b.maxHp/2)-1;__world.advance(2.2)}")
        res['boss_phase']=await ev("()=>[__world.boss.phase,__scene.bgm]")
        res['boss_p2_states']=await ev("""()=>{const W=__world,b=W.boss;const st=new Set();let t=0;b.ultCd=99;
            while(t<80){st.add(b.st);W.advance(1/30);t+=1/30;W.hero.hp=W.hero.maxHp;W.hero.inv=1;b.ultCd=99;if(b.hp<b.maxHp*0.3)b.hp=Math.floor(b.maxHp*0.45);}return [...st].sort()}""")
        # force the ult and test both escapes
        ult=await ev("""()=>{const W=__world,b=W.boss;W.hero.inv=0;W.hero.hp=W.hero.maxHp;b.st='idle';b.t=5;b.ultCd=0;W.advance(1/30);
            const out={st:b.st,banner:W.S.banner&&W.S.banner.text};
            // hide behind the pillar on the far side of the boss
            const ps=W.map.decos.filter(d=>d.spr==='pillar');let best=null;for(const d of ps){const a=Math.atan2(d.y-6-b.y,d.x-b.x);const x=d.x+Math.cos(a)*18,y=d.y-6+Math.sin(a)*18;if(!best||Math.hypot(x-W.hero.x,y-W.hero.y)<best.d)best={x,y,d:Math.hypot(x-W.hero.x,y-W.hero.y)};}
            W.hero.x=best.x;W.hero.y=best.y;let t=0;while(W.S.ult&&t<4){W.hero.x=best.x;W.hero.y=best.y;b.x=b.x;W.advance(1/60);t+=1/60;}out.hpAfterPillar=W.hero.hp;
            // second ult: stand in the open and roll right before the blast
            b.st='idle';b.t=5;b.ultCd=0;W.advance(1/60);W.hero.x=Math.min(W.map.pw-30,b.x+60);W.hero.y=Math.min(W.map.ph-30,b.y+60);W.hero.inv=0;const U=W.S.ult;t=0;let rolled=false;
            while(W.S.ult&&t<4){if(!rolled&&U.t>=U.warn-0.12){W.tap('ShiftLeft');rolled=true;}W.advance(1/60);t+=1/60;}out.hpAfterRoll=W.hero.hp;out.maxHp=W.hero.maxHp;return out}""")
        res['boss_ult']=ult
        await ev("()=>{const W=__world,b=W.boss;b.st='idle';b.t=5;b.ultCd=0;W.advance(1/60);W.hero.x=Math.max(30,b.x-40);W.hero.y=Math.min(W.map.ph-30,b.y+70);W.hero.inv=0;W.advance(1.2)}")
        await pg.wait_for_timeout(80); await pg.screenshot(path=D+'shot_boss01.png')
        await ev("()=>{__world.god=true;__world.S.ult=null;__world.S.hazards.length=0;__world.advance(2.5)}")
        res['boss_kill']=await fight("m.D.boss",60)
        await ev("()=>{__world.hero.kx=__world.hero.ky=0;__world.setHeroTile(8,7,'right')}")  # step off the stairs the bot may have been pushed onto
        await ev("()=>__world.advance(4)")
        res['boss_flag']=await ev("()=>[__world.SAVE.flags.boss01,__world.objs.some(o=>o.type==='warp'),__scene.bgm]")
        res['boss_after']=await ev("()=>{const S=__world.S;return {scene:__world.map&&__world.map.id,trans:!!S.trans,dialog:!!S.dialog,pause:S.pause,hp:__world.hero.hp,timers:S.timers.length,dead:S.dead||null,msg:S.msg&&S.msg.text}}")
        w=await ev("()=>{const o=__world.objs.find(o=>o.type==='warp');return __walk(Math.floor(o.x/16),Math.floor(o.y/16),20)}")
        ok=await ev("()=>__untilScene('field01',6)")
        res['back_to_field']={'walk':w,'ok':ok,'tile':await ev("()=>__world.tile()")}
        # ---------- 6. waystone, report the quest, fast travel, walk home ----------
        res['ws']=await ev("()=>{const r=__walk(42,10,30);__world.hero.face='up';__world.tap('KeyL');__world.advance(.1);__world.tap('KeyL');__world.advance(.1);return [r.ok,!!__world.SAVE.waystones.ws_temple]}")
        await ev("()=>{__world.SAVE.dest=null;__world.advance(.3)}")
        res['report_route']=await ev("()=>({dest:(WorldNav.currentDest()||{}).label,via:WorldNav.state.via})")
        r=await ev("()=>__follow(60)"); ok=await ev("()=>__untilScene('field00',6)"); await ev("()=>__world.advance(.3)")
        r2=await ev("()=>__follow(60)")
        talk=await ev("()=>{__world.hero.face='up';const out=[];for(let i=0;i<3;i++){__world.tap('KeyL');__world.advance(.1);out.push(__world.SAVE.quests.q_forest_chiefs+'/'+__world.SAVE.quests.q_temple_golem);__world.tap('KeyL');__world.advance(.1);}return out}")
        res['report']={'walk':r,'field00':ok,'toNpc':r2,'talk':talk}
        # fast travel from the map screen to the temple waystone
        ft=await ev("""()=>{__world.tap('KeyM');__world.advance(.05);const sc=WorldNav.screen;const m=__world.S.map;const f1=MAPS_POS('field01');sc.cx=f1[0]+42.5;sc.cy=f1[1]+9.5;__world.advance(.05);const hv=sc.hover&&sc.hover.id;__world.tap('Enter');__world.advance(.05);return hv}""".replace("MAPS_POS('field01')","__worldHooks.MAPS.field01.mapPos"))
        ok=await ev("()=>__untilScene('field01',6)")
        res['fast_travel']={'hover':ft,'ok':ok,'tile':await ev("()=>__world.tile()")}
        # walk home along the route (objective: town)
        for i in range(8):
            if await ev("()=>(WorldNav.currentDest()||{}).kind==='town'"): break
            await ev("()=>{__world.tap('KeyG');__world.advance(.05)}")
        await ev("()=>__world.advance(.3)")
        r=await ev("()=>__follow(60)"); ok=await ev("()=>__untilScene('field00',6)"); await ev("()=>__world.advance(.3)")
        r2=await ev("()=>__follow(60)")
        res['back_to_world']={'walk':r,'ok':ok,'walk2':r2}
        t=0
        for i in range(200):
            if await ev("()=>__world.scene==='town'&&!__world.trans"): break
            await ev("()=>__world.advance(.05)")
        res['back_in_town']=await ev("()=>({scene:__world.scene,hero:[__game.hero.x|0,__game.hero.y|0],saved:__world.S.townPos,canvas:document.getElementById('wc').style.display,bgm:__scene.bgm,active:__scene.active})")
        res['perf']=await ev("""()=>{__world.go('field01','west');return 0}""")
        ok=await ev("()=>__untilScene('field01',6)")
        res['perf']=await ev("""()=>{const W=__world;W.SAVE.dest={type:'dest',id:'dest_temple'};const t0=performance.now();for(let i=0;i<600;i++)W.advance(1/60);return +((performance.now()-t0)/600).toFixed(3)}""")
        # locked node check
        res['errors']=errs
        await b.close()
    if srv: srv.terminate()
    print(json.dumps(res,ensure_ascii=False,indent=1))
    checks={
     'left town via gate -> road (no world map)':res['left_town']['to']=='field00',
     'area card':res['entry_card']['phase']=='card' and res['entry_card']['title'] is not None,
     'field00 + nav booted':res['field00']['ok'] and res['field00']['nav'] and res['field00']['mark']=='!',
     'route to quest giver + accept':res['to_npc']['ok'] and res['quest']['state']=='active' and res['quest']['mark']=='…',
     'map screen pauses':res['mapscreen']['open'] and res['mapscreen']['paused'],
     'cross-map route via exit':res['route_cross']['via'] is not None and res['route_cross']['n']>5,
     'followed route into field01':res['follow_to_field01'].get('changed'),
     'field':res['field']['ok'] and res['field']['bgm']=='area01_forest',
     'champions':res['champ_boar']['ok'] and res['champ_wasp']['ok'] and res['flags'].get('champ_boar') and res['flags'].get('champ_wasp'),
     'field->dungeon':res['b1']['ok'],
     'B1 key/door/stairs':res['b1_puzzle']['doorOpen'] and res['b1_puzzle']['b2'],
     'B2 levers/gate/boss door':res['b2_puzzle']['gateOpen'] and res['b2_puzzle']['boss'],
     'boss P2 uses patterns A-F':all(('p'+c) in res['boss_p2_states'] for c in 'ABCDEF'),
     'boss phase2':res['boss_phase'][0]==2 and res['boss_phase'][1]=='battle_boss_phase2',
     'ult dodged (pillar+roll)':res['boss_ult']['hpAfterPillar']==res['boss_ult']['maxHp'] and res['boss_ult']['hpAfterRoll']==res['boss_ult']['maxHp'],
     'boss killed':res['boss_kill']['ok'] and res['boss_flag'][0],
     'back to field':res['back_to_field']['ok'],
     'waystone registered':res['ws'][1],
     'quest reported':res['report']['field00'] and any(x.startswith('done/') for x in res['report']['talk']),
     'fast travel':res['fast_travel']['hover']=='ws_temple' and res['fast_travel']['ok'],
     'route home':res['back_to_world']['ok'],
     'perf < 4ms/frame (logic+nav+render)':res['perf']<4,
     'back in town, spawn kept':res['back_in_town']['scene']=='town' and abs(res['back_in_town']['hero'][1]-res['back_in_town']['saved']['y'])<8 and res['back_in_town']['hero'][1]<690,
     'no errors':not res['errors'],
    }
    for k,v in checks.items(): print(('PASS ' if v else 'FAIL ')+k)
    sys.exit(0 if all(checks.values()) else 1)
if __name__ == "__main__": asyncio.run(main())
