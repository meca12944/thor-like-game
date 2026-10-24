/* [title] Minimal title screen for the town demo (self-contained, never touches game logic).
 *   '제목 미정' logo placeholder -> 'Press any key' -> menu 새 게임 / 이어하기 / 설정.
 *   Title BGM (bgm.json 'title' = user-supplied title_user01.ogg) starts on the first key/click (browser autoplay rule,
 *   handled by bgm.js which follows window.__titleScreen.active), then crossfades into the town music on start.
 *   While active it swallows keys in the capture phase so the game behind it does not react.
 *   Skipped automatically under automation (navigator.webdriver) so existing headless tests are unaffected;
 *   URL ?titlescreen=1 forces it (also under automation), ?notitle skips it.
 */
(function () {
  'use strict';
  const Q = new URLSearchParams(location.search);
  const force = Q.get('titlescreen') === '1';
  if (!force && (Q.has('notitle') || Q.has('start') || navigator.webdriver)) { window.__titleScreen = { active: false, skipped: true }; return; }
  const LSQ = 'townDemo.quicksave';
  const hasSave = (() => { try { const d = JSON.parse(localStorage.getItem(LSQ)); return !!(d && d.v === 1); } catch (e) { return false; } })();
  const TS = window.__titleScreen = { active: true, stage: 'press', sel: 0, choice: null };

  const css = document.createElement('style');
  css.textContent = `
#ttl{position:fixed;inset:0;z-index:60;background:radial-gradient(ellipse at 50% 40%,#1b1630 0%,#08070f 70%,#000 100%);
 display:flex;flex-direction:column;align-items:center;justify-content:center;color:#e8d6b0;font-family:sans-serif;user-select:none;
 transition:opacity .9s ease;}
#ttl.out{opacity:0;pointer-events:none}
#ttl .logo{font:900 clamp(40px,8vw,92px)/1.1 serif;letter-spacing:.12em;color:#f3e2b8;
 text-shadow:0 0 18px #b8862b88,0 3px 0 #5a3b12,0 6px 18px #000;animation:ttlGlow 3.2s ease-in-out infinite alternate}
#ttl .sub{margin-top:10px;font:600 14px sans-serif;letter-spacing:.35em;color:#9a8c70}
#ttl .press{margin-top:64px;font:700 18px sans-serif;letter-spacing:.2em;color:#ffe08a;animation:ttlBlink 1.1s steps(2,start) infinite}
#ttl ul{list-style:none;margin:56px 0 0;padding:0;min-width:240px;text-align:center}
#ttl li{font:700 20px sans-serif;padding:7px 18px;margin:4px 0;color:#bfb08f;border:2px solid transparent;border-radius:4px}
#ttl li.on{color:#fff3c4;border-color:#e8d6b0;background:#ffffff10}
#ttl li.off{color:#5c5547}
#ttl .set{margin-top:22px;font:13px/1.7 sans-serif;color:#cdbf9c;text-align:center;min-height:3.4em}
#ttl .foot{position:absolute;bottom:14px;font:12px sans-serif;color:#6d6455}
@keyframes ttlGlow{from{text-shadow:0 0 10px #b8862b55,0 3px 0 #5a3b12,0 6px 18px #000}to{text-shadow:0 0 26px #e0a83caa,0 3px 0 #5a3b12,0 6px 18px #000}}
@keyframes ttlBlink{to{visibility:hidden}}`;
  const el = document.createElement('div'); el.id = 'ttl';
  el.innerHTML = '<div class="logo">제목 미정</div><div class="sub">TITLE NOT CHOSEN YET</div><div class="press">PRESS ANY KEY</div>' +
    '<ul hidden></ul><div class="set" hidden></div><div class="foot">↑↓ 선택 · Enter 결정 · Esc 뒤로</div>';
  const mount = () => { document.head.appendChild(css); document.body.appendChild(el); };
  document.body ? mount() : addEventListener('DOMContentLoaded', mount);
  const ul = el.querySelector('ul'), press = el.querySelector('.press'), set = el.querySelector('.set');

  const ITEMS = [
    { id: 'new', label: '새 게임', ok: true },
    { id: 'continue', label: '이어하기', ok: hasSave },
    { id: 'settings', label: '설정', ok: true },
  ];
  TS.sel = hasSave ? 1 : 0;
  function draw() {
    ul.innerHTML = ITEMS.map((it, i) => `<li data-i="${i}" class="${i === TS.sel ? 'on' : ''} ${it.ok ? '' : 'off'}">${it.label}${it.ok ? '' : ' (저장 없음)'}</li>`).join('');
    if (TS.stage === 'settings') {
      const s = window.BGM ? window.BGM.state : { vol: 0.6, muted: false };
      set.innerHTML = `음악 볼륨: <b>${s.muted ? '끔' : Math.round(s.vol * 100) + '%'}</b> &nbsp; ◀ ▶ 조절 · M 끄기/켜기<br>조작 키 변경 · 창 투명도는 게임 안 Esc 메뉴에서`;
      set.hidden = false;
    } else set.hidden = true;
  }
  function toMenu() { TS.stage = 'menu'; press.hidden = true; ul.hidden = false; draw(); }
  function startGame(choice) {
    TS.choice = choice;
    // owner 10-23: 새 게임 / 이어하기 both enter the real game (the hero sandbox had an older hero and dash; it is no longer reachable from the title)
    const hasWorld = (() => { try { const w = JSON.parse(localStorage.getItem('thor.world.v1') || '{}'); return Object.keys(w.quests || {}).length || Object.keys(w.flags || {}).length; } catch (e) { return false; } })();
    if (choice === 'new' && (hasSave || hasWorld)) {   // fresh run: no quick save, world progress reset (quests/flags), without deleting the quick save
      const q = new URLSearchParams(location.search); q.set('nosave', ''); q.set('notitle', ''); q.set('worldreset', '');
      location.search = q.toString().replace(/=(&|$)/g, '$1'); return;
    }
    TS.stage = 'out'; TS.active = false; el.classList.add('out');
    setTimeout(() => el.remove(), 1000);
  }
  function choose(i) {
    const it = ITEMS[i]; if (!it || !it.ok) return;
    if (it.id === 'settings') { TS.stage = TS.stage === 'settings' ? 'menu' : 'settings'; draw(); return; }
    startGame(it.id);
  }
  function key(e) {
    if (!TS.active) return;
    e.stopImmediatePropagation(); e.preventDefault();
    if (e.type !== 'keydown' || e.repeat && TS.stage === 'press') return;
    const c = e.code;
    if (TS.stage === 'press') { toMenu(); return; }
    if (TS.stage === 'settings' && window.BGM) {
      const s = window.BGM.state;
      if (c === 'ArrowLeft' || c === 'ArrowRight') { window.BGM.setVolume(Math.round((s.vol + (c === 'ArrowLeft' ? -0.1 : 0.1)) * 10) / 10); if (s.muted) window.BGM.toggleMute(); draw(); return; }
      if (c === 'KeyM') { window.BGM.toggleMute(); draw(); return; }
      if (c === 'Escape' || c === 'Backspace') { TS.stage = 'menu'; draw(); return; }
    }
    if (c === 'ArrowUp' || c === 'KeyW') { do TS.sel = (TS.sel + ITEMS.length - 1) % ITEMS.length; while (!ITEMS[TS.sel].ok); if (TS.stage === 'settings' && ITEMS[TS.sel].id !== 'settings') TS.stage = 'menu'; draw(); }
    else if (c === 'ArrowDown' || c === 'KeyS') { do TS.sel = (TS.sel + 1) % ITEMS.length; while (!ITEMS[TS.sel].ok); if (TS.stage === 'settings' && ITEMS[TS.sel].id !== 'settings') TS.stage = 'menu'; draw(); }
    else if (c === 'Enter' || c === 'Space' || c === 'KeyZ' || c === 'NumpadEnter') choose(TS.sel);
    else if (c === 'Escape' && TS.stage === 'menu') { TS.stage = 'press'; ul.hidden = true; press.hidden = false; }
  }
  // capture phase on window: runs before the game's own window listeners (bgm.js's first-input starter is registered earlier, so audio still unlocks)
  addEventListener('keydown', key, true); addEventListener('keyup', key, true); addEventListener('keypress', key, true);
  el.addEventListener('pointerdown', e => {
    e.stopPropagation();
    if (TS.stage === 'press') { toMenu(); return; }
    const li = e.target.closest('li'); if (li) { TS.sel = +li.dataset.i; choose(TS.sel); }
  });
  TS.choose = id => choose(ITEMS.findIndex(it => it.id === id));
})();
