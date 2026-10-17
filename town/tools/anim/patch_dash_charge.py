"""Dash attack (run + attack) + charge attack (hold attack, 2 levels) for town (game.template.html / index.html) and world.js.
Idempotent text/json patch: safe on origin blobs and on working copies holding other workers' WIP.
usage: python3 patch_dash_charge.py <kind> <in> <out>   kind = src|herojson|build|template|index|world|controls|animation"""
import json,sys
def rep(t,a,b,n=1):
    if b in t: return t
    c=t.count(a); assert c==n,('count',c,a[:100]); return t.replace(a,b)
SPECIAL={
 "dash":{"name":"돌진베기","anim":"@hit1","kind":"slash","dur":26,"a0":4,"a1":12,"cancel":12,"stop":5,"kb":420,"lunge":90,"rangeMul":1.0,"arc":100,"dmgMul":1.3,"cool":0.3,"strike":[0.25,0.6]},
 "charge":{"t1":0.6,"t2":1.2,"moveMul":0.4,"hold":{"anim":"@hit3","p":0.18},
  "lv1":{"name":"모아베기","anim":"@hit3","kind":"overhead","dur":34,"a0":6,"a1":14,"cancel":20,"stop":8,"kb":650,"lunge":24,"rangeMul":1.15,"arc":100,"dmgMul":2,"cool":0.25,"shake":0,"strike":[0.3,0.6],"trail":["150,220,255","255,255,255"]},
  "lv2":{"name":"극 모아베기","anim":"@hit3","kind":"overhead","dur":40,"a0":6,"a1":16,"cancel":24,"stop":10,"kb":850,"lunge":30,"rangeMul":1.4,"arc":100,"dmgMul":3,"cool":0.3,"shake":"fin","fin":True,"strike":[0.3,0.6],"trail":["255,214,110","255,255,255"],
         "wave":{"speed":560,"range":260,"rad":28,"dmgMul":1.0,"kb":380,"pierce":True,"col":["255,214,110","120,80,10","255,255,255"]}}}}
SPECIAL_DOC=("Attacks besides the 3-hit combo, for every weapon type (per-weapon override: weapons[type].special with the same keys). "
 "dash = 돌진베기: attack while RUNNING (double-tap run) -> forward lunge slash; lunge = travel in town world px (90 = ~1.7 tiles), range = weapon hit-1 range x rangeMul, arc deg, dmgMul x hit-1 damage, cool = s before the next attack (no spam), cancel = dodge-cancel tick. "
 "charge = 모으기: hold attack (tap still = combo; the hold time counts from the press) -> lv1 at t1 s, lv2 at t2 s (glow + sound cue each); release -> lv1 / lv2 slash; moveMul = walk speed while charging; a hit cancels the charge unless super armor; lv2 also fires a forward sword wave (wave.dmgMul x hit-1). "
 "anim '@hit1' / '@hit3' = the weapon's own combo anim (swap in dedicated frames by naming an anim here); hold = pose held while charging (anim + fraction p of it). Ticks are 60 fps and scale with the weapon's hit-1 length (dur/17, clamped .7-1.4). World (16 px tiles) uses the same data x .3. Forward-only (no 360).")
def anim_obj(d,src=True):
    if 'special' not in d:
        d['special']=json.loads(json.dumps(SPECIAL))
        if src: d['_special_doc']=SPECIAL_DOC
    return d
def build(t):
    return rep(t,"titleCombo=C.get('titleCombo', {}))","titleCombo=C.get('titleCombo', {}), special=C.get('special', {}))")
