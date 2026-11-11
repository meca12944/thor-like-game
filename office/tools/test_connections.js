// 연결·기능 시험. office/ 에서: node tools/test_connections.js
// 가짜 주소·열쇠가 화면 답과 기록에 나오면 실패해요. 시험 보내기는 봇에게 가지 않아요.
'use strict';
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const assert = require('assert');
const { spawn } = require('child_process');

const root = path.join(__dirname, '..');
const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'office-conn-'));
const MARK = 'ZZZOFFICELEAK';

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
function getRaw(port, pathname) {
  return new Promise((resolve, reject) => {
    http.get({ host: '127.0.0.1', port, path: pathname }, (res) => {
      let d = ''; res.on('data', (c) => (d += c)); res.on('end', () => resolve({ status: res.statusCode, body: d }));
    }).on('error', reject);
  });
}
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

async function main() {
  const catalog = fs.readFileSync(path.join(root, 'connections.json'), 'utf8');
  assert.ok(!/https?:\/\//.test(catalog), '목록 파일에 주소가 있으면 안 돼요');
  assert.ok(!/sk-|ghp_|github_pat_/.test(catalog), '목록 파일에 열쇠처럼 보이는 글자가 있으면 안 돼요');
  const doc = JSON.parse(catalog);
  const ids = doc.connections.map((c) => c.id);
  ['claude-code', 'grok-bot', 'github', 'claude-api', 'game-repo', 'emp-folders', 'mcp-office', 'grok-drive', 'grok-github', 'grok-supabase', 'grok-ads', 'grok-x', 'grok-origin'].forEach((id) => {
    assert.ok(ids.includes(id), id);
  });
  assert.ok(doc.features.some((f) => f.name === '연결·기능'));
  assert.ok(doc.features.some((f) => String(f.what).includes('영상 기획팀')));

  const hookPort = await freePort();
  const appPort = await freePort();
  let hits = 0;
  const hook = http.createServer((q, s) => { hits += 1; s.statusCode = 204; s.end(); });
  await new Promise((resolve) => hook.listen(hookPort, '127.0.0.1', resolve));
  fs.mkdirSync(path.join(dataDir, 'prompts'), { recursive: true });
  fs.mkdirSync(path.join(dataDir, '.git'));
  const botUrl = `http://127.0.0.1:${hookPort}/hook-${MARK}`;
  const botKey = `botkey-${MARK}-0123456789`;
  const ghToken = `ghp_${MARK}0123456789abcd`;
  const apiKey = `sk-ant-${MARK}0123456789`;
  fs.writeFileSync(path.join(dataDir, 'state.json'), JSON.stringify({
    settings: { botUrl, botKey, ghToken, gameRepo: dataDir },
    employees: [
      { id: 'e1', name: '팀장', role: '총괄', dept: 'game', folder: dataDir, queue: [] },
      { id: 'e2', name: '없는직원', role: '시험', dept: 'video', folder: path.join(dataDir, '없는폴더'), queue: [] },
    ],
  }));
  const child = spawn(process.execPath, ['server.js'], {
    cwd: root,
    env: { ...process.env, OFFICE_DATA: dataDir, OFFICE_PORT: String(appPort), OFFICE_CLAUDE: 'false', ANTHROPIC_API_KEY: apiKey },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let log = '';
  child.stdout.on('data', (c) => (log += c));
  child.stderr.on('data', (c) => (log += c));
  const stop = () => { try { child.kill('SIGTERM'); } catch (e) { /* */ } };
  const timer = setTimeout(() => { stop(); console.error(log); process.exit(1); }, 40000);
  try {
    for (let i = 0; i < 80 && !log.includes('문 열림'); i++) {
      if (child.exitCode !== null) throw new Error('서버가 바로 끝났어요\n' + log);
      await sleep(100);
    }
    assert.ok(log.includes('문 열림'), log);
    for (let i = 0; i < 40 && !log.includes('클로드 코드'); i++) await sleep(100);
    const got = await getRaw(appPort, '/api/connections');
    assert.strictEqual(got.status, 200);
    const body = JSON.parse(got.body);
    const text = got.body;
    assert.ok(!text.includes(MARK), '화면 답에 가짜 열쇠가 나왔어요');
    assert.ok(!text.includes(botUrl), '화면 답에 주소가 나왔어요');
    assert.ok(!text.includes(dataDir), '화면 답에 폴더 주소가 나왔어요');
    assert.ok(!text.includes('botUrl') && !text.includes('botKey') && !text.includes('ghToken'));
    const byId = Object.fromEntries(body.connections.map((c) => [c.id, c]));
    assert.strictEqual(byId['grok-bot'].state, 'on');
    assert.strictEqual(byId['grok-bot'].label, '설정 있음');
    assert.strictEqual(byId['grok-bot'].canTest, false);
    assert.strictEqual(byId['claude-api'].label, '있음');
    assert.strictEqual(byId['claude-api'].state, 'on');
    assert.strictEqual(byId['game-repo'].state, 'on');
    assert.strictEqual(byId['emp-folders'].state, 'off');
    assert.ok(byId['emp-folders'].people.some((p) => p.name === '없는직원' && p.ok === false));
    assert.strictEqual(byId['mcp-office'].state, 'on');
    assert.strictEqual(byId['mcp-office'].label, '코드에 있음');
    ['grok-drive', 'grok-github', 'grok-supabase', 'grok-ads', 'grok-x', 'grok-origin'].forEach((id) => {
      assert.strictEqual(byId[id].state, 'unknown');
      assert.strictEqual(byId[id].label, '그록 봇에서 관리');
      assert.strictEqual(byId[id].canTest, false);
    });
    assert.ok(body.features.some((f) => f.screen === '회사 홈' && f.name === '연결·기능'));
    const checked = await post(appPort, '/api/connections/check', { id: 'grok-bot', command: 'ping', url: botUrl });
    assert.strictEqual(checked.ok, true);
    assert.strictEqual(checked.item.canTest, false);
    assert.ok(!JSON.stringify(checked).includes(MARK));
    assert.strictEqual(hits, 0, '시험 확인이 봇에게 글을 보냈어요');
    const bad = await post(appPort, '/api/connections/check', { id: '없는-명령' });
    assert.strictEqual(bad.ok, false);
    const page = await getRaw(appPort, '/ui/connections.js');
    assert.strictEqual(page.status, 200);
    assert.ok(page.body.includes('data-links'));
    const missing = await getRaw(appPort, '/connections.json');
    assert.strictEqual(missing.status, 404);
    assert.ok(!log.includes(MARK), '서버 기록에 가짜 열쇠가 남았어요');
    console.log('연결·기능 시험 통과');
  } finally {
    clearTimeout(timer);
    stop();
    await new Promise((resolve) => hook.close(resolve));
    await sleep(100);
  }
}
main().catch((e) => { console.error(e && e.stack || e); process.exit(1); });
