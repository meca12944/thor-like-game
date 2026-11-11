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
let homeDeptDraft = '';
let homeDeptWho = '';
let homeTalkDraft = '';
let homeGallery = false;
let homeEdit = null;
let homeAddOpen = false;
let homeAddName = '';
let homeAddRole = '';
let homeAPI = null;
let homeDeptFolder = '';
let homeComposing = false;
let homePaintWait = false;

const HOME_DEPTS = [
  { id: 'game', name: '게임 필멸자', sub: '게임 코드·그림·영상·음악', icon: '🎮', lead: '클로드' },
  { id: 'zero', name: '제로폰', sub: '사이트·정책·개통 안내', icon: '📱', lead: '제로폰 홈페이지' },
  { id: 'promo', name: '홍보', sub: '블로그·마케팅·영상', icon: '📣', lead: '제로폰 홍보 · 제로폰 관리' },
  { id: 'admin', name: '경영지원', sub: '해피콜·안내·생산·투자', icon: '💼', lead: '폰클매니저 미래 오케이' },
  { id: 'stco', name: 'STCO', sub: '온라인·오프라인', icon: '🛍', lead: 'STCO 인동점 SEO·홍보' },
  { id: 'video', name: '영상 기획팀', sub: '영상 기획·대본', icon: '🎬', lead: '영상 기획 팀장', grokLead: '영상 기획 팀장' },
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
function homeTexting(node) {
  if (!node || !node.tagName) return false;
  const tag = node.tagName;
  if (tag === 'TEXTAREA' || tag === 'SELECT') return true;
  if (tag === 'INPUT') {
    const t = String(node.type || 'text').toLowerCase();
    return t === 'text' || t === 'search' || t === 'password' || t === '';
  }
  return false;
}
function homeFieldBusy(el) {
  if (homeComposing) return true;
  const ae = document.activeElement;
  return !!(el && ae && el.contains(ae) && homeTexting(ae));
}
function homeSnap(el) {
  const cmd = el.querySelector('#homeTopCmd');
  const dept = el.querySelector('#homeTopDept');
  if (cmd) homeTopDraft = cmd.value;
  if (dept && dept.value) homeTopSave(dept.value);
  const cmd2 = el.querySelector('#homeCmd');
  const who = el.querySelector('#homeWho');
  const talk = el.querySelector('#homeTalk');
  const addName = el.querySelector('#zAddName');
  const addRole = el.querySelector('#zAddRole');
  if (cmd2) homeDeptDraft = cmd2.value;
  if (who) homeDeptWho = who.value;
  if (talk) homeTalkDraft = talk.value;
  if (addName) homeAddName = addName.value;
  if (addRole) homeAddRole = addRole.value;
  const folder = el.querySelector('#homeDeptFolder');
  if (folder) homeDeptFolder = folder.value;
  if (homeEdit) {
    const en = el.querySelector('#zEditName');
    const er = el.querySelector('#zEditRole');
    const nick = el.querySelector('#zEditNick');
    if (en) homeEdit.name = en.value;
    if (er) homeEdit.role = er.value;
    if (nick) homeEdit.nick = nick.value;
  }
  const ae = document.activeElement;
  const focusId = ae && el.contains(ae) && ae.id ? ae.id : '';
  const caret = ae && (ae.selectionStart || ae.selectionStart === 0) ? ae.selectionStart : null;
  return { focusId, caret };
}
function homeRestoreFocus(el, snap) {
  if (!snap || !snap.focusId) return;
  const node = el.querySelector('#' + (window.CSS && CSS.escape ? CSS.escape(snap.focusId) : snap.focusId));
  if (!node || typeof node.focus !== 'function') return;
  node.focus();
  if (snap.caret != null && node.setSelectionRange && typeof node.value === 'string') {
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
    const mark = claude ? '🧠' : '🤖';
    return `<li><span class="who-ico">${mark}</span> <b>${esc(p.name)}</b>${lead} — ${esc(p.role || '')}${job}</li>`;
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
  // 글 쓰는 중에는 입력칸을 다시 만들지 않아요. 보고 목록만 조용히 새로고침합니다.
  if (homeFieldBusy(el)) {
    homeSnap(el);
    homePaintWait = true;
    const slot = el.querySelector('#zDeptReports') || el.querySelector('#homeReports');
    if (slot && typeof renderReports === 'function') {
      const opt = slot.id === 'zDeptReports' ? { dept: homeCurrentDept(A).name, title: '📋 이 부서 보고' } : undefined;
      renderReports(slot, opt);
    }
    return;
  }
  homePaintWait = false;
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
function homeCurrentDept(A, pack) {
  const list = (pack || homeDepts(A)).depts || [];
  return list.find((x) => x.id === homeDeptId) || { id: homeDeptId, name: '부서', icon: '🏢', sub: '' };
}
function homeBotNick(A, name) {
  const map = (A && A.state && A.state.botNicks) || {};
  const nick = map && map[name];
  return nick ? String(nick) : name;
}
function homeStatusWord(e) {
  if (!e) return '';
  if (e.status === 'working') return '일하는 중';
  if (e.status === 'waiting') return '답 기다리는 중';
  if (e.status === 'error') return '문제';
  if (e.queue) return '일 기다리는 중';
  return '쉬는 중';
}
function homeArtCount(deptName) {
  const items = (typeof reportPack !== 'undefined' && reportPack && reportPack.items) || [];
  let n = 0;
  for (const r of items) if (typeof reportInDept === 'function' && reportInDept(r, deptName)) n += (r.artifacts || []).length;
  return n;
}
function homeGalleryInner(deptName, esc) {
  const items = (typeof reportPack !== 'undefined' && reportPack && reportPack.items) || [];
  const photos = [];
  const rest = [];
  for (const r of items) {
    if (typeof reportInDept === 'function' && !reportInDept(r, deptName)) continue;
    for (const a of r.artifacts || []) {
      if (!a) continue;
      const row = { a, id: r.id || '' };
      if (a.kind === 'photo' && (a.src || a.url)) photos.push(row);
      else rest.push(row);
    }
  }
  if (!photos.length && !rest.length) return '<div class="muted small">이 부서 결과물이 아직 없어요. 일이 끝나면 사진과 파일이 여기에 모입니다.</div>';
  const grid = photos.length ? `<div class="art-photos">${photos.map((row) => `<figure class="art-photo"><img src="${esc(row.a.src || row.a.url)}" alt="${esc(row.a.name || '사진')}"><figcaption>${esc(row.a.name || '사진')}</figcaption></figure>`).join('')}</div>` : '';
  const list = rest.map((row) => {
    const a = row.a;
    if (a.kind === 'photo') return `<div class="art-file">🖼 ${esc(a.name || '사진')}</div>`;
    if (a.kind === 'file') return `<button type="button" class="art-file" data-art-open="1" data-id="${esc(row.id)}" data-a="${esc(a.i)}">📄 ${esc(a.path || a.name || '파일')}</button>`;
    if (a.kind === 'link' && /^https?:\/\//i.test(String(a.url || ''))) return `<a class="art-link" href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">🔗 ${esc(a.name || '링크')}</a>`;
    if (a.kind === 'text' && a.text) return `<div class="art-text">📝 ${esc(a.text)}</div>`;
    return '';
  }).join('');
  return `${grid}<div class="art-files">${list}</div>`;
}
function homeAfterReports() {
  try {
    const el = document.getElementById('home');
    if (!el || homeMode !== 'dept' || !homeAPI) return;
    const d = homeCurrentDept(homeAPI);
    const n = el.querySelector('#zArtCount');
    if (n) n.textContent = String(homeArtCount(d.name));
    const g = el.querySelector('#zArtGallery');
    if (g && homeGallery) g.innerHTML = homeGalleryInner(d.name, homeAPI.esc);
  } catch (e) { /* 결과물 칸만 비워 두고 화면은 유지 */ }
}
function homeWhoHtml(A, claude, bots, esc) {
  const opts = [];
  const sorted = claude.slice().sort((a, b) => (b.lead === true) - (a.lead === true) || String(a.name).localeCompare(String(b.name), 'ko'));
  for (const e of sorted) opts.push({ v: 'emp:' + e.id, label: '👤 ' + e.name + (e.lead ? ' (팀장)' : ' (직원)') });
  for (const b of bots) {
    const nick = homeBotNick(A, b.name);
    const label = nick === b.name ? b.name : nick + ' · 원래 ' + b.name;
    opts.push({ v: 'bot:' + b.name, label: '🤖 ' + label });
  }
  const cur = opts.some((o) => o.v === homeDeptWho) ? homeDeptWho : (opts[0] ? opts[0].v : '');
  homeDeptWho = cur;
  if (!opts.length) return '<option value="">팀원이 없어요</option>';
  return opts.map((o) => `<option value="${esc(o.v)}"${o.v === cur ? ' selected' : ''}>${esc(o.label)}</option>`).join('');
}
function homeEmpRows(claude, esc) {
  if (!claude.length) {
    return '<p class="muted small">아직 클로드 직원이 없어요. 아래 「만들기」를 눌러요.</p>';
  }
  const sorted = claude.slice().sort((a, b) => (b.lead === true) - (a.lead === true) || String(a.name).localeCompare(String(b.name), 'ko'));
  return `<ul class="dept-people">${sorted.map((e) => {
    if (homeEdit && homeEdit.kind === 'emp' && homeEdit.id === e.id) {
      return `<li class="dept-edit"><b>이름 고치기</b>
        <input id="zEditName" value="${esc(homeEdit.name)}" placeholder="예: 안내담당" autocomplete="off">
        <input id="zEditRole" value="${esc(homeEdit.role || '')}" placeholder="맡은 일 (예: 고객 안내 글)" autocomplete="off">
        <div class="dept-edit-row"><button type="button" class="btn small" data-home="edit-save">저장</button><button type="button" class="btn ghost small" data-home="edit-cancel">취소</button></div>
        <div class="muted small">폴더와 하던 대화는 그대로예요.</div></li>`;
    }
    return `<li><div class="dept-row"><div><b>${esc(e.name)}</b>${e.lead ? ' <span class="muted small">(팀장)</span>' : ''} <span class="muted small">${esc(homeStatusWord(e))}</span><div class="muted small">${esc(e.role || '')}</div>${homeJobLine(e, esc)}</div><button type="button" class="btn ghost small" data-home="edit" data-id="${esc(e.id)}">수정</button></div></li>`;
  }).join('')}</ul>`;
}
function homeBotRows(A, bots, esc) {
  if (!bots.length) return '<p class="muted small">아직 그록 봇이 없어요.</p>';
  return `<ul class="dept-people">${bots.map((b) => {
    const nick = homeBotNick(A, b.name);
    if (homeEdit && homeEdit.kind === 'bot' && homeEdit.origin === b.name) {
      return `<li class="dept-edit"><b>화면에 보일 이름</b>
        <div class="muted small">일을 보낼 때는 원래 이름 「${esc(b.name)}」을 써요.</div>
        <input id="zEditNick" value="${esc(homeEdit.nick || '')}" placeholder="예: 폰팀" autocomplete="off">
        <div class="dept-edit-row"><button type="button" class="btn small" data-home="nick-save" data-name="${esc(b.name)}">저장</button><button type="button" class="btn ghost small" data-home="edit-cancel">취소</button></div></li>`;
    }
    const shown = nick === b.name ? esc(b.name) : esc(nick) + ' <span class="muted small">원래 ' + esc(b.name) + '</span>';
    return `<li><div class="dept-row"><div><b>${shown}</b>${b.lead ? ' <span class="muted small">(팀장)</span>' : ''}<div class="muted small">${esc(b.role || '')}</div></div><button type="button" class="btn ghost small" data-home="nick" data-name="${esc(b.name)}">별명</button></div></li>`;
  }).join('')}</ul>`;
}
function homeAddHtml(esc) {
  if (!homeAddOpen) return '<button type="button" class="btn ghost small" data-home="add">＋ 직원 추가</button>';
  return `<div class="dept-edit">
    <b>이 부서에 직원 추가</b>
    <input id="zAddName" value="${esc(homeAddName)}" placeholder="이름 (예: 안내담당)" autocomplete="off">
    <input id="zAddRole" value="${esc(homeAddRole)}" placeholder="맡은 일 (예: 고객 안내 글)" autocomplete="off">
    <div class="dept-edit-row"><button type="button" class="btn small" data-home="add-save">저장</button><button type="button" class="btn ghost small" data-home="add-cancel">취소</button></div>
    <div class="muted small">게임 폴더가 있어야 자리를 만들 수 있어요.</div>
  </div>`;
}
async function homeLoadTalk(el, A, d) {
  const names = homeClaudeList(A, d.id).map((e) => e.name);
  let coop = [];
  try {
    const data = await fetch('/api/coop/chat', { cache: 'no-store' }).then((r) => r.json());
    coop = ((data && data.items) || []).filter((c) => {
      const t = String(c && c.text || '');
      if (t.indexOf('[부서:' + d.name + ']') >= 0 || t.indexOf(d.name) >= 0) return true;
      return names.some((n) => n && t.indexOf(n) >= 0);
    }).slice(-6);
  } catch (e) { coop = []; }
  const local = ((A.state && A.state.reports) || []).filter((r) => names.indexOf(r.empName) >= 0).slice(0, 6);
  const esc = A.esc;
  const lines = [];
  for (const c of coop) {
    const who = c.who === 'grok' ? '그록' : c.who === 'claude' ? '클로드' : '사장님';
    lines.push(`<div class="dept-line"><b>${esc(who)}</b> <span class="muted small">${esc(String(c.text || '').replace(/\s+/g, ' ').slice(0, 160))}</span></div>`);
  }
  for (const r of local) {
    const text = String(r.text || r.task || '').split('\n').map((s) => s.trim()).filter(Boolean)[0] || '';
    lines.push(`<div class="dept-line"><b>${esc(r.empName || '직원')} 답</b> <span class="muted small">${esc(text.slice(0, 160))}</span></div>`);
  }
  const html = lines.length ? lines.join('') : '<div class="muted small">아직 이 부서 대화가 없어요. 아래에 적으면 고른 사람에게 가요.</div>';
  const box = el.querySelector('#zTalkList');
  if (!box || homeMode !== 'dept' || homeDeptId !== d.id) return;
  box.innerHTML = html;
}
async function homeDeptAssign(el, A, d, who, command) {
  const err = el.querySelector('#homeSendErr');
  const show = (ok, text) => {
    homeDeptNote = { id: d.id, ok, text };
    if (homeMode === 'dept' && homeDeptId === d.id) homePaint(el, A);
  };
  if (!who) return show(false, '받을 사람을 골라 주세요.');
  if (!command) return show(false, '할 일을 적어 주세요.');
  let r = null;
  try {
    if (who.indexOf('emp:') === 0) r = await A.api('/api/order', { to: who.slice(4), text: command, dept: d.name });
    else if (who.indexOf('bot:') === 0) r = await A.api('/api/bot/command', { target: who.slice(4), command, skipClaude: true });
    else r = { ok: false, error: '받을 사람을 골라 주세요.' };
  } catch (e) {
    r = { ok: false, error: '못 보냈어요. 회사 프로그램이 켜져 있는지 봐 주세요.' };
  }
  const ok = !!(r && r.ok);
  const text = ok ? '넣었어요. 바로 아래 보고에 접수로 떠요.' : ((r && r.error) || '못 보냈어요');
  if (ok) {
    homeDeptDraft = '';
    homeTalkDraft = '';
    const cmd = el.querySelector('#homeCmd');
    const talk = el.querySelector('#homeTalk');
    if (cmd) cmd.value = '';
    if (talk) talk.value = '';
    reportAt = 0;
    if (A.toast) A.toast(d.name + '에 넣었어요');
  }
  homeComposing = false;
  const typing = document.activeElement;
  if (typing && el.contains(typing) && homeTexting(typing)) typing.blur();
  show(ok, text);
}
function homePaintDept(el, A, pack, esc) {
  const d = homeCurrentDept(A, pack);
  const bots = (pack.bots || []).filter((b) => b.dept === d.id);
  const claude = homeClaudeList(A, d.id);
  const makeHtml = `<div class="dept-make">
      <button type="button" class="btn" data-home="makedept">＋ 만들기</button>
      <div class="muted small">이 부서에 없는 클로드 직원을 만들어요. 폴더를 비우면 게임 폴더 옆에 자리를 만들어요. 켤 때 저절로 만들지 않아요.</div>
      <label class="dept-folder-label">폴더 주소 (직접 고를 때)
        <input id="homeDeptFolder" class="dept-folder" type="text" autocomplete="off" placeholder="예: D:\\일\\홍보" value="${esc(homeDeptFolder)}">
      </label>
      <div class="muted small">주소를 적으면 그 폴더 안에 직원마다 자리를 만들어요.</div>
    </div>`;
  const note = homeDeptNote && homeDeptNote.id === d.id ? homeDeptNote : null;
  const example = d.id === 'game' ? '보스 그림 정리해서 보고해' : '오늘 할 일 정리해서 보고해';
  const galleryBtn = homeGallery ? '결과물 접기' : '결과물 모아 보기';
  el.innerHTML = `<div class="dept-page home-fit">
    <div class="dept-bar">
      <button type="button" class="btn ghost" data-home="back">← 회사 홈</button>
      <div class="dept-name"><span class="ico">${d.icon || '🏢'}</span><div><b>${esc(d.name)}</b><div class="muted small">${esc(d.sub || '')} · 클로드 ${claude.length}명 · 그록 ${bots.length}명</div></div></div>
      <button type="button" class="btn" data-home="gallery">🗂 ${galleryBtn} <span id="zArtCount">${homeArtCount(d.name)}</span></button>
    </div>
    ${homeGallery ? `<div class="art-gallery" id="zArtGallery">${homeGalleryInner(d.name, esc)}</div>` : '<div id="zArtGallery" hidden></div>'}
    <div class="dept-grid">
      <section class="card dept-col">
        <div class="dept-block"><b>👤 팀원 · 클로드</b> <span class="muted small">${claude.length}명</span>
          ${homeEmpRows(claude, esc)}
          ${makeHtml}
          ${homeAddHtml(esc)}
        </div>
        <div class="dept-block"><b>🤖 팀원 · 그록 봇</b> <span class="muted small">${bots.length}명</span>
          <div class="muted small">별명은 이 화면에서만 바뀝니다. 일을 보낼 때는 원래 이름을 써요.</div>
          ${homeBotRows(A, bots, esc)}
        </div>
        <div class="card dept-talk">
          <b>💬 이 부서 대화·답</b>
          <div class="muted small">이 부서 이야기와 직원 답을 여기 모아요.</div>
          <div id="zTalkList" class="dept-talk-list"><div class="muted small">불러오는 중…</div></div>
          <form id="homeTalkSend" class="dept-talk-send">
            <input id="homeTalk" type="text" autocomplete="off" placeholder="짧은 말 (예: 오늘 할 일만 먼저 해 줘)" value="${esc(homeTalkDraft)}">
            <button class="btn small" type="submit">보내기</button>
          </form>
        </div>
      </section>
      <section class="dept-col dept-work">
        <form class="card dept-send" id="homeSend">
          <b>✍️ 일 시키기</b>
          <div class="muted small">팀장이나 직원을 고르고 할 일을 적어요. 보내면 바로 접수로 보고에 떠요.</div>
          <label class="home-order-pick">받을 사람 <select id="homeWho">${homeWhoHtml(A, claude, bots, esc)}</select></label>
          <textarea id="homeCmd" class="home-text" rows="4" placeholder="예: ${esc(example)}">${esc(homeDeptDraft)}</textarea>
          <div id="homeSendErr" class="home-err${note && note.ok ? ' ok' : ''}">${note ? esc(note.text) : ''}</div>
          <button class="btn" type="submit">보내기</button>
        </form>
        <section class="dept-reports" id="zDeptReports"></section>
      </section>
    </div>
  </div>`;
  if (typeof renderReports === 'function') renderReports(el.querySelector('#zDeptReports'), { dept: d.name, title: '📋 이 부서 보고' });
  homeLoadTalk(el, A, d);
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
    if (!form || !el.contains(form)) return;
    if (form.id === 'homeTopSend') { ev.preventDefault(); homeTopSend(el, A); return; }
    if (form.id !== 'homeSend' && form.id !== 'homeTalkSend') return;
    ev.preventDefault();
    const d = homeCurrentDept(A);
    const who = (el.querySelector('#homeWho') || {}).value || homeDeptWho;
    if (form.id === 'homeTalkSend') {
      const talk = el.querySelector('#homeTalk');
      const command = talk ? String(talk.value || '').trim() : '';
      homeTalkDraft = command;
      homeDeptAssign(el, A, d, who, command);
      return;
    }
    const cmd = el.querySelector('#homeCmd');
    const command = cmd ? String(cmd.value || '').trim() : '';
    homeDeptDraft = command;
    homeDeptAssign(el, A, d, who, command);
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
  el.addEventListener('compositionstart', () => { homeComposing = true; });
  el.addEventListener('compositionend', () => { homeComposing = false; homeSnap(el); });
  el.addEventListener('focusout', () => {
    if (!homePaintWait) return;
    setTimeout(() => {
      if (!homePaintWait || homeFieldBusy(el)) return;
      homePaint(el, A);
    }, 0);
  });
  el.addEventListener('click', (ev) => {
    const art = ev.target.closest('[data-art-open]');
    if (art && el.contains(art)) {
      ev.preventDefault();
      fetch('/api/openFile', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ c: art.getAttribute('data-id') || '', a: Number(art.getAttribute('data-a')) }) }).catch(() => {});
      return;
    }
    const b = ev.target.closest('[data-home]');
    if (!b || !el.contains(b)) return;
    const act = b.getAttribute('data-home');
    if (act === 'back') { homeMode = 'home'; homeConn = -1; homeEdit = null; }
    else if (act === 'dept') { homeMode = 'dept'; homeDeptId = b.getAttribute('data-id') || ''; homeEdit = null; homeGallery = false; }
    else if (act === 'workshop') { if (A.openWorkshop) A.openWorkshop(); return; }
    else if (act === 'conn') { homeMode = 'conn'; homeConn = -1; }
    else if (act === 'connone') { homeMode = 'conn'; homeConn = Number(b.getAttribute('data-i')); }
    else if (act === 'team') { homeMakeTeams(A); return; }
    else if (act === 'gallery') { homeGallery = !homeGallery; }
    else if (act === 'edit') {
      const id = b.getAttribute('data-id') || '';
      const emp = homeClaudeList(A, homeDeptId).find((e) => e.id === id);
      if (emp) homeEdit = { kind: 'emp', id: emp.id, name: emp.name, role: emp.role || '' };
    } else if (act === 'edit-cancel' || act === 'add-cancel') { homeEdit = null; homeAddOpen = false; }
    else if (act === 'edit-save') { homeSaveEmp(el, A); return; }
    else if (act === 'nick') {
      const name = b.getAttribute('data-name') || '';
      homeEdit = { kind: 'bot', origin: name, nick: homeBotNick(A, name) === name ? '' : homeBotNick(A, name) };
    } else if (act === 'nick-save') { homeSaveNick(el, A, b.getAttribute('data-name') || ''); return; }
    else if (act === 'add') { homeAddOpen = true; }
    else if (act === 'add-save') { homeAddEmp(el, A); return; }
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
async function homeSaveEmp(el, A) {
  const d = homeCurrentDept(A);
  const name = String((el.querySelector('#zEditName') || {}).value || '').trim();
  const role = String((el.querySelector('#zEditRole') || {}).value || '').trim();
  const id = homeEdit && homeEdit.id;
  let r = null;
  try { r = await A.api('/api/employee', { id, rename: true, name, role }); }
  catch (e) { r = { ok: false, error: '저장하지 못했어요.' }; }
  if (!r || !r.ok) homeDeptNote = { id: d.id, ok: false, text: (r && r.error) || '이름을 못 고쳤어요.' };
  else {
    homeEdit = null;
    homeDeptNote = { id: d.id, ok: true, text: '이름을 ' + r.name + '으로 고쳤어요.' };
    if (A.toast) A.toast('이름을 고쳤어요');
  }
  if (homeMode === 'dept') homePaint(el, A);
}
async function homeSaveNick(el, A, origin) {
  const d = homeCurrentDept(A);
  const nick = String((el.querySelector('#zEditNick') || {}).value || '').trim();
  const name = origin || (homeEdit && homeEdit.origin) || '';
  let r = null;
  try { r = await A.api('/api/bot/nick', { name, nick }); }
  catch (e) { r = { ok: false, error: '별명을 못 고쳤어요.' }; }
  if (!r || !r.ok) homeDeptNote = { id: d.id, ok: false, text: (r && r.error) || '별명을 못 고쳤어요.' };
  else {
    homeEdit = null;
    homeDeptNote = { id: d.id, ok: true, text: nick ? '화면 이름을 ' + nick + '으로 바꿨어요. 보낼 때는 원래 이름을 써요.' : '원래 이름으로 돌려놨어요.' };
  }
  if (homeMode === 'dept') homePaint(el, A);
}
async function homeAddEmp(el, A) {
  const d = homeCurrentDept(A);
  const name = String((el.querySelector('#zAddName') || {}).value || '').trim();
  const role = String((el.querySelector('#zAddRole') || {}).value || '').trim();
  if (!name) {
    homeDeptNote = { id: d.id, ok: false, text: '이름을 적어 주세요.' };
    homePaint(el, A);
    return;
  }
  let r = null;
  try { r = await A.api('/api/employee', { name, role, dept: d.id, autoFolder: true }); }
  catch (e) { r = { ok: false, error: '직원을 못 만들었어요.' }; }
  if (!r || !r.ok) homeDeptNote = { id: d.id, ok: false, text: (r && r.error) || '직원을 못 만들었어요.' };
  else {
    homeAddOpen = false;
    homeAddName = '';
    homeAddRole = '';
    homeDeptNote = { id: d.id, ok: true, text: name + ' 직원을 이 부서에 넣었어요.' };
    if (A.toast) A.toast(name + ' 직원을 넣었어요');
  }
  if (homeMode === 'dept') homePaint(el, A);
}
window.AldeulHome = {
  render(el, A) {
    if (!el || !A) return;
    homeAPI = A;
    homeBind(el, A);
    homePaint(el, A);
  },
};
// 상태 알림이 이 파일보다 먼저 와도, 홈을 한 번 그려요.
if (window.Aldeul && document.getElementById('home') && window.Aldeul.view === 'home') {
  window.AldeulHome.render(document.getElementById('home'), window.Aldeul);
}
