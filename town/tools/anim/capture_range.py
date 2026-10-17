# Static check: combo hit 1/2/3 in 4 directions with the debug sector (yellow) vs the swing trail. -> shot_range_<weapon>.png
import asyncio, io, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
B='http://localhost:18931/index.html?nosave=1&debug=1'; D='/workspace/town-demo/'
F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',16)
WEAP=sys.argv[1:] or ['w_bronze_long']
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    await pg.goto(B); await pg.wait_for_function('window.__game&&window.__game.ready')
    for wid in WEAP:
      cells=[]
      for face in ['right','left','down','up']:
        for i in range(3):
          info=await pg.evaluate("""([wid,face,i])=>{const g=__game;g.setManual(true);document.getElementById('hint').style.display='none';
            const h=g.hero;h.atk=null;g.INV.equip.weapon={id:wid,plus:0};g.syncWeapon();h.x=330;h.y=540;h.face=face;h.hz=face==='left'?'left':'right';h.atk=null;h.inv=0;h.vx=h.vy=0;
            g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9;});
            const s=g.SWINGS[i];g.startSwingForTest(i);const t=s.a0+(s.a1-s.a0)*.7;while(h.atk&&h.atk.t<t)g.advance(1/60);h.x=330;h.y=540;g.render();
            return {range:Math.round(g.swingRange(s)),arc:s.arc||g.FEEL.arcDeg,anim:s.anim,name:s.name}}""",[wid,face,i])
          png=await pg.screenshot(clip={'x':130,'y':370,'width':400,'height':300})
          im=Image.open(io.BytesIO(png)).convert('RGB');d=ImageDraw.Draw(im)
          d.text((6,4),f"{face} hit{i+1} {info['name']} r={info['range']} {info['arc']}°",font=F,fill='#ffe08a',stroke_width=2,stroke_fill='black')
          cells.append(im)
      W=Image.new('RGB',(1200,1200));[W.paste(c,((k%3)*400,(k//3)*300)) for k,c in enumerate(cells)]
      W.save(D+f'shot_range_{wid}.png');print(wid,'ok')
    print('errs',errs);await b.close()
asyncio.run(main())
