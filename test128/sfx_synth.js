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
    talk:      [['t', { type: 'triangle', f0: 540, f1: 500, dur: .035, v: .07 }]],                                      // dialogue letter blip (soft, 2 letters per blip)
    deny:      [['t', { type: 'sine', f0: 240, f1: 200, dur: .07, v: .16 }]],                                            // item can't be used: one quiet low tick (no buzzer)                                                  // Linette's needle
    // sandbox-only stand-ins for the town's recorded swing / hit sounds (the game keeps the recordings)
    slash:     [['n', { f0: 1400, f1: 3800, dur: .11, v: .3, a: .015 }]],
    slash_big: [['n', { f0: 900, f1: 3200, dur: .18, v: .4, a: .02 }], ['t', { type: 'sawtooth', f0: 160, f1: 90, dur: .15, v: .06 }]],
    hit:       [['n', { f0: 2600, f1: 900, dur: .07, v: .45 }], ['t', { type: 'square', f0: 260, f1: 120, dur: .08, v: .16 }]],
    hit_big:   [['n', { f0: 2000, f1: 500, dur: .12, v: .55 }], ['t', { type: 'square', f0: 200, f1: 70, dur: .14, v: .22 }], ['n', { f0: 300, f1: 80, dur: .2, v: .3, filter: 'lowpass' }]],
    // 타격 재질 1겹 (타격감 보고서 3-6): 맞은 몹의 몸 = 살 / 실 / 뼈·갑옷 / 껍질 — world_mobs.js D.sfxMat
    mat_flesh:  [['n', { f0: 900, f1: 180, dur: .09, v: .38, filter: 'lowpass', q: .8 }], ['t', { type: 'sine', f0: 150, f1: 70, dur: .08, v: .16 }]],     // 퍽
    mat_thread: [['n', { f0: 3600, f1: 5200, dur: .06, v: .22, q: 2 }], ['t', { type: 'triangle', f0: 1700, f1: 2500, dur: .06, v: .07 }]],              // 실 끊김 (팅)
    mat_bone:   [['n', { f0: 1900, f1: 1200, dur: .07, v: .3, q: 5 }], ['t', { type: 'square', f0: 880, f1: 660, dur: .045, v: .08 }]],                  // 딱
    mat_shell:  [['n', { f0: 2600, f1: 700, dur: .09, v: .32, q: 2.2 }], ['t', { type: 'triangle', f0: 520, f1: 260, dur: .06, v: .1 }]],              // 껍질 깨짐 (빠직)
    hit_thud:   [['t', { type: 'sine', f0: 92, f1: 44, dur: .22, v: .45 }], ['n', { f0: 260, f1: 60, dur: .18, v: .3, filter: 'lowpass', q: .7 }]],      // 3타 저음 쿵
    fight_end:  [['t', { type: 'triangle', f0: 784, dur: .1, v: .1 }], ['t', { type: 'triangle', f0: 1175, dur: .3, v: .1, d: .09 }], ['n', { f0: 6000, f1: 7500, dur: .3, v: .04, filter: 'highpass', d: .09 }]], // 들판 마지막 적: 짧은 마무리
  };
  function voice(ctx, dest, nb, k, vol, rate, t0) { const out = ctx.createGain(); out.gain.value = vol; out.connect(dest); const r = rate * (.975 + Math.random() * .05); // 무작위 ±2.5% (콤보 +3% 계단이 들리게)
    for (const [kind, o0] of DEF[k]) { const o = Object.assign({}, o0, { out, nb, f0: o0.f0 * r, f1: (o0.f1 || o0.f0) * r }); (kind === 't' ? tone : noise)(ctx, t0 + (o0.d || 0), o); } }
  let busy = [];   // voice cap: at most 8 sounds started per 0.15s (a burst of hits / telegraphs used to stack dozens of audio nodes)
  function play(k, vol = 1, rate = 1) { if (OFF || !ac || !DEF[k]) return; const now = ac.currentTime; if (last[k] && now - last[k] < .04) return; busy = busy.filter(t => now - t < .15); if (busy.length >= 8) return; busy.push(now); last[k] = now; if (ac.state === 'suspended') ac.resume();
    voice(ac, master, noiseBuf, k, vol, rate, now); }
  function render(list, secs) { const sr = 44100, oc = new OfflineAudioContext(1, Math.ceil(sr * secs), sr), m = oc.createGain(); m.gain.value = .45; m.connect(oc.destination); const nb = mkNoise(oc);
    for (const [k, t, v, rt] of list) voice(oc, m, nb, k, v || 1, rt || 1, t); return oc.startRendering().then(b => Array.from(b.getChannelData(0))); }
  window.SFX2 = { play, setVol(v) { vol = Math.max(0, Math.min(1, v)); if (master) master.gain.value = .45 * vol; }, get vol() { return vol; }, render, has: k => !!DEF[k], names: Object.keys(DEF), get ready() { return !!ac; } };
})();
