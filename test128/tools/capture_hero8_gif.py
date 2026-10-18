"""Render hero8 walk / run (8 dirs) and cast from the GAME CANVAS (headless Chromium, fixed 60 fps ticks) into GIFs.
python3 tools/test/capture_hero8_gif.py <page e.g. index128.html> <out_dir>"""
import asyncio, io, os, sys
from PIL import Image
from playwright.async_api import async_playwright
PAGE=sys.argv[1]; OUT=sys.argv[2]; os.makedirs(OUT,exist_ok=True)
U=f'http://127.0.0.1:18952/{PAGE}?nosave=1'
KEYS={'right':['ArrowRight'],'downright':['ArrowDown','ArrowRight'],'down':['ArrowDown'],'downleft':['ArrowDown','ArrowLeft'],
      'left':['ArrowLeft'],'upleft':['ArrowUp','ArrowLeft'],'up':['ArrowUp'],'upright':['ArrowUp','ArrowRight']}
START={'right':(250,560),'downright':(250,470),'down':(330,420),'downleft':(560,470),'left':(620,560),'upleft':(620,640),'up':(330,690),'upright':(250,640)}
async def grab(pg,n,step,fix=True):
    fr=[]
    await pg.evaluate("()=>{const h=__game.hero;window.__g0=[h.x,h.y]}")
    for i in range(n):
        st=await pg.evaluate("(k)=>{for(let i=0;i<k;i++){__game.advance(1/60);const h=__game.hero;if(Math.hypot(h.x-__g0[0],h.y-__g0[1])>140){h.x=__g0[0];h.y=__g0[1];}}return new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>{const h=__game.hero;r([h.x,h.y])})))}",step)
        x,y=st; sx,sy=x*1.5,y*1.5  # town 1280x720 world -> 1920x1080 screen
        png=await pg.screenshot(clip={'x':max(0,sx-150),'y':max(0,sy-200),'width':300,'height':240})
        fr.append(Image.open(io.BytesIO(png)).convert('RGB'))
    return fr
def save(fr,path,ms):
    fr[0].save(path,save_all=True,append_images=fr[1:],duration=ms,loop=0)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1920,'height':1080}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        await pg.goto(U); await pg.wait_for_function('window.__game&&window.__game.ready'); await pg.wait_for_timeout(5500)
        await pg.evaluate("()=>{const g=__game;g.setManual(true);g.slimes.forEach(m=>{m.dead=true;m.respawn=1e9});}")
        sheet=[]
        for mode in ['walk','run']:
            for d,ks in KEYS.items():
                vx,vy={'right':(1,0),'downright':(.7,.7),'down':(0,1),'downleft':(-.7,.7),'left':(-1,0),'upleft':(-.7,-.7),'up':(0,-1),'upright':(.7,-.7)}[d]
                L=150
                x,y=await pg.evaluate(f"""()=>{{const g=__game,h=g.hero;let best=null;for(let cx=200;cx<=1080;cx+=40)for(let cy=420;cy<=600;cy+=30){{
                  const sx=cx-({vx})*{L}/2,sy=cy-({vy})*{L}/2;h.x=sx;h.y=sy;let ok=true;for(let i=0;i<12;i++){{const px=h.x,py=h.y;g.moveCol(h,({vx})*{L}/12,({vy})*{L}/12,12);if(Math.hypot(h.x-px,h.y-py)<{L}/12*.95){{ok=false;break;}}}}
                  if(ok){{const dc=Math.hypot(cx-560,cy-560);if(!best||dc<best[2])best=[sx,sy,dc];}}}}return best?[best[0],best[1]]:[330,540]}}""")
                await pg.evaluate(f"()=>{{const h=__game.hero;h.x={x};h.y={y};h.vx=h.vy=0;h.run=false;}}"); await pg.wait_for_timeout(400)
                if mode=='run':
                    await pg.keyboard.down(ks[-1]);await pg.keyboard.up(ks[-1]);await pg.wait_for_timeout(60)
                    for k in ks: await pg.keyboard.down(k)
                else:
                    for k in ks: await pg.keyboard.down(k)
                await pg.evaluate("(k)=>{for(let i=0;i<k;i++)__game.advance(1/60)}",4)
                await pg.evaluate(f"()=>{{const h=__game.hero;h.x={x};h.y={y};}}")
                scn=await pg.evaluate('()=>window.__world?__world.scene:"town"');fr=await grab(pg,36 if mode=='walk' else 30,2);print(mode,d,x,y,scn)   # 2 ticks per GIF frame = real-time 30 fps
                for k in ks: await pg.keyboard.up(k)
                await pg.evaluate("(k)=>{for(let i=0;i<k;i++)__game.advance(1/60)}",30)
                save(fr,f'{OUT}/{mode}_{d}.gif',33); sheet.append(fr)
        # cast: skill 1 (fire), 2 (water, dive away from fountain) and Q area — standing, facing down / right
        for nm,key,face,f8 in [('cast_fire_down','Digit1','down','down'),('cast_quake_right','Digit3','right','right'),('cast_area_downleft','KeyQ','left','downleft')]:
            await pg.evaluate(f"()=>{{const h=__game.hero;h.x=330;h.y=560;h.vx=h.vy=0;h.face='{face}';h.f8='{f8}';h.inv=0}}")
            await pg.evaluate("(k)=>{for(let i=0;i<k;i++)__game.advance(1/60)}",200)
            await pg.keyboard.press(key); fr=await grab(pg,45,2); save(fr,f'{OUT}/{nm}.gif',33)
        print('errors',errs)
        await b.close()
asyncio.run(main())
