# patch_hero_v4.py — wire hero v4 (assets/anim/hero8.json from hero_v4_atlas.py) into index128.html + test128_world.js.new (test128 build only).
# Re-run safe: always applied from the pre-v4 sources in _backup_hero8_pre_v4_20261018/ (= deployed test128 at 3f606ed).
import re
B='/workspace/town-demo/_backup_hero8_pre_v4_20261018/'; P='/workspace/town-demo/index128.html'; PW='/workspace/town-demo/test128_world.js.new'
s=open(B+'index128.html',encoding='utf-8').read(); H8=open('/workspace/town-demo/assets/anim/hero8.json').read()
s=re.sub(r'/\*H8\*/.*?/\*/H8\*/',lambda m:"/*H8*/const H8=new URLSearchParams(location.search).get('hero8')==='0'?null:"+H8+";/*/H8*/",s,count=1,flags=re.S)
def rep(old,new,cnt=1):
    global s
    n=s.count(old); assert n==cnt,(n,old[:90]); s=s.replace(old,new)
# real left frames for every motion (incl. cast); fx layers made for 'right' are mirrored on left (H8.fxMirrorLeft)
rep("function heroCell8(){const h=hero,sd=sdir(),fl=sd==='left',d=fl?'right':sd;",
    "function heroCell8(){const h=hero,sd=sdir(),L8=!!H8.left&&sd==='left',fl=sd==='left'&&!L8,d=L8?'left':fl?'right':sd;")
rep("const o={c,dx:0,dy:0,fl,sy:1,h8:e[0],bob};","const o={c,dx:0,dy:0,fl,sy:1,h8:e[0],bob,ffl:fl||(L8&&!!H8.fxMirrorLeft)};")
rep("if(o.fxb)h8fx(o.fxb,o.fl);","if(o.fxb)h8fx(o.fxb,o.ffl??o.fl);")
rep("h8fx(o.fxf,o.fl)","h8fx(o.fxf,o.ffl??o.fl)",2)
# death: H8 death_<dir> (100 ms/frame, last frame held until respawn) instead of the old 128 sheet
rep("function heroCell(){if(H8&&IMG.h8_0&&!(hero.deadT>0)){","function heroCell(){if(H8&&IMG.h8_0&&(!(hero.deadT>0)||H8.anims.death_down)){")
rep("\n if(h.hurtT>0){const L=A('hurt');e=h8seq(L,(tk(FEEL.hurtTicks)-h.hurtT)*60);}",
    "\n if(h.deadT>0){const L=A('death');e=h8seq(L,(tk(FEEL.deathTicks)-h.deadT)*60);}\n else if(h.hurtT>0){const L=A('hurt');e=h8seq(L,(tk(FEEL.hurtTicks)-h.hurtT)*60);}")
# guard / jump have no game input: visual-only preview pose (__game.heroPose('guard'|'jump')), cancelled by any action
rep(" else if(H8.v3){const L=A('idle');"," else if(h.pose&&H8.anims[h.pose.n+'_'+d]){e=h8seq(A(h.pose.n),h.pose.t);}\n else if(H8.v3){const L=A('idle');")
# gait cycle (8-frame walk ~90 ms/frame at walk speed, run ~70 ms/frame at run speed) + cast 5 ticks/frame from the atlas; ?walkcyc= / ?runcyc= still override
rep("const H8T={walkCyc:+(Q0().get('walkcyc')||84),runCyc:+(Q0().get('runcyc')||119),castTpf:3,",
    "const H8T={walkCyc:+(Q0().get('walkcyc')||(H8&&H8.gait&&H8.gait.walkCyc)||84),runCyc:+(Q0().get('runcyc')||(H8&&H8.gait&&H8.gait.runCyc)||119),castTpf:(H8&&H8.castTpf)||3,")
# dash afterimages: ghosts of the current frame at recent positions (every 2 ticks), cool cyan 'dodge' tint, newest->oldest 55/38/22/10 %, fade out ~10 ticks after the dash
rep("if(tt%2===0&&tt<(DODGE.burstTicks||14)){const c=heroCell();if(c)(d.trail=d.trail||[]).push({c,x:hero.x,y:hero.y});}",
    "if(tt%2===0&&tt<(DODGE.durTicks||17)){const c=heroCell();if(c)(hero.gh=hero.gh||[]).push({c,x:hero.x,y:hero.y,a:0});}")
