"""Double-tap run / dodge / range checks (town + world). Run: python3 tools/test_run.py (needs :18931 or serves :18941)"""
import asyncio, json, socket, subprocess, sys, os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/';PORT=18941;U='http://127.0.0.1:%d/index.html?nosave=1'%PORT
def srv():
  s=socket.socket()
  try: s.connect(('127.0.0.1',PORT));s.close();return None
  except OSError: return subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
async def main():
  p0=srv();await asyncio.sleep(.8);R={};errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1280,'height':720});pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(U);await pg.wait_for_function('window.__game&&window.__game.ready')
    await pg.evaluate("()=>{const g=__game;g.setManual(true);g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9});const h=g.hero;h.x=330;h.y=540;h.face='right';}")
    adv="(n)=>{for(let i=0;i<n;i++)__game.advance(1/60);const h=__game.hero;return {x:h.x,vx:h.vx,run:!!h.run,anim:__game.heroAnimName(),skid:h.skidT>0}}"
    # single tap + hold = walk
    await pg.keyboard.down('ArrowRight');w=await pg.evaluate(adv,30);await pg.keyboard.up('ArrowRight');await pg.evaluate(adv,30)
    R['walk_no_run']=[not w['run'] and abs(w['vx']-215)<10,w]
    await pg.evaluate("()=>{const h=__game.hero;h.x=330;h.vx=h.vy=0}")
    # double tap within .25s then hold = run
    await pg.keyboard.down('ArrowRight');await pg.keyboard.up('ArrowRight');await pg.wait_for_timeout(90);await pg.keyboard.down('ArrowRight')
    s0=await pg.evaluate(adv,3);s1=await pg.evaluate(adv,30)
    R['run_start']=[s0['run'] and s0['anim']=='runstart' and s0['vx']>215*1.8,s0]
    R['run_speed']=[s1['run'] and s1['anim']=='run' and 1.8*215<s1['vx']<2.0*215,s1]
    await pg.keyboard.up('ArrowRight');k=await pg.evaluate(adv,2)
    R['skid']=[k['skid'] and not k['run'] and k['anim']=='skid',k];await pg.evaluate(adv,30)
    # slow double tap (> .25s) = no run
    await pg.keyboard.down('ArrowLeft');await pg.keyboard.up('ArrowLeft');await pg.wait_for_timeout(400);await pg.keyboard.down('ArrowLeft');s=await pg.evaluate(adv,20);await pg.keyboard.up('ArrowLeft');await pg.evaluate(adv,30)
    R['slow_tap_walk']=[not s['run'],s]
    # diagonal: hold down, double-tap right
    await pg.evaluate("()=>{const h=__game.hero;h.x=330;h.y=480;h.vx=h.vy=0}")
    await pg.keyboard.down('ArrowDown');await pg.keyboard.down('ArrowRight');await pg.keyboard.up('ArrowRight');await pg.wait_for_timeout(80);await pg.keyboard.down('ArrowRight')
    d=await pg.evaluate("(n)=>{for(let i=0;i<n;i++)__game.advance(1/60);const h=__game.hero;return {run:!!h.run,sp:Math.hypot(h.vx,h.vy)}}",30)
    R['diagonal_run']=[d['run'] and d['sp']>1.8*215,d]
    # run -> attack = running slash (lunge), then dodge from run keeps momentum
    await pg.evaluate("()=>{const h=__game.hero;h.x=330;h.y=540;}")
    await pg.keyboard.up('ArrowDown');await pg.evaluate(adv,6)
    x0=await pg.evaluate("()=>__game.hero.x");await pg.keyboard.press('KeyJ');a=await pg.evaluate("(n)=>{for(let i=0;i<n;i++)__game.advance(1/60);const h=__game.hero;return {rs:!!(h.atk&&h.atk.runSlash),x:h.x}}",8)
    R['run_slash']=[a['rs'] and a['x']-x0>25,[a,x0]]
    await pg.evaluate(adv,30);await pg.evaluate("()=>{const h=__game.hero;h.x=330;}")
    await pg.evaluate(adv,4);r=await pg.evaluate("()=>{const h=__game.hero;return {run:!!h.run}}")
    await pg.keyboard.press('ShiftLeft');dd=await pg.evaluate("(n)=>{const h=__game.hero;const x0=h.x;for(let i=0;i<n;i++)__game.advance(1/60);return {carry:h.dash?h.dash.carry:null,dx:h.x-x0,run:!!h.run}}",6)
    e=await pg.evaluate("(n)=>{for(let i=0;i<n;i++)__game.advance(1/60);const h=__game.hero;return {vx:h.vx,run:!!h.run,dash:!!h.dash}}",14)
    R['dodge_from_run']=[r['run'] and dd['carry'] and not e['dash'] and e['run'] and e['vx']>1.5*215,[r,dd,e]]
    await pg.keyboard.up('ArrowRight');await pg.evaluate(adv,30)
    # always-run option
    await pg.evaluate("()=>{__game.toggleAlwaysRun();const h=__game.hero;h.x=330;h.vx=h.vy=0}")
    await pg.keyboard.down('ArrowRight');ar=await pg.evaluate(adv,20);await pg.keyboard.up('ArrowRight');await pg.evaluate(adv,30);await pg.evaluate("()=>__game.toggleAlwaysRun()")
    R['always_run']=[ar['run'],ar]
    await pg.keyboard.press('Escape');mt=await pg.evaluate("()=>document.body.innerText");await pg.keyboard.press('Escape')
    R['menu_row']=['달리기 기본: 끔' in mt,1]
    # ranges / arc
    R['ranges']=[await pg.evaluate("()=>{const g=__game;g.hero.atk=null;g.syncWeapon();return g.SWINGS.slice(0,3).every((s,i)=>g.swingRange(s)>=96&&(s.arc||g.FEEL.arcDeg)>=(i<2?130:100))}"),1]
    # hit 3 = finishing slash for every weapon: 100 deg, reach 1.15x hit 1, active window >=8 ticks and >=1.2x hit 1 (old hit 3 +60%), strike frames pinned to the active window
    R['hit3_all_weapons']=[await pg.evaluate("""()=>{const g=__game,W=g.ANIM.weapons;const ok=Object.keys(W).every(t=>{g.buildSwings(t);const S=g.SWINGS,a=S[0],c=S[2];
      return c.arc===100&&Math.abs(g.swingRange(c)/g.swingRange(a)-1.15)<.02&&(c.a1-c.a0)>=1.2*(a.a1-a.a0)&&(c.a1-c.a0)>=8/60-1e-6&&c.strike&&c.strike[0]<c.strike[1]});g.buildSwings(g.weaponType||'sword');return ok}"""),1]
    # run cycle: 8 frames cover ~208 world px at 1.9x (stride, not cadence, grows -> no foot sliding)
    cyc=await pg.evaluate("()=>{const g=__game,h=g.hero;h.x=330;h.y=540;h.vx=h.vy=0;h.run=true;h.runStartT=0;h.walkT=0;const x0=h.x;return x0}")
    await pg.keyboard.down('ArrowRight');cy=await pg.evaluate("(n)=>{const h=__game.hero;h.run=true;h.runStartT=0;const x0=h.x,w0=h.walkT;for(let i=0;i<n;i++)__game.advance(1/60);return {dist:h.x-x0,cycles:(h.walkT-w0)*60/32}}",30);await pg.keyboard.up('ArrowRight');await pg.evaluate(adv,30)
    R['run_cycle_stride']=[190<cy['dist']/cy['cycles']<230,cy]
    # world: double tap run in field00
    await pg.wait_for_function("window.__world&&__world.ready",timeout=15000)
    await pg.evaluate("()=>{__world.setManual(true);__world.go('field00','town')}")
    for i in range(120):
      if await pg.evaluate("()=>{__world.advance(1/20);return !__world.trans&&__world.map&&__world.map.id==='field00'}"): break
      await pg.wait_for_timeout(30)
    wr=await pg.evaluate("()=>{const W=__world,h=W.hero;const sx=h.x,sy=h.y;W.key('ArrowDown',true);W.advance(.15);const vw=(h.y-sy)/.15;W.key('ArrowDown',false);W.advance(.5);h.x=sx;h.y=sy;W.dirTap('down');W.dirTap('down');W.key('ArrowDown',true);const x0=h.y;W.advance(.15);const r={run:!!h.run,v:(h.y-x0)/.15,vw};W.key('ArrowDown',false);W.advance(.05);r.skid=h.skidT>0;r.run2=!!h.run;return r}")
    R['world_run']=[wr['run'] and wr['skid'] and not wr['run2'] and wr['v']>1.7*wr['vw']>0,wr]
    R['world_hit3']=[await pg.evaluate("()=>__world.SWING.arc3===100&&Math.abs(__world.swingR(2)/__world.swingR(0)-1.15)<.01"),1]
    R['noErrors']=[not errs,errs]
    await b.close()
  if p0:p0.terminate()
  bad=[k for k,v in R.items() if not v[0]];print(json.dumps(R,ensure_ascii=False,default=str));print('FAIL',bad) if bad else print('PASS')
asyncio.run(main())
