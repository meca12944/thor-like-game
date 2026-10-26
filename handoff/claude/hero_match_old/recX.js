const {chromium}=require('playwright');const fs=require('fs');
const D=process.argv[2];
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto(process.argv[3]+'/test128/index.html?nosave&worldreset&noscene&go=field_felt'+(process.argv[4]||''),{waitUntil:'load'});
await p.waitForFunction(()=>window.__world&&__world.ready&&__world.map&&__world.map.id==='field_felt',null,{timeout:30000});
await p.waitForFunction(()=>!__world.trans,null,{timeout:30000});await p.waitForTimeout(3000);
await p.evaluate(()=>{const W=__world;W.setManual(true);W.killAll();W.setHeroTile(28,18,'down');W.advance(0.3);window.__mob=null;});
let n=0;const labels=[];const CW=640,CH=360;
const K={up:'ArrowUp',down:'ArrowDown',left:'ArrowLeft',right:'ArrowRight'};
async function frame(lab){const pos=await p.evaluate(()=>{const W=__world,S=W.S,h=W.hero;W.advance(1/60);return [S.view.ox+(h.x-S.cam[0])*S.view.k,S.view.oy+(h.y-S.cam[1])*S.view.k,h.inv||0,h.hp]});
 let x=Math.round(pos[0]-CW/2),y=Math.round(pos[1]-CH*0.70);x=Math.max(0,Math.min(1920-CW,x));y=Math.max(0,Math.min(1080-CH,y));
 await p.screenshot({path:D+String(n).padStart(5,'0')+'.png',clip:{x,y,width:CW,height:CH}});labels.push(lab);n++;return pos;}
async function keys(ks,down){await p.evaluate(([ks,down])=>{for(const k of ks)__world.key(k,down)},[ks,down]);}
async function reset(tx,ty,face,keepMob){await keys(Object.values(K).concat(['KeyJ','KeyK','Space']),false);await p.evaluate(([tx,ty,face,keep])=>{const W=__world;W.killAll(m=>!(keep&&m===window.__mob));W.hero.run=false;W.hero.runReq=false;W.hero.inv=0;W.hero.hp=W.hero.hpMax||50;W.hero.st=100;W.setHeroTile(tx,ty,face);W.advance(0.4);},[tx,ty,face,!!keepMob]);}
async function seg(lab,dirs,ticks,o={}){if(!o.keepFace)await reset(o.tx||28,o.ty||18,o.face||dirs[0]||'down',o.keepMob);
 const ks=dirs.map(d=>K[d]);await keys(ks,true);if(o.run)await p.evaluate(()=>{__world.hero.runReq=true});
 for(let t=0;t<ticks;t++){if(o.at&&o.at[t])await p.evaluate(c=>{__world.tap(c)},o.at[t]);await frame(lab);}
 await keys(ks,false);for(let t=0;t<(o.tail||0);t++)await frame(lab);}
await seg('달리기 →',['right'],60,{run:1,tx:14});await seg('달리기 ←',['left'],60,{run:1,tx:40});await seg('달리기 ↓',['down'],60,{run:1,ty:8});await seg('달리기 ↑',['up'],60,{run:1,ty:28});
await seg('달리기 ↘ (대각)',['down','right'],55,{run:1,tx:18,ty:10});await seg('달리기 ↗ (대각)',['up','right'],55,{run:1,tx:18,ty:26});await seg('걷기 ↖ (대각)',['up','left'],50,{tx:34,ty:24});
await seg('출발·멈춤 →',['right'],0,{tx:14});
{ await keys([K.right],true);await p.evaluate(()=>{__world.hero.runReq=true});for(let t=0;t<50;t++)await frame('출발·멈춤 →');await keys([K.right],false);for(let t=0;t<40;t++)await frame('출발·멈춤 →'); }
await seg('달리며 180° 꺾기 →←',['right'],40,{run:1,tx:22});
{ await keys([K.right],false);await keys([K.left],true);for(let t=0;t<45;t++)await frame('달리며 180° 꺾기 →←');await keys([K.left],false);for(let t=0;t<30;t++)await frame('달리며 180° 꺾기 →←'); }
await seg('달리며 90° 꺾기 →↓',['right'],40,{run:1,tx:22,ty:12});
{ await keys([K.right],false);await keys([K.down],true);for(let t=0;t<45;t++)await frame('달리며 90° 꺾기 →↓');await keys([K.down],false);for(let t=0;t<30;t++)await frame('달리며 90° 꺾기 →↓'); }
fs.writeFileSync(D+'labels.json',JSON.stringify(labels));console.log('frames',n,'errors',JSON.stringify(errs.slice(0,5)));await b.close();})();
