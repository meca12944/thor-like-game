// More characters (see chars.js for helpers / z-order)
(function(){
const CX=300,H=window.TACHIE_CHARS,{qpath,M,rev,strands,bangs,lock,pleatSkirt,boots,stockings,bracer,bangle,cups,underBust,gem,coin,sandals,bow,pal}=window.TACHIE_HELP;
function longBack(c,hc,o){const w=o.w||110,len=o.len||900,wv=o.wave||0,n=o.n||7;const P=[[300,60,-.1],[386,96,-.14],[CX+w-10,220,-.08]];
 for(let y=360,i=0;y<len-60;y+=140,i++)P.push([CX+w+(i%2?wv:-wv)+(o.flare||0)*(y-300)/600,y,(i%2?.08:-.08)]);
 const tw=w+(o.flare||0)*(len-300)/600;for(let i=0;i<=n;i++){const t=i/n,x=CX+tw-2*tw*t;P.push([x,len+((i%2)?-50:0)-Math.sin(t*Math.PI)*(o.dip||30),.05]);}
 for(let y=len-80,i=0;y>300;y-=140,i++)P.push([CX-w-(i%2?wv:-wv)-(o.flare||0)*(y-300)/600,y,(i%2?.08:-.08)]);
 P.push([CX-w+10,220,-.08],[214,96,-.14]);
 const sx=[];for(let k=-3;k<=3;k++)if(k)sx.push(`M${CX+k*28},${200} Q${CX+k*(34+wv*.3)},${(200+len)/2} ${CX+k*(30+(o.flare||0)*.4)},${len-60}`);
 return c.part(qpath(P,.06),hc,{sh:[-8,-4],extra:strands(c,hc,sx)});}
function crop(c,cl,y1,o={}){const top=c.sym([[0,o.neck||392],[28,o.neckW||366],[60,342],[90,336],[106,350],[104,410],[106,456],[96,y1-8],[60,y1+4],[0,y1]]);return c.part(c.sm(top),cl,{sh:[-10,-6],extra:(o.extra||'')+underBust(c,y1-2)});}
function slit(c,cl,y0,y1,w0,w1,o={}){ // tight H-line / wrap skirt; slit on viewer-right
 const d=`M${CX-w0},${y0} Q${CX},${y0+14} ${CX+w0},${y0} Q${CX+w0+14},${y0+120} ${CX+w1},${y1-6} L${CX+w1-18},${y1} L${CX+(o.slitX||70)},${o.slitY||y1-90} L${CX+(o.slitX||70)-14},${y1+4} Q${CX},${y1+14} ${CX-w1},${y1} Q${CX-w0-14},${y0+120} ${CX-w0},${y0}Z`;
 return c.part(d,cl,{sh:[-10,-4],extra:(o.extra||'')+c.line(`M${CX-30},${y0+40} Q${CX-26},${(y0+y1)/2} ${CX-34},${y1-10}`,cl.shade,3,'opacity=".6"')});}
function earrings(c,col,y=230){return [-1,1].map(k=>gem(c,CX+k*80,y,5,col)).join('');}
function orbs(c,col){let s='';for(const [x,y,r] of[[150,640,30],[470,560,24]]){s+=c.circ(x,y,r*1.8,c.rad([[0,col,.45],[1,col,0]]))+c.circ(x,y,r,c.rad([[0,'#ffffff'],[.4,col],[1,'#3a1060']],.35,.3,.75),'stroke="#e0c8ff" stroke-width="2"')+c.ell(x-r*.35,y-r*.4,r*.3,r*.18,'#fff','opacity=".8"');}return s;}

// ======================= 베일라 (h_mystic) =======================
H.h_mystic={name:'베일라',skin:pal('#fbe6dc','#e8beb0','#fff6f0','#7a4a4c'),hair:pal('#e6e6f2','#b4b4cc','#ffffff','#6a6a8a'),eyes:'#9a5ae0',eyesLight:'#f0d0ff',eyesDark:'#2a1050',lash:'#2a2038',brow:'#8a8aa8',
 draw(c){const hc=this.hair,{add,part,line,fillp,lin}=c;const pur=pal('#7a3cb0','#52207e','#c69af0','#2a0e48');
  add(8,fillp(`M${CX-120},${90} Q${CX-200},${600} ${CX-170},${1000} Q${CX},${1060} ${CX+170},${1000} Q${CX+200},${600} ${CX+120},${90}Z`,lin([[0,'#b080e0',.5],[1,'#b080e0',.12]]),'stroke="#c8a8f0" stroke-width="1.5" stroke-opacity=".6"')); // veil back
  add(10,longBack(c,hc,{w:100,len:960,wave:4,n:9,dip:20}));
  add(36,sandals(c,pal('#e8c060','#a07a20','#fff0b0','#5a4008'))+[-1,1].map(k=>c.ell(CX+k*40,1606,24,5,'none','stroke="#e8c060" stroke-width="3"')+coin(c,CX+k*40,1614,4)).join(''));
  add(45,slit(c,pur,606,960,90,104,{slitX:62,slitY:840,extra:line(`M${CX+90},${612} Q${CX+40},${760} ${CX+62},${840}`,pur.line,2)})+
   part(`M${CX-92},604 Q${CX},626 ${CX+92},604 L${CX+94},620 Q${CX},642 ${CX-94},620Z`,pal('#f0c850','#b08a20','#fff4c0','#5a4008'),{lw:1.6})+
   Array.from({length:13},(_,i)=>coin(c,CX-84+i*14,640+Math.sin(i/12*Math.PI)*10,5)).join(''));
  add(50,underBust(c,500)+cups(c,pur,{y0:410,y1:500,cx:44,w:52,strap:'#e0b040',extra:(k,x)=>line(`M${x-k*30},${440} Q${x},${452} ${x+k*30},${470}`,'#e0b040',2)})+
   Array.from({length:12},(_,i)=>{const k=i<6?-1:1,j=i%6;return coin(c,CX+k*(14+j*15),497+j*1.5,5);}).join('')+
   [0,1,2,3,4].map(i=>coin(c,CX-28+i*14,320+Math.abs(i-2)*-3+10,4.5)).join(''));
  add(66,[-1,1].map(k=>bangle(c,742,'#e0b040',k,{x:121})+bangle(c,756,'#e0b040',k,{x:122})+bangle(c,400,'#e0b040',k,{x:116,rx:14})).join(''));
  add(100,bangs(c,hc,{n:10,tipY:172,sideL:[[214,420],[204,260]],sideR:[[386,420],[396,260]],str:['M300,70 Q296,120 298,170','M340,80 Q350,140 344,180']}));
  add(108,fillp(`M${CX-110},${130} Q${CX},${40} ${CX+110},${130} Q${CX+130},${200} ${CX+118},${260} Q${CX+96},${150} ${CX},${118} Q${CX-96},${150} ${CX-118},${260} Q${CX-130},${200} ${CX-110},${130}Z`,lin([[0,'#a070e0',.55],[1,'#a070e0',.2]]),'stroke="#d8c0ff" stroke-width="1.5" stroke-opacity=".7"')+
   line(`M${CX-84},${126} Q${CX},${100} ${CX+84},${126}`,'#e0b040',4)+gem(c,CX,112,8,'#b070ff')+[-2,-1,1,2].map(i=>coin(c,CX+i*34,118+Math.abs(i)*5,4)).join('')+earrings(c,'#b070ff'));
  add(120,orbs(c,'#b070ff'));
 }};
// ======================= 자이라 (g_dancer) =======================
H.g_dancer={name:'자이라',skin:pal('#d79a6c','#b0704a','#f4c8a0','#5a3020'),hair:pal('#9a2232','#6a1020','#e0606a','#3a0810'),eyes:'#e0a020',eyesLight:'#fff0a0',eyesDark:'#4a2008',lash:'#2a1010',
 draw(c){const hc=this.hair,{add,part,line,fillp,lin}=c;const red=pal('#c0203a','#880f22','#ff7a80','#3a0610'),gold=pal('#f0c850','#b08a20','#fff4c0','#5a4008');
  add(10,longBack(c,hc,{w:116,len:980,wave:16,n:9,flare:20,dip:24}));
  add(36,sandals(c,gold)+[-1,1].map(k=>c.ell(CX+k*40,1604,24,5,'none','stroke="#e8c060" stroke-width="3"')+coin(c,CX+k*34,1612,4)+coin(c,CX+k*48,1612,4)).join(''));
  // bikini bottom + low sheer chiffon skirt
  add(44,part(`M${CX-104},686 Q${CX},708 ${CX+104},686 Q${CX+50},770 ${CX},820 Q${CX-50},770 ${CX-104},686Z`,red,{lw:2}));
  add(45,fillp(`M${CX-112},676 Q${CX},700 ${CX+112},676 Q${CX+150},820 ${CX+136},930 Q${CX+60},960 ${CX},948 Q${CX-60},960 ${CX-136},930 Q${CX-150},820 ${CX-112},676Z`,lin([[0,'#ff5a70',.55],[1,'#ff5a70',.28]]),'stroke="#ffb0b8" stroke-width="1.6" stroke-opacity=".8"')+
   [-3,-2,-1,0,1,2,3].map(i=>line(`M${CX+i*30},${700} Q${CX+i*36},${820} ${CX+i*40},${940}`,'#ffd0d8',1.2,'opacity=".6"')).join('')+
   part(`M${CX-112},670 Q${CX},694 ${CX+112},670 L${CX+114},686 Q${CX},710 ${CX-114},686Z`,gold,{lw:1.6})+Array.from({length:15},(_,i)=>coin(c,CX-98+i*14,704+Math.sin(i/14*Math.PI)*12,5)).join(''));
  add(50,underBust(c,500)+cups(c,red,{y0:404,y1:502,cx:46,w:56,strap:'#e0b040',extra:(k,x)=>line(`M${x-k*30},${436} Q${x},${450} ${x+k*34},${472}`,'#e0b040',2.2)})+
   Array.from({length:12},(_,i)=>{const k=i<6?-1:1,j=i%6;return coin(c,CX+k*(14+j*16),499+j*1.5,5.5)+(j%2?c.circ(CX+k*(14+j*16),512,3.5,'#ffe070','stroke="#6a4a08" stroke-width="1"'):'');}).join(''));
  add(66,[-1,1].map(k=>bangle(c,742,'#e0b040',k,{x:121})+bangle(c,758,'#e0b040',k,{x:123})+part(`M${CX+k*100},${410} L${CX+k*126},${408} L${CX+k*126},${426} L${CX+k*100},${428}Z`,gold,{lw:1.4})).join(''));
  add(100,bangs(c,hc,{n:9,tipY:176,edgeLen:40,sideL:[[206,440],[196,280]],sideR:[[394,440],[404,280]],str:['M300,70 Q290,120 296,170','M260,90 Q240,150 250,190','M344,84 Q360,140 350,186']}));
  add(108,line(`M${CX-86},${130} Q${CX},${150} ${CX+86},${130}`,'#e0b040',3)+line(`M${CX-70},${110} Q${CX},${126} ${CX+70},${110}`,'#e0b040',2.4)+gem(c,CX,148,7,'#ff3040')+coin(c,CX-40,144,4)+coin(c,CX+40,144,4)+earrings(c,'#ffd040',238));
 }};
// ======================= 마렌 (f_diver) =======================
H.f_diver={browGap:1,name:'마렌',skin:pal('#c98c5e','#a0663e','#ecc09a','#4a2a18'),hair:pal('#22262e','#0e1016','#5a6a80','#05060a'),eyes:'#2ab89a',eyesLight:'#c0fff0',eyesDark:'#06302a',lash:'#0a0a0a',
 draw(c){const hc=this.hair,{add,part,line,fillp,lin}=c;const teal=pal('#1e8a8a','#0e5a60','#7ae0d8','#062a30');
  // high ponytail
  add(10,lock(c,hc,[[290,70],[330,30,.1],[400,40,.15],[440,120,.1],[452,260,-.08],[470,420,.1],[440,560],[430,420,-.1],[410,280,.08],[400,160,-.1],[350,100,.1]],.1,{extra:strands(c,hc,['M400,60 Q440,200 450,380','M380,80 Q420,220 430,420'])})+
   lock(c,hc,[[214,140],[206,250],[220,300],[300,280],[380,300],[394,250],[386,140]],.05));
  add(5,line(`M${CX+144},${260} L${CX+144},${1660}`,'#6a4a2a',9)+line(`M${CX+144},${260} L${CX+144},${1660}`,'#a07a50',4)+part(`M${CX+144},${170} L${CX+158},${260} L${CX+144},${250} L${CX+130},${260}Z`,pal('#d8e0e8','#8a98a8','#fff','#3a4450'),{lw:2}));
  add(35,boots(c,teal,1450,{cuff:20,cuffCol:'#0e5a60',extra:P=>fillp(`M${P[0][0]},${1470} l${(P[0][0]>300?24:-24)},-30 l${(P[0][0]>300?-6:6)},60Z`,'#7ae0d8','stroke="#062a30" stroke-width="2"')}));
  add(44,part(`M${CX-100},676 Q${CX},694 ${CX+100},676 Q${CX+48},764 ${CX},814 Q${CX-48},764 ${CX-100},676Z`,teal,{lw:2}));
  // fishnet sarong
  add(45,(()=>{const d=`M${CX-112},670 Q${CX},690 ${CX+112},670 Q${CX+150},820 ${CX+120},940 L${CX+20},930 Q${CX-60},800 ${CX-112},670Z`;const cp=c.clip(d);let net='';
   for(let i=-20;i<20;i++)net+=line(`M${CX+i*18},${660} l${300},${300} M${CX+i*18},${660} l${-300},${300}`,'#0e3a40',1.4);
   return `<g clip-path="${cp}"><path d="${d}" fill="#1e8a8a" fill-opacity=".18"/>${net}</g>`+line(d,'#0e3a40',2)+part(`M${CX-110},664 Q${CX},684 ${CX+110},664 L${CX+112},680 Q${CX},702 ${CX-112},680Z`,pal('#c8b080','#8a7040','#fff0c0','#3a2a10'),{lw:1.6});})());
  add(50,underBust(c,500)+cups(c,teal,{y0:404,y1:502,cx:46,w:56,strap:'#0e3a40',extra:(k,x)=>[0,1,2].map(j=>line(`M${x-k*34+j*k*8},${440+j*16} Q${x+j*k*4},${430+j*18} ${x+k*34},${452+j*14}`,'#7ae0d8',1.6,'opacity=".8"')).join('')}));
  add(66,[-1,1].map(k=>bracer(c,teal,690,760,{})).join('').slice(0,0)+bracer(c,teal,690,760,{extra:k=>line(`M${CX+k*108},${716} L${CX+k*136},${716}`,'#7ae0d8',2)}));
  add(100,bangs(c,hc,{n:8,tipY:166,edgeLen:30,sideL:[[214,300],[206,240]],sideR:[[386,300],[394,240]],str:['M300,70 Q300,120 296,166','M330,74 Q350,120 344,170']}));
  add(108,[0,1,2,3,4,5,6].map(i=>{const t=i/6,x=CX-46+t*92,y=338+Math.sin(t*Math.PI)*26;return c.ell(x,y,6,5,'#fff6ea','stroke="#a08870" stroke-width="1.4"');}).join('')+c.ell(CX,370,9,7,'#f8f0ff','stroke="#a090b0" stroke-width="1.6"')+line(`M${CX-46},${338} Q${CX},${370} ${CX+46},${338}`,'#a08870',1.2)+
   c.ell(CX+60,76,14,8,'#2ab89a','stroke="#062a30" stroke-width="2"'));
  add(120,c.ell(CX+144,800,20,24,c.C.skin.base,`stroke="${c.C.skin.line}" stroke-width="2.4"`)); // hand gripping the harpoon
 }};
// ======================= 로자린드 (e_tailor) =======================
H.e_tailor={name:'로자린드',skin:pal('#fde4d8','#ecb8a6','#fff6f0','#6a3a34'),hair:pal('#d02a34','#981624','#ff8a8a','#4a0810'),eyes:'#d02040',eyesLight:'#ffb0b0',eyesDark:'#3a0610',lash:'#1a0808',
 draw(c){const hc=this.hair,{add,part,line,fillp,lin}=c;const blk=pal('#2a2a32','#121218','#7a7a90','#000000');
  add(10,lock(c,hc,[[300,60],[396,100,-.12],[412,220,-.1],[404,330,-.1],[392,350],[300,300],[208,350],[196,330],[188,220,-.1],[204,100,-.12]],.1));
  // flame thigh-high boots
  add(35,(()=>{let s='';for(const leg of[c.G.legL,c.G.legR]){const cp=c.clip(leg);let fl='';for(let i=0;i<8;i++){const x=150+i*42;fl+=fillp(`M${x},1640 Q${x-14},1500 ${x+6},1420 Q${x+4},1500 ${x+20},1440 Q${x+30},1540 ${x+26},1640Z`,lin([[0,'#ffcf40'],[1,'#e02010']]),'opacity=".9"');}
   s+=`<g clip-path="${cp}"><path d="M0,1000 Q300,1016 600,1000 V1720 H0Z" fill="#1c1c22"/>${fl}<path d="M0,1000 Q300,1016 600,1000 V1720 H0Z" fill="${lin([[0,'#fff',.12],[.5,'#fff',0],[1,'#000',.3]],0,0,1,0)}"/><path d="M0,1000 Q300,1016 600,1000 V1016 Q300,1032 0,1016Z" fill="#c02020"/></g>`+line(leg,'#000',2.4);}return s;})());
  add(45,slit(c,blk,604,958,92,98,{slitX:70,slitY:880,extra:line(`M${CX-92},${640} Q${CX},${656} ${CX+92},${640}`,'#c02030',3)+[0,1,2,3].map(i=>line(`M${CX-60+i*40},${700} l0,200`,'#3a3a46',1.4)).join('')})+
   part(`M${CX-94},612 Q${CX},632 ${CX+94},612 L${CX+96},628 Q${CX},650 ${CX-96},628Z`,blk,{lw:1.6})+part(`M${CX-14},618 h28 v22 h-28z`,pal('#c0c0cc','#7a7a88','#fff','#202028'),{lw:1.6})+
   [0,1,2].map(i=>c.ell(CX-110,680+i*14,28,10,'none','stroke="#a01424" stroke-width="5"')).join(''));
  // leather bustier (ends under the bust)
  add(50,underBust(c,504)+part(c.sm(c.sym([[0,450],[20,412],[50,398],[86,410],[104,440],[100,474],[94,500],[60,510],[0,500]])),blk,{sh:[-10,-6],extra:
   [-1,1].map(k=>line(`M${CX+k*8},${452} Q${CX+k*46},${430} ${CX+k*96},${448}`,'#5a5a6a',2)+line(`M${CX+k*52},${404} Q${CX+k*56},${460} ${CX+k*52},${506}`,'#4a4a58',1.8)).join('')+
   [0,1,2].map(i=>line(`M${CX-7},${462+i*13} L${CX+7},${470+i*13} M${CX+7},${462+i*13} L${CX-7},${470+i*13}`,'#c02030',1.6)).join('')})+
   [-1,1].map(k=>line(`M${CX+k*52},${400} Q${CX+k*40},${350} ${CX+k*26},${318}`,'#1a1a20',4)).join('')+part(`M${CX-30},312 Q${CX},330 ${CX+30},312 L${CX+30},324 Q${CX},342 ${CX-30},324Z`,blk,{lw:1.4})+gem(c,CX,334,6,'#ff2040'));
  // long leather gloves
  add(65,[c.G.armL,c.G.armR].map(a=>{const cp=c.clip(a);return `<g clip-path="${cp}"><path d="M0,560 Q300,540 600,560 V1720 H0Z" fill="#1c1c22"/><path d="M0,560 Q300,540 600,560 V580 Q300,560 0,580Z" fill="#c02030"/></g>`+line(a,'#000',2.2);}).join(''));
  add(100,bangs(c,hc,{n:9,tipY:168,edgeLen:30,sideL:[[204,330],[198,250]],sideR:[[396,330],[402,250]],str:['M300,70 Q286,120 290,168','M340,80 Q356,130 348,176','M250,92 Q236,150 240,200']}));
  add(108,earrings(c,'#ff2040',236));
 }};
// ======================= 이벨린 (c_priest) =======================
H.c_priest={name:'이벨린',skin:pal('#fff0ea','#ecc8c0','#ffffff','#7a5050'),hair:pal('#c6e4ff','#8ab8e8','#ffffff','#4a70a0'),eyes:'#4a8ae0',eyesLight:'#d0f0ff',eyesDark:'#0a2050',lash:'#203050',brow:'#7a9ac8',
 draw(c){const hc=this.hair,{add,part,line,fillp,lin}=c;const wht=pal('#ffffff','#d4e0ee','#ffffff','#6a7a98'),fur=pal('#ffffff','#dde6f0','#ffffff','#8a9ab0');
  add(5,line(`M${CX-150},${200} L${CX-150},${1660}`,'#8a9ab8',8)+line(`M${CX-150},${200} L${CX-150},${1660}`,'#e8f0ff',3.5)+
   [0,60,120].map(a=>`<g transform="rotate(${a} ${CX-150} 170)">${part(`M${CX-150},${120} L${CX-140},${170} L${CX-150},${220} L${CX-160},${170}Z`,pal('#d0f0ff','#7ac0f0','#ffffff','#3a70b0'),{lw:1.6})}</g>`).join('')+c.circ(CX-150,170,8,'#bfe8ff','stroke="#3a70b0" stroke-width="2"'));
  add(10,longBack(c,hc,{w:108,len:980,wave:6,n:9,dip:20}));
  add(35,stockings(c,pal('#ffffff','#d8e2f0',null,'#7a8aa8'),1010,{band:14,bandCol:'#bcd6f4'})+boots(c,wht,1500,{cuff:16,cuffCol:'#bcd6f4'}));
  // mermaid mini: tight to the thigh, flared hem
  add(45,part(`M${CX-90},604 Q${CX},622 ${CX+90},604 Q${CX+120},720 ${CX+104},860 Q${CX+150},920 ${CX+150},960 Q${CX},984 ${CX-150},960 Q${CX-150},920 ${CX-104},860 Q${CX-120},720 ${CX-90},604Z`,wht,{sh:[-10,-4],extra:
   line(`M${CX-104},${862} Q${CX},${880} ${CX+104},${862}`,'#9ab8e0',2.4)+[-2,-1,0,1,2].map(i=>line(`M${CX+i*30},${880} Q${CX+i*44},${930} ${CX+i*56},${968}`,'#c8d6ea',1.6)).join('')})+
   gem(c,CX,616,7,'#60b8ff')+line(`M${CX-90},${612} Q${CX},${630} ${CX+90},${612}`,'#9ab8e0',3));
  // fur-trimmed crop top
  add(50,crop(c,wht,508,{neck:404,neckW:380,extra:[-1,1].map(k=>line(`M${CX+k*10},${470} Q${CX+k*50},${452} ${CX+k*96},${470}`,'#c8d6ea',2)).join('')})+
   fillp(c.sm(c.sym([[0,520],[60,520],[100,506],[104,494],[60,506],[0,506]])),'#ffffff','stroke="#a8b8d0" stroke-width="1.6"')+
   [-1,1].map(k=>fillp(`M${CX+k*4},${404} Q${CX+k*40},${376} ${CX+k*100},${346} l${k*6},${14} Q${CX+k*44},${394} ${CX+k*6},${416}Z`,'#ffffff','stroke="#a8b8d0" stroke-width="1.6"')).join('')+gem(c,CX,410,9,'#60b8ff')+
   (()=>{let s='';for(let i=0;i<6;i++){const a=i*Math.PI/3;s+=line(`M${CX},410 l${Math.cos(a)*18},${Math.sin(a)*18}`,'#9ad0ff',2);}return s;})());
  // detached fur sleeves
  add(66,[-1,1].map(k=>{const x0=CX+k*96,x1=CX+k*126;return part(`M${x0},${452} Q${CX+k*112},${446} ${x1+k*2},${452} L${CX+k*150},${770} Q${CX+k*120},${786} ${CX+k*100},${770}Z`,wht,{sh:[-k*5,-3]})+
   part(c.sm([[x0-k*4,450],[CX+k*112,440],[x1+k*6,450],[CX+k*112,464]]),fur,{lw:1.6})+part(c.sm([[CX+k*98,772],[CX+k*124,760],[CX+k*154,772],[CX+k*124,790]]),fur,{lw:1.6})+gem(c,CX+k*124,600,5,'#60b8ff');}).join(''));
  add(100,bangs(c,hc,{n:10,tipY:170,sideL:[[212,430],[202,270]],sideR:[[388,430],[398,270]],str:['M300,70 Q296,120 298,170','M260,86 Q250,130 254,178']}));
  add(108,(()=>{let s='';const x=CX+74,y=106;for(let i=0;i<6;i++){const a=i*Math.PI/3;s+=`<g transform="rotate(${i*60} ${x} ${y})">${part(`M${x},${y-30} L${x+7},${y-10} L${x},${y} L${x-7},${y-10}Z`,pal('#e8f8ff','#8ac8f0','#ffffff','#3a70b0'),{lw:1.4})}</g>`;}return s+gem(c,x,y,6,'#60b8ff');})());
 }};
// ======================= 유나 (d_yuna) — modern-world outfit (only her) =======================
H.d_yuna={browGap:1,name:'유나',skin:pal('#ffe8de','#f0c0b0','#fff8f2','#6a3a34'),hair:pal('#26222e','#121018','#6a6a8a','#050408'),eyes:'#8a5ad0',eyesLight:'#e0c8ff',eyesDark:'#200a40',lash:'#100810',
 draw(c){const hc=this.hair,{add,part,line,fillp,lin}=c;const blk=pal('#2a2a34','#14141a','#6a6a80','#000'),wht=pal('#ffffff','#dcd6e0','#ffffff','#6a6070');
  add(10,longBack(c,hc,{w:106,len:940,wave:3,n:9,dip:16}));
  add(35,stockings(c,pal('#24242c','#101016',null,'#000'),1004,{band:12,bandCol:'#3a3a48'})+(()=>{let s='';for(const k of[-1,1]){const x=CX+k*42;s+=part(`M${x-24},${1640} Q${x},${1620} ${x+24},${1640} L${x+28},${1680} Q${x},${1696} ${x-28},${1680}Z`,pal('#4a2a20','#2a140c','#a07060','#0a0402'),{lw:2});}return s;})());
  add(45,pleatSkirt(c,blk,606,900,84,126,14)+part(`M${CX-86},606 Q${CX},622 ${CX+86},606 L${CX+88},620 Q${CX},638 ${CX-88},620Z`,blk,{lw:1.4})+
   line(`M${CX-88},${640} Q${CX},${690} ${CX+96},${650}`,'#c8c8d8',3,'stroke-dasharray="7 4"')+
   part(`M${CX-118},${700} L${CX-60},${640} L${CX-52},${648} L${CX-110},${708}Z`,pal('#a08060','#6a5030','#e0c0a0','#2a1a0a'),{lw:1.6})+line(`M${CX-110},${708} L${CX-170},${770}`,'#c8d0e0',7)+line(`M${CX-110},${708} L${CX-170},${770}`,'#606878',1.4));
  add(50,crop(c,wht,514,{neck:398,neckW:376,extra:line(`M${CX},${400} L${CX},${430}`,'#c8bcd0',2)+[-1,1].map(k=>line(`M${CX+k*8},${470} Q${CX+k*50},${452} ${CX+k*98},${470}`,'#ccc4d4',2)).join('')})+
   fillp(c.sm(c.sym([[0,526],[60,526],[100,512],[100,500],[60,514],[0,514]])),'#ffffff','stroke="#a8a0b0" stroke-width="1.4"'));
  add(52,[-1,1].map(k=>fillp(`M${CX+k*8},${396} Q${CX+k*50},${376} ${CX+k*96},${372}`,'none')).join(''));
  // off-shoulder puff sleeves (over arms)
  add(66,[-1,1].map(k=>part(c.sm([[CX+k*84,372],[CX+k*120,366],[CX+k*146,396],[CX+k*140,438],[CX+k*104,440],[CX+k*92,410]]),wht,{sh:[-k*6,-4],extra:line(`M${CX+k*100},${436} Q${CX+k*122},${448} ${CX+k*142},${436}`,'#c8c0d0',2.4)})).join('')+
   line(`M${CX-84},${376} Q${CX},${400} ${CX+84},${376}`,'#bdb4c8',2.4));
  add(100,bangs(c,hc,{n:11,tipY:176,edgeLen:24,sideL:[[214,420],[204,270]],sideR:[[386,420],[396,270]],str:['M300,70 Q300,120 300,176','M270,80 Q262,130 266,180','M332,80 Q340,130 334,180']}));
  add(108,part(`M${CX-26},282 Q${CX},292 ${CX+26},282 L${CX+26},294 Q${CX},304 ${CX-26},294Z`,blk,{lw:1.4})+part(`M${CX},${304} c-10,-12 -18,0 0,14 c18,-14 10,-26 0,-14z`,pal('#d03060','#901838','#ff9ab0','#300810'),{lw:1.4}));
 }};
// ======================= 필멸자 (hero) =======================
H.hero={name:'필멸자',male:true,skin:pal('#f8dcc8','#e0b298','#fff2e6','#5a3424'),hair:pal('#22222e','#0e0e16','#5a5a7a','#020208'),eyes:'#8a5a2a',eyesLight:'#f0c890',eyesDark:'#200c04',lash:'#101010',
 browGap:1,exprOver:{smile:{mouth:'smile',lowerUp:3},blush:{mouth:'line',blush:.8},angry:{vein:0}},
 draw(c){const hc=this.hair,{add,part,line,fillp,lin}=c;const blue=pal('#2a4ea8','#1a3274','#7aa0f0','#0a1430'),gold=pal('#e8c050','#a07a20','#fff0b0','#4a3008'),lea=pal('#8a5a34','#5a3618','#c89060','#2a1608'),red=pal('#c02a2a','#801818','#ff7a6a','#300808');
  // cape
  add(5,part(`M${CX-120},330 Q${CX-210},900 ${CX-190},1440 Q${CX},1480 ${CX+190},1440 Q${CX+210},900 ${CX+120},330Z`,red,{sh:[-12,-4]}));
  add(10,'');
  add(30,'');
  // trousers + boots
  add(35,(()=>{let s='';for(const leg of[c.G.legL,c.G.legR]){const cp=c.clip(leg);s+=`<g clip-path="${cp}"><rect x="0" y="700" width="600" height="1020" fill="#5a4030"/><rect x="0" y="700" width="600" height="1020" fill="${lin([[0,'#000',0],[1,'#000',.35]],0,0,1,0)}"/></g>`+line(leg,'#1a0e06',2.4);}return s;})()+boots(c,lea,1340,{cuff:34,cuffCol:'#6a4020'}));
  // tunic coat (to mid-thigh)
  add(45,part(c.sm(c.sym([[0,330],[40,322],[96,336],[130,350],[132,400],[120,470],[106,560],[98,640],[110,760],[122,1000],[60,1010],[0,1000]])),blue,{sh:[-12,-5],extra:
   line(`M${CX},${360} L${CX},${1000}`,'#0a1430',2.4)+line(`M${CX-6},${360} L${CX-6},${1000}`,'#e8c050',3)+line(`M${CX+6},${360} L${CX+6},${1000}`,'#e8c050',3)+
   line(`M${CX-120},${996} Q${CX},${1016} ${CX+120},${996}`,'#e8c050',5)})+
   part(c.sm(c.sym([[0,350],[40,318],[64,316],[50,360],[24,400],[0,420]])),pal('#e8e4dc','#b8b0a0','#fff','#3a3428'),{lw:2})+
   part(`M${CX-104},640 Q${CX},660 ${CX+104},640 L${CX+106},676 Q${CX},696 ${CX-106},676Z`,lea,{lw:2})+part(`M${CX-16},648 h32 v30 h-32z`,gold,{lw:2})+
   part(`M${CX-128},${690} L${CX-60},${640} L${CX-52},${652} L${CX-120},${702}Z`,lea,{lw:1.6})+line(`M${CX-122},${700} L${CX-210},${780}`,'#c8d0e0',10)+line(`M${CX-122},${700} L${CX-210},${780}`,'#606878',2)+part(`M${CX-62},${628} l18,18 l-6,6 l-18,-18z`,gold,{lw:1.4}));
  // arms (sleeves) + pauldrons + bracers
  add(65,[c.G.armL,c.G.armR].map(a=>{const cp=c.clip(a);return `<g clip-path="${cp}"><rect x="0" y="300" width="600" height="440" fill="#2a4ea8"/><rect x="0" y="300" width="600" height="440" fill="${lin([[0,'#000',0],[1,'#000',.3]],0,0,1,0)}"/></g>`+line(a,'#0a1430',2.4);}).join('')+
   bracer(c,lea,660,770,{x0:118,x1:150,x2:126,x3:160,extra:k=>line(`M${CX+k*122},${700} L${CX+k*154},${700}`,'#e8c050',2.4)})+
   [-1,1].map(k=>part(c.sm([[CX+k*96,336],[CX+k*140,340],[CX+k*162,384],[CX+k*150,420],[CX+k*118,404],[CX+k*102,372]]),pal('#c8ccd8','#7a8090','#ffffff','#20242e'),{sh:[-k*6,-4],extra:line(`M${CX+k*110},${396} Q${CX+k*140},${404} ${CX+k*156},${400}`,'#e8c050',3)})).join('')+
   c.ell(CX-140,782,18,6,'none','stroke="#6ac8ff" stroke-width="5"')+gem(c,CX-140,786,5,'#40b0ff'));
  // spiky hair
  add(100,(()=>{const P=[[212,200],[200,150,-.1],[176,120],[214,98,-.1],[204,56],[250,66,-.1],[268,22],[300,52,-.1],[340,18],[350,62,-.1],[398,48],[392,96,-.1],[428,112],[396,140,-.1],[392,200],
   [376,176,.05],[370,206],[350,156,.05],[334,196],[318,150,.05],[300,192],[286,148,.05],[262,190],[252,152,.05],[232,196],[226,166,.05]];
   return c.part(qpath(P,.05),hc,{sh:[-6,-8],extra:window.TACHIE_HELP.hairRing(c,hc,100,60)});})());
 }};
})();
