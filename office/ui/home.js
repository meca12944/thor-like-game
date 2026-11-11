// 알들 컴퍼니 회사 홈·부서 화면. 보고 창은 여기서만 불러요.
// A = window.Aldeul. 색은 theme.css 이름만 써요. 움직임·네온 없음.
'use strict';
let homeMode = 'home';
let homeDeptId = '';
let homeConn = -1;
const HOME_DEPT_KEY = 'aldeulHomeDept';
let homeTopDraft = '';
let homeTopDeptMem = '';
let homeTopNote = null;
let homeTopBusy = false;

const HOME_DEPTS = [
  { id: 'game', name: '게임 필멸자', sub: '게임 코드·그림·영상·음악', icon: '🎮', lead: '클로드' },
  { id: 'zero', name: '제로폰', sub: '사이트·정책·개통 안내', icon: '📱', lead: '제로폰 홈페이지' },
  { id: 'promo', name: '홍보', sub: '블로그·마케팅·영상', icon: '📣', lead: '제로폰 홍보 · 제로폰 관리' },
  { id: 'admin', name: '경영지원', sub: '해피콜·안내·생산·투자', icon: '💼', lead: '폰클매니저 미래 오케이' },
  { id: 'stco', name: 'STCO', sub: '온라인·오프라인', icon: '🛍', lead: 'STCO 인동점 SEO·홍보' },
  { id: 'ai', name: 'AI 협력·연결', sub: '명령 중계·보고 창·클로드 연결', icon: '🔗', lead: '그록봇 최적화 예전 이벨린' },
];
function homeDepts(A) {
  const t = A && A.state && A.state.botTargets;
  if (t && Array.isArray(t.depts) && t.depts.length) return t;
  return { depts: HOME_DEPTS, bots: [] };
}
function homeConnOn(c, A) {
  const s = (A && A.state && A.state.settings) || {};
  const claude = A && A.state && A.state.claude;
  if (c.id === 'bot') return !!s.botFrom;
  if (c.id === 'reports') return !!s.reportsFile;
  if (c.id === 'game') return !!s.gameRepo;
  if (c.id === 'claude') return !!(claude && claude.ok);
  return false;
}
function homeTopRead() {
  try { return localStorage.getItem(HOME_DEPT_KEY) || ''; } catch (e) { return ''; }
}
function homeTopSave(name) {
  if (!name) return;
  homeTopDeptMem = name;
  try { localStorage.setItem(HOME_DEPT_KEY, name); } catch (e) { /* 기억 못 해도 이번 화면은 유지 */ }
}
function homeTopPick(pack) {
  const names = (pack.depts || []).map((d) => d.name).filter(Boolean);
  const saved = [homeTopDeptMem, homeTopRead()].find((n) => names.includes(n));
  if (saved) return saved;
  if (names.includes('AI 협력·연결')) return 'AI 협력·연결';
  return names[0] || '';
}
function homeTopPaintNote(root) {
  const note = root.querySelector('#homeTopNote');
  if (!note) return;
  if (!homeTopNote) {
    note.className = 'home-order-note hint';
    note.textContent = '부서를 고르고 할 일을 적은 뒤, 보내기나 엔터를 눌러요.';
    return;
  }
  note.className = 'home-order-note ' + (homeTopNote.ok ? 'ok' : 'bad');
  note.textContent = homeTopNote.text;
}
function homeSnap(el) {
  const cmd = el.querySelector('#homeTopCmd');
  const dept = el.querySelector('#homeTopDept');
  if (cmd) homeTopDraft = cmd.value;
  if (dept && dept.value) homeTopSave(dept.value);
  const ae = document.activeElement;
  const focusId = ae && el.contains(ae) ? ae.id : '';
  const caret = focusId === 'homeTopCmd' && cmd ? cmd.selectionStart : null;
  return { focusId, caret };
}
function homeRestoreFocus(el, snap) {
  if (!snap || (snap.focusId !== 'homeTopCmd' && snap.focusId !== 'homeTopDept')) return;
  const node = el.querySelector('#' + snap.focusId);
  if (!node || typeof node.focus !== 'function') return;
  node.focus();
  if (snap.focusId === 'homeTopCmd' && snap.caret != null && node.setSelectionRange) {
    const n = Math.min(snap.caret, node.value.length);
    node.setSelectionRange(n, n);
  }
}
function homeOrderHtml(pack, esc) {
  const picked = homeTopPick(pack);
  const opts = (pack.depts || []).map((d) => {
    const on = d.name === picked ? ' selected' : '';
    return `<option value="${esc(d.name)}"${on}>${esc(d.icon || '🏢')} ${esc(d.name)}</option>`;
  }).join('');
  return `<form class="home-order" id="homeTopSend">
    <div class="home-order-row">
      <b class="home-order-title">✍️ 일 시키기</b>
      <label class="home-order-pick">보낼 곳
        <select id="homeTopDept">${opts}</select>
      </label>
      <input id="homeTopCmd" type="text" autocomplete="off" placeholder="할 일을 적고 엔터 (예: 오늘 할 일 정리해서 보고해)" value="${esc(homeTopDraft)}">
      <button class="btn" type="submit">보내기</button>
    </div>
    <div id="homeTopNote" class="home-order-note hint">부서를 고르고 할 일을 적은 뒤, 보내기나 엔터를 눌러요.</div>
  </form>`;
}
async function homeTopSend(el, A) {
  if (homeTopBusy) return;
  const sel = el.querySelector('#homeTopDept');
  const inp = el.querySelector('#homeTopCmd');
  const name = sel ? String(sel.value || '').trim() : '';
  const command = inp ? String(inp.value || '').trim() : '';
  if (inp) homeTopDraft = inp.value;
  if (name) homeTopSave(name);
  if (!name) { homeTopNote = { ok: false, text: '보낼 곳을 골라 주세요.' }; homeTopPaintNote(el); return; }
  if (!command) { homeTopNote = { ok: false, text: '할 일을 적어 주세요.' }; homeTopPaintNote(el); return; }
  homeTopBusy = true;
  const btn = el.querySelector('#homeTopSend button[type="submit"]');
  if (btn) btn.disabled = true;
  let r = null;
  try {
    r = await A.api('/api/bot/command', { target: name, command });
  } catch (e) {
    r = { ok: false, error: '못 보냈어요. 회사 프로그램이 켜져 있는지 봐 주세요.' };
  }
  homeTopBusy = false;
  const btnNow = el.querySelector('#homeTopSend button[type="submit"]');
  if (btnNow) btnNow.disabled = false;
  if (!r || !r.ok) {
    homeTopNote = { ok: false, text: (r && r.error) || '못 보냈어요' };
    homeTopPaintNote(el);
    return;
  }
  homeTopDraft = '';
  const inpNow = el.querySelector('#homeTopCmd');
  if (inpNow) inpNow.value = '';
  homeTopNote = { ok: true, text: name + '에 보냈어요. 그록이 받았어요 → 보고 창에 접수로 떠요' };
  homeTopPaintNote(el);
  reportAt = 0;
  const slot = el.querySelector('#homeReports');
  if (typeof renderReports === 'function' && slot) renderReports(slot);
}
function homePaint(el, A) {
  const snap = homeSnap(el);
  const pack = homeDepts(A);
  const esc = A.esc;
  if (homeMode === 'dept') return homePaintDept(el, A, pack, esc);
  if (homeMode === 'conn') return homePaintConn(el, A, esc);
  const tiles = pack.depts.map((d) => `<button type="button" class="tile" data-home="dept" data-id="${esc(d.id)}"><div class="ico">${d.icon || '🏢'}</div><div class="nm">${esc(d.name)}</div><div class="ds">${esc(d.sub || '')}</div></button>`).join('');
  el.innerHTML = `<div class="home-page home-fit">
    ${homeOrderHtml(pack, esc)}
    <div class="home-grid">
      <section class="home-col home-col-reports">
        <div id="homeReports"></div>
      </section>
      <section class="home-col home-col-work">
        <div class="title">🏢 부서 <span class="muted small">아이콘을 누르면 그 부서 화면</span></div>
        <div class="home-depts">${tiles}</div>
        <div class="home-shortcuts">
          <button type="button" class="btn" data-home="workshop">🧠 클로드 작업장</button>
          <button type="button" class="btn ghost" data-home="conn">🔌 연결 설명</button>
        </div>
      </section>
      <section class="home-col home-col-chat">
        <div class="title">💬 클로드 ↔ 그록 <span class="muted small">최근 말</span><button type="button" class="link" data-act="coopall">모두 보기</button></div>
        <div id="homeChat" class="home-chat"></div>
      </section>
    </div>
  </div>`;
  homeTopPaintNote(el);
  homeRestoreFocus(el, snap);
  if (typeof renderReports === 'function') renderReports(el.querySelector('#homeReports'));
  const chat = el.querySelector('#homeChat');
  if (chat && typeof A.chatWidget === 'function') A.chatWidget(chat, 4);
  else if (chat && typeof A.coopChat === 'function') A.coopChat(chat);
}
function homePaintDept(el, A, pack, esc) {
  const d = pack.depts.find((x) => x.id === homeDeptId) || { id: homeDeptId, name: '부서', icon: '🏢', sub: '' };
  const bots = (pack.bots || []).filter((b) => b.dept === d.id);
  const people = bots.length
    ? `<ul class="dept-people">${bots.map((b) => `<li><b>${esc(b.name)}</b>${b.lead ? ' <span class="muted small">(팀장)</span>' : ''} — ${esc(b.role || '')}</li>`).join('')}</ul>`
    : '<p class="muted">아직 팀원 목록이 없어요.</p>';
  const game = d.id === 'game';
  const blurb = game
    ? '게임 일을 직접 보려면 오른쪽 위 「클로드 작업장」을 눌러요.'
    : '오른쪽에 할 일을 적으면 팀장이 나눠 맡기고, 끝나면 보고 창에 올려요.';
  el.innerHTML = `<div class="dept-page home-fit">
    <div class="dept-bar">
      <button type="button" class="btn ghost" data-home="back">← 회사 홈</button>
      <div class="dept-name"><span class="ico">${d.icon || '🏢'}</span><div><b>${esc(d.name)}</b><div class="muted small">${esc(d.sub || '')}${d.lead ? ` · 팀장 ${esc(d.lead)}` : ''}</div></div></div>
      ${game ? '<button type="button" class="btn" data-home="workshop">🧠 클로드 작업장</button>' : ''}
    </div>
    <div class="dept-grid">
      <section class="card dept-card"><b>👥 팀원</b><div class="muted small">${blurb}</div>${people}</section>
      <form class="card dept-card dept-send" id="homeSend">
        <b>✍️ 이 부서에 일 시키기</b>
        <div class="muted small">예: ${game ? '보스 그림 정리해서 보고해' : '오늘 할 일 정리해서 보고해'}</div>
        <textarea id="homeCmd" class="home-text" rows="4" placeholder="할 일을 적어 주세요"></textarea>
        <div id="homeSendErr" class="home-err"></div>
        <button class="btn" type="submit">보내기</button>
      </form>
    </div>
  </div>`;
  const form = el.querySelector('#homeSend');
  if (form) form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const command = (el.querySelector('#homeCmd').value || '').trim();
    const err = el.querySelector('#homeSendErr');
    if (!command) { err.textContent = '할 일을 적어 주세요.'; return; }
    const r = await A.api('/api/bot/command', { target: d.name, command });
    if (!r.ok) { err.textContent = r.error || '못 보냈어요'; return; }
    err.textContent = '';
    el.querySelector('#homeCmd').value = '';
    A.toast(d.name + '에 보냈어요');
    reportAt = 0;
  });
}
function homePaintConn(el, A, esc) {
  const list = window.AldeulGrokConnectors || [];
  const tiles = list.map((c, i) => {
    const on = homeConnOn(c, A);
    const sel = i === homeConn ? ' sel' : '';
    return `<button type="button" class="tile${sel}" data-home="connone" data-i="${i}"><span class="lamp ${on ? 'on' : 'off'}">${on ? '🟢' : '⚪'}</span><div class="ico">${esc(c.ico || '🔗')}</div><div class="nm">${esc(c.nm || '')}</div><div class="ds">${esc(c.ds || '')}</div></button>`;
  }).join('');
  const c = list[homeConn];
  const detail = c ? `<div class="card conn-detail" id="connDetail">
      <div class="conn-head"><span class="ico">${esc(c.ico || '🔗')}</span><div><b>${esc(c.nm || '')}</b><div class="muted small">${esc(c.ds || '')}</div></div></div>
      <div class="qa"><div class="qh">이게 뭐예요?</div>${esc(c.what || '')}</div>
      <div class="qa"><div class="qh">무슨 기능?</div>${esc(c.func || '')}</div>
      <div class="qa"><div class="qh">어떻게 켜요?</div>${esc(c.how || '')}</div>
    </div>` : `<div class="card conn-detail"><b>아이콘을 눌러 주세요</b><p class="muted">왼쪽 아이콘을 누르면, 무엇인지와 켜는 법이 여기에 나와요. 초록 불은 정말 이어졌을 때만 켜져요.</p></div>`;
  el.innerHTML = `<div class="conn-page home-fit">
    <div class="dept-bar">
      <button type="button" class="btn ghost" data-home="back">← 회사 홈</button>
      <div class="title" style="margin:0">🔌 연결 설명 <span class="muted small">초록 불은 정말 이어졌을 때만 켜져요</span></div>
    </div>
    <div class="conn-grid">
      <div class="tiles home-conn-tiles">${tiles}</div>
      ${detail}
    </div>
  </div>`;
}
function homeBind(el, A) {
  if (el.dataset.homeBound === '1') return;
  el.dataset.homeBound = '1';
  el.addEventListener('submit', (ev) => {
    const form = ev.target;
    if (!form || form.id !== 'homeTopSend' || !el.contains(form)) return;
    ev.preventDefault();
    homeTopSend(el, A);
  });
  el.addEventListener('change', (ev) => {
    const t = ev.target;
    if (!t || t.id !== 'homeTopDept' || !el.contains(t)) return;
    homeTopSave(t.value);
  });
  el.addEventListener('input', (ev) => {
    const t = ev.target;
    if (!t || t.id !== 'homeTopCmd' || !el.contains(t)) return;
    homeTopDraft = t.value;
    if (homeTopNote) { homeTopNote = null; homeTopPaintNote(el); }
  });
  el.addEventListener('click', (ev) => {
    const b = ev.target.closest('[data-home]');
    if (!b || !el.contains(b)) return;
    const act = b.getAttribute('data-home');
    if (act === 'back') { homeMode = 'home'; homeConn = -1; }
    else if (act === 'dept') { homeMode = 'dept'; homeDeptId = b.getAttribute('data-id') || ''; }
    else if (act === 'workshop') { if (A.openWorkshop) A.openWorkshop(); return; }
    else if (act === 'conn') { homeMode = 'conn'; homeConn = -1; }
    else if (act === 'connone') { homeMode = 'conn'; homeConn = Number(b.getAttribute('data-i')); }
    else return;
    homePaint(el, A);
  });
}
window.AldeulHome = {
  render(el, A) {
    if (!el || !A) return;
    homeBind(el, A);
    homePaint(el, A);
  },
};
// 상태 알림이 이 파일보다 먼저 와도, 홈을 한 번 그려요.
if (window.Aldeul && document.getElementById('home') && window.Aldeul.view === 'home') {
  window.AldeulHome.render(document.getElementById('home'), window.Aldeul);
}
