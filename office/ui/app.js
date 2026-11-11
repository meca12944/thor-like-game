// 클로드 작업장 — 화면 (단순판, 사장님 11-11 「ui를 단순하고 쉽게」)
'use strict';
let S = { employees: [], reports: [], pending: [], rules: [], settings: {}, claude: {}, grokLog: [] };
let tab = 'report', target = '', roomMode = 'grok', allEmp = '', botTarget = '전체';
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
const MODES = { '': '작업장 기본값', auto: '알아서 하고, 애매한 것만 물어봐요 (추천)', acceptEdits: '파일 고치기만 알아서, 나머지는 물어봐요', all: '아무것도 안 물어봐요 (조심)' };
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
  $('#connDot').textContent = !S.claude.ok || !S.settings.gameRepo ? '⚠' : S.settings.botFrom ? '🟢' : '⚪';
  $('#cReport').textContent = S.reports.filter((r) => isBoss(r) && !r.read).length || '';
  const seen = Number(localStorage.getItem('grokSeen') || 0);
  $('#cGrok').textContent = tab === 'grok' ? '' : (S.grokLog.filter((g) => new Date(g.time) > seen).length || '');
  const n = S.pending.length + relays().length + S.reports.filter((r) => isBoss(r) && !r.read).length;
  document.title = (n ? `(${n}) ` : '') + '클로드 작업장';
}
function renderAsks() {
  let h = '';
  if (!S.claude.ok) h += `<div class="banner-red"><b>클로드 코드를 못 찾았어요.</b> 폴더 안 「처음_설치.bat」 을 두 번 누르고, 로그인한 뒤 다시 켜 주세요.</div>`;
  for (const p of S.pending) h += `<div class="ask"><div class="q"><b>🙋 ${esc(p.empName)}: 「${esc(p.label)}」 해도 될까요?</b><code>${esc(p.detail)}</code><div class="note">한 번 허락하면 다음부터 다시 안 물어요.</div></div>
    <button class="btn green" data-ans="always" data-id="${p.id}">허락</button><button class="btn red" data-ans="no" data-id="${p.id}">거절</button></div>`;
  $('#asks').innerHTML = h;
}
function renderEmps() {
  if (!S.employees.length) { $('#emps').innerHTML = `<div class="empty">아직 직원이 없어요.<br><br><button class="btn" data-act="team">👥 기본 팀 한 번에 뽑기 (7명)</button><br><span class="small">팀장·UI·스토리·몬스터·효과·모션·AI협력팀</span><br><br><button class="link" data-act="hire">한 명씩 뽑기</button></div>`; return; }
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
  if (tab === 'company') return renderCompany(box);
  let list = S.reports;
  let head = '';
  if (tab === 'report') list = list.filter(isBoss);
  else {
    if (allEmp) list = list.filter((r) => r.emp === allEmp);
    head = `<div><select id="allEmp" class="btn ghost small"><option value="">모든 직원</option>${S.employees.map((e) => `<option value="${e.id}" ${e.id === allEmp ? 'selected' : ''}>${esc(e.name)}</option>`).join('')}</select> <span class="muted small">직원끼리 주고받은 것까지 모두</span></div>`;
  }
  box.innerHTML = head + (list.length ? list.map(cardHtml).join('') : `<div class="empty">${tab === 'report' ? '<div style="font-size:40px">📋</div>아직 받은 보고가 없어요.<br>👈 왼쪽에서 직원을 누르고, 👇 아래에 할 일을 적어 Enter!' : '기록이 없어요.'}</div>`);
  if (tab === 'report' && document.hasFocus()) {
    clearTimeout(renderFeed._r);
    renderFeed._r = setTimeout(() => { if (tab === 'report' && list.some((r) => !r.read)) api('/api/report/read', { all: true }); }, 4000);
  }
}
function companyPack() {
  const t = S.botTargets;
  if (t && Array.isArray(t.depts) && Array.isArray(t.bots)) return t;
  return { all: '전체', depts: [], bots: [] };
}
function companySelectHtml() {
  const pack = companyPack();
  const opt = (value, label) => `<option value="${esc(value)}"${value === botTarget ? ' selected' : ''}>${label}</option>`;
  let h = `<select id="botTarget" style="padding:4px 8px;border:1px solid var(--line);background:var(--panel);min-width:260px;max-width:100%;border-radius:4px">`;
  h += opt('전체', '🏢 전체');
  if (pack.depts.length) {
    h += '<optgroup label="부서">';
    for (const d of pack.depts) h += opt(d.name, d.icon + ' ' + esc(d.name));
    h += '</optgroup>';
    for (const d of pack.depts) {
      h += `<optgroup label="${esc(d.icon + ' ' + d.name)}">`;
      for (const b of pack.bots.filter((x) => x.dept === d.id)) {
        const tag = b.lead ? ' · 팀장' : (b.grokLead ? ' · 그록 쪽 대표' : '');
        h += opt(b.name, d.icon + ' ' + esc(b.name) + tag);
      }
      h += '</optgroup>';
    }
  }
  h += '</select>';
  return h;
}
function companyPickBtn(name, label, bold, tip) {
  const on = botTarget === name;
  return `<button type="button" data-act="settarget" data-name="${esc(name)}" title="${esc(tip || name)}" style="display:block;width:100%;text-align:left;border:0;background:${on ? 'var(--bg)' : 'transparent'};padding:3px 8px;cursor:pointer;border-radius:6px;${bold ? 'font-weight:700' : ''}">${label}</button>`;
}
function renderCompany(box) {
  const hist = S.botHistory || [];
  const pack = companyPack();
  const connected = !!S.settings.botFrom;
  const groups = pack.depts.map((d) => {
    const rep = d.grokLead ? ` · 그록 쪽 대표 ${esc(d.grokLead)}` : '';
    return `<div style="padding:4px 0;border-top:1px solid var(--line)">
      ${companyPickBtn(d.name, d.icon + ' ' + esc(d.name), true)}
      <div class="muted small" style="padding:0 8px 2px">${esc(d.sub)} · 팀장 ${esc(d.lead)}${rep}</div>
    </div>`;
  }).join('');
  box.innerHTML = `<div class="card"><div class="conn-head"><span class="ico">🏢</span><div><b>회사 일 시키기</b>
      <div class="muted small">보내면 그 부서 팀장이 나눠 맡기고, 검수해서 보고 창에 올려요.</div>
      <div class="small">예: 「제로폰 오늘 정책 확인해서 보고해」</div></div></div>
    <div class="small" style="margin:4px 0 8px">${connected ? '<span style="color:var(--green)">🟢 그록 봇 연결됨</span>' : '<span class="muted">⚪ 그록 봇이 아직 안 이어졌어요</span>'}</div>
    <div class="row-btns"><button class="btn ghost small" data-act="opencompany">🏢 알들 컴퍼니 보고 창 열기</button>${connected ? '' : '<button class="btn small" data-act="openconn">🔌 먼저 그록 봇 잇기</button>'}</div>
    <div style="margin-top:12px"><div class="muted small" style="margin-bottom:4px">보낼 곳. 이름을 누르면 아래 목록에도 골라져요.</div>
      ${companyPickBtn('전체', '🏢 전체', true)}
      ${groups}
    </div></div>
    ${hist.length ? hist.map((h) => `<div class="card"><div class="card-head"><b>${esc(h.target)}</b><span class="small" style="color:${h.ok ? 'var(--green)' : 'var(--red)'}">${h.ok ? '🟢 보냄' : '🔴 ' + esc(h.result)}</span><time>${ago(h.time)}</time></div><div class="text">${esc(h.command)}</div></div>`).join('') : '<div class="empty">아직 보낸 일이 없어요.</div>'}`;
}
function renderChat(box) {
  try { localStorage.setItem('grokSeen', String(Date.now())); } catch (e) { /* */ }
  const how0 = { bot: '그록 봇(알들 컴퍼니)과 자동으로 연결돼 있어요. 보내면 그록 봇에게 바로 가고, 답은 저절로 와요.', paste: '반자동: 그록에게 가는 말은 아래 노란 칸에서 복사해 그록 앱에 붙여 넣고, 그록 답을 붙여 넣어 주세요.', api: '그록 키로 바로 연결돼 있어요.' }[S.settings.grokWay] || '';
  const how = how0 + (S.settings.grokWay === 'paste' ? '<br>🔌 「연결 → 그록 봇」을 이어 두면 옮겨 주지 않아도 돼요.' : '');
  if (!S.grokLog.length) { box.innerHTML = `<div class="empty"><div style="font-size:40px">💬</div>사장님 · 그록 · 클로드가 함께 이야기하는 곳이에요.<br>👇 아래에서 고르고 적어 보세요.<br><br><span class="small">${how}</span></div>`; return; }
  const stick = box.scrollTop + box.clientHeight > box.scrollHeight - 60;
  box.innerHTML = `<div class="chat">${S.grokLog.map((g) => {
    const cls = g.kind === 'boss' ? 'boss' : g.kind === 'sys' ? 'sys' : (g.kind === 'claude' || g.kind === 'ask') ? 'claude' : 'grok';
    const who = cls === 'boss' ? '사장님' : cls === 'sys' ? '' : cls === 'claude' ? esc(g.empName) + ' (클로드)' : '그록';
    const wait = g.relay && g.relay.state === 'waiting' ? `<span class="wait">${g.relay.sent ? '🤖 그록 봇에게 보냈어요 · 답 기다리는 중' : g.relay.way === 'bot' && !g.relay.sendError ? '🤖 그록 봇에게 보내는 중…' : '⏳ 그록에게 옮겨 주기를 기다려요 (아래 노란 칸)'}</span>` : '';
    return `<div class="bubble ${cls}" data-gid="${g.id}">${who ? `<div class="who">${who} · ${ago(g.time)}</div>` : ''}<span class="gtext ${g.streaming ? 'typing' : ''}">${md(g.text)}</span>${mediaHtml(g.files, (f) => `/grokfile?g=${g.id}&i=${f.i}`)}${wait}</div>`;
  }).join('')}</div>`;
  if (stick || !box._once || box._count !== S.grokLog.length) { box.scrollTop = box.scrollHeight; box._once = true; box._count = S.grokLog.length; }
}
const relays = () => S.grokLog.filter((g) => g.relay && g.relay.state === 'waiting' && (g.relay.way !== 'bot' || g.relay.sendError || g.relay.manual));
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
  box.innerHTML = `${r.relay.sendError ? `<div class="step" style="color:var(--red)">${esc(r.relay.sendError)}</div>` : ''}<div class="step"><span class="num">1</span><b>${esc(r.empName)}</b>이(가) 그록에게 할 말이 있어요${list.length > 1 ? ` (남은 것 ${list.length}개)` : ''}
      <button class="btn small" data-act="relaycopy" data-id="${r.id}">📋 그록에 붙일 글 복사</button>
      ${r.files.length ? `<span class="files">같이 줄 그림: ${r.files.map((f) => esc(f.name)).join(', ')}</span>` : ''}</div>
    <div class="step"><span class="num">2</span>그록 앱에 붙여 넣고, 그록 답을 복사해서 아래에 붙여 넣어 주세요. 그림·영상은 Ctrl+V 나 끌어다 놓기.</div>
    <textarea id="relayText" rows="2" placeholder="그록 답 붙여 넣기"></textarea>
    <div class="step" style="margin:8px 0 0"><span class="files" id="relayFiles"></span><span style="flex:1"></span><button class="btn green" data-act="relaysend" data-id="${r.id}">그록 답 넣기</button></div>`;
}
function renderSay() {
  const to = $('#sayTo'), ta = $('#sayText');
  if (tab === 'company') {
    if (document.activeElement && document.activeElement.id === 'botTarget') return; // 목록 고르는 중이면 그대로
    to.innerHTML = `📣 보낼 곳 ${companySelectHtml()}<div class="muted small" style="flex-basis:100%">보내면 그 부서 팀장이 나눠 맡기고, 검수해서 보고 창에 올려요.</div>`;
    ta.placeholder = '예: 제로폰 오늘 정책 확인해서 보고해';
    return;
  }
  if (tab === 'grok') {
    const p = partner();
    const chips = [['grok', '🤖 그록에게 말하기'], ['claude', '🧠 클로드(' + (p ? p.name : 'AI협력팀') + ')에게'], ['meeting', '🗣 둘이 회의시키기'], ['image', '🎨 그록에게 그림 부탁']];
    to.innerHTML = chips.map(([k, v]) => `<button type="button" data-room="${k}" class="${roomMode === k ? 'on' : ''}">${v}</button>`).join('') + '<span style="flex:1"></span><button type="button" class="link" data-act="roomreset">새 대화</button>';
    ta.placeholder = { grok: '그록에게 할 말 (예: 주인공 망토 색 추천해 줘)', claude: '클로드에게 할 말 — 필요하면 클로드가 그록에게도 물어봐요', meeting: '회의 주제 (예: 1장 보스 공격 패턴 정하기) — 둘이 이야기하고 결론을 보고해요', image: '그릴 것 (예: 붉은 망토 기사, 옆모습, 투명 배경)' }[roomMode] + '  · Enter 보내기';
  } else {
    const e = S.employees.find((x) => x.id === target);
    to.innerHTML = e ? `✍️ <b>${esc(e.name)}</b>에게 일 시키기 <span class="muted small">(다른 직원은 왼쪽에서 누르기)</span><span style="flex:1"></span>${S.employees.length > 1 ? `<button type="button" data-act="toall" class="${target === 'all' ? 'on' : ''}">모두에게</button>` : ''}` : '먼저 직원을 뽑아 주세요.';
    ta.placeholder = '할 일을 적어 주세요 (예: 몹 점검 표 다시 뽑아서 보고해)  · Enter 보내기, Shift+Enter 줄바꿈';
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
  dialog(`<h2>⚙ 그 밖의 설정</h2>
    <p class="muted small">다른 프로그램·AI 와 잇는 것은 위의 「🔌 연결」에 있어요.</p>
    <div class="row-btns">
      <button class="btn ghost" value="rules">✅ 허락해 둔 일 목록</button>
      <button class="btn red" value="stopall">✋ 모든 직원 멈추기</button>
    </div>
    <details class="more-set"><summary>더 보기 (잘 안 바꾸는 것)</summary>
      <div class="field"><label>직원이 물어보는 정도</label><select name="defaultMode">${Object.entries(MODES).filter(([k]) => k).map(([k, v]) => `<option value="${k}" ${k === s.defaultMode ? 'selected' : ''}>${v}</option>`).join('')}</select></div>
      <div class="field"><label>직원끼리 말이 오가는 최대 횟수</label><input type="text" name="maxHops" value="${esc(s.maxHops)}"><div class="help">직원끼리 끝없이 말을 주고받지 않게 막아요.</div></div>
      <div class="field"><label>직원 작업 공간 위치</label><input type="text" name="workspace" value="${esc(s.workspace)}"><div class="help">비워 두면 게임 폴더 옆 「…_직원」 폴더</div></div>
    </details>
    <div class="err-text"></div>
    <div class="dlg-foot"><button class="btn ghost" value="quit" style="margin-right:auto">작업장 끄기</button><button class="btn ghost" value="cancel">닫기</button><button class="btn" value="ok">저장</button></div>`,
  async (fd, v) => {
    if (v === 'rules') { setTimeout(rules, 30); return; }
    if (v === 'stopall') { if (confirm('모든 직원의 일을 멈출까요?')) await api('/api/stopAll'); return; }
    if (v === 'quit') { if (confirm('클로드 작업장을 끌까요? 일하던 직원도 멈춰요.')) { await api('/api/quit'); document.body.innerHTML = '<div class="empty">작업장 문을 닫았어요. 이 창을 닫아도 돼요.</div>'; } return; }
    const r = await api('/api/settings', fd); return r.ok ? null : r.error;
  });
}
// ───────── 🔌 연결 (커넥터) ─────────
function conns() {
  const s = S.settings;
  return [
    { id: 'claude', ico: '🧠', nm: '클로드 코드', ds: '직원(클로드)이 일하는 프로그램', on: S.claude.ok, lamp: S.claude.ok ? '켜짐' : '없음',
      what: '직원들이 실제로 일하는 프로그램이에요. 지금 쓰는 클로드 구독으로 돌아가서 돈이 더 들지 않아요.',
      how: S.claude.ok ? `잘 연결돼 있어요 (${esc(S.claude.version)}).` : '폴더 안 「처음_설치.bat」 을 두 번 누르면 깔려요. 깔고 나서 로그인하고 작업장을 다시 켜 주세요.',
      fields: `<div class="field"><label>프로그램 이름 (보통 그대로)</label><input type="text" name="claudeCmd" value="${esc(s.claudeCmd)}"></div>` },
    { id: 'game', ico: '🎮', nm: '게임 폴더', ds: '직원들이 고칠 게임 파일이 있는 곳', on: !!s.gameRepo, lamp: s.gameRepo ? '정해짐' : '안 정함',
      what: '「필멸자」 게임 파일이 들어 있는 폴더예요. 새 직원을 뽑으면 여기서 그 직원만 쓰는 자리를 만들어 줘요.',
      how: '보통 「C:\\Users\\(이름)\\thor-like-game」 이에요. 처음_설치.bat 이 받아 둔 곳이에요.',
      fields: `<div class="field"><label>게임 폴더</label><input type="text" name="gameRepo" value="${esc(s.gameRepo)}" placeholder="예) C:\\Users\\이름\\thor-like-game"></div>` },
    { id: 'bot', ico: '🤖', nm: '그록 봇', ds: '클로드가 그록에게 바로 말을 보내요', on: !!s.botFrom, lamp: s.botFrom ? '연결됨' : '안 됨',
      what: '알들 컴퍼니의 그록 봇이에요. 연결하면 클로드가 그록에게 할 말이 생길 때 사장님이 옮겨 주지 않아도 바로 가요. 공짜예요.',
      how: '알들 컴퍼니 명령창 「설정」에 넣은 <b>웹훅 주소</b>와 <b>웹훅 키</b>를 똑같이 아래에 붙여 넣으세요. 한 번만 하면 돼요.',
      fields: `<div class="field"><label>웹훅 주소</label><input type="text" name="botUrl" value="${esc(s.botUrl)}" placeholder="https://… (명령창과 같은 것)"></div>
        <div class="field"><label>웹훅 키</label><input type="password" name="botKey" placeholder="${s.hasBotKey ? '들어 있어요 (바꿀 때만 넣기)' : '명령창과 같은 키'}" autocomplete="off"></div>
        <input type="hidden" name="grokMode" value="bot">` },
    { id: 'mail', ico: '📮', nm: '그록 답 우편함', ds: '그록의 답을 받아 오는 곳 (깃허브)', on: s.coop && s.coop.ok, lamp: s.coop && s.coop.ok ? '받는 중' : '대기',
      what: `그록 봇이 답을 깃허브 <a href="${esc(s.issueUrl)}" target="_blank">AI협력 대화방</a>에 남기면, 작업장이 가져와서 기다리던 클로드에게 넘겨 줘요. 공짜예요.`,
      how: '따로 할 일은 없어요. 그록 봇을 연결하면 저절로 켜져요. 기다리는 답이 있으면 20초마다, 없으면 3분마다 확인해요.<br>더 빨리(늘 20초) 받고 싶으면 깃허브 열쇠를 넣으세요 (없어도 돼요).',
      fields: `<div class="field"><label>깃허브 열쇠 (없어도 돼요)</label><input type="password" name="ghToken" placeholder="${s.hasGhToken ? '들어 있어요' : '비워 둬도 돼요'}" autocomplete="off"></div>` },
    { id: 'company', ico: '🏢', nm: '알들 컴퍼니', ds: '회사 전체 화면 (모든 부서)', on: !!s.companyUrl, lamp: '열기',
      what: '회사 전체 부서와 그록 봇 팀원이 있는 화면이에요. 이 작업장은 그 안의 「게임 필멸자」 부서예요.',
      how: '위의 「🏢 알들 컴퍼니」 단추를 누르면 열려요.',
      fields: `<div class="field"><label>알들 컴퍼니 주소</label><input type="text" name="companyUrl" value="${esc(s.companyUrl)}"></div>`, act: 'company' },
    { id: 'board', ico: '📋', nm: '업무판', ds: '그록·다른 AI 에게 우리 일을 알려 줘요', on: true, lamp: '켜짐',
      what: '지금 게임 상태·최근 결정·할 일이 저절로 모이는 공개 게시판이에요. 그록에게 주소를 한 번 주면 우리 일을 알고 일해요.',
      how: '아래 「주소 복사」를 누르고 그록에게 붙여 넣으세요.', fields: '', act: 'board' },
    { id: 'folder', ico: '📁', nm: '그록 폴더', ds: '그록 그림이 오면 저절로 확인해요', on: !!s.grokDir, lamp: s.grokDir ? '지켜보는 중' : '안 정함',
      what: '구글 드라이브의 그록 공유 폴더를 PC 폴더로 보이게 해 두면, 새 그림·영상이 올 때 AI협력팀이 저절로 확인하고 보고해요.',
      how: 'PC에 「Google Drive 데스크톱」을 깔고, 그 폴더 주소를 아래에 넣으세요 (예: G:\\내 드라이브\\…).',
      fields: `<div class="field"><label>그록 폴더 (PC 주소)</label><input type="text" name="grokDir" value="${esc(s.grokDir)}"></div>`, act: 'folder' },
    { id: 'github', ico: '🐙', nm: '깃허브 올리기', ds: '직원이 고친 것을 깃허브에 올려요 (PR)', on: !!(s.ghPush && s.ghPush.ok), lamp: s.ghPush ? (s.ghPush.ok ? '올릴 수 있음' : '로그인 필요') : '확인 안 함',
      what: '직원(클로드)이 게임을 고치면, 깃허브에 올리고 「합치기 부탁(PR)」을 만들어요. 그러려면 이 PC 가 사장님 깃허브 계정으로 한 번 로그인돼 있어야 해요.',
      how: `아래 「로그인·확인」을 누르세요. 로그인이 안 돼 있으면 <b>깃허브 로그인 창</b>이 떠요 → 사장님 깃허브 계정으로 로그인 → 다시 「로그인·확인」. 실제로 올리지는 않고 확인만 해요.${s.ghPush ? `<br><br>마지막 확인: <b>${esc(s.ghPush.msg)}</b> (${ago(s.ghPush.at)})${s.ghPush.name ? `<br>커밋 이름: ${esc(s.ghPush.name)} / ${esc(s.ghPush.email || '이메일 없음')}` : '<br>⚠ 커밋 이름이 없어요. 아래에 적어 주세요.'}` : ''}`,
      fields: `<div class="field"><label>커밋에 남길 이름 (비워 두면 그대로)</label><input type="text" name="gitName" placeholder="${esc((s.ghPush && s.ghPush.name) || '예: meca12944')}"></div>
        <div class="field"><label>커밋에 남길 이메일 (비워 두면 그대로)</label><input type="text" name="gitEmail" placeholder="${esc((s.ghPush && s.ghPush.email) || '깃허브 계정 이메일')}"></div>`, act: 'github' },
    { id: 'pixellab', ico: '🎨', nm: 'PixelLab', ds: '직원이 도트 그림을 만들 때 써요', on: !!s.hasPixellab, lamp: s.hasPixellab ? '넣어 둠' : '안 넣음',
      what: '도트(픽셀) 그림을 만들어 주는 서비스예요. 직원이 몹·주인공 그림을 만들 때 이 키를 써요. <b>쓸 때마다 크레딧(돈)이 줄어요.</b> 직원은 일이 끝나면 쓴 크레딧을 보고해요.',
      how: 'pixellab.ai 에 로그인 → 계정 설정에서 API 키를 복사 → 아래에 붙여 넣기. 키는 이 PC 의 data 폴더에만 있고 화면·기록에 안 나와요.',
      fields: `<div class="field"><label>PixelLab 키</label><input type="password" name="pixellabKey" placeholder="${s.hasPixellab ? '들어 있어요 (바꿀 때만 넣기)' : 'PixelLab API 키'}" autocomplete="off"></div>
        ${s.hasPixellab ? '<div class="field"><label class="check"><input type="checkbox" name="pixellabClear"> 키 지우기</label></div>' : ''}` },
    { id: 'mcp', ico: '🧩', nm: '클로드 연결 도구', ds: '구글 드라이브·노션 같은 바깥 서비스', on: !!(s.mcpList && s.mcpList.count), lamp: s.mcpList ? (s.mcpList.count ? `${s.mcpList.count}개 연결` : '없음') : '확인 안 함',
      what: '클로드가 구글 드라이브·노션·깃허브 같은 바깥 서비스를 직접 쓰게 해 주는 연결이에요 (영어로 「MCP 커넥터」). 여기 목록에 나오는 것만 PC 직원들이 쓸 수 있어요.',
      how: `아래 「목록 보기」로 지금 이어진 것을 확인해요. 더 잇고 싶으면 이 대화방의 클로드에게 「○○ 연결해 줘」라고 말하면 순서를 알려 드려요. 지금 없어도 일하는 데는 문제없어요 (그록과는 🤖 그록 봇으로 이어져 있어요).${s.mcpList ? `<br><br>마지막 확인 (${ago(s.mcpList.at)}):<code style="display:block;white-space:pre-wrap;margin-top:4px">${esc(s.mcpList.text)}</code>` : ''}`,
      fields: '', act: 'mcp' },
    { id: 'xai', ico: '🔑', nm: '그록 키 (유료)', ds: '돈을 내고 그록과 완전 자동으로', on: s.grokWay === 'api', lamp: s.grokWay === 'api' ? '쓰는 중' : '안 씀',
      what: '그록 회사(xAI)의 유료 키예요. 그록 봇 없이도 완전 자동이지만, 쓴 만큼 돈이 나가요 (말 한 번 약 30원, 그림 1장 약 60원).',
      how: '보통은 필요 없어요. 쓰려면 console.x.ai 에서 키를 만들어 아래에 넣고 「이걸로 쓰기」에 체크하세요.',
      fields: `<div class="field"><label>그록 키</label><input type="password" name="xaiKey" placeholder="${s.hasXaiKey ? '들어 있어요' : 'xai- 로 시작'}" autocomplete="off"></div>
        <div class="field"><label class="check"><input type="checkbox" name="useApi" ${s.grokMode === 'api' ? 'checked' : ''}> 이걸로 쓰기 (끄면 그록 봇 → 붙여넣기 순서로 써요)</label></div>
        <div class="field"><label>하루 한도 (달러)</label><input type="text" name="grokBudget" value="${esc(s.grokBudget)}"><div class="help">오늘 쓴 돈 $${(s.grokSpent || 0).toFixed(2)}</div></div>` },
  ];
}
function connections() {
  dialog(`<h2>🔌 연결</h2><p class="muted">작업장과 이어지는 것들이에요. 눌러 보면 무엇인지, 어떻게 잇는지 나와요.</p>
    <div class="tiles">${conns().map((c) => `<button class="tile" value="c:${c.id}"><span class="lamp ${c.on ? 'on' : 'off'}">${c.on ? '🟢' : '⚪'} ${c.lamp}</span><div class="ico">${c.ico}</div><div class="nm">${c.nm}</div><div class="ds">${c.ds}</div></button>`).join('')}</div>
    <div class="dlg-foot"><button class="btn ghost" value="cancel">닫기</button></div>`,
  async (fd, v) => { if (v.startsWith('c:')) setTimeout(() => connOne(v.slice(2)), 30); });
}
function connOne(id) {
  const c = conns().find((x) => x.id === id); if (!c) return;
  dialog(`<div class="conn-head"><span class="ico">${c.ico}</span><div><h2 style="margin:0">${c.nm}</h2><span class="lamp ${c.on ? 'on' : 'off'}">${c.on ? '🟢' : '⚪'} ${c.lamp}</span></div></div>
    <div class="qa"><div class="qh">이게 뭐예요?</div>${c.what}</div>
    <div class="qa"><div class="qh">어떻게 해요?</div>${c.how}</div>
    ${c.fields}
    <div class="err-text"></div>
    <div class="dlg-foot"><button class="btn ghost" value="back" style="margin-right:auto">← 연결 목록</button>
      ${c.act === 'board' ? '<button class="btn" value="board">📋 주소 복사</button>' : ''}
      ${c.act === 'company' ? '<button class="btn ghost" value="company">열기</button>' : ''}
      ${c.act === 'folder' && S.settings.grokDir ? '<button class="btn ghost" value="folder">지금 확인시키기</button>' : ''}
      ${c.act === 'github' ? '<button class="btn ghost" value="ghcheck">🐙 로그인·확인</button>' : ''}
      ${c.act === 'mcp' ? '<button class="btn" value="mcpcheck">🧩 목록 보기</button>' : ''}
      ${c.fields ? '<button class="btn" value="ok">저장</button>' : '<button class="btn ghost" value="cancel">닫기</button>'}</div>`,
  async (fd, v) => {
    if (v === 'back') { setTimeout(connections, 30); return; }
    if (v === 'board') { copy('우리 팀 업무 공유판이야. 일하기 전에 꼭 읽고, 여기 적힌 결정과 규칙을 따라 줘: ' + BOARD, '복사했어요. 그록에 붙여 넣으세요'); return ''; }
    if (v === 'company') { window.open(S.settings.companyUrl, '_blank'); return ''; }
    if (v === 'folder') { const r = await api('/api/grokCheck'); if (!r.ok) return r.error; toast('AI협력팀이 그록 폴더를 확인해요'); return; }
    if (v === 'ghcheck' || v === 'mcpcheck') {
      toast(v === 'ghcheck' ? '깃허브 확인 중… 로그인 창이 뜨면 로그인해 주세요' : '연결 도구 목록을 보는 중… (최대 1분)');
      const r = await api('/api/conn/check', { id: v === 'ghcheck' ? 'github' : 'mcp' });
      if (!r.ok) return r.error;
      setTimeout(() => connOne(id), 200); return;
    }
    if (id === 'xai') fd.grokMode = fd.useApi ? 'api' : 'bot';
    const r = await api('/api/settings', fd);
    if (!r.ok) return r.error;
    toast('저장했어요'); setTimeout(connections, 300);
  });
}
// ───────── ❓ 사용법 ─────────
function guide() {
  dialog(`<h2>❓ 클로드 작업장 쓰는 법</h2>
    <div class="guide">
      <div class="g"><div class="big">👆</div><b>1. 직원 고르기</b><span>왼쪽에서 일 시킬 직원 이름을 눌러요.<br>모르겠으면 <b>팀장</b>에게!</span></div>
      <div class="g"><div class="big">✍️</div><b>2. 할 일 적기</b><span>맨 아래 칸에 할 일을 적고<br><b>Enter</b> 를 눌러요.</span></div>
      <div class="g"><div class="big">📋</div><b>3. 보고 보기</b><span>일이 끝나면 「받은 보고」에<br>글·사진·영상이 와요.</span></div>
    </div>
    <ul class="tips">
      <li>🙋 위에 <b>노란 칸 「해도 될까요?」</b>가 뜨면 <b>허락</b>을 눌러요. 한 번 허락하면 다시 안 물어요.</li>
      <li>💬 <b>그록과 이야기</b> 칸에서 그록에게 말하거나, 클로드와 그록에게 회의를 시킬 수 있어요.</li>
      <li>🔌 <b>연결</b>에서 그록 봇·게임 폴더·깃허브·PixelLab 같은 것을 이어요 (아이콘 11개). 아이콘을 누르면 「이게 뭐예요? / 어떻게 해요?」가 나와요. 🟢 = 이어짐, ⚪ = 아직.</li>
      <li>⋯ 직원 이름 옆 <b>⋯</b> 를 누르면: 지금 하는 일 보기, 멈추기, 고치기.</li>
      <li>직원끼리는 알아서 말을 주고받아요. 사장님이 말을 옮길 필요 없어요.</li>
    </ul>
    <div class="dlg-foot"><button class="btn" value="cancel">알겠어요</button></div>`);
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
  if (a === 'settarget') { botTarget = t.getAttribute('data-name') || '전체'; render(); return; }
  if (a === 'opencompany') { if (S.settings.companyUrl) window.open(S.settings.companyUrl, '_blank'); }
  if (a === 'openconn') connOne('bot');
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
document.addEventListener('input', (ev) => { if (ev.target.id === 'botTarget') botTarget = ev.target.value; });
document.addEventListener('change', (ev) => {
  if (ev.target.id === 'botTarget') { botTarget = ev.target.value; if (tab === 'company') render(); return; }
  if (ev.target.id === 'allEmp') { allEmp = ev.target.value; renderFeed(); }
});
$('#say').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const text = $('#sayText').value.trim();
  if (!text) {
    if (tab === 'company') alert('할 일을 적어 주세요. 예: 제로폰 오늘 정책 확인해서 보고해');
    return;
  }
  let r;
  if (tab === 'company') {
    botTarget = ($('#botTarget') && $('#botTarget').value.trim()) || botTarget;
    r = await api('/api/bot/command', { target: botTarget, command: text });
    if (r.ok) toast(`📣 ${botTarget}에게 보냈어요`);
  } else if (tab === 'grok') {
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
$('#btnCompany').onclick = () => { if (S.settings.companyUrl) window.open(S.settings.companyUrl, '_blank'); };
$('#btnSettings').onclick = settings;
$('#btnConn').onclick = connections;
$('#btnHelp').onclick = guide;
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
try { if (!localStorage.getItem('guideSeen')) { localStorage.setItem('guideSeen', '1'); setTimeout(guide, 800); } } catch (e) { /* */ }
