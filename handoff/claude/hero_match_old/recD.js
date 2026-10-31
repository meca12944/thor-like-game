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
await seg('걷기 ↘',['down','right'],50,{tx:22,ty:12});await seg('걷기 ↗',['up','right'],50,{tx:22,ty:24});await seg('걷기 ↙',['down','left'],50,{tx:34,ty:12});await seg('걷기 ↖',['up','left'],50,{tx:34,ty:24});
await seg('달리기 ↘',['down','right'],55,{run:1,tx:18,ty:10});await seg('달리기 ↗',['up','right'],55,{run:1,tx:18,ty:26});await seg('달리기 ↑',['up'],55,{run:1,ty:28});
for(const [d,lab,o] of [[['down','right'],'회피대시 ↘',{tx:24,ty:15}],[['up','right'],'회피대시 ↗',{tx:24,ty:21}],[['up'],'회피대시 ↑',{ty:22}]]) await seg(lab,d,8,Object.assign({at:{2:'KeyK'},tail:34},o));
await seg('점프 ↘ (걸으며)',['down','right'],8,{tx:22,ty:12,at:{2:'Space'},tail:46});await seg('점프 ↗ (걸으며)',['up','right'],8,{tx:22,ty:24,at:{2:'Space'},tail:46});
{ await reset(28,18,'down');const seq=[['right'],['down','right'],['down'],['down','left'],['left'],['up','left'],['up'],['up','right'],['right']];
  for(const d of seq){await keys(d.map(x=>K[x]),true);for(let t=0;t<5;t++)await frame('제자리 8방향 돌기');await keys(d.map(x=>K[x]),false);for(let t=0;t<16;t++)await frame('제자리 8방향 돌기');} }
fs.writeFileSync(D+'labels.json',JSON.stringify(labels));console.log('frames',n,'errors',JSON.stringify(errs.slice(0,5)));await b.close();})();
