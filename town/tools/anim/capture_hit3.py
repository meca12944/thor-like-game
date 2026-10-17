# GIF: combo hit 3 (finishing slash, 100 deg) — sword combo for contrast, hit 3 in 4 directions, slow-mo frame sequencing, greatsword / spear hit 3. Trail = hitbox.
import asyncio, io, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
B='http://localhost:18931/index.html?nosave=1'; D='/workspace/town-demo/'
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',20)
HX,HY=360,520
SET="""(w)=>{const g=__game;g.setManual(true);const hi=document.getElementById('hint');if(hi)hi.style.display='none';const h=g.hero;h.atk=null;
 g.INV.equip.weapon={id:w,plus:0};g.syncWeapon();h.x=%d;h.y=%d;h.vx=h.vy=0;h.inv=0;h.hp=h.maxHp;g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9;});}"""%(HX,HY)
MOBS="""(a)=>{const g=__game,R=g.swingRange(g.SWINGS[2]);let i=0;g.slimes.forEach(m=>{if(m.kind==='boar'||i>=3){m.dead=true;m.respawn=1e9;return;}const t=a[0]+(i-1)*a[1]*Math.PI/180;i++;
 m.dead=false;m.x=%d+Math.cos(t)*R*.85;m.y=%d-8+Math.sin(t)*R*.85*.75;m.hp=200;m.maxHp=200;m.hpLag=200;m.t=99;m.state='idle';m.spawnT=0;m.respawn=1e9;m.kx=m.ky=0;});}"""%(HX,HY)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    await pg.goto(B); await pg.wait_for_function('window.__game&&window.__game.ready')
    fr=[];label=['']
    async def step(n,lab=None,tk=2):
      if lab: label[0]=lab
      for _ in range(n):
        await pg.evaluate("(k)=>{const g=__game;for(let i=0;i<k;i++){g.advance(1/60);g.slimes.forEach(m=>{m.t=99;m.state='idle';m.kx=m.ky=0})}g.render()}",tk)
        png=await pg.screenshot(clip={'x':HX-330,'y':HY-250,'width':660,'height':400})
        im=Image.open(io.BytesIO(png)).convert('RGB');d=ImageDraw.Draw(im);d.text((10,6),label[0],font=F,fill='#ffe08a',stroke_width=3,stroke_fill='black');fr.append(im)
    async def hit3(w,face,lab,tk=2,n=None):
      await pg.evaluate(SET,w);ang={'right':0,'down':90,'left':180,'up':-90}[face]
      await pg.evaluate("(f)=>{const h=__game.hero;h.face=f;if(f==='left'||f==='right')h.hz=f;}",face)
      await pg.evaluate(MOBS,[ang,70]);await step(3,lab,tk)
      await pg.evaluate("()=>{const g=__game,h=g.hero;h.combo=1;g.startSwingForTest(2)}")
      d=await pg.evaluate("()=>__game.hero.atk.s.dur");await step(n or int(d*60/tk)+6,None,tk)
    await pg.evaluate(SET,'w_bronze_long');await pg.evaluate("()=>{__game.hero.face='right';__game.hero.hz='right'}");await pg.evaluate(MOBS,[0,70])
    label[0]='한손검 3연타 — 3타: 정면 100° · 사거리 ×1.15 · 긴 휘두름'
    for i in range(3):
      await pg.keyboard.press('KeyJ'); await step(9 if i<2 else 24)
    await step(4)
    for f in ('down','left','up'): await hit3('w_bronze_long',f,'3타 마무리 베기 — 4방향 (궤적 = 판정)')
    await hit3('w_bronze_long','right','슬로 ×0.5 — 휘두름 프레임이 판정 구간에 맞춰짐',tk=1)
    await hit3('w_boar_tusk','right','대검 3타 — 100° · 사거리 140')
    await hit3('w_harpoon_blade','down','창 3타 — 100° · 사거리 159')
    q=[f.resize((440,267),Image.LANCZOS).quantize(colors=48,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for f in fr]
    q[0].save(D+'anim_hit3_long.gif',save_all=True,append_images=q[1:],duration=33,loop=0,optimize=True)
    for k in (30,40,60,90,120,150,175): 
      if k<len(fr): fr[k].save(f'/tmp/h3_{k}.png')
    print(json.dumps({'frames':len(fr),'errs':errs}))
    await b.close()
asyncio.run(main())
