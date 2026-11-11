// 클로드 회사 — 화면
'use strict';
let S = { employees: [], reports: [], pending: [], rules: [], settings: {}, claude: {}, grokLog: [] };
let filter = 'boss', filterEmp = '';
const openTasks = new Set();
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const api = (p, body) => fetch(p, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body || {}) }).then((r) => r.json());
const COLORS = ['#c8643b', '#2f6fde', '#1f9d55', '#8b5cf6', '#d13b7a', '#0e8f8f', '#b7791f', '#5b6b8a'];
const colorOf = (s) => { let h = 0; for (const c of String(s)) h = (h * 31 + c.charCodeAt(0)) >>> 0; return COLORS[h % COLORS.length]; };
const avatar = (name) => `<span class="avatar" style="background:${colorOf(name)}">${esc(String(name).slice(0, 1))}</span>`;
const STATUS = { idle: '쉬는 중', working: '일하는 중', waiting: '허락 기다림', error: '문제 있음' };
const MODES = { '': '회사 기본값', auto: '알아서 (위험한 것만 물어봄)', acceptEdits: '파일 고치기만 자동 (명령은 물어봄)', all: '전부 허락 (아무것도 안 물어봄)' };
function ago(t) {
  const s = (Date.now() - new Date(t)) / 1000;
  if (s < 60) return '방금'; if (s < 3600) return Math.floor(s / 60) + '분 전'; if (s < 86400) return Math.floor(s / 3600) + '시간 전';
  return new Date(t).toLocaleString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function md(t) {
  let h = esc(t);
  h = h.replace(/```[\w-]*\n?([\s\S]*?)```/g, (m, c) => `<code style="display:block;white-space:pre-wrap">${c}</code>`);
  h = h.replace(/^#{1,4}\s+(.+)$/gm, '<h4>$1</h4>');
  h = h.replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>');
  h = h.replace(/`([^`\n]+)`/g, '<code>$1</code>');
  h = h.replace(/\n?(<h4>)/g, '$1').replace(/(<\/h4>)\n/g, '$1');
  return h;
}

// ───── 그리기 ─────
function render() {
  const E = S.employees;
  const n = (st) => E.filter((e) => e.status === st).length;
  $('#summary').innerHTML = [
    `<span class="chip">직원 ${E.length}명</span>`,
    n('working') ? `<span class="chip work">일하는 중 ${n('working')}</span>` : '',
    S.pending.length ? `<span class="chip wait">허락 기다림 ${S.pending.length}</span>` : '',
    n('error') ? `<span class="chip err">문제 ${n('error')}</span>` : '',
    S.employees.some((e) => e.partner) ? `<span class="chip grok" title="그록 터널: 오늘 쓴 돈 / 하루 한도">그록 ${S.settings.hasXaiKey ? `연결됨 · 오늘 $${(S.settings.grokSpent || 0).toFixed(2)} / $${S.settings.grokBudget}` : '키 없음 (폴더 방식)'}</span>` : '',
  ].join('');
  $('#empCount').textContent = E.length ? `${E.length}명` : '';
  renderBanners(); renderEmps(); renderOrderTo(); renderReports();
  const unread = S.reports.filter((r) => !r.read).length;
  document.title = (S.pending.length || unread ? `(${S.pending.length + unread}) ` : '') + '클로드 회사';
}
function renderBanners() {
  let h = '';
  if (!S.claude.ok) h += `<div class="banner red"><h3>클로드 코드를 못 찾았어요</h3>직원이 일하려면 PC에 클로드 코드가 깔려 있어야 해요. 폴더 안 <b>처음_설치.bat</b> 을 두 번 눌러 설치하고, 「명령 프롬프트」에서 <code>claude</code> 를 한 번 실행해 로그인한 뒤 이 프로그램을 다시 켜 주세요.<pre>${esc(S.claude.error || '')}</pre></div>`;
  for (const p of S.pending) {
    h += `<div class="banner ask"><div><div class="what">🙋 ${esc(p.empName)}: 「${esc(p.label)}」 해도 될까요?</div><code>${esc(p.detail)}</code></div>
      <div class="btns"><button class="btn green" data-ans="always" data-id="${p.id}">항상 허락</button><button class="btn ghost" data-ans="once" data-id="${p.id}">이번만</button><button class="btn danger" data-ans="no" data-id="${p.id}">거절</button></div>
      <div class="rule">「항상 허락」을 누르면 다음부터 모든 직원이 안 묻고 해요: ${p.rules.map((r) => `<code style="display:inline;padding:0 4px">${esc(r)}</code>`).join(' ')}</div></div>`;
  }
  $('#banners').innerHTML = h;
}
function renderEmps() {
  if (!S.employees.length) { $('#emps').innerHTML = `<div class="empty">아직 직원이 없어요.<br><br><button class="btn" onclick="makeTeam()">기본 팀 만들기 (팀장 + 5명)</button><br><br><button class="btn ghost" onclick="hire()">＋ 한 명씩 뽑기</button><p class="small">기본 팀은 팀 회의 교본 1-6 의 나눔 그대로예요.<br>먼저 설정에서 「게임 원본 폴더」가 정해져 있어야 해요.</p></div>`; return; }
  $('#emps').innerHTML = S.employees.map((e) => `
    <div class="emp ${e.status}">
      <div class="emp-head">${avatar(e.name)}<div><div class="emp-name">${esc(e.name)}${e.partner ? '<span class="tag">그록</span>' : ''}</div><div class="emp-role">${esc(e.role)}</div></div>
        <span class="pill ${e.status}"><span class="dot"></span>${STATUS[e.status] || e.status}</span></div>
      ${e.now ? `<div class="emp-now">${esc(e.now)}</div>` : ''}
      ${e.task ? `<div class="emp-task">📋 ${e.taskFrom !== '사장님' ? `[${esc(e.taskFrom)}] ` : ''}${esc(e.task)}</div>` : ''}
      <div class="emp-foot"><span class="q">${e.queue ? `대기 ${e.queue}건` : ''}${e.startedAt && e.status === 'working' ? ` · ${ago(e.startedAt)} 시작` : ''}</span>
        <button class="btn small" data-act="give" data-id="${e.id}">일 시키기</button>
        <button class="btn ghost small" data-act="log" data-id="${e.id}">작업 보기</button>
        ${e.status === 'working' || e.status === 'waiting' ? `<button class="btn danger small" data-act="stop" data-id="${e.id}">멈춤</button>` : ''}
        <button class="btn ghost small" data-act="more" data-id="${e.id}">⋯</button></div>
    </div>`).join('');
}
function renderOrderTo() {
  const sel = $('#orderTo'); const cur = sel.value;
  sel.innerHTML = S.employees.map((e) => `<option value="${e.id}">${esc(e.name)} — ${esc(e.role)}</option>`).join('') + (S.employees.length > 1 ? '<option value="all">모두에게</option>' : '');
  if (cur && [...sel.options].some((o) => o.value === cur)) sel.value = cur;
  const fe = $('#filterEmp'); const c2 = fe.value;
  fe.innerHTML = '<option value="">모든 직원</option>' + S.employees.map((e) => `<option value="${e.id}">${esc(e.name)}</option>`).join('');
  fe.value = c2;
}
function renderReports() {
  $('#cUnread').textContent = S.reports.filter((r) => !r.read).length || '';
  const isBoss = (r) => r.toBoss !== false || r.needBoss || r.isError;
  $('#cBoss').textContent = S.reports.filter((r) => isBoss(r) && !r.read).length || '';
  const seenGrok = Number(localStorage.getItem('grokSeen') || 0);
  $('#cGrok').textContent = S.grokLog.filter((g) => new Date(g.time) > seenGrok).length || '';
  if (filter === 'grok') return renderGrok();
  let list = S.reports;
  if (filter === 'unread') list = list.filter((r) => !r.read);
  if (filter === 'boss') list = list.filter(isBoss);
  if (filter === 'team') list = list.filter((r) => !isBoss(r));
  if (filter === 'media') list = list.filter((r) => r.files.length);
  if (filter === 'error') list = list.filter((r) => r.isError || r.denials.length);
  if (filterEmp) list = list.filter((r) => r.emp === filterEmp);
  const box = $('#reports');
  // 재생 중인 영상은 다시 그리지 않음
  if ([...box.querySelectorAll('video')].some((v) => !v.paused)) { box.dataset.dirty = '1'; return; }
  box.dataset.dirty = '';
  if (!list.length) { box.innerHTML = `<div class="empty">보고가 아직 없어요.</div>`; return; }
  box.innerHTML = list.map((r) => {
    const long = r.text.length > 900;
    return `<article class="rep ${r.read ? '' : 'unread'} ${r.needBoss ? 'boss' : ''} ${r.isError ? 'err' : ''}" data-rid="${r.id}">
      <div class="rep-head">${avatar(r.empName)}<b>${esc(r.empName)}</b><span class="from">${r.from === '사장님' ? '사장님이 시킨 일' : esc(r.from) + '이(가) 보낸 일'}${r.stopped ? ' · 멈춤' : ''}${r.isError ? ' · 문제' : ''}</span><time title="${esc(new Date(r.time).toLocaleString('ko-KR'))}">${ago(r.time)}</time></div>
      <div class="rep-task ${openTasks.has(r.id) ? 'open' : ''}" data-act="task" data-id="${r.id}">📋 ${esc(r.task)}</div>
      ${r.asks.length ? `<div class="asks"><b>사장님 확인이 필요해요</b><br>${r.asks.map(esc).join('<br>')}</div>` : ''}
      <div class="rep-text ${long ? 'clamp' : ''}">${md(r.text)}</div>
      ${long ? `<button class="link" data-act="more-text">더 보기</button>` : ''}
      ${r.files.length ? `<div class="media">${r.files.map((f) => f.kind === 'video' ? `<figure><video src="/file?r=${r.id}&i=${f.i}" controls preload="metadata" playsinline></video><figcaption>${esc(f.name)}</figcaption></figure>` : `<figure><img src="/file?r=${r.id}&i=${f.i}" loading="lazy" data-act="zoom"><figcaption>${esc(f.name)}</figcaption></figure>`).join('')}</div>` : ''}
      <div class="rep-foot">
        ${r.forwards.length ? `<span>📨 전달: ${r.forwards.map(esc).join(', ')}</span>` : ''}
        ${r.denials.length ? `<span class="warn">⛔ 거절된 일: ${r.denials.map(esc).join(', ')}</span>` : ''}
        <span class="sp"></span>
        ${r.cost ? `<span title="구독이면 실제 돈은 안 나가요. 일의 크기를 보는 숫자예요.">일의 양 ${r.cost.toFixed(2)}</span>` : ''}
        ${r.read ? '' : `<button class="link" data-act="read" data-id="${r.id}">읽음</button>`}
        ${/```/.test(r.text) ? `<button class="link" data-act="copy" data-id="${r.id}">붙여넣기 글 복사</button>` : ''}
        <button class="link" data-act="copyall" data-id="${r.id}">복사</button>
        <button class="link" data-act="reply" data-id="${r.id}">답하기</button>
        ${r.files.length ? `<button class="link" data-act="openfile" data-id="${r.id}">폴더 열기</button>` : ''}
        <button class="link" data-act="delrep" data-id="${r.id}" style="color:var(--muted)">지우기</button>
      </div></article>`;
  }).join('');
}

