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
  const BUILD_V = (Date.parse(document.lastModified) || 0).toString(36); // deploy stamp (see index.html): new deploy -> new asset URLs
  const V = u => (window.__v ? __v(u) : u); // 지도·그림 주소에 배포 시각 붙이기 (index.html __v)
  function fieldDash(D) { return D.travel ? D.travel * 1.5 / 124 * H128FIG : D.tiles * 16 * .68; } // town: travel (=150 logical px / LSC 1.5) for a 124 px figure -> same ratio for the 30 px field figure (36 px, 1.21 hero-heights)
  function rollDur() { const D = DG(); return D ? D.durTicks / 60 : ROLL.dur; }
  // [balance] levels.json roll.base: 0.18s i-frames in a 0.22s roll, 0.40s cooldown (speed raised so the roll still covers ~40px)
  // [balance] numeric HP (hero 50), hero combo 10/10/14, difficulty multipliers from the town template (window.__game.diff = levels.json difficulty.levels[])
  const ATK_DMG = [10, 10, 20]; // [combat research] hit 3 14 -> 20 so the full combo out-damages hit-1 spam
  const ATK_MOVE = 0.7; // [combat research] move speed kept while a basic swing plays (stick held)
  const POT = { heal: 30, cd: 4.0, heartPct: 5, heartDrop: 0.04 };
  // 심연의 힘 (주인 10-23, 벌칙 없는 역전 장치 · 가슴 속 사멸의 코어가 새어 나옴): 맞아서 체력이 25% 이하가 되면 8초 동안 공격·검기 x1.8, 45초마다 한 번
  const LAST_STAND = { hpPct: 0.25, dur: 8, cd: 20, atk: 1.8, flag: 'abyss_awake' }; // cd: 초필살기를 아직 안 썼으면 20초 뒤 다시 켜질 수 있음 (쓰고 나면 쉼터에서 쉴 때까지 끝) // 중반 해금: 5장 보스 발바도스를 베면 flag (폭주의 기억). 시험용 ?abyss=1
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
  const low = document.createElement('canvas'); low.width = LW + 1; low.height = LH + 1; const lx = low.getContext('2d'); let EW = LW, EH = LH; // EW x EH = world px on screen (bigger than LW x LH when a town view zooms out, owner 10-23 「마을 카메라 조금 멀리」) // +1: the sub-pixel camera shifts it by the fraction (owner 10-23 「걸을때 뛸때 화면이 흔들린다」)
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
  if (Q.has('worldreset') && !navigator.webdriver) { try { localStorage.setItem(LS, JSON.stringify(SAVE)); } catch (e) {} try { const u = new URL(location.href); u.searchParams.delete('worldreset'); history.replaceState(null, '', u.pathname + u.search.replace(/=(&|$)/g, '$1') + u.hash); } catch (e) {} } // new game: wipe once, then drop the flag so a page refresh keeps the progress
  for (const k of ['explored', 'waystones', 'landmarks', 'quests']) SAVE[k] = SAVE[k] || {};
  if (SAVE.fogV !== 'temple01') { for (const k of ['field00', 'field01', 'dungeon01_b1', 'dungeon01_b2']) delete SAVE.explored[k]; SAVE.fogV = 'temple01'; } // 바람길 + 시작의 숲 stitched into one map (owner 10-23)
  const save = () => { try { localStorage.setItem(LS, JSON.stringify(SAVE)); } catch (e) {} };

  // ---------------- assets ----------------
  const IMG = {}; let ATLAS = null, TILESETS = null; const MAPS = {};
  const loadImg = (k, src) => new Promise((res, rej) => { const i = new Image(); i.onload = () => { IMG[k] = i; res(); }; i.onerror = () => rej(new Error('load ' + src)); i.src = V(src); });
  const getJSON = u => fetch(window.__v ? __v(u) : u).then(r => { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); });
  function loadMap(id) { return MAPS[id] ? Promise.resolve(MAPS[id]) : getJSON('maps/' + id + '.json').then(j => j.compose ? composeMap(j) : j.bg ? loadBg(j) : j).then(loadHD).then(j => (MAPS[id] = buildMap(j))); }
  // 고해상도 배경 (owner 10-23 「펠트 마을 최고 퀄리티」, 마을배경방과 정한 형식): map JSON "hd" = {D, ground, props[], lights[], grade}.
  // Drawn at the characters' pixel density (D art px per world px) on the screen canvas, not in the 384x216 low canvas: the ground picture
  // under everything, props (buildings / trees) one by one, y-sorted with the hero (see-through when the hero is behind), light pools on top.
  const HDIMG = {};
  function loadHD(j) { if (!j.hds && j.hd) j.hds = [Object.assign({}, j.hd, { gx: 0, gy: 0 })]; if (!j.hds) return j;
    const urls = new Set(); for (const h of j.hds) { if (h.ground) urls.add(h.ground); for (const q of h.props || []) urls.add(q.img); for (const k in h.decoArt || {}) for (const v of h.decoArt[k]) urls.add(v.img); }
    return Promise.all([...urls].map(u => HDIMG[u] ? 0 : new Promise(res => { const im = new Image(); im.onload = () => { HDIMG[u] = im; res(); }; im.onerror = () => res(); im.src = V(u); }))).then(() => j); }
  // 이어 붙인 지도 (세미 오픈월드, owner 10-23 「추천대로」): j.compose = [{map, x, y}] -> the part maps are read as they are (other rooms keep editing
  // felt.json / field_felt.json) and laid side by side into ONE map: ground rows, objects, spawns ('<part>:<name>'), exits between parts dropped.
  // Each part becomes an area {part, name, sub, bgm, grade, bg}: painted backgrounds and colour grades stay per part, the music follows the area.
  function composeMap(j) { return Promise.all(j.compose.map(p => getJSON('maps/' + p.map + '.json').then(r => r.bg ? loadBg(r) : r))).then(parts => {
    const ids = j.compose.map(p => p.map), W = Math.max(...j.compose.map((p, i) => p.x + parts[i].w)), H = Math.max(...j.compose.map((p, i) => p.y + parts[i].h));
    const rows = Array.from({ length: H }, () => Array(W).fill('#')), legend = {}, solid = new Set(), objects = [], spawns = {}, areas = [], chests = {};
    j.compose.forEach((p, i) => { const r = parts[i]; Object.assign(legend, r.legend || {}); for (const c of r.solid || []) solid.add(c);
      r.ground.forEach((row, y) => { for (let x = 0; x < r.w; x++) rows[p.y + y][p.x + x] = row[x] || '#'; });
      for (const o of r.objects || []) { if (o.type === 'exit' && (ids.includes(o.to) || (j.dropExits || []).includes(o.to))) continue; objects.push(Object.assign({}, o, { x: o.x + p.x, y: o.y + p.y })); }
      for (const k in r.spawns || {}) { const v = r.spawns[k]; spawns[p.map + ':' + k] = [v[0] + p.x, v[1] + p.y].concat(v.slice(2)); }
      for (const k in r.chests || {}) { const [cx, cy] = k.split(',').map(Number); chests[(cx + p.x) + ',' + (cy + p.y)] = r.chests[k]; }
      if (r.hd) (j._hds = j._hds || []).push(Object.assign({}, r.hd, { gx: p.x, gy: p.y }));
      areas.push({ town: r.type === 'town', zoom: r.viewZoom, id: p.map, part: p.map, name: (r.title && r.title.name) || r.name, sub: (r.title && r.title.sub) || '', x: p.x, y: p.y, w: r.w, h: r.h, bgm: r.bgm, battleBgm: r.battleBgm, grade: r.grade, bg: r.bg }); });
    spawns.default = spawns.default || spawns[ids[0] + ':default'];
    return Object.assign({}, parts[0], j, { type: 'field', w: W, h: H, ground: rows.map(r => r.join('')), legend, solid: [...solid], objects, spawns, chests, areas: j.areas || areas, bg: null, grade: null,
      title: j.title || parts[0].title, name: j.name || parts[0].name, bgm: parts[0].bgm, mapPos: [0, 0], hd: null, hds: j._hds || null }); }); }
  function composeGround(m) { const c = renderGround(m), g = c.getContext('2d'), T = m.T; // tiles everywhere, then each part's painting / grade on its own rectangle
    for (const a of m.areas) { const x = a.x * T, y = a.y * T, w = a.w * T, h = a.h * T;
      if (a.bg && BGIMG[a.bg]) { g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high'; g.drawImage(BGIMG[a.bg], x, y, w, h); g.imageSmoothingEnabled = false; continue; }
      if (a.grade) { const sub = document.createElement('canvas'); sub.width = w; sub.height = h; sub.getContext('2d').drawImage(c, x, y, w, h, 0, 0, w, h);
        const sm = { T, w: a.w, h: a.h, pw: w, ph: h, grade: a.grade, solidG: Uint8Array.from({ length: a.w * a.h }, (_, i) => m.solidG[(a.y + Math.floor(i / a.w)) * m.w + a.x + i % a.w]) };
        scarGround(sm, gradeCanvas(sub, a.grade)); g.clearRect(x, y, w, h); g.drawImage(sub, x, y); } }
    return c; }
  const areaOf = (m, x, y) => (m && m.areas) ? m.areas.find(a => x >= a.x * m.T && x < (a.x + a.w) * m.T && y >= a.y * m.T && y < (a.y + a.h) * m.T) || null : null;
  const gradeAt = (m, x, y) => { const a = m && m.compose ? areaOf(m, x, y) : null; return a ? a.grade : m && m.grade; };
  // painted-background maps (town B): j.bg = image drawn over the whole map instead of tiles; ground rows only carry collision
  const BGIMG = {};
  function loadBg(j) { return new Promise(res => { const im = new Image(); im.onload = () => { BGIMG[j.bg] = im; res(j); }; im.onerror = () => res(j); im.src = V(j.bg); }); }
  const NPCIMG = {};
  function npcImg(id) { if (!NPCIMG[id]) { const im = new Image(); im.src = V('assets/npcs/' + id + '.png'); NPCIMG[id] = im; } return NPCIMG[id]; }
  // Felt NPCs (owner 10-23): 4-way walk/idle atlas assets/npcs/felt/<anim>.json (hero atlas format, figure ~118 px = hero scale), drawn hi-res like the hero
  const NPCA = {};
  function npcAnim(id) { if (NPCA[id] === undefined) { NPCA[id] = null; const P = id.includes('/'), base = P ? 'assets/' : 'assets/npcs/felt/'; // 'anim/hero8' style ids = any hero-format atlas (dialogue portraits)
      getJSON(base + (P ? id : id) + '.json').then(j => { const ims = j.sheets.map(() => null), want = new Set(['idle_south', 'idle_down', 'idle_up', 'idle_right', 'idle_left', 'walk_down', 'walk_up', 'walk_right', 'walk_left'].flatMap(k => (j.anims[k] || []).map(q => q[0]))); let n = 0;
        j.sheets.forEach((sh, i) => { if (!want.has(i)) return; const im = new Image(); im.onload = () => { ims[i] = im; if (++n === want.size) NPCA[id] = { J: j, im: ims[0], ims }; }; im.src = V(base + sh); }); }).catch(() => {}); } return NPCA[id]; }
  const PORIMG = {};
  function porImg(id) { if (!PORIMG[id]) { const im = new Image(); im.src = V('assets/portraits/' + id + '.png'); PORIMG[id] = im; } return PORIMG[id]; }
  const ready = getJSON('assets/world/world_atlas.json').then(a => { ATLAS = a;
    return Promise.all([loadImg('field', 'assets/' + a.sheets.field.src), loadImg('dungeon', 'assets/' + a.sheets.dungeon.src), loadImg('spr', 'assets/' + a.sprites.src),
      getJSON('maps/tilesets.json').then(t => TILESETS = t)]); }).then(() => loadMap('world'));

  // sprite helpers ------------------------------------------------------------
  const tintCache = {};
  // 맵 색 보정 (map JSON "grade"): 'ash' = 잿빛 들판 (주인 10-23 "다시 칠해라") — ground + scenery only; hero, mobs and effects keep their colours
  const GRADE = { ash: (r, g, b) => { const L = (r * .3 + g * .59 + b * .11) * .82, k = .9, t = [L * .9 + 12, L * .84 + 9, L * .88 + 14]; return [r + (t[0] - r) * k, g + (t[1] - g) * k, b + (t[2] - b) * k]; } };
  function gradeCanvas(c, mode) { const f = GRADE[mode]; if (!f) return c; const g = c.getContext('2d'), d = g.getImageData(0, 0, c.width, c.height), a = d.data;
    for (let i = 0; i < a.length; i += 4) { if (!a[i + 3]) continue; const o = f(a[i], a[i + 1], a[i + 2]); a[i] = o[0]; a[i + 1] = o[1]; a[i + 2] = o[2]; } g.putImageData(d, 0, 0); return c; }
  function scarGround(m, c) { if (m.grade !== 'ash') return c; const g = c.getContext('2d'), T = m.T, R = n => { const x = Math.sin(n * 91.7 + m.w) * 43758.5453; return x - Math.floor(x); }; // 그을린 자국 + 거미줄 실, baked once (dither, no gradients)
    const free = (x, y) => { const tx = Math.floor(x / T), ty = Math.floor(y / T); return tx >= 0 && ty >= 0 && tx < m.w && ty < m.h && !m.solidG[ty * m.w + tx]; };
    for (let i = 0; i < 46; i++) { const cx = R(i) * m.pw, cy = R(i + 300) * m.ph; if (!free(cx, cy)) continue; const rx = 8 + R(i + 600) * 22, ry = rx * .45;
      for (let y = -ry; y <= ry; y++) for (let x = -rx; x <= rx; x++) { const q = (x / rx) ** 2 + (y / ry) ** 2; if (q > 1) continue; const px = Math.round(cx + x), py = Math.round(cy + y); if (q > .55 && (px + py) & 1) continue; if (q > .82 && (px & 1)) continue;
        g.fillStyle = q < .3 ? 'rgba(14,10,16,.55)' : 'rgba(26,20,24,.4)'; g.fillRect(px, py, 1, 1); } }
    for (let i = 0; i < 18; i++) { let ax = R(i + 900) * m.pw, ay = R(i + 1200) * m.ph, bx = ax + (R(i + 1500) - .5) * 70, by = ay + (R(i + 1800) - .3) * 40; // threads strung between nearby trees
      const sag = 6 + R(i + 2100) * 8, n = Math.ceil(Math.hypot(bx - ax, by - ay)); g.fillStyle = 'rgba(214,206,220,.5)';
      for (let k = 0; k <= n; k += 1) { const t = k / n, x = ax + (bx - ax) * t, y = ay + (by - ay) * t + Math.sin(t * Math.PI) * sag; if (k % 3 !== 2) g.fillRect(Math.round(x), Math.round(y), 1, 1); }
      if (i % 3 === 0) { const wx = Math.round(ax), wy = Math.round(ay); g.fillStyle = 'rgba(220,214,228,.42)'; for (let a = 0; a < 6; a++) { const an = a / 6 * Math.PI * 2; for (let d = 1; d < 7; d++) g.fillRect(Math.round(wx + Math.cos(an) * d), Math.round(wy + Math.sin(an) * d * .7), 1, 1); }
        for (let rr = 3; rr <= 6; rr += 3) for (let a = 0; a < 18; a++) { const an = a / 18 * Math.PI * 2; g.fillRect(Math.round(wx + Math.cos(an) * rr), Math.round(wy + Math.sin(an) * rr * .7), 1, 1); } } }
    return c; }
  function drawAshFall(g, m, cx, cy) { if (m.grade !== 'ash') return; for (let i = 0; i < 46; i++) { const h1 = Math.sin(i * 12.9898) * 43758.5453 % 1, h2 = Math.sin(i * 78.233) * 12345.678 % 1, sp = 6 + Math.abs(h2) * 10; // slow falling ash (screen space)
      const x = ((Math.abs(h1) * EW + Math.sin(S.t * .6 + i) * 6) % EW + EW) % EW, y = ((Math.abs(h2) * EH + S.t * sp) % (EH + 8)) - 4; g.fillStyle = i % 5 ? 'rgba(196,190,204,.55)' : 'rgba(255,170,110,.6)'; g.fillRect(Math.round(cx + x), Math.round(cy + y), 1, 1); } }
  // 던전 분위기 층 (팀장 마을배경방, 주인 10-24 「다크한 설정이 잘 나오게 · 웅장한 보스전」): m.dark 지도 전부 — 떠도는 먼지(어둠 아래라 빛 근처만 보임),
  // 천장에서 늘어진 실 가닥(월드에 붙어 흔들림), 위에서 비스듬히 내려오는 희미한 빛줄기, 가장자리 어둠. 보스 2페이즈면 붉게 맥박친다.
  const hsh = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  function lairP2() { for (const mm of S.mobs) if (mm.D && mm.D.boss && mm.phase === 2 && mm.hp > 0) return true; return false; }
  function drawLairBelow(g, m, cx, cy) { if (!m.dark) return; const p2 = lairP2();
    for (let i = 0; i < 44; i++) { const a = hsh(i), b = hsh(i + 50), sp = 2 + b * 3; // dust motes
      const x = ((a * EW + S.t * sp + Math.sin(S.t * .4 + i) * 5) % EW + EW) % EW, y = ((b * EH - S.t * (1 + a) + Math.sin(S.t * .7 + i * 2) * 3) % EH + EH) % EH;
      g.fillStyle = p2 && i % 3 === 0 ? 'rgba(255,90,90,.55)' : 'rgba(214,206,226,.45)'; g.fillRect(Math.round(cx + x), Math.round(cy + y), 1, 1); }
    const step = 29, x0 = Math.floor(cx / step) * step; g.save(); g.lineWidth = 1; // thread strands hanging into view from above
    for (let wx = x0; wx < cx + EW + step; wx += step) { const k = Math.floor(wx / step), r = hsh(k); if (r < .45) continue;
      const len = 14 + hsh(k + 9) * 46, sw = Math.sin(S.t * (.8 + r) + k) * (2 + r * 3), top = cy - 2, ex = wx + sw, ey = top + len;
      g.strokeStyle = p2 ? `rgba(220,60,70,${.28 + .12 * Math.sin(S.t * 4 + k)})` : 'rgba(226,220,236,.22)';
      g.beginPath(); g.moveTo(wx, top); g.quadraticCurveTo(wx + sw * .3, top + len * .6, ex, ey); g.stroke();
      if (r > .8) { g.fillStyle = p2 ? 'rgba(200,50,60,.5)' : 'rgba(230,226,240,.35)'; g.fillRect(Math.round(ex) - 1, Math.round(ey), 2, 3); } } // a tiny cocoon bead
    g.restore(); }
  function drawLairAbove(g, m) { if (!m.dark) return; const p2 = lairP2(); g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
    g.globalCompositeOperation = 'lighter'; for (let i = 0; i < 3; i++) { const br = .035 + .02 * Math.sin(S.t * .5 + i * 2), x = EW * (.18 + i * .32); // faint light shafts from cracks above
      const gr = g.createLinearGradient(x, 0, x + EH * .45, EH); gr.addColorStop(0, `rgba(${p2 ? '200,90,110' : '170,165,210'},${br})`); gr.addColorStop(1, 'rgba(0,0,0,0)');
      g.fillStyle = gr; g.beginPath(); g.moveTo(x - 10, 0); g.lineTo(x + 14, 0); g.lineTo(x + 14 + EH * .45, EH); g.lineTo(x - 10 + EH * .45, EH); g.closePath(); g.fill(); }
    g.globalCompositeOperation = 'source-over';
    const vg = g.createRadialGradient(EW / 2, EH * .48, Math.min(EW, EH) * .38, EW / 2, EH * .48, Math.max(EW, EH) * .72); // edge darkness
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, p2 ? `rgba(34,0,6,${.5 + .06 * Math.sin(S.t * 3)})` : 'rgba(2,2,8,.55)'); g.fillStyle = vg; g.fillRect(0, 0, EW + 1, EH + 1);
    // (2페이즈 화면 전체 붉은 칠은 뺌: 지도 담당의 붉은 빛과 겹쳐 붉은 예고가 안 보였음 → 가장자리만 붉게)
    g.restore(); }
  function sprCanvas(name, mode) { // mode: 'white' flash | 'rage' red | 'gray' | a GRADE name
    const key = name + '|' + mode; if (tintCache[key]) return tintCache[key];
    const r = ATLAS.sprites.rects[name]; if (!r) return null;
    const c = document.createElement('canvas'); c.width = r[2]; c.height = r[3]; const g = c.getContext('2d');
    g.drawImage(IMG.spr, r[0], r[1], r[2], r[3], 0, 0, r[2], r[3]);
    if (mode === 'white') { g.globalCompositeOperation = 'source-atop'; g.fillStyle = '#fff'; g.fillRect(0, 0, r[2], r[3]); }
    if (mode === 'dodge') { const AI = (DG() && DG().afterimage) || {}; if (AI.tint && AI.tintMix && AI.keepTint) { g.globalCompositeOperation = 'source-atop'; g.globalAlpha = AI.tintMix; g.fillStyle = AI.tint; g.fillRect(0, 0, r[2], r[3]); g.globalAlpha = 1; } } // 회피대시 잔상 = 주인공 모습 그대로 (주인 10-24 「푸른 잔상 → 주인공 모습 그대로」): 색 덮기 없음, 투명도만
    if (GRADE[mode]) gradeCanvas(c, mode);
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
      if (L.hop) { (m.hopG || (m.hopG = new Uint8Array(j.w * j.h)))[y * j.w + x] = 1; solid = true; } // 점프로만 넘는 칸 (울타리·개울·구멍; 3번방 약속 10-24)
      m.solidG[y * j.w + x] = solid ? 1 : 0;
      if (L.deco) m.decos.push({ x: (x + .5) * T, y: (y + 1) * T - 1, spr: L.deco, tx: x, ty: y, solid });
      if (L.obj) m.objs.push(mkObj(m, L.obj, x, y));
    }
    const byId = {}; for (const o of (j.objects || [])) if (o.id) byId[o.id] = o; // NPC spot relative to a building/landmark: near:[id,dx,dy] (owner 10-23, survives a village re-layout)
    for (const o of (j.objects || [])) if (o.near && byId[o.near[0]]) { const r = byId[o.near[0]]; o.x = r.x + o.near[1]; o.y = r.y + o.near[2]; }
    for (const o of (j.objects || [])) if (!['spawn', 'champion', 'mark'].includes(o.type)) m.objs.push(Object.assign({}, o, { tx: o.x, ty: o.y, x: (o.x + .5) * T, y: (o.y + .5) * T }));
    for (const o of m.objs) if (['chest', 'sign', 'heal', 'waystone', 'npc', 'door'].includes(o.type) && !o.walk && !o.wander) m.solidG[Math.floor(o.ty) * j.w + Math.floor(o.tx)] = 1;
    for (const o of m.objs) if (o.type === 'secret_wall') m.solidG[Math.floor(o.ty) * j.w + Math.floor(o.tx)] = SAVE.flags[o.flag] ? 0 : 1; // 숨은 방: a cracked wall tile
    for (const h of j.hds || []) { const im = HDIMG[h.ground], A = h.decoArt; if (!A || !im) continue; const hw = im.width / h.D / T, hh = im.height / h.D / T; // hd deco art (decoArt {legend char or deco name: [{img, ax, ay, flip}]}):
      for (const d of m.decos) { const vs = A[(j.ground[d.ty] || '')[d.tx]] || A[d.spr]; if (!vs || !vs.length || d.tx < h.gx || d.ty < h.gy || d.tx >= h.gx + hw || d.ty >= h.gy + hh) continue; // the tile deco keeps its rules (solid, breakable, pillar shade)
        const f = n => { const v = Math.sin(d.tx * 127.1 + d.ty * 311.7 + n * 74.7) * 43758.5453; return v - Math.floor(v); }, v = vs[Math.floor(f(1) * vs.length)]; // and only its picture changes: variant, flip, jitter per tile
        const jt = v.flip === false ? 0 : 1; d.hd = { v, D: v.D || 3, flip: jt && f(2) < .5, dx: jt * Math.round((f(3) - .5) * 5), dy: jt * Math.round((f(4) - .5) * 3) }; } } // flip:false = a tiling piece (fence): no flip, no jitter
    m.hds = j.hds || null; for (const h of m.hds || []) for (const q of h.props || []) if (q.solid) { const [x0, y0, x1, y1] = q.solid; for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) { const X = x + h.gx, Y = y + h.gy; if (X >= 0 && Y >= 0 && X < j.w && Y < j.h) m.solidG[Y * j.w + X] = 1; } }
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
    interact: ['KeyL', 'KeyC', 'Enter'], dive: ['Space'], potion: ['KeyE'], ult: ['KeyR'], menu: ['Escape'], save: ['F5'] };
  function KM() { const g = window.__game; return (g && g.ctl && g.ctl.KEYMAP) || DEFKEYS; }
  const ARROW = { up: 'ArrowUp', down: 'ArrowDown', left: 'ArrowLeft', right: 'ArrowRight' }; // 방향키는 언제나 이동 (owner 10-23)
  function codesOf(a) { const l = (KM()[a] || DEFKEYS[a] || []).slice(); if (ARROW[a] && !l.includes(ARROW[a])) l.push(ARROW[a]); if (a === 'dash') l.push('ShiftLeft', 'ShiftRight'); if (a === 'menu' && !l.includes('Escape')) l.push('Escape'); return l; }
  const isHeld = a => codesOf(a).some(c => held.has(c));
  const takePress = a => { const cs = codesOf(a); const i = queue.findIndex(c => cs.includes(c)); if (i < 0) return false; queue.splice(i, 1); return true; };
  const active = () => (S.scene !== 'town' || !!S.trans) && !(window.__game && window.__game.ui); // a DOM UI (shop over a town-B door) takes the keys
  addEventListener('keydown', e => { if (!active() || PASS.has(e.code)) return; e.preventDefault(); e.stopPropagation();
    if (!e.repeat) { queue.push(e.code); for (const d of ['up', 'down', 'left', 'right']) if (codesOf(d).includes(e.code)) dirTap(d); } held.add(e.code); if (queue.length > 8) queue.shift(); }, true);
  // double-tap a direction (press->press <= .25s) -> dash start + run while held (same rule as the town; Esc '달리기 기본' = always run)
  const lastTap = {}; function dirTap(d) { const now = performance.now() / 1000; if (now - (lastTap[d] ?? -9) <= RUN.dblTap) hero.runReq = true; lastTap[d] = now; }
  addEventListener('keyup', e => { held.delete(e.code); }, true);
  addEventListener('blur', () => held.clear());

  // ---------------- 폰 터치 (사장님 10-23 "핸드폰으로 조작하게"): 마을 화면의 이동 패드·공격·대시·달리기 버튼을 게임 지도 위로 올리고,
  // 공격 버튼을 이쪽 공격 키(J)에 잇고, 지도에서 필요한 조사·물약·필살기·메뉴 버튼을 더함(키를 누른 것처럼 보냄). 키보드 조작은 그대로.
  { const st = document.createElement('style'); st.textContent = 'body.touch.inworld #ui{z-index:45;visibility:visible!important} body.touch.inworld #ui>*{visibility:visible} body.inworld #ui>.slot,body.inworld #slotsKeys,body.inworld #wbtn,body.inworld #hint,body.inworld #khud,body.inworld #qslot{display:none!important}'
      + '.wtb{position:fixed;display:none;border-radius:50%;pointer-events:auto;text-align:center;color:#fff6e0;font:bold 15px sans-serif;border:4px solid #1a1206;box-shadow:0 0 0 3px #e8d6b0 inset,0 4px 0 #000a;text-shadow:2px 2px 0 #000;user-select:none;-webkit-user-select:none;touch-action:none}'
      + '.wtb.on{transform:scale(.92);filter:brightness(1.25)} body.touch.inworld .wtb{display:block}'
      + 'body.wdlg #atk,body.wdlg #dashb,body.wdlg #runb,body.wdlg #stick,body.wdlg .wtb:not(#wtb_act):not(#wtb_menu){opacity:0!important;pointer-events:none!important;transition:opacity .15s}'
      + '#wtb_ult{right:max(34px,env(safe-area-inset-right));bottom:max(148px,calc(env(safe-area-inset-bottom) + 118px));width:72px;height:72px;line-height:64px;background:radial-gradient(circle at 40% 35%,#ffe9a0,#d09a20 60%,#6a4608)}'
      + '#wtb_act{right:max(124px,calc(env(safe-area-inset-right) + 96px));bottom:max(196px,calc(env(safe-area-inset-bottom) + 166px));width:60px;height:60px;line-height:52px;background:radial-gradient(circle at 40% 35%,#d8d0ff,#6a5ab8 60%,#2e2466)}'
      + '#wtb_pot{right:max(40px,env(safe-area-inset-right));bottom:max(232px,calc(env(safe-area-inset-bottom) + 202px));width:60px;height:60px;line-height:52px;background:radial-gradient(circle at 40% 35%,#ffb0c0,#c03050 60%,#5a1020)}'
      + '#wtb_pot .pc{position:absolute;right:-6px;top:-8px;min-width:22px;height:22px;line-height:18px;border-radius:11px;background:#141826;border:2px solid #e8d6b0;font:bold 12px sans-serif;text-shadow:none}#wtb_pot::after{content:"";position:absolute;inset:0;border-radius:50%;background:conic-gradient(rgba(0,0,0,.55) var(--cd,0%),transparent 0);pointer-events:none}#wtb_pot.zero{filter:grayscale(1) brightness(.6)}'
      + '#wtb_menu{left:50%;transform:translateX(-50%);top:max(8px,env(safe-area-inset-top));width:auto;height:auto;padding:4px 14px;border-radius:12px;font-size:13px;line-height:18px;background:#1b2550}#wtb_menu.on{transform:translateX(-50%) scale(.92)}';
    document.head.appendChild(st); const ui = document.getElementById('ui') || document.body;
    const send = (code, down) => dispatchEvent(new KeyboardEvent(down ? 'keydown' : 'keyup', { code, key: code, bubbles: true }));
    const wire = (el, code) => { if (!el) return; const dn = e => { if (!active()) return; e.preventDefault(); e.stopImmediatePropagation(); el.classList.add('on'); send(code, true); },
      up = e => { if (!active()) return; e.preventDefault(); e.stopImmediatePropagation(); el.classList.remove('on'); send(code, false); };
      el.addEventListener('touchstart', dn, { passive: false, capture: true }); el.addEventListener('touchend', up, { passive: false, capture: true }); el.addEventListener('touchcancel', up, { passive: false, capture: true }); };
    wire(document.getElementById('atk'), 'KeyJ'); wire(document.getElementById('jumpb'), 'Space'); // 점프 버튼 (10-24) // town attack button -> this scene's attack key (hold = charge, same as the key)
    for (const [id, label, code] of [['wtb_ult', '필살기', 'KeyR'], ['wtb_act', '조사', 'KeyL'], ['wtb_pot', '물약', 'KeyE'], ['wtb_menu', '메뉴', 'Escape']]) { const el = document.createElement('div'); el.id = id; el.className = 'wtb'; el.textContent = label; ui.appendChild(el); wire(el, code); } }

  addEventListener('pointerdown', e => { if (S.dialog && e.target && e.target.tagName === 'CANVAS') S.dlgTap = true; }); // phone: tap the picture to go on
  // ---------------- helpers ----------------
  const M = () => S.map;
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  function solidAt(px, py) { const m = M(); if (!m) return true; const x = Math.floor(px / m.T), y = Math.floor(py / m.T);
    if (x < 0 || y < 0 || x >= m.w || y >= m.h) return true; if (m.solidG[y * m.w + x] && !(hopNow && m.hopG && m.hopG[y * m.w + x])) return true;
    for (const t of S.temp) if (Math.hypot(px - t.x, py - t.y) < t.r) return true;
    for (const o of m.objs) if (o.wander && o !== npcSelf && Math.abs(px - o.x) < 5 && py > o.y + 2 && py < o.y + 9) return true; return false; }
  let npcSelf = null;
  // Felt NPC wander: idle 2-5 s, then walk to a random free spot within o.wander tiles of the home spot; stop and face the hero when he comes close
  function stepNpcs(dt) { const m = M();
    for (const o of m.objs) { if (o.type !== 'npc' || !o.wander) continue;
      if (o.hx === undefined) { o.hx = o.x; o.hy = o.y; o.wt = 1 + Math.random() * 3; o.face = o.face0 || 'down'; o.at = Math.random() * 9; }
      o.at += dt; const dh = Math.hypot(hero.x - o.x, hero.y - o.y);
      if (dh < 28 || S.talked === o.id && S.dialog) { o.tgt = null; const dx = hero.x - o.x, dy = hero.y - o.y; o.face = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up'); continue; }
      if (!o.tgt) { if ((o.wt -= dt) > 0) continue; const R = o.wander * m.T, a = Math.random() * TAU, r = R * (.35 + .65 * Math.random()), tx = o.hx + Math.cos(a) * r, ty = o.hy + Math.sin(a) * r * .7;
        npcSelf = o; const ok = !blocked(tx, ty + 6, 4); npcSelf = null; if (ok) { o.tgt = [tx, ty]; o.at = 0; } else o.wt = .5; continue; }
      const dx = o.tgt[0] - o.x, dy = o.tgt[1] - o.y, L = Math.hypot(dx, dy), v = 18 * dt;
      if (L < v) { o.tgt = null; o.wt = 2 + Math.random() * 3; o.at = 0; if (o.face0) o.face = o.face0; continue; } // back at rest: turn to the spot's own facing (롬 = forge)
      o.face = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up');
      npcSelf = o; const nx = o.x + dx / L * v, ny = o.y + dy / L * v; if (!blocked(nx, ny + 6, 4) && Math.hypot(hero.x - nx, hero.y - ny) > 10) { o.x = nx; o.y = ny; } else { o.tgt = null; o.wt = 1; } npcSelf = null; } }
  function npcCell(o) { const A = npcAnim(o.anim); if (!A) return null; const J = A.J, seq = J.anims[(o.tgt ? 'walk_' : 'idle_') + (o.face || 'down')] || J.anims.idle_down; let t = Math.floor((o.at || 0) * 60) % seq.reduce((a, s) => a + s[2], 0);
    for (const s of seq) { if (t < s[2]) return [A.ims[s[0]], J.cells[s[0]][s[1]]]; t -= s[2]; } return null; }
  // ---- hd map layer (see loadHD) ----
  // on-screen test for the hd layer (screen px): only what is in the view is drawn (owner 10-23 「최적화」: big grounds / many props cost every frame)
  const onView = (x, y, w, h) => { const v = S.view, m = 2 * v.k; return x + w > v.ox - m && y + h > v.oy - m && x < v.ox + (EW + 2) * v.k + m && y < v.oy + (EH + 2) * v.k + m; };
  function drawHDGround(k) { const m = M(); if (!m || !m.hds) return; ctx.imageSmoothingEnabled = false; const v = S.view;
    for (const h of m.hds) { const im = hdBake(h, m.T); if (!im) continue; const [sx, sy] = W2S(h.gx * m.T, h.gy * m.T), sc = k / h.D;
      const x0 = Math.max(0, Math.floor((v.ox - k - sx) / sc)), y0 = Math.max(0, Math.floor((v.oy - k - sy) / sc)), x1 = Math.min(im.width, Math.ceil((v.ox + (EW + 2) * k - sx) / sc)), y1 = Math.min(im.height, Math.ceil((v.oy + (EH + 2) * k - sy) / sc));
      if (x1 > x0 && y1 > y0) ctx.drawImage(im, x0, y0, x1 - x0, y1 - y0, Math.round(sx + x0 * sc), Math.round(sy + y0 * sc), Math.round((x1 - x0) * sc), Math.round((y1 - y0) * sc)); // the visible part only
      for (const q of h.props || []) { if (!q.under) continue; const pi = HDIMG[q.img]; if (!pi) continue; const Dq = q.D || h.D, s2 = k / Dq, [px, py] = W2S((h.gx + q.x) * m.T, (h.gy + q.y) * m.T); // under: walked on (bridge planks)
        ctx.drawImage(pi, Math.round(px - (q.ax ?? pi.width / 2) * s2), Math.round(py - (q.ay ?? pi.height) * s2), Math.round(pi.width * s2), Math.round(pi.height * s2)); } } }
  function drawPropsHi(k, front) { const m = M(); if (!m || !m.hds) return; const T = m.T;
    for (const h of m.hds) for (const q of h.props || []) { hdBake(h, T); const im = q._lit || HDIMG[q.img]; if (!im || q.under) continue;
      const fx = (h.gx + q.x) * T, fy = (h.gy + q.y) * T; if ((fy > hero.y) !== !!front) continue;
      const Dq = q.D || h.D, sc = k / Dq, ax = q.ax ?? im.width / 2, ay = q.ay ?? im.height, wl = fx - ax / Dq, wr = wl + im.width / Dq, wt = fy - ay / Dq; // a prop may carry its own D (e.g. a D=3 part on a D=1.25 board)
      const behind = q.fade && hero.y < fy && hero.y > wt + 6 && hero.x > wl + 4 && hero.x < wr - 4; q._a = (q._a ?? 1) + ((behind ? .42 : 1) - (q._a ?? 1)) * .2; // see-through when the hero walks behind
      const [sx, sy] = W2S(fx, fy); if (!onView(sx - ax * sc, sy - ay * sc, im.width * sc, im.height * sc + 4 * k)) continue;
      if (q.shadow) { ctx.fillStyle = 'rgba(18,12,20,.32)'; ctx.beginPath(); ctx.ellipse(sx + 3 * k, sy - 1 * k, im.width * sc * .42, Math.max(3 * k, im.width * sc * .06), 0, 0, TAU); ctx.fill(); }
      hdBlit(im, sx, sy, ax * sc, ay * sc, sc, q.flip, q._a); }
    const cx0 = S.cam[0] - 60, cx1 = S.cam[0] + EW + 60, cy1 = S.cam[1] + EH + 140;
    for (const d of m.decos) { const e = d.hd; if (!e || d.broken || (d.y > hero.y) !== !!front || d.x < cx0 || d.x > cx1 || d.y < S.cam[1] - 10 || d.y > cy1) continue; const im = HDIMG[e.v.img]; if (!im) continue;
      const sc = k / e.D, fx = d.x + e.dx, fy = d.y + e.dy, wl = fx - e.v.ax / e.D, wt = fy - e.v.ay / e.D, wr = wl + im.width / e.D;
      const behind = im.height / e.D > 28 && hero.y < fy && hero.y > wt + 6 && hero.x > wl + 4 && hero.x < wr - 4; d._a = (d._a ?? 1) + ((behind ? .5 : 1) - (d._a ?? 1)) * .2;
      const [sx, sy] = W2S(fx, fy); ctx.fillStyle = 'rgba(14,10,18,.3)'; ctx.beginPath(); ctx.ellipse(sx + 2 * k, sy - k, im.width * sc * .34, Math.max(2 * k, im.width * sc * .07), 0, 0, TAU); ctx.fill();
      hdBlit(im, sx, sy, e.v.ax * sc, e.v.ay * sc, sc, e.flip, d._a); } }
  function hdBlit(im, sx, sy, ax, ay, sc, flip, a) { // one picture at its foot point, no save/restore (owner 10-23 「최적화」: save/restore per prop was ~20 % of a frame)
    ctx.imageSmoothingEnabled = false; ctx.globalAlpha = a ?? 1; const X = Math.round(sx), Y = Math.round(sy), w = Math.round(im.width * sc), h = Math.round(im.height * sc);
    if (flip) { ctx.setTransform(-1, 0, 0, 1, X, Y); ctx.drawImage(im, -Math.round(ax), -Math.round(ay), w, h); ctx.setTransform(1, 0, 0, 1, 0, 0); } else ctx.drawImage(im, X - Math.round(ax), Y - Math.round(ay), w, h);
    ctx.globalAlpha = 1; }
  // light pools are static: baked ONCE per map into the ground picture and into each prop's picture (lit copy) — no per-frame additive pass
  // (owner 10-23 「최적화」: the additive light pass was the costliest part of a town frame; characters keep the dusk grade only)
  function hdBake(h, T) { if (h._g !== undefined) return h._g; const im = HDIMG[h.ground]; if (!im) return null; if (!(h.lights && h.lights.length)) return (h._g = im);
    const lm = document.createElement('canvas'); lm.width = Math.ceil(im.width / h.D / 2); lm.height = Math.ceil(im.height / h.D / 2); const g = lm.getContext('2d'); g.globalCompositeOperation = 'lighter';
    for (const [lx, ly, r, col, a] of h.lights) g.drawImage(lightSprite(col, a, Math.round(r / 2)), lx * T / 2 - r / 2, ly * T / 2 - r / 2 * .72, r, r * .72); // half world px: soft anyway
    const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const cg = c.getContext('2d'); cg.drawImage(im, 0, 0); cg.globalCompositeOperation = 'lighter'; cg.imageSmoothingEnabled = true; cg.drawImage(lm, 0, 0, lm.width * 2 * h.D, lm.height * 2 * h.D);
    for (const q of h.props || []) { const pi = HDIMG[q.img]; if (!pi || q.under) continue; const Dq = q.D || h.D, ax = q.ax ?? pi.width / 2, ay = q.ay ?? pi.height, wl = q.x * T - ax / Dq, wt = q.y * T - ay / Dq; // the light that falls on this prop
      const t = document.createElement('canvas'); t.width = pi.width; t.height = pi.height; const tg = t.getContext('2d'); tg.imageSmoothingEnabled = true; tg.drawImage(lm, wl / 2, wt / 2, pi.width / Dq / 2, pi.height / Dq / 2, 0, 0, pi.width, pi.height);
      tg.globalCompositeOperation = 'destination-in'; tg.drawImage(pi, 0, 0); const o = document.createElement('canvas'); o.width = pi.width; o.height = pi.height; const og = o.getContext('2d'); og.drawImage(pi, 0, 0); og.globalCompositeOperation = 'lighter'; og.drawImage(t, 0, 0);
      q._lit = o; }
    return (h._g = c); }
  const LIGHTC = {}; function lightSprite(col, a, R) { // a light pool drawn once per colour / strength / size, then blitted (was a new radial gradient per light per frame)
    const key = col + a + '|' + R; let c = LIGHTC[key]; if (c) return c; c = LIGHTC[key] = document.createElement('canvas'); c.width = c.height = R * 2; const g = c.getContext('2d'), gr = g.createRadialGradient(R, R, 0, R, R, R);
    const h = col.replace('#', ''), rr = parseInt(h.slice(0, 2), 16), gg = parseInt(h.slice(2, 4), 16), bb = parseInt(h.slice(4, 6), 16);
    gr.addColorStop(0, `rgba(${rr},${gg},${bb},${.32 * a})`); gr.addColorStop(.5, `rgba(${rr},${gg},${bb},${.12 * a})`); gr.addColorStop(1, `rgba(${rr},${gg},${bb},0)`); g.fillStyle = gr; g.fillRect(0, 0, R * 2, R * 2); return c; }
  function drawHDLight(k) { const m = M(); if (!m || !m.hds) return; const v = S.view, T = m.T;
    for (const h of m.hds) { const [ox, oy] = W2S(h.gx * T, h.gy * T), im = HDIMG[h.ground], gw = im ? im.width / h.D * k : 0, gh = im ? im.height / h.D * k : 0;
      if (h.grade === 'dusk') { const ax = Math.max(ox, v.ox), ay = Math.max(oy, v.oy), bx = Math.min(ox + gw, v.ox + (EW + 1) * v.k), by = Math.min(oy + gh, v.oy + (EH + 1) * v.k);
        if (bx > ax && by > ay) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = 'rgb(206,196,222)'; ctx.fillRect(ax, ay, bx - ax, by - ay); ctx.restore(); } } // dusk: one grade over ground, props and characters alike
      if (h.webs) { ctx.save(); ctx.lineCap = 'round'; for (const [x1, y1, x2, y2, sag, al] of h.webs) { // 거미줄 실 (breadcrumbs toward the Arachne gate), swaying a little
        const [ax, ay] = W2S((h.gx + x1) * T, (h.gy + y1) * T), [bx, by] = W2S((h.gx + x2) * T, (h.gy + y2) * T), sw = Math.sin(S.t * 1.3 + x1) * .6 * k;
        ctx.strokeStyle = `rgba(226,224,236,${al ?? .55})`; ctx.lineWidth = Math.max(1, k / 3); ctx.beginPath(); ctx.moveTo(ax, ay); ctx.quadraticCurveTo((ax + bx) / 2 + sw, (ay + by) / 2 + (sag || 1) * T * k / 2, bx, by); ctx.stroke(); }
        ctx.restore(); }
      if (h.water) { ctx.save(); ctx.fillStyle = 'rgba(170,184,196,.22)'; const v = S.view, ph = S.t * 5; // 잔물결 (code): short pale dashes drifting along each water run [y, x0, x1]
        for (const [y, x0, x1] of h.water) { const [, sy] = W2S(0, (h.gy + y) * T); if (sy < v.oy - T * k || sy > v.oy + (EH + 2) * k) continue;
          for (let x = x0; x <= x1; x++) for (let j = 0; j < 2; j++) { const hsh = Math.sin((x * 12.9 + y * 78.2 + j * 37.7)) * 43758.5, f = hsh - Math.floor(hsh), u = (f * T + ph * (1 + f)) % T, a = Math.sin(S.t * 1.7 + f * 6.3);
            if (a < .2) continue; const [sx, sy2] = W2S((h.gx + x) * T + u, (h.gy + y) * T + 3 + j * 8 + f * 3); ctx.fillRect(Math.round(sx), Math.round(sy2), Math.round((2 + 3 * a) * k), Math.max(1, Math.round(k * .5))); } }
        ctx.restore(); }
      if (h.phase2) { const b = S.bossRef, on = S.roomP2 !== undefined ? +S.roomP2 : b && !b.dead && b.phase === 2 ? 1 : 0; h._p2 = (h._p2 || 0) + (on - (h._p2 || 0)) * (S.roomP2Rate || .025); const p = h._p2; // turns with the boss' roar ('boss-phase' event), unravels on 'boss-dead' // 보스 2페이즈: the room turns (red threads close in, light goes red, cocoons sway overhead)
        if (p > .01) { const P = h.phase2; ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = `rgba(${Math.round(255 - 30 * p)},${Math.round(255 - 40 * p)},${Math.round(255 - 36 * p)},1)`; ctx.fillRect(v.ox, v.oy, (EW + 1) * v.k, (EH + 1) * v.k); ctx.restore(); // floor keeps ~85 % of its stone colour: the red telegraphs must stay the brightest red (team lead)
          ctx.save(); ctx.globalCompositeOperation = 'lighter'; const seen = new Set(); for (const [x1, y1, x2, y2] of P.threads || []) for (const [x, y] of [[x1, y1], [x2, y2]]) { const key = x + ',' + y; if (seen.has(key)) continue; seen.add(key); // red only where the threads are tied (pillars, walls)
            const [sx, sy] = W2S((h.gx + x) * T, (h.gy + y) * T), R = 22 * k, gr = ctx.createRadialGradient(sx, sy, 0, sx, sy, R); gr.addColorStop(0, `rgba(170,20,35,${.28 * p})`); gr.addColorStop(1, 'rgba(170,20,35,0)'); ctx.fillStyle = gr; ctx.fillRect(sx - R, sy - R, R * 2, R * 2); }
          ctx.restore();
          ctx.save(); ctx.lineCap = 'round'; for (const [x1, y1, x2, y2, sag] of P.threads || []) { const [ax, ay] = W2S((h.gx + x1) * T, (h.gy + y1) * T), [bx, by] = W2S((h.gx + x2) * T, (h.gy + y2) * T), sw = Math.sin(S.t * 2 + x1) * k;
            ctx.strokeStyle = `rgba(190,40,55,${.55 * p})`; ctx.lineWidth = Math.max(1, k * .5); ctx.beginPath(); ctx.moveTo(ax, ay); ctx.quadraticCurveTo((ax + bx) / 2 + sw, (ay + by) / 2 + (sag || 1) * T * k / 2, bx, by); ctx.stroke(); }
          for (const [ci, [x, y]] of (P.cocoons || []).entries()) { if ((S.cocoonGone || []).includes(ci)) continue; const [sx, sy] = W2S((h.gx + x) * T, (h.gy + y) * T), sw = Math.sin(S.t * 1.7 + x * 3) * 2 * k, top = sy - 60 * k * p; // hanging cocoons drop into view
            ctx.strokeStyle = `rgba(230,220,230,${.6 * p})`; ctx.lineWidth = Math.max(1, k / 3); ctx.beginPath(); ctx.moveTo(sx, v.oy); ctx.lineTo(sx + sw, top); ctx.stroke();
            ctx.fillStyle = `rgba(214,200,190,${p})`; ctx.beginPath(); ctx.ellipse(sx + sw, top + 9 * k, 5 * k, 10 * k, 0, 0, TAU); ctx.fill(); ctx.fillStyle = `rgba(150,30,45,${.5 * p})`; ctx.fillRect(sx + sw - k, top + 4 * k, 2 * k, 12 * k); }
          ctx.restore(); } }
      for (const [x0, y0, sz] of h.smoke || []) for (let i = 0; i < 9; i++) { // 연기 (code, not baked): puffs rise, drift with the wind, grow and fade
        const ph = (S.t * .16 + i / 9 + x0 * .37) % 1, wx = (h.gx + x0) * T + ph * 14 * sz + Math.sin(S.t * .9 + i * 2.1) * 2 * sz, wy = (h.gy + y0) * T - ph * 46 * sz, [sx, sy] = W2S(wx, wy);
        ctx.fillStyle = `rgba(${74 - ph * 20 | 0},${66 - ph * 18 | 0},${72 - ph * 16 | 0},${(.42 * Math.min(1, ph * 6) * (1 - ph)).toFixed(3)})`; ctx.beginPath(); ctx.arc(sx, sy, (2.5 + ph * 7) * sz * k, 0, TAU); ctx.fill(); }
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      ctx.restore(); } }
  function drawNpcHi(k, front) { const m = M(); if (!m || m.type === 'world') return;
    for (const o of m.objs) { if (o.type !== 'npc' || !o.anim || (o.y > hero.y) !== !!front) continue; const c = npcCell(o); if (!c) continue;
      const sc = k * H128FIG / 117, [sx, sy] = W2S(o.x, o.y + 7), [im, r] = c, v = S.view; ctx.save(); ctx.beginPath(); ctx.rect(v.ox, v.oy, EW * v.k, EH * v.k); ctx.clip(); ctx.imageSmoothingEnabled = sc < 1; ctx.drawImage(im, r[0], r[1], r[2], r[3], Math.round(sx - r[4] * sc), Math.round(sy - r[5] * sc), Math.round(r[2] * sc), Math.round(r[3] * sc)); ctx.restore(); } }
  function blocked(x, y, r) { return solidAt(x, y) || solidAt(x - r, y) || solidAt(x + r, y) || solidAt(x, y - r * .6) || solidAt(x, y + r * .4); }
  let hopNow = false; // true only while the airborne hero moves: hop cells are open for him alone
  function moveCol(e, dx, dy, r, fly) {
    const m = M(); let ok = true; hopNow = e === hero && !!(hero.jump && hero.jump.air);
    const b0 = fly ? (x, y) => x < 6 || y < 10 || x > m.pw - 6 || y > m.ph - 4 : (x, y) => blocked(x, y, r);
    const bl = e !== hero && m.compose ? (x, y) => b0(x, y) || !!(areaOf(m, x, y) || {}).town : b0; // mobs never enter a town part (마을 = 전투 없음)
    if (dx) { if (!bl(e.x + dx, e.y)) e.x += dx; else ok = false; }
    if (dy) { if (!bl(e.x, e.y + dy)) e.y += dy; else ok = false; }
    hopNow = false; return ok;
  }
  function msg(text, t = 2.2) { S.msg = { text, t }; }
  // ---- 보스전 연출 (2번방 10-24, 팀장 「재밌고 다크하고 웅장한 보스전」): 시네마 띠 + 등장 그림 · 2페이즈 글자 · 처치 슬로·번쩍 · 화면 번쩍
  const SPLASH = {}; function splashImg(src) { if (!src) return null; if (!SPLASH[src]) { const im = new Image(); im.src = V(src); SPLASH[src] = im; } const im = SPLASH[src]; return im.complete && im.naturalWidth ? im : null; }
  function flash(t, rgb, a) { S.flashT = t; S.flashMax = t; S.flashRGB = rgb || '255,255,255'; S.flashA = a ?? .8; }
  function josa(w, a, b) { const c = (w || '').charCodeAt(w.length - 1) - 0xac00; return c >= 0 && c <= 11171 && c % 28 ? a : b; } // 을/를
  function bossCineIntro(B, b) { if (B.splash) splashImg(B.splash); S.cine = { kind: 'intro', t: 0, dur: B.splash ? 2.3 : .6, hold: true, img: B.splash, name: B.name || b.D.name, title: b.D.title || '', sub: B.sub || '' }; sfx('impact', .5, .6); }
  function bossCinePhase(b) { S.cine = { kind: 'phase', t: 0, dur: 2.0, text: b.D.phaseLine || '실이 끊어진다', sub: '— 2페이즈 —' }; flash(.18, '160,10,20', .45); shake(3); S.banner = null; }
  function bossCineKill(B, m) { S.killSlow = 1.3; S.cine = { kind: 'kill', t: 0, dur: 4.2, text: (m.D.title || B.name) + josa(m.D.title || B.name, '을', '를') + ' 쓰러뜨렸다', sub: m.D.title ? B.name : '' }; after(.35, () => flash(.35, '255,255,255', .9)); }
  function cineBars(ox, oy, SW, SH, u, k) { const bh = Math.round(SH * .11 * k); if (bh < 1) return; ctx.fillStyle = '#000'; ctx.fillRect(ox, oy, SW, bh); ctx.fillRect(ox, oy + SH - bh, SW, bh); ctx.fillStyle = 'rgba(140,20,30,.55)'; ctx.fillRect(ox, oy + bh - Math.max(1, u), SW, Math.max(1, u)); ctx.fillRect(ox, oy + SH - bh, SW, Math.max(1, u)); }
  function drawBossCine(ox, oy, SW, SH, u) { const C = S.cine, b = S.bossRef;
    const want = C ? 1 : (S.introT > 0 || (S.dialog && b && !b.dead && b.st === 'intro')) ? 1 : 0; S.barK = (S.barK || 0) + (want - (S.barK || 0)) * .18; cineBars(ox, oy, SW, SH, u, S.barK);
    if (C && C.kind === 'intro' && C.img) { const im = splashImg(C.img), t = C.t, a = Math.min(1, Math.max(0, (t - .25) / .3)) * (t > 2.0 ? Math.max(0, 1 - (t - 2.0) / .3) : 1);
      if (im && a > 0) { const sc = 1 + .04 * Math.min(1, t / 2.0), w = SW * sc, h = SH * sc; ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = '#000'; ctx.fillRect(ox, oy, SW, SH); ctx.beginPath(); ctx.rect(ox, oy, SW, SH); ctx.clip(); ctx.imageSmoothingEnabled = false;
        ctx.drawImage(im, ox + (SW - w) / 2, oy + (SH - h) / 2, w, h); const pa = Math.min(1, Math.max(0, (t - .6) / .35)); ctx.globalAlpha = a * pa; const px = ox + SW * .04, py = oy + SH * .78;
        textOut('「' + C.title + '」', px, py - 18 * u, 11 * u, '#c9b8a8', '#000', 'left'); textOut(C.name, px, py + 6 * u, 26 * u, '#f1e6d6', '#3a0008', 'left'); ctx.fillStyle = '#8a1020'; ctx.fillRect(px, py + 12 * u, 150 * u * pa, 2 * u);
        if (C.sub) textOut(C.sub, px, py + 26 * u, 10 * u, '#a08f80', '#000', 'left'); ctx.restore(); }
      if (t > 1.95 && t < 2.15) { ctx.fillStyle = `rgba(255,255,255,${(1 - Math.abs(t - 2.03) / .12) * .85})`; ctx.fillRect(ox, oy, SW, SH); } }
    if (C && (C.kind === 'phase' || C.kind === 'kill')) { const t = C.t, a = Math.min(1, t / .25, (C.dur - t) / .4), cy = oy + SH * (C.kind === 'kill' ? .45 : .3);
      if (C.kind === 'phase') { ctx.fillStyle = `rgba(90,0,10,${.18 * (1 + Math.sin(t * 9)) * a})`; ctx.fillRect(ox, oy, SW, SH); }
      if (C.kind === 'kill' && t > .45) { const k2 = Math.min(1, (t - .45) / .5) * a; ctx.globalAlpha = k2; ctx.fillStyle = 'rgba(0,0,0,.45)'; ctx.fillRect(ox, cy - 26 * u, SW, 44 * u); ctx.fillStyle = '#7a1020'; ctx.fillRect(ox + SW * .2, cy - 26 * u, SW * .6, Math.max(1, u)); ctx.fillRect(ox + SW * .2, cy + 18 * u, SW * .6, Math.max(1, u));
        textOut(C.text, ox + SW / 2, cy + 4 * u, 19 * u, '#f3e9d8', '#2a0006'); if (C.sub) textOut(C.sub, ox + SW / 2, cy - 12 * u, 10 * u, '#b8a898', '#000'); ctx.globalAlpha = 1; }
      if (C.kind === 'phase') { const sp = 1 + Math.max(0, .25 - t) * 2; ctx.globalAlpha = a; textOut(C.text, ox + SW / 2, cy, 20 * u * sp, '#ff5a4a', '#1a0004'); textOut(C.sub, ox + SW / 2, cy + 16 * u, 10 * u, '#e8b0a0', '#000'); ctx.globalAlpha = 1; } }
    if (S.flashT > 0) { ctx.fillStyle = `rgba(${S.flashRGB},${S.flashA * S.flashT / S.flashMax})`; ctx.fillRect(ox, oy, SW, SH); } }
  function drawBossBar(b, cxs, oy, SH, u) { // 웅장한 보스 체력바: 이름·칭호, 2페이즈 눈금(50%), 깎인 자리 하얀 잔상(hpLag), 2페이즈는 붉게 맥박
    const w = Math.round(300 * u), h = Math.round(8 * u), x = Math.round(cxs - w / 2), y = Math.round(oy + SH - 22 * u), fr = Math.max(0, b.hp / b.maxHp), lg = Math.max(fr, (b.hpLag ?? b.hp) / b.maxHp), P2 = b.phase === 2, pul = P2 ? .5 + .5 * Math.sin(S.t * 6) : 0;
    ctx.fillStyle = 'rgba(4,2,8,.9)'; ctx.fillRect(x - 3 * u, y - 3 * u, w + 6 * u, h + 6 * u); ctx.strokeStyle = P2 ? `rgb(${120 + 60 * pul},30,36)` : '#6a5640'; ctx.lineWidth = Math.max(1, u); ctx.strokeRect(x - 2.5 * u, y - 2.5 * u, w + 5 * u, h + 5 * u);
    for (const ex of [x - 6 * u, x + w + 6 * u]) { ctx.fillStyle = P2 ? '#8a1020' : '#7a6448'; ctx.beginPath(); ctx.moveTo(ex, y + h / 2 - 5 * u); ctx.lineTo(ex + 4 * u, y + h / 2); ctx.lineTo(ex, y + h / 2 + 5 * u); ctx.lineTo(ex - 4 * u, y + h / 2); ctx.fill(); }
    ctx.fillStyle = '#16080c'; ctx.fillRect(x, y, w, h);
    if (lg > fr) { ctx.fillStyle = 'rgba(255,248,236,.85)'; ctx.fillRect(x + w * fr, y, w * (lg - fr), h); }
    const g = ctx.createLinearGradient(0, y, 0, y + h); if (P2) { g.addColorStop(0, `rgb(${200 + 40 * pul},40,46)`); g.addColorStop(1, '#5a0a12'); } else { g.addColorStop(0, '#d9cfbd'); g.addColorStop(1, '#7d6f5e'); }
    ctx.fillStyle = b.hitT > .15 ? '#fff' : g; ctx.fillRect(x, y, w * fr, h);
    ctx.fillStyle = 'rgba(0,0,0,.6)'; ctx.fillRect(x + w / 2 - Math.max(1, u), y - 2 * u, 2 * Math.max(1, u), h + 4 * u); ctx.fillStyle = P2 ? '#ff6a5a' : '#b8a488'; ctx.fillRect(x + w / 2 - .5 * u, y - 3 * u, Math.max(1, u), 2 * u); // 2페이즈 눈금
    textOut(b.D.name, x, y - 7 * u, 14 * u, P2 ? '#ffb0a0' : '#efe4d2', '#000', 'left'); if (b.D.title) { ctx.font = font(14 * u); textOut('「' + b.D.title + '」', x + ctx.measureText(b.D.name).width + 6 * u, y - 7 * u, 10 * u, '#9a8a7a', '#000', 'left'); }
    if (P2) textOut('2페이즈', x + w, y - 7 * u, 10 * u, '#ff7a6a', '#000', 'right'); }
  function banner(text, t = 1.6, small) { S.banner = { text, t, max: t, small }; }
  function after(t, f) { S.timers.push({ t, f }); }
  function shake(v) { const g = window.__game; if (g && g.shakeScale) v = g.shakeScale(v); S.shake = Math.max(S.shake, v); } // [hitfeel] capped ≤3px + '화면 흔들림' option (game.template.html)
  function addFx(type, x, y, o = {}) { S.fx.push(Object.assign({ type, x, y, t: 0, life: o.life || 0.5 }, o)); }
  const NAMES = { potion: '물약', antidote: '해독초', heart_piece: '하트 조각', spirit_drop: '정령의 이슬', m_hardwood: '단단한 목재', m_a1_shared: '숲의 정수', bomb: '폭탄', m_spore: '독 포자',
    m_rabbit_horn: '토끼 뿔', m_wasp_sting: '말벌 독침', m_boar_hide: '멧돼지 가죽', m_pumpkin_vine: '호박 덩굴', m_forest_gel: '숲 젤리', m_acorn_shell: '도토리 껍질', m_sprout_wood: '새싹 목재' };
  const itemName = id => NAMES[id] || id;
  function giveLoot(list) { const g = window.__game; const names = [];
    for (const [id, n] of list) { if (id === 'gold') { if (g && g.addGold && g.addGold(n)) { names.push('금화 ' + n); feedAdd('금화', n, '#ffd84a'); } continue; } feedAdd(itemName(id), n, id === 'potion' ? '#ff7a7a' : '#cfe8ff'); try { if (id === 'potion' && g) g.potions = (g.potions || 0) + n; else if (g && g.invAdd) g.invAdd(id, n); } catch (e) {}
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
  function lastStandOn() { return !!(S.lastStand && S.lastStand.t > 0); }
  function checkLastStand() { const L = S.lastStand || (S.lastStand = { t: 0, cd: 0 }); if (!(SAVE.flags[LAST_STAND.flag] || Q.has('abyss')) || S.abyssSpent || L.t > 0 || L.cd > 0 || hero.hp <= 0 || hero.hp > hero.maxHp * LAST_STAND.hpPct) return;
    L.t = LAST_STAND.dur; banner('가슴의 문양이 깨어난다 — 심연의 힘', 2.2); shake(3); addFx('text', hero.x, hero.y - 34, { text: '심연의 힘', life: 1, color: '#c9a0ff' }); }
  function stepLastStand(dt) { const L = S.lastStand; if (!L) return; if (L.t > 0) { L.t -= dt; if (L.t <= 0) L.cd = LAST_STAND.cd; } else if (L.cd > 0) L.cd -= dt; }
  function hurt(dmg, src, raw) {
    if (S.scene === 'world' || hero.hp <= 0 || S.deadT > 0) return false;
    if (W_API.god || S.ultFx) return false; // invulnerable during the 필살기
    if (hero.roll && hero.roll.t < iframe()) { const just = !hero.roll.just && hero.roll.t < (DIFF().perfect_ticks || 7) / 60; // 저스트 회피 = 회피대시 시작 perfect_ticks 안 (보통 7틱) -> 필살기 게이지 크게
      if (just) { const ow = src && (src.owner || (src.D ? src : null)); if (ow && ow.D && ow.D.felt) { ow.dazeT = .6; addFx('text', ow.x, ow.y - (ow.D.h || 20) - 8, { text: '?', life: .6, color: '#cfe6ff' }); } // the attacker is caught off guard
        hero.roll.just = true; S.slowmo = .3; flash(.14, '170,230,255', .28); addFx('justring', hero.x, hero.y - 12, { life: .4 }); ultAdd('gainPerfect', 1); if (lastStandOn() && !S.abyssSpent) { S.slowmo = 0; castAbyss(); return false; } addFx('text', hero.x, hero.y - 30, { text: '저스트 회피!', life: .7, color: '#ffe08a' }); } else if (hero.dodgeT <= 0) addFx('text', hero.x, hero.y - 30, { text: '회피!', life: .6, color: '#9ff' }); if (just) sfx('dodge', .6); hero.dodgeT = .3; return false; }
    if (hero.inv > 0) return false;
    if (!raw) dmg = Math.max(1, Math.round(dmg * DIFF().enemy_dmg)); hero.hp = Math.max(0, hero.hp - dmg); sfx('hurt', .9); hero.inv = 1.0; hero.charge = null; hero.holdOk = false; shake(3); S.freezeT = .07; ultAdd('gainHit', 1);
    if (src && src.x !== undefined) { const a = Math.atan2(hero.y - src.y, hero.x - src.x); if (!hero.atk) setFace(-Math.cos(a), -Math.sin(a)); hero.kb = { x: Math.cos(a) * 3.3, y: Math.sin(a) * 3.3, n: 0 }; } // turn to the attacker (the recoil pose leans away from it) and slide ~8px over 7 ticks instead of a 1-tick teleport (motion lab 10-23)
    addFx('text', hero.x, hero.y - 30, { text: '-' + dmg, life: .7, color: '#ff6a5a' });
    syncTownHp(); checkLastStand();
    if (hero.hp <= 0) die();
    return true;
  }
  function ultAdd(k, n) { const g = window.__game; if (g && g.addUlt && g.ULT_CFG) g.addUlt(g.ULT_CFG[k] * n); } // 필살기 게이지: 싸우는 동안 저절로 · 피격 1번마다 · 저스트 회피 (template ULT_CFG)
  function touch(m, r, dmg) { if (Math.hypot(hero.x - m.x, hero.y - m.y) < r + 5) hurt(dmg, m); }
  function shot(s) { sfx('shot', .45); if (s.owner && s.owner.D && s.owner.D.felt) addFx('muzzle', s.x, s.y, { life: .15, a: s.a }); s.t = 0; s.vx = Math.cos(s.a) * s.sp; s.vy = Math.sin(s.a) * s.sp; s.life = s.life || 2; S.shots.push(s); }
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
    const D = m.D; dmg *= D.dmgMul ? D.dmgMul(m) : 1; if (lastStandOn()) dmg *= LAST_STAND.atk;
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
    { const uf = S.ultFx; if (uf && uf.U.whole && uf.fx && uf.fx !== 'pillar' && fxQ() >= 3) addFx('voidpop', m.x, m.y - 6, { life: .45, big: D.boss || D.champion }); else addFx('poof', m.x, m.y - 8, { life: .5, big: D.boss || D.champion }); } // 심연: pixel void burst instead of the white puff sfx('mob_die', .8);
    if (D.onDeath) D.onDeath(m, W);
    if (!m.noDrop && !m.summoned && window.__game && window.__game.addGold) { const gv = window.__game.addGold(window.__game.goldFor(D.boss ? 'boss' : D.champion ? 'champion' : 'mob', D.area || 1)); if (gv) { sfx('coin', .6); } if (gv) addFx('text', m.x + 8, m.y - (D.h || 20) - 12, { text: '+' + gv + 'G', life: .9, color: '#ffd84a' }); } // gold curve: data/economy.json
    if (!m.noDrop && D.mat && (D.champion || D.boss || Math.random() < .45)) { const n = D.matN || 1; giveLoot([[D.mat, n]]); } // shown in the pickup feed (right), not as text over the fight
    if (!D.boss && !D.champion && !m.noDrop && Math.random() < POT.heartDrop) S.fx.push({ type: 'heart', x: m.x, y: m.y, t: 0, life: 8 });
    if (m.flag) { SAVE.flags[m.flag] = true; save(); }
    if (m.loot && !m.noDrop) { const got = giveLoot(m.loot); if (got) banner('얻었다: ' + got, 2); }
    if (D.champion) { banner('챔피언 격파 — ' + D.name + '!', 2.2); jingle(); const L = (M().links || {}).boss_door || {}, left = (L.needFlags || ['champ_boar', 'champ_wasp']).filter(f => !SAVE.flags[f]).length;
      after(2.3, () => msg(left ? '남은 챔피언: ' + left + ' — 모두 쓰러뜨리면 ' + (L.openText || '골렘의 방이 열린다') : (L.doneText || '숲의 두 우두머리를 쓰러뜨렸다! 신전 B2의 봉인된 문이 열린다.'), 3.5)); } // per-dungeon text (links.boss_door)
    if (D.boss) bossDefeated(m);
    if (m.spawnRef && m.spawnRef.respawn > 0) m.spawnRef.timer = m.spawnRef.respawn;
    if (S.engaged === m) S.engaged = null;
  }
  function bossDefeated(m) {
    const B = M().boss; SAVE.flags[B.flag] = true; save(); playScene('boss_post:' + (B.id || B.kind), 3.4); bossCineKill(B, m);
    S.hazards.length = 0; S.shots.length = 0; S.temp.length = 0; S.ult = null;
    S.mobs.forEach(o => { if (o !== m && !o.dead) killMob(o); });
    shake(4); jingle();
    after(1.6, () => { const l = giveLoot(B.reward || []); msg((B.absorb ? '능력 흡수: ' + B.absorb + (l ? '  ·  ' : '') : '') + (l ? '획득: ' + l : ''), 5); });
    after(3.2, () => { addWarp(M()); msg(B.exitMsg || (B.exit && B.exit.to === 'felt' ? '빛의 문이 열렸다 — 들어가면 펠트로 돌아간다' : '빛의 문이 열렸다 — 들어가면 신전 입구로 돌아간다'), 4); });
  }
  function addWarp(m) { if (!m.objs.some(o => o.type === 'warp')) m.objs.push({ type: 'warp', x: m.pw / 2, y: m.ph / 2 + 16, tx: -1, ty: -1, to: m.boss.exit.to, spawn: m.boss.exit.spawn }); }
  function phase2(m) { banner('2페이즈 — 골렘이 수정 갑옷을 일으킨다!', 2); shake(5); for (let i = 0; i < 14; i++) addFx('crystal', m.x + Math.cos(i / 14 * TAU) * 30, m.y + Math.sin(i / 14 * TAU) * 22, { life: .8 }); }
  function ult(m, warn) { banner('필살 — 대지 붕괴!  기둥 뒤로 숨거나, 폭발 순간 회피대시', 2.6); S.ult = hazard({ shape: 'all', x: m.x, y: m.y, owner: m, warn, act: 0.05, dmg: Math.ceil(hero.maxHp * Math.min(0.52 * DIFF().enemy_dmg, DIFF().ult_cap || 0.9)), raw: true, kind: 'ult' }); m.ultW = S.ult.warn; } // 52% of max HP (normal), capped so a full-HP hero survives one
  function jingle() { try { if (window.BGM && BGM.jingle) { BGM.jingle('jingle_victory'); S.jingleT = 3.5; } } catch (e) {} }

  // the API handed to mob behaviours (world_mobs.js)
  const W = { get hero() { return hero; }, get map() { return M(); }, hazard, shot, hurt, touch, moveCol, token, get mobs() { return S.mobs; }, get diff() { return DIFF(); }, blockedAt: (x, y) => blocked(x, y, 4), dist, spawn, count, engage,
    fx: addFx, sfx, shake, banner, after, tempSolid, randomFloor, breakDecoNear, phase2, ult, say: msg };

  // ---------------- scene manager ----------------
  // 세미 오픈월드 (owner 10-23): field01 (시작의 숲) now lives inside field00 at x+56 (tools/stitch_region01.py); old links keep working
  const ALIAS = { field01: { to: 'field00', pre: 'f01_' }, dungeon01_b2: { to: 'dungeon01_b1', pre: 'b2_' }, felt: { to: 'ch1', pre: 'felt:' }, field_felt: { to: 'ch1', pre: 'field_felt:' } }; // 1장: 펠트 + 잿빛 들판 = maps/ch1.json (composeMap)
  // a point given in a part map's own tiles (quest targets, ?at=) -> the composite map
  function aliasPt(t) { const A = ALIAS[t.map]; if (!A) return t; const m = MAPS[A.to], a = m && m.areas && m.areas.find(q => q.part === t.map); if (a) { t.x += a.x; t.y += a.y; } t.map = A.to; return t; } // + 신전 B2 at x+46 (tools/stitch_temple01.py)
  function go(to, spawnName, opt = {}) {
    if (S.trans) return false;
    const AL = ALIAS[to]; S.aliasFrom = AL ? to : null; if (AL) { to = AL.to; spawnName = AL.pre + (spawnName || 'default'); }
    S.trans = { phase: 'out', t: 0, to, spawn: spawnName, card: opt.card, fromTown: S.scene === 'town' };
    if (S.trans.fromTown) { const g = window.__game; S.townPos = { x: g.hero.x, y: g.hero.y - 34 }; g.setManual(true); syncFromTown(); show(true); }
    return true;
  }
  function show(v) { cv.style.display = v ? 'block' : 'none'; document.body.classList.toggle('inworld', !!v); }
  function enterScene(to, spawnName) {
    S.roomP2 = undefined; S.cocoonGone = []; S.mobs = []; S.hazards = []; S.shots = []; S.fx = []; S.temp = []; S.timers = []; S.ult = null; S.engaged = null; S.dialog = null; S.bossRef = null; S.pause = false;
    if (to === 'town') { S.scene = 'town'; S.map = null; return Promise.resolve(); }
    return loadMap(to).then(m => {
      S.map = m; S.scene = m.type === 'world' ? 'world' : 'map'; S.bgm = m.bgm;
      if (!m.groundC) { m.groundC = m.compose ? composeGround(m) : m.grade ? scarGround(m, gradeCanvas(renderGround(m), m.grade)) : renderGround(m);
        for (const h of m.hds || []) { const im = HDIMG[h.ground]; if (im) m.groundC.getContext('2d').clearRect(h.gx * m.T, h.gy * m.T, im.width / h.D, im.height / h.D); } }
      let sp = m.spawns && m.spawns[spawnName];
      if (!sp && spawnName && spawnName.startsWith('ws:')) { const w = m.objs.find(o => o.type === 'waystone' && o.id === spawnName.slice(3)); if (w) sp = [w.tx + .5, w.ty + 1.6, 'down']; } // fast travel
      if (!sp && spawnName && spawnName.startsWith('snap:')) sp = spawnName.slice(5).split(',').map(Number).concat([hero.face]); // death retry: just before the fight
      if (!sp && spawnName === 'resume' && SAVE.resume && SAVE.resume.map === m.id) sp = [SAVE.resume.x, SAVE.resume.y, SAVE.resume.face || 'down'];
      if (!sp && m.type === 'world') { const n = (m.nodes || []).find(n => n.id === spawnName); if (n) sp = [n.x + .5, n.y + 2.2, 'down']; }
      sp = sp || (m.spawns && m.spawns.default) || [m.w / 2, m.h / 2];
      hero.x = sp[0] * m.T; hero.y = sp[1] * m.T; hero.face = sp[2] || 'down'; hero.safe = [hero.x, hero.y]; hero.atk = hero.roll = null; hero.inv = .5; hero.moving = false;
      S.nodeArmed = false; S.nearNode = null;
      for (const o of (m.objects || [])) {
        if (o.type === 'spawn') { o.timer = 0; const mm = spawn(o.mob, (o.x + .5) * m.T, (o.y + .5) * m.T); if (mm) { mm.spawnRef = o; o.mob = mm; } }
        if (o.type === 'champion' && !SAVE.flags[o.id]) spawn(o.mob, (o.x + .5) * m.T, (o.y + .5) * m.T, { flag: o.id, loot: o.loot }); // o.loot = the champion's drop (map data)
      }
      if (m.boss && !SAVE.flags[m.boss.flag]) { const b = spawn(m.boss.kind, m.boss.x * m.T, m.boss.y * m.T, { flag: m.boss.flag }); S.bossRef = b; S.engaged = b; if (m.boss.intro) S.introT = m.boss.intro; bossCineIntro(m.boss, b); playScene('boss_pre:' + (m.boss.id || m.boss.kind), (m.boss.intro || 0) + .6); }
      if (m.boss && SAVE.flags[m.boss.flag]) addWarp(m);
      for (const o of m.objs) { if ((o.type === 'door_locked' || o.type === 'gate') && SAVE.opened[o.key]) o.open = true; if (o.type === 'lever' && SAVE.levers[o.key]) o.on = true;
        if (o.type === 'door_locked' || o.type === 'gate' || o.type === 'boss_door') m.solidG[o.ty * m.w + o.tx] = o.open ? 0 : 1; }
      updateGate(m, true);
      S.lock = null; S.snap = null; S.calmT = 0; const ar0 = areaAt(m, hero.x, hero.y); S.area = ar0 ? ar0.id : null; S.areaCard = null; areaScene(ar0 ? ar0.id : m.id, 1.2);
      if (S.pendingMsg) { msg(S.pendingMsg, 2.2); S.pendingMsg = null; }
      if (S.pendingHp) { hero.hp = Math.max(1, Math.min(hero.maxHp, S.pendingHp)); S.pendingHp = 0; syncTownHp(); }
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
    syncTownHp(); g.setManual(false); S.scene = 'town'; S.bgm = null; held.clear(); if (SAVE.resume) { SAVE.resume = null; save(); }
  }
  function syncFromTown() { const g = window.__game; if (!g) return; hero.maxHp = g.hero.maxHp || 50; hero.hp = Math.max(1, g.hero.hp ?? hero.maxHp); }
  function syncTownHp() { const g = window.__game; if (g && g.hero) { g.hero.hp = hero.hp; g.hero.maxHp = hero.maxHp; } }
  function die() { S.deadT = 0.01; banner('쓰러졌다…', 2.2); }
  // ---------------- semi-open world (owner 10-23 「세미 오픈월드 이스8처럼 … 중간세이브」) ----------------
  // areas: named parts of one seamless map (name card, no fade; first visit = auto-save). save anywhere out of combat (F5),
  // waystones save + become the respawn point. death: J = retry from just before the fight / T = last waystone.
  // champion thorn ring: walking up to a champion raises a ring of thorns that holds the hero in until it falls.
  const LOCK_R = 150, LOCK_SQ = .75;  // ring radius (px, 16px tiles) and its 3/4-view squash
  function areaAt(m, x, y) { const tx = x / m.T, ty = y / m.T; return (m.areas || []).find(a => tx >= a.x && tx < a.x + a.w && ty >= a.y && ty < a.y + a.h) || null; }
  function inCombat() { return !!S.lock || !!(S.bossRef && !S.bossRef.dead) || S.mobs.some(mm => !mm.dead && !(mm.spawnT > 0) && Math.hypot(mm.x - hero.x, mm.y - hero.y) < 140); }
  function saveHere(kind) { const m = M(); if (!m || m.type === 'world' || S.deadT > 0) return false;
    if (kind === 'manual' && inCombat()) { msg('근처에 적이 있어 저장할 수 없다', 1.4); sfx('locked', .5); return false; }
    SAVE.resume = { map: m.id, x: +(hero.x / m.T).toFixed(2), y: +(hero.y / m.T).toFixed(2), face: hero.face, hp: hero.hp }; save();
    const g = window.__game; if (g && g.quickSave) try { g.quickSave(); } catch (e) {} // bag / gold / gear ride along with the town quick save
    S.saved = { t: 1.8, text: kind === 'auto' ? '자동 저장' : '저장 완료' }; if (kind === 'manual') msg('저장 완료 — 다음에 켜면 여기서 이어한다', 1.6); return true; }
  function retry(how) { const m = M(), sn = S.snap; abyssRest(); S.deadT = 0; S.lock = null; S.snap = null; hero.inv = 1;
    if (how === 'snap' && sn) { hero.hp = Math.max(sn.hp, Math.ceil(hero.maxHp / 2)); syncTownHp(); S.pendingMsg = '전투 직전으로 돌아왔다'; go(sn.map, 'snap:' + sn.x + ',' + sn.y, { card: false }); return; }
    hero.hp = hero.maxHp; syncTownHp(); const w = SAVE.lastWay; S.pendingMsg = w ? '마지막 비석에서 다시 시작' : null;
    if (w) go(w.map, 'ws:' + w.id, { card: false }); else respawnAfterDeath(); }
  function stepOpen(m, dt) {
    // champion ring: raise when the hero walks up to a living champion, release when it falls
    if (!S.lock) { const c = S.mobs.find(mm => !mm.dead && mm.D.champion && !(mm.spawnT > 0) && Math.hypot(mm.x - hero.x, mm.y - hero.y) < 90);
      if (c && hero.hp > 0) { S.snap = S.snap || { map: m.id, x: +((hero.px ?? hero.x) / m.T).toFixed(2), y: +((hero.py ?? hero.y) / m.T).toFixed(2), hp: hero.hp };
        S.lock = { x: (c.x + hero.x) / 2, y: (c.y + hero.y) / 2, mob: c, t: 0 }; engage(c); banner(c.D.name + ' — 가시덩굴이 퇴로를 막았다!', 2, true); shake(2); sfx('impact', .7); } }
    if (S.lock) { const L = S.lock; L.t += dt;
      if (L.mob.dead) { S.lock = null; msg('가시덩굴이 걷혔다', 1.6); after(1.4, () => { if (!inCombat()) saveHere('auto'); }); }
      else { const dx = hero.x - L.x, dy = (hero.y - L.y) / LOCK_SQ, d = Math.hypot(dx, dy); if (d > LOCK_R - 6) { const k = (LOCK_R - 6) / d; hero.x = L.x + dx * k; hero.y = L.y + dy * k * LOCK_SQ; } } }
    // fight snapshot for the retry: hero state at the moment a fight starts; dropped after 2.5s of calm
    const f = inCombat(); if (f && !S.snap && hero.hp > 0) S.snap = { map: m.id, x: +((hero.px ?? hero.x) / m.T).toFixed(2), y: +((hero.py ?? hero.y) / m.T).toFixed(2), hp: hero.hp };
    S.calmT = f ? 0 : (S.calmT || 0) + dt; if (S.calmT > 2.5) S.snap = null; if (!f) { hero.px = hero.x; hero.py = hero.y; }
    // seamless area change: name card only, first visit auto-saves
    const ar = areaAt(m, hero.x, hero.y); if (ar && ar.id !== S.area) { S.area = ar.id; S.areaCard = { a: ar, t: 2.4 }; sfx('page', .4);
      const k = 'area:' + ar.id; if (!SAVE.visited[k]) { SAVE.visited[k] = true; save(); if (!f) saveHere('auto'); } areaScene(ar.id, .9); }
    if (S.areaCard && (S.areaCard.t -= dt) <= 0) S.areaCard = null; if (S.saved && (S.saved.t -= dt) <= 0) S.saved = null; }
  function drawLock(g) { const L = S.lock; if (!L) return; const k = Math.min(1, L.t / .35), n = 56;
    for (let i = 0; i < n; i++) { const a = i / n * TAU, x = L.x + Math.cos(a) * LOCK_R, y = L.y + Math.sin(a) * LOCK_R * LOCK_SQ, h = (7 + (i % 3) * 3 + Math.sin(S.t * 4 + i) * 1) * k;
      g.fillStyle = i % 2 ? '#3c1a2a' : '#5a2236'; g.beginPath(); g.moveTo(x - 3, y + 1); g.lineTo(x + (i % 2 ? 1 : -1), y - h); g.lineTo(x + 3, y + 1); g.fill();
      if (i % 4 === 0) { g.fillStyle = '#2a1420'; g.fillRect(Math.round(x) - 4, Math.round(y), 8, 2); } } }
  function respawnAfterDeath() { abyssRest(); hero.hp = hero.maxHp; syncTownHp(); S.deadT = 0; const m = M(); go(m.type === 'boss' ? 'dungeon01_b2' : m.id, 'default', { card: false }); }

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
  // ---- 몹 시험장 (owner 10-23 "플레이 한번 해보게 / 주소 만들고"): ?go=field01&arena=c1_silmamul,c1_unrotting_hound*2[&tough=1][&ult=full]
  //   [&at=17,18 start tile] clears the map's own mobs, spawns the listed group around the hero and brings it back 1.5s after it is wiped. tough=1: the hero never dies. test128/lab.html = buttons.
  const AQ = new URLSearchParams(location.search), ARENA = (AQ.get('arena') || '').split(',').filter(Boolean).flatMap(t => { const [k, n] = t.split('*'); return Array(Math.max(1, Math.min(8, +n || 1))).fill(k); }), TOUGH = AQ.get('tough') === '1';
  function arenaTick(dt) { if (!ARENA.length || !S.map || S.map.type === 'world') return;
    if (S.arenaMap !== S.map) { S.arenaMap = S.map; S.arenaT = .8; const at = (AQ.get('at') || '').split(',').map(Number); if (S.aliasFrom && at.length === 2) { const q = aliasPt({ map: S.aliasFrom, x: at[0], y: at[1] }); at[0] = q.x; at[1] = q.y; } /* ?go=field_felt&at= is in the part map's tiles */ if (at.length === 2 && at.every(v => v >= 0)) { hero.x = (at[0] + .5) * S.map.T; hero.y = (at[1] + .5) * S.map.T; snapCam(); } /* at=tx,ty: start in an open spot */ for (const o of (S.map.objects || [])) if (o.type === 'spawn') o.respawn = 0; for (const m of S.mobs) if (!m.D.boss) m.dead = true; }
    if (TOUGH && hero.hp < 15) { hero.hp = hero.maxHp; addFx('text', hero.x, hero.y - 34, { text: '체력 회복 (시험장)', life: .8, color: '#9fffb0' }); }
    if (S.mobs.some(m => !m.dead && m.arena)) return;
    if ((S.arenaT -= dt) > 0) return; S.arenaT = 1.5;
    ARENA.forEach((k, i) => { let x = hero.x, y = hero.y; for (let t = 0; t < 12; t++) { const a = i * 2.4 + t * .7, r = 95 + t * 4; x = hero.x + Math.cos(a) * r; y = hero.y + Math.sin(a) * r * .8; if (!blocked(x, y, 6)) break; }
      const m = spawn(k, x, y); if (m) m.arena = true; }); }
  function step(dt) {
    S.t += dt; { const g = window.__game; if (g && g.potionCd > 0 && S.scene !== 'town') g.potionCd = Math.max(0, g.potionCd - dt); }
    if (S.trans) { stepTrans(dt); if (S.trans && S.trans.phase !== 'in') return; }
    if (hero.kb) { const K = hero.kb; moveCol(hero, K.x, K.y, 5); K.x *= .6; K.y *= .6; if (++K.n >= 7) hero.kb = null; } // hit knockback slide (see hurt)
    if (S.scene === 'town') return;
    arenaTick(dt);
    { const g = window.__game; if (g && g.ui) { queue.length = 0; return; } } // DOM UI (shop) open over a map: paused
    if (S.dialog) { stepDialog(dt); queue.length = 0; return; }
    if (NAV() && NAV().screenStep(dt)) { queue.length = 0; return; } // full map screen open (paused)
    if (takePress('menu')) { const g = window.__game; if (g && g.ctl && !S.pause) { g.ctl.openUI('menu'); queue.length = 0; return; } S.pause = !S.pause; } // Esc = the shared pause menu (설정 · 귀환 inside)
    if (S.pause) { if (queue.includes('KeyT')) { queue.length = 0; S.pause = false; if (Q.has('old')) go('town', null, { card: false }); else go('felt', 'default', { card: false }); } queue.length = 0; return; }
    if (S.ultFx) { const f = S.ultFx; if (f.t > f.fz + .15 && f.t < f.fz + f.ci && (takePress('attack') || takePress('interact'))) f.t = f.fz + f.ci; stepUlt(dt); queue.length = 0; updateCam(dt); return; } // skip the cut-in (retries) // 필살기: world frozen (timers, mobs, hazards, shots)
    if (S.cine) { S.cine.t += dt; if (S.cine.t >= S.cine.dur) S.cine = null; else if (S.cine.hold) { queue.length = 0; return; } } // 보스 연출 (2번방 10-24): intro = world waits
    if (S.flashT > 0) S.flashT -= dt; if (S.killSlow > 0) { S.killSlow -= dt; dt *= .25; } { const b = S.bossRef; if (b && !b.dead && b.phase === 2 && !b.cineP2) { b.cineP2 = true; bossCinePhase(b); } }
    if (S.freezeT > 0) { S.freezeT -= dt; updateCam(dt); return; } // hitstop when a mob lands a hit (owner 10-23 "생동감 있게 공격")
    if (S.slowmo > 0) { S.slowmo -= dt; dt *= .3; } // just-dodge: a short slow-motion beat (like the town's Flash Move)
    for (let i = S.timers.length - 1; i >= 0; i--) { const tm = S.timers[i]; tm.t -= dt; if (tm.t <= 0) { S.timers.splice(i, 1); tm.f(); } }
    if (S.msg && (S.msg.t -= dt) <= 0) S.msg = null;
    if (S.qs) { const Q = S.qs; Q.flash = Math.max(0, (Q.flash || 0) - dt * 2.5); Q.shake = Math.max(0, (Q.shake || 0) - dt * 4); Q.noteT = Math.max(0, (Q.noteT || 0) - dt); }
    if (S.feed) { for (const f of S.feed) f.t += dt; S.feed = S.feed.filter(f => f.t < f.life); }
    if (S.banner && (S.banner.t -= dt) <= 0) S.banner = null;
    if (S.jingleT > 0) S.jingleT -= dt;
    S.shake = Math.max(0, S.shake - dt * 14);
    if (S.deadT > 0) { S.deadT += dt; if (S.deadT > 1.4) { if (takePress('attack') || takePress('interact')) retry(S.snap ? 'snap' : 'way'); else if (queue.includes('KeyT')) retry('way'); } queue.length = 0; return; }
    if (S.scene !== 'world' && takePress('save')) saveHere('manual');
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
    const m = M(); stepLastStand(dt); stepNpcs(dt);
    hero.inv = Math.max(0, hero.inv - dt); hero.rollCd = Math.max(0, hero.rollCd - dt); hero.slowT = Math.max(0, hero.slowT - dt); hero.dodgeT = Math.max(0, hero.dodgeT - dt); hero.atkCd = Math.max(0, (hero.atkCd || 0) - dt);
    const [ix, iy] = dirInput();
    if (takePress('potion')) usePotion();
    if (takePress('ult') && !S.ultFx) castUlt();
    // 점프 (사장님 10-24 「점프 모션 입력시켜」, 2번방): 마을과 같은 박자(웅크림 4틱 → 공중 0.5초 → 착지 8틱), 공중 높이 16px = 주인공 키의 반, 높이 뜬 동안 바닥 공격(원·줄 장판) 넘김
    if (takePress('dive') && !hero.jump && !hero.roll && !hero.atk && !hero.charge && hero.hp > 0) { const run = hero.run && hero.moving; hero.jump = { t: 0, T: JUMP.T, pre: run ? 0 : JUMP.pre, land: JUMP.land, run }; addFx('dust', hero.x, hero.y, { life: .3 }); sfx('roll', .35, 1.5); }
    if (hero.jump) { const J = hero.jump; J.t += dt; const ta = J.t - J.pre, p = Math.max(0, Math.min(1, ta / J.T)); J.air = ta > 0 && ta < J.T; hero.z = J.air ? 4 * p * (1 - p) * JUMP.h : 0;
      if (J.air) for (const c of codesOf('dash').concat(codesOf('attack'))) { const qi = queue.indexOf(c); if (qi >= 0) queue.splice(qi, 1); } // no dash / swing in the air (same as the town)
      if (ta >= J.T && !J.landed) { J.landed = true; const mm = M(), tx = Math.floor(hero.x / mm.T), ty = Math.floor(hero.y / mm.T);
        if (mm.hopG && mm.hopG[ty * mm.w + tx]) { hero.x = hero.safe[0]; hero.y = hero.safe[1]; addFx('text', hero.x, hero.y - 30, { text: '추락!', life: .7, color: '#ffb0a0' }); hero.inv = 0; hurt(3, null, true); hero.jump = null; hero.z = 0; } // landed in a gap / water: small hit, back to the last solid ground
        else { addFx('dust', hero.x - 5, hero.y, { life: .3 }); addFx('dust', hero.x + 5, hero.y, { life: .3 }); } }
      if (hero.jump && J.landed && (ta >= J.T + J.land || hero.roll)) { hero.jump = null; hero.z = 0; } }
    if (takePress('dash') && !hero.roll && hero.rollCd <= 0) { let dx = ix, dy = iy; if (!dx && !dy) { const f8 = hero.f8 && hero.f8.includes(hero.face) ? hero.f8 : null, a = f8 ? DIR8.indexOf(f8) * Math.PI / 4 : null; [dx, dy] = a !== null ? [Math.cos(a), Math.sin(a)] : FACEV[hero.face]; } const L = Math.hypot(dx, dy);
      hero.roll = { t: 0, dx: dx / L, dy: dy / L, carry: hero.run ? HERO_SPEED * RUN.mul : 0 }; hero.atk = null; setFace(dx, dy); addFx('dust', hero.x, hero.y, { life: .35 }); sfx('roll', .8); }
    // [combat research 10-23] attack input buffer: a press is kept 0.18s, so a press during the swing / roll is not lost
    if (takePress('attack')) hero.atkBuf = .18;
    if (hero.atkBuf > 0 && !hero.roll && !(hero.atkCd > 0) && (!hero.atk || hero.atk.t > atkT(hero.atk.i).a1)) { hero.atkBuf = 0; hero.holdT = 0; hero.holdOk = true; hero.charge = null; const prevAtk = hero.atk; // running + attack = 돌진베기
      if (hero.run && hero.moving && !hero.atk) { hero.atk = { t: 0, hit: new Set(), i: 3 }; addFx('dust', hero.x, hero.y, { life: .35 }); sfx('swing_heavy', .8); } else { hero.combo = prevAtk && prevAtk.i < 2 ? prevAtk.i + 1 : (hero.comboT > 0 && hero.combo < 2) ? hero.combo + 1 : 0; hero.atk = { t: 0, hit: new Set(), i: hero.combo, runSlash: !!(hero.run && hero.moving) }; /* [combat research] a press during the swing continues the combo (was: back to hit 1) */ sfx(hero.combo === 2 ? 'swing_heavy' : 'swing_light', .7); if (hero.atk.runSlash) addFx('dust', hero.x, hero.y, { life: .3 }); if (ix || iy) setFace(ix, iy); else aimAssist(hero.combo); } }
    hero.atkBuf = Math.max(0, (hero.atkBuf || 0) - dt);
    if (isHeld('attack') && hero.holdOk) hero.holdT += dt; else hero.holdOk = false; // charge (모으기): keep holding attack -> lv1 t1 / lv2 t2, release = charged slash; a hit / dodge cancels
    if (!hero.charge && hero.holdOk && hero.holdT > .14 && !hero.atk && !hero.roll && hero.hp > 0) { hero.charge = { t: hero.holdT, lv: 0, flash: 0 }; hero.run = false; }
    if (hero.charge) { const C = hero.charge, CF = spW().charge; C.t += dt; C.flash = Math.max(0, C.flash - dt); const lv = C.t >= CF.t2 ? 2 : C.t >= CF.t1 ? 1 : 0;
      if (lv > C.lv) { C.lv = lv; C.flash = .25; sfx(lv > 1 ? 'ult_cutin' : 'hit_crit', lv > 1 ? .4 : .5, lv > 1 ? 1.9 : 1.7); addFx('spark', hero.x, hero.y - 12, { life: .3 }); }
      if (!hero.holdOk || hero.roll || hero.atk || hero.hp <= 0) { const rel = !hero.holdOk && !hero.roll && !hero.atk && hero.hp > 0 && C.lv > 0; hero.charge = null; if (rel) { hero.atk = { t: 0, hit: new Set(), i: 3 + C.lv }; sfx('swing_heavy', 1); } } }
    if (takePress('interact')) interact();
    tickTrail(dt);
    if (hero.roll) { const r = hero.roll, D = DG(), RD = rollDur(); const p0 = Math.min(1, r.t / RD); r.t += dt; const p = Math.min(1, r.t / RD);
      if (D && D.burstTicks) { const TB = D.burstTicks / 60, q0 = Math.min(1, (r.t - dt) / TB), q1 = Math.min(1, r.t / TB), E2 = q => 1 - Math.pow(1 - q, 2.6), st = fieldDash(D) * (E2(q1) - E2(q0)), n = Math.max(1, Math.ceil(st / 3)); for (let i = 0; i < n; i++) moveCol(hero, r.dx * st / n, r.dy * st / n, 5);
        const tt = Math.round((r.t - dt) * 60); if (tt % 2 === 0 && tt < D.burstTicks && h128()) { S.trail = S.trail || []; S.trail.push({ c128: h128Cell(), x: hero.x, y: hero.y, t: 0, life: (D.durTicks - tt) / 60 + .05, a: .8 * Math.pow(.8, S.trail.length) }); } }
      else if (D) { const E = EASE[D.ease] || EASE.outCubic, st = D.tiles * 16 * (E(p) - E(p0)), n = Math.max(1, Math.ceil(st / 3)); for (let i = 0; i < n; i++) moveCol(hero, r.dx * st / n, r.dy * st / n, 5); // dash: fixed distance, ease-out
        const AI = D.afterimage || {}; r.ai = (r.ai || 0) - 1; r.ain = r.ain || 0; if (r.ai <= 0 && r.ain < (AI.count || 5) && p < .95) { r.ai = AI.intervalTicks || 2; r.ain++; S.trail = S.trail || []; S.trail.push({ c128: h128() ? h128Cell() : null, name: heroFrameName(), x: hero.x, y: hero.y, flip: hero.face === 'left', t: 0, life: AI.fade || .25, a: AI.alpha ?? .55 }); } }
      else { const sp = Math.max(ROLL.speed * (1 - r.t / ROLL.dur * .55), r.carry); moveCol(hero, r.dx * sp * dt, r.dy * sp * dt, 5); }
      hero.walkT += dt * 3;
      if (r.t >= RD) { hero.roll = null; hero.rollCd = DG() ? DG().cdTicks / 60 : ROLL.cd; if (r.carry) { hero.run = true; } } }
    else if (hero.atk) { const a = hero.atk; a.t += dt; const dv = FACEV[hero.face]; const H = (h128() || {}).H128 || {}, AT = atkT(a.i), lv = a.i >= 3 ? (a.t < AT.a1 ? (spOf(a.i).lunge || 0) * .3 / AT.a1 * 2 * (1 - a.t / AT.a1) : 0) : a.runSlash && (ix || iy) && a.t < AT.a1 ? 20 + HERO_SPEED * RUN.mul * (1 - a.t / AT.a1) : 0; // 제자리 공격 (주인 10-23 「공격 버튼 누르면 캐릭이 전진한다」→「제자리 공격」): 기본 베기는 앞으로 안 나감, 이동 키·패드를 누르고 있을 때만 걸으며 벰(아래 ATK_MOVE). 돌진·차지(a.i>=3)는 그대로
      moveCol(hero, dv[0] * lv * dt, dv[1] * lv * dt, 5); // running slash carries momentum
      { const mv = !!(ix || iy); hero.moving = mv; if (mv) { const sp = HERO_SPEED * (hero.run ? RUN.mul : 1) * ATK_MOVE * (hero.slowT > 0 ? .45 : 1); moveCol(hero, ix * sp * dt, iy * sp * dt, 5); hero.walkT += dt * (hero.run ? RUN.mul * RUN.cadence : 1) * ATK_MOVE; } } // [combat research] keep running while slashing (was: rooted for the whole swing)
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
      if (hero.moving && hero.run && hero.lastMv && ix * hero.lastMv[0] + iy * hero.lastMv[1] < -.5 && !(hero.pivotT > 0)) { hero.pivotT = PIVOT.t; addFx('dust', hero.x + hero.lastMv[0] * 4, hero.y, { life: .3 }); addFx('dust', hero.x, hero.y, { life: .25 }); } // 달리다 반대로 꺾기 = 짧은 디딤(조작감 연구 10-24, ?pivot=0 끔)
      if (hero.moving) hero.lastMv = [ix, iy]; const pv = hero.pivotT > 0 && PIVOT.on ? PIVOT.lo + (1 - PIVOT.lo) * (1 - hero.pivotT / PIVOT.t) : 1; hero.pivotT = Math.max(0, (hero.pivotT || 0) - dt);
      if (hero.moving) { heroTurnFx(ix, iy, dt); if (!hero.charge) setFace(ix, iy); moveCol(hero, ix * sp * pv * dt, iy * sp * pv * dt, 5); const w0 = hero.walkT; hero.walkT += dt * (hero.run ? rk * RUN.cadence : 1); if (hero.run && Math.floor(hero.walkT * 4) !== Math.floor(w0 * 4)) addFx('dust', hero.x - ix * 3, hero.y, { life: .25 }); } // footfall dust
      else { hero.wasMv = false; if (hero.skidT > 0) { hero.skidT -= dt; const k = hero.skidT / RUN.skidT; moveCol(hero, hero.skidV[0] * HERO_SPEED * 1.2 * k * dt, hero.skidV[1] * HERO_SPEED * 1.2 * k * dt, 5); } } } // short skid
    stepHW(dt);
    stepOpen(m, dt);
    if (!hero.atk) hero.comboT = Math.max(0, hero.comboT - dt);
    // tiles & objects: pits, spikes, exits, stairs, keys, doors, warp
    const cx = Math.floor(hero.x / m.T), cy = Math.floor(hero.y / m.T);
    let onPit = false, onSpike = false;
    for (const o of m.objs) {
      const inside = o.tx === cx && o.ty === cy;
      const air = !!(hero.jump && hero.jump.air); // 점프 공중: 구멍·가시 함정 위를 지나감 (3번방 10-24)
      if (o.type === 'pit' && inside && !hero.roll && !air) onPit = true;
      if (o.type === 'spikes' && inside && spikeUp(o) && !air) onSpike = true;
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
    else if (!onSpike && !hero.roll && !hero.jump && !trapAt(cx, cy) && Math.floor(S.t * 4) !== Math.floor((S.t - dt) * 4)) hero.safe = [hero.x, hero.y];
    // mobs
    for (const mm of S.mobs) {
      if (mm.dead) continue;
      mm.spawnT = Math.max(0, mm.spawnT - dt); mm.hitT = Math.max(0, mm.hitT - dt); mm.flash = Math.max(0, mm.flash - dt);
      if (mm.lagDelay > 0) mm.lagDelay -= dt; else mm.hpLag = Math.max(mm.hp, mm.hpLag - dt * mm.maxHp * .8);
      if (mm.kx || mm.ky) { moveCol(mm, mm.kx * dt, mm.ky * dt, mm.r, mm.fly); mm.kx *= Math.pow(.002, dt); mm.ky *= Math.pow(.002, dt); if (Math.abs(mm.kx) + Math.abs(mm.ky) < 5) mm.kx = mm.ky = 0; }
      if (mm.abyStun > 0) { mm.abyStun -= dt; mm.shake = mm.abyStun > 0 ? .3 : 0; continue; } // 심연 기절: 생각·공격 멈춤
      if (mm.spawnT <= 0 && hero.hp > 0) mm.D.update(mm, W, dt);
    }
    for (const o of (m.objects || [])) if (o.type === 'spawn' && o.respawn > 0 && o.mob && o.mob.dead) { o.timer -= dt; // respawn out of sight
      const px = (o.x + .5) * m.T, py = (o.y + .5) * m.T; if (o.timer <= 0 && Math.hypot(hero.x - px, hero.y - py) > 200) { const mm = spawn(o.mob.kind, px, py); mm.spawnRef = o; o.mob = mm; } }
    S.mobs = S.mobs.filter(mm => !mm.dead);
    // hazards
    for (let i = S.hazards.length - 1; i >= 0; i--) { const h = S.hazards[i]; h.t += dt;
      if (h.owner && h.owner.dead && h.t < h.warn) { S.hazards.splice(i, 1); continue; }
      const live = h.t >= h.warn && h.t < h.warn + (h.act || 0);
      if (live && h.dmg && !h.hit && !(hero.z > JUMP.h * .45 && h.shape !== 'all') && inHaz(h, hero.x, hero.y - 4)) { if (hurt(h.dmg, h.shape === 'all' ? null : h, h.raw)) { h.hit = true; if (h.slow) hero.slowT = h.slow; } }
      if (live && h.zone && inHaz(h, hero.x, hero.y - 4)) hero.slowT = Math.max(hero.slowT, .15);
      if (h.t >= h.warn && !h.fired) { h.fired = true; if (h.onEnd) h.onEnd(h); hazardFx(h); }
      if (h.linger && h.t >= h.warn + (h.act || 0) && h.t < h.warn + h.act + h.linger && !h.hit && Math.hypot(hero.x - h.x, (hero.y - h.y) * 1.15) < h.r * .8) { if (hurt(1, h)) h.hit = true; }
      if (h.t > h.warn + (h.act || 0) + (h.linger || 0) + .25) { S.hazards.splice(i, 1); if (h === S.ult) S.ult = null; }
    }
    for (let i = S.shots.length - 1; i >= 0; i--) { const s = S.shots[i]; s.t += dt; s.x += s.vx * dt; s.y += s.vy * dt;
      if (s.ret && !s.back && s.t > s.life / 2) { s.back = true; s.vx = -s.vx; s.vy = -s.vy; } // boomerang (felt puppet blades)
      if (Math.hypot(hero.x - s.x, hero.y - 8 - s.y) < s.r + 5 && hurt(s.dmg, s)) { if (s.pull && s.owner && !s.owner.dead) { const a = Math.atan2(s.owner.y - hero.y, s.owner.x - hero.x); moveCol(hero, Math.cos(a) * s.pull, Math.sin(a) * s.pull, 5); const H = s.owner.hist || (s.owner.hist = []); if (!(H[0] === 'melee' && H[1] === 'melee')) { s.owner.intent = 'melee'; s.owner.cd = Math.min(s.owner.cd || 0, .15); H.unshift('melee'); H.length = Math.min(H.length, 2); } } // thread yank -> follow-up claw
        if (s.slow) hero.slowT = Math.max(hero.slowT, s.slow); S.shots.splice(i, 1); continue; }
      if (s.t > s.life || solidAt(s.x, s.y + 6)) { if (s.zone) hazard({ shape: 'circle', x: s.x, y: s.y + 6, r: 12, warn: 0, act: 2, dmg: 0, kind: 'web', zone: true }); // slowing web patch
        addFx('spark', s.x, s.y, { life: .2 }); S.shots.splice(i, 1); } }
    for (let i = S.temp.length - 1; i >= 0; i--) if ((S.temp[i].life -= dt) <= 0) { const t = S.temp[i]; if (t.kind === 'thread') addFx('tsnap', t.x, t.y - 10, { life: .55, red: threadRed(), seed: (Math.random() * 2147483646 | 0) + 1 }); S.temp.splice(i, 1); }
    for (let i = S.fx.length - 1; i >= 0; i--) { const f = S.fx[i]; f.t += dt;
      if (f.type === 'heart' && Math.hypot(hero.x - f.x, hero.y - f.y) < 10) { const hv = Math.ceil(hero.maxHp * POT.heartPct / 100); hero.hp = Math.min(hero.maxHp, hero.hp + hv); syncTownHp(); addFx('text', f.x, f.y - 20, { text: '+' + hv, life: .7, color: '#ff8aa0' }); sfx('heart', .7); S.fx.splice(i, 1); continue; }
      if (f.t > f.life) S.fx.splice(i, 1); }
    // music: area theme / champion battle / boss (phase 2 track) / back to area theme after the clear
    const e = S.engaged, arM = m.compose ? areaOf(m, hero.x, hero.y) : null; let want = (arM && arM.bgm) || m.bgm;
    if (m.type === 'boss') want = S.bossRef && !S.bossRef.dead ? (S.bossRef.phase === 2 ? m.bgm2 : m.bgm) : (m.bgmAfter || 'area01_forest');
    else if (e && !e.dead && e.D.champion && dist(e, hero) < 260) want = (arM && arM.battleBgm) || m.battleBgm || 'battle_champion';
    S.bgm = want;
  }
  function onTile(name) { const m = M(); const c = m.cells[Math.floor(hero.y / m.T) * m.w + Math.floor(hero.x / m.T)]; return c && c.g === name; }
  // spikes: 2.6s cycle (offset per column): down 1.5s, warning tips 0.5s, up 0.6s (hurts)
  const spikePhase = o => ((S.t + o.tx * .18) % 2.6);
  const spikeUp = o => spikePhase(o) > 2.0;
  const spikeWarn = o => spikePhase(o) > 1.5 && spikePhase(o) <= 2.0;
  const trapAt = (cx, cy) => M().objs.some(o => (o.type === 'spikes' || o.type === 'pit') && Math.abs(o.tx - cx) <= 1 && Math.abs(o.ty - cy) <= 1);
  // potion = one key, no pop-up boxes (owner 10-23 "불쾌감 없이 세련되고 깔끔한 아이템 UI"): the HUD slot shakes / shows a short grey word when it can't be used,
  // flashes green when it is, and the heal shows as a green number on the hero. The centre message box is kept for story, not for item spam.
  function usePotion() { const g = window.__game; const n = g ? g.potions : 0, Q = S.qs || (S.qs = {});
    const deny = (word, k) => { Q.shake = k; Q.note = word; Q.noteT = word ? 1.1 : 0; sfx('deny', .5); };
    if (!n) return deny('물약 없음', 1); if (hero.hp >= hero.maxHp) return deny('체력 가득', .6); if (g.potionCd > 0) return deny('', .6);
    const hv = Math.ceil(hero.maxHp * POT.heal / 100); g.potions = n - 1; g.potionCd = POT.cd; hero.hp = Math.min(hero.maxHp, hero.hp + hv); syncTownHp(); addFx('heal', hero.x, hero.y - 20);
    addFx('text', hero.x, hero.y - 32, { text: '+' + hv, life: .9, color: '#8fffa0' }); Q.flash = 1; Q.noteT = 0; sfx('quaff', .7); }
  function feedAdd(name, n, col) { const F = S.feed || (S.feed = []), o = F.find(f => f.name === name && f.t < 1.6); if (o) { o.n += n; o.t = Math.min(o.t, .2); return; } F.push({ name, n, col, t: 0, life: 2.6 }); if (F.length > 5) F.shift(); }
  // 대화창 v2 (2번방 10-23, 1장 어두운 톤): pages ('\n\n' or 3 lines), typewriter DLG.cps with a soft blip, skip = show the page, choices [{t, f}] picked with up/down
  const DLG = { cps: 38, lines: 3 };
  function dlgWrap(line, W) { if (!W) return [line]; const out = []; let cur = ''; // fit one line to the box (UI_GUIDE 8): break at a space when it is past half, else at any letter
    for (const ch of line) { if (cur && ctx.measureText(cur + ch).width > W) { const sp = cur.lastIndexOf(' '); if (sp > cur.length * .5) { out.push(cur.slice(0, sp)); cur = cur.slice(sp + 1) + ch; } else { out.push(cur); cur = ch; } } else cur += ch; }
    out.push(cur); return out; }
  function dlgPages(d) { if (!d.pages) { const P = []; if (d.wrapF) ctx.font = d.wrapF; for (const pg of String(d.text || '…').split(/\n{2,}/)) { const L = [].concat(...pg.split('\n').map(l => dlgWrap(l, d.wrapW))); for (let i = 0; i < L.length; i += DLG.lines) P.push(L.slice(i, i + DLG.lines).join('\n')); }
      d.pages = P.length ? P : ['…']; d.pi = 0; d.ch = 0; d.sel = 0; d.t = 0; } return d.pages; }
  function stepDialog(dt) { const d = S.dialog, P = dlgPages(d), pg = P[d.pi], full = pg.length, last = d.pi === P.length - 1, b4 = Math.floor(d.ch); d.t += dt;
    if (d.cg && (!S.cgL || S.cgL.src !== d.cg || S.t - S.cgL.since < .6)) { S.dlgTap = false; return; } // new story picture: 0.6 s of picture alone first
    d.ch = Math.min(full, d.ch + dt * DLG.cps); const n = Math.floor(d.ch); if (n > b4 && n % 2 === 0 && !/\s/.test(pg[n - 1] || ' ')) sfx('talk', .5, d.pitch || 1);
    if (last && d.choices && d.ch >= full) { if (takePress('up')) d.sel = (d.sel + d.choices.length - 1) % d.choices.length; if (takePress('down')) d.sel = (d.sel + 1) % d.choices.length; }
    const adv = takePress('interact') || takePress('attack') || queue.includes('Space') || queue.includes('Enter') || S.dlgTap; S.dlgTap = false; // phone: tap the picture (UI_GUIDE 10)
    if (adv && d.t > .12) { if (d.ch < full) d.ch = full; else if (!last) { d.pi++; d.ch = 0; sfx('page'); } else { const c = d.choices && d.choices[d.sel]; S.dialog = null; if (c && c.f) c.f(); else if (d.then) d.then(); } }
    else if (takePress('menu') && !d.choices) S.dialog = null; }
  // 1장 대사 (maps/dialog_ch1.json): '이름: 대사' lines switch the speaker (portrait + name tag), '( … )' lines are narration, blank line = new page.
  // NPC lines by stage: meet (first talk) / mid / after (boss_arachne). Scenes play once: area:<id> first visit, boss_pre:<id>, boss_post:<id>.
  let DLGD = null; getJSON('maps/dialog_ch1.json').then(j => { DLGD = j; }).catch(() => {});
  function speakerOf(name) { const sp = DLGD && DLGD.speakers && DLGD.speakers[name]; if (sp) return Object.assign({ name }, sp); const m = M(), o = m && m.objs.find(x => x.type === 'npc' && x.name === name); return o ? { name, role: o.role, anim: o.anim } : null; }
  function toSeq(text, def) { const out = []; let cur = def || null;
    for (const block of String(text || '…').split(/\n{2,}/)) { let it = null;
      for (const raw of block.split('\n')) { const l = raw.trim(); if (!l) continue; const m = l.match(/^([^\s:()「」]{1,8}): ?(.*)$/), sp = m && speakerOf(m[1]); let who = cur, t = l;
        if (sp) { who = sp; t = m[2]; cur = sp; } else if (/^\(.*\)$/.test(l)) who = { name: '', narr: true };
        if (!it || it.who !== who) { it = { who, lines: [] }; out.push(it); } it.lines.push(t); if (who && who.narr) { it = null; } } }
    return out; }
  function playSeq(seq, last) { if (!seq.length) return; const [h, ...rest] = seq, w = h.who || {};
    S.dialog = Object.assign({ text: h.lines.join('\n'), name: w.name || '', role: w.role, anim: w.anim, por: w.por, cg: h.cg, cgDx: h.cgDx, cgLast: !!h.cgLast, creep: !!w.creep, narr: !!w.narr, pitch: w.pitch || 1 }, rest.length ? { then: () => playSeq(rest, last) } : (last || {})); }
  function talkAs(o, text, last, artKey) { const sq = toSeq(text, { name: o.name, role: o.role, anim: o.anim, pitch: o.voice || 1 }); playSeq(artKey ? withArt(sq, artKey) : sq, last); }
  function npcLine(o) { const D = DLGD && DLGD.npc && DLGD.npc[o.id], F = SAVE.flags; if (!D) return o.idle || '…';
    if (F.boss_arachne && D.after) return D.after; if (D.meet && !F['met_' + o.id]) { F['met_' + o.id] = true; save(); return D.meet; } return D.mid || o.idle || '…'; }
  addEventListener('boss-phase', e => { const d = e.detail || {}; if (d.phase === 2) { S.roomP2 = true; S.roomP2Rate = Math.min(.2, 1 / (60 * (d.dur || 1.8)) * 3); } }); // monster room's boss events (claude/arachne-epic)
  addEventListener('boss-dead', () => { S.roomP2 = false; S.roomP2Rate = .012; });
  addEventListener('cocoon-drop', e => { const i = (e.detail || {}).i; if (i !== undefined) (S.cocoonGone = S.cocoonGone || []).push(i); }); // a ceiling cocoon falls (고치 비): hide it here // the red threads unravel slowly
  function areaScene(id, delay) { playScene('area:' + id, delay); if (SAVE.flags.boss_arachne) playScene('area:' + id + ':after', delay + .3); } // ':after' = first visit after the chapter boss (펠트 재방문 → 리네트 동행)
  function playScene(key, delay) { if (Q.has('noscene')) return; /* ?noscene: tests / recordings run without story scenes */ after(delay || 0, () => { const t = DLGD && DLGD.scenes && DLGD.scenes[key]; if (!t || SAVE.flags['scene_' + key]) return; SAVE.flags['scene_' + key] = true; save(); const sq = withArt(toSeq(t), key); if (!S.dialog) playSeq(sq); else { const d = S.dialog, th = d.then; d.then = () => { if (th) th(); playSeq(sq); }; } }); }
  function withArt(seq, key) { const A = DLGD && DLGD.sceneArt && DLGD.sceneArt[key]; if (A) { seq.forEach((it, i) => { for (const [src, from, dx] of A) if (i >= from) { it.cg = src; it.cgDx = dx || 0; } }); seq.forEach((it, i) => { if (it.cg && (!seq[i + 1] || seq[i + 1].cg !== it.cg)) it.cgLast = true; }); } return seq; } // 이야기 그림: sceneArt[장면] = [[그림, 몇 번째 말부터, 시선 -1/0/1]]; cgLast = 그 그림의 마지막 말 (SCENE_FX snap)
  function interact() {
    const m = M(); const dv = FACEV[hero.face]; const fx = Math.floor((hero.x + dv[0] * 12) / m.T), fy = Math.floor((hero.y - 3 + dv[1] * 12) / m.T);
    for (const o of m.objs) {
      if (!((o.tx === fx && o.ty === fy) || Math.hypot(o.x - hero.x, o.y - hero.y) < 15)) continue;
      if (o.type === 'sign') { S.dialog = { text: o.text }; return; }
      if (o.type === 'npc') { let text = (o.quests && NAV()) ? NAV().talk(o) : (o.idle || '…'); S.talked = o.id; const plain = text === (o.idle || '…'); if (plain) text = npcLine(o);
        if ((o.shop || o.forge) && plain && window.__game && (window.__game.openForge || window.__game.openShop)) { talkAs(o, text, { choices: [{ t: o.forge ? '강화·제작' : '물건을 본다', f: () => openTrade(o) }, { t: '그만둔다' }] }); return; } // 대사 먼저, 고르면 가게 // Felt: 롬 = 대장간(강화·제작), 세라·벤 = 상점 — quest talk comes first
        const mk = 'meet:' + o.id, mArt = DLGD && DLGD.sceneArt && DLGD.sceneArt[mk] && !SAVE.flags['cg_' + mk]; if (mArt) { SAVE.flags['cg_' + mk] = true; save(); talkAs(o, text, null, mk); return; } // first talk with story art (리네트 첫 만남)
        if (!o.anim && o.main && !/^[^\s:()「」]{1,8}: /m.test(text)) { S.dialog = { text, name: o.name, role: o.role, por: o.portrait || o.art || o.id }; return; } talkAs(o, text); return; }
      if (o.type === 'clue') { clue(o); return; }
      if (o.type === 'secret_wall') { if (!SAVE.flags[o.flag]) { SAVE.flags[o.flag] = true; save(); m.solidG[o.ty * m.w + o.tx] = 0; shake(4); sfx('impact', .8); for (let i = 0; i < 14; i++) addFx('dust', o.x + (Math.random() - .5) * 16, o.y + (Math.random() - .5) * 10, { life: .6 }); banner(o.name || '숨겨진 길이 드러났다', 2); } else S.dialog = { text: o.textDone || '무너진 벽 너머로 좁은 방이 보인다.' }; return; }
      if (o.type === 'door') { // town B building doors: shops open the shop UI, the inn heals, others show their sign
        const g = window.__game;
        if ((o.shop || o.forge) && openTrade(o)) { S.door = o.id; return; }
        if (o.wish && g && g.INV) { // town H 소원 우물: 10G 동전 던지기 운세 (1/8 chance the well pays 40G back)
          if (g.INV.gold < 10) { S.dialog = { text: '동전이 모자란다. (10G 필요)', name: o.name }; return; }
          g.INV.gold -= 10; const F = ['대길 — 오늘은 무엇을 해도 잘 풀린다.', '길 — 갱도에서 좋은 원석을 만날 운세.', '소길 — 작은 행운이 따른다.', '평 — 평범한 하루. 조심해서 나쁠 건 없다.', '흉 — 박쥐 떼를 조심하라.'];
          const lucky = Math.random() < 1 / 8; if (lucky) g.addGold(40);
          S.wish = (S.wish || 0) + 1; S.dialog = { text: '동전을 던졌다… (-10G)\n' + F[Math.floor(Math.random() * F.length)] + (lucky ? '\n우물이 반짝이며 40G를 돌려주었다!' : ''), name: o.name }; S.door = o.id; return; }
        if (o.race) { S.dialog = { text: '광차 경주 트랙. 「바퀴」가 접수를 받는다.\n광차 경주 미니게임은 아직 준비 중이다. (stub)', name: o.name }; S.door = o.id; return; }
        if (o.heal) { abyssRest(); hero.hp = hero.maxHp; syncTownHp(); addFx('heal', hero.x, hero.y - 20); }
        if (o.to) { go(o.to, o.spawn || 'default'); return; } // a door into another map (펠트 → 아라크네의 폐공방)
        S.dialog = { text: o.text || ('「' + (o.name || '건물') + '」'), name: o.name }; S.door = o.id; return; }
      if (o.type === 'waystone') { const first = !SAVE.waystones[o.id]; SAVE.waystones[o.id] = true; SAVE.lastWay = { map: m.id, id: o.id }; save(); abyssRest(); hero.hp = hero.maxHp; syncTownHp(); addFx('heal', hero.x, hero.y - 20); saveHere('way');
        S.dialog = { text: (first ? '비석에 손을 대자 빛이 깃들었다 — 「' + o.name + '」 등록!\n' : '「' + o.name + '」\n') + '체력 회복 · 저장 완료 · 쓰러지면 여기서 다시 시작\n지도 화면(' + 'M' + ')에서 등록한 비석으로 순간이동할 수 있다.' }; return; }
      if (o.type === 'chest') { if (SAVE.chests[o.id]) { msg('빈 상자다'); return; } SAVE.chests[o.id] = true; save(); banner('보물상자! ' + giveLoot((o.loot || []).concat([['gold', window.__game && window.__game.goldFor ? window.__game.goldFor('chest', o.area || 1) : 0]])), 2.2); addFx('sparkle', o.x, o.y - 10, { life: .8 }); return; }
      if (o.type === 'heal') { abyssRest(); hero.hp = hero.maxHp; syncTownHp(); msg('쉼터에서 쉬었다. 체력 회복!'); addFx('heal', hero.x, hero.y - 20); return; }
      if (o.type === 'lever') { if (o.on) { msg('이미 당긴 레버다'); return; } o.on = true; SAVE.levers[o.key] = true; save(); shake(1); updateGate(m); return; }
      if (o.type === 'door_locked') { tryDoor(o); return; }
      if (o.type === 'boss_door') { bossDoor(o); return; }
      if (o.type === 'gate' && !o.open) { msg('철창이다. 어딘가의 레버로 열 수 있을 것 같다'); return; }
    }
    for (const o of m.objs) if (o.type === 'hidden' && !SAVE.chests[o.id] && Math.hypot(o.x - hero.x, o.y - hero.y) < 22) { SAVE.chests[o.id] = true; save(); banner('풀숲에서 찾았다! ' + giveLoot(o.loot || []), 2.2); return; }
  }
  function openTrade(o) { const g = window.__game; if (!g) return false;
    if (o.forge && g.openForge) { S.dialog = null; g.openForge(); return true; }
    if (o.shop && g.openShop) { S.dialog = null; g.openShop(o.shop); return true; } return false; }
  function questOn(id) { return SAVE.quests[id] === 'active'; }
  function clueReady(o) { return !SAVE.flags[o.flag] && (!o.needQuest || questOn(o.needQuest)) && (o.needFlags || []).every(f => SAVE.flags[f]); }
  function clue(o) { // quest clue (maps: type 'clue'): look once -> sets o.flag (+ loot); text before the quest / while locked / after
    if (SAVE.flags[o.flag]) { S.dialog = { text: o.textDone || '이미 살펴본 곳이다.', name: o.name }; return; }
    if (o.needQuest && !questOn(o.needQuest)) { S.dialog = { text: o.textIdle || o.textLocked || '…', name: o.name }; return; }
    if (!(o.needFlags || []).every(f => SAVE.flags[f])) { S.dialog = { text: o.textLocked || '지금은 할 수 있는 게 없다.', name: o.name }; return; }
    SAVE.flags[o.flag] = true; save(); const got = o.loot ? giveLoot(o.loot) : '';
    S.dialog = { text: o.text + (got ? '\n얻었다: ' + got : ''), name: o.name, cg: o.cg, cgDx: o.cgDx || 0 }; addFx('sparkle', o.x, o.y - 10, { life: .8 }); }
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
  function hazardFx(h) { if (h.dmg && h.kind === 'swipe' && h.owner && h.owner.D && h.owner.D.felt) addFx('claw', h.x, h.y - 6, { life: .22, a: Math.atan2(h.y - h.owner.y, h.x - h.owner.x), r: h.r }); // claw marks at the strike if (h.dmg) sfx(h.kind === 'swipe' || h.kind === 'thud' ? 'mob_swing' : h.kind === 'root' || h.kind === 'web' ? 'mob_swing' : 'impact', .7); if (h.kind === 'rock' || h.kind === 'crystal' || h.kind === 'quake') addFx(h.kind === 'rock' ? 'debris' : 'crystal', h.x, h.y, { life: .5 });
    if (h.kind === 'ult') { shake(7); for (let i = 0; i < 30; i++) { const p = randomFloor(); addFx('crystal', p[0], p[1], { life: .7 }); } }
    if (h.kind === 'poison') addFx('cloud', h.x, h.y, { life: (h.act || 0) + (h.linger || 0) + .2, r: h.r }); }

  // ---------------- camera ----------------
  function clampC(v, max) { return max <= 0 ? max / 2 : Math.max(0, Math.min(max, v)); }
  function camTarget() { const m = M(), b = S.introT > 0 && S.bossRef, fx = b ? b.x : hero.x, fy = b ? b.y - 20 : hero.y - 10; return [clampC(fx - EW / 2, m.pw - EW), clampC(fy - EH / 2, m.ph - EH)]; } // boss intro: the camera looks at the boss first (art room 10-23)
  function snapCam() { if (M()) S.cam = camTarget(); }
  function viewZoomOf(m) { if (m && m.compose) { const a = areaOf(m, hero.x, hero.y); return (a && a.zoom) || 1; } return (m && m.viewZoom) || 1; }
  function updateCam(dt) { if (!M()) return; { const t = viewZoomOf(M()); S.vz = S.vz || t; S.vz += (t - S.vz) * Math.min(1, dt * 2.5); if (Math.abs(t - S.vz) < .002) S.vz = t; EW = Math.ceil(LW / S.vz); EH = Math.ceil(LH / S.vz); } // town view: a little wider, eased at the area seam
    if (S.introT > 0) S.introT -= dt; const [tx, ty] = camTarget(); const k = 1 - Math.pow(S.introT > 0 ? .02 : .0005, dt); S.cam[0] += (tx - S.cam[0]) * k; S.cam[1] += (ty - S.cam[1]) * k; }

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
      drawLow(); ctx.imageSmoothingEnabled = false; const z = cutZoom();
      const bodies = kk => { drawPropsHi(kk, 0); drawNpcHi(kk, 0); drawFeltHi(kk, mm => mm.y <= hero.y); drawPetHi(kk, false); drawHeroHi(kk); drawPetHi(kk, true); drawPropsHi(kk, 1); drawFeltHi(kk, mm => mm.y > hero.y); drawNpcHi(kk, 1); drawHDLight(kk); if (!SLASH_BODY) gkDraw(kk); }; // hi-res bodies (검기 above the mobs it hits)
      const kv = k * (S.vz || 1); S.view = { k: kv, ox, oy }; // world scale on screen (k, or less in a wider town view)
      if (z > 1.001) { const px = hero.x - S.camI[0], py = hero.y - 14 - S.camI[1], kz = kv * z, zx = ox + LW * k / 2 - px * kz, zy = oy + LH * k / 2 - py * kz, mix = Math.min(1, (z - 1) / .6);
        const vx = Math.round(ox + (zx - ox) * mix + (ox + px * kv - px * kz - ox) * (1 - mix)), vy = Math.round(oy + (zy - oy) * mix + (oy + py * kv - py * kz - oy) * (1 - mix));
        const cf = S.camF; S.camF = [0, 0]; ctx.save(); ctx.beginPath(); ctx.rect(ox, oy, LW * k, LH * k); ctx.clip(); S.view = { k: kz, ox: vx, oy: vy }; drawHDGround(kz); ctx.drawImage(low, vx, vy, (EW + 1) * kz, (EH + 1) * kz); bodies(kz); ctx.restore(); S.view = { k: kv, ox, oy }; S.camF = cf; }
      else { const cf = S.camF || [0, 0]; ctx.save(); ctx.beginPath(); ctx.rect(ox, oy, LW * k, LH * k); ctx.clip(); drawHDGround(kv); ctx.drawImage(low, ox - Math.round(cf[0] * kv), oy - Math.round(cf[1] * kv), (EW + 1) * kv, (EH + 1) * kv); bodies(kv); ctx.restore(); } // hi-res bodies stay inside the view (no spill into the letterbox)
      drawHiRes(k, ox, oy);
    }
    if (tr) { let a = 1;
      if (tr.phase === 'out') a = Math.min(1, tr.t / FADE); else if (tr.phase === 'in') a = 1 - Math.min(1, tr.t / FADE);
      if (tr.phase === 'card' && tr.cardData) drawCard(tr, k); else { ctx.fillStyle = `rgba(0,0,0,${a})`; ctx.fillRect(0, 0, CW, CH); }
    }
  }
  function drawLow() {
    const g = lx, m = M();
    // smooth pixel camera: the low canvas is drawn at the whole-pixel camera, the leftover fraction shifts the upscaled image on screen.
    // Rounding alone made the view jump 1-2 px (walk) / 2-3 px (run) on alternating frames = the 'shaking' while moving.
    let cx = Math.floor(S.cam[0]), cy = Math.floor(S.cam[1]); S.camF = [S.cam[0] - cx, S.cam[1] - cy];
    if (S.shake > 0) { cx += Math.round((Math.random() - .5) * S.shake * 2); cy += Math.round((Math.random() - .5) * S.shake * 2); }
    S.camI = [cx, cy];
    g.setTransform(1, 0, 0, 1, 0, 0); g.imageSmoothingEnabled = false; g.fillStyle = m.type === 'world' ? '#0b2a5a' : '#06070a'; if (low.width !== EW + 1 || low.height !== EH + 1) { low.width = EW + 1; low.height = EH + 1; } if (m.hds) g.clearRect(0, 0, EW + 1, EH + 1); else g.fillRect(0, 0, EW + 1, EH + 1);
    g.drawImage(m.groundC, -cx, -cy);
    g.translate(-cx, -cy);
    if (m.type === 'world') { drawWorldNodes(g, m); drawHeroSprite(g, WORLD_ZOOM); g.setTransform(1, 0, 0, 1, 0, 0); return; }
    for (const o of m.objs) drawObjTile(g, m, o);
    if (NAV()) NAV().drawGround(g, cx, cy);                  // guide route breadcrumbs
    for (const h of S.hazards) drawHazard(g, h, false);     // telegraphs on the floor, under sprites
    drawLock(g);
    const list = [];                                         // y-sorted sprites
    for (const d of m.decos) if (!d.broken && !d.hd && d.x > cx - 40 && d.x < cx + EW + 40 && d.y > cy - 10 && d.y < cy + EH + 70) list.push({ y: d.y, f: () => { const gr = gradeAt(m, d.x, d.y); drawSpr(g, d.spr, d.x, d.y + 1, gr ? { mode: gr } : {}); } });
    for (const o of m.objs) {
      if (o.type === 'chest') list.push({ y: o.y + 6, f: () => drawSpr(g, SAVE.chests[o.id] ? 'chest_open' : 'chest', o.x, o.y + 7) });
      if (o.type === 'secret_wall' && SAVE.flags[o.flag]) list.push({ y: o.y - 9, f: () => { g.fillStyle = '#0b0806'; g.fillRect(o.x - 7, o.y - 9, 14, 17); g.fillStyle = '#3e362e'; for (const [dx, dy] of [[-7, 6], [-3, 7], [4, 6], [6, 7], [0, 8]]) g.fillRect(o.x + dx, o.y + dy, 2, 1); } }); // the broken wall: a dark gap + rubble
      if (o.type === 'sign') list.push({ y: o.y + 6, f: () => drawSpr(g, 'sign', o.x, o.y + 8) });
      if (o.type === 'heal') list.push({ y: o.y + 6, f: () => drawBench(g, o) });
      if (o.type === 'door_deco') list.push({ y: o.y - 8, f: () => drawSpr(g, o.sprite, o.x, o.y + 8) });
      if (o.type === 'hidden' && !SAVE.chests[o.id] && Math.sin(S.t * 3 + o.x) > .8) list.push({ y: o.y, f: () => { g.fillStyle = '#fff8c0'; g.fillRect(o.x - 1, o.y - 7, 2, 3); g.fillRect(o.x - 3, o.y - 6, 6, 1); } });
      if (o.type === 'warp') list.push({ y: o.y, f: () => drawWarp(g, o) });
      if (o.type === 'clue' && clueReady(o) && Math.sin(S.t * 4 + o.x) > .3) list.push({ y: o.y, f: () => { g.fillStyle = '#fff3a0'; g.fillRect(o.x - 1, o.y - 8, 2, 5); g.fillRect(o.x - 3, o.y - 6, 6, 1); } });
      if (o.type === 'npc' && o.anim && npcAnim(o.anim)) list.push({ y: o.y + 6, f: () => { g.fillStyle = 'rgba(0,0,0,.28)'; g.beginPath(); g.ellipse(o.x, o.y + 7, 5, 2, 0, 0, TAU); g.fill();
        if (o.main) { g.fillStyle = '#ffe08a'; g.fillRect(Math.round(o.x) - 1, Math.round(o.y + 7 - 34), 2, 2); } } });
      else if (o.type === 'npc') list.push({ y: o.y + 6, f: () => { const im = o.art && npcImg(o.art);
        if (im && im.complete && im.naturalWidth) { const h = o.h || 26, w = im.naturalWidth * h / im.naturalHeight; g.drawImage(im, Math.round(o.x - w / 2), Math.round(o.y + 7 - h), w, h); }
        else drawSpr(g, o.sprite || 'npc_bard', o.x, o.y + 7);
        if (o.main) { g.fillStyle = '#ffe08a'; g.fillRect(Math.round(o.x) - 1, Math.round(o.y + 7 - (o.h || 26)) - 4, 2, 2); } } });
      if (o.type === 'waystone' && o.art !== 'hd') list.push({ y: o.y + 6, f: () => drawWaystone(g, o) }); // art:'hd' = the map's hd part is the stone
    }
    for (const t of S.temp) list.push({ y: t.y + 3, f: () => { if (t.kind === 'cocoon') { const x = Math.round(t.x), y = Math.round(t.y); g.globalAlpha = Math.min(1, t.life * 2); g.fillStyle = 'rgba(0,0,0,.3)'; g.fillRect(x - 6, y + 1, 12, 3); g.fillStyle = '#e8e2d4'; g.beginPath(); g.ellipse(x, y - 6, 6, 8, .2, 0, TAU); g.fill(); g.strokeStyle = 'rgba(120,110,100,.8)'; g.lineWidth = 1; for (let i = -1; i <= 1; i++) { g.beginPath(); g.moveTo(x - 6, y - 6 + i * 4); g.lineTo(x + 6, y - 4 + i * 4); g.stroke(); } g.globalAlpha = 1; return; } // 고치 비: landed cocoon (obstacle)
      if (t.kind !== 'thread' && t.kind !== 'threadwall') return drawSpr(g, 'crystal', t.x, t.y + 5, { alpha: Math.min(1, t.life * 3) });
      const x = Math.round(t.x), y = Math.round(t.y); g.globalAlpha = t.kind === 'threadwall' ? 1 : Math.min(1, t.life * 3); g.fillStyle = 'rgba(0,0,0,.3)'; g.fillRect(x - 5, y + 2, 10, 3); // 실 감옥 기둥 (아라크네): a steel-thread spool post, code-drawn
        g.fillStyle = '#5a3a22'; g.fillRect(x - 5, y - 13, 10, 3); g.fillRect(x - 5, y, 10, 3); g.fillStyle = '#9aa0ae'; g.fillRect(x - 4, y - 10, 8, 10); g.fillStyle = '#d8dce6'; for (let i = 0; i < 4; i++) g.fillRect(x - 4, y - 9 + i * 3, 8, 1);
        g.fillStyle = 'rgba(230,232,245,.55)'; g.fillRect(x, y - 22, 1, 9); g.globalAlpha = 1; } });
    for (const mm of S.mobs) if (!mm.dead) list.push({ y: mm.y + (mm.D.hover ? 8 : 0), f: () => drawMob(g, mm) });
    if (lastStandOn()) list.push({ y: hero.y - .1, f: () => { const p = .5 + .5 * Math.sin(S.t * 10); g.save(); for (let i = 0; i < 3; i++) { g.fillStyle = `rgba(${18 + i * 30},0,${40 + i * 40},${.45 - i * .12 + p * .1})`; g.beginPath(); g.ellipse(hero.x, hero.y + 2, 8 + i * 4 + p * 2, 3.5 + i * 2 + p, 0, 0, TAU); g.fill(); } /* void wisps rising from the feet */ g.globalCompositeOperation = 'lighter'; for (let k = 0; k < 6; k++) { const ph = (S.t * .9 + k / 6) % 1, ax = hero.x + Math.sin(k * 2.4 + S.t * 3) * (6 + k % 3 * 2), ay = hero.y + 2 - ph * 26; g.fillStyle = `rgba(150,90,255,${.5 * (1 - ph)})`; g.fillRect(Math.round(ax), Math.round(ay), 1, 2 + (k % 2)); } g.restore(); } });
    list.push({ y: hero.y, f: () => drawHeroSprite(g, 1) });
    for (const f of S.fx) if (f.type === 'heart') list.push({ y: f.y, f: () => drawHeartPick(g, f) });
    list.sort((a, b) => a.y - b.y).forEach(o => o.f());
    if (S.ultFx && S.ultFx.U.whole && S.ultFx.fx && S.ultFx.fx !== 'pillar') { abyssDark(g, S.ultFx); drawAbyssLow(g, S.ultFx); } // pixel effect in the world canvas (same pixels as the map)
    for (const s of S.shots) drawShot(g, s);
    for (const h of S.hazards) drawHazard(g, h, true);
    for (const f of S.fx) drawFx(g, f);
    drawAshFall(g, m.compose ? { grade: gradeAt(m, hero.x, hero.y) } : m, cx, cy);
    drawLairBelow(g, m, cx, cy);
    if (m.dark) { // dungeon darkness, light around the hero, torches and crystals
      const D = darkLayer(), d = D.getContext('2d'); d.setTransform(1, 0, 0, 1, 0, 0); d.globalCompositeOperation = 'source-over'; d.clearRect(0, 0, EW + 1, EH + 1);
      d.fillStyle = lairP2() ? `rgba(14,2,6,${m.dark})` : `rgba(4,6,12,${m.dark})`; d.fillRect(0, 0, EW + 1, EH + 1); d.globalCompositeOperation = 'destination-out';
      const light = (x, y, r) => { const gr = d.createRadialGradient(x - cx, y - cy, 0, x - cx, y - cy, r); gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(.6, 'rgba(0,0,0,.7)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); d.fillStyle = gr; d.fillRect(x - cx - r, y - cy - r, r * 2, r * 2); };
      light(hero.x, hero.y - 10, 100);
      for (const o of m.objs) if (o.type === 'torch') light(o.x, o.y + 8, 50 + Math.sin(S.t * 9 + o.x) * 3);
      for (const dd of m.decos) if (dd.spr === 'crystal') light(dd.x, dd.y - 6, 26);
      for (const mm of S.mobs) if (mm.D.boss) light(mm.x, mm.y - 30, 70);
      g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(D, 0, 0); g.translate(-cx, -cy);
      g.globalCompositeOperation = 'lighter'; for (const o of m.objs) if (o.type === 'torch') { g.fillStyle = `rgba(255,140,40,${.12 + Math.sin(S.t * 11 + o.x) * .03})`; g.beginPath(); g.arc(o.x, o.y + 6, 15, 0, TAU); g.fill(); } g.globalCompositeOperation = 'source-over'; }
    drawLairAbove(g, m);
    drawThreadGlow(g); // 실 효과: after the darkness so the aimed thread reads in the dark boss room
    if (S.ult) drawUlt(g, S.ult);
    g.setTransform(1, 0, 0, 1, 0, 0);
  }
  let _dark = null; function darkLayer() { if (!_dark) _dark = document.createElement('canvas'); if (_dark.width !== EW + 1 || _dark.height !== EH + 1) { _dark.width = EW + 1; _dark.height = EH + 1; } return _dark; }
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
  // ---- 자연스러운 방향 전환 (모션연구방 10-23, 사장님 "누가 봐도 자연스러운 방향전환"): 그림 방향은 45°씩 돌아감(90° 이상 꺾으면 사이 방향을 0.04초씩 거침,
  // 뒤로 돌 때는 화면 쪽(↓)으로 돎) + 동작이 바뀌는 순간 머리가 순간이동하지 않게 그 차이를 0.06초에 걸쳐 풀어 줌(H8POP). 그림만 바뀌고 이동·공격 방향은 그대로.
  const PIVOT = { on: Q.get('pivot') !== '0', t: .08, lo: .35 }; // run reversal: 0.08 s plant, speed 35% -> 100% (input / facing / attack direction stay instant)
  const TURN_STEP = .04, POP_TAU = .06, H8HX = new Map(); let h8HXcv = null;
  function h8Turn(h, f8) { const T = DIR8.indexOf(f8), now = S.t; if (T < 0) return f8;
    if (h.vd == null || S.deadT > 0 || h.roll || now < (h.vdT ?? now)) { h.vd = T; h.vdTg = T; h.vdT = now; h.vdAcc = 0; return f8; }
    const dt = Math.min(.1, now - h.vdT); h.vdT = now; let diff = ((T - h.vd) % 8 + 8) % 8;
    if (T !== h.vdTg) { h.vdTg = T; if (diff === 1 || diff === 7) { h.vd = T; return f8; } h.vdAcc = TURN_STEP; h.vdDir = diff < 4 ? 1 : diff > 4 ? 7 : [1, 2, 3].some(i => (h.vd + i) % 8 === 2) ? 1 : [1, 2, 3].some(i => (h.vd + 8 - i) % 8 === 2) ? 7 : (h.vd === 2) === (h.hz === 'left') ? 1 : 7; } else h.vdAcc += dt;
    while (diff && h.vdAcc >= TURN_STEP) { h.vdAcc -= TURN_STEP; h.vd = (h.vd + (h.vdDir || 1)) % 8; diff = ((T - h.vd) % 8 + 8) % 8; }
    return DIR8[h.vd]; }
  function h8HeadX(c) { const key = c.h8 + ':' + c[0] + ':' + c[1]; if (H8HX.has(key)) return H8HX.get(key); const im = h128().H8img(c.h8); if (!im || !im.complete || !im.naturalWidth) return null; let v = 0;
    try { const w = c[2], hh = c[3]; h8HXcv = h8HXcv || document.createElement('canvas'); h8HXcv.width = w; h8HXcv.height = hh; const g = h8HXcv.getContext('2d', { willReadFrequently: true }); g.clearRect(0, 0, w, hh); g.drawImage(im, c[0], c[1], w, hh, 0, 0, w, hh); const d = g.getImageData(0, 0, w, hh).data;
      const on = (x, y) => { const i = (y * w + x) * 4, r = d[i], gg = d[i + 1], b = d[i + 2], mn = Math.min(r, gg, b), mx = Math.max(r, gg, b); return d[i + 3] > 40 && !(mn > 150 && mx - mn < 40); }; // body pixels, not the sword blade
      let top = -1; for (let y = 0; y < hh && top < 0; y++) { let n = 0; for (let x = 0; x < w; x++) if (on(x, y)) n++; if (n >= 2) top = y; }
      let sx = 0, n = 0; for (let y = top; y >= 0 && y < Math.min(hh, top + 10); y++) for (let x = 0; x < w; x++) if (on(x, y)) { sx += x; n++; } v = n ? sx / n - c[4] : 0; } catch (e) { v = 0; }
    H8HX.set(key, v); return v; }
  function h8Pop(h, c, L, fl) { const hx = h8HeadX(c), now = S.t; if (hx == null) return h.pop || 0; const tg = fl ? -hx : hx, dt = Math.min(.1, Math.max(0, now - (h.popT ?? now))); h.popT = now;
    h.pop = (h.pop || 0) * Math.exp(-dt / POP_TAU); if (h.popL && (h.popL !== L || h.popF !== fl) && !(S.deadT > 0)) h.pop = Math.max(-60, Math.min(60, h.pop + h.popTg - tg));
    h.popL = L; h.popF = fl; h.popTg = tg; return Math.abs(h.pop) < .5 ? 0 : h.pop; }
  function h8Cell() { const G = h128(), H = G.H8, h = hero; if (!H || !G.H8img(0) || (S.deadT > 0 && !H.anims.death_down)) return null; const f8 = h8Turn(h, h.f8 && h.f8.includes(h.face) ? h.f8 : (h.face || 'down'));
    // same choice as the town (index.html heroCell8, owner 10-23 "합본"): facing up/down -> the front / back art (diagonals too, mirrored when heading left), else the side art
    if (f8.includes('left')) h.hz = 'left'; else if (f8.includes('right')) h.hz = 'right';
    const fc = H.diag && h.vd != null ? (f8.includes('down') ? 'down' : f8.includes('up') ? 'up' : f8) : /^(right|left|up|down)$/.test(h.face) ? h.face : 'down', vert = !!H.diag && (fc === 'down' || fc === 'up'), hl = vert ? (f8.includes('left') || (!f8.includes('right') && h.hz === 'left')) : fc === 'left';
    const sd = vert ? (hl ? 'left' : 'right') : fc, L8 = H.left && sd === 'left'; let fl = sd === 'left' && !L8, d = L8 ? 'left' : fl ? 'right' : sd;
    const DIAG8 = /^(idle|walk|run|dash|jump|hit1|hit2|hit3)$/, pick = k => { const dk = fc === 'down' && f8 !== 'down' && H.anims[k + '_dr'] ? 'dr' : fc === 'up' && f8 === 'up' && H.anims[k + '_n'] ? 'n' : fc; /* ↘/↙ = *_dr art (mirrored for ↙), ↑ = *_n straight back (never mirrored), motion lab 10-23 */ if (vert && DIAG8.test(k) && H.anims[k + '_' + dk]) { fl = dk === 'n' ? false : hl; d = dk; } else { fl = sd === 'left' && !L8; d = L8 ? 'left' : fl ? 'right' : sd; } return H.anims[k + '_' + d]; };
    let LL = null; const A = k => (LL = pick(k) || H.anims[k + '_' + (hl && H.anims[k + '_left'] ? 'left' : 'right')]), /* hurt has side views only: facing up/down used to crash */ seq = (L, t) => { let i = 0; for (; i < L.length - 1; i++) { if (t < L[i][2]) break; t -= L[i][2]; } return L[i]; }, tot = L => L.reduce((a, f) => a + f[2], 0); let e;
    // 출발·멈춤 (모션연구방 10-23, 걷기 박자 연구): 서 있다 출발하면 다리 모인 장(한 바퀴의 0.28)부터, 멈추면 다음 다리 모인 장까지 빠르게 마저 디딘 뒤 서기
    if (h.moving && !h.wasMov) { h.gp = .28; h.stopT = null; } if (!h.moving && h.wasMov) { h.stopT = S.t; h.stopRun = h.run; h.stopU = S.t; } h.wasMov = h.moving;
    { const dx = h.x - (h.gx ?? h.x), dy = h.y - (h.gy ?? h.y); let m = Math.hypot(dx, dy); h.gx = h.x; h.gy = h.y; const dtg = Math.min(.1, S.t - (h.gT ?? S.t)); h.gT = S.t; if (h.moving && dtg > 0) m = Math.max(m, HERO_SPEED * (h.run ? RUN.mul : 1) * dtg * .7); /* blocked: walk / run in place (owner 10-23 「장애물 부딪히면 모션이 안나오고」) */ if (m < 20 && h.moving) h.gp = ((h.gp || 0) + m / (h.run ? (H.gait && H.gait.runCyc ? H.gait.runCyc * 46 / 119 : 46) : (H.gait && H.gait.walkCyc ? H.gait.walkCyc * 32 / 84 : 32))) % 1; } // gait phase by distance (town 84 / 119 px per cycle x 30/78 field scale)
    if (S.deadT > 0) e = seq(A('death'), S.deadT * 60);
    else if (h.atk && SLASH_BODY) { const i = h.atk.i, AT = atkT(i), L = A(i === 3 ? 'hit1' : i >= 4 || i === 2 ? 'hit3' : i === 1 ? 'hit2' : 'hit1'); e = seq(L, Math.min(.999, h.atk.t / AT.dur) * tot(L)); }
    else if (h.charge) e = A('hold')[0];
    else if (h.jump && H.anims.jump_right) { const J = h.jump, L = J.run && !vert && H.anims['rjump_' + d] ? H.anims['rjump_' + d] : A('jump'); e = seq(L, Math.min(.999, J.t / (J.pre + J.T + J.land)) * tot(L)); }
    else if (h.roll) { const L = A('dash'); e = seq(L, h.roll.t / rollDur() * tot(L)); }
    else if (hero.inv > .67 && S.scene !== 'world') { const L = A(H.anims.hurtys_right ? 'hurtys' : 'hurt'); e = seq(L, (1 - hero.inv) * 60); }
    else if (h.moving) { const L = A(h.run ? 'run' : 'walk'); e = L[Math.floor((h.gp || 0) * L.length) % L.length]; }
    else if (h.stopT != null && S.t - h.stopT < .2 && !h.atk && !h.roll && !h.charge) { const dd = ((.28 - (h.gp || 0)) % .5 + .5) % .5, adv = Math.min(dd, Math.max(0, S.t - (h.stopU ?? S.t)) * 3); h.stopU = S.t; h.gp = ((h.gp || 0) + adv) % 1;
      if (dd - adv < .01) { h.stopT = null; const L = A('idle'); e = H.v4 ? seq(L, (S.t * 60) % tot(L)) : L[0]; } else { const L = A(h.stopRun ? 'run' : 'walk'); e = L[Math.floor(h.gp * L.length) % L.length]; } } // finish the step onto the legs-together frame
    else if (H.v4) { const L = A('idle'); e = seq(L, (S.t * 60) % tot(L)); }
    else e = A('idle')[0];
    if (!e) return null; const c = H.cells[e[0]][e[1]].slice(); c.h8 = e[0]; c.fl = fl; c.ox = h8Pop(h, c, LL, fl); return c; }
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
  function drawH128(c, x, y, k, alpha, tint) { const G = h128(); let im = tint ? (G.H128tint || {})[tint] : G.H128img; if (c.h8 !== undefined) { im = G.H8img(c.h8); if (im && tint) { const t = G.h8tinted(im, c, tint); return drawH128Raw(t, Object.assign([0, 0, c[2], c[3], c[4], c[5]], { ox: c.ox }), x, y, k, alpha, c.fl); } } if (!im) return; return drawH128Raw(im, c, x, y, k, alpha, c.fl); }
  function drawH128Raw(im, c, x, y, k, alpha, fl) { const sc = k * H128FIG / 117, [sx0, sy] = W2S(x, y), sx = sx0 + (c.ox || 0) * sc;
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
      if (f) { const [k, w, dd] = f, ad = Math.abs(dd); if (ad < w / 2 + 6) { cr = 40; cg = 110; cb = 255; al = 40 + 80 * k; } if (ad >= w / 2 && ad < w / 2 + 4) { cr = 16; cg = 28; cb = 72; al = 255; } /* [검흔 어울림 연구 10-23] navy rim (the hero's coat): contrast vs the ground x1.6-2 on all maps */ if (ad < w / 2) { cr = 90 + 165 * k * k; cg = 190 + 65 * k; cb = 255; al = 230; } if ((ad < w / 5 && k > .25) || (dd > w / 2 - 1.5 && dd < w / 2 && k > .4)) { cr = cg = cb = 255; al = 255; } }
      if (al < 230) { const e = sField(R * .78, span * .85, T * .45, head * .95, tail + .1, ca, sa, rev, sq, flip, x, y); if (e && Math.abs(e[2]) < e[1] / 2) { cr = 150; cg = 225; cb = 255; al = Math.max(al, 180 * e[0]); } }
      if (al) { d[i] = cr; d[i + 1] = cg; d[i + 2] = cb; d[i + 3] = al; } }
    g.putImageData(id, 0, 0); sCache.set(key, c2); return c2; }
  // owner 10-23 "검흔 문제점": the hit used to reach 2-3x past the drawn arc (old painted-slash hitbox) and land before the arc flew.
  // Now each arc flies out to the hit range (hbR) in GK_FLY steps and hits a mob only when its front passes it; diagonal input = 45° arc.
  const GK_FLY = 8, GK_K = H128FIG / 117; // arc steps to reach the hit range; atlas px -> field px
  // [combat research] no stick held at the press: turn to the nearest mob within reach + 30px and 70° of the facing (8 directions)
  function aimAssist(i) { const v = gkDir(), reach = (i <= 2 ? GK_REACH[i] : hbR(i)) + 30; let best = null, bd = 1e9;
    for (const mm of S.mobs) { if (mm.dead) continue; const dx = mm.x - hero.x, dy = (mm.y - hero.y) / .8, d = Math.hypot(dx, dy); if (d > reach || d < 1) continue; if ((dx * v[0] + dy * v[1]) / d < Math.cos(70 * Math.PI / 180)) continue; if (d < bd) { bd = d; best = [dx, dy]; } }
    if (best) setFace(best[0], best[1]); }
  function gkDir() { const f8 = hero.f8 && hero.f8.includes(hero.face) ? hero.f8 : null; if (f8 && f8 !== hero.face) { const a = DIR8.indexOf(f8) * Math.PI / 4; return [Math.cos(a), Math.sin(a)]; } return FACEV[hero.face] || [1, 0]; }
  // owner 10-23 "게임을 좀 어렵게 / 검기 판정 줄여": the hit reaches about as far as the drawn arc (was 67 / 49 / 62 px, 150-170°) and only in front
  // [검기 난이도 연구 10-23] reach x0.8 (≈ the chapter-1 felt mobs' melee reach 34-46px with the body pad) so a hit means stepping into danger, arc x1.3 so aiming stays forgiving
  const GK_REACH = [32, 30, 37], GK_ARC = [130, 143, 156]; // field px per combo hit 1-3 (specials 3+ keep hbR), degrees
  function gkSpawn(i) { const v = gkDir(), l = Math.hypot(v[0], v[1]) || 1, dx = v[0] / l, dy = v[1] / l, n = Math.min(2, i), Y = GK[n], reach = i <= 2 ? GK_REACH[i] : hbR(i);
    const sp = Math.max(Y.v, (reach / GK_K - Y.fwd - Y.R * (1 + .025 * GK_FLY)) / GK_FLY);
    S.gk = S.gk || []; S.gk.push({ n, i, dir: [dx, dy], v: sp, reach, cosA: Math.cos((i <= 2 ? GK_ARC[i] : hbA(i)) / 2 * Math.PI / 180), hit: new Set(), rx: dx * Y.fwd, ry: Math.abs(dx) < .1 ? -44 + dy * (Y.fwd + 20) : -Y.y + dy * 20, t: 0, seed: (Math.random() * 2147483646 | 0) + 1, map: S.map }); }
  function gkHits(f) { if (f.t * GK_STEP > GK_HITA) return;
    for (const mm of S.mobs) { if (mm.dead || f.hit.has(mm)) continue; const mh = (mm.D.h || 20) * (mm.scale || 1);
      if (gkTouch(f, mm, mh)) { f.hit.add(mm); S.gkImp = S.gkImp || []; S.gkImp.push({ x: mm.x, y: mm.y - mh * .45, t: 0, big: f.i >= 2, thread: !!mm.D.felt, a: Math.atan2(mm.y - hero.y, mm.x - hero.x), seed: (Math.random() * 2147483646 | 0) + 1 });
        hitMob(mm, f.i >= 3 ? ATK_DMG[0] * (spOf(f.i).dmgMul || 1) : ATK_DMG[Math.min(2, f.i)], Math.atan2(mm.y - hero.y, mm.x - hero.x), true); if (f.i >= 3) sfx(f.i === 5 ? 'hit_crit' : 'hit_heavy', .8);
        if (!f.stopped) { f.stopped = true; S.freezeT = Math.max(S.freezeT || 0, HITSTOP_HERO[Math.min(3, f.i)]); if (f.i >= 2) shake(1.5); } } } } // [combat research] hit-stop on the hero's own hits (was none in the field)
  const JUMP = { T: .5, pre: 4 / 60, land: 8 / 60, h: 16 }; // field jump (town FEEL.jumpTicks 30 / jumpPreTicks 4 / jumpLandTicks 8)
  const HITSTOP_HERO = [2 / 60, 3 / 60, 5 / 60, 5 / 60];
  // [검흔 어울림 연구 10-23 「맞는 곳 = 보이는 곳」] one arc placement for the drawing and the hit: the arc stops flying at its reach (GK_FLY)
  // and sits where it crosses a mob's body (side +27, up +60, down -75 atlas px); a mob is hit when a point of its body (feet..head x left/mid/right)
  // is inside the drawn band. Measured with 1132 dummy mobs x 3 directions: hit-but-not-touched 25% -> 3%, touched-but-missed 35% -> 20%, reach same.
  const GK_DY = { side: 27, up: 60, down: -75 }, GK_HITA = 11, gkQ = v => Math.round(v * 4) / 4;
  function gkPose(f) { const a = f.t * GK_STEP, Y = GK[f.n], [dx, dy] = f.dir, fl = dx < 0, tr = Math.min(a, GK_FLY), ang = Math.atan2(dy, Math.abs(dx)) * 180 / Math.PI;
    return { a, Y, fl, head: Math.min(1, (a + 1) / 2.5), tail: a < 4 ? 0 : Math.min(1, (a - 4) / 7), ox: f.rx + dx * tr * f.v, oy: f.ry + dy * tr * f.v + (Math.abs(dx) < .1 ? (dy < 0 ? GK_DY.up : GK_DY.down) : GK_DY.side),
      R: Y.R * (1 + .025 * gkQ(a)), T: Y.T * (a < 6 ? 1 : Math.max(.35, 1 - (a - 6) / 7)), rot: Y.rot + ang * (fl ? -1 : 1) }; }
  function gkTouch(f, mm, mh) { const P = gkPose(f); if (!(P.tail < P.head)) return false; const an = P.rot * Math.PI / 180, ca = Math.cos(an), sa = Math.sin(an), r = mm.r || 6;
    for (let j = 0; j <= 4; j++) for (const ex of [-r, 0, r]) { const e = sField(P.R, P.Y.span, P.T, gkQ(P.head), gkQ(P.tail), ca, sa, P.Y.rev, P.Y.sq, P.fl, (mm.x + ex - hero.x) / GK_K - P.ox, (mm.y - mh * j / 4 - hero.y) / GK_K - P.oy);
      if (e && Math.abs(e[2]) < e[1] / 2 + 6) return true; }
    return false; }
  function gkTick() { if (S.gk) { for (const f of S.gk) { f.t++; if (f.map === S.map && S.scene !== 'world') gkHits(f); } S.gk = S.gk.filter(f => f.t * GK_STEP <= GK_LIFE + 3 && f.map === S.map); } if (S.gkImp) { for (const m of S.gkImp) m.t++; S.gkImp = S.gkImp.filter(m => m.t < 10); } }
  function gkArcDraw(ctx, f) { // one arc at the local origin (hero feet), atlas px; shared with the town (window.GKART)
    const P = gkPose(f), { a, Y, fl, ox, oy } = P, [dx, dy] = f.dir; // rides with the hero, flies forward to its reach and stops there
      if (P.tail < P.head) { const im = sArc(P.R, Y.span, P.T, gkQ(P.head), gkQ(P.tail), P.rot, Y.rev, Y.sq, fl); ctx.drawImage(im, Math.round(ox - im.width / 2), Math.round(oy - im.height / 2)); }
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
      if (a < 4) { const L = (m.big ? 18 : 12) * (1 - a / 5); ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.fillRect(-L, -1, 2 * L, 2); ctx.fillRect(-1, -L, 2, 2 * L); }
      if (m.thread) threadSpray(ctx, m, al); ctx.restore(); } }
  function gkKick(a) { // body recoil for a 검기 swing, feet planted (motion lab 10-23): wind-up = lean back + crouch, release = lean forward + stretch,
    // then a damped spring settles it (small overshoot = follow-through); hit 3 also takes a short step. lean/step in art px at head height / feet.
    const AT = atkT(a.i), u = a.t, big = a.i === 2;
    if (u < AT.a0) { const q = u / Math.max(AT.a0, 1e-3), e = q * q * (3 - 2 * q); return { lean: -3 * e, step: 0, sq: 1 - .04 * e }; }
    const t = u - AT.a0, w = 30, z = .45, wd = w * Math.sqrt(1 - z * z), sp = Math.exp(-z * w * t) * (Math.cos(wd * t) + z / Math.sqrt(1 - z * z) * Math.sin(wd * t));
    const L0 = big ? 9 : 6, st = (big ? 5 : 1.5) * (1 - Math.exp(-t * 28)) * Math.max(0, Math.min(1, (AT.dur - u) / (AT.dur * .35))); // the step eases back during the recovery (draw offset only)
    return { lean: L0 * sp, step: st, sq: 1 + .045 * Math.exp(-t * 30) * Math.cos(t * 40) };
  }
  // 출발·멈춤 무게감 (모션연구방 10-23, "사용자 입장에서 더 실제처럼"): 속도가 바뀌는 순간 몸(머리 쪽)이 스프링처럼 쏠림 —
  // 출발하면 앞으로 숙였다 돌아오고, 멈추면 뒤로 버텼다가 살짝 앞으로 넘어갔다 섬. 발은 땅에 그대로(그리기에서 기울이기만). 단위: 머리 높이에서 그림 px
  const LEAN = { kick: 150, w: 14, z: .4, max: 12 };

  // ---- 방향 꺾기 효과 (사장님 10-24 「방향 전환 시 모션이 있어야 부드럽고 역동적」, 이펙트 담당; 몸 돌기 그림은 모션 담당):
  // 달리던 방향에서 꺾으면 135°+ = 브레이크(흙 튐 크게 + 미끄러진 자국 + 옛 방향으로 쏠림 + 망토가 늦게 따라오는 잔상 1장), 45~90° = 발밑 먼지 작게 + 살짝 쏠림.
  const TURN = { big: 120, small: 40, minT: .12, cd: .14, leanBig: 1.4, leanSmall: .55, ghost: .32, ghostLife: .11 };
  function heroTurnFx(ix, iy, dt) { const a = Math.atan2(iy, ix), h = hero; h.turnCd = Math.max(0, (h.turnCd || 0) - dt);
    if (h.mvA == null || !h.wasMv) { h.mvA = a; h.mvT = 0; h.wasMv = true; return; }
    let d = Math.abs(a - h.mvA) * 180 / Math.PI; if (d > 180) d = 360 - d; const old = [Math.cos(h.mvA), Math.sin(h.mvA)];
    if (d >= TURN.small && h.mvT >= TURN.minT && h.turnCd <= 0 && !h.atk && !h.roll && !(h.jump && h.jump.air)) { const big = d >= TURN.big, run = h.run ? 1 : .6; h.turnCd = TURN.cd;
      h.lnDir = old; h.lnV = (h.lnV || 0) + LEAN.kick * (big ? TURN.leanBig : TURN.leanSmall) * run; // the body keeps going the old way for a beat (same spring as start/stop)
      if (big) { for (let i = 0; i < 3; i++) addFx('dust', h.x + old[0] * (2 + i * 4), h.y + old[1] * (1 + i * 2), { life: .32 + i * .06 }); addFx('skid', h.x, h.y, { life: .45, dx: old[0], dy: old[1] }); sfx('roll', .35);
        if (h128()) { S.trail = S.trail || []; S.trail.push({ c128: h128Cell(), x: h.x - old[0] * 1.5, y: h.y - old[1] * 1.5, t: 0, life: TURN.ghostLife, a: TURN.ghost * run }); } } // cape/hair lag: one faint copy of the old pose
      else addFx('dust', h.x + old[0] * 2, h.y, { life: .22 }); h.mvT = 0; }
    h.mvA = a; h.mvT += dt; }
  function h8Lean(h) { const now = S.t, sp = h.moving && !h.roll ? (h.run ? RUN.mul : 1) : 0; let dt = Math.min(.1, Math.max(0, now - (h.lnT ?? now))); h.lnT = now;
    if (h.lnSp == null) h.lnSp = sp; const dv = sp - h.lnSp; h.lnSp = sp; if (h.roll || S.deadT > 0) { h.lnL = h.lnV = 0; return null; }
    if (dv) { if (h.moving) h.lnDir = FACEV[h.face] || [1, 0]; h.lnV = (h.lnV || 0) + dv * LEAN.kick; }
    for (; dt > 1e-6; dt -= 1 / 120) { const d = Math.min(dt, 1 / 120); h.lnV += (-LEAN.w * LEAN.w * (h.lnL || 0) - 2 * LEAN.z * LEAN.w * h.lnV) * d; h.lnL = (h.lnL || 0) + h.lnV * d; }
    const L = Math.max(-LEAN.max, Math.min(LEAN.max, h.lnL || 0)); return Math.abs(L) < .05 ? null : { L, v: h.lnDir || FACEV[h.face] || [1, 0] }; }
  function drawHeroHi(k) { if (!h128() || !S.map || S.map.type === 'world') return; const h = hero;
    if (S.trail) for (const a of S.trail) if (a.c128) { const q = 1 - a.t / a.life; drawH128(a.c128, a.x, a.y, k, q * q * a.a, null); } // 잔상 = 주인공 모습 그대로 (색 덮기 없음)
    if (h.inv > 0 && Math.floor(h.inv * 20) % 2 && !h.roll && S.deadT <= 0 && !S.ultFx) return; // no blink / white wash during an ultimate (the hero is the star of the shot)
    let kx = 0, ky = 0, sq = 1, lean = 0; if (h.atk && !SLASH_BODY) { const K = gkKick(h.atk), v = FACEV[h.face] || [1, 0], f = H128FIG / 117; kx = v[0] * K.step * f; ky = v[1] * K.step * f * .5; sq = K.sq; lean = v[0] * K.lean * f * k; if (v[1]) sq *= 1 - v[1] * K.lean * .006; } // side: shear (head leans, feet stay); up/down: lean shows as a slight squash/stretch
    { const LN = h8Lean(h); if (LN) { const f = H128FIG / 117; lean += LN.v[0] * LN.L * f * k; if (LN.v[1]) sq *= 1 - Math.abs(LN.v[1]) * LN.L * .006; } } // start / stop weight (motion lab 10-23)
    ky -= h.z || 0; const [fx, fy] = W2S(h.x + kx, h.y + ky); ctx.save(); ctx.translate(fx, fy); ctx.scale(1 + (1 - sq) * .6, sq); if (lean) ctx.transform(1, 0, -lean / (H128FIG * k), 1, 0, 0); ctx.translate(-fx, -fy);
    drawH128(h128Cell(), h.x + kx, h.y + ky, k, 1, null); if (h.inv > .8 && !h.roll && !S.ultFx) drawH128(h128Cell(), h.x + kx, h.y + ky, k, .5, 'white'); ctx.restore();
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
    { const zs = 1 - Math.min(.45, (h.z || 0) / 36); g.fillStyle = `rgba(0,0,0,${.28 * zs})`; g.beginPath(); g.ellipse(h.x, h.y, (6 * zoom + 1) * zs, (2.5 * zoom + .5) * zs, 0, 0, TAU); g.fill(); } // jump: the shadow stays on the ground and shrinks
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
  const FELTIMG = {}; function feltImg(src) { if (!FELTIMG[src]) { const im = new Image(); im.src = V(src + '.png'); FELTIMG[src] = im; } return FELTIMG[src]; }
  function feltFrame(m) { const a = m.D.anim[m.anim || 'walk'], i = feltFrame0(m); return a && a.map ? a.map[i] : i; } // optional frame remap per strip
  function feltFrame0(m) { const A = m.D.anim, a = A[m.anim || 'walk'];
    if (a && a.once) { let t = m.at; for (let i = 0; i < a.n; i++) { t -= a.ticks[i] / 60; if (t < 0) return i; } return a.n - 1; } // one-shot strip (hurt)
    if (a && a.loop) { const T = a.ticks.reduce((x, v) => x + v, 0) / 60; let t = (S.t + m.home[0]) % T, i = 0; for (; i < a.n - 1; i++) { t -= a.ticks[i] / 60; if (t < 0) break; } return i; } // looping stance (rage)
    if (a && (a.hit !== undefined || a.release !== undefined)) { const key = a.release !== undefined ? a.release : a.hit, sc = m.preT > 0 ? m.keyT / m.preT : 1; let t = m.at, i = 0;
      if (t < m.keyT) { for (; i < key; i++) { t -= a.ticks[i] / 60 * sc; if (t < 0) return i; } return key; }
      t -= m.keyT; for (i = key; i < a.n; i++) { t -= a.ticks[i] / 60 * (m.D.rec || 1); if (t < 0) return i; } return a.n - 1; }
    if (!m.moving) return 0; const i = ((Math.floor((m.wph !== undefined ? m.wph : S.t) * 60 / a.ticks[0] + m.home[0]) % a.n) + a.n) % a.n; return m.back ? a.n - 1 - i : i; } // wph = distance-based walk clock
  function drawFeltHi(k, pick) { const m = S.map; if (!m || m.type === 'world') return;
    for (const mm of S.mobs) { if (mm.dead || !pick(mm)) continue; if (mm.D.s47) { drawS47(mm, k); continue; } if (!mm.D.felt) continue; const A = mm.D.anim, name = mm.anim || 'walk', wd = name === 'walk' && mm.wdir && mm.wdir !== 'side' ? mm.wdir : '', im = feltImg(A.src + '_' + name + (wd ? '_' + wd : '')); if (!im.complete || !im.naturalWidth) continue;
      const sc = (mm.scale || 1) * (mm.spawnT > 0 ? Math.max(0, 1 - mm.spawnT * 1.8) : 1); if (sc <= 0) continue;
      const f = feltFrame(mm), idle = name === 'walk' && !mm.moving, sz = A.F * k * sc, P = mm.D.style, ph = S.t + mm.home[0];
      // body language (code, owner 10-23 "생동감"): wind-up squash + shiver before the hit, stretch on release, squash when hit, hop on first sight, per-mob idle habit
      const atkA = !!A[name] && (A[name].hit !== undefined || A[name].release !== undefined), tele = atkA && mm.at < mm.keyT, q = tele ? mm.at / mm.keyT : 0; let bx = 1, by = 1, ox = 0, oy = 0, rot = 0;
      if (tele) { bx = 1 + .1 * q; by = 1 - .12 * q; if (q > .7) ox = (Math.random() - .5) * 2 * k; } else if (atkA && mm.at < mm.keyT + .1) { bx = .92; by = 1.1; }
      if (mm.hitT > .18) { bx *= 1.12; by *= .88; }
      if (mm.alertT > 0) oy = -Math.sin(Math.PI * (1 - mm.alertT / .45)) * 6 * k;
      if (idle && !tele) { if (P === 'duel') rot = Math.sin(ph * 2.6) * .05; else if (P === 'skirm') ox += (Math.floor(ph * 3) % 4 === 0 ? 1 : 0) * k * .6; else if (P === 'lunge') { by *= 1 + .03 * Math.sin(ph * 7); rot = Math.sin(ph * .9) > .8 ? .04 : 0; } else by *= 1 + .02 * Math.sin(ph * 4); }
      const [x, y] = W2S(mm.x + (mm.shake ? (Math.random() - .5) * 2 : 0), mm.y);
      if (tele || mm.rage) { ctx.save(); ctx.globalAlpha = tele ? .15 + .35 * q : .12 + .08 * Math.sin(S.t * 8); ctx.fillStyle = '#ff3c28'; ctx.beginPath(); ctx.ellipse(Math.round(x), Math.round(y), sz * .28, sz * .09, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore(); } // red ground glow = "about to strike" / angry
      ctx.save(); ctx.translate(Math.round(x + ox), Math.round(y + oy)); if (mm.face < 0 && wd !== 's' && wd !== 'n') ctx.scale(-1, 1); if (rot) ctx.rotate(rot); ctx.scale(bx, by);
      if (mm.flash > 0) ctx.filter = 'brightness(3)'; else if (mm.D.tint) ctx.filter = mm.D.tint; // champions: recoloured felt art
      blitFrame(im, f, 256, 256, sz / 256, Math.round(-sz / 2), Math.round(-sz * 250 / 256)); ctx.restore(); } }
  // ---- companion Linette (owner 10-22 "전캐릭 인게임"): follows the hero in 바람길 (field00) and thrusts at nearby mobs.
  // Atlas assets/anim/linette8.json (hero8 format, 117px figure = hero scale); thrust tip/dir from A.thrust, trail drawn in code.
  const PET = { A: null, IM: [] }; getJSON('assets/anim/linette8.json').then(j => { PET.A = j; PET.IM = j.sheets.map(p => { const i = new Image(); i.src = 'assets/' + p + '?v=' + BUILD_V; return i; }); }).catch(() => {});
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
    if (P.moving) P.gp = ((P.gp || 0) + Math.hypot(mx, my) / (P.run ? 32.8 : 23.4)) % 1; } // one cycle per field px = Linette's drawn stride (walk 1.9 / run 4.0 art px per tick x clip ticks x 30/117): feet stay planted (motion lab 10-23; was 46/32 = ~1.4x foot slide)
  function drawPetHi(k, front) { const P = S.pet; if (!P || !PET.A || P.map !== S.map || (P.y > hero.y) !== front) return; const A = PET.A, a = P.atk;
    const an = a ? a.clip : P.moving ? (P.run ? 'run' : 'walk') : 'idle', L = A.anims[an + '_' + (a ? a.dir : P.dir)] || A.anims[an + '_right']; if (!L) return;
    let e; if (a) { let t = a.t, i = 0; for (; i < L.length - 1; i++) { if (t < L[i][2]) break; t -= L[i][2]; } e = L[i]; } else if (P.moving) { let t = ((P.gp || 0) % 1) * petTot(L), i = 0; for (; i < L.length - 1; i++) { if (t < L[i][2]) break; t -= L[i][2]; } e = L[i]; } /* walk/run frames have their own ticks (longer where the foot travels further) */ else { let t = (S.t * 60) % petTot(L), i = 0; for (; i < L.length - 1; i++) { if (t < L[i][2]) break; t -= L[i][2]; } e = L[i]; }
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
  const S47IMG = {}; function s47Img(id, k) { const key = id + '_' + k; if (!S47IMG[key]) { const im = new Image(); im.src = V('assets/mobs47/' + key + '.webp'); S47IMG[key] = im; } return S47IMG[key]; }
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
  function hazMute(r, g, b) { const y = .3 * r + .59 * g + .11 * b; return [Math.round(r * .78 + y * .22), Math.round(g * .78 + y * .22), Math.round(b * .78 + y * .22)]; } // 채도 낮춘 예고색
  function hazColor(h) { return ({ web: [225, 225, 240], poison: [170, 80, 255], root: [120, 220, 80], crystal: [90, 255, 160], cage: [90, 255, 160], summon: [255, 220, 60], acorn: [255, 160, 60] })[h.kind] || [255, 60, 50]; }

  // ---- 실 효과 (보스전 팀 10-24, 공격 검흔 담당; 이펙트는 코드로): 1장 펠트(실) 몹·아라크네의 겨냥 실 / 실 감옥 실 가닥 / 끊어질 때 파편 /
  // 2페이즈 붉은 실 맥박 / 주인공 검기가 실 몹을 벨 때 튀는 실. Drawn after the dungeon darkness (emissive) so the warnings read in the dark boss room.
  const THR = { core: [236, 232, 248], glow: [150, 135, 215], rcore: [255, 214, 216], rglow: [205, 18, 40] };
  function threadRed() { for (const m of S.mobs) if (!m.dead && m.D.boss && m.D.felt && m.phase === 2) return true; return false; }
  function heartbeat() { const c = S.t % 1.1, b = (u, w) => Math.exp(-(u * u) / (w * w)); return Math.min(1, b(c, .07) + .7 * b(c - .24, .07)); } // lub-dub, 1.1 s
  function thrCol(red, part, a) { const c = red ? (part ? THR.rglow : THR.rcore) : (part ? THR.glow : THR.core); return `rgba(${c[0]},${c[1]},${c[2]},${Math.max(0, Math.min(1, a))})`; }
  function isThreadHaz(h) { return h.shape === 'line' && h.t < h.warn && h.owner && h.owner.D && h.owner.D.felt; }
  function threadLine(g, x0, y0, x1, y1, amp, ph, red, al, w) { const L = Math.hypot(x1 - x0, y1 - y0), n = Math.max(2, Math.ceil(L / 3)), nx = -(y1 - y0) / (L || 1), ny = (x1 - x0) / (L || 1);
    g.beginPath(); for (let i = 0; i <= n; i++) { const u = i / n, o = Math.sin(u * Math.PI) * Math.sin(u * 9 + ph) * amp; const x = x0 + (x1 - x0) * u + nx * o, y = y0 + (y1 - y0) * u + ny * o; i ? g.lineTo(x, y) : g.moveTo(x, y); }
    g.strokeStyle = `rgba(6,4,12,${Math.min(1, al) * .6})`; g.lineWidth = w + 4; g.stroke(); /* dark rim: reads on any floor (검흔 연구와 같은 수) */
    g.strokeStyle = thrCol(red, 1, al * .7); g.lineWidth = w + 2; g.stroke(); g.strokeStyle = thrCol(red, 0, al); g.lineWidth = w; g.stroke(); }
  function drawThreadGlow(g) { const red = threadRed(), hb = red ? heartbeat() : 0; g.save(); g.lineCap = 'round';
    for (const h of S.hazards) { if (!isThreadHaz(h)) continue; const p = Math.min(1, h.t / (h.warn || 1e-3)), pluck = h.warn - h.t < .1; // aimed thread: slack + trembling -> pulled taut on the beat
      threadLine(g, h.x, h.y - 2, h.x2, h.y2, 3.5 * Math.pow(1 - p, 1.5), S.t * 40, red, (pluck ? 1 : .45 + .45 * p) + hb * .3, pluck ? 2 : 1);
      const bx = h.x + (h.x2 - h.x) * p, by = h.y + (h.y2 - h.y) * p; g.fillStyle = thrCol(red, 0, .9); g.fillRect(Math.round(bx) - 1, Math.round(by) - 1, 3, 3); } // a bead runs up the thread = the countdown
    const posts = S.temp.filter(t => t.kind === 'thread'); // 실 감옥: glowing strands between neighbouring posts (the gap has none)
    for (let i = 0; i < posts.length; i++) for (let j = i + 1; j < posts.length; j++) { const A = posts[i], B = posts[j], d = Math.hypot(A.x - B.x, A.y - B.y); if (d > 34) continue;
      const al = Math.min(1, Math.min(A.life, B.life) * 3) * (.75 + .15 * Math.sin(S.t * 7 + A.x) + hb * .3);
      threadLine(g, A.x, A.y - 18, B.x, B.y - 18, 1.2, S.t * 6 + A.x, red, al, 1); threadLine(g, A.x, A.y - 8, B.x, B.y - 8, 1, S.t * 5 + B.y, red, al * .8, 1); }
    if (red) for (const h of S.hazards) { if (!h.dmg || h.t >= h.warn || h.shape === 'all') continue; // 팀장 10-24: phase 2 reddens the room -> every damaging warning gets a dark rim + pale-gold edge, and the inside flickers white on the last third
      const p = h.t / (h.warn || 1e-3), fl = p > .66 && Math.floor(S.t * 12) % 2 === 0, path = () => { g.beginPath(); if (h.shape === 'line') { const L = Math.hypot(h.x2 - h.x, h.y2 - h.y), ux = (h.x2 - h.x) / (L || 1), uy = (h.y2 - h.y) / (L || 1), w = h.width / 2;
          g.moveTo(h.x - uy * w, h.y + ux * w); g.lineTo(h.x2 - uy * w, h.y2 + ux * w); g.lineTo(h.x2 + uy * w, h.y2 - ux * w); g.lineTo(h.x + uy * w, h.y - ux * w); g.closePath(); } else { g.ellipse(h.x, h.y, h.r, h.r / 1.15, 0, 0, TAU); if (h.shape === 'ring' && h.r0 > 0) { g.moveTo(h.x + h.r0, h.y); g.ellipse(h.x, h.y, h.r0, h.r0 / 1.15, 0, 0, TAU, true); } } };
      path(); if (fl) { g.fillStyle = 'rgba(255,248,225,.3)'; g.fill('evenodd'); }
      g.strokeStyle = 'rgba(8,2,6,.55)'; g.lineWidth = 4; g.stroke(); g.strokeStyle = `rgba(255,240,190,${.9 + .1 * hb})`; g.lineWidth = 2; g.stroke(); }
    if (red) for (const m of S.mobs) { if (m.dead || !m.D.boss || !m.D.felt) continue; // phase 2: red threads hang from the dark above her and throb
      for (let k = 0; k < 6; k++) { const ox = (k - 2.5) * 9, sw = Math.sin(S.t * 1.7 + k * 1.3) * 4; threadLine(g, m.x + ox, m.y - 34, m.x + ox * 1.8 + sw, m.y - 150, 1.5, S.t * 3 + k, true, .25 + .55 * hb, 1); }
      g.fillStyle = thrCol(true, 1, .10 + .22 * hb); g.beginPath(); g.ellipse(m.x, m.y, 30 + hb * 6, 12 + hb * 2, 0, 0, TAU); g.fill(); }
    g.restore(); }
  function threadSpray(ctx, m, al) { const red = threadRed(); let sd = m.seed || 1; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647, n = m.big ? 9 : 5, t = m.t; // cut threads fly off the hit
    ctx.lineCap = 'round'; for (let i = 0; i < n; i++) { const b = m.a + (rnd() - .5) * 1.6, sp = 4 + rnd() * 4, L = 10 + rnd() * 14, r0 = t * sp, cv = (rnd() - .5) * 1.4, fall = t * t * .25;
      const x0 = Math.cos(b) * r0, y0 = Math.sin(b) * r0 + fall, x1 = Math.cos(b + cv) * (r0 + L), y1 = Math.sin(b + cv) * (r0 + L) + fall * 1.3;
      ctx.strokeStyle = thrCol(red, 1, al * .6); ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.quadraticCurveTo((x0 + x1) / 2 + cv * 6, (y0 + y1) / 2, x1, y1); ctx.stroke();
      ctx.strokeStyle = thrCol(red, 0, al); ctx.lineWidth = 1.2; ctx.stroke(); }
    if (m.big && t < 6) { ctx.fillStyle = `rgba(255,236,190,${1 - t / 6})`; for (let i = 0; i < 10; i++) { const b = m.a + (rnd() - .5) * 2.4, r = t * (6 + rnd() * 6); ctx.fillRect(Math.round(Math.cos(b) * r) - 1, Math.round(Math.sin(b) * r) - 1, 3, 3); } } } // 3타: sparks
  function drawHazard(g, h, top) {
    if (h.shape === 'all') return;
    const [r, gg, b] = hazColor(h), warnP = Math.min(1, h.t / (h.warn || 1e-3)), live = h.t >= h.warn && h.t < h.warn + (h.act || 0);
    if (!top && h.t < h.warn) { // telegraph (사장님 10-24 「촌스럽다, 깔끔하게」): faint fill + 1px dark rim + thin muted outline; a fill sweeps from the centre (circle) /
      // the inner edge (ring) / the back (line) and reaches the outline on the hit = the time left; the outline flickers only in the last 0.15 s
      const pulse = .5 + .5 * Math.sin(h.t * 22), [cr, cg, cb] = hazMute(r, gg, b), left = h.warn - h.t, flick = left < .15 && Math.floor(h.t * 30) % 2 === 0, e = 1 - Math.pow(1 - warnP, 1.6);
      const path = (k0, k1) => { g.beginPath(); if (h.shape === 'line') { const L = Math.hypot(h.x2 - h.x, h.y2 - h.y), ux = (h.x2 - h.x) / (L || 1), uy = (h.y2 - h.y) / (L || 1), w = h.width / 2, a0 = L * k0, a1 = L * k1;
          g.moveTo(h.x + ux * a0 - uy * w, h.y + uy * a0 + ux * w); g.lineTo(h.x + ux * a1 - uy * w, h.y + uy * a1 + ux * w); g.lineTo(h.x + ux * a1 + uy * w, h.y + uy * a1 - ux * w); g.lineTo(h.x + ux * a0 + uy * w, h.y + uy * a0 - ux * w); g.closePath(); }
        else { const r0 = h.shape === 'ring' ? (h.r0 || 0) : 0, ra = r0 + (h.r - r0) * k0, rb = r0 + (h.r - r0) * k1; g.ellipse(h.x, h.y, rb, rb / 1.15, 0, 0, TAU); if (ra > .5) { g.moveTo(h.x + ra, h.y); g.ellipse(h.x, h.y, ra, ra / 1.15, 0, 0, TAU, true); } } }; // moveTo: no seam line between the two edges
      if (h.shape === 'circle' || h.shape === 'ring' || h.shape === 'line') {
        path(0, 1); g.fillStyle = `rgba(${cr},${cg},${cb},.06)`; g.fill('evenodd'); // the whole area, barely there
        path(0, e); g.fillStyle = `rgba(${cr},${cg},${cb},${.1 + .08 * warnP})`; g.fill('evenodd'); // the sweep = the countdown
        path(Math.max(0, e - .06), e); g.fillStyle = `rgba(${Math.min(255, cr + 50)},${Math.min(255, cg + 50)},${Math.min(255, cb + 50)},.7)`; g.fill('evenodd'); // its leading edge
        path(0, 1); g.strokeStyle = 'rgba(8,4,6,.55)'; g.lineWidth = 3; g.stroke(); g.strokeStyle = flick ? 'rgba(255,246,236,.95)' : `rgba(${cr},${cg},${cb},.85)`; g.lineWidth = 1; g.stroke(); }
      if (h.kind === 'acorn' && h.from) { const p = warnP, x = h.from[0] + (h.x - h.from[0]) * p, y = h.from[1] + (h.y - h.from[1]) * p - Math.sin(p * Math.PI) * 30; g.fillStyle = '#8a5a2a'; g.beginPath(); g.arc(x, y, 2.5, 0, TAU); g.fill(); }
      if (h.kind === 'rock') { const p = warnP; g.fillStyle = 'rgba(0,0,0,.3)'; g.beginPath(); g.ellipse(h.x, h.y, h.r * p, h.r * p / 1.6, 0, 0, TAU); g.fill(); if (p > .6) { g.fillStyle = '#7a7060'; g.fillRect(h.x - 4, h.y - (1 - p) * 120 - 8, 8, 7); } }
      if (h.kind === 'cage') { g.globalAlpha = .35 + .3 * pulse; drawSpr(g, 'crystal', h.x, h.y + 5); g.globalAlpha = 1; }
    }
    if (top && live) {
      const [mr, mg, mb] = hazMute(r, gg, b); g.fillStyle = `rgba(${Math.min(255, mr + 90)},${Math.min(255, mg + 90)},${Math.min(255, mb + 90)},.5)`; // the hit: one short bright flash of the area
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
    if (f.type === 'voidpop') { const q = fxQ(), R = (f.big ? 20 : 10) * (.3 + p); for (let i = 0; i < 12; i++) { const a = i / 12 * TAU + f.x, r = R * (.6 + .4 * hash(i + f.y)); abPx(g, f.x + Math.cos(a) * r, f.y + Math.sin(a) * r * .7, i % 3 ? 1 : 2, i % 2 ? AB_PAL.lit : AB_PAL.void, 1 - p, q); } abEll(g, f.x, f.y, 4 * (1 - p), 3 * (1 - p), AB_PAL.core, 1 - p, q); g.globalAlpha = 1; return; }
    if (f.type === 'scorch') { const q = fxQ(), a = 1 - p; abEll(g, f.x, f.y, 10, 4, AB_PAL.void, a * .9, q); abEll(g, f.x, f.y, 6, 2, AB_PAL.deep, a, q); for (let i = 0; i < 4; i++) { const ph = (p * 2 + i / 4) % 1; abPx(g, f.x + (hash(i + f.x) - .5) * 14, f.y - ph * 18, 1, i % 2 ? AB_PAL.lit : AB_PAL.vio, a * (1 - ph), q); } g.globalAlpha = 1; return; } // 그을린 자국 + 올라가는 불티
    if (f.type === 'spark') { g.fillStyle = `rgba(255,255,220,${1 - p})`; for (let i = 0; i < 4; i++) { const a = i * 1.57 + .7; g.fillRect(f.x + Math.cos(a) * p * 8 - 1, f.y + Math.sin(a) * p * 8 - 1, 2, 2); } }
    if (f.type === 'poof') { g.fillStyle = `rgba(240,240,255,${.8 * (1 - p)})`; const R = (f.big ? 22 : 9) * (0.4 + p); for (let i = 0; i < 6; i++) { const a = i * TAU / 6; g.beginPath(); g.arc(f.x + Math.cos(a) * R, f.y + Math.sin(a) * R * .6, 3 * (1 - p) + 1, 0, TAU); g.fill(); } }
    if (f.type === 'skid') { const a = (1 - p) * .55; g.fillStyle = `rgba(70,52,36,${a})`; for (const o of [-2, 2]) for (let i = 0; i < 9; i++) g.fillRect(Math.round(f.x - f.dy * o - f.dx * i * 1.2), Math.round(f.y + f.dx * o * .6 - f.dy * i * .8), 1, 1); return; } // 미끄러진 자국
    if (f.type === 'dust') { g.fillStyle = `rgba(200,180,140,${.6 * (1 - p)})`; for (let i = 0; i < 3; i++) { g.beginPath(); g.arc(f.x + (i - 1) * 5 * (1 + p), f.y - p * 4, 2 + p * 2, 0, TAU); g.fill(); } }
    if (f.type === 'debris') { g.fillStyle = `rgba(130,120,100,${1 - p})`; for (let i = 0; i < 6; i++) { const a = i * 1.05; g.fillRect(f.x + Math.cos(a) * p * 14, f.y + Math.sin(a) * p * 8 - Math.sin(p * 3) * 6, 3, 3); } }
    if (f.type === 'crystal') { g.globalAlpha = Math.max(0, 1 - p); drawSpr(g, 'crystal', f.x, f.y + 4, { scale: .6 + p * .3, alpha: Math.max(0, 1 - p) }); g.globalAlpha = 1; }
    if (f.type === 'heal') { g.fillStyle = `rgba(120,255,140,${1 - p})`; g.fillRect(f.x - 1, f.y - p * 14 - 3, 2, 6); g.fillRect(f.x - 3, f.y - p * 14 - 1, 6, 2); }
    if (f.type === 'stars') { g.fillStyle = '#ffe060'; for (let i = 0; i < 3; i++) { const a = S.t * 6 + i * 2.1; g.fillRect(f.x + Math.cos(a) * 6, f.y + Math.sin(a) * 2, 2, 2); } }
    if (f.type === 'sparkle') { g.fillStyle = `rgba(255,250,180,${1 - p})`; for (let i = 0; i < 5; i++) { const a = i * 1.26 + p; g.fillRect(f.x + Math.cos(a) * p * 12, f.y + Math.sin(a) * p * 12 - p * 6, 2, 2); } }
    if (f.type === 'tring') { g.strokeStyle = 'rgba(225,228,240,.75)'; g.lineWidth = 1; for (const dy of [-12, -6]) { g.beginPath(); g.ellipse(f.x, f.y + dy, f.R, f.R * .8, 0, f.gap + f.gw / 2, f.gap - f.gw / 2 + TAU); g.stroke(); } } // 실 감옥: two strands of steel thread between the posts
    if (f.type === 'cocoonfall') { const k = Math.min(1, f.t / f.warn), x = Math.round(f.x), y = Math.round(f.y); // 고치 비: shadow grows, the cocoon drops in the last 40 %
      g.fillStyle = `rgba(0,0,0,${.15 + .35 * k})`; g.beginPath(); g.ellipse(x, y + 2, 4 + 10 * k, 2 + 4 * k, 0, 0, TAU); g.fill();
      const q = Math.max(0, (k - .6) / .4), sx = f.fx !== undefined ? Math.round(f.fx + (x - f.fx) * q) : x, cy = (f.fy !== undefined ? f.fy - 30 + (y - f.fy + 30) * q * q : y - 140 * (1 - q * q)); if (k > .6) { const x = sx; // from the ceiling cocoon (3번방) toward the marked spot g.fillStyle = '#e8e2d4'; g.beginPath(); g.ellipse(x, cy - 8, 5, 9, 0, 0, TAU); g.fill(); g.strokeStyle = 'rgba(120,110,100,.8)'; g.lineWidth = 1;
        for (let i = -1; i <= 1; i++) { g.beginPath(); g.moveTo(x - 5, cy - 8 + i * 4); g.lineTo(x + 5, cy - 6 + i * 4); g.stroke(); } g.strokeStyle = 'rgba(230,230,240,.5)'; g.beginPath(); g.moveTo(x, cy - 17); g.lineTo(x, cy - 60); g.stroke(); } }
    if (f.type === 'unravel') { const n = f.n || 20; g.lineWidth = 1; for (let i = 0; i < n; i++) { const a = i * 2.39996, L = 10 + p * (40 + (i * 37 % 30)), w = Math.sin(p * 6 + i) * 6; // boss death: her threads come loose and fly out
        g.strokeStyle = `rgba(${i % 3 ? '220,220,235' : '160,40,40'},${Math.max(0, 1 - p)})`; g.beginPath(); g.moveTo(f.x, f.y); g.quadraticCurveTo(f.x + Math.cos(a) * L * .5 - Math.sin(a) * w, f.y + Math.sin(a) * L * .4 + Math.cos(a) * w, f.x + Math.cos(a) * L, f.y + Math.sin(a) * L * .7 + p * 20); g.stroke(); } }
    if (f.type === 'strip') { const im = feltImg(f.src); let t = f.t, i = 0; for (; i < f.ticks.length - 1; i++) { t -= f.ticks[i] / 60; if (t < 0) break; } // a one-shot body strip left in the world (boss death: legs fold, she slumps)
      if (im.complete && im.naturalWidth) { g.save(); g.globalAlpha = Math.max(0, Math.min(1, (f.life - f.t) * 1.5)); g.translate(Math.round(f.x), Math.round(f.y)); if (f.face < 0) g.scale(-1, 1); g.drawImage(im, i * 256, 0, 256, 256, -f.F / 2, -f.F * 250 / 256, f.F, f.F); g.restore(); } }
    if (f.type === 'tsnap') { let sd = f.seed || 1; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647; g.save(); g.lineCap = 'round'; // 실 감옥 post snaps: short thread shards whip out and drop
      for (let i = 0; i < 8; i++) { const b = rnd() * TAU, v = 30 + rnd() * 40, x = f.x + Math.cos(b) * v * f.t, y = f.y + Math.sin(b) * v * .7 * f.t + 60 * f.t * f.t, L = 3 + rnd() * 4, r = b + f.t * (rnd() * 20 - 10);
        g.strokeStyle = thrCol(f.red, 0, 1 - p); g.lineWidth = 1; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(r) * L, y + Math.sin(r) * L); g.stroke(); }
      if (f.t < .08) { g.fillStyle = thrCol(f.red, 0, 1); g.fillRect(Math.round(f.x) - 2, Math.round(f.y) - 2, 5, 5); } g.restore(); return; }
    if (f.type === 'tclone') { const tt = f.t, k = tt < f.warn ? 0 : Math.min(1, (tt - f.warn) / f.dash), x = f.x + (f.x1 - f.x) * k, y = f.y + (f.y1 - f.y) * k, im = feltImg(f.src + '_attack'); // 실 분신: pale thread copy of the boss, dashes on the beat
      if (im.complete && im.naturalWidth) { g.save(); g.globalAlpha = Math.max(0, Math.min(.85, tt * 3, (f.life - tt) * 3)); g.filter = 'grayscale(1) brightness(1.5) contrast(1.3)'; g.translate(Math.round(x), Math.round(y)); if (f.face < 0) g.scale(-1, 1);
        g.drawImage(im, (tt < f.warn ? 2 : 6) * 256, 0, 256, 256, -f.F / 2, -f.F * 250 / 256, f.F, f.F); g.restore(); } }
    if (f.type === 'fluff') { const n = f.n || 12; for (let i = 0; i < n; i++) { const a = i * 2.39996 + (f.x % 7), sp = 10 + (i * 37 % 13), x = f.x + Math.cos(a) * sp * p * 1.6, y = f.y + Math.sin(a) * sp * p * .9 - Math.sin(Math.min(1, p * 1.6) * Math.PI) * 10 + p * p * 8; // felt fluff + thread bits
        g.globalAlpha = Math.max(0, 1 - p * p); g.fillStyle = i % 3 === 0 ? '#f2ede2' : (f.col || '#b0a890'); if (i % 4 === 1) g.fillRect(x, y, 4, 1); else g.fillRect(x - 1, y - 1, 3, 3); } g.globalAlpha = 1; }
    if (f.type === 'claw') { g.save(); g.translate(f.x, f.y); g.rotate(f.a + Math.PI / 2); const R = (f.r || 12) * 1.1, L = Math.min(1, p * 3); g.globalAlpha = Math.max(0, 1 - p); g.lineWidth = 2; // 3 curved scratches sweeping across the strike circle
        for (let i = -1; i <= 1; i++) { g.strokeStyle = i ? '#ff6a50' : '#fff4e8'; g.beginPath(); g.arc(i * 5, R * .9, R, -Math.PI / 2 - .9, -Math.PI / 2 - .9 + 1.8 * L); g.stroke(); } g.restore(); g.globalAlpha = 1; }
    if (f.type === 'bite') { const c = Math.min(1, p * 4), o = (1 - c) * 7; g.globalAlpha = Math.max(0, 1 - p); g.strokeStyle = '#fff'; g.lineWidth = 2; // jaws snapping shut
      g.beginPath(); g.arc(f.x, f.y - o, 7, Math.PI * .15, Math.PI * .85); g.stroke(); g.beginPath(); g.arc(f.x, f.y + o, 7, Math.PI * 1.15, Math.PI * 1.85); g.stroke(); g.globalAlpha = 1; }
    if (f.type === 'muzzle') { g.fillStyle = `rgba(255,240,210,${1 - p})`; for (let i = -1; i <= 1; i++) { const a = f.a + i * .5, d = 3 + p * 7; g.fillRect(f.x + Math.cos(a) * d - 1, f.y + Math.sin(a) * d - 1, 2, 2); } }
    if (f.type === 'justring') { g.strokeStyle = `rgba(150,235,255,${1 - p})`; g.lineWidth = 2; g.beginPath(); g.ellipse(f.x, f.y, 6 + p * 26, (6 + p * 26) * .7, 0, 0, TAU); g.stroke(); }
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
  function W2S(x, y) { const v = S.view, f = S.camF || [0, 0]; return [v.ox + (x - S.camI[0] - Math.round(f[0] * v.k) / v.k) * v.k, v.oy + (y - S.camI[1] - Math.round(f[1] * v.k) / v.k) * v.k]; } // same screen-pixel shift as the ground
  function font(px) { return 'bold ' + Math.max(8, Math.round(px)) + 'px "Malgun Gothic","Apple SD Gothic Neo","Noto Sans CJK KR",sans-serif'; }
  function textOut(t, x, y, px, fill, stroke = '#000', align = 'center') { ctx.font = font(px); ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.lineJoin = 'round'; ctx.lineWidth = Math.max(2, px / 5); ctx.strokeStyle = stroke; ctx.strokeText(t, x, y); ctx.fillStyle = fill; ctx.fillText(t, x, y); }
  function panel(x, y, w, h) { ctx.fillStyle = 'rgba(12,18,44,.78)'; ctx.fillRect(x, y, w, h); ctx.strokeStyle = '#e2c27a'; ctx.lineWidth = 2; ctx.strokeRect(x + 1, y + 1, w - 2, h - 2); ctx.strokeStyle = 'rgba(226,194,122,.4)'; ctx.lineWidth = 1; ctx.strokeRect(x + 5, y + 5, w - 10, h - 10); }
  function dlgBust(d, x, y, sz) { // portrait = the NPC's own in-game pixel sprite, head + shoulders, nearest-scaled (0 credits, always matches the map)
    const A = d.anim && npcAnim(d.anim); if (!A) return false; const seq = A.J.anims.idle_south || A.J.anims.idle_down; if (!seq) return false; const t = Math.floor(d.t * 60) % seq.reduce((a, q) => a + q[2], 0); let q = seq[0], acc = 0; for (const e of seq) { acc += e[2]; if (t < acc) { q = e; break; } }
    const c = A.J.cells[q[0]][q[1]], [cx, cy, cw, ch] = c, top = cy + Math.max(0, c[5] - 124), bh = 64, bw = 64, bx = cx + c[4] - 32; // head + shoulders: top 64 px of a ~124 px figure, centred on the feet anchor
    ctx.save(); ctx.beginPath(); ctx.rect(x, y, sz, sz); ctx.clip(); ctx.imageSmoothingEnabled = false; const sc = sz / bw, s0 = Math.max(cx, bx), s1 = Math.min(cx + cw, bx + bw), t1 = Math.min(cy + ch, top + bh); if (s1 > s0 && t1 > top) ctx.drawImage(A.ims[q[0]], s0, top, s1 - s0, t1 - top, Math.round(x + (s0 - bx) * sc), Math.round(y + 2 * sc), Math.round((s1 - s0) * sc), Math.round((t1 - top) * sc)); /* only this cell's pixels (atlas neighbours stay out) */ ctx.restore(); return true; }
  function drawCg(L, e, fade, ox, oy, SW, SH, d) { // story picture (CG_MEETING 결론): darken, 0.4 s fade in, 1.00 -> 1.03 push-in + 5 px drift toward the gaze over 9 s, pixel-crisp
    const im = splashImg('assets/' + L.src), k = Math.min(1, e / 9), a = Math.min(1, e / .4) * fade; ctx.save(); ctx.fillStyle = `rgba(0,0,0,${.88 * Math.min(1, e / .25) * fade})`; ctx.fillRect(ox, oy, SW, SH);
    if (im) { const sc = 1 + .03 * k, iw = SW * sc, ih = SH * sc, px = (L.dx || 0) * 5 * (SW / LW) * k; ctx.beginPath(); ctx.rect(ox, oy, SW, SH); ctx.clip(); ctx.globalAlpha = a; ctx.imageSmoothingEnabled = false; const ix = Math.round(ox + (SW - iw) / 2 + px), iy = Math.round(oy + (SH - ih) / 2); ctx.drawImage(im, ix, iy, Math.round(iw), Math.round(ih)); drawSceneFx(ctx, d || { cg: L.src, t: 0 }, e, ix, iy, iw / (im.naturalWidth || 384)); } ctx.restore(); }
  function drawCgOut(ox, oy, SW, SH) { if (!S.dialog && S.cgL) { S.cgOut = Object.assign({ until: S.t + .4, e: S.t - S.cgL.since }, S.cgL); S.cgL = null; } const O = S.cgOut; if (!O) return; const f = (O.until - S.t) / .4; if (f <= 0 || S.dialog) { S.cgOut = null; return; } drawCg(O, O.e, f, ox, oy, SW, SH); } // 0.4 s fade out after the last line

  // ---- 이야기 그림 위 효과 (CG 회의 10-24, 이펙트 담당; 코드로): 정지 그림을 살짝 살림. 그림당 1종, 1~2px, 얼굴 위 금지, 처음 0.4초 정지.
  // 좌표 = 그림 픽셀(384x216). ember = 재·불씨 떠오름, dust = 빛줄기 먼지, thread = 붉은 실 흔들림 + 쿵-쿵 맥박, snap = 그 그림 마지막 말에서 실이 팽팽해지며 번쩍.
  const SCENE_FX = {
    cg_felt_arrival: { kind: 'ember', box: [130, 95, 384, 216], n: 22 },
    cg_memory_fire: { kind: 'ember', box: [0, 70, 384, 216], n: 26, snap: { from: [151, 102], to: [[40, 165], [70, 122], [236, 92], [262, 176], [204, 212]] } },
    cg_arachne_end: { kind: 'thread', lines: [[150, 138, 122, 192], [186, 150, 232, 200], [84, 118, 40, 92], [112, 98, 96, 42], [60, 150, 34, 196]] },
    cg_linette_meet: { kind: 'dust', box: [30, 14, 196, 206], n: 24 },
    cg_arachne_past: { kind: 'dust', c: [161, 104], r: 48, n: 16, warm: true },
    cg_felix_scarf: { kind: 'dust', box: [90, 40, 300, 196], n: 12 } };
  function sceneThread(g, x0, y0, x1, y1, amp, ph, al, w) { const L = Math.hypot(x1 - x0, y1 - y0), n = Math.max(2, Math.ceil(L / 3)), nx = -(y1 - y0) / (L || 1), ny = (x1 - x0) / (L || 1); // a hair-thin red thread for the art (no dark rim: the art is already dark)
    g.beginPath(); for (let i = 0; i <= n; i++) { const u = i / n, o = Math.sin(u * Math.PI) * Math.sin(u * 7 + ph) * amp; const x = x0 + (x1 - x0) * u + nx * o, y = y0 + (y1 - y0) * u + ny * o; i ? g.lineTo(x, y) : g.moveTo(x, y); }
    g.strokeStyle = thrCol(true, 1, al * .45); g.lineWidth = w * 2.2; g.stroke(); g.strokeStyle = thrCol(true, 0, al); g.lineWidth = w; g.stroke(); }
  function drawSceneFx(g, d, e, ix, iy, s) { const name = (d.cg || '').replace(/^.*\//, '').replace(/\.\w+$/, ''), F = SCENE_FX[name]; if (!F || e < .4) return;
    const k = Math.min(1, (e - .4) / .8), t = e - .4, h = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }; // fade in after the still beat; h = fixed per-mote random
    g.save(); g.translate(ix, iy); g.scale(s, s); g.imageSmoothingEnabled = false;
    if (F.kind === 'ember') { const [x0, y0, x1, y1] = F.box, H = y1 - y0; for (let i = 0; i < F.n; i++) { const v = 5 + h(i) * 7, y = y1 - ((t * v + h(i + 9) * H) % H), x = x0 + h(i + 3) * (x1 - x0) + Math.sin(t * .7 + i) * 2, life = (y1 - y) / H, fl = .55 + .45 * Math.sin(t * 5 + i * 2.3);
        g.fillStyle = `rgba(255,${120 + (h(i + 5) * 70 | 0)},${50 + (h(i + 7) * 30 | 0)},${k * fl * Math.min(1, life * 4) * (1 - life * .7)})`; g.fillRect(Math.round(x), Math.round(y), 1, 1); } }
    if (F.kind === 'dust') { for (let i = 0; i < F.n; i++) { let x, y; if (F.c) { const a = h(i) * TAU + t * .08 * (h(i + 2) - .5), r = F.r * Math.sqrt(h(i + 4)); x = F.c[0] + Math.cos(a) * r; y = F.c[1] + Math.sin(a) * r * .8 - ((t * 1.5 + h(i + 6) * 10) % 10); }
        else { const [x0, y0, x1, y1] = F.box; x = x0 + ((h(i) * (x1 - x0) + t * (1.2 + h(i + 1) * 1.5)) % (x1 - x0)); y = y0 + ((h(i + 2) * (y1 - y0) + t * (2 + h(i + 3) * 2)) % (y1 - y0)); x += Math.sin(t * .5 + i) * 1.5; }
        const tw = .35 + .35 * Math.sin(t * 1.3 + i * 1.7); g.fillStyle = F.warm ? `rgba(255,214,150,${k * tw})` : `rgba(220,214,200,${k * tw * .8})`; g.fillRect(Math.round(x), Math.round(y), 1, 1); } }
    if (F.kind === 'thread') { const c = e % 1.1, b = (u, w) => Math.exp(-(u * u) / (w * w)), hb = Math.min(1, b(c, .07) + .7 * b(c - .24, .07)); g.lineCap = 'round'; // same lub-dub as the phase-2 threads
      F.lines.forEach((L, i) => sceneThread(g, L[0], L[1], L[2], L[3], 1.5, t * 1.2 + i, k * (.35 + .5 * hb), .6)); }
    if (F.snap && d.cgLast && d.t > .3) { const u = Math.min(1, (d.t - .3) / .25), [fx, fy] = F.snap.from; g.lineCap = 'round'; // the memory's last line: the threads in her chest pull taut and flash
      for (const [tx, ty] of F.snap.to) sceneThread(g, fx, fy, tx, ty, 4 * (1 - u), t * 30, .45 + .45 * u, .6);
      const fl = d.t - .55; if (fl > 0 && fl < .35) { const a2 = 1 - fl / .35; g.fillStyle = `rgba(255,236,236,${a2})`; g.beginPath(); g.arc(fx, fy, 3 + fl * 20, 0, TAU); g.fill(); g.fillStyle = `rgba(255,40,60,${a2 * .18})`; g.fillRect(0, 0, 384, 216); } }
    g.restore(); }
  function drawDialog(ox, oy, SW, SH, u) { const d0 = S.dialog, ts = (window.__game && window.__game.textScale) || 1, dpr = ctx.canvas.width / Math.max(1, innerWidth), fs = Math.round(Math.max(13 * u, 15 * dpr) * ts), lh = Math.round(fs * 1.6), psz = Math.round(Math.min(Math.max(92 * u, lh * 3 + 30 * u) - 16 * u, Math.max(76 * u, lh * 2.6))), nf = Math.round(Math.max(12 * u, fs * .8)); // 글자: 폰에서도 15px 이상 + 설정 → 화면 → 글자 크기 (UI_GUIDE 8)
    { const wF = font(fs), wW = Math.round(Math.min(SW - 40 * u, Math.max(560 * u, fs * 34)) - 18 * u - (!d0.cg && (d0.anim || d0.por) ? psz + 14 * u : 0) - 24 * u); if (d0.wrapW !== wW || d0.wrapF !== wF) { const keep = d0.pages ? d0.pi : 0; d0.wrapW = wW; d0.wrapF = wF; d0.pages = null; dlgPages(d0); d0.pi = Math.min(keep, d0.pages.length - 1); d0.ch = keep ? 0 : d0.ch; } }
    const d = S.dialog, P = dlgPages(d), pg = P[d.pi], shown = pg.slice(0, Math.floor(d.ch)), done = d.ch >= pg.length;
    if (d.cg) { if (!S.cgL || S.cgL.src !== d.cg) { S.cgL = { src: d.cg, since: S.t, dx: d.cgDx || 0 }; const sn = SAVE.cgSeen || (SAVE.cgSeen = {}); if (!sn[d.cg]) { sn[d.cg] = true; save(); } } // seen list = 기억 조각 (2차 메뉴)
      drawCg(S.cgL, S.t - S.cgL.since, 1, ox, oy, SW, SH, d); if (S.t - S.cgL.since < .6) return; } else S.cgL = null;
    const g0 = ctx.createLinearGradient(0, oy + SH * .45, 0, oy + SH); g0.addColorStop(0, 'rgba(6,4,10,0)'); g0.addColorStop(1, 'rgba(6,4,10,.55)'); ctx.fillStyle = g0; ctx.fillRect(ox, oy + SH * .45, SW, SH * .55); // dusk under the box
    const w = Math.min(SW - 40 * u, Math.max(560 * u, fs * 34)), x = Math.round(ox + (SW - w) / 2), h = Math.max(92 * u, lh * 3 + 30 * u), y = Math.round(oy + SH - h - 16 * u), sz = psz, hasB = d.anim && npcAnim(d.anim), pi = !hasB && d.por && porImg(d.por), hasP = pi && pi.complete && pi.naturalWidth, port = !d.cg && (hasB || hasP); /* picture scenes: name tag only */
    ctx.fillStyle = 'rgba(10,8,14,.92)'; ctx.fillRect(x, y, w, h); ctx.strokeStyle = '#5c4a38'; ctx.lineWidth = 2 * u; ctx.strokeRect(x + u, y + u, w - 2 * u, h - 2 * u); ctx.strokeStyle = 'rgba(150,120,90,.25)'; ctx.lineWidth = u; ctx.strokeRect(x + 5 * u, y + 5 * u, w - 10 * u, h - 10 * u);
    ctx.fillStyle = '#8a2a2a'; for (let i = 0; i < w - 24 * u; i += 3 * u) if ((i / u | 0) % 7 !== 3) ctx.fillRect(x + 12 * u + i, y + 3 * u + Math.round(Math.sin(i / (14 * u) + d.t * .6) * u), 2 * u, Math.max(1, u)); // 붉은 실 한 가닥 (1장 = 아라크네의 실)
    for (const [cx, cy] of [[x, y], [x + w, y], [x, y + h], [x + w, y + h]]) { ctx.fillStyle = '#7a6448'; ctx.fillRect(cx - 3 * u, cy - 3 * u, 6 * u, 6 * u); ctx.fillStyle = '#1a1420'; ctx.fillRect(cx - u, cy - u, 2 * u, 2 * u); }
    let tx = x + 18 * u;
    if (port) { const px = x + 10 * u, py = y + (h - sz) / 2; ctx.fillStyle = '#16111c'; ctx.fillRect(px, py, sz, sz); if (hasB) dlgBust(d, px, py, sz); else { const j = d.creep ? [(Math.random() * 3 | 0) - 1, (Math.random() * 3 | 0) - 1] : [0, 0]; ctx.imageSmoothingEnabled = false; ctx.drawImage(pi, px + j[0] * u, py + j[1] * u, sz, sz); if (d.creep && Math.sin(d.t * 23) > .7) { ctx.fillStyle = 'rgba(140,0,10,.22)'; ctx.fillRect(px, py, sz, sz); } } /* creep = horror twitch + red flicker (아라크네) */
      ctx.strokeStyle = '#5c4a38'; ctx.lineWidth = 2 * u; ctx.strokeRect(px, py, sz, sz); tx = px + sz + 14 * u; }
    if (d.name) { ctx.font = font(nf); const nw = ctx.measureText(d.name).width + (d.role ? ctx.measureText(' · ' + d.role).width * .85 : 0) + nf * 1.8, ny = y - nf * 1.2;
      ctx.fillStyle = 'rgba(10,8,14,.95)'; ctx.fillRect(tx - 10 * u, ny, nw, nf * 1.5); ctx.strokeStyle = '#5c4a38'; ctx.lineWidth = 2 * u; ctx.strokeRect(tx - 10 * u, ny, nw, nf * 1.5);
      textOut(d.name, tx, ny + nf * 1.12, nf, '#e8d3a8', '#000', 'left'); if (d.role) { ctx.font = font(nf); textOut(' · ' + d.role, tx + ctx.measureText(d.name).width, ny + nf * 1.12, nf * .83, '#8f8478', '#000', 'left'); } }
    shown.split('\n').forEach((l, i) => textOut(l, tx, y + 13 * u + fs + i * lh, fs, d.narr ? '#a99f90' : '#ece6dc', '#000', 'left')); /* narration = dim grey, no name tag */
    if (done && d.pi === P.length - 1 && d.choices) d.choices.forEach((c, i) => { const cy = y - (d.choices.length - i) * 22 * u - 22 * u, on = i === d.sel; ctx.font = font(12 * u); const cw = ctx.measureText(c.t).width + 34 * u, cx = x + w - cw - 8 * u;
      ctx.fillStyle = on ? 'rgba(60,18,22,.95)' : 'rgba(10,8,14,.9)'; ctx.fillRect(cx, cy, cw, 19 * u); ctx.strokeStyle = on ? '#b04a3a' : '#5c4a38'; ctx.lineWidth = 2 * u; ctx.strokeRect(cx, cy, cw, 19 * u); textOut((on ? '▶ ' : '   ') + c.t, cx + 9 * u, cy + 14 * u, 12 * u, on ? '#ffe2c8' : '#a99c8c', '#000', 'left'); });
    if (done && !(d.choices && d.pi === P.length - 1)) { const bob = Math.round(Math.sin(d.t * 6) * 1.5 * u); textOut(d.pi < P.length - 1 ? '▼' : '■', x + w - 16 * u, y + h - 10 * u + bob, Math.max(10 * u, fs * .7), '#b04a3a', '#000', 'right'); }
    if (P.length > 1) textOut((d.pi + 1) + '/' + P.length, x + w - 18 * u - fs * .8, y + h - 10 * u, Math.max(9 * u, fs * .6), '#6e6458', '#000', 'right'); }
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
      if (window.HUD && HUD.drawQuick) { const Q = S.qs || {}; hb = HUD.drawQuick(ctx, { x: ox + 12 * hu, y: hb - 6 * hu, u: hu, n: g ? g.potions : 0, cap: DIFF().potion_cap || 5, cd: g ? g.potionCd : 0, cdMax: POT.cd, key: keyHint('potion'), low: hero.hp > 0 && hero.hp < hero.maxHp * .35, flash: Q.flash || 0, shake: Q.shake || 0, note: Q.noteT > 0 ? Q.note : '' }) + 4 * hu; if (S.hudY) S.hudY = hb; }
      else textOut(`물약 ${g ? g.potions : 0}/${DIFF().potion_cap || 5} [${keyHint('potion')}]` + (g && g.potionCd > 0 ? ' ' + g.potionCd.toFixed(1) + 's' : ''), ox + 12 * u, hb, 11 * u, '#cfe8ff', '#000', 'left');
      { const pb = document.getElementById('wtb_pot'); if (pb && g) { const n = g.potions || 0, cf = g.potionCd > 0 ? g.potionCd / POT.cd : 0, sig = n + '|' + Math.round(cf * 40); if (pb._sig !== sig) { pb._sig = sig; pb.innerHTML = '물약<b class="pc">' + n + '</b>'; pb.style.setProperty('--cd', (cf * 100).toFixed(1) + '%'); pb.classList.toggle('zero', !n); } } } // touch button = same count / cooldown as the HUD slot
      if (window.HUD && HUD.drawFeed && S.feed && S.feed.length) HUD.drawFeed(ctx, { x: ox + SW - 12 * hu, y: oy + SH - 40 * hu, u: hu, items: S.feed });
      if (lastStandOn()) { textOut(`심연의 힘 ${S.lastStand.t.toFixed(1)}초 · 저스트 회피 → 반격 「사멸의 궤적」`, ox + 12 * u, hb + 14 * u, 10 * u, '#c9a0ff', '#000', 'left'); if (S.hudY) S.hudY += 14 * u; }
      const arN = areaAt(m, hero.x, hero.y); textOut(arN ? arN.name : m.name, ox + SW - 10 * u, oy + 20 * u, 12 * u, '#ffe08a', '#000', 'right');
      if (S.areaCard) { const A = S.areaCard, al = Math.max(0, Math.min(1, A.t * 2, (2.4 - A.t) * 4)); ctx.globalAlpha = al; textOut(A.a.name, cxs, oy + 40 * u, 20 * u, '#f4ead2'); textOut(A.a.sub || '', cxs, oy + 56 * u, 11 * u, '#d8cbb0'); ctx.globalAlpha = 1; }
      { const fc = inCombat(); textOut(S.saved ? '✔ ' + S.saved.text : fc ? '● 전투 중 — 저장 불가' : `● 저장 가능 [${keyHint('save') || 'F5'}]`, ox + SW - 10 * u, oy + SH - 20 * u, 10 * u, S.saved ? '#bff5c0' : fc ? '#ff9a8a' : 'rgba(190,240,190,.85)', '#000', 'right'); }
      if (m.area && /^(field0[01]|dungeon01|boss01)/.test(m.id)) { const n = ['champ_boar', 'champ_wasp'].filter(f => SAVE.flags[f]).length; textOut(`챔피언 ${n}/2` + (SAVE.flags.boss01 ? '  ·  골렘 격파 ✓' : ''), ox + SW - 10 * u, oy + 35 * u, 10 * u, n === 2 ? '#8f8' : '#fff', '#000', 'right'); }
      if (m.type === 'dungeon') { const keys = Object.keys(SAVE.keys).filter(k2 => SAVE.keys[k2] === true && !k2.endsWith(':used') && !SAVE.keys[k2 + ':used']).length; if (keys) textOut('열쇠 ×' + keys, ox + SW - 10 * u, oy + 50 * u, 10 * u, '#ffe08a', '#000', 'right'); }
      const b = S.bossRef; if (b && !b.dead && !(S.cine && S.cine.hold)) drawBossBar(b, cxs, oy, SH, u);
      if (S.ult && S.ult.t < S.ult.warn) { ctx.strokeStyle = `rgba(255,30,20,${.5 + .4 * Math.sin(S.t * 18)})`; ctx.lineWidth = 10 * u; ctx.strokeRect(ox + 5 * u, oy + 5 * u, SW - 10 * u, SH - 10 * u);
        textOut('필살 · 대지 붕괴  ' + Math.max(0, S.ult.warn - S.ult.t).toFixed(1), cxs, oy + 62 * u, 17 * u, '#ff6040'); }
      if (!S.dialog && !(b && !b.dead)) textOut(`이동 방향키/WASD · 공격 ${keyHint('attack')} · 회피대시 Shift/${keyHint('dash')} (무적) · 조사 ${keyHint('interact')} · 물약 ${keyHint('potion')} · 지도 M · 미니맵 V · 목표 G · Esc`, cxs, oy + SH - (b && !b.dead ? 48 : 6) * u, 9 * u, 'rgba(230,230,240,.85)');
    }
    if (NAV() && m.type !== 'world') NAV().drawHud(k, ox, oy, u);
    if (S.banner) { const bn = S.banner, a = Math.max(0, Math.min(1, bn.t * 3, (bn.max - bn.t) * 6 + .2)); ctx.globalAlpha = a; textOut(bn.text, cxs, oy + (bn.small ? 82 : 90) * u, (bn.small ? 14 : 19) * u, bn.small ? '#ffd0a0' : '#ffe08a'); ctx.globalAlpha = 1; }
    if (S.msg) { ctx.globalAlpha = Math.min(1, S.msg.t * 3); ctx.font = font(12 * u); const tw = Math.max(300 * u, ctx.measureText(S.msg.text).width + 30 * u); panel(cxs - tw / 2, oy + SH - 90 * u, tw, 28 * u); textOut(S.msg.text, cxs, oy + SH - 71 * u, 12 * u, '#fff'); ctx.globalAlpha = 1; }
    if (M() && M().type !== 'world') drawBossCine(ox, oy, SW, SH, u);
    drawCgOut(ox, oy, SW, SH);
    if (S.dialog) drawDialog(ox, oy, SW, SH, u);
    { const on = !!(S.dialog || (window.__game && window.__game.ui)); if (document.body.classList.contains('wdlg') !== on) document.body.classList.toggle('wdlg', on); } // phone: fight buttons step aside while talking
    if (S.pause) { ctx.fillStyle = 'rgba(0,0,0,.5)'; ctx.fillRect(ox, oy, SW, SH); panel(cxs - 150 * u, oy + SH / 2 - 50 * u, 300 * u, 100 * u);
      textOut('일시정지', cxs, oy + SH / 2 - 14 * u, 20 * u, '#ffe08a'); textOut(Q.has('old') ? 'Esc: 계속   ·   T: 마을로 귀환' : 'Esc: 계속   ·   T: 펠트로 귀환', cxs, oy + SH / 2 + 18 * u, 13 * u, '#fff'); }
    if (S.deadT > 0) { ctx.fillStyle = `rgba(60,0,0,${Math.min(.6, S.deadT)})`; ctx.fillRect(ox, oy, SW, SH);
      if (S.deadT > 1.4) { panel(cxs - 170 * u, oy + SH / 2 - 46 * u, 340 * u, 92 * u); textOut('쓰러졌다', cxs, oy + SH / 2 - 16 * u, 19 * u, '#ffb0a0');
        textOut(S.snap ? `${keyHint('attack')}  다시 도전 (전투 직전부터)` : `${keyHint('attack')}  마지막 비석에서`, cxs, oy + SH / 2 + 10 * u, 13 * u, '#fff'); textOut('T  마지막 비석에서', cxs, oy + SH / 2 + 30 * u, 13 * u, '#ddd'); } }
    if (m.type !== 'world') { drawFieldUlt(k, ox, oy, SW, SH); { const now = performance.now(), dt = S._rT ? Math.min(.1, (now - S._rT) / 1000) : 0; S._rT = now; drawUlt2Result(ox, oy, SW, SH, manual ? 1 / 30 : dt); } }
  }
  // ---------------- 필살기 (R) in fields / dungeons / boss rooms: reuses the town ULTS (천광낙뢰 / 멸계강림 / 찬검·해동), same cut-in timing,
  // world frozen + hero invulnerable for the whole move, damage to every enemy on screen. Consumes the full gauge (template ULT_CFG / addUlt).
  // 심연 초필살기 (주인 10-23 "심연의 힘이 켜지면 맵 전체 초필살기, 창세기전 2처럼"): 심연의 힘 동안 필살기 키 -> 게이지 없이 맵 전체의 적을 친다, 쓰면 심연의 힘이 끝난다
  const ABYSS_U = { id: 'abyss', name: '사멸의 궤적', en: 'Trail of Extinction', route: '심연', hitT: [.3, .55, .8, 1.05, 1.3, 1.6], por: 'hero', band: '#c9a0ff', tint: '16,0,34',
    col: ['230,200,255', '130,50,230', '40,0,90'], dur: 2.3, whole: true, label: '심연 반격 초필살기', mob: 999, champ: .30, boss: .15, stun: 3 };
  const FULT = { freeze: .2, cutin: 1.05, mob: 150, champ: .25, boss: .22 };
  // 요즘 연출 실험 (?ult2=lb,impact,type,punch,slow,result | none): lb 영화 띠 · impact 임팩트 프레임(반전 2프레임) · type 기술 이름 베기 등장 · punch 타격마다 카메라 펀치 · slow 마지막 타격 슬로모션 · result 결과 표시
  const ULT2 = new Set(((Q.get('ult2') ?? 'lb,impact,type,punch,slow,result') === 'none' ? '' : (Q.get('ult2') ?? 'lb,impact,type,punch,slow,result')).split(',').filter(Boolean));
  function u2(k, f) { return f && f.U.whole && ULT2.has(k); }
  // 컷인 방식 실험 (?cut=band|zoom|eye|hybrid): band = 일러스트 초상화 띠(옛), zoom = 게임 화면 그대로 주인공 확대, eye = 도트 얼굴 눈 띠, hybrid = 확대 + 눈 띠
  const CUT_T = { band: [.2, 1.05], zoom: [.08, .72], eye: [.08, .62], hybrid: [.08, .8] };
  // 연구 결과 (handoff/claude/ult_research/CUTIN_ko.md): 심연 초필살기 = hybrid (드물게 쓰니 크게), 일반 필살기 = zoom (자주 쓰니 짧게). 공격/조사 키로 컷인 건너뛰기
  function cutMode(def) { const q = Q.get('cut'); return CUT_T[q] ? q : def; } // total over all hits: normal mobs 150 (lethal), champion 25% / boss 22% of max HP (cap, so medium-hard bosses stay a fight)
  const PORI = {}; function porImg(id) { if (!PORI[id]) { const im = new Image(); im.src = V('assets/portraits/' + id + '.png'); PORI[id] = im; } return PORI[id]; }
  function onScreen(mm) { const x0 = S.camI[0], y0 = S.camI[1]; return mm.x > x0 - 8 && mm.x < x0 + EW + 8 && mm.y > y0 - 8 && mm.y < y0 + EH + 24; }
  function castAbyss() { const g = window.__game; if (S.ultFx || hero.hp <= 0 || S.deadT > 0) return; // 심연 초필살기: 심연의 힘 중 저스트 회피 = 반격 (한 번 쉴 때마다 한 번)
    const U = ABYSS_U; S.abyssSpent = true; S.lastStand.t = 0; S.lastStand.cd = 0; S.msg = null; hero.atk = null; hero.roll = null; hero.inv = 9; porImg(U.por);
    const cm = cutMode('hybrid'), fx = ['pillar', 'rift', 'trail', 'both'].includes(Q.get('fx')) ? Q.get('fx') : 'rift'; S.ultFx = { U, t: 0, hitI: 0, boomed: false, cut: cm, fx, seed: Math.random() * 1000, fz: CUT_T[cm][0], ci: CUT_T[cm][1], vic: S.mobs.filter(mm => !mm.dead && !(mm.spawnT > 0)) }; try { g && g.SFX.play('ult_cutin', 1); } catch (e) {} }
  function abyssRest() { S.abyssSpent = false; if (S.lastStand) S.lastStand.cd = 0; } // 쉼터·여관·비석에서 쉬면 다시 쓸 수 있음
  function castUlt() { const g = window.__game; if (!g || !g.ULTS || !g.ULT_CFG || S.ultFx) return;
    if (g.ultG < g.ULT_CFG.max) { msg('필살기 게이지 부족 (' + Math.floor(g.ultG) + '%)'); return; }
    if (hero.hp <= 0 || S.deadT > 0) return;
    const U = g.ULTS[g.ultId ? g.ultId() : 'tenkou'] || g.ULTS.tenkou; g.ultG = 0; S.msg = null; hero.atk = null; hero.roll = null; hero.inv = 9; porImg(U.por);
    const cm = cutMode('zoom'); S.ultFx = { U, t: 0, hitI: 0, boomed: false, cut: cm, fz: CUT_T[cm][0], ci: CUT_T[cm][1], vic: S.mobs.filter(mm => !mm.dead && !(mm.spawnT > 0) && onScreen(mm)) };
    try { g.SFX.play('ult_cutin', 1); } catch (e) {} }
  function stepUlt(dt) { const f = S.ultFx, U = f.U, g = window.__game; { const e0 = f.t - f.fz - f.ci, L = U.hitT[U.hitT.length - 1]; if (u2('slow', f) && e0 > L - .06 && e0 < L + .28) dt *= .35; } f.t += dt; hero.inv = Math.max(hero.inv, 1); S.shake = Math.max(0, S.shake - dt * 14);
    const e = f.t - f.fz - f.ci;
    if (e >= 0 && !f.boomed) { f.boomed = true; shake(2); try { g.SFX.play('ult_boom', 1); } catch (er) {} } // modest: 2px boom, 1px per hit (world cap 3px + '화면 흔들림' option)
    while (e >= 0 && f.hitI < U.hitT.length && e >= U.hitT[f.hitI]) { f.hitI++; shake(1); const n = U.hitT.length;
      for (const mm of f.vic) { if (mm.dead || mm.invuln) continue; const D = mm.D, F = U.whole ? U : FULT, tot = D.boss ? mm.maxHp * F.boss : D.champion ? mm.maxHp * F.champ : F.mob, d = Math.max(1, Math.round(tot / n));
        mm.hp -= d; mm.hitT = .3; mm.flash = U.whole && f.fx && f.fx !== 'pillar' && fxQ() >= 3 ? 0 : .12; mm.lagDelay = .35; // the world is frozen during the ult: a flash would stay white the whole time if (onScreen(mm)) { addFx('spark', mm.x, mm.y - (D.h || 20) / 2, { life: .25 }); addFx('text', mm.x, mm.y - (D.h || 20) - 4 - f.hitI * 3, { text: String(d), life: .8, color: '#ffe9a8' }); }
        if (D.boss || D.champion) engage(mm); if (mm.hp <= 0) killMob(mm); } }
    if (e >= U.dur) { S.ultFx = null; hero.inv = .6; if (U.whole && f.fx === 'rift' && fxQ() >= 3) for (const mm of f.vic) addFx('scorch', mm.x, mm.y + 2, { life: 1.6 }); if (u2('result', f)) { const n = f.vic.filter(mm => mm.dead).length, b = f.vic.find(mm => !mm.dead && (mm.D.boss || mm.D.champion)); S.ult2Res = { t: 0, text: n ? `적 ${n} 소멸` : '', sub: b ? `${b.D.name || '강적'} 3초 기절` : '' }; } if (U.stun) { S.hazards.length = 0; S.shots.length = 0; for (const mm of f.vic) if (!mm.dead) { mm.abyStun = U.stun; mm.atk = null; } banner('적이 심연에 짓눌려 움직이지 못한다!', 1.6, true); } } }
  function cutZoom() { const f = S.ultFx; if (!f || (f.cut !== 'zoom' && f.cut !== 'hybrid' && !u2('punch', f))) return 1; const c = f.t - f.fz, e = c - f.ci; // push in during the cut, snap back on the boom
    if (c < 0) return 1; if (e < 0) { const q = Math.min(1, c / (f.ci * .85)); return 1 + .75 * (q * q * (3 - 2 * q)); } let z = e < .12 ? 1 + .75 * (1 - e / .12) : 1;
    if (u2('punch', f)) for (const t of f.U.hitT) { const d = e - t; if (d >= 0 && d < .1) z = Math.max(z, 1 + .06 * (1 - d / .1)); } return z; }
  function drawCutZoom(f, U, q, u, ox, oy, SW, SH) { const [hx, hy] = W2S(hero.x, hero.y - 14), k = S.view.k; // spotlight on the hero, chest emblem lights up, name in the world
    const r0 = Math.max(SW, SH) * (1 - .55 * Math.min(1, q * 1.6)), gr = ctx.createRadialGradient(hx, hy, r0 * .12, hx, hy, r0);
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, `rgba(${U.tint},.85)`); ctx.fillStyle = gr; ctx.fillRect(ox, oy, SW, SH);
    const pul = .5 + .5 * Math.sin(f.t * 30), cy = hy - 2 * k * cutZoom(); ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 3; i++) { ctx.fillStyle = `rgba(${U.col[1]},${(.35 - i * .1) * Math.min(1, q * 3)})`; ctx.beginPath(); ctx.arc(hx, cy, (6 + i * 7 + pul * 3) * k * .5 * Math.min(1, q * 2.5), 0, TAU); ctx.fill(); }
    const L = (SW * .5) * Math.min(1, Math.max(0, q - .35) * 2.2); ctx.strokeStyle = `rgba(${U.col[0]},.9)`; ctx.lineWidth = Math.max(1, k * .5);
    for (let i = 0; i < 8; i++) { const a = i / 8 * TAU + f.t * .6; ctx.beginPath(); ctx.moveTo(hx + Math.cos(a) * 8 * k, cy + Math.sin(a) * 8 * k); ctx.lineTo(hx + Math.cos(a) * (8 * k + L), cy + Math.sin(a) * (8 * k + L)); ctx.stroke(); }
    ctx.restore(); const fs = Math.round(SH * .075), a = Math.min(1, Math.max(0, q - .3) * 3); ctx.globalAlpha = a;
    textOut(U.name, ox + SW / 2, oy + SH * .2, fs, U.band); textOut(U.label || U.route + ' 필살기', ox + SW / 2, oy + SH * .2 + fs * .75, Math.round(SH * .028), '#fff'); ctx.globalAlpha = 1; }
  function drawCutEye(f, U, q, u, ox, oy, SW, SH) { // pixel eye strip: the in-game hero sprite's face, nearest-scaled, sliding through a thin band
    const inn = Math.min(1, q / .2), out = q > .82 ? (q - .82) / .18 : 0, bh = SH * .2 * inn * (1 - out), by = oy + SH * .42; if (bh < 2) return;
    ctx.save(); ctx.fillStyle = 'rgba(4,2,10,.92)'; ctx.fillRect(ox, by - bh / 2, SW, bh); const lw = Math.max(2, SH * .006); ctx.fillStyle = U.band; ctx.fillRect(ox, by - bh / 2, SW, lw); ctx.fillRect(ox, by + bh / 2 - lw, SW, lw);
    ctx.beginPath(); ctx.rect(ox, by - bh / 2 + lw, SW, bh - lw * 2); ctx.clip();
    const G = h128(), c = G && h128Cell(); let im = null; if (c) im = c.h8 !== undefined ? G.H8img(c.h8) : G.H128img;
    if (im && c) { const FIG = 117, fy0 = c[1] + c[5] - FIG * 1.02, faceH = FIG * .36, faceW = FIG * .62, fx0 = c[0] + c[4] - faceW / 2; // head of the figure: top 36% above the feet anchor
      const sc = SH * .2 * 1.25 / faceH, sx = ox + SW * (.64 - q * .12) - faceW * sc / 2; ctx.imageSmoothingEnabled = false;
      ctx.drawImage(im, fx0, fy0, faceW, faceH, sx, by - faceH * sc * .45, faceW * sc, faceH * sc); }
    ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = `rgba(${U.col[1]},.25)`; ctx.fillRect(ox, by - bh / 2, SW, bh); ctx.restore();
    const fs = Math.round(SH * .06); ctx.globalAlpha = inn * (1 - out); textOut(U.name, ox + SW * .27, by + fs * .3, fs, U.band); ctx.globalAlpha = 1; }
  // 심연 초필살기 도트 이펙트 실험 (?fx=pillar|rift|trail|both): 맵과 같은 저해상도 캔버스에 fillRect만으로 (그라데이션·부드러운 선 없음)
  const AB_PAL = { void: '#0b0614', deep: '#2a0f4a', vio: '#6b2bd6', lit: '#b98cff', core: '#efe2ff' };
  function hash(n) { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); }
  // 퀄리티 단계 실험 (?fxq=0..3, 누적): 1 = 맵만 어둡게 하고 이펙트는 그 위에 밝게(빛나는 금) · 2 = 12fps로 끊어 움직이고 사라질 때 디더링(도트답게) · 3 = 힘 모으기·충격 고리·갈래 금·튀는 돌·그을린 자국(준비-충격-여운)
  function fxQ() { const v = +Q.get('fxq'); return Q.has('fxq') && v >= 0 && v <= 3 ? v : 3; }
  const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
  function dith(x, y, a) { return a >= 1 || (a > 0 && BAYER[(y & 3) * 4 + (x & 3)] < a * 16); }
  function abPx(g, x, y, w, col, a, q) { x = Math.round(x); y = Math.round(y); if (q >= 2) { if (!dith(x, y, a)) return; g.globalAlpha = 1; } else g.globalAlpha = a; g.fillStyle = col; g.fillRect(x, y, w, w); }
  function abLine(g, x0, y0, x1, y1, w, col, a, q) { const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0))); for (let i = 0; i <= n; i++) abPx(g, x0 + (x1 - x0) * i / n - w / 2, y0 + (y1 - y0) * i / n - w / 2, w, col, a, q); }
  function abEll(g, cx, cy, rx, ry, col, a, q) { if (rx < .5 || ry < .5) return; for (let y = -Math.floor(ry); y <= Math.floor(ry); y++) { const h = Math.round(rx * Math.sqrt(Math.max(0, 1 - (y / ry) ** 2)));
      if (q >= 2 && a < 1) { for (let x = -h; x < h; x++) abPx(g, cx + x, cy + y, 1, col, a, q); } else { g.globalAlpha = a; g.fillStyle = col; g.fillRect(Math.round(cx - h), Math.round(cy + y), h * 2, 1); } } }
  function abyssDark(g, f) { const q = fxQ(); if (q < 1 || !f.fx || f.fx === 'pillar') return; const a = Math.min(.62, .62 * f.t / Math.max(.01, f.fz)); g.save(); g.globalAlpha = 1; g.fillStyle = `rgba(10,0,26,${a})`; g.fillRect(S.camI[0] - 4, S.camI[1] - 4, EW + 8, EH + 8); g.restore(); }
  function drawAbyssLow(g, f) { const U = f.U, q = fxQ(), P = AB_PAL; let e = f.t - f.fz - f.ci; if (q >= 2) e = Math.floor(e * 12) / 12; const end = U.dur;
    const hx = hero.x, hy = hero.y - 4, cy0 = hero.y - 12; g.save();
    if (q >= 3 && e < 0 && e > -.3) { const k = 1 + e / .3; for (let i = 0; i < 18; i++) { const a = hash(f.seed + i) * TAU, r = (1 - k) * (26 + hash(i + 3) * 22) + 2; abPx(g, hx + Math.cos(a) * r, cy0 + Math.sin(a) * r * .7, i % 4 ? 1 : 2, i % 3 ? P.lit : P.core, 1, q); } } // 힘 모으기: motes implode into the chest
    if (e < 0) { g.restore(); return; }
    const fade = e > end - .4 ? Math.max(0, (end - e) / .4) : 1, vic = f.vic.slice().sort((a, b) => Math.hypot(a.x - hx, a.y - hy) - Math.hypot(b.x - hx, b.y - hy)), SP = 300;
    if (q >= 3 && e < .18) { const r = 6 + e * 260; for (let i = 0; i < 48; i++) { const a = i / 48 * TAU; abPx(g, hx + Math.cos(a) * r, hy + Math.sin(a) * r * .55, 2, e < .08 ? P.core : P.lit, 1 - e / .18, q); } } // 충격 고리
    if (f.fx === 'rift' || f.fx === 'both') {
      const targets = vic.map(m => [m.x, m.y]).concat(Array.from({ length: 5 }, (_, i) => { const a = i / 5 * TAU + hash(f.seed + i); return [hx + Math.cos(a) * 600, hy + Math.sin(a) * 380]; }));
      targets.forEach(([tx, ty], j) => { const L = Math.hypot(tx - hx, ty - hy), reach = Math.min(L, e * SP), segs = Math.max(2, Math.round(L / 14)), age = e - L / SP, ca = fade * (age > .35 ? Math.max(.3, 1 - (age - .35) / .5) : 1); let px = hx, py = hy;
        for (let k = 1; k <= segs; k++) { const d = L * k / segs; if (d > reach + 14) break; const jit = (hash(f.seed + j * 31 + k) - .5) * 10, nx = (ty - hy) / L, ny = -(tx - hx) / L;
          const qx = hx + (tx - hx) * k / segs + (k < segs ? nx * jit : 0), qy = hy + (ty - hy) * k / segs + (k < segs ? ny * jit * .6 : 0), cut = Math.min(1, Math.max(0, (reach - d + 14) / 14));
          const ex = px + (qx - px) * cut, ey = py + (qy - py) * cut, hot = (Math.floor(e * 12) + k) % 3 === 0;
          abLine(g, px, py, ex, ey, k < 3 ? 3 : 2, P.void, ca, q); abLine(g, px, py, ex, ey, 1, hot ? P.core : P.lit, ca, q);
          if (q >= 3 && cut >= 1 && hash(f.seed + j * 13 + k) > .62) { const sgn = hash(k + j) > .5 ? 1 : -1, ba = Math.atan2(ty - hy, tx - hx) + sgn * .7, bl = 6 + hash(k * 7 + j) * 10, grow = Math.min(1, (reach - d) / 20); // 갈래 금
            abLine(g, qx, qy, qx + Math.cos(ba) * bl * grow, qy + Math.sin(ba) * bl * grow * .7, 1, P.vio, ca, q); }
          px = qx; py = qy; }
        if (q >= 3 && reach < L) { const fx_ = hx + (tx - hx) * reach / L, fy_ = hy + (ty - hy) * reach / L; for (let i = 0; i < 3; i++) { const ph = ((e * 5 + i / 3 + hash(j)) % 1), back = ph * 18, hop = Math.sin(ph * Math.PI) * 7; // 튀는 돌
          abPx(g, fx_ - (tx - hx) / L * back + (i - 1) * 2, fy_ - (ty - hy) / L * back - hop, 1, i ? P.deep : P.lit, 1, q); } } });
      vic.forEach((m, j) => { const at = Math.hypot(m.x - hx, m.y - hy) / SP, t = e - at; if (t < 0) return;
        const open = Math.min(1, t / .25), shut = t > end - at - .5 ? Math.max(0, (end - e) / .5) : 1, r = 12 * open * shut, pul = U.hitT.some(tt => e - tt >= 0 && e - tt < .1);
        abEll(g, m.x, m.y + 2, r + 2, (r + 2) * .45, pul ? P.core : P.lit, 1, q); abEll(g, m.x, m.y + 2, r + 1, (r + 1) * .45, P.vio, 1, q); abEll(g, m.x, m.y + 2, r, r * .45, P.void, 1, q);
        if (q >= 3) for (let k = 0; k < 6; k++) { const a = k / 6 * TAU + hash(j + k) , len = r * (.6 + .5 * Math.abs(Math.sin(e * 9 + k))); abLine(g, m.x + Math.cos(a) * r * .7, m.y + 2 + Math.sin(a) * r * .3, m.x + Math.cos(a) * (r * .7 + len * .5), m.y + 2 + Math.sin(a) * r * .3 - len * .9, 1, P.deep, open * shut, q); } // 촉수
        for (let k = 0; k < 10; k++) { const a = hash(f.seed + j * 7 + k) * TAU + e * 6, rr = (1 - ((e * 1.6 + hash(k + j)) % 1)) * 22 + 2; abPx(g, m.x + Math.cos(a) * rr, m.y - 6 + Math.sin(a) * rr * .6, 1, k % 3 ? P.lit : P.core, 1, q); } }); }
    if (f.fx === 'trail' || f.fx === 'both') { const n = vic.length, t0 = U.hitT[0], span = Math.max(.3, U.hitT[U.hitT.length - 1] - t0 - .2); let px = hx, py = hy - 4;
      vic.forEach((m, j) => { const tj = t0 + span * j / Math.max(1, n), t = e - tj, mx = m.x, my = m.y - 8;
        if (t >= -.12 && t < .3) { const head = Math.min(1, (t + .12) / .12), tail = Math.max(0, t / .3); const ax = px + (mx - px) * tail, ay = py + (my - py) * tail, bx = px + (mx - px) * head, by = py + (my - py) * head;
          abLine(g, ax, ay, bx, by, 4, P.void, fade, q); abLine(g, ax, ay, bx, by, 2, P.vio, fade, q); abLine(g, ax, ay, bx, by, 1, P.core, fade, q); }
        if (t >= 0 && t < .45) { const L = 10 + 6 * Math.min(1, t / .08), al = fade * (1 - t / .45); abLine(g, mx - L, my - L * .7, mx + L, my + L * .7, 3, P.vio, al, q); abLine(g, mx - L, my + L * .7, mx + L, my - L * .7, 3, P.vio, al, q); abLine(g, mx - L, my - L * .7, mx + L, my + L * .7, 1, P.core, al, q); abLine(g, mx - L, my + L * .7, mx + L, my - L * .7, 1, P.core, al, q); }
        px = mx; py = my; }); }
    g.restore(); }
  function drawUlt2(f, U, e, u, ox, oy, SW, SH) { if (!U.whole) return;
    if (u2('impact', f)) { const L = U.hitT[U.hitT.length - 1], on = (e >= 0 && e < 2 / 30) || (e >= L && e < L + 2 / 30); // impact frames: 2 frames of a violet negative at the boom and the last hit
      if (on) { ctx.save(); ctx.globalCompositeOperation = 'difference'; ctx.fillStyle = '#fff'; ctx.fillRect(ox, oy, SW, SH); ctx.globalCompositeOperation = 'saturation'; ctx.fillStyle = '#808080'; ctx.fillRect(ox, oy, SW, SH);
        ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = '#b48cff'; ctx.fillRect(ox, oy, SW, SH); ctx.restore(); } }
    if (u2('lb', f)) { const tot = f.fz + f.ci + U.dur, inn = Math.min(1, f.t / .18), out = Math.min(1, Math.max(0, (tot - f.t) / .25)), h = Math.round(SH * .1 * inn * out); // cinema bars
      ctx.fillStyle = '#000'; ctx.fillRect(ox, oy, SW, h); ctx.fillRect(ox, oy + SH - h, SW, h); }
    if (u2('type', f) && e >= 0 && e < 1.5) { const rv = Math.min(1, e / .16), al = e > 1.2 ? 1 - (e - 1.2) / .3 : 1, fs = Math.round(SH * .085), x0 = ox + SW * .06, y0 = oy + SH * .8; // skill name slashes in, lower left
      ctx.save(); ctx.globalAlpha = al; ctx.translate(x0, y0); ctx.transform(1, 0, -.22, 1, 0, 0); ctx.font = font(fs); const w = ctx.measureText(U.name).width + fs * .4;
      ctx.fillStyle = `rgba(${U.col[1]},.9)`; ctx.fillRect(-fs * .2, fs * .12, w * Math.min(1, e / .1), Math.max(2, fs * .1));
      ctx.beginPath(); ctx.rect(-fs * .3, -fs * 1.1, w * rv + fs * .2, fs * 1.4); ctx.clip(); textOut(U.name, 0, 0, fs, '#f3eaff', '#14002e', 'left');
      textOut((U.label || '') + ' · ' + U.en, fs * .05, fs * .62, Math.round(fs * .3), '#c9a0ff', '#000', 'left');
      if (e < .16) { ctx.fillStyle = '#fff'; ctx.fillRect(w * rv - fs * .25, -fs * 1.05, Math.max(2, fs * .06), fs * 1.3); } ctx.restore(); } }
  function drawUlt2Result(ox, oy, SW, SH, dt) { const R = S.ult2Res; if (!R) return; R.t += dt; if (R.t > 1.8 || !R.text) { if (R.t > 1.8) S.ult2Res = null; return; } // 결과 표시: kills (+ stunned boss), lower left, after the move
    const a = Math.min(1, R.t / .12) * (R.t > 1.4 ? (1.8 - R.t) / .4 : 1), fs = Math.round(SH * .045), x = ox + SW * .06 + (1 - Math.min(1, R.t / .15)) * -20, y = oy + SH * .8;
    ctx.globalAlpha = a; textOut(R.text, x, y, fs, '#f3eaff', '#14002e', 'left'); if (R.sub) textOut(R.sub, x, y + fs * 1.1, Math.round(fs * .7), '#c9a0ff', '#000', 'left'); ctx.globalAlpha = 1; }
  function drawFieldUlt(k, ox, oy, SW, SH) { const f = S.ultFx; if (!f) return; const U = f.U, u = k / 3, e = f.t - f.fz - f.ci, c = f.t - f.fz;
    ctx.save(); ctx.beginPath(); ctx.rect(ox, oy, SW, SH); ctx.clip();
    if (!(U.whole && f.fx && f.fx !== 'pillar' && fxQ() >= 1)) { ctx.fillStyle = `rgba(${U.tint},${.45 * Math.min(1, f.t / f.fz)})`; ctx.fillRect(ox, oy, SW, SH); } // q1+: the map is darkened on the world canvas instead, so the effect stays bright
    if (U.whole && e >= 0 && (!f.fx || f.fx === 'pillar')) { const [hx, hy] = W2S(hero.x, hero.y - 8), R = Math.hypot(SW, SH); ctx.globalCompositeOperation = 'lighter'; // 심연: rings sweep the whole map from the hero
      for (let i = 0; i < U.hitT.length; i++) { const q = (e - U.hitT[i] + .2) / .7; if (q < 0 || q > 1) continue; ctx.strokeStyle = `rgba(${U.col[1]},${(1 - q) * .9})`; ctx.lineWidth = (18 - q * 14) * u;
        ctx.beginPath(); ctx.ellipse(hx, hy, R * q, R * q * .62, 0, 0, TAU); ctx.stroke(); ctx.strokeStyle = `rgba(255,255,255,${(1 - q) * .7})`; ctx.lineWidth = 2 * u; ctx.stroke(); }
      ctx.globalCompositeOperation = 'source-over'; }
    if (e >= 0 && !(U.whole && f.fx && f.fx !== 'pillar')) { ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < U.hitT.length; i++) { const q = (e - U.hitT[i] + .15) / .5; if (q < 0 || q > 1) continue; const al = 1 - q;
        if (U.id === 'chan') { const ang = [-.42, .38, -.12, .6, -.7][i % 5], cy = oy + SH * (.3 + .1 * i); ctx.save(); ctx.translate(ox + SW / 2, cy); ctx.rotate(ang); const L = SW * 1.4 * Math.min(1, q * 4);
          ctx.fillStyle = `rgba(${U.col[1]},${al * .6})`; ctx.fillRect(-L / 2, -14 * u * (1 - q), L, 28 * u * (1 - q)); ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.fillRect(-L / 2, -3 * u, L, 6 * u); ctx.restore(); }
        const list = f.vic.length ? f.vic : [{ x: hero.x + 40, y: hero.y }, { x: hero.x - 40, y: hero.y - 20 }];
        for (const mm of list) { const [sx, sy] = W2S(mm.x, mm.y); const w = (22 + (i % 2) * 8) * u * (1 - q * .5);
          const gr = ctx.createLinearGradient(0, oy, 0, sy); gr.addColorStop(0, `rgba(${U.col[2]},0)`); gr.addColorStop(.7, `rgba(${U.col[1]},${al * .7})`); gr.addColorStop(1, `rgba(${U.col[0]},${al})`);
          ctx.fillStyle = gr; ctx.fillRect(sx - w / 2, oy, w, sy - oy); ctx.fillStyle = `rgba(255,255,255,${al})`; ctx.fillRect(sx - w * .18, oy, w * .36, sy - oy);
          ctx.fillStyle = `rgba(${U.col[1]},${al * .8})`; ctx.beginPath(); ctx.ellipse(sx, sy, w * 1.8 * (.6 + q), w * .6 * (.6 + q), 0, 0, TAU); ctx.fill(); } }
      ctx.globalCompositeOperation = 'source-over'; }
    if (c >= 0 && c < f.ci && (f.cut === 'zoom' || f.cut === 'hybrid')) drawCutZoom(f, U, c / f.ci, u, ox, oy, SW, SH);
    if (c >= 0 && c < f.ci && (f.cut === 'eye' || (f.cut === 'hybrid' && c / f.ci > .45))) drawCutEye(f, U, f.cut === 'hybrid' ? (c / f.ci - .45) / .55 : c / f.ci, u, ox, oy, SW, SH);
    if (c >= 0 && c < f.ci && f.cut === 'band') { const q = c / f.ci, inn = Math.min(1, q / .15), out = q > .85 ? (q - .85) / .15 : 0, bh = SH * .34 * inn * (1 - out), by = oy + SH * .5;
      ctx.fillStyle = 'rgba(0,0,0,.55)'; ctx.fillRect(ox, oy, SW, SH);
      ctx.save(); ctx.translate(ox + SW / 2, by); ctx.rotate(-.06); ctx.fillStyle = '#07070c'; ctx.fillRect(-SW, -bh / 2, SW * 2, bh); const lw = Math.max(2, SH * .006);
      ctx.fillStyle = U.band; ctx.fillRect(-SW, -bh / 2, SW * 2, lw); ctx.fillRect(-SW, bh / 2 - lw, SW * 2, lw);
      const im = porImg(U.por);
      if (im.complete && im.naturalWidth) { const ih = bh * 1.25, iw = ih * im.naturalWidth / im.naturalHeight, ease = 1 - Math.pow(1 - Math.min(1, q / .3), 3), px = SW * .75 - ease * SW * .68 + q * SW * .04;
        ctx.save(); ctx.beginPath(); ctx.rect(-SW, -bh / 2, SW * 2, bh); ctx.clip(); ctx.imageSmoothingEnabled = false; ctx.drawImage(im, px - SW / 2, -ih * .42, iw, ih); ctx.restore(); }
      ctx.restore();
      const tx = ox + SW * .62 - (1 - Math.min(1, q / .25)) * SW * .3, fs = Math.round(SH * .085); ctx.globalAlpha = Math.min(1, q / .2) * (1 - out);
      textOut(U.name, tx, by + fs * .25, fs, U.band); textOut((U.label || U.route + ' 필살기') + ' · ' + U.en, tx, by + fs * .25 + SH * .05, Math.round(SH * .026), '#fff'); ctx.globalAlpha = 1; }
    drawUlt2(f, U, e, u, ox, oy, SW, SH);
    if (e >= 0 && e < .25) { ctx.fillStyle = U.whole && f.fx && f.fx !== 'pillar' ? `rgba(20,0,48,${.75 * (1 - e / .25)})` : `rgba(255,255,255,${.6 * (1 - e / .25)})`; ctx.fillRect(ox, oy, SW, SH); } // 심연: darkness falls instead of a white flash // softer flash than the town (.9)
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
  const FPSEL = Q.has('fps') ? Object.assign(document.body.appendChild(document.createElement('div')), { style: 'position:fixed;left:6px;bottom:6px;z-index:70;font:12px monospace;color:#9f9;background:#000a;padding:2px 5px' }) : null; let fpsN = 0, fpsT = 0, fpsW = 0; // ?fps: frames per second on any device (worst frame in ms)
  function frame(t) {
    const dt = Math.min(.1, (t - last) / 1000 || 0); last = t;
    if (FPSEL) { fpsN++; fpsW = Math.max(fpsW, dt * 1000); if (t - fpsT > 1000) { FPSEL.textContent = Math.round(fpsN * 1000 / (t - fpsT)) + ' fps · 최악 ' + Math.round(fpsW) + 'ms'; fpsN = 0; fpsT = t; fpsW = 0; } }
    if (!manual) { if (S.scene === 'town' && !S.trans) watchTown(); else { acc += dt; let n = 0; while (acc >= DT && n < 6) { step(DT); acc -= DT; n++; } if (n >= 6) acc = 0; } }
    if (S.scene !== 'town' || S.trans) render();
    publish();
    requestAnimationFrame(frame);
  }
  window.__worldHooks = { hudY: () => S.hudY, S, M, MAPS, loadMap, aliasPt, renderGround, hero, get SAVE() { return SAVE; }, save, go, takePress, isHeld, held, queue, codesOf, keyHint, textOut, panel, font, W2S, ctx, cv, drawSpr, msg, banner, giveLoot, addFx, syncTownHp, LW, LH, TAU, get IMG() { return IMG; }, get ATLAS() { return ATLAS; }, ready };
  const W_API = window.__world = { mobApi: W, /* test: the helper object mobs get (force a boss move) */ replayScene: (k, d) => { delete SAVE.flags["scene_" + k]; playScene(k, d || 0); }, /* test: replay a 1장 scene */
    WORLD_ZOOM, LW, LH, ROLL, ready: false, hero, S, get SAVE() { return SAVE; }, get scene() { return S.scene; }, get map() { return S.map; }, get mobs() { return S.mobs; }, get trans() { return S.trans; },
    go, dirTap, hitMob, RUN, SWING, swingR, hbR, hbA, spOf, arcW, setManual(v) { manual = v; }, cell8() { const c = h8Cell(); return c && [c.h8, c[0], c[1], c[2], c[3], c[4], c[5], c.fl ? 1 : 0, c.ox || 0]; },
    advance(sec) { for (let t = 0; t < sec - 1e-9; t += DT) { if (S.scene === 'town' && !S.trans) watchTown(); else step(DT); } render(); publish(); },
    key(code, down) { if (down) { if (!held.has(code)) queue.push(code); held.add(code); } else held.delete(code); },
    tap(code) { queue.push(code); },
    flag(id, v = true) { SAVE.flags[id] = v; save(); }, reset() { SAVE = { flags: {}, chests: {}, keys: {}, opened: {}, levers: {}, visited: {}, explored: {}, waystones: {}, landmarks: {}, quests: {}, pin: null, dest: null }; save(); if (NAV()) NAV().reset(); },
    get nav() { return NAV(); },
    killAll(filter) { S.mobs.filter(m => !m.dead && (!filter || filter(m))).forEach(killMob); },
    home() { S.pause = false; if (Q.has('old')) go('town', null, { card: false }); else go('felt', 'default', { card: false }); },
    hurt, spawn, render, tile: () => [Math.floor(hero.x / S.map.T), Math.floor(hero.y / S.map.T)],
    setHeroTile(x, y, face) { hero.x = (x + .5) * S.map.T; hero.y = (y + .5) * S.map.T; if (face) hero.face = face; snapCam(); },
    interact, LAST_STAND, castAbyss, castUlt, get ultFx() { return S.ultFx; }, get hazards() { return S.hazards; }, get boss() { return S.bossRef; }, get objs() { return S.map && S.map.objs; },
  };
  // ?go=world | field00..field09 | dungeon01_b1 ... : start straight in that scene instead of the town (owner 10-22 "실행할수 있게")
  const GO = new URLSearchParams(location.search).get('go');
  if (GO) ready.then(() => { const t = setInterval(() => { if (!window.__game) return; clearInterval(t); go(GO, 'default'); }, 100); });
  ready.then(() => { W_API.ready = true; requestAnimationFrame(t => { last = t; requestAnimationFrame(frame); }); }).catch(e => console.error('[world] init failed', e));
  const START = GO ? null : Q.get('start') || (Q.has('old') ? null : 'felt'); /* ?go= (샌드박스·시험) wins over the Felt start */ // 새 판 (주인 10-23 "최신 저장한 것만, 1장만"): the game opens in Felt; ?old = the previous build (old start village, areas 1-9)
  if (START) { cv.style.background = '#000'; show(true); } // 새 판 starts in the world: black behind the world canvas from boot, so the old town demo never shows through the fade (owner 10-23 「옛날버전 화면이 잠깐」)
  if (START) ready.then(() => { const id = START; let t0 = Date.now(); const tryGo = () => { const g = window.__game, T = window.__titleScreen; if (T && T.active) { t0 = Date.now(); setTimeout(tryGo, 100); return; } /* wait for the title: the map canvas would cover it while it still takes the keys */ const R0 = !Q.get('start') && !Q.has('nosave') && SAVE.resume; /* 이어하기 (owner 10-23): saved in a field -> start there */ if (g && g.ready && (R0 ? (S.pendingHp = R0.hp, S.pendingMsg = '이어하기 — 저장한 곳에서 시작', go(R0.map, 'resume', { card: false })) : go(id, 'default', { card: false }))) return; if (Date.now() - t0 < 8000) setTimeout(tryGo, 100); }; tryGo(); }); // ?start=felt: begin in a map scene (dev / test)
})();
