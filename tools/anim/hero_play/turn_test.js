// 방향 전환 숫자 기록: 달리다 → 반대로 꺾을 때 화면마다 [시각, 그림 방향 칸(vd 0=→ 2=↓ 4=←), face, 달리기, 움직임, 잔상 수, x, 잔상 수명]
// 쓰는 법: node turn_test.js <포트> <녹화 폴더> [go=felt]  → 꺾은 뒤 vd가 0→1→2→3→4로 한 칸씩, 칸마다 잔상 1장(수명 0.25)이면 정상
const { chromium } = require('playwright');
(async () => {
  const [port, out, q] = [process.argv[2], process.argv[3], process.argv[4] || 'go=felt'];
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: out, size: { width: 1280, height: 720 } } });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const T0 = Date.now();
  await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&${q}`);
  await p.waitForTimeout(14000);
  const hold = async (k, ms) => { await p.keyboard.down(k); await p.waitForTimeout(ms); await p.keyboard.up(k); };
  await hold('s', 1200); await p.waitForTimeout(400);
  // 기록: 매 화면마다 그림 방향·잔상 수
  await p.evaluate(() => { const H = window.__worldHooks, S = H.S, h = H.hero; window.__log = []; const f = () => { window.__log.push([Math.round(performance.now()), h.vd, h.face, !!h.run, h.moving ? 1 : 0, (S.trail || []).length, Math.round(h.x), (S.trail || []).map(a => a.life.toFixed(2)).join('|')]); if (window.__log.length < 400) requestAnimationFrame(f); }; requestAnimationFrame(f); });
  const t1 = Date.now() - T0;
  await p.keyboard.press('d'); await p.waitForTimeout(60); await p.keyboard.down('d'); await p.waitForTimeout(1300);
  const t2 = Date.now() - T0;
  await p.keyboard.down('a'); await p.keyboard.up('d'); await p.waitForTimeout(1300); await p.keyboard.up('a');
  await p.waitForTimeout(500);
  const log = await p.evaluate(() => window.__log); const tp = await p.evaluate(() => performance.timeOrigin); const t2p = T0 + t2 - tp;
  console.log('runStart', t1, 'turn', t2, 'errors', errs.length);
  for (const r of log) if (r[0] > t2p - 100 && r[0] < t2p + 900) console.log(JSON.stringify(r));
  await ctx.close(); await b.close();
})();
