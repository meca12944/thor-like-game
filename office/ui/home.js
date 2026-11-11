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
let homeTeamBusy = false;
let homeDeptNote = null;
let homeDeptFolder = '';

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
function homeClaudeList(A, deptId) {
  const all = (A && A.state && A.state.employees) || [];
  return all.filter((e) => (e.dept || 'game') === deptId);
}
function homeJobLine(e, esc) {
  const raw = String(e.task || e.wait || '').replace(/\s+/g, ' ').trim();
  if (!raw) return '';
  let nice = '';
  const boxed = raw.match(/부서 일\]\s*(.+?)(?:\s+너는 이 부서|$)/);
  if (boxed) nice = boxed[1];
  else {
    const lines = String(e.task || e.wait || '').split('\n').map((s) => s.trim()).filter(Boolean);
    nice = lines.find((s) => s.charAt(0) !== '[' && s.indexOf('너는 이 부서') !== 0) || '';
  }
  nice = nice.trim();
  if (!nice) return '';
  return `<div class="muted small">${e.task ? '지금' : '맡은 일'}: ${esc(nice.slice(0, 90))}</div>`;
}
function homePeopleHtml(list, esc, claude) {
  if (!list.length) return '';
  const sorted = list.slice().sort((a, b) => (b.lead === true) - (a.lead === true) || String(a.name).localeCompare(String(b.name), 'ko'));
  return `<ul class="dept-people">${sorted.map((p) => {
    const lead = p.lead ? ' <span class="muted small">(팀장)</span>' : '';
    const job = claude ? homeJobLine(p, esc) : '';
    return `<li><b>${esc(p.name)}</b>${lead} — ${esc(p.role || '')}${job}</li>`;
  }).join('')}</ul>`;
}
async function homeMakeTeams(A) {
  if (homeTeamBusy) return;
  homeTeamBusy = true;
  if (A.toast) A.toast('클로드 팀 자리를 만드는 중이에요');
  let r = null;
  try { r = await A.api('/api/team'); }
  catch (e) { r = { ok: false, error: '회사 프로그램이 켜져 있는지 봐 주세요.' }; }
  homeTeamBusy = false;
  if (!r || !r.ok) { if (A.toast) A.toast((r && r.error) || '못 만들었어요'); return; }
  const n = (r.made || []).length;
  if (A.toast) A.toast(n ? '클로드 직원 ' + n + '명을 만들었어요' : '이미 모든 부서에 클로드 직원이 있어요');
}
async function homeMakeDept(A) {
  if (homeTeamBusy) return;
  const dept = homeDeptId;
  const folder = String(homeDeptFolder || '').trim();
  homeTeamBusy = true;
  if (A.toast) A.toast('이 부서 직원을 만드는 중이에요');
  let r = null;
  try { r = await A.api('/api/team', { dept, folder }); }
  catch (e) { r = { ok: false, error: '회사 프로그램이 켜져 있는지 봐 주세요.' }; }
  homeTeamBusy = false;
  if (!r || !r.ok) { if (A.toast) A.toast((r && r.error) || '못 만들었어요'); return; }
  const n = (r.made || []).length;
  if (A.toast) A.toast(n ? '클로드 직원 ' + n + '명을 만들었어요' : '이 부서에는 이미 클로드 직원이 다 있어요');
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
    let text = (r && r.error) || '못 보냈어요';
    if (r && r.claudeLead && text.indexOf(r.claudeLead) < 0) text += ' 클로드 팀장 ' + r.claudeLead + '에게는 넣어 두었어요.';
    homeTopNote = { ok: false, text };
    homeTopPaintNote(el);
    return;
  }
  homeTopDraft = '';
  const inpNow = el.querySelector('#homeTopCmd');
  if (inpNow) inpNow.value = '';
  const leadBit = r.claudeLead ? ' 클로드 ' + r.claudeLead + '에게도 넣었어요.' : '';
  homeTopNote = { ok: true, text: name + '에 보냈어요. 그록이 받았어요.' + leadBit + ' → 보고 창에 접수로 떠요' };
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
  const tiles = pack.depts.map((d) => {
    const n = homeClaudeList(A, d.id).length;
    return `<button type="button" class="tile" data-home="dept" data-id="${esc(d.id)}"><div class="ico">${d.icon || '🏢'}</div><div class="nm">${esc(d.name)}</div><div class="ds">${esc(d.sub || '')}</div><div class="home-cnt">클로드 ${n}명</div></button>`;
  }).join('');
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
        <button type="button" class="btn ghost home-team-btn" data-home="team">👥 부서마다 클로드 팀 만들기</button>
        <div class="muted small">누르기 전에는 만들지 않아요. 한 부서만 만들려면 그 부서 화면의 「만들기」를 눌러요.</div>
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
  const claude = homeClaudeList(A, d.id);
  const lead = claude.find((e) => e.lead) || claude.find((e) => /팀장$/.test(e.name));
  const claudeHtml = claude.length
    ? homePeopleHtml(claude, esc, true)
    : '<p class="muted">아직 클로드 직원이 없어요. 아래 「만들기」를 눌러요.</p>';
  const makeHtml = `<div class="dept-make">
      <button type="button" class="btn" data-home="makedept">＋ 만들기</button>
      <div class="muted small">이 부서에 없는 클로드 직원을 만들어요. 폴더를 비우면 게임 폴더 옆에 자리를 만들어요.</div>
      <label class="dept-folder-label">폴더 주소 (직접 고를 때)
        <input id="homeDeptFolder" class="dept-folder" type="text" autocomplete="off" placeholder="예: D:\\일\\홍보" value="${esc(homeDeptFolder)}">
      </label>
      <div class="muted small">주소를 적으면 그 폴더 안에 직원마다 자리를 만들어요. 게임 폴더는 필요 없어요.</div>
    </div>`;
  const botHtml = bots.length ? homePeopleHtml(bots, esc, false) : '<p class="muted">아직 그록 봇 목록이 없어요.</p>';
  const game = d.id === 'game';
  const note = homeDeptNote && homeDeptNote.id === d.id ? homeDeptNote : null;
  const hint = lead
    ? `보내면 그록 팀장에게 가고, 클로드 팀장(${esc(lead.name)})에게도 같은 일이 들어가요.`
    : '보내면 그록 팀장에게 가요. 클로드 팀장이 있으면 그 사람에게도 넣어요.';
  el.innerHTML = `<div class="dept-page home-fit">
    <div class="dept-bar">
      <button type="button" class="btn ghost" data-home="back">← 회사 홈</button>
      <div class="dept-name"><span class="ico">${d.icon || '🏢'}</span><div><b>${esc(d.name)}</b><div class="muted small">${esc(d.sub || '')} · 클로드 ${claude.length}명 · 그록 ${bots.length}명</div></div></div>
      ${game ? '<button type="button" class="btn" data-home="workshop">🧠 클로드 작업장</button>' : ''}
    </div>
    <div class="dept-grid">
      <section class="card dept-card">
        <div class="dept-block"><b>🧠 클로드 직원</b> <span class="muted small">${claude.length}명</span>
          <div class="muted small">${game ? '게임 일을 직접 보려면 오른쪽 위 「클로드 작업장」을 눌러요.' : '이 부서의 클로드 팀이에요. 일을 보내면 팀장이 받아요.'}</div>
          ${claudeHtml}
          ${makeHtml}
        </div>
        <div class="dept-block"><b>🤖 그록 봇</b> <span class="muted small">${bots.length}명</span>
          ${botHtml}
        </div>
      </section>
      <form class="card dept-card dept-send" id="homeSend">
        <b>✍️ 이 부서에 일 시키기</b>
        <div class="muted small">${hint}<br>예: ${game ? '보스 그림 정리해서 보고해' : '오늘 할 일 정리해서 보고해'}</div>
        <textarea id="homeCmd" class="home-text" rows="4" placeholder="할 일을 적어 주세요"></textarea>
        <div id="homeSendErr" class="home-err${note && note.ok ? ' ok' : ''}">${note ? esc(note.text) : ''}</div>
        <button class="btn" type="submit">보내기</button>
      </form>
    </div>
  </div>`;
  const form = el.querySelector('#homeSend');
  if (form) form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const command = (el.querySelector('#homeCmd').value || '').trim();
    const err = el.querySelector('#homeSendErr');
    if (!command) { if (err) err.textContent = '할 일을 적어 주세요.'; return; }
    const r = await A.api('/api/bot/command', { target: d.name, command });
    let text = '';
    let ok = !!(r && r.ok);
    if (!ok) {
      text = (r && r.error) || '못 보냈어요';
      if (r && r.claudeLead && text.indexOf(r.claudeLead) < 0) text += ' 클로드 팀장 ' + r.claudeLead + '에게는 넣어 두었어요.';
    } else {
      text = d.name + '에 보냈어요.' + (r.claudeLead ? ' 클로드 ' + r.claudeLead + '에게도 넣었어요.' : '');
      A.toast(text);
      reportAt = 0;
    }
    homeDeptNote = { id: d.id, ok, text };
    if (homeMode === 'dept' && homeDeptId === d.id) homePaint(el, A);
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
    if (!t || !el.contains(t)) return;
    if (t.id === 'homeDeptFolder') { homeDeptFolder = t.value; return; }
    if (t.id !== 'homeTopCmd') return;
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
    else if (act === 'team') { homeMakeTeams(A); return; }
    else if (act === 'makedept') {
      const inp = el.querySelector('#homeDeptFolder');
      if (inp) homeDeptFolder = inp.value;
      homeMakeDept(A);
      return;
    }
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
