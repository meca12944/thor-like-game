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
  const FELT_SPD = 1.4; // owner 10-22 "걷는속도 빠르게": move x1.4, walk cycle 5 ticks/frame (was 7)
  const FELT_SC = 1.35, FELT_CD = .6, FELT_REC = .7; // owner 10-22 "크기 더 키우고 공속 더빠르게": body x1.35 (reach x1.15), cooldowns x0.6, recovery after the hit x0.7 (telegraphs unchanged)
  function felt(o) {
    return Object.assign({ felt: true, update(m, W, dt) {
      const h = W.hero, A = this.anim; m.t += dt; m.at = (m.at || 0) + dt; m.cd = (m.cd ?? rnd(1, 2)) - dt; const d = W.dist(m, h);
      if (m.st === 'melee' || m.st === 'shoot') { if (m.at > m.dur) { set(m, 'idle'); m.anim = 'walk'; } return; }
      m.anim = 'walk'; const x0 = m.x, y0 = m.y;
      if (m.cd <= 0 && !m.intent) m.intent = Math.random() < 1 / 3 ? 'melee' : 'shoot'; // each cooldown: rush in (1/3) or shoot from mid range (2/3)
      const want = m.intent === 'melee' ? this.melee.range : m.intent === 'shoot' ? 70 : 52; // hold ~52px between attacks
      if (d < 200) { if (d > want + 6) toward(m, W, dt, this.sp * FELT_SPD, h.x, h.y); else if (d < want - 14) toward(m, W, dt, -this.sp * FELT_SPD * .7, h.x, h.y); else m.face = h.x > m.x ? 1 : -1; }
      else wander(m, W, dt, this.sp * FELT_SPD * .5);
      const vx = m.x - x0, vy = m.y - y0; m.moving = Math.abs(vx) + Math.abs(vy) > 1e-3;
      if (m.moving) { const k = ((Math.round(Math.atan2(vy, vx) / (Math.PI / 4)) % 8) + 8) % 8; m.wdir = ['side', 'se', 's', 'se', 'side', 'ne', 'n', 'ne'][k]; if (Math.abs(vx) > 1e-4) m.face = vx > 0 ? 1 : -1; } // 8-way walk strips (↙↖ = mirrored ↘↗)
      if (m.cd > 0 || d > 150) return;
      if (m.intent === 'melee' && d < this.melee.range + 12 && tok(m, W)) { m.intent = null; const a = ang(m, h.x, h.y), reach = this.melee.range * .6; m.face = Math.cos(a) >= 0 ? 1 : -1;
        const z = W.hazard({ shape: 'circle', x: m.x + Math.cos(a) * reach, y: m.y + Math.sin(a) * reach * .8, r: this.melee.rad, warn: 0.55, act: 0.05, dmg: this.melee.dmg, kind: 'swipe', owner: m });
        startAnim(m, 'attack', A.attack, A.attack.hit, z.warn); set(m, 'melee'); m.cd = 1.6 * FELT_CD / agg(W); return; }
      if (m.intent === 'shoot' && d > 40 && tok(m, W, true)) { m.intent = null; m.pi = ((m.pi ?? Math.floor(Math.random() * 2)) + 1) % 2; const p = this.shots[m.pi]; m.face = h.x > m.x ? 1 : -1;
        let tw = 0.6; for (let i = 0; i < 8; i++) tw = lineTele(W, m, i * Math.PI / 4, Math.min(150, p.sp * 1.4), 0.6, 6);
        startAnim(m, 'shoot', A.shoot, A.shoot.release, tw); set(m, 'shoot'); m.cd = 2.4 * FELT_CD / agg(W);
        for (const w of p.waves) W.after(tw + w, () => { if (m.dead) return; for (let i = 0; i < 8; i++) W.shot(Object.assign({ x: m.x, y: m.y - this.h * .45, a: i * Math.PI / 4, sp: p.sp, owner: m }, p.shot)); }); }
    } }, o);
  }

  const def = {
    // ------------------------------------------------ area 1 regulars (WORLD_PLAN.md / MONSTERS.md)
    mushroom: { name: '독버섯', aff: { weak: ['slash'], resist: ['blunt'] }, hp: 50, spr: 'mushroom', h: 20, r: 6, mat: 'm_spore',
      update(m, W, dt) { m.t += dt; m.cd = (m.cd || 0) - dt;
        if (m.st === 'puff') { if (m.t > 1.0) set(m, 'idle'); return; }
        wander(m, W, dt, 10);
        if (m.cd <= 0 && (near(m, W, 30) || m.hitT > 0) && tok(m, W)) { set(m, 'puff'); m.cd = 2.4 / agg(W); // spore burst: ring warns 0.7s, then a short poison cloud
          W.hazard({ shape: 'circle', x: m.x, y: m.y - 4, r: 30, warn: 0.6, act: 0.9, dmg: 5, kind: 'poison', owner: m }); }
      } },
    rabbit: { name: '뿔토끼', aff: { weak: ['slash'], resist: [] }, hp: 40, spr: 'rabbit', h: 22, r: 5, mat: 'm_rabbit_horn',
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
    wasp: { name: '말벌', aff: { weak: ['pierce'], resist: ['blunt'] }, hp: 50, spr: 'wasp', h: 20, r: 5, fly: true, hover: 10, mat: 'm_wasp_sting',
      update(m, W, dt) { const h = W.hero; m.t += dt; m.cd = (m.cd ?? rnd(1, 2.5)) - dt;
        if (m.st === 'aim') { if (m.t > m.warn) { W.shot({ x: m.x, y: m.y, a: m.aim, sp: 130, r: 3, dmg: 5, kind: 'sting', owner: m }); set(m, 'retreat'); } return; }
        if (m.st === 'retreat') { const a = ang(m, h.x, h.y) + Math.PI; W.moveCol(m, Math.cos(a) * 50 * dt, Math.sin(a) * 50 * dt, m.r, true); if (m.t > 0.6) set(m, 'idle'); return; }
        const d = W.dist(m, h);
        if (d > 75) toward(m, W, dt, 50, h.x, h.y); else if (d < 50) toward(m, W, dt, -30, h.x, h.y);
        else { m.orb = (m.orb || 0) + dt; W.moveCol(m, Math.cos(m.orb) * 20 * dt, Math.sin(m.orb * 1.3) * 14 * dt, m.r, true); }
        if (m.cd <= 0 && d < 143 && tok(m, W, true)) { m.cd = 1.92 / agg(W); m.aim = ang(m, h.x, h.y - 8); set(m, 'aim'); m.warn = lineTele(W, m, m.aim, 120, 0.51, 6); }
      } },
    boar: { name: '멧돼지', aff: { weak: ['pierce'], resist: ['blunt'] }, hp: 60, spr: 'boar', h: 20, r: 7, mat: 'm_boar_hide',
      update(m, W, dt) { const h = W.hero; m.t += dt; const rage = m.hp <= m.maxHp / 2; m.tint = rage ? 'rage' : null;
        if (m.st === 'aim') { m.shake = 1; if (m.t > m.warn) { set(m, 'charge'); m.shake = 0; } return; }
        if (m.st === 'charge') { const sp = (rage ? 250 : 160) * dt; W.touch(m, 9, 6); m.face = Math.cos(m.aim) > 0 ? 1 : -1;
          if (!W.moveCol(m, Math.cos(m.aim) * sp, Math.sin(m.aim) * sp, m.r) || m.t > 0.9) { set(m, 'rest'); W.fx('dust', m.x, m.y); } return; }
        if (m.st === 'rest') { if (m.t > (rage ? 0.6 : 1.1)) set(m, 'idle'); return; }
        wander(m, W, dt, rage ? 40 : 20);
        if (W.dist(m, h) < 130 && m.t > 1 && tok(m, W)) { m.aim = ang(m, h.x, h.y); set(m, 'aim'); m.warn = lineTele(W, m, m.aim, 150, rage ? 0.45 : 0.55, 14); }
      } },
    scarecrow: { name: '호박 허수아비', aff: { weak: ['slash'], resist: ['pierce'] }, hp: 55, spr: 'scarecrow', h: 30, r: 6, mat: 'm_pumpkin_vine',
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
    slime: { name: '숲 슬라임', aff: { weak: ['blunt'], resist: ['pierce'] }, hp: 40, spr: 'slime', sprAtk: 'slime_atk', h: 18, r: 6, mat: 'm_forest_gel',
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
    squirrel: { name: '도토리 다람쥐', aff: { weak: ['blunt'], resist: [] }, hp: 40, spr: 'squirrel', sprAtk: 'squirrel_atk', h: 22, r: 5, mat: 'm_acorn_shell',
      update(m, W, dt) { const h = W.hero; m.t += dt; m.cd = (m.cd ?? rnd(1, 2)) - dt; const d = W.dist(m, h);
        if (m.st === 'throw') { m.atk = m.t < 0.4; if (m.t > 0.9) set(m, 'idle'); return; }
        if (d < 55) toward(m, W, dt, -35, h.x, h.y); else if (d > 100) toward(m, W, dt, 31, h.x, h.y); else wander(m, W, dt, 10);
        if (m.cd <= 0 && d < 156 && tok(m, W, true)) { m.cd = 2.08 / agg(W); set(m, 'throw'); m.face = h.x > m.x ? 1 : -1; // lobbed acorn: target marker 0.85s
          W.hazard({ shape: 'circle', x: h.x, y: h.y, r: 10, warn: 0.72, act: 0.05, dmg: 5, kind: 'acorn', from: [m.x, m.y - 12], owner: m }); }
      } },
    sprout: { name: '나무 정령 새싹', aff: { weak: ['slash'], resist: ['pierce'] }, hp: 60, spr: 'sprout', sprAtk: 'sprout_atk', h: 22, r: 5, mat: 'm_sprout_wood',
      update(m, W, dt) { const h = W.hero; m.t += dt; m.cd = (m.cd ?? rnd(1.5, 3)) - dt; const d = W.dist(m, h);
        if (m.st === 'cast') { m.atk = true; if (m.t > 1.1) { set(m, 'idle'); m.atk = false; } return; }
        if (d > 50 && d < 195) toward(m, W, dt, 18, h.x, h.y); else wander(m, W, dt, 8);
        if (m.cd <= 0 && d < 169 && tok(m, W, true)) { m.cd = 2.56 / agg(W); set(m, 'cast'); // root bind: circle under the hero 0.9s, roots slow on hit
          W.hazard({ shape: 'circle', x: h.x, y: h.y, r: 14, warn: 0.77, act: 0.05, dmg: 5, kind: 'root', slow: 1.2, owner: m }); }
      } },

    // ------------------------------------------------ area 1 champions (field)
    champ_boar: { name: '돌엄니', aff: { weak: ['pierce'], resist: ['blunt'] }, title: '거대 왕멧돼지', champion: true, hp: 320, spr: 'champ_boar', h: 38, r: 12, mat: 'm_boar_hide', matN: 3,
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
    champ_wasp: { name: '여왕 말벌', aff: { weak: ['pierce'], resist: ['blunt'] }, title: '숲의 여왕', champion: true, hp: 320, spr: 'champ_wasp', h: 40, r: 10, fly: true, hover: 14, mat: 'm_wasp_sting', matN: 3,
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
    c1_silmamul: felt({ name: '실마물', aff: { weak: ['slash'], resist: ['pierce'] }, hp: 50, h: 26, r: 7, sp: 22,
      melee: { range: 24, rad: 14, dmg: 5 },
      shots: [{ name: '바늘 사방 사격', sp: 150, waves: [0], shot: { kind: 'needle', r: 2, dmg: 4, life: 1.1 } },
        { name: '실타래 탄', sp: 70, waves: [0], shot: { kind: 'threadball', r: 4, dmg: 4, life: 2.2, slow: 1.0 } }], // hit = bound (slowed) 1s
      anim: { src: 'assets/mobs_felt/c1_01_silmamul', F: 36, walk: { n: 8, ticks: [5,  5,  5,  5,  5,  5,  5,  5] }, attack: { n: 11, ticks: [6,  4,  4,  3,  3,  3,  3,  3,  3,  8,  4], hit: 8 }, shoot: { n: 7, ticks: [5,  5,  10,  5,  5,  5,  5], release: 2 } } }),
    c1_thread_puppet: felt({ name: '실 꼭두각시', aff: { weak: ['slash'], resist: ['blunt'] }, hp: 55, h: 30, r: 6, sp: 20,
      melee: { range: 26, rad: 15, dmg: 6 },
      shots: [{ name: '가위날 투척', sp: 105, waves: [0], shot: { kind: 'blade', r: 4, dmg: 5, life: 1.6, ret: true } }, // flies out, comes back
        { name: '시침핀 3연사', sp: 135, waves: [0, 0.13, 0.27], shot: { kind: 'pin', r: 2, dmg: 3, life: 1.2 } }],
      anim: { src: 'assets/mobs_felt/c1_02_thread_puppet', F: 40, walk: { n: 8, ticks: [5,  5,  5,  5,  5,  5,  5,  5] }, attack: { n: 11, ticks: [6,  4,  4,  3,  3,  3,  3,  3,  3,  8,  4], hit: 8 }, shoot: { n: 12, ticks: [5,  5,  5,  5,  5,  10,  5,  5,  5,  5,  5,  5], release: 5 } } }),
    c1_needle_spider: felt({ name: '바늘 거미', aff: { weak: ['blunt'], resist: ['pierce'] }, hp: 45, h: 22, r: 7, sp: 30,
      melee: { range: 20, rad: 12, dmg: 5 },
      shots: [{ name: '거미줄 탄', sp: 85, waves: [0], shot: { kind: 'web', r: 4, dmg: 3, life: 1.6, slow: 0.6, zone: true } }, // leaves a slowing web where it ends
        { name: '독침 2파', sp: 128, waves: [0, 0.4], shot: { kind: 'venom', r: 2, dmg: 3, life: 1.2 } }],
      anim: { src: 'assets/mobs_felt/c1_03_needle_spider', F: 34, walk: { n: 8, ticks: [5,  5,  5,  5,  5,  5,  5,  5] }, attack: { n: 10, ticks: [6,  4,  4,  3,  3,  3,  3,  3,  8,  4], hit: 7 }, shoot: { n: 9, ticks: [5,  5,  5,  5,  10,  5,  5,  5,  5], release: 4 } } }),
    c1_unrotting_hound: felt({ name: '썩지 않는 들개', aff: { weak: ['blunt'], resist: ['slash'] }, hp: 60, h: 24, r: 8, sp: 34,
      melee: { range: 28, rad: 15, dmg: 6 },
      shots: [{ name: '독기 구체', sp: 80, waves: [0], shot: { kind: 'orb', r: 5, dmg: 5, life: 2.0 } },
        { name: '돌껍질 파편 2파', sp: 120, waves: [0, 0.23], shot: { kind: 'stone', r: 3, dmg: 4, life: 1.3 } }],
      anim: { src: 'assets/mobs_felt/c1_04_unrotting_hound', F: 36, walk: { n: 8, ticks: [5,  5,  5,  5,  5,  5,  5,  5] }, attack: { n: 11, ticks: [6,  4,  4,  3,  3,  3,  3,  3,  3,  8,  4], hit: 8 }, shoot: { n: 9, ticks: [5,  5,  5,  5,  10,  5,  5,  5,  5], release: 4 } } }),
  };
  for (const k in def) { const D = def[k]; if (!D.felt) continue; // 8-way shots (owner 10-22 "4방향 -> 8방향"), bigger, faster attacks
    D.anim.F *= FELT_SC; D.h = Math.round(D.h * FELT_SC); D.r = Math.round(D.r * 1.2); D.melee.range *= 1.15; D.melee.rad *= 1.15; D.rec = FELT_REC; }
  window.WorldMobs = { def };
})();
