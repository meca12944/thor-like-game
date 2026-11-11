// 알들 컴퍼니 보고 창. 회사 화면에서 renderReports(el) 한 번만 불러요.
// 색은 전부 var(--이름, 기본값). 나중에 theme.css 가 같은 이름을 정하면 그대로 따라가요.
'use strict';
const REPORT_DEPTS = [
  ['전체', '전체'],
  ['게임 필멸자', '🎮 게임'],
  ['제로폰', '📱 제로폰'],
  ['홍보', '📣 홍보'],
  ['경영지원', '💼 경영'],
  ['STCO', '🛍 STCO'],
  ['AI 협력·연결', '🔗 AI 협력'],
];
let reportDept = '전체';
let reportList = null;
let reportAt = 0;
let reportStamp = '';
let reportFlight = null;

function reportEsc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function reportStatusColor(status) {
  if (status === '완료') return 'var(--green,#1f9d55)';
  if (status === '문제 있음') return 'var(--red,#d13b3b)';
  if (status === '접수') return 'var(--blue,#2f6fde)';
  return 'var(--muted,#6b7280)';
}
function reportInDept(r, name) {
  if (!name || name === '전체') return true;
  if (r.dept === name || r.target === name) return true;
  const short = String(name).split('·')[0];
  return !!short && r.target === short;
}
function reportShown(list) {
  const all = Array.isArray(list) ? list : [];
  if (reportDept === '전체') return all;
  return all.filter((r) => reportInDept(r, reportDept));
}
function reportNowStamp() {
  try {
    const h = S.botHistory || [];
    const n = (S.reports && S.reports.length) || 0;
    return n + '|' + h.length + '|' + (h[0] && h[0].id ? h[0].id : '');
  } catch (e) {
    return '';
  }
}
function loadReportList() {
  if (reportFlight) return reportFlight;
  reportFlight = (async () => {
    try {
      const r = await fetch('/api/company/reports', { cache: 'no-store' });
      const data = await r.json();
      return Array.isArray(data) ? data : null;
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
function reportHtml(list) {
  const boxStyle = 'background:var(--panel,#ffffff);color:var(--text,#1d2129);border:1px solid var(--line,#e2e5ea)';
  const muted = 'color:var(--muted,#6b7280);font-size:13px';
  if (!Array.isArray(list)) {
    return `<div class="card" style="${boxStyle}"><b>📋 보고 창</b><div style="${muted}">보고를 불러오는 중…</div></div>`;
  }
  const shown = reportShown(list);
  const n = (st) => shown.filter((r) => r.status === st).length;
  const buttons = REPORT_DEPTS.map(([name, label]) => {
    const on = reportDept === name;
    const st = `border:1px solid var(--line,#e2e5ea);background:${on ? 'var(--bg,#f3f4f6)' : 'var(--panel,#ffffff)'};color:var(--text,#1d2129);border-radius:8px;padding:4px 10px;cursor:pointer;font-weight:${on ? '700' : '500'}`;
    return `<button type="button" data-reportdept="${reportEsc(name)}" style="${st}">${reportEsc(label)}</button>`;
  }).join('');
  const cards = shown.map((r) => {
    const who = r.lead ? ` · ${(r.status === '완료' || r.status === '문제 있음') ? '검수' : '담당'}: ${reportEsc(r.lead)}` : '';
    const lines = (Array.isArray(r.summary) ? r.summary : []).map((s) => reportEsc(s)).join('<br>');
    return `<article class="card" style="${boxStyle};border-left:4px solid ${reportStatusColor(r.status)};margin-top:8px">
      <div style="display:flex;gap:8px;align-items:baseline;flex-wrap:wrap">
        <b>${reportEsc(r.target || '대상 없음')}</b>
        <span style="color:${reportStatusColor(r.status)};font-weight:700">${reportEsc(r.status || '')}</span>
        <span style="margin-left:auto;${muted}">${reportEsc(r.time || '')}</span>
      </div>
      <div>${reportEsc(r.command || '')}</div>
      <div style="${muted}">올린 쪽: ${reportEsc(r.source || '')}${who}</div>
      <div>${lines}</div>
      ${reportLink(r.where)}
    </article>`;
  }).join('');
  const empty = shown.length ? '' : `<div class="empty">${reportDept === '전체' ? '아직 올라온 보고가 없어요.' : '이 부서에는 아직 보고가 없어요.'}</div>`;
  return `<div class="card" style="${boxStyle}">
      <b>📋 보고 창</b>
      <div style="${muted}">그록 팀장 보고와 클로드 직원 보고를 시간 순으로 모았어요. 시간은 한국 시간이에요.</div>
      <div style="margin:6px 0;font-weight:700">접수 ${n('접수')} · 진행 중 ${n('진행 중')} · 완료 ${n('완료')} · 문제 ${n('문제 있음')}</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px">${buttons}</div>
    </div>${cards}${empty}`;
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
        el.innerHTML = reportHtml(reportList);
      });
    }
    el.innerHTML = reportHtml(reportList);
    const stamp = reportNowStamp();
    if (reportList && stamp === reportStamp && Date.now() - reportAt < 20000) return;
    const data = await loadReportList();
    if (Array.isArray(data)) reportList = data;
    else if (!reportList) reportList = [];
    reportAt = Date.now();
    reportStamp = reportNowStamp();
    const slot = el.isConnected ? el : document.getElementById('companyReports');
    if (slot) slot.innerHTML = reportHtml(reportList);
  } catch (e) {
    el.innerHTML = '<div class="card" style="background:var(--panel,#ffffff);color:var(--muted,#6b7280);border:1px solid var(--line,#e2e5ea)">보고 창을 그리지 못했어요.</div>';
  }
}
