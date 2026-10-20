import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]);s=s.replace(a,b)
rep("function attack(){if(P.dead||P.air)return;if(P.st==='atk'){P.queued=true;return;}if(P.st==='dash'||P.st==='hurt'||P.st==='cast')return;P.combo=1;start('atk','hit1_'+dirKey());}",
"""// up/down attack feel test (owner 2026-10-20): M cycles 0 = current, A = diagonal art + code FX (lunge along the diagonal, thrust streak /
// crescent, tip spark, afterimage, contact stretch), B = side attack art while facing up/down + the same diagonal FX / hit box.
let ATKMODE=0;const ATKNAME=['현재','A 대각선+연출','B 옆모습 공격+연출'];const FXL=[];
const isDiag=k=>k!=='right'&&k!=='left';
function atkClip(n,dk){return 'hit'+n+'_'+(ATKMODE===2&&isDiag(dk)?(dk.endsWith('l')?'left':'right'):dk);}
function attack(){if(P.dead||P.air)return;if(P.st==='atk'){P.queued=true;return;}if(P.st==='dash'||P.st==='hurt'||P.st==='cast')return;P.combo=1;P.ad=dirKey();start('atk',atkClip(1,P.ad));}""")
rep("if(P.queued&&P.combo<3&&P.t>=C.cancel){P.queued=false;P.combo++;start('atk','hit'+P.combo+'_'+dirKey());return;}}",
    "if(P.queued&&P.combo<3&&P.t>=C.cancel){P.queued=false;P.combo++;P.ad=dirKey();start('atk',atkClip(P.combo,P.ad));return;}}")
rep("    if(P.st==='atk'){const C=COMBO[P.combo-1],dir=DV[P.clip.split('_')[1]];\n      if(P.t<C.hit)moveHero(dir[0]*.9,dir[1]*.9);   // step into the swing",
"""    if(P.st==='atk'){const C=COMBO[P.combo-1],dir=DV[P.ad||P.clip.split('_')[1]],fxOn=ATKMODE>0&&isDiag(P.ad||'');
      if(P.t<C.hit)moveHero(dir[0]*.9,dir[1]*.9);   // step into the swing
      if(fxOn&&P.t>=C.hit-2&&P.t<C.hit+3)moveHero(dir[0]*(P.combo===3?3.5:2.5),dir[1]*(P.combo===3?3.5:2.5)); // A/B: burst lunge along the diagonal
      if(fxOn&&P.t===C.hit)FXL.push({t:0,dir,combo:P.combo,r:C.r});""")
rep("if(showHB){ctx.strokeStyle='rgba(120,200,255,.9)';ctx.beginPath();ctx.ellipse(sx,sy,HERO_R,HERO_R/1.4,0,0,7);ctx.stroke();\n      if(P.st==='atk'){const C=COMBO[P.combo-1],dir=DV[P.clip.split('_')[1]];",
    "if(showHB){ctx.strokeStyle='rgba(120,200,255,.9)';ctx.beginPath();ctx.ellipse(sx,sy,HERO_R,HERO_R/1.4,0,0,7);ctx.stroke();\n      if(P.st==='atk'){const C=COMBO[P.combo-1],dir=DV[P.ad||P.clip.split('_')[1]];")
