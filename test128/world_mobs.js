/* =====================================================================
 *  world_mobs.js — mob / champion / boss behaviours for the outside world (area 1).
 *  Registry: WorldMobs.def[kind] = {hp, spr, h, r, ...,  update(m, W, dt)}
 *  Combat rule (user): NO GUARD. The only defense is the dodge roll (Shift, i-frames).
 *  => every damaging attack here goes through a telegraph first:
 *     W.hazard({...warn>0}) draws the warning shape (fill grows until it hits),
 *     line telegraphs precede every charge / shot, and bodies only hurt while attacking.
 *     Hazard hit windows are 0.05s (ground pulses / slams / 필살), the roll's i-frames 0.18s (normal; >=0.15s on
 *     every difficulty), so any roll started up to ~0.13s (nightmare ~0.10s) before the hit avoids it; every attack can
 *     also be walked out of.
 *  [balance] values = town/BALANCE_TODO.md (normal). HP / dmg in HP units (hero 50). warn literals are the NORMAL
 *     telegraphs; world.js hazard() scales them by difficulty and clamps to the difficulty floor. Attack starts
 *     ask W.token(m[, ranged]) (max 2 melee + 1 ranged attackers at once, normal).
 *  To add a mob for areas 2-10: add an entry here and place {type:'spawn', mob:'<kind>'} in a map JSON.
 * ===================================================================== */
