import asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
U='http://localhost:18931/index.html'; D='/workspace/town-demo/'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.on('requestfailed',lambda r: errs.append('FAIL '+r.url))
    await pg.goto(U)
    for i in range(100):
      if await pg.evaluate('!!(window.__game&&window.__game.ready)'): break
      await pg.wait_for_timeout(100)
    await pg.evaluate("()=>{const g=__game;g.setManual(true);document.getElementById('hint').style.display='none';g.slimes.forEach(m=>{m.dead=true;m.respawn=99});const h=g.hero;h.x=640;h.y=460;h.face='down';}")
    shots=[];names=[]
    loaded=await pg.evaluate("()=>Object.keys(SPR).filter(k=>k.includes('@')).filter(k=>!IMG[k]).length")
    for n in range(5):
      if n: await pg.keyboard.press('g')
      await pg.evaluate("()=>__game.advance(.05)"); await pg.wait_for_timeout(120)
      names.append((await pg.evaluate('()=>__gear()'))['name'])
      f=D+f'shot_gear_{n}.png'; await pg.screenshot(path=f); shots.append(f)
    await b.close()
  ims=[Image.open(f).convert('RGB') for f in shots]
  # 주인공 주변만 잘라 5칸 비교
  crops=[im.crop((im.width//2-150,im.height//2-260,im.width//2+150,im.height//2+60)) for im in ims]
  W=sum(c.width for c in crops); out=Image.new('RGB',(W,crops[0].height+40),(20,20,24)); d=ImageDraw.Draw(out)
  f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',20)
  for i,c in enumerate(crops): out.paste(c,(i*c.width,40)); d.text((i*c.width+c.width/2,20),names[i],font=f,fill='white',anchor='mm')
  out.save(D+'shot_gear.png'); print('names',names,'missing',loaded,'errors',errs)
asyncio.run(main())