function renderGrok() {
  const box = $('#reports');
  try { localStorage.setItem('grokSeen', String(Date.now())); } catch (e) { /* */ }
  $('#cGrok').textContent = '';
  if ([...box.querySelectorAll('video')].some((v) => !v.paused)) { box.dataset.dirty = '1'; return; }
  if (!S.grokLog.length) {
    box.innerHTML = `<div class="empty">아직 그록과 나눈 이야기가 없어요.<br><br>${S.settings.hasXaiKey ? 'AI협력팀에게 「그록에게 ~ 부탁해」 라고 시키면 여기에 실시간으로 보여요.' : '설정에서 <b>그록 키</b>를 넣으면 AI협력팀이 그록과 바로 이야기해요 (실시간 터널).<br>키가 없으면 지금처럼 드라이브 폴더로 주고받아요.'}</div>`;
    return;
  }
  const stick = box.scrollTop + box.clientHeight > box.scrollHeight - 40;
  box.innerHTML = `<div class="grok">${S.grokLog.map((g) => {
    const me = g.kind === 'ask';
    return `<div class="bubble ${me ? 'me' : ''}"><div class="who">${me ? esc(g.empName) + ' → 그록' : '그록 → ' + esc(g.empName)} · ${ago(g.time)}</div>${md(g.text)}${g.files.length ? `<div class="media">${g.files.map((f) => f.kind === 'video' ? `<figure><video src="/grokfile?g=${g.id}&i=${f.i}" controls preload="metadata"></video><figcaption>${esc(f.name)}</figcaption></figure>` : `<figure><img src="/grokfile?g=${g.id}&i=${f.i}" loading="lazy" data-act="zoom"><figcaption>${esc(f.name)}</figcaption></figure>`).join('')}</div>` : ''}</div>`;
  }).join('')}</div>`;
  if (stick) box.scrollTop = box.scrollHeight;
}

