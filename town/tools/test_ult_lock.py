"""필살기 story lock: locked by default (no gauge gain, hidden gauge, R = nothing, town + field), ?ult=1 / ?ult=full debug override,
ultDebug() console toggle, unlockUltimate() persists flags.ultUnlocked in the world save (thor.world.v1), flag 'mid_story' unlocks,
'필살기 해방!' notice. Screenshot: town/hud_preview/ult_locked.png. Run: python3 tools/test_ult_lock.py (serves town/ on :18953)"""
import asyncio, json, subprocess, sys, os, time
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/';PORT=int(os.environ.get('ULT_PORT','18953'));B='http://127.0.0.1:%d/index.html'%PORT
READY='!!(window.__game&&window.__game.ready&&window.__world&&window.__world.ready)'
async def main():
  srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.8);R={};errs=[]
  try:
    async with async_playwright() as p:
      b=await p.chromium.launch();ctx=await b.new_context(viewport={'width':1280,'height':720});pg=await ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
      async def load(q=''):
        await pg.goto(B+'?nosave=1'+q);await pg.wait_for_function(READY,timeout=20000)
        await pg.evaluate("()=>{const g=__game;g.setManual(true);g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9});if(g.boar){g.boar.x=-9999;g.boar.t=1e9}window.__ultDraws=0;const o=HUD.drawUlt;HUD.drawUlt=function(){__ultDraws++;return o.apply(this,arguments)}}")
      ev=pg.evaluate
      # ---- default: locked
      await load()
      s=await ev("""()=>{const g=__game,o={unlocked:g.ultUnlocked};g.addUlt(50);g.hurtHero(1,0,10);o.gAfterGain=g.ultG;g.hero.hp=g.hero.maxHp;g.hero.inv=0;
        g.ultG=100;g.castUlt();o.fxAfterCast=!!g.ultFx;o.gAfterCast=g.ultG;g.advance(.2);g.render();o.draws=__ultDraws;return o}""")
      R['locked_default']=[s['unlocked'] is False and s['gAfterGain']==0 and not s['fxAfterCast'] and s['gAfterCast']==100 and s['draws']==0,s]
      await pg.keyboard.press('KeyR');await ev("()=>__game.advance(.1)")
      R['locked_R_key']=[await ev("()=>!__game.ultFx&&__game.ultG===100"),1]
      await ev("()=>{__game.ultG=0;__game.advance(.5);__game.render()}");await pg.wait_for_timeout(300)
      await pg.screenshot(path=D+'hud_preview/ult_locked.png')
      # field: no cast, no HUD gauge, no gain from world hurt
      await ev("()=>{__world.setManual(true);__world.go('field01','west')}")
      for i in range(200):
        if await ev("()=>__world.scene!=='town'&&!__world.trans"): break
        await ev("()=>__world.advance(.05)");await pg.wait_for_timeout(25)
      f=await ev("""()=>{const W=__world,g=__game;W.advance(.3);W.god=false;const o={scene:W.scene,map:W.map&&W.map.id};__ultDraws=0;W.advance(.3);o.draws=__ultDraws;
        g.ultG=100;W.tap('KeyR');W.advance(.2);o.fx=!!W.ultFx;g.ultG=0;W.hero.inv=0;W.hurt(5);o.gain=g.ultG;return o}""")
      R['locked_field']=[f['scene']!='town' and f['draws']==0 and not f['fx'] and f['gain']==0,f]
      # mid-story placeholder flag -> unlock + notice + persisted
      u=await ev("""()=>{const W=__world,g=__game;W.hero.hp=W.hero.maxHp;W.flag('mid_story');const o={unlocked:g.ultUnlocked,banner:W.S.banner&&W.S.banner.text,
        saved:JSON.parse(localStorage.getItem('thor.world.v1')).flags.ultUnlocked};__ultDraws=0;W.advance(.2);o.draws=__ultDraws;W.hero.inv=0;W.hurt(4);o.gain=g.ultG;
        g.ultG=100;W.tap('KeyR');W.advance(.1);o.fx=!!W.ultFx;W.advance(4);return o}""")
      R['mid_story_unlock']=[u['unlocked'] and u['saved'] is True and '필살기 해방' in str(u['banner']) and u['draws']>0 and u['gain']>0 and u['fx'],u]
      # persisted across reload
      await load();R['persisted']=[await ev("()=>__game.ultUnlocked===true"),1]
      # unlockUltimate() in town: notice message, returns true once
      await ev("()=>localStorage.removeItem('thor.world.v1')");await load()
      t=await ev("()=>{const g=__game,o={before:g.ultUnlocked,first:unlockUltimate(),second:unlockUltimate(),after:g.ultUnlocked};o.saved=JSON.parse(localStorage.getItem('thor.world.v1')).flags.ultUnlocked;g.advance(.1);g.render();o.draws=__ultDraws;return o}")
      R['unlockUltimate']=[t['before'] is False and t['first'] and not t['second'] and t['after'] and t['saved'] and t['draws']>0,t]
      # debug overrides: ?ult=1 (session only, save untouched), ultDebug toggle, ?ult=full
      await ev("()=>localStorage.removeItem('thor.world.v1')");await load('&ult=1')
      d=await ev("()=>{const g=__game,o={unlocked:g.ultUnlocked};g.hurtHero(1,0,10);o.gain=g.ultG;g.ultG=100;g.castUlt();o.fx=!!g.ultFx;g.advance(4);o.saved=localStorage.getItem('thor.world.v1');o.off=ultDebug(false);o.on=ultDebug(true);return o}")
      R['debug_url_ult1']=[d['unlocked'] and d['gain']>0 and d['fx'] and not (d['saved'] and 'ultUnlocked' in d['saved']) and d['off'] is False and d['on'] is True,d]
      await load('&ult=full');R['debug_url_full']=[await ev("()=>__game.ultUnlocked&&__game.ultG===100"),1]
      await b.close()
  finally: srv.terminate()
  R['noErrors']=[not errs,errs]
  bad=[k for k,v in R.items() if not v[0]];print(json.dumps(R,ensure_ascii=False,default=str));print('FAIL',bad) if bad else print('PASS');sys.exit(1 if bad else 0)
asyncio.run(main())
