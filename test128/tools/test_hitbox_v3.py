import asyncio,json,sys,subprocess,time,io
from playwright.async_api import async_playwright
from PIL import Image
D='/workspace/town-demo';PORT=18954;BASE=sys.argv[1] if len(sys.argv)>1 else f'http://127.0.0.1:{PORT}/index128.html'
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL) if len(sys.argv)<=1 else None;time.sleep(1);errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1920,'height':1080});pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(BASE+('&' if '?' in BASE else '?')+'nosave=1&hitbox=1');await pg.wait_for_function('window.__game&&window.__game.ready',timeout=90000);await pg.wait_for_timeout(5500)
        await pg.evaluate("()=>{const g=__game;g.setManual(true);g.slimes.forEach(m=>{m.x+=5000;m.respawn=1e9})}")
        test="""([d,i,r])=>{const g=__game,h=g.hero,m=g.slimes[0];h.x=900;h.y=560;h.vx=h.vy=0;h.face=d;h.f8=d;h.atk=null;h.cool=0;h.inv=9;
          const v={right:[1,0],left:[-1,0],down:[0,1],up:[0,-1]}[d];m.dead=false;m.hp=m.maxHp=99999;m.x=h.x+v[0]*r;m.y=h.y-8+v[1]*r*.75;m.vx=m.vy=0;m.kx=m.ky=0;m.state='idle';m.t=-99;
          const hp=m.hp;g.startSwingForTest(i);const s=h.atk.s;let n=0;while(h.atk&&n<80){g.advance(1/60);n++;m.x=h.x+v[0]*r;m.y=h.y-8+v[1]*r*.75;}return m.hp<hp}"""
        R={}
        HB=await pg.evaluate("()=>H8HB")
        for d in ['right','left','down','up']:
            for i in range(3):
                Rr=HB['r'][d][i]; row={}
                for r in [60,round(Rr*.9),Rr,Rr+16,Rr+40]:
                    row[r]=await pg.evaluate(test,[d,i,r])
                R[f'{d}_hit{i+1}']=dict(R=Rr,hits=row)
            # screenshot: hit3 active with overlay, enemy at trail edge
            await pg.evaluate("""([d,r])=>{const g=__game,h=g.hero,m=g.slimes[0];h.x=900;h.y=560;h.face=d;h.f8=d;h.atk=null;const v={right:[1,0],left:[-1,0],down:[0,1],up:[0,-1]}[d];m.dead=false;m.hp=99999;m.x=h.x+v[0]*r;m.y=h.y-8+v[1]*r*.75;
              g.startSwingForTest(2);for(let k=0;k<14;k++)g.advance(1/60);}""",[d,HB['r'][d][2]-10])
            await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
            a=Image.open(io.BytesIO(await pg.screenshot())).convert('RGB')
            hx,hy=await pg.evaluate("()=>{const h=__game.hero,k=__game.VIEW.logicalW/1280;let cx=0,cy=0;try{cx=camX;cy=camY}catch(e){};return [(h.x-cx)*k,(h.y-cy)*k]}")
            a.crop((int(hx)-420,int(hy)-420,int(hx)+420,int(hy)+360)).save(f'/workspace/review/test128_v3/hitbox_{d}.png')
            await pg.evaluate("()=>{for(let k=0;k<60;k++)__game.advance(1/60)}")
        await b.close()
    if srv:srv.terminate()
    print(json.dumps(R),'errors',errs)
asyncio.run(main())
