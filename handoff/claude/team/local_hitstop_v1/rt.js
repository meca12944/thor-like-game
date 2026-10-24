// node rt.js <port> <sec> [video dir] : real-time mash J 30 s next to 4 felt mobs (respawned), sample every frame:
// whole-screen freeze % (S.freezeT>0), hero stop %, slow %, per-hit mob stop ticks
const {chromium}=require('playwright');(async()=>{const [port,sec,vid]=process.argv.slice(2);const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const ctx=await b.newContext({viewport:{width:1280,height:720},...(vid?{recordVideo:{dir:vid,size:{width:1280,height:720}}}:{})});const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{let s=777;Math.random=()=>(s=(s*16807)%2147483647)/2147483647;});
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=field_felt`);await p.waitForFunction('window.__world&&__world.map&&!__world.trans',{timeout:30000});
await p.evaluate(()=>{const W=__world,h=W.hero,S=W.S;W.mobs.forEach(o=>o.dead=true);window.X0=h.x;window.Y0=h.y;const ids=['c1_silmamul','c1_silmamul','c1_silmamul','c1_silmamul'];
 window.R={fr:0,frz:0,hst:0,slow:0,stops:[],hits:0,kills:0};const seen=new WeakMap();
 const spawnAll=()=>{ids.forEach((id,i)=>{const a=i*Math.PI/2+.4;const m=W.spawn(id,X0+Math.cos(a)*34,Y0+Math.sin(a)*26);m.spawnT=0;m.ours=1;});};spawnAll();
 setInterval(()=>{h.hp=h.maxHp;S.dialog=null;for(const m of S.mobs)if(!m.ours){m.dead=true;}if(!S.mobs.some(m=>!m.dead&&m.ours)){R.kills+=4;h.x=X0;h.y=Y0;spawnAll();}},100);
 const f=()=>{R.fr++;if(S.freezeT>0)R.frz++;if(S.heroStopT>0)R.hst++;if(S.lastKillT>0||S.killSlow>0)R.slow++;
  for(const m of S.mobs){if(m.stopT>0&&!seen.get(m)){seen.set(m,1);R.stops.push(Math.round(m.stopT*60));}if(!(m.stopT>0))seen.delete(m);}requestAnimationFrame(f);};requestAnimationFrame(f);});
const t0=Date.now();let k=0;while(Date.now()-t0<sec*1000){
 {const d=await p.evaluate(()=>{const W=__world,h=W.hero;let best=null,bd=1e9;for(const m of W.mobs){if(m.dead)continue;const d=Math.hypot(m.x-h.x,m.y-h.y);if(d<bd){bd=d;best=m;}}if(!best)return null;const dx=best.x-h.x,dy=best.y-h.y;return [Math.abs(dx)>Math.abs(dy)?(dx<0?'ArrowLeft':'ArrowRight'):(dy<0?'ArrowUp':'ArrowDown'),bd];});
  if(d){await p.keyboard.down(d[0]);await p.waitForTimeout(d[1]>22?120:25);await p.keyboard.up(d[0]);}}
 await p.keyboard.down('KeyJ');await p.waitForTimeout(30);await p.keyboard.up('KeyJ');await p.waitForTimeout(90);k++;}
const R=await p.evaluate(()=>R);const st={};R.stops.forEach(x=>st[x]=(st[x]||0)+1);
console.log(JSON.stringify({port,frames:R.fr,freezePct:(100*R.frz/R.fr).toFixed(1),heroStopPct:(100*R.hst/R.fr).toFixed(1),slowPct:(100*R.slow/R.fr).toFixed(1),mobStops:R.stops.length,kills:R.kills,stopTicks:st,errs:errs.slice(0,2)}));
await ctx.close();await b.close();})();
