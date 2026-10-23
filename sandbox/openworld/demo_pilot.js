// in-page autopilot used only for recording the demo
window.PIL=(()=>{const S=__sbx,K=S.K;const keys=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'];const clear=()=>keys.forEach(k=>K[k]=0);
 function steer(vx,vy){clear();const l=Math.hypot(vx,vy)||1;vx/=l;vy/=l;if(vx>.38)K.ArrowRight=1;if(vx<-.38)K.ArrowLeft=1;if(vy>.38)K.ArrowDown=1;if(vy<-.38)K.ArrowUp=1;}
 function path(tx,ty){const P=S.P,c0=Math.floor(P.x/CELL),r0=Math.floor(P.y/CELL),c1=Math.floor(tx/CELL),r1=Math.floor(ty/CELL),prev=new Int32Array(GW*GH).fill(-2),q=[r0*GW+c0];prev[q[0]]=-1;
  const ok=i=>{const x=i%GW,y=(i/GW)|0;const cx=(x+.5)*CELL,cy=(y+.5)*CELL;return !blocked(cx,cy)&&!blocked(cx-14,cy)&&!blocked(cx+14,cy)&&!blocked(cx,cy-12)&&!blocked(cx,cy+12);};
  for(let h=0;h<q.length;h++){const i=q[h];if(i===r1*GW+c1)break;const x=i%GW,y=(i/GW)|0;for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){const nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=GW||ny>=GH)continue;const j=ny*GW+nx;if(prev[j]!==-2||(!ok(j)&&j!==r1*GW+c1))continue;if(dx&&dy&&(!ok(y*GW+nx)||!ok(ny*GW+x)))continue;prev[j]=i;q.push(j);}}
  const out=[];let i=r1*GW+c1;if(prev[i]===-2)return null;while(i>=0){out.push([(i%GW+.5)*CELL,((i/GW|0)+.5)*CELL]);i=prev[i];}out.reverse();out[out.length-1]=[tx,ty];return out;}
 function go(tx,ty,run=true){return new Promise(res=>{const pts=path(tx,ty);if(!pts){console.log('nopath');res(false);return;}let k=1,stuck=0,lx=0,ly=0;S.P.run=run;
  const tick=()=>{const P=S.P;if(P.dead){clear();res(false);return;}const fo=S.foes.find(e=>e.aggro&&!e.dead&&!e.gone);if(fo&&!S.LOCK&&pi.fightOnWay){clear();fight().then(()=>{const p2=path(tx,ty);pts.length=0;pts.push(...p2);k=1;requestAnimationFrame(tick);});return;}
   while(k<pts.length-1&&Math.hypot(pts[k][0]-P.x,pts[k][1]-P.y)<26)k++;const[x,y]=pts[k];if(k>=pts.length-1&&Math.hypot(x-P.x,y-P.y)<14){clear();S.P.run=false;res(true);return;}
   steer(x-P.x,y-P.y);if(Math.hypot(P.x-lx,P.y-ly)<.2){if(++stuck>40){K.ArrowUp=!K.ArrowUp?1:0;stuck=0;}}else stuck=0;lx=P.x;ly=P.y;requestAnimationFrame(tick);};tick();});}
 function fight(maxT=60*60){return new Promise(res=>{let t=0;S.P.run=false;const tick=()=>{const P=S.P;t++;
   const live=S.foes.filter(e=>!e.dead&&!e.gone&&(e.aggro||(S.LOCK&&e.champ)));if(!live.length||P.dead||t>maxT){clear();res(!P.dead);return;}
   let e=live[0];for(const f of live)if(Math.hypot(f.x-P.x,f.y-P.y)<Math.hypot(e.x-P.x,e.y-P.y))e=f;const dx=e.x-P.x,dy=(e.y-P.y),d=Math.hypot(dx,dy);
   if((e.st==='wind'&&(e.k==='boar'?e.wt<10:e.wt<6))&&d<(e.k==='boar'?300:120)&&P.st!=='dash'&&Math.random()<.5){steer(-dy,dx);S.P.run=false;window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyK'}));window.dispatchEvent(new KeyboardEvent('keyup',{code:'KeyK'}));}
   else if(d>(e.r+60)){steer(dx,dy);}else{steer(dx,dy);if(t%7===0)S.attack();setTimeout(clear,0);}
   requestAnimationFrame(tick);};tick();});}
 const pi={go,fight,steer,clear,fightOnWay:true};return pi;})();