def template(t):
    t=rep(t,"function buildSwings(type){",
"""// dash attack (run + attack) / charge attack (hold attack) — data: hero_anim.src.json 'special' (+ per-weapon weapons[type].special). SWINGS[4]=dash, [5]=charge lv1, [6]=charge lv2
const SP_I={dash:4,c1:5,c2:6};
function spCfg(type){const S=(ANIM&&ANIM.special)||{},W=(ANIM&&ANIM.weapons&&ANIM.weapons[type]&&ANIM.weapons[type].special)||{},SC=S.charge||{},WC=W.charge||{};
 return {dash:Object.assign({},S.dash,W.dash),charge:Object.assign({},SC,WC,{lv1:Object.assign({},SC.lv1,WC.lv1),lv2:Object.assign({},SC.lv2,WC.lv2),hold:Object.assign({},SC.hold,WC.hold)})};}
function spAnim(n,L){return n==='@hit1'?L[0].anim:n==='@hit2'?L[1].anim:n==='@hit3'?(L[2].titleSpin?'atk3':L[2].anim):n;}
function buildSpecials(type,L){const C=spCfg(type),k=Math.min(1.4,Math.max(.7,(L[0].dur||tk(17))/tk(17)));
 return [C.dash,C.charge.lv1,C.charge.lv2].map((h,j)=>h&&h.dur?Object.assign({},h,{special:['dash','c1','c2'][j],anim:spAnim(h.anim||'@hit1',L),dur:tk(h.dur*k),a0:tk(h.a0*k),a1:tk(h.a1*k),cancel:tk(h.cancel*k),range:Math.round(swingRange(L[0])*(h.rangeMul||1)),hits:L[0].hits||1}):null);}
function buildSwings(type){""")
    t=rep(t,"SWINGS.length=0;SWINGS.push(...L,LEAP);}","SWINGS.length=0;SWINGS.push(...L,LEAP,...buildSpecials(type,L));}")
    t=rep(t,"function startSwing(i){const s=SWINGS[i];const runSlash=hero.run&&","function startSwing(i){const s=SWINGS[i];hero.charge=null;const runSlash=!s.special&&hero.run&&")
    t=rep(t," if(runSlash){hero.runStartT=0;"," if(s.special==='dash'){hero.runStartT=0;burst(hero.x,hero.y-2,10,['#e8dcc0','#cbb894','#fff'],170,0,3);spawnRing(hero.x,hero.y,6,46,.22,'255,255,255',4,.5);} // 돌진베기: kick-off dust\n if(runSlash){hero.runStartT=0;")
    t=rep(t,"if(atkPressed){atkPressed=false;hero.atkBuf=FEEL.bufferTicks;} // 8-tick input queue",
            "if(atkPressed){atkPressed=false;hero.atkBuf=FEEL.bufferTicks;hero.holdT=0;hero.holdOk=true;} // 8-tick input queue; holdT = how long this press is held (charge)\n if(keys.attack&&hero.holdOk)hero.holdT+=dt;else hero.holdOk=false;")
    t=rep(t,"  else if(hero.cool<=0){faceTarget();startSwing(hero.chainT>0&&hero.combo<2?hero.combo+1:0);hero.atkBuf=0;}",
            "  else if(hero.cool<=0){if(hero.run&&hero.moving&&SWINGS[SP_I.dash]&&Math.hypot(hero.vx,hero.vy)>FEEL.walkSpeed*1.2)startSwing(SP_I.dash); // running + attack = 돌진베기\n   else{faceTarget();startSwing(hero.chainT>0&&hero.combo<2?hero.combo+1:0);}hero.atkBuf=0;}")
    t=rep(t," const a=hero.atk,sk=hero.sk;\n if(a){a.t+=dt;",
""" // charge (모으기): keep holding attack after the swing -> lv1 / lv2; release fires the charged slash; dodge / skill / a flinching hit cancels it (super armor keeps it)
 if(!hero.charge&&hero.holdOk&&hero.holdT>tk(8)&&SWINGS[SP_I.c1]&&!hero.atk&&!hero.dash&&!hero.sk&&!hero.swim&&!uw&&!(hero.hurtT>0)&&!(hero.deadT>0)){const CF=spCfg(weaponType).charge;hero.charge={t:hero.holdT,lv:0,flash:0,mv:CF.moveMul||.4,anim:spAnim((CF.hold&&CF.hold.anim)||'@hit3',SWINGS),p:(CF.hold&&CF.hold.p)||.18};hero.run=false;}
 if(hero.charge){const C=hero.charge,CF=spCfg(weaponType).charge;C.t+=dt;if(C.flash>0)C.flash-=dt;const lv=C.t>=(CF.t2||1.2)?2:C.t>=(CF.t1||.6)?1:0;
  if(lv>C.lv){C.lv=lv;C.flash=.25;SFX.play(lv>1?'ult_cutin':'hit_crit',lv>1?.4:.5,lv>1?1.9:1.7);spawnRing(hero.x,hero.y-40,6,lv>1?70:50,.3,lv>1?'255,214,110':'150,220,255',5,.6);burst(hero.x,hero.y-46,lv>1?14:8,lv>1?['#ffe08a','#fff']:['#aee8ff','#fff'],150,0,3,.4);}
  if(Math.random()<(lv>1?.7:lv?.45:.2)){const an=Math.random()*Math.PI*2,d=34+Math.random()*14;parts.push({x:hero.x+Math.cos(an)*d,y:hero.y-44+Math.sin(an)*d*.8,vx:-Math.cos(an)*d*3.2,vy:-Math.sin(an)*d*2.6,g:0,t:0,life:.28,c:lv>1?'#ffe08a':lv?'#aee8ff':'#ffffff',s:3});}
  if(!hero.holdOk||hero.atk||hero.dash||hero.sk||hero.hurtT>0||hero.deadT>0){hero.charge=null;if(!hero.holdOk&&C.lv>0&&!hero.atk&&!hero.dash&&!hero.sk&&!(hero.hurtT>0)&&!(hero.deadT>0))startSwing(C.lv>1?SP_I.c2:SP_I.c1);}}
 const a=hero.atk,sk=hero.sk;
 if(a){a.t+=dt;""")
    t=rep(t,"  if(s.titleSpin&&s.waves&&!a.waved&&a.t>=s.a0+tk(4)){a.waved=1;spawnWaves(s.waves);}",
            "  if(s.titleSpin&&s.waves&&!a.waved&&a.t>=s.a0+tk(4)){a.waved=1;spawnWaves(s.waves);}\n  if(s.wave&&!a.waved&&a.t>=s.a0){a.waved=1;spawnWaves(Object.assign({n:1,col:['255,214,110','120,80,10','255,255,255']},s.wave,{dir:Math.atan2(dv[1],dv[0]),dmg:ATK_DMG[0]*(s.wave.dmgMul||1)/DMG_UNIT}));} // charge lv2: forward sword wave")
    t=rep(t,"damageSlime(m,kx,ky,ATK_DMG[Math.min(2,a.i)]*(s.hits||1),s.kb,{stop:tk(s.stop||3),shake:s.fin?'fin':0,",
            "damageSlime(m,kx,ky,(s.dmgMul?ATK_DMG[0]*s.dmgMul:ATK_DMG[Math.min(2,a.i)])*(s.hits||1),s.kb,{stop:tk(s.stop||3),shake:s.shake!==undefined?s.shake:(s.fin?'fin':0),")
    t=rep(t,"if(a.i>=2){hero.cool=.18;hero.combo=0;}","if(a.i>=2){hero.cool=s.cool||.18;hero.combo=0;}")
    t=rep(t,"const a=k/W.n*Math.PI*2+Math.PI/W.n;w.on=true;","const a=W.dir!==undefined?W.dir+(k-(W.n-1)/2)*(W.spread||0):k/W.n*Math.PI*2+Math.PI/W.n;w.on=true;")
    t=rep(t,"  if(l>0&&!busy&&(hero.runReq||alwaysRun)&&!hero.run){","  if(l>0&&!busy&&!hero.charge&&(hero.runReq||alwaysRun)&&!hero.run){")
    t=rep(t,"  const runK=hero.run?FEEL.runMul","  const runK=hero.charge?hero.charge.mv:hero.run?FEEL.runMul")
    t=rep(t,"   if(Math.abs(ix)>Math.abs(iy)*0.9){hero.face=ix>0?'right':'left';hero.hz=hero.face;}else hero.face=iy>0?'down':'up';}",
            "   if(hero.charge){}else if(Math.abs(ix)>Math.abs(iy)*0.9){hero.face=ix>0?'right':'left';hero.hz=hero.face;}else hero.face=iy>0?'down':'up';} // charging: facing locked")
    t=rep(t,"if(h.atk)return h.atk.s.anim||'atk1';if(h.dash)","if(h.atk)return h.atk.s.anim||'atk1';if(h.charge)return h.charge.anim;if(h.dash)")
    t=rep(t,"if(h.atk)tick=atkAnimP(h.atk)*A.ticks;","if(h.atk)tick=atkAnimP(h.atk)*A.ticks;else if(h.charge)tick=h.charge.p*A.ticks;")
    t=rep(t,"function drawSlash(){",
"""function drawCharge(front){const C=hero.charge;if(!C)return;const lv=C.lv,col=lv>1?'255,214,110':lv?'140,215,255':'255,255,255',pul=.5+.5*Math.sin(C.t*(lv>1?22:14)),r=(lv>1?46:lv?38:26)+pul*6,cx=hero.x,cy=hero.y-42; // charge glow: white -> lv1 blue -> lv2 gold (aura behind the hero; ring, converging sparks, level-up flash in front)
 ctx.save();ctx.globalCompositeOperation='lighter';
 if(!front){const g=ctx.createRadialGradient(cx,cy,2,cx,cy,r);g.addColorStop(0,`rgba(${col},${Math.min(1,.5+.3*pul+(C.flash||0)*2)})`);g.addColorStop(.6,`rgba(${col},${.22+.15*pul})`);g.addColorStop(1,`rgba(${col},0)`);ctx.fillStyle=g;ctx.beginPath();ctx.ellipse(cx,cy,r*.8,r*1.1,0,0,Math.PI*2);ctx.fill();}
 else{if(lv){ctx.strokeStyle=`rgba(${col},${.6+.4*pul})`;ctx.lineWidth=lv>1?4:3;ctx.beginPath();ctx.ellipse(hero.x,hero.y-4,(lv>1?36:28)+pul*3,(lv>1?13:10)+pul,0,0,Math.PI*2);ctx.stroke();}
  const n=(lv+1)*3;ctx.fillStyle=`rgba(${col},.95)`;for(let i=0;i<n;i++){const an=C.t*5+i*Math.PI*2/n,d=r*(1-((C.t*2.2+i*.37)%1));ctx.fillRect(cx+Math.cos(an)*d*.8-2,cy+Math.sin(an)*d-2,4,4);}
  if(C.flash>0){ctx.fillStyle=`rgba(255,255,255,${Math.min(.8,C.flash*3)})`;ctx.beginPath();ctx.ellipse(cx,cy,r*.5,r*.7,0,0,Math.PI*2);ctx.fill();}}
 ctx.restore();}
function drawSlash(){""")
    t=rep(t,"drawHero();drawBarrier();drawSlash();","drawCharge(0);drawHero();drawCharge(1);drawBarrier();drawSlash();")
    t=rep(t,"window.__game={startSwingForTest:i=>startSwing(i),","window.__game={startSwingForTest:i=>startSwing(i),SP_I,spCfg,")
    return t