rep("if(H8){const sp=Math.hypot(hero.vx,hero.vy);",
    "if(H8){if(hero.gh){for(const g of hero.gh)g.a++;hero.gh=hero.gh.filter(g=>g.a<GH8.life).slice(-GH8.alpha.length);if(!hero.gh.length)hero.gh=null;}\n  if(hero.pose){hero.pose.t++;if(hero.pose.t>=hero.pose.max||hero.moving||hero.atk||hero.dash||hero.sk||hero.hurtT>0||hero.deadT>0||hero.charge)hero.pose=null;}\n  const sp=Math.hypot(hero.vx,hero.vy);")
rep(" if(d.trail){const T=d.trail.slice(-5),burst=tt<=B;T.forEach((g,gi)=>{const age=T.length-gi;blitHero(g.c,g.x,g.y,burst?(210/255)*Math.pow(.72,age):(120/255)*Math.pow(.6,age),'dodge');});}",
    " // afterimages: drawGhosts8() (hero v4)")
rep("function drawDash8(){",
    "const GH8={alpha:[.55,.38,.22,.10],fadeFrom:8,life:18};\nfunction drawGhosts8(){const G=hero.gh;if(!G||!G.length||!H8||!IMG.h8_0)return;for(let i=0;i<G.length;i++){const g=G[i],r=G.length-1-i,a=GH8.alpha[r]*Math.max(0,Math.min(1,(GH8.life-g.a)/(GH8.life-GH8.fadeFrom)));if(a>0)blitHero(g.c,g.x,g.y,a,'dodge');}}\nfunction drawDash8(){")
rep("function drawHero(){const h=hero;","function drawHero(){const h=hero;drawGhosts8();")
rep("window.__game={","window.__game={get heroGhosts(){return hero.gh},heroPose:(n)=>{const L=H8&&H8.anims[n+'_down'];if(!L)return false;hero.pose={n,t:0,max:h8tot(L)+30};return true;},")
open(P,'w',encoding='utf-8').write(s); print('patched',P,len(s))
w=open(B+'test128_world.js.new',encoding='utf-8').read()
def repw(old,new):
    global w
    assert w.count(old)==1,old[:80]; w=w.replace(old,new)
repw("fl = sd === 'left', d = fl ? 'right' : sd; // 4-way sprite, diagonals = side, left = mirror",
     "L8 = H.left && sd === 'left', fl = sd === 'left' && !L8, d = L8 ? 'left' : fl ? 'right' : sd; // 4-way sprite, diagonals = side; hero v4 has real left frames (else left = mirror)")
repw("h.gp = ((h.gp || 0) + m / (h.run ? 46 : 32)) % 1;",
     "h.gp = ((h.gp || 0) + m / (h.run ? (H.gait && H.gait.runCyc ? H.gait.runCyc * 46 / 119 : 46) : (H.gait && H.gait.walkCyc ? H.gait.walkCyc * 32 / 84 : 32))) % 1;")
repw("    else e = A('idle')[0];\n    if (!e) return null; const c = H.cells",
     "    else if (H.v4) { const L = A('idle'); e = seq(L, (S.t * 60) % tot(L)); }\n    else e = A('idle')[0];\n    if (!e) return null; const c = H.cells")
# field death: H8 death_<dir> (S.deadT counts up 0 -> 2.2 s)
repw("if (!H || !G.H8img(0) || S.deadT > 0) return null;","if (!H || !G.H8img(0) || (S.deadT > 0 && !H.anims.death_down)) return null;")
repw("    if (h.atk) { const i = h.atk.i, AT = atkT(i), L = A(","    if (S.deadT > 0) e = seq(A('death'), S.deadT * 60);\n    else if (h.atk) { const i = h.atk.i, AT = atkT(i), L = A(")
open(PW,'w',encoding='utf-8').write(w); print('patched',PW)
