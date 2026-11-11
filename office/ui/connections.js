// 연결·기능 화면. 홈에는 단추만 있고, 이 파일이 화면을 그려요.
// 색은 theme.css 이름만. 움직임·네온 없음. 열쇠·주소 값은 그리지 않아요.
'use strict';
let linksTab = 'conn';
let linksSel = '';
let linksPack = null;
let linksBusy = '';
let linksErr = '';

function linksEsc(s) {
  const A = window.Aldeul;
  if (A && A.esc) return A.esc(s);
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function linksRoot() {
  let el = document.getElementById('links');
  if (el) return el;
  const home = document.getElementById('view-home');
  el = document.createElement('div');
  el.id = 'links';
  el.hidden = true;
  if (home) home.appendChild(el);
  else document.body.appendChild(el);
  return el;
}
function linksToast(text) {
  const A = window.Aldeul;
  if (A && A.toast) A.toast(text);
}
function linksOpen() {
  const home = document.getElementById('home');
  const box = linksRoot();
  if (home) home.hidden = true;
  box.hidden = false;
  linksLoad();
}
function linksClose() {
  const home = document.getElementById('home');
  const box = document.getElementById('links');
  if (box) box.hidden = true;
  if (home) home.hidden = false;
}
async function linksLoad() {
  linksErr = '';
  linksPaint();
  try {
    const r = await fetch('/api/connections', { cache: 'no-store' });
    const data = await r.json();
    linksPack = data && typeof data === 'object' ? data : null;
    if (!linksPack || !Array.isArray(linksPack.connections)) linksErr = '연결 목록을 못 읽었어요.';
  } catch (e) {
    linksErr = '회사 프로그램이 켜져 있는지 봐 주세요.';
  }
  if (!linksSel && linksPack && linksPack.connections && linksPack.connections[0]) linksSel = linksPack.connections[0].id;
  linksPaint();
}
function linksGoTitle(kind) {
  if (kind === 'dialog') return '맨 위 연결 창을 열어요. 주소와 열쇠는 그 창에만 있고, 여기에는 안 나와요.';
  if (kind === 'none') return '그록 봇이 관리해요. 이 화면에서는 켜지지 않아요.';
  return '이 컴퓨터에서 지금 상태를 살펴봐요.';
}
function linksPaint() {
  const box = document.getElementById('links');
  if (!box || box.hidden) return;
  const list = box.querySelector('.links-list');
  const detail = box.querySelector('.links-detail');
  const feat = box.querySelector('.links-body.mode-feat');
  const scroll = {
    list: list ? list.scrollTop : 0,
    detail: detail ? detail.scrollTop : 0,
    feat: feat ? feat.scrollTop : 0,
  };
  const esc = linksEsc;
  const conns = (linksPack && linksPack.connections) || [];
  const feats = (linksPack && linksPack.features) || [];
  const legend = (linksPack && linksPack.legend) || '초록은 직접 확인한 것만, 회색은 확인 안 된 것이에요.';
  let body = '';
  if (linksErr && !conns.length) {
    body = `<div class="card">${esc(linksErr)}</div>`;
  } else if (linksTab === 'feat') {
    let screen = '';
    const cards = feats.map((f) => {
      const head = f.screen !== screen ? `<div class="title links-feat-screen">${esc(f.screen)}</div>` : '';
      screen = f.screen;
      return `${head}<article class="card links-feat"><b>${esc(f.name)}</b><div>${esc(f.what)}</div><div class="muted small">언제: ${esc(f.when)}</div></article>`;
    }).join('');
    body = `<div class="links-body mode-feat"><div class="links-feats">${cards || '<div class="card">설명이 없어요.</div>'}</div></div>`;
  } else {
    let group = '';
    const cards = conns.map((c) => {
      const head = c.group !== group ? `<div class="links-group">${esc(c.group)}</div>` : '';
      group = c.group;
      const st = c.state === 'on' || c.state === 'off' ? c.state : 'unknown';
      const sel = c.id === linksSel ? ' sel' : '';
      const busy = linksBusy === c.id;
      return `${head}<div class="links-card${sel}" data-links="pick" data-id="${esc(c.id)}" tabindex="0">
        <div class="links-card-top"><span class="ico">${esc(c.icon || '🔗')}</span><span class="nm">${esc(c.name)}</span><span class="links-status ${st}"><i class="links-dot ${st}"></i>${esc(c.label || '')}</span></div>
        <div class="links-line">${esc(c.line || '')}</div>
        <div class="links-actions">
          <button type="button" class="btn small" data-links="go" data-id="${esc(c.id)}" title="${esc(linksGoTitle(c.connect))}">${busy ? '확인 중…' : '연결'}</button>
          <button type="button" class="btn ghost small" data-links="recheck" data-id="${esc(c.id)}" title="지금 상태를 다시 살펴봐요. 직접 확인한 것만 초록이 돼요.">${busy ? '확인 중…' : '다시 확인'}</button>
        </div>
      </div>`;
    }).join('');
    const cur = conns.find((c) => c.id === linksSel);
    const steps = cur && cur.steps && cur.steps.length ? `<ol class="links-steps">${cur.steps.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>` : '<p class="muted">순서가 없어요.</p>';
    const people = cur && cur.people && cur.people.length ? `<ul class="links-people">${cur.people.map((p) => `<li><b>${esc(p.name)}</b>${p.dept ? ' · ' + esc(p.dept) : ''} — <span class="${p.ok ? 'ok' : 'no'}">${p.ok ? '폴더 있음' : '폴더 없음'}</span></li>`).join('')}</ul>` : '';
    const right = cur ? `<div class="card links-detail">
        <div class="conn-head"><span class="ico">${esc(cur.icon || '🔗')}</span><div><b>${esc(cur.name)}</b><div class="links-status ${cur.state === 'on' || cur.state === 'off' ? cur.state : 'unknown'}"><i class="links-dot ${cur.state === 'on' || cur.state === 'off' ? cur.state : 'unknown'}"></i>${esc(cur.label || '')}</div></div></div>
        <div class="qa"><div class="qh">이걸로 무엇을 하나요?</div>${esc(cur.line || '')}</div>
        <div class="qa"><div class="qh">지금 상태</div>${esc(cur.detail || '')}${people}</div>
        <div class="qa"><div class="qh">연결하는 방법</div>${steps}</div>
      </div>` : `<div class="card links-detail"><b>왼쪽에서 하나를 누르세요</b><p class="muted">이름, 하는 일, 상태, 켜는 순서가 여기에 나와요.</p></div>`;
    body = `<div class="links-body mode-conn"><div class="links-list">${cards || '<div class="card">연결 목록이 없어요.</div>'}</div>${right}</div>`;
  }
  box.innerHTML = `<div class="links-bar">
      <button type="button" class="btn ghost" data-links="close" title="회사 홈으로 돌아가요">← 회사 홈</button>
      <div class="title">🔌 연결·기능</div>
    </div>
    <div class="links-legend">${esc(legend)}${linksErr ? ' · ' + esc(linksErr) : ''}</div>
    <div class="links-tabs">
      <button type="button" class="btn ${linksTab === 'conn' ? '' : 'ghost'}" data-links="tab" data-tab="conn" title="이어진 것들을 보고, 켜는 방법을 봐요">연결 목록</button>
      <button type="button" class="btn ${linksTab === 'feat' ? '' : 'ghost'}" data-links="tab" data-tab="feat" title="화면과 단추가 무엇을 하는지 봐요">기능 안내</button>
    </div>
    ${body}`;
  const listNow = box.querySelector('.links-list');
  const detailNow = box.querySelector('.links-detail');
  const featNow = box.querySelector('.links-body.mode-feat');
  if (listNow) listNow.scrollTop = scroll.list;
  if (detailNow) detailNow.scrollTop = scroll.detail;
  if (featNow) featNow.scrollTop = scroll.feat;
}
async function linksRecheck(id) {
  if (!id || linksBusy) return;
  linksBusy = id;
  linksSel = id;
  linksPaint();
  let r = null;
  try {
    const res = await fetch('/api/connections/check', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ id }) });
    r = await res.json();
  } catch (e) {
    r = { ok: false, error: '다시 확인하지 못했어요.' };
  }
  linksBusy = '';
  if (!r || !r.ok || !r.item) {
    linksToast((r && r.error) || '다시 확인하지 못했어요.');
    linksPaint();
    return;
  }
  if (linksPack && Array.isArray(linksPack.connections)) {
    const i = linksPack.connections.findIndex((c) => c.id === id);
    if (i >= 0) linksPack.connections[i] = r.item;
  }
  linksPaint();
}
function linksGo(id) {
  const conns = (linksPack && linksPack.connections) || [];
  const c = conns.find((x) => x.id === id);
  linksSel = id;
  if (!c || c.connect === 'none') {
    linksToast('그록 봇이 관리해요. 이 화면에서는 켜거나 끄지 못해요.');
    linksPaint();
    return;
  }
  if (c.connect === 'dialog') {
    const A = window.Aldeul;
    linksPaint();
    if (A && A.openConnections) A.openConnections();
    else linksToast('맨 위 「연결」 단추를 눌러 주세요.');
    return;
  }
  linksRecheck(id);
}

