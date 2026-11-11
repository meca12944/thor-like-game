// 부서 이름 보내기 · 켤 때 자리 안 만들기 시험. office/ 에서: node tools/test_dept_send.js
'use strict';
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const assert = require('assert');
const { spawn } = require('child_process');

const root = path.join(__dirname, '..');
const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'office-dept-'));
const picked = path.join(dataDir, '고른폴더');
const fakeRepo = path.join(dataDir, 'fake-game');
fs.mkdirSync(picked);
fs.mkdirSync(fakeRepo);
fs.writeFileSync(path.join(fakeRepo, '.git'), 'gitdir: nowhere\n');

function freePort() {
  return new Promise((resolve, reject) => {
    const s = http.createServer();
    s.on('error', reject);
    s.listen(0, '127.0.0.1', () => {
      const p = s.address().port;
      s.close(() => resolve(p));
    });
  });
}
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function post(port, pathname, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body || {});
    const req = http.request({ host: '127.0.0.1', port, path: pathname, method: 'POST', headers: { 'content-type': 'application/json', 'content-length': Buffer.byteLength(data) } }, (res) => {
      let d = ''; res.on('data', (c) => (d += c)); res.on('end', () => { try { resolve(JSON.parse(d || '{}')); } catch (e) { reject(e); } });
    });
    req.on('error', reject);
    req.end(data);
  });
}
function getJson(port, pathname) {
  return new Promise((resolve, reject) => {
    http.get({ host: '127.0.0.1', port, path: pathname }, (res) => {
      let d = ''; res.on('data', (c) => (d += c)); res.on('end', () => { try { resolve(JSON.parse(d || '{}')); } catch (e) { reject(e); } });
    }).on('error', reject);
  });
}
function checkSource() {
  const server = fs.readFileSync(path.join(root, 'server.js'), 'utf8');
  const home = fs.readFileSync(path.join(root, 'ui', 'home.js'), 'utf8');
  assert.ok(!server.includes('onlyEmpty'), '켤 때 빈 부서를 만드는 코드가 남았어요');
  const listenAt = server.indexOf('server.listen');
  assert.ok(listenAt > 0);
  assert.ok(!server.slice(listenAt, listenAt + 700).includes('ensureDeptClaude'), '켤 때 직원 자리를 만들면 안 돼요');
  assert.ok(!server.includes("name: '영상기획'"), '홍보에 영상기획이 남았어요');
  assert.ok(server.includes("name: '클로드 홍보2'"));
  assert.ok(server.includes('게시·광고 수정은 안 함'));
  assert.ok(server.includes("id: 'video'") && server.includes("name: '영상 기획팀'"));
  assert.ok(server.includes("name: '영상 기획 직원'") && server.includes("name: '영상 기획 2'"));
  assert.ok(home.includes("id: 'video'") && home.includes("name: '영상 기획팀'"));
  const sendAt = server.indexOf('async function sendToBot');
  const sendFn = server.slice(sendAt, server.indexOf('function pollSoon'));
  assert.ok(sendFn.includes("const target = dept || 'AI 협력'"));
  assert.ok(!sendFn.includes('settings.botTarget'));
  assert.ok(home.includes('data-home="makedept"'));
  assert.ok(home.includes('＋ 만들기'));
  assert.ok(home.includes('homeDeptFolder'));
}

