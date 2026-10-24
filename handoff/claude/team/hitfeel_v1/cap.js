// node cap.js <port> <out> <map> <mode: hit|warn>
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const [port,out,map,mode]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&go=${map}`);await p.waitForFunction('window.__world&&__world.map',{timeout:30000});
await p.evaluate(()=>{__world.setManual(true)});await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5);__world.advance(1)});
await p.evaluate(mode=>{const W=__world,h=W.hero,S=W.S;window.X0=h.x;window.Y0=h.y;W.mobs.forEach(o=>o.dead=true);S.hazards.length=0;window.MS=[];
 if(mode==='hit'){for(const [dx,dy] of [[30,0],[26,-20]]){const m=W.spawn('c1_thread_puppet',X0+dx,Y0+dy);m.spawnT=0;m.hp=m.maxHp=1e9;m.px=m.x;m.py=m.y;MS.push(m);}h.face='right';h.f8='right';W.key('ArrowRight',true);}
 W.advance(1/60);},mode);
let n=0;const info=[];
for(let f=0;f<(mode==='hit'?60:84);f++){
 if(mode==='warn'&&f%42===0)await p.evaluate(()=>{const S=__world.S,h=__world.hero;S.hazards.length=0;
   S.hazards.push({shape:'circle',x:h.x+45,y:h.y-4,r:24,warn:.66,act:.05,dmg:9,kind:'swipe',t:0,hit:false});
   S.hazards.push({shape:'line',x:h.x-80,y:h.y+34,x2:h.x+80,y2:h.y+34,width:16,warn:.66,act:.05,dmg:7,kind:'swipe',t:0,hit:false});
   S.hazards.push({shape:'ring',x:h.x-60,y:h.y-36,r:30,r0:16,warn:.66,act:.05,dmg:8,kind:'quake',t:0,hit:false});});
 const r=await p.evaluate(([f,mode])=>{const W=__world,h=W.hero,S=W.S;for(const m of MS){m.x=m.px;m.y=m.py;m.kx=m.ky=0;m.cd=9;m.st='idle';}h.x=X0;h.y=Y0;h.inv=99;h.hp=h.maxHp;if(mode==='hit'){S.hazards.length=0;if(f%15===2&&f<47)W.tap('KeyJ');}W.advance(1/60);return [(h.x-S.cam[0])*3+64,(h.y-S.cam[1])*3+36];},[f,mode]);info.push(r);
 await p.screenshot({path:`${out}/${String(n).padStart(4,'0')}a.png`});
 if(mode==='warn'){await p.evaluate(()=>{const S=__world.S;window.__hz=S.hazards.slice();S.hazards.length=0;__world.advance(0);});await p.screenshot({path:`${out}/${String(n).padStart(4,'0')}b.png`});await p.evaluate(()=>{__world.S.hazards.push(...__hz);});}
 n++;}
fs.writeFileSync(out+'/pos.json',JSON.stringify(info[0]));console.log(out,'errs',errs.slice(0,2));await b.close();})();
