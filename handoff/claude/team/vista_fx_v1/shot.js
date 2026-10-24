// node shot.js <port> <out prefix> : phone-size shots of field_felt at zoom 1 and 0.72 + CPU x4 profile of the ash/fog functions
const {chromium}=require('playwright');(async()=>{const [port,out]=process.argv.slice(2);const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await b.newPage({viewport:{width:844,height:390},deviceScaleFactor:2});await p.addInitScript({path:'setz.js'});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=field_felt`);await p.waitForFunction('window.__world&&__world.map&&!__world.trans',{timeout:30000});
await p.evaluate(()=>{const W=__world;W.mobs.forEach(o=>o.dead=true);setInterval(()=>{W.S.dialog=null;},100);});await p.waitForTimeout(1500);
await p.screenshot({path:out+'_z100.png'});
await p.evaluate(()=>{__setZ(.72);});await p.waitForTimeout(2500);await p.screenshot({path:out+'_z072.png'});
const c=await p.context().newCDPSession(p);await c.send('Emulation.setCPUThrottlingRate',{rate:4});
const res={};for(const z of [1,.72]){await p.evaluate(z=>{__setZ(z);},z);await p.waitForTimeout(2500);
 await c.send('Profiler.enable');await c.send('Profiler.setSamplingInterval',{interval:100});await c.send('Profiler.start');
 const fr=await p.evaluate(()=>new Promise(r=>{let n=0;const t0=performance.now();const f=()=>{n++;if(performance.now()-t0<6000)requestAnimationFrame(f);else r(n);};requestAnimationFrame(f);}));
 const {profile}=await c.send('Profiler.stop');const byId={};profile.nodes.forEach(n=>byId[n.id]=n);const self={};profile.samples.forEach((id,i)=>{const n=byId[id].callFrame.functionName;self[n]=(self[n]||0)+(profile.timeDeltas[i+1]||0)/1000;});
 // total time incl. children for the two functions
 const tot={};const parent={};profile.nodes.forEach(n=>(n.children||[]).forEach(ch=>parent[ch]=n.id));
 profile.samples.forEach((id,i)=>{let x=id;const seen=new Set();while(x){const nm=byId[x].callFrame.functionName;if((nm==='drawAshFall'||nm==='drawFarFog')&&!seen.has(nm)){seen.add(nm);tot[nm]=(tot[nm]||0)+(profile.timeDeltas[i+1]||0)/1000;}x=parent[x];}});
 res['z'+z]={frames:fr,ash_ms:+(tot.drawAshFall||0).toFixed(1),fog_ms:+(tot.drawFarFog||0).toFixed(1),perFrame_ms:+(((tot.drawAshFall||0)+(tot.drawFarFog||0))/fr).toFixed(3)};}
console.log(port,JSON.stringify(res),'errs',errs.length,errs[0]||'');await b.close();})();
