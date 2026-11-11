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
  if (!homeTopNote) { note.textContent = ''; note.className = 'home-order-note'; return; }
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
    <div class="home-order-head"><b>✍️ 일 시키기</b><span class="muted small">보낼 부서를 고르고 할 일을 적어요. 엔터를 눌러도 바로 보내요.</span></div>
    <div class="home-order-row">
      <label class="home-order-pick">보낼 곳
        <select id="homeTopDept">${opts}</select>
      </label>
      <input id="homeTopCmd" type="text" autocomplete="off" placeholder="할 일을 적고 엔터 (예: 오늘 할 일 정리해서 보고해)" value="${esc(homeTopDraft)}">
      <button class="btn" type="submit">보내기</button>
    </div>
    <div id="homeTopNote" class="home-order-note"></div>
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
  el.innerHTML = `<div class="home-page">
    ${homeOrderHtml(pack, esc)}
    <div class="home-wrap">
      <section>
        <div id="homeReports"></div>
      </section>
      <section>
        <div class="title">🏢 부서 <span class="muted small">이름을 누르면 부서 화면이 나와요</span></div>
        <div class="tiles">${tiles}</div>
        <div class="title" style="margin-top:8px">🔌 연결 <span class="muted small">이게 무엇인지 먼저 봐요</span></div>
        <button type="button" class="btn ghost" data-home="conn">🔌 연결 설명 보기</button>
        <div class="title" style="margin-top:8px">💬 클로드 ↔ 그록 대화 <span class="muted small">둘이 나눈 말</span></div>
        <div id="homeChat"></div>
      </section>
    </div>
  </div>`;
  homeTopPaintNote(el);
  homeRestoreFocus(el, snap);
  if (typeof renderReports === 'function') renderReports(el.querySelector('#homeReports'));
  const chat = el.querySelector('#homeChat');
  if (chat && typeof A.coopChat === 'function') A.coopChat(chat);
  else if (chat && typeof A.chatWidget === 'function') A.chatWidget(chat, 4);
}
function homePaintDept(el, A, pack, esc) {
  const d = pack.depts.find((x) => x.id === homeDeptId) || { id: homeDeptId, name: '부서', icon: '🏢', sub: '' };
  const bots = (pack.bots || []).filter((b) => b.dept === d.id);
  const people = bots.length ? bots.map((b) => `• <b>${esc(b.name)}</b>${b.lead ? ' (팀장)' : ''} — ${esc(b.role || '')}`).join('<br>') : '아직 팀원 목록이 없어요.';
  const game = d.id === 'game';
  el.innerHTML = `<div>
    <button type="button" class="btn ghost" data-home="back">← 회사 홈</button>
    <div class="card" style="margin-top:12px">
      <div class="card-head"><span class="ico" style="font-size:28px">${d.icon || '🏢'}</span><b>${esc(d.name)}</b></div>
      <div class="muted small">${esc(d.sub || '')}${d.lead ? ` · 팀장 ${esc(d.lead)}` : ''}</div>
      ${game ? `<p>여기는 게임 부서 화면이에요. 작업장은 아래 단추를 눌러야 열려요.</p><button type="button" class="btn" data-home="workshop">🧠 클로드 작업장</button>` : '<p>이 부서에 일을 적으면 팀장이 나눠 맡기고, 끝난 뒤 보고 창에 올려요.</p>'}
    </div>
    <div class="card" style="margin-top:12px"><b>👥 팀원</b><div style="margin-top:6px">${people}</div></div>
    <form class="card" id="homeSend" style="margin-top:12px">
      <b>✍️ 이 부서에 일 시키기</b>
      <div class="muted small">예: ${game ? '보스 그림 정리해서 보고해' : '오늘 할 일 정리해서 보고해'}</div>
      <textarea id="homeCmd" rows="3" style="width:100%;margin-top:8px;padding:8px 10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--text)" placeholder="할 일을 한 줄로 적어요"></textarea>
      <div id="homeSendErr" style="color:var(--red);min-height:1.2em"></div>
      <button class="btn" type="submit">보내기</button>
    </form>
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
    return `<button type="button" class="tile" data-home="connone" data-i="${i}"><span class="lamp ${on ? 'on' : 'off'}">${on ? '🟢' : '⚪'}</span><div class="ico">${esc(c.ico || '🔗')}</div><div class="nm">${esc(c.nm || '')}</div><div class="ds">${esc(c.ds || '')}</div></button>`;
  }).join('');
  const c = list[homeConn];
  const detail = c ? `<div class="card" id="connDetail" style="margin-top:12px">
      <b>${esc(c.ico || '')} ${esc(c.nm || '')}</b>
      <div style="margin-top:8px"><b>이게 뭐예요?</b><div>${esc(c.what || '')}</div></div>
      <div style="margin-top:8px"><b>무슨 기능?</b><div>${esc(c.func || '')}</div></div>
      <div style="margin-top:8px"><b>어떻게 켜요?</b><div>${esc(c.how || '')}</div></div>
    </div>` : '';
  el.innerHTML = `<div>
    <button type="button" class="btn ghost" data-home="back">← 회사 홈</button>
    <div class="title" style="margin-top:12px">🔌 연결 설명 <span class="muted small">초록 불은 정말 이어졌을 때만 켜져요</span></div>
    <div class="tiles">${tiles}</div>
    ${detail}
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
