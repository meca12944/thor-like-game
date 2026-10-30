// 끊김 재기: 게임 안에서 화면 간격(rAF)·주인공 빠르기·카메라 이동을 화면마다 기록. 쓰는 법: node smooth_probe.js <포트> [go=felt] [녹화 폴더(있으면 recordVideo도 켬)]
const { chromium } = require('playwright');
(async () => {
  const [port, q, rec] = [process.argv[2], process.argv[3] || 'go=felt', process.argv[4]];
  const b = await chromium.launch();
  const opt = { viewport: { width: 1280, height: 720 } }; if (rec) opt.recordVideo = { dir: rec, size: { width: 1280, height: 720 } };
  const ctx = await b.newContext(opt); const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&${q}`);
  await p.waitForTimeout(14000);
  const hold = async (k, ms) => { await p.keyboard.down(k); await p.waitForTimeout(ms); await p.keyboard.up(k); };
  await hold('s', 900); await p.waitForTimeout(300);
  await p.evaluate(() => { const H = window.__worldHooks, S = H.S, h = H.hero; window.__L = []; const f = t => { window.__L.push([t, S.cam[0], S.cam[1], h.x, h.y]); if (window.__L.length < 260) requestAnimationFrame(f); }; requestAnimationFrame(f); });
  await p.keyboard.press('d'); await p.waitForTimeout(60); await hold('d', 1800); await hold('s', 1500);
  const L = await p.evaluate(() => window.__L);
  const dts = L.slice(1).map((r, i) => r[0] - L[i][0]); dts.sort((a, b) => a - b);
  const q50 = dts[dts.length >> 1], q90 = dts[Math.floor(dts.length * .9)], q99 = dts[Math.floor(dts.length * .99)], long = dts.filter(d => d > 25).length;
  console.log('화면 간격 ms: 중간', q50.toFixed(1), '90%', q90.toFixed(1), '99%', q99.toFixed(1), '최대', dts[dts.length - 1].toFixed(1), '25ms 넘은 화면', long, '/', dts.length);
  // 화면 위 주인공 자리 (월드 → 낮은 해상도 화면): hero.x - cam[0]
  const sx = L.map(r => r[3] - r[1]); const v = L.slice(1).map((r, i) => (r[3] - L[i][3]) / ((r[0] - L[i][0]) / 1000));
  console.log('화면 위 주인공 x (처음 40):', sx.slice(20, 60).map(a => a.toFixed(1)).join(' '));
  console.log('주인공 빠르기 px/s (처음 40):', v.slice(20, 60).map(a => a.toFixed(0)).join(' '));
  const cdx = L.slice(1).map((r, i) => r[1] - L[i][1]); console.log('카메라 x 이동/화면 (처음 40):', cdx.slice(20, 60).map(a => a.toFixed(2)).join(' '));
  console.log('errors', errs.length);
  await ctx.close(); await b.close();
})();
