// 보고 창. home.js 에서 renderReports(el) 또는 renderReports(el, { dept, title }) 로 불러요.
// 목록은 /api/company/reports 의 { items, depts } 를 읽어요. 부서 이름은 서버 목록을 그대로 써요.
// 색은 theme.css 이름만 써요.
'use strict';
let reportDept = '전체';
let reportPack = null;
let reportAt = 0;
let reportFlight = null;
const reportOpen = new Set();

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
  const shown = reportShown(list, lockDept);
  const n = (st) => shown.filter((r) => r.status === st).length;
  const depts = reportDepts(pack);
  if (!lockDept && reportDept !== '전체' && !depts.some((d) => d.name === reportDept)) reportDept = '전체';
  const buttons = lockDept ? '' : ['전체'].concat(depts.map((d) => d.name)).map((name) => {
    const d = depts.find((x) => x.name === name);
    const label = name === '전체' ? '전체' : ((d && d.icon) ? d.icon + ' ' : '') + name;
    const on = reportDept === name ? ' on' : '';
    return `<button type="button" class="${on.trim()}" data-reportdept="${reportEsc(name)}">${reportEsc(label)}</button>`;
  }).join('');
  const cards = shown.map((r) => {
    const who = r.lead ? ` · ${(r.status === '완료' || r.status === '문제 있음') ? '검수' : '담당'}: ${reportEsc(r.lead)}` : '';
    const lines = (Array.isArray(r.summary) ? r.summary : []).map((s) => reportEsc(s)).join('<br>');
    const arts = Array.isArray(r.artifacts) ? r.artifacts.length : 0;
    const open = reportOpen.has(r.id || '');
    const id = r.id || '';
    return `<article class="card home-report-card" data-status="${reportEsc(r.status || '')}" data-report-toggle="1" data-report-id="${reportEsc(id)}">
      <div class="card-head">
        <span class="st-lamp${r.status === '완료' ? ' on' : ''}"></span>
        <b>${reportEsc(r.dept || r.target || '부서 없음')}</b>
        <span class="rst">${reportEsc(r.status || '')}</span>
        ${r.needBoss ? '<span class="boss">사장님 확인 필요</span>' : ''}
        <time>${reportEsc(r.time || '')}</time>
      </div>
      <div>${reportEsc(r.command || '')}</div>
      <div class="who">올린 쪽: ${reportEsc(r.source || '그록')}${who}${arts ? ' · 결과물 ' + arts + '개' : ''}${open ? '' : ' · 누르면 결과물'}</div>
      <div class="sum">${lines}</div>
      ${reportArtHtml(r)}
    </article>`;
  }).join('');
  const emptyText = (lockDept || reportDept !== '전체') ? '이 부서에는 아직 보고가 없어요.' : '아직 올라온 보고가 없어요.';
  const empty = shown.length ? '' : `<div class="home-report-empty">${emptyText}${pack.error ? `<span class="small">${reportEsc(pack.error)}</span>` : '<span class="small">일을 보내면 여기에 접수로 떠요.</span>'}</div>`;
  const hint = lockDept ? '이 부서 보고만, 최신순이에요. 초록 불은 끝났을 때만 켜져요.' : '모든 부서 보고를 시간 순으로 모았어요. 초록 불은 끝났을 때만 켜져요.';
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
          el.innerHTML = reportHtml(reportPack, reportOpt(el));
          return;
        }
        const card = ev.target.closest('[data-report-toggle]');
        if (!card) return;
        const id = card.getAttribute('data-report-id') || '';
        if (!id) return;
        if (reportOpen.has(id)) reportOpen.delete(id);
        else reportOpen.add(id);
        el.innerHTML = reportHtml(reportPack, reportOpt(el));
      });
    }
    el.innerHTML = reportHtml(reportPack, reportOpt(el));
    if (reportPack && Date.now() - reportAt < 15000) {
      if (typeof homeAfterReports === 'function') homeAfterReports();
      return;
    }
    const data = await loadReportPack();
    if (data && Array.isArray(data.items)) reportPack = { items: data.items, depts: data.depts || [], error: data.ok ? '' : (data.error || '') };
    else if (!reportPack) reportPack = { items: [], depts: [], error: '보고를 불러오지 못했어요.' };
    reportAt = Date.now();
    const slot = el.isConnected ? el : document.getElementById('homeReports');
    if (slot) slot.innerHTML = reportHtml(reportPack, reportOpt(slot));
    if (typeof homeAfterReports === 'function') homeAfterReports();
  } catch (e) {
    el.innerHTML = '<div class="card home-report-panel"><b>보고 창</b><div class="muted small">보고 창을 그리지 못했어요.</div></div>';
  }
}
