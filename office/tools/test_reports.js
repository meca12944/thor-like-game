// 보고 창 시험. office/ 에서: node tools/test_reports.js
'use strict';
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const assert = require('assert');
const { spawn } = require('child_process');

const root = path.join(__dirname, '..');
const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'office-rep-'));
const secret = 'test-key-do-not-leak';

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
function readJson(p) { return JSON.parse(fs.readFileSync(p, 'utf8')); }
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
function getRaw(port, pathname) {
  return new Promise((resolve, reject) => {
    http.get({ host: '127.0.0.1', port, path: pathname }, (res) => {
      let d = ''; res.on('data', (c) => (d += c)); res.on('end', () => resolve({ status: res.statusCode, type: res.headers['content-type'] || '', body: d }));
    }).on('error', reject);
  });
}

function checkColors() {
  const src = fs.readFileSync(path.join(root, 'ui', 'reports.js'), 'utf8');
  const re = /#[0-9a-fA-F]{3,8}/g;
  const bad = [];
  let m;
  while ((m = re.exec(src))) {
    const ctx = src.slice(Math.max(0, m.index - 40), m.index);
    if (!/var\(--[A-Za-z0-9-]+\s*,\s*$/.test(ctx)) bad.push(ctx + m[0]);
  }
  assert.deepStrictEqual(bad, [], 'reports.js 색은 var(--이름, 기본값)만 써요');
  assert.ok(src.includes('function renderReports'), 'renderReports 가 있어야 해요');
}

function checkPublicFile() {
  const list = readJson(path.join(root, 'data-public', 'reports.json'));
  assert.ok(Array.isArray(list) && list.length >= 2, '공개 보고가 2개 이상이어야 해요');
  const text = JSON.stringify(list);
  assert.ok(!/bearer|api[_-]?key|webhook|password|token|시크릿/i.test(text), '공개 보고에 비밀이 있으면 안 돼요');
  const a = list[0];
  assert.strictEqual(a.id, 'rpt-20261111-1622-design');
  assert.strictEqual(a.time, '2026-11-11 16:22');
  assert.strictEqual(a.source, '그록');
  assert.strictEqual(a.status, '완료');
  assert.strictEqual(a.target, 'AI 협력');
  assert.ok(a.summary.length >= 1 && a.summary.length <= 3);
  assert.ok(/^https:\/\//.test(a.where));
}

async function main() {
  checkColors();
  checkPublicFile();
  const hookPort = await freePort();
  const appPort = await freePort();
  const seen = [];
  let posts = 0;
  const hook = http.createServer((q, s) => {
    if (q.method !== 'POST' || q.url !== '/hook') { s.statusCode = 500; s.end('no'); return; }
    let d = '';
    q.on('data', (c) => (d += c));
    q.on('end', () => {
      posts += 1;
      let body = {};
      try { body = JSON.parse(d || '{}'); } catch (e) { body = { raw: d }; }
      seen.push(body);
      if (posts >= 2) { s.statusCode = 500; s.end('no'); return; }
      s.setHeader('content-type', 'application/json');
      s.end('{"ok":true}');
    });
  });
  await new Promise((resolve) => hook.listen(hookPort, '127.0.0.1', resolve));

  const claudeReport = {
    id: 'claude-keep-1',
    emp: 'e1',
    empName: '팀장',
    time: '2026-11-11T05:00:00.000Z',
    from: '사장님',
    task: '몹 점검 표 다시 뽑기',
    text: '표를 다시 뽑았어요.\napi_key=supersecret 이 줄은 숨겨요\n빨간 칸은 없어요.\n결과 https://github.com/meca12944/thor-like-game/issues/207',
    files: [],
    isError: false,
    needBoss: false,
    toBoss: true,
    asks: [],
    read: false,
    forwards: [],
    denials: [],
    keep: '그대로',
  };
  fs.writeFileSync(path.join(dataDir, 'state.json'), JSON.stringify({
    settings: { botUrl: `http://127.0.0.1:${hookPort}/hook`, botKey: secret },
    reports: [claudeReport],
  }));
  fs.writeFileSync(path.join(dataDir, 'company-reports.json'), JSON.stringify([
    { id: 'rpt-local-zero', time: '2026-11-11 16:30', target: '제로폰', command: '오늘 정책 확인해서 보고해', lead: '', status: '접수', summary: ['명령을 받았어요.'], source: '그록' },
    { id: 'rpt-20261111-1622-design', time: '2026-11-11 16:00', target: 'AI 협력', command: '옛 접수', lead: '', status: '접수', summary: ['아직 접수'], source: '그록' },
  ]));

  const child = spawn(process.execPath, ['server.js'], {
    cwd: root,
    env: {
      ...process.env,
      OFFICE_DATA: dataDir,
      OFFICE_PORT: String(appPort),
      OFFICE_CLAUDE: 'false',
      OFFICE_GH_API: `http://127.0.0.1:${hookPort}`,
      OFFICE_REPORTS_URL: `http://127.0.0.1:${hookPort}/reports.json`,
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let log = '';
  child.stdout.on('data', (c) => (log += c));
  child.stderr.on('data', (c) => (log += c));
  const stop = () => { try { child.kill('SIGTERM'); } catch (e) { /* */ } };
  const timer = setTimeout(() => { stop(); console.error(log); console.error('시험이 너무 오래 걸렸어요'); process.exit(1); }, 25000);

  try {
    const block = fs.readFileSync(path.join(root, 'server.js'), 'utf8').split('// ── 그록: 보고 창 ──')[1];
    assert.ok(block, '보고 창 덩어리가 파일 맨 쪽에 있어야 해요');
    assert.ok(!/state\.reports\s*=/.test(block), '직원 보고 목록을 바꾸면 안 돼요');
    assert.ok(!/state\.reports\.(unshift|push|splice|pop|shift)\s*\(/.test(block));
    assert.ok(!/\br\.status\s*=/.test(block), '직원 보고 상태를 바꾸면 안 돼요');

    for (let i = 0; i < 50; i++) {
      if (log.includes('문 열림')) break;
      if (child.exitCode !== null) throw new Error('서버가 바로 끝났어요\n' + log);
      await sleep(100);
    }
    assert.ok(log.includes('문 열림'), '서버가 안 열렸어요\n' + log);
    await sleep(400);
    const before = readJson(path.join(dataDir, 'state.json')).reports.find((r) => r.id === 'claude-keep-1');
    assert.ok(before && before.keep === '그대로' && before.status === undefined);

    const got = await getRaw(appPort, '/api/company/reports');
    assert.strictEqual(got.status, 200);
    assert.ok(got.type.includes('json'));
    const list = JSON.parse(got.body);
    assert.ok(Array.isArray(list), '보고 목록은 배열이에요');
    const ids = list.map((r) => r.id);
    assert.strictEqual(ids.filter((id) => id === 'rpt-20261111-1622-design').length, 1, '같은 번호는 한 장만');
    const design = list.find((r) => r.id === 'rpt-20261111-1622-design');
    assert.strictEqual(design.status, '완료', '공개 보고 상태가 접수를 이겨야 해요');
    assert.ok(design.summary.join(' ').includes('설계안 3개'));
    assert.ok(!design.summary.join(' ').includes('아직 접수'));
    assert.strictEqual(design.dept, 'AI 협력·연결');
    assert.strictEqual(design.source, '그록');
    const zero = list.find((r) => r.id === 'rpt-local-zero');
    assert.ok(zero && zero.status === '접수' && zero.dept === '제로폰');
    const claude = list.find((r) => r.id === 'claude-keep-1');
    assert.ok(claude, '클로드 직원 보고도 목록에 있어야 해요');
    assert.strictEqual(claude.source, '클로드');
    assert.strictEqual(claude.status, '완료');
    assert.strictEqual(claude.target, '게임 필멸자');
    assert.ok(claude.summary.join('\n').includes('표를 다시 뽑았어요'));
    assert.ok(!claude.summary.join('\n').includes('supersecret'));
    assert.ok(!JSON.stringify(list).includes(secret));
    assert.ok(!JSON.stringify(list).includes('그대로'));
    assert.strictEqual(claude.where, 'https://github.com/meca12944/thor-like-game/issues/207');
    for (let i = 1; i < list.length; i++) {
      const prev = Date.parse(list[i - 1].time.replace(' ', 'T') + ':00+09:00');
      const cur = Date.parse(list[i].time.replace(' ', 'T') + ':00+09:00');
      assert.ok(prev >= cur, '최신이 위예요: ' + list[i - 1].time + ' / ' + list[i].time);
    }

    const localBefore = readJson(path.join(dataDir, 'company-reports.json')).length;
    const empty = await post(appPort, '/api/bot/command', { target: '제로폰', command: '   ' });
    assert.strictEqual(empty.ok, false);
    assert.strictEqual(readJson(path.join(dataDir, 'company-reports.json')).length, localBefore, '빈 명령은 접수가 생기면 안 돼요');

    const ok = await post(appPort, '/api/bot/command', { target: '제로폰', command: '오늘 시세 확인해' });
    assert.strictEqual(ok.ok, true);
    assert.strictEqual(seen.length, 1);
    assert.ok(seen[0].reportId, '보고서 번호를 함께 보내야 해요');
    assert.strictEqual(seen[0].source, '알들 컴퍼니 명령창');
    assert.strictEqual(seen[0].target, '제로폰');
    assert.ok(!JSON.stringify(seen[0]).includes(secret));
    const again = await getRaw(appPort, '/api/company/reports');
    const list2 = JSON.parse(again.body);
    const made = list2.find((r) => r.id === seen[0].reportId);
    assert.ok(made && made.status === '접수' && made.source === '그록');
    assert.strictEqual(made.command, '오늘 시세 확인해');
    assert.ok(!JSON.stringify(list2).includes(secret));
    const saved = JSON.stringify(readJson(path.join(dataDir, 'company-reports.json')));
    assert.ok(saved.includes(seen[0].reportId));
    assert.ok(!saved.includes(secret));

    const bad = await post(appPort, '/api/bot/command', { target: '홍보', command: '블로그 초안 써 줘' });
    assert.strictEqual(bad.ok, false);
    assert.strictEqual(seen.length, 2);
    const list3 = JSON.parse((await getRaw(appPort, '/api/company/reports')).body);
    const failed = list3.find((r) => r.id === seen[1].reportId);
    assert.ok(failed && failed.status === '문제 있음');
    assert.ok(failed.summary.join(' ').includes('넘기지 못했어요'));
    assert.ok(!failed.summary.join(' ').includes('127.0.0.1'));

    await sleep(500);
    const after = readJson(path.join(dataDir, 'state.json')).reports.find((r) => r.id === 'claude-keep-1');
    assert.deepStrictEqual(after, before, '직원 보고 원본은 그대로예요');
    console.log('보고 창 시험 통과');
  } finally {
    clearTimeout(timer);
    stop();
    await new Promise((resolve) => hook.close(resolve));
    await sleep(100);
  }
}

main().catch((e) => { console.error(e && e.stack || e); process.exit(1); });
