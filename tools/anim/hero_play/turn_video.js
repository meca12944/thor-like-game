// 방향 전환 시험 녹화: 달리며 ↓→←↑↓→ 꺾기, 걸으며 ←→ 꺾기. 키를 놓기 전에 다음 키를 눌러 달리기가 끊기지 않게. 찍은 시각(ms) 출력
// 쓰는 법: node turn_video.js <포트> <녹화 폴더> [go=felt]
const { chromium } = require('playwright');
(async () => {
  const [port, out, q] = [process.argv[2], process.argv[3], process.argv[4] || 'go=felt'];
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: out, size: { width: 1280, height: 720 } } });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const T0 = Date.now(); const marks = [];
  await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&${q}`);
  await p.waitForTimeout(14000);
  const sw = async (from, to, ms) => { await p.keyboard.down(to); await p.keyboard.up(from); marks.push([to, Date.now() - T0]); await p.waitForTimeout(ms); };
  await p.keyboard.press('s'); await p.waitForTimeout(60); await p.keyboard.down('s'); marks.push(['s', Date.now() - T0]); await p.waitForTimeout(1000);
  await sw('s', 'd', 1300); await sw('d', 'a', 1200); await sw('a', 'w', 900); await sw('w', 's', 900); await sw('s', 'd', 900);
  await p.keyboard.up('d'); await p.waitForTimeout(600);
  // 걸으며 꺾기
  await p.keyboard.down('a'); marks.push(['walk a', Date.now() - T0]); await p.waitForTimeout(1000); await sw('a', 'd', 1000); await p.keyboard.up('d'); await p.waitForTimeout(500);
  console.log(JSON.stringify(marks), 'errors', errs.length, errs.slice(0, 3).join('|'));
  await ctx.close(); await b.close();
})();