(function () {
  'use strict';
  const TAU = Math.PI * 2;
  const rnd = (a, b) => a + Math.random() * (b - a);
  const ang = (m, x, y) => Math.atan2(y - m.y, x - m.x);
  const agg = W => (W.diff && W.diff.aggression) || 1; // difficulty aggression: approach speed / attack cooldown
  // ---------- shared helpers ----------
  function wander(m, W, dt, sp) {
    m.wt = (m.wt || 0) - dt;
    if (m.wt <= 0) { m.wt = rnd(0.8, 2.2); const a = rnd(0, TAU); m.wx = Math.random() < 0.35 ? 0 : Math.cos(a); m.wy = Math.random() < 0.35 ? 0 : Math.sin(a); }
    // stay near home
    if (m.home && Math.hypot(m.x - m.home[0], m.y - m.home[1]) > 70) { const a = ang(m, m.home[0], m.home[1]); m.wx = Math.cos(a); m.wy = Math.sin(a); }
    if (m.wx || m.wy) { if (!W.moveCol(m, m.wx * sp * dt, m.wy * sp * dt, m.r, m.fly)) m.wt = 0; if (m.wx) m.face = m.wx > 0 ? 1 : -1; }
  }
  function toward(m, W, dt, sp, x, y) { sp *= agg(W); const a = ang(m, x, y); W.moveCol(m, Math.cos(a) * sp * dt, Math.sin(a) * sp * dt, m.r, m.fly); m.face = x > m.x ? 1 : -1; }
  function lineTele(W, m, a, len, warn, width) { // visual-only warning line (for charges / shots)
    return W.hazard({ shape: 'line', x: m.x, y: m.y, x2: m.x + Math.cos(a) * len, y2: m.y + Math.sin(a) * len, width: width || 8, warn, act: 0, dmg: 0, owner: m }).warn;
  }
  function set(m, st) { m.st = st; m.t = 0; }
  const near = (m, W, d) => W.dist(m, W.hero) < d;
  const tok = (m, W, r) => !W.token || W.token(m, r);

  // chapter-1 Felt mobs (strip-animated, see def.c1_*): approach, then melee when close or a 4-way shot pattern (alternating) at range
  const T60 = a => a.reduce((s, v) => s + v, 0) / 60;
  function startAnim(m, name, a, key, warn) { // play strip `name`; frames before `key` stretch so frame `key` lands at `warn` s (the telegraph end)
    m.anim = name; m.at = 0; m.keyT = warn; m.preT = T60(a.ticks.slice(0, key)); m.dur = warn + T60(a.ticks.slice(key)) * (m.D.rec || 1); }
  // 엘든링식 속도 기본 (사장님 10-25 「엘든링식이 제일 좋다」, 몬스터 교본 1-8): 주인공 걷기 72 · 늦은 제자리 베기 · 스태미나 → 한 번에 한 마리와 싸우게
  //   공격 간격 x0.6→x1, 공격 뒤 빈틈 x1.4, 맞은 뒤 회복 x0.7→x1, 걸음 1.4→1.1 (주인공 걷기의 47~74%), 일반 몹 체력 x0.7
  const FELT_SPD = 1.1; // was 1.4 (owner 10-22 "걷는속도 빠르게"); walk cycle 5 ticks/frame
  // 몹 공격 기준 (owner 10-23 "펠트 몹으로 기준을 잡자"; handoff/claude/MOBS_ROOM4_ko.md 기준표): seconds the mob stands still after each attack = the opening to slash
  const FELT_STD = { restMelee: .91, restShoot: .7, restLunge: 1.26, restLeap: 1.19, backOff: 40 }; // x1.4 for the souls pace (was .65/.5/.9/.85) // 10-24 팀 기준(경고 0.6~0.8, 빈틈 0.8~1.2): strike -> moves again measured 0.73~0.82 s -> +0.1~0.15
  const FELT_SC = 1.35, FELT_CD = 1, FELT_REC = 1; /* souls pace: cooldown / recovery back to x1 (were .6/.7) */ // owner 10-22 "크기 더 키우고 공속 더빠르게": body x1.35 (reach x1.15), cooldowns x0.6, recovery after the hit x0.7 (telegraphs unchanged)
  function pickIntent(P, d, m) { // distance decides which move is likely; the same move never 3 times in a row
    const O = P === 'lunge' ? [['lunge', d >= 35 && d < 110 ? 3 : 1], ['shoot', d >= 90 ? 3 : .6]] : P === 'skirm' ? [['leap', d < 80 ? 3 : 1], ['shoot', d >= 60 ? 3 : 1]]
      : P === 'duel' ? [['combo', d < 60 ? 3 : 1], ['shoot', d >= 60 ? 3 : 1]] : [['melee', d < 45 ? 3 : 1], ['shoot', d >= 45 ? 3 : 1]];
    const H = m.hist || (m.hist = []); for (const o of O) if (H.length >= 2 && H[0] === o[0] && H[1] === o[0]) o[1] = 0;
    for (const o of O) if (o[0] === 'shoot' && !(m.D.shots || []).length) o[1] = 0; // no shots (새끼 거미): bite only
    let t = O.reduce((a, o) => a + o[1], 0) * Math.random(), pick = O[0][0]; for (const o of O) { t -= o[1]; if (t <= 0) { pick = o[0]; break; } }
    H.unshift(pick); H.length = Math.min(H.length, 2); return pick; }
  function felt(o) {
    // style (owner 10-23 "공격 패턴도 타게임이랑 분석해"): each felt mob gets one role instead of the shared melee + 8-way burst.
    //   base = old shared pattern / bind = 실마물 (aimed thread that binds + thread trap under the hero) /
    //   skirm = 바늘 거미 (pounce onto a marked spot + aimed spit) / lunge = 들개 (crouch -> straight dash bite -> 0.8s opening, circles the hero) /
    //   duel = 실 꼭두각시 (scissor 2-hit combo + aimed blade boomerang / pin burst).
    return Object.assign({ felt: true, update(m, W, dt) {
      const h = W.hero, A = this.anim, P = this.style || 'base'; m.t += dt; m.at = (m.at || 0) + dt; m.cd = (m.cd ?? rnd(1, 2)) - dt; m.losT = (m.losT || 0) - dt; if (m.losT <= 0) { m.losT = .25; m.sees = !W.los || W.los(m, h); }
      const d = m.sees || m.st !== 'idle' ? W.dist(m, h) : 999; // 팀장 10-24: behind a wall the hero counts as far away (no alert, no shots, just wanders)
      m.burstT = (m.burstT || 0) - dt; m.burstCd = (m.burstCd || 0) - dt; m.hopCd = (m.hopCd || 0) - dt; const RG = m.rage ? .8 : 1; // RG: angry = shorter cooldowns
      if (!m.alerted && d < 160) { m.alerted = true; m.alertT = .45; W.fx('text', m.x, m.y - this.h * FELT_SC - 6, { text: '!', life: .7, color: '#ffd84a' }); if (W.sfx) W.sfx('tele', .6); m.cd = Math.max(m.cd, .5); } // first sight: "!" + a hop (drawn)
      if (m.alertT > 0) { m.alertT -= dt; m.anim = 'walk'; m.moving = false; return; }
      if (!m.rage && m.hp > 0 && m.hp < m.maxHp * .3) { m.rage = true; m.rageT = .5; W.fx('text', m.x, m.y - this.h * FELT_SC - 6, { text: '!!', life: .8, color: '#ff5a4a' }); } // low HP: angry (faster, shorter cooldowns, extra move)
      if (m.st === 'hop') { const k = Math.min(1, m.t / .3), e = k * (2 - k); W.moveCol(m, m.sx + (m.tx - m.sx) * e - m.x, m.sy + (m.ty - m.sy) * e - m.y, m.r); if (m.t > .3) { set(m, 'idle'); m.intent = 'shoot'; m.cd = 0; } return; } // spider: hop back, then spit
      if (m.hitT > .08 && (m.st === 'idle' || m.st === 'rest')) { // flinch when hit while walking / in the opening (never during a telegraph)
        if (P === 'skirm' && m.hopCd <= 0) { const a = ang(m, h.x, h.y) + Math.PI; m.sx = m.x; m.sy = m.y; m.tx = m.x + Math.cos(a) * 40; m.ty = m.y + Math.sin(a) * 40; m.hopCd = 3; set(m, 'hop'); m.anim = 'walk'; return; }
        m.anim = 'walk'; m.moving = false; return; }
      if (m.dazeT > 0 && (m.st === 'idle' || m.st === 'rest')) { m.dazeT -= dt; m.anim = 'walk'; m.moving = false; return; } // the hero just-dodged its attack: stunned for a moment
      if (m.st === 'melee' || m.st === 'shoot') { if (m.at > m.dur) { const r = m.st === 'melee' ? FELT_STD.restMelee : FELT_STD.restShoot; set(m, 'rest'); m.restT = r; m.anim = 'walk'; } return; }
      if (m.st === 'rest') { m.moving = false; if (m.t > m.restT) set(m, 'idle'); return; } // standard opening: stands still after an attack
      if (m.st === 'lunge') { // committed: the aim does not follow the hero after the line appears
        if (m.sub === 'aim') { if (m.t > m.warn) { m.sub = 'go'; m.t = 0; m.bit = false; } return; }
        if (m.sub === 'go' && !m.bit && m.t > (m.second ? .25 : .38) && !m.second) { m.second = true; m.aim = ang(m, h.x, h.y); m.face = Math.cos(m.aim) >= 0 ? 1 : -1; m.sub = 'aim'; m.t = 0; m.warn = lineTele(W, m, m.aim, 230 * .25, .6, m.r * 2 + 12); startAnim(m, 'attack', A.attack, A.attack.hit, m.warn); W.fx('dust', m.x, m.y); return; } // missed: one short follow-up lunge (new warning)
        if (m.sub === 'go') { if (!m.bit && Math.hypot(h.x - m.x, h.y - m.y) < m.r + 9) { m.bit = true; W.touch(m, m.r + 4, this.melee.dmg); W.fx('bite', h.x, h.y - 10, { life: .22 }); }
          const sp = 230 * dt; if (!W.moveCol(m, Math.cos(m.aim) * sp, Math.sin(m.aim) * sp, m.r) || m.t > (m.second ? .25 : .38)) { m.sub = 'rec'; m.t = 0; W.fx('dust', m.x, m.y); } return; }
        if (m.t > FELT_STD.restLunge) { set(m, 'idle'); m.sub = null; m.anim = 'walk'; } return; } // recovery = the punish window
      if (m.st === 'leap') { if (m.t < m.warn) { const k = Math.min(1, m.t / m.warn), e = k * k * (3 - 2 * k), nx = m.sx + (m.tx - m.sx) * e, ny = m.sy + (m.ty - m.sy) * e; W.moveCol(m, nx - m.x, ny - m.y, m.r); }
        else if (m.t > m.warn + FELT_STD.restLeap) { set(m, 'idle'); m.anim = 'walk'; } return; }
      m.anim = 'walk'; const x0 = m.x, y0 = m.y;
      if (m.cd <= 0 && !m.intent) m.intent = pickIntent(P, d, m); // each cooldown: pick one move (distance-weighted, never 3 in a row)
      const want = m.intent === 'melee' || m.intent === 'combo' ? this.melee.range : m.intent === 'lunge' ? 70 : m.intent === 'leap' ? 55 : m.intent === 'shoot' ? 70 : 52; // hold ~52px between attacks
      if ((P === 'bind' || P === 'duel') && (m.intent === 'melee' || m.intent === 'combo') && d > this.melee.range + 20 && d < 110 && m.burstCd <= 0) { m.burstT = .3; m.burstCd = 2.5; W.fx('dust', m.x, m.y); } // quick scuttle / step-in before a close attack
      const spd = this.sp * FELT_SPD * (m.burstT > 0 ? 3 : 1) * (m.rage ? 1.25 : 1);
      if (d < 200) { if (d > want + 6) toward(m, W, dt, spd, h.x, h.y); else if (d < (m.intent === 'shoot' ? FELT_STD.backOff : want - 14)) toward(m, W, dt, -this.sp * FELT_SPD * .5, h.x, h.y); // shooters only back off when the hero is right on them
        else if (P === 'lunge') { m.orb = m.orb || (Math.random() < .5 ? 1 : -1); const a = ang(m, h.x, h.y) + m.orb * Math.PI / 2, sp = this.sp * FELT_SPD * .6 * agg(W); // circle the hero like a dog pack
          if (!W.moveCol(m, Math.cos(a) * sp * dt, Math.sin(a) * sp * dt, m.r)) m.orb = -m.orb; m.face = h.x > m.x ? 1 : -1; }
        else m.face = h.x > m.x ? 1 : -1; }
      else wander(m, W, dt, this.sp * FELT_SPD * .5);
      if (W.mobs) for (const o of W.mobs) { if (o === m || o.dead) continue; const dx = m.x - o.x, dy = m.y - o.y, dd = Math.hypot(dx, dy) || .01, gap = m.r + o.r + 8; // spread out around the hero instead of stacking
        if (dd < gap) { const push = Math.min(gap - dd, 60 * dt); W.moveCol(m, dx / dd * push, dy / dd * push, m.r); } }
      const vx = m.x - x0, vy = m.y - y0, mv = Math.hypot(vx, vy); m.moving = mv > 1e-3; m.wph = (m.wph || 0) + mv / (this.sp * FELT_SPD); // walk cycle advances with the distance moved (legs match the ground speed)
      m.stepAcc = (m.stepAcc || 0) + mv; if (m.stepAcc > 16) { m.stepAcc = 0; W.fx('dust', m.x, m.y, { life: .3 }); } // little puffs at the feet
      const engaged = d < 200, fa = engaged ? ang(m, h.x, h.y) : Math.atan2(vy, vx); // engaged: always look at the hero (backpedal / sidestep), else face the way it walks
      if (engaged || m.moving) { const k = ((Math.round(fa / (Math.PI / 4)) % 8) + 8) % 8; m.wdir = ['side', 'se', 's', 'se', 'side', 'ne', 'n', 'ne'][k]; if (Math.abs(Math.cos(fa)) > 1e-3) m.face = Math.cos(fa) > 0 ? 1 : -1; } // 8-way walk strips (↙↖ = mirrored ↘↗)
      m.back = engaged && m.moving && vx * Math.cos(fa) + vy * Math.sin(fa) < 0; // walking away from where it looks -> walk strip plays backwards
      if (m.cd > 0 || d > 150) return;
      if (m.intent === 'melee' && d < this.melee.range + 12 && tok(m, W)) { m.intent = null; const a = ang(m, h.x, h.y), reach = this.melee.range * .6; m.face = Math.cos(a) >= 0 ? 1 : -1;
        const z = W.hazard({ shape: 'circle', x: m.x + Math.cos(a) * reach, y: m.y + Math.sin(a) * reach * .8, r: this.melee.rad, warn: 0.55, act: 0.05, dmg: this.melee.dmg, kind: 'swipe', owner: m });
        startAnim(m, 'attack', A.attack, A.attack.hit, z.warn); set(m, 'melee'); m.cd = 1.6 * FELT_CD * RG / agg(W); return; }
      if (m.intent === 'combo' && d < this.melee.range + 12 && tok(m, W)) { m.intent = null; const a = ang(m, h.x, h.y), r1 = this.melee.range * .6, r2 = this.melee.range * 1.25; m.face = Math.cos(a) >= 0 ? 1 : -1; // scissor 2-hit: snip, then a longer snip 0.3s later
        const z = W.hazard({ shape: 'circle', x: m.x + Math.cos(a) * r1, y: m.y + Math.sin(a) * r1 * .8, r: this.melee.rad, warn: 0.55, act: 0.05, dmg: this.melee.dmg, kind: 'swipe', owner: m });
        W.hazard({ shape: 'circle', x: m.x + Math.cos(a) * r2, y: m.y + Math.sin(a) * r2 * .8, r: this.melee.rad, warn: z.warn + 0.3, act: 0.05, dmg: this.melee.dmg, kind: 'swipe', owner: m });
        if (m.rage) { const r3 = this.melee.range * 1.9; W.hazard({ shape: 'circle', x: m.x + Math.cos(a) * r3, y: m.y + Math.sin(a) * r3 * .8, r: this.melee.rad, warn: z.warn + 0.6, act: 0.05, dmg: this.melee.dmg, kind: 'swipe', owner: m }); } // angry: a third snip
        startAnim(m, 'attack', A.attack, A.attack.hit, z.warn + 0.3); set(m, 'melee'); m.cd = 1.9 * FELT_CD * RG / agg(W); return; }
      const packBusy = P === 'lunge' && W.mobs && W.mobs.some(o => o !== m && !o.dead && o.kind === m.kind && o.st === 'lunge' && o.sub !== 'rec'); // pack: one dog lunges at a time, the rest keep circling
      if (m.intent === 'lunge' && d < 95 && !packBusy && tok(m, W)) { m.intent = null; m.aim = ang(m, h.x, h.y); m.face = Math.cos(m.aim) >= 0 ? 1 : -1;
        const w = lineTele(W, m, m.aim, 230 * .38, 0.6, m.r * 2 + 12); set(m, 'lunge'); m.sub = 'aim'; m.warn = w; m.second = false; startAnim(m, 'attack', A.attack, A.attack.hit, w); m.cd = 1.9 * FELT_CD * RG / agg(W); return; }
      if (m.intent === 'leap' && d < 85 && tok(m, W)) { m.intent = null; const a = ang(m, h.x, h.y), L = Math.min(d, 60); m.face = Math.cos(a) >= 0 ? 1 : -1;
        let aa = a; for (let t = 0; t < 4 && W.mobs && W.mobs.some(o => o !== m && !o.dead && Math.hypot(o.x - (m.x + Math.cos(aa) * L), o.y - (m.y + Math.sin(aa) * L)) < o.r + m.r + 6); t++) aa = a + (t % 2 ? -1 : 1) * .45 * (1 + (t >> 1)); // don't land on a packmate
        m.sx = m.x; m.sy = m.y; m.tx = m.x + Math.cos(aa) * L; m.ty = m.y + Math.sin(aa) * L; // lands on the marked spot (where the hero stood)
        const z = W.hazard({ shape: 'circle', x: m.tx, y: m.ty, r: this.melee.rad, warn: 0.55, act: 0.05, dmg: this.melee.dmg, kind: 'swipe', owner: m });
        m.warn = z.warn; startAnim(m, 'attack', A.attack, A.attack.hit, z.warn); set(m, 'leap'); m.cd = 1.7 * FELT_CD * RG / agg(W); return; }
      if (m.intent === 'shoot' && d > 40 && tok(m, W, true)) { m.intent = null; m.pi = ((m.pi ?? Math.floor(Math.random() * 2)) + 1) % this.shots.length; const p = this.shots[m.pi]; m.face = h.x > m.x ? 1 : -1;
        let tw = 0.6;
        if (p.trap) { tw = W.hazard({ shape: 'circle', x: h.x, y: h.y, r: p.trap.r, warn: 0.8, act: 0.05, dmg: p.trap.dmg, slow: p.trap.slow, kind: 'web', owner: m }).warn; } // thread trap under the hero
        else { const aim = ang(m, h.x, h.y - 8), dirs = p.spread ? p.spread.map(s => aim + s) : [0, 1, 2, 3, 4, 5, 6, 7].map(i => i * Math.PI / 4); // aimed fan (style mobs) or the old 8-way ring
          for (const a of dirs) tw = lineTele(W, m, a, Math.min(150, p.sp * 1.4), 0.6, 6);
          const bid = m.bid || 0; for (const w of p.waves) W.after(tw + w, () => { if (m.dead || (m.bid || 0) !== bid) return; /* a break (경직) cancels the volley */ for (const a of dirs) W.shot(Object.assign({ x: m.x, y: m.y - this.h * .45, a, sp: p.sp, owner: m }, p.shot)); }); }
        startAnim(m, 'shoot', A.shoot, A.shoot.release, tw); set(m, 'shoot'); m.cd = 2.4 * FELT_CD * RG / agg(W); }
    }, onDeath(m, W) { W.fx('fluff', m.x, m.y - this.h * .5, { life: .9, col: this.col || '#b0a890', n: 14 }); } }, o); // felt-like death: fluff and thread bits burst out
  }

  // areas 2-9 regulars (room-3 strips, assets/mobs47: idle 8 frames + attack 12 frames, hit frame 4; drawn hi-res by world.js drawS47).
  // One shared AI per attack style, every hit telegraphed: melee = circle in front / shoot = aim line then shot(s) / charge = aim line then dash /
  // aoe = ring around itself / drop = circle under the hero. HP / dmg grow by area. h = body height in field px (strip body px x 0.2).
  const ATK47 = { n: 12, ticks: [6, 3, 3, 2, 3, 3, 3, 3, 2, 3, 4, 6], hit: 4 };
  const SHOT47 = { beam: { sp: 190, r: 3, life: 1.0 }, arrow: { sp: 150, r: 2, life: 1.3 }, firearrow: { sp: 155, r: 2, life: 1.3 }, spike: { sp: 120, r: 2, life: 1.0 },
    ink: { sp: 95, r: 4, life: 1.5, slow: 0.8 }, bolt: { sp: 170, r: 3, life: 1.0 }, feather: { sp: 130, r: 2, life: 1.2 }, orb: { sp: 85, r: 5, life: 2.0 } };
  const HAZ47 = { rock: 'rock', sand: 'web', bolt: 'crystal', poison: 'poison', shock: 'crystal', wave: 'swipe' };
  function s47(o) {
    const a = o.area, dmg = Math.round(5 + (a - 1) * 0.6);
    return Object.assign({ s47: o.id, anim: { attack: ATK47 }, hp: 50 + (a - 1) * 14, r: Math.max(5, Math.round(o.h * .22)), sp: o.fly ? 34 : 26, aff: { weak: [], resist: [] }, dmg,
      update(m, W, dt) {
        const h = W.hero, D = this; m.t += dt; m.at = (m.at || 0) + dt; m.cd = (m.cd ?? rnd(1, 2.2)) - dt; const d = W.dist(m, h);
        if (m.st === 'dash') { const sp = 210 * dt; W.touch(m, m.r + 4, D.dmg); if (!W.moveCol(m, Math.cos(m.aim) * sp, Math.sin(m.aim) * sp, m.r, m.fly) || m.t > 0.55) { set(m, 'idle'); m.anim = null; W.fx('dust', m.x, m.y); } return; }
        if (m.st === 'atk') { if (m.at > m.dur) { if (m.next) { const f = m.next; m.next = null; f(); } else { set(m, 'idle'); m.anim = null; } } return; }
        const x0 = m.x, y0 = m.y, want = D.ai === 'melee' ? 22 : D.ai === 'aoe' ? 16 : D.ai === 'charge' ? 80 : 95;
        if (D.sp && d < 200) { if (d > want + 8) toward(m, W, dt, D.sp, h.x, h.y); else if (d < want - 24) toward(m, W, dt, -D.sp * .7, h.x, h.y); else m.face = h.x > m.x ? 1 : -1; }
        else if (D.sp) wander(m, W, dt, D.sp * .5); else m.face = h.x > m.x ? 1 : -1;
        m.moving = Math.abs(m.x - x0) + Math.abs(m.y - y0) > 1e-3;
        if (m.cd > 0 || d > (D.ai === 'melee' || D.ai === 'aoe' ? want + 16 : 160)) return;
        const ranged = D.ai === 'shoot' || D.ai === 'drop'; if (!tok(m, W, ranged)) return;
        const A = ang(m, h.x, h.y); m.face = Math.cos(A) >= 0 ? 1 : -1; let warn = 0.6;
        if (D.ai === 'melee') { const reach = 14; warn = W.hazard({ shape: 'circle', x: m.x + Math.cos(A) * reach, y: m.y + Math.sin(A) * reach * .8, r: 15, warn: 0.55, act: 0.05, dmg: D.dmg, kind: 'swipe', owner: m }).warn; m.cd = 1.5 / agg(W); }
        else if (D.ai === 'aoe') { warn = W.hazard({ shape: 'circle', x: m.x, y: m.y, r: 34, warn: 0.75, act: 0.1, dmg: D.dmg, kind: HAZ47[D.fx] || 'swipe', owner: m }).warn; m.cd = 2.2 / agg(W); }
        else if (D.ai === 'drop') { warn = W.hazard({ shape: 'circle', x: h.x, y: h.y, r: 16, warn: 0.8, act: 0.05, dmg: D.dmg, kind: HAZ47[D.fx] || 'rock', owner: m }).warn; m.cd = 2.2 / agg(W); }
        else if (D.ai === 'charge') { m.aim = A; warn = lineTele(W, m, A, 130, 0.55, 14); m.next = () => { set(m, 'dash'); m.anim = 'hold'; if (W.sfx) W.sfx('mob_dash', .7); }; m.cd = 2.0 / agg(W); }
        else { const S2 = SHOT47[D.fx] || SHOT47.arrow, dirs = D.pat === 'ring' ? [...Array(8)].map((_, i) => i * Math.PI / 4) : D.pat === 'fan' ? [A - .3, A, A + .3] : [A];
          for (const b of dirs) warn = lineTele(W, m, b, Math.min(150, S2.sp * 1.2), 0.6, 6);
          W.after(warn, () => { if (m.dead) return; for (const b of dirs) W.shot(Object.assign({ x: m.x, y: m.y - D.h * .45, a: b, dmg: D.dmg - 1, kind: D.fx, owner: m }, S2)); }); m.cd = 2.0 / agg(W); }
        startAnim(m, 'attack', ATK47, ATK47.hit, warn); set(m, 'atk'); if (D.ai === 'charge') m.dur = warn;
      } }, o);
  }

  const def = {
    // ------------------------------------------------ area 1 regulars (WORLD_PLAN.md / MONSTERS.md)
    mushroom: { name: '독버섯', aff: { weak: ['slash'], resist: ['blunt'] }, hp: 50, spr: 'mushroom', h: 20, r: 6,
      update(m, W, dt) { m.t += dt; m.cd = (m.cd || 0) - dt;
        if (m.st === 'puff') { if (m.t > 1.0) set(m, 'idle'); return; }
        wander(m, W, dt, 10);
        if (m.cd <= 0 && (near(m, W, 30) || m.hitT > 0) && tok(m, W)) { set(m, 'puff'); m.cd = 2.4 / agg(W); // spore burst: ring warns 0.7s, then a short poison cloud
          W.hazard({ shape: 'circle', x: m.x, y: m.y - 4, r: 30, warn: 0.6, act: 0.9, dmg: 5, kind: 'poison', owner: m }); }
      } },
    rabbit: { name: '뿔토끼', aff: { weak: ['slash'], resist: [] }, hp: 40, spr: 'rabbit', h: 22, r: 5,
      update(m, W, dt) { const h = W.hero; m.t += dt;
        if (m.st === 'aim') { m.shake = 1; if (m.t > m.warn) { set(m, 'charge'); m.shake = 0; } return; }
        if (m.st === 'charge') { const sp = 190 * dt; m.face = m.dx > 0 ? 1 : m.dx < 0 ? -1 : m.face;
          W.touch(m, 8, 5);
          if (!W.moveCol(m, m.dx * sp, m.dy * sp, m.r)) { set(m, 'stun'); W.fx('stars', m.x, m.y - 20); W.shake(1); }
          else if (m.t > 0.75) set(m, 'rest'); return; }
        if (m.st === 'stun') { if (m.t > 1.3) set(m, 'idle'); return; }
        if (m.st === 'rest') { if (m.t > 0.9) set(m, 'idle'); return; }
        wander(m, W, dt, 22);
        const dx = h.x - m.x, dy = h.y - m.y, d = Math.hypot(dx, dy);
        if (d < 156 && (Math.abs(dx) < 10 || Math.abs(dy) < 10) && m.t > 0.6 && tok(m, W)) { // straight-line charge only when lined up
          m.dx = Math.abs(dx) < 10 ? 0 : Math.sign(dx); m.dy = Math.abs(dx) < 10 ? Math.sign(dy) : 0;
          set(m, 'aim'); m.warn = lineTele(W, m, Math.atan2(m.dy, m.dx), 140, 0.47, 10); }
      } },
    wasp: { name: '말벌', aff: { weak: ['pierce'], resist: ['blunt'] }, hp: 50, spr: 'wasp', h: 20, r: 5, fly: true, hover: 10,
      update(m, W, dt) { const h = W.hero; m.t += dt; m.cd = (m.cd ?? rnd(1, 2.5)) - dt;
        if (m.st === 'aim') { if (m.t > m.warn) { W.shot({ x: m.x, y: m.y, a: m.aim, sp: 130, r: 3, dmg: 5, kind: 'sting', owner: m }); set(m, 'retreat'); } return; }
        if (m.st === 'retreat') { const a = ang(m, h.x, h.y) + Math.PI; W.moveCol(m, Math.cos(a) * 50 * dt, Math.sin(a) * 50 * dt, m.r, true); if (m.t > 0.6) set(m, 'idle'); return; }
        const d = W.dist(m, h);
        if (d > 75) toward(m, W, dt, 50, h.x, h.y); else if (d < 50) toward(m, W, dt, -30, h.x, h.y);
        else { m.orb = (m.orb || 0) + dt; W.moveCol(m, Math.cos(m.orb) * 20 * dt, Math.sin(m.orb * 1.3) * 14 * dt, m.r, true); }
        if (m.cd <= 0 && d < 143 && tok(m, W, true)) { m.cd = 1.92 / agg(W); m.aim = ang(m, h.x, h.y - 8); set(m, 'aim'); m.warn = lineTele(W, m, m.aim, 120, 0.51, 6); }
      } },
    boar: { name: '멧돼지', aff: { weak: ['pierce'], resist: ['blunt'] }, hp: 60, spr: 'boar', h: 20, r: 7,
      update(m, W, dt) { const h = W.hero; m.t += dt; const rage = m.hp <= m.maxHp / 2; m.tint = rage ? 'rage' : null;
        if (m.st === 'aim') { m.shake = 1; if (m.t > m.warn) { set(m, 'charge'); m.shake = 0; } return; }
        if (m.st === 'charge') { const sp = (rage ? 250 : 160) * dt; W.touch(m, 9, 6); m.face = Math.cos(m.aim) > 0 ? 1 : -1;
          if (!W.moveCol(m, Math.cos(m.aim) * sp, Math.sin(m.aim) * sp, m.r) || m.t > 0.9) { set(m, 'rest'); W.fx('dust', m.x, m.y); } return; }
        if (m.st === 'rest') { if (m.t > (rage ? 0.6 : 1.1)) set(m, 'idle'); return; }
        wander(m, W, dt, rage ? 40 : 20);
        if (W.dist(m, h) < 130 && m.t > 1 && tok(m, W)) { m.aim = ang(m, h.x, h.y); set(m, 'aim'); m.warn = lineTele(W, m, m.aim, 150, rage ? 0.45 : 0.55, 14); }
      } },
    scarecrow: { name: '호박 허수아비', aff: { weak: ['slash'], resist: ['pierce'] }, hp: 55, spr: 'scarecrow', h: 30, r: 6,
      init(m) { m.st = 'dormant'; m.noBar = true; },
      update(m, W, dt) { const h = W.hero; m.t += dt;
        if (m.st === 'dormant') { m.lean = 1; if (near(m, W, 36) || m.hitT > 0) { set(m, 'rise'); m.noBar = false;
            W.hazard({ shape: 'circle', x: m.x, y: m.y, r: 26, warn: 0.6, act: 0.05, dmg: 5, kind: 'swipe', owner: m }); } return; }
        m.lean = Math.max(0, (m.lean || 0) - dt * 3);
        if (m.st === 'rise') { if (m.t > 0.8) set(m, 'chase'); return; }
        if (m.st === 'swipe') { if (m.t > 1.0) set(m, 'chase'); return; }
        toward(m, W, dt, 22, h.x, h.y); m.hop = Math.abs(Math.sin(m.t * 8)) * 3;
        if (m.t > 1.8 && near(m, W, 40) && tok(m, W)) { set(m, 'swipe'); const a = ang(m, h.x, h.y);
          W.hazard({ shape: 'circle', x: m.x + Math.cos(a) * 14, y: m.y + Math.sin(a) * 10, r: 20, warn: 0.6, act: 0.05, dmg: 5, kind: 'swipe', owner: m }); }
      } },
    slime: { name: '숲 슬라임', aff: { weak: ['blunt'], resist: ['pierce'] }, hp: 40, spr: 'slime', sprAtk: 'slime_atk', h: 18, r: 6,
      update(m, W, dt) { const h = W.hero; m.t += dt; const sc = m.mini ? 0.6 : 1;
        if (m.st === 'prep') { const pw = Math.max(0.1, (m.warn || 0.68) - 0.35); m.squash = Math.min(1, m.t / pw); if (m.t > pw) { set(m, 'jump'); m.sx = m.x; m.sy = m.y; } return; }
        if (m.st === 'jump') { const p = Math.min(1, m.t / 0.35); m.x = m.sx + (m.tx - m.sx) * p; m.y = m.sy + (m.ty - m.sy) * p; m.hz = Math.sin(p * Math.PI) * 14; m.squash = 0;
          if (p >= 1) { m.hz = 0; set(m, 'idle'); if (W.blockedAt(m.x, m.y)) { m.x = m.sx; m.y = m.sy; } } return; }
        if (m.t > (m.mini ? 0.9 : 1.3) && W.dist(m, h) < 143 && tok(m, W)) { // hop at the hero: landing spot shown 0.45s before it lands
          const a = ang(m, h.x, h.y), d = Math.min(W.dist(m, h), 34); m.tx = m.x + Math.cos(a) * d; m.ty = m.y + Math.sin(a) * d; m.face = Math.cos(a) > 0 ? 1 : -1;
          if (W.blockedAt(m.tx, m.ty)) { m.t = 0; return; }
          set(m, 'prep'); m.warn = W.hazard({ shape: 'circle', x: m.tx, y: m.ty, r: 11 * sc + 2, warn: 0.68, act: 0.05, dmg: 5, kind: 'thud', owner: m }).warn;
        } else if (m.t > 2.5) { m.t = 0; }
        if (m.st === 'idle' && W.dist(m, h) >= 110) wander(m, W, dt, 8);
      },
      onDeath(m, W) { if (!m.mini) for (const s of [-1, 1]) { const k = W.spawn('slime', m.x + s * 8, m.y, { mini: true, noDrop: true }); k.hp = k.maxHp = Math.round(20 * ((W.diff && W.diff.enemy_hp) || 1)); k.hpLag = k.hp; k.scale = 0.6; } } },
    squirrel: { name: '도토리 다람쥐', aff: { weak: ['blunt'], resist: [] }, hp: 40, spr: 'squirrel', sprAtk: 'squirrel_atk', h: 22, r: 5,
      update(m, W, dt) { const h = W.hero; m.t += dt; m.cd = (m.cd ?? rnd(1, 2)) - dt; const d = W.dist(m, h);
        if (m.st === 'throw') { m.atk = m.t < 0.4; if (m.t > 0.9) set(m, 'idle'); return; }
        if (d < 55) toward(m, W, dt, -35, h.x, h.y); else if (d > 100) toward(m, W, dt, 31, h.x, h.y); else wander(m, W, dt, 10);
        if (m.cd <= 0 && d < 156 && tok(m, W, true)) { m.cd = 2.08 / agg(W); set(m, 'throw'); m.face = h.x > m.x ? 1 : -1; // lobbed acorn: target marker 0.85s
          W.hazard({ shape: 'circle', x: h.x, y: h.y, r: 10, warn: 0.72, act: 0.05, dmg: 5, kind: 'acorn', from: [m.x, m.y - 12], owner: m }); }
      } },
    sprout: { name: '나무 정령 새싹', aff: { weak: ['slash'], resist: ['pierce'] }, hp: 60, spr: 'sprout', sprAtk: 'sprout_atk', h: 22, r: 5,
      update(m, W, dt) { const h = W.hero; m.t += dt; m.cd = (m.cd ?? rnd(1.5, 3)) - dt; const d = W.dist(m, h);
        if (m.st === 'cast') { m.atk = true; if (m.t > 1.1) { set(m, 'idle'); m.atk = false; } return; }
        if (d > 50 && d < 195) toward(m, W, dt, 18, h.x, h.y); else wander(m, W, dt, 8);
        if (m.cd <= 0 && d < 169 && tok(m, W, true)) { m.cd = 2.56 / agg(W); set(m, 'cast'); // root bind: circle under the hero 0.9s, roots slow on hit
          W.hazard({ shape: 'circle', x: h.x, y: h.y, r: 14, warn: 0.77, act: 0.05, dmg: 5, kind: 'root', slow: 1.2, owner: m }); }
      } },

    // ------------------------------------------------ area 1 champions (field)
    champ_boar: { name: '돌엄니', aff: { weak: ['pierce'], resist: ['blunt'] }, title: '거대 왕멧돼지', champion: true, hp: 320, spr: 'champ_boar', h: 38, r: 12,
      update(m, W, dt) { const h = W.hero; m.t += dt; const rage = m.hp <= m.maxHp * 0.4; m.sprite = rage ? 'champ_boar_rage' : (m.st === 'charge' ? 'champ_boar_run' : 'champ_boar');
        if (rage && !m.raged) { m.raged = true; W.banner('돌엄니가 분노했다!'); W.shake(3); }
        const k = rage ? 1 / 1.2 : 1; // enrage: everything x1.2 faster (telegraphs still clamped to the floor)
        if (m.st === 'aim') { m.shake = 1; if (m.t > m.warn) { set(m, 'charge'); m.shake = 0; } return; }
        if (m.st === 'charge') { const sp = (rage ? 264 : 220) * dt; W.touch(m, 14, 9); m.face = Math.cos(m.aim) > 0 ? 1 : -1;
          W.breakDecoNear(m.x + Math.cos(m.aim) * 14, m.y + Math.sin(m.aim) * 8, 12); // smashes rocks / bushes on the way (벽 부수며 돌진)
          const ok = W.moveCol(m, Math.cos(m.aim) * sp, Math.sin(m.aim) * sp, m.r);
          if (!ok || m.t > 1.1) { W.fx('dust', m.x, m.y); if (!ok) W.shake(2);
            if (--m.chain > 0) { m.aim = ang(m, h.x, h.y); set(m, 'aim'); m.warn = lineTele(W, m, m.aim, 240, 0.47 * k, 26); } else set(m, 'rest'); }
          return; }
        if (m.st === 'stomp') { if (m.t > 1.2) set(m, 'rest'); return; }
        if (m.st === 'rest') { if (m.t > 1.2 * k) set(m, 'idle'); return; }
        if (!m.aggro) { wander(m, W, dt, 15); if (near(m, W, 156) || m.hitT > 0) { m.aggro = true; W.engage(m); } return; }
        toward(m, W, dt, 28, h.x, h.y);
        if (m.t > 0.9) { if (m.last !== 'stomp' && near(m, W, 50)) { m.last = 'stomp'; set(m, 'stomp');
            W.hazard({ shape: 'circle', x: m.x, y: m.y, r: 46, warn: 0.72 * k, act: 0.05, dmg: 9, kind: 'quake', owner: m }); }
          else { m.last = 'charge'; m.chain = rage ? 3 : 2; m.aim = ang(m, h.x, h.y); set(m, 'aim'); m.warn = lineTele(W, m, m.aim, 240, 0.59 * k, 26); } }
      } },
    champ_wasp: { name: '여왕 말벌', aff: { weak: ['pierce'], resist: ['blunt'] }, title: '숲의 여왕', champion: true, hp: 320, spr: 'champ_wasp', h: 40, r: 10, fly: true, hover: 14,
      update(m, W, dt) { const h = W.hero; m.t += dt; m.sprite = m.st === 'dive' || m.st === 'rain' ? 'champ_wasp_atk' : 'champ_wasp';
        if (m.st === 'aim') { if (m.t > m.warn) set(m, 'dive'); return; }
        if (m.st === 'dive') { const sp = 260 * dt; W.touch(m, 11, 9); W.moveCol(m, Math.cos(m.aim) * sp, Math.sin(m.aim) * sp, m.r, true); if (m.t > 0.6) set(m, 'rest'); return; }
        if (m.st === 'rain' || m.st === 'summon') { if (m.t > 1.6) set(m, 'rest'); return; }
        if (m.st === 'rest') { m.orb = (m.orb || 0) + dt * 1.5; W.moveCol(m, Math.cos(m.orb) * 30 * dt, Math.sin(m.orb) * 20 * dt, m.r, true); if (m.t > 1.1) set(m, 'idle'); return; }
        if (!m.aggro) { m.orb = (m.orb || 0) + dt; W.moveCol(m, Math.cos(m.orb) * 12 * dt, Math.sin(m.orb * 1.4) * 8 * dt, m.r, true); if (near(m, W, 156) || m.hitT > 0) { m.aggro = true; W.engage(m); } return; }
        const d = W.dist(m, h); if (d > 80) toward(m, W, dt, 50, h.x, h.y); else if (d < 50) toward(m, W, dt, -30, h.x, h.y);
        if (m.t < 1) return;
        const opts = ['dive', 'rain', 'summon'].filter(p => p !== m.last && (p !== 'summon' || W.count('wasp') < 3));
        const p = opts[Math.floor(Math.random() * opts.length)]; m.last = p;
        if (p === 'dive') { m.aim = ang(m, h.x, h.y); set(m, 'aim'); m.warn = lineTele(W, m, m.aim, 170, 0.59, 20); }
        else if (p === 'rain') { set(m, 'rain'); // poison rain: 7 drops (one on the hero) each warns ~1s, leaves a short visible pool
          for (let i = 0; i < 7; i++) { const a = rnd(0, TAU), rr = i ? rnd(16, 70) : 0;
            W.hazard({ shape: 'circle', x: h.x + Math.cos(a) * rr, y: h.y + Math.sin(a) * rr * 0.8, r: 12, warn: 0.81 + i * 0.08, act: 0.05, dmg: 9, kind: 'poison', linger: 1.6, owner: m }); } }
        else { set(m, 'summon'); W.banner('여왕 말벌이 병정 말벌을 부른다!', 1.2);
          for (let i = 0; i < 3; i++) { const a = i * TAU / 3, x = m.x + Math.cos(a) * 26, y = m.y + Math.sin(a) * 20;
            W.hazard({ shape: 'circle', x, y, r: 8, warn: 0.6, act: 0, dmg: 0, kind: 'summon', onEnd: () => { const s = W.spawn('wasp', x, y, { noDrop: true }); s.summoned = true; } }); } }
      } },

    // ------------------------------------------------ area 1 boss: 이끼 수정 골렘 (BOSS_PATTERNS.md §1)
    golem: { name: '이끼 수정 골렘', aff: { weak: ['blunt'], resist: ['pierce'] }, boss: true, hp: 1673, spr: 'golem', h: 72, r: 15, kb: 0,
      init(m) { m.phase = 1; m.st = 'intro'; m.ultCd = 6; },
      update(m, W, dt) { const h = W.hero; m.t += dt; const P2 = m.phase === 2, k = P2 ? 0.8 : 1;
        if (m.phase === 1 && m.hp <= m.maxHp / 2 && m.st !== 'phase') { set(m, 'phase'); m.invuln = true; m.phase = 2; W.phase2(m); return; }
        if (P2) m.ultCd -= dt;
        switch (m.st) {
          case 'intro': if (m.t > 1.4) set(m, 'idle'); return;
          case 'phase': m.shake = 1; if (m.t > 1.8) { m.invuln = false; m.shake = 0; set(m, 'idle'); } return;
          case 'idle': {
            if (W.dist(m, h) > 60) toward(m, W, dt, 20, h.x, h.y);
            if (m.t < (P2 ? 0.7 : 1.1)) return;
            if (P2 && m.ultCd <= 0) { m.ultCd = 24; m.last = 'ult'; set(m, 'ult'); W.ult(m, 2.21); return; }
            const pool = P2 ? ['A', 'B', 'C', 'D', 'E', 'F'] : ['A', 'B', 'C'];
            const opts = pool.filter(p => p !== m.last && !(p === 'C' && m.hp > m.maxHp * 0.85));
            const p = opts[Math.floor(Math.random() * opts.length)]; m.last = p; set(m, 'p' + p); m.n = 0;
            W.banner(({ A: '대지 강타', B: '수정 파편', C: '이끼 재생', D: '구르기 돌진', E: '수정 감옥', F: '낙석 비' })[p], 1.0, true);
            if (p === 'A') { // slam: three expanding crystal rings, each with its own warning
              [[0, 36, 0.77], [36, 66, 1.02], [66, 98, 1.27]].forEach(([r0, r1, w]) => W.hazard({ shape: 'ring', x: m.x, y: m.y, r0, r: r1, warn: w * k, act: 0.05, dmg: 11, kind: 'crystal', owner: m }));
              W.after(0.77 * k, () => W.shake(3)); }
            if (p === 'B') m.n = P2 ? 2 : 1;
            if (p === 'C') { m.regenHits = 0; }
            if (p === 'D') { m.bounces = 3; m.aim = ang(m, h.x, h.y); m.sub = 'aim'; m.warn = lineTele(W, m, m.aim, 320, 0.68, 28); }
            if (p === 'E') { const gap = Math.floor(rnd(0, 12)); const hx = h.x, hy = h.y;
              for (let i = 0; i < 12; i++) { if (i === gap || i === (gap + 1) % 12) continue; const a = i * TAU / 12;
                W.hazard({ shape: 'circle', x: hx + Math.cos(a) * 36, y: hy + Math.sin(a) * 28, r: 6, warn: 0.64, act: 0, dmg: 0, kind: 'cage', onEnd: (z) => W.tempSolid(z.x, z.y, 7, 2.8, 'crystal') }); }
              W.hazard({ shape: 'circle', x: hx, y: hy, r: 30, warn: 1.7, act: 0.05, dmg: 11, kind: 'quake', owner: m }); } // slam inside the cage; leave by the gap or roll
            if (p === 'F') { W.shake(2); for (let i = 0; i < 11; i++) { const pt = i ? W.randomFloor() : [h.x, h.y];
                W.hazard({ shape: 'circle', x: pt[0], y: pt[1], r: 13, warn: 0.85 + i * 0.07, act: 0.05, dmg: 11, kind: 'rock', owner: m }); } }
            return; }
          case 'pA': if (m.t > 2.0 * k) set(m, 'idle'); return;
          case 'pB': if (m.t > 0.2 && m.n > 0 && !m.aiming) { m.aiming = true; m.aim = ang(m, h.x, h.y);
              let tw = 0.55; for (let i = -2; i <= 2; i++) tw = lineTele(W, m, m.aim + i * 0.33, 150, 0.55, 6);
              W.after(tw, () => { for (let i = -2; i <= 2; i++) W.shot({ x: m.x, y: m.y - 10, a: m.aim + i * 0.33, sp: 150, r: 4, dmg: 11, kind: 'shard', owner: m }); m.n--; m.aiming = false; m.t = 0.2; }); }
            if (m.n <= 0 && !m.aiming && m.t > 0.9) set(m, 'idle'); return;
          case 'pC': m.regen = true; // kneel & heal; 3 hits on it (back crystal) break the channel -> long stagger
            if (Math.floor(m.t / 0.5) > Math.floor((m.t - dt) / 0.5)) { m.hp = Math.min(Math.floor(m.maxHp * (P2 ? 0.5 : 0.85)), m.hp + Math.round(m.maxHp * 0.01)); W.fx('heal', m.x, m.y - 30); }
            if (m.regenHits >= 3) { m.regen = false; set(m, 'stagger'); W.banner('재생 차단! 골렘이 휘청인다', 1.2); return; }
            if (m.t > 3) { m.regen = false; set(m, 'idle'); } return;
          case 'stagger': m.shake = 0.5; if (m.t > 2.2) { m.shake = 0; set(m, 'idle'); } return;
          case 'pD': m.rolling = m.sub === 'roll';
            if (m.sub === 'aim') { if (m.t > m.warn) { m.sub = 'roll'; m.t = 0; } return; }
            if (m.sub === 'roll') { W.touch(m, 18, 11); const sp = 240 * dt;
              if (!W.moveCol(m, Math.cos(m.aim) * sp, Math.sin(m.aim) * sp, m.r) || m.t > 1.6) { W.shake(2); W.fx('dust', m.x, m.y);
                if (--m.bounces > 0) { m.aim = ang(m, h.x, h.y); m.sub = 'aim'; m.t = 0; m.warn = lineTele(W, m, m.aim, 320, 0.45, 28); } else { m.rolling = false; set(m, 'idle'); } } }
            return;
          case 'pE': if (m.t > 2.6) set(m, 'idle'); return;
          case 'pF': if (m.t > 2.2) set(m, 'idle'); return;
          case 'ult': m.charge = Math.min(1, m.t / (m.ultW || 2.21)); if (m.t > (m.ultW || 2.21) + 0.6) { m.charge = 0; set(m, 'idle'); } return;
        }
      },
      onHit(m) { if (m.st === 'pC') m.regenHits = (m.regenHits || 0) + 1; },
      dmgMul(m) { return m.st === 'stagger' ? 2 : 1; } },

    // ------------------------------------------------ chapter 1 펠트 (art/mobs/felt): PixelLab walk / attack / shoot strips, drawn hi-res by world.js drawFeltHi.
    // 3 patterns each = 1 melee (circle in front; the strip's strike frame lands when the telegraph fills) + 2 eight-way shots (owner 10-22; was right/down/left/up,
    // line telegraphs first). Projectiles are drawn in code (world.js drawShot kinds). Spec + preview: art/mobs/felt/patterns.json, felt_mobs_*.mp4.
    c1_silmamul: felt({ name: '실마물', style: 'bind', col: '#9a9aa4', aff: { weak: ['slash'], resist: ['pierce'] }, hp: 50, h: 26, r: 7, sp: 22,
      melee: { range: 24, rad: 14, dmg: 5 },
      shots: [{ name: '실타래 3갈래', sp: 80, waves: [0], spread: [-.35, 0, .35], shot: { kind: 'threadball', r: 4, dmg: 4, life: 2.0, slow: 1.0, pull: 16 } }, // aimed at the hero; hit = bound (slowed) 1s and yanked 16px toward it, then it claws
        { name: '실 함정', trap: { r: 16, dmg: 4, slow: 1.0 } }], // circle under the hero, 0.8s warning
      anim: { src: 'assets/mobs_felt/c1_01_silmamul', F: 36, walk: { n: 8, ticks: [5,  5,  5,  5,  5,  5,  5,  5] }, attack: { n: 11, ticks: [6,  4,  4,  3,  3,  3,  3,  3,  3,  8,  4], hit: 8 }, shoot: { n: 7, ticks: [5,  5,  10,  5,  5,  5,  5], release: 2 } } }),
    c1_thread_puppet: felt({ name: '실 꼭두각시', style: 'duel', col: '#d2b98c', aff: { weak: ['slash'], resist: ['blunt'] }, hp: 55, h: 30, r: 6, sp: 20,
      melee: { range: 26, rad: 15, dmg: 6 },
      shots: [{ name: '가위날 투척', sp: 105, waves: [0], spread: [0], shot: { kind: 'blade', r: 4, dmg: 5, life: 1.6, ret: true } }, // aimed; flies out, comes back
        { name: '시침핀 3연사', sp: 135, waves: [0, 0.13, 0.27], spread: [0], shot: { kind: 'pin', r: 2, dmg: 3, life: 1.2 } }], // aimed burst
      anim: { src: 'assets/mobs_felt/c1_02_thread_puppet', F: 40, walk: { n: 8, ticks: [5,  5,  5,  5,  5,  5,  5,  5] }, attack: { n: 11, ticks: [6,  4,  4,  3,  3,  3,  3,  3,  3,  8,  4], hit: 8 }, shoot: { n: 12, ticks: [5,  5,  5,  5,  5,  10,  5,  5,  5,  5,  5,  5], release: 5 } } }),
    c1_needle_spider: felt({ name: '바늘 거미', style: 'skirm', col: '#5a4670', aff: { weak: ['blunt'], resist: ['pierce'] }, hp: 45, h: 22, r: 7, sp: 30,
      melee: { range: 20, rad: 12, dmg: 5 },
      shots: [{ name: '거미줄 탄', sp: 85, waves: [0], spread: [0], shot: { kind: 'web', r: 4, dmg: 3, life: 1.6, slow: 0.6, zone: true } }, // aimed; leaves a slowing web where it ends
        { name: '독침 3갈래 2파', sp: 128, waves: [0, 0.4], spread: [-.3, 0, .3], shot: { kind: 'venom', r: 2, dmg: 3, life: 1.2 } }],
      anim: { src: 'assets/mobs_felt/c1_03_needle_spider', F: 34, walk: { n: 8, ticks: [5,  5,  5,  5,  5,  5,  5,  5] }, attack: { n: 10, ticks: [6,  4,  4,  3,  3,  3,  3,  3,  8,  4], hit: 7 }, shoot: { n: 9, ticks: [5,  5,  5,  5,  10,  5,  5,  5,  5], release: 4, map: [0, 1, 2, 3, 3, 2, 8, 8, 8] } } }), // map: skip the strip's steep rear-up frames 4-7 (looked upside-down)
    c1_unrotting_hound: felt({ name: '썩지 않는 들개', style: 'lunge', col: '#80766a', aff: { weak: ['blunt'], resist: ['slash'] }, hp: 60, h: 24, r: 8, sp: 34,
      melee: { range: 28, rad: 15, dmg: 6 },
      shots: [{ name: '돌껍질 파편 3갈래 2파', sp: 120, waves: [0, 0.23], spread: [-.25, 0, .25], shot: { kind: 'stone', r: 3, dmg: 4, life: 1.3 } }], // aimed; the main move is the lunge
      anim: { src: 'assets/mobs_felt/c1_04_unrotting_hound', F: 36, walk: { n: 8, ticks: [5,  5,  5,  5,  5,  5,  5,  5] }, attack: { n: 11, ticks: [6,  4,  4,  3,  3,  3,  3,  3,  3,  8,  4], hit: 8 }, shoot: { n: 9, ticks: [5,  5,  5,  5,  10,  5,  5,  5,  5], release: 4 } } }),

    // ------------------------------------------------ areas 2-9 (owner 10-22 "만들어 놓은 몬스터 전부 인게임"): placed in maps/field02..field09
    a2_06_glow_worm: s47({ name: '반딧불 지렁이', area: 2, h: 30, ai: 'melee' }),
    a2_07_cave_mole: s47({ name: '동굴 두더지', area: 2, h: 31, ai: 'drop', fx: 'rock' }),
    a2_08_crystal_slime: s47({ name: '수정 슬라임', area: 2, h: 29, ai: 'shoot', fx: 'beam' }),
    a3_03_sand_viper: s47({ name: '모래 독사', area: 3, h: 38, ai: 'charge' }),
    a3_04_bald_vulture: s47({ name: '대머리 독수리', area: 3, h: 33, ai: 'charge', fly: true }),
    a3_05_desert_bandit: s47({ name: '사막 도적', area: 3, h: 40, ai: 'melee' }),
    a3_06_sand_spirit: s47({ name: '모래 정령', area: 3, h: 40, ai: 'aoe', fx: 'sand' }),
    a3_07_camel_tortoise: s47({ name: '낙타 거북', area: 3, h: 36, ai: 'charge' }),
    a3_08_antlion: s47({ name: '개미귀신', area: 3, h: 40, ai: 'drop', fx: 'sand' }),
    a4_02_scarab_swarm: s47({ name: '스카라베 떼', area: 4, h: 30, ai: 'charge' }),
    a4_03_anubis_guard: s47({ name: '아누비스 경비병', area: 4, h: 49, ai: 'melee' }),
    a4_04_cursed_jar: s47({ name: '저주 항아리', area: 4, h: 37, ai: 'aoe', fx: 'poison' }),
    a4_05_serpent_statue: s47({ name: '뱀 머리 석상', area: 4, h: 47, ai: 'shoot', fx: 'beam', sp: 0 }),
    a4_06_ghost_cat: s47({ name: '고양이 망령', area: 4, h: 39, ai: 'melee', fly: true }),
    a4_07_slab_golem: s47({ name: '함정 석판 골렘', area: 4, h: 45, ai: 'drop', fx: 'rock' }),
    a4_08_sand_skeleton_archer: s47({ name: '모래 해골 궁수', area: 4, h: 37, ai: 'shoot', fx: 'arrow' }),
    a5_02_jellyfish: s47({ name: '해파리', area: 5, h: 36, ai: 'aoe', fx: 'shock' }),
    a5_03_spiny_puffer: s47({ name: '가시 복어', area: 5, h: 28, ai: 'shoot', fx: 'spike', pat: 'ring' }),
    a5_04_shark_trooper: s47({ name: '상어 돌격병', area: 5, h: 40, ai: 'charge' }),
    a5_05_octopus_inker: s47({ name: '문어 먹물병', area: 5, h: 38, ai: 'shoot', fx: 'ink', pat: 'fan' }),
    a5_06_electric_eel: s47({ name: '전기 뱀장어', area: 5, h: 29, ai: 'shoot', fx: 'bolt' }),
    a5_07_anglerfish: s47({ name: '아귀', area: 5, h: 30, ai: 'melee' }),
    a5_08_hermit_crab: s47({ name: '소라게', area: 5, h: 30, ai: 'melee' }),
    a6_02_seagull: s47({ name: '갈매기', area: 6, h: 28, ai: 'charge', fly: true }),
    a6_03_pirate_skeleton: s47({ name: '해적 해골', area: 6, h: 40, ai: 'melee' }),
    a6_04_barnacle_golem: s47({ name: '따개비 골렘', area: 6, h: 42, ai: 'melee' }),
    a6_05_turtle_shieldbearer: s47({ name: '바다 거북 방패병', area: 6, h: 38, ai: 'melee' }),
    a6_06_wave_spirit: s47({ name: '파도 정령', area: 6, h: 33, ai: 'aoe', fx: 'wave' }),
    a6_07_starfish: s47({ name: '불가사리', area: 6, h: 26, ai: 'shoot', fx: 'spike', pat: 'ring' }),
    a6_08_pirate_parrot: s47({ name: '해적 앵무새', area: 6, h: 32, ai: 'shoot', fx: 'feather', pat: 'fan' }),
    a7_07_flame_hound: s47({ name: '화염 사냥개', area: 7, h: 34, ai: 'charge' }),
    a7_08_obsidian_archer: s47({ name: '흑요석 궁수', area: 7, h: 39, ai: 'shoot', fx: 'firearrow' }),
    a8_06_thundercloud_bird: s47({ name: '뇌운 새', area: 8, h: 38, ai: 'drop', fx: 'bolt', fly: true }),
    a8_07_ice_turtle: s47({ name: '얼음 거북', area: 8, h: 30, ai: 'charge' }),
    a8_08_storm_gargoyle: s47({ name: '폭풍 가고일', area: 8, h: 41, ai: 'drop', fx: 'bolt' }),
    a9_05_shadow_assassin: s47({ name: '그림자 암살자', area: 9, h: 37, ai: 'charge' }),
    a9_06_void_eye: s47({ name: '공허 눈알', area: 9, h: 36, ai: 'shoot', fx: 'beam' }),
    a9_07_gargoyle_statue: s47({ name: '가고일 석상', area: 9, h: 50, ai: 'melee' }),
    a9_08_cursed_doll: s47({ name: '저주 인형', area: 9, h: 41, ai: 'shoot', fx: 'orb', pat: 'fan' }),
  };
  // ------------------------------------------------ 1장 보스: 『실타래의 재단사』 아라크네 (owner 10-23 「제1던전까지」, 몬스터 교본 1부; 정본: 강철 실로 이동 봉인, 실 분신 기습)
  // 3 rules (CLAUDE.md 게임 핵심): every move aims at the hero with a warning that ends on one beat (just-dodge) -> a clear standing opening after it -> she never runs away
  // (walks in to ~60px, the pounce closes long gaps). Phase 2 (HP 50%): + 실 감옥 / 바늘 비, 3 clones, 5 threads. Body = PixelLab strips drawn by drawFeltHi (felt: true).
  const ARA = { rest: { chop: .35, bind: .7, clone: .6, pounce: 1.0, cage: .8, rain: .7, brood: .5, cocoon: .9, trap: .6, orb: .8, pull: .9, stitch: .8, ult: 1.2 }, name: { chop: '뼈 다리 칼끝 찍기', bind: '강철 실 봉인', clone: '실 분신 기습', pounce: '거미 덮치기', cage: '실 감옥', rain: '바늘 비', brood: '새끼 풀기', cocoon: '고치 비', trap: '실타래 덫', orb: '붉은 실타래 구체', pull: '붉은 실 당기기', stitch: '영혼 꿰매기', ult: '천 갈래 붉은 실' }, broodMax: 6, ceil: [[6, 9], [11, 7], [17, 7], [22, 9], [10.5, 12.5], [17.5, 12.5]] /* arachne_boss ceiling cocoons (3번방 hd.phase2) */ };
  function spinWebs(m, W) { const map = W.map, P = (map.decos || []).filter(d => d.spr === 'pillar'), L = []; // 붉은 베틀 실: threads strung between the room's pillars (and to the walls if few pillars)
    for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) { const a = P[i], b = P[j], dd = Math.hypot(a.x - b.x, a.y - b.y); if (dd > 40 && dd < 200) L.push({ x: a.x, y: a.y - 6, x2: b.x, y2: b.y - 6, dd }); }
    L.sort((p, q) => p.dd - q.dd); let ws = L.slice(0, 6); if (ws.length < 4) { const cx = map.pw / 2, cy = map.ph / 2; ws = ws.concat([0, 1, 2, 3].map(k => { const a = k * Math.PI / 4 + .3; return { x: cx + Math.cos(a) * 150, y: cy + Math.sin(a) * 100, x2: cx - Math.cos(a) * 150, y2: cy - Math.sin(a) * 100 }; })).slice(0, 6); }
    W.webs(ws.map(w => ({ x: w.x, y: w.y, x2: w.x2, y2: w.y2, cut: false }))); W.banner('붉은 실이 방 전체에 쳐진다 — 칼로 베어 길을 열어라', 1.6, true); }
  def.arachne = { name: '아라크네', title: '실타래의 재단사', boss: true, felt: true, style: 'boss', col: '#c8c2d0', aff: { weak: ['slash'], resist: ['pierce'] }, hp: 1500, h: 110, r: 30, kb: 0, sp: 26, dmgMul(m) { return m.st === 'rest' || m.anim === 'hurt' ? 1 : .45; }, // 팀장 10-24 플레이 점검: 연타만으로 20초 → 빈틈(rest)에 베야 제대로 들어간다
    // 그록판 (새 주인공 H128FIG 34의 3.2배 = F184·h110·r30, 10-25) (사장님 10-24 「아라크네도 이걸로」, handoff/claude/arachne_grok_v1): 그록 4면·엎드린 거미형 + PixelLab 걷기 8장·핵심 자세 4장. 사이 장은 그리지 않고
    // (그림 도구가 칼 빛줄기를 구워 넣음) 같은 장을 map 으로 붙잡고, 웅크림·늘임·흔들림은 drawFeltHi 코드가 맡는다. 2페이즈 = 엎드린 거미형(rage·ragewalk).
    anim: { src: 'assets/mobs_felt/c1_boss_arachne', F: 184, walk: { n: 8, ticks: [6, 6, 6, 6, 6, 6, 6, 6] }, attack: { n: 12, ticks: [6, 5, 5, 4, 4, 4, 9, 6, 8, 14, 6, 5], hit: 6, map: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0] }, // 뼈 다리 칼끝: 찍고 → 박힌 채 빈틈 → 뽑기
      pounce: { n: 13, ticks: [5, 5, 5, 5, 8, 4, 4, 4, 4, 4, 6, 6, 6], hit: 9, air: 5, map: [0, 0, 0, 0, 0, 1, 2, 2, 1, 3, 3, 3, 0] }, hurt: { n: 6, ticks: [2, 3, 4, 6, 4, 4], once: true, map: [1, 1, 1, 1, 0, 0] }, death: { n: 13, ticks: [6, 6, 6, 6, 5, 5, 4, 4, 20, 8, 8, 10, 40], map: [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2] },
      roar: { n: 10, ticks: [5, 5, 6, 6, 10, 40, 8, 8, 10, 10], release: 4, map: [0, 0, 0, 1, 1, 1, 1, 1, 0, 0] }, rage: { n: 4, ticks: [8, 8, 8, 8], loop: true, map: [0, 0, 1, 1] }, ragewalk: { n: 8, ticks: [4, 4, 4, 4, 4, 4, 4, 4], map: [0, 1, 2, 1, 0, 1, 2, 1] },
      prison: { n: 9, ticks: [5, 5, 6, 6, 12, 6, 6, 6, 6], release: 4, map: [0, 0, 0, 1, 1, 1, 1, 1, 0] }, rain: { n: 9, ticks: [5, 5, 6, 6, 12, 6, 6, 6, 6], release: 4, map: [0, 0, 0, 1, 1, 1, 1, 1, 0] }, shoot: { n: 9, ticks: [5, 5, 5, 5, 10, 5, 5, 5, 5], release: 4, map: [0, 0, 0, 1, 1, 1, 1, 0, 0] } },
    init(m) { m.phase = 1; m.st = 'intro'; m.t = 0; m.anim = 'walk'; },
    update(m, W, dt) { const h = W.hero, A = this.anim, P2 = m.phase === 2, d = W.dist(m, h); m.t += dt; m.at = (m.at || 0) + dt; m.cd = (m.cd ?? 1.2) - dt;
      const HP = p => Math.max(1, Math.round((h.maxHp || 50) * p)); if (P2) m.ultCd = (m.ultCd ?? 7) - dt; // 정본 7-0: a boss hit = 30~40 % of the hero's HP
      const look = () => { m.face = h.x >= m.x ? 1 : -1; }, rest = k => { set(m, 'rest'); m.restT = ARA.rest[k] + (m.dazeT > 0 ? .3 : 0); m.dazeT = 0; if (m.anim !== 'attack' && m.anim !== 'pounce') m.anim = m.phase === 2 ? 'rage' : 'walk'; m.moving = false; }; /* the chop's panting / the landing frames carry on into the opening */
      if (m.phase === 1 && m.hp <= m.maxHp / 2 && m.st !== 'phase') { m.phase = 2; set(m, 'phase'); m.invuln = true; startAnim(m, 'roar', A.roar, A.roar.release, A.roar.ticks.slice(0, 4).reduce((a, v) => a + v, 0) / 60);
        W.banner('「키아아아——!!」 재단사가 강철 실을 풀어 놓는다', 2.2); W.shake(6); W.fx('text', m.x, m.y - 70, { text: '!!', life: 1.4, color: '#ff4a3a' }); try { dispatchEvent(new CustomEvent('boss-phase', { detail: { kind: 'arachne', phase: 2, dur: 1.8 } })); } catch (e) { } /* 팀: UI·지도 담당이 받아 방을 어둡게 (roar, 1.8 s invulnerable) */ for (let i = 0; i < 12; i++) W.fx('text', m.x + Math.cos(i / 12 * TAU) * 34, m.y - 20 + Math.sin(i / 12 * TAU) * 20, { text: '✂', life: .7, color: '#d8d8e8' }); return; }
      switch (m.st) {
        case 'intro': m.moving = false; look(); if (m.t > Math.max(1.6, ((W.map && W.map.boss && W.map.boss.intro) || 0) + 1.6)) set(m, 'idle'); return; // waits out the camera intro + the boss_pre dialogue (shown 0.6s after it; the world is paused while it is open)
        case 'phase': m.moving = false; if (m.t > 1.8) { m.invuln = false; set(m, 'idle'); m.cd = .4; m.anim = 'walk'; spinWebs(m, W); } return;
        case 'ult': m.moving = false; if (m.t > (m.ultW || 2.4) + .6) rest('ult'); return;
        case 'rest': m.moving = false; m.hurtCd = (m.hurtCd || 0) - dt; if (m.hitT > .1 && m.hurtCd <= 0 && m.anim !== 'hurt') { m.anim = 'hurt'; m.at = 0; m.hurtCd = 1.2; } if (m.anim === 'hurt' && m.at > .4) m.anim = m.phase === 2 ? 'rage' : 'walk'; // flinch when slashed in the opening
          if (m.t > m.restT) set(m, 'idle'); return; // the opening: stands still, run in and slash
        case 'atk': if (m.at > m.dur && m.t > (m.hold || 0)) rest(m.last); return; // waiting for the strike / clones / volleys to finish
        case 'cage': { const c = m.cg; c.t += dt; m.moving = false; const k = Math.min(1, c.t / c.T), e = 1 - (1 - k) * (1 - k), R = c.R0 + (c.R1 - c.R0) * e, gw = Math.min(1.1, 34 / R), n = Math.ceil(TAU * R / 17);
          if (k < 1) for (let i = 0; i < n; i++) { const b = i * TAU / n, dg = Math.atan2(Math.sin(b - c.gap), Math.cos(b - c.gap)); if (Math.abs(dg) < gw / 2) continue; W.tempSolid(c.cx + Math.cos(b) * R, c.cy + Math.sin(b) * R * .8, 6, .05, 'threadwall'); } // the wall: thread posts, re-placed every frame a little further in
          if (k < 1) W.fx('tring', c.cx, c.cy, { R, gap: c.gap, gw, life: .035 }); // strands between the posts
          if (m.t > c.T + .1) rest('cage'); return; }
        case 'pounce': if (m.t < m.warn) { const P = A.pounce, f0 = P.ticks.slice(0, P.air).reduce((a, v) => a + v, 0) / P.ticks.slice(0, P.hit).reduce((a, v) => a + v, 0), k = Math.max(0, Math.min(1, (m.t / m.warn - f0) / (1 - f0))), e = k * k * (3 - 2 * k); /* crouch in place, travel only while airborne */ W.moveCol(m, m.sx + (m.tx - m.sx) * e - m.x, m.sy + (m.ty - m.sy) * e - m.y, m.r); }
          else { if (!m.landed) { m.landed = true; W.shake(3); W.fx('dust', m.x - 10, m.y); W.fx('dust', m.x + 10, m.y); } if (m.t > m.warn + .1) rest('pounce'); } return;
      }
      // idle: walk in, always facing her; never backs off
      const x0 = m.x, y0 = m.y; if (d > 62) toward(m, W, dt, this.sp * (P2 ? 1.2 : 1), h.x, h.y); look();
      if (W.mobs) for (const o of W.mobs) { if (o === m || o.dead) continue; const dx = m.x - o.x, dy = m.y - o.y, dd = Math.hypot(dx, dy) || .01, gap = m.r + o.r + 8; if (dd < gap) W.moveCol(m, dx / dd * Math.min(gap - dd, 60 * dt), dy / dd * Math.min(gap - dd, 60 * dt), m.r); } // no stacking
      const mv = Math.hypot(m.x - x0, m.y - y0); m.moving = mv > 1e-3; m.wph = (m.wph || 0) + mv / this.sp; m.wdir = 'side'; m.anim = P2 ? (m.moving ? 'ragewalk' : 'rage') : 'walk'; // phase 2: angry stance / fast walk (모션 v2)
      m.shedT = (m.shedT ?? 3) - dt; if (m.shedT <= 0) { m.shedT = P2 ? 4.5 : 7; // 사장님 10-24 「몸통에서 새끼 거미가 계속 나와서」: while she walks, the spool-belly drops one spiderling (2번방 numbers)
        if ((W.mobs || []).filter(o => !o.dead && o.mom === m).length < ARA.broodMax) { const bx = m.x - m.face * 20, by = m.y - 8; W.fx('fluff', bx, by, { life: .5, col: '#3a2a40', n: 7 }); if (W.sfx) W.sfx('deny', .6, .7);
          const c = W.spawn('c1_spiderling', bx, m.y + 4); if (c) { c.mom = m; c.noDrop = true; c.alerted = true; c.cd = .6; c.spawnT = .25; } } }
      if (P2 && W.webs && (!W.webs() || W.webs().every(w => w.cut))) { m.webT = (m.webT || 0) + dt; if (m.webT > 12) { m.webT = 0; spinWebs(m, W); } } // cut them all: she spins them again 12 s later
      if (P2 && m.ultCd <= 0 && m.st === 'idle' && W.ult) { m.ultCd = 26; m.last = 'ult'; W.banner(ARA.name.ult, .9, true); W.ult(m, 2.4, { text: '필살 — 천 갈래 붉은 실!  기둥 뒤로 숨거나, 조이는 순간 회피대시', pct: .4 }); startAnim(m, 'prison', A.prison, A.prison.release, 1.2); set(m, 'ult'); return; } // 정본 7-0 맵 전체 스킬
      if (!P2 && !m.ult1 && m.hp < m.maxHp * .75 && m.st === 'idle' && W.ult) { m.ult1 = true; m.last = 'ult'; W.banner(ARA.name.ult, .9, true); W.ult(m, 2.6, { text: '필살 — 천 갈래 붉은 실!  기둥 뒤로 숨거나, 조이는 순간 회피대시', pct: .35 }); startAnim(m, 'prison', A.prison, A.prison.release, 1.2); set(m, 'ult'); return; }
      if (m.cd > 0) return;
      const webOn = P2 && W.webs && W.webs() && W.webs().some(w => !w.cut);
      const O = [['trap', P2 ? .8 : 1.4], ['orb', d >= 60 ? 1.6 : .7]].concat(P2 ? [['pull', webOn ? 1.6 : 0], ['stitch', h.ccCd > 0 ? 0 : 1.2]] : []).concat([['chop', d < 70 ? 3 : 0], ['bind', d >= 50 ? 2 : .8], ['clone', 1.4], ['pounce', d >= 90 ? 3 : d >= 55 ? 1 : 0], ['brood', (W.mobs || []).filter(o => !o.dead && o.mom === m).length < ARA.broodMax - 1 ? (P2 ? 2 : 1.1) : 0]].concat(P2 ? [['cage', 1.2], ['rain', d >= 60 ? 1.3 : .6], ['cocoon', 1.4]] : []));
      for (const o of O) if (o[0] === m.last) o[1] = 0; // never the same move twice in a row
      let t = O.reduce((a, o) => a + o[1], 0) * Math.random(), k = O[0][0]; for (const o of O) { if (o[1] <= 0) continue; k = o[0]; t -= o[1]; if (t <= 0) break; }
      m.last = k; m.cd = (P2 ? 1.0 : 1.3) / agg(W); W.banner(ARA.name[k], .9, true); const a = ang(m, h.x, h.y); look(); m.hold = 0;
      if (k === 'trap') { const x = h.x, y = h.y; // 실타래 덫 (정본 1페이즈): a snare under the hero, one beat; it stays 4 s and slows by 30 %
        const z = W.hazard({ shape: 'circle', x, y, r: 22, warn: .7, act: .05, dmg: HP(.1), kind: 'web', owner: m, onEnd: () => { if (!m.dead && W.zone) W.zone({ x, y, r: 24, life: 4, k: .7 }); } });
        startAnim(m, 'shoot', A.shoot, A.shoot.release, z.warn); set(m, 'atk'); return; }
      if (k === 'orb') { const n = P2 ? 2 : 1; let tw = .65; for (let i = 0; i < n; i++) tw = lineTele(W, m, a + (i - (n - 1) / 2) * .5, 150, .65, 12); // 붉은 실타래 구체 (정본 7-0): aimed, slow, follows a little (outrun it or just-dodge it)
        W.after(tw, () => { if (m.dead) return; for (let i = 0; i < n; i++) W.shot({ x: m.x, y: m.y - 32, a: ang(m, W.hero.x, W.hero.y) + (i - (n - 1) / 2) * .5, sp: 72, r: 7, dmg: HP(.35), life: 3.2, home: 1.1, homeAfter: .3, kind: 'bloodorb', owner: m }); });
        startAnim(m, 'shoot', A.shoot, A.shoot.release, tw); set(m, 'atk'); m.hold = tw + .3; return; }
      if (k === 'pull') { const ws = (W.webs() || []).filter(w => !w.cut); let tw = .7; // 베틀 당기기 (정본 2페이즈 「멀리서 실로 끌어당김」): every web lights up, then snaps (on a web = hit), then the hero is yanked toward her
        for (const w of ws) { w.hot = true; tw = W.hazard({ shape: 'line', x: w.x, y: w.y, x2: w.x2, y2: w.y2, width: 10, warn: .7, act: .05, dmg: HP(.15), kind: 'web', owner: m }).warn; }
        W.after(tw, () => { for (const w of ws) w.hot = false; const H = W.hero; if (m.dead || H.roll || H.ccCd > 0 || W.tethered) return; const b = ang(H, m.x, m.y), L = Math.min(44, Math.max(0, W.dist(m, H) - 40));
          W.moveCol(H, Math.cos(b) * L, Math.sin(b) * L, 5); H.ccCd = 2.5; W.fx('text', H.x, H.y - 34, { text: '끌려간다!', life: .7, color: '#ff9a8a' }); m.intent = null; m.cd = .25; m.last = 'pull'; });
        startAnim(m, 'prison', A.prison, A.prison.release, tw); set(m, 'atk'); m.hold = tw + .1; return; }
      if (k === 'stitch') { const tw = lineTele(W, m, a, Math.min(220, d + 20), .7, 4); // 영혼 꿰매기: a thread to the hero, one beat -> tied to her 1.5 s (a dash cuts it; just-dodge it and it never lands)
        W.after(tw, () => { const H = W.hero; if (m.dead || H.ccCd > 0 || W.tethered) return; if (H.roll) { W.fx('text', H.x, H.y - 34, { text: '끊었다!', life: .6, color: '#ffd0a0' }); return; } W.tether({ mob: m, r: 70, life: 1.5 }); H.ccCd = 2.5; W.fx('text', H.x, H.y - 34, { text: '꿰매짐! 회피대시로 끊기', life: .8, color: '#ff9a8a' }); });
        startAnim(m, 'shoot', A.shoot, A.shoot.release, tw); set(m, 'atk'); return; }
      if (k === 'chop') { const reach = 48, z = W.hazard({ shape: 'circle', x: m.x + Math.cos(a) * reach, y: m.y + Math.sin(a) * reach * .8, r: 32, warn: .6, act: .05, dmg: HP(.32), kind: 'swipe', owner: m });
        if (P2) W.hazard({ shape: 'circle', x: m.x + Math.cos(a) * reach * 1.9, y: m.y + Math.sin(a) * reach * 1.5, r: 20, warn: z.warn + .35, act: .05, dmg: HP(.3), kind: 'swipe', owner: m }); // phase 2: a second, longer snip
        startAnim(m, 'attack', A.attack, A.attack.hit, z.warn + (P2 ? .35 : 0)); set(m, 'atk'); return; }
      if (k === 'bind') { const n = P2 ? 5 : 3, sp = .3, dirs = Array.from({ length: n }, (_, i) => a + (i - (n - 1) / 2) * sp); let tw = .6;
        for (const b of dirs) tw = lineTele(W, m, b, 170, .6, 6);
        W.after(tw, () => { if (m.dead) return; for (const b of dirs) W.shot({ x: m.x, y: m.y - 30, a: b, sp: 125, r: 4, dmg: HP(.12), life: 1.6, slow: 1.2, pull: 14, root: .6, kind: 'threadball', owner: m }); });
        startAnim(m, 'shoot', A.shoot, A.shoot.release, tw); set(m, 'atk'); return; }
      if (k === 'clone') { const n = P2 ? 3 : 2, gap = .45; let last = 0; // thread clones appear beside the hero and dash through it one after another; she stands channelling (the big opening)
        for (let i = 0; i < n; i++) { const ca = a + Math.PI / 2 * (i % 2 ? -1 : 1) + (i === 2 ? Math.PI / 2 : 0), R = 78, cx = h.x + Math.cos(ca) * R, cy = h.y + Math.sin(ca) * R * .8,
            da = Math.atan2(h.y - cy, h.x - cx), L = R * 2, x1 = cx + Math.cos(da) * L, y1 = cy + Math.sin(da) * L, w = .55 + i * gap;
          const z = W.hazard({ shape: 'line', x: cx, y: cy, x2: x1, y2: y1, width: 16, warn: w, act: .05, dmg: HP(.28), kind: 'swipe', owner: m });
          W.fx('tclone', cx, cy, { x1, y1, warn: z.warn, dash: .16, life: z.warn + .5, src: A.src, F: A.F * .85, face: x1 > cx ? 1 : -1 }); last = z.warn; }
        startAnim(m, 'shoot', A.shoot, A.shoot.release, .5); set(m, 'atk'); m.hold = last + .2; return; }
      if (k === 'pounce') { const L = Math.min(d, 120); m.sx = m.x; m.sy = m.y; m.tx = m.x + Math.cos(a) * L; m.ty = m.y + Math.sin(a) * L; m.landed = false; // lands on the marked spot
        const z = W.hazard({ shape: 'circle', x: m.tx, y: m.ty, r: 26, warn: .85, act: .05, dmg: HP(.38), kind: 'quake', owner: m }); m.warn = z.warn;
        startAnim(m, 'pounce', A.pounce, A.pounce.hit, z.warn); set(m, 'pounce'); return; }
      if (k === 'brood') { const n = P2 ? 3 : 2, z = W.hazard({ shape: 'circle', x: m.x - m.face * 14, y: m.y - 4, r: 20, warn: .6, act: 0, dmg: 0, kind: 'web' }); m.swell = z.warn; // 사장님 10-24 「몸통에서 새끼 거미가 계속 나와서 주인공을 공격」: the spool-belly swells (warning), then spiderlings burst out
        W.after(z.warn, () => { if (m.dead) return; W.shake(2); W.fx('fluff', m.x - m.face * 14, m.y - 18, { life: .7, col: '#3a2a40', n: 12 });
          for (let i = 0; i < n; i++) { if ((W.mobs || []).filter(o => !o.dead && o.mom === m).length >= ARA.broodMax) break; const b = rnd(0, TAU), c = W.spawn('c1_spiderling', m.x - m.face * 14 + Math.cos(b) * 14, m.y + Math.sin(b) * 10);
            if (c) { c.mom = m; c.noDrop = true; c.alerted = true; c.cd = .3 + i * .25; c.spawnT = .25; } } });
        startAnim(m, 'shoot', A.shoot, A.shoot.release, z.warn); set(m, 'atk'); return; }
      if (k === 'cage') { const R = W.map && W.map.pw ? Math.min(170, W.map.pw * .4) : 150; // 실 감옥 (팀장 10-24): a thread wall closes in from the room edge around the hero, one gap; escape through it before the centre crushes
        m.cg = { cx: h.x, cy: h.y, R0: R, R1: 24, t: 0, T: 2.6, gap: ang(m, h.x, h.y) + rnd(-1.2, 1.2) };
        const z = W.hazard({ shape: 'circle', x: h.x, y: h.y, r: 34, warn: m.cg.T, act: .05, dmg: HP(.4), kind: 'web', owner: m }); m.cg.T = z.warn;
        W.hazard({ shape: 'ring', x: h.x, y: h.y, r0: R - 4, r: R + 4, warn: .5, act: 0, dmg: 0, kind: 'web' }); // where the wall rises
        startAnim(m, 'prison', A.prison, A.prison.release, .6); set(m, 'cage'); return; }
      if (k === 'cocoon') { const n = 5; // 고치 비 (팀장 10-24): cocoons drop from the ceiling onto where the hero is, shadow first; landed ones stay as obstacles, some hatch
        for (let i = 0; i < n; i++) W.after(i * .45, () => { if (m.dead) return; const H = W.hero, x = H.x, y = H.y, T = (W.map && W.map.T) || 16, U = m.ccUsed || (m.ccUsed = {}); // 3번방: the room's 6 ceiling cocoons drop first, nearest to the hero (still aimed at the hero), then plain drops
          let ci = -1, bd = 1e9; ARA.ceil.forEach(([cx, cy], j) => { if (U[j]) return; const dd = Math.hypot(cx * T - x, cy * T - y); if (dd < bd) { bd = dd; ci = j; } });
          const from = ci >= 0 ? { fx: ARA.ceil[ci][0] * T, fy: ARA.ceil[ci][1] * T } : {}; if (ci >= 0) { U[ci] = 1; try { dispatchEvent(new CustomEvent('cocoon-drop', { detail: { i: ci } })); } catch (e) { } }
          const z = W.hazard({ shape: 'circle', x, y, r: 15, warn: .9, act: .05, dmg: HP(.3), kind: 'quake', owner: m }); W.fx('cocoonfall', x, y, Object.assign({ life: z.warn + .05, warn: z.warn }, from));
          W.after(z.warn, () => { if (m.dead) return; W.shake(2); W.fx('fluff', x, y - 4, { life: .5, col: '#e8e2d4', n: 8 }); W.tempSolid(x, y, 7, 4, 'cocoon');
            if (Math.random() < .3 && (W.mobs || []).filter(o => !o.dead && o.mom === m).length < ARA.broodMax) { const c = W.spawn('c1_spiderling', x, y + 8); if (c) { c.mom = m; c.noDrop = true; c.alerted = true; c.cd = .8; c.spawnT = .25; } } }); });
        startAnim(m, 'rain', A.rain, A.rain.release, .6); set(m, 'atk'); m.hold = .45 * 4 + .9 + .1; return; }
      if (k === 'rain') { let tw = .55; for (let w = 0; w < 3; w++) W.after(w * .5, () => { if (m.dead) return; const b = ang(m, W.hero.x, W.hero.y); // 3 aimed pin fans, each with its own line
          for (const s of [-.22, 0, .22]) lineTele(W, m, b + s, 150, tw, 5);
          W.after(tw, () => { if (m.dead) return; for (const s of [-.22, 0, .22]) W.shot({ x: m.x, y: m.y - 30, a: b + s, sp: 150, r: 2, dmg: HP(.1), life: 1.3, kind: 'pin', owner: m }); }); });
        startAnim(m, 'shoot', A.shoot, A.shoot.release, tw); set(m, 'atk'); m.hold = 1.0 + tw + .1; return; }
    },
    onDeath(m, W) { const D = this.anim.death; W.fx('strip', m.x, m.y, { src: this.anim.src + '_death', ticks: D.ticks, F: this.anim.F, face: m.face, life: D.ticks.reduce((a, v) => a + v, 0) / 60 + 1.6 }); W.fx('fluff', m.x, m.y - 30, { life: 1.2, col: '#c8c2d0', n: 26 }); W.fx('unravel', m.x, m.y - 30, { life: 2.2, n: 26 }); W.shake(5); try { dispatchEvent(new CustomEvent('boss-dead', { detail: { kind: 'arachne' } })); } catch (e) { } /* collapse: the threads holding her together unravel */ for (const o of W.mobs || []) if (!o.dead && o.mom === m) { o.dead = true; W.fx('fluff', o.x, o.y - 6, { life: .5, col: '#3a2a40', n: 6 }); } } }; // her brood dies with her
  // 새끼 거미 (아라크네 몸통에서 나옴): the needle spider's art at half size, dog-like straight bite (lunge role: short line, one beat), weak, lives 9 s
  { const B = def.c1_needle_spider, up = B.update; def.c1_spiderling = Object.assign({}, B, { name: '새끼 거미', summoned: true, style: 'lunge', tint: 'brightness(1.45) saturate(1.3)', hp: 8, h: 11, r: 4, sp: 44, col: '#3a2a40', anim: Object.assign({}, B.anim, { F: B.anim.F * .5 }), melee: Object.assign({}, B.melee, { range: 16, rad: 8, dmg: 3 }),
      shots: [], update(m, W, dt) { m.life = (m.life ?? 9) - dt; if (m.life <= 0 && m.st !== 'lunge') { m.dead = true; W.fx('fluff', m.x, m.y - 6, { life: .5, col: this.col, n: 6 }); return; } up.call(this, m, W, dt); } }); }
  // 1장 던전 챔피언 (owner 10-23 「챔피언 2종」, 크레딧 0: 펠트 그림을 키우고 색을 바꿈). champion = the base mob's role + one extra rule, red glow (always angry)
  // 챔피언 고유 기술 (팀장 10-24 「색만 바꾼 상태 → 생김새·기술 차이」, 크레딧 0): every 8 s, when free and in range, one move the base mob never does, then a clear opening.
  function champSig(m, W, dt, cd, range, start) { if (m.st === 'sig') { m.t += dt; m.at = (m.at || 0) + dt; m.moving = false; if (m.t > m.sigEnd) { m.st = 'rest'; m.t = 0; m.restT = .8; m.anim = 'walk'; } return true; }
    m.sigCd = (m.sigCd ?? cd * .6) - dt; const d = W.dist(m, W.hero); if (m.sigCd > 0 || d > range || !(m.st === 'idle' || m.st === 'rest') || m.dazeT > 0) return false;
    m.sigCd = cd; m.face = W.hero.x >= m.x ? 1 : -1; const end = start(m, W); m.st = 'sig'; m.t = 0; m.sigEnd = end; return true; }
  // 타격 재질 소리 (sfx_synth.js mat_*): 살 / 실 / 뼈·갑옷 / 껍질 — 챔피언은 아래에서 바탕 몹 것을 그대로 물려받음
  for (const [k, mt] of Object.entries({ mushroom: 'flesh', rabbit: 'flesh', boar: 'flesh', squirrel: 'flesh', slime: 'flesh', champ_boar: 'flesh', scarecrow: 'thread', c1_silmamul: 'thread', c1_thread_puppet: 'thread',
    golem: 'bone', wasp: 'shell', champ_wasp: 'shell', sprout: 'shell', c1_needle_spider: 'shell', c1_unrotting_hound: 'shell', arachne: 'shell' })) if (def[k]) def[k].sfxMat = mt;
  { const mk = (id, base, o, extra) => { const B = def[base]; def[id] = Object.assign({}, B, { champion: true, init(m) { m.rage = true; }, anim: Object.assign({}, B.anim, { F: B.anim.F * 1.3 }), melee: Object.assign({}, B.melee, { dmg: B.melee.dmg + 3, rad: B.melee.rad * 1.3 }) }, o);
      if (extra) { const up = B.update; def[id].update = function (m, W, dt) { if (extra.call(this, m, W, dt) === true) return; up.call(this, m, W, dt); }; } };
    mk('champ_c1_loom', 'c1_thread_puppet', { name: '베틀 파수꾼', title: '실 공방의 우두머리', hp: 280, h: 34, r: 10, tint: 'hue-rotate(-25deg) saturate(1.4) brightness(.9)', deco: 'strings' }, function (m, W, dt) { // 날실 가르기: three parallel warp threads aimed through the hero, one beat -> slip between them or dodge
      return champSig(m, W, dt, 8, 130, (m, W) => { const h = W.hero, a = ang(m, h.x, h.y), nx = -Math.sin(a), ny = Math.cos(a); let w = .7;
        for (const o of [-22, 0, 22]) { const x = m.x + nx * o, y = m.y + ny * o; w = W.hazard({ shape: 'line', x, y, x2: x + Math.cos(a) * 170, y2: y + Math.sin(a) * 170, width: 10, warn: .75, act: .05, dmg: 7, kind: 'swipe', owner: m }).warn; }
        W.fx('text', m.x, m.y - 50, { text: '날실 가르기', life: .9, color: '#ffb0a0' }); startAnim(m, 'attack', this.anim.attack, this.anim.attack.hit, w); return w + .25; }); }); // 꼭두각시 + always the 3-snip combo (rage)
    mk('champ_c1_cocoon', 'c1_needle_spider', { name: '고치 어미', title: '고치 저장고의 우두머리', hp: 210, h: 28, r: 11, tint: 'hue-rotate(40deg) saturate(1.3)', deco: 'sac' }, function (m, W, dt) {
      if (champSig(m, W, dt, 9, 120, (m, W) => { const h = W.hero; // 거미줄 그물: a web ring closes around the hero (the middle is safe, the ring binds) -> stay in or dodge out on the beat
        const z = W.hazard({ shape: 'ring', x: h.x, y: h.y, r0: 16, r: 44, warn: .85, act: .05, dmg: 4, slow: 1.2, kind: 'web', owner: m }); W.fx('text', m.x, m.y - 44, { text: '거미줄 그물', life: .9, color: '#e8e0d0' });
        startAnim(m, 'shoot', this.anim.shoot, this.anim.shoot.release, z.warn); return z.warn + .2; })) return true; m.hopCd = 99; // the mother does not hop away when hit (stays to be fought; 팀장 10-24 fight ran > 6 min) // 소환 role: a marked cocoon bursts into a spiderling (max 2)
      m.sumT = (m.sumT ?? 4) - dt; if (m.sumT > 0 || W.dist(m, W.hero) > 170) return; m.sumT = 9;
      if ((W.mobs || []).filter(o => !o.dead && o.mom === m).length >= 2) return;
      const a = rnd(0, TAU), x = m.x + Math.cos(a) * 36, y = m.y + Math.sin(a) * 26; W.hazard({ shape: 'circle', x, y, r: 9, warn: .8, act: 0, dmg: 0, kind: 'web' });
      W.after(.8, () => { if (m.dead) return; W.fx('fluff', x, y - 6, { life: .6, col: '#e8e0d0', n: 10 }); const c = W.spawn('c1_spiderling', x, y); if (c) { c.mom = m; c.noDrop = true; c.alerted = true; c.spawnT = .25; } }); }); } // babies, not full spiders: weak, 9 s (팀장 10-24: the fight ran > 6 min)
  // 잿빛 들판 챔피언 (팀장 10-24 「들판이 2~3분으로 짧다」, 크레딧 0): 들개 우두머리 = 들개 역할 + 울부짖음(12초마다 주변 들개를 깨워 곧바로 돌진, 무리가 적으면 1마리 부름, 최대 2)
  { const B = def.c1_unrotting_hound, up = B.update; def.champ_c1_hound = Object.assign({}, B, { champion: true, name: '썩지 않는 사냥개 우두머리', title: '잿빛 들판의 우두머리', hp: 180, deco: 'eyes', h: 30, r: 11, tint: 'saturate(.6) brightness(1.25) contrast(1.15)',
      init(m) { m.rage = true; }, anim: Object.assign({}, B.anim, { F: B.anim.F * 1.3 }), melee: Object.assign({}, B.melee, { dmg: B.melee.dmg + 3, rad: B.melee.rad * 1.3 }),
      update(m, W, dt) { // 사냥 3연 돌진 (고유): after each lunge recovers it lunges again, up to 3 in a row, then a long pant (1.4 s opening)
        if (m.st === 'lunge' && m.sub === 'rec' && m.t > .25 && (m.chain || 0) < 2 && W.dist(m, W.hero) < 130) { m.chain = (m.chain || 0) + 1; const h = W.hero; m.aim = ang(m, h.x, h.y); m.face = Math.cos(m.aim) >= 0 ? 1 : -1; // the chain stays one attack (one lunge state)
          m.sub = 'aim'; m.t = 0; m.second = true; m.warn = lineTele(W, m, m.aim, 230 * .38, .6, m.r * 2 + 12); startAnim(m, 'attack', this.anim.attack, this.anim.attack.hit, m.warn); W.fx('dust', m.x, m.y); }
        if (m.pst === 'lunge' && m.st === 'idle') { if ((m.chain || 0) >= 2) { m.st = 'rest'; m.t = 0; m.restT = 1.4; m.cd = Math.max(m.cd || 0, 1.5); W.fx('text', m.x, m.y - 40, { text: '헉헉', life: .9, color: '#cfc4b0' }); } m.chain = 0; } // the chain is one pick in pickIntent's history (never 3 lunges in a row)
        m.pst = m.st;
        m.howlT = (m.howlT ?? 5) - dt; const d = W.dist(m, W.hero);
        if (m.howlT <= 0 && d < 170 && (m.st === 'idle' || m.st === 'rest')) { m.howlT = 12; W.fx('text', m.x, m.y - 44, { text: '아우우——!', life: 1.1, color: '#e8d8c0' }); W.shake(2); if (W.sfx) W.sfx('tele', .8, .6);
          const pack = (W.mobs || []).filter(o => !o.dead && o !== m && o.kind === 'c1_unrotting_hound' && W.dist(o, m) < 220); for (const o of pack) { o.alerted = true; o.cd = Math.min(o.cd || 0, .3); o.intent = 'lunge'; }
          if (pack.length < 2 && (W.mobs || []).filter(o => !o.dead && o.mom === m).length < 2) { const a = rnd(0, TAU), x = m.x + Math.cos(a) * 60, y = m.y + Math.sin(a) * 45; W.hazard({ shape: 'circle', x, y, r: 10, warn: .7, act: 0, dmg: 0, kind: 'web' });
            W.after(.7, () => { if (m.dead) return; W.fx('dust', x, y); const c = W.spawn('c1_unrotting_hound', x, y); if (c) { c.mom = m; c.noDrop = true; c.alerted = true; c.spawnT = .25; } }); } }
        up.call(this, m, W, dt); } }); }
  // 1장 던전 placeholders (owner 10-23 「제1던전까지」) until the monster room's real champions / boss land under the same ids: bigger copies of the felt mobs
  for (const [id, base, name, title, hp, boss] of [['champ_c1_loom', 'c1_thread_puppet', '베틀 파수꾼', '실 공방의 우두머리', 260], ['champ_c1_cocoon', 'c1_needle_spider', '고치 어미', '고치 저장고의 우두머리', 240], ['champ_c1_hound', 'c1_unrotting_hound', '썩지 않는 사냥개 우두머리', '잿빛 들판의 우두머리', 180],
    ['arachne', 'c1_silmamul', '아라크네', '실타래의 재단사', 900, 1]]) if (!def[id]) { const B = def[base];
    def[id] = Object.assign({}, B, { name, title, hp, champion: !boss, boss: !!boss, stub: true, h: Math.round(B.h * (boss ? 1.8 : 1.4)), r: Math.round(B.r * 1.4), anim: Object.assign({}, B.anim, { F: B.anim.F * (boss ? 1.8 : 1.4) }), melee: Object.assign({}, B.melee, { dmg: B.melee.dmg + 3 }) }); }
  for (const k in def) if (def[k].s47 === undefined && def[k].ai) def[k].s47 = k;
  // area-1 regulars keep their AI and get the room-3 hi-res strips (body height x1.3)
  for (const [k, id] of Object.entries({ mushroom: 'field_mushroom', rabbit: 'field_horned_rabbit', wasp: 'field_wasp', boar: 'field_boar', scarecrow: 'field_scarecrow', slime: 'a1_06_forest_slime', squirrel: 'a1_07_acorn_squirrel', sprout: 'a1_08_spirit_sprout' })) { def[k].s47 = id; def[k].h = Math.round(def[k].h * 1.3); }
  for (const k in def) { const D = def[k]; if (!D.felt || D.style === 'boss') continue; // 8-way shots (owner 10-22 "4방향 -> 8방향"), bigger, faster attacks
    if (!D.champion && !D.elite && !D.boss) D.hp = Math.round(D.hp * .7); /* souls pace: a regular mob falls in 3~4 slashes = one stamina bar (교본 1-8) */ D.anim.F *= FELT_SC; D.h = Math.round(D.h * FELT_SC); D.r = Math.round(D.r * 1.2); D.melee.range *= 1.15; D.melee.rad *= 1.15; D.rec = FELT_REC; }
  window.WorldMobs = { def };
})();
