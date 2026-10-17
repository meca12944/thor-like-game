# GIF: double-tap run (dash start + dust) -> skid, sword combo with the wider 150° sector trail hitting at range, dodge afterimages (회피 잔상 대시) in 2 directions, running slash.
import asyncio, io, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
B='http://localhost:18931/index.html?nosave=1'; D='/workspace/town-demo/'
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',20)
SET="""()=>{const g=__game;g.setManual(true);document.getElementById('hint').style.display='none';const h=g.hero;h.atk=null;
 g.INV.equip.weapon={id:'w_bronze_long',plus:0};g.syncWeapon();h.x=250;h.y=520;h.face='right';h.hz='right';h.inv=0;h.hp=h.maxHp;
 const P=[[560,500],[575,560],[545,450]];let i=0;g.slimes.forEach(m=>{if(m.kind==='boar'||i>=3){m.dead=true;m.respawn=1e9;return;}const p=P[i++];m.dead=false;m.x=p[0];m.y=p[1];m.hp=60;m.maxHp=60;m.hpLag=60;m.t=99;m.state='idle';m.spawnT=0;m.respawn=1e9;m.kx=m.ky=0;});}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    await pg.goto(B); await pg.wait_for_function('window.__game&&window.__game.ready'); await pg.evaluate(SET)
    fr=[];label=['']
    async def step(n,lab=None):
      if lab: label[0]=lab
      for _ in range(n):
        await pg.evaluate("()=>{const g=__game;for(let k=0;k<2;k++){g.advance(1/60);g.slimes.forEach(m=>{m.t=99;m.state='idle'})}g.render()}")
        png=await pg.screenshot(clip={'x':140,'y':330,'width':640,'height':330})
        im=Image.open(io.BytesIO(png)).convert('RGB');d=ImageDraw.Draw(im);d.text((10,6),label[0],font=F,fill='#ffe08a',stroke_width=3,stroke_fill='black');fr.append(im)
    await step(6,'걷기')
    await pg.keyboard.down('ArrowRight'); await step(10)
    await pg.keyboard.up('ArrowRight'); await step(4)
    # double tap -> run
    await pg.keyboard.down('ArrowRight');await pg.keyboard.up('ArrowRight');await pg.wait_for_timeout(60);await pg.keyboard.down('ArrowRight')
    await step(9,'방향키 더블탭 → 출발 대시 + 달리기 (×1.9)')
    await pg.keyboard.up('ArrowRight'); await step(8,'손 떼면 짧은 미끄러짐')
    await pg.evaluate("()=>{const h=__game.hero;h.x=420;h.y=505;h.face='right';h.vx=h.vy=0}")
    label[0]='3연타 — 정면 150° 부채꼴, 궤적 = 판정 (2타 정면 되베기)'
    for i in range(3):
      await pg.keyboard.press('KeyJ'); await step(9 if i<2 else 16)
    await step(6)
    await pg.evaluate("()=>{const h=__game.hero;h.x=520;h.y=600;h.face='left';h.hz='left';h.vx=h.vy=0;h.dashCd=0}")
    await pg.keyboard.down('ArrowLeft'); await pg.keyboard.press('ShiftLeft'); await step(9,'회피 — 잔상 대시 (0.18초 무적)'); await pg.keyboard.up('ArrowLeft'); await step(5)
    await pg.evaluate("()=>{__game.hero.dashCd=0}")
    await pg.keyboard.down('ArrowUp'); await pg.keyboard.press('ShiftLeft'); await step(9); await pg.keyboard.up('ArrowUp'); await step(5)
    # run -> running slash
    await pg.evaluate("()=>{const h=__game.hero;h.x=230;h.y=505;h.face='right';h.hz='right';h.vx=h.vy=0}")
    await pg.keyboard.down('ArrowRight');await pg.keyboard.up('ArrowRight');await pg.wait_for_timeout(60);await pg.keyboard.down('ArrowRight')
    await step(12,'달리며 베기 · 달리며 회피(속도 유지)'); await pg.keyboard.press('KeyJ'); await step(12); await pg.keyboard.up('ArrowRight'); await step(8)
    q=[f.resize((480,248),Image.LANCZOS).quantize(colors=64,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for f in fr]
    q[0].save(D+'anim_run_combo_dodge.gif',save_all=True,append_images=q[1:],duration=33,loop=0,optimize=True)
    for k in (25,45,60,80,100): 
      if k<len(fr): fr[k].save(f'/tmp/rc{k}.png')
    print(json.dumps({'frames':len(fr),'errs':errs}))
    await b.close()
asyncio.run(main())
