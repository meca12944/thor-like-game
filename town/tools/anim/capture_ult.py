# Headless capture of the 3 full-screen ultimates -> anim_ultimate_<id>.gif (640x360, 30 fps)
import asyncio, io, json, sys
from playwright.async_api import async_playwright
from PIL import Image
U='http://localhost:18931/index.html?nosave=1'; D='/workspace/town-demo/'
SET="""(o)=>{const g=__game;g.setManual(true);document.getElementById('hint').style.display='none';g.setTitle(o.title);
 if(o.w)g.INV.equip.weapon={id:o.w,plus:0};g.syncWeapon();const h=g.hero;h.x=560;h.y=470;h.face='right';h.hz='right';
 const P=[[700,480],[760,520],[640,380],[380,560],[900,600]];let i=0;g.slimes.forEach(m=>{const p=P[i++%P.length];m.dead=false;m.x=p[0];m.y=p[1];m.hp=m.kind==='boar'?40:30;m.maxHp=m.hp;m.hpLag=m.hp;m.t=99;m.state='idle';m.spawnT=0;m.respawn=1e9;});
 g.ultG=g.ULT_CFG.max;g.advance(.1);g.castUlt();return [g.ultFx&&g.ultFx.U.id, g.slimes.map(m=>[m.kind,m.hp])];}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]; rep={}
    pg.on('pageerror',lambda e: errs.append(str(e)))
    for uid,o in [('tenkou',dict(title='영웅',w=None)),('metsukai',dict(title='마왕',w=None)),('chan',dict(title='영웅',w='hs_chan'))]:
      await pg.goto(U); await pg.wait_for_function('window.__game&&window.__game.ready')
      r=await pg.evaluate(SET,o); fr=[]
      for i in range(110):
        await pg.evaluate("()=>{__game.advance(2/60);__game.render()}")
        im=Image.open(io.BytesIO(await pg.screenshot())).convert('RGB').resize((512,288),Image.LANCZOS); fr.append(im)
      after=await pg.evaluate("()=>[!!__game.ultFx,__game.slimes.map(m=>[m.kind,+m.hp.toFixed(1),m.dead])]")
      rep[uid]={'started':r[0],'before':r[1],'after':after}
      q=[f.quantize(colors=112,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for f in fr]
      q[0].save(D+f'anim_ultimate_{uid}.gif',save_all=True,append_images=q[1:],duration=33,loop=0,optimize=True)
      fr[30].save(f'/tmp/ult_{uid}_cut.png');fr[50].save(f'/tmp/ult_{uid}_fx.png');fr[64].save(f'/tmp/ult_{uid}_fx2.png')
    print(json.dumps({'rep':rep,'errs':errs},ensure_ascii=False))
    await b.close()
asyncio.run(main())
