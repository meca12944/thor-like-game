// node cap.js <port> <out> : run right, 180° brake to left, 90° to up, 135° to down-right, walk 45° turns; screenshots around the hero
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const [port,out]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=field03`);await p.waitForFunction('window.__world&&__world.map',{timeout:30000});
await p.evaluate(()=>{__world.setManual(true)});await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5);__world.advance(1);__world.mobs.forEach(m=>m.dead=true);});
const K={R:'ArrowRight',L:'ArrowLeft',U:'ArrowUp',D:'ArrowDown'};const plan=[['R',40,1],['L',36,1],['U',30,1],['D R',36,1],['U L',30,1],['R',30,0],['U R',24,0],['U',24,0],['',30,0]];
let n=0,held=[];const info=[];
for(const [ks,F,run] of plan){await p.evaluate(([held,ks,run])=>{for(const k of held)__world.key(k,false);for(const k of ks)__world.key(k,true);__world.hero.runReq=!!run;if(!run)__world.hero.run=false;},[held,ks.split(' ').filter(Boolean).map(c=>K[c]),run]);held=ks.split(' ').filter(Boolean).map(c=>K[c]);
 for(let f=0;f<F;f++){const r=await p.evaluate(()=>{const W=__world,h=W.hero,S=W.S;W.mobs.forEach(m=>m.dead=true);if(h.moving&&h.run===false&&W.hero.runReq)W.hero.runReq=true;W.advance(1/60);return [(h.x-S.cam[0])*3+64,(h.y-S.cam[1])*3+36]});info.push(r);
  await p.screenshot({path:`${out}/${String(n++).padStart(4,'0')}.png`,clip:{x:Math.max(0,Math.min(1280-480,r[0]-240)),y:Math.max(0,Math.min(720-360,r[1]-220)),width:480,height:360}});}}
console.log(out,n,'errs',errs.slice(0,3));await b.close();})();
