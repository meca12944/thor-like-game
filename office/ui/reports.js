// 보고 창. home.js 에서 renderReports(el) 한 번만 불러요.
// 목록은 /api/company/reports 의 { items } 를 읽어요. 색은 theme.css 이름만 써요.
'use strict';
const REPORT_DEPTS = [
  ['전체', '전체'],
  ['게임 필멸자', '🎮 게임'],
  ['제로폰', '📱 제로폰'],
  ['홍보', '📣 홍보'],
  ['경영지원', '💼 경영'],
  ['STCO', '🛍 STCO'],
  ['영상 기획팀', '🎬 영상'],
  ['AI 협력·연결', '🔗 AI 협력'],
];
let reportDept = '전체';
let reportPack = null;
let reportAt = 0;
let reportFlight = null;

function reportEsc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function reportStatusColor(status) {
  if (status === '완료' || status === '문제 있음' || status === '접수' || status === '진행 중') return status;
  return '';
}
function reportInDept(r, name) {
  if (!name || name === '전체') return true;
  if (r.dept === name || r.target === name) return true;
  const short = String(name).split('·')[0];
  return !!short && r.target === short;
}
function reportShown(items) {
  const all = Array.isArray(items) ? items : [];
  if (reportDept === '전체') return all;
  return all.filter((r) => reportInDept(r, reportDept));
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
function reportLink(url) {
  const s = String(url || '');
  if (!/^https?:\/\//i.test(s)) return '';
  return `<a href="${reportEsc(s)}" target="_blank" rel="noopener noreferrer" style="color:var(--blue,#2f6fde)">결과 보기</a>`;
}
function reportHtml(pack) {
  if (!pack) {
    return `<div class="card home-report-panel"><div class="home-report-head"><b>📋 보고 창</b><div class="muted small">보고를 불러오는 중…</div></div></div>`;
  }
  const list = Array.isArray(pack.items) ? pack.items : [];
  const shown = reportShown(list);
  const n = (st) => shown.filter((r) => r.status === st).length;
  const reportTips = {
    '전체': '모든 부서 보고를 봐요',
    '게임 필멸자': '게임 부서 보고만 봐요',
    '제로폰': '제로폰 보고만 봐요',
    '홍보': '홍보 부서 보고만 봐요',
    '경영지원': '경영지원 보고만 봐요',
    'STCO': 'STCO 보고만 봐요',
    '영상 기획팀': '영상 기획팀 보고만 봐요',
    'AI 협력·연결': 'AI 협력 보고만 봐요',
  };
  const buttons = REPORT_DEPTS.map(([name, label]) => {
    const on = reportDept === name ? ' on' : '';
    return `<button type="button" class="${on.trim()}" data-reportdept="${reportEsc(name)}" title="${reportEsc(reportTips[name] || name)}">${reportEsc(label)}</button>`;
  }).join('');
  const cards = shown.map((r) => {
    const who = r.lead ? ` · ${(r.status === '완료' || r.status === '문제 있음') ? '검수' : '담당'}: ${reportEsc(r.lead)}` : '';
    const lines = (Array.isArray(r.summary) ? r.summary : []).map((s) => reportEsc(s)).join('<br>');
    const lamp = r.status === '완료' ? '<span class="lamp on">🟢</span>' : '';
    const status = reportStatusColor(r.status);
    return `<article class="card home-report-card" data-status="${reportEsc(status)}">
      <div class="card-head">
        <b>${reportEsc(r.target || '대상 없음')}</b>
        <span class="rst">${reportEsc(r.status || '')}</span>
        ${r.needBoss ? '<span class="boss">사장님 확인 필요</span>' : ''}
        ${lamp}
        <time>${reportEsc(r.time || '')}</time>
      </div>
      <div>${reportEsc(r.command || '')}</div>
      <div class="who">올린 쪽: ${reportEsc(r.source || '그록')}${who}</div>
      <div class="sum">${lines}</div>
      ${reportLink(r.result || r.where)}
    </article>`;
  }).join('');
  const emptyText = reportDept === '전체' ? '아직 올라온 보고가 없어요.' : '이 부서에는 아직 보고가 없어요.';
  const empty = shown.length ? '' : `<div class="home-report-empty">${emptyText}${pack.error ? `<span class="small">${reportEsc(pack.error)}</span>` : '<span class="small">일을 보내면 여기에 접수로 떠요.</span>'}</div>`;
  return `<div class="card home-report-panel">
      <div class="home-report-head">
        <div class="home-report-title"><b>📋 보고 창</b><span class="muted small">시간 순이에요. 초록 불은 정말 끝났을 때만 켜져요.</span></div>
        <div class="home-report-counts">접수 ${n('접수')} · 진행 중 ${n('진행 중')} · 완료 ${n('완료')} · 문제 ${n('문제 있음')}</div>
        <div class="home-report-filters">${buttons}</div>
      </div>
      <div class="home-report-list">${cards}${empty}</div>
    </div>`;
}
async function renderReports(el) {
  if (!el) return;
  try {
    if (el.dataset.bound !== '1') {
      el.dataset.bound = '1';
      el.addEventListener('click', (ev) => {
        const b = ev.target.closest('[data-reportdept]');
        if (!b) return;
        reportDept = b.getAttribute('data-reportdept') || '전체';
        el.innerHTML = reportHtml(reportPack);
      });
    }
    el.innerHTML = reportHtml(reportPack);
    if (reportPack && Date.now() - reportAt < 15000) return;
    const data = await loadReportPack();
    if (data && Array.isArray(data.items)) reportPack = { items: data.items, error: data.ok ? '' : (data.error || '') };
    else if (!reportPack) reportPack = { items: [], error: '보고를 불러오지 못했어요.' };
    reportAt = Date.now();
    const slot = el.isConnected ? el : document.getElementById('homeReports');
    if (slot) slot.innerHTML = reportHtml(reportPack);
  } catch (e) {
    el.innerHTML = '<div class="card" style="background:var(--panel,#ffffff);color:var(--muted,#6b7280);border:1px solid var(--line,#e2e5ea)">보고 창을 그리지 못했어요.</div>';
  }
}
