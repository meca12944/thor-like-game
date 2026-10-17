// [tachie] Japanese VN/JRPG-style UPPER-BODY BUST dialogue portraits (head to just below the waist).
// Data: assets/bust/index.json + assets/bust/<id>/<expr>.webp|png, written by tools/import_bust.py from the illustrator's
// docs_art/bust/<id>/<expr>.png (1024x1280 transparent). Temporary busts: tools/make_bust_temp.py (crop of the full-body art).
// Layout: hero bottom-left, partner bottom-right, standing up from the screen bottom beside/behind the dialogue box.
// Drawn on a separate DOM layer (#tachie) above the pixel canvas, at display resolution with smooth scaling
// (the world canvas is nearest-scaled; this layer is not). Only CSS transform/opacity/filter animate -> GPU-composited, 60 fps.
// Dialogue lines (TALK[id].lines[i]() in the main script) may return {who:'hero'|'<charId>'|'none', expr:'smile', t:'...'};
// TALK[id].tachie = partner char id (defaults to TALK[id].por), TALK[id].expr = default expression. Unknown/missing expr -> neutral.
(function(){
'use strict';
const BASE='assets/bust/';
let IDX=null;const ready=fetch(BASE+'index.json').then(r=>r.json()).then(j=>{IDX=j;}).catch(()=>{IDX={chars:{},expressions:[],alias:{}};});
// --bh = bust height; width follows the 1024x1280 canvas. The inner edge tucks ~22% of the bust behind the dialogue box sides.
const css=`#tachie{position:fixed;inset:0;pointer-events:none;overflow:hidden;contain:strict;--bh:min(64vh,1280px,calc(42vw*1.25))}
#tachie .ts{position:absolute;bottom:0;height:var(--bh);aspect-ratio:1024/1280;opacity:0;transform:translate3d(var(--off),var(--dy,0px),0) scale(var(--sc,1));transform-origin:50% 100%;
 transition:opacity .24s ease,transform .32s cubic-bezier(.2,.8,.25,1),filter .22s ease;will-change:transform,opacity,filter;filter:brightness(1);z-index:1}
#tachie .ts.L{left:max(-3vw,calc(50% - min(360px,46vw) - var(--bh)*.8*.78));--off:-10vh}
#tachie .ts.R{right:max(-3vw,calc(50% - min(360px,46vw) - var(--bh)*.8*.78));--off:10vh}
#tachie .ts.on{opacity:1;--off:0px}
#tachie .ts.dim{filter:brightness(.55) saturate(.8);--sc:.965;--dy:1.2vh;z-index:0}
#tachie .ts.talk{--sc:1;--dy:0px;z-index:2}
#tachie .tb{position:absolute;inset:0;transform-origin:50% 100%;animation:tachieBreath 3.6s ease-in-out infinite;will-change:transform}
#tachie .ts.R .tb{animation-delay:-1.7s}
#tachie img{position:absolute;inset:0;width:100%;height:100%;opacity:0;transition:opacity .14s linear;image-rendering:auto;-webkit-user-drag:none}
#tachie img.cur{opacity:1}
@keyframes tachieBreath{0%,100%{transform:scale(1,1)}50%{transform:scale(1.004,1.012)}}
@media (max-aspect-ratio:4/3){#tachie{--bh:min(50vh,calc(52vw*1.25))}}
body.wscene #tachie{visibility:hidden}
#dlg.tachie{z-index:2}`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
const layer=document.createElement('div');layer.id='tachie';
const dlgEl0=document.getElementById('dlg');(dlgEl0&&dlgEl0.parentNode||document.body).insertBefore(layer,dlgEl0||null);
function mkSlot(side){const s=document.createElement('div');s.className='ts '+side;const b=document.createElement('div');b.className='tb';const a=new Image(),c=new Image();a.alt=c.alt='';a.decoding=c.decoding='async';
 b.appendChild(a);b.appendChild(c);s.appendChild(b);layer.appendChild(s);return {el:s,imgs:[a,c],cur:0,id:null,expr:null};}
const SL={L:mkSlot('L'),R:mkSlot('R')};
const cache={};
function has(id){return !!(IDX&&IDX.chars[id]);}
function normExpr(id,e){if(!has(id))return null;const C=IDX.chars[id];e=(IDX.alias&&IDX.alias[e])||e||'neutral';return C.expr[e]?e:(C.expr.neutral?'neutral':Object.keys(C.expr)[0]);}
function src(id,e){return BASE+IDX.chars[id].expr[normExpr(id,e)];}
function preload(id){if(!has(id))return;for(const e in IDX.chars[id].expr){const u=src(id,e);if(!cache[u]){const im=new Image();im.decoding='async';im.src=u;cache[u]=im;if(im.decode)im.decode().catch(()=>{});}}}
function setSlot(S,id,e,lit){if(!id){S.el.classList.remove('on','dim','talk');S.id=null;return;}
 e=normExpr(id,e);
 if(S.id!==id||S.expr!==e){const u=src(id,e),nx=1-S.cur,ni=S.imgs[nx],oi=S.imgs[S.cur];
  const swap=()=>{ni.classList.add('cur');oi.classList.remove('cur');S.cur=nx;};
  if(S.id!==id){oi.classList.remove('cur');oi.removeAttribute('src');}
  ni.src=u;const c=cache[u];if(c&&c.complete)swap();else if(ni.decode)ni.decode().then(swap,swap);else ni.onload=swap;
  S.id=id;S.expr=e;}
 S.el.classList.add('on');S.el.classList.toggle('dim',!lit);S.el.classList.toggle('talk',!!lit);}
function hide(){setSlot(SL.L,null);setSlot(SL.R,null);state.key=null;}
const state={key:null,heroIn:false,heroExpr:'neutral',partner:null,partnerExpr:'neutral'};
function evalLine(T,i){try{const L=T.lines[i]();return L&&typeof L==='object'?L:{t:L};}catch(e){return {t:''};}}
// called after every renderUI(): reads the current dialogue line and updates the bust portraits
function sync(){
 if(!IDX)return;
 if(typeof ui==='undefined'||ui!=='dialog'||typeof dlg==='undefined'||!dlg){if(state.key)hide();return;}
 const T=TALK[dlg.id];if(!T)return;
 const key=dlg.id;
 if(state.key!==key){ // new conversation: who takes part?
  state.key=key;state.partner=null;state.heroIn=false;state.heroExpr=T.heroExpr||'neutral';state.partnerExpr=T.expr||'neutral';
  const p=T.tachie||T.por;if(has(p))state.partner=p;
  for(let i=0;i<T.lines.length;i++){const L=evalLine(T,i);if(L.who==='hero')state.heroIn=true;else if(!state.partner&&L.who&&has(L.who))state.partner=L.who;}
  if(state.partner)state.heroIn=state.heroIn||T.withHero!==false;
  if(state.partner)preload(state.partner);if(state.heroIn)preload('hero');}
 const L=evalLine(T,dlg.i);const who=L.who==='hero'?'hero':L.who==='none'?null:(L.who&&has(L.who)?L.who:(L.who?null:state.partner));
 if(who==='hero')state.heroExpr=L.expr||'neutral';else if(who&&who===state.partner)state.partnerExpr=L.expr||T.expr||'neutral';
 else if(L.who&&has(L.who)){state.partner=L.who;state.partnerExpr=L.expr||'neutral';preload(L.who);}
 setSlot(SL.L,state.heroIn?'hero':null,state.heroExpr,who==='hero');
 setSlot(SL.R,state.partner,state.partnerExpr,who===state.partner);
 // small in-box portrait is replaced by the bust for characters that have one
 const de=document.getElementById('dlg');if(de){const shown=(who==='hero'&&state.heroIn)||(who&&who===state.partner);
  de.classList.toggle('tachie',!!(state.heroIn||state.partner));
  if(shown){const dp=de.querySelector('.dp');if(dp){dp.remove();de.classList.remove('hasp');}}}
}
// ---- hook the main script's dialogue renderer (global function bindings; no edits to the main script needed) ----
function hook(){if(typeof renderUI!=='function'||typeof closeUI!=='function'||typeof TALK==='undefined')return false;
 const r0=renderUI,c0=closeUI;
 renderUI=function(){const v=r0.apply(this,arguments);try{sync();}catch(e){console.error('[tachie]',e);}return v;};
 closeUI=function(){const v=c0.apply(this,arguments);try{hide();}catch(e){}return v;};
 return true;}
// ---- heroine conversations (data-driven; lines carry speaker + expression) ----
const HL={
 a_tailor:[['n','나비예요! 「나비 재봉소」에 온 걸 환영해요.'],['h','neutral','망토를 하나 맞추고 싶은데.'],['smile','역시! 같이 오길 잘했어요. 색은 제가 골라 드릴게요!'],['surprised','에엣, 숲에 같이 가자고요? 거미가 있는 그 숲?!'],['sad','…사실 저, 혼자서는 무서워서 못 가요.'],['h','smile','내가 지켜 줄게.'],['blush','저기… 그럼 오늘은 조금 더 같이 있어도 돼요?'],['angry','…방금 웃었죠? 지금 장난해요?']],
 h_mystic:[['n','운이에요. 수정이 당신이 올 걸 알려 주었죠.'],['h','surprised','내가 올 걸 알고 있었다고?'],['smile','후후, 운명은 두 갈래. 어느 쪽을 고를지는 당신 몫이에요.'],['sad','정해진 미래만 보는 건… 꽤 쓸쓸한 일이랍니다.'],['angry','수정을 함부로 만지지 마세요. 갈라진 운명이 흐려져요.'],['surprised','어머… 이 환시는 처음 봐요.'],['blush','…당신 옆에서는 미래가 잘 안 보여요. 이상하죠?']],
 g_dancer:[['n','어서 와, 손님! 방울의 바자르 장신구는 사막 최고야.'],['smile','흥정은 대환영! 대신 약속은 꼭 지키는 게 내 방식이야.'],['h','neutral','태양 방울을 찾고 있다고 들었어.'],['sad','…엄마의 유품이야. 도적들이 가져갔지.'],['angry','그놈들, 다음에 만나면 칼춤으로 혼쭐을 내 줄 거야!'],['surprised','같이 가 준다고? 정말?'],['blush','후후… 축제 날, 너만을 위한 춤을 춰 줄까?']],
 f_diver:[['n','숨비다. 항구 최고의 해녀지!'],['smile','진주 캐기 대결, 한판 어때? 지면 생선 구이 사기다!'],['h','surprised','바다 속까지 같이 들어가자고?'],['angry','유령 해적 놈들… 아버지 배를 가라앉힌 놈들이야.'],['sad','아버지 작살만은… 꼭 되찾고 싶어.'],['surprised','어? 너 숨 오래 참는구나!'],['blush','…고마워. 이런 말, 잘 안 하는데.']],
 e_tailor:[['n','「불꽃 옷감」에 무슨 볼일이죠? 구경만 할 거면 나가 줘요.'],['h','neutral','불사조 깃털을 찾는 동료가 필요하다며.'],['surprised','…어떻게 알았죠?'],['angry','흥, 실력도 없으면서 화산 정상에 오르겠다고요?'],['smile','좋아요. 그 눈빛, 마음에 들어요.'],['sad','타지 않는 천… 아무도 믿어 주지 않았어요.'],['blush','치, 칭찬해 봤자 할인은 없어! …정말 없다니까.']],
 c_priest:[['n','눈의 신전에 오신 걸 환영해요. 저는 설화예요.'],['smile','추우셨죠? 따뜻한 수프 드릴게요.'],['h','neutral','순례길에 설인이 나온다던데.'],['sad','…어둠 신전 사람들이 또 움직이고 있어요.'],['surprised','같이 가 주신다고요? 위험한 길인데…'],['angry','봉인을 해치려는 자는, 성녀로서 용서하지 않아요.'],['blush','눈꽃 축제… 같이 걸어 주실래요?']],
 d_yuna:[['n','어, 저기! 혹시 말 통해요? 다행이다…'],['surprised','여기 진짜 게임 같은 세계구나. 휴대폰은 배터리 0%고.'],['h','surprised','하늘에서 떨어졌다고?'],['smile','유나라고 해요! 서울에서 고고학 공부하던 대학원생.'],['sad','…집에 가는 방법, 있긴 한 걸까.'],['angry','벌레만은 진짜 싫어! 저리 가!'],['blush','그래도… 너랑 같이면, 여기도 나쁘지 않을지도.']],
};
function addTalks(){for(const id in HL){const nm=(IDX&&IDX.chars[id]&&IDX.chars[id].name)||id;
  TALK['tachie_'+id]={name:nm,por:id,tachie:id,lines:HL[id].map(l=>{if(l[0]==='h')return ()=>({who:'hero',expr:l[1],t:l[2]});if(l[0]==='n')return ()=>({who:id,expr:'neutral',t:l[1]});return ()=>({who:id,expr:l[0],t:l[1]});})};}}
// 나비 stands in the start town (her home); talk to her with the interact key
let nabi=null;const NABI_POS=[400,570];
function nearNabi(){const n=nabi;return n&&!n.dead&&!(n.fainted>0)&&!(n.alert>0)&&!(typeof uw!=='undefined'&&uw)&&Math.hypot(hero.x-n.x,hero.y-n.y)<110?n:null;}
function placeNabi(){if(typeof spawnNpc!=='function'||typeof interactTarget!=='function')return;let [x,y]=NABI_POS;
 if(typeof blocked==='function'&&blocked(x,y,14)){for(let r=20;r<300;r+=20){let ok=false;for(let a=0;a<6.28;a+=.5){const xx=x+Math.cos(a)*r,yy=y+Math.sin(a)*r;if(!blocked(xx,yy,14)){x=xx;y=yy;ok=true;break;}}if(ok)break;}}
 nabi=spawnNpc('a_tailor',x,y,{});const it0=interactTarget;interactTarget=function(){const t=it0();if(t==='shop'||t==='fountain')return t;return nearNabi()?'tachie_a_tailor':t;};}
// test / preview API: open any heroine conversation (?talk=<id>)
function openTalk(id,line=0){const k=TALK[id]?id:'tachie_'+id;if(!TALK[k])return false;dlg={id:k,i:line};openUI('dialog');return true;}
ready.then(()=>{if(!hook()){console.warn('[tachie] main script not found');return;}addTalks();placeNabi();preload('hero');
 for(const id in IDX.chars)if(id!=='hero'){} // lazy preload per conversation
 window.__tachie={openTalk,sync,has,get state(){return state},get nabi(){return nabi},chars:()=>Object.keys(IDX.chars),slots:SL};
 const q=new URLSearchParams(location.search).get('talk');if(q)setTimeout(()=>openTalk(q),400);});
})();