// ───── 대화창 ─────
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
    d.close();
  };
  d.showModal();
  const first = $('input[type=text],textarea', f); if (first) first.focus();
}
function hire(emp) {
  const e = emp || {};
  const hasRepo = !!S.settings.gameRepo;
  dialog(`<h2>${emp ? '직원 고치기' : '직원 뽑기'}</h2>
    <div class="field"><label>이름</label><input type="text" name="name" value="${esc(e.name || '')}" placeholder="예) 팀장, 몬스터, 모션"></div>
    <div class="field"><label>맡은 일</label><input type="text" name="role" value="${esc(e.role || '')}" placeholder="예) 몹·보스 만들기와 몹 점검"><div class="help">다른 직원들이 이걸 보고 누구에게 일을 넘길지 정해요.</div></div>
    <div class="field"><label>일하는 폴더</label>
      ${emp ? '' : `<label class="radio"><input type="radio" name="where" value="auto" ${hasRepo ? 'checked' : 'disabled'}> <span>자동으로 만들기 — 게임 원본에서 이 직원 전용 작업 공간을 따로 만들어요 (직원끼리 파일이 안 엉켜요)${hasRepo ? '' : '<br><span class="muted small">먼저 설정에서 「게임 원본 폴더」를 정해 주세요.</span>'}</span></label>`}
      <label class="radio"><input type="radio" name="where" value="manual" ${emp || !hasRepo ? 'checked' : ''}> <span>직접 적기</span></label>
      <input type="text" name="folder" value="${esc(e.folder || '')}" placeholder="예) C:\\Users\\사장님\\thor-like-game"></div>
    <div class="field"><label class="radio"><input type="checkbox" name="partner" ${e.partner ? 'checked' : ''}> <span><b>AI협력팀</b> — 그록 등 다른 AI와 일하는 직원 (그록 터널·그록 폴더를 맡아요)</span></label></div>
    <div class="field"><label>허락 방식</label><select name="mode">${Object.entries(MODES).map(([k, v]) => `<option value="${k}" ${k === (e.mode || '') ? 'selected' : ''}>${v}</option>`).join('')}</select>
      <div class="help">어떤 방식이든 「항상 허락」한 일은 다시 안 물어요.</div></div>
    <div class="field"><label>모델 (비워 두면 기본)</label><input type="text" name="model" value="${esc(e.model || '')}" placeholder="예) opus, sonnet"></div>
    <div class="err-text"></div>
    <div class="dlg-foot">${emp ? `<button class="btn danger" value="delete" style="margin-right:auto">내보내기</button>` : ''}<button class="btn ghost" value="cancel">닫기</button><button class="btn" value="ok">${emp ? '저장' : '뽑기'}</button></div>`,
  async (fd, v) => {
    if (v === 'delete') { if (!confirm(`${e.name} 직원을 내보낼까요? (폴더와 파일은 그대로 남아요)`)) return '취소함'; await api('/api/employee/delete', { id: e.id }); return; }
    const r = await api('/api/employee', { id: e.id, name: fd.name, role: fd.role, folder: fd.where === 'auto' ? '' : fd.folder, autoFolder: fd.where === 'auto', mode: fd.mode, model: fd.model, partner: !!fd.partner });
    return r.ok ? null : r.error;
  });
}
async function makeTeam() {
  if (!S.settings.gameRepo) { alert('먼저 설정에서 「게임 원본 폴더」를 정해 주세요.'); return settings(); }
  $('#emps').innerHTML = '<div class="empty">직원 자리(작업 공간)를 만드는 중… 처음엔 1~2분 걸려요.</div>';
  const r = await api('/api/team');
  if (!r.ok) alert(r.error);
}
function settings() {
  const s = S.settings;
  dialog(`<h2>설정</h2>
    <div class="field"><label>게임 원본 폴더</label><input type="text" name="gameRepo" value="${esc(s.gameRepo)}" placeholder="예) C:\\Users\\사장님\\thor-like-game"><div class="help">git 으로 받아 둔 게임 폴더. 새 직원을 뽑을 때 여기서 직원 전용 작업 공간을 만들어요.</div></div>
    <div class="field"><label>직원 작업 공간을 둘 곳 (비워 두면 원본 옆 「…_직원」 폴더)</label><input type="text" name="workspace" value="${esc(s.workspace)}"></div>
    <div class="field"><label>그록 키 (xAI) — 그록 실시간 터널</label><input type="password" name="xaiKey" placeholder="${s.hasXaiKey ? '들어 있음 (바꿀 때만 새로 넣기)' : 'xai- 로 시작하는 키'}" autocomplete="off">
      <div class="help">console.x.ai 에서 만든 키. 이 PC에만 저장되고 AI협력팀에게만 주어져요. 쓴 만큼 돈이 나가요 (그림 1장 약 $0.04, 영상 1초 약 $0.08).${s.hasXaiKey ? ' <label><input type="checkbox" name="xaiKeyClear"> 키 지우기</label>' : ''}</div></div>
    <div class="field"><label>그록 하루 한도 (달러)</label><input type="text" name="grokBudget" value="${esc(s.grokBudget)}"><div class="help">이만큼 쓰면 그록 터널이 그날은 멈춰요. 오늘 쓴 돈: $${(s.grokSpent || 0).toFixed(2)}</div></div>
    <div class="field"><label>그록 폴더 (PC에 동기화된 구글 드라이브 폴더)</label><input type="text" name="grokDir" value="${esc(s.grokDir)}" placeholder="예) G:\\내 드라이브\\그록 할 일 (필멸자)\\★ 그록 부탁 (10-31)…"><div class="help">「Google Drive 데스크톱」을 깔면 드라이브 폴더가 PC 폴더로 보여요. 여기에 새 파일이 오면 AI협력팀이 저절로 확인하고 보고해요.</div></div>
    <div class="field"><label>회사 기본 허락 방식</label><select name="defaultMode">${Object.entries(MODES).filter(([k]) => k).map(([k, v]) => `<option value="${k}" ${k === s.defaultMode ? 'selected' : ''}>${v}</option>`).join('')}</select>
      <div class="help">추천: 「알아서」. 안전한 일은 묻지 않고, 애매한 것만 위에 「허락 요청」으로 떠요. 한 번 「항상 허락」하면 다시 안 물어요.</div></div>
    <div class="field"><label>직원끼리 말이 오갈 수 있는 최대 횟수</label><input type="text" name="maxHops" value="${esc(s.maxHops)}"><div class="help">직원끼리 끝없이 말을 주고받지 않게 막는 숫자예요.</div></div>
    <div class="field"><label>클로드 코드 명령</label><input type="text" name="claudeCmd" value="${esc(s.claudeCmd)}"><div class="help">보통 그대로 두면 돼요. 지금: ${S.claude.ok ? '찾음 ' + esc(S.claude.version) : '<b style="color:var(--red)">못 찾음</b>'}</div></div>
    <div class="err-text"></div>
    <div class="dlg-foot"><button class="btn ghost" value="quit" style="margin-right:auto">회사 문 닫기(끄기)</button><button class="btn ghost" value="cancel">닫기</button><button class="btn" value="ok">저장</button></div>`,
  async (fd, v) => {
    if (v === 'quit') { if (confirm('클로드 회사를 끌까요? 일하던 직원도 멈춰요.')) { await api('/api/quit'); document.body.innerHTML = '<div class="empty">회사 문을 닫았어요. 이 창을 닫아도 돼요.</div>'; } return; }
    const r = await api('/api/settings', { ...fd, xaiKeyClear: !!fd.xaiKeyClear }); return r.ok ? null : r.error;
  });
}
function rules() {
  const draw = () => `<h2>허락 목록</h2><p class="muted small">여기 있는 일은 모든 직원이 묻지 않고 해요. ✕ 를 누르면 다시 물어봐요.</p>
    <div class="rules">${S.rules.map((r, i) => `<span>${esc(r)} <button value="del:${i}" title="빼기">✕</button></span>`).join('')}</div>
    <div class="field" style="margin-top:12px"><label>직접 더하기</label><input type="text" name="add" placeholder="예) Bash(python3:*)  또는  WebFetch(domain:github.com)"></div>
    <div class="dlg-foot"><button class="btn ghost" value="cancel">닫기</button><button class="btn" value="add">더하기</button></div>`;
  dialog(draw(), async (fd, v) => {
    let list = S.rules.slice();
    if (v.startsWith('del:')) list.splice(Number(v.slice(4)), 1);
    else if (v === 'add' && fd.add && fd.add.trim()) list.push(fd.add.trim());
    await api('/api/rules', { rules: list }); S.rules = list; $('#dlgForm').innerHTML = draw(); return '';
  });
}
async function showLog(id) {
  const e = S.employees.find((x) => x.id === id); if (!e) return;
  const lines = await fetch('/api/log?id=' + id).then((r) => r.json());
  const K = { order: '▶ 일 받음', tool: '·', say: '💬', done: '✅ 보고', sys: '⚙' };
  const fmt = (l) => `<div class="k-${l.kind}">${new Date(l.t).toLocaleTimeString('ko-KR')} ${K[l.kind] || ''} ${esc(l.text)}</div>`;
  dialog(`<h2>${esc(e.name)} — 작업 보기</h2><div class="log" id="logBox">${lines.map(fmt).join('') || '<span class="muted">아직 기록이 없어요.</span>'}</div><div class="dlg-foot"><button class="btn ghost" value="cancel">닫기</button></div>`);
  const box = $('#logBox'); box.scrollTop = box.scrollHeight; box.dataset.emp = id; box._fmt = fmt;
}
function more(id) {
  const e = S.employees.find((x) => x.id === id); if (!e) return;
  dialog(`<h2>${esc(e.name)}</h2>
    <div class="dlg-foot" style="justify-content:flex-start;flex-wrap:wrap">
      <button class="btn ghost" value="edit">고치기 · 내보내기</button>
      <button class="btn ghost" value="open">일하는 폴더 열기</button>
      <button class="btn ghost" value="new">새 대화로 시작</button>
      <button class="btn ghost" value="clear">대기 중인 일 비우기</button>
      <button class="btn ghost" value="cancel" style="margin-left:auto">닫기</button></div>
    <p class="muted small">「새 대화로 시작」: 이 직원이 지금까지 나눈 이야기를 잊고 새로 시작해요. 대화가 너무 길어져 느려졌을 때 써요.</p>`,
  async (fd, v) => {
    if (v === 'edit') { setTimeout(() => hire(e), 50); return; }
    if (v === 'open') await api('/api/open', { id });
    if (v === 'new') await api('/api/newChat', { id });
    if (v === 'clear') await api('/api/stop', { id, clear: true });
  });
}