old="    if(!blink){if(P.white>0){ctx.save();ctx.filter='brightness(0) invert(1)';ctx.drawImage(SH[s],x,y,w,h,sx-ax,sy-ay,w,h);ctx.restore();P.white--;}else ctx.drawImage(SH[s],x,y,w,h,sx-ax,sy-ay,w,h);}"
new="""    const AC=P.st==='atk'?COMBO[P.combo-1]:null,fxOn=AC&&ATKMODE>0&&isDiag(P.ad||''),ct=AC?P.t-AC.hit:-99,adv=fxOn?DV[P.ad]:null;
    if(!blink&&fxOn&&ct>=0&&ct<5){ctx.save();ctx.globalAlpha=.35*(1-ct/5);ctx.drawImage(SH[s],x,y,w,h,sx-ax-Math.round(adv[0]*10),sy-ay-Math.round(adv[1]*10),w,h);ctx.restore();} // afterimage
    const st=fxOn&&ct>=0&&ct<3;if(st){ctx.save();ctx.translate(sx,sy);ctx.scale(1.07,.95);ctx.translate(-sx,-sy);} // contact stretch
    if(!blink){if(P.white>0){ctx.save();ctx.filter='brightness(0) invert(1)';ctx.drawImage(SH[s],x,y,w,h,sx-ax,sy-ay,w,h);ctx.restore();P.white--;}else ctx.drawImage(SH[s],x,y,w,h,sx-ax,sy-ay,w,h);}
    if(st)ctx.restore();
    for(const f of FXL){const L=f.combo===3?12:9,k=f.t/L,cx=sx,cy=sy-44,d=f.dir,a0=Math.atan2(d[1],d[0]);ctx.save();ctx.globalCompositeOperation='lighter';
      if(f.combo<3){const r0=22+k*10,r1=f.r*.95+k*14;const g=ctx.createLinearGradient(cx+d[0]*r0,cy+d[1]*r0,cx+d[0]*r1,cy+d[1]*r1);g.addColorStop(0,'rgba(255,255,255,0)');g.addColorStop(.7,`rgba(230,250,255,${.9*(1-k)})`);g.addColorStop(1,`rgba(255,255,255,${1-k})`);
        ctx.strokeStyle=g;ctx.lineCap='round';ctx.lineWidth=7*(1-k)+1;ctx.beginPath();ctx.moveTo(cx+d[0]*r0,cy+d[1]*r0);ctx.lineTo(cx+d[0]*r1,cy+d[1]*r1);ctx.stroke();
        ctx.strokeStyle=`rgba(140,230,255,${.8*(1-k)})`;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(cx+d[0]*(r0+6),cy+d[1]*(r0+6));ctx.lineTo(cx+d[0]*(r1-4),cy+d[1]*(r1-4));ctx.stroke();}
      else{const R=f.r*.72,sp=1.25;ctx.strokeStyle=`rgba(255,255,255,${1-k})`;ctx.lineCap='round';for(let j=0;j<3;j++){ctx.lineWidth=(9-j*3)*(1-k)+1;ctx.beginPath();ctx.arc(cx,cy,R-j*5,a0-sp*(.4+k*.6),a0+sp*(.4+k*.6)*.6);ctx.stroke();}}
      if(f.t<6){const tx=cx+d[0]*f.r*.85,ty=cy+d[1]*f.r*.85;ctx.strokeStyle=`rgba(255,240,170,${1-f.t/6})`;ctx.lineWidth=2;for(let j=0;j<6;j++){const a=j*Math.PI/3+f.t*.3,l=6+f.t*3;ctx.beginPath();ctx.moveTo(tx+Math.cos(a)*3,ty+Math.sin(a)*3);ctx.lineTo(tx+Math.cos(a)*l,ty+Math.sin(a)*l);ctx.stroke();}}
      ctx.restore();}"""
rep(old,new)
rep("  for(const p of pops)p.t++;pops=pops.filter(p=>p.t<40);","  for(const p of pops)p.t++;pops=pops.filter(p=>p.t<40);\n  for(const f of FXL)f.t++;for(let i=FXL.length-1;i>=0;i--)if(FXL[i].t>(FXL[i].combo===3?12:9))FXL.splice(i,1);")
rep("if(c==='KeyP')die();});","if(c==='KeyP')die();if(c==='KeyM'){ATKMODE=(ATKMODE+1)%3;ui();}});")
rep("function ui(){","function ui(){const mb=document.getElementById('bMode');if(mb)mb.textContent=['현재','A','B'][ATKMODE];const hm=document.getElementById('hmode');if(hm)hm.textContent='공격 방식(M): '+ATKNAME[ATKMODE];")
rep('<div id="keys">','<div id="hmode" style="position:absolute;left:8px;top:calc(46px + env(safe-area-inset-top));color:#9fe8ff;font:bold 13px sans-serif;text-shadow:0 1px 2px #000;pointer-events:none">공격 방식(M): 현재</div>\n<div id="keys">')
rep('<div class="btn small" id="bDie"','<div class="btn small" id="bMode" style="right:calc(128px + env(safe-area-inset-right));top:calc(40px + env(safe-area-inset-top))">현재</div>\n<div class="btn small" id="bDie"')
rep("tap('bDie',die);","tap('bDie',die);tap('bMode',()=>{ATKMODE=(ATKMODE+1)%3;ui();});")
rep("판정 H · 사망 P</div>","판정 H · 사망 P · 공격방식 M</div>",2)
rep("window.__sbx={P,","window.__sbx={get ATKMODE(){return ATKMODE},set ATKMODE(v){ATKMODE=v;ui();},P,")
open(p,'w',encoding='utf-8').write(s);print('ok')
