// 보고 창. home.js 에서 renderReports(el) 또는 renderReports(el, { dept, title }) 로 불러요.
// 목록은 /api/company/reports 의 { items, depts } 를 읽어요. 부서 이름은 서버 목록을 그대로 써요.
// 색은 theme.css 이름만 써요.
'use strict';
let reportDept = '전체';
let reportPack = null;
let reportAt = 0;
let reportFlight = null;
const reportOpen = new Set();
const reportLogOpen = new Set();

function reportEsc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function reportInDept(r, name) {
  if (!name || name === '전체') return true;
  if (!r) return false;
  if (r.dept === name) return true;
  if (!r.dept && (r.target === name || r.target === String(name).split('·')[0])) return true;
  return false;
}
function reportDepts(pack) {
  const fromServer = pack && Array.isArray(pack.depts) ? pack.depts.filter((d) => d && d.name) : [];
  if (fromServer.length) return fromServer;
  const names = [];
  for (const r of (pack && pack.items) || []) {
    const n = r && (r.dept || r.target);
    if (n && names.indexOf(n) < 0) names.push(n);
  }
  return names.map((name) => ({ id: name, name, icon: '🏢' }));
}
function reportMs(time) {
  const s = String(time || '').trim();
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}/.test(s)) {
    const ms = Date.parse(s.slice(0, 16).replace(' ', 'T') + ':00+09:00');
    if (!Number.isNaN(ms)) return ms;
  }
  const ms = Date.parse(s);
  return Number.isNaN(ms) ? 0 : ms;
}
function reportRank(r) {
  if (!r) return 5;
  if (r.needBoss || r.stage === '사장님 확인 필요') return 2;
  if (r.status === '진행 중') return 0;
  if (r.status === '문제 있음') return 1;
  if (r.silent || r.status === '접수') return 3;
  if (r.status === '완료') return 4;
  return 5;
}
function reportSort(a, b) {
  const d = reportRank(a) - reportRank(b);
  if (d) return d;
  return reportMs(b.updated || b.time) - reportMs(a.updated || a.time);
}
function reportVisual(r) {
  if (r && r.silent) return '응답 없음';
  if (r && (r.stage === '사장님 확인 필요' || (r.needBoss && r.status !== '완료'))) return '사장님 확인 필요';
  if (r && (r.status === '완료' || r.status === '문제 있음' || r.status === '접수' || r.status === '진행 중')) return r.status;
  return (r && r.status) || '';
}
function reportLabel(r) {
  if (r && r.silent) return '응답 없음 — 그록이 아직 안 받음';
  if (r && r.stage) return r.stage;
  return (r && r.status) || '';
}
function reportIsLive() {
  const items = (reportPack && reportPack.items) || [];
  return items.some((r) => r && (r.status === '진행 중' || r.needBoss || (r.status === '접수' && !r.silent)));
}
function reportLogHtml(r) {
  const id = (r && (r.cmdId || r.id)) || '';
  const open = reportLogOpen.has(id) ? ' open' : '';
  const hist = r && Array.isArray(r.history) ? r.history : [];
  const rows = hist.map((h) => {
    const notes = (Array.isArray(h.notes) ? h.notes : []).map((n) => '<div>' + reportEsc(n) + '</div>').join('');
    return '<li><time>' + reportEsc(h.time || '') + '</time> <b>' + reportEsc(h.stage || '') + '</b>' + notes + '</li>';
  }).join('');
  const body = rows || '<li class="muted">아직 진행 기록이 없어요.</li>';
  return '<details class="cmd-fold" data-cmd="' + reportEsc(id) + '"' + open + '><summary>' + reportEsc((r && r.command) || '명령') + '</summary><div class="cmd-log"><b>진행 기록</b><ol>' + body + '</ol></div></details>';
}
function reportShown(items, lockDept) {
  const all = Array.isArray(items) ? items : [];
  const name = lockDept || reportDept;
  if (!name || name === '전체') return all;
  return all.filter((r) => reportInDept(r, name));
}
function loadReportPack() {
  if (reportFlight) return reportFlight;
  reportFlight = (async () => {
    try {
      const r = await fetch('/api/company/reports', { cache: 'no-store' });
      const data = await r.json();
      return data && typeof data === 'object' ? data : { items: [] };
    } catch (e) {
      return null;
    }
  })();
  reportFlight.finally(() => { reportFlight = null; });
  return reportFlight;
}
function reportArtHtml(r) {
  const list = Array.isArray(r.artifacts) ? r.artifacts : [];
  if (!reportOpen.has(r.id || '')) {
    return '';
  }
  if (!list.length) return '<div class="art-box muted small">아직 결과물이 없어요.</div>';
  const bits = list.map((a) => {
    if (!a || typeof a !== 'object') return '';
    if (a.kind === 'photo') {
      const src = a.src || a.url || '';
      if (!src) return `<div class="art-file">🖼 ${reportEsc(a.name || '사진')}</div>`;
      return `<figure class="art-photo"><img src="${reportEsc(src)}" alt="${reportEsc(a.name || '사진')}"><figcaption>${reportEsc(a.name || '사진')}</figcaption></figure>`;
    }
    if (a.kind === 'file') {
      const where = a.path || a.name || '파일';
      return `<button type="button" class="art-file" data-art-open="1" data-id="${reportEsc(r.id || '')}" data-a="${reportEsc(a.i)}">📄 ${reportEsc(where)}</button>`;
    }
    if (a.kind === 'link') {
      const url = String(a.url || '');
      if (!/^https?:\/\//i.test(url)) return '';
      return `<a class="art-link" href="${reportEsc(url)}" target="_blank" rel="noopener noreferrer">🔗 ${reportEsc(a.name || '링크')}</a>`;
    }
    if (a.kind === 'text' && a.text) return `<div class="art-text">📝 ${reportEsc(a.text)}</div>`;
    return '';
  }).join('');
  return `<div class="art-box">${bits}</div>`;
}
function reportHtml(pack, opt) {
  const lockDept = opt && opt.dept ? String(opt.dept) : '';
  const title = (opt && opt.title) || '📋 보고 창';
  if (!pack) {
    return `<div class="card home-report-panel"><div class="home-report-head"><b>${reportEsc(title)}</b><div class="muted small">보고를 불러오는 중…</div></div></div>`;
  }
  const list = Array.isArray(pack.items) ? pack.items : [];
  const shown = reportShown(list, lockDept).slice().sort(reportSort);
  const n = (st) => shown.filter((r) => r.status === st).length;
  const depts = reportDepts(pack);
  if (!lockDept && reportDept !== '전체' && !depts.some((d) => d.name === reportDept)) reportDept = '전체';
  const buttons = lockDept ? '' : ['전체'].concat(depts.map((d) => d.name)).map((name) => {
    const d = depts.find((x) => x.name === name);
    const label = name === '전체' ? '전체' : ((d && d.icon) ? d.icon + ' ' : '') + name;
    const tip = name === '전체' ? '모든 부서 보고를 봐요' : (name + ' 보고만 봐요');
    const on = reportDept === name ? ' on' : '';
    return `<button type="button" class="${on.trim()}" data-reportdept="${reportEsc(name)}" title="${reportEsc(tip)}">${reportEsc(label)}</button>`;
  }).join('');
  const cards = shown.map((r) => {
    const who = r.lead ? ` · ${(r.status === '완료' || r.status === '문제 있음') ? '검수' : '담당'}: ${reportEsc(r.lead)}` : '';
    const lines = (Array.isArray(r.summary) ? r.summary : []).map((s) => reportEsc(s)).join('<br>');
    const arts = Array.isArray(r.artifacts) ? r.artifacts.length : 0;
    const open = reportOpen.has(r.id || '');
    const id = r.id || '';
    const when = r.updated ? ('바뀜 ' + r.updated) : (r.time || '');
    return `<article class="card home-report-card" data-status="${reportEsc(reportVisual(r))}" data-report-toggle="1" data-report-id="${reportEsc(id)}">
      <div class="card-head">
        <span class="st-lamp${r.status === '완료' && !r.silent ? ' on' : ''}"></span>
        <b>${reportEsc(r.dept || r.target || '부서 없음')}</b>
        <span class="rst">${reportEsc(reportLabel(r))}</span>
        ${r.needBoss && r.stage !== '사장님 확인 필요' ? '<span class="boss">사장님 확인 필요</span>' : ''}
        <time>${reportEsc(when)}</time>
      </div>
      ${reportLogHtml(r)}
      <div class="who">올린 쪽: ${reportEsc(r.source || '그록')}${who}${arts ? ' · 결과물 ' + arts + '개' : ''}${open ? '' : ' · 누르면 결과물'}</div>
      <div class="sum">${lines}</div>
      ${reportArtHtml(r)}
    </article>`;
  }).join('');
  const emptyText = (lockDept || reportDept !== '전체') ? '이 부서에는 아직 보고가 없어요.' : '아직 올라온 보고가 없어요.';
  const empty = shown.length ? '' : `<div class="home-report-empty">${emptyText}${pack.error ? `<span class="small">${reportEsc(pack.error)}</span>` : '<span class="small">일을 보내면 여기에 접수로 떠요.</span>'}</div>`;
  const hint = lockDept ? '이 부서만. 진행 중인 일부터 보여요. 명령을 누르면 진행 기록. 초록 불은 끝났을 때만.' : '진행 중인 일부터 보여요. 명령을 누르면 진행 기록. 초록 불은 끝났을 때만.';
  return `<div class="card home-report-panel">
      <div class="home-report-head">
        <div class="home-report-title"><b>${reportEsc(title)}</b><span class="muted small">${hint}</span></div>
        <div class="home-report-counts">접수 ${n('접수')} · 진행 중 ${n('진행 중')} · 완료 ${n('완료')} · 문제 ${n('문제 있음')}</div>
        ${buttons ? `<div class="home-report-filters">${buttons}</div>` : ''}
      </div>
      <div class="home-report-list">${cards}${empty}</div>
    </div>`;
}
function reportOpt(el) {
  const dept = el && el.dataset ? (el.dataset.lockDept || '') : '';
  const title = el && el.dataset ? (el.dataset.reportTitle || '') : '';
  return { dept, title };
}
const reportDrawn = new WeakMap();
function reportPaint(el) {
  if (!el) return;
  if (typeof homeUserScrolling === 'function' && homeUserScrolling()) {
    el.dataset.reportDirty = '1';
    return;
  }
  delete el.dataset.reportDirty;
  const html = reportHtml(reportPack, reportOpt(el));
  if (reportDrawn.get(el) === html) return;
  const list = el.querySelector('.home-report-list');
  let top = 0;
  let height = 0;
  let atTop = true;
  if (list) {
    top = list.scrollTop;
    height = list.scrollHeight;
    atTop = top < 8;
  } else if (window.homeReportScroll) {
    top = window.homeReportScroll.top;
    height = window.homeReportScroll.height;
    atTop = window.homeReportScroll.atTop;
  }
  reportDrawn.set(el, html);
  el.innerHTML = html;
  const next = el.querySelector('.home-report-list');
  if (!next) return;
  if (atTop) next.scrollTop = 0;
  else next.scrollTop = top + Math.max(0, next.scrollHeight - height);
}
async function reportOpenFile(id, index) {
  try {
    await fetch('/api/openFile', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ c: id, a: Number(index) }) });
  } catch (e) { /* 열기 실패는 화면을 멈추지 않아요 */ }
}
async function renderReports(el, opt) {
  if (!el) return;
  try {
    if (opt && opt.dept) el.dataset.lockDept = String(opt.dept);
    else if (opt) delete el.dataset.lockDept;
    if (opt && opt.title) el.dataset.reportTitle = String(opt.title);
    if (el.dataset.bound !== '1') {
      el.dataset.bound = '1';
      el.addEventListener('click', (ev) => {
        if (ev.target.closest('.report-more')) return;
        const fold = ev.target.closest('.cmd-fold');
        if (fold) {
          const cid = fold.getAttribute('data-cmd') || '';
          setTimeout(() => {
            if (fold.open) reportLogOpen.add(cid); else reportLogOpen.delete(cid);
          }, 0);
          return;
        }
        const art = ev.target.closest('[data-art-open]');
        if (art) {
          ev.preventDefault();
          ev.stopPropagation();
          reportOpenFile(art.getAttribute('data-id'), art.getAttribute('data-a'));
          return;
        }
        if (ev.target.closest('a, .art-box')) return;
        const deptBtn = ev.target.closest('[data-reportdept]');
        if (deptBtn) {
          reportDept = deptBtn.getAttribute('data-reportdept') || '전체';
          reportDrawn.delete(el);
          reportPaint(el);
          return;
        }
        const card = ev.target.closest('[data-report-toggle]');
        if (!card) return;
        const id = card.getAttribute('data-report-id') || '';
        if (!id) return;
        if (reportOpen.has(id)) reportOpen.delete(id);
        else reportOpen.add(id);
        reportDrawn.delete(el);
        reportPaint(el);
      });
    }
    reportPaint(el);
    const wait = reportIsLive() ? 0 : 15000;
    if (reportPack && Date.now() - reportAt < wait) {
      if (typeof homeAfterReports === 'function') homeAfterReports();
      return;
    }
    const data = await loadReportPack();
    if (data && Array.isArray(data.items)) reportPack = { items: data.items, depts: data.depts || [], error: data.ok ? '' : (data.error || '') };
    else if (!reportPack) reportPack = { items: [], depts: [], error: '보고를 불러오지 못했어요.' };
    reportAt = Date.now();
    const slot = el.isConnected ? el : document.getElementById('homeReports');
    if (slot) reportPaint(slot);
    if (typeof homeAfterReports === 'function') homeAfterReports();
  } catch (e) {
    el.innerHTML = '<div class="card home-report-panel"><b>보고 창</b><div class="muted small">보고 창을 그리지 못했어요.</div></div>';
  }
}
setInterval(() => {
  if (typeof document === 'undefined' || !reportIsLive()) return;
  const nodes = document.querySelectorAll('#homeReports, #zDeptReports');
  if (!nodes.length) return;
  reportAt = 0;
  nodes.forEach((el) => renderReports(el));
}, 8000);
