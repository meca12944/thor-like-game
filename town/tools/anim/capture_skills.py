# Headless capture of all 10 hero skills at the zoomed-out scale (fixed 60 Hz sim, 30 fps GIF).
# python3 tools/anim/capture_skills.py  -> anim_skill_01..10.gif + anim_skills_all.gif
import asyncio, io, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
U='http://localhost:18931/index.html?nosave=1'; D='/workspace/town-demo/'
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',20)
F2=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',17)
HX,HY=470,470; CW,CHh=600,340; CX,CY=HX+150,HY-70
SETUP="""(o)=>{const g=__game;g.setManual(true);document.getElementById('hint').style.display='none';
 const h=g.hero;h.x=o.hx;h.y=o.hy;h.face='right';h.hz='right';g.gauge=1;h.inv=0;
 g.slimes.forEach((m,i)=>{const p=o.sl[i];if(p&&m.kind!=='boar'){m.dead=false;m.x=p[0];m.y=p[1];m.hp=99;m.maxHp=99;m.hpLag=99;m.t=99;m.state='idle';m.spawnT=0;m.hz=0;m.kx=m.ky=0;m.squash=0;m.respawn=1e9;}else{m.dead=true;m.respawn=1e9;}});}"""
def quant(fr): return [f.quantize(colors=128,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for f in fr]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    skills=None; allf=[]; report={}
    for idx in range(10):
      await pg.goto(U)
      for i in range(100):
        if await pg.evaluate('!!(window.__game&&window.__game.ready)'): break
        await pg.wait_for_timeout(100)
      if skills is None: skills=await pg.evaluate("()=>__game.SKILLS.map(s=>[s.id,s.name,s.superArmor!==false])")
      sid,name,sa=skills[idx]
      sl=[[HX+110,HY],[HX+170,HY+28],[HX+230,HY-22]]
      if sid=='shield': sl=[[HX+70,HY]]
      await pg.evaluate(SETUP,dict(hx=HX,hy=HY,sl=sl))
      ok=await pg.evaluate("(a)=>__game.useSkill(a[0],{hold:a[1]})",[sid,1.2])
      demo_sa = sid=='dragon'
      frames=[]; sa_log=None
      for f in range(60):
        cap=f'{idx+1:02d}  {name}  (슬롯 스킬 · 슈퍼아머)'
        if demo_sa and f==14:
          sa_log=await pg.evaluate("()=>{const g=__game,h=g.hero;h.inv=0;const before=!!h.sk;g.hurtHero?g.hurtHero(-1,0):null;return {castBefore:before,hp:h.hp}}")
        if demo_sa and f==16: sa_log['mid']=await pg.evaluate("()=>{const h=__game.hero;return {sk:h.sk&&h.sk.id,hurtT:h.hurtT,kx:h.kx,redT:h.redT}}")
        if demo_sa and 14<=f<40: cap+='  ← 피격! 끊기지 않음'
        await pg.evaluate("()=>{__game.advance(2/60);__game.render()}")
        png=await pg.screenshot(clip={'x':CX-CW/2,'y':CY-CHh/2,'width':CW,'height':CHh})
        im=Image.open(io.BytesIO(png)).convert('RGB'); d=ImageDraw.Draw(im)
        d.text((10,6),cap,font=F,fill='white',stroke_width=3,stroke_fill='black')
        frames.append(im)
      dmg=await pg.evaluate("()=>__game.slimes.filter(m=>m.kind!=='boar'&&m.respawn>1e8||1).map(m=>m.dead?'dead':99-m.hp)")
      report[sid]={'ok':ok,'name':name,'dmg':dmg,'sa':sa_log}
      q=quant(frames)
      q[0].save(D+f'anim_skill_{idx+1:02d}.gif',save_all=True,append_images=q[1:],duration=33,loop=0,optimize=True)
      allf+= [f.resize((420,238),Image.LANCZOS) for f in frames[::3]]  # all-in-one: 10 fps, smaller
    q=quant(allf)
    q[0].save(D+'anim_skills_all.gif',save_all=True,append_images=q[1:],duration=100,loop=0,optimize=True)
    print(json.dumps({'report':report,'errs':errs},ensure_ascii=False))
    await b.close()
asyncio.run(main())
