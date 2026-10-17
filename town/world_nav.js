/* =====================================================================
 *  world_nav.js — navigation for the outside world (Ys-style seamless fields)
 *   - exploration fog per map (saved), corner minimap (V: small / large / off), full map screen (M)
 *   - objectives (G cycles: current quest / town / dungeon / pin / off), pins (P on the map screen)
 *   - route finding: area-level Dijkstra over map exits (maps/index.json) + tile A* inside the current map
 *     (preallocated typed arrays, resumable with a node budget per frame, recomputed only when needed)
 *   - guide breadcrumbs on the ground + route on the minimap + edge-of-screen arrow with distance
 *   - quests (maps/quests.json): NPC markers ! / ?, talk(), rewards; landmarks; waystone fast travel
 *  world.js calls: onEnter(map), step(dt), screenStep(dt) -> paused?, drawGround(g,cx,cy), drawHud(k,ox,oy,u), talk(npc), reset()
 *  Data-driven: new areas only need map JSON (exits/waystones/npcs/landmarks) + an entry in maps/index.json. See WORLD.md.
 * ===================================================================== */
(function () {
  'use strict';
  const H = () => window.__worldHooks;
  const NAV_BUDGET = 900;        // A* node expansions per frame (incremental search)
  const REPLAN_EVERY = 0.25;     // s between off-route checks
  const OFF_ROUTE = 2.5;         // tiles away from the route => replan
  const FOG_R = { field: 8, dungeon: 5, boss: 7 };
  const MINI = [{ w: 112, h: 76, tile: 3 }, { w: 216, h: 140, tile: 0 }]; // display units (u); tile 0 = fit the whole map
  let IDX = null, QUESTS = [], QBY = {}, booted = false;
  const NM = {};                 // per-map nav data: { portals, markers, fog, img, mini, cost }
  const st = { miniMode: 0, screen: null, uiA: .65, uiT: 0, dirty: true, checkT: 0, periodicT: 0, goal: null, extra: 0, label: '', destKey: '', noRoute: false, lastTile: -1 };

  // ---------------- boot ----------------
  const getJSON = u => fetch(u).then(r => { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); });
  function boot() {
    const h = H(); if (!h) { setTimeout(boot, 50); return; }
    h.ready.then(() => Promise.all([getJSON('maps/index.json'), getJSON('maps/quests.json')])).then(([idx, q]) => {
      IDX = idx; QUESTS = q.quests || []; for (const x of QUESTS) QBY[x.id] = x;
      return Promise.all(idx.maps.map(id => h.loadMap(id).then(m => navData(m))));
    }).then(() => { booted = true; st.dirty = true; }).catch(e => console.error('[nav] boot', e));
  }
  boot();

  // ---------------- per-map nav data ----------------
  const COL = { water: [58, 120, 200], water2: [58, 120, 200], water_deep: [40, 90, 170], bridge_h: [160, 112, 64], stones: [150, 150, 150], dirt: [214, 186, 128], dirt_pebble: [214, 186, 128],
    sand: [226, 206, 150], tallgrass: [62, 118, 48], cliff: [110, 92, 72], soil: [130, 100, 70], floor: [138, 143, 154], floor2: [138, 143, 154], floor_moss: [118, 140, 110], floor_moss2: [118, 140, 110], floor_crack: [128, 132, 140] };
  const DECO = { tree: [34, 80, 42], pine: [30, 70, 38], boulder: [128, 128, 128], rocks: [128, 128, 128], bush: [52, 100, 44], stump: [100, 80, 50], fence: [140, 100, 60], pillar: [170, 165, 150], crystal: [120, 230, 200] };
  function cellColor(m, c, i) {
    if (c.deco && m.solidG[i] && DECO[c.deco]) return DECO[c.deco];
    if (c.obj === 'pit') return [8, 8, 10]; if (c.obj === 'spikes') return [170, 90, 90];
    if (c.g && c.g.startsWith('wall')) return [42, 44, 54];
    if (COL[c.g]) return COL[c.g]; if (c.g && c.g.startsWith('grass')) return [80, 138, 58];
    return m.solidG[i] ? [60, 60, 66] : [90, 130, 70];
  }
  function navData(m) {
    if (NM[m.id]) return NM[m.id];
    const n = m.w * m.h, d = NM[m.id] = { id: m.id, fog: new Uint8Array(n), cost: new Uint8Array(n), portals: [], markers: [] };
    // colours + cost grid (0 blocked, 200 = door: passable at a price, so the route can lead to a locked door / the boss door)
    const mini = document.createElement('canvas'); mini.width = m.w; mini.height = m.h; d.mini = mini; d.mctx = mini.getContext('2d');
    d.base = new Uint8ClampedArray(n * 4); d.img = d.mctx.createImageData(m.w, m.h);
    for (let i = 0; i < n; i++) { const c = m.cells[i], col = cellColor(m, c, i); d.base[i * 4] = col[0]; d.base[i * 4 + 1] = col[1]; d.base[i * 4 + 2] = col[2]; d.base[i * 4 + 3] = 255;
      d.cost[i] = m.solidG[i] ? 0 : (c.g === 'tallgrass' ? 2 : 1); if (c.obj === 'pit' || c.obj === 'spikes') d.cost[i] = 9; }
    for (const o of m.objs) { const i = Math.floor(o.ty) * m.w + Math.floor(o.tx);
      if (o.type === 'door_locked' || o.type === 'gate' || o.type === 'boss_door') d.cost[i] = 200;
      if (o.type === 'exit') for (let y = o.ty; y < o.ty + (o.h || 1); y++) for (let x = o.tx; x < o.tx + (o.w || 1); x++) d.cost[y * m.w + x] = 0; // never path through an exit by accident
      if (o.type === 'stairs_up' || o.type === 'stairs_down') d.cost[i] = 0; }
    // portals (area graph edges) + static markers
    for (const o of m.objs) {
      let p = null;
      if (o.type === 'exit') p = { x: o.tx + Math.floor((o.w || 1) / 2), y: o.ty + Math.floor((o.h || 1) / 2), to: o.to, spawn: o.spawn, label: o.label };
      if ((o.type === 'stairs_up' || o.type === 'stairs_down') && m.links && m.links[o.type]) p = { x: o.tx, y: o.ty, to: m.links[o.type].to, spawn: m.links[o.type].spawn, label: o.type === 'stairs_up' ? '위층' : '아래층' };
      if (o.type === 'boss_door' && m.links && m.links.boss_door) p = { x: o.tx, y: o.ty, to: m.links.boss_door.to, spawn: m.links.boss_door.spawn, label: '골렘의 방' };
      if (p) { d.portals.push(p); d.markers.push({ kind: p.to === 'town' ? 'town' : (/^dungeon|^boss/.test(p.to) && m.type === 'field' ? 'dungeon' : (o.type === 'boss_door' ? 'boss' : 'exit')), x: p.x, y: p.y, label: p.label || p.to, portal: p }); }
      if (o.type === 'waystone') d.markers.push({ kind: 'waystone', x: o.tx, y: o.ty, label: o.name, id: o.id });
      if (o.type === 'npc') d.markers.push({ kind: 'npc', x: o.tx, y: o.ty, label: o.name, id: o.id, npc: o });
      if (o.type === 'landmark') d.markers.push({ kind: 'landmark', x: o.tx, y: o.ty, label: o.name, id: o.id });
    }
    loadFog(m, d); return d;
  }
  function loadFog(m, d) { const s = H().SAVE.explored[m.id]; if (!s) return; try { const b = atob(s); for (let i = 0; i < d.fog.length; i++) d.fog[i] = (b.charCodeAt(i >> 3) >> (i & 7)) & 1; } catch (e) {} paintFog(m, d); }
  function saveFog(m, d) { let out = ''; for (let i = 0; i < d.fog.length; i += 8) { let v = 0; for (let k = 0; k < 8; k++) if (d.fog[i + k]) v |= 1 << k; out += String.fromCharCode(v); } H().SAVE.explored[m.id] = btoa(out); d.fogDirty = false; }
  function paintFog(m, d) { const a = d.img.data, b = d.base; for (let i = 0; i < d.fog.length; i++) { const j = i * 4; if (d.fog[i]) { a[j] = b[j]; a[j + 1] = b[j + 1]; a[j + 2] = b[j + 2]; a[j + 3] = 255; } else a[j + 3] = 0; } d.mctx.putImageData(d.img, 0, 0); }
  function reveal(m, d, tx, ty) {
    const R = FOG_R[m.type] || 6; let changed = false;
    for (let y = Math.max(0, ty - R); y <= Math.min(m.h - 1, ty + R); y++) for (let x = Math.max(0, tx - R); x <= Math.min(m.w - 1, tx + R); x++) {
      const i = y * m.w + x; if (!d.fog[i] && (x - tx) * (x - tx) + (y - ty) * (y - ty) <= R * R) { d.fog[i] = 1; changed = true; const j = i * 4, a = d.img.data; a[j] = d.base[j]; a[j + 1] = d.base[j + 1]; a[j + 2] = d.base[j + 2]; a[j + 3] = 255; } }
    if (changed) { d.mctx.putImageData(d.img, 0, 0); d.fogDirty = true; }
  }

  // ---------------- A* (preallocated, resumable) ----------------
  let CAP = 0, G, F, PAR, OPEN, CLOSED, HEAP, HN = 0, STAMP = 0;
  let PX = new Int16Array(4096), PY = new Int16Array(4096), PN = 0, PI0 = 0; // current path (tiles), progress index
  const srch = { on: false, m: null, d: null, goal: -1, sx: 0, sy: 0, gx: 0, gy: 0, best: -1, bestH: 1e9 };
  function ensureCap(n) { if (n <= CAP) return; CAP = n; G = new Float32Array(n); F = new Float32Array(n); PAR = new Int32Array(n); OPEN = new Uint32Array(n); CLOSED = new Uint32Array(n); HEAP = new Int32Array(n * 2); STAMP = 0; }
  function hpush(i) { let k = HN++; HEAP[k] = i; while (k > 0) { const p = (k - 1) >> 1; if (F[HEAP[p]] <= F[HEAP[k]]) break; const t = HEAP[p]; HEAP[p] = HEAP[k]; HEAP[k] = t; k = p; } }
  function hpop() { const top = HEAP[0]; HEAP[0] = HEAP[--HN]; let k = 0; for (;;) { const l = k * 2 + 1, r = l + 1; let s = k; if (l < HN && F[HEAP[l]] < F[HEAP[s]]) s = l; if (r < HN && F[HEAP[r]] < F[HEAP[s]]) s = r; if (s === k) break; const t = HEAP[s]; HEAP[s] = HEAP[k]; HEAP[k] = t; k = s; } return top; }
  const octile = (ax, ay, bx, by) => { const dx = Math.abs(ax - bx), dy = Math.abs(ay - by); return Math.max(dx, dy) + .4142 * Math.min(dx, dy); };
  function startSearch(m, d, sx, sy, gx, gy) {
    ensureCap(m.w * m.h); STAMP++; HN = 0;
    Object.assign(srch, { on: true, m, d, sx, sy, gx, gy, goal: gy * m.w + gx, best: -1, bestH: 1e9 });
    const s = sy * m.w + sx; G[s] = 0; F[s] = octile(sx, sy, gx, gy); PAR[s] = -1; OPEN[s] = STAMP; hpush(s);
  }
  const DX = new Int8Array([1, -1, 0, 0, 1, -1, 1, -1]), DY = new Int8Array([0, 0, 1, -1, 1, 1, -1, -1]); // 4 orthogonal + 4 diagonal
  function runSearch(budget) {
    const m = srch.m, d = srch.d, W = m.w, Hh = m.h, cost = d.cost, solid = m.solidG;
    const pass = (x, y) => { if (x < 0 || y < 0 || x >= W || y >= Hh) return 0; const i = y * W + x; if (i === srch.goal) return 1; const c = cost[i]; return c === 200 ? (solid[i] ? 20 : 1) : c; };
    while (budget-- > 0) {
      if (!HN) { srch.on = false; return finish(srch.best); }           // unreachable: go as close as we got
      const cur = hpop(); if (CLOSED[cur] === STAMP) continue; CLOSED[cur] = STAMP;
      const cx = cur % W, cy = (cur / W) | 0;
      const hh = octile(cx, cy, srch.gx, srch.gy); if (hh < srch.bestH) { srch.bestH = hh; srch.best = cur; }
      if (cur === srch.goal) { srch.on = false; return finish(cur); }
      for (let k = 0; k < 8; k++) { const dx = DX[k], dy = DY[k];
        const nx = cx + dx, ny = cy + dy, c = pass(nx, ny); if (!c) continue;
        if (dx && dy && (!pass(cx + dx, cy) || !pass(cx, cy + dy))) continue; // no corner cutting
        const ni = ny * W + nx, ng = G[cur] + c * (dx && dy ? 1.4142 : 1);
        if (CLOSED[ni] === STAMP) continue;
        if (OPEN[ni] !== STAMP || ng < G[ni]) { OPEN[ni] = STAMP; G[ni] = ng; F[ni] = ng + octile(nx, ny, srch.gx, srch.gy); PAR[ni] = cur; hpush(ni); } }
    }
    return false;
  }
  function finish(end) {
    PN = 0; if (end < 0) { st.noRoute = true; return true; }
    const W = srch.m.w; let n = 0; for (let i = end; i >= 0 && n < 4096; i = PAR[i]) n++;
    PN = n; let k = n - 1; for (let i = end; i >= 0 && k >= 0; i = PAR[i], k--) { PX[k] = i % W; PY[k] = (i / W) | 0; }
    PI0 = 0; st.noRoute = end !== srch.goal; st.pathLen = 0; for (let i = 1; i < PN; i++) st.pathLen += Math.hypot(PX[i] - PX[i - 1], PY[i] - PY[i - 1]);
    return true;
  }

  // ---------------- quests ----------------
  const qs = id => H().SAVE.quests[id];
  const flagsOk = q => (q.need && q.need.flags || []).every(f => H().SAVE.flags[f]);
  const avail = q => !qs(q.id) && (q.requires || []).every(r => qs(r) === 'done');
  function npcMark(id) { let mk = null;
    for (const q of QUESTS) { if (q.giver !== id) continue; const s = qs(q.id);
      if (s === 'active' && flagsOk(q)) return '?'; if (avail(q)) mk = '!'; else if (s === 'active' && !mk) mk = '…'; }
    return mk; }
  function findNpc(id) { for (const mid in NM) for (const mk of NM[mid].markers) if (mk.kind === 'npc' && mk.id === id) return { map: mid, x: mk.x, y: mk.y + 1, label: mk.label }; return null; }
  function questGoal(q) {
    if (!q || qs(q.id) === 'done') return null;
    if (!qs(q.id) || flagsOk(q)) { const n = findNpc(q.giver); return n && Object.assign(n, { label: (flagsOk(q) && qs(q.id) ? '보고: ' : '') + n.label, quest: q }); }
    const S = H().SAVE;
    for (const t of q.targets || []) { if (t.untilFlag && S.flags[t.untilFlag]) continue; if (t.untilMapVisited && S.visited[t.untilMapVisited]) continue; return { map: t.map, x: t.x, y: t.y, label: t.label, quest: q }; }
    return null;
  }
  function talk(o) {
    const h = H();
    for (const id of o.quests || []) { const q = QBY[id]; if (q && qs(id) === 'active' && flagsOk(q)) { h.SAVE.quests[id] = 'done'; const got = h.giveLoot(q.reward || []); h.save(); h.banner('퀘스트 완료: ' + q.title, 2.2); st.dirty = true; return q.done + (got ? '\n보상: ' + got : ''); } }
    for (const id of o.quests || []) { const q = QBY[id]; if (q && qs(id) === 'active') return q.progress; }
    for (const id of o.quests || []) { const q = QBY[id]; if (q && avail(q)) { h.SAVE.quests[id] = 'active'; h.SAVE.dest = { type: 'quest', id }; h.save(); h.banner('퀘스트 수락: ' + q.title, 2.2, true); st.dirty = true; return q.offer + '\n(목표가 지도와 미니맵에 표시된다 · G: 목표 전환)'; } }
    return o.idle || '…';
  }

  // ---------------- objectives ----------------
  function autoGoal() {
    for (const q of QUESTS) if (qs(q.id) === 'active') { const g = questGoal(q); if (g) return g; }
    for (const q of QUESTS) if (avail(q)) { const g = questGoal(q); if (g) return g; }
    const t = IDX && IDX.destinations.find(d => d.kind === 'dungeon'); return t && !H().SAVE.flags.boss01 ? Object.assign({}, t) : null;
  }
  function currentDest() {
    const S = H().SAVE, d = S.dest;
    if (!IDX) return null;
    if (!d) return autoGoal();
    if (d.type === 'off') return null;
    if (d.type === 'quest') return questGoal(QBY[d.id]) || autoGoal();
    if (d.type === 'dest') { const t = IDX.destinations.find(x => x.id === d.id); return t ? Object.assign({}, t) : null; }
    if (d.type === 'pin') return S.pin ? { map: S.pin.map, x: S.pin.x, y: S.pin.y, label: '핀' } : null;
    if (d.type === 'marker') return { map: d.map, x: d.x, y: d.y, label: d.label };
    return null;
  }
  function cycleDest() {
    const S = H().SAVE, list = [null].concat(IDX.destinations.map(t => ({ type: 'dest', id: t.id })));
    if (S.pin) list.push({ type: 'pin' }); list.push({ type: 'off' });
    const key = JSON.stringify(S.dest || null); let i = list.findIndex(x => JSON.stringify(x) === key); i = (i + 1) % list.length;
    S.dest = list[i]; H().save(); st.dirty = true;
    const g = currentDest(); H().banner('목표: ' + (S.dest && S.dest.type === 'off' ? '없음 (안내 끔)' : (g ? g.label : '없음')) + (S.dest ? '' : '  (자동 · 퀘스트)'), 1.6, true);
  }
  // area-level route: Dijkstra over maps (arrival points), first portal out of the current map
  function areaRoute(m, fx, fy, dest) {
    const front = [{ map: m.id, x: fx, y: fy, cost: 0, first: null }], done = {}; let best = null;
    while (front.length) {
      let bi = 0; for (let i = 1; i < front.length; i++) if (front[i].cost < front[bi].cost) bi = i; const n = front.splice(bi, 1)[0];
      if (n.map === dest.map) { const c = n.cost + Math.hypot(n.x - dest.x, n.y - dest.y); if (!best || c < best.cost) best = { cost: c, first: n.first, firstCost: n.firstCost }; continue; }
      if (done[n.map]) continue; done[n.map] = 1;
      const d = NM[n.map], M2 = H().MAPS; if (!d) continue;
      for (const p of d.portals) { const tm = M2[p.to]; if (!tm) continue; const sp = (tm.spawns && (tm.spawns[p.spawn] || tm.spawns.default)) || [tm.w / 2, tm.h / 2];
        const c = n.cost + Math.hypot(n.x - p.x, n.y - p.y) + 2; front.push({ map: p.to, x: sp[0], y: sp[1], cost: c, first: n.first || p, firstCost: n.first ? n.firstCost : c }); }
    }
    return best;
  }
  function plan() {
    const h = H(), m = h.M(); if (!m || !NM[m.id] || m.type === 'world') return;
    const d = NM[m.id], dest = currentDest(); st.dest = dest; st.dirty = false; st.periodicT = 3;
    const tx = Math.floor(h.hero.x / m.T), ty = Math.floor(h.hero.y / m.T);
    if (!dest) { st.goal = null; PN = 0; srch.on = false; return; }
    let gx, gy, extra = 0, lbl = dest.label;
    if (dest.map === m.id) { gx = dest.x; gy = dest.y; }
    else { const r = areaRoute(m, tx, ty, dest); if (!r || !r.first) { st.goal = null; PN = 0; srch.on = false; st.noRoute = true; return; }
      gx = r.first.x; gy = r.first.y; extra = Math.max(0, r.cost - r.firstCost); lbl = dest.label; st.via = r.first.label; }
    if (dest.map === m.id) st.via = null;
    gx = Math.max(0, Math.min(m.w - 1, Math.round(gx))); gy = Math.max(0, Math.min(m.h - 1, Math.round(gy)));
    st.goal = { x: gx, y: gy, final: dest.map === m.id }; st.extra = extra; st.label = lbl;
    startSearch(m, d, Math.max(0, Math.min(m.w - 1, tx)), Math.max(0, Math.min(m.h - 1, ty)), gx, gy);
  }

  // ---------------- per-frame ----------------
  function onEnter(m) { const d = navData(m); st.dirty = true; PN = 0; srch.on = false; st.lastTile = -1; if (d && m.type !== 'world') reveal(m, d, Math.floor(H().hero.x / m.T), Math.floor(H().hero.y / m.T)); }
  function tapCode(code) { const q = H().queue, i = q.indexOf(code); if (i < 0) return false; q.splice(i, 1); return true; }
  function step(dt) {
    const h = H(), m = h.M(); if (!booted || !m || m.type === 'world') return; const d = NM[m.id] || navData(m);
    if (tapCode('KeyV')) { st.miniMode = (st.miniMode + 1) % 3; h.banner('미니맵: ' + ['작게', '크게', '끔'][st.miniMode], 1, true); }
    if (tapCode('KeyG')) cycleDest();
    const tx = Math.floor(h.hero.x / m.T), ty = Math.floor(h.hero.y / m.T), ti = ty * m.w + tx;
    if (ti !== st.lastTile) { st.lastTile = ti; reveal(m, d, tx, ty);
      for (const mk of d.markers) if (mk.kind === 'landmark' && !h.SAVE.landmarks[mk.id] && Math.abs(mk.x - tx) + Math.abs(mk.y - ty) <= 4) { h.SAVE.landmarks[mk.id] = true; h.save(); h.banner('발견 — ' + mk.label, 1.8, true); } }
    st.fogT = (st.fogT || 0) - dt; if (st.fogT <= 0 && d.fogDirty) { st.fogT = 3; saveFog(m, d); h.save(); }
    // objective changed (quest progress, flags)?
    const dest = currentDest(), key = dest ? dest.map + ':' + dest.x + ',' + dest.y : '';
    if (key !== st.destKey) { st.destKey = key; st.dirty = true; }
    st.periodicT -= dt; if (st.periodicT <= 0 && !srch.on) st.dirty = true;   // doors may have opened
    if (srch.on) runSearch(NAV_BUDGET);
    else if (st.dirty) { plan(); if (srch.on) runSearch(NAV_BUDGET); }
    // progress along the path + off-route check (throttled)
    if (PN) { while (PI0 < PN - 1 && Math.abs(PX[PI0 + 1] - tx) + Math.abs(PY[PI0 + 1] - ty) <= Math.abs(PX[PI0] - tx) + Math.abs(PY[PI0] - ty)) PI0++; }
    st.checkT -= dt; if (st.checkT <= 0 && PN && !srch.on) { st.checkT = REPLAN_EVERY; let best = 1e9;
      for (let i = Math.max(0, PI0 - 2); i < Math.min(PN, PI0 + 14); i++) { const dd = Math.hypot(PX[i] - tx, PY[i] - ty); if (dd < best) best = dd; }
      if (best > OFF_ROUTE) st.dirty = true; }
  }
  function remaining() { let r = 0; for (let i = PI0 + 1; i < PN; i++) r += Math.abs(PX[i] - PX[i - 1]) + Math.abs(PY[i] - PY[i - 1]) > 1 ? 1.4142 : 1; return r + st.extra; }

  // ---------------- drawing: ground breadcrumbs (low-res, world coords) ----------------
  function drawGround(g) {
    const h = H(), m = h.M(); if (!PN || !m || srch.on) return; const T = m.T, t = h.S.t, end = Math.min(PN, PI0 + 70);
    for (let i = PI0 + 1; i < end; i++) {
      const x = (PX[i] + .5) * T, y = (PY[i] + .5) * T, w = Math.sin(i * .8 - t * 7);
      const a = (.28 + .5 * Math.max(0, w)) * Math.min(1, (end - i) / 12);
      g.globalAlpha = a; g.fillStyle = '#3a1c00'; g.fillRect(x - 2, y - 2, 5, 4);
      g.fillStyle = '#ffe680'; g.fillRect(x - 1, y - 1, 3, 2);
      if (w > .8) { g.fillStyle = '#ffffff'; g.fillRect(x - 1, y - 1, 1, 1); } g.globalAlpha = 1;
    }
    if (st.goal && st.goal.final) { const x = (st.goal.x + .5) * T, y = (st.goal.y + .5) * T, b = Math.sin(t * 5) * 2; // target ring on the ground
      g.strokeStyle = `rgba(255,216,74,${.55 + .3 * Math.sin(t * 5)})`; g.lineWidth = 1; g.beginPath(); g.ellipse(x, y + 4, 8 + b * .5, 3.5, 0, 0, h.TAU); g.stroke(); }
  }

  // ---------------- drawing: HUD (display resolution) ----------------
  function uiAlpha() { const h = H(); if (h.S.t - st.uiT > 1 || !st.uiT) { st.uiT = h.S.t || .01; const v = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--ui-alpha')); st.uiA = isFinite(v) ? v : .65; } return st.uiA; }
  const MKCOL = { town: '#ffffff', dungeon: '#ff9a5a', boss: '#ff5a4a', exit: '#ffe08a', waystone: '#7fe8ff', npc: '#ffffff', landmark: '#c8f0a0', target: '#ffd84a', pin: '#ff4a6a' };
  function icon(c, kind, x, y, r, on) {
    c.save(); c.translate(x, y); c.lineWidth = Math.max(1, r / 3); c.strokeStyle = 'rgba(0,0,0,.85)'; c.fillStyle = MKCOL[kind] || '#fff';
    if (kind === 'town') { c.beginPath(); c.moveTo(-r, 0); c.lineTo(0, -r); c.lineTo(r, 0); c.lineTo(r * .7, 0); c.lineTo(r * .7, r * .8); c.lineTo(-r * .7, r * .8); c.lineTo(-r * .7, 0); c.closePath(); c.stroke(); c.fill(); }
    else if (kind === 'dungeon' || kind === 'boss') { c.beginPath(); c.moveTo(-r, r * .8); c.lineTo(-r, -r * .2); c.arc(0, -r * .2, r, Math.PI, 0); c.lineTo(r, r * .8); c.closePath(); c.stroke(); c.fill(); c.fillStyle = '#301008'; c.fillRect(-r * .35, -r * .1, r * .7, r * .9); }
    else if (kind === 'waystone') { c.globalAlpha *= on ? 1 : .55; c.beginPath(); c.moveTo(0, -r); c.lineTo(r * .7, 0); c.lineTo(0, r); c.lineTo(-r * .7, 0); c.closePath(); c.stroke(); c.fill(); }
    else if (kind === 'exit') { c.beginPath(); c.arc(0, 0, r * .6, 0, Math.PI * 2); c.stroke(); c.fill(); }
    else if (kind === 'landmark') { c.beginPath(); for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + i * Math.PI * 2 / 5; c.lineTo(Math.cos(a) * r * .8, Math.sin(a) * r * .8); c.lineTo(Math.cos(a + .63) * r * .35, Math.sin(a + .63) * r * .35); } c.closePath(); c.stroke(); c.fill(); }
    else if (kind === 'target') { c.beginPath(); for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + i * Math.PI * 2 / 5; c.lineTo(Math.cos(a) * r, Math.sin(a) * r); c.lineTo(Math.cos(a + .63) * r * .45, Math.sin(a + .63) * r * .45); } c.closePath(); c.stroke(); c.fill(); }
    else if (kind === 'pin') { c.beginPath(); c.arc(0, -r * .5, r * .55, 0, Math.PI * 2); c.moveTo(-r * .3, -r * .2); c.lineTo(0, r); c.lineTo(r * .3, -r * .2); c.stroke(); c.fill(); }
    else { c.beginPath(); c.arc(0, 0, r * .5, 0, Math.PI * 2); c.stroke(); c.fill(); }
    c.restore();
  }
  function heroArrow(c, x, y, r, face) { const a = { up: -Math.PI / 2, down: Math.PI / 2, left: Math.PI, right: 0 }[face] || 0;
    c.save(); c.translate(x, y); c.rotate(a); c.fillStyle = '#ff3a2a'; c.strokeStyle = '#fff'; c.lineWidth = Math.max(1, r / 4); c.beginPath(); c.moveTo(r, 0); c.lineTo(-r * .7, r * .7); c.lineTo(-r * .3, 0); c.lineTo(-r * .7, -r * .7); c.closePath(); c.fill(); c.stroke(); c.restore(); }
  function questMarkText(mk) { return mk.kind === 'npc' ? npcMark(mk.id) : null; }
  // draws one map's explored image + markers + route into a screen rect; (ox,oy) = screen pos of tile (0,0), s = px per tile
  function drawMapLayer(c, m, d, ox, oy, s, o) {
    c.imageSmoothingEnabled = false; c.drawImage(d.mini, ox, oy, m.w * s, m.h * s);
    const h = H(), r = Math.max(4, Math.min(9, s * 1.6)) * (o.big ? 1.25 : 1);
    if (o.route && PN && !srch.on) { c.strokeStyle = 'rgba(255,230,120,.95)'; c.lineWidth = Math.max(1.5, s * .5); c.setLineDash([s * 1.2, s * .8]); c.beginPath();
      for (let i = PI0; i < PN; i++) { const x = ox + (PX[i] + .5) * s, y = oy + (PY[i] + .5) * s; if (i === PI0) c.moveTo(x, y); else c.lineTo(x, y); } c.stroke(); c.setLineDash([]); }
    for (const mk of d.markers) { const seen = d.fog[mk.y * m.w + mk.x] || (mk.kind === 'npc' && npcMark(mk.id)); if (!seen && !o.all) continue;
      const x = ox + (mk.x + .5) * s, y = oy + (mk.y + .5) * s; icon(c, mk.kind, x, y, r, mk.kind !== 'waystone' || h.SAVE.waystones[mk.id]);
      const qm = questMarkText(mk); if (qm) qMark(c, qm, x, y - r * 1.6, r * 1.3);
      if (o.labels) h.textOut(mk.label, x, y - r * 1.4 - (qm ? r * 1.4 : 0), Math.max(9, r * 1.25), mk.kind === 'waystone' && !h.SAVE.waystones[mk.id] ? '#9ab' : '#fff'); }
    const dest = st.dest; if (dest && dest.map === m.id) icon(c, 'target', ox + (dest.x + .5) * s, oy + (dest.y + .5) * s, r * 1.15);
    const P = h.SAVE.pin; if (P && P.map === m.id) icon(c, 'pin', ox + (P.x + .5) * s, oy + (P.y + .5) * s, r * 1.1);
    if (h.M() === m) heroArrow(c, ox + h.hero.x / m.T * s, oy + h.hero.y / m.T * s, r * 1.15, h.hero.face);
  }
  function qMark(c, t, x, y, sz) { const h = H(); h.textOut(t, x, y, sz * 1.3, t === '…' ? '#c8c8d0' : '#ffd84a', '#3a1a00'); }
  function drawMinimap(k, ox, oy, u) {
    const h = H(), m = h.M(), d = NM[m.id]; if (!d || st.miniMode === 2) return; const c = h.ctx, cfg = MINI[st.miniMode];
    const W = cfg.w * u, Hh = cfg.h * u, x0 = ox + h.LW * k - W - 8 * u, y0 = oy + 50 * u;
    c.save(); c.globalAlpha = Math.min(1, uiAlpha() + .2);
    c.fillStyle = 'rgba(8,12,28,.62)'; c.fillRect(x0, y0, W, Hh); c.beginPath(); c.rect(x0 + 2, y0 + 2, W - 4, Hh - 4); c.clip();
    let s, mx, my;
    if (cfg.tile) { s = cfg.tile * u; mx = x0 + W / 2 - h.hero.x / m.T * s; my = y0 + Hh / 2 - h.hero.y / m.T * s; }
    else { s = Math.min((W - 8) / m.w, (Hh - 8) / m.h); mx = x0 + (W - m.w * s) / 2; my = y0 + (Hh - m.h * s) / 2; }
    drawMapLayer(c, m, d, mx, my, s, { route: true, big: !cfg.tile });
    c.restore(); c.save(); c.globalAlpha = Math.min(1, uiAlpha() + .3); c.strokeStyle = '#e2c27a'; c.lineWidth = 2; c.strokeRect(x0 + 1, y0 + 1, W - 2, Hh - 2); c.restore();
    h.textOut('V ' + ['작게', '크게'][st.miniMode] + ' · M 지도', x0 + W - 4 * u, y0 + Hh + 11 * u, 8 * u, 'rgba(230,230,240,.85)', '#000', 'right');
  }
  function drawGuide(k, ox, oy, u) {
    const h = H(), m = h.M(), c = h.ctx, SW = h.LW * k, SH = h.LH * k;
    // objective line (top-left, under the hearts)
    const dest = st.dest, dist = Math.round(remaining());
    if (dest) h.textOut('◆ 목표: ' + st.label + (st.via ? '  (→ ' + st.via + ')' : '') + (PN && !srch.on ? '  ' + dist + 'm' : '') + (st.noRoute ? '  · 길이 막혀 있다' : ''), ox + 12 * u, (h.hudY && h.hudY()) || oy + 38 * u, 10 * u, '#ffe08a', '#000', 'left');
    // quest markers over NPC heads + bobbing target marker
    const d = NM[m.id]; if (d) for (const mk of d.markers) if (mk.kind === 'npc') { const t = npcMark(mk.id); if (!t) continue; const [sx, sy] = h.W2S((mk.x + .5) * m.T, mk.y * m.T - 24 + Math.sin(h.S.t * 4) * 1.5); qMark(c, t, sx, sy, 14 * u); }
    if (!st.goal || srch.on) return;
    const gx = (st.goal.x + .5) * m.T, gy = (st.goal.y + .5) * m.T, [sx, sy] = h.W2S(gx, gy);
    const inX = sx > ox + 10 * u && sx < ox + SW - 10 * u, inY = sy > oy + 10 * u && sy < oy + SH - 10 * u;
    if (inX && inY) { if (st.goal.final) icon(c, 'target', sx, sy - 22 * u + Math.sin(h.S.t * 5) * 3 * u, 7 * u); return; }
    // off-screen: edge arrow pointing at the goal (or the exit that leads there) + distance
    const cx = ox + SW / 2, cy = oy + SH / 2, a = Math.atan2(sy - cy, sx - cx), mX = SW / 2 - 26 * u, mY = SH / 2 - 26 * u;
    const tt = Math.min(Math.abs(mX / (Math.cos(a) || 1e-6)), Math.abs(mY / (Math.sin(a) || 1e-6))), ax = cx + Math.cos(a) * tt, ay = cy + Math.sin(a) * tt;
    c.save(); c.globalAlpha = Math.min(1, uiAlpha() + .3); c.translate(ax, ay); c.rotate(a); const R = 11 * u * (1 + .08 * Math.sin(h.S.t * 6));
    c.fillStyle = '#ffd84a'; c.strokeStyle = '#3a1a00'; c.lineWidth = 2 * u; c.beginPath(); c.moveTo(R, 0); c.lineTo(-R * .6, R * .7); c.lineTo(-R * .25, 0); c.lineTo(-R * .6, -R * .7); c.closePath(); c.stroke(); c.fill(); c.restore();
    h.textOut(dist + 'm', ax - Math.cos(a) * 20 * u, ay - Math.sin(a) * 20 * u + 4 * u, 10 * u, '#fff');
  }
  function drawHud(k, ox, oy, u) {
    const h = H(), m = h.M(); if (!booted || !m) return;
    if (st.screen) { drawScreen(k, ox, oy, u); return; }
    drawGuide(k, ox, oy, u); drawMinimap(k, ox, oy, u);
  }

  // ---------------- full map screen (M): explored region, markers, objective, pins, waystone fast travel ----------------
  function regionOf(m) { if (!IDX) return null; for (const id in IDX.regions) if (IDX.regions[id].maps.includes(m.id)) return Object.assign({ id }, IDX.regions[id]); return { id: m.id, name: m.name, maps: [m.id] }; }
  function regionBounds(reg) { const M2 = H().MAPS; let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const id of reg.maps) { const m = M2[id]; if (!m) continue; const p = m.mapPos || [0, 0]; x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0] + m.w); y1 = Math.max(y1, p[1] + m.h); }
    if (reg.town) { const tm = M2[reg.town.map], p = (tm && tm.mapPos) || [0, 0]; y0 = Math.min(y0, p[1] + reg.town.y - 3); }
    return { x0, y0, x1, y1 }; }
  function screenMarkers(reg) { // [{map, x, y, kind, label, ...}] in map tiles, explored only
    const out = [], M2 = H().MAPS, S = H().SAVE;
    for (const id of reg.maps) { const d = NM[id], m = M2[id]; if (!d || !m) continue;
      for (const mk of d.markers) if (d.fog[mk.y * m.w + mk.x] || (mk.kind === 'npc' && npcMark(mk.id))) out.push(Object.assign({ map: id }, mk)); }
    if (S.pin && reg.maps.includes(S.pin.map)) out.push({ map: S.pin.map, x: S.pin.x, y: S.pin.y, kind: 'pin', label: '핀' });
    return out; }
  function openScreen() { const h = H(), m = h.M(), reg = regionOf(m); if (!reg) return; const p = m.mapPos || [0, 0];
    st.screen = { reg, cx: p[0] + h.hero.x / m.T, cy: p[1] + h.hero.y / m.T, hover: null }; }
  function screenStep(dt) {
    const h = H(), m = h.M(); if (!booted || !m || m.type === 'world') return false;
    if (!st.screen) { if (tapCode('KeyM')) { openScreen(); return true; } return false; }
    const sc = st.screen, sp = (h.held.has('ShiftLeft') || h.held.has('ShiftRight') ? 60 : 24) * dt;
    if (h.isHeld('left')) sc.cx -= sp; if (h.isHeld('right')) sc.cx += sp; if (h.isHeld('up')) sc.cy -= sp; if (h.isHeld('down')) sc.cy += sp;
    const B = regionBounds(sc.reg); sc.cx = Math.max(B.x0, Math.min(B.x1, sc.cx)); sc.cy = Math.max(B.y0, Math.min(B.y1, sc.cy));
    // hovered marker (within 2.5 tiles of the cursor)
    let best = null, bd = 2.5; for (const mk of screenMarkers(sc.reg)) { const p = h.MAPS[mk.map].mapPos || [0, 0], dd = Math.hypot(p[0] + mk.x + .5 - sc.cx, p[1] + mk.y + .5 - sc.cy); if (dd < bd) { bd = dd; best = mk; } }
    sc.hover = best;
    if (tapCode('KeyM') || tapCode('Escape')) { st.screen = null; return true; }
    if (tapCode('KeyG')) cycleDest();
    if (tapCode('KeyP')) { // place / remove a pin at the cursor (and make it the objective)
      const hit = mapAt(sc.reg, sc.cx, sc.cy);
      if (best && best.kind === 'pin') { h.SAVE.pin = null; if (h.SAVE.dest && h.SAVE.dest.type === 'pin') h.SAVE.dest = null; h.banner('핀 제거', 1, true); }
      else if (hit) { h.SAVE.pin = { map: hit.m.id, x: hit.x, y: hit.y }; h.SAVE.dest = { type: 'pin' }; h.banner('핀을 꽂았다 — 목표로 설정', 1.4, true); }
      h.save(); st.dirty = true; }
    const ok = h.codesOf('interact').some(c => tapCode(c)) || tapCode('Enter');
    if (ok && best) {
      if (best.kind === 'waystone' && h.SAVE.waystones[best.id]) { st.screen = null; h.banner('순간이동 — ' + best.label, 1.2, true); h.go(best.map, 'ws:' + best.id, { card: false }); return true; }
      if (best.kind === 'waystone') { h.banner('아직 등록하지 않은 비석이다 (직접 가서 조사)', 1.6, true); }
      else { h.SAVE.dest = { type: 'marker', map: best.map, x: best.x, y: best.y + (best.kind === 'npc' ? 1 : 0), label: best.label }; h.save(); st.dirty = true; h.banner('목표: ' + best.label, 1.4, true); }
    }
    return true;
  }
  function mapAt(reg, rx, ry) { const M2 = H().MAPS; for (const id of reg.maps) { const m = M2[id]; if (!m) continue; const p = m.mapPos || [0, 0], x = Math.floor(rx - p[0]), y = Math.floor(ry - p[1]);
    if (x >= 0 && y >= 0 && x < m.w && y < m.h) return { m, x, y }; } return null; }
  let worldC = null;
  function drawScreen(k, ox, oy, u) {
    const h = H(), c = h.ctx, SW = h.LW * k, SH = h.LH * k, sc = st.screen, reg = sc.reg, M2 = h.MAPS, S = h.SAVE;
    c.save(); c.fillStyle = 'rgba(4,8,20,.9)'; c.fillRect(ox, oy, SW, SH);
    const PW = SW * .7, PH = SH - 70 * u, px = ox + 12 * u, py = oy + 40 * u;
    c.fillStyle = 'rgba(20,30,60,.6)'; c.fillRect(px, py, PW, PH); c.strokeStyle = '#e2c27a'; c.lineWidth = 2; c.strokeRect(px, py, PW, PH);
    const B = regionBounds(reg), s = Math.min((PW - 20 * u) / (B.x1 - B.x0), (PH - 20 * u) / (B.y1 - B.y0)), bx = px + (PW - (B.x1 - B.x0) * s) / 2 - B.x0 * s, by = py + (PH - (B.y1 - B.y0) * s) / 2 - B.y0 * s;
    c.beginPath(); c.rect(px + 2, py + 2, PW - 4, PH - 4); c.clip();
    for (const id of reg.maps) { const m = M2[id], d = NM[id]; if (!m || !d) continue; const p = m.mapPos || [0, 0];
      if (S.visited[id]) { c.strokeStyle = 'rgba(226,194,122,.25)'; c.lineWidth = 1; c.strokeRect(bx + p[0] * s, by + p[1] * s, m.w * s, m.h * s); }
      drawMapLayer(c, m, d, bx + p[0] * s, by + p[1] * s, s, { route: h.M() === m, labels: true, big: true }); }
    if (reg.town) { const tm = M2[reg.town.map], p = (tm && tm.mapPos) || [0, 0], x = bx + (p[0] + reg.town.x + .5) * s, y = by + (p[1] + reg.town.y + .5) * s; c.fillStyle = 'rgba(200,170,120,.25)'; c.fillRect(x - 14 * u, y - 8 * u, 28 * u, 14 * u); } // town footprint just north of the gate
    // cursor
    const cx = bx + sc.cx * s, cy = by + sc.cy * s; c.strokeStyle = `rgba(255,255,255,${.6 + .3 * Math.sin(h.S.t * 6)})`; c.lineWidth = 2;
    c.beginPath(); c.moveTo(cx - 10 * u, cy); c.lineTo(cx - 3 * u, cy); c.moveTo(cx + 3 * u, cy); c.lineTo(cx + 10 * u, cy); c.moveTo(cx, cy - 10 * u); c.lineTo(cx, cy - 3 * u); c.moveTo(cx, cy + 3 * u); c.lineTo(cx, cy + 10 * u); c.stroke();
    if (sc.hover) { const hv = sc.hover, ws = hv.kind === 'waystone'; h.textOut(hv.label + (ws ? (S.waystones[hv.id] ? '  [Enter] 순간이동' : '  (미등록)') : '  [Enter] 목표로'), cx, cy + 24 * u, 11 * u, ws ? '#7fe8ff' : '#ffe08a'); }
    c.restore();
    h.textOut('지도 — ' + reg.name, px, oy + 26 * u, 16 * u, '#ffe08a', '#000', 'left');
    // side panel: objective, quests, legend, waystones, world inset
    const qx = px + PW + 12 * u, qw = ox + SW - qx - 10 * u; let y = py + 12 * u; const line = (t, col, sz = 10) => { h.textOut(t, qx, y, sz * u, col, '#000', 'left'); y += (sz + 5) * u; };
    const dest = st.dest; line('목표', '#e2c27a', 11); line(dest ? '◆ ' + dest.label : '— 없음 —', '#fff'); if (PN) line('남은 거리 ' + Math.round(remaining()) + 'm', '#cde');
    y += 4 * u; line('퀘스트', '#e2c27a', 11);
    let any = false; for (const q of QUESTS) { const s2 = S.quests[q.id]; if (!s2) continue; any = true; line((s2 === 'done' ? '✓ ' : flagsOk(q) ? '? ' : '· ') + q.title, s2 === 'done' ? '#8c8' : '#fff', 9); } if (!any) line('(마을 밖 나그네에게 말을 걸어 보자 !)', '#aab', 9);
    y += 4 * u; line('등록한 비석', '#e2c27a', 11); let ws = 0; for (const id in NM) for (const mk of NM[id].markers) if (mk.kind === 'waystone' && S.waystones[mk.id]) { line('◇ ' + mk.label, '#7fe8ff', 9); ws++; } if (!ws) line('(없음)', '#aab', 9);
    // world overview inset (the old world map, now view-only)
    const wm = M2.world; if (wm) { if (!worldC) { worldC = wm.groundC || h.renderGround(wm); wm.groundC = worldC; }
      const iw = qw, ih = iw * wm.ph / wm.pw, ix = qx, iy = oy + SH - 30 * u - ih; c.save(); c.globalAlpha = .9; c.imageSmoothingEnabled = true; c.drawImage(worldC, ix, iy, iw, ih); c.restore();
      c.strokeStyle = '#e2c27a'; c.lineWidth = 1; c.strokeRect(ix, iy, iw, ih); const ks = iw / wm.w;
      for (const n of wm.nodes || []) { const nx = ix + (n.x + .5) * ks, ny = iy + (n.y + .5) * ks, here = n.id === reg.worldNode;
        c.fillStyle = here ? `rgba(255,60,40,${.7 + .3 * Math.sin(h.S.t * 6)})` : (n.locked ? 'rgba(120,120,130,.8)' : '#ffe08a'); c.beginPath(); c.arc(nx, ny, (here ? 3.5 : 2) * u, 0, Math.PI * 2); c.fill(); }
      h.textOut('왕국 전도 (보기 전용)', ix, iy - 4 * u, 9 * u, '#cde', '#000', 'left'); }
    h.textOut('방향키 커서 (Shift 빠르게) · Enter 목표 설정/순간이동 · P 핀 · G 목표 전환 · M/Esc 닫기', ox + SW / 2, oy + SH - 10 * u, 10 * u, 'rgba(230,230,240,.9)');
  }

  function reset() { for (const id in NM) { NM[id].fog.fill(0); const m = H().MAPS[id]; if (m) paintFog(m, NM[id]); } st.dirty = true; st.screen = null; PN = 0; }
  window.WorldNav = { onEnter, step, screenStep, drawGround, drawHud, talk, reset,
    get booted() { return booted; }, get state() { return st; }, get path() { return { n: PN, i0: PI0, x: PX, y: PY, searching: srch.on }; }, currentDest, cycleDest, npcMark, nm: NM,
    setMini(v) { st.miniMode = v; }, get screen() { return st.screen; } };
})();
