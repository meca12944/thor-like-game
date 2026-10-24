/* felt_live.js — Felt's live layer (owner 10-24 「펠트 업그레이드」): everything here is drawn by code each frame, nothing is baked.
 *  - fountain: falling streams + rings + drifting glints over the (now wet) basin, and a quiet looping water sound by distance (SFX2.ambient)
 *  - flicker: 5-8 flames (brazier, forge, plaza lamps, chapel candles) breathe on top of the baked light pools
 *  - code sign planks only where no illustrator sign exists (inn / smith / atelier); the rest are art (maps/src/felt_slots.json)
 *  - story switches for the art slots (show): memorial wall day / night, thread clump whole / cut
 *  - story time of day (3단계): grade per phase, who stands where, south gate shut at night, ash buttons, thread clumps, Gas' dice, Bart's board, memorial wall, ration help, bright BGM after the boss
 * Data = maps/felt.json hd.live (written by tools/hd/build_felt.py). world.js calls FELT_LIVE.props / .over / .grade / .bgm / .show. */
(function () {
  'use strict';
  const TAU = Math.PI * 2, W = () => window.__worldHooks;
  let lastSound = 0;
  const hash = n => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); };
  const noise = (t, s) => .5 + .27 * Math.sin(t * 7.3 + s) + .15 * Math.sin(t * 13.1 + s * 2.7) + .08 * Math.sin(t * 23.7 + s * 5.1); // flame: 3 sines, never in step
  // fountain picture px -> world px
  function fpx(h, F, px, py, T) { return [(h.gx + F.x) * T + (px - F.ax) / F.D, (h.gy + F.y) * T + (py - F.ay) / F.D]; }
  function fountainProp(h) { return h._fq || (h._fq = (h.props || []).find(q => q.id === 'fountain')); }
  function drawFountain(k, h, T) { const w = W(), ctx = w.ctx, S = w.S, F = h.live.fountain, q = fountainProp(h), a0 = q && q._a !== undefined ? q._a : 1, t = S.t;
    const [cx, cy] = fpx(h, F, F.pool[0], F.pool[1], T), rx = F.pool[2] / F.D, ry = F.pool[3] / F.D, [sx, sy] = w.W2S(cx, cy);
    if (F.art) return waterSound(w, cx, cy);                                                    // the illustrator's fountain_water_strip draws the water now (a prop right above fountain.png)
    if (sx < -200 * k || sy < -200 * k || sx > innerWidth * 3 || sy > innerHeight * 3) return;
    const [px, py] = w.W2S(...fpx(h, F, F.ped[0], F.ped[1], T)), prx = F.ped[2] / F.D * k, pry = F.ped[3] / F.D * k;
    ctx.save(); ctx.globalAlpha = a0; ctx.beginPath(); ctx.ellipse(sx, sy, rx * k, ry * k, 0, 0, TAU); ctx.clip(); // stay inside the basin, off the pedestal
    ctx.beginPath(); ctx.rect(sx - rx * k - 4, sy - ry * k - 4, rx * 2 * k + 8, ry * 2 * k + 8); ctx.ellipse(px, py, prx, pry, 0, 0, TAU); ctx.rect(px - prx, py - 200 * k, prx * 2, 200 * k); ctx.clip('evenodd');
    ctx.lineWidth = Math.max(1, k * .5);
    for (const [jx, , jb] of F.jets) { const [bx, by] = w.W2S(...fpx(h, F, jx, jb, T)); // rings spreading where each stream lands
      for (let i = 0; i < 3; i++) { const ph = (t * .55 + i / 3 + jx * .013) % 1, r = (1.5 + ph * 9) * k; ctx.strokeStyle = `rgba(200,226,232,${(.5 * (1 - ph)).toFixed(3)})`; ctx.beginPath(); ctx.ellipse(bx, by, r, r * .38, 0, 0, TAU); ctx.stroke(); } }
    ctx.fillStyle = 'rgba(214,236,240,.55)'; for (let i = 0; i < 34; i++) { // glints drifting round the basin
      const f = hash(i), rr = .35 + .6 * hash(i + 50), ang = f * TAU + t * (.12 + .1 * hash(i + 9)) * (i % 2 ? 1 : -1), tw = Math.sin(t * 2.3 + i * 1.7); if (tw < .15) continue;
      const gx = sx + Math.cos(ang) * rx * rr * k, gy = sy + Math.sin(ang) * ry * rr * k; ctx.fillRect(Math.round(gx), Math.round(gy), Math.round((1.5 + 2.5 * tw) * k), Math.max(1, Math.round(k * .45))); }
    ctx.restore();
    ctx.save(); ctx.globalAlpha = a0; ctx.lineCap = 'round'; // falling streams (over the pedestal's lip, in front of it)
    for (const [jx, jt, jb] of F.jets) { const [ax, ay] = w.W2S(...fpx(h, F, jx, jt, T)), [, by] = w.W2S(...fpx(h, F, jx, jb, T)), L = by - ay;
      ctx.strokeStyle = 'rgba(170,206,216,.42)'; ctx.lineWidth = Math.max(1, k * .9); ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(ax, by); ctx.stroke();
      ctx.fillStyle = 'rgba(232,246,250,.85)'; for (let i = 0; i < 4; i++) { const ph = (t * 1.6 + i / 4 + jx * .07) % 1, yy = ay + L * ph * ph; ctx.fillRect(Math.round(ax - k * .4), Math.round(yy), Math.max(1, Math.round(k * .8)), Math.round(k * (1.2 + ph * 1.6))); }
      ctx.fillStyle = 'rgba(232,246,250,.6)'; for (let i = 0; i < 3; i++) { const ph = (t * 2.2 + i / 3 + jx) % 1, dx = (hash(i + jx) - .5) * 5 * k * ph; ctx.fillRect(Math.round(ax + dx), Math.round(by - ph * (1 - ph) * 9 * k), Math.max(1, Math.round(k * .6)), Math.max(1, Math.round(k * .6))); } } // splash
    ctx.restore();
    waterSound(w, cx, cy); }
  function waterSound(w, cx, cy) { // louder near the basin (quiet: a background murmur, never over the music)
    const hero = w.hero, d = Math.hypot(hero.x - cx, hero.y - cy), g = Math.max(0, 1 - d / 170); lastSound = performance.now();
    if (window.SFX2 && SFX2.ambient) SFX2.ambient('water', .32 * g * g); }
  setInterval(() => { if (performance.now() - lastSound > 400 && window.SFX2 && SFX2.ambient) SFX2.ambient('water', 0); }, 300); // left Felt / paused: fade out
  // picture signs (placeholders: a plank + a code icon) — swapped for art via hd.live.signs later
  function icon(ctx, kind, x, y, u) { ctx.fillStyle = '#e8d6b0'; const R = (a, b, c, d) => ctx.fillRect(Math.round(x + a * u), Math.round(y + b * u), Math.max(1, Math.round(c * u)), Math.max(1, Math.round(d * u)));
    if (kind === 'sword') { R(-.4, -3, .8, 4.6); R(-1.6, 1.4, 3.2, .7); R(-.4, 2.1, .8, 1.3); }
    else if (kind === 'bag') { R(-2, -1, 4, 3.6); R(-1, -2.2, 2, 1.2); ctx.fillStyle = '#5a3a22'; R(-.4, .2, .8, 1.2); }
    else if (kind === 'leaf') { ctx.fillStyle = '#9fc070'; ctx.beginPath(); ctx.ellipse(x, y, 1.6 * u, 3 * u, .6, 0, TAU); ctx.fill(); ctx.fillStyle = '#4d5a2c'; R(-.2, -2, .4, 4); }
    else if (kind === 'mug') { R(-1.8, -2, 3, 4.2); R(1.2, -1, 1.2, .6); R(1.8, -1, .6, 2.2); R(1.2, .8, 1.2, .6); ctx.fillStyle = '#fff6dc'; R(-1.8, -2.6, 3, .8); }
    else if (kind === 'anvil') { R(-2.6, -1.4, 5.2, 1.4); R(-1, 0, 2, 1.4); R(-2, 1.4, 4, 1); }
    else if (kind === 'needle') { R(-.3, -3, .6, 6); ctx.strokeStyle = '#d04a4a'; ctx.lineWidth = Math.max(1, u * .5); ctx.beginPath(); ctx.moveTo(x, y - 2.4 * u); ctx.quadraticCurveTo(x + 3 * u, y - 1 * u, x + 1.5 * u, y + 2.5 * u); ctx.stroke(); } }
  function plank(ctx, sx, sy, k, wpx, hpx, sway) { ctx.fillStyle = 'rgba(14,10,18,.35)'; ctx.fillRect(Math.round(sx - wpx / 2 * k + k), Math.round(sy + k), Math.round(wpx * k), Math.round(hpx * k));
    ctx.fillStyle = '#5a3a22'; ctx.fillRect(Math.round(sx - wpx / 2 * k), Math.round(sy), Math.round(wpx * k), Math.round(hpx * k)); ctx.fillStyle = '#76583a'; ctx.fillRect(Math.round(sx - wpx / 2 * k), Math.round(sy), Math.round(wpx * k), Math.max(1, Math.round(k)));
    ctx.fillStyle = '#2e2318'; ctx.fillRect(Math.round(sx - wpx / 2 * k), Math.round(sy + (hpx - 1) * k), Math.round(wpx * k), Math.max(1, Math.round(k))); }
  function drawSigns(k, front, h, T) { const w = W(), ctx = w.ctx, S = w.S, hero = w.hero;
    for (const [x, y, kind] of h.live.signs || []) { const wx = (h.gx + x) * T, wy = (h.gy + y) * T; if ((wy > hero.y) !== !!front) continue; const [sx, sy] = w.W2S(wx, wy), sw = Math.sin(S.t * 1.1 + x) * .5 * k;
      ctx.fillStyle = '#2e2318'; ctx.fillRect(Math.round(sx - 5 * k), Math.round(sy - 14 * k), Math.round(10 * k), Math.max(1, Math.round(k * .8))); // bracket
      ctx.save(); ctx.translate(sx + sw, sy - 13 * k); plank(ctx, 0, 0, k, 9, 9, 0); icon(ctx, kind, 0, 4.5 * k, k * .9); ctx.restore(); }
    }   // the south gate plank is art now (sign_gate_sunset.png, felt_slots.json)
  // flames: a glow that breathes over the baked pool + a small bright core
  const GL = {}; function glow(col) { if (GL[col]) return GL[col]; const c = GL[col] = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    const r = parseInt(col.slice(1, 3), 16), gg = parseInt(col.slice(3, 5), 16), b = parseInt(col.slice(5, 7), 16); gr.addColorStop(0, `rgba(${r},${gg},${b},.55)`); gr.addColorStop(.4, `rgba(${r},${gg},${b},.18)`); gr.addColorStop(1, `rgba(${r},${gg},${b},0)`); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return c; }
  function drawFlick(k, h, T, boost) { const w = W(), ctx = w.ctx, S = w.S; ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (const [i, [x, y, r, col, a]] of (h.live.flick || []).entries()) { const n = noise(S.t, i * 3.1), [sx, sy] = w.W2S((h.gx + x) * T, (h.gy + y) * T), R = r * k * (.85 + .3 * n);
      ctx.globalAlpha = Math.min(1, a * (.25 + .55 * n) * (boost || 1)); ctx.drawImage(glow(col), sx - R, sy - R * .8, R * 2, R * 1.6);
      ctx.globalAlpha = Math.min(1, a * (.5 + .5 * n)); ctx.drawImage(glow('#fff0c0'), sx - 3 * k, sy - 3.5 * k - n * k, 6 * k, 6 * k); }
    ctx.restore(); }
  const flags = () => { const w = W(); return (w && w.SAVE && w.SAVE.flags) || {}; };
  // story time of day (STORY_ANSWERS 시간표): arrival = late afternoon, after Linette joins = dusk, after the boss = night (candles / prayer), the day you leave = morning
  function phase() { const F = flags(); if (F.felt_morning) return 'morning'; if (F.boss_arachne) return 'night'; const w = W(); if (w && w.SAVE && w.SAVE.quests && w.SAVE.quests.q_felt_main) return 'dusk'; return 'afternoon'; }
  // ---------- story time of day (owner 10-24 펠트 업그레이드 3단계; data = maps/src/felt_story.json via build_felt.py) ----------
  const GRADE = { afternoon: 'rgb(232,222,214)', dusk: 'rgb(214,196,214)', night: 'rgb(120,124,170)', morning: 'rgb(246,244,240)' }, BOOST = { afternoon: 1, dusk: 1.2, night: 1.6, morning: .5 };
  const IMC = {}; function img(src) { let im = IMC[src]; if (!im) { im = IMC[src] = new Image(); im.src = src; } return im.complete && im.naturalWidth ? im : null; }
  let STORY = null, lastPh = null, lastMap = null;
  const nBtn = () => { const F = flags(); let c = 0; for (let i = 1; i <= 6; i++) if (F['felt_button_' + i]) c++; return c; };
  const say = (text, last) => { const w = W(), mm = text.match(/^([^\s:()「」]{1,8}): /);   // 'name: line' even for someone not on this map (Bart's board)
    if (mm && !/\n[^\s:()「」]{1,8}: /.test(text)) return w.talkAs({ name: mm[1] }, text.slice(mm[0].length), last); w.talkAs({ name: '' }, text, last); };
  const heroIn = (m) => { const w = W(); return { tx: Math.floor(w.hero.x / m.T), ty: Math.floor(w.hero.y / m.T) }; };
  function applyPhase(m) { const p = phase(), w = W();   // who stands where, who is out, the south gate at night
    for (const o of m.objs) {
      if (o.when) o.hide = !o.when.includes(p);
      if (o.pos) { if (!o._b) o._b = [o.tx, o.ty]; const d = o.pos[p] || [0, 0], nx = o._b[0] + d[0], ny = o._b[1] + d[1];
        if (nx !== o.tx || ny !== o.ty) { if (!o.wander) { m.solidG[o.ty * m.w + o.tx] = 0; m.solidG[ny * m.w + nx] = 1; }
          o.tx = nx; o.ty = ny; o.x = (nx + .5) * m.T; o.y = (ny + .5) * m.T; o.hx = o.x; o.hy = o.y; } } }
    lastPh = p; lastMap = m; }
  function gateStep(m) { const g = m.objs.find(o => o.felt === 'gate'); if (!g) return;   // only the south gate shuts at night, and only on the way out (coming home in the dark, Gas lets you in: no lock-out)
    const shut = phase() === 'night' && heroIn(m).ty < g.ty;
    if (g._shut === shut) return; g._shut = shut;
    for (const dy of g.drows) for (const dx of g.dxs) { const i = (g.ty + dy) * m.w + g.tx + dx; if (shut) { if (g['_s' + i] === undefined) g['_s' + i] = m.solidG[i]; m.solidG[i] = 1; } else if (g['_s' + i] !== undefined) m.solidG[i] = g['_s' + i]; } }
  function buttonsDone() { const w = W(), F = flags(); if (F.felt_buttons_done || nBtn() < 6 || !STORY) return false;
    F.felt_buttons_done = 1; F.felt_aff_linette = (F.felt_aff_linette || 0) + 1;   // no affinity system in the game yet: an optional counter flag (no GAME_VER bump)
    say(STORY.done, { then: () => { w.giveLoot([['acc_guard_button', 1]]); w.save && w.save(); } }); return true; }
  const linetteNear = () => { const F = flags(), w = W(); return !!(w.SAVE.quests && w.SAVE.quests.q_felt_main) || !!F.boss_arachne; };   // she is with you from dusk on
  function interact(o) { const w = W(), F = flags(), p = phase();
    if (o.id === 'f_linette' && nBtn() >= 6 && !F.felt_buttons_done) return buttonsDone();
    if (o.id === 'fi_inn_rest' && p === 'night') { F.felt_morning = 1; w.addFx('text', w.hero.x, w.hero.y - 34, { text: '동이 텄다', life: 1.6, color: '#ffe8b0' }); return false; }   // rest at the inn: night -> clear morning (then the normal rest heals)
    if (!o.felt) return false;
    const k = o.felt;
    if (k === 'btn') { if (F['felt_button_' + o.n]) return true; F['felt_button_' + o.n] = 1; w.sfx('chest', .7); w.addFx('sparkle', o.x, o.y, { life: .6 });
      const c = nBtn(); say(o.text + '\n(' + c + '/6)', { then: () => { if (!(c >= 6 && linetteNear() && buttonsDone())) w.save && w.save(); } }); return true; }
    if (k === 'thread') { const id = 'felt_thread_' + o.n; if (F.boss_arachne || F[id]) return false; F[id] = 1; w.sfx('swing', .5); w.addFx('fluff', o.x, o.y - 6, { life: .8, n: 8 }); w.addFx('dust', o.x, o.y, { life: .5 });
      say('( 엉킨 실을 걷어 냈다. )'); w.save && w.save(); return true; }
    if (k === 'gate') { if (p !== 'night' || heroIn(w.S.map).ty >= o.ty) return false; say(o.text); return true; }
    if (k === 'board') { say(F.boss_arachne ? o.after : o.before); return true; }
    if (k === 'memorial') { let t = '( 천에 적힌 이름들 )\n' + o.cloths.slice(0, 4).map(c => '「' + c + '」').join('\n') + '\n\n' + o.cloths.slice(4).map(c => '「' + c + '」').join('\n') + '\n\n( 찾습니다 )\n' + o.tags.map(c => '「' + c + '」').join('\n');
      if (F.boss_arachne) t += '\n\n' + o.scarf; say(t); return true; }
    if (k === 'ration') { const id = 'felt_ration_' + p; if (F[id]) { say('( 오늘 배급은 다 나눴다. )'); return true; }
      say('( 배급을 거들까? )', { choices: [{ t: '거든다', f: () => { F[id] = 1; const got = w.giveLoot([['c_food_s', 1]]); say('( 줄이 조금 줄었다. 마르타가 ' + got + '을(를) 쥐여 주었다. )'); w.save && w.save(); } }, { t: '그만둔다', f: () => {} }] }); return true; }
    if (k === 'dice') { dice(o); return true; }
    return false; }
  function dice(o) { const w = W(), F = flags(), id = 'felt_dice_' + phase(), n = F[id] || 0;
    if (n >= o.rounds) { say(o.open + '\n( 오늘은 세 판 다 했다. )'); return; }
    say(o.open, { choices: [{ t: '한 판 (' + o.stake + 'G)', f: () => {
      const r = F[id] || 0; if (r >= o.rounds) { say(o.open + '\n( 오늘은 세 판 다 했다. )'); return; }
      if (typeof INV === 'undefined' || INV.gold < o.stake) { say('( 금화가 모자란다. )'); return; }
      F[id] = r + 1; let a, b; do { a = 2 + Math.floor(Math.random() * 6) + Math.floor(Math.random() * 6); b = 2 + Math.floor(Math.random() * 6) + Math.floor(Math.random() * 6); } while (a === b);
      w.sfx('roll', .6); const win = a > b; if (win) window.__game.addGold(o.stake); else INV.gold -= o.stake; if (win) w.sfx('coin', .7);
      say('( 필멸자 ' + a + ' : ' + b + ' 가스 )\n\n' + (win ? o.win : o.lose)); w.save && w.save(); } }, { t: '그만둔다', f: () => {} }] }); }
  function drawCandles(k, h, T) { const p = phase(); if (p !== 'dusk' && p !== 'night') return; const w = W(), ctx = w.ctx, S = w.S, m = S.map, o = m && m.objs.find(o => o.felt === 'memorial'); if (!o || !o.candles) return;   // memorial candles glow over the dusk / night tint (lit from dusk; all lit after the boss)
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; const all = !!flags().boss_arachne;
    for (const [i, [px, py]] of o.candles.entries()) { if (!all && i % 2) continue; const n = noise(S.t, i * 2.3 + 7), [sx, sy] = w.W2S(31.59 * T + (px - 92.5) * T / 48 + (o.tx - 31) * T, 12.71 * T + (py - 148) * T / 48 + (o.ty - 12) * T), R = (p === 'night' ? 16 : 11) * k * (.85 + .3 * n);
      ctx.globalAlpha = .55 + .35 * n; ctx.drawImage(glow('#ffb060'), sx - R, sy - R * .8, R * 2, R * 1.6); ctx.globalAlpha = .9; ctx.drawImage(glow('#fff0c0'), sx - 2.5 * k, sy - 4 * k - n * k, 5 * k, 5 * k); }
    ctx.restore(); }
  // code-drawn bits: ash-button glint (art strip, frame 0 held 2s then 1, 2 at 100ms), the scarf on Felix's tag, two dice by the barrels, Bart's number board
  const BTN_SEQ = [[0, 2000], [1, 100], [2, 100]]; function seqF(seq, t, ph) { const tot = seq.reduce((s, q) => s + q[1], 0); let u = ((t * 1000 + ph) % tot + tot) % tot; for (const [f, ms] of seq) { if (u < ms) return f; u -= ms; } return 0; }
  function objs(k, front, m) { const w = W(); if (!w) return; const T = m.T, ctx = w.ctx, hero = w.hero, F = flags(), S = w.S;
    if (!front) { if (m !== lastMap || phase() !== lastPh) applyPhase(m); gateStep(m); const h = (m.hds || []).find(h => h.live && h.live.story); if (h) STORY = h.live.story; }
    const u = k * T / 48;   // art px -> screen px (48 art px = 1 tile)
    for (const o of m.objs) { if (o.hide) continue; if ((o.y > hero.y) !== !!front) continue;
      if (o.hi && o.art) { const im = img('assets/npcs/' + o.art + '.png'); if (!im) continue; const hh = (o.h || 26) * k, ww = im.naturalWidth * hh / im.naturalHeight, [sx, sy] = w.W2S(o.x, o.y + 7);
        ctx.drawImage(im, Math.round(sx - ww / 2), Math.round(sy - hh), Math.round(ww), Math.round(hh)); continue; }
      if (o.felt === 'btn' && !F['felt_button_' + o.n]) { const im = img('assets/world/felt_slots/ash_button_glint_strip.png'); if (!im) continue; const fw = im.naturalWidth / 3, f = seqF(BTN_SEQ, S.t, o.n * 377), [sx, sy] = w.W2S(o.x, o.y + 3);
        ctx.drawImage(im, f * fw, 0, fw, im.naturalHeight, Math.round(sx - fw * u / 2), Math.round(sy - im.naturalHeight * u / 2), Math.round(fw * u), Math.round(im.naturalHeight * u)); continue; }
      if (o.felt === 'dice') { const [sx, sy] = w.W2S(o.x, o.y + 2), d = 2.6 * k; for (const [ox, oy] of [[-3, 0], [1.5, 1]]) { ctx.fillStyle = 'rgba(14,10,18,.35)'; ctx.fillRect(Math.round(sx + ox * k + k * .5), Math.round(sy + oy * k + k * .5), Math.round(d), Math.round(d)); ctx.fillStyle = '#e8e0cc'; ctx.fillRect(Math.round(sx + ox * k), Math.round(sy + oy * k), Math.round(d), Math.round(d)); ctx.fillStyle = '#2e2318'; ctx.fillRect(Math.round(sx + (ox + 1) * k), Math.round(sy + (oy + 1) * k), Math.max(1, Math.round(k * .6)), Math.max(1, Math.round(k * .6))); } continue; }
      if (o.felt === 'board') { const [sx, sy] = w.W2S(o.x, o.y + 6); ctx.fillStyle = '#3a2a1c'; ctx.fillRect(Math.round(sx - k), Math.round(sy - 14 * k), Math.round(2 * k), Math.round(14 * k)); plank(ctx, sx, sy - 22 * k, k, 14, 10, 0);
        ctx.fillStyle = '#e8d6b0'; for (let r = 0; r < 3; r++) for (let c = 0; c < (r === 2 && F.boss_arachne ? 0 : 4); c++) ctx.fillRect(Math.round(sx + (-5 + c * 2.6) * k), Math.round(sy + (-20 + r * 2.6) * k), Math.max(1, Math.round(k * .5)), Math.round(k * 1.6)); continue; }   // tally marks; after the boss the 'gone' row stays empty
      if (o.felt === 'memorial' && F.boss_arachne) { const [sx, sy] = w.W2S(31.59 * T + (140 - 92.5) * T / 48 + (o.tx - 31) * T, 12.71 * T + (84 - 148) * T / 48 + (o.ty - 12) * T), sw = Math.sin(S.t * .9) * .4 * u;   // Felix's tag: a piece of his scarf (code)
        ctx.fillStyle = '#7a3430'; ctx.fillRect(Math.round(sx + sw), Math.round(sy), Math.round(4 * u), Math.round(13 * u)); ctx.fillStyle = '#9a4a3c'; for (let i = 0; i < 4; i++) ctx.fillRect(Math.round(sx + sw), Math.round(sy + (1 + i * 3) * u), Math.round(4 * u), Math.max(1, Math.round(u)));
        ctx.fillStyle = '#5a2624'; for (let i = 0; i < 3; i++) ctx.fillRect(Math.round(sx + sw * 1.4 + (i * 1.4) * u), Math.round(sy + 13 * u), Math.max(1, Math.round(u * .7)), Math.round(2.4 * u)); } } }
  window.FELT_LIVE = {
    props(k, front, h, T) { if (!h.live) return; if (!front && h.live.fountain) drawFountain(k, h, T); drawSigns(k, front, h, T); },
    over(k, h, T) { if (!h.live) return; drawFlick(k, h, T, BOOST[phase()]); drawCandles(k, h, T); },   // flames burn brighter as it gets dark
    grade(h) { return h.live ? GRADE[phase()] : null; },   // the time-of-day tint (art is uncoloured); afternoon = the old weak dusk rgb(224,216,232) a touch warmer
    phase, objs, interact,
    show(key) { const [k, n] = key.split(':'), p = phase(), F = flags();   // art-slot story switches (felt_slots.json show)
      const lit = p === 'dusk' || p === 'night'; if (k === 'day') return !lit; if (k === 'night') return lit;   // candles from dusk on
      const cut = !!(F.boss_arachne || F['felt_thread_' + n]); if (k === 'thread') return !cut; if (k === 'thread_cut') return cut; return true; },
    bgm(want) { return want === 'town_ruin' && flags().boss_arachne ? 'town_felt_bright' : want; },   // after the boss: 잿더미 위의 별 (assets/bgm/felt_bright.ogg)
  };
})();
