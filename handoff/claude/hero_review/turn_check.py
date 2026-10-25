import asyncio, json, sys
from playwright.async_api import async_playwright
BASE=sys.argv[1]
JS = r"""async ()=>{const W=__world,S=W.S,h=W.hero,G=__game;W.setManual(true);W.killAll(()=>true);S.mobs.length=0;
 const seen=new WeakSet(); let dustN=0; const T=()=>{W.advance(1/60); for(const x of S.fx){ if(!seen.has(x)){seen.add(x); if(x.type==='dust')dustN++;} }}; const keys=new Set(); const set=(c,v)=>{W.key(c,v);};
 const rel=()=>{for(const c of ['ArrowRight','ArrowLeft','ArrowUp','ArrowDown','ShiftLeft','KeyJ'])set(c,false);};
 const D8=['right','down_right','down','down_left','left','up_left','up','up_right']; const f=()=>h.vd==null?'?':h.vd;
 const R={};
 // 1) 180 turn right -> left while walking
 rel(); set('ArrowRight',true); for(let i=0;i<40;i++)T(); set('ArrowRight',false); set('ArrowLeft',true); const seq=[]; for(let i=0;i<20;i++){T(); seq.push(f());} R.turn180=seq; rel(); for(let i=0;i<20;i++)T();
 // 2) 90 turn right -> down
 set('ArrowRight',true); for(let i=0;i<30;i++)T(); set('ArrowRight',false); set('ArrowDown',true); const s2=[]; for(let i=0;i<14;i++){T(); s2.push(f());} R.turn90=s2; rel(); for(let i=0;i<20;i++)T();
 // 3) diagonal release grace: hold right+down then release right first, down 4 ticks later
 set('ArrowRight',true);set('ArrowDown',true); for(let i=0;i<20;i++)T(); set('ArrowRight',false); const s3=[]; for(let i=0;i<4;i++){T(); s3.push(f());} set('ArrowDown',false); for(let i=0;i<8;i++){T(); s3.push(f());} R.diagRelease=s3; rel(); for(let i=0;i<20;i++)T();
 // 4) attack immediate turn: face right, input left + attack same tick
 set('ArrowRight',true); for(let i=0;i<10;i++)T(); set('ArrowRight',false); for(let i=0;i<20;i++)T(); set('ArrowLeft',true); set('KeyJ',true); T(); const a1=f(); set('KeyJ',false); T(); R.attackTurn=[a1,f()]; rel(); for(let i=0;i<60;i++)T();
 // 5) dash immediate turn
 set('ArrowRight',true); for(let i=0;i<10;i++)T(); set('ArrowRight',false); for(let i=0;i<20;i++)T(); set('ArrowLeft',true); set('ShiftLeft',true); T(); const d1=f(); set('ShiftLeft',false); T(); R.dashTurn=[d1,f(),!!h.roll]; rel(); for(let i=0;i<60;i++)T();
 // 6) dust at start / stop / land
 const dust=()=>dustN; let n0=dust(); set('ArrowRight',true); for(let i=0;i<6;i++)T(); R.dustStart=dust()-n0; for(let i=0;i<40;i++)T(); n0=dust(); set('ArrowRight',false); for(let i=0;i<8;i++)T(); R.dustStop=dust()-n0; for(let i=0;i<30;i++)T();
 h.runReq=true; set('ArrowRight',true); for(let i=0;i<40;i++)T(); n0=dust(); set('ArrowRight',false); for(let i=0;i<14;i++)T(); R.dustRunStop=dust()-n0; for(let i=0;i<30;i++)T();
 n0=dust(); set('Space',true); T(); set('Space',false); for(let i=0;i<60;i++)T(); R.dustJump=dust()-n0;
 // 7) walk->run phase keep
 set('ArrowRight',true); for(let i=0;i<23;i++)T(); const g0=h.gp; h.runReq=true; T(); T(); R.phase=[g0,h.gp]; rel(); for(let i=0;i<30;i++)T();
 // 8) attack squash/lean/step via atkTick sampling
 const kk=[]; set('KeyJ',true); T(); set('KeyJ',false); for(let i=0;i<30;i++){T(); const a=W.atkTick&&W.atkTick(); if(a) kk.push(a);} R.atkTick=kk.slice(0,30);
 return R;}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium'); pg=await b.new_page(viewport={'width':1280,'height':720}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(BASE+'/index.html?nosave&worldreset&noscene&go=field_felt'); await pg.wait_for_function('window.__world&&__world.ready&&__world.map',timeout=90000); await pg.wait_for_timeout(1500)
    await pg.evaluate("()=>{const W=__world;W.setManual(true);const q={x:23,y:21};W.setHeroTile(q.x,q.y);}")
    r=await pg.evaluate(JS); print(json.dumps(r,ensure_ascii=False)[:4000]); print(errs[:2]); await b.close()
asyncio.run(main())
