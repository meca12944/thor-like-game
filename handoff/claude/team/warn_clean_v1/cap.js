// node cap.js <port> <out> <map> <phase0|1|2> : 3 warnings (circle, line, ring) cycle twice; frames with and without warnings
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const [port,out,map,ph]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=${map}`);await p.waitForFunction('window.__world&&__world.map',{timeout:30000});
await p.evaluate(()=>{__world.setManual(true)});await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5);__world.advance(2.5)});
await p.evaluate(ph=>{const W=__world,S=W.S,h=W.hero,m=S.mobs.find(o=>o.D&&o.D.boss)||S.mobs[0];window.M=m;S.mobs.forEach(o=>{if(o!==m)o.dead=true});if(m){if(m.D.boss)m.phase=+ph||1;m.st='rest';m.restT=999;m.cd=999;m.x=h.x+110;m.y=h.y-30;if(m.D.boss)m.hp=m.maxHp*(+ph===2?.4:.9);}h.inv=999;S.hazards.length=0;W.advance(1);},ph);
let n=0;
for(let k=0;k<84;k++){
 if(k%42===0)await p.evaluate(()=>{const S=__world.S,h=__world.hero,m=M;S.hazards.length=0;
   S.hazards.push({shape:'circle',x:h.x+45,y:h.y-4,r:24,warn:.66,act:.05,dmg:9,kind:'swipe',owner:m,t:0,hit:false});
   S.hazards.push({shape:'line',x:h.x-80,y:h.y+34,x2:h.x+80,y2:h.y+34,width:16,warn:.66,act:.05,dmg:7,kind:'swipe',owner:m,t:0,hit:false});
   S.hazards.push({shape:'ring',x:h.x-60,y:h.y-36,r:30,r0:16,warn:.66,act:.05,dmg:8,kind:'quake',owner:m,t:0,hit:false});});
 await p.evaluate(()=>{const W=__world,h=W.hero;h.inv=999;h.hp=h.maxHp;if(M){M.st='rest';M.restT=999;M.cd=999;}W.advance(1/60);});
 await p.screenshot({path:`${out}/${String(n).padStart(4,'0')}a.png`});
 await p.evaluate(()=>{const S=__world.S;window.__hz=S.hazards.slice();S.hazards.length=0;__world.advance(0);});
 await p.screenshot({path:`${out}/${String(n).padStart(4,'0')}b.png`});
 await p.evaluate(()=>{const S=__world.S;S.hazards.push(...__hz);});n++;}
console.log(out,'errs',errs.slice(0,3));await b.close();})();