// ───── 알림 ─────
let audio;
function ding() {
  try { audio = audio || new AudioContext(); const o = audio.createOscillator(), g = audio.createGain(); o.frequency.value = 880; g.gain.setValueAtTime(0.15, audio.currentTime); g.gain.exponentialRampToValueAtTime(0.001, audio.currentTime + 0.35); o.connect(g).connect(audio.destination); o.start(); o.stop(audio.currentTime + 0.35); } catch (e) { /* */ }
}
function notify(title, body) {
  ding();
  if (document.hasFocus()) return;
  if ('Notification' in window && Notification.permission === 'granted') new Notification(title, { body, icon: '/ui/icon.png' });
}

// ───── 이벤트 ─────
document.addEventListener('click', async (ev) => {
  const t = ev.target.closest('[data-act],[data-ans]'); if (!t) return;
  if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission();
  if (t.dataset.ans) return api('/api/perm/answer', { id: t.dataset.id, answer: t.dataset.ans });
  const id = t.dataset.id, a = t.dataset.act;
  if (a === 'give') { $('#orderTo').value = id; $('#orderText').focus(); }
  if (a === 'log') showLog(id);
  if (a === 'stop') api('/api/stop', { id });
  if (a === 'more') more(id);
  if (a === 'read') api('/api/report/read', { id });
  if (a === 'delrep') api('/api/report/delete', { id });
  if (a === 'openfile') api('/api/openFile', { r: id, i: 0 });
  if (a === 'task') { openTasks.has(id) ? openTasks.delete(id) : openTasks.add(id); t.classList.toggle('open'); }
  if (a === 'more-text') { t.previousElementSibling.classList.remove('clamp'); t.remove(); }
  if (a === 'zoom') { const z = document.createElement('div'); z.className = 'zoom'; z.innerHTML = `<img src="${t.src}">`; z.onclick = () => z.remove(); document.body.append(z); }
  if (a === 'copy' || a === 'copyall') {
    const r = S.reports.find((x) => x.id === id); if (!r) return;
    const m = r.text.match(/```[\w-]*\n?([\s\S]*?)```/);
    await navigator.clipboard.writeText(a === 'copy' && m ? m[1].trim() : r.text);
    t.textContent = '복사됨 ✓'; setTimeout(() => (t.textContent = a === 'copy' ? '붙여넣기 글 복사' : '복사'), 1500);
  }
  if (a === 'reply') {
    const r = S.reports.find((x) => x.id === id); if (!r) return;
    $('#orderTo').value = r.emp; $('#orderText').value = ''; $('#orderText').placeholder = `${r.empName}에게 답하기…`; $('#orderText').focus();
    api('/api/report/read', { id });
  }
});
$('#orderBox').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const text = $('#orderText').value.trim(), to = $('#orderTo').value;
  if (!text || !to) return;
  const r = await api('/api/order', { to, text });
  if (r.ok) { $('#orderText').value = ''; $('#orderText').placeholder = '할 일을 적어 주세요. (Ctrl+Enter 로 보내기)'; }
});
$('#orderText').addEventListener('keydown', (ev) => { if (ev.key === 'Enter' && (ev.ctrlKey || ev.metaKey)) $('#orderBox').requestSubmit(); });
$('#tabs').addEventListener('click', (ev) => { const b = ev.target.closest('button'); if (!b) return; filter = b.dataset.f; $('#tabs').querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b)); renderReports(); });
$('#filterEmp').addEventListener('change', (ev) => { filterEmp = ev.target.value; renderReports(); });
$('#btnReadAll').onclick = () => api('/api/report/read', { all: true });
$('#btnHire').onclick = () => hire();
$('#btnFolder').onclick = async () => { const r = await api('/api/grokCheck'); if (!r.ok) alert(r.error); };
$('#btnSettings').onclick = settings;
$('#btnRules').onclick = rules;
$('#btnStopAll').onclick = () => { if (confirm('모든 직원의 일을 멈추고 대기 중인 일도 비울까요?')) api('/api/stopAll'); };
document.addEventListener('pause', () => { const b = $('#reports'); if (b.dataset.dirty) renderReports(); }, true);
setInterval(() => { if (S.employees.some((e) => e.status === 'working')) renderEmps(); }, 30000);

