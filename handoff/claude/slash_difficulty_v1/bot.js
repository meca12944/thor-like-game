// automated skilled player vs 3 chapter-1 felt mobs, 60 s per setting; knobs: window.__gkK (hit reach x), __gkA (arc width x)
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:960,height:540}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8793/t/index.html?nosave=1&go=field01');await p.waitForFunction('window.__world&&__world.ready&&__world.scene&&__world.scene!="town"&&__world.map',{timeout:90000});await p.waitForTimeout(2500);
const SET=JSON.parse(process.argv[2]||'[[1,1,.2,.9]]');const SEEDS=+process.argv[3]||3;
const r=await p.evaluate(([SET,SEEDS])=>{const W=__world,h=W.hero,S=W.S;W.setManual(true);(W.map.objects||[]).forEach(o=>{if(o.type==='spawn')o.respawn=1e9});W.setHeroTile(17,18);W.killAll();
 const H0=[h.x,h.y];const MAP=W.map.id;const KS=['c1_silmamul','c1_thread_puppet','c1_needle_spider','c1_unrotting_hound'];const out=[];
 const inHaz=(z,x,y)=>{if(z.shape==='circle')return Math.hypot(x-z.x,(y-z.y)*1.15)<z.r+8;if(z.shape==='line'){const vx=z.x2-z.x,vy=z.y2-z.y,L=Math.hypot(vx,vy)||1,u=((x-z.x)*vx+(y-z.y)*vy)/(L*L);if(u<-.1||u>1.1)return false;return Math.hypot(z.x+vx*u-x,z.y+vy*u-y)<z.width/2+8;}return false;};
 let rs=1;const rnd=()=>(rs=(rs*16807)%2147483647)/2147483647;
 for(const [K,A,RT,PD] of SET){window.__gkK=K;window.__gkA=A;const seenZ=new Map();let kills=0,taken=0,swings=0,time=0,hitsSafe=0,hitsAll=0;
  for(let sd=0;sd<SEEDS;sd++){rs=1234+sd*77;W.killAll();S.mobs.length=0;S.hazards.length=0;S.shots.length=0;h.x=H0[0];h.y=H0[1];h.hp=h.maxHp=50;h.inv=0;h.atk=null;h.roll=null;
   const spawnOne=k=>{const a=rnd()*6.28;const m=W.spawn(KS[k%4],H0[0]+Math.cos(a)*90,H0[1]+Math.sin(a)*70);m.spawnT=0;return m;};
   let ms=[spawnOne(sd),spawnOne(sd+1),spawnOne(sd+2)],kc=0,dodgeCd=0,lastHp=h.hp;
   const keys={};const setK=(c,v)=>{if(!!keys[c]!==v){W.key(c,v);keys[c]=v;}};
   for(let f=0;f<3600;f++){
     for(let i=0;i<ms.length;i++)if(ms[i].dead){kills++;kc++;ms[i]=spawnOne(sd+3+kc);}
     // threat check
     let dodge=null;
     for(const z of S.hazards){if(!z.dmg||z.hit)continue;if(!seenZ.has(z))seenZ.set(z,{f,roll:rnd()<PD});const sz=seenZ.get(z);const tti=z.warn-z.t;if(!sz.roll||f-sz.f<RT*60||tti<-.02||tti>.35)continue;if(inHaz(z,h.x,h.y-4)){const ox=(z.owner?z.owner.x:z.x),oy=(z.owner?z.owner.y:z.y);dodge=[h.x-ox,h.y-oy];break;}}
     if(!dodge)for(const s of S.shots){if(!seenZ.has(s))seenZ.set(s,{f,roll:rnd()<PD});const sz=seenZ.get(s);if(!sz.roll||f-sz.f<RT*60)continue;const dx=h.x-s.x,dy=(h.y-8)-s.y,d=Math.hypot(dx,dy);if(d<34&&(s.vx*dx+s.vy*dy)>0){dodge=[-s.vy,s.vx];break;}}
     const t=ms.filter(m=>!m.dead).sort((a,b)=>Math.hypot(a.x-h.x,a.y-h.y)-Math.hypot(b.x-h.x,b.y-h.y))[0];
     let ix=0,iy=0;
     if(dodge&&dodgeCd<=0&&!h.roll&&h.rollCd<=0){const L=Math.hypot(...dodge)||1;ix=dodge[0]/L;iy=dodge[1]/L;W.tap('KeyK');dodgeCd=20;}
     else if(t){const dx=t.x-h.x,dy=t.y-h.y,d=Math.hypot(dx,dy)||1,keep=52*K-6;
       if(d>keep+4){ix=dx/d;iy=dy/d;}else if(d<keep-8){ix=-dx/d;iy=-dy/d;}
       if(d<52*K+2&&f%5===0){if(Math.abs(dx)>Math.abs(dy))h.face=dx>0?'right':'left';else h.face=dy>0?'down':'up';W.tap('KeyJ');swings++;}}
     setK('KeyD',ix>.38);setK('KeyA',ix<-.38);setK('KeyS',iy>.38);setK('KeyW',iy<-.38);
     const hpB=ms.map(m=>m.hp);dodgeCd--;W.advance(1/60);time++;
     ms.forEach((m,i)=>{if(m.hp<hpB[i]){hitsAll++;const M=m.D.melee||{range:24,rad:14};if(Math.hypot(m.x-h.x,m.y-h.y)>M.range+M.rad+3)hitsSafe++;}});
     if(h.hp<lastHp)taken+=lastHp-h.hp;h.hp=50;lastHp=50;if(S.deadT>0)S.deadT=0;}
   for(const c in keys)if(keys[c])W.key(c,false);}
  out.push({reachX:K,arcX:A,react:RT,dodgeP:PD,killsPerMin:+(kills/(time/3600)).toFixed(1),dmgTakenPerMin:+(taken/(time/3600)).toFixed(1),dmgPerKill:+(taken/Math.max(1,kills)).toFixed(1),swingsPerKill:+(swings/Math.max(1,kills)).toFixed(1),safeHitPct:Math.round(hitsSafe/Math.max(1,hitsAll)*100)});}
 out.push({map:MAP});return out;},[SET,SEEDS]);
for(const o of r)console.log(JSON.stringify(o));console.log('errs',errs.slice(0,3));await b.close();})();
