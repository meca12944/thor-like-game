// node cap.js <port> <out> <map> <dir> <qs> : 3 dummy mobs ahead, 3-hit combo; frames with and without the slash + per-frame mob hit log
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const [port,out,map,dir,qs]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=${map}${qs||''}`);await p.waitForFunction('window.__world&&__world.map',{timeout:30000});
await p.evaluate(()=>{__world.setManual(true)});await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5);__world.advance(1)});
await p.evaluate(dir=>{const W=__world,h=W.hero,S=W.S;window.X0=h.x;window.Y0=h.y;W.mobs.forEach(o=>o.dead=true);S.hazards.length=0;const V={right:[1,0],down:[0,1],up:[0,-1]}[dir],N=[-V[1],V[0]];window.MS=[];
 for(const [f,s] of [[16,0],[22,-14],[26,10]]){const m=W.spawn('c1_silmamul',X0+V[0]*f+N[0]*s,Y0+V[1]*f+N[1]*s);m.spawnT=0;m.hp=m.maxHp=1e9;m.px=m.x;m.py=m.y;MS.push(m);}
 h.face=dir;h.f8=dir;W.key({right:'ArrowRight',down:'ArrowDown',up:'ArrowUp'}[dir],true);W.advance(1/60);},dir);
const log=[];
for(let f=0;f<72;f++){const r=await p.evaluate(f=>{const W=__world,h=W.hero,S=W.S;for(const m of MS){m.x=m.px;m.y=m.py;m.kx=m.ky=0;m.cd=9;m.st='idle';}h.x=X0;h.y=Y0;h.inv=99;h.hp=h.maxHp;S.hazards.length=0;const hp0=MS.map(m=>m.hp);const tap=(f%22===2&&f<60);if(tap)W.tap('KeyJ');W.advance(1/60);
   return {tap,hit:MS.map((m,i)=>m.hp<hp0[i]?1:0),hx:(h.x-S.cam[0])*3+64,hy:(h.y-S.cam[1])*3+36,gk:(S.gk||[]).length};},f);log.push(r);
 await p.screenshot({path:`${out}/${String(f).padStart(3,'0')}a.png`});
 await p.evaluate(()=>{const S=__world.S;window.__sv=[S.gk,S.gkImp];S.gk=[];__world.advance(0);});
 await p.screenshot({path:`${out}/${String(f).padStart(3,'0')}b.png`});
 await p.evaluate(()=>{const S=__world.S;[S.gk,S.gkImp]=__sv;});}
fs.writeFileSync(out+'/log.json',JSON.stringify(log));console.log(out,'errs',errs.slice(0,3));await b.close();})();
