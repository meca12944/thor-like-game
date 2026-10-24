/* [title] Title screen "C" (docs_art/title_screen, 고성으로 향하는 외길) — self-contained, never touches game logic.
 *   Owner 10-24 「가만히 서있다가 스타트 누르면 움직이는걸로」:
 *     idle   : still picture (= frame 0 of the bg loop) + logo + live menu 새 게임 / 이어하기 / 설정. Nothing moves.
 *     start  : 새 게임 or 이어하기 -> the bg video plays from frame 0, logo + menu fade out,
 *              after TITLE_INTRO_SEC the screen fades to black and the game appears.
 *   Layers: bg (still/video) covers the whole screen (object-fit: cover, like the game canvas which fills the window);
 *   the logo is drawn in a 1920x1080 stage scaled to fit (contain) so it is never cropped; the menu is live DOM text
 *   placed at the README coordinates (row, centre x 1360, y 962 @1920x1080, 나눔명조, #F0E4C8 / #C8BA9E, red diamond #B04034).
 *   The baked menu in title_c_overlay.png is NOT used (it cannot show the selection or a disabled 이어하기), so the logo
 *   layer is title_c_logo.png = overlay minus menu (docs_art/title_screen/make_logo_overlay.py).
 *   Title BGM (bgm.json 'title') starts on the first key/click (bgm.js follows window.__titleScreen.active, which stays
 *   true until the fade to black so the title theme keeps playing during the animation), then crossfades into the town music.
 *   While active it swallows keys in the capture phase so the game behind it does not react.
 *   Skipped automatically under automation (navigator.webdriver) so existing headless tests are unaffected;
 *   URL ?titlescreen=1 forces it (also under automation), ?notitle skips it, ?titleintro=9 overrides TITLE_INTRO_SEC.
 */
