// [town_a] 시작 마을 A — multi-screen town map runtime (tools/town_a/build_town_a.py -> assets/level.json "ta" + assets/town_a/*).
// Loaded BEFORE the main script; every hook is called lazily by the engine (window.TOWN_A.*), so engine globals
// (hero, LVL, keys, TALK, spawnNpc, ...) are only touched at call time.
(function(){
'use strict';
const BASE='assets/town_a/';
const IM={};let rooms=null,TA=null,curRoom=null,fade=null,banner=null,inited=false,lastRoomId=null;
const SKEY='townA.v1';let SV={opened:[],flags:{}};
function persist(){try{if(!(typeof Q!=='undefined'&&Q.has('nosave')))localStorage.setItem(SKEY,JSON.stringify(SV));}catch(e){}}
function loadSave(){try{if(typeof Q!=='undefined'&&Q.has('nosave'))return;const v=JSON.parse(localStorage.getItem(SKEY)||'null');if(v&&Array.isArray(v.opened))SV=Object.assign({opened:[],flags:{}},v);}catch(e){}}
function ta(){if(!TA&&typeof LVL!=='undefined'&&LVL.ta){TA=LVL.ta;rooms=TA.rooms;for(const r of rooms){const g=r.grid;if(g){const s=atob(g.b64),b=new Uint8Array(s.length);for(let i=0;i<s.length;i++)b[i]=s.charCodeAt(i);g.bits=b;}}}return TA;}
function img(src){return new Promise(res=>{const i=new Image();i.onload=()=>res(i);i.onerror=()=>res(null);i.src=BASE+src;});}
function load(){ta();const jobs=[];
 for(const k in TA.imgs)jobs.push(img(TA.imgs[k].src).then(i=>{IM[k]=i;}));
 for(const r of rooms){if(r.bg)for(const c of r.bg)jobs.push(img(c.src).then(i=>{c.im=i;}));if(r.bgimg)jobs.push(img(TA.imgs[r.bgimg].src).then(i=>{r.im=i;}));}
 jobs.push(img(TA.minimap.src).then(i=>{IM._mini=i;}));
 return Promise.all(jobs);}
function roomAt(x,y){if(!ta())return null;for(const r of rooms)if(x>=r.x0&&x<r.x1&&y>=r.y0&&y<r.y1)return r;return null;}
function room(){const r=roomAt(hero.x,hero.y)||curRoom||rooms[0];curRoom=r;return r;}
function blockedPt(x,y){const r=roomAt(x,y);if(!r)return true;const g=r.grid;if(!g)return false;
 const cx=((x-r.x0)/g.cell)|0,cy=((y-r.y0)/g.cell)|0;if(cx<0||cy<0||cx>=g.w||cy>=g.h)return true;const i=cy*g.w+cx;return (g.bits[i>>3]>>(7-(i&7)))&1;}
function inView(x,y,w,h,m=60){return x+w>camX-m&&x<camX+viewW+m&&y+h>camY-m&&y<camY+viewH+m;}
function ground(c){ta();const sm=c.imageSmoothingEnabled;c.imageSmoothingEnabled=true;
 for(const r of rooms){if(!inView(r.x0,r.y0,r.x1-r.x0,r.y1-r.y0,0))continue;
  if(r.bg){for(const k of r.bg)if(k.im&&inView(k.x,k.y,k.w,k.h,4))c.drawImage(k.im,k.x,k.y,k.w+.6,k.h+.6);}
  else if(r.im)c.drawImage(r.im,r.x0,r.y0,r.x1-r.x0,r.y1-r.y0);}
 c.imageSmoothingEnabled=sm;}
function layers(L){ta();for(const o of TA.overlays){if(!inView(o.x,o.y,o.w,o.h))continue;let k=o.img;
  if(o.tag&&SV.opened.includes(o.tag))k=k==='basket'?'basket':'chest_open';const im=IM[k];if(!im)continue;
  L.push({y:o.sortY,ov:1,f:()=>ctx.drawImage(im,o.x,o.y,o.w,o.h)});}}
// ---------------- interactables ----------------
function itName(id){const d=typeof IT!=='undefined'&&IT[id];return (d&&(d.n||d.name))||id;}
function give(items){const got=[];for(const[id,n]of items){if(typeof IT!=='undefined'&&IT[id]){if(invAdd(id,n)!==false){dropNote(id,n);got.push(itName(id)+' ×'+n);}}else got.push(id+' ×'+n);}return got;}
function chestReady(c){if(!c.need)return true;if(c.need==='bomb')return invCount('bomb')>0||invCount('o_ore_pick')>0;
 if(c.need==='earth_crystal'){try{return !!(window.__world&&__world.SAVE&&__world.SAVE.flags&&__world.SAVE.flags.boss01);}catch(e){return false;}}return !!SV.flags[c.need];}
const SPOT_TEXT={
 cradle:['낡은 버들 바구니다. 스무 해 전, 광장 분수 곁에서 이 바구니에 담긴 갓난아기가 발견되었다… 바로 너다.','바구니 바닥에 물에 번진 글씨가 남아 있지만 읽을 수 없다.'],
 taxbox:['촌장의 세금 상자다. 묵직한 자물쇠가 걸려 있고, 낡은 장부가 함께 묶여 있다.','표지에 「요람의 장부」라고 적혀 있다. 몇 장이 찢겨 나갔다. (A9 「촌장의 세금 상자」)'],
 scroll:['도장 벽의 족자. 「발을 멈추지 마라. 막지 말고 굴러라.」 — 사범 바렌의 글씨다.'],
 letter:['책상 위에 쓰다 만 편지가 있다. 「…오늘 밤, 그 아이의 집을 찾아가야 한다. 무엇을 쥐고 갈지는 아직 정하지 못했다.」'],
 grate:['분수 뒤 하수로 입구다. 녹슨 쇠창살 너머로 물소리가 울린다.','「종이 울리면 아이들은 하수로로」 — 엘스베트가 늘 하던 말이다.'],
 bell:['마을의 경종. 마왕이 오던 날 밤, 이 종이 울릴 것이다.','기둥에 「종이 울리면 분수 뒤 하수로로」라고 새겨져 있다.'],
 notice:['광장 게시판.','「뿔토끼가 밭을 망칩니다 — 하로」 「약초 배달 구함 — 세레스」 「남문 밖 바람길, 해 지기 전에 돌아올 것 — 경비 베른」'],
 alley:['촌장 집 뒷골목. 스무 번째 생일 밤, 이 골목 끝에서 무언가를 보았다.'],
 nest:['엘스베트 집 담장 위의 까치둥지. 무언가 반짝이는 것을 물어다 놓은 것 같다.'],
};
let HOT=[];
function buildHot(){ta();HOT=[];const sp=k=>{for(const r of rooms)if(r.spots&&r.spots[k])return r.spots[k];return null;};
 for(const c of TA.chests)HOT.push({id:'chest:'+c.id,x:c.x,y:c.y-6,r:c.id==='a_chest_tak'?150:70,c});
 for(const s of TA.spots)HOT.push({id:'toy:'+s.id,x:s.x,y:s.y,r:s.r,s});
 for(const k of ['cradle','taxbox','scroll','letter']){const p=sp(k);if(p)HOT.push({id:'spot:'+k,x:p[0],y:p[1]+20,r:70});}
 HOT.push({id:'spot:grate',x:777,y:272,r:60},{id:'spot:bell',x:1240,y:262,r:70},{id:'spot:notice',x:1150,y:265,r:60},{id:'spot:alley',x:870,y:-860,r:110},{id:'spot:nest',x:1560,y:-740,r:90});
 for(const d of TA.doors){if(d.kind==='trap')HOT.push({id:'trap:'+d.id,x:d.x,y:d.y,r:56,d});else if(d.locked)HOT.push({id:'locked:'+d.id,x:d.x,y:d.y+24,r:46,d});}}
function nearHot(){let b=null,bd=1e9;for(const h of HOT){const d=Math.hypot(hero.x-h.x,(hero.y-h.y)*1.2);if(d<h.r&&d<bd){bd=d;b=h;}}return b;}
function npcNear(){let b=null,bd=110;for(const n of NPCS){if(n.dead||n.fainted>0||n.alert>0)continue;const d=Math.hypot(hero.x-n.x,hero.y-n.y);if(d<bd){bd=d;b=n;}}return b;}
function pick(){const n=npcNear(),h=nearHot();if(n&&h){const dn=Math.hypot(hero.x-n.x,hero.y-n.y),dh=Math.hypot(hero.x-h.x,(hero.y-h.y)*1.2);return dh<dn?{h}:{n};}return n?{n}:h?{h}:{};}
function say(id,name,lines,then,por){TALK[id]={name,por,lines:lines.map(l=>typeof l==='function'?l:()=>l),then};dlg={id,i:0};openUI('dialog');}
function useHot(h){const k=h.id.split(':')[0];
 if(k==='chest'){const c=h.c,id='ta_chest';
  if(SV.opened.includes(c.id)){say(id,'보물상자',['이미 열어 본 상자다.']);return;}
  if(!chestReady(c)){say(id,c.id==='a_chest_tak'?'금빛 사슬 상자':'?',[c.msg||'아직 열 수 없다.']);return;}
  const got=give(c.items);SV.opened.push(c.id);persist();SFX&&SFX.ev&&SFX.ev.pickup&&SFX.ev.pickup();
  say(id,c.kind==='hidden'?'반짝이는 것':'보물상자',[(c.kind==='hidden'?'벤치 밑에서 무언가를 찾았다! ':'상자를 열었다! ')+got.join(', ')]);return;}
 if(k==='toy'){const s=h.s,f=SV.flags;if(f[s.id]){say('ta_toy','나무 장난감',['이미 찾은 자리다.']);return;}
  f[s.id]=1;persist();const n=['a3_toy_1','a3_toy_2','a3_toy_3'].filter(t=>f[t]).length;
  say('ta_toy','토비의 보물지도',[`${s.where}에서 토비의 나무 장난감을 찾았다! (${n}/3)`,n>=3?'세 개 모두 찾았다. 토비에게 가져다주자.':'지도에 표시된 곳이 더 남아 있다.']);return;}
 if(k==='spot'){const t=SPOT_TEXT[h.id.slice(5)];say('ta_spot','조사',t);return;}
 if(k==='trap'){go(h.d.to,h.d.inside,'up');return;}
 if(k==='locked'){say('ta_spot',h.d.label,[h.d.locked]);return;}}
// ---------------- NPCs ----------------
const NPCS=[];let SM=null,SMITH=null;
const NAMES={a_chief:'오스왈드 · 촌장',a_granny:'엘스베트 · 분수지기',a_kid:'토비',a_guard:'베른 · 경비병',a_farmer:'하로 · 농부',a_herb:'세레스 · 약초꾼',a_bard:'라우렌 · 음유시인',a_smith:'브란트 · 대장간',sm_A:'바렌 · 사범'};
function npcTalk(n){const id=n.id,T=TA.talk&&TA.talk[id];
 if(id==='sm_A'){say('ta_npc','바렌 · 사범',[
  ()=>'왔느냐. 검은 휘두르는 것이 아니라 흘려보내는 것이다.',
  ()=>`${keyLabel('attack')} 로 베고, ${keyLabel('dash')} 로 굴러라. 구르는 동안엔 칼끝이 닿지 않는다. 발을 멈추지 마라. 막지 말고 굴러라.`,
  ()=>`${keyLabel('target')} 로 노릴 상대를 바꿔라. 눈이 가는 곳으로 칼이 간다.`,
  ()=>'마당의 슬라임들은 내가 길들인 연습 상대다. 마음껏 베어라, 금세 다시 기어 나온다.',
  ()=>'숲으로 가려거든 남문으로 나가 바람길을 따라라. 지도를 펼치면('+keyLabel('map',1)+') 길이 보인다.'],null,'sm_A');return;}
 if(id==='a_kid'){const f=SV.flags,n3=['a3_toy_1','a3_toy_2','a3_toy_3'].every(t=>f[t]);
  if(n3&&!f.a3_done){f.a3_done=1;persist();const got=give([['heart_piece',1]]);say('ta_npc','토비',['우와, 내 장난감 전부 찾아 줬어?! 형 최고!','이거, 내 보물이야. 줄게! — '+got.join(', ')],null,'a_kid');return;}
  if(!f.a3_got){f.a3_got=1;persist();say('ta_npc','토비',['형! 내 보물지도 봐 봐. 나무 장난감을 세 군데 숨겨 놨는데… 어디 뒀는지 까먹었어.','대장간 뒤, 촌장님네 울타리, 분수 꽃밭! 찾아 주면 내 보물 줄게!'],null,'a_kid');return;}}
 const lines=(T&&T.lines.map(l=>l[1]))||['…'];
 if(id==='a_smith'){say('ta_npc',NAMES[id],lines.slice(0,2),()=>{openShop('a_smith');invTab=2;renderUI();},'a_smith');return;}
 say('ta_npc',NAMES[id]||id,lines,null,id);}
function spawnAll(){const N=TA.npcs;
 for(const id in N){const p=N[id];const path=Array.isArray(p[0])?p:null;const[x,y]=path?p[0]:p;
  const n=spawnNpc(id,x,y,id==='a_kid'?{child:true,h:92}:{h:id==='sm_A'?134:120});if(path){n.path=path.map(q=>q.slice());n.seg=0;}n.taTalk=1;NPCS.push(n);if(id==='sm_A')SM=n;}
 const I=TA.inside;SMITH=spawnNpc('a_smith',I.a_smith[0],I.a_smith[1],{h:124});SMITH.taTalk=1;NPCS.push(SMITH);
 if(shopNpc){shopNpc.x=I.a_tool[0];shopNpc.y=I.a_tool[1];shopNpc.path=null;}
 if(typeof SHOP_NAMES!=='undefined')SHOP_NAMES.a_smith='브란트의 대장간';}
let nabiMoved=false;
function moveNabi(){if(nabiMoved||!window.__tachie||!__tachie.nabi)return;const n=__tachie.nabi,p=TA.inside.a_tailor;n.x=p[0];n.y=p[1];n.path=[[p[0]-60,p[1]],[p[0]+60,p[1]]];n.seg=0;n._px=n.x;n._py=n.y;nabiMoved=true;}
// ---------------- doors / rooms ----------------
function go(to,pos,face){if(fade)return;fade={t:0,to,pos,face,done:false};}
function doTeleport(f){hero.x=f.pos[0];hero.y=f.pos[1];hero.face=f.face||'up';hero.vx=hero.vy=0;hero.kx=hero.ky=0;hero._px=hero.x;hero._py=hero.y;hero.dash=null;hero.atk=null;
 camInit=false;const r=roomAt(hero.x,hero.y);if(r)curRoom=r;}
function update(dt){if(!ta()||!inited)return;moveNabi();
 if(fade){fade.t+=dt;if(!fade.done&&fade.t>=.2){fade.done=true;doTeleport(fade);}if(fade.t>=.45)fade=null;return;}
 const r=room();
 if(r.id!==lastRoomId){if(lastRoomId!==null)banner={t:2.2,text:r.name};lastRoomId=r.id;}
 if(banner&&(banner.t-=dt)<=0)banner=null;
 const busy=uw||hero.swim||hero.sk||hero.atk||hero.dash;
 if(!busy){
  if(r.id==='out'){for(const d of TA.doors){if(!d.to||d.kind==='trap')continue;
    if(Math.abs(hero.x-d.x)<d.w/2+8&&hero.y>=d.y-4&&hero.y<d.y+(d.reach||40)&&hero.face==='up'&&(keys.up||hero.vy<-1||hero.moving)){go(d.to,d.inside,'up');try{SFX.ev.blip();}catch(e){}return;}}}
  else if(r.exit){const e=r.exit;if(Math.abs(hero.x-e.x)<e.w/2+10&&hero.y>e.y+8&&r.back){go('out',r.back,'down');return;}}}
 // practice slimes stay inside 바렌's yard (the boar too)
 const Z=TA.slimeZone;for(const m of slimes){if(m.dead)continue;if(m.x<Z[0])m.x=Z[0];if(m.x>Z[2])m.x=Z[2];if(m.y<Z[1])m.y=Z[1];if(m.y>Z[3])m.y=Z[3];}
 // daytime sparkle over the mossy bench + unopened easy chests
 sparkT-=dt;if(sparkT<=0){sparkT=.8+Math.random();for(const c of TA.chests){if(SV.opened.includes(c.id)||c.kind==='later')continue;if(Math.hypot(hero.x-c.x,hero.y-c.y)>150)continue;
   fx.push({type:'twinkle',x:c.x+(Math.random()-.5)*30,y:c.y-14+(Math.random()-.5)*10,t:0,life:.55});}}}
let sparkT=1;
// ---------------- screen-res world UI: shop signs, prompts ----------------
function worldUI(c){if(!ta())return;c.save();c.textAlign='center';c.textBaseline='middle';
 for(const s of TA.signs){if(!inView(s.x,s.y,s.w,s.h))continue;const n=[...s.text].reduce((q,ch)=>q+(/[\x00-\x7f]/.test(ch)?.55:1),0),fs=Math.min(s.h*.6,s.w*.86/Math.max(2,n));
  c.font=`bold ${fs}px "NanumGothic","Nanum Gothic","Noto Sans CJK KR",sans-serif`;c.lineJoin='round';c.lineWidth=fs*.22;c.strokeStyle='rgba(30,16,6,.9)';c.fillStyle='#fff3cf';
  c.strokeText(s.text,s.x+s.w/2,s.y+s.h/2+1);c.fillText(s.text,s.x+s.w/2,s.y+s.h/2+1);}
 // name plates over the doors when close
 const r=curRoom;if(r&&r.id==='out')for(const d of TA.doors){if(d.kind==='trap')continue;const dd=Math.hypot(hero.x-d.x,hero.y-d.y);if(dd>200)continue;
  const al=Math.min(1,(200-dd)/80);c.globalAlpha=al;c.font='bold 17px "NanumGothic",sans-serif';const t=(d.locked?'🔒 ':'▲ ')+d.label;const w=c.measureText(t).width+16;
  c.fillStyle='rgba(12,10,20,.72)';c.fillRect(d.x-w/2,d.y-112,w,26);c.fillStyle=d.locked?'#d8d0c0':'#ffe08a';c.fillText(t,d.x,d.y-98);c.globalAlpha=1;}
 // interact prompt
 const t=promptTarget();if(t&&!ui){c.font='bold 15px "NanumGothic",sans-serif';const s=`${keyLabel('interact',1)} ${t.label}`;const w=c.measureText(s).width+14;
  c.fillStyle='rgba(12,10,20,.75)';c.fillRect(t.x-w/2,t.y-22,w,22);c.fillStyle='#fff';c.fillText(s,t.x,t.y-11);}
 c.restore();}
function promptTarget(){if(fade||uw)return null;const P=pick(),n=P.n;if(n)return {x:n.x,y:n.y-(n.id==='a_kid'?110:150),label:'말 걸기'};
 const h=P.h;if(!h)return null;const k=h.id.split(':')[0];
 if(k==='chest'&&SV.opened.includes(h.c.id))return null;if(k==='toy'&&SV.flags[h.s.id])return null;
 return {x:h.x,y:h.y-70,label:k==='chest'?(h.c.kind==='hidden'?'살펴보기':'열기'):k==='trap'?'내려가기':k==='locked'?'문 두드리기':'조사하기'};}
// ---------------- HUD: minimap + objective arrow + location banner + door fade ----------------
function hud(c){if(!ta())return;const W=cv.width,H=cv.height,hu=Math.max(.75,H/600);c.save();c.setTransform(1,0,0,1,0,0);
 const r=curRoom||rooms[0],o=rooms[0];
 if(!ui&&!(typeof winOpen!=='undefined'&&winOpen)&&IM._mini){const mw=Math.round(210*hu),mh=Math.round(mw*(o.y1-o.y0)/(o.x1-o.x0)),mx=W-mw-12*hu,my=Math.round(58*hu); // below the 스킬창 button
  c.globalAlpha=.88;c.fillStyle='rgba(10,10,18,.8)';c.fillRect(mx-3,my-3,mw+6,mh+6+20*hu);c.drawImage(IM._mini,mx,my,mw,mh);c.globalAlpha=1;
  const k=mw/(o.x1-o.x0),P=(x,y)=>[mx+(x-o.x0)*k,my+(y-o.y0)*k];
  let hp=r.id==='out'?[hero.x,hero.y]:(r.back||[hero.x,hero.y]);const[hx,hy]=P(hp[0],hp[1]);
  const G=TA.gate,[gx,gy]=P((G.x0+G.x1)/2,G.y+30);const bl=(performance.now()/400|0)%2;
  c.fillStyle='#7fd8ff';c.beginPath();c.moveTo(gx,gy+6*hu);c.lineTo(gx-6*hu,gy-3*hu);c.lineTo(gx+6*hu,gy-3*hu);c.fill();
  c.fillStyle=bl?'#ffffff':'#ffe08a';c.strokeStyle='#000';c.lineWidth=2;c.beginPath();c.arc(hx,hy,4*hu,0,7);c.fill();c.stroke();
  c.font=`bold ${Math.round(12*hu)}px "NanumGothic",sans-serif`;c.textAlign='left';c.fillStyle='#ffe08a';c.fillText('시작 마을 · '+(r.id==='out'?areaName(hero.x,hero.y):r.name),mx,my+mh+15*hu);
  // objective: the south gate road to 시작의 숲 (Ys-style seamless exit)
  if(r.id==='out'){const dx=(G.x0+G.x1)/2-hero.x,dy=G.y-hero.y,d=Math.hypot(dx,dy);if(d>240){const a=Math.atan2(dy,dx);const ty=my+mh+20*hu+12*hu;
    c.fillStyle='rgba(10,10,18,.8)';c.fillRect(mx-3,ty-11*hu,mw+6,22*hu);
    c.textAlign='right';c.fillStyle='#bfefff';c.font=`bold ${Math.round(12*hu)}px "NanumGothic",sans-serif`;c.fillText('남문 → 시작의 숲 '+Math.round(d/10)+'m',mx+mw,ty+4*hu);
    const cx=mx+10*hu;c.save();c.translate(cx,ty);c.rotate(a);c.fillStyle='rgba(127,216,255,.95)';c.beginPath();c.moveTo(9*hu,0);c.lineTo(-6*hu,-7*hu);c.lineTo(-2*hu,0);c.lineTo(-6*hu,7*hu);c.fill();c.restore();}}}
 if(banner){const al=Math.min(1,banner.t/.4,(2.2-banner.t)/.3+.2);c.globalAlpha=Math.max(0,Math.min(1,al));c.textAlign='center';c.font=`bold ${Math.round(24*hu)}px "NanumGothic",sans-serif`;
  c.lineWidth=5;c.strokeStyle='rgba(0,0,0,.8)';c.strokeText(banner.text,W/2,H*.2);c.fillStyle='#ffe08a';c.fillText(banner.text,W/2,H*.2);c.globalAlpha=1;}
 if(fade){const a=fade.t<.2?fade.t/.2:Math.max(0,1-(fade.t-.2)/.25);c.fillStyle=`rgba(0,0,0,${a})`;c.fillRect(0,0,W,H);}
 c.restore();}
function areaName(x,y){if(y>440&&x<600&&x>-450)return '바렌의 수련장';if(x<-450&&y>150)return '하로의 밭';if(x<-450)return '서쪽 언덕';
 if(y<-100&&x<1250)return '북쪽 언덕';if(y<-60&&x>=1250)return x>1740?'재봉소 뒤뜰':'엘스베트의 골목';if(x>1260&&y>200)return '장인 거리';if(y>600&&x>520&&x<840)return '남문';return '분수 광장';}
// ---------------- map screen (M): town map + world map ----------------
function mapHTML(){const o=rooms[0],r=curRoom||o,p=r.id==='out'?[hero.x,hero.y]:(r.back||[hero.x,hero.y]);const fx=(p[0]-o.x0)/(o.x1-o.x0)*100,fy=(p[1]-o.y0)/(o.y1-o.y0)*100;
 const lab=TA.labels.map(l=>`<span style="position:absolute;left:${(l.x-o.x0)/(o.x1-o.x0)*100}%;top:${(l.y-o.y0)/(o.y1-o.y0)*100}%;transform:translate(-50%,-50%);font:bold 11px sans-serif;color:#fff;text-shadow:0 0 3px #000,0 0 3px #000;white-space:nowrap">${l.text.replace(/\s*「.*」/,'')}</span>`).join('');
 return `<h2>시작 마을 지도</h2><div style="position:relative;display:block;width:100%"><img src="${BASE+TA.minimap.src}" style="display:block;width:100%;max-width:none;image-rendering:auto;border:2px solid #e8d6b0">${lab}`+
  `<span style="position:absolute;left:${fx}%;top:${fy}%;width:12px;height:12px;margin:-6px;border-radius:50%;background:#ffe08a;border:2px solid #000;box-shadow:0 0 6px #fff"></span>`+
  `<span style="position:absolute;left:${(680-o.x0)/(o.x1-o.x0)*100}%;bottom:2%;transform:translateX(-50%);font:bold 12px sans-serif;color:#7fd8ff;text-shadow:0 0 3px #000">▼ 남문 · 바람길 → 시작의 숲</span></div>`+
  `<div class="sub">현재 위치: ${r.id==='out'?areaName(hero.x,hero.y):r.name}</div><div class="sub" style="margin-top:6px">월드맵</div><img class="wmap" src="assets/world_map.jpg" alt="월드맵" style="width:min(300px,40%)">`;}
// ---------------- init ----------------
function init(){if(inited||!ta())return;inited=true;loadSave();buildHot();spawnAll();
 const Z=TA.slimeZone;
 randSpot=function(){for(let k=0;k<200;k++){const x=Z[0]+Math.random()*(Z[2]-Z[0]),y=Z[1]+Math.random()*(Z[3]-Z[1]);if(!blocked(x,y,20)&&Math.hypot(x-hero.x,y-hero.y)>200)return[x,y];}return[300,600];};
 Object.assign(BOAR_ZONE,{x0:Z[0]+40,x1:Z[2]-60,y0:Z[1]+20,y1:Z[3]-10});
 const sp=[[548,544],[300,640],[120,520]];slimes.filter(m=>m.kind!=='boar').forEach((m,i)=>{const p=sp[i%3];m.x=p[0];m.y=p[1];});
 // interactTarget is polled every frame by the key-hint HUD, so it must stay side-effect free; the action runs in interact().
 const it0=interactTarget;interactTarget=function(){const t=it0();if(t==='shop'||t==='fountain'||String(t).startsWith('tachie_'))return t;
  const P=pick(),n=P.n;if(n){if(TALK.ta_npc_hint===undefined)TALK.ta_npc_hint={name:'',lines:[()=>'']};TALK.ta_npc_hint.name=NAMES[n.id]||n.id;return 'ta_npc_hint';}
  if(P.h)return 'ta_hot';return t;};
 interact=function(){if(uw||hero.swim||hero.sk||hero.atk)return;const t=interactTarget();
  const P=pick();if(t==='ta_npc_hint'&&P.n){npcTalk(P.n);return;}if(t==='ta_hot'&&P.h){useHot(P.h);return;}
  dlg={id:t,i:0};openUI('dialog');};
 TALK.ta_hot={name:'조사',lines:[()=>'']};
 const r0=renderUI;renderUI=function(){const v=r0.apply(this,arguments);if(ui==='map'){ovp.classList.add('wide');ovp.innerHTML=mapHTML()+hintBar([[keyLabel('map',1)+' / Esc','닫기']]);}return v;};
 if(typeof pickUp==='function'){const p0=pickUp;pickUp=function(){const s=uw&&uw.spot;const v=p0.apply(this,arguments);
  if(s&&s.id==='fountain'&&!SV.flags.k_cradle_page){SV.flags.k_cradle_page=1;persist();msg('「요람의 장부 조각」도 함께 건져 올렸다 (A6)');}return v;};}
 lastRoomId=room().id;}
function hintLabel(){const n=pick().n;if(n)return (NAMES[n.id]||n.id).split(' · ')[0]+'와 대화';const p=promptTarget();return p?p.label:'조사하기';}
window.TOWN_A={hintLabel,load,init,room,roomAt,blockedPt,ground,layers,worldUI,hud,update,go,get save(){return SV},get fade(){return fade},get npcs(){return NPCS},get smith(){return SMITH},get baren(){return SM},
 get data(){return ta()},hot:()=>HOT,interactNow:()=>{const t=interactTarget();return t;}};
})();
