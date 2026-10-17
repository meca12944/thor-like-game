# Side-by-side hit-feel comparison: ?juice=0 (before) vs default (after). Same scripted sword combo + skill + kill.
import asyncio, io, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
B='http://localhost:18931/index.html?nosave=1'; D='/workspace/town-demo/'
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',18)
SET="""()=>{const g=__game;g.setManual(true);document.getElementById('hint').style.display='none';Math.random=(()=>{let s=7;return()=>{s=(s*16807)%2147483647;return s/2147483647;}})();
 g.INV.equip.weapon={id:'w_bronze_long',plus:0};g.syncWeapon();const h=g.hero;h.x=520;h.y=480;h.face='right';h.hz='right';
 const P=[[585,480],[605,505],[575,455]];let i=0;g.slimes.forEach(m=>{if(m.kind==='boar'){m.dead=true;m.respawn=1e9;return;}const p=P[i++];m.dead=false;m.x=p[0];m.y=p[1];m.hp=i===3?2:12;m.maxHp=m.hp;m.hpLag=m.hp;m.t=99;m.state='idle';m.spawnT=0;m.respawn=1e9;m.kx=m.ky=0;});}"""
async def run(pg,url):
  await pg.goto(url); await pg.wait_for_function('window.__game&&window.__game.ready'); await pg.evaluate(SET)
  tot=await pg.evaluate("()=>__game.SWINGS.slice(0,3).map(s=>Math.round(s.dur*60))")
  t1,t2=tot[0]-3,tot[0]+tot[1]-6;T=sum(tot)
  fr=[]
  for i in range((T+60+230)//3):
    t=i*3
    await pg.evaluate("(t)=>{const g=__game;g.hero.inv=99;if(t===0||(t>=%d&&t<%d)||(t>=%d&&t<%d)||(t>=%d&&t<%d))g.press();if(t===%d)g.useSkill('fire');for(let k=0;k<3;k++)g.advance(1/60);g.render()}"%(t1,t1+3,t2,t2+3,T+21,T+24,T+51),t)
    png=await pg.screenshot(clip={'x':380,'y':170,'width':900,'height':520})
    fr.append(Image.open(io.BytesIO(png)).convert('RGB').resize((432,250),Image.LANCZOS))
  return fr
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    a=await run(pg,B+'&juice=0'); c=await run(pg,B)
    n=min(len(a),len(c)); out=[]
    for i in range(n):
      im=Image.new('RGB',(872,262),(0,0,0));im.paste(a[i],(0,12));im.paste(c[i],(440,12));d=ImageDraw.Draw(im)
      d.text((6,10),'BEFORE',font=F,fill='#ccc',stroke_width=2,stroke_fill='black');d.text((446,10),'AFTER · 손맛 패스',font=F,fill='#ffe08a',stroke_width=2,stroke_fill='black');out.append(im)
    q=[f.quantize(colors=128,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for f in out]
    q[0].save(D+'anim_hitfeel.gif',save_all=True,append_images=q[1:],duration=50,loop=0,optimize=True)
    [out[k].save(f'/tmp/hf{k}.png') for k in (20,50,80,105) if k<len(out)]
    print(json.dumps({'frames':n,'errs':errs}))
    await b.close()
asyncio.run(main())
