// node hitgrid.js <map> <dir> <json cfg> <out.json> : dummy 실마물 on a grid (16 passes, 16px apart so they don't shove each other),
// hold the direction (no auto-aim), 3-hit combo, record which swing hit which spot = game truth
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const [map,dir,cfg,outp]=process.argv.slice(2);const K=JSON.parse(cfg);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1280,height:720}});
await p.goto(`http://localhost:8794/t/index.html?nosave&worldreset&go=${map}`);await p.waitForFunction('window.__world&&window.__world.map',{timeout:30000});
await p.evaluate(()=>{__world.setManual(true)});await p.evaluate(()=>{for(let i=0;i<20&&__world.trans;i++)__world.advance(.5);__world.advance(.5)});
await p.evaluate(()=>{window.X0=__world.hero.x;window.Y0=__world.hero.y;});const all=[];let meta;
for(let ox=0;ox<16;ox+=4)for(let oy=0;oy<16;oy+=4){
const res=await p.evaluate(([k,dir,ox,oy])=>{const W=__world,h=W.hero,S=W.S;Object.assign(window,{__gkDY:k.dy||0,__gkDYu:k.dyu||0,__gkDYd:k.dyd||0,__gkSPAN:k.span||1,__gkSQ:k.sq||null,__gkShapeHit:!!k.shape,__gkShapeA:k.shapeA||11,__gkShapeM:k.shapeM??6,__gkShapeCap:!!k.cap,__gkStop:!!k.stop});
 W.mobs.forEach(o=>o.dead=true);S.gk=[];S.gkImp=[];S.hazards&&(S.hazards.length=0);const MS=[];
 for(let mx=-72+ox;mx<=72;mx+=16)for(let my=-60+oy;my<=60;my+=16){if(Math.abs(mx)<10&&Math.abs(my)<8)continue;const m=W.spawn('c1_silmamul',X0+mx,Y0+my);m.spawnT=0;m.hp=m.maxHp=1e9;m.px=X0+mx;m.py=Y0+my;m.gx=mx;m.gy=my;m.hm=0;MS.push(m);}
 h.x=X0;h.y=Y0;h.atk=null;h.combo=0;h.comboT=0;h.run=false;h.face=dir;h.f8=dir;const KC={right:'ArrowRight',left:'ArrowLeft',up:'ArrowUp',down:'ArrowDown'}[dir];W.key(KC,true);
 for(let f=0;f<60;f++){for(const m of MS){m.x=m.px;m.y=m.py;m.kx=m.ky=0;m.cd=9;m.st='idle';m.dead=false;}h.inv=9;h.hp=h.maxHp;h.x=X0;h.y=Y0;S.hazards&&(S.hazards.length=0);if(f%14===0&&f<42)W.tap('KeyJ');W.advance(1/60);
  for(const g of S.gk||[])for(const m of g.hit)m.hm|=1<<g.i;}
 W.key(KC,false);W.advance(.5);
 return {pad:MS[0].r+(MS[0].D.h||20)*(MS[0].scale||1)*.2,r:MS[0].r,h:(MS[0].D.h||20)*(MS[0].scale||1),list:MS.map(m=>[m.gx,m.gy,m.hm])};},[K,dir,ox,oy]);
 meta=res;all.push(...res.list);}
meta.list=all;fs.writeFileSync(outp,JSON.stringify(meta));console.log('pad',meta.pad,'r',meta.r,'h',meta.h,'n',all.length,'hit',[0,1,2].map(i=>all.filter(x=>x[2]>>i&1).length));await b.close();})();