(function () {
  'use strict';
  // ---- timing (change here) ----
  // Seconds the bg video plays after Start before the screen is fully black. 'full' = play the whole 9.04 s loop once.
  const TITLE_INTRO_SEC = 3;
  const OVERLAY_FADE_SEC = 0.7;   // logo + menu fade-out right after Start
  const BLACK_FADE_SEC = 0.9;     // fade to black at the end of the intro (part of TITLE_INTRO_SEC)
  const REVEAL_SEC = 0.8;         // black -> game fade-in
  const LOOP_SEC = 217 / 24;      // title_c_bg.mp4 length (9.04 s)
  const A = 'assets/title/';
  const STILL = A + 'title_c_still.jpg', VIDEO = A + 'title_c_bg.mp4', LOGO = A + 'title_c_logo.png';

  const Q = new URLSearchParams(location.search);
  const force = Q.get('titlescreen') === '1';
  // reloaded after 새 게임 (fresh-run URL): start black and fade into the game, so the intro's fade-out continues seamlessly
  if (Q.has('ttlfade') && !force) {
    const cover = document.createElement('div');
    cover.style.cssText = `position:fixed;inset:0;z-index:61;background:#000;pointer-events:none;transition:opacity ${REVEAL_SEC}s ease`;
    const put = () => { document.body.appendChild(cover); setTimeout(() => { cover.style.opacity = '0'; setTimeout(() => cover.remove(), REVEAL_SEC * 1000 + 100); }, 150); };
    document.body ? put() : addEventListener('DOMContentLoaded', put);
    try { const q = new URLSearchParams(location.search); q.delete('ttlfade'); history.replaceState(null, '', location.pathname + (q.toString() ? '?' + q.toString().replace(/=(&|$)/g, '$1') : '') + location.hash); } catch (e) {}
  }
  if (!force && (Q.has('notitle') || Q.has('start') || navigator.webdriver)) { window.__titleScreen = { active: false, skipped: true }; return; }
  const qi = Q.get('titleintro');
  const introSec = qi === 'full' ? LOOP_SEC : (qi && +qi > 0) ? +qi : TITLE_INTRO_SEC === 'full' ? LOOP_SEC : TITLE_INTRO_SEC;
  const LSQ = 'townDemo.quicksave';
  // save versions = the ones index.html loadQuick() accepts (quickSave writes v:3; the old title only knew v:1, so 이어하기 was always greyed out)
  const hasSave = (() => { try { const d = JSON.parse(localStorage.getItem(LSQ)); return !!(d && (d.v === 1 || d.v === 2 || d.v === 3)); } catch (e) { return false; } })();
  const TS = window.__titleScreen = { active: true, stage: 'menu', sel: 0, choice: null, introSec };

  const css = document.createElement('style');
  css.textContent = `
@font-face{font-family:TtlMyeongjo;font-weight:400;src:url(${A}nanum_myeongjo_regular_sub.woff) format('woff')}
@font-face{font-family:TtlMyeongjo;font-weight:700;src:url(${A}nanum_myeongjo_bold_sub.woff) format('woff')}
#ttl{position:fixed;inset:0;z-index:60;background:#000;overflow:hidden;user-select:none;-webkit-user-select:none;color:#F0E4C8}
#ttl .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
#ttl video.bg{opacity:0}
#ttl video.bg.on{opacity:1}
#ttl .shade{position:absolute;left:0;right:0;bottom:0;height:28%;pointer-events:none;
 background:linear-gradient(to bottom,rgba(18,10,6,0) 0%,rgba(18,10,6,.07) 25%,rgba(18,10,6,.25) 50%,rgba(18,10,6,.45) 75%,rgba(18,10,6,.67) 100%)}
#ttl .fadeable{transition:opacity ${OVERLAY_FADE_SEC}s ease}
#ttl.go .fadeable{opacity:0;pointer-events:none}
#ttl .stage{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0;pointer-events:none}
#ttl .stage img{position:absolute;left:0;top:0;width:1920px;height:540px}
#ttl ul{position:absolute;margin:0;padding:0;list-style:none;display:flex;transform:translateX(-50%);white-space:nowrap;
 font-family:TtlMyeongjo,'Nanum Myeongjo','NanumMyeongjo',serif;letter-spacing:.15em;line-height:1.15}
#ttl li{position:relative;cursor:pointer;color:#C8BA9E;font-weight:400;text-shadow:.07em .1em .15em rgba(15,8,4,.85),0 0 .3em rgba(15,8,4,.6)}
#ttl li.on{color:#F0E4C8;font-weight:700}
#ttl li.on::before{content:'';position:absolute;left:-.75em;top:.4em;width:.32em;height:.32em;background:#B04034;transform:rotate(45deg)}
#ttl li.off{color:#6f6656;cursor:default}
#ttl li small{position:absolute;left:50%;top:100%;transform:translateX(-50%);font:600 max(.42em,10px) sans-serif;letter-spacing:.1em;color:#8a7f6a;white-space:nowrap}
#ttl .set{position:absolute;transform:translateX(-50%);font:14px/1.7 sans-serif;color:#e8dcc0;text-align:center;background:#120a06b0;
 padding:8px 16px;border-radius:4px;white-space:nowrap;text-shadow:1px 1px 0 #000}
#ttl .foot{position:absolute;right:12px;bottom:8px;font:12px sans-serif;color:#cdbf9c99;text-shadow:1px 1px 0 #000}
#ttl .black{position:absolute;inset:0;background:#000;opacity:0;pointer-events:none;transition:opacity ${BLACK_FADE_SEC}s ease-in}
#ttl.end .black{opacity:1}
#ttl.out{opacity:0;pointer-events:none;transition:opacity ${REVEAL_SEC}s ease}`;
  const el = document.createElement('div'); el.id = 'ttl';
  el.innerHTML = `<img class="bg still" alt="" src="${STILL}"><video class="bg" muted playsinline preload="auto" disablepictureinpicture></video>` +
    `<div class="shade fadeable"></div><div class="stage fadeable"><img alt="Trail of Extinction · 사멸의 궤적" src="${LOGO}"></div>` +
    `<ul class="fadeable"></ul><div class="set fadeable" hidden></div><div class="foot fadeable">←→ / ↑↓ 선택 · Enter 결정</div><div class="black"></div>`;
  const ul = el.querySelector('ul'), set = el.querySelector('.set'), stage = el.querySelector('.stage');
  const still = el.querySelector('img.still'), video = el.querySelector('video');
  video.muted = true; video.defaultMuted = true; video.setAttribute('muted', ''); video.playsInline = true;
  let videoOk = true;
  video.addEventListener('error', () => { videoOk = false; }, true);
  video.src = VIDEO;
  // loop only when the intro is longer than one pass of the clip (default 3 s and 'full' play a single pass from frame 0)
  video.loop = introSec > LOOP_SEC + 0.05;
  const mount = () => { document.head.appendChild(css); document.body.appendChild(el); layout(); };
  document.body ? mount() : addEventListener('DOMContentLoaded', mount);

  // ---- layout: logo stage = contain-fit 1920x1080; menu at README coords (landscape) or a centred column (portrait) ----
  function layout() {
    const W = innerWidth, H = innerHeight, narrow = W / H < 1.2;
    // portrait/narrow: logo pinned to the top and scaled to the screen width (the logo itself is ~1100 px of the 1920 stage)
    const s = narrow ? W / 1150 : Math.min(W / 1920, H / 1080);
    const ox = (W - 1920 * s) / 2, oy = narrow ? 0 : (H - 1080 * s) / 2;
    stage.style.transform = `translate(${ox}px,${oy}px) scale(${s})`;
    if (!narrow) {
      const fs = Math.max(40 * s, 15);
      Object.assign(ul.style, { flexDirection: 'row', gap: (90 * s) + 'px', alignItems: 'baseline', left: (ox + 1360 * s) + 'px', top: (oy + 962 * s - (fs - 40 * s) * 0.6) + 'px', bottom: '', fontSize: fs + 'px' });
      Object.assign(set.style, { left: (ox + 1360 * s) + 'px', top: '', bottom: (H - (oy + 962 * s) + 18) + 'px' });
    } else {
      Object.assign(ul.style, { flexDirection: 'column', gap: '18px', alignItems: 'center', left: '50%', top: '', bottom: '12%', fontSize: '24px' });
      Object.assign(set.style, { left: '50%', top: '', bottom: 'calc(12% + 190px)' });
    }
  }
  addEventListener('resize', layout);

  const ITEMS = [
    { id: 'new', label: '새 게임', ok: true },
    { id: 'continue', label: '이어하기', ok: hasSave },
    { id: 'settings', label: '설정', ok: true },
  ];
  TS.sel = hasSave ? 1 : 0;
  function draw() {
    ul.innerHTML = ITEMS.map((it, i) => `<li data-i="${i}" class="${i === TS.sel ? 'on' : ''} ${it.ok ? '' : 'off'}">${it.label}${it.ok ? '' : '<small>저장 없음</small>'}</li>`).join('');
    if (TS.stage === 'settings') {
      const s = window.BGM ? window.BGM.state : { vol: 0.6, muted: false };
      set.innerHTML = `음악 볼륨: <b>${s.muted ? '끔' : Math.round(s.vol * 100) + '%'}</b> &nbsp; ◀ ▶ 조절 · M 끄기/켜기 · Esc 닫기<br>조작 키 변경 · 창 투명도는 게임 안 Esc 메뉴에서`;
      set.hidden = false;
    } else set.hidden = true;
  }
  draw();

  // ---- Start: still -> video plays from frame 0, overlay fades, then black, then the game ----
  function startGame(choice) {
    if (TS.stage === 'intro') return;
    TS.choice = choice; TS.stage = 'intro'; TS.introT0 = performance.now();
    el.classList.add('go');
    // video: frame 0 == the still, so it is only revealed once it is really playing (no flash); on failure the still stays
    if (videoOk) {
      try { video.currentTime = 0; } catch (e) {}
      const p = video.play();
      const reveal = () => { video.classList.add('on'); TS.videoPlaying = true; };
      if (p && p.then) p.then(() => { if (video.readyState >= 2) reveal(); else video.addEventListener('playing', reveal, { once: true }); }).catch(() => { TS.videoFailed = true; });
      else video.addEventListener('playing', reveal, { once: true });
    } else TS.videoFailed = true;
    const blackAt = Math.max(0.3, introSec - BLACK_FADE_SEC);
    setTimeout(() => el.classList.add('end'), blackAt * 1000);
    setTimeout(() => enterGame(choice), introSec * 1000);
  }
  function enterGame(choice) {
    // owner 10-23: 새 게임 / 이어하기 both enter the real game (the hero sandbox had an older hero and dash; it is no longer reachable from the title)
    const hasWorld = (() => { try { const w = JSON.parse(localStorage.getItem('thor.world.v1') || '{}'); return Object.keys(w.quests || {}).length || Object.keys(w.flags || {}).length; } catch (e) { return false; } })();
    if (choice === 'new' && (hasSave || hasWorld)) {   // fresh run: no quick save, world progress reset (quests/flags), without deleting the quick save
      const q = new URLSearchParams(location.search); q.set('nosave', ''); q.set('notitle', ''); q.set('worldreset', ''); q.set('ttlfade', ''); q.delete('titlescreen');
      location.search = q.toString().replace(/=(&|$)/g, '$1'); return;
    }
    TS.stage = 'out'; TS.active = false;
    try { video.pause(); } catch (e) {}
    el.classList.add('out');
    setTimeout(() => { el.remove(); try { video.removeAttribute('src'); video.load(); } catch (e) {} }, REVEAL_SEC * 1000 + 100);
  }
  function choose(i) {
    const it = ITEMS[i]; if (!it || !it.ok) return;
    if (it.id === 'settings') { TS.stage = TS.stage === 'settings' ? 'menu' : 'settings'; draw(); return; }
    startGame(it.id);
  }
  function move(d) {
    do TS.sel = (TS.sel + ITEMS.length + d) % ITEMS.length; while (!ITEMS[TS.sel].ok);
    if (TS.stage === 'settings' && ITEMS[TS.sel].id !== 'settings') TS.stage = 'menu';
    draw();
  }
  function key(e) {
    if (!TS.active) return;
    e.stopImmediatePropagation(); e.preventDefault();
    if (e.type !== 'keydown' || TS.stage === 'intro' || TS.stage === 'out') return;
    const c = e.code;
    if (TS.stage === 'settings' && window.BGM) {
      const s = window.BGM.state;
      if (c === 'ArrowLeft' || c === 'ArrowRight') { window.BGM.setVolume(Math.round((s.vol + (c === 'ArrowLeft' ? -0.1 : 0.1)) * 10) / 10); if (s.muted) window.BGM.toggleMute(); draw(); return; }
      if (c === 'KeyM') { window.BGM.toggleMute(); draw(); return; }
      if (c === 'Escape' || c === 'Backspace') { TS.stage = 'menu'; draw(); return; }
    }
    if (e.repeat && (c === 'Enter' || c === 'Space' || c === 'KeyZ' || c === 'NumpadEnter')) return;
    if (c === 'ArrowLeft' || c === 'ArrowUp' || c === 'KeyA' || c === 'KeyW') move(-1);
    else if (c === 'ArrowRight' || c === 'ArrowDown' || c === 'KeyD' || c === 'KeyS') move(1);
    else if (c === 'Enter' || c === 'Space' || c === 'KeyZ' || c === 'NumpadEnter') choose(TS.sel);
    else if (c === 'Escape' && TS.stage === 'settings') { TS.stage = 'menu'; draw(); }
  }
  // capture phase on window: runs before the game's own window listeners (bgm.js's first-input starter is registered earlier, so audio still unlocks)
  addEventListener('keydown', key, true); addEventListener('keyup', key, true); addEventListener('keypress', key, true);
  el.addEventListener('pointerdown', e => {
    e.stopPropagation();
    if (TS.stage === 'intro' || TS.stage === 'out') return;
    const li = e.target.closest('li'); if (li) { TS.sel = +li.dataset.i; choose(TS.sel); }
  });
  TS.choose = id => choose(ITEMS.findIndex(it => it.id === id));
})();
