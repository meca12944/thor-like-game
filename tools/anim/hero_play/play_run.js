// 주인공 시험 녹화: 새 저장으로 들판에 들어가 ↓↑→← 달리기, 걷기, 공격(J), 점프(Space) → 걸음 소리 수·오류 수 출력 + 녹화(webm)
// 쓰는 법: node play_run.js <서버 포트> <녹화 폴더> [주소 뒤 예 go=field_felt]
const { chromium } = require('playwright');
(async () => {
  const [port, out, q] = [process.argv[2], process.argv[3], process.argv[4] || 'go=field_felt'];
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: out, size: { width: 1280, height: 720 } } });
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push('pageerror ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push('console ' + m.text()); });
  await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&${q}`);
  await p.waitForTimeout(14000);
  await p.evaluate(() => { window.__steps = []; const g = window.__game; if (g && g.SFX) { const o = g.SFX.play.bind(g.SFX); g.SFX.play = (k, v, r) => { if (String(k).startsWith('step')) window.__steps.push([k, Math.round(performance.now())]); return o(k, v, r); }; } });
  const hold = async (k, ms) => { await p.keyboard.down(k); await p.waitForTimeout(ms); await p.keyboard.up(k); };
  const run = async (k, ms) => { await p.keyboard.press(k); await p.waitForTimeout(70); await hold(k, ms); };
  await run('s', 1800); await p.waitForTimeout(600);
  await run('w', 1800); await p.waitForTimeout(600);
  await run('d', 1200); await p.waitForTimeout(400);
  await run('a', 1200); await p.waitForTimeout(400);
  await hold('s', 1200); await p.waitForTimeout(500);
  await p.keyboard.press('j'); await p.waitForTimeout(500); await p.keyboard.press('Space'); await p.waitForTimeout(900);
  const steps = await p.evaluate(() => window.__steps || []);
  console.log('steps', steps.length, JSON.stringify(steps.slice(0, 12)));
  console.log('errors', errs.length, errs.slice(0, 5).join(' | '));
  await ctx.close(); await b.close();
})();