def index(t):
    t=template(t);k=t.index('const ANIM=')+len('const ANIM=');e=t.index('\n',k);d=json.loads(t[k:e][:-1])
    return t[:k]+json.dumps(anim_obj(d,False),separators=(',',':'),ensure_ascii=False)+';'+t[e:]
def world(t):
    t=rep(t,"  const atkT = i => i === 2 ? ATK3 : ATK;",
"""  const atkT = i => i >= 3 ? atkTS(i) : i === 2 ? ATK3 : ATK;
  // dash attack (run + attack, i 3) / charge attack lv1 / lv2 (hold attack, i 4 / 5): same data as the town (__game.ANIM.special), town px x .3, ticks / 60
  const SPW_DEF = { dash: { dur: 26, a0: 4, a1: 12, lunge: 90, rangeMul: 1, arc: 100, dmgMul: 1.3, cool: .3 }, charge: { t1: .6, t2: 1.2, moveMul: .4,
    lv1: { dur: 34, a0: 6, a1: 14, lunge: 24, rangeMul: 1.15, arc: 100, dmgMul: 2, cool: .25 }, lv2: { dur: 40, a0: 6, a1: 16, lunge: 30, rangeMul: 1.4, arc: 100, dmgMul: 3, cool: .3, wave: { speed: 560, range: 260, rad: 28, dmgMul: 1 } } } };
  function spW() { const g = window.__game; return (g && g.ANIM && g.ANIM.special && g.ANIM.special.dash) ? g.ANIM.special : SPW_DEF; }
  function spOf(i) { const C = spW(); return i === 3 ? C.dash : i === 4 ? C.charge.lv1 : C.charge.lv2; }
  function atkTS(i) { const h = spOf(i); return { dur: h.dur / 60, a0: h.a0 / 60, a1: h.a1 / 60 }; }
  function arcW(i) { return i >= 3 ? (spOf(i).arc || 100) : i === 2 ? SWING.arc3 : SWING.arc; }
  function sfx(k, v, r) { try { const g = window.__game; if (g && g.SFX) g.SFX.play(k, v, r); } catch (e) { } }""")
    t=rep(t,"hero.dodgeT = Math.max(0, hero.dodgeT - dt);","hero.dodgeT = Math.max(0, hero.dodgeT - dt); hero.atkCd = Math.max(0, (hero.atkCd || 0) - dt);")
    t=rep(t,"if (takePress('attack') && !hero.roll && (!hero.atk || hero.atk.t > atkT(hero.atk.i).a1)) {",
            "if (takePress('attack') && !hero.roll && !(hero.atkCd > 0) && (!hero.atk || hero.atk.t > atkT(hero.atk.i).a1)) { hero.holdT = 0; hero.holdOk = true; hero.charge = null; // running + attack = 돌진베기\n      if (hero.run && hero.moving && !hero.atk) { hero.atk = { t: 0, hit: new Set(), i: 3 }; addFx('dust', hero.x, hero.y, { life: .35 }); sfx('swing_heavy', .8); } else {")
    t=rep(t,"if (hero.atk.runSlash) addFx('dust', hero.x, hero.y, { life: .3 }); if (ix || iy) setFace(ix, iy); }",
            "if (hero.atk.runSlash) addFx('dust', hero.x, hero.y, { life: .3 }); if (ix || iy) setFace(ix, iy); } }\n"
            "    if (isHeld('attack') && hero.holdOk) hero.holdT += dt; else hero.holdOk = false; // charge (모으기): keep holding attack -> lv1 t1 / lv2 t2, release = charged slash; a hit / dodge cancels\n"
            "    if (!hero.charge && hero.holdOk && hero.holdT > .14 && !hero.atk && !hero.roll && hero.hp > 0) { hero.charge = { t: hero.holdT, lv: 0, flash: 0 }; hero.run = false; }\n"
            "    if (hero.charge) { const C = hero.charge, CF = spW().charge; C.t += dt; C.flash = Math.max(0, C.flash - dt); const lv = C.t >= CF.t2 ? 2 : C.t >= CF.t1 ? 1 : 0;\n"
            "      if (lv > C.lv) { C.lv = lv; C.flash = .25; sfx(lv > 1 ? 'ult_cutin' : 'hit_crit', lv > 1 ? .4 : .5, lv > 1 ? 1.9 : 1.7); addFx('spark', hero.x, hero.y - 12, { life: .3 }); }\n"
            "      if (!hero.holdOk || hero.roll || hero.atk || hero.hp <= 0) { const rel = !hero.holdOk && !hero.roll && !hero.atk && hero.hp > 0 && C.lv > 0; hero.charge = null; if (rel) { hero.atk = { t: 0, hit: new Set(), i: 3 + C.lv }; sfx('swing_heavy', 1); } } }")
    t=rep(t,"const AT = atkT(a.i), lv = a.runSlash && a.t < AT.a1 ?","const AT = atkT(a.i), lv = a.i >= 3 ? (a.t < AT.a1 ? (spOf(a.i).lunge || 0) * .3 / AT.a1 * 2 * (1 - a.t / AT.a1) : 0) : a.runSlash && a.t < AT.a1 ?")
    t=rep(t,"(a.i === 2 ? SWING.arc3 : SWING.arc)","arcW(a.i)",2)
    t=rep(t,"a.hit.add(mm); hitMob(mm, ATK_DMG[Math.min(2, a.i)], Math.atan2(mm.y - hero.y, mm.x - hero.x)); }",
            "a.hit.add(mm); hitMob(mm, a.i >= 3 ? ATK_DMG[0] * (spOf(a.i).dmgMul || 1) : ATK_DMG[Math.min(2, a.i)], Math.atan2(mm.y - hero.y, mm.x - hero.x)); if (a.i >= 3) sfx(a.i === 5 ? 'hit_crit' : 'hit_heavy', .8); }")
    t=rep(t,"      if (a.t >= AT.dur) { hero.atk = null; hero.comboT = ATK.chain; } }",
            "      if (a.i === 5 && !a.waved && a.t >= AT.a0) { a.waved = true; spawnHW(Math.atan2(dv[1], dv[0])); shake(1); } // charge lv2: forward sword wave (1px shake only)\n"
            "      if (a.t >= AT.dur) { hero.atk = null; hero.comboT = a.i >= 3 ? 0 : ATK.chain; if (a.i >= 3) hero.atkCd = spOf(a.i).cool || .2; } }")
    t=rep(t,"if (mv && !hero.run && (hero.runReq","if (mv && !hero.run && !hero.charge && (hero.runReq")
    t=rep(t,"const sp = HERO_SPEED * rk * (hero.slowT > 0 ? .45 : 1)","const sp = HERO_SPEED * rk * (hero.charge ? (spW().charge.moveMul || .4) : 1) * (hero.slowT > 0 ? .45 : 1)")
    t=rep(t,"if (hero.moving) { setFace(ix, iy); moveCol(hero, ix * sp * dt","if (hero.moving) { if (!hero.charge) setFace(ix, iy); moveCol(hero, ix * sp * dt")
    t=rep(t,"    if (!hero.atk) hero.comboT = Math.max(0, hero.comboT - dt);","    stepHW(dt);\n    if (!hero.atk) hero.comboT = Math.max(0, hero.comboT - dt);")
    t=rep(t,"hero.hp = Math.max(0, hero.hp - dmg); hero.inv = 1.0;","hero.hp = Math.max(0, hero.hp - dmg); hero.inv = 1.0; hero.charge = null; hero.holdOk = false;")
    t=rep(t,"  function drawHeroSprite(g, zoom) {\n",
"""  function spawnHW(dir) { const w = spOf(5).wave || {}; S.hw = S.hw || []; const v = (w.speed || 560) * .3; S.hw.push({ x: hero.x, y: hero.y - 6, vx: Math.cos(dir) * v, vy: Math.sin(dir) * v * .8, d: 0, R: (w.range || 260) * .3, rad: (w.rad || 28) * .3, dmg: ATK_DMG[0] * (w.dmgMul || 1), hit: new Set(), map: S.map }); sfx('wave', .7); }
  function stepHW(dt) { if (!S.hw) return; for (let i = S.hw.length - 1; i >= 0; i--) { const w = S.hw[i]; w.x += w.vx * dt; w.y += w.vy * dt; w.d += Math.hypot(w.vx, w.vy) * dt;
      if (w.map !== S.map || w.d > w.R || solidAt(w.x, w.y + 6)) { S.hw.splice(i, 1); continue; }
      for (const mm of S.mobs) { if (mm.dead || w.hit.has(mm)) continue; const mh = (mm.D.h || 20) * (mm.scale || 1); if (Math.hypot(mm.x - w.x, (mm.y - mh * .3) - w.y) < w.rad + mm.r) { w.hit.add(mm); hitMob(mm, w.dmg, Math.atan2(w.vy, w.vx)); } } } }
  function drawHW(g) { if (!S.hw) return; for (const w of S.hw) { const al = Math.max(0, 1 - w.d / w.R), a = Math.atan2(w.vy / .8, w.vx); g.save(); g.translate(w.x, w.y); g.scale(1, .8); g.rotate(a); g.lineCap = 'round';
      g.strokeStyle = `rgba(255,214,110,${.8 * al})`; g.lineWidth = 4; g.beginPath(); g.arc(-3, 0, 10, -1.1, 1.1); g.stroke(); g.strokeStyle = `rgba(255,255,255,${al})`; g.lineWidth = 1.5; g.beginPath(); g.arc(-3, 0, 10, -1, 1); g.stroke(); g.restore(); } }
  function drawCharge(g) { const C = hero.charge; if (!C) return; const lv = C.lv, col = lv > 1 ? '255,214,110' : lv ? '140,215,255' : '255,255,255', pul = .5 + .5 * Math.sin(C.t * (lv > 1 ? 22 : 14)), r = (lv > 1 ? 13 : lv ? 11 : 8) + pul * 1.5, cx = hero.x, cy = hero.y - 10; // white -> lv1 blue -> lv2 gold
    g.save(); g.globalCompositeOperation = 'lighter'; const gr = g.createRadialGradient(cx, cy, 1, cx, cy, r); gr.addColorStop(0, `rgba(${col},${Math.min(1, .35 + .25 * pul + C.flash * 2)})`); gr.addColorStop(1, `rgba(${col},0)`); g.fillStyle = gr; g.beginPath(); g.ellipse(cx, cy, r * .8, r, 0, 0, TAU); g.fill();
    const n = (lv + 1) * 3; g.fillStyle = `rgba(${col},.95)`; for (let i = 0; i < n; i++) { const a = C.t * 5 + i * TAU / n, d = r * (1 - ((C.t * 2.2 + i * .37) % 1)); g.fillRect(cx + Math.cos(a) * d - .6, cy + Math.sin(a) * d * .8 - .6, 1.2, 1.2); } g.restore(); }
  function drawHeroSprite(g, zoom) {
    if (zoom === 1) { drawHW(g); drawCharge(g); }
""")
    t=rep(t,"return SWING.range * k * (i === 2 ? SWING.r3 : 1); }","return SWING.range * k * (i === 2 ? SWING.r3 : i >= 3 ? (spOf(i).rangeMul || 1) : 1); }")
    t=rep(t,"go, dirTap, RUN, SWING, swingR, setManual(v)","go, dirTap, RUN, SWING, swingR, spOf, arcW, setManual(v)")
    return t
