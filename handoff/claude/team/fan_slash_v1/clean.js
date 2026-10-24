// node clean.js <port> <out> <map> <dir> <qs> : no mobs, 3-hit combo, clip around the hero
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const [port,out,map,dir,qs]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=${map}${qs||''}`);await p.waitForFunction('window.__world&&__world.map',{timeout:30000});
await p.evaluate(()=>{__world.setManual(true)});await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5);__world.advance(1)});
await p.evaluate(dir=>{const W=__world,h=W.hero,S=W.S;window.X0=h.x;window.Y0=h.y;W.mobs.forEach(o=>o.dead=true);S.hazards.length=0;h.face=dir;h.f8=dir;W.key({right:'ArrowRight',down:'ArrowDown',up:'ArrowUp'}[dir],true);W.advance(1/60);},dir);
for(let f=0;f<72;f++){const r=await p.evaluate(f=>{const W=__world,h=W.hero,S=W.S;W.mobs.forEach(o=>o.dead=true);h.x=X0;h.y=Y0;h.inv=0;h.hp=h.maxHp;S.hazards.length=0;if(f%22===2&&f<60)W.tap('KeyJ');W.advance(1/60);return [(h.x-S.cam[0])*3+64,(h.y-S.cam[1])*3+36];},f);
 await p.screenshot({path:`${out}/${String(f).padStart(3,'0')}.png`,clip:{x:Math.round(r[0]-200),y:Math.round(r[1]-200),width:400,height:300}});}
console.log(out,'errs',errs.slice(0,3));await b.close();})();
