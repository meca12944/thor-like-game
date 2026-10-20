import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]);s=s.replace(a,b)
rep("function atkClip(n,dk){return 'hit'+n+'_'+(ATKMODE===2&&isDiag(dk)?(dk.endsWith('l')?'left':'right'):dk);}",
"""// V = small hit-3 crescent (hit3s_* clips, crescent x0.7 about the chest), G = afterimages behind hits 1-2 (owner 2026-10-20 tests)
let SMALLC=false,GHOST=false,TICK=0;const GH=[];
function atkClip(n,dk){return 'hit'+(n===3&&SMALLC?'3s':n)+'_'+(ATKMODE===2&&isDiag(dk)?(dk.endsWith('l')?'left':'right'):dk);}""")
rep("function step(){","function step(){TICK++;for(let i=GH.length-1;i>=0;i--)if(TICK-GH[i].b>14)GH.splice(i,1);")
# push + draw ghosts in drawHero, before the afterimage/sprite
rep("    const AC=P.st==='atk'?COMBO[P.combo-1]:null,",
"""    if(GHOST&&P.st==='atk'&&P.combo<3&&P.t>0&&P.t<=COMBO[P.combo-1].hit+3&&P.t%2===0&&(!GH.length||GH[GH.length-1].k!==P.combo*100+P.t))GH.push({s,c,x:P.x,y:P.y-P.z,b:TICK,k:P.combo*100+P.t});
    for(const g of GH){const [gx,gy,gw,gh2,gax,gay]=A.cells[g.s][g.c],age=TICK-g.b;ctx.save();ctx.globalAlpha=.5*(1-age/14);ctx.filter='brightness(.75) sepia(1) hue-rotate(165deg) saturate(3)';
      ctx.drawImage(SH[g.s],gx,gy,gw,gh2,Math.round(g.x-camX)-gax,Math.round(g.y-camY)-gay,gw,gh2);ctx.restore();}   // afterimages (blue, fade in 14 ticks)
    const AC=P.st==='atk'?COMBO[P.combo-1]:null,""")
rep("if(c==='KeyM'){ATKMODE=(ATKMODE+1)%NM;ui();}","if(c==='KeyM'){ATKMODE=(ATKMODE+1)%NM;ui();}if(c==='KeyV'){SMALLC=!SMALLC;ui();}if(c==='KeyG'){GHOST=!GHOST;ui();}")
rep("function ui(){","function ui(){const vb=document.getElementById('bSmall'),gb=document.getElementById('bGhost');if(vb)vb.classList.toggle('on',SMALLC);if(gb)gb.classList.toggle('on',GHOST);const hv=document.getElementById('hvg');if(hv)hv.textContent='3타 반달 작게(V): '+(SMALLC?'켬':'끔')+' · 기본타 잔상(G): '+(GHOST?'켬':'끔');")
rep('<div id="keys">','<div id="hvg" style="position:absolute;left:8px;top:calc(64px + env(safe-area-inset-top));color:#ffd38a;font:bold 13px sans-serif;text-shadow:0 1px 2px #000;pointer-events:none">3타 반달 작게(V): 끔 · 기본타 잔상(G): 끔</div>\n<div id="keys">')
rep('<div class="btn small" id="bDie"','<div class="btn small" id="bSmall" style="right:calc(184px + env(safe-area-inset-right));top:calc(40px + env(safe-area-inset-top))">반달</div>\n<div class="btn small" id="bGhost" style="right:calc(240px + env(safe-area-inset-right));top:calc(40px + env(safe-area-inset-top))">잔상</div>\n<div class="btn small" id="bDie"')
rep("tap('bDie',die);","tap('bDie',die);tap('bSmall',()=>{SMALLC=!SMALLC;ui();});tap('bGhost',()=>{GHOST=!GHOST;ui();});")
rep("판정 H · 사망 P · 공격방식 M</div>","판정 H · 사망 P · 공격방식 M · 반달 V · 잔상 G</div>",2)
rep("window.__sbx={","window.__sbx={get SMALLC(){return SMALLC},set SMALLC(v){SMALLC=v;ui();},get GHOST(){return GHOST},set GHOST(v){GHOST=v;ui();},")
open(p,'w',encoding='utf-8').write(s);print('ok')
