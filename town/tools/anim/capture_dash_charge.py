# GIF: 돌진베기 (run + attack) and 모으기 (hold attack: lv1 blue 0.6 s, lv2 gold 1.2 s, release = strong slash; lv2 + forward wave).
import asyncio, io, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
B='http://localhost:18931/index.html?nosave=1'; D='/workspace/town-demo/'
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',20)
CX,CY=430,520
SET="""()=>{const g=__game;g.setManual(true);const hi=document.getElementById('hint');if(hi)hi.style.display='none';const h=g.hero;h.atk=null;h.charge=null;g.FEEL.critChance=0;
 g.INV.equip.weapon={id:'w_bronze_long',plus:0};g.syncWeapon();h.inv=0;h.hp=h.maxHp;g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9;});}"""
MOBS="""(P)=>{const g=__game;let i=0;g.slimes.forEach(m=>{if(m.kind==='boar'||i>=P.length){m.dead=true;m.respawn=1e9;return;}const p=P[i++];m.dead=false;m.x=p[0];m.y=p[1];m.hp=m.maxHp=300;m.hpLag=300;m.t=99;m.state='idle';m.spawnT=0;m.respawn=1e9;m.kx=m.ky=0;});}"""
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
        png=await pg.screenshot(clip={'x':CX-300,'y':CY-230,'width':640,'height':330})
        im=Image.open(io.BytesIO(png)).convert('RGB');d=ImageDraw.Draw(im);d.text((10,6),label[0],font=F,fill='#ffe08a',stroke_width=3,stroke_fill='black');fr.append(im)
    async def place(x,y,face='right'):
      await pg.evaluate("(a)=>{const h=__game.hero;h.x=a[0];h.y=a[1];h.vx=h.vy=0;h.face=a[2];if(a[2]==='left'||a[2]==='right')h.hz=a[2];h.cool=0;h.atk=null;h.run=false}",[x,y,face])
    # 1) dash attack
    await place(CX-260,CY);await pg.evaluate(MOBS,[[CX+40,CY],[CX+60,CY-40]]);await step(4,'달리기 (더블탭) → 공격 = 돌진베기')
    await pg.keyboard.down('ArrowRight');await pg.keyboard.up('ArrowRight');await pg.wait_for_timeout(60);await pg.keyboard.down('ArrowRight')
    await step(9);await pg.keyboard.press('KeyJ');await step(14,'돌진베기 — 약 1.6타일 돌진 · 정면 100° · 1타의 1.3배');await pg.keyboard.up('ArrowRight');await step(8)
    # 2) charge lv2 (+ slow walk while charging)
    await place(CX-150,CY);await pg.evaluate(MOBS,[[CX+10,CY],[CX+90,CY+10],[CX+170,CY-10]]);await step(3,'모으기 — 공격 키 누른 채 유지')
    await pg.keyboard.down('KeyJ');await step(16,'모으기 — 공격 키 누른 채 유지 (처음엔 그대로 1타)')
    await step(10,'0.6초: 1단계 (푸른 빛 + 효과음)')
    await pg.keyboard.down('ArrowRight');await step(10,'모으는 중엔 천천히 이동 (방향 고정)');await pg.keyboard.up('ArrowRight')
    await step(12,'1.2초: 2단계 (금빛 + 다른 효과음)')
    await pg.keyboard.up('KeyJ');await step(26,'떼면 극 모아베기 — 1타의 3배 · 사거리 ×1.4 + 검기')
    await step(6)
    # 3) charge lv1 release
    await place(CX-120,CY);await pg.evaluate(MOBS,[[CX+10,CY]]);await pg.keyboard.down('KeyJ');await step(20,'1단계에서 떼면 모아베기 — 1타의 2배 · 사거리 ×1.15')
    await pg.keyboard.up('KeyJ');await step(20)
    q=[f.resize((480,248),Image.LANCZOS).quantize(colors=64,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for f in fr]
    q[0].save(D+'anim_dash_charge.gif',save_all=True,append_images=q[1:],duration=33,loop=0,optimize=True)
    for k in (20,40,62,80,95,110,125,150): 
      if k<len(fr): fr[k].save(f'/tmp/dc_{k}.png')
    print(json.dumps({'frames':len(fr),'errs':errs}))
    await b.close()
asyncio.run(main())