def controls(t):
    a="| 전투 | 공격 (3연타 콤보) | **J** / **Z** |"
    i=t.index(a);e=t.index('\n',i)
    add=("\n| 전투 | 돌진베기 (달리며 공격) | 달리는 중(더블탭) **J** / **Z** | 앞으로 약 1.7타일 돌진하며 베기. 정면 100° · 1타 사거리 · 피해 1타의 1.3배. 끝난 뒤 0.3초 동안 다음 공격 불가(연타 방지), 판정 뒤 **회피로 캔슬** 가능. 모든 무기 · 마을과 필드/던전/보스 공통 |"
         "\n| 전투 | 모으기 (차지 공격) | **J** / **Z** 를 **누르고 유지** | 짧게 누르면 그대로 3연타. 누른 채로 **0.6초 = 1단계**(푸른 빛 + 효과음), **1.2초 = 2단계**(금빛 + 다른 효과음) → 떼면 강한 정면 베기: 1단계 피해 1타의 2배 · 사거리 ×1.15, 2단계 3배 · 사거리 ×1.4 + 앞으로 검기 1발. 모으는 동안 천천히 이동(걷기의 0.4배, 방향 고정). 맞으면 모으기 취소(슈퍼아머 중에는 유지), 회피도 취소. 정면 전용(360° 없음) |")
    if "돌진베기 (달리며 공격)" not in t: t=t[:e]+add+t[e:]
    return t
