// node cap.js <port> <outdir> : scenes in the arachne boss room; each frame saved; returns meta
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const [port,out]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=arachne_boss`);await p.waitForFunction('window.__world&&__world.map',{timeout:30000});
await p.evaluate(()=>{__world.setManual(true)});await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5);__world.advance(2.5)});
const info=await p.evaluate(()=>{const W=__world,S=W.S,h=W.hero,m=S.mobs.find(o=>o.D&&o.D.boss);return {boss:!!m,hx:h.x,hy:h.y,mx:m&&m.x,my:m&&m.y,map:W.map.id,dark:W.map.dark}});console.log(JSON.stringify(info));
let n=0;const shot=async(tag)=>{await p.screenshot({path:`${out}/${String(n++).padStart(4,'0')}_${tag}.png`});};
const reset=async(phase)=>p.evaluate(phase=>{const W=__world,S=W.S,h=W.hero,m=S.mobs.find(o=>o.D&&o.D.boss);S.mobs.forEach(o=>{if(o!==m)o.dead=true});S.hazards.length=0;S.shots.length=0;S.temp.length=0;S.fx.length=0;
  m.phase=phase;m.invuln=false;m.st='rest';m.restT=99;m.t=0;m.cd=99;m.hp=m.maxHp*(phase===2?.4:.9);m.x=h.x+70;m.y=h.y-10;h.inv=99;window.M=m;W.advance(1/60);},phase);
const step=async(k,tag,fr)=>{for(let i=0;i<k;i++){await p.evaluate(fr=>{const W=__world,h=W.hero;h.hp=h.maxHp;h.inv=99;if(fr)fr();W.advance(1/60);},null);await shot(tag);}};
for(const ph of [1,2]){
 // aimed threads (강철 실 봉인 telegraph): 3 lines toward the hero
 await reset(ph);await p.evaluate(()=>{const S=__world.S,h=__world.hero,m=M,a=Math.atan2(h.y-m.y,h.x-m.x);for(const s of [-.3,0,.3])S.hazards.push({shape:'line',x:m.x,y:m.y,x2:m.x+Math.cos(a+s)*170,y2:m.y+Math.sin(a+s)*170,width:6,warn:.6,act:0,dmg:0,owner:m,t:0,hit:false});});
 await step(40,`bind${ph}`);
 // cage around the hero
 await reset(ph);await p.evaluate(()=>{const S=__world.S,h=__world.hero,m=M,g0=3;for(let i=0;i<10;i++){if(i===g0||i===g0+1)continue;const b=i*Math.PI*2/10;S.temp.push({x:h.x+Math.cos(b)*40,y:h.y+Math.sin(b)*30,r:7,life:1.2,kind:'thread'});}S.hazards.push({shape:'circle',x:h.x,y:h.y,r:32,warn:1.6,act:.05,dmg:0,kind:'web',owner:m,t:0,hit:false});});
 await step(130,`cage${ph}`);
 // hero 3-hit on the boss
 await reset(ph);await p.evaluate(()=>{const h=__world.hero;M.x=h.x+34;M.y=h.y;h.face='right';h.f8='right';__world.key('ArrowRight',true);});
 for(let i=0;i<50;i++){await p.evaluate(i=>{const W=__world,h=W.hero;h.inv=99;M.x=h.x+34;M.y=h.y;if(i%14===0&&i<42)W.tap('KeyJ');W.advance(1/60);},i);await shot(`hit${ph}`);}
 await p.evaluate(()=>__world.key('ArrowRight',false));}
fs.writeFileSync(out+'/meta.json',JSON.stringify(info));console.log('errs',errs.slice(0,3));await b.close();})();
