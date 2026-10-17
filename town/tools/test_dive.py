import asyncio, json
from playwright.async_api import async_playwright
U='http://localhost:18931/index.html'; D='/workspace/town-demo/'
async def ready(pg):
  for i in range(100):
    if await pg.evaluate('!!(window.__game&&window.__game.ready)'): return
    await pg.wait_for_timeout(100)
PREP="""(o)=>{const g=__game;g.setManual(true);document.getElementById('hint').style.display='none';g.slimes.forEach(m=>{m.dead=true;m.respawn=999});
 const h=g.hero;h.x=o[0];h.y=o[1];h.face=o[2];h.hz=o[2]==='left'?'left':'right';g.gauge=1;if(o[3])h.hp=o[3];}"""
SWIM="""async()=>{const g=__game,h=g.hero,[fx,fy]=g.DIVE.floorItem;let n=0;
 while(g.uw&&g.uw.item&&n<400){g.keys['d']=h.x<fx-20;g.keys['a']=h.x>fx+20;g.keys['s']=h.y<fy-50;g.keys['w']=h.y>fy-10;g.advance(1/30);n++;}
 for(const k of 'wasd')g.keys[k]=false;return n}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); errs=[]; out={}
    pg=await b.new_page(viewport={'width':1280,'height':720})
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    await pg.goto(U); await ready(pg); await pg.evaluate("()=>localStorage.clear()"); await pg.reload(); await ready(pg)
    out['start']=await pg.evaluate("()=>[__game.hero.maxHp,__game.coins,__game.slots.slice()]")
    # sparkle near the barrel (hidden spot) vs far away
    await pg.evaluate(PREP,[450,224,'up'])
    out['sparkleNearBarrel']=await pg.evaluate("()=>{const g=__game;let mx=0;for(let i=0;i<240;i++){g.advance(1/60);mx=Math.max(mx,g.fx.filter(f=>f.type==='twinkle').length)}return mx}")
    await pg.wait_for_timeout(60)
    await pg.evaluate("()=>{const g=__game;for(let i=0;i<200;i++){g.advance(1/60);if(g.fx.some(f=>f.type==='twinkle'&&f.t>.2&&f.t<.35))break}}"); await pg.wait_for_timeout(60)
    await pg.screenshot(path='/tmp/spark_barrel.png',clip=dict(x=340,y=110,width=240,height=160))
    await pg.evaluate(PREP,[300,600,'right'])
    out['sparkleFar']=await pg.evaluate("()=>{const g=__game;g.fx.length=0;let mx=0;for(let i=0;i<240;i++){g.advance(1/60);mx=Math.max(mx,g.fx.filter(f=>f.type==='twinkle').length)}return mx}")
    await pg.evaluate(PREP,[868,590,'up']); await pg.evaluate("()=>{const g=__game;for(let i=0;i<300;i++){g.advance(1/60);if(g.fx.some(f=>f.type==='twinkle'&&f.t>.2&&f.t<.35))break}}"); await pg.wait_for_timeout(60)
    await pg.screenshot(path='/tmp/spark_puddle.png',clip=dict(x=760,y=500,width=240,height=160))
    # not near any spot -> plain water cannon
    await pg.evaluate(PREP,[300,600,'right']); out['farIsCannon']=await pg.evaluate("()=>{__game.useSkill('water');__game.advance(.3);return [!!__game.uw,__game.fx.some(f=>f.type==='proj')]}")
    await pg.evaluate("()=>__game.advance(1)")
    res={}
    for sid,pos,hp in [('fountain',[590,410,'right'],0),('barrel',[450,222,'up'],0),('puddle',[868,580,'up'],2)]:
      await pg.evaluate(PREP,pos+[hp] if hp else pos)
      r={}
      r['used']=await pg.evaluate("()=>__game.useSkill('water')")
      await pg.evaluate("()=>__game.advance(.62)"); r['uw']=await pg.evaluate("()=>__game.uw&&[__game.uw.spot.id,__game.uw.item]")
      await pg.evaluate("()=>__game.advance(.5)")
      if sid=='fountain':
        await pg.evaluate("()=>{const g=__game;g.hero.x=700;g.hero.y=470;g.advance(.05)}"); await pg.wait_for_timeout(60)
        await pg.screenshot(path='/tmp/uw_before.png')
      r['swimSteps']=await pg.evaluate(SWIM)
      await pg.evaluate("()=>__game.advance(.25)"); await pg.wait_for_timeout(60)
      r['popup']=await pg.evaluate("()=>__game.popup&&[__game.popup.title,__game.popup.sub]")
      if sid=='fountain': await pg.screenshot(path=D+'shot_dive.png')
      if sid=='puddle': await pg.screenshot(path='/tmp/uw_puddle.png')
      if sid=='barrel': await pg.screenshot(path='/tmp/uw_barrel.png')
      r['state']=await pg.evaluate("()=>[__game.hero.hp,__game.hero.maxHp,__game.coins,__game.diveTaken.slice()]")
      await pg.evaluate("()=>{__game.useSkill('water');__game.advance(.6)}")
      r['surfaced']=await pg.evaluate("()=>[!__game.uw,__game.hero.x|0,__game.hero.y|0]")
      res[sid]=r
    out['dives']=res
    await pg.evaluate("()=>{__game.setManual(false)}"); await pg.wait_for_timeout(200); await pg.screenshot(path='/tmp/hud_after.png')
    await pg.reload(); await ready(pg)
    out['afterReload']=await pg.evaluate("()=>[__game.hero.maxHp,__game.hero.hp,__game.coins,__game.diveTaken.slice()]")
    await pg.evaluate(PREP,[590,410,'right'])
    out['reDive']=await pg.evaluate("()=>{const g=__game;g.useSkill('water');g.advance(1.2);return g.uw&&[g.uw.spot.id,g.uw.item,g.uw.emptyMsg>0]}")
    await pg.evaluate("()=>{__game.useSkill('water');__game.advance(.6)}")
    # attack button also surfaces
    await pg.evaluate(PREP,[868,580,'up']); out['atkSurfaces']=await pg.evaluate("()=>{const g=__game;g.useSkill('water');g.advance(1.2);const a=!!g.uw;g.press();g.advance(.6);return [a,!g.uw]}")
    # debug reset
    pd=await b.new_page(viewport={'width':1280,'height':720}); pd.on('pageerror',lambda e:errs.append(str(e)))
    await pd.goto(U+'?debug=1'); await ready(pd); await pd.wait_for_timeout(300); await pd.screenshot(path='/tmp/debug_dive.png')
    await pd.click('#dreset'); out['afterReset']=await pd.evaluate("()=>[__game.hero.maxHp,__game.coins,__game.diveTaken.slice(),localStorage.getItem('townDemo.dive')]")
    await pd.reload(); await ready(pd); out['afterResetReload']=await pd.evaluate("()=>[__game.hero.maxHp,__game.coins]")
    out['errs']=errs; print(json.dumps(out,ensure_ascii=False)); await b.close()
asyncio.run(main())
