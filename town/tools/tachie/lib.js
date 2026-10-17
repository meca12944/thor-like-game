// Procedural vector "tachie" (full-body standing art) builder. Canvas 600x1720, figure centred at x=300.
// Exports window.TACHIE_ART.build(charId, expr) -> SVG string. Characters: tools/tachie/chars.js
(function(){
const CX=300;
let defs=[],uid=0;
const nid=p=>(p||'i')+(++uid);
// Catmull-Rom spline through points -> cubic bezier path
function sm(P,closed=true,t=0.5){const n=P.length;if(n<2)return'';let d=`M${P[0][0].toFixed(1)},${P[0][1].toFixed(1)}`;
 const g=i=>closed?P[(i+n)%n]:P[Math.max(0,Math.min(n-1,i))];const last=closed?n:n-1;
 for(let i=0;i<last;i++){const p0=g(i-1),p1=g(i),p2=g(i+1),p3=g(i+2);
  const c1=[p1[0]+(p2[0]-p0[0])*t/3,p1[1]+(p2[1]-p0[1])*t/3],c2=[p2[0]-(p3[0]-p1[0])*t/3,p2[1]-(p3[1]-p1[1])*t/3];
  d+=`C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;}
 return d+(closed?'Z':'');}
// right-half points given as [dx,y] -> absolute; sym() builds a closed symmetric outline
const R=pts=>pts.map(([x,y])=>[CX+x,y]);
const L=pts=>pts.map(([x,y])=>[CX-x,y]);
function sym(half){const r=R(half),l=L(half.slice().reverse());return r.concat(l);}
const mirrorPts=P=>P.map(([x,y])=>[2*CX-x,y]);
function clip(d){const id=nid('c');defs.push(`<clipPath id="${id}"><path d="${d}"/></clipPath>`);return `url(#${id})`;}
function lin(stops,x1=0,y1=0,x2=0,y2=1){const id=nid('g');defs.push(`<linearGradient id="${id}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}">${stops.map(([o,c,a])=>`<stop offset="${o}" stop-color="${c}"${a!=null?` stop-opacity="${a}"`:''}/>`).join('')}</linearGradient>`);return `url(#${id})`;}
function rad(stops,cx=.5,cy=.5,r=.5){const id=nid('r');defs.push(`<radialGradient id="${id}" cx="${cx}" cy="${cy}" r="${r}">${stops.map(([o,c,a])=>`<stop offset="${o}" stop-color="${c}"${a!=null?` stop-opacity="${a}"`:''}/>`).join('')}</radialGradient>`);return `url(#${id})`;}
// cel-shaded part: shadow fill + lit fill shifted toward the light (upper-left) + soft gloss + outline
function part(d,c,o={}){const sh=o.sh||[-9,-5],lw=o.lw==null?2.6:o.lw,line=o.line||c.line||'#3a2420';const cp=clip(d);
 let s=`<g${o.op!=null?` opacity="${o.op}"`:''}><path d="${d}" fill="${c.shade}"/>`;
 s+=`<g clip-path="${cp}"><path d="${d}" fill="${c.base}" transform="translate(${sh[0]},${sh[1]})"/>`;
 if(c.deep)s+=`<path d="${d}" fill="${c.deep}" transform="translate(${-sh[0]*2.2+4},${-sh[1]*2.2+6})" opacity="0" />`;
 if(o.extra)s+=o.extra;
 if(c.hi&&!o.nohi)s+=`<path d="${d}" fill="${lin([[0,c.hi,.55],[.35,c.hi,0]],0,0,.7,1)}"/>`;
 s+=`</g>`;if(lw)s+=`<path d="${d}" fill="none" stroke="${line}" stroke-width="${lw}" stroke-linejoin="round" stroke-linecap="round"/>`;return s+'</g>';}
const line=(d,col,w=2,extra='')=>`<path d="${d}" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" ${extra}/>`;
const fillp=(d,col,extra='')=>`<path d="${d}" fill="${col}" ${extra}/>`;
const circ=(x,y,r,f,extra='')=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${f}" ${extra}/>`;
const ell=(x,y,rx,ry,f,extra='')=>`<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="${f}" ${extra}/>`;
const shift=(P,dx,dy)=>P.map(([x,y])=>[x+dx,y+dy]);

// ---------------- body geometry (female; hero overrides via body.male) ----------------
function bodyGeo(m){ // m=male
 const s=m?1.12:1;
 const neck=sym([[m?28:21,236],[m?30:23,300],[m?34:28,322]]);
 const torso=m?sym([[34,312],[78,328],[124,346],[132,380],[118,420],[110,480],[100,560],[86,620],[90,690],[96,760],[96,830],[76,880],[0,892]])
  :sym([[26,312],[66,326],[100,342],[110,372],[100,410],[100,458],[88,516],[60,586],[66,640],[96,706],[116,772],[112,834],[82,878],[0,892]]);
 const armR=m?[[118,344],[144,370],[150,440],[146,520],[144,600],[150,680],[156,760],[164,800],[166,850],[152,880],[134,872],[130,828],[130,770],[124,690],[118,600],[116,500],[112,420]]
  :[[100,340],[118,368],[124,430],[122,510],[124,590],[130,670],[136,748],[142,786],[144,836],[132,866],[116,858],[112,816],[110,762],[104,686],[98,596],[96,500],[92,418]];
 const legR=m?[[96,770],[100,880],[96,1010],[84,1150],[78,1250],[84,1340],[80,1430],[66,1540],[58,1612],[64,1650],[76,1680],[28,1686],[26,1640],[28,1608],[28,1500],[24,1400],[20,1300],[18,1240],[14,1100],[6,900],[0,892]]
  :[[112,776],[116,868],[106,1000],[86,1150],[74,1242],[80,1330],[78,1420],[62,1540],[50,1612],[56,1648],[70,1680],[30,1686],[26,1644],[26,1606],[26,1500],[22,1400],[18,1300],[16,1242],[12,1100],[6,900],[0,892]];
 return {neck:sm(neck),torso:sm(torso),armR:sm(R(armR)),armL:sm(L(armR)),legR:sm(R(legR)),legL:sm(L(legR)),armPts:armR,legPts:legR};}

// ---------------- face ----------------
const FACE_F={top:80,chin:280,eyeY:198,eyeDX:39,mouthY:252};
function head(o){const m=o.male;const d=m?sm([[222,140],[226,206],[250,252],[286,284],[300,290],[314,284],[350,252],[374,206],[378,140],[300,70]])
 :sm([[221,140],[224,204],[246,246],[282,274],[300,281],[318,274],[354,246],[376,204],[379,140],[300,74]]);return d;}
function ears(c,m){const y=m?190:186;let s='';for(const k of[-1,1]){const x=CX+k*(m?78:77);const d=sm([[x,y-14],[x+k*14,y-16],[x+k*16,y+8],[x+k*6,y+30],[x-k*2,y+28]]);s+=part(d,c.skin,{lw:2,sh:[-k*4,-2]});}return s;}
function eye(o,k,E){ // k=-1 left (viewer), 1 right
 const m=o.male,ex=CX+k*(m?37:39),ey=(m?200:198)+(E.eyeDY||0),w=m?24:28,col=o.eyes;
 const open=E.open==null?1:E.open; // 1 normal, >1 wide, <1 narrowed, 0 closed (happy arc)
 let s='';
 if(open===0){ // closed happy arc
  s+=line(`M${ex-w},${ey+2} Q${ex},${ey-16} ${ex+w},${ey+2}`,o.lash||'#2a1a18',4.5);return s;}
 const topY=ey-(m?17:27)*open+(E.lidDrop||0),botY=ey+(m?15:21)*Math.min(open,1.15)-(E.lowerUp||0);
 const inner=ex-k*w,outer=ex+k*(w+2);
 const tilt=(E.outerDown||0)*k; // sad: outer corner down
 const iy0=ey+1+(E.inDown||0),oy=ey-4+(E.outerDown||0),tc=[ex-k*6+(E.inDown?k*8:0),2*topY-ey-6+(E.inDown||0)*.6],bc=[ex+k*6,2*botY-ey+2];
 const white=`M${inner},${iy0} Q${tc[0]},${tc[1]} ${outer},${oy} Q${bc[0]},${bc[1]} ${inner},${iy0}Z`;
 const cp=clip(white);
 s+=fillp(white,'#fffaf6');
 const ir=(m?13:18.5)*(E.iris||1),iy=ey+3+(E.look?E.look[1]:0),ix=ex+(E.look?E.look[0]:0)-k*1;
 s+=`<g clip-path="${cp}">`;
 s+=fillp(white,'#e8d8dc','transform="translate(0,6)" opacity=".0"');
 s+=ell(ix,iy,ir*.92,ir*1.18,lin([[0,o.eyesDark||'#2a1830'],[.45,col],[1,o.eyesLight||'#ffe6a0']]));
 s+=ell(ix,iy+1,ir*.48*(E.pupil||1),ir*.62*(E.pupil||1),o.eyesDark||'#24121c');
 s+=ell(ix,iy+ir*.55,ir*.6,ir*.35,o.eyesLight||'#fff2c0','opacity=".55"');
 s+=fillp(`M${inner-4},${ey-30} L${outer+4},${ey-30} L${outer+4},${topY+8} Q${ex},${topY+2} ${inner-4},${topY+10}Z`,'#3a2028','opacity=".22"'); // lid shadow
 s+=circ(ix-k*5-3,iy-ir*.45,ir*.3,'#fff');s+=circ(ix+k*5+2,iy+ir*.4,ir*.14,'#fff','opacity=".9"');
 s+='</g>';
 // upper lash: thick
 s+=line(`M${inner+k*1},${iy0} Q${tc[0]},${tc[1]} ${outer},${oy}`,o.lash||'#2a1a18',m?4.5:5.5);
 if(!m)s+=line(`M${outer-k*2},${ey-4+(E.outerDown||0)} l${k*8},${-5+(E.outerDown||0)*.5}`,o.lash||'#2a1a18',3.5); // outer flick
 s+=line(`M${ex-k*2},${botY+1} Q${ex+k*12},${botY} ${outer-k*3},${ey+6}`,o.lash||'#5a3430',1.8,'opacity=".7"');
 if(E.lidLine)s+=line(`M${inner+k*4},${topY-4} Q${ex},${topY-12} ${outer-k*2},${ey-10}`,o.lash||'#5a3430',1.4,'opacity=".6"');
 return s;}
function brows(o,E){let s='';const m=o.male;for(const k of[-1,1]){const ex=CX+k*(m?37:39),by=(m?160:152)+(E.browY||0);
 const inY=by+(E.browIn||0),outY=by+(E.browOut||0)-2;const w=m?5.5:3.4;
 const bd=`M${ex-k*20},${inY} Q${ex+k*2},${Math.min(inY,outY)-8} ${ex+k*26},${outY+4}`;if(o.browGap)s+=line(bd,o.skin.base,w+5);s+=line(bd,o.brow||o.hair.line,w);}
 return s;}
function mouth(o,E){const y=(o.male?258:252),x=CX;const lip=o.lip||'#b85a5a';let s='';
 switch(E.mouth){
  case 'line':s+=line(`M${x-9},${y} Q${x},${y+3} ${x+9},${y}`,'#7a3a34',2.4);break;
  case 'smile':s+=line(`M${x-12},${y-2} Q${x},${y+7} ${x+12},${y-2}`,'#7a3a34',2.6);break;
  case 'open':s+=fillp(`M${x-15},${y-3} Q${x},${y-1} ${x+15},${y-3} Q${x+9},${y+18} ${x},${y+18} Q${x-9},${y+18} ${x-15},${y-3}Z`,'#8a2c34');
   s+=fillp(`M${x-8},${y+12} Q${x},${y+7} ${x+8},${y+12} Q${x},${y+18} ${x-8},${y+12}Z`,'#e7787e');s+=fillp(`M${x-13},${y-2} Q${x},${y} ${x+13},${y-2} L${x+11},${y+2} Q${x},${y+4} ${x-11},${y+2}Z`,'#fff');
   s+=line(`M${x-15},${y-3} Q${x},${y-1} ${x+15},${y-3} Q${x+9},${y+18} ${x},${y+18} Q${x-9},${y+18} ${x-15},${y-3}Z`,'#5a1e22',2);break;
  case 'frown':s+=line(`M${x-10},${y+4} Q${x},${y-3} ${x+10},${y+4}`,'#7a3a34',2.6);break;
  case 'grit':s+=fillp(`M${x-13},${y+4} Q${x},${y-4} ${x+13},${y+4} L${x+10},${y+12} Q${x},${y+8} ${x-10},${y+12}Z`,'#fff','stroke="#5a1e22" stroke-width="2.2"');s+=line(`M${x-11},${y+7} Q${x},${y+2} ${x+11},${y+7}`,'#c0a0a0',1.2);break;
  case 'shout':s+=fillp(`M${x-13},${y+1} Q${x},${y-6} ${x+13},${y+1} Q${x+8},${y+15} ${x},${y+15} Q${x-8},${y+15} ${x-13},${y+1}Z`,'#8a2c34');
   s+=fillp(`M${x-11},${y} Q${x},${y-5} ${x+11},${y} L${x+10},${y+3} Q${x},${y-1} ${x-10},${y+3}Z`,'#fff');
   s+=line(`M${x-13},${y+1} Q${x},${y-6} ${x+13},${y+1} Q${x+8},${y+15} ${x},${y+15} Q${x-8},${y+15} ${x-13},${y+1}Z`,'#5a1e22',2);break;
  case 'o':s+=ell(x,y+5,7,9,'#8a2c34','stroke="#5a1e22" stroke-width="2"');s+=ell(x,y+9,4,3,'#e7787e');break;
  case 'wavy':s+=line(`M${x-11},${y+1} q${5.5},-5 11,0 q5.5,5 11,0`,'#7a3a34',2.4);break;
  case 'pout':s+=line(`M${x-7},${y+3} Q${x},${y-1} ${x+7},${y+3}`,'#7a3a34',2.4);s+=line(`M${x-4},${y+7} Q${x},${y+9} ${x+4},${y+7}`,'#b06060',1.6);break;}
 return s;}
function face(o,E){let s='';const m=o.male;
 // blush base (always a hint for women)
 const bl=E.blush||0;if(!m||bl>0){for(const k of[-1,1]){s+=ell(CX+k*48,236,24,11,rad([[0,'#ff7a8a',.18+bl*.45],[1,'#ff7a8a',0]]));
  if(bl>0.5)for(let i=0;i<3;i++)s+=line(`M${CX+k*(36+i*8)},${242} l${k*-5},${-9}`,'#e0505e',1.6,'opacity=".7"');}}
 s+=eye(o,-1,E);s+=eye(o,1,E);
 // nose
 s+=line(`M${CX+3},${m?228:224} q2,4 -3,6`,'#c08070',1.8);
 s+=mouth(o,E);
 if(E.tear){for(const k of[-1,1])s+=fillp(`M${CX+k*44},${214} q${-k*3},12 0,16 q${k*4},-4 0,-16Z`,'#9fdcff','stroke="#5aa0d0" stroke-width="1.2"');}
 if(E.sweat)s+=fillp(`M${CX+76},${140} q-6,14 0,18 q6,-4 0,-18Z`,'#bfe8ff','stroke="#5aa0d0" stroke-width="1.5"');
 if(E.vein)s+=line(`M${CX+50},${118} l8,8 m0,-8 l-8,8 m-2,-4 l12,0`,'#d0303a',3);
 return s;}
const EXPR={
 neutral:{mouth:'line'},
 smile:{mouth:'open',lowerUp:5,browY:-3,open:.95},
 happy:{mouth:'open',open:0,browY:-4},
 angry:{mouth:'grit',browIn:18,browOut:-8,open:.8,inDown:7,iris:.92,vein:1},
 sad:{mouth:'frown',browIn:-10,browOut:8,outerDown:4,open:.82,lidDrop:4,look:[0,3],tear:1},
 surprised:{mouth:'o',browY:-10,open:1.18,iris:.86,pupil:.7,sweat:1},
 blush:{mouth:'wavy',blush:1,open:.86,lidDrop:2,look:[-5,2],browIn:-4,browOut:2},
};
// ------------- build -------------
function build(C,exprName){defs=[];uid=0;const E=Object.assign({},EXPR.neutral,EXPR[exprName]||{},(C.exprOver||{})[exprName]||{});
 const G=bodyGeo(C.male);const ctx={C,G,E,CX,sm,sym,R,L,part,line,fillp,circ,ell,clip,lin,rad,shift,mirrorPts};
 const layers=[];const add=(z,s)=>layers.push([z,s]);ctx.add=add;
 const skin=C.skin;
 // base body
 add(30,part(G.legL,skin,{sh:[-7,-3]})+part(G.legR,skin,{sh:[-7,-3]}));
 add(40,part(G.torso,skin,{sh:[-10,-4],extra:C.male?'':
  line(`M${CX},${600} q-2,10 0,16`,'#c0806e',2.2)+line(`M${CX-50},${560} Q${CX-30},${600} ${CX-34},${660}`,skin.shade,5,'opacity=".2"')+line(`M${CX+50},${560} Q${CX+30},${600} ${CX+34},${660}`,skin.shade,5,'opacity=".2"')+
  line(`M${CX-30},${336} Q${CX-60},${330} ${CX-86},${344}`,skin.shade,2.4,'opacity=".8"')+line(`M${CX+30},${336} Q${CX+60},${330} ${CX+86},${344}`,skin.shade,2.4,'opacity=".8"')}));
 add(60,part(G.armL,skin,{sh:[-6,-3]})+part(G.armR,skin,{sh:[-6,-3]}));
 add(70,part(G.neck,skin,{sh:[-8,-10],extra:fillp(`M${CX-30},${250} Q${CX},${300} ${CX+30},${250} L${CX+30},${240} L${CX-30},${240}Z`,skin.shade)}));
 add(80,ears(C,C.male)+part(head(C),skin,{sh:[-7,-4],lw:2.6}));
 add(90,face(C,E));add(105,`<g opacity="${C.browOp||.9}">${brows(C,E)}</g>`);
 C.draw(ctx);
 layers.sort((a,b)=>a[0]-b[0]);
 return `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="1720" viewBox="0 0 600 1720"><defs>${defs.join('')}</defs>${layers.map(l=>l[1]).join('')}</svg>`;}
window.TACHIE_ART={build,EXPR,sm,CX};
})();
