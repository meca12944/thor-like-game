import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
U='http://localhost:18931/index.html'
D='/workspace/town-demo/'
async def waitready(pg):
  for i in range(100):
    if await pg.evaluate('!!(window.__game&&window.__game.ready)'): return
    await pg.wait_for_timeout(100)
  raise Exception('not ready')
SETUP="""(o)=>{const g=__game;g.setManual(true);document.getElementById('hint').style.display='none';
 const h=g.hero;h.x=o.hx;h.y=o.hy;h.face=o.face||'right';h.hz=h.face==='left'?'left':'right';g.gauge=1;
 g.slimes.forEach((m,i)=>{const p=o.sl[i];if(p){m.dead=false;m.x=p[0];m.y=p[1];m.hp=2;m.t=99;m.state='idle';m.spawnT=0;m.hz=0;m.kx=m.ky=0;m.squash=0;}else{m.dead=true;m.respawn=99;}});}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    errs=[];res={}
    async def page(vp,url=U,touch=False):
      pg=await b.new_page(viewport=vp,has_touch=touch,is_mobile=touch)
      pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
      pg.on('pageerror',lambda e: errs.append(str(e)))
      pg.on('requestfailed',lambda r: errs.append('FAIL '+r.url))
      await pg.goto(url); await waitready(pg); return pg
    pg=await page({'width':1280,'height':720})
    await pg.evaluate("()=>localStorage.clear()")
    # ---- combo ----
    await pg.evaluate(SETUP,dict(hx=520,hy=500,sl=[[640,500],[600,560],[430,470]]))
    log=[]
    async def st(): return await pg.evaluate("()=>{const a=__game.hero.atk;return a?[a.i,a.s.name,+a.t.toFixed(2),__game.slimes.map(m=>m.hp)]:null}")
    await pg.evaluate("()=>{__game.press();__game.advance(.11)}"); log.append(await st()); await pg.wait_for_timeout(80); await pg.screenshot(path=D+'shot_combo_1.png')
    await pg.evaluate("()=>{__game.press();__game.advance(.17+.13)}"); log.append(await st()); await pg.wait_for_timeout(80); await pg.screenshot(path=D+'shot_combo_2.png')
    await pg.evaluate("()=>{__game.press();__game.advance(.17+.18)}"); log.append(await st()); await pg.wait_for_timeout(80); await pg.screenshot(path=D+'shot_combo_3.png')
    await pg.evaluate("()=>__game.advance(.6)"); log.append(['after',await pg.evaluate("()=>[__game.hero.atk,__game.hero.combo,__game.slimes.map(m=>m.dead)]")])
    # chain window expiry -> restart at 횡베기
    await pg.evaluate("()=>{__game.press();__game.advance(.5);__game.press();__game.advance(.05)}"); log.append(['reset',await st()])
    res['combo']=log
    # debug view during spin
    pd=await page({'width':1280,'height':720},U+'?debug=1')
    await pd.evaluate(SETUP,dict(hx=520,hy=500,sl=[[640,500],[600,560]]))
    await pd.evaluate("()=>{const g=__game;g.press();g.advance(.1);g.press();g.advance(.3);g.press();g.advance(.38)}"); await pd.wait_for_timeout(80)
    await pd.screenshot(path=D+'shot_debug.png'); await pd.close()
    # ---- skills ----
    T={'quake':.42,'thread':.3,'sand':1.0,'pact':.95,'water':.29,'shield':.26,'fire':.42,'bolt':.24,'time':1.1,'dragon':1.0}
    crops=[];skl={}
    for sid,tt in T.items():
      await pg.goto(U); await waitready(pg)
      sl=[[700,500],[640,560],[760,450]]
      if sid=='shield': sl=[[556,500]]
      if sid in('water','fire'): sl=[[840,505],[700,600],[300,620]]
      if sid=='time': sl=[[700,500],[640,580],[380,560]]
      await pg.evaluate(SETUP,dict(hx=520,hy=500,sl=sl))
      before=await pg.evaluate("()=>__game.slimes.map(m=>[m.x|0,m.y|0,m.hp])")
      if sid=='time': await pg.evaluate("()=>__game.slimes.forEach(m=>{m.t=0.01})")
      ok=await pg.evaluate("(a)=>__game.useSkill(a[0],{hold:a[1]})",[sid,1.2])
      if sid=='time':
        await pg.evaluate("()=>__game.advance(.62)"); await pg.wait_for_timeout(80)
        hx0=520;await pg.screenshot(path='/tmp/sk_time.png',clip=dict(x=hx0-230,y=500-270,width=700,height=400))
        fz=await pg.evaluate("()=>{const g=__game;g.advance(.45);const a=g.slimes.map(m=>[m.x|0,m.y|0]);g.keys['d']=true;g.advance(.65);g.keys['d']=false;const b=g.slimes.map(m=>[m.x|0,m.y|0]);return {frozen:JSON.stringify(a)===JSON.stringify(b),a,b,heroX:g.hero.x|0}}")
        skl['time_frozen_check']=fz
      else:
        await pg.evaluate("(t)=>__game.advance(t)",tt)
      await pg.wait_for_timeout(80)
      info=await pg.evaluate("()=>{const g=__game;return {sk:g.hero.sk&&g.hero.sk.id,ph:g.hero.sk&&g.hero.sk.ph,fx:g.fx.map(f=>f.type),hero:[g.hero.x|0,g.hero.y|0],hidden:g.hero.hidden,ts:+g.timeStop.toFixed(2),gauge:+g.gauge.toFixed(2),sl:g.slimes.map(m=>[m.x|0,m.y|0,m.hp,m.dead])}}")
      hx,hy=info['hero']
      x0=max(0,min(1280-700,hx-230)); y0=max(0,min(720-400,hy-270))
      if sid!='time': await pg.screenshot(path='/tmp/sk_%s.png'%sid,clip=dict(x=x0,y=y0,width=700,height=400))
      await pg.evaluate("()=>__game.advance(3.5)")
      after=await pg.evaluate("()=>__game.slimes.map(m=>[m.x|0,m.y|0,m.hp,m.dead])")
      skl[sid]=dict(ok=ok,mid=info,before=before,after=after); crops.append((sid,'/tmp/sk_%s.png'%sid))
    # dive into the fountain + swim + exit
    await pg.goto(U); await waitready(pg)
    await pg.evaluate(SETUP,dict(hx=590,hy=410,sl=[]))
    near=await pg.evaluate("()=>{const g=__game;return [g.blocked(600,440,12)]}")
    await pg.evaluate("()=>{__game.useSkill('water');__game.advance(.7);__game.keys['d']=true;__game.advance(.5);__game.keys['d']=false}")
    await pg.wait_for_timeout(80)
    sw=await pg.evaluate("()=>{const h=__game.hero;return [!!__game.uw,h.x|0,h.y|0]}")
    await pg.screenshot(path='/tmp/sk_dive.png',clip=dict(x=520,y=220,width=520,height=300))
    await pg.evaluate("()=>{__game.useSkill('water');__game.advance(.6)}")
    sw2=await pg.evaluate("()=>{const h=__game.hero;return [!!__game.uw,h.x|0,h.y|0]}")
    skl['dive']=dict(blockedStart=near,swimming=sw,afterExit=sw2)
    res['skills']=skl
    # contact sheet 5x2 (+dive inset)
    cw,ch=700,400; sheet=Image.new('RGB',(cw*5,ch*2+0),(0,0,0)); d=ImageDraw.Draw(sheet)
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf',30)
    except Exception: font=None
    names=await pg.evaluate("()=>Object.fromEntries(__game.SKILLS.map(s=>[s.id,s.name+'  '+s.en]))")
    for i,(sid,fn) in enumerate(crops):
      im=Image.open(fn).convert('RGB'); x,y=(i%5)*cw,(i//5)*ch; sheet.paste(im,(x,y))
      if sid=='water':
        dv=Image.open('/tmp/sk_dive.png').convert('RGB').resize((260,150)); sheet.paste(dv,(x+cw-264,y+ch-154)); d.rectangle([x+cw-265,y+ch-155,x+cw-3,y+ch-3],outline=(255,255,255),width=2)
        d.text((x+cw-258,y+ch-150),'dive/swim',fill=(255,255,255),font=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Nanum Gothic/NanumGothic-Bold.ttf',18) if font else None)
      d.rectangle([x,y,x+cw-1,y+ch-1],outline=(20,20,20),width=3)
      d.text((x+12,y+8),'%d. %s'%(i+1,names[sid]),fill=(255,255,255),font=font,stroke_width=3,stroke_fill=(0,0,0))
    sheet.save(D+'shot_skills.png')
    # ---- skill window ----
    await pg.goto(U); await waitready(pg)
    await pg.evaluate("()=>{__game.setManual(true);document.getElementById('hint').style.display='none'}")
    await pg.keyboard.press('o'); await pg.wait_for_timeout(100)
    w1=await pg.evaluate("()=>[__game.winOpen,__game.slots.slice()]")
    await pg.click('.wi[data-id=bolt]'); await pg.click('#wslots .ws:nth-child(2)')
    w2=await pg.evaluate("()=>[__game.slots.slice(),localStorage.getItem('townDemo.skillSlots')]")
    await pg.click('#wslots .ws:nth-child(3)')   # unequip slot 3
    await pg.click('.wi[data-id=shield]')        # -> first empty slot (3)
    await pg.click('.wi[data-id=fire]'); await pg.click('#wslots .ws:nth-child(2)')  # swap fire (slot1) <-> bolt (slot2)
    w3=await pg.evaluate("()=>[__game.slots.slice(),localStorage.getItem('townDemo.skillSlots')]")
    hp=await pg.evaluate("()=>{const x=__game.hero.x;__game.setManual(false);return x}")
    await pg.keyboard.down('d'); await pg.wait_for_timeout(300); await pg.keyboard.up('d')
    paused=await pg.evaluate("(x)=>__game.hero.x===x",hp)
    await pg.click('.wi[data-id=quake]'); await pg.wait_for_timeout(100)
    await pg.screenshot(path=D+'shot_skillwindow.png')
    await pg.keyboard.press('Escape')
    await pg.reload(); await waitready(pg)
    w4=await pg.evaluate("()=>__game.slots.slice()")
    # keys 1/2/3 fire slots (real-time)
    await pg.evaluate("()=>{__game.gauge=1;document.getElementById('hint').style.display='none'}")
    await pg.keyboard.press('1'); await pg.wait_for_timeout(50); k1=await pg.evaluate("()=>__game.hero.sk&&__game.hero.sk.id")
    await pg.wait_for_timeout(1200); await pg.screenshot(path=D+'shot.png')
    res['window']=dict(open=w1,afterAssign=w2,afterUnequipEquipSwap=w3,pausedWhileOpen=paused,afterReload=w4,key1=k1)
    # fps
    res['fps']=await pg.evaluate("()=>new Promise(r=>{let n=0,t0=performance.now();function f(){n++;if(performance.now()-t0<1000)requestAnimationFrame(f);else r(n)}requestAnimationFrame(f)})")
    pp=await page({'width':844,'height':390},touch=True); await pp.evaluate("()=>{}"); await pp.wait_for_timeout(500)
    await pp.screenshot(path=D+'shot_touch_landscape.png')
    pq=await page({'width':390,'height':844},touch=True); await pq.wait_for_timeout(500)
    await pq.screenshot(path=D+'shot_portrait.png')
    # ---- HP bars + CHAMPION label ----
    await pg.goto(U); await waitready(pg)
    await pg.evaluate(SETUP,dict(hx=520,hy=520,sl=[[640,500],[610,600],[430,470]]))
    await pg.evaluate("()=>{const b=__game.boar;Object.assign(b,{dead:false,x:665,y:560,hp:8,hpLag:8,state:'idle',t:99,spawnT:0,kx:0,ky:0,face:-1})}")
    hb={}
    hb['before']=await pg.evaluate("()=>__game.slimes.map(m=>[m.kind,m.hp,m.maxHp,m.champion||false])")
    await pg.evaluate("()=>{const g=__game;g.press();g.advance(.11);g.press();g.advance(.3);g.press();g.advance(.2)}")
    hb['justHit']=await pg.evaluate("()=>__game.slimes.map(m=>[m.kind,m.hp,+m.hpLag.toFixed(2),+m.hitT.toFixed(2),m.dead])")
    await pg.evaluate("()=>{const g=__game,b=g.boar;g.damageSlime(g.slimes[1],1,0,1,0,{skill:1});g.advance(.25);g.damageSlime(b,1,0,2,0,{skill:1});g.advance(.06);g.hero.atk=null;b.state='idle';b.t=99;b.kx=b.ky=0;g.slimes.forEach(m=>{m.kx=m.ky=0})}")
    hb['shotState']=await pg.evaluate("()=>__game.slimes.map(m=>[m.kind,m.hp,+m.hpLag.toFixed(2),+m.lagDelay.toFixed(2)])")
    await pg.wait_for_timeout(80); await pg.screenshot(path=D+'shot_hpbars.png')
    await pg.evaluate("()=>__game.advance(1.2)")
    hb['caughtUp']=await pg.evaluate("()=>__game.slimes.map(m=>[m.kind,m.hp,+m.hpLag.toFixed(2)])")
    # boar charge + wall stun, enhanced label render, map reload at random valid spots
    hb['charge']=await pg.evaluate("()=>{const g=__game,b=g.boar;g.hero.x=300;g.hero.y=560;Object.assign(b,{x:700,y:560,state:'idle',t:0,hp:8,hpLag:8});const st=[];for(let i=0;i<120;i++){g.advance(1/60);if(!st.includes(b.state))st.push(b.state);}return st}")
    hb['wallStun']=await pg.evaluate("()=>{const g=__game,b=g.boar;g.hero.x=600;g.hero.y=560;const B=g.blocked;let x=600;while(!B(x,560,26)&&x>0)x-=4;Object.assign(b,{x:x+40,y:560,state:'charge',t:.9,vx:-430,vy:0});const st=[];for(let i=0;i<30;i++){g.advance(1/60);if(!st.includes(b.state))st.push(b.state);}return st}")
    hb['enhancedRender']=await pg.evaluate("()=>{const b=__game.boar;b.champion='enhanced';__game.render();b.champion=true;return true}")
    hb['reload']=await pg.evaluate("()=>{const g=__game;g.reloadMap();return g.slimes.map(m=>{const d=Math.hypot(m.x-g.hero.x,m.y-g.hero.y);return [m.kind,m.x|0,m.y|0,d>260&&!g.blocked(m.x,m.y,20),m.hp]})}")
    res['hpbars']=hb
    res['errs']=errs
    print(json.dumps(res,ensure_ascii=False,indent=0))
    await b.close()
asyncio.run(main())
