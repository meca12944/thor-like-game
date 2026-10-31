// 고른 녹화 (사장님 10-30 「움직일 때 왜 화면이 턱턱 끊기면서 부드럽지가 않니」): 게임은 60장/초로 고른데, 클라우드 녹화(Playwright recordVideo 25장/초)가
// 같은 장을 두 번 찍거나 건너뛰어 영상만 턱턱 끊겼음(장마다 화면 이동 16·17칸이어야 할 곳이 9·34, 8·25). → 게임 시계를 직접 1/60초씩 넘기며 한 장씩 찍음.
// 쓰는 법: node smooth_rec.js <포트> <출력 폴더> [주소 뒤 go=felt] [장면 turns|side|run|dash] [찍기 배수 1=60장/초, 2=30장/초]
//   → <출력 폴더>/f00000.jpg … (그 다음 ffmpeg -framerate 60 -i f%05d.jpg … mp4)
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [port, out, q, scene, every] = [process.argv[2], process.argv[3], process.argv[4] || 'go=felt', process.argv[5] || 'turns', +(process.argv[6] || 1)];
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1280, height: 720 } }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(() => { // 게임 시계를 손으로: rAF·performance.now를 바꿈. __adv(ms) = 그만큼 시간을 넘기고 rAF 한 번
    let now = 0; const q = []; performance.now = () => now;
    window.requestAnimationFrame = cb => { q.push(cb); return q.length; }; window.cancelAnimationFrame = () => {};
    window.__adv = ms => { now += ms; const c = q.splice(0); for (const f of c) { try { f(now); } catch (e) { console.error(e); } } return c.length; };
  });
  await p.goto(`http://localhost:${port}/test128/index.html?nosave&worldreset&noscene&${q}`);
  const F = 1000 / 60; let n = 0, shot = 0;
  const step = async (cap) => { await p.evaluate(F => window.__adv(F), F); n++; if (cap && n % every === 0) { await p.screenshot({ path: `${out}/f${String(shot++).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 }); } };
  // 불러오기: 실제 시간도 흐르게(그림·맵 불러오기) 하면서 게임 시계 14초
  for (let i = 0; i < 840; i++) { await step(false); if (i % 4 === 0) await p.waitForTimeout(20); }
  const frames = async (k, cap = true) => { for (let i = 0; i < k; i++) await step(cap); };
  const down = k => p.keyboard.down(k), up = k => p.keyboard.up(k);
  const tap = async k => { await down(k); await frames(2); await up(k); await frames(3); }; // 두 번 눌러 달리기의 첫 번
  const sw = async (a, c, k) => { await down(c); await up(a); await frames(k); };
  const S = {
    turns: async () => { await tap('s'); await down('s'); await frames(60); await sw('s', 'd', 78); await sw('d', 'a', 72); await sw('a', 'w', 54); await sw('w', 's', 54); await sw('s', 'd', 54); await up('d'); await frames(36); await down('a'); await frames(60); await sw('a', 'd', 60); await up('d'); await frames(30); },
    side: async () => { await tap('s'); await down('s'); await frames(90); await up('s'); await frames(30); await tap('d'); await down('d'); await frames(130); await up('d'); await frames(30); await tap('a'); await down('a'); await frames(130); await up('a'); await frames(30); await down('d'); await frames(90); await up('d'); await frames(30); },
    dash: async () => { const dsh = async (dir) => { await down(dir); await frames(10); await down('Shift'); await frames(2); await up('Shift'); await frames(28); await up(dir); await frames(30); };
      await tap('s'); await down('s'); await frames(70); await up('s'); await frames(30); await dsh('d'); await dsh('a'); await dsh('s'); await dsh('w'); await dsh('d'); },
    run: async () => { await tap('s'); await down('s'); await frames(100); await sw('s', 'd', 100); await sw('d', 'w', 100); await sw('w', 'a', 100); await up('a'); await frames(40); },
  };
  await S[scene]();
  console.log('찍은 장', shot, '게임 장', n, 'errors', errs.length, errs.slice(0, 3).join(' | '));
  await ctx.close(); await b.close();
})();