def animation(t):
    a="| run (더블탭 달리기) |";i=t.index(a);e=t.index('\n',i)
    add=("\n| 돌진베기 (special.dash) | 무기 1타 애니 재사용 (`@hit1`) | 판정 구간에 맞춤 | 달리며 공격. `hero_anim.src.json` 의 `special.dash` — anim 이름만 바꾸면 전용 프레임으로 교체. 시작 때 흙먼지 + 고리 |"
         "\n| 모으기 (special.charge) | 유지 자세 = 무기 3타 애니의 예비 동작(`hold.p` 0.18) · 해제 = 3타 애니 (`@hit3`) | 판정 구간에 맞춤 | 모으는 동안 빛(흰색 → 1단계 푸른색 → 2단계 금색) + 모여드는 입자, 단계마다 고리 + 효과음. 2단계 해제는 금빛 궤적 + 검기. 전용 프레임은 `special.charge.hold` / `lv1` / `lv2` 의 anim 으로 지정 |")
    if "돌진베기 (special.dash)" not in t: t=t[:e]+add+t[e:]
    return t
kind,src,dst=sys.argv[1:4];s=open(src).read()
if kind=='src':o=json.dumps(anim_obj(json.loads(s)),indent=1,ensure_ascii=False)
elif kind=='herojson':o=json.dumps(anim_obj(json.loads(s),False),separators=(',',':'),ensure_ascii=False)+('\n' if s.endswith('\n') else '')
else:o={'build':build,'template':template,'index':index,'world':world,'controls':controls,'animation':animation}[kind](s)
open(dst,'w').write(o)