async function main() {
  checkSource();
  const hookPort = await freePort();
  const appPort = await freePort();
  const seen = [];
  const hook = http.createServer((q, s) => {
    if (q.method !== 'POST' || q.url !== '/hook') { s.statusCode = 404; s.end('{}'); return; }
    let d = '';
    q.on('data', (c) => (d += c));
    q.on('end', () => {
      let body = {};
      try { body = JSON.parse(d || '{}'); } catch (e) { body = { bad: true }; }
      seen.push({ authOk: q.headers.authorization === 'Bearer hook-key', body });
      s.end('{"ok":true}');
    });
  });
  await new Promise((resolve) => hook.listen(hookPort, '127.0.0.1', resolve));
  fs.writeFileSync(path.join(dataDir, 'state.json'), JSON.stringify({
    settings: {
      gameRepo: fakeRepo,
      grokMode: 'bot',
      botUrl: `http://127.0.0.1:${hookPort}/hook`,
      botKey: 'hook-key',
      botTarget: '다른곳',
    },
    employees: [{ id: 'emp-promo', name: '홍보팀장', role: '팀장', dept: 'promo', lead: true, partner: false, folder: '', queue: [], status: 'idle' }],
  }));
  const child = spawn(process.execPath, ['server.js'], {
    cwd: root,
    env: { ...process.env, OFFICE_DATA: dataDir, OFFICE_PORT: String(appPort), OFFICE_CLAUDE: 'false', OFFICE_GH_API: `http://127.0.0.1:${hookPort}` },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let log = '';
  child.stdout.on('data', (c) => (log += c));
  child.stderr.on('data', (c) => (log += c));
  const stop = () => { try { child.kill('SIGTERM'); } catch (e) { /* */ } };
  const timer = setTimeout(() => { stop(); console.error(log); process.exit(1); }, 25000);
  try {
    for (let i = 0; i < 50 && !log.includes('문 열림'); i++) {
      if (child.exitCode !== null) throw new Error('서버가 바로 끝났어요\n' + log);
      await sleep(100);
    }
    assert.ok(log.includes('문 열림'), log);
    await sleep(800);
    assert.ok(!log.includes('작업 공간을 못 만들었어요') && !log.includes('[부서 클로드]'), '켤 때 게임 자리를 만들려고 했어요\n' + log);
    const boot = await getJson(appPort, '/api/state');
    assert.strictEqual(boot.employees.length, 1, '켤 때 직원을 더 만들면 안 돼요');
    assert.strictEqual(boot.employees[0].dept, 'promo');

    const missing = await post(appPort, '/api/team', { dept: 'promo', folder: path.join(dataDir, '없는폴더') });
    assert.strictEqual(missing.ok, false);
    const badDept = await post(appPort, '/api/team', { dept: '없는부서', folder: picked });
    assert.strictEqual(badDept.ok, false);
    const made = await post(appPort, '/api/team', { dept: 'promo', folder: picked });
    assert.strictEqual(made.ok, true, made.error || '');
    assert.ok(made.made.includes('클로드 홍보2'));
    assert.ok(!made.made.includes('영상기획'));
    assert.ok(made.made.includes('블로그글') && made.made.includes('광고문안'));
    assert.ok(!made.made.includes('제로폰팀장') && !made.made.includes('홍보팀장') && !made.made.includes('영상 기획 팀장'));
    await sleep(500);
    const st = await getJson(appPort, '/api/state');
    const names = st.employees.map((e) => e.name);
    assert.ok(!names.includes('제로폰팀장'));
    for (const e of st.employees) assert.strictEqual(e.dept, 'promo', e.name + ' 부서 저장은 id 여야 해요');
    const promo2 = st.employees.find((e) => e.name === '클로드 홍보2');
    assert.ok(promo2 && promo2.dept === 'promo' && promo2.folder && promo2.folder.startsWith(picked));
    assert.ok(fs.existsSync(promo2.folder));
    assert.ok(!fs.existsSync(path.join(promo2.folder, '.git')));
    const saved = JSON.parse(fs.readFileSync(path.join(dataDir, 'state.json'), 'utf8'));
    assert.ok(saved.employees.every((e) => e.dept === 'promo'));
    const vidDir = path.join(dataDir, '영상폴더');
    fs.mkdirSync(vidDir);
    const vid = await post(appPort, '/api/team', { dept: 'video', folder: vidDir });
    assert.strictEqual(vid.ok, true, vid.error || '');
    assert.deepStrictEqual(vid.made.slice().sort(), ['영상 기획 팀장', '영상 기획 직원'].sort());
    await sleep(400);
    const st2 = await getJson(appPort, '/api/state');
    const vLead = st2.employees.find((e) => e.name === '영상 기획 팀장');
    const vStaff = st2.employees.find((e) => e.name === '영상 기획 직원');
    assert.ok(vLead && vLead.dept === 'video' && vLead.lead === true && vLead.folder.startsWith(vidDir));
    assert.ok(vStaff && vStaff.dept === 'video' && vStaff.folder.startsWith(vidDir));
    assert.ok(!fs.existsSync(path.join(vLead.folder, '.git')));
    assert.ok(!st2.employees.some((e) => e.name === '영상기획'));
    const vDept = st2.botTargets.depts.find((d) => d.id === 'video');
    assert.ok(vDept && vDept.name === '영상 기획팀');
    const vBots = st2.botTargets.bots.filter((b) => b.dept === 'video').map((b) => b.name).sort();
    assert.deepStrictEqual(vBots, ['영상 기획 2', '영상 기획 팀장']);

    await post(appPort, '/api/room/relay', { emp: 'emp-promo', kind: 'chat', text: '쇼츠 문구 부탁' });
    await post(appPort, '/api/room/relay', { kind: 'chat', text: '사장님 말' });
    for (let i = 0; i < 30 && seen.length < 2; i++) await sleep(100);
    assert.strictEqual(seen.length, 2, '그록에게 두 통이 가야 해요');
    assert.ok(seen.every((x) => x.authOk));
    const empMsg = seen.find((x) => String(x.body.command || '').includes('쇼츠 문구'));
    const bossMsg = seen.find((x) => String(x.body.command || '').includes('사장님 말'));
    assert.ok(empMsg && bossMsg);
    assert.strictEqual(empMsg.body.target, '홍보');
    assert.strictEqual(empMsg.body.dept, '홍보');
    assert.ok(String(empMsg.body.command).includes('[부서:홍보]'));
    assert.ok(!String(empMsg.body.command).includes('[부서:promo]'));
    assert.ok(!String(empMsg.body.command).includes('promo'));
    assert.strictEqual(bossMsg.body.target, 'AI 협력');
    assert.strictEqual(bossMsg.body.dept, '');
    assert.ok(!String(bossMsg.body.command).includes('[부서:'));
    const room = (await getJson(appPort, '/api/state')).grokLog.find((g) => String(g.text || '').includes('쇼츠 문구'));
    assert.ok(room && room.text.startsWith('[부서:홍보] '));
    console.log('부서 보내기 시험 통과');
  } finally {
    clearTimeout(timer);
    stop();
    await new Promise((resolve) => hook.close(resolve));
    await sleep(100);
    try { fs.rmSync(dataDir, { recursive: true, force: true }); } catch (e) { /* */ }
  }
}
main().catch((e) => { console.error(e); process.exit(1); });
