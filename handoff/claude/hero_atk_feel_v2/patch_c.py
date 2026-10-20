import sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]);s=s.replace(a,b)
rep("let ATKMODE=0;const ATKNAME=['현재','A 대각선+연출','B 옆모습 공격+연출'];",
"""let ATKMODE=0;const ATKNAME=['현재','A 대각선+연출','B 옆모습 공격+연출','C 리네트 방식'];
// C = 2번방 리네트 방식 (test128/linette.html, PR #21): trail straight up/down the screen for up/down attacks (art stays diagonal), lunge
// along the input 8/10/18 px in the 4 ticks before the strike, hit-stop 4/5/9 + screen shake 1.5/2/4 (x0.82 decay) on every strike,
// 3rd hit: shockwave ring (16 ticks) + white flash (4 ticks). Trail = layered lance (port of linette trailOne).
const CHIT=[{push:8,stop:4,shake:1.5},{push:10,stop:5,shake:2},{push:18,stop:9,shake:4}];let SHAKE=0,FLASH=0;const WAVES=[],CTR=[];
const cDir=k=>k==='down'||k==='downl'?[0,1]:k==='up'||k==='upl'?[0,-1]:DV[k];""")
rep("const isDiag=k=>k!=='right'&&k!=='left';","const isDiag=k=>k!=='right'&&k!=='left';const NM=4;")
rep("ATKMODE=(ATKMODE+1)%3;ui();}});","ATKMODE=(ATKMODE+1)%NM;ui();}});")
rep("tap('bMode',()=>{ATKMODE=(ATKMODE+1)%3;ui();});","tap('bMode',()=>{ATKMODE=(ATKMODE+1)%NM;ui();});")
rep("mb.textContent=['현재','A','B'][ATKMODE];","mb.textContent=['현재','A','B','C'][ATKMODE];")
# update: C lunge / strike
rep("    if(P.st==='atk'){const C=COMBO[P.combo-1],dir=DV[P.ad||P.clip.split('_')[1]],fxOn=ATKMODE>0&&isDiag(P.ad||'');",
"""    if(P.st==='atk'&&ATKMODE===3){const C=COMBO[P.combo-1],H=CHIT[P.combo-1],k=P.ad||P.clip.split('_')[1],iv=DV[k],dir=cDir(k);
      if(P.t<C.hit-4)moveHero(iv[0]*.9,iv[1]*.9);
      if(P.t>=C.hit-4&&P.t<C.hit)moveHero(iv[0]*H.push/4,iv[1]*H.push/4);   // lunge along the input
      if(!P.hitDone&&P.t>=C.hit){P.hitDone=true;stop=H.stop;SHAKE=Math.max(SHAKE,H.shake);if(P.combo===3)FLASH=4;
        const v=dir[1]&&!dir[0]?dir[1]:0,ox=P.x+(v?0:dir[0]*20),oy=P.y+(v>0?-34:v<0?-96:-44);CTR.push({x:ox,y:oy,dir,t:0,heavy:P.combo===3,big:P.combo>1});
        if(P.combo===3)WAVES.push({x:ox+dir[0]*70,y:oy+dir[1]*70,t:0});
        const cx=ox,cy=oy;if(!M.dead&&P.z<30&&inSector(cx,cy,dir,C.r,C.arc,M.x,M.y-22,20)){M.hp-=C.dmg;M.flash=8;M.kbx=dir[0]*C.kb;M.kby=dir[1]*C.kb;pops.push({x:M.x,y:M.y-60,t:0,s:String(C.dmg)});if(M.hp<=0){M.dead=90;}window.__sbx.hits++;}}
      if(P.queued&&P.combo<3&&P.t>=C.cancel){P.queued=false;P.combo++;P.ad=dirKey();start('atk',atkClip(P.combo,P.ad));return;}}
    else if(P.st==='atk'){const C=COMBO[P.combo-1],dir=DV[P.ad||P.clip.split('_')[1]],fxOn=ATKMODE>0&&isDiag(P.ad||'');""")
