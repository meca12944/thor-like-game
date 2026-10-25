// node gamecap.js <dir> : the current code slash (combo 1-3) with the hero hidden (blink trick), per tick: a = with slash, b = without -> slash layer
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const dir=process.argv[2];const out='cc_'+dir+(process.argv[3]||'');fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8790/test128/index.html?nosave&worldreset&noscene&go='+(process.argv[4]||'field_felt')+'');await p.waitForFunction('window.__world&&__world.map&&!__world.trans',{timeout:30000});
await p.evaluate(()=>{__world.setManual(true)});await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5);__world.advance(1)});
const K={right:'ArrowRight',left:'ArrowLeft',down:'ArrowDown',up:'ArrowUp'}[dir];
await p.evaluate(([dir,K])=>{const W=__world,h=W.hero,S=W.S;window.X0=h.x;window.Y0=h.y;W.mobs.forEach(o=>o.dead=true);S.hazards.length=0;h.face=dir;h.f8=dir;W.key(K,true);W.advance(1/60);W.key(K,false);W.advance(1/60);},[dir,K]);
const log=[];
for(let f=0;f<70;f++){const r=await p.evaluate(f=>{const W=__world,h=W.hero,S=W.S;h.x=X0;h.y=Y0;h.inv=0;h.hp=h.maxHp;S.hazards.length=0;const tap=(f%22===2&&f<60);if(tap)W.tap('KeyJ');W.advance(1/60);W.advance(0);
   return {tap,i:h.atk?h.atk.i:-1,t:h.atk?Math.round(h.atk.t*60):-1,gk:(S.gk||[]).length,hx:(h.x-S.cam[0])*3+64,hy:(h.y-S.cam[1])*3+36,cam:S.cam.slice()};},f);log.push(r);
 await p.screenshot({path:`${out}/${String(f).padStart(3,'0')}a.png`});
 
 
 }
fs.writeFileSync(out+'/log.json',JSON.stringify(log));console.log(dir,'errs',errs.slice(0,2),JSON.stringify(log.filter(l=>l.tap).map(l=>[l.i,l.hx,l.hy])));await b.close();})();
