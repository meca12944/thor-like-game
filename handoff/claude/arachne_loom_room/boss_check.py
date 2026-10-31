import asyncio,sys,json
from playwright.async_api import async_playwright
PORT=sys.argv[1]
STILL="""()=>{const W=__world,S=W.S,h=W.hero;W.setManual(true);const B=W.map.boss;W.killAll(()=>true);S.mobs.length=0;S.hazards.length=0;S.shots.length=0;
 const sp=W.map.spawns.default;W.setHeroTile(Math.floor(sp[0]),Math.floor(sp[1]));const m=W.spawn('arachne',B.x*W.map.T,B.y*W.map.T);S.bossRef=m;m.st='idle';m.cd=1;
 const out={};for(const ph of [1,2]){if(ph===2){m.hp=Math.floor(m.maxHp*.49);}const seq=[];let prev='',still=0,chase=0,dsum=0,n=0;
  for(let i=0;i<3600;i++){h.hp=999;h.inv=0;S.dialog=null;W.advance(1/60);n++;const d=Math.hypot(m.x-h.x,m.y-h.y);dsum+=d;
   let s=m.st;if(s==='atk'||s==='pounce'||s==='cage'||s==='ult')s=m.last||s;if(s!==prev){if(!['idle','rest','phase','intro'].includes(s))seq.push(s);prev=s;}
   if(m.st==='rest')still+=1/60;if(m.st==='idle'&&m.moving)chase+=1/60;}
  let run=1,best=1;for(let i=1;i<seq.length;i++){run=seq[i]===seq[i-1]?run+1:1;best=Math.max(best,run);}
  const kinds={};seq.forEach(k=>kinds[k]=(kinds[k]||0)+1);
  out['p'+ph]={attacks:seq.length,longestRepeat:best,openSec:+still.toFixed(1),chaseSec:+chase.toFixed(1),avgDist:Math.round(dsum/n),kinds};}
 return out}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium');pg=await b.new_page(viewport={'width':960,'height':540});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(f'http://127.0.0.1:{PORT}/index.html?nosave&worldreset&noscene&go=arachne_boss');await pg.wait_for_function('window.__world&&__world.ready&&__world.map&&__world.map.id=="arachne_boss"',timeout=90000);await pg.wait_for_timeout(1500)
    r=await pg.evaluate(STILL);print(json.dumps(r,ensure_ascii=False));print('errors',errs[:3]);await b.close()
asyncio.run(main())
