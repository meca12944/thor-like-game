const {chromium}=require('playwright');(async()=>{for(const v of ['base','new']){const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});
await p.goto(`http://localhost:8792/${v}/index.html`);await p.waitForFunction('window.__world&&window.__game',{timeout:30000});await p.waitForTimeout(1200);
await p.evaluate(()=>{const W=__world;W.setManual(true);W.go('field00');});await p.evaluate(()=>__world.advance(2));await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5)});
const r=await p.evaluate(()=>{const W=__world,h=W.hero,S=W.S;const out={};const X0=h.x,Y0=h.y;
 for(const N of [4,8,12,999]){W.mobs.forEach(o=>o.dead=true);h.x=X0;h.y=Y0;h.roll=null;h.atk=null;h.combo=0;h.comboT=0;h.atkCd=0;h.hp=h.maxHp;h.inv=99;h.face='down';h.run=true;
  const x0=h.x,y0=h.y;const ms=[];for(let k=0;k<12;k++){const m=W.spawn('slime',x0,y0+50+k*45);m.spawnT=0;m.hp=m.maxHp=30;ms.push(m);}
  W.key('KeyS',true);let seq='',st=0,hits=0;const t0=S.t;
  for(let f=0;f<240;f++){for(const [k,m] of ms.entries()){m.cd=9;m.st='idle';m.x=x0;m.kx=0;}h.run=true;if(f%N===0)W.tap('KeyJ');const b4=h.atk;W.advance(1/60);if(h.atk&&h.atk!==b4){st++;seq+=h.atk.i;}h.inv=99;}
  W.key('KeyS',false);out[N]={seq,started:st,kills:ms.filter(m=>m.dead).length,dist:Math.round(h.y-y0)};}
 return out;});
console.log(v,JSON.stringify(r));await b.close();}})();
