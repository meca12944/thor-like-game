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
  const boxStyle = 'background:var(--panel,#ffffff);color:var(--text,#1d2129);border:1px solid var(--line,#e2e5ea)';
  const muted = 'color:var(--muted,#6b7280);font-size:13px';
  if (!pack) {
    return `<div class="card" style="${boxStyle}"><b>📋 보고 창</b><div style="${muted}">보고를 불러오는 중…</div></div>`;
  }
  const list = Array.isArray(pack.items) ? pack.items : [];
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
    const lamp = r.status === '완료' ? '<span class="lamp on">🟢</span>' : '';
    return `<article class="card" style="${boxStyle};border-left:4px solid ${reportStatusColor(r.status)};margin-top:8px">
      <div class="card-head">
        <b>${reportEsc(r.target || '대상 없음')}</b>
        <span style="color:${reportStatusColor(r.status)};font-weight:700">${reportEsc(r.status || '')}</span>
        ${r.needBoss ? '<span style="color:var(--blue,#2f6fde);font-weight:700">사장님 확인 필요</span>' : ''}
        ${lamp}
        <time>${reportEsc(r.time || '')}</time>
      </div>
      <div>${reportEsc(r.command || '')}</div>
      <div style="${muted}">올린 쪽: ${reportEsc(r.source || '그록')}${who}</div>
      <div>${lines}</div>
      ${reportLink(r.result || r.where)}
    </article>`;
  }).join('');
  const empty = shown.length ? '' : `<div class="empty">${reportDept === '전체' ? '아직 올라온 보고가 없어요.' : '이 부서에는 아직 보고가 없어요.'}${pack.error ? `<br><span class="small">${reportEsc(pack.error)}</span>` : ''}</div>`;
  return `<div class="card" style="${boxStyle}">
      <b>📋 보고 창</b>
      <div style="${muted}">팀장 보고와 클로드 직원 보고를 시간 순으로 모았어요. 시간은 한국 시간이에요. 초록 불은 정말 끝났을 때만 켜져요.</div>
      <div style="margin:6px 0;font-weight:700;color:var(--text,#1d2129)">접수 ${n('접수')} · 진행 중 ${n('진행 중')} · 완료 ${n('완료')} · 문제 ${n('문제 있음')}</div>
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
