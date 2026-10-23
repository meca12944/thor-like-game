const {chromium}=require('playwright');(async()=>{const url=process.argv[2];const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(url);await p.waitForFunction('window.__world&&window.__game',{timeout:30000});await p.waitForTimeout(1200);
await p.evaluate(()=>{const W=__world;W.setManual(true);W.go('field00');});await p.evaluate(()=>__world.advance(2));await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5)});
const r=await p.evaluate(()=>{const W=__world,h=W.hero,S=W.S,G=__game;const X0=h.x,Y0=h.y;const out={};
 const TYPES=['sword','saber','dagger','greatsword','spear','whip','twin','hidden','chan','demon'];
 const clear=()=>{W.mobs.forEach(o=>o.dead=true);if(S.gk)S.gk.length=0;S.freezeT=0;h.x=X0;h.y=Y0;h.atk=null;h.combo=0;h.comboT=0;h.atkCd=0;h.roll=null;h.face='down';h.f8='down';h.hp=h.maxHp;h.run=false;h.moving=false;h.skidT=0;};
 const mk=(dx,dy,hp)=>{const m=W.spawn('slime',X0+dx,Y0+dy);m.spawnT=0;m.hp=m.maxHp=hp;m.px=X0+dx;m.py=Y0+dy;return m;};
 const hold=ms=>{for(const m of ms){if(m.dead)continue;m.x=m.px;m.y=m.py;m.kx=m.ky=0;m.cd=9;m.st='idle';}h.inv=9;h.hp=h.maxHp;};
 const mash=(ms,frames,N=4)=>{let st=0;for(let f=0;f<frames;f++){hold(ms);if(f%N===0)W.tap('KeyJ');const b4=h.atk;W.advance(1/60);if(h.atk&&h.atk!==b4)st++;}return st;};
 for(const T of TYPES){Object.defineProperty(G,'weaponType',{get:()=>T,configurable:true});const o={};
  clear();let ms=[mk(0,30,1e5)];let hp0=ms[0].hp;o.atk=mash(ms,180);o.single=Math.round(hp0-ms[0].hp);
  clear();ms=[];for(let k=0;k<6;k++){const a=(-60+k*24)*Math.PI/180;ms.push(mk(Math.sin(a)*34,Math.cos(a)*34,1e5));}mash(ms,180);o.crowd=Math.round(ms.reduce((s,m)=>s+(1e5-m.hp),0));o.crowdN=ms.filter(m=>m.hp<1e5).length;
  clear();ms=[];for(let k=0;k<5;k++)ms.push(mk(0,26+k*16,1e5));mash(ms,180);o.line=Math.round(ms.reduce((s,m)=>s+(1e5-m.hp),0));o.lineN=ms.filter(m=>m.hp<1e5).length;
  clear();ms=[mk(0,62,1e5)];mash(ms,180);o.far=Math.round(1e5-ms[0].hp);
  clear();ms=[];for(let k=0;k<12;k++){const m=mk(0,50+k*34,40);ms.push(m);}W.key('KeyS',true);for(let f=0;f<240;f++){for(const m of ms){if(!m.dead){m.x=m.px;m.cd=9;m.st='idle';}}h.inv=9;h.run=true;if(f%5===0)W.tap('KeyJ');W.advance(1/60);}W.key('KeyS',false);o.runKills=ms.filter(m=>m.dead).length;o.runDist=Math.round(h.y-Y0);
  out[T]=o;}
 return out;});
console.log(JSON.stringify(r));console.log('errs',errs.slice(0,3));await b.close();})();
