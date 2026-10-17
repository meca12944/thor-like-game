// Modern HUD gauges (HP / MP / EXP / 필살기) shared by the town engine (tools/game.template.html) and the field (world.js).
// Thin continuous gauges on a translucent dark panel, gradient fill, delayed "damage ghost" trail, soft edge glow,
// slow low-HP pulse (no movement / scaling — motion-sickness friendly). Drawn at display resolution (device px), never pixelated.
(function () {
  'use strict';
  const FONT = '"Segoe UI","Inter","Noto Sans KR","Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif';
  const CFG = { ghostHold: .45, ghostDrain: .55, fillEase: 14, lowHp: .3, pulseHz: .9 }; // ghost: hold s, then drains maxValue*.55/s
  const st = {}; let lastT = 0, T = 0;
  function tick() { const n = performance.now() / 1000, dt = lastT ? Math.min(.1, n - lastT) : 0; lastT = n; T += dt; return dt; }
  // per-gauge smoothing: shown value eases to the target, ghost holds then drains toward it
  function track(id, f, dt) {
    let s = st[id]; if (!s || !isFinite(s.v)) s = st[id] = { v: f, g: f, hold: 0 };
    if (f < s.v - 1e-4) { if (s.g < s.v) s.g = s.v; s.hold = CFG.ghostHold; s.v = f; }
    else s.v += (f - s.v) * Math.min(1, dt * CFG.fillEase);
    if (s.g > s.v) { if (s.hold > 0) s.hold -= dt; else s.g = Math.max(s.v, s.g - dt * CFG.ghostDrain * Math.max(.35, (s.g - s.v) * 3)); } else s.g = s.v;
    return s;
  }
  function rr(c, x, y, w, h, r) { r = Math.min(r, h / 2, w / 2); c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
  function txt(c, t, x, y, px, col, align = 'left', w = 600) { c.font = `${w} ${Math.round(px)}px ${FONT}`; c.textAlign = align; c.textBaseline = 'alphabetic';
    c.shadowColor = 'rgba(0,0,0,.85)'; c.shadowBlur = Math.max(1, px * .25); c.shadowOffsetY = Math.max(1, px * .06); c.fillStyle = col; c.fillText(t, x, y); c.shadowColor = 'transparent'; c.shadowBlur = 0; c.shadowOffsetY = 0; }
  // one thin gauge. pal = [c0, c1, glow rgb]
  function gauge(c, x, y, w, h, s, pal, o = {}) {
    const r = h / 2;
    rr(c, x - 1, y - 1, w + 2, h + 2, r + 1); c.fillStyle = 'rgba(0,0,0,.55)'; c.fill();           // crisp dark outline
    rr(c, x, y, w, h, r); c.fillStyle = 'rgba(255,255,255,.07)'; c.fill();                        // track
    if (s.g > s.v + .001) { const gx = x + w * s.v, gw = w * (s.g - s.v), a = s.hold > 0 ? 1 : .85;
      const gg = c.createLinearGradient(gx, 0, gx + gw, 0); gg.addColorStop(0, `rgba(255,120,96,${.9 * a})`); gg.addColorStop(1, `rgba(255,244,236,${.95 * a})`);
      c.save(); rr(c, x, y, w, h, r); c.clip(); c.fillStyle = gg; c.fillRect(gx, y, gw, h); c.restore(); }   // damage ghost (white -> red, drains after the hold)
    const fw = Math.max(0, Math.min(1, s.v)) * w;
    if (fw > .5) {
      c.save(); rr(c, x, y, w, h, r); c.clip();
      const g = c.createLinearGradient(x, 0, x + w, 0); g.addColorStop(0, pal[0]); g.addColorStop(1, pal[1]); c.fillStyle = g; c.fillRect(x, y, fw, h);
      c.fillStyle = 'rgba(255,255,255,.32)'; c.fillRect(x, y, fw, Math.max(1, h * .34));                 // top sheen
      c.restore();
      if (fw < w - .5 || o.full) { const ex = x + fw, gr = c.createRadialGradient(ex, y + h / 2, 0, ex, y + h / 2, h * 2.6);          // soft glow on the fill edge
        gr.addColorStop(0, `rgba(${pal[2]},${.75 * (o.glowA ?? 1)})`); gr.addColorStop(1, `rgba(${pal[2]},0)`); c.fillStyle = gr; c.fillRect(ex - h * 2.6, y - h * 2, h * 5.2, h * 5); }
    }
    if (o.ring > 0) { rr(c, x - 2, y - 2, w + 4, h + 4, r + 2); c.strokeStyle = `rgba(${o.ringCol || pal[2]},${o.ring})`; c.lineWidth = Math.max(1, h * .4); c.stroke(); }
  }
  function panel(c, x, y, w, h, u, alpha) {
    rr(c, x, y, w, h, 6 * u); const g = c.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, `rgba(16,20,32,${.62 * alpha})`); g.addColorStop(1, `rgba(8,10,18,${.48 * alpha})`);
    c.fillStyle = g; c.fill(); c.strokeStyle = `rgba(255,255,255,${.12 * alpha})`; c.lineWidth = 1; c.stroke();
  }
  const HP = ['#2fbf71', '#6ff0a4', '120,255,180'], HPL = ['#c8261f', '#ff6a55', '255,110,90'], MP = ['#2f6dff', '#62c4ff', '120,200,255'], EXP = ['#c99a2e', '#ffe08a', '255,224,138'];
  // o: { x, y, u, hp, maxHp, mp, maxMp, exp, expNext, lvl, lvFlash, alpha }  -> returns bottom y of the panel (device px)
  function drawPlayer(c, o) {
    const dt = tick(), u = o.u, a = o.alpha ?? 1; c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
    const bx = Math.round(o.x), by = Math.round(o.y), badge = Math.round(30 * u), gw = Math.round(124 * u), hh = Math.max(3, Math.round(5 * u)), mh = Math.max(2, Math.round(3.5 * u)), eh = Math.max(1, Math.round(1.5 * u));
    const pw = badge + gw + Math.round(26 * u), ph = Math.round(48 * u); panel(c, bx, by, pw, ph, u, a);
    // level badge: thin gold ring, number centred
    const cx = bx + Math.round(8 * u) + badge / 2, cy = by + ph / 2; c.beginPath(); c.arc(cx, cy, badge / 2, 0, Math.PI * 2); c.fillStyle = 'rgba(0,0,0,.45)'; c.fill();
    const lf = o.lvFlash > 0 ? .5 + .5 * Math.cos(T * 5) : 0; c.strokeStyle = `rgba(255,214,120,${.75 + .25 * lf})`; c.lineWidth = Math.max(1, 1.4 * u); c.stroke();
    txt(c, 'LV', cx, cy - 4 * u, 7 * u, 'rgba(255,224,160,.8)', 'center', 700); txt(c, String(o.lvl), cx, cy + 9 * u, 13 * u, lf ? '#ffffff' : '#ffe9b0', 'center', 700);
    const gx = bx + Math.round(16 * u) + badge, hy = by + Math.round(15 * u), my = hy + hh + Math.round(13 * u), ey = my + mh + Math.round(5 * u);
    const hf = Math.max(0, o.hp / o.maxHp), low = hf <= CFG.lowHp && o.hp > 0, hs = track('hp', hf, dt);
    const pulse = low ? .5 - .5 * Math.cos(T * Math.PI * 2 * CFG.pulseHz) : 0;
    if (low) { c.save(); c.shadowColor = `rgba(255,50,40,${.35 + .45 * pulse})`; c.shadowBlur = 10 * u; rr(c, gx - 1, hy - 1, gw + 2, hh + 2, hh); c.strokeStyle = `rgba(255,70,60,${.25 + .45 * pulse})`; c.lineWidth = Math.max(1, u); c.stroke(); c.restore(); }
    gauge(c, gx, hy, gw, hh, hs, low ? HPL : HP);
    txt(c, 'HP', gx, hy - 4 * u, 8.5 * u, low ? '#ff9a8a' : 'rgba(210,240,220,.85)', 'left', 700);
    txt(c, `${Math.max(0, Math.ceil(o.hp))}`, gx + gw - 26 * u, hy - 4 * u, 10.5 * u, low ? '#ffb0a4' : '#f2fff6', 'right', 600); txt(c, `/ ${o.maxHp}`, gx + gw, hy - 4 * u, 8.5 * u, 'rgba(220,235,225,.7)', 'right', 500);
    if (o.maxMp) { const ms = track('mp', Math.max(0, Math.min(1, o.mp / o.maxMp)), dt); gauge(c, gx, my, gw, mh, ms, MP);
      txt(c, 'MP', gx, my - 3 * u, 8 * u, 'rgba(200,225,255,.85)', 'left', 700); txt(c, `${Math.round(o.mp)} / ${o.maxMp}`, gx + gw, my - 3 * u, 8.5 * u, 'rgba(215,232,255,.85)', 'right', 500); }
    if (o.expNext) { const es = track('exp', Math.max(0, Math.min(1, o.exp / o.expNext)), dt); es.g = es.v; gauge(c, gx, ey, gw, eh, es, EXP, { glowA: .5 }); }
    c.restore(); return by + ph;
  }
  // 필살기 gauge, bottom centre: o { cx, y, u, v (0..1), name, key, locked }. Hidden while the ultimate is story-locked (__game.ultUnlocked false)
  function drawUlt(c, o) {
    const g = window.__game; if (o.locked || (g && g.ultUnlocked === false)) return;
    const u = o.u, w = Math.round(180 * u), h = Math.max(2, Math.round(4 * u)), x = Math.round(o.cx - w / 2), y = Math.round(o.y), full = o.v >= 1;
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0); const s = track('ult', Math.max(0, Math.min(1, o.v)), 0); s.v = s.g = Math.max(0, Math.min(1, o.v));
    const br = full ? .5 - .5 * Math.cos(T * Math.PI * 2 * .8) : 0;   // gentle breathing glow when READY (~0.8 Hz, no motion)
    rr(c, x - 10 * u, y - 18 * u, w + 20 * u, h + 26 * u, 6 * u); c.fillStyle = 'rgba(8,10,18,.42)'; c.fill(); c.strokeStyle = full ? `rgba(255,214,120,${.35 + .35 * br})` : 'rgba(255,255,255,.1)'; c.lineWidth = 1; c.stroke();
    if (full) { c.save(); c.shadowColor = `rgba(255,190,80,${.5 + .4 * br})`; c.shadowBlur = 14 * u; rr(c, x - 1, y - 1, w + 2, h + 2, h); c.fillStyle = 'rgba(255,200,90,.35)'; c.fill(); c.restore(); }
    gauge(c, x, y, w, h, s, full ? ['#ffb83a', '#fff1b8', '255,220,140'] : ['#b8741c', '#ffbf47', '255,190,90'], { full, glowA: full ? .6 + .4 * br : 1 });
    if (full) txt(c, o.key ? `READY (${o.key})` : 'READY', o.cx, y - 5 * u, 11 * u, `rgb(255,${226 + Math.round(20 * br)},${150 + Math.round(60 * br)})`, 'center', 700);
    else { txt(c, '필살기', x, y - 5 * u, 8.5 * u, 'rgba(255,225,170,.85)', 'left', 700); txt(c, `${Math.floor(o.v * 100)}%`, x + w, y - 5 * u, 9 * u, 'rgba(255,236,200,.9)', 'right', 600); }
    const sub = full && !o.key ? o.fieldNote : o.name; if (sub) txt(c, sub, o.cx, y + h + 6 * u, 7.5 * u, full ? 'rgba(255,236,190,.9)' : 'rgba(220,210,190,.6)', 'center', 500);
    c.restore();
  }
  window.HUD = { drawPlayer, drawUlt, CFG, reset() { for (const k in st) delete st[k]; } };
})();
