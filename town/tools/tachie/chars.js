// Character designs for the procedural tachie builder (lib.js). Each char: palette + draw(ctx) adding z-ordered layers.
// z: 5 cape/back props · 10 back hair · 30 legs · 35 legwear · 40 torso · 45 bottoms · 50 tops · 60 arms · 65 armwear · 70 neck · 80 head · 90 face · 100 front hair · 110 accessories
(function(){
const CX=300;
const pal=(base,shade,hi,line)=>({base,shade,hi,line});
// path with sharp corners at points and curved (bulged) edges between them
function qpath(P,bulge=.12,closed=true){let d=`M${P[0][0]},${P[0][1]}`;const n=P.length,last=closed?n:n-1;
 for(let i=0;i<last;i++){const a=P[i],b=P[(i+1)%n],bb=(b[2]!=null?b[2]:bulge);const mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2,dx=b[0]-a[0],dy=b[1]-a[1];
  d+=` Q${(mx-dy*bb).toFixed(1)},${(my+dx*bb).toFixed(1)} ${b[0]},${b[1]}`;}return d+(closed?'Z':'');}
const M=P=>P.map(([x,y,b])=>b!=null?[2*CX-x,y,-b]:[2*CX-x,y]);
const rev=P=>P.slice().reverse().map(([x,y,b])=>[x,y,b]);
function hairRing(c,hc,y=116,w=70){const {line,fillp}=c;return line(`M${CX-w},${y+8} Q${CX},${y-18} ${CX+w},${y+8}`,hc.hi,9,'opacity=".55"')+line(`M${CX-w+14},${y+6} Q${CX},${y-12} ${CX+w-18},${y+6}`,'#fff',3,'opacity=".45"');}
function strands(c,hc,list){return list.map(d=>c.line(d,hc.line,1.4,'opacity=".55"')).join('');}
// generic bangs: crown + locks. tips: array of [x,y] alternating tip/valley along the forehead from right to left
function bangs(c,hc,o={}){const sL=o.sideL||[[212,300],[206,230]],sR=o.sideR||[[388,300],[394,230]];
 const crown=[[206,176,-.12],[218,112,-.14],[256,74,-.12],[300,62,-.1],[344,74,-.1],[382,112,-.12],[394,176,-.14]];
 const n=o.n||9,tipY=o.tipY||168,valY=o.valY||124,x0=o.x0||382,x1=o.x1||218;let tips=[];
 for(let i=0;i<=n;i++){const t=i/n,x=x0+(x1-x0)*t,edge=Math.abs(t-.5)*2;tips.push([x,(tipY+(o.edgeLen||34)*edge*edge+((i*37)%11)-5),.1]);
  if(i<n)tips.push([x+(x1-x0)/n*.5+((i*13)%7)-3,valY+edge*18,-.06]);}
 if(o.part)tips=o.part(tips);
 const P=[...crown,...sR.map(p=>[p[0],p[1],-.08]),...tips,...rev(sL).map(p=>[p[0],p[1],.08])];
 const d=qpath(P,.06);
 // under-layer locks (darker) peeking between front locks
 const P2=[[214,150],[300,96],[386,150],...tips.map(([x,y])=>[x+((x-300)*.04),y-10+(((x|0)%3)*4),.08])];
 return c.part(qpath(P2,.05),{base:hc.shade,shade:hc.line,line:hc.line},{lw:1.2,nohi:1})+c.part(d,hc,{sh:[-6,-8],extra:hairRing(c,hc,o.ringY||112,o.ringW||66)})+strands(c,hc,o.str||[]);}
function lock(c,hc,P,b=.1,o={}){return c.part(qpath(P,b),hc,Object.assign({sh:[-5,-5]},o));}
// pleated skirt
function pleatSkirt(c,cl,y0,y1,w0,w1,n=10,o={}){const {fillp,line,part}=c;let pts=[[CX-w0,y0],[CX+w0,y0]];
 const hem=[];for(let i=0;i<=n;i++){const t=i/n,x=CX+w1-(2*w1)*t,y=y1+(i%2?10:0)+Math.sin(t*Math.PI)*12;hem.push([x,y]);}
 const d=`M${CX-w0},${y0} L${CX+w0},${y0} Q${CX+w0+20},${(y0+y1)/2} ${hem[0][0]},${hem[0][1]} `+hem.slice(1).map(p=>`L${p[0]},${p[1]}`).join(' ')+` Q${CX-w0-20},${(y0+y1)/2} ${CX-w0},${y0}Z`;
 let ex='';for(let i=1;i<n;i++){const t=i/n,xt=CX-w0+2*w0*t,xb=CX-w1+2*w1*t;ex+=line(`M${xt},${y0+6} L${xb},${y1+(i%2?0:10)+Math.sin(t*Math.PI)*12}`,cl.line,1.6,'opacity=".55"');
  if(i%2)ex+=fillp(`M${xt},${y0+6} L${xb},${y1+Math.sin(t*Math.PI)*12} L${CX-w1+2*w1*(t+1/n)},${y1+10+Math.sin((t+1/n)*Math.PI)*12} L${CX-w0+2*w0*(t+1/n)},${y0+6}Z`,cl.shade,'opacity=".45"');}
 return part(d,cl,{sh:[-10,-4],extra:ex});}
function bootR(c,cl,top,o={}){ // right boot outline from leg geometry, mirrored for left
 const P=[[60,top],[80,top+40],[80,top+110],[64,1540],[52,1612],[60,1650],[74,1682],[24,1688],[22,1640],[24,1606],[24,1500],[22,top+60],[20,top+10]];
 return P;}
function boots(c,cl,top,o={}){const R=c.R(bootR(c,cl,top)),Lp=c.L(bootR(c,cl,top));let s='';
 for(const P of[R,Lp]){const d=c.sm(P);let ex='';if(o.lace)for(let y=top+30;y<1560;y+=26)ex+=c.line(`M${(P[0][0]+P[12][0])/2-8},${y} l16,8 m0,-8 l-16,8`,o.lace,1.6);
  if(o.cuff)ex+=c.fillp(`M0,${top-4} H600 V${top+o.cuff} H0Z`,o.cuffCol||cl.shade);if(o.extra)ex+=o.extra(P);s+=c.part(d,cl,{sh:[-6,-3],extra:ex});
  s+=c.line(`M${P[5][0]},${1650} Q${(P[5][0]+P[8][0])/2},${1662} ${P[8][0]},${1650}`,cl.line,1.5,'opacity=".6"');}
 return s;}
function stockings(c,cl,top,o={}){let s='';for(const leg of[c.G.legL,c.G.legR]){const cp=c.clip(leg);let st='';
  if(o.stripe)for(let y=top+30;y<1700;y+=o.stripe*2)st+=c.fillp(`M0,${y} H600 V${y+o.stripe} H0Z`,o.stripeCol);
  s+=`<g clip-path="${cp}"><path d="M0,${top} Q300,${top+16} 600,${top} V1720 H0Z" fill="${cl.base}"/>${st}<path d="M0,${top} Q300,${top+16} 600,${top} V1720 H0Z" fill="${c.lin([[0,'#fff',.0],[.5,'#000',.0],[1,'#000',.25]],0,0,1,0)}"/>`+
   `<path d="M0,${top} Q300,${top+16} 600,${top} V${top+(o.band||14)} Q300,${top+(o.band||14)+16} 0,${top+(o.band||14)}Z" fill="${o.bandCol||cl.shade}"/></g>`+c.line(leg,cl.line,2.2);}
 return s;}
function bracer(c,cl,y0,y1,o={}){let s='';for(const k of[-1,1]){const x0=CX+k*(o.x0||104),x1=CX+k*(o.x1||134),x2=CX+k*(o.x2||110),x3=CX+k*(o.x3||142);
  const d=`M${x0},${y0} Q${(x0+x1)/2},${y0-6} ${x1},${y0} L${x3},${y1} Q${(x2+x3)/2},${y1+6} ${x2},${y1}Z`;s+=c.part(d,cl,{sh:[-k*4,-2],lw:2.2,extra:o.extra?o.extra(k):''});}return s;}
function bangle(c,y,col,k,o={}){const x=CX+k*(o.x||124);return c.ell(x,y,o.rx||17,5,'none',`stroke="${col}" stroke-width="${o.w||4}"`)+c.ell(x-k*3,y-1,(o.rx||17)*.6,2,'none','stroke="#fff6c0" stroke-width="1.4" opacity=".7"');}
// bikini/crop cups: shape over the bust. a=lower width, returns symmetric path pair
function cups(c,cl,o={}){const y0=o.y0||405,y1=o.y1||500,cx=o.cx||46,w=o.w||50;let s='';
 for(const k of[-1,1]){const x=CX+k*cx;const d=`M${CX+k*5},${y1-10} C${CX+k*2},${y0+40} ${x-k*14},${y0+8} ${x-k*4},${y0} C${x+k*w*.6},${y0+14} ${x+k*w*1.05},${y1-40} ${x+k*w},${y1-12} C${x+k*w*.8},${y1+12} ${CX+k*20},${y1+10} ${CX+k*5},${y1-10}Z`;
  s+=c.part(d,cl,{sh:[-k*7,-6],lw:2.2,extra:(o.extra?o.extra(k,x):'')+c.ell(x+k*w*.1,y0+(y1-y0)*.45,w*.32,(y1-y0)*.22,'#fff','opacity=".22"')})+c.line(`M${CX+k*8},${y1-6} Q${x+k*w*.4},${y1+16} ${x+k*w},${y1-12}`,c.C.skin.shade,3,'opacity=".5"');}
 // straps to neck & under-band
 if(!o.noStrap)for(const k of[-1,1])s+=c.line(`M${CX+k*(cx-4)},${y0+2} Q${CX+k*30},${360} ${CX+k*24},${318}`,o.strap||cl.line,o.strapW||3);
 if(o.band!==false)for(const k of[-1,1])s+=c.line(`M${CX+k*(cx+w-2)},${y1-16} Q${CX+k*(cx+w+12)},${y1-10} ${CX+k*94},${y1-22}`,o.strap||cl.line,o.strapW||3);
 return s;}
function underBust(c,y=500){return c.line(`M${CX-84},${y-6} Q${CX-50},${y+8} ${CX-8},${y-2}`,c.C.skin.shade,4,'opacity=".55"')+c.line(`M${CX+84},${y-6} Q${CX+50},${y+8} ${CX+8},${y-2}`,c.C.skin.shade,4,'opacity=".55"');}
function gem(c,x,y,r,col){return c.circ(x,y,r,c.rad([[0,'#fff'],[.35,col],[1,'#301030']],.35,.35,.7),`stroke="#4a3010" stroke-width="1.4"`);}
function coin(c,x,y,r=6){return c.circ(x,y,r,c.rad([[0,'#fff7c0'],[.5,'#f0c040'],[1,'#a0700a']],.35,.35,.7),'stroke="#6a4a08" stroke-width="1.2"');}
function sandals(c,col){let s='';for(const k of[-1,1]){const x=CX+k*42;s+=c.part(`M${x-20},${1676} Q${x},${1692} ${x+22},${1676} L${x+20},${1688} Q${x},${1698} ${x-20},${1688}Z`,col,{lw:1.6});
 s+=c.line(`M${x-14},${1652} L${x+14},${1676} M${x+14},${1652} L${x-14},${1676} M${x-16},${1626} Q${x},${1636} ${x+16},${1626}`,col.base,3);}return s;}

const H={};
// ======================= 리네트 (a_tailor) — fantasy seamstress =======================
H.a_tailor={name:'리네트',skin:pal('#ffe7da','#f2bca8','#fff6ee','#7a4a3c'),hair:pal('#f8d878','#dba944','#fff4b8','#8a5a1c'),eyes:'#e0952a',eyesLight:'#ffe9a0',eyesDark:'#5a2a10',lash:'#3a2418',
 draw(c){const hc=this.hair,{add,part,line,fillp}=c;
  // twin tails (back)
  const tail=[[236,104],[190,116,.2],[146,190,.1],[126,300,-.1],[146,420,.12],[124,540,-.1],[150,650,.1],[128,760],[170,700,-.05],[190,600,.1],[176,480,-.1],[196,360,.1],[190,250,-.1],[222,160,.1]];
  add(10,lock(c,hc,tail,.1,{extra:strands(c,hc,['M200,180 Q170,300 186,420','M190,260 Q176,420 170,560','M210,420 Q190,520 176,660'])})+lock(c,hc,M(tail),.1,{extra:strands(c,hc,['M400,180 Q430,300 414,420','M410,260 Q424,420 430,560','M390,420 Q410,520 424,660'])}));
  add(12,lock(c,hc,[[214,140],[206,260],[214,330],[300,300],[386,330],[394,260],[386,140]],.05));
  // stockings + boots
  add(35,stockings(c,pal('#f6f0ff','#cbbbe6',null,'#6a5a8a'),1010,{stripe:22,stripeCol:'#b9a6e0',band:16,bandCol:'#8f7cc0'}));
  add(36,boots(c,pal('#9a6236','#6a3c1c','#d8a070','#3a2010'),1430,{lace:'#e8d0a0',cuff:26,cuffCol:'#7a4a24'}));
  // skirt + belt + pincushion
  add(45,pleatSkirt(c,pal('#8fc8f0','#5a96cc','#e6f6ff','#2a4a78'),604,912,82,128,12));
  add(47,part(`M${CX-84},606 Q${CX},626 ${CX+84},606 L${CX+88},632 Q${CX},652 ${CX-88},632Z`,pal('#9a5a2c','#6a3a18','#e0a070','#3a2010'),{lw:2})+
   fillp(`M${CX-14},616 h28 v22 h-28z`,'#e8c060','stroke="#6a4a08" stroke-width="2"')+
   part(`M${CX+58},620 q30,-8 40,22 q4,30 -22,34 q-28,0 -30,-26z`,pal('#b088d8','#7a58a8','#f0e0ff','#3a2058'),{lw:2})+line(`M${CX+70},${626} l-6,-18 M${CX+82},${628} l2,-20 M${CX+92},${634} l10,-14`,'#d0d0e0',2)+circ3(c,[[CX+64,606,'#ff6080'],[CX+84,606,'#60c0ff'],[CX+104,618,'#ffd040']]));
  // fantasy linen crop blouse with laced front
  const bl=pal('#fffaf0','#e0d2c0','#ffffff','#7a6a58');
  const top=c.sym([[0,396],[30,368],[56,340],[84,334],[104,348],[104,410],[106,456],[96,504],[60,516],[0,512]]);
  add(50,part(c.sm(top),bl,{sh:[-10,-6],extra:underBust(c,508)+line(`M${CX},392 L${CX},470`,'#b8a890',2)+
   [0,1,2,3].map(i=>line(`M${CX-10},${400+i*18} L${CX+10},${410+i*18} M${CX+10},${400+i*18} L${CX-10},${410+i*18}`,'#8a5a30',1.8)).join('')+
   line(`M${CX-60},${470} Q${CX-40},${490} ${CX-10},${484}`,bl.shade,3)+line(`M${CX+60},${470} Q${CX+40},${490} ${CX+10},${484}`,bl.shade,3)})+
   fillp(`M${CX-94},508 Q${CX},528 ${CX+94},508 l-2,10 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 q-10,8 -18,0 Z`,'#fffaf0','stroke="#9a8a70" stroke-width="1.4"'));
  // sky ribbon bow on chest
  add(52,bow(c,CX,384,pal('#8fd0ff','#4a90d0','#e8f8ff','#1a4a80'),1));
  // puff sleeves + leather bracers
  for(const k of[-1,1])add(66,part(c.sm([[CX+k*96,340],[CX+k*130,350],[CX+k*144,392],[CX+k*136,430],[CX+k*104,426],[CX+k*96,390]]),bl,{sh:[-k*6,-4],extra:line(`M${CX+k*104},${424} Q${CX+k*122},${436} ${CX+k*138},${428}`,'#8fc8f0',4)}));
  add(66,bracer(c,pal('#a0683a','#6a3c1c','#e0a878','#3a2010'),680,756,{x0:104,x1:132,x2:110,x3:138,extra:k=>line(`M${CX+k*108},${700} L${CX+k*134},${700} M${CX+k*110},${730} L${CX+k*136},${730}`,'#e8d0a0',2)}));
  // front hair
  add(100,bangs(c,hc,{sideL:[[218,300],[208,240]],sideR:[[382,300],[392,240]],str:['M300,70 Q290,120 294,180','M330,80 Q340,120 336,170','M266,84 Q256,130 262,180']}));
  add(110,bow(c,232,104,pal('#e8f6ff','#8fc0e8','#ffffff','#2a5a90'),1.25,true)+bow(c,368,104,pal('#e8f6ff','#8fc0e8','#ffffff','#2a5a90'),1.25,true));
 }};
function circ3(c,L){return L.map(([x,y,col])=>c.circ(x,y,5,col,'stroke="#402020" stroke-width="1"')).join('');}
function bow(c,x,y,cl,s=1,butterfly){const w=34*s,h=22*s;let d=`M${x},${y} Q${x-w*.6},${y-h*1.3} ${x-w},${y-h*.4} Q${x-w*1.05},${y+h*.6} ${x},${y} Z M${x},${y} Q${x+w*.6},${y-h*1.3} ${x+w},${y-h*.4} Q${x+w*1.05},${y+h*.6} ${x},${y}Z`;
 let s2=c.part(d,cl,{lw:2,sh:[-3,-3]});
 if(butterfly)s2+=c.part(`M${x},${y} Q${x-w*.8},${y+h*1.4} ${x-w*.4},${y+h*1.1} Q${x-w*.15},${y+h*.5} ${x},${y}Z M${x},${y} Q${x+w*.8},${y+h*1.4} ${x+w*.4},${y+h*1.1} Q${x+w*.15},${y+h*.5} ${x},${y}Z`,cl,{lw:2,sh:[-3,-3]})+
  c.circ(x-w*.55,y-h*.4,4*s,'#b090e0')+c.circ(x+w*.55,y-h*.4,4*s,'#b090e0');
 else s2+=c.part(`M${x-4},${y+2} L${x-16*s},${y+34*s} L${x-4*s},${y+30*s} Z M${x+4},${y+2} L${x+16*s},${y+34*s} L${x+4*s},${y+30*s}Z`,cl,{lw:1.8});
 return s2+c.ell(x,y,6*s,6*s,cl.shade,`stroke="${cl.line}" stroke-width="1.8"`);}
window.TACHIE_HELP={qpath,M,rev,hairRing,strands,bangs,lock,pleatSkirt,boots,stockings,bracer,bangle,cups,underBust,gem,coin,sandals,bow,pal};
window.TACHIE_CHARS=H;
})();
