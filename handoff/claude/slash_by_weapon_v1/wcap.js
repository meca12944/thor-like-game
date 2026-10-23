const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});
await p.goto('http://localhost:8790/test128/index.html');await p.waitForFunction('window.__world&&window.__game',{timeout:30000});await p.waitForTimeout(1200);
await p.evaluate(()=>{const W=__world;W.setManual(true);W.go('field00');});await p.evaluate(()=>__world.advance(2));await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5)});
const D=__dirname+'/wcap/';require('fs').mkdirSync(D,{recursive:true});let n=0;const labels=[];
const TYPES=process.argv[2]?process.argv[2].split(','):['sword','saber','dagger','greatsword','spear','whip','twin','hidden','chan','demon'];const FR=+process.argv[3]||100;
await p.evaluate(()=>{window.X0=__world.hero.x;window.Y0=__world.hero.y;});
for(const T of TYPES){await p.evaluate(T=>{const W=__world,h=W.hero,S=W.S,G=__game;Object.defineProperty(G,'weaponType',{get:()=>T,configurable:true});W.mobs.forEach(o=>o.dead=true);if(S.gk)S.gk.length=0;h.x=X0;h.y=Y0;h.atk=null;h.combo=0;h.comboT=0;h.run=false;h.face='down';h.f8='down';
  window.MS=[];const pos=[[0,30],[-22,26],[22,26],[0,52],[-30,44],[30,44],[0,76]];for(const [dx,dy] of pos){const m=W.spawn('slime',X0+dx,Y0+dy);m.spawnT=0;m.hp=m.maxHp=9999;m.px=X0+dx;m.py=Y0+dy;MS.push(m);}},T);
 for(let f=0;f<FR;f++){await p.evaluate(f=>{const W=__world,h=W.hero;for(const m of MS){m.x=m.px;m.y=m.py;m.kx=m.ky=0;m.cd=9;m.st='idle';}h.inv=0;h.hp=h.maxHp;if(f%6===0&&f<60)W.tap('KeyJ');W.advance(1/60);if(W.render)W.render();},f);
  await p.screenshot({path:D+String(n++).padStart(5,'0')+'.png'});labels.push(T);}}
require('fs').writeFileSync(D+'labels.json',JSON.stringify(labels));await b.close();})();
