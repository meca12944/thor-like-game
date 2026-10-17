"""Double-tap run / dodge / range / dash attack / charge attack checks (town + world). Run: python3 tools/test_run.py (needs :18931 or serves :18941)"""
import asyncio, json, socket, subprocess, sys, os
from playwright.async_api import async_playwright
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/';PORT=int(os.environ.get('RUN_PORT','18941'));U='http://127.0.0.1:%d/index.html?nosave=1'%PORT
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
    x0=await pg.evaluate("()=>__game.hero.x");await pg.keyboard.press('KeyJ');a=await pg.evaluate("(n)=>{for(let i=0;i<n;i++)__game.advance(1/60);const h=__game.hero;return {rs:!!(h.atk&&h.atk.s.special==='dash'),x:h.x}}",8)
    R['run_slash']=[a['rs'] and a['x']-x0>25,[a,x0]]  # running + attack = 돌진베기 (dash attack)
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
    # ---- dash attack (run + attack) / charge attack (hold attack) ----
    await pg.evaluate("()=>{const g=__game;g.FEEL.critChance=0;g.hero.atk=null;g.hero.cool=0;g.syncWeapon();g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9});const h=g.hero;h.x=300;h.y=540;h.vx=h.vy=0;h.face='right';h.hz='right';h.charge=null;h.chainT=0;h.combo=0}")
    await pg.keyboard.down('ArrowRight');await pg.keyboard.up('ArrowRight');await pg.wait_for_timeout(60);await pg.keyboard.down('ArrowRight');await pg.evaluate(adv,18)
    await pg.evaluate("()=>{const g=__game,h=g.hero,m=g.slimes.find(m=>m.kind!=='boar');m.dead=false;m.x=h.x+120;m.y=h.y;m.hp=m.maxHp=500;m.hpLag=500;m.t=99;m.state='idle';m.spawnT=0;m.respawn=1e9;window.__dm=m;window.__x0=h.x}")
    await pg.keyboard.press('KeyJ')
    da=await pg.evaluate("()=>{const g=__game,h=g.hero;g.advance(1/60);const s=h.atk&&h.atk.s;const r={special:s&&s.special,arc:s&&s.arc,range:s&&g.swingRange(s),r1:g.swingRange(g.SWINGS[0])};let n=0;while(h.atk&&n<120){g.advance(1/60);n++;}r.travel=h.x-window.__x0;r.dmg=500-window.__dm.hp;r.cool=h.cool;return r}")
    await pg.keyboard.up('ArrowRight')
    R['dash_attack']=[da['special']=='dash' and da['arc']==100 and abs(da['range']-da['r1'])<2 and 80<=da['travel']<=170 and abs(da['dmg']-13)<.01 and da['cool']>.2,da]
    sp=await pg.evaluate("()=>{const g=__game,h=g.hero;h.atkBuf=0;window.__k=h.atk;return 1}")
    await pg.keyboard.press('KeyJ');ns=await pg.evaluate("()=>{const g=__game,h=g.hero;g.advance(1/60);return !h.atk}")
    R['dash_attack_no_spam']=[ns,1];await pg.evaluate(adv,30)
    # dodge-cancel of the dash attack
    await pg.evaluate("()=>{const h=__game.hero;h.x=300;h.y=540;h.vx=h.vy=0;h.cool=0;h.dashCd=0;h.atk=null}")
    await pg.keyboard.down('ArrowRight');await pg.keyboard.up('ArrowRight');await pg.wait_for_timeout(60);await pg.keyboard.down('ArrowRight');await pg.evaluate(adv,12)
    await pg.keyboard.press('KeyJ');await pg.evaluate("()=>{const g=__game,h=g.hero;let n=0;while(h.atk&&h.atk.t<h.atk.s.cancel&&n<60){g.advance(1/60);n++}}")
    await pg.keyboard.press('ShiftLeft');dc=await pg.evaluate("()=>{const g=__game,h=g.hero;g.advance(1/60);return {dash:!!h.dash,atk:!!h.atk}}")
    await pg.keyboard.up('ArrowRight');await pg.evaluate(adv,40)
    R['dash_attack_dodge_cancel']=[dc['dash'] and not dc['atk'],dc]
    # tap = normal combo (no charge)
    await pg.evaluate("()=>{const h=__game.hero;h.x=330;h.y=540;h.vx=h.vy=0;h.cool=0;h.atk=null;h.chainT=0;h.combo=0;h.run=false}")
    await pg.keyboard.down('KeyJ');await pg.evaluate(adv,3);await pg.keyboard.up('KeyJ')
    tp=await pg.evaluate("()=>{const g=__game,h=g.hero;const i=h.atk&&h.atk.i;let ch=false;for(let n=0;n<50;n++){g.advance(1/60);ch=ch||!!h.charge}return {i,ch}}")
    R['tap_is_combo']=[tp['i']==0 and not tp['ch'],tp];await pg.evaluate(adv,20)
    # hold -> charge lv0 / lv1 (0.6 s) / lv2 (1.2 s); slow move; release lv2 = strong slash + wave
    await pg.evaluate("()=>{const g=__game,h=g.hero;h.x=330;h.y=540;h.vx=h.vy=0;h.cool=0;h.atk=null;h.chainT=0;h.combo=0;const m=window.__dm;m.dead=false;m.x=h.x+110;m.y=h.y;m.hp=500;m.hpLag=500;m.kx=m.ky=0;m.t=99;m.state='idle'}")
    await pg.keyboard.down('KeyJ')
    st=await pg.evaluate("()=>{const g=__game,h=g.hero,o={};const at=n=>{for(let i=0;i<n;i++){g.advance(1/60);window.__dm.t=99;window.__dm.state='idle';window.__dm.kx=window.__dm.ky=0}};at(24);o.c0=h.charge?h.charge.lv:-1;at(20);o.c1=h.charge?h.charge.lv:-1;o.anim=g.heroAnimName();at(40);o.c2=h.charge?h.charge.lv:-1;return o}")
    await pg.keyboard.down('ArrowRight');mv=await pg.evaluate("()=>{const g=__game,h=g.hero;for(let i=0;i<12;i++)g.advance(1/60);return {vx:h.vx,face:h.face,lv:h.charge&&h.charge.lv}}");await pg.keyboard.up('ArrowRight')
    await pg.evaluate("()=>{const g=__game,h=g.hero;for(let i=0;i<14;i++)g.advance(1/60);h.vx=h.vy=0;const m=window.__dm;m.x=h.x+110;m.y=h.y;m.hp=500;window.__mx=1}")
    await pg.keyboard.up('KeyJ')
    rl=await pg.evaluate("()=>{const g=__game,h=g.hero;g.advance(1/60);const s=h.atk&&h.atk.s,o={special:s&&s.special,range:s&&g.swingRange(s),r1:g.swingRange(g.SWINGS[0]),arc:s&&s.arc};let w=false,n=0;while(h.atk&&n<120){g.advance(1/60);window.__dm.t=99;window.__dm.state='idle';w=w||g.WAVES.some(x=>x.on);n++}o.wave=w;o.dmg=500-window.__dm.hp;return o}")
    R['charge_levels']=[st['c0']==0 and st['c1']==1 and st['c2']==2,st]
    R['charge_slow_move']=[60<mv['vx']<110 and mv['lv']==2,mv]
    R['charge_lv2_release']=[rl['special']=='c2' and rl['arc']==100 and rl['range']/rl['r1']>1.35 and rl['wave'] and abs(rl['dmg']-18)<.01,rl]
    # lv1 release damage = 1.15x hit 1; a flinching hit cancels the charge
    await pg.evaluate("()=>{const g=__game,h=g.hero;h.cool=0;h.atk=null;const m=window.__dm;m.x=h.x+100;m.y=h.y;m.hp=500;m.kx=m.ky=0}")
    await pg.keyboard.down('KeyJ');await pg.evaluate("()=>{const g=__game;for(let i=0;i<44;i++){g.advance(1/60);window.__dm.t=99;window.__dm.state='idle';window.__dm.kx=window.__dm.ky=0}window.__dm.hp=500}");await pg.keyboard.up('KeyJ')
    l1=await pg.evaluate("()=>{const g=__game,h=g.hero;g.advance(1/60);const sp=h.atk&&h.atk.s.special;let n=0;while(h.atk&&n<120){g.advance(1/60);window.__dm.t=99;window.__dm.state='idle';n++}return {sp,dmg:500-window.__dm.hp}}")
    R['charge_lv1_release']=[l1['sp']=='c1' and abs(l1['dmg']-11.5)<.01,l1]
    await pg.evaluate("()=>{const g=__game;g.hero.cool=0;window.__dm.dead=true}");await pg.evaluate(adv,20)
    await pg.keyboard.down('KeyJ');hc=await pg.evaluate("()=>{const g=__game,h=g.hero;for(let i=0;i<40;i++)g.advance(1/60);const before=!!h.charge;h.inv=0;g.hurtHero(1,0,1);for(let i=0;i<6;i++)g.advance(1/60);return {before,after:!!h.charge}}");await pg.keyboard.up('KeyJ')
    R['hit_cancels_charge']=[hc['before'] and not hc['after'],hc];await pg.evaluate("()=>{const g=__game,h=g.hero;h.hp=h.maxHp;for(let i=0;i<60;i++)g.advance(1/60)}")
    # world: double tap run in field00
    await pg.wait_for_function("window.__world&&__world.ready",timeout=15000)
    await pg.evaluate("()=>{__world.setManual(true);__world.go('field00','town')}")
    for i in range(120):
      if await pg.evaluate("()=>{__world.advance(1/20);return !__world.trans&&__world.map&&__world.map.id==='field00'}"): break
      await pg.wait_for_timeout(30)
    wr=await pg.evaluate("()=>{const W=__world,h=W.hero;const sx=h.x,sy=h.y;W.key('ArrowDown',true);W.advance(.15);const vw=(h.y-sy)/.15;W.key('ArrowDown',false);W.advance(.5);h.x=sx;h.y=sy;W.dirTap('down');W.dirTap('down');W.key('ArrowDown',true);const x0=h.y;W.advance(.15);const r={run:!!h.run,v:(h.y-x0)/.15,vw};W.key('ArrowDown',false);W.advance(.05);r.skid=h.skidT>0;r.run2=!!h.run;return r}")
    R['world_run']=[wr['run'] and wr['skid'] and not wr['run2'] and wr['v']>1.7*wr['vw']>0,wr]
    R['world_hit3']=[await pg.evaluate("()=>__world.SWING.arc3===100&&Math.abs(__world.swingR(2)/__world.swingR(0)-1.15)<.01"),1]
    # world: dash attack + charge lv2 (+ wave) + hit cancels charge
    wd=await pg.evaluate("""()=>{const W=__world,h=W.hero;W.killAll();h.atk=null;h.atkCd=0;h.inv=0;const sx=h.x,sy=h.y;W.dirTap('down');W.dirTap('down');W.key('ArrowDown',true);W.advance(.12);W.key('KeyJ',true);W.advance(1/60);
      const o={i:h.atk&&h.atk.i,arc:W.arcW(3)};const y0=h.y;W.key('KeyJ',false);W.advance(.2);o.travel=h.y-y0;W.key('ArrowDown',false);W.advance(.4);o.cd=h.atkCd;W.advance(.5);
      h.x=sx;h.y=sy;h.run=false;W.key('KeyJ',true);W.advance(.3);o.c0=h.charge&&h.charge.lv;W.advance(1.0);o.c2=h.charge&&h.charge.lv;W.key('KeyJ',false);W.advance(1/60);o.rel=h.atk&&h.atk.i;W.advance(.12);o.hw=(W.S.hw||[]).length;o.r5=W.swingR(5)/W.swingR(0);W.advance(1.2);
      W.key('KeyJ',true);W.advance(.4);o.cb=!!h.charge;h.inv=0;W.hurt(1,{x:h.x+10,y:h.y},true);W.advance(1/60);o.ca=!!h.charge;W.key('KeyJ',false);W.advance(.5);h.hp=h.maxHp;return o}""")
    R['world_dash_charge']=[wd['i']==3 and wd['arc']==100 and wd['travel']>18 and wd['c0']==0 and wd['c2']==2 and wd['rel']==5 and wd['hw']>=1 and wd['r5']>1.35 and wd['cb'] and not wd['ca'],wd]
    R['noErrors']=[not errs,errs]
    await b.close()
  if p0:p0.terminate()
  bad=[k for k,v in R.items() if not v[0]];print(json.dumps(R,ensure_ascii=False,default=str));print('FAIL',bad) if bad else print('PASS')
asyncio.run(main())