rep("  for(const f of FXL)f.t++;","  for(const f of CTR)f.t++;for(let i=CTR.length-1;i>=0;i--)if(CTR[i].t>=(CTR[i].heavy?20:CTR[i].big?16:12))CTR.splice(i,1);for(const w of WAVES)w.t++;for(let i=WAVES.length-1;i>=0;i--)if(WAVES[i].t>=16)WAVES.splice(i,1);\n  for(const f of FXL)f.t++;")
# camera shake
rep("  const camX=Math.round(P.x-VW/2),camY=Math.round(P.y-VH*0.55);",
    "  const shx=SHAKE?Math.round((Math.random()*2-1)*SHAKE):0,shy=SHAKE?Math.round((Math.random()*2-1)*SHAKE):0;if(!window.__sbx||!window.__sbx.manual||true)SHAKE=SHAKE>0.3?SHAKE*0.82:0;\n  const camX=Math.round(P.x-VW/2)+shx,camY=Math.round(P.y-VH*0.55)+shy;")
# draw C trails/waves/flash after pops
rep("  ctx.font='bold 12px system-ui';ctx.textAlign='center';for(const p of pops)",
"""  for(const w of WAVES){const a=1-w.t/16,r=10+w.t*7;ctx.strokeStyle=`rgba(200,240,255,${.8*a})`;ctx.lineWidth=3*a+1;ctx.beginPath();ctx.ellipse(Math.round(w.x-camX),Math.round(w.y-camY),r,r*.45,0,0,7);ctx.stroke();}
  for(const f of CTR)trailC(f.x-camX,f.y-camY,f);
  if(FLASH>0){ctx.fillStyle=`rgba(255,255,255,${FLASH*0.05})`;ctx.fillRect(0,0,VW,VH);FLASH--;}
  ctx.font='bold 12px system-ui';ctx.textAlign='center';for(const p of pops)""")
rep("function hb(cx,cy,dir,r,arc,col){",
"""function lanceC(cx,cy,dx,dy,nx,ny,back,ahead,w,col){ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(cx-dx*back,cy-dy*back);ctx.lineTo(cx+nx*w/2,cy+ny*w/2);ctx.lineTo(cx+dx*ahead,cy+dy*ahead);ctx.lineTo(cx-nx*w/2,cy-ny*w/2);ctx.closePath();ctx.fill();}
function trailC(tx,ty,f){const age=f.t,heavy=f.heavy,big=f.big,life=heavy?20:big?16:12;if(age>=life)return;const g=Math.min(1,(age+1)/2),a=1-age/life,[dx,dy]=f.dir,nx=-dy,ny=dx;
  const ahead=(heavy?92:big?70:52)*g,back=heavy?40:big?34:26,W=heavy?16:big?12:9,cx=tx+dx*ahead*.35,cy=ty+dy*ahead*.35;
  if(heavy)lanceC(cx,cy,dx,dy,nx,ny,back+ahead*.45,ahead*.75,W*1.6,`rgba(60,150,255,${.31*a})`);
  lanceC(cx,cy,dx,dy,nx,ny,back+ahead*.35,ahead*.65,W,`rgba(90,210,255,${.47*a})`);lanceC(cx,cy,dx,dy,nx,ny,back*.8+ahead*.3,ahead*.6,W*.45,`rgba(210,250,255,${.86*a})`);
  lanceC(cx,cy,dx,dy,nx,ny,back*.6+ahead*.25,ahead*.55,Math.max(1.5,W*.18),`rgba(255,255,255,${a})`);
  ctx.strokeStyle=`rgba(200,245,255,${.67*a})`;ctx.lineWidth=1;for(const[o,l]of(big?[[.9,.6],[-.9,.5],[1.6,.35],[-1.6,.3]]:[[.9,.55],[-.9,.45]])){const sx=cx+nx*o*W-dx*back*.6,sy=cy+ny*o*W-dy*back*.6,L=(back+ahead)*l;ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(sx+dx*L,sy+dy*L);ctx.stroke();}
  if(age<4){const ex=tx+dx*ahead*.95,ey=ty+dy*ahead*.95,r=big?5:4;ctx.fillStyle=`rgba(255,255,255,${a})`;ctx.fillRect(ex-r,ey,2*r,1);ctx.fillRect(ex,ey-r,1,2*r);}}
function hb(cx,cy,dir,r,arc,col){""")
open(p,'w',encoding='utf-8').write(s);print('ok')
