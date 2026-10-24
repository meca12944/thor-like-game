// node run.js <port> <mode: shot|prof|vid>
const {chromium}=require('playwright');(async()=>{const [port,mode]=process.argv.slice(2);const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const ctx=await b.newContext({viewport:{width:1280,height:720},...(mode==='vid'?{recordVideo:{dir:'vid',size:{width:1280,height:720}}}:{})});const p=await ctx.newPage();await p.addInitScript({path:'put.js'});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=field_felt`);await p.waitForFunction('window.__world&&__world.map&&!__world.trans',{timeout:30000});
await p.evaluate(()=>{const W=__world;W.mobs.forEach(o=>o.dead=true);setInterval(()=>{W.S.dialog=null;},100);});
if(mode==='prof'){const c=await ctx.newCDPSession(p);await c.send('Emulation.setCPUThrottlingRate',{rate:4});const out={};
 for(const on of [0,1]){if(on)await p.evaluate(()=>__putSfx());await p.waitForTimeout(2000);await c.send('Profiler.enable');await c.send('Profiler.setSamplingInterval',{interval:100});await c.send('Profiler.start');
  const fr=await p.evaluate(()=>new Promise(r=>{let n=0;const t0=performance.now();const f=()=>{n++;if(performance.now()-t0<6000)requestAnimationFrame(f);else r(n);};requestAnimationFrame(f);}));
  const {profile}=await c.send('Profiler.stop');const byId={},par={};profile.nodes.forEach(n=>{byId[n.id]=n;(n.children||[]).forEach(ch=>par[ch]=n.id);});let t=0;
  profile.samples.forEach((id,i)=>{let x=id;while(x){if(byId[x].callFrame.functionName==='drawSceneObjs'){t+=(profile.timeDeltas[i+1]||0)/1000;break;}x=par[x];}});out[on?'on':'off']={frames:fr,ms:+t.toFixed(1),perFrame:+(t/fr).toFixed(3)};}
 console.log(JSON.stringify(out),'errs',errs.length,errs[0]||'');}
if(mode==='shot'){await p.evaluate(()=>__putSfx());await p.waitForTimeout(1500);await p.screenshot({path:'all.png'});console.log('errs',errs.length,errs[0]||'');}
if(mode==='vid'){await p.evaluate(()=>__putSfx());await p.waitForTimeout(3000);for(const k of ['ArrowLeft','ArrowUp','ArrowRight','ArrowDown']){await p.keyboard.down(k);await p.waitForTimeout(900);await p.keyboard.up(k);await p.waitForTimeout(600);}await p.waitForTimeout(1500);}
await ctx.close();await b.close();})();
