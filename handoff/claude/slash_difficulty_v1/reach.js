const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:960,height:540}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8793/t/index.html?nosave=1&go=field_felt');await p.waitForFunction('window.__world&&__world.ready&&__world.scene&&__world.scene!="town"&&__world.map',{timeout:90000});await p.waitForTimeout(2500);
const r=await p.evaluate(()=>{const W=__world,h=W.hero,S=W.S;W.setManual(true);(W.map.objects||[]).forEach(o=>{if(o.type==='spawn')o.respawn=1e9});W.killAll();S.mobs.length=0;
 const H0=[h.x,h.y];const out={map:W.map.id||'',hero:H0};
 const KS=['c1_silmamul','c1_thread_puppet','c1_needle_spider','c1_unrotting_hound'];
 for(const K of KS){const o={};
  // mob melee reach: mob held at distance d (to the right), hero still
  let maxHit=0;for(let d=18;d<=66;d+=4){W.killAll();S.mobs.length=0;S.hazards.length=0;S.shots.length=0;h.x=H0[0];h.y=H0[1];const m=W.spawn(K,h.x+d,h.y);m.spawnT=0;let hits=0;const seen=new Set();
    for(let f=0;f<480;f++){m.x=h.x+d;m.y=h.y;h.x=H0[0];h.y=H0[1];h.hp=999;h.inv=0;h.roll=null;S.shots.length=0;W.advance(1/60);for(const z of S.hazards){if(z.kind==='swipe'&&z.hit&&!seen.has(z)){seen.add(z);hits++;}}}
    if(hits>0)maxHit=d;o['m'+d]=hits;}
  o.mobMeleeReach=maxHit;
  // hero sword reach vs this mob: max d at which hit 1 connects
  let pr=0;for(let d=20;d<=80;d+=2){W.killAll();S.mobs.length=0;S.hazards.length=0;S.shots.length=0;h.x=H0[0];h.y=H0[1];h.face='right';h.f8='right';h.atk=null;h.combo=0;h.comboT=0;const m=W.spawn(K,h.x+d,h.y);m.spawnT=0;m.hp=m.maxHp=9999;
    W.tap('KeyJ');for(let f=0;f<24;f++){m.x=h.x+d;m.y=h.y;m.st='idle';m.cd=9;W.advance(1/60);}if(m.hp<9999)pr=d;}
  o.heroReach=pr;o.r=S.mobs[0]?S.mobs[0].r:0;out[K]=o;}
 return out;});
console.log(JSON.stringify(r));console.log('errs',errs.slice(0,3));await b.close();})();
