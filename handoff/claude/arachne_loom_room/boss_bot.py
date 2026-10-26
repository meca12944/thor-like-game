import asyncio,sys,json
from playwright.async_api import async_playwright
PORT=sys.argv[1]; BOT=open('/tmp/claude-0/-home-user-thor-like-game/9b89e068-1cf6-52f8-81a2-45cf8cb3d459/scratchpad/sim_bot.js').read()
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium');pg=await b.new_page(viewport={'width':960,'height':540});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    out=[]
    for run in range(int(sys.argv[2]) if len(sys.argv)>2 else 2):
      await pg.goto(f'http://127.0.0.1:{PORT}/index.html?nosave&worldreset&noscene&go=arachne_boss');await pg.wait_for_function('window.__world&&__world.ready&&__world.map&&__world.map.id=="arachne_boss"',timeout=90000);await pg.wait_for_timeout(1000)
      await pg.add_script_tag(content=BOT)
      r=await pg.evaluate("""()=>{const W=__world;W.setManual(true);const s=SIM.st;const adv=W.advance.bind(W);window.__far=0;window.__webs=0;window.__pil=(W.map.decos||[]).filter(d=>d.spr==='pillar').length;W.advance=dt=>{adv(dt);const m=W.S.bossRef;if(m&&!m.dead&&Math.hypot(m.x-W.hero.x,m.y-W.hero.y)>90)window.__far+=dt;if(W.S.webs)window.__webs=Math.max(window.__webs,W.S.webs.length);};for(let i=0;i<60*3;i++)SIM.tick();let far=0,webs=0,t0=s.t;
        const B=()=>W.S.bossRef; for(let k=0;k<60*400&&!(B()&&B().dead)&&!W.SAVE.flags.boss_arachne;k++){const m=B();if(!m){SIM.tick();continue;}const dx=m.x-W.hero.x,dy=m.y-W.hero.y,d=Math.hypot(dx,dy);if(d>80)far+=1/60;
          if(W.webs&&W.webs())webs=Math.max(webs,W.webs().length);if(d>70){SIM.go(Math.floor(m.x/W.map.T),Math.floor(m.y/W.map.T),60);}else SIM.fight(900);} 
        return {sec:Math.round(s.t-t0),farSec:Math.round(window.__far),pillars:window.__pil,webs:window.__webs,boss:!!W.SAVE.flags.boss_arachne||!!(B()&&B().dead),dmg:Math.round(s.dmg)}}""")
      out.append(r); print(json.dumps(r))
    print('errors',errs[:3]); await b.close()
asyncio.run(main())