const LINKS_TITLES = [
  ['#homeTopSend button[type="submit"]', '고른 부서에 할 일을 보내요'],
  ['#homeTopDept', '일을 받을 부서를 골라요'],
  ['#homeTopCmd', '할 일을 적고 엔터를 눌러요. 예: 오늘 할 일 정리해서 보고해'],
  ['[data-home="dept"]', '이 부서 화면을 열어요'],
  ['[data-home="workshop"]', '게임 일을 하는 클로드 직원 화면을 열어요'],
  ['[data-home="conn"]', '이어진 것을 쉬운 말로 봐요'],
  ['[data-links="open"]', '이어진 것과, 단추마다 하는 일을 봐요'],
  ['[data-home="team"]', '없는 클로드 직원을 한 번에 만들어요. 누르기 전에는 만들지 않아요'],
  ['[data-home="back"]', '회사 홈으로 돌아가요'],
  ['[data-home="makedept"]', '이 부서에 없는 클로드 직원을 만들어요'],
  ['#homeDeptFolder', '직원 자리를 만들 폴더를 적어요. 비우면 게임 폴더 옆에 만들어요'],
  ['#homeCmd', '이 부서에 시킬 일을 적어요'],
  ['#homeSend button[type="submit"]', '이 부서에 할 일을 보내요'],
  ['[data-home="connone"]', '이 연결이 무엇인지 봐요'],
  ['.home-col-chat > .title [data-act="coopall"]', '클로드와 그록이 나눈 말을 더 봐요'],
  ['#btnHire', '클로드 직원을 한 명 더 뽑아요. 새 역할이 필요할 때 써요'],
  ['[data-reportdept="전체"]', '모든 부서 보고를 봐요'],
  ['[data-reportdept="게임 필멸자"]', '게임 부서 보고만 봐요'],
  ['[data-reportdept="제로폰"]', '제로폰 보고만 봐요'],
  ['[data-reportdept="홍보"]', '홍보 부서 보고만 봐요'],
  ['[data-reportdept="경영지원"]', '경영지원 보고만 봐요'],
  ['[data-reportdept="STCO"]', 'STCO 보고만 봐요'],
  ['[data-reportdept="영상 기획팀"]', '영상 기획팀 보고만 봐요'],
  ['[data-reportdept="AI 협력·연결"]', 'AI 협력 보고만 봐요'],
];
function linksApplyTitles() {
  const home = document.getElementById('home');
  LINKS_TITLES.forEach((pair) => {
    const sel = pair[0];
    const tip = pair[1];
    const nodes = sel === '#btnHire' ? [document.getElementById('btnHire')] : (home ? home.querySelectorAll(sel) : []);
    Array.prototype.forEach.call(nodes, (el) => {
      if (el && !el.getAttribute('title')) el.setAttribute('title', tip);
    });
  });
}
function linksBoot() {
  const home = document.getElementById('home');
  if (home) new MutationObserver(() => linksApplyTitles()).observe(home, { childList: true, subtree: true });
  linksApplyTitles();
  document.addEventListener('click', (ev) => {
    const start = ev.target && ev.target.closest ? ev.target : (ev.target && ev.target.parentElement);
    if (!start || !start.closest) return;
    const open = start.closest('[data-links="open"]');
    if (open) { linksOpen(); return; }
    const box = document.getElementById('links');
    if (!box || box.hidden) return;
    const t = start.closest('[data-links]');
    if (!t || !box.contains(t)) return;
    const act = t.getAttribute('data-links');
    if (act === 'close') { linksClose(); return; }
    if (act === 'tab') { linksTab = t.getAttribute('data-tab') === 'feat' ? 'feat' : 'conn'; linksPaint(); return; }
    if (act === 'pick') { linksSel = t.getAttribute('data-id') || linksSel; linksPaint(); return; }
    if (act === 'go') { linksGo(t.getAttribute('data-id') || ''); return; }
    if (act === 'recheck') { linksRecheck(t.getAttribute('data-id') || ''); }
  });
  document.addEventListener('keydown', (ev) => {
    if (ev.key !== 'Enter') return;
    const box = document.getElementById('links');
    if (!box || box.hidden) return;
    const card = ev.target.closest && ev.target.closest('[data-links="pick"]');
    if (!card || !box.contains(card)) return;
    linksSel = card.getAttribute('data-id') || linksSel;
    linksPaint();
  });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', linksBoot);
else linksBoot();
