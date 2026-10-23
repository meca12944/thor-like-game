// shared probes for the field combat: run as node probe.js <url>
const {chromium}=require('playwright');
module.exports=async function(url){const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(url);await p.waitForFunction('window.__world&&window.__game',{timeout:30000});await p.waitForTimeout(1200);
await p.evaluate(()=>{const W=__world;W.setManual(true);W.go('field00');});await p.evaluate(()=>__world.advance(2));await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5)});
const r=await p.evaluate(()=>{const W=__world,h=W.hero,S=W.S;const m=W.mobs.find(m=>!m.dead);W.mobs.forEach(o=>{if(o!==m){o.dead=true;}});
  const place=(dx,dy)=>{m.x=h.x+dx;m.y=h.y+dy+((m.D.h||20)*(m.scale||1))*.3-4;m.kx=m.ky=0;m.st='idle';m.t=0;m.cd=9;m.spawnT=0;};
  const reset=()=>{h.atk=null;h.combo=0;h.comboT=0;h.atkCd=0;h.hp=h.maxHp;h.inv=9;S.deadT=0;m.hp=m.maxHp=99999;m.dead=false;if(S.gk)S.gk.length=0;};
  const out={};
  // mash rates
  out.mash={};for(const N of [3,6,9,12,15,18,24]){reset();h.face='right';let pr=0,st=0,seq='';const hp0=m.hp;for(let f=0;f<180;f++){place(34,0);if(f%N===0){W.tap('KeyJ');pr++;}const b4=h.atk;W.advance(1/60);if(h.atk&&h.atk!==b4){st++;seq+=h.atk.i;}}out.mash[N]={pr,st,seq,dmg:hp0-m.hp,dps:Math.round((hp0-m.hp)/3)};}
  // latency: tap at f0, frames until mob hp drops, by distance
  out.lat={};for(const d of [20,30,40,50,60]){reset();h.face='right';W.advance(.2);place(d,0);const hp0=m.hp;W.tap('KeyJ');let f=0;for(;f<40;f++){place(d,0);W.advance(1/60);if(m.hp<hp0)break;}out.lat[d]=f<40?f+1:'miss';}
  // 8 directions: mob at 32px around, hero faces its current face (right) and taps with the stick held toward the mob
  out.dir={};for(let k=0;k<8;k++){reset();const a=k*Math.PI/4,dx=Math.cos(a)*32,dy=Math.sin(a)*32;h.face='right';h.f8='right';W.advance(.2);const hp0=m.hp;
     const keys=[];if(dx>5)keys.push('KeyD');if(dx<-5)keys.push('KeyA');if(dy>5)keys.push('KeyS');if(dy<-5)keys.push('KeyW');
     for(const c of keys)W.key(c,true);W.advance(1/60);for(const c of keys)W.key(c,false);place(dx,dy);W.tap('KeyJ');for(let f=0;f<30;f++){place(dx,dy);W.advance(1/60);}out.dir[k*45]=m.hp<hp0?'hit':'miss';}
  // no stick: mob off-axis 30deg at 34px while facing right
  out.offaxis={};for(const deg of [0,20,35,50,70]){reset();h.face='right';h.f8='right';W.advance(.1);const a=deg*Math.PI/180;const hp0=m.hp;place(Math.cos(a)*34,Math.sin(a)*34);W.tap('KeyJ');for(let f=0;f<30;f++){place(Math.cos(a)*34,Math.sin(a)*34);W.advance(1/60);}out.offaxis[deg]=m.hp<hp0?'hit':'miss';}
  // hitstop on hero hits: does the world freeze after a connect?
  out.freeze={};for(let i=0;i<3;i++){reset();h.face='right';W.advance(.1);place(26,0);if(i>0){h.combo=i-1;h.comboT=.2;}W.tap('KeyJ');let frz=0,last=-1;for(let f=0;f<30;f++){place(26,0);W.advance(1/60);const t=h.atk?h.atk.t:null;if(t!==null&&t===last)frz++;last=t;}out.freeze['hit'+(i+1)]=frz;}
  return out;});
await b.close();return {r,errs};};
if(require.main===module)module.exports(process.argv[2]).then(o=>console.log(JSON.stringify(o)));
