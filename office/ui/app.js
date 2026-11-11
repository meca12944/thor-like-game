// 클로드 회사 — 화면 (단순판, 사장님 11-11 「ui를 단순하고 쉽게」)
'use strict';
let S = { employees: [], reports: [], pending: [], rules: [], settings: {}, claude: {}, grokLog: [] };
let tab = 'report', target = '', roomMode = 'grok', allEmp = '';
const openTasks = new Set();
const uploads = []; // 그록 답에 붙일 그림·영상
const BOARD = 'https://raw.githubusercontent.com/meca12944/thor-like-game/main/handoff/GROK_BRIEFING_ko.md';
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const api = (p, body) => fetch(p, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body || {}) }).then((r) => r.json());
const COLORS = ['#c8643b', '#2f6fde', '#1f9d55', '#8b5cf6', '#d13b7a', '#0e8f8f', '#b7791f', '#5b6b8a'];
const colorOf = (s) => { let h = 0; for (const c of String(s)) h = (h * 31 + c.charCodeAt(0)) >>> 0; return COLORS[h % COLORS.length]; };
const avatar = (name) => `<span class="avatar" style="background:${colorOf(name)}">${esc(String(name).slice(0, 1))}</span>`;
const STATUS = { idle: '쉬는 중', working: '일하는 중', waiting: '기다리는 중', error: '문제 있음' };
const MODES = { '': '회사 기본값', auto: '알아서 (애매한 것만 물어봄) — 추천', acceptEdits: '파일 고치기만 자동', all: '전부 허락 (아무것도 안 물어봄)' };
const partner = () => S.employees.find((e) => e.partner);
const isBoss = (r) => r.toBoss !== false || r.needBoss || r.isError;
function toast(t) { const el = $('#toast'); el.textContent = t; el.hidden = false; clearTimeout(el._t); el._t = setTimeout(() => (el.hidden = true), 2200); }
async function copy(t, msg) { try { await navigator.clipboard.writeText(t); toast(msg || '복사했어요'); } catch (e) { prompt('아래 글을 복사하세요 (Ctrl+C)', t); } }
function ago(t) {
  const s = (Date.now() - new Date(t)) / 1000;
  if (s < 60) return '방금'; if (s < 3600) return Math.floor(s / 60) + '분 전'; if (s < 86400) return Math.floor(s / 3600) + '시간 전';
  return new Date(t).toLocaleString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function md(t) {
  let h = esc(t);
  h = h.replace(/```[\w-]*\n?([\s\S]*?)```/g, (m, c) => `<code style="display:block;white-space:pre-wrap">${c}</code>`);
  h = h.replace(/^#{1,4}\s+(.+)$/gm, '<h4>$1</h4>').replace(/\n?(<h4>)/g, '$1').replace(/(<\/h4>)\n/g, '$1');
  h = h.replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>').replace(/`([^`\n]+)`/g, '<code>$1</code>');
  return h;
}
const mediaHtml = (files, url) => files.length ? `<div class="media">${files.map((f) => f.kind === 'video'
  ? `<figure><video src="${url(f)}" controls preload="metadata" playsinline></video><figcaption>${esc(f.name)}</figcaption></figure>`
  : `<figure><img src="${url(f)}" loading="lazy" data-act="zoom"><figcaption>${esc(f.name)}</figcaption></figure>`).join('')}</div>` : '';

// ───────── 그리기 ─────────
function render() {
  if (!target || !S.employees.some((e) => e.id === target)) target = (S.employees.find((e) => e.name === '팀장') || S.employees[0] || {}).id || '';
  const E = S.employees, working = E.filter((e) => e.status === 'working').length;
  $('#summary').innerHTML = E.length ? `직원 ${E.length}명 · <b>${working ? working + '명 일하는 중' : '모두 쉬는 중'}</b>` : '';
  renderAsks(); renderEmps(); renderFeed(); renderRelay(); renderSay();
  $('#cReport').textContent = S.reports.filter((r) => isBoss(r) && !r.read).length || '';
  const seen = Number(localStorage.getItem('grokSeen') || 0);
  $('#cGrok').textContent = tab === 'grok' ? '' : (S.grokLog.filter((g) => new Date(g.time) > seen).length || '');
  const n = S.pending.length + relays().length + S.reports.filter((r) => isBoss(r) && !r.read).length;
  document.title = (n ? `(${n}) ` : '') + '클로드 회사';
}
function renderAsks() {
  let h = '';
  if (!S.claude.ok) h += `<div class="banner-red"><b>클로드 코드를 못 찾았어요.</b> 폴더 안 「처음_설치.bat」 을 두 번 누르고, 로그인한 뒤 다시 켜 주세요.</div>`;
  for (const p of S.pending) h += `<div class="ask"><div class="q"><b>🙋 ${esc(p.empName)}: 「${esc(p.label)}」 해도 될까요?</b><code>${esc(p.detail)}</code><div class="note">한 번 허락하면 다음부터 다시 안 물어요.</div></div>
    <button class="btn green" data-ans="always" data-id="${p.id}">허락</button><button class="btn red" data-ans="no" data-id="${p.id}">거절</button></div>`;
  $('#asks').innerHTML = h;
}
function renderEmps() {
  if (!S.employees.length) { $('#emps').innerHTML = `<div class="empty">아직 직원이 없어요.<br><br><button class="btn" data-act="team">기본 팀 만들기 (7명)</button><br><br><button class="link" data-act="hire">한 명씩 뽑기</button></div>`; return; }
  $('#emps').innerHTML = S.employees.map((e) => `
    <div class="emp ${e.id === target ? 'sel' : ''}" data-act="pick" data-id="${e.id}">
      ${avatar(e.name)}
      <div class="who"><div class="name">${esc(e.name)}${e.partner ? '<span class="badge">그록</span>' : ''} <span class="st ${e.status}">${STATUS[e.status] || ''}</span></div>
        <div class="now">${esc(e.now || e.role)}${e.queue ? ` · 대기 ${e.queue}` : ''}</div></div>
      <button class="more" data-act="menu" data-id="${e.id}" title="더 보기">⋯</button>
    </div>`).join('');
}
function cardHtml(r) {
  const long = r.text.length > 900;
  return `<article class="card ${r.read ? '' : 'new'} ${r.needBoss ? 'boss' : ''} ${r.isError ? 'err' : ''}">
    <div class="card-head">${avatar(r.empName)}<b>${esc(r.empName)}</b><span class="muted small">${r.from === '사장님' ? '' : '← ' + esc(r.from)}${r.stopped ? ' · 멈춤' : ''}</span><time>${ago(r.time)}</time></div>
    <div class="card-task ${openTasks.has(r.id) ? 'open' : ''}" data-act="task" data-id="${r.id}">📋 ${esc(r.task)}</div>
    ${r.asks.length ? `<div class="need">🙋 <b>사장님 확인이 필요해요</b><br>${r.asks.map(esc).join('<br>')}</div>` : ''}
    <div class="text ${long ? 'clamp' : ''}">${md(r.text)}</div>
    ${long ? `<button class="link" data-act="moretext">더 보기</button>` : ''}
    ${mediaHtml(r.files, (f) => `/file?r=${r.id}&i=${f.i}`)}
    <div class="card-foot">
      ${r.forwards.length ? `<span>📨 ${r.forwards.map(esc).join(', ')}에게 넘김</span>` : ''}
      ${r.denials.length ? `<span style="color:var(--red)">⛔ 거절된 일: ${r.denials.map(esc).join(', ')}</span>` : ''}
      <span class="sp"></span>
      ${/```/.test(r.text) ? `<button class="link" data-act="copycode" data-id="${r.id}">붙여넣기 글 복사</button>` : ''}
      <button class="link" data-act="copy" data-id="${r.id}">복사</button>
      <button class="link" data-act="reply" data-id="${r.id}">답하기</button>
    </div></article>`;
}
function renderFeed() {
  const box = $('#feed');
  if ([...box.querySelectorAll('video')].some((v) => !v.paused)) { box.dataset.dirty = '1'; return; }
  box.dataset.dirty = '';
  if (tab === 'grok') return renderChat(box);
  let list = S.reports;
  let head = '';
  if (tab === 'report') list = list.filter(isBoss);
  else {
    if (allEmp) list = list.filter((r) => r.emp === allEmp);
    head = `<div><select id="allEmp" class="btn ghost small"><option value="">모든 직원</option>${S.employees.map((e) => `<option value="${e.id}" ${e.id === allEmp ? 'selected' : ''}>${esc(e.name)}</option>`).join('')}</select> <span class="muted small">직원끼리 주고받은 것까지 모두</span></div>`;
  }
  box.innerHTML = head + (list.length ? list.map(cardHtml).join('') : `<div class="empty">${tab === 'report' ? '아직 보고가 없어요.<br>아래에 할 일을 적어 보내 보세요.' : '기록이 없어요.'}</div>`);
  if (tab === 'report' && document.hasFocus()) {
    clearTimeout(renderFeed._r);
    renderFeed._r = setTimeout(() => { if (tab === 'report' && list.some((r) => !r.read)) api('/api/report/read', { all: true }); }, 4000);
  }
}
function renderChat(box) {
  try { localStorage.setItem('grokSeen', String(Date.now())); } catch (e) { /* */ }
  const how = S.settings.grokPaste ? '반자동: 그록에게 가는 말은 아래 노란 칸에서 복사해 그록 앱에 붙여 넣고, 그록 답을 붙여 넣어 주세요.' : '그록 키로 바로 연결돼 있어요.';
  if (!S.grokLog.length) { box.innerHTML = `<div class="empty">그록 대화방이에요. 사장님 · 그록 · 클로드가 함께 이야기해요.<br>${how}</div>`; return; }
  const stick = box.scrollTop + box.clientHeight > box.scrollHeight - 60;
  box.innerHTML = `<div class="chat">${S.grokLog.map((g) => {
    const cls = g.kind === 'boss' ? 'boss' : g.kind === 'sys' ? 'sys' : (g.kind === 'claude' || g.kind === 'ask') ? 'claude' : 'grok';
    const who = cls === 'boss' ? '사장님' : cls === 'sys' ? '' : cls === 'claude' ? esc(g.empName) + ' (클로드)' : '그록';
    const wait = g.relay && g.relay.state === 'waiting' ? '<span class="wait">⏳ 그록에게 옮겨 주기를 기다려요 (아래 노란 칸)</span>' : '';
    return `<div class="bubble ${cls}" data-gid="${g.id}">${who ? `<div class="who">${who} · ${ago(g.time)}</div>` : ''}<span class="gtext ${g.streaming ? 'typing' : ''}">${md(g.text)}</span>${mediaHtml(g.files, (f) => `/grokfile?g=${g.id}&i=${f.i}`)}${wait}</div>`;
  }).join('')}</div>`;
  if (stick || !box._once || box._count !== S.grokLog.length) { box.scrollTop = box.scrollHeight; box._once = true; box._count = S.grokLog.length; }
}
const relays = () => S.grokLog.filter((g) => g.relay && g.relay.state === 'waiting');
function renderRelay() {
  const box = $('#relayBox'); const list = relays();
  if (!list.length) { box.hidden = true; box.dataset.id = ''; return; }
  const r = list[0];
  if (tab !== 'grok') { // 다른 칸에서는 한 줄로만 알림
    box.hidden = false; box.dataset.id = ''; box.className = 'relay slim';
    box.innerHTML = `💬 <b>${esc(r.empName)}</b>이(가) 그록에게 할 말이 있어요${list.length > 1 ? ` (${list.length}개)` : ''}<span style="flex:1"></span><button class="btn small" data-act="gogrok">그록 대화방에서 옮겨 주기</button>`;
    return;
  }
  if (box.dataset.id === r.id && !box.hidden) return; // 쓰는 중이면 다시 안 그림
  box.hidden = false; box.dataset.id = r.id; box.className = 'relay'; uploads.length = 0;
  box.innerHTML = `<div class="step"><span class="num">1</span><b>${esc(r.empName)}</b>이(가) 그록에게 할 말이 있어요${list.length > 1 ? ` (남은 것 ${list.length}개)` : ''}
      <button class="btn small" data-act="relaycopy" data-id="${r.id}">📋 그록에 붙일 글 복사</button>
      ${r.files.length ? `<span class="files">같이 줄 그림: ${r.files.map((f) => esc(f.name)).join(', ')}</span>` : ''}</div>
    <div class="step"><span class="num">2</span>그록 앱에 붙여 넣고, 그록 답을 복사해서 아래에 붙여 넣어 주세요. 그림·영상은 Ctrl+V 나 끌어다 놓기.</div>
    <textarea id="relayText" rows="2" placeholder="그록 답 붙여 넣기"></textarea>
    <div class="step" style="margin:8px 0 0"><span class="files" id="relayFiles"></span><span style="flex:1"></span><button class="btn green" data-act="relaysend" data-id="${r.id}">그록 답 넣기</button></div>`;
}
function renderSay() {
  const to = $('#sayTo'), ta = $('#sayText');
  if (tab === 'grok') {
    const p = partner();
    const chips = [['grok', '그록에게'], ['claude', (p ? p.name : 'AI협력팀') + '에게'], ['meeting', '둘이 회의'], ['image', '🎨 그림 부탁']];
    to.innerHTML = chips.map(([k, v]) => `<button type="button" data-room="${k}" class="${roomMode === k ? 'on' : ''}">${v}</button>`).join('') + '<span style="flex:1"></span><button type="button" class="link" data-act="roomreset">새 대화</button>';
    ta.placeholder = { grok: '그록에게 할 말', claude: '클로드에게 할 말 — 필요하면 클로드가 그록에게도 물어봐요', meeting: '회의 주제 — 클로드와 그록이 주고받고 결론을 보고해요', image: '그록에게 부탁할 그림' }[roomMode] + ' (Enter 보내기)';
  } else {
    const e = S.employees.find((x) => x.id === target);
    to.innerHTML = e ? `받는 사람: <b>${esc(e.name)}</b> <span class="muted small">(왼쪽에서 바꾸기)</span><span style="flex:1"></span>${S.employees.length > 1 ? `<button type="button" data-act="toall" class="${target === 'all' ? 'on' : ''}">모두에게</button>` : ''}` : '먼저 직원을 뽑아 주세요.';
    ta.placeholder = '할 일을 적어 주세요 (Enter 보내기, Shift+Enter 줄바꿈)';
  }
}

// ───────── 창 ─────────
function dialog(html, onSubmit) {
  const d = $('#dlg'), f = $('#dlgForm');
  f.innerHTML = html;
  f.onsubmit = async (ev) => {
    const btn = ev.submitter;
    if (!btn || btn.value === 'cancel') return;
    ev.preventDefault();
    const fd = Object.fromEntries(new FormData(f).entries());
    const err = onSubmit ? await onSubmit(fd, btn.value) : null;
    if (err) { const el = $('.err-text', f); if (el) el.textContent = err; return; }
    if (err !== '') d.close();
  };
  d.showModal();
}
function hire(emp) {
  const e = emp || {}, hasRepo = !!S.settings.gameRepo;
  dialog(`<h2>${emp ? '직원 고치기' : '직원 뽑기'}</h2>
    <div class="field"><label>이름</label><input type="text" name="name" value="${esc(e.name || '')}" placeholder="예) 사운드"></div>
    <div class="field"><label>맡은 일</label><input type="text" name="role" value="${esc(e.role || '')}" placeholder="예) 배경음악·효과음"><div class="help">다른 직원들이 이걸 보고 일을 넘겨요.</div></div>
    ${emp ? '' : `<div class="field"><label class="check"><input type="checkbox" name="auto" ${hasRepo ? 'checked' : 'disabled'}> 일하는 자리를 자동으로 만들기 (추천)</label>${hasRepo ? '' : '<div class="help">설정에서 「게임 폴더」를 먼저 정하면 쓸 수 있어요.</div>'}</div>`}
    <div class="field"><label class="check"><input type="checkbox" name="partner" ${e.partner ? 'checked' : ''}> AI협력팀 (그록과 일하는 직원)</label></div>
    <details class="more-set"><summary>더 보기</summary>
      <div class="field"><label>일하는 폴더 (직접 적을 때)</label><input type="text" name="folder" value="${esc(e.folder || '')}"></div>
      <div class="field"><label>허락 방식</label><select name="mode">${Object.entries(MODES).map(([k, v]) => `<option value="${k}" ${k === (e.mode || '') ? 'selected' : ''}>${v}</option>`).join('')}</select></div>
      <div class="field"><label>모델 (비워 두면 기본)</label><input type="text" name="model" value="${esc(e.model || '')}" placeholder="예) sonnet"></div>
    </details>
    <div class="err-text"></div>
    <div class="dlg-foot">${emp ? '<button class="btn red" value="delete" style="margin-right:auto">내보내기</button>' : ''}<button class="btn ghost" value="cancel">닫기</button><button class="btn" value="ok">${emp ? '저장' : '뽑기'}</button></div>`,
  async (fd, v) => {
    if (v === 'delete') { if (!confirm(`${e.name} 직원을 내보낼까요? (파일은 그대로 남아요)`)) return ''; await api('/api/employee/delete', { id: e.id }); return; }
    const auto = !emp && fd.auto && !fd.folder;
    const r = await api('/api/employee', { id: e.id, name: fd.name, role: fd.role, folder: auto ? '' : (fd.folder || e.folder || ''), autoFolder: !!auto, mode: fd.mode || '', model: fd.model || '', partner: !!fd.partner });
    if (r.ok && r.id) target = r.id;
    return r.ok ? null : r.error;
  });
}
function empMenu(id) {
  const e = S.employees.find((x) => x.id === id); if (!e) return;
  dialog(`<h2>${avatar(e.name)} ${esc(e.name)}</h2><p class="muted">${esc(e.role)}</p>
    <div class="menu">
      <button class="btn ghost" value="log">👀 지금 하는 일 자세히 보기</button>
      ${e.status === 'working' || e.status === 'waiting' ? '<button class="btn ghost" value="stop">✋ 하던 일 멈추기</button>' : ''}
      ${e.queue ? `<button class="btn ghost" value="clear">🧹 기다리는 일 ${e.queue}개 비우기</button>` : ''}
      <button class="btn ghost" value="new">🔄 새 대화로 시작 (대화가 너무 길어 느릴 때)</button>
      <button class="btn ghost" value="open">📁 일하는 폴더 열기</button>
      <button class="btn ghost" value="edit">✏ 고치기 · 내보내기</button>
    </div><div class="dlg-foot"><button class="btn ghost" value="cancel">닫기</button></div>`,
  async (fd, v) => {
    if (v === 'log') { setTimeout(() => showLog(id), 30); return; }
    if (v === 'edit') { setTimeout(() => hire(e), 30); return; }
    if (v === 'stop') await api('/api/stop', { id });
    if (v === 'clear') await api('/api/stop', { id, clear: true });
    if (v === 'new') await api('/api/newChat', { id });
    if (v === 'open') await api('/api/open', { id });
  });
}
function settings() {
  const s = S.settings;
  dialog(`<h2>설정</h2>
    <div class="field"><label>게임 폴더</label><input type="text" name="gameRepo" value="${esc(s.gameRepo)}" placeholder="예) C:\\Users\\이름\\thor-like-game"><div class="help">새 직원의 일하는 자리를 여기서 만들어요.</div></div>
    <div class="field"><label>그록 연결</label>
      <label class="check"><input type="radio" name="grokMode" value="paste" ${s.grokMode !== 'api' ? 'checked' : ''}> 반자동 붙여넣기 — 공짜 (추천)</label>
      <label class="check"><input type="radio" name="grokMode" value="api" ${s.grokMode === 'api' ? 'checked' : ''}> 그록 키 — 자동, 쓴 만큼 돈 (말 한 번 약 30원)</label>
      <input type="password" name="xaiKey" placeholder="${s.hasXaiKey ? '그록 키 들어 있음 (바꿀 때만 넣기)' : '그록 키 (xai-…) — 키 방식일 때만'}" autocomplete="off" style="margin-top:6px"></div>
    <h3>바로 하기</h3>
    <div class="row-btns">
      <button class="btn ghost" value="board">📋 업무판 주소 복사 (그록에 붙이기)</button>
      <button class="btn ghost" value="folder">📁 그록 폴더 확인</button>
      <button class="btn ghost" value="rules">✅ 허락 목록</button>
      <button class="btn red" value="stopall">✋ 모두 멈춤</button>
    </div>
    <details class="more-set"><summary>더 보기</summary>
      <div class="field"><label>그록 폴더 (PC 의 구글 드라이브 폴더)</label><input type="text" name="grokDir" value="${esc(s.grokDir)}"><div class="help">새 파일이 오면 AI협력팀이 저절로 확인해요.</div></div>
      <div class="field"><label>기본 허락 방식</label><select name="defaultMode">${Object.entries(MODES).filter(([k]) => k).map(([k, v]) => `<option value="${k}" ${k === s.defaultMode ? 'selected' : ''}>${v}</option>`).join('')}</select></div>
      <div class="field"><label>그록 키 하루 한도 (달러)</label><input type="text" name="grokBudget" value="${esc(s.grokBudget)}"><div class="help">오늘 쓴 돈 $${(s.grokSpent || 0).toFixed(2)}</div></div>
      <div class="field"><label>직원 작업 공간 위치</label><input type="text" name="workspace" value="${esc(s.workspace)}"></div>
      <div class="field"><label>직원끼리 말이 오가는 최대 횟수</label><input type="text" name="maxHops" value="${esc(s.maxHops)}"></div>
      <div class="field"><label>클로드 코드 명령</label><input type="text" name="claudeCmd" value="${esc(s.claudeCmd)}"><div class="help">${S.claude.ok ? '찾음 ' + esc(S.claude.version) : '못 찾음'}</div></div>
    </details>
    <div class="err-text"></div>
    <div class="dlg-foot"><button class="btn ghost" value="quit" style="margin-right:auto">회사 끄기</button><button class="btn ghost" value="cancel">닫기</button><button class="btn" value="ok">저장</button></div>`,
  async (fd, v) => {
    if (v === 'board') { copy('우리 팀 업무 공유판이야. 일하기 전에 꼭 읽고, 여기 적힌 결정과 규칙을 따라 줘: ' + BOARD, '복사했어요. 그록에 붙여 넣으세요'); return ''; }
    if (v === 'folder') { const r = await api('/api/grokCheck'); if (!r.ok) return r.error; toast('AI협력팀이 그록 폴더를 확인해요'); return; }
    if (v === 'rules') { setTimeout(rules, 30); return; }
    if (v === 'stopall') { if (confirm('모든 직원의 일을 멈출까요?')) await api('/api/stopAll'); return; }
    if (v === 'quit') { if (confirm('클로드 회사를 끌까요? 일하던 직원도 멈춰요.')) { await api('/api/quit'); document.body.innerHTML = '<div class="empty">회사 문을 닫았어요. 이 창을 닫아도 돼요.</div>'; } return; }
    const r = await api('/api/settings', fd); return r.ok ? null : r.error;
  });
}
function rules() {
  const draw = () => `<h2>허락 목록</h2><p class="muted small">여기 있는 일은 모든 직원이 묻지 않고 해요. ✕ 를 누르면 다시 물어봐요.</p>
    <div class="rules">${S.rules.map((r, i) => `<span>${esc(r)} <button value="del:${i}" title="빼기">✕</button></span>`).join('')}</div>
    <div class="field" style="margin-top:12px"><label>직접 더하기</label><input type="text" name="add" placeholder="예) Bash(python3:*)"></div>
    <div class="dlg-foot"><button class="btn ghost" value="cancel">닫기</button><button class="btn" value="add">더하기</button></div>`;
  dialog(draw(), async (fd, v) => {
    const list = S.rules.slice();
    if (v.startsWith('del:')) list.splice(Number(v.slice(4)), 1); else if (fd.add && fd.add.trim()) list.push(fd.add.trim());
    await api('/api/rules', { rules: list }); S.rules = list; $('#dlgForm').innerHTML = draw(); return '';
  });
}
async function showLog(id) {
  const e = S.employees.find((x) => x.id === id); if (!e) return;
  const lines = await fetch('/api/log?id=' + id).then((r) => r.json());
  const K = { order: '▶ 일 받음', tool: '·', say: '💬', done: '✅ 보고', sys: '⚙' };
  const fmt = (l) => `<div class="k-${l.kind}">${new Date(l.t).toLocaleTimeString('ko-KR')} ${K[l.kind] || ''} ${esc(l.text)}</div>`;
  dialog(`<h2>${esc(e.name)} — 지금 하는 일</h2><div class="log" id="logBox">${lines.map(fmt).join('') || '<span class="muted">아직 기록이 없어요.</span>'}</div><div class="dlg-foot"><button class="btn ghost" value="cancel">닫기</button></div>`);
  const box = $('#logBox'); box.scrollTop = box.scrollHeight; box.dataset.emp = id; box._fmt = fmt;
}

// ───────── 알림 ─────────
let audio;
function ding() { try { audio = audio || new AudioContext(); const o = audio.createOscillator(), g = audio.createGain(); o.frequency.value = 880; g.gain.setValueAtTime(0.15, audio.currentTime); g.gain.exponentialRampToValueAtTime(0.001, audio.currentTime + 0.35); o.connect(g).connect(audio.destination); o.start(); o.stop(audio.currentTime + 0.35); } catch (e) { /* */ } }
function notify(title, body) { ding(); if (!document.hasFocus() && 'Notification' in window && Notification.permission === 'granted') new Notification(title, { body, icon: '/ui/icon.png' }); }

// ───────── 누르기 ─────────
document.addEventListener('click', async (ev) => {
  const t = ev.target.closest('[data-act],[data-ans],[data-room]'); if (!t) return;
  if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission();
  if (t.dataset.ans) return api('/api/perm/answer', { id: t.dataset.id, answer: t.dataset.ans });
  if (t.dataset.room) { roomMode = t.dataset.room; renderSay(); $('#sayText').focus(); return; }
  const id = t.dataset.id, a = t.dataset.act;
  if (a === 'pick') { target = id; if (tab === 'grok') setTab('report'); renderEmps(); renderSay(); $('#sayText').focus(); }
  if (a === 'menu') { ev.stopPropagation(); empMenu(id); }
  if (a === 'team') { if (!S.settings.gameRepo) { toast('설정에서 「게임 폴더」를 먼저 정해 주세요'); return settings(); } $('#emps').innerHTML = '<div class="empty">직원 자리를 만드는 중… (1~2분)</div>'; const r = await api('/api/team'); if (!r.ok) alert(r.error); }
  if (a === 'hire') hire();
  if (a === 'gogrok') setTab('grok');
  if (a === 'toall') { target = 'all'; renderSay(); }
  if (a === 'task') { openTasks.has(id) ? openTasks.delete(id) : openTasks.add(id); t.classList.toggle('open'); }
  if (a === 'moretext') { t.previousElementSibling.classList.remove('clamp'); t.remove(); }
  if (a === 'zoom') { const z = document.createElement('div'); z.className = 'zoom'; z.innerHTML = `<img src="${t.src}">`; z.onclick = () => z.remove(); document.body.append(z); }
  if (a === 'copy' || a === 'copycode') {
    const r = S.reports.find((x) => x.id === id); if (!r) return;
    const m = r.text.match(/```[\w-]*\n?([\s\S]*?)```/);
    copy(a === 'copycode' && m ? m[1].trim() : r.text);
  }
  if (a === 'reply') { const r = S.reports.find((x) => x.id === id); if (!r) return; target = r.emp; setTab('report'); $('#sayText').focus(); }
  if (a === 'roomreset') { if (confirm('새 대화를 시작할까요? (그록 앱에서도 새 대화를 열어 주세요)')) api('/api/room/reset'); }
  if (a === 'relaycopy') { const g = S.grokLog.find((x) => x.id === id); if (g) copy(g.relay.paste, '복사했어요. 그록 앱에 붙여 넣으세요'); }
  if (a === 'relaysend') {
    const text = $('#relayText').value.trim();
    if (!text && !uploads.length) return toast('그록 답을 붙여 넣어 주세요');
    t.disabled = true; t.textContent = '넣는 중…';
    const r = await api('/api/room/answer', { id, text, uploads: uploads.slice() });
    if (!r.ok) { t.disabled = false; t.textContent = '그록 답 넣기'; return alert(r.error); }
    $('#relayBox').dataset.id = ''; uploads.length = 0; toast('그록 답을 넣었어요');
  }
});
function setTab(t) { tab = t; $('#relayBox').dataset.id = ''; $('#tabs').querySelectorAll('button').forEach((x) => x.classList.toggle('on', x.dataset.t === t)); $('#feed')._once = false; $('#feed')._count = -1; render(); if (t !== 'grok') $('#feed').scrollTop = 0; }
$('#tabs').addEventListener('click', (ev) => { const b = ev.target.closest('button'); if (b) setTab(b.dataset.t); });
document.addEventListener('change', (ev) => { if (ev.target.id === 'allEmp') { allEmp = ev.target.value; renderFeed(); } });
$('#say').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const text = $('#sayText').value.trim(); if (!text) return;
  let r;
  if (tab === 'grok') {
    const mode = { grok: 'chat', claude: 'claude', meeting: 'meeting', image: 'image' }[roomMode];
    r = await api('/api/room/send', { mode, text });
    if (r.ok && r.paste) copy(r.paste, '그록에 붙일 글을 복사했어요. 그록 앱에 붙여 넣으세요');
  } else {
    if (!target) return toast('먼저 직원을 뽑아 주세요');
    r = await api('/api/order', { to: target, text });
    if (r.ok) toast('보냈어요');
  }
  if (!r.ok) return alert(r.error || '못 보냈어요');
  $('#sayText').value = '';
});
$('#sayText').addEventListener('keydown', (ev) => { if (ev.key === 'Enter' && !ev.shiftKey && !ev.isComposing) { ev.preventDefault(); $('#say').requestSubmit(); } });
// 그록 답에 그림·영상 붙이기 (Ctrl+V, 끌어다 놓기)
function addFiles(files) {
  for (const f of files) {
    if (!/^(image|video)\//.test(f.type)) continue;
    const rd = new FileReader();
    rd.onload = () => { uploads.push({ name: f.name || 'grok.png', data: rd.result }); const el = $('#relayFiles'); if (el) el.textContent = `붙인 파일 ${uploads.length}개: ` + uploads.map((u) => u.name).join(', '); };
    rd.readAsDataURL(f);
  }
}
document.addEventListener('paste', (ev) => { if (!$('#relayBox').hidden && ev.clipboardData && ev.clipboardData.files.length) { addFiles(ev.clipboardData.files); } });
$('#relayBox').addEventListener('dragover', (ev) => ev.preventDefault());
$('#relayBox').addEventListener('drop', (ev) => { ev.preventDefault(); addFiles(ev.dataTransfer.files); });
document.addEventListener('pause', () => { if ($('#feed').dataset.dirty) renderFeed(); }, true);
$('#btnHire').onclick = () => hire();
$('#btnSettings').onclick = settings;
setInterval(() => { if (S.employees.some((e) => e.status === 'working')) renderEmps(); }, 30000);

// ───────── 실시간 연결 ─────────
function connect() {
  const es = new EventSource('/api/events');
  let first = true;
  es.addEventListener('state', (ev) => {
    const old = S; S = JSON.parse(ev.data); render();
    if (!first) {
      const oa = new Set(old.pending.map((p) => p.id)); for (const p of S.pending) if (!oa.has(p.id)) notify('허락 요청', `${p.empName}: ${p.label}`);
      const orl = new Set(old.grokLog.filter((g) => g.relay && g.relay.state === 'waiting').map((g) => g.id)); for (const g of relays()) if (!orl.has(g.id) && g.emp !== 'boss') notify('그록에게 옮겨 줄 말', `${g.empName}: ${g.text.slice(0, 80)}`);
      const or = new Set(old.reports.map((r) => r.id)); for (const r of S.reports) if (!or.has(r.id) && isBoss(r)) notify(`${r.empName} 보고`, r.text.slice(0, 120));
    }
    first = false;
  });
  es.addEventListener('grokdelta', (ev) => {
    const d = JSON.parse(ev.data); const g = S.grokLog.find((x) => x.id === d.id); if (g) g.text = d.text;
    const el = document.querySelector(`[data-gid="${d.id}"] .gtext`); if (!el) return;
    const box = $('#feed'); const stick = box.scrollTop + box.clientHeight > box.scrollHeight - 60;
    el.innerHTML = md(d.text); if (stick) box.scrollTop = box.scrollHeight;
  });
  es.addEventListener('log', (ev) => {
    const box = $('#logBox'); if (!box || !$('#dlg').open) return;
    const d = JSON.parse(ev.data); if (d.emp !== box.dataset.emp) return;
    const stick = box.scrollTop + box.clientHeight > box.scrollHeight - 30;
    box.insertAdjacentHTML('beforeend', box._fmt(d.line)); if (stick) box.scrollTop = box.scrollHeight;
  });
  es.onerror = () => { $('#summary').innerHTML = '<span style="color:var(--red)">회사 본체와 연결이 끊겼어요. 다시 잇는 중…</span>'; };
}
connect();
