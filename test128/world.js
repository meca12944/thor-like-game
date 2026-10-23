/* =====================================================================
 *  world.js — outside world for the town demo: scene manager + world map + field + dungeon + boss.
 *  Self-contained module (loaded after the town script). It only talks to the town through window.__game:
 *    hero position / hp, setManual() to pause the town, ctl.KEYMAP for the player's key bindings,
 *    invAdd()/potions for loot. The town template only needs the <script src="world.js"> include.
 *  Scenes:  town -> (exit gate) -> title card -> world map -> field01 -> dungeon01_b1 -> dungeon01_b2 -> boss01 -> back
 *  Data:    maps/*.json (format: WORLD.md), assets/world/world_atlas.json (tools/world_assets.py)
 *  Scale:   DQ6-like. Logical screen LW x LH (384x216) integer-scaled; 16px tiles; hero ~16x27.
 *           WORLD_ZOOM scales the overworld (tiles 16*WORLD_ZOOM px, smaller hero, wider view).
 *  Combat:  no guard — Shift (or the 회피 key) = dodge roll with i-frames; every enemy attack is telegraphed.
 *  Test API: window.__world (see bottom).
 * ===================================================================== */
(function () {
  'use strict';
  // ---------------- tweakables ----------------
  const WORLD_ZOOM = 0.5;          // overworld scale vs field (0.5 => 8px tiles, ~13px hero). Try 0.75 / 1.
  const LW = 384, LH = 216;        // logical screen (DQ6 SFC-like 16:9), integer-scaled to the window
  const HERO_SPEED = 82, WORLD_SPEED = 46;
  const RUN = { mul: 1.9, startMul: 2.3, startT: 0.17, skidT: 0.2, dblTap: 0.25, cadence: .9 }; // run: 1.9x walk, no MP/stamina; anim cadence = speed x .9 (no foot sliding)
  // swing hitbox = forward sector (tile 16): sword 29px = 1.8 tiles, 150 deg; other weapons scale with the town range table (__game.swingRange)
  const SWING = { range: 29, arc: 150, arc3: 100, r3: 1.15 }; // hit 3 = finishing slash: 100 deg forward, reach x1.15 (longer swing timing ATK3 kept)
  const ROLL = { dur: 0.22, iframe: 0.18, speed: 250, cd: 0.4 }; const DG = () => (window.__game && window.__game.DODGE) || null; // dodge dash config (ANIM.dodge); ROLL kept as fallback
  const EASE = { outCubic: p => 1 - (1 - p) ** 3, outQuad: p => 1 - (1 - p) ** 2, linear: p => p };
  function rollDur() { const D = DG(); return D ? D.durTicks / 60 : ROLL.dur; }
  // [balance] levels.json roll.base: 0.18s i-frames in a 0.22s roll, 0.40s cooldown (speed raised so the roll still covers ~40px)
  // [balance] numeric HP (hero 50), hero combo 10/10/14, difficulty multipliers from the town template (window.__game.diff = levels.json difficulty.levels[])
  const ATK_DMG = [10, 10, 14];
  const POT = { heal: 30, cd: 4.0, heartPct: 5, heartDrop: 0.04 };
  const DIFF0 = { id: 'normal', enemy_hp: 1, enemy_dmg: 1, telegraph: 1, aggression: 1, tokens: 2, potion_cap: 5, iframe_bonus: 0, ult_cap: 0.9, telegraph_floor: { attack: 0.45, aoe: 0.6, charge_line: 0.45, ult: 2.2 } };
  const DIFF = () => { const g = window.__game; return (g && g.diff) || DIFF0; };
  const iframe = () => (DG() && DG().iframeTicks ? DG().iframeTicks / 60 : ROLL.iframe) + (DIFF().iframe_bonus || 0); // same invincible window as the town (DODGE.iframeTicks, owner 10-23)
  // telegraph = authored (normal) value x difficulty, never below the difficulty floor (charge lines / ground AoE / attacks / 필살기)
  function teleScale(h) { if (!(h.warn > 0)) return; const d = DIFF(), F = d.telegraph_floor || DIFF0.telegraph_floor;
    const fl = h.kind === 'ult' ? F.ult : h.shape === 'line' ? F.charge_line : (h.dmg ? F.aoe : F.attack); h.warn = Math.max(fl, h.warn * d.telegraph); }
  // attack tokens: at most N melee + 1 ranged enemies may start an attack at once; a token is handed back ~1.2s later + 0.6s cooldown
  function token(m, ranged) { if (m.D.boss || m.D.champion) return true; const now = S.t, d = DIFF(); S.tokens = (S.tokens || []).filter(t => t.until > now && !t.m.dead);
    if (S.tokens.some(t => t.m === m)) return true; const lim = ranged ? 1 : (d.tokens || 2); if (S.tokens.filter(t => !!t.r === !!ranged).length >= lim) return false;
    S.tokens.push({ m, r: !!ranged, until: now + 1.2 + 0.6 }); return true; }
  const ATK = { dur: 0.26, a0: 0.05, a1: 0.16, chain: 0.32, reach: 15, r: 13 };
  const ATK3 = Object.assign({}, ATK, { dur: 0.38, a0: 0.07, a1: 0.24 }); // hit 3: longer active window + follow-through
  const atkT = i => i >= 3 ? atkTS(i) : i === 2 ? ATK3 : ATK;
  // dash attack (run + attack, i 3) / charge attack lv1 / lv2 (hold attack, i 4 / 5): same data as the town (__game.ANIM.special), town px x .3, ticks / 60
  const SPW_DEF = { dash: { dur: 26, a0: 4, a1: 12, lunge: 90, rangeMul: 1, arc: 100, dmgMul: 1.3, cool: .3 }, charge: { t1: .6, t2: 1.2, moveMul: .4,
    lv1: { dur: 34, a0: 6, a1: 14, lunge: 24, rangeMul: 1.15, arc: 100, dmgMul: 2, cool: .25 }, lv2: { dur: 40, a0: 6, a1: 16, lunge: 30, rangeMul: 1.4, arc: 100, dmgMul: 3, cool: .3, wave: { speed: 560, range: 260, rad: 28, dmgMul: 1 } } } };
  function spW() { const g = window.__game; return (g && g.ANIM && g.ANIM.special && g.ANIM.special.dash) ? g.ANIM.special : SPW_DEF; }
  function spOf(i) { const C = spW(); return i === 3 ? C.dash : i === 4 ? C.charge.lv1 : C.charge.lv2; }
  function atkTS(i) { const h = spOf(i); return { dur: h.dur / 60, a0: h.a0 / 60, a1: h.a1 / 60 }; }
  function arcW(i) { return i >= 3 ? (spOf(i).arc || 100) : i === 2 ? SWING.arc3 : SWING.arc; }
  function sfx(k, v, r) { try { if (window.SFX2 && SFX2.has(k)) return SFX2.play(k, v, r); const g = window.__game; if (g && g.SFX) g.SFX.play(k, v, r); } catch (e) { } } // SFX2 = code-made sounds (sfx_synth.js), else the town's recorded ones
  const FADE = 0.35, CARD = 2.1;
  const Q = new URLSearchParams(location.search);
  const LS = 'thor.world.v1';
  const TAU = Math.PI * 2;
  const NAV = () => window.WorldNav || null; // world_nav.js: minimap, map screen, objectives, A* route, quests (optional module)

  // ---------------- DOM ----------------
  const cv = document.createElement('canvas'); cv.id = 'wc';
  cv.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:40;display:none;image-rendering:pixelated;background:transparent';
  const ctx = cv.getContext('2d');
  const low = document.createElement('canvas'); low.width = LW; low.height = LH; const lx = low.getContext('2d');
  const gateHint = document.createElement('div');
  gateHint.style.cssText = 'position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:35;padding:3px 12px;background:rgba(12,18,44,.7);color:#ffe08a;font:bold 13px sans-serif;border:2px solid #e2c27a;border-radius:3px;pointer-events:none;display:none';
  gateHint.textContent = '▼ 마을 밖으로 (바람길)';
  const st0 = document.createElement('style');
  st0.textContent = 'body.wscene #ui,body.wscene #dlg,body.wscene #win{visibility:hidden}body.wscene #ov:not(.open){visibility:hidden}';
  function mountDom() { document.body.appendChild(cv); document.body.appendChild(gateHint); document.head.appendChild(st0); }
  if (document.body) mountDom(); else addEventListener('DOMContentLoaded', mountDom);

  // ---------------- persistent world state ----------------
  let SAVE = { flags: {}, chests: {}, keys: {}, opened: {}, levers: {}, visited: {}, explored: {}, waystones: {}, landmarks: {}, quests: {}, pin: null, dest: null };
  try { Object.assign(SAVE, JSON.parse(localStorage.getItem(LS) || '{}')); } catch (e) {}
  if (Q.has('worldreset')) SAVE = { flags: {}, chests: {}, keys: {}, opened: {}, levers: {}, visited: {}, explored: {}, waystones: {}, landmarks: {}, quests: {}, pin: null, dest: null };
  for (const k of ['explored', 'waystones', 'landmarks', 'quests']) SAVE[k] = SAVE[k] || {};
  const save = () => { try { localStorage.setItem(LS, JSON.stringify(SAVE)); } catch (e) {} };

  // ---------------- assets ----------------
  const IMG = {}; let ATLAS = null, TILESETS = null; const MAPS = {};
  const loadImg = (k, src) => new Promise((res, rej) => { const i = new Image(); i.onload = () => { IMG[k] = i; res(); }; i.onerror = () => rej(new Error('load ' + src)); i.src = src; });
  const getJSON = u => fetch(u).then(r => { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); });
  function loadMap(id) { return MAPS[id] ? Promise.resolve(MAPS[id]) : getJSON('maps/' + id + '.json').then(j => j.bg ? loadBg(j) : j).then(j => (MAPS[id] = buildMap(j))); }
  // painted-background maps (town B): j.bg = image drawn over the whole map instead of tiles; ground rows only carry collision
  const BGIMG = {};
  function loadBg(j) { return new Promise(res => { const im = new Image(); im.onload = () => { BGIMG[j.bg] = im; res(j); }; im.onerror = () => res(j); im.src = j.bg; }); }
  const NPCIMG = {};
  function npcImg(id) { if (!NPCIMG[id]) { const im = new Image(); im.src = 'assets/npcs/' + id + '.png'; NPCIMG[id] = im; } return NPCIMG[id]; }
  const PORIMG = {};
  function porImg(id) { if (!PORIMG[id]) { const im = new Image(); im.src = 'assets/portraits/' + id + '.png'; PORIMG[id] = im; } return PORIMG[id]; }
  const ready = getJSON('assets/world/world_atlas.json').then(a => { ATLAS = a;
    return Promise.all([loadImg('field', 'assets/' + a.sheets.field.src), loadImg('dungeon', 'assets/' + a.sheets.dungeon.src), loadImg('spr', 'assets/' + a.sprites.src),
      getJSON('maps/tilesets.json').then(t => TILESETS = t)]); }).then(() => loadMap('world'));

  // sprite helpers ------------------------------------------------------------
  const tintCache = {};
  function sprCanvas(name, mode) { // mode: 'white' flash | 'rage' red | 'gray'
    const key = name + '|' + mode; if (tintCache[key]) return tintCache[key];
    const r = ATLAS.sprites.rects[name]; if (!r) return null;
    const c = document.createElement('canvas'); c.width = r[2]; c.height = r[3]; const g = c.getContext('2d');
    g.drawImage(IMG.spr, r[0], r[1], r[2], r[3], 0, 0, r[2], r[3]);
    if (mode === 'white') { g.globalCompositeOperation = 'source-atop'; g.fillStyle = '#fff'; g.fillRect(0, 0, r[2], r[3]); }
    if (mode === 'dodge') { const AI = (DG() && DG().afterimage) || {}; g.globalCompositeOperation = 'source-atop'; g.globalAlpha = AI.tintMix ?? .45; g.fillStyle = AI.tint || '#bff4ff'; g.fillRect(0, 0, r[2], r[3]); g.globalAlpha = 1; }
    if (mode === 'rage') { g.globalCompositeOperation = 'source-atop'; g.fillStyle = 'rgba(255,40,20,.35)'; g.fillRect(0, 0, r[2], r[3]); }
    if (mode === 'gray') { const d = g.getImageData(0, 0, r[2], r[3]); for (let i = 0; i < d.data.length; i += 4) { const v = (d.data[i] * .3 + d.data[i + 1] * .59 + d.data[i + 2] * .11) * .7; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; } g.putImageData(d, 0, 0); }
    return (tintCache[key] = c);
  }
  function drawSpr(g, name, x, y, o = {}) { // (x,y) = bottom-centre (feet)
    const r = ATLAS.sprites.rects[name]; if (!r) return;
    const s = o.scale || 1, w = r[2] * s, h = r[3] * s * (o.sy || 1);
    g.save(); g.globalAlpha = o.alpha ?? 1; g.translate(Math.round(x), Math.round(y));
    if (o.rot) g.rotate(o.rot);
    if (o.flip) g.scale(-1, 1);
    const src = o.mode ? sprCanvas(name, o.mode) : null;
    if (src) g.drawImage(src, -w / 2, -h, w, h); else g.drawImage(IMG.spr, r[0], r[1], r[2], r[3], Math.round(-w / 2), Math.round(-h), w, h);
    g.restore();
  }
  function tileXY(sheet, name) { const S_ = ATLAS.sheets[sheet]; const k = S_.index[name]; if (k === undefined) return null; return [(k % S_.cols) * 16, Math.floor(k / S_.cols) * 16]; }

  // ---------------- map building ----------------
  function legendOf(m, ch) { let L = m.legend[ch]; if (L === undefined) L = m.tileset === 'dungeon' ? 'wall' : 'grass'; return typeof L === 'string' ? { ground: L } : L; }
  function buildMap(j) {
    const T = j.type === 'world' ? Math.round(16 * WORLD_ZOOM) : (j.tile || 16);
    const m = Object.assign({}, j, { T, pw: j.w * T, ph: j.h * T, solidG: new Uint8Array(j.w * j.h), cells: [], decos: [], objs: [] });
    const solidChars = new Set(j.solid || []);
    const ts = (TILESETS && TILESETS[j.tileset || 'field']) || {};
    for (let y = 0; y < j.h; y++) for (let x = 0; x < j.w; x++) {
      const ch = (j.ground[y] || '')[x] || '#'; const L = legendOf(j, ch);
      m.cells.push({ ch, g: L.ground, deco: L.deco, obj: L.obj });
      let solid = solidChars.has(ch); if (L.solid !== undefined) solid = L.solid;
      if (ts.solidTiles && ts.solidTiles.includes(L.ground)) solid = true;
      m.solidG[y * j.w + x] = solid ? 1 : 0;
      if (L.deco) m.decos.push({ x: (x + .5) * T, y: (y + 1) * T - 1, spr: L.deco, tx: x, ty: y, solid });
      if (L.obj) m.objs.push(mkObj(m, L.obj, x, y));
    }
    for (const o of (j.objects || [])) if (!['spawn', 'champion'].includes(o.type)) m.objs.push(Object.assign({}, o, { tx: o.x, ty: o.y, x: (o.x + .5) * T, y: (o.y + .5) * T }));
    for (const o of m.objs) if (['chest', 'sign', 'heal', 'waystone', 'npc', 'door'].includes(o.type) && !o.walk) m.solidG[Math.floor(o.ty) * j.w + Math.floor(o.tx)] = 1;
    return m;
  }
  function mkObj(m, type, x, y) {
    const o = { type, tx: x, ty: y, x: (x + .5) * m.T, y: (y + .5) * m.T, key: m.id + ':' + x + ',' + y };
    const id = x + ',' + y;
    if (type === 'chest') Object.assign(o, (m.chests || {})[id] || { id: m.id + '_' + id, loot: [['potion', 1]] });
    if (type === 'key') o.keyId = (m.keys || {})[id] || m.id + '_key';
    return o;
  }
  // pre-render the static ground to a canvas (with soft autotile edges)
  function renderGround(m) {
    const c = document.createElement('canvas'); c.width = m.pw; c.height = m.ph; const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
    if (m.bg && BGIMG[m.bg]) { g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high'; g.drawImage(BGIMG[m.bg], 0, 0, m.pw, m.ph); return c; }
    const T = m.T, W = m.w, H = m.h, sheet = m.tileset || 'field';
    const at = (x, y) => (x < 0 || y < 0 || x >= W || y >= H) ? null : m.cells[y * W + x];
    const hash = (x, y) => ((x * 73856093) ^ (y * 19349663)) >>> 0;
    const ALIAS = (TILESETS && TILESETS.alias) || {};
    function put(name, x, y) { let n = name; if (!tileXY(sheet, n) && !tileXY('field', n) && ALIAS[n]) n = ALIAS[n];
      const sh = tileXY(sheet, n) ? sheet : 'field'; const p = tileXY(sh, n); if (!p) return false;
      g.drawImage(IMG[sh], p[0], p[1], 16, 16, x * T, y * T, T, T); return true; }
    const VAR = (TILESETS && TILESETS.variants) || {};
    const groundName = (cell, x, y) => { const v = VAR[cell.g]; return v ? v[hash(x, y) % v.length] : cell.g; };
    const isG = (x, y, set) => { const c2 = at(x, y); return c2 ? set.includes(c2.g) : true; };
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const cell = at(x, y); let n = groundName(cell, x, y);
      if (sheet === 'dungeon' && cell.g.startsWith('wall')) { // 3/4 walls: face where the floor is below, dark top elsewhere
        const below = at(x, y + 1); const face = below && !below.g.startsWith('wall');
        n = face ? (cell.obj === 'torch' ? 'wall' : ['wall', 'wall', 'wall_moss', 'wall_vine', 'wall_crack', 'wall_moss2'][hash(x, y) % 6]) : 'walltop_dark';
        put(n, x, y);
        if (!face) { g.fillStyle = 'rgba(8,10,14,.55)'; g.fillRect(x * T, y * T, T, T);
          const edge = (dx, dy) => { const c2 = at(x + dx, y + dy); return c2 && !c2.g.startsWith('wall'); };
          g.fillStyle = '#5d6b4c'; if (edge(-1, 0)) g.fillRect(x * T, y * T, 2, T); if (edge(1, 0)) g.fillRect(x * T + T - 2, y * T, 2, T); if (edge(0, -1)) g.fillRect(x * T, y * T, T, 2); }
        else { g.fillStyle = 'rgba(0,0,0,.35)'; g.fillRect(x * T, y * T + T - 2, T, 2); }
        continue; }
      const soft = (TILESETS && TILESETS.soft || {})[cell.g]; // soft edges: neighbour ground first, then this tile through a rounded clip
      if (soft) {
        const grp = soft.group; const N_ = isG(x, y - 1, grp), Sd = isG(x, y + 1, grp), Wl = isG(x - 1, y, grp), Er = isG(x + 1, y, grp);
        put(soft.under, x, y);
        const rr = T * 0.45; const r4 = [(!N_ && !Wl) ? rr : 0, (!N_ && !Er) ? rr : 0, (!Sd && !Er) ? rr : 0, (!Sd && !Wl) ? rr : 0];
        g.save(); g.beginPath(); g.roundRect(x * T, y * T, T, T, r4); g.clip(); put(n, x, y);
        if (soft.rim) { g.fillStyle = soft.rim; const bw = Math.max(1, Math.round(T / 8));
          if (!N_) g.fillRect(x * T, y * T, T, bw); if (!Sd) g.fillRect(x * T, y * T + T - bw, T, bw); if (!Wl) g.fillRect(x * T, y * T, bw, T); if (!Er) g.fillRect(x * T + T - bw, y * T, bw, T);
          if (r4.some(v => v)) { g.strokeStyle = soft.rim; g.lineWidth = bw * 2; g.beginPath(); g.roundRect(x * T, y * T, T, T, r4); g.stroke(); } }
        g.restore();
        if (m.type === 'world') worldDeco(g, m, cell, x, y, hash(x, y));
        continue; }
      if (cell.g === 'cliff') { const up = at(x, y - 1); put(up && up.g === 'cliff' ? 'cliff_rock' : 'cliff', x, y); continue; }
      if (cell.g === 'bridge_h') { put((TILESETS && TILESETS.bridgeUnder) || 'water', x, y); put('bridge_h', x, y); continue; }
      if (!put(n, x, y)) { g.fillStyle = '#f0f'; g.fillRect(x * T, y * T, T, T); }
      if (m.type === 'world') worldDeco(g, m, cell, x, y, hash(x, y));
    }
    if (sheet === 'dungeon') for (const o of m.objs) if (['stairs_up', 'stairs_down', 'pit'].includes(o.type)) put(o.type, o.tx, o.ty);
    return c;
  }
  // world-map decorations (mini forests / mountains / hills) at WORLD_ZOOM scale
  function worldDeco(g, m, cell, x, y, h) {
    const T = m.T, px = x * T, py = y * T;
    if (cell.g === 'forest') { for (let i = 0; i < 2; i++) { const ox = (i ? T * .5 : T * .05) + ((h >> (i * 3)) & 1), oy = i ? T * .0 : T * .3;
        g.fillStyle = '#123c16'; g.beginPath(); g.moveTo(px + ox + T * .22, py + oy); g.lineTo(px + ox + T * .48, py + oy + T * .62); g.lineTo(px + ox - T * .04, py + oy + T * .62); g.fill();
        g.fillStyle = '#2f7d2a'; g.beginPath(); g.moveTo(px + ox + T * .22, py + oy + 1); g.lineTo(px + ox + T * .38, py + oy + T * .5); g.lineTo(px + ox + T * .06, py + oy + T * .5); g.fill();
        g.fillStyle = '#5a3a1c'; g.fillRect(px + ox + T * .17, py + oy + T * .62, Math.max(1, T * .12), T * .18); } }
    if (cell.g === 'mountain' || cell.g === 'snowpeak') { const snow = cell.g === 'snowpeak';
      g.fillStyle = '#2a2622'; g.beginPath(); g.moveTo(px - 1, py + T); g.lineTo(px + T / 2, py - T * .35); g.lineTo(px + T + 1, py + T); g.fill();
      g.fillStyle = snow ? '#8d9ab0' : '#7d6f5c'; g.beginPath(); g.moveTo(px + .5, py + T - .5); g.lineTo(px + T / 2, py - T * .2); g.lineTo(px + T - .5, py + T - .5); g.fill();
      g.fillStyle = snow ? '#5f6b80' : '#5a4e40'; g.beginPath(); g.moveTo(px + T / 2, py - T * .2); g.lineTo(px + T - .5, py + T - .5); g.lineTo(px + T * .55, py + T - .5); g.fill();
      g.fillStyle = '#f2f6ff'; g.beginPath(); g.moveTo(px + T / 2, py - T * .2); g.lineTo(px + T * .68, py + T * .2); g.lineTo(px + T * .32, py + T * .2); g.fill(); }
    if (cell.g === 'hill') { g.fillStyle = 'rgba(30,40,10,.45)'; g.beginPath(); g.ellipse(px + T / 2, py + T * .7, T * .45, T * .28, 0, Math.PI, 0); g.fill();
      g.fillStyle = 'rgba(200,220,120,.25)'; g.fillRect(px + T * .3, py + T * .45, T * .25, 1); }
  }

  // ---------------- runtime state ----------------
  const S = { scene: 'town', map: null, mobs: [], hazards: [], shots: [], fx: [], timers: [], temp: [], banner: null, dialog: null, msg: null, ult: null,
    cam: [0, 0], camI: [0, 0], shake: 0, t: 0, trans: null, townPos: null, pause: false, deadT: 0, engaged: null, bgm: null, bgmCard: null, bossRef: null, jingleT: 0, view: { k: 1, ox: 0, oy: 0 } };
  const hero = { x: 0, y: 0, face: 'down', hp: 50, maxHp: 50, inv: 0, walkT: 0, moving: false, atk: null, combo: 0, comboT: 0, roll: null, rollCd: 0, slowT: 0, safe: [0, 0], dodgeT: 0 };
  let manual = false;

  // ---------------- input (captured only while a world scene is active; town keys untouched) ----------------
  const held = new Set(), queue = [];
  const PASS = new Set(['KeyB', 'KeyN', 'Minus', 'Equal', 'NumpadSubtract', 'NumpadAdd', 'F12']); // BGM keys keep working
  const DEFKEYS = { up: ['ArrowUp', 'KeyW'], down: ['ArrowDown', 'KeyS'], left: ['ArrowLeft', 'KeyA'], right: ['ArrowRight', 'KeyD'], attack: ['KeyJ', 'KeyZ'], dash: ['KeyK', 'KeyX'],
    interact: ['KeyL', 'KeyC', 'Enter'], potion: ['KeyE'], ult: ['KeyR'], menu: ['Escape'] };
  function KM() { const g = window.__game; return (g && g.ctl && g.ctl.KEYMAP) || DEFKEYS; }
  function codesOf(a) { const l = (KM()[a] || DEFKEYS[a] || []).slice(); if (a === 'dash') l.push('ShiftLeft', 'ShiftRight'); if (a === 'menu' && !l.includes('Escape')) l.push('Escape'); return l; }
  const isHeld = a => codesOf(a).some(c => held.has(c));
  const takePress = a => { const cs = codesOf(a); const i = queue.findIndex(c => cs.includes(c)); if (i < 0) return false; queue.splice(i, 1); return true; };
  const active = () => (S.scene !== 'town' || !!S.trans) && !(window.__game && window.__game.ui); // a DOM UI (shop over a town-B door) takes the keys
  addEventListener('keydown', e => { if (!active() || PASS.has(e.code)) return; e.preventDefault(); e.stopPropagation();
    if (!e.repeat) { queue.push(e.code); for (const d of ['up', 'down', 'left', 'right']) if (codesOf(d).includes(e.code)) dirTap(d); } held.add(e.code); if (queue.length > 8) queue.shift(); }, true);
  // double-tap a direction (press->press <= .25s) -> dash start + run while held (same rule as the town; Esc '달리기 기본' = always run)
  const lastTap = {}; function dirTap(d) { const now = performance.now() / 1000; if (now - (lastTap[d] ?? -9) <= RUN.dblTap) hero.runReq = true; lastTap[d] = now; }
  addEventListener('keyup', e => { held.delete(e.code); }, true);
  addEventListener('blur', () => held.clear());

  // ---------------- helpers ----------------
  const M = () => S.map;
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  function solidAt(px, py) { const m = M(); if (!m) return true; const x = Math.floor(px / m.T), y = Math.floor(py / m.T);
    if (x < 0 || y < 0 || x >= m.w || y >= m.h) return true; if (m.solidG[y * m.w + x]) return true;
    for (const t of S.temp) if (Math.hypot(px - t.x, py - t.y) < t.r) return true; return false; }
  function blocked(x, y, r) { return solidAt(x, y) || solidAt(x - r, y) || solidAt(x + r, y) || solidAt(x, y - r * .6) || solidAt(x, y + r * .4); }
  function moveCol(e, dx, dy, r, fly) {
    const m = M(); let ok = true;
    const bl = fly ? (x, y) => x < 6 || y < 10 || x > m.pw - 6 || y > m.ph - 4 : (x, y) => blocked(x, y, r);
    if (dx) { if (!bl(e.x + dx, e.y)) e.x += dx; else ok = false; }
    if (dy) { if (!bl(e.x, e.y + dy)) e.y += dy; else ok = false; }
    return ok;
  }
  function msg(text, t = 2.2) { S.msg = { text, t }; }
  function banner(text, t = 1.6, small) { S.banner = { text, t, max: t, small }; }
  function after(t, f) { S.timers.push({ t, f }); }
  function shake(v) { const g = window.__game; if (g && g.shakeScale) v = g.shakeScale(v); S.shake = Math.max(S.shake, v); } // [hitfeel] capped ≤3px + '화면 흔들림' option (game.template.html)
  function addFx(type, x, y, o = {}) { S.fx.push(Object.assign({ type, x, y, t: 0, life: o.life || 0.5 }, o)); }
  const NAMES = { potion: '물약', heart_piece: '하트 조각', spirit_drop: '정령의 이슬', m_hardwood: '단단한 목재', m_a1_shared: '숲의 정수', bomb: '폭탄', m_spore: '독 포자',
    m_rabbit_horn: '토끼 뿔', m_wasp_sting: '말벌 독침', m_boar_hide: '멧돼지 가죽', m_pumpkin_vine: '호박 덩굴', m_forest_gel: '숲 젤리', m_acorn_shell: '도토리 껍질', m_sprout_wood: '새싹 목재' };
  const itemName = id => NAMES[id] || id;
  function giveLoot(list) { const g = window.__game; const names = [];
    for (const [id, n] of list) { if (id === 'gold') { if (g && g.addGold && g.addGold(n)) names.push('금화 ' + n); continue; } try { if (id === 'potion' && g) g.potions = (g.potions || 0) + n; else if (g && g.invAdd) g.invAdd(id, n); } catch (e) {}
      names.push(itemName(id) + (n > 1 ? ' ×' + n : '')); }
    return names.join(', '); }

  // ---------------- hazards / shots: the only things that can hurt the hero ----------------
  function hazard(h) { h.t = 0; h.hit = false; teleScale(h); S.hazards.push(h); if (h.warn > 0) sfx('tele', .5, h.dmg ? 1 : 1.3); return h; }
  function inHaz(h, x, y) {
    if (h.shape === 'circle') return Math.hypot(x - h.x, (y - h.y) * 1.15) < h.r + 3;
    if (h.shape === 'ring') { const d = Math.hypot(x - h.x, (y - h.y) * 1.15); return d > h.r0 - 3 && d < h.r + 3; }
    if (h.shape === 'line') { const vx = h.x2 - h.x, vy = h.y2 - h.y, L = Math.hypot(vx, vy) || 1, u = ((x - h.x) * vx + (y - h.y) * vy) / (L * L);
      if (u < 0 || u > 1) return false; return Math.hypot(h.x + vx * u - x, h.y + vy * u - y) < h.width / 2 + 3; }
    if (h.shape === 'all') return !ultSafe(h, x, y);
    return false;
  }
  function hurt(dmg, src, raw) {
    if (S.scene === 'world' || hero.hp <= 0 || S.deadT > 0) return false;
    if (W_API.god || S.ultFx) return false; // invulnerable during the 필살기
    if (hero.roll && hero.roll.t < iframe()) { const just = !hero.roll.just && hero.roll.t < (DIFF().perfect_ticks || 7) / 60; // 저스트 회피 = 회피대시 시작 perfect_ticks 안 (보통 7틱) -> 필살기 게이지 크게
      if (just) { const ow = src && (src.owner || (src.D ? src : null)); if (ow && ow.D && ow.D.felt) { ow.dazeT = .6; addFx('text', ow.x, ow.y - (ow.D.h || 20) - 8, { text: '?', life: .6, color: '#cfe6ff' }); } // the attacker is caught off guard
        hero.roll.just = true; ultAdd('gainPerfect', 1); addFx('text', hero.x, hero.y - 30, { text: '저스트 회피!', life: .7, color: '#ffe08a' }); } else if (hero.dodgeT <= 0) addFx('text', hero.x, hero.y - 30, { text: '회피!', life: .6, color: '#9ff' }); if (just) sfx('dodge', .6); hero.dodgeT = .3; return false; }
    if (hero.inv > 0) return false;
    if (!raw) dmg = Math.max(1, Math.round(dmg * DIFF().enemy_dmg)); hero.hp = Math.max(0, hero.hp - dmg); sfx('hurt', .9); hero.inv = 1.0; hero.charge = null; hero.holdOk = false; shake(2); ultAdd('gainHit', 1);
    if (src && src.x !== undefined) { const a = Math.atan2(hero.y - src.y, hero.x - src.x); moveCol(hero, Math.cos(a) * 8, Math.sin(a) * 8, 5); }
    addFx('text', hero.x, hero.y - 30, { text: '-' + dmg, life: .7, color: '#ff6a5a' });
    syncTownHp();
    if (hero.hp <= 0) die();
    return true;
  }
  function ultAdd(k, n) { const g = window.__game; if (g && g.addUlt && g.ULT_CFG) g.addUlt(g.ULT_CFG[k] * n); } // 필살기 게이지: 싸우는 동안 저절로 · 피격 1번마다 · 저스트 회피 (template ULT_CFG)
  function touch(m, r, dmg) { if (Math.hypot(hero.x - m.x, hero.y - m.y) < r + 5) hurt(dmg, m); }
  function shot(s) { sfx('shot', .45); s.t = 0; s.vx = Math.cos(s.a) * s.sp; s.vy = Math.sin(s.a) * s.sp; s.life = s.life || 2; S.shots.push(s); }
  function tempSolid(x, y, r, life, kind) { S.temp.push({ x, y, r, life, kind }); const d = Math.hypot(hero.x - x, hero.y - y); if (d < r + 5) { const a = Math.atan2(hero.y - y, hero.x - x) || 0, need = r + 6 - d; moveCol(hero, Math.cos(a) * need, Math.sin(a) * need, 5);
      if (Math.hypot(hero.x - x, hero.y - y) < r + 5) S.temp.pop(); } } // push out, never through a wall; if there is no room the crystal just doesn't form
  function randomFloor() { const m = M(); for (let i = 0; i < 60; i++) { const x = (2 + Math.random() * (m.w - 4)) * m.T, y = (2 + Math.random() * (m.h - 4)) * m.T; if (!blocked(x, y, 6)) return [x, y]; } return [hero.x, hero.y]; }
  function breakDecoNear(x, y, r) { const m = M(); for (const d of m.decos) if (!d.broken && ['boulder', 'rocks', 'bush', 'stump', 'fence'].includes(d.spr) && Math.hypot(d.x - x, d.y - 6 - y) < r + 6) {
      d.broken = true; m.solidG[d.ty * m.w + d.tx] = 0; addFx('debris', d.x, d.y - 6, { life: .6 }); shake(2); } }
  // 필살기 safe zone: in a pillar's shadow as seen from the boss (computed live)
  function ultSafe(h, x, y) { const b = h.owner; for (const d of M().decos) { if (d.spr !== 'pillar') continue;
      const px = d.x, py = d.y - 6, vx = x - b.x, vy = y - b.y, L = Math.hypot(vx, vy); if (L < 1) continue;
      const u = ((px - b.x) * vx + (py - b.y) * vy) / (L * L); if (u <= 0 || u >= 1) continue;
      if (Math.hypot(b.x + vx * u - px, b.y + vy * u - py) < 10) return true; } return false; }

  // ---------------- mobs ----------------
  function spawn(kind, x, y, o = {}) {
    const D = WorldMobs.def[kind]; if (!D) { console.warn('[world] unknown mob', kind); return null; }
    const m = Object.assign({ kind, D, x, y, home: [x, y], hp: Math.round(D.hp * DIFF().enemy_hp), maxHp: Math.round(D.hp * DIFF().enemy_hp), hpLag: Math.round(D.hp * DIFF().enemy_hp), st: 'idle', t: Math.random(), face: -1, r: D.r, fly: !!D.fly, hitT: 0, flash: 0, hz: 0, kx: 0, ky: 0, spawnT: .4, lagDelay: 0 }, o);
    if (D.init) D.init(m); S.mobs.push(m); return m;
  }
  function count(kind) { return S.mobs.filter(m => m.kind === kind && !m.dead).length; }
  function engage(m) { S.engaged = m; }
  function hitMob(m, dmg, dir, melee) {
    if (m.dead || m.invuln || m.spawnT > 0) return;
    const D = m.D; dmg *= D.dmgMul ? D.dmgMul(m) : 1;
    const AF = melee && window.GameAff ? window.GameAff.of(D) : null; if (AF) dmg *= AF.mul; // weapon damage type vs D.aff (weak x1.5 / resist x0.5)
    m.hp -= dmg; m.hitT = .3; m.flash = .12; m.lagDelay = .35; if (D.onHit) D.onHit(m); sfx(melee && dmg >= 12 ? 'hit_heavy' : 'hit_light', .8);
    const armored = D.felt && (m.st === 'melee' || m.st === 'shoot' || m.st === 'leap' || (m.st === 'lunge' && m.sub !== 'rec')); // felt mobs: no knockback while telegraphing / attacking (the warning stays on the body)
    if (!D.boss && !armored) { const kb = D.champion ? 50 : 160; m.kx = Math.cos(dir) * kb; m.ky = Math.sin(dir) * kb; }
    addFx('spark', m.x + Math.cos(dir) * 4, m.y - (D.h || 20) / 2, { life: .25 });
    addFx('text', m.x, m.y - (D.h || 20) - 4, { text: String(Math.round(dmg)) + (AF && AF.label ? ' ' + AF.label : ''), life: .6, color: AF && AF.col ? AF.col : '#fff' });
    if (D.boss || D.champion) engage(m);
    if (m.hp <= 0) killMob(m);
  }
  function killMob(m) {
    if (m.dead) return; m.dead = true; m.hp = 0; const D = m.D;
    addFx('poof', m.x, m.y - 8, { life: .5, big: D.boss || D.champion }); sfx('mob_die', .8);
    if (D.onDeath) D.onDeath(m, W);
    if (!m.noDrop && !m.summoned && window.__game && window.__game.addGold) { const gv = window.__game.addGold(window.__game.goldFor(D.boss ? 'boss' : D.champion ? 'champion' : 'mob', D.area || 1)); if (gv) { sfx('coin', .6); } if (gv) addFx('text', m.x + 8, m.y - (D.h || 20) - 12, { text: '+' + gv + 'G', life: .9, color: '#ffd84a' }); } // gold curve: data/economy.json
    if (!m.noDrop && D.mat && (D.champion || D.boss || Math.random() < .45)) { const n = D.matN || 1; giveLoot([[D.mat, n]]); addFx('text', m.x, m.y - 26, { text: '+' + itemName(D.mat) + (n > 1 ? ' ×' + n : ''), life: 1, color: '#ffe08a' }); }
    if (!D.boss && !D.champion && !m.noDrop && Math.random() < POT.heartDrop) S.fx.push({ type: 'heart', x: m.x, y: m.y, t: 0, life: 8 });
    if (m.flag) { SAVE.flags[m.flag] = true; save(); }
    if (D.champion) { banner('챔피언 격파 — ' + D.name + '!', 2.2); jingle(); const left = ['champ_boar', 'champ_wasp'].filter(f => !SAVE.flags[f]).length;
      after(2.3, () => msg(left ? '남은 챔피언: ' + left + ' — 모두 쓰러뜨리면 골렘의 방이 열린다' : '숲의 두 우두머리를 쓰러뜨렸다! 신전 B2의 봉인된 문이 열린다.', 3.5)); }
    if (D.boss) bossDefeated(m);
    if (m.spawnRef && m.spawnRef.respawn > 0) m.spawnRef.timer = m.spawnRef.respawn;
    if (S.engaged === m) S.engaged = null;
  }
  function bossDefeated(m) {
    const B = M().boss; SAVE.flags[B.flag] = true; save();
    S.hazards.length = 0; S.shots.length = 0; S.temp.length = 0; S.ult = null;
    S.mobs.forEach(o => { if (o !== m && !o.dead) killMob(o); });
    shake(5); jingle(); banner(B.name + ' 격파!', 3);
    after(1.6, () => { const l = giveLoot(B.reward || []); msg('능력 흡수: ' + B.absorb + (l ? '  ·  획득: ' + l : ''), 5); });
    after(3.2, () => { addWarp(M()); msg('빛의 문이 열렸다 — 들어가면 신전 입구로 돌아간다', 4); });
  }
  function addWarp(m) { if (!m.objs.some(o => o.type === 'warp')) m.objs.push({ type: 'warp', x: m.pw / 2, y: m.ph / 2 + 16, tx: -1, ty: -1, to: m.boss.exit.to, spawn: m.boss.exit.spawn }); }
  function phase2(m) { banner('2페이즈 — 골렘이 수정 갑옷을 일으킨다!', 2); shake(5); for (let i = 0; i < 14; i++) addFx('crystal', m.x + Math.cos(i / 14 * TAU) * 30, m.y + Math.sin(i / 14 * TAU) * 22, { life: .8 }); }
  function ult(m, warn) { banner('필살 — 대지 붕괴!  기둥 뒤로 숨거나, 폭발 순간 회피대시', 2.6); S.ult = hazard({ shape: 'all', x: m.x, y: m.y, owner: m, warn, act: 0.05, dmg: Math.ceil(hero.maxHp * Math.min(0.52 * DIFF().enemy_dmg, DIFF().ult_cap || 0.9)), raw: true, kind: 'ult' }); m.ultW = S.ult.warn; } // 52% of max HP (normal), capped so a full-HP hero survives one
  function jingle() { try { if (window.BGM && BGM.jingle) { BGM.jingle('jingle_victory'); S.jingleT = 3.5; } } catch (e) {} }

  // the API handed to mob behaviours (world_mobs.js)
  const W = { get hero() { return hero; }, get map() { return M(); }, hazard, shot, hurt, touch, moveCol, token, get mobs() { return S.mobs; }, get diff() { return DIFF(); }, blockedAt: (x, y) => blocked(x, y, 4), dist, spawn, count, engage,
    fx: addFx, sfx, shake, banner, after, tempSolid, randomFloor, breakDecoNear, phase2, ult, say: msg };

  // ---------------- scene manager ----------------
  function go(to, spawnName, opt = {}) {
    if (S.trans) return false;
    S.trans = { phase: 'out', t: 0, to, spawn: spawnName, card: opt.card, fromTown: S.scene === 'town' };
    if (S.trans.fromTown) { const g = window.__game; S.townPos = { x: g.hero.x, y: g.hero.y - 34 }; g.setManual(true); syncFromTown(); show(true); }
    return true;
  }
  function show(v) { cv.style.display = v ? 'block' : 'none'; }
  function enterScene(to, spawnName) {
    S.mobs = []; S.hazards = []; S.shots = []; S.fx = []; S.temp = []; S.timers = []; S.ult = null; S.engaged = null; S.dialog = null; S.bossRef = null; S.pause = false;
    if (to === 'town') { S.scene = 'town'; S.map = null; return Promise.resolve(); }
    return loadMap(to).then(m => {
      S.map = m; S.scene = m.type === 'world' ? 'world' : 'map'; S.bgm = m.bgm;
      if (!m.groundC) m.groundC = renderGround(m);
      let sp = m.spawns && m.spawns[spawnName];
      if (!sp && spawnName && spawnName.startsWith('ws:')) { const w = m.objs.find(o => o.type === 'waystone' && o.id === spawnName.slice(3)); if (w) sp = [w.tx + .5, w.ty + 1.6, 'down']; } // fast travel
      if (!sp && m.type === 'world') { const n = (m.nodes || []).find(n => n.id === spawnName); if (n) sp = [n.x + .5, n.y + 2.2, 'down']; }
      sp = sp || (m.spawns && m.spawns.default) || [m.w / 2, m.h / 2];
      hero.x = sp[0] * m.T; hero.y = sp[1] * m.T; hero.face = sp[2] || 'down'; hero.safe = [hero.x, hero.y]; hero.atk = hero.roll = null; hero.inv = .5; hero.moving = false;
      S.nodeArmed = false; S.nearNode = null;
      for (const o of (m.objects || [])) {
        if (o.type === 'spawn') { o.timer = 0; const mm = spawn(o.mob, (o.x + .5) * m.T, (o.y + .5) * m.T); if (mm) { mm.spawnRef = o; o.mob = mm; } }
        if (o.type === 'champion' && !SAVE.flags[o.id]) spawn(o.mob, (o.x + .5) * m.T, (o.y + .5) * m.T, { flag: o.id });
      }
      if (m.boss && !SAVE.flags[m.boss.flag]) { const b = spawn(m.boss.kind, m.boss.x * m.T, m.boss.y * m.T, { flag: m.boss.flag }); S.bossRef = b; S.engaged = b; }
      if (m.boss && SAVE.flags[m.boss.flag]) addWarp(m);
      for (const o of m.objs) { if ((o.type === 'door_locked' || o.type === 'gate') && SAVE.opened[o.key]) o.open = true; if (o.type === 'lever' && SAVE.levers[o.key]) o.on = true;
        if (o.type === 'door_locked' || o.type === 'gate' || o.type === 'boss_door') m.solidG[o.ty * m.w + o.tx] = o.open ? 0 : 1; }
      updateGate(m, true);
      snapCam();
      if (NAV()) NAV().onEnter(m);
    });
  }
  function stepTrans(dt) {
    const tr = S.trans; tr.t += dt;
    if (tr.phase === 'out' && tr.t >= FADE) {
      tr.phase = 'load'; tr.t = 0;
      const first = !SAVE.visited[tr.to];
      enterScene(tr.to, tr.spawn).then(() => {
        if (tr.to === 'town') returnToTown();
        const m = S.map; const wantCard = tr.card !== undefined ? tr.card : !!(m && m.title && (first || m.type === 'boss'));
        SAVE.visited[tr.to] = true; save();
        tr.cardData = wantCard && m ? m.title : null;
        tr.phase = tr.cardData ? 'card' : 'in'; tr.t = 0;
        document.body.classList.toggle('wscene', S.scene !== 'town');
      }).catch(e => { console.error(e); S.trans = null; msg('맵을 불러오지 못했다: ' + e.message); });
    }
    if (tr.phase === 'card') { if (tr.t > 0.6 && (takePress('attack') || takePress('interact'))) tr.t = Math.max(tr.t, CARD - .35); if (tr.t >= CARD) { tr.phase = 'in'; tr.t = 0; } }
    if (tr.phase === 'in' && tr.t >= FADE) { S.trans = null; if (S.scene === 'town') show(false); queue.length = 0; }
  }
  function returnToTown() {
    const g = window.__game; if (!g) return;
    if (S.townPos) { g.hero.x = S.townPos.x; g.hero.y = S.townPos.y; g.hero.face = 'up'; }
    syncTownHp(); g.setManual(false); S.scene = 'town'; S.bgm = null; held.clear();
  }
  function syncFromTown() { const g = window.__game; if (!g) return; hero.maxHp = g.hero.maxHp || 50; hero.hp = Math.max(1, g.hero.hp ?? hero.maxHp); }
  function syncTownHp() { const g = window.__game; if (g && g.hero) { g.hero.hp = hero.hp; g.hero.maxHp = hero.maxHp; } }
  function die() { S.deadT = 0.01; banner('쓰러졌다…', 2.2); }
  function respawnAfterDeath() { hero.hp = hero.maxHp; syncTownHp(); S.deadT = 0; const m = M(); go(m.type === 'boss' ? 'dungeon01_b2' : m.id, 'default', { card: false }); }

  // ---------------- town exit gate (town coords; maps/world.json "townGate" overrides) ----------------
  function townGate() { const m = MAPS.world; return Object.assign({ x0: 560, x1: 800, y: 690, hintY: 640, to: 'field00', spawn: 'town' }, (m && m.townGate) || {}); }
  function watchTown() {
    const g = window.__game; if (!g || !g.ready || S.trans) return;
    const G = townGate(), h = g.hero, inX = h.x > G.x0 && h.x < G.x1, free = !g.ui && !g.winOpen && !g.uw;
    gateHint.style.display = inX && h.y > G.hintY && free ? 'block' : 'none';
    if (inX && h.y >= G.y && free) { gateHint.style.display = 'none'; go(townGate().to || 'field00', townGate().spawn || 'town'); }
  }

  // ---------------- update ----------------
  function dirInput() { let ix = (isHeld('right') ? 1 : 0) - (isHeld('left') ? 1 : 0), iy = (isHeld('down') ? 1 : 0) - (isHeld('up') ? 1 : 0); if (ix && iy) { ix *= .7071; iy *= .7071; }
    if (!ix && !iy) { const st = window.__game && window.__game.stick; if (st && st.id !== null && Math.hypot(st.dx, st.dy) >= .18) { const l = Math.hypot(st.dx, st.dy); ix = st.dx / l; iy = st.dy / l; } } return [ix, iy]; }
  const FACEV = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };
  function setFace(ix, iy) { if (Math.abs(ix) > Math.abs(iy)) hero.face = ix > 0 ? 'right' : 'left'; else if (iy) hero.face = iy > 0 ? 'down' : 'up'; if (ix || iy) hero.f8 = DIR8[((Math.round(Math.atan2(iy, ix) / (Math.PI / 4)) % 8) + 8) % 8]; }
  const DIR8 = ['right', 'downright', 'down', 'downleft', 'left', 'upleft', 'up', 'upright']; // test128 hero8: 8-way facing for the new hero frames (hitboxes stay 4-way FACEV)
  function step(dt) {
    S.t += dt; { const g = window.__game; if (g && g.potionCd > 0 && S.scene !== 'town') g.potionCd = Math.max(0, g.potionCd - dt); }
    if (S.trans) { stepTrans(dt); if (S.trans && S.trans.phase !== 'in') return; }
    if (S.scene === 'town') return;
    { const g = window.__game; if (g && g.ui) { queue.length = 0; return; } } // DOM UI (shop) open over a map: paused
    if (S.dialog) { if (takePress('interact') || takePress('attack') || takePress('menu')) S.dialog = null; queue.length = 0; return; }
    if (NAV() && NAV().screenStep(dt)) { queue.length = 0; return; } // full map screen open (paused)
    if (takePress('menu')) S.pause = !S.pause;
    if (S.pause) { if (queue.includes('KeyT')) { queue.length = 0; S.pause = false; go('town', null, { card: false }); } queue.length = 0; return; }
    if (S.ultFx) { stepUlt(dt); queue.length = 0; updateCam(dt); return; } // 필살기: world frozen (timers, mobs, hazards, shots)
    for (let i = S.timers.length - 1; i >= 0; i--) { const tm = S.timers[i]; tm.t -= dt; if (tm.t <= 0) { S.timers.splice(i, 1); tm.f(); } }
    if (S.msg && (S.msg.t -= dt) <= 0) S.msg = null;
    if (S.banner && (S.banner.t -= dt) <= 0) S.banner = null;
    if (S.jingleT > 0) S.jingleT -= dt;
    S.shake = Math.max(0, S.shake - dt * 14);
    if (S.deadT > 0) { S.deadT += dt; if (S.deadT > 2.2) respawnAfterDeath(); queue.length = 0; return; }
    if (hero.hp > 0 && S.mobs.some(m => !m.dead && Math.hypot(m.x - hero.x, m.y - hero.y) < 150)) ultAdd('autoPerSec', dt); // 필살기 게이지: 싸우는 동안 저절로 (몹이 가까이 있을 때만, owner 10-23)
    if (S.scene === 'world') stepWorld(dt); else { stepMap(dt); gkTick(); if (S.map && !S.trans && S.deadT <= 0) stepPet(dt); if (NAV() && S.map && !S.trans) NAV().step(dt); }
    queue.length = 0;
    updateCam(dt);
  }
  function stepWorld(dt) {
    const m = M(); const [ix, iy] = dirInput(); hero.moving = !!(ix || iy);
    if (hero.moving) { setFace(ix, iy); moveCol(hero, ix * WORLD_SPEED * dt, iy * WORLD_SPEED * dt, 2); hero.walkT += dt; }
    let nearN = null, nd = 1e9;
    for (const n of m.nodes) { const x = (n.x + .5) * m.T, y = (n.y + .5) * m.T, d = Math.hypot(hero.x - x, hero.y - y); if (d < nd) { nd = d; nearN = n; }
      if (n.locked && d < m.T * 1.3) { const a = Math.atan2(hero.y - y, hero.x - x) || 1.57; hero.x = x + Math.cos(a) * m.T * 1.3; hero.y = y + Math.sin(a) * m.T * 1.3; } } // locked: visible but blocked
    S.nearNode = nd < m.T * 2.4 ? nearN : null;
    if (nd > m.T * 2.6) S.nodeArmed = true;
    const n = S.nearNode;
    if (n && !n.locked && n.scene && (takePress('interact') || (S.nodeArmed && nd < m.T * .9))) {
      S.nodeArmed = false;
      if (n.scene === 'town') go('town', null, { card: false }); else go(n.scene, 'world');
    }
  }
  function stepMap(dt) {
    const m = M();
    hero.inv = Math.max(0, hero.inv - dt); hero.rollCd = Math.max(0, hero.rollCd - dt); hero.slowT = Math.max(0, hero.slowT - dt); hero.dodgeT = Math.max(0, hero.dodgeT - dt); hero.atkCd = Math.max(0, (hero.atkCd || 0) - dt);
    const [ix, iy] = dirInput();
    if (takePress('potion')) usePotion();
    if (takePress('ult') && !S.ultFx) castUlt();
    if (takePress('dash') && !hero.roll && hero.rollCd <= 0) { let dx = ix, dy = iy; if (!dx && !dy) { const f8 = hero.f8 && hero.f8.includes(hero.face) ? hero.f8 : null, a = f8 ? DIR8.indexOf(f8) * Math.PI / 4 : null; [dx, dy] = a !== null ? [Math.cos(a), Math.sin(a)] : FACEV[hero.face]; } const L = Math.hypot(dx, dy);
      hero.roll = { t: 0, dx: dx / L, dy: dy / L, carry: hero.run ? HERO_SPEED * RUN.mul : 0 }; hero.atk = null; setFace(dx, dy); addFx('dust', hero.x, hero.y, { life: .35 }); sfx('roll', .8); }
    if (takePress('attack') && !hero.roll && !(hero.atkCd > 0) && (!hero.atk || hero.atk.t > atkT(hero.atk.i).a1)) { hero.holdT = 0; hero.holdOk = true; hero.charge = null; // running + attack = 돌진베기
      if (hero.run && hero.moving && !hero.atk) { hero.atk = { t: 0, hit: new Set(), i: 3 }; addFx('dust', hero.x, hero.y, { life: .35 }); sfx('swing_heavy', .8); } else { hero.combo = (hero.comboT > 0 && hero.combo < 2) ? hero.combo + 1 : 0; hero.atk = { t: 0, hit: new Set(), i: hero.combo, runSlash: !!(hero.run && hero.moving) }; sfx(hero.combo === 2 ? 'swing_heavy' : 'swing_light', .7); if (hero.atk.runSlash) addFx('dust', hero.x, hero.y, { life: .3 }); if (ix || iy) setFace(ix, iy); } }
    if (isHeld('attack') && hero.holdOk) hero.holdT += dt; else hero.holdOk = false; // charge (모으기): keep holding attack -> lv1 t1 / lv2 t2, release = charged slash; a hit / dodge cancels
    if (!hero.charge && hero.holdOk && hero.holdT > .14 && !hero.atk && !hero.roll && hero.hp > 0) { hero.charge = { t: hero.holdT, lv: 0, flash: 0 }; hero.run = false; }
    if (hero.charge) { const C = hero.charge, CF = spW().charge; C.t += dt; C.flash = Math.max(0, C.flash - dt); const lv = C.t >= CF.t2 ? 2 : C.t >= CF.t1 ? 1 : 0;
      if (lv > C.lv) { C.lv = lv; C.flash = .25; sfx(lv > 1 ? 'ult_cutin' : 'hit_crit', lv > 1 ? .4 : .5, lv > 1 ? 1.9 : 1.7); addFx('spark', hero.x, hero.y - 12, { life: .3 }); }
      if (!hero.holdOk || hero.roll || hero.atk || hero.hp <= 0) { const rel = !hero.holdOk && !hero.roll && !hero.atk && hero.hp > 0 && C.lv > 0; hero.charge = null; if (rel) { hero.atk = { t: 0, hit: new Set(), i: 3 + C.lv }; sfx('swing_heavy', 1); } } }
    if (takePress('interact')) interact();
    tickTrail(dt);
    if (hero.roll) { const r = hero.roll, D = DG(), RD = rollDur(); const p0 = Math.min(1, r.t / RD); r.t += dt; const p = Math.min(1, r.t / RD);
      if (D && D.burstTicks) { const TB = D.burstTicks / 60, q0 = Math.min(1, (r.t - dt) / TB), q1 = Math.min(1, r.t / TB), E2 = q => 1 - Math.pow(1 - q, 2.6), st = D.tiles * 16 * .68 * (E2(q1) - E2(q0)), n = Math.max(1, Math.ceil(st / 3)); for (let i = 0; i < n; i++) moveCol(hero, r.dx * st / n, r.dy * st / n, 5);
        const tt = Math.round((r.t - dt) * 60); if (tt % 2 === 0 && tt < D.burstTicks && h128()) { S.trail = S.trail || []; S.trail.push({ c128: h128Cell(), x: hero.x, y: hero.y, t: 0, life: (D.durTicks - tt) / 60 + .05, a: .8 * Math.pow(.8, S.trail.length) }); } }
      else if (D) { const E = EASE[D.ease] || EASE.outCubic, st = D.tiles * 16 * (E(p) - E(p0)), n = Math.max(1, Math.ceil(st / 3)); for (let i = 0; i < n; i++) moveCol(hero, r.dx * st / n, r.dy * st / n, 5); // dash: fixed distance, ease-out
        const AI = D.afterimage || {}; r.ai = (r.ai || 0) - 1; r.ain = r.ain || 0; if (r.ai <= 0 && r.ain < (AI.count || 5) && p < .95) { r.ai = AI.intervalTicks || 2; r.ain++; S.trail = S.trail || []; S.trail.push({ c128: h128() ? h128Cell() : null, name: heroFrameName(), x: hero.x, y: hero.y, flip: hero.face === 'left', t: 0, life: AI.fade || .25, a: AI.alpha ?? .55 }); } }
      else { const sp = Math.max(ROLL.speed * (1 - r.t / ROLL.dur * .55), r.carry); moveCol(hero, r.dx * sp * dt, r.dy * sp * dt, 5); }
      hero.walkT += dt * 3;
      if (r.t >= RD) { hero.roll = null; hero.rollCd = DG() ? DG().cdTicks / 60 : ROLL.cd; if (r.carry) { hero.run = true; } } }
    else if (hero.atk) { const a = hero.atk; a.t += dt; const dv = FACEV[hero.face]; const H = (h128() || {}).H128 || {}, AT = atkT(a.i), lv = a.i >= 3 ? (a.t < AT.a1 ? (spOf(a.i).lunge || 0) * .3 / AT.a1 * 2 * (1 - a.t / AT.a1) : 0) : a.runSlash && a.t < AT.a1 ? 20 + HERO_SPEED * RUN.mul * (1 - a.t / AT.a1) : H.v4 ? (a.t < AT.a1 ? (H.lunge || [9, 11, 14])[Math.min(2, a.i)] * 29 / 96 / AT.a1 * 2 * (1 - a.t / AT.a1) : 0) : 20; // hero v4: per-hit forward advance (town px scaled to field)
      moveCol(hero, dv[0] * lv * dt, dv[1] * lv * dt, 5); // running slash carries momentum
      if (!SLASH_BODY && !a.gk && a.t >= AT.a0 - 2 / 60) { a.gk = true; gkSpawn(a.i); }
      if (SLASH_BODY && a.t >= AT.a0 && a.t <= AT.a1) { // 검기 mode: hits are dealt by the flying arc (gkTick) const R = hbR(a.i), cosA = Math.cos(hbA(a.i) / 2 * Math.PI / 180);
        for (const mm of S.mobs) { if (mm.dead || a.hit.has(mm)) continue; const mh = (mm.D.h || 20) * (mm.scale || 1);
          const ddx = mm.x - hero.x, ddy = ((mm.y - mh * .3) - (hero.y - 4)) / .8, dd = Math.hypot(ddx, ddy);
          if (dd < R + mm.r + mh * .2 && (dd < 6 || (ddx * dv[0] + ddy * dv[1]) / dd >= cosA)) { /* forward sector (same radius/arc as the trail) */ a.hit.add(mm); if (!SLASH_BODY) { S.gkImp = S.gkImp || []; S.gkImp.push({ x: mm.x, y: mm.y - mh * .45, t: 0, big: a.i >= 2 }); } hitMob(mm, a.i >= 3 ? ATK_DMG[0] * (spOf(a.i).dmgMul || 1) : ATK_DMG[Math.min(2, a.i)], Math.atan2(mm.y - hero.y, mm.x - hero.x), true); if (a.i >= 3) sfx(a.i === 5 ? 'hit_crit' : 'hit_heavy', .8); } } }
      if (a.i === 5 && !a.waved && a.t >= AT.a0) { a.waved = true; spawnHW(Math.atan2(dv[1], dv[0])); shake(1); } // charge lv2: forward sword wave (1px shake only)
      if (a.t >= AT.dur) { hero.atk = null; hero.comboT = a.i >= 3 ? 0 : ATK.chain; if (a.i >= 3) hero.atkCd = spOf(a.i).cool || .2; } }
    else { const g = window.__game, mv = !!(ix || iy);
      if (mv && !hero.run && !hero.charge && (hero.runReq || (g && g.alwaysRun))) { hero.run = true; hero.runStartT = RUN.startT; addFx('dust', hero.x - ix * 4, hero.y, { life: .35 }); } // dash start + dust kick-up
      hero.runReq = false; if (!mv && hero.run) { hero.run = false; hero.skidT = RUN.skidT; hero.skidV = [FACEV[hero.face][0], FACEV[hero.face][1]]; addFx('dust', hero.x, hero.y, { life: .3 }); }
      hero.runStartT = Math.max(0, (hero.runStartT || 0) - dt);
      const rk = hero.run ? RUN.mul + (RUN.startMul - RUN.mul) * hero.runStartT / RUN.startT : 1;
      const sp = HERO_SPEED * rk * (hero.charge ? (spW().charge.moveMul || .4) : 1) * (hero.slowT > 0 ? .45 : 1) * (onTile('tallgrass') ? .8 : 1); hero.moving = mv;
      if (hero.moving) { if (!hero.charge) setFace(ix, iy); moveCol(hero, ix * sp * dt, iy * sp * dt, 5); const w0 = hero.walkT; hero.walkT += dt * (hero.run ? rk * RUN.cadence : 1); if (hero.run && Math.floor(hero.walkT * 4) !== Math.floor(w0 * 4)) addFx('dust', hero.x - ix * 3, hero.y, { life: .25 }); } // footfall dust
      else if (hero.skidT > 0) { hero.skidT -= dt; const k = hero.skidT / RUN.skidT; moveCol(hero, hero.skidV[0] * HERO_SPEED * 1.2 * k * dt, hero.skidV[1] * HERO_SPEED * 1.2 * k * dt, 5); } } // short skid
    stepHW(dt);
    if (!hero.atk) hero.comboT = Math.max(0, hero.comboT - dt);
    // tiles & objects: pits, spikes, exits, stairs, keys, doors, warp
    const cx = Math.floor(hero.x / m.T), cy = Math.floor(hero.y / m.T);
    let onPit = false, onSpike = false;
    for (const o of m.objs) {
      const inside = o.tx === cx && o.ty === cy;
      if (o.type === 'pit' && inside && !hero.roll) onPit = true;
      if (o.type === 'spikes' && inside && spikeUp(o)) onSpike = true;
      if (o.type === 'key' && inside && !SAVE.keys[o.keyId]) { SAVE.keys[o.keyId] = true; save(); banner('열쇠를 얻었다!', 1.6); }
      if ((o.type === 'stairs_up' || o.type === 'stairs_down') && inside && m.links && m.links[o.type]) {
        if (m.boss && S.bossRef && !S.bossRef.dead) { hero.y = cy * m.T - 3; if (!S.msg) msg('봉인의 결계 — 보스를 쓰러뜨리기 전에는 나갈 수 없다', 1.6); continue; } // no fleeing mid-fight
        const L = m.links[o.type]; go(L.to, L.spawn); return; }
      if (o.type === 'exit' && hero.x >= o.tx * m.T && hero.x < (o.tx + o.w) * m.T && hero.y >= o.ty * m.T && hero.y < (o.ty + o.h) * m.T) { go(o.to, o.spawn); return; }
      if (o.type === 'warp' && Math.hypot(hero.x - o.x, hero.y - o.y) < 10) { go(o.to, o.spawn, { card: false }); return; }
      const bump = Math.abs(hero.x - o.x) < 10 && hero.y > o.y && hero.y - o.y < m.T * 1.05 && isHeld('up');
      if (o.type === 'boss_door' && bump) bossDoor(o);
      if (o.type === 'door_locked' && !o.open && bump) tryDoor(o);
    }
    if (onSpike) hurt(1, { x: hero.x, y: hero.y + 10 });
    if (onPit) { hero.x = hero.safe[0]; hero.y = hero.safe[1]; addFx('text', hero.x, hero.y - 30, { text: '추락!', life: .7, color: '#ffb0a0' }); hero.inv = 0; hurt(1); }
    else if (!onSpike && !hero.roll && !trapAt(cx, cy) && Math.floor(S.t * 4) !== Math.floor((S.t - dt) * 4)) hero.safe = [hero.x, hero.y];
    // mobs
    for (const mm of S.mobs) {
      if (mm.dead) continue;
      mm.spawnT = Math.max(0, mm.spawnT - dt); mm.hitT = Math.max(0, mm.hitT - dt); mm.flash = Math.max(0, mm.flash - dt);
      if (mm.lagDelay > 0) mm.lagDelay -= dt; else mm.hpLag = Math.max(mm.hp, mm.hpLag - dt * mm.maxHp * .8);
      if (mm.kx || mm.ky) { moveCol(mm, mm.kx * dt, mm.ky * dt, mm.r, mm.fly); mm.kx *= Math.pow(.002, dt); mm.ky *= Math.pow(.002, dt); if (Math.abs(mm.kx) + Math.abs(mm.ky) < 5) mm.kx = mm.ky = 0; }
      if (mm.spawnT <= 0 && hero.hp > 0) mm.D.update(mm, W, dt);
    }
    for (const o of (m.objects || [])) if (o.type === 'spawn' && o.respawn > 0 && o.mob && o.mob.dead) { o.timer -= dt; // respawn out of sight
      const px = (o.x + .5) * m.T, py = (o.y + .5) * m.T; if (o.timer <= 0 && Math.hypot(hero.x - px, hero.y - py) > 200) { const mm = spawn(o.mob.kind, px, py); mm.spawnRef = o; o.mob = mm; } }
    S.mobs = S.mobs.filter(mm => !mm.dead);
    // hazards
    for (let i = S.hazards.length - 1; i >= 0; i--) { const h = S.hazards[i]; h.t += dt;
      if (h.owner && h.owner.dead && h.t < h.warn) { S.hazards.splice(i, 1); continue; }
      const live = h.t >= h.warn && h.t < h.warn + (h.act || 0);
      if (live && h.dmg && !h.hit && inHaz(h, hero.x, hero.y - 4)) { if (hurt(h.dmg, h.shape === 'all' ? null : h, h.raw)) { h.hit = true; if (h.slow) hero.slowT = h.slow; } }
      if (live && h.zone && inHaz(h, hero.x, hero.y - 4)) hero.slowT = Math.max(hero.slowT, .15);
      if (h.t >= h.warn && !h.fired) { h.fired = true; if (h.onEnd) h.onEnd(h); hazardFx(h); }
      if (h.linger && h.t >= h.warn + (h.act || 0) && h.t < h.warn + h.act + h.linger && !h.hit && Math.hypot(hero.x - h.x, (hero.y - h.y) * 1.15) < h.r * .8) { if (hurt(1, h)) h.hit = true; }
      if (h.t > h.warn + (h.act || 0) + (h.linger || 0) + .25) { S.hazards.splice(i, 1); if (h === S.ult) S.ult = null; }
    }
    for (let i = S.shots.length - 1; i >= 0; i--) { const s = S.shots[i]; s.t += dt; s.x += s.vx * dt; s.y += s.vy * dt;
      if (s.ret && !s.back && s.t > s.life / 2) { s.back = true; s.vx = -s.vx; s.vy = -s.vy; } // boomerang (felt puppet blades)
      if (Math.hypot(hero.x - s.x, hero.y - 8 - s.y) < s.r + 5 && hurt(s.dmg, s)) { if (s.pull && s.owner && !s.owner.dead) { const a = Math.atan2(s.owner.y - hero.y, s.owner.x - hero.x); moveCol(hero, Math.cos(a) * s.pull, Math.sin(a) * s.pull, 5); s.owner.intent = 'melee'; s.owner.cd = Math.min(s.owner.cd || 0, .15); } // thread yank -> follow-up claw
        if (s.slow) hero.slowT = Math.max(hero.slowT, s.slow); S.shots.splice(i, 1); continue; }
      if (s.t > s.life || solidAt(s.x, s.y + 6)) { if (s.zone) hazard({ shape: 'circle', x: s.x, y: s.y + 6, r: 12, warn: 0, act: 2, dmg: 0, kind: 'web', zone: true }); // slowing web patch
        addFx('spark', s.x, s.y, { life: .2 }); S.shots.splice(i, 1); } }
    for (let i = S.temp.length - 1; i >= 0; i--) if ((S.temp[i].life -= dt) <= 0) S.temp.splice(i, 1);
    for (let i = S.fx.length - 1; i >= 0; i--) { const f = S.fx[i]; f.t += dt;
      if (f.type === 'heart' && Math.hypot(hero.x - f.x, hero.y - f.y) < 10) { const hv = Math.ceil(hero.maxHp * POT.heartPct / 100); hero.hp = Math.min(hero.maxHp, hero.hp + hv); syncTownHp(); addFx('text', f.x, f.y - 20, { text: '+' + hv, life: .7, color: '#ff8aa0' }); sfx('heart', .7); S.fx.splice(i, 1); continue; }
      if (f.t > f.life) S.fx.splice(i, 1); }
    // music: area theme / champion battle / boss (phase 2 track) / back to area theme after the clear
    const e = S.engaged; let want = m.bgm;
    if (m.type === 'boss') want = S.bossRef && !S.bossRef.dead ? (S.bossRef.phase === 2 ? m.bgm2 : m.bgm) : (m.bgmAfter || 'area01_forest');
    else if (e && !e.dead && e.D.champion && dist(e, hero) < 260) want = m.battleBgm || 'battle_champion';
    S.bgm = want;
  }
  function onTile(name) { const m = M(); const c = m.cells[Math.floor(hero.y / m.T) * m.w + Math.floor(hero.x / m.T)]; return c && c.g === name; }
  // spikes: 2.6s cycle (offset per column): down 1.5s, warning tips 0.5s, up 0.6s (hurts)
  const spikePhase = o => ((S.t + o.tx * .18) % 2.6);
  const spikeUp = o => spikePhase(o) > 2.0;
  const spikeWarn = o => spikePhase(o) > 1.5 && spikePhase(o) <= 2.0;
  const trapAt = (cx, cy) => M().objs.some(o => (o.type === 'spikes' || o.type === 'pit') && Math.abs(o.tx - cx) <= 1 && Math.abs(o.ty - cy) <= 1);
  function usePotion() { const g = window.__game; const n = g ? g.potions : 0; if (!n) { msg('물약이 없다'); return; } if (hero.hp >= hero.maxHp) { msg('체력이 가득하다'); return; }
    if (g.potionCd > 0) { msg('물약 재사용 대기 ' + g.potionCd.toFixed(1) + '초'); return; }
    const hv = Math.ceil(hero.maxHp * POT.heal / 100); g.potions = n - 1; g.potionCd = POT.cd; hero.hp = Math.min(hero.maxHp, hero.hp + hv); syncTownHp(); addFx('heal', hero.x, hero.y - 20); msg('물약 사용 (+' + hv + ' HP)  남은 물약 ' + (n - 1)); }
  function interact() {
    const m = M(); const dv = FACEV[hero.face]; const fx = Math.floor((hero.x + dv[0] * 12) / m.T), fy = Math.floor((hero.y - 3 + dv[1] * 12) / m.T);
    for (const o of m.objs) {
      if (!((o.tx === fx && o.ty === fy) || Math.hypot(o.x - hero.x, o.y - hero.y) < 15)) continue;
      if (o.type === 'sign') { S.dialog = { text: o.text }; return; }
      if (o.type === 'npc') { S.dialog = { text: (o.quests && NAV()) ? NAV().talk(o) : (o.idle || '…'), name: o.name, por: o.main ? (o.portrait || o.art || o.id) : null }; S.talked = o.id; return; }
      if (o.type === 'door') { // town B building doors: shops open the shop UI, the inn heals, others show their sign
        const g = window.__game;
        if (o.shop && g && g.openShop) { S.dialog = null; g.openShop(o.shop); S.door = o.id; return; }
        if (o.wish && g && g.INV) { // town H 소원 우물: 10G 동전 던지기 운세 (1/8 chance the well pays 40G back)
          if (g.INV.gold < 10) { S.dialog = { text: '동전이 모자란다. (10G 필요)', name: o.name }; return; }
          g.INV.gold -= 10; const F = ['대길 — 오늘은 무엇을 해도 잘 풀린다.', '길 — 갱도에서 좋은 원석을 만날 운세.', '소길 — 작은 행운이 따른다.', '평 — 평범한 하루. 조심해서 나쁠 건 없다.', '흉 — 박쥐 떼를 조심하라.'];
          const lucky = Math.random() < 1 / 8; if (lucky) g.addGold(40);
          S.wish = (S.wish || 0) + 1; S.dialog = { text: '동전을 던졌다… (-10G)\n' + F[Math.floor(Math.random() * F.length)] + (lucky ? '\n우물이 반짝이며 40G를 돌려주었다!' : ''), name: o.name }; S.door = o.id; return; }
        if (o.race) { S.dialog = { text: '광차 경주 트랙. 「바퀴」가 접수를 받는다.\n광차 경주 미니게임은 아직 준비 중이다. (stub)', name: o.name }; S.door = o.id; return; }
        if (o.heal) { hero.hp = hero.maxHp; syncTownHp(); addFx('heal', hero.x, hero.y - 20); }
        S.dialog = { text: o.text || ('「' + (o.name || '건물') + '」'), name: o.name }; S.door = o.id; return; }
      if (o.type === 'waystone') { const first = !SAVE.waystones[o.id]; SAVE.waystones[o.id] = true; save(); hero.hp = hero.maxHp; syncTownHp(); addFx('heal', hero.x, hero.y - 20);
        S.dialog = { text: (first ? '비석에 손을 대자 빛이 깃들었다 — 「' + o.name + '」 등록!\n' : '「' + o.name + '」\n') + '체력 회복 · 지도 화면(' + 'M' + ')에서 등록한 비석으로 순간이동할 수 있다.' }; return; }
      if (o.type === 'chest') { if (SAVE.chests[o.id]) { msg('빈 상자다'); return; } SAVE.chests[o.id] = true; save(); banner('보물상자! ' + giveLoot((o.loot || []).concat([['gold', window.__game && window.__game.goldFor ? window.__game.goldFor('chest', o.area || 1) : 0]])), 2.2); addFx('sparkle', o.x, o.y - 10, { life: .8 }); return; }
      if (o.type === 'heal') { hero.hp = hero.maxHp; syncTownHp(); msg('쉼터에서 쉬었다. 체력 회복!'); addFx('heal', hero.x, hero.y - 20); return; }
      if (o.type === 'lever') { if (o.on) { msg('이미 당긴 레버다'); return; } o.on = true; SAVE.levers[o.key] = true; save(); shake(1); updateGate(m); return; }
      if (o.type === 'door_locked') { tryDoor(o); return; }
      if (o.type === 'boss_door') { bossDoor(o); return; }
      if (o.type === 'gate' && !o.open) { msg('철창이다. 어딘가의 레버로 열 수 있을 것 같다'); return; }
    }
    for (const o of m.objs) if (o.type === 'hidden' && !SAVE.chests[o.id] && Math.hypot(o.x - hero.x, o.y - hero.y) < 22) { SAVE.chests[o.id] = true; save(); banner('풀숲에서 찾았다! ' + giveLoot(o.loot || []), 2.2); return; }
  }
  function tryDoor(o) { const m = M(); if (o.open) return;
    const keyId = Object.keys(SAVE.keys).find(k => SAVE.keys[k] === true && !k.endsWith(':used') && !SAVE.keys[k + ':used']);
    if (!keyId) { if (!S.msg) msg('잠겨 있다. 열쇠가 필요하다'); return; }
    SAVE.keys[keyId + ':used'] = true; o.open = true; SAVE.opened[o.key] = true; save(); m.solidG[o.ty * m.w + o.tx] = 0; banner('열쇠로 문을 열었다', 1.4); shake(1); }
  function updateGate(m, silent) { if (m.gateNeeds !== 'levers') return; const lv = m.objs.filter(o => o.type === 'lever'); const on = lv.filter(o => o.on).length;
    if (!silent) msg('레버를 당겼다 (' + on + '/' + lv.length + ')');
    if (on === lv.length) for (const o of m.objs) if (o.type === 'gate' && !o.open) { o.open = true; SAVE.opened[o.key] = true; save(); m.solidG[o.ty * m.w + o.tx] = 0; if (!silent) { banner('철창이 열렸다!', 1.6); shake(2); } } }
  function bossDoor(o) { const m = M(); const L = m.links.boss_door; const need = (L.needFlags || []).filter(f => !SAVE.flags[f]);
    if (need.length) { if (!S.msg) msg(L.lockedText + '  (남은 챔피언 ' + need.length + ')', 3); return; }
    go(L.to, L.spawn); }
  function hazardFx(h) { if (h.dmg) sfx(h.kind === 'swipe' || h.kind === 'thud' ? 'mob_swing' : h.kind === 'root' || h.kind === 'web' ? 'mob_swing' : 'impact', .7); if (h.kind === 'rock' || h.kind === 'crystal' || h.kind === 'quake') addFx(h.kind === 'rock' ? 'debris' : 'crystal', h.x, h.y, { life: .5 });
    if (h.kind === 'ult') { shake(7); for (let i = 0; i < 30; i++) { const p = randomFloor(); addFx('crystal', p[0], p[1], { life: .7 }); } }
    if (h.kind === 'poison') addFx('cloud', h.x, h.y, { life: (h.act || 0) + (h.linger || 0) + .2, r: h.r }); }

  // ---------------- camera ----------------
  function clampC(v, max) { return max <= 0 ? max / 2 : Math.max(0, Math.min(max, v)); }
  function camTarget() { const m = M(); return [clampC(hero.x - LW / 2, m.pw - LW), clampC(hero.y - 10 - LH / 2, m.ph - LH)]; }
  function snapCam() { if (M()) S.cam = camTarget(); }
  function updateCam(dt) { if (!M()) return; const [tx, ty] = camTarget(); const k = 1 - Math.pow(.0005, dt); S.cam[0] += (tx - S.cam[0]) * k; S.cam[1] += (ty - S.cam[1]) * k; }

  // ---------------- render: low-res world, then display-res text/HUD ----------------
  function render() {
    const dpr = Math.min(devicePixelRatio || 1, 2), /* owner 10-22 "너무 끊기는데": 3x phones drew 2.25x the pixels */ CW = Math.round(innerWidth * dpr), CH = Math.round(innerHeight * dpr);
    if (cv.width !== CW || cv.height !== CH) { cv.width = CW; cv.height = CH; }
    const k = Math.max(1, Math.floor(Math.min(CW / LW, CH / LH))), ox = Math.floor((CW - LW * k) / 2), oy = Math.floor((CH - LH * k) / 2);
    S.view = { k, ox, oy };
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, CW, CH);
    const tr = S.trans;
    const showWorld = S.scene !== 'town' && S.map && !(tr && (tr.phase === 'load' || (tr.phase === 'out' && tr.fromTown)));
    if (showWorld) {
      ctx.fillStyle = '#000'; ctx.fillRect(0, 0, CW, CH);
      drawLow(); ctx.imageSmoothingEnabled = false; ctx.drawImage(low, ox, oy, LW * k, LH * k);
      ctx.save(); ctx.beginPath(); ctx.rect(ox, oy, LW * k, LH * k); ctx.clip(); // hi-res bodies stay inside the view (no spill into the letterbox)
      drawFeltHi(k, mm => mm.y <= hero.y); drawPetHi(k, false); drawHeroHi(k); drawPetHi(k, true); drawFeltHi(k, mm => mm.y > hero.y); if (!SLASH_BODY) gkDraw(k); /* 검기 above the mobs it hits */ ctx.restore(); drawHiRes(k, ox, oy);
    }
    if (tr) { let a = 1;
      if (tr.phase === 'out') a = Math.min(1, tr.t / FADE); else if (tr.phase === 'in') a = 1 - Math.min(1, tr.t / FADE);
      if (tr.phase === 'card' && tr.cardData) drawCard(tr, k); else { ctx.fillStyle = `rgba(0,0,0,${a})`; ctx.fillRect(0, 0, CW, CH); }
    }
  }
  function drawLow() {
    const g = lx, m = M();
    let cx = Math.round(S.cam[0]), cy = Math.round(S.cam[1]);
    if (S.shake > 0) { cx += Math.round((Math.random() - .5) * S.shake * 2); cy += Math.round((Math.random() - .5) * S.shake * 2); }
    S.camI = [cx, cy];
    g.setTransform(1, 0, 0, 1, 0, 0); g.imageSmoothingEnabled = false; g.fillStyle = m.type === 'world' ? '#0b2a5a' : '#06070a'; g.fillRect(0, 0, LW, LH);
    g.drawImage(m.groundC, -cx, -cy);
    g.translate(-cx, -cy);
    if (m.type === 'world') { drawWorldNodes(g, m); drawHeroSprite(g, WORLD_ZOOM); g.setTransform(1, 0, 0, 1, 0, 0); return; }
    for (const o of m.objs) drawObjTile(g, m, o);
    if (NAV()) NAV().drawGround(g, cx, cy);                  // guide route breadcrumbs
    for (const h of S.hazards) drawHazard(g, h, false);     // telegraphs on the floor, under sprites
    const list = [];                                         // y-sorted sprites
    for (const d of m.decos) if (!d.broken && d.x > cx - 40 && d.x < cx + LW + 40 && d.y > cy - 10 && d.y < cy + LH + 70) list.push({ y: d.y, f: () => drawSpr(g, d.spr, d.x, d.y + 1) });
    for (const o of m.objs) {
      if (o.type === 'chest') list.push({ y: o.y + 6, f: () => drawSpr(g, SAVE.chests[o.id] ? 'chest_open' : 'chest', o.x, o.y + 7) });
      if (o.type === 'sign') list.push({ y: o.y + 6, f: () => drawSpr(g, 'sign', o.x, o.y + 8) });
      if (o.type === 'heal') list.push({ y: o.y + 6, f: () => drawBench(g, o) });
      if (o.type === 'door_deco') list.push({ y: o.y - 8, f: () => drawSpr(g, o.sprite, o.x, o.y + 8) });
      if (o.type === 'hidden' && !SAVE.chests[o.id] && Math.sin(S.t * 3 + o.x) > .8) list.push({ y: o.y, f: () => { g.fillStyle = '#fff8c0'; g.fillRect(o.x - 1, o.y - 7, 2, 3); g.fillRect(o.x - 3, o.y - 6, 6, 1); } });
      if (o.type === 'warp') list.push({ y: o.y, f: () => drawWarp(g, o) });
      if (o.type === 'npc') list.push({ y: o.y + 6, f: () => { const im = o.art && npcImg(o.art);
        if (im && im.complete && im.naturalWidth) { const h = o.h || 26, w = im.naturalWidth * h / im.naturalHeight; g.drawImage(im, Math.round(o.x - w / 2), Math.round(o.y + 7 - h), w, h); }
        else drawSpr(g, o.sprite || 'npc_bard', o.x, o.y + 7);
        if (o.main) { g.fillStyle = '#ffe08a'; g.fillRect(Math.round(o.x) - 1, Math.round(o.y + 7 - (o.h || 26)) - 4, 2, 2); } } });
      if (o.type === 'waystone') list.push({ y: o.y + 6, f: () => drawWaystone(g, o) });
    }
    for (const t of S.temp) list.push({ y: t.y + 3, f: () => drawSpr(g, 'crystal', t.x, t.y + 5, { alpha: Math.min(1, t.life * 3) }) });
    for (const mm of S.mobs) if (!mm.dead) list.push({ y: mm.y + (mm.D.hover ? 8 : 0), f: () => drawMob(g, mm) });
    list.push({ y: hero.y, f: () => drawHeroSprite(g, 1) });
    for (const f of S.fx) if (f.type === 'heart') list.push({ y: f.y, f: () => drawHeartPick(g, f) });
    list.sort((a, b) => a.y - b.y).forEach(o => o.f());
    for (const s of S.shots) drawShot(g, s);
    for (const h of S.hazards) drawHazard(g, h, true);
    for (const f of S.fx) drawFx(g, f);
    if (m.dark) { // dungeon darkness, light around the hero, torches and crystals
      const D = darkLayer(), d = D.getContext('2d'); d.setTransform(1, 0, 0, 1, 0, 0); d.globalCompositeOperation = 'source-over'; d.clearRect(0, 0, LW, LH);
      d.fillStyle = `rgba(4,6,12,${m.dark})`; d.fillRect(0, 0, LW, LH); d.globalCompositeOperation = 'destination-out';
      const light = (x, y, r) => { const gr = d.createRadialGradient(x - cx, y - cy, 0, x - cx, y - cy, r); gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(.6, 'rgba(0,0,0,.7)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); d.fillStyle = gr; d.fillRect(x - cx - r, y - cy - r, r * 2, r * 2); };
      light(hero.x, hero.y - 10, 100);
      for (const o of m.objs) if (o.type === 'torch') light(o.x, o.y + 8, 50 + Math.sin(S.t * 9 + o.x) * 3);
      for (const dd of m.decos) if (dd.spr === 'crystal') light(dd.x, dd.y - 6, 26);
      for (const mm of S.mobs) if (mm.D.boss) light(mm.x, mm.y - 30, 70);
      g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(D, 0, 0); g.translate(-cx, -cy);
      g.globalCompositeOperation = 'lighter'; for (const o of m.objs) if (o.type === 'torch') { g.fillStyle = `rgba(255,140,40,${.12 + Math.sin(S.t * 11 + o.x) * .03})`; g.beginPath(); g.arc(o.x, o.y + 6, 15, 0, TAU); g.fill(); } g.globalCompositeOperation = 'source-over'; }
    if (S.ult) drawUlt(g, S.ult);
    g.setTransform(1, 0, 0, 1, 0, 0);
  }
  let _dark = null; function darkLayer() { if (!_dark) { _dark = document.createElement('canvas'); _dark.width = LW; _dark.height = LH; } return _dark; }
  let _ultC = null;
  function drawWaystone(g, o) { const on = SAVE.waystones[o.id], p = .5 + .5 * Math.sin(S.t * 3);
    g.fillStyle = 'rgba(0,0,0,.3)'; g.beginPath(); g.ellipse(o.x, o.y + 6, 8, 3, 0, 0, TAU); g.fill();
    g.fillStyle = '#6c6f7a'; g.fillRect(o.x - 5, o.y - 12, 10, 18); g.fillStyle = '#8d909c'; g.fillRect(o.x - 5, o.y - 12, 10, 3); g.fillStyle = '#4a4c55'; g.fillRect(o.x + 3, o.y - 9, 2, 15);
    g.fillStyle = on ? `rgba(120,230,255,${.7 + .3 * p})` : '#3a5060'; g.fillRect(o.x - 2, o.y - 8, 4, 8); g.fillRect(o.x - 1, o.y - 10, 2, 12);
    if (on) { g.fillStyle = `rgba(120,230,255,${.15 + .1 * p})`; g.beginPath(); g.arc(o.x, o.y - 4, 12, 0, TAU); g.fill(); } }
  function drawBench(g, o) { g.fillStyle = '#4a2c14'; g.fillRect(o.x - 9, o.y - 2, 18, 3); g.fillStyle = '#9a6a34'; g.fillRect(o.x - 9, o.y - 5, 18, 3); g.fillStyle = '#3a2210'; g.fillRect(o.x - 8, o.y + 1, 2, 5); g.fillRect(o.x + 6, o.y + 1, 2, 5); }
  function drawWarp(g, o) { for (let i = 0; i < 3; i++) { g.strokeStyle = `rgba(160,255,190,${.7 - i * .18})`; g.lineWidth = 1; g.beginPath(); g.ellipse(o.x, o.y, 8 + i * 3 + Math.sin(S.t * 4 + i) * 1.5, 4 + i * 1.5, 0, 0, TAU); g.stroke(); }
    g.fillStyle = 'rgba(200,255,220,.6)'; for (let i = 0; i < 3; i++) g.fillRect(o.x - 6 + i * 6, o.y - 4 - ((S.t * 20 + i * 7) % 16), 1, 4); }
  function drawHeartPick(g, f) { const b = Math.sin(f.t * 6) * 1.5; g.fillStyle = '#e0201c'; g.beginPath(); g.arc(f.x - 2, f.y - 6 + b, 2.2, 0, TAU); g.arc(f.x + 2, f.y - 6 + b, 2.2, 0, TAU); g.fill(); g.beginPath(); g.moveTo(f.x - 4.2, f.y - 5.5 + b); g.lineTo(f.x, f.y - 1 + b); g.lineTo(f.x + 4.2, f.y - 5.5 + b); g.fill(); }
  function drawObjTile(g, m, o) {
    const put = (n, a = 1) => { const p = tileXY('dungeon', n); if (!p) return; g.globalAlpha = a; g.drawImage(IMG.dungeon, p[0], p[1], 16, 16, o.tx * m.T, o.ty * m.T, m.T, m.T); g.globalAlpha = 1; };
    if (o.type === 'spikes') { put('floor'); if (spikeUp(o)) put('spikes'); else if (spikeWarn(o)) put('spikes', .3 + .25 * Math.sin(S.t * 30)); else put('plate_down', .55); }
    if (o.type === 'door_locked') drawSpr(g, o.open ? 'doorway_big' : 'door_big', o.x, o.y + 8);
    if (o.type === 'gate') drawSpr(g, o.open ? 'doorway_big' : 'gate_big', o.x, o.y + 8);
    if (o.type === 'boss_door') { const ok = ['champ_boar', 'champ_wasp'].every(f => SAVE.flags[f]); drawSpr(g, ok ? 'doorway_big' : 'gate_big', o.x, o.y + 8);
      g.fillStyle = ok ? 'rgba(120,255,160,.7)' : `rgba(255,60,60,${.45 + .25 * Math.sin(S.t * 3)})`; g.fillRect(o.x - 3, o.y - 24, 6, 4); }
    if (o.type === 'lever') { put('floor'); g.fillStyle = '#3a3a44'; g.fillRect(o.x - 5, o.y + 2, 10, 4); g.strokeStyle = '#c8a860'; g.lineWidth = 2; g.beginPath(); g.moveTo(o.x, o.y + 3); g.lineTo(o.x + (o.on ? 6 : -6), o.y - 6); g.stroke(); g.fillStyle = o.on ? '#6f6' : '#f55'; g.fillRect(o.x + (o.on ? 5 : -8), o.y - 9, 3, 3); }
    if (o.type === 'key' && !SAVE.keys[o.keyId]) { put('key_floor'); if (Math.sin(S.t * 5) > .6) { g.fillStyle = '#fff8c0'; g.fillRect(o.x + 3, o.y - 5, 2, 2); } }
    if (o.type === 'torch') { put('torch'); g.fillStyle = Math.sin(S.t * 13 + o.x) > 0 ? '#ffd040' : '#ff8a20'; g.fillRect(o.x - 1, o.y - 5, 2, 2); }
  }
  function spawnHW(dir) { const w = spOf(5).wave || {}; S.hw = S.hw || []; const v = (w.speed || 560) * .3; S.hw.push({ x: hero.x, y: hero.y - 6, vx: Math.cos(dir) * v, vy: Math.sin(dir) * v * .8, d: 0, R: (w.range || 260) * .3, rad: (w.rad || 28) * .3, dmg: ATK_DMG[0] * (w.dmgMul || 1), hit: new Set(), map: S.map }); sfx('wave', .7); }
  function stepHW(dt) { if (!S.hw) return; for (let i = S.hw.length - 1; i >= 0; i--) { const w = S.hw[i]; w.x += w.vx * dt; w.y += w.vy * dt; w.d += Math.hypot(w.vx, w.vy) * dt;
      if (w.map !== S.map || w.d > w.R || solidAt(w.x, w.y + 6)) { S.hw.splice(i, 1); continue; }
      for (const mm of S.mobs) { if (mm.dead || w.hit.has(mm)) continue; const mh = (mm.D.h || 20) * (mm.scale || 1); if (Math.hypot(mm.x - w.x, (mm.y - mh * .3) - w.y) < w.rad + mm.r) { w.hit.add(mm); hitMob(mm, w.dmg, Math.atan2(w.vy, w.vx)); } } } }
  function drawHW(g) { if (!S.hw) return; for (const w of S.hw) { const al = Math.max(0, 1 - w.d / w.R), a = Math.atan2(w.vy / .8, w.vx); g.save(); g.translate(w.x, w.y); g.scale(1, .8); g.rotate(a); g.lineCap = 'round';
      g.strokeStyle = `rgba(255,214,110,${.8 * al})`; g.lineWidth = 4; g.beginPath(); g.arc(-3, 0, 10, -1.1, 1.1); g.stroke(); g.strokeStyle = `rgba(255,255,255,${al})`; g.lineWidth = 1.5; g.beginPath(); g.arc(-3, 0, 10, -1, 1); g.stroke(); g.restore(); } }
  function drawCharge(g) { const C = hero.charge; if (!C) return; const lv = C.lv, col = lv > 1 ? '255,214,110' : lv ? '140,215,255' : '255,255,255', pul = .5 + .5 * Math.sin(C.t * (lv > 1 ? 22 : 14)), r = (lv > 1 ? 13 : lv ? 11 : 8) + pul * 1.5, cx = hero.x, cy = hero.y - 10; // white -> lv1 blue -> lv2 gold
    g.save(); g.globalCompositeOperation = 'lighter'; const gr = g.createRadialGradient(cx, cy, 1, cx, cy, r); gr.addColorStop(0, `rgba(${col},${Math.min(1, .35 + .25 * pul + C.flash * 2)})`); gr.addColorStop(1, `rgba(${col},0)`); g.fillStyle = gr; g.beginPath(); g.ellipse(cx, cy, r * .8, r, 0, 0, TAU); g.fill();
    const n = (lv + 1) * 3; g.fillStyle = `rgba(${col},.95)`; for (let i = 0; i < n; i++) { const a = C.t * 5 + i * TAU / n, d = r * (1 - ((C.t * 2.2 + i * .37) % 1)); g.fillRect(cx + Math.cos(a) * d - .6, cy + Math.sin(a) * d * .8 - .6, 1.2, 1.2); } g.restore(); }
  function heroFrameName() { const h = hero, d = h.face === 'left' ? 'right' : h.face, D = DG(); let fi = h.moving || h.roll ? Math.floor(h.walkT * 8) % 4 : 0;
    if (h.roll && D && D.frames && D.frames.world) { const p = h.roll.t / rollDur(), ph = D.frames.world.find(f => p <= f.until); if (ph) fi = ph.frame; } return 'hero_' + d + '_' + fi; }
  function tickTrail(dt) { if (!S.trail) return; for (const a of S.trail) a.t += dt; S.trail = S.trail.filter(a => a.t < a.life); }
  // ---- test128: 128px hero drawn in the hi-res pass (fields/dungeons; the overworld map keeps the tiny sprite) ----
  const H128FIG = 30; // figure height in field px (tile 16): about the old hero's 28px
  function h128() { const g = window.__game; return g && g.H128 && g.H128img && g.H128img.complete ? g : null; }
  function h8Cell() { const G = h128(), H = G.H8, h = hero; if (!H || !G.H8img(0) || (S.deadT > 0 && !H.anims.death_down)) return null; const f8 = h.f8 && h.f8.includes(h.face) ? h.f8 : (h.face || 'down');
    const sd = /^(right|left|up|down)$/.test(f8) ? f8 : (f8.includes('right') ? 'right' : 'left'), L8 = H.left && sd === 'left', fl = sd === 'left' && !L8, d = L8 ? 'left' : fl ? 'right' : sd; // 4-way sprite, diagonals = side; hero v4 has real left frames (else left = mirror)
    const A = k => H.anims[k + '_' + d] || H.anims[k + '_' + (String(h.f8 || '').includes('left') && H.anims[k + '_left'] ? 'left' : 'right')], /* hurt has side views only: facing up/down used to crash */ seq = (L, t) => { let i = 0; for (; i < L.length - 1; i++) { if (t < L[i][2]) break; t -= L[i][2]; } return L[i]; }, tot = L => L.reduce((a, f) => a + f[2], 0); let e;
    { const dx = h.x - (h.gx ?? h.x), dy = h.y - (h.gy ?? h.y), m = Math.hypot(dx, dy); h.gx = h.x; h.gy = h.y; if (m < 20 && h.moving) h.gp = ((h.gp || 0) + m / (h.run ? (H.gait && H.gait.runCyc ? H.gait.runCyc * 46 / 119 : 46) : (H.gait && H.gait.walkCyc ? H.gait.walkCyc * 32 / 84 : 32))) % 1; } // gait phase by distance (town 84 / 119 px per cycle x 30/78 field scale)
    if (S.deadT > 0) e = seq(A('death'), S.deadT * 60);
    else if (h.atk && SLASH_BODY) { const i = h.atk.i, AT = atkT(i), L = A(i === 3 ? 'hit1' : i >= 4 || i === 2 ? 'hit3' : i === 1 ? 'hit2' : 'hit1'); e = seq(L, Math.min(.999, h.atk.t / AT.dur) * tot(L)); }
    else if (h.charge) e = A('hold')[0];
    else if (h.roll) { const L = A('dash'); e = seq(L, h.roll.t / rollDur() * tot(L)); }
    else if (hero.inv > .67 && S.scene !== 'world') { const L = A('hurt'); e = seq(L, (1 - hero.inv) * 60); }
    else if (h.moving) { const L = A(h.run ? 'run' : 'walk'); e = L[Math.floor((h.gp || 0) * L.length) % L.length]; }
    else if (H.v4) { const L = A('idle'); e = seq(L, (S.t * 60) % tot(L)); }
    else e = A('idle')[0];
    if (!e) return null; const c = H.cells[e[0]][e[1]].slice(); c.h8 = e[0]; c.fl = fl; return c; }
  function h128Cell() { { const c8 = h8Cell(); if (c8) return c8; } const G = h128(), H = G.H128, h = hero, dir = h.face || 'down'; let an = 'idle', p = null, tick = S.t * 60 / 8;
    if (S.deadT > 0) { an = 'death'; p = Math.min(1, S.deadT / 1.2); }
    else if (h.atk) { const i = h.atk.i, AT = atkT(i); an = i >= 4 || i === 2 ? 'attack3' : i === 1 ? 'attack2' : 'attack1'; const k = AT.a1 / AT.dur; const q = h.atk.t / AT.dur; p = q < AT.a0 / AT.dur ? .25 * q / (AT.a0 / AT.dur) : q < k ? .25 + .35 * (q - AT.a0 / AT.dur) / Math.max(1e-6, k - AT.a0 / AT.dur) : .6 + .4 * Math.min(1, (q - k) / Math.max(1e-6, 1 - k)); }
    else if (h.charge) { an = 'attack3'; p = .1; }
    else if (h.roll) { an = 'dodge'; p = Math.min(1, h.roll.t / rollDur()); }
    else if (hero.inv > .75 && S.scene !== 'world') { an = 'hurt'; tick = (1 - hero.inv) * 20; }
    else if (h.moving) { an = h.run && H.anims['run_' + dir] ? 'run' : 'walk'; tick = h.walkT * (h.run ? 14 : 11); }
    const L = H.anims[an + '_' + dir] || H.anims[an + '_down'], n = L.length;
    let f = p != null ? Math.min(n - 1, Math.floor(p * n)) : (an === 'idle' ? Math.floor(tick) % n : (an === 'walk' || an === 'run') ? 1 + Math.floor(tick) % (n - 1) : Math.min(n - 1, Math.floor(tick)));
    return H.cells[L[f]]; }
  function drawH128(c, x, y, k, alpha, tint) { const G = h128(); let im = tint ? (G.H128tint || {})[tint] : G.H128img; if (c.h8 !== undefined) { im = G.H8img(c.h8); if (im && tint) { const t = G.h8tinted(im, c, tint); return drawH128Raw(t, [0, 0, c[2], c[3], c[4], c[5]], x, y, k, alpha, c.fl); } } if (!im) return; return drawH128Raw(im, c, x, y, k, alpha, c.fl); }
  function drawH128Raw(im, c, x, y, k, alpha, fl) { const sc = k * H128FIG / 117, [sx, sy] = W2S(x, y);
    ctx.save(); ctx.globalAlpha = alpha; ctx.imageSmoothingEnabled = sc < 1; if (fl) { ctx.translate(Math.round(sx), 0); ctx.scale(-1, 1); ctx.drawImage(im, c[0], c[1], c[2], c[3], -Math.round(c[4] * sc), Math.round(sy - c[5] * sc), Math.round(c[2] * sc), Math.round(c[3] * sc)); } else ctx.drawImage(im, c[0], c[1], c[2], c[3], Math.round(sx - c[4] * sc), Math.round(sy - c[5] * sc), Math.round(c[2] * sc), Math.round(c[3] * sc)); ctx.restore(); }
  // ---- 검기 (owner 10-22 "검 베는 모션은 안쓰려구" / "최종 샌드박스 검기만 나가고 있어"): the attack no longer plays the slash body clips;
  // the hero keeps the idle/walk pose with a small code-made kick (lean back -> snap forward + squash), and the sword energy arcs of the
  // 주인공 / 몬스터 샌드박스 (hero_slash_a v1) fly out. Arc art is generated in code (sArc), in atlas px, drawn at the hero's hi-res scale.
  const SLASH_BODY = false; // true = old slash clips (hit1-3)
  const GK = [{ R: 52, span: 140, T: 18, rot: 0, y: 78, fwd: 22, v: 4, rev: 0, sq: .5 }, { R: 54, span: 140, T: 18, rot: 35, y: 90, fwd: 22, v: 4, rev: 1, sq: .75 }, { R: 72, span: 170, T: 26, rot: 0, y: 74, fwd: 22, v: 3, rev: 0, sq: 1 }];
  const GK_LIFE = 13, GK_STEP = .8, sCache = new Map();
  function sField(R, span, T, head, tail, ca, sa, rev, sq, flip, x, y) { if (flip) x = -x; const xr = x * ca + y * sa, yr = (-x * sa + y * ca) / sq, r = Math.hypot(xr, yr); let u = (Math.atan2(yr, xr) * 180 / Math.PI + span / 2) / span; if (rev) u = 1 - u;
    if (u < tail || u > head || u < 0 || u > 1) return null; const k = Math.min(1, Math.max(0, (u - tail) / Math.max(head - tail, 1e-3))), w = T * Math.pow(Math.sin(Math.PI * u), .6) * (.15 + .85 * Math.pow(k, 1.3)); return [k, w, r - R + w * .35]; }
  function sArc(R, span, T, head, tail, rot, rev, sq, flip) { const key = [R, span, T, head, tail, rot, rev, sq, flip].map(v => Math.round(v * 100)).join('|'); let c2 = sCache.get(key); if (c2) return c2;
    if (sCache.size > 400) sCache.clear(); const N = Math.ceil(2 * R + 2 * T + 30), c = N / 2; c2 = document.createElement('canvas'); c2.width = c2.height = N; const g = c2.getContext('2d'), id = g.createImageData(N, N), d = id.data, an = rot * Math.PI / 180, ca = Math.cos(an), sa = Math.sin(an);
    for (let py = 0; py < N; py++) for (let px = 0; px < N; px++) { const x = px - c, y = py - c, i = (py * N + px) * 4; let f = sField(R, span, T, head, tail, ca, sa, rev, sq, flip, x, y), cr = 0, cg = 0, cb = 0, al = 0;
      if (f) { const [k, w, dd] = f, ad = Math.abs(dd); if (ad < w / 2 + 6) { cr = 40; cg = 110; cb = 255; al = 40 + 80 * k; } if (ad < w / 2) { cr = 90 + 165 * k * k; cg = 190 + 65 * k; cb = 255; al = 230; } if ((ad < w / 5 && k > .25) || (dd > w / 2 - 1.5 && dd < w / 2 && k > .4)) { cr = cg = cb = 255; al = 255; } }
      if (al < 230) { const e = sField(R * .78, span * .85, T * .45, head * .95, tail + .1, ca, sa, rev, sq, flip, x, y); if (e && Math.abs(e[2]) < e[1] / 2) { cr = 150; cg = 225; cb = 255; al = Math.max(al, 180 * e[0]); } }
      if (al) { d[i] = cr; d[i + 1] = cg; d[i + 2] = cb; d[i + 3] = al; } }
    g.putImageData(id, 0, 0); sCache.set(key, c2); return c2; }
  // owner 10-23 "검흔 문제점": the hit used to reach 2-3x past the drawn arc (old painted-slash hitbox) and land before the arc flew.
  // Now each arc flies out to the hit range (hbR) in GK_FLY steps and hits a mob only when its front passes it; diagonal input = 45° arc.
  const GK_FLY = 8, GK_K = H128FIG / 117; // arc steps to reach the hit range; atlas px -> field px
  function gkDir() { const f8 = hero.f8 && hero.f8.includes(hero.face) ? hero.f8 : null; if (f8 && f8 !== hero.face) { const a = DIR8.indexOf(f8) * Math.PI / 4; return [Math.cos(a), Math.sin(a)]; } return FACEV[hero.face] || [1, 0]; }
  // owner 10-23 "게임을 좀 어렵게 / 검기 판정 줄여": the hit reaches about as far as the drawn arc (was 67 / 49 / 62 px, 150-170°) and only in front
  const GK_REACH = [40, 38, 46], GK_ARC = [100, 110, 120]; // field px per combo hit 1-3 (specials 3+ keep hbR), degrees
  function gkSpawn(i) { const v = gkDir(), l = Math.hypot(v[0], v[1]) || 1, dx = v[0] / l, dy = v[1] / l, n = Math.min(2, i), Y = GK[n], reach = i <= 2 ? GK_REACH[i] : hbR(i);
    const sp = Math.max(Y.v, (reach / GK_K - Y.fwd - Y.R * (1 + .025 * GK_FLY)) / GK_FLY);
    S.gk = S.gk || []; S.gk.push({ n, i, dir: [dx, dy], v: sp, reach, cosA: Math.cos((i <= 2 ? GK_ARC[i] : hbA(i)) / 2 * Math.PI / 180), hit: new Set(), rx: dx * Y.fwd, ry: Math.abs(dx) < .1 ? -44 + dy * (Y.fwd + 20) : -Y.y + dy * 20, t: 0, seed: (Math.random() * 2147483646 | 0) + 1, map: S.map }); }
  function gkHits(f) { const a = f.t * GK_STEP; if (a > GK_FLY + 1) return; const Y = GK[f.n], front = Math.min(f.reach, GK_K * (Y.fwd + Y.R * (1 + .025 * a) + a * f.v)), [dx, dy] = f.dir;
    for (const mm of S.mobs) { if (mm.dead || f.hit.has(mm)) continue; const mh = (mm.D.h || 20) * (mm.scale || 1), pad = mm.r + mh * .2;
      const ddx = mm.x - hero.x, ddy = ((mm.y - mh * .3) - (hero.y - 4)) / .8, dd = Math.hypot(ddx, ddy);
      if (dd < front + pad && (dd < 6 || (ddx * dx + ddy * dy) / dd >= f.cosA)) { f.hit.add(mm); S.gkImp = S.gkImp || []; S.gkImp.push({ x: mm.x, y: mm.y - mh * .45, t: 0, big: f.i >= 2 });
        hitMob(mm, f.i >= 3 ? ATK_DMG[0] * (spOf(f.i).dmgMul || 1) : ATK_DMG[Math.min(2, f.i)], Math.atan2(mm.y - hero.y, mm.x - hero.x), true); if (f.i >= 3) sfx(f.i === 5 ? 'hit_crit' : 'hit_heavy', .8); } } }
  function gkTick() { if (S.gk) { for (const f of S.gk) { f.t++; if (f.map === S.map && S.scene !== 'world') gkHits(f); } S.gk = S.gk.filter(f => f.t * GK_STEP <= GK_LIFE + 3 && f.map === S.map); } if (S.gkImp) { for (const m of S.gkImp) m.t++; S.gkImp = S.gkImp.filter(m => m.t < 10); } }
  function gkArcDraw(ctx, f) { // one arc at the local origin (hero feet), atlas px; shared with the town (window.GKART)
    const a = f.t * GK_STEP, Y = GK[f.n], head = Math.min(1, (a + 1) / 2.5), tail = a < 4 ? 0 : Math.min(1, (a - 4) / 7), [dx, dy] = f.dir, fl = dx < 0;
      const ox = f.rx + dx * a * f.v, oy = f.ry + dy * a * f.v; // rides with the hero and flies forward
      if (tail < head) { const ang = Math.atan2(dy, Math.abs(dx)) * 180 / Math.PI, T = Y.T * (a < 6 ? 1 : Math.max(.35, 1 - (a - 6) / 7)), q = v => Math.round(v * 4) / 4;
        const im = sArc(Y.R * (1 + .025 * q(a)), Y.span, T, q(head), q(tail), Y.rot + ang * (fl ? -1 : 1), Y.rev, Y.sq, fl); ctx.drawImage(im, Math.round(ox - im.width / 2), Math.round(oy - im.height / 2)); }
      const nx = -dy, ny = dx, big = f.n === 2; let sd = f.seed; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
      const la = Math.max(0, 1 - a / 8); if (la > 0) { ctx.fillStyle = `rgba(200,240,255,${.86 * la})`; for (let i = 0; i < (big ? 7 : 4); i++) { const o = rnd() * 60 - 30, L = 14 + rnd() * 20, b = Y.R * .4 - rnd() * 30 + a * 5; for (let j = 0; j < L; j++) ctx.fillRect(Math.round(ox + dx * (b + j) + nx * o), Math.round(oy + dy * (b + j) + ny * o), 1, 1); } } // speed lines
      const tx = ox + dx * Y.R * .95, ty = oy + dy * Y.R * .95;
      if (a <= 3) { const L = (big ? 10 : 7) * (1 - a / 4) + 3, al = 1 - a / 4; ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.fillRect(Math.round(tx - L), Math.round(ty) - 1, Math.round(2 * L), 2); ctx.fillRect(Math.round(tx), Math.round(ty - L * .6), 1, Math.round(L * 1.2)); ctx.fillStyle = `rgba(220,245,255,${al})`; ctx.beginPath(); ctx.arc(tx, ty, 3, 0, TAU); ctx.fill(); }
      if (a >= 1) { ctx.fillStyle = `rgba(220,250,255,${Math.max(0, 1 - a * 28 / 255)})`; const ba = Math.atan2(dy, dx); for (let i = 0; i < (big ? 14 : 8); i++) { const g = ba + rnd() * 2.6 - 1.3, L = a * (2 + rnd() * 3); ctx.fillRect(Math.round(tx + Math.cos(g) * L), Math.round(ty + Math.sin(g) * L), 2, 2); } } }
  window.GKART = { GK, STEP: GK_STEP, LIFE: GK_LIFE, FLY: GK_FLY, K: GK_K, REACH: GK_REACH, ARC: GK_ARC, draw: gkArcDraw };
  function gkDraw(k) { if ((!S.gk || !S.gk.length) && (!S.gkImp || !S.gkImp.length)) return; const sc = k * H128FIG / 117, [hx0, hy0] = W2S(hero.x, hero.y);
    ctx.save(); ctx.translate(Math.round(hx0), Math.round(hy0)); ctx.scale(sc, sc); ctx.imageSmoothingEnabled = false;
    for (const f of S.gk || []) gkArcDraw(ctx, f);
    ctx.restore();
    for (const m of S.gkImp || []) { const a = m.t, al = 1 - a / 10; if (al <= 0) continue; const [x, y] = W2S(m.x, m.y); ctx.save(); ctx.translate(Math.round(x), Math.round(y)); ctx.scale(sc, sc); // impact: ring + cross flash
      ctx.strokeStyle = `rgba(220,245,255,${al})`; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(0, 0, 4 + a * (m.big ? 4 : 3), 0, TAU); ctx.stroke();
      if (a < 4) { const L = (m.big ? 18 : 12) * (1 - a / 5); ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.fillRect(-L, -1, 2 * L, 2); ctx.fillRect(-1, -L, 2, 2 * L); } ctx.restore(); } }
  function gkKick(a) { const AT = atkT(a.i), u = a.t; return u < AT.a0 ? { x: -2 * u / Math.max(AT.a0, 1e-3), sq: 1 } : { x: 4 * Math.exp(-(u - AT.a0) * 14), sq: 1 - .05 * Math.exp(-(u - AT.a0) * 14) }; } // atlas px: lean back, snap forward, squash
  function drawHeroHi(k) { if (!h128() || !S.map || S.map.type === 'world') return; const h = hero;
    if (S.trail) for (const a of S.trail) if (a.c128) { const q = 1 - a.t / a.life; drawH128(a.c128, a.x, a.y, k, q * q * a.a, 'dodge'); }
    if (h.inv > 0 && Math.floor(h.inv * 20) % 2 && !h.roll && S.deadT <= 0) return;
    let kx = 0, ky = 0, sq = 1; if (h.atk && !SLASH_BODY) { const K = gkKick(h.atk), v = FACEV[h.face] || [1, 0], f = H128FIG / 117; kx = v[0] * K.x * f; ky = v[1] * K.x * f * .5; sq = K.sq; }
    const [fx, fy] = W2S(h.x + kx, h.y + ky); ctx.save(); ctx.translate(fx, fy); ctx.scale(1 + (1 - sq) * .6, sq); ctx.translate(-fx, -fy);
    drawH128(h128Cell(), h.x + kx, h.y + ky, k, 1, null); if (h.inv > .8 && !h.roll) drawH128(h128Cell(), h.x + kx, h.y + ky, k, .5, 'white'); ctx.restore();
    if (h.atk && !h128().H8) drawSlashHi(k); if (h.atk) drawHB(ctx, k); } // hero8 attack frames carry their own painted slash trail
  function drawSlashHi(k) { const a = hero.atk, AT = atkT(a.i), p = a.t / AT.dur, dv = FACEV[hero.face], base = Math.atan2(dv[1], dv[0]); if (p > (a.i === 2 ? .9 : .85)) return;
    const G = h128(), SL = (G.H128.slash || {}), hs = SL[a.i >= 2 ? 'hit3' : a.i === 1 ? 'hit2' : 'hit1'] || {}, pv = (SL.pivot || {})[hero.face] || [0, -34], f = H128FIG / 78; // town px -> field px via figure ratio
    const sweep = (a.i % 2 ? -1 : 1), half = arcW(a.i) / 2 * Math.PI / 180, a0 = base - sweep * half, a1 = a0 + sweep * 2 * half * Math.min(1, p / (AT.a1 / AT.dur));
    const [sx, sy] = W2S(hero.x + pv[0] * f, hero.y + pv[1] * f), r = (hs.r || 52) * f * k, wm = (hs.w || 1) * k / 5, R = (swingR(a.i) - 2) * k;
    ctx.save(); ctx.translate(sx, sy); ctx.scale(1, .78); ctx.lineCap = 'round';
    ctx.fillStyle = 'rgba(120,220,255,.07)'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, R, Math.min(a0, a1), Math.max(a0, a1)); ctx.closePath(); ctx.fill();
    for (const [w, c, rr] of [[16 * wm, 'rgba(120,220,255,.35)', r], [7 * wm, a.i === 2 ? 'rgba(255,236,150,.95)' : 'rgba(255,255,255,.92)', r], [2.5 * wm, 'rgba(120,220,255,1)', r - 8 * k / 5]]) { ctx.strokeStyle = c; ctx.lineWidth = w; ctx.beginPath(); ctx.arc(0, 0, rr, Math.min(a0, a1), Math.max(a0, a1)); ctx.stroke(); }
    ctx.restore(); }
  function drawHeroSprite(g, zoom) {
    if (zoom === 1) { drawHW(g); drawCharge(g); }
    const h = hero; if (h.inv > 0 && S.scene !== 'world' && Math.floor(h.inv * 20) % 2 && !h.roll) return;
    const d = h.face === 'left' ? 'right' : h.face; const fi = h.moving || h.roll ? Math.floor(h.walkT * 8) % 4 : 0;
    const name = 'hero_' + d + '_' + fi;
    g.fillStyle = 'rgba(0,0,0,.28)'; g.beginPath(); g.ellipse(h.x, h.y, 6 * zoom + 1, 2.5 * zoom + .5, 0, 0, TAU); g.fill();
    if (zoom === 1 && h128() && S.map && S.map.type !== 'world') return; // test128: body + trail + slash drawn by drawHeroHi
    if (S.trail) for (const a of S.trail) { const q = 1 - a.t / a.life; drawSpr(g, a.name, a.x, a.y, { flip: a.flip, alpha: q * q * a.a, mode: 'dodge' }); } // dash afterimages
    if (h.roll) { if (DG()) { drawSpr(g, heroFrameName(), h.x, h.y, { flip: h.face === 'left' }); if (h.roll.t < iframe()) { g.fillStyle = 'rgba(160,240,255,.22)'; g.beginPath(); g.ellipse(h.x, h.y - 9, 8, 10, 0, 0, TAU); g.fill(); } return; }
      const p = h.roll.t / ROLL.dur; // legacy tumble (no dodge config)
      for (let i = 1; i <= 2; i++) drawSpr(g, name, h.x - h.roll.dx * i * 6, h.y - h.roll.dy * i * 6, { flip: h.face === 'left', alpha: .25 / i, sy: .7, mode: 'white' });
      drawSpr(g, name, h.x, h.y, { flip: h.face === 'left', sy: .62 + .3 * Math.abs(Math.cos(p * Math.PI * 2)), rot: (h.roll.dx >= 0 ? 1 : -1) * Math.sin(p * Math.PI) * .5 });
      if (h.roll.t < iframe()) { g.fillStyle = 'rgba(160,240,255,.3)'; g.beginPath(); g.ellipse(h.x, h.y - 9, 9, 11, 0, 0, TAU); g.fill(); }
      return; }
    if (zoom !== 1) { drawSmallHero(g, name, h.x, h.y, zoom); return; }
    drawSpr(g, name, h.x, h.y, { flip: h.face === 'left', mode: (h.inv > .8 && S.scene !== 'world') ? 'white' : null });
    if (h.atk) drawSlash(g); if (h.atk && !h128()) drawHB(g);
  }
  const smallCache = {};
  function drawSmallHero(g, name, x, y, z) { // world map: pre-scaled with smoothing so the tiny hero stays readable
    const key = name + z; let c = smallCache[key];
    if (!c) { const r = ATLAS.sprites.rects[name]; c = document.createElement('canvas'); c.width = Math.max(1, Math.round(r[2] * z)); c.height = Math.max(1, Math.round(r[3] * z));
      const cg = c.getContext('2d'); cg.imageSmoothingEnabled = true; cg.imageSmoothingQuality = 'high'; cg.drawImage(IMG.spr, r[0], r[1], r[2], r[3], 0, 0, c.width, c.height);
      const d = cg.getImageData(0, 0, c.width, c.height); for (let i = 3; i < d.data.length; i += 4) d.data[i] = d.data[i] > 100 ? 255 : 0; cg.putImageData(d, 0, 0); smallCache[key] = c; }
    g.save(); g.translate(Math.round(x), Math.round(y)); if (hero.face === 'left') g.scale(-1, 1); g.drawImage(c, -Math.round(c.width / 2), -c.height); g.restore();
  }
  // test128: hero basic-attack hitbox = town H8HB table (per hit & direction, town px -> field px x29/96, weapon scale kept); specials keep swingR/arcW
  function hbKey() { const f = hero.face || 'down', T = (window.__game || {}).H8HB; return T && T.r[f] ? f : /left/.test(f) ? 'left' : /right/.test(f) ? 'right' : /up/.test(f) ? 'up' : 'down'; }
  function hbR(i) { const g = window.__game, T = g && g.H8HB; if (!T || i > 2) return swingR(i); let k = 1; try { if (g.swingRange && g.SWINGS) k = g.swingRange(g.SWINGS[0]) / 96; } catch (e) { } return T.r[hbKey()][i] * 29 / 96 * k; }
  function hbA(i) { const T = (window.__game || {}).H8HB; return T && i <= 2 ? T.arc[i] : arcW(i); }
  function drawHB(g, k) { const G = window.__game, a = hero.atk; if (!G || !G.HBDBG || !a) return; if (k) { const [sx, sy] = W2S(0, 0); g.save(); g.translate(sx, sy); g.scale(k, k); drawHB(g); g.restore(); return; } /* k: hi-res ctx (screen) pass */ const AT = atkT(a.i), on = a.t >= AT.a0 && a.t <= AT.a1, dv = FACEV[hero.face], b = Math.atan2(dv[1], dv[0]), h = hbA(a.i) * Math.PI / 360, R = hbR(a.i);
    g.save(); g.translate(hero.x, hero.y - 4); g.scale(1, .8); g.fillStyle = on ? 'rgba(255,40,40,.28)' : 'rgba(255,220,40,.14)'; g.strokeStyle = on ? '#ff3030' : '#ffd030'; g.lineWidth = 1;
    g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, R, b - h, b + h); g.closePath(); g.fill(); g.stroke(); g.restore();
    g.strokeStyle = 'rgba(80,200,255,.8)'; for (const mm of S.mobs) { if (mm.dead) continue; const mh = (mm.D.h || 20) * (mm.scale || 1); g.beginPath(); g.ellipse(mm.x, mm.y - mh * .3, mm.r + mh * .2, (mm.r + mh * .2) * .8, 0, 0, TAU); g.stroke(); } }
  function swingR(i) { const g = window.__game; let k = 1; try { if (g && g.swingRange && g.SWINGS) k = g.swingRange(g.SWINGS[0]) / 96; } catch (e) { } return SWING.range * k * (i === 2 ? SWING.r3 : i >= 3 ? (spOf(i).rangeMul || 1) : 1); }
  function drawSlash(g) { const a = hero.atk, AT = atkT(a.i), p = a.t / AT.dur, dv = FACEV[hero.face], base = Math.atan2(dv[1], dv[0]);
    if (p > (a.i === 2 ? .9 : .85)) return; const sweep = (a.i % 2 ? -1 : 1), R = swingR(a.i) - 2, half = arcW(a.i) / 2 * Math.PI / 180; // trail = hitbox radius/arc; hit2 sweeps back across the FRONT
    const a0 = base - sweep * half, a1 = a0 + sweep * 2 * half * Math.min(1, p / (AT.a1 / AT.dur));
    g.save(); g.translate(hero.x, hero.y - 4); g.scale(1, .8); g.lineCap = 'round';
    g.strokeStyle = a.i === 2 ? 'rgba(255,230,120,.9)' : 'rgba(255,255,255,.85)'; g.lineWidth = a.i === 2 ? 4 : 3; g.beginPath(); g.arc(0, 0, R, Math.min(a0, a1), Math.max(a0, a1)); g.stroke();
    g.strokeStyle = 'rgba(180,220,255,.5)'; g.lineWidth = 1.5; g.beginPath(); g.arc(0, 0, R - 4, Math.min(a0, a1), Math.max(a0, a1)); g.stroke(); g.restore(); }
  function drawMob(g, m) {
    const D = m.D; let name = m.sprite || D.spr; if ((m.atk || m.st === 'prep' || m.st === 'throw' || m.st === 'cast') && D.sprAtk) name = D.sprAtk;
    const sc = (m.scale || 1) * (m.spawnT > 0 ? Math.max(0, 1 - m.spawnT * 1.8) : 1); if (sc <= 0) return;
    const hover = D.hover ? D.hover + Math.sin(S.t * 6 + m.x) * 2 : 0;
    g.fillStyle = 'rgba(0,0,0,.3)'; g.beginPath(); g.ellipse(m.x, m.y, (m.r + 2) * sc, (m.r * .45 + 1) * sc, 0, 0, TAU); g.fill();
    if (D.felt || (D.s47 && M47 && M47[D.s47])) return; // body: drawFeltHi / drawS47 (hi-res pass)
    const sx = m.shake ? (Math.random() - .5) * 2 : 0;
    const mode = m.flash > 0 ? 'white' : (m.tint === 'rage' ? 'rage' : null);
    let sy = 1; if (m.squash) sy = 1 - m.squash * .3; if (m.st === 'pC') sy = .86;
    if (D.boss && m.charge) { g.fillStyle = `rgba(255,${80 + 100 * Math.sin(S.t * 20)},60,${.25 + m.charge * .4})`; g.beginPath(); g.ellipse(m.x, m.y - 32, 30 + m.charge * 10, 40 + m.charge * 10, 0, 0, TAU); g.fill(); }
    if (m.regen) { g.fillStyle = `rgba(80,255,120,${.2 + .15 * Math.sin(S.t * 8)})`; g.beginPath(); g.ellipse(m.x, m.y - 30, 30, 38, 0, 0, TAU); g.fill(); }
    if (m.rolling) { g.save(); g.translate(m.x, m.y - 16); g.rotate(S.t * 18); g.fillStyle = '#4a5a34'; g.beginPath(); g.arc(0, 0, 16, 0, TAU); g.fill(); g.strokeStyle = '#1c2410'; g.lineWidth = 1; g.stroke(); g.fillStyle = '#5cff8a'; for (let i = 0; i < 5; i++) { g.rotate(TAU / 5); g.fillRect(9, -2, 7, 4); } g.restore(); return; }
    drawSpr(g, name, m.x + sx, m.y - (m.hz || 0) - hover, { flip: m.face > 0, scale: sc, sy, mode, rot: m.lean ? m.lean * .9 * (m.face > 0 ? 1 : -1) : 0 });
  }
  // ---- chapter-1 Felt mobs: PixelLab strips (256px cells, foot at y 250, art faces right) drawn in the hi-res pass, y-split around the hero
  const FELTIMG = {}; function feltImg(src) { if (!FELTIMG[src]) { const im = new Image(); im.src = src + '.png'; FELTIMG[src] = im; } return FELTIMG[src]; }
  function feltFrame(m) { const a = m.D.anim[m.anim || 'walk'], i = feltFrame0(m); return a && a.map ? a.map[i] : i; } // optional frame remap per strip
  function feltFrame0(m) { const A = m.D.anim, a = A[m.anim || 'walk'];
    if (m.anim === 'attack' || m.anim === 'shoot') { const key = m.anim === 'attack' ? a.hit : a.release, sc = m.preT > 0 ? m.keyT / m.preT : 1; let t = m.at, i = 0;
      if (t < m.keyT) { for (; i < key; i++) { t -= a.ticks[i] / 60 * sc; if (t < 0) return i; } return key; }
      t -= m.keyT; for (i = key; i < a.n; i++) { t -= a.ticks[i] / 60 * (m.D.rec || 1); if (t < 0) return i; } return a.n - 1; }
    if (!m.moving) return 0; const i = ((Math.floor((m.wph !== undefined ? m.wph : S.t) * 60 / a.ticks[0] + m.home[0]) % a.n) + a.n) % a.n; return m.back ? a.n - 1 - i : i; } // wph = distance-based walk clock
  function drawFeltHi(k, pick) { const m = S.map; if (!m || m.type === 'world') return;
    for (const mm of S.mobs) { if (mm.dead || !pick(mm)) continue; if (mm.D.s47) { drawS47(mm, k); continue; } if (!mm.D.felt) continue; const A = mm.D.anim, name = mm.anim || 'walk', wd = name === 'walk' && mm.wdir && mm.wdir !== 'side' ? mm.wdir : '', im = feltImg(A.src + '_' + name + (wd ? '_' + wd : '')); if (!im.complete || !im.naturalWidth) continue;
      const sc = (mm.scale || 1) * (mm.spawnT > 0 ? Math.max(0, 1 - mm.spawnT * 1.8) : 1); if (sc <= 0) continue;
      const f = feltFrame(mm), idle = name === 'walk' && !mm.moving, sz = A.F * k * sc, P = mm.D.style, ph = S.t + mm.home[0];
      // body language (code, owner 10-23 "생동감"): wind-up squash + shiver before the hit, stretch on release, squash when hit, hop on first sight, per-mob idle habit
      const atkA = name === 'attack' || name === 'shoot', tele = atkA && mm.at < mm.keyT, q = tele ? mm.at / mm.keyT : 0; let bx = 1, by = 1, ox = 0, oy = 0, rot = 0;
      if (tele) { bx = 1 + .1 * q; by = 1 - .12 * q; if (q > .7) ox = (Math.random() - .5) * 2 * k; } else if (atkA && mm.at < mm.keyT + .1) { bx = .92; by = 1.1; }
      if (mm.hitT > .18) { bx *= 1.12; by *= .88; }
      if (mm.alertT > 0) oy = -Math.sin(Math.PI * (1 - mm.alertT / .45)) * 6 * k;
      if (idle && !tele) { if (P === 'duel') rot = Math.sin(ph * 2.6) * .05; else if (P === 'skirm') ox += (Math.floor(ph * 3) % 4 === 0 ? 1 : 0) * k * .6; else if (P === 'lunge') { by *= 1 + .03 * Math.sin(ph * 7); rot = Math.sin(ph * .9) > .8 ? .04 : 0; } else by *= 1 + .02 * Math.sin(ph * 4); }
      const [x, y] = W2S(mm.x + (mm.shake ? (Math.random() - .5) * 2 : 0), mm.y);
      if (tele || mm.rage) { ctx.save(); ctx.globalAlpha = tele ? .15 + .35 * q : .12 + .08 * Math.sin(S.t * 8); ctx.fillStyle = '#ff3c28'; ctx.beginPath(); ctx.ellipse(Math.round(x), Math.round(y), sz * .28, sz * .09, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore(); } // red ground glow = "about to strike" / angry
      ctx.save(); ctx.translate(Math.round(x + ox), Math.round(y + oy)); if (mm.face < 0 && wd !== 's' && wd !== 'n') ctx.scale(-1, 1); if (rot) ctx.rotate(rot); ctx.scale(bx, by);
      if (mm.flash > 0) ctx.filter = 'brightness(3)';
      blitFrame(im, f, 256, 256, sz / 256, Math.round(-sz / 2), Math.round(-sz * 250 / 256)); ctx.restore(); } }
  // ---- companion Linette (owner 10-22 "전캐릭 인게임"): follows the hero in 바람길 (field00) and thrusts at nearby mobs.
  // Atlas assets/anim/linette8.json (hero8 format, 117px figure = hero scale); thrust tip/dir from A.thrust, trail drawn in code.
  const PET = { A: null, IM: [] }; getJSON('assets/anim/linette8.json').then(j => { PET.A = j; PET.IM = j.sheets.map(p => { const i = new Image(); i.src = 'assets/' + p; return i; }); }).catch(() => {});
  const PET_MAPS = ['field00'];
  const petDir = (dx, dy, cur) => Math.abs(dx) > Math.abs(dy) * 1.4 ? (dx > 0 ? 'right' : 'left') : dy > 0 ? (dx > 0 || (!dx && !/l$|left/.test(cur)) ? 'down' : 'downl') : (dx > 0 || (!dx && !/l$|left/.test(cur)) ? 'up' : 'upl');
  const petTot = L => L.reduce((a, f) => a + f[2], 0);
  function stepPet(dt) { const m = M(); if (!PET.A || !PET_MAPS.includes(m.id)) { S.pet = null; return; }
    let P = S.pet; if (!P || P.map !== m) P = S.pet = { x: hero.x - 14, y: hero.y + 4, dir: 'right', t: 0, cd: 0, n: 0, map: m, moving: false, run: false };
    P.t += dt; P.cd -= dt; const x0 = P.x, y0 = P.y;
    if (P.atk) { const a = P.atk, L = PET.A.anims[a.clip + '_' + a.dir]; a.t += dt * 60;
      if (!a.done && a.t >= a.hitT) { a.done = true; sfx('thrust', .6); const tg = a.tg; if (tg && !tg.dead && Math.hypot(tg.x - P.x, tg.y - P.y) < 30) hitMob(tg, 6, Math.atan2(tg.y - P.y, tg.x - P.x), false); }
      if (a.t >= petTot(L)) P.atk = null; P.moving = false; return; }
    let tg = null, bd = 90; for (const o of S.mobs) { if (o.dead || o.spawnT > 0 || o.noBar || o.D.boss) continue; const d = Math.hypot(o.x - P.x, o.y - P.y); if (d < bd && Math.hypot(o.x - hero.x, o.y - hero.y) < 120) { bd = d; tg = o; } }
    let gx, gy, sp; if (tg) { gx = tg.x - Math.sign(tg.x - P.x || 1) * 14; gy = tg.y; sp = 95; } else { const fv = FACEV[hero.face] || [1, 0]; gx = hero.x - fv[0] * 18 - 8; gy = hero.y - fv[1] * 12 + 4; sp = 0; }
    const dx = gx - P.x, dy = gy - P.y, d = Math.hypot(dx, dy);
    if (!tg && d > 240) { P.x = gx; P.y = gy; }
    else if (tg && Math.hypot(tg.x - P.x, tg.y - P.y) < 22 && P.cd <= 0) { const clip = P.n++ % 2 ? 'atk2' : 'atk1', dir = petDir(tg.x - P.x, tg.y - P.y, P.dir), th = PET.A.thrust[clip + '_' + dir], L = PET.A.anims[clip + '_' + dir];
      P.dir = dir; P.atk = { t: 0, clip, dir, tg, hitT: petTot(L.slice(0, th ? th.frame : 4)) }; P.cd = 0.9; P.moving = false; return; }
    else if (d > (tg ? 3 : 14)) { const v = (sp || (d > 60 ? 130 : 78)) * dt, k = Math.min(1, v / d); moveCol(P, dx * k, dy * k, 4); P.run = sp ? true : d > 60; }
    const mx = P.x - x0, my = P.y - y0; P.moving = Math.abs(mx) + Math.abs(my) > 1e-3; if (P.moving) P.dir = petDir(mx, my, P.dir); else if (tg) P.dir = petDir(tg.x - P.x, tg.y - P.y, P.dir);
    if (P.moving) P.gp = ((P.gp || 0) + Math.hypot(mx, my) / (P.run ? 46 : 32)) % 1; }
  function drawPetHi(k, front) { const P = S.pet; if (!P || !PET.A || P.map !== S.map || (P.y > hero.y) !== front) return; const A = PET.A, a = P.atk;
    const an = a ? a.clip : P.moving ? (P.run ? 'run' : 'walk') : 'idle', L = A.anims[an + '_' + (a ? a.dir : P.dir)] || A.anims[an + '_right']; if (!L) return;
    let e; if (a) { let t = a.t, i = 0; for (; i < L.length - 1; i++) { if (t < L[i][2]) break; t -= L[i][2]; } e = L[i]; } else if (P.moving) e = L[Math.floor((P.gp || 0) * L.length) % L.length]; else { let t = (S.t * 60) % petTot(L), i = 0; for (; i < L.length - 1; i++) { if (t < L[i][2]) break; t -= L[i][2]; } e = L[i]; }
    const im = PET.IM[e[0]], c = A.cells[e[0]][e[1]]; if (!im || !im.complete) return; const sc = k * H128FIG / 117, [sx, sy] = W2S(P.x, P.y);
    ctx.save(); ctx.fillStyle = 'rgba(0,0,0,.28)'; ctx.beginPath(); ctx.ellipse(sx, sy, 6 * k, 2.5 * k, 0, 0, TAU); ctx.fill(); ctx.imageSmoothingEnabled = sc < 1;
    ctx.drawImage(im, c[0], c[1], c[2], c[3], Math.round(sx - c[4] * sc), Math.round(sy - c[5] * sc), Math.round(c[2] * sc), Math.round(c[3] * sc));
    const th = a && A.thrust[a.clip + '_' + a.dir]; if (th && a.t >= a.hitT - 4 && a.t < a.hitT + 10) { const q = 1 - Math.max(0, a.t - a.hitT) / 10, tx = sx + th.tip[0] * sc, ty = sy + th.tip[1] * sc; // thrust trail (code)
      ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round'; for (const [w, col] of [[6, `rgba(150,220,255,${.35 * q})`], [2.5, `rgba(255,255,255,${.9 * q})`]]) { ctx.strokeStyle = col; ctx.lineWidth = w * k / 3; ctx.beginPath(); ctx.moveTo(tx - th.dir[0] * 34 * sc, ty - th.dir[1] * 34 * sc); ctx.lineTo(tx, ty); ctx.stroke(); } }
    ctx.restore(); }
  // ---- room-3 strips (assets/mobs47, tools/anim/mobs47/import.py): idle 8 frames (8fps) + attack 12 frames (hit = frame 4), all facing right.
  // ram strips (left-facing art mirrored, field 5) have no attack strip: the idle frame lunges in code. Old area-1 AIs (no startAnim) show the
  // attack strip's strike pose while they wind up / attack.
  let M47 = null; getJSON('assets/mobs47/mobs47.json').then(j => M47 = j).catch(() => {});
  // pre-scaled strip cache: big strips (150-300px cells) are shrunk once per on-screen size with high-quality smoothing, then blitted 1:1
  // (resampling every frame per mob was the main per-frame cost on phones). Key = image + scale rounded to 1/40.
  const SCL = new Map();
  function scaledStrip(im, s) { if (!im.complete || !im.naturalWidth) return null; const q = Math.round(s * 40) / 40, key = im.src + '|' + q; let c = SCL.get(key); if (c) return c;
    if (SCL.size > 160) SCL.clear(); c = document.createElement('canvas'); c.width = Math.max(1, Math.ceil(im.naturalWidth * q)); c.height = Math.max(1, Math.ceil(im.naturalHeight * q)); c.q = q;
    const g2 = c.getContext('2d'); g2.imageSmoothingEnabled = true; g2.imageSmoothingQuality = 'high'; g2.drawImage(im, 0, 0, c.width, c.height); SCL.set(key, c); return c; }
  function blitFrame(im, fi, cw, ch, s, dx, dy) { // draw frame fi (cell cw x ch) of strip im at scale s with its top-left at (dx, dy) in the current transform
    const c = scaledStrip(im, s); if (!c) return; const q = c.q, k = s / q; ctx.imageSmoothingEnabled = Math.abs(k - 1) > .01;
    ctx.drawImage(c, Math.round(fi * cw * q), 0, Math.round(cw * q), Math.round(ch * q), dx, dy, cw * s, ch * s); }
  const S47IMG = {}; function s47Img(id, k) { const key = id + '_' + k; if (!S47IMG[key]) { const im = new Image(); im.src = 'assets/mobs47/' + key + '.webp'; S47IMG[key] = im; } return S47IMG[key]; }
  const LUNGE = [0, -6, -10, 14, 24, 26, 24, 20, 14, 8, 3, 0]; // ram: x offset per attack frame (strip px)
  const OLDATK = ['prep', 'throw', 'cast', 'aim', 'charge', 'puff', 'swipe', 'rise', 'jump'];
  function s47Frame(m) { const a = m.D.anim.attack, sc = m.preT > 0 ? m.keyT / m.preT : 1; let t = m.at, i = 0;
    if (m.anim === 'hold') return a.hit; if (t < m.keyT) { for (; i < a.hit; i++) { t -= a.ticks[i] / 60 * sc; if (t < 0) return i; } return a.hit; }
    t -= m.keyT; for (i = a.hit; i < a.n; i++) { t -= a.ticks[i] / 60; if (t < 0) return i; } return a.n - 1; }
  function drawS47(mm, k) { const J = M47 && M47[mm.D.s47]; if (!J) return; const D = mm.D;
    const sc = (mm.scale || 1) * (mm.spawnT > 0 ? Math.max(0, 1 - mm.spawnT * 1.8) : 1); if (sc <= 0) return;
    let f = -1; if (mm.anim === 'attack' || mm.anim === 'hold') f = s47Frame(mm); else if (!D.anim || !D.anim.attack.n || !D.ai) { if (mm.atk || OLDATK.includes(mm.st)) f = mm.st === 'prep' || mm.st === 'aim' || mm.st === 'rise' ? 2 : 5; }
    const useAtk = f >= 0 && !J.ram && J.atk, im = s47Img(D.s47, useAtk ? 'atk' : 'idle'); if (!im.complete || !im.naturalWidth) return;
    const C = useAtk ? J.atk : J.idle, s = D.h / J.body * sc * k, ph = mm.home ? mm.home[0] : 0;
    const fi = useAtk ? f : Math.floor(S.t * 8 + ph) % J.idle.n, dx = f >= 0 && !useAtk ? LUNGE[f] : 0;
    const hop = mm.moving && !D.fly ? Math.abs(Math.sin(S.t * 11 + ph)) * 1.5 : 0, lift = (mm.hz || 0) + (mm.hop || 0) + hop + (D.hover ? D.hover + Math.sin(S.t * 6 + mm.x) * 2 : 0);
    let sy = 1; if (mm.squash) sy = 1 - mm.squash * .3; if (mm.st === 'pC') sy = .86;
    const [x, y] = W2S(mm.x + (mm.shake ? (Math.random() - .5) * 2 : 0), mm.y - lift);
    ctx.save(); ctx.translate(Math.round(x), Math.round(y)); if (mm.face < 0) ctx.scale(-1, 1); if (mm.lean) ctx.rotate(mm.lean * .9); ctx.scale(1, sy);
    if (mm.flash > 0) ctx.filter = 'brightness(3)'; else if (mm.tint === 'rage') ctx.filter = 'sepia(1) saturate(4) hue-rotate(-30deg)';
    blitFrame(im, fi, C.w, C.h, s, Math.round((-C.w / 2 + dx) * s), Math.round(-C.foot * s)); ctx.restore(); }
  const FELT_SHOT = { // code-drawn projectiles (rotated to the flight direction; +x = forward)
    needle(g) { g.fillStyle = '#1e1e24'; g.fillRect(-5, -1, 10, 2); g.fillStyle = '#dfe2ea'; g.fillRect(-4, 0, 8, 1); g.fillStyle = '#9a9aa6'; g.fillRect(-9, 0, 3, 1); },
    threadball(g, s) { g.fillStyle = '#28262a'; g.beginPath(); g.arc(0, 0, 4, 0, TAU); g.fill(); g.fillStyle = '#c8c6be'; g.beginPath(); g.arc(0, 0, 3, 0, TAU); g.fill();
      g.strokeStyle = '#7a7672'; g.lineWidth = 1; g.beginPath(); g.arc(0, 0, 2, s.t * 9, s.t * 9 + 2); g.stroke(); g.strokeStyle = '#bebab2'; g.beginPath(); g.moveTo(-4, 0);
      for (let i = 1; i < 6; i++) g.lineTo(-4 - i * 2, Math.sin(s.t * 14 + i) * 1.5); g.stroke(); },
    blade(g, s) { g.rotate(s.t * 18); g.fillStyle = '#3a1c10'; g.fillRect(-6, -2, 12, 4); g.fillRect(-2, -6, 4, 12); g.fillStyle = '#b05c30'; g.fillRect(-5, -1, 10, 2); g.fillRect(-1, -5, 2, 10); g.fillStyle = '#ecc890'; g.fillRect(-1, -1, 2, 2); },
    pin(g) { g.fillStyle = '#1e1e24'; g.fillRect(-4, -1, 8, 2); g.fillStyle = '#d6dae0'; g.fillRect(-3, 0, 7, 1); g.fillStyle = '#c81e28'; g.fillRect(-6, -1, 3, 3); },
    web(g, s) { g.fillStyle = 'rgba(235,235,240,.75)'; g.beginPath(); g.arc(0, 0, 4.5, 0, TAU); g.fill(); g.strokeStyle = '#8c8c98'; g.lineWidth = 1;
      for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3 + s.t * 2; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(a) * 4.5, Math.sin(a) * 4.5); g.stroke(); } },
    venom(g) { g.fillStyle = '#14281a'; g.fillRect(-5, -1, 9, 2); g.fillStyle = '#96e65a'; g.fillRect(-4, 0, 8, 1); g.fillStyle = '#64c83c'; g.fillRect(-8, 0, 1, 1); g.fillRect(-11, 0, 1, 1); },
    orb(g, s) { const r = 4 + Math.sin(s.t * 18) * .6; g.fillStyle = 'rgba(120,40,170,.35)'; g.beginPath(); g.arc(0, 0, r + 2.5, 0, TAU); g.fill();
      g.fillStyle = '#9640d2'; g.beginPath(); g.arc(0, 0, r, 0, TAU); g.fill(); g.fillStyle = '#e6beff'; g.fillRect(-1, -2, 2, 2); },
    beam(g, s) { g.fillStyle = 'rgba(200,120,255,.35)'; g.fillRect(-9, -2, 14, 4); g.fillStyle = '#f0d8ff'; g.fillRect(-8, -1, 13, 2); g.fillStyle = '#fff'; g.fillRect(2, -1, 3, 2); },
    arrow(g) { g.fillStyle = '#5a4630'; g.fillRect(-6, 0, 10, 1); g.fillStyle = '#d8d8d0'; g.fillRect(4, -1, 2, 3); g.fillStyle = '#e8e0c8'; g.fillRect(-7, -1, 2, 1); g.fillRect(-7, 1, 2, 1); },
    firearrow(g, s) { g.fillStyle = `rgba(255,${120 + 60 * Math.sin(s.t * 30)},40,.6)`; g.fillRect(-10, -1, 6, 3); g.fillStyle = '#2a1a14'; g.fillRect(-6, 0, 10, 1); g.fillStyle = '#ffb040'; g.fillRect(4, -1, 2, 3); },
    spike(g) { g.fillStyle = '#3a3010'; g.fillRect(-3, -1, 6, 2); g.fillStyle = '#f0d860'; g.fillRect(-2, 0, 6, 1); },
    ink(g, s) { const r = 3.5 + Math.sin(s.t * 14) * .5; g.fillStyle = '#1c1028'; g.beginPath(); g.arc(0, 0, r, 0, TAU); g.fill(); g.fillStyle = '#4a3060'; g.fillRect(-1, -2, 2, 1); g.fillStyle = 'rgba(28,16,40,.6)'; g.fillRect(-8, -1, 4, 2); },
    bolt(g, s) { g.strokeStyle = '#fff6a0'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(-8, 0); for (let i = 1; i <= 4; i++) g.lineTo(-8 + i * 3, (i % 2 ? -2 : 2) * Math.sin(s.t * 40 + i)); g.stroke(); g.fillStyle = 'rgba(255,240,120,.3)'; g.beginPath(); g.arc(4, 0, 3, 0, TAU); g.fill(); },
    feather(g) { g.fillStyle = '#c83020'; g.fillRect(-5, -1, 8, 2); g.fillStyle = '#30a040'; g.fillRect(-7, -1, 2, 2); g.fillStyle = '#f0e0a0'; g.fillRect(3, 0, 2, 1); },
    stone(g, s) { g.rotate(s.t * 14); g.fillStyle = '#28261f'; g.beginPath(); g.moveTo(-4, -3); g.lineTo(5, 0); g.lineTo(-3, 4); g.closePath(); g.fill();
      g.fillStyle = '#827e78'; g.beginPath(); g.moveTo(-3, -2); g.lineTo(4, 0); g.lineTo(-2, 3); g.closePath(); g.fill(); g.fillStyle = '#a05ac8'; g.fillRect(-1, 0, 2, 1); },
  };
  function drawShot(g, s) { g.save(); g.translate(s.x, s.y); g.rotate(Math.atan2(s.vy, s.vx));
    if (FELT_SHOT[s.kind]) FELT_SHOT[s.kind](g, s);
    else if (s.kind === 'shard') { g.fillStyle = '#8affb0'; g.beginPath(); g.moveTo(6, 0); g.lineTo(-4, -3); g.lineTo(-4, 3); g.fill(); g.fillStyle = '#e8fff0'; g.fillRect(-1, -1, 5, 2); }
    else { g.fillStyle = '#ffe070'; g.fillRect(-4, -1, 8, 2); g.fillStyle = '#3a2a10'; g.fillRect(3, -1, 2, 2); }
    g.restore(); }
  function hazColor(h) { return ({ web: [225, 225, 240], poison: [170, 80, 255], root: [120, 220, 80], crystal: [90, 255, 160], cage: [90, 255, 160], summon: [255, 220, 60], acorn: [255, 160, 60] })[h.kind] || [255, 60, 50]; }
  function drawHazard(g, h, top) {
    if (h.shape === 'all') return;
    const [r, gg, b] = hazColor(h), warnP = Math.min(1, h.t / (h.warn || 1e-3)), live = h.t >= h.warn && h.t < h.warn + (h.act || 0);
    if (!top && h.t < h.warn) { // telegraph: outline + an inner fill that grows until impact (the timing cue for the roll)
      const pulse = .5 + .5 * Math.sin(h.t * 22);
      g.strokeStyle = `rgba(${r},${gg},${b},${.55 + .35 * pulse})`; g.fillStyle = `rgba(${r},${gg},${b},${.10 + .2 * warnP})`; g.lineWidth = 1;
      if (h.shape === 'circle') { g.beginPath(); g.ellipse(h.x, h.y, h.r, h.r / 1.15, 0, 0, TAU); g.fill(); g.stroke(); g.fillStyle = `rgba(${r},${gg},${b},.35)`; g.beginPath(); g.ellipse(h.x, h.y, h.r * warnP, h.r * warnP / 1.15, 0, 0, TAU); g.fill(); }
      if (h.shape === 'ring') { g.beginPath(); g.ellipse(h.x, h.y, h.r, h.r / 1.15, 0, 0, TAU); if (h.r0 > 0) g.ellipse(h.x, h.y, h.r0, h.r0 / 1.15, 0, 0, TAU, true); g.fill('evenodd'); g.stroke(); }
      if (h.shape === 'line') { g.save(); g.translate(h.x, h.y); g.rotate(Math.atan2(h.y2 - h.y, h.x2 - h.x)); const L = Math.hypot(h.x2 - h.x, h.y2 - h.y);
        g.fillRect(0, -h.width / 2, L, h.width); g.fillStyle = `rgba(${r},${gg},${b},.35)`; g.fillRect(0, -h.width / 2, L * warnP, h.width);
        g.strokeRect(0, -h.width / 2, L, h.width); for (let i = 10; i < L; i += 14) { g.beginPath(); g.moveTo(i - 3, -2); g.lineTo(i + 1, 0); g.lineTo(i - 3, 2); g.stroke(); } g.restore(); }
      if (h.kind === 'acorn' && h.from) { const p = warnP, x = h.from[0] + (h.x - h.from[0]) * p, y = h.from[1] + (h.y - h.from[1]) * p - Math.sin(p * Math.PI) * 30; g.fillStyle = '#8a5a2a'; g.beginPath(); g.arc(x, y, 2.5, 0, TAU); g.fill(); }
      if (h.kind === 'rock') { const p = warnP; g.fillStyle = 'rgba(0,0,0,.3)'; g.beginPath(); g.ellipse(h.x, h.y, h.r * p, h.r * p / 1.6, 0, 0, TAU); g.fill(); if (p > .6) { g.fillStyle = '#7a7060'; g.fillRect(h.x - 4, h.y - (1 - p) * 120 - 8, 8, 7); } }
      if (h.kind === 'cage') { g.globalAlpha = .35 + .3 * pulse; drawSpr(g, 'crystal', h.x, h.y + 5); g.globalAlpha = 1; }
    }
    if (top && live) {
      g.fillStyle = `rgba(${Math.min(255, r + 60)},${Math.min(255, gg + 60)},${Math.min(255, b + 60)},.55)`;
      if (h.shape === 'circle') { g.beginPath(); g.ellipse(h.x, h.y, h.r, h.r / 1.15, 0, 0, TAU); g.fill(); }
      if (h.shape === 'ring') { g.beginPath(); g.ellipse(h.x, h.y, h.r, h.r / 1.15, 0, 0, TAU); if (h.r0 > 0) g.ellipse(h.x, h.y, h.r0, h.r0 / 1.15, 0, 0, TAU, true); g.fill('evenodd');
        for (let i = 0; i < 12; i++) { const a = i / 12 * TAU, rr = (h.r + h.r0) / 2; drawSpr(g, 'crystal', h.x + Math.cos(a) * rr, h.y + Math.sin(a) * rr / 1.15 + 4, { scale: .7 }); } }
    }
    if (!top && h.linger && h.t >= h.warn && h.t < h.warn + (h.act || 0) + h.linger) { g.fillStyle = 'rgba(150,60,220,.4)'; g.beginPath(); g.ellipse(h.x, h.y, h.r * .8, h.r * .6, 0, 0, TAU); g.fill(); }
  }
  function drawUlt(g, h) { // 필살기 telegraph: whole room red except each pillar's shadow (the safe zone)
    const m = M(), b = h.owner; if (h.t > h.warn + .3) return;
    const p = Math.min(1, h.t / h.warn);
    if (!_ultC || _ultC.width !== m.pw || _ultC.height !== m.ph) { _ultC = document.createElement('canvas'); _ultC.width = m.pw; _ultC.height = m.ph; }
    const d = _ultC.getContext('2d'); d.globalCompositeOperation = 'source-over'; d.clearRect(0, 0, m.pw, m.ph);
    d.fillStyle = h.t >= h.warn ? 'rgba(255,240,200,.85)' : `rgba(255,30,20,${.16 + .2 * p + .08 * Math.sin(S.t * 20)})`; d.fillRect(0, 0, m.pw, m.ph);
    d.globalCompositeOperation = 'destination-out'; d.fillStyle = '#000';
    for (const dd of m.decos) { if (dd.spr !== 'pillar') continue; const px = dd.x, py = dd.y - 6, a = Math.atan2(py - b.y, px - b.x), D = Math.hypot(px - b.x, py - b.y), w = Math.asin(Math.min(1, 9 / D));
      d.beginPath(); d.moveTo(px + Math.cos(a + Math.PI / 2) * 9, py + Math.sin(a + Math.PI / 2) * 9);
      d.lineTo(px + Math.cos(a + w) * 600, py + Math.sin(a + w) * 600); d.lineTo(px + Math.cos(a - w) * 600, py + Math.sin(a - w) * 600);
      d.lineTo(px + Math.cos(a - Math.PI / 2) * 9, py + Math.sin(a - Math.PI / 2) * 9); d.fill(); }
    g.drawImage(_ultC, 0, 0);
  }
  function drawFx(g, f) { const p = f.t / f.life;
    if (f.type === 'spark') { g.fillStyle = `rgba(255,255,220,${1 - p})`; for (let i = 0; i < 4; i++) { const a = i * 1.57 + .7; g.fillRect(f.x + Math.cos(a) * p * 8 - 1, f.y + Math.sin(a) * p * 8 - 1, 2, 2); } }
    if (f.type === 'poof') { g.fillStyle = `rgba(240,240,255,${.8 * (1 - p)})`; const R = (f.big ? 22 : 9) * (0.4 + p); for (let i = 0; i < 6; i++) { const a = i * TAU / 6; g.beginPath(); g.arc(f.x + Math.cos(a) * R, f.y + Math.sin(a) * R * .6, 3 * (1 - p) + 1, 0, TAU); g.fill(); } }
    if (f.type === 'dust') { g.fillStyle = `rgba(200,180,140,${.6 * (1 - p)})`; for (let i = 0; i < 3; i++) { g.beginPath(); g.arc(f.x + (i - 1) * 5 * (1 + p), f.y - p * 4, 2 + p * 2, 0, TAU); g.fill(); } }
    if (f.type === 'debris') { g.fillStyle = `rgba(130,120,100,${1 - p})`; for (let i = 0; i < 6; i++) { const a = i * 1.05; g.fillRect(f.x + Math.cos(a) * p * 14, f.y + Math.sin(a) * p * 8 - Math.sin(p * 3) * 6, 3, 3); } }
    if (f.type === 'crystal') { g.globalAlpha = Math.max(0, 1 - p); drawSpr(g, 'crystal', f.x, f.y + 4, { scale: .6 + p * .3, alpha: Math.max(0, 1 - p) }); g.globalAlpha = 1; }
    if (f.type === 'heal') { g.fillStyle = `rgba(120,255,140,${1 - p})`; g.fillRect(f.x - 1, f.y - p * 14 - 3, 2, 6); g.fillRect(f.x - 3, f.y - p * 14 - 1, 6, 2); }
    if (f.type === 'stars') { g.fillStyle = '#ffe060'; for (let i = 0; i < 3; i++) { const a = S.t * 6 + i * 2.1; g.fillRect(f.x + Math.cos(a) * 6, f.y + Math.sin(a) * 2, 2, 2); } }
    if (f.type === 'sparkle') { g.fillStyle = `rgba(255,250,180,${1 - p})`; for (let i = 0; i < 5; i++) { const a = i * 1.26 + p; g.fillRect(f.x + Math.cos(a) * p * 12, f.y + Math.sin(a) * p * 12 - p * 6, 2, 2); } }
    if (f.type === 'fluff') { const n = f.n || 12; for (let i = 0; i < n; i++) { const a = i * 2.39996 + (f.x % 7), sp = 10 + (i * 37 % 13), x = f.x + Math.cos(a) * sp * p * 1.6, y = f.y + Math.sin(a) * sp * p * .9 - Math.sin(Math.min(1, p * 1.6) * Math.PI) * 10 + p * p * 8; // felt fluff + thread bits
        g.globalAlpha = Math.max(0, 1 - p * p); g.fillStyle = i % 3 === 0 ? '#f2ede2' : (f.col || '#b0a890'); if (i % 4 === 1) g.fillRect(x, y, 4, 1); else g.fillRect(x - 1, y - 1, 3, 3); } g.globalAlpha = 1; }
    if (f.type === 'cloud') { g.fillStyle = `rgba(160,80,220,${.3 * (1 - p)})`; g.beginPath(); g.ellipse(f.x, f.y - 4, f.r || 20, (f.r || 20) * .6, 0, 0, TAU); g.fill(); }
  }
  function drawWorldNodes(g, m) {
    for (const n of m.nodes) { const x = (n.x + .5) * m.T, y = (n.y + .5) * m.T, locked = n.locked;
      if (n.kind === 'town') { const cols = locked ? ['#6a6a6a', '#9a9a9a', '#4a4a4a'] : ['#c8322a', '#f0dcae', '#5a2a1a'];
        g.fillStyle = 'rgba(0,0,0,.3)'; g.beginPath(); g.ellipse(x, y + 4, 8, 3, 0, 0, TAU); g.fill();
        for (const [dx, dy] of [[-4, -1], [3, -3], [1, 2]]) { g.fillStyle = cols[1]; g.fillRect(x + dx - 3, y + dy - 1, 6, 4); g.fillStyle = cols[0]; g.beginPath(); g.moveTo(x + dx - 4, y + dy - 1); g.lineTo(x + dx, y + dy - 5); g.lineTo(x + dx + 4, y + dy - 1); g.fill(); g.fillStyle = cols[2]; g.fillRect(x + dx - 1, y + dy + 1, 2, 2); }
        if (!locked) { g.strokeStyle = `rgba(255,255,255,${.35 + .25 * Math.sin(S.t * 4)})`; g.lineWidth = 1; g.beginPath(); g.ellipse(x, y, 10, 8, 0, 0, TAU); g.stroke(); } }
      else { const R = 6; g.fillStyle = locked ? 'rgba(40,40,50,.85)' : 'rgba(30,70,20,.92)'; g.beginPath(); g.arc(x, y, R, 0, TAU); g.fill();
        g.strokeStyle = locked ? '#888' : '#ffd84a'; g.lineWidth = 1; g.beginPath(); g.arc(x, y, R, 0, TAU); g.stroke();
        if (!locked) { g.fillStyle = '#ffe08a'; g.fillRect(x - 1, y - 3, 2, 6); g.fillRect(x - 3, y - 1, 6, 2); }
        if (locked) { g.fillStyle = '#c8c8d0'; g.fillRect(x - 2, y - 1, 5, 4); g.strokeStyle = '#c8c8d0'; g.beginPath(); g.arc(x + .5, y - 1, 1.6, Math.PI, 0); g.stroke(); }
        if (!locked) { g.strokeStyle = `rgba(255,216,74,${.4 + .3 * Math.sin(S.t * 4)})`; g.beginPath(); g.arc(x, y, R + 2 + Math.sin(S.t * 4), 0, TAU); g.stroke(); } }
    }
  }
  // display-resolution text: names, HP bars, CHAMPION labels, HUD, dialogs (crisp at any integer scale)
  function W2S(x, y) { const v = S.view; return [v.ox + (x - S.camI[0]) * v.k, v.oy + (y - S.camI[1]) * v.k]; }
  function font(px) { return 'bold ' + Math.max(8, Math.round(px)) + 'px "Malgun Gothic","Apple SD Gothic Neo","Noto Sans CJK KR",sans-serif'; }
  function textOut(t, x, y, px, fill, stroke = '#000', align = 'center') { ctx.font = font(px); ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.lineJoin = 'round'; ctx.lineWidth = Math.max(2, px / 5); ctx.strokeStyle = stroke; ctx.strokeText(t, x, y); ctx.fillStyle = fill; ctx.fillText(t, x, y); }
  function panel(x, y, w, h) { ctx.fillStyle = 'rgba(12,18,44,.78)'; ctx.fillRect(x, y, w, h); ctx.strokeStyle = '#e2c27a'; ctx.lineWidth = 2; ctx.strokeRect(x + 1, y + 1, w - 2, h - 2); ctx.strokeStyle = 'rgba(226,194,122,.4)'; ctx.lineWidth = 1; ctx.strokeRect(x + 5, y + 5, w - 10, h - 10); }
  function keyHint(a) { const c = codesOf(a)[0] || ''; return c.replace(/^Key/, '').replace(/^Digit/, ''); }
  function drawHiRes(k, ox, oy) {
    const u = k / 3, m = M(), SW = LW * k, SH = LH * k, cxs = ox + SW / 2;
    if (m.type === 'world') {
      for (const n of m.nodes) { const [sx, sy] = W2S((n.x + .5) * m.T, (n.y + .5) * m.T); const near = S.nearNode === n;
        textOut((n.kind === 'area' ? n.area + '. ' : '') + n.name, sx, sy - 9 * u, (near ? 14 : 10) * u, n.locked ? '#b8b8c0' : (n.kind === 'area' ? '#ffe08a' : '#ffffff'));
        if (n.locked && near) textOut('봉인됨', sx, sy + 16 * u, 9 * u, '#ff9a8a'); }
      const n = S.nearNode; if (n) { const tx = n.locked ? '봉인됨 — 아직 갈 수 없다' : n.scene ? `[${keyHint('interact')}] ${n.kind === 'area' ? '들어가기' : '마을로 들어가기'}` : '준비 중';
        panel(cxs - 190 * u, oy + SH - 44 * u, 380 * u, 34 * u); textOut(((n.kind === 'area' ? n.area + '지역 ' : '') + n.name) + '  ·  ' + tx, cxs, oy + SH - 22 * u, 13 * u, '#fff'); }
      textOut('월드맵', ox + 10 * u, oy + 20 * u, 15 * u, '#ffe08a', '#000', 'left');
      textOut(`이동 방향키/WASD · ${keyHint('interact')}/Enter 들어가기`, ox + 10 * u, oy + 36 * u, 10 * u, '#dde', '#000', 'left');
    } else {
      for (const mm of S.mobs) { if (mm.dead || mm.spawnT > 0 || mm.D.boss || mm.noBar) continue; if (mm.hp >= mm.maxHp && !mm.D.champion) continue;
        const [sx, sy] = W2S(mm.x, mm.y - (mm.D.h || 20) * (mm.scale || 1) - (mm.D.hover || 0) - 3); hpBar(mm, sx, sy, (mm.D.champion ? 46 : 20) * u, 4 * u);
        if (mm.D.champion) { textOut('CHAMPION', sx, sy - 4 * u, 10 * u, 'rgb(255,205,50)', '#5a0a0a'); textOut(mm.D.name, sx, sy - 15 * u, 9 * u, '#fff'); } }
      for (const f of S.fx) if (f.type === 'text') { const [sx, sy] = W2S(f.x, f.y - f.t * 16); ctx.globalAlpha = Math.max(0, 1 - f.t / f.life); textOut(f.text, sx, sy, 12 * u, f.color || '#fff'); ctx.globalAlpha = 1; }
      const g = window.__game, hu = Math.max(.75, SH / 600); let hb = oy + 26 * u; S.hudY = 0; // modern HUD (town/hud.js): HP/MP/EXP + Lv badge, 필살기 gauge bottom centre
      if (window.HUD) { hb = HUD.drawPlayer(ctx, { x: ox + 10 * hu, y: oy + 10 * hu, u: hu, hp: hero.hp, maxHp: hero.maxHp, mp: g ? g.mp : 0, maxMp: g ? g.mpMax() : 0, exp: g ? g.exp : 0, expNext: g && g.expNext ? g.expNext(g.lvl) : 0, lvl: g ? g.lvl : 1 }) + 14 * hu; S.hudY = hb + 14 * hu;
        if (g && g.ULT_CFG) HUD.drawUlt(ctx, { cx: cxs, y: oy + SH - (b0() ? 62 : 40) * hu, u: hu, v: g.ultG / g.ULT_CFG.max, name: g.ULTS && g.ultId ? g.ULTS[g.ultId()].name : '', key: keyHint('ult') || 'R', pop: g.ultPop }); }
      textOut(`물약 ${g ? g.potions : 0}/${DIFF().potion_cap || 5} [${keyHint('potion')}]` + (g && g.potionCd > 0 ? ' ' + g.potionCd.toFixed(1) + 's' : ''), ox + 12 * u, hb, 11 * u, '#cfe8ff', '#000', 'left');
      textOut(m.name, ox + SW - 10 * u, oy + 20 * u, 12 * u, '#ffe08a', '#000', 'right');
      if (m.area) { const n = ['champ_boar', 'champ_wasp'].filter(f => SAVE.flags[f]).length; textOut(`챔피언 ${n}/2` + (SAVE.flags.boss01 ? '  ·  골렘 격파 ✓' : ''), ox + SW - 10 * u, oy + 35 * u, 10 * u, n === 2 ? '#8f8' : '#fff', '#000', 'right'); }
      if (m.type === 'dungeon') { const keys = Object.keys(SAVE.keys).filter(k2 => SAVE.keys[k2] === true && !k2.endsWith(':used') && !SAVE.keys[k2 + ':used']).length; if (keys) textOut('열쇠 ×' + keys, ox + SW - 10 * u, oy + 50 * u, 10 * u, '#ffe08a', '#000', 'right'); }
      const b = S.bossRef; if (b && !b.dead) { const w = 260 * u, y = oy + SH - 20 * u; hpBar(b, cxs, y, w, 7 * u);
        textOut(b.D.name + (b.phase === 2 ? '  — 2페이즈' : ''), cxs, y - 5 * u, 12 * u, b.phase === 2 ? '#ff9a7a' : '#fff');
        ctx.fillStyle = 'rgba(255,255,255,.8)'; ctx.fillRect(Math.round(cxs) - 1, y - 2 * u, 2, 11 * u); }
      if (S.ult && S.ult.t < S.ult.warn) { ctx.strokeStyle = `rgba(255,30,20,${.5 + .4 * Math.sin(S.t * 18)})`; ctx.lineWidth = 10 * u; ctx.strokeRect(ox + 5 * u, oy + 5 * u, SW - 10 * u, SH - 10 * u);
        textOut('필살 · 대지 붕괴  ' + Math.max(0, S.ult.warn - S.ult.t).toFixed(1), cxs, oy + 62 * u, 17 * u, '#ff6040'); }
      textOut(`이동 방향키/WASD · 공격 ${keyHint('attack')} · 회피대시 Shift/${keyHint('dash')} (무적) · 조사 ${keyHint('interact')} · 물약 ${keyHint('potion')} · 지도 M · 미니맵 V · 목표 G · Esc`, cxs, oy + SH - (b && !b.dead ? 38 : 6) * u, 9 * u, 'rgba(230,230,240,.85)');
    }
    if (NAV() && m.type !== 'world') NAV().drawHud(k, ox, oy, u);
    if (S.banner) { const bn = S.banner, a = Math.max(0, Math.min(1, bn.t * 3, (bn.max - bn.t) * 6 + .2)); ctx.globalAlpha = a; textOut(bn.text, cxs, oy + (bn.small ? 82 : 90) * u, (bn.small ? 14 : 19) * u, bn.small ? '#ffd0a0' : '#ffe08a'); ctx.globalAlpha = 1; }
    if (S.msg) { ctx.globalAlpha = Math.min(1, S.msg.t * 3); ctx.font = font(12 * u); const tw = Math.max(300 * u, ctx.measureText(S.msg.text).width + 30 * u); panel(cxs - tw / 2, oy + SH - 90 * u, tw, 28 * u); textOut(S.msg.text, cxs, oy + SH - 71 * u, 12 * u, '#fff'); ctx.globalAlpha = 1; }
    if (S.dialog) { const x = ox + 30 * u, y = oy + SH - 108 * u, w = SW - 60 * u; panel(x, y, w, 84 * u);
      const pi = S.dialog.por && porImg(S.dialog.por), hasP = pi && pi.complete && pi.naturalWidth, tx = x + (hasP ? 96 : 18) * u;
      if (hasP) { ctx.imageSmoothingEnabled = true; ctx.drawImage(pi, x + 10 * u, y - 10 * u, 80 * u, 80 * u); ctx.imageSmoothingEnabled = false; }
      if (S.dialog.name) textOut(S.dialog.name, tx, y + 16 * u, 12 * u, '#ffe08a', '#000', 'left');
      S.dialog.text.split('\n').forEach((l, i) => textOut(l, tx, y + ((S.dialog.name ? 38 : 28) + i * 20) * u, 13 * u, '#fff', '#000', 'left'));
      textOut('▼ ' + keyHint('interact'), x + w - 14 * u, y + 76 * u, 10 * u, '#ffe08a', '#000', 'right'); }
    if (S.pause) { ctx.fillStyle = 'rgba(0,0,0,.5)'; ctx.fillRect(ox, oy, SW, SH); panel(cxs - 150 * u, oy + SH / 2 - 50 * u, 300 * u, 100 * u);
      textOut('일시정지', cxs, oy + SH / 2 - 14 * u, 20 * u, '#ffe08a'); textOut('Esc: 계속   ·   T: 마을로 귀환', cxs, oy + SH / 2 + 18 * u, 13 * u, '#fff'); }
    if (S.deadT > 0) { ctx.fillStyle = `rgba(60,0,0,${Math.min(.6, S.deadT)})`; ctx.fillRect(ox, oy, SW, SH); }
    if (m.type !== 'world') drawFieldUlt(k, ox, oy, SW, SH);
  }
  // ---------------- 필살기 (R) in fields / dungeons / boss rooms: reuses the town ULTS (천광낙뢰 / 멸계강림 / 찬검·해동), same cut-in timing,
  // world frozen + hero invulnerable for the whole move, damage to every enemy on screen. Consumes the full gauge (template ULT_CFG / addUlt).
  const FULT = { freeze: .2, cutin: 1.05, mob: 150, champ: .25, boss: .22 }; // total over all hits: normal mobs 150 (lethal), champion 25% / boss 22% of max HP (cap, so medium-hard bosses stay a fight)
  const PORI = {}; function porImg(id) { if (!PORI[id]) { const im = new Image(); im.src = 'assets/portraits/' + id + '.png'; PORI[id] = im; } return PORI[id]; }
  function onScreen(mm) { const x0 = S.camI[0], y0 = S.camI[1]; return mm.x > x0 - 8 && mm.x < x0 + LW + 8 && mm.y > y0 - 8 && mm.y < y0 + LH + 24; }
  function castUlt() { const g = window.__game; if (!g || !g.ULTS || !g.ULT_CFG || S.ultFx) return;
    if (g.ultG < g.ULT_CFG.max) { msg('필살기 게이지 부족 (' + Math.floor(g.ultG) + '%)'); return; }
    if (hero.hp <= 0 || S.deadT > 0) return;
    const U = g.ULTS[g.ultId ? g.ultId() : 'tenkou'] || g.ULTS.tenkou; g.ultG = 0; S.msg = null; hero.atk = null; hero.roll = null; hero.inv = 9; porImg(U.por);
    S.ultFx = { U, t: 0, hitI: 0, boomed: false, vic: S.mobs.filter(mm => !mm.dead && !(mm.spawnT > 0) && onScreen(mm)) };
    try { g.SFX.play('ult_cutin', 1); } catch (e) {} }
  function stepUlt(dt) { const f = S.ultFx, U = f.U, g = window.__game; f.t += dt; hero.inv = Math.max(hero.inv, 1); S.shake = Math.max(0, S.shake - dt * 14);
    const e = f.t - FULT.freeze - FULT.cutin;
    if (e >= 0 && !f.boomed) { f.boomed = true; shake(2); try { g.SFX.play('ult_boom', 1); } catch (er) {} } // modest: 2px boom, 1px per hit (world cap 3px + '화면 흔들림' option)
    while (e >= 0 && f.hitI < U.hitT.length && e >= U.hitT[f.hitI]) { f.hitI++; shake(1); const n = U.hitT.length;
      for (const mm of f.vic) { if (mm.dead || mm.invuln) continue; const D = mm.D, tot = D.boss ? mm.maxHp * FULT.boss : D.champion ? mm.maxHp * FULT.champ : FULT.mob, d = Math.max(1, Math.round(tot / n));
        mm.hp -= d; mm.hitT = .3; mm.flash = .12; mm.lagDelay = .35; addFx('spark', mm.x, mm.y - (D.h || 20) / 2, { life: .25 }); addFx('text', mm.x, mm.y - (D.h || 20) - 4 - f.hitI * 3, { text: String(d), life: .8, color: '#ffe9a8' });
        if (D.boss || D.champion) engage(mm); if (mm.hp <= 0) killMob(mm); } }
    if (e >= U.dur) { S.ultFx = null; hero.inv = .6; } }
  function drawFieldUlt(k, ox, oy, SW, SH) { const f = S.ultFx; if (!f) return; const U = f.U, u = k / 3, e = f.t - FULT.freeze - FULT.cutin, c = f.t - FULT.freeze;
    ctx.save(); ctx.beginPath(); ctx.rect(ox, oy, SW, SH); ctx.clip();
    ctx.fillStyle = `rgba(${U.tint},${.45 * Math.min(1, f.t / FULT.freeze)})`; ctx.fillRect(ox, oy, SW, SH);
    if (e >= 0) { ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < U.hitT.length; i++) { const q = (e - U.hitT[i] + .15) / .5; if (q < 0 || q > 1) continue; const al = 1 - q;
        if (U.id === 'chan') { const ang = [-.42, .38, -.12, .6, -.7][i % 5], cy = oy + SH * (.3 + .1 * i); ctx.save(); ctx.translate(ox + SW / 2, cy); ctx.rotate(ang); const L = SW * 1.4 * Math.min(1, q * 4);
          ctx.fillStyle = `rgba(${U.col[1]},${al * .6})`; ctx.fillRect(-L / 2, -14 * u * (1 - q), L, 28 * u * (1 - q)); ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.fillRect(-L / 2, -3 * u, L, 6 * u); ctx.restore(); }
        const list = f.vic.length ? f.vic : [{ x: hero.x + 40, y: hero.y }, { x: hero.x - 40, y: hero.y - 20 }];
        for (const mm of list) { const [sx, sy] = W2S(mm.x, mm.y); const w = (22 + (i % 2) * 8) * u * (1 - q * .5);
          const gr = ctx.createLinearGradient(0, oy, 0, sy); gr.addColorStop(0, `rgba(${U.col[2]},0)`); gr.addColorStop(.7, `rgba(${U.col[1]},${al * .7})`); gr.addColorStop(1, `rgba(${U.col[0]},${al})`);
          ctx.fillStyle = gr; ctx.fillRect(sx - w / 2, oy, w, sy - oy); ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.fillRect(sx - w * .18, oy, w * .36, sy - oy);
          ctx.fillStyle = `rgba(${U.col[1]},${al * .8})`; ctx.beginPath(); ctx.ellipse(sx, sy, w * 1.8 * (.6 + q), w * .6 * (.6 + q), 0, 0, TAU); ctx.fill(); } }
      ctx.globalCompositeOperation = 'source-over'; }
    if (c >= 0 && c < FULT.cutin) { const q = c / FULT.cutin, inn = Math.min(1, q / .15), out = q > .85 ? (q - .85) / .15 : 0, bh = SH * .34 * inn * (1 - out), by = oy + SH * .5;
      ctx.fillStyle = 'rgba(0,0,0,.55)'; ctx.fillRect(ox, oy, SW, SH);
      ctx.save(); ctx.translate(ox + SW / 2, by); ctx.rotate(-.06); ctx.fillStyle = '#07070c'; ctx.fillRect(-SW, -bh / 2, SW * 2, bh); const lw = Math.max(2, SH * .006);
      ctx.fillStyle = U.band; ctx.fillRect(-SW, -bh / 2, SW * 2, lw); ctx.fillRect(-SW, bh / 2 - lw, SW * 2, lw);
      const im = porImg(U.por);
      if (im.complete && im.naturalWidth) { const ih = bh * 1.25, iw = ih * im.naturalWidth / im.naturalHeight, ease = 1 - Math.pow(1 - Math.min(1, q / .3), 3), px = SW * .75 - ease * SW * .68 + q * SW * .04;
        ctx.save(); ctx.beginPath(); ctx.rect(-SW, -bh / 2, SW * 2, bh); ctx.clip(); ctx.imageSmoothingEnabled = false; ctx.drawImage(im, px - SW / 2, -ih * .42, iw, ih); ctx.restore(); }
      ctx.restore();
      const tx = ox + SW * .62 - (1 - Math.min(1, q / .25)) * SW * .3, fs = Math.round(SH * .085); ctx.globalAlpha = Math.min(1, q / .2) * (1 - out);
      textOut(U.name, tx, by + fs * .25, fs, U.band); textOut(U.route + ' 필살기 · ' + U.en, tx, by + fs * .25 + SH * .05, Math.round(SH * .026), '#fff'); ctx.globalAlpha = 1; }
    if (e >= 0 && e < .25) { ctx.fillStyle = `rgba(255,255,255,${.6 * (1 - e / .25)})`; ctx.fillRect(ox, oy, SW, SH); } // softer flash than the town (.9)
    ctx.restore(); }
  function b0() { const b = S.bossRef; return !!(b && !b.dead); }
  function hpBar(e, x, y, w, h) { x = Math.round(x - w / 2); y = Math.round(y); const fr = Math.max(0, e.hp / e.maxHp), lg = Math.max(fr, (e.hpLag ?? e.hp) / e.maxHp);
    ctx.fillStyle = e.hitT > .15 ? 'rgba(255,255,255,.8)' : 'rgba(8,6,14,.85)'; ctx.fillRect(x - 1, y - 1, w + 2, h + 2); ctx.fillStyle = '#3a1010'; ctx.fillRect(x, y, w, h);
    if (lg > fr) { ctx.fillStyle = '#ffd84a'; ctx.fillRect(x + w * fr, y, w * (lg - fr), h); }
    const c = fr > .5 ? ['#46d84a', '#a8f58a'] : fr > .25 ? ['#f0c030', '#fff0a0'] : ['#e83a2a', '#ff9a8a']; ctx.fillStyle = c[0]; ctx.fillRect(x, y, w * fr, h); ctx.fillStyle = c[1]; ctx.fillRect(x, y, w * fr, Math.max(1, h / 4)); }
  function heart(x, y, r, full) { ctx.fillStyle = '#1a0606'; hpath(x, y, r + 1.5); ctx.fill(); ctx.fillStyle = full ? '#e0201c' : '#3a1414'; hpath(x, y, r); ctx.fill(); if (full) { ctx.fillStyle = '#ffb4a0'; ctx.fillRect(x - r * .55, y - r * .45, r * .35, r * .3); } }
  function hpath(x, y, r) { ctx.beginPath(); ctx.moveTo(x, y + r); ctx.bezierCurveTo(x - r * 1.6, y - r * .1, x - r * .8, y - r * 1.3, x, y - r * .45); ctx.bezierCurveTo(x + r * .8, y - r * 1.3, x + r * 1.6, y - r * .1, x, y + r); }
  // title card (월드맵 진입 화면 / area / floor / boss): wipe bars sweep in, kicker + name + subtitle, wipe out
  function drawCard(tr, k) {
    const t = tr.t, c = tr.cardData, CW = cv.width, CH = cv.height, u = k / 3;
    ctx.fillStyle = '#05060c'; ctx.fillRect(0, 0, CW, CH);
    const wipeIn = Math.min(1, t / .45), wipeOut = Math.max(0, (t - (CARD - .45)) / .45), bars = 9;
    for (let i = 0; i < bars; i++) { const y0 = i * CH / bars, p = wipeIn - wipeOut, w = CW * Math.max(0, Math.min(1, p * 1.3 - i * .03));
      ctx.fillStyle = i % 2 ? '#0f1830' : '#122042'; ctx.fillRect(i % 2 ? CW - w : 0, y0, w, CH / bars + 1); }
    ctx.globalAlpha = Math.max(0, Math.min(1, (t - .3) * 3)) * (1 - wipeOut);
    const cx = CW / 2, cy = CH / 2, lw = 260 * u * Math.max(0, Math.min(1, (t - .3) * 2.5));
    ctx.strokeStyle = '#e2c27a'; ctx.lineWidth = 2 * u;
    ctx.beginPath(); ctx.moveTo(cx - lw, cy + 18 * u); ctx.lineTo(cx + lw, cy + 18 * u); ctx.stroke(); ctx.beginPath(); ctx.moveTo(cx - lw * .7, cy - 52 * u); ctx.lineTo(cx + lw * .7, cy - 52 * u); ctx.stroke();
    textOut(c.kicker || '', cx, cy - 62 * u, 14 * u, '#c9d3f0');
    textOut(c.name || '', cx, cy + 4 * u, 40 * u, '#ffe08a', '#3a1a00');
    textOut(c.sub || '', cx, cy + 46 * u, 18 * u, '#fff');
    ctx.globalAlpha = 1;
  }

  // ---------------- main loop: own fixed 60 fps timestep (independent of the town loop) ----------------
  let last = 0, acc = 0; const DT = 1 / 60;
  function publish() { // read by bgm.js: null = let the town decide
    const tr = S.trans; let bgm = null;
    if (S.scene !== 'town' || tr) { if (tr && tr.to === 'town') bgm = null; else if (S.jingleT > 0) bgm = null; else if (tr && tr.phase !== 'in' && tr.phase !== 'card' && S.scene === 'town') bgm = null; else bgm = S.bgm; }
    window.__scene = { active: active(), scene: S.scene, map: S.map && S.map.id, bgm, jingle: S.jingleT > 0 };
  }
  function frame(t) {
    const dt = Math.min(.1, (t - last) / 1000 || 0); last = t;
    if (!manual) { if (S.scene === 'town' && !S.trans) watchTown(); else { acc += dt; let n = 0; while (acc >= DT && n < 6) { step(DT); acc -= DT; n++; } if (n >= 6) acc = 0; } }
    if (S.scene !== 'town' || S.trans) render();
    publish();
    requestAnimationFrame(frame);
  }
  window.__worldHooks = { hudY: () => S.hudY, S, M, MAPS, loadMap, renderGround, hero, get SAVE() { return SAVE; }, save, go, takePress, isHeld, held, queue, codesOf, keyHint, textOut, panel, font, W2S, ctx, cv, drawSpr, msg, banner, giveLoot, addFx, syncTownHp, LW, LH, TAU, get IMG() { return IMG; }, get ATLAS() { return ATLAS; }, ready };
  const W_API = window.__world = {
    WORLD_ZOOM, LW, LH, ROLL, ready: false, hero, S, get SAVE() { return SAVE; }, get scene() { return S.scene; }, get map() { return S.map; }, get mobs() { return S.mobs; }, get trans() { return S.trans; },
    go, dirTap, RUN, SWING, swingR, hbR, hbA, spOf, arcW, setManual(v) { manual = v; },
    advance(sec) { for (let t = 0; t < sec - 1e-9; t += DT) { if (S.scene === 'town' && !S.trans) watchTown(); else step(DT); } render(); publish(); },
    key(code, down) { if (down) { if (!held.has(code)) queue.push(code); held.add(code); } else held.delete(code); },
    tap(code) { queue.push(code); },
    flag(id, v = true) { SAVE.flags[id] = v; save(); }, reset() { SAVE = { flags: {}, chests: {}, keys: {}, opened: {}, levers: {}, visited: {}, explored: {}, waystones: {}, landmarks: {}, quests: {}, pin: null, dest: null }; save(); if (NAV()) NAV().reset(); },
    get nav() { return NAV(); },
    killAll(filter) { S.mobs.filter(m => !m.dead && (!filter || filter(m))).forEach(killMob); },
    hurt, spawn, render, tile: () => [Math.floor(hero.x / S.map.T), Math.floor(hero.y / S.map.T)],
    setHeroTile(x, y, face) { hero.x = (x + .5) * S.map.T; hero.y = (y + .5) * S.map.T; if (face) hero.face = face; snapCam(); },
    castUlt, get ultFx() { return S.ultFx; }, get hazards() { return S.hazards; }, get boss() { return S.bossRef; }, get objs() { return S.map && S.map.objs; },
  };
  // ?go=world | field00..field09 | dungeon01_b1 ... : start straight in that scene instead of the town (owner 10-22 "실행할수 있게")
  const GO = new URLSearchParams(location.search).get('go');
  if (GO) ready.then(() => { const t = setInterval(() => { if (!window.__game) return; clearInterval(t); go(GO, 'default'); }, 100); });
  ready.then(() => { W_API.ready = true; requestAnimationFrame(t => { last = t; requestAnimationFrame(frame); }); }).catch(e => console.error('[world] init failed', e));
})();