// ───── 실시간 연결 ─────
function connect() {
  const es = new EventSource('/api/events');
  let first = true;
  es.addEventListener('state', (ev) => {
    const old = S; S = JSON.parse(ev.data); render();
    if (!first) {
      const oldAsk = new Set(old.pending.map((p) => p.id));
      for (const p of S.pending) if (!oldAsk.has(p.id)) notify('허락 요청', `${p.empName}: ${p.label}`);
      const oldRep = new Set(old.reports.map((r) => r.id));
      for (const r of S.reports) if (!oldRep.has(r.id) && (r.from === '사장님' || r.needBoss)) notify(`${r.empName} 보고`, r.text.slice(0, 120));
    }
    first = false;
  });
  es.addEventListener('log', (ev) => {
    const box = $('#logBox'); if (!box || !$('#dlg').open) return;
    const d = JSON.parse(ev.data); if (d.emp !== box.dataset.emp) return;
    const stick = box.scrollTop + box.clientHeight > box.scrollHeight - 30;
    box.insertAdjacentHTML('beforeend', box._fmt(d.line)); if (stick) box.scrollTop = box.scrollHeight;
  });
  es.addEventListener('grok', () => { if (filter === 'grok') renderGrok(); });
  es.onerror = () => { $('#summary').innerHTML = '<span class="chip err">회사 본체와 연결이 끊겼어요. 다시 잇는 중…</span>'; };
}
connect();
