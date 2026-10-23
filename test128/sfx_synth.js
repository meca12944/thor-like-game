/* =====================================================================
 *  sfx_synth.js — code-made sound effects (WebAudio, no files, 0 credits) for the field / dungeon combat that had no sound.
 *  window.SFX2.play(name, vol=1, rate=1). Each sound = a few oscillator / noise layers with pitch + volume envelopes (jsfxr style).
 *  ?sfx2=0 turns it off (compare). SFX2.render(list, secs) renders offline for preview videos (tools/sfx_preview.py).
 * ===================================================================== */
(function () {
  'use strict';
  const OFF = new URLSearchParams(location.search).get('sfx2') === '0';
  let ac = null, master = null, noiseBuf = null, vol = 1; const last = {}; // vol = 효과음 크기 (설정 → 소리)
  try { const v = localStorage.getItem('sfxVol'); if (v !== null) vol = Math.max(0, Math.min(1, +v)); } catch (e) { }
  const mkNoise = ctx => { const b = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate), d = b.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; return b; };
  function init() { if (ac || OFF) return; try { ac = new (window.AudioContext || window.webkitAudioContext)(); master = ac.createGain(); master.gain.value = .45 * vol; master.connect(ac.destination); noiseBuf = mkNoise(ac); } catch (e) { ac = null; } }
  addEventListener('keydown', init); addEventListener('pointerdown', init);
  // tone layer: wave type, f0 -> f1 Hz over dur, attack/decay volume envelope
  function tone(ctx, t0, o) { const os = ctx.createOscillator(), g = ctx.createGain(); os.type = o.type || 'square'; os.frequency.setValueAtTime(o.f0, t0); os.frequency.exponentialRampToValueAtTime(Math.max(20, o.f1), t0 + o.dur);
    g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(o.v, t0 + (o.a || .004)); g.gain.exponentialRampToValueAtTime(.001, t0 + o.dur); os.connect(g); g.connect(o.out); os.start(t0); os.stop(t0 + o.dur + .02); }
  // noise layer through a filter that sweeps f0 -> f1
  function noise(ctx, t0, o) { const s = ctx.createBufferSource(), f = ctx.createBiquadFilter(), g = ctx.createGain(); s.buffer = o.nb; f.type = o.filter || 'bandpass'; f.Q.value = o.q || 1.2;
    f.frequency.setValueAtTime(o.f0, t0); f.frequency.exponentialRampToValueAtTime(Math.max(30, o.f1), t0 + o.dur);
    g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(o.v, t0 + (o.a || .004)); g.gain.exponentialRampToValueAtTime(.001, t0 + o.dur); s.connect(f); f.connect(g); g.connect(o.out); s.start(t0, Math.random() * .5); s.stop(t0 + o.dur + .02); }
  // [layer kind t=tone / n=noise, params]; d = delay (s)
  const DEF = {
    roll:      [['n', { f0: 900, f1: 2600, dur: .16, v: .35, a: .03 }]],                                                   // whoosh
    hurt:      [['t', { type: 'square', f0: 220, f1: 70, dur: .2, v: .3 }], ['n', { f0: 600, f1: 200, dur: .12, v: .4 }]],   // hero hit
    dodge:     [['t', { type: 'triangle', f0: 1320, dur: .12, v: .25 }], ['t', { type: 'triangle', f0: 1980, dur: .2, v: .2, d: .06 }]], // perfect roll chime
    tele:      [['t', { type: 'triangle', f0: 760, f1: 700, dur: .07, v: .12 }]],                                         // enemy warning tick
    mob_swing: [['n', { f0: 500, f1: 1400, dur: .12, v: .3, a: .02 }]],                                                   // enemy melee lands
    mob_dash:  [['n', { f0: 300, f1: 1200, dur: .25, v: .3, a: .05 }], ['t', { type: 'sawtooth', f0: 90, f1: 140, dur: .2, v: .08 }]],
    shot:      [['t', { type: 'square', f0: 1100, f1: 380, dur: .1, v: .12 }]],                                           // pew
    impact:    [['n', { f0: 400, f1: 60, dur: .28, v: .55, filter: 'lowpass', q: .7 }], ['t', { type: 'sine', f0: 120, f1: 40, dur: .25, v: .35 }]], // ground pulse / drop
    mob_die:   [['n', { f0: 1200, f1: 150, dur: .3, v: .4, a: .01 }], ['t', { type: 'triangle', f0: 520, f1: 90, dur: .28, v: .2 }]],
    coin:      [['t', { type: 'square', f0: 988, dur: .07, v: .12 }], ['t', { type: 'square', f0: 1319, dur: .18, v: .12, d: .07 }]],
    heart:     [['t', { type: 'triangle', f0: 660, dur: .1, v: .2 }], ['t', { type: 'triangle', f0: 880, dur: .1, v: .2, d: .08 }], ['t', { type: 'triangle', f0: 1320, dur: .2, v: .2, d: .16 }]],
    thrust:    [['n', { f0: 1800, f1: 4200, dur: .09, v: .22, a: .01 }]],
    quaff:     [['t', { type: 'sine', f0: 420, f1: 780, dur: .12, v: .22 }], ['t', { type: 'triangle', f0: 880, f1: 1320, dur: .16, v: .14, d: .08 }]], // potion drunk: soft rising gulp + chime
    page:      [['t', { type: 'triangle', f0: 1180, f1: 1240, dur: .045, v: .07 }]],                                      // dialog next page: tiny soft tick
    talk:      [['t', { type: 'sine', f0: 660, f1: 880, dur: .08, v: .1 }]],                                                 // dialog opens: small rising note
    deny:      [['t', { type: 'sine', f0: 240, f1: 200, dur: .07, v: .16 }]],                                            // item can't be used: one quiet low tick (no buzzer)                                                  // Linette's needle
    // sandbox-only stand-ins for the town's recorded swing / hit sounds (the game keeps the recordings)
    slash:     [['n', { f0: 1400, f1: 3800, dur: .11, v: .3, a: .015 }]],
    slash_big: [['n', { f0: 900, f1: 3200, dur: .18, v: .4, a: .02 }], ['t', { type: 'sawtooth', f0: 160, f1: 90, dur: .15, v: .06 }]],
    hit:       [['n', { f0: 2600, f1: 900, dur: .07, v: .45 }], ['t', { type: 'square', f0: 260, f1: 120, dur: .08, v: .16 }]],
    hit_big:   [['n', { f0: 2000, f1: 500, dur: .12, v: .55 }], ['t', { type: 'square', f0: 200, f1: 70, dur: .14, v: .22 }], ['n', { f0: 300, f1: 80, dur: .2, v: .3, filter: 'lowpass' }]],
  };
  function voice(ctx, dest, nb, k, vol, rate, t0) { const out = ctx.createGain(); out.gain.value = vol; out.connect(dest); const r = rate * (.95 + Math.random() * .1);
    for (const [kind, o0] of DEF[k]) { const o = Object.assign({}, o0, { out, nb, f0: o0.f0 * r, f1: (o0.f1 || o0.f0) * r }); (kind === 't' ? tone : noise)(ctx, t0 + (o0.d || 0), o); } }
  let busy = [];   // voice cap: at most 8 sounds started per 0.15s (a burst of hits / telegraphs used to stack dozens of audio nodes)
  function play(k, vol = 1, rate = 1) { if (OFF || !ac || !DEF[k]) return; const now = ac.currentTime; if (last[k] && now - last[k] < .04) return; busy = busy.filter(t => now - t < .15); if (busy.length >= 8) return; busy.push(now); last[k] = now; if (ac.state === 'suspended') ac.resume();
    voice(ac, master, noiseBuf, k, vol, rate, now); }
  function render(list, secs) { const sr = 44100, oc = new OfflineAudioContext(1, Math.ceil(sr * secs), sr), m = oc.createGain(); m.gain.value = .45; m.connect(oc.destination); const nb = mkNoise(oc);
    for (const [k, t, v] of list) voice(oc, m, nb, k, v || 1, 1, t); return oc.startRendering().then(b => Array.from(b.getChannelData(0))); }
  window.SFX2 = { play, setVol(v) { vol = Math.max(0, Math.min(1, v)); if (master) master.gain.value = .45 * vol; }, get vol() { return vol; }, render, has: k => !!DEF[k], names: Object.keys(DEF), get ready() { return !!ac; } };
})();
