/* felt_live.js — Felt's live layer (owner 10-24 「펠트 업그레이드」): everything here is drawn by code each frame, nothing is baked.
 *  - fountain: falling streams + rings + drifting glints over the (now wet) basin, and a quiet looping water sound by distance (SFX2.ambient)
 *  - flicker: 5-8 flames (brazier, forge, plaza lamps, chapel candles) breathe on top of the baked light pools
 *  - code sign planks only where no illustrator sign exists (inn / smith / atelier); the rest are art (maps/src/felt_slots.json)
 *  - story switches for the art slots (show): memorial wall day / night, thread clump whole / cut
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
  window.FELT_LIVE = {
    props(k, front, h, T) { if (!h.live) return; if (!front && h.live.fountain) drawFountain(k, h, T); drawSigns(k, front, h, T); },
    over(k, h, T) { if (!h.live) return; drawFlick(k, h, T, 1); },
    grade(h) { return h.live ? 'rgb(224,216,232)' : null; },   // Felt's dusk grade: weaker than the old rgb(206,196,222) (owner 10-24 「노을 약하게」)
    phase,
    show(key) { const [k, n] = key.split(':'), p = phase(), F = flags();   // art-slot story switches (felt_slots.json show)
      if (k === 'day') return p !== 'night'; if (k === 'night') return p === 'night';
      const cut = !!(F.boss_arachne || F['felt_thread_' + n]); if (k === 'thread') return !cut; if (k === 'thread_cut') return cut; return true; },
    bgm(want) { return want; },
  };
})();
