import asyncio,json,sys
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium');pg=await b.new_page(viewport={'width':960,'height':540})
    res=[]
    for hide in [True,False,True,False]:
      await pg.goto(f'http://127.0.0.1:{sys.argv[1]}/index.html?nosave&worldreset&noscene&go=arachne_boss');await pg.wait_for_function('window.__world&&__world.ready&&__world.map&&__world.map.id=="arachne_boss"',timeout=90000);await pg.wait_for_timeout(800)
      r=await pg.evaluate("""(hide)=>{const W=__world,S=W.S,h=W.hero;W.setManual(true);let m=null;
        for(let i=0;i<60*120;i++){S.dialog=null;h.hp=h.maxHp;h.inv=Math.max(h.inv,1);W.advance(1/60);m=S.bossRef;if(m&&m.phase===1&&m.st==='idle'&&m.hp>m.maxHp*.5)m.hp=Math.floor(m.maxHp*.49);if(m&&m.st==='ult')break;}
        if(!m||m.st!=='ult')return {err:'no ult',st:m&&m.st};
        const P=W.map.decos.filter(d=>d.spr==='pillar');let best=null,bd=1e9;for(const d of P){const dd=Math.hypot(d.x-m.x,d.y-m.y);if(dd<bd&&dd>60){bd=dd;best=d;}}
        const vx=best.x-m.x,vy=best.y-6-m.y,L=Math.hypot(vx,vy),ux=vx/L,uy=vy/L;
        const hx=hide?best.x+ux*24:best.x+uy*60, hy=hide?best.y+uy*24:best.y-ux*60; h.x=hx;h.y=hy;h.inv=0;h.hp=h.maxHp;const hp0=h.hp;
        for(let i=0;i<60*4&&m.st==='ult';i++){S.dialog=null;h.inv=0;h.roll=null;W.advance(1/60);h.x=hx;h.y=hy;}
        return {hide,dmg:hp0-h.hp,maxHp:h.maxHp}}""",hide)
      res.append(r)
    print(json.dumps(res)); await b.close()
asyncio.run(main())
