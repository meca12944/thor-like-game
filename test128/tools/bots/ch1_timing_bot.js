// usage: (cd test128 && python3 -m http.server 8931) then NODE_PATH=$(npm root -g) node test128/tools/bots/ch1_timing_bot.js
// chapter-1 timing bot: runs the game in simulated time (manual advance), walks waypoints (BFS), fights whatever comes close (J), never dies (hp topped, damage counted)
const {chromium}=require('playwright');
const BOT=`window.SIM=(()=>{const W=__world,K=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'];
 const keys=(vx,vy)=>{const l=Math.hypot(vx,vy)||1;vx/=l;vy/=l;const w={ArrowRight:vx>.38,ArrowLeft:vx<-.38,ArrowDown:vy>.38,ArrowUp:vy<-.38};for(const k of K)W.key(k,!!w[k]);};
 const stop=()=>{for(const k of K)W.key(k,false);};
 function path(tx,ty){const m=W.map,T=m.T,w=m.w,h=m.h,s=m.solidG,c0=Math.floor(W.hero.x/T),r0=Math.floor(W.hero.y/T);const prev=new Int32Array(w*h).fill(-2),q=[r0*w+c0];prev[q[0]]=-1;let best=q[0],bd=1e9;
  for(let i=0;i<q.length;i++){const p=q[i];const x=p%w,y=(p/w)|0;const d=Math.hypot(x-tx,y-ty);if(d<bd){bd=d;best=p;}if(d<.5)break;for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){const nx=x+dx,ny=y+dy,j=ny*w+nx;if(nx<1||ny<1||nx>=w-1||ny>=h-1||prev[j]!==-2||s[j])continue;prev[j]=p;q.push(j);}}
  const out=[];let i=best;while(i>=0){out.push([(i%w+.5)*T,((i/w|0)+.5)*T]);i=prev[i];}return out.reverse();}
 const st={t:0,dmg:0,kills:0,fight:0};
 function tick(){const h=W.hero;const hp0=h.hp;W.advance(1/60);st.t+=1/60;if(h.hp<hp0)st.dmg+=hp0-h.hp;if(h.hp<h.maxHp*.5)h.hp=h.maxHp;if(W.S.dialog){W.tap('KeyL');} }
 function nearMob(r){let b=null,bd=r;for(const m of W.mobs){if(m.dead||m.hp<=0)continue;const d=Math.hypot(m.x-W.hero.x,m.y-W.hero.y);if(d<bd){bd=d;b=m;}}return b;}
 function fight(r){let n=0,m;while((m=nearMob(r))&&n<60*90){const dx=m.x-W.hero.x,dy=m.y-W.hero.y,d=Math.hypot(dx,dy);if(d>22)keys(dx,dy);else{stop();if(n%12===0){keys(dx,dy);W.advance(1/60);stop();W.tap('KeyJ');}}tick();n++;st.fight+=1/60;if(m.dead||m.hp<=0)st.kills++;}stop();}
 function go(tx,ty,fr){let pts=path(tx,ty),k=0,stuck=0,lx=0,ly=0;for(let n=0;n<60*120;n++){if(fr&&nearMob(fr)){fight(fr+40);pts=path(tx,ty);k=0;}const h=W.hero;while(k<pts.length-1&&Math.hypot(pts[k][0]-h.x,pts[k][1]-h.y)<8)k++;const [x,y]=pts[k];if(k>=pts.length-1&&Math.hypot(x-h.x,y-h.y)<7){stop();return true;}keys(x-h.x,y-h.y);tick();if(Math.hypot(h.x-lx,h.y-ly)<.05){if(++stuck>120){stop();pts=path(tx,ty);k=0;stuck=0;}}else stuck=0;lx=h.x;ly=h.y;}stop();return false;}
 function look(){W.tap('KeyL');for(let i=0;i<30;i++)tick();}
 return {go,fight,look,st,tick};})();`;
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const pg=await b.newPage({viewport:{width:960,height:540}});
const res={};const run=async(name,url,fn)=>{await pg.goto('http://127.0.0.1:8931/index.html?nosave&worldreset&noscene&'+url);await pg.waitForFunction('window.__world&&__world.map&&!__world.trans',null,{timeout:40000});await pg.waitForTimeout(800);
 await pg.addScriptTag({content:BOT});await pg.evaluate(()=>__world.setManual(true));const r=await pg.evaluate(fn);res[name]=r;console.log(name,JSON.stringify(r));};
await run('A 펠트 → 들판(사슴) → 폐공방 문','go=ch1',()=>{const s=SIM.st;SIM.go(30,26,90);SIM.go(25,18,90);SIM.go(30,33,90);SIM.go(30,45,90);SIM.go(15,56,110);SIM.look();SIM.go(30,45,110);SIM.go(30,30,90);SIM.go(51,25,90);return {sec:Math.round(s.t),fight:Math.round(s.fight),kills:s.kills,dmg:s.dmg};});
await run('B 지하 1층','go=arachne',()=>{const s=SIM.st;for(const [x,y] of [[20,7],[24,17],[17,17],[7,18],[4,16],[30,5],[41,20],[42,30]]){SIM.go(x,y,110);SIM.look();}return {sec:Math.round(s.t),fight:Math.round(s.fight),kills:s.kills,dmg:s.dmg};});
await run('C 지하 2층','go=arachne&at=42,33',()=>{const s=SIM.st;__world.setHeroTile(42,33,'down');for(const [x,y] of [[24,38],[7,36],[10,50],[12,54],[30,50],[41,50],[35,56]]){SIM.go(x,y,110);SIM.look();}return {sec:Math.round(s.t),fight:Math.round(s.fight),kills:s.kills,dmg:s.dmg};});
await run('D 보스','go=arachne_boss',()=>{const s=SIM.st;for(let i=0;i<60*3;i++)SIM.tick();SIM.fight(400);return {sec:Math.round(s.t),fight:Math.round(s.fight),boss:!!__world.SAVE.flags.boss_arachne,dmg:s.dmg};});
console.log(JSON.stringify(res));await b.close();})();
