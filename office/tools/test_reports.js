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
const driveFile = path.join(dataDir, 'drive-reports.json');
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
function post(port, pathname, body, headers) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body || {});
    const req = http.request({ host: '127.0.0.1', port, path: pathname, method: 'POST', headers: { 'content-type': 'application/json', 'content-length': Buffer.byteLength(data), ...(headers || {}) } }, (res) => {
      let d = ''; res.on('data', (c) => (d += c)); res.on('end', () => {
        let json = {};
        try { json = JSON.parse(d || '{}'); } catch (e) { return reject(e); }
        json._status = res.statusCode;
        resolve(json);
      });
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
  const src = fs.readFileSync(path.join(root, 'ui', 'reports.js'), 'utf8') + fs.readFileSync(path.join(root, 'ui', 'home.js'), 'utf8');
  const re = /#[0-9a-fA-F]{3,8}/g;
  const bad = [];
  let m;
  while ((m = re.exec(src))) {
    const ctx = src.slice(Math.max(0, m.index - 40), m.index);
    if (!/var\(--(?:bg|text|panel|line|muted|green|red|blue)\s*,\s*$/.test(ctx)) bad.push(ctx + m[0]);
  }
  assert.deepStrictEqual(bad, [], '색은 theme.css 이름만 써요');
  assert.ok(!fs.existsSync(path.join(root, 'data-public', 'reports.json')), '공개 보고 파일은 없어요');
  const server = fs.readFileSync(path.join(root, 'server.js'), 'utf8');
  assert.strictEqual(server.split("if (p === '/api/company/reports')").length - 1, 1, '보고 주소는 하나예요');
}

async function main() {
  checkColors();
  const hookPort = await freePort();
  const appPort = await freePort();
  const seen = [];
  let posts = 0;
  const ghComments = [];
  const hook = http.createServer((q, s) => {
    if (q.method === 'GET' && String(q.url || '').startsWith('/repos/meca12944/thor-like-game/issues/207/comments')) {
      s.setHeader('content-type', 'application/json');
      s.setHeader('x-ratelimit-remaining', '40');
      s.end(JSON.stringify(ghComments));
      return;
    }
    if (q.method !== 'POST' || q.url !== '/hook') { s.statusCode = 500; s.end('no'); return; }
    let d = '';
    q.on('data', (c) => (d += c));
    q.on('end', () => {
      posts += 1;
      let body = {};
      try { body = JSON.parse(d || '{}'); } catch (e) { body = {}; }
      seen.push(body);
      if (posts >= 2) { s.statusCode = 500; s.end('no'); return; }
      s.end('{"ok":true}');
    });
  });
  await new Promise((resolve) => hook.listen(hookPort, '127.0.0.1', resolve));

  fs.writeFileSync(driveFile, JSON.stringify([
    { id: 'rpt-same', time: '2026-11-11 16:22', target: 'AI 협력', command: '설계안 검토', lead: '그록봇 최적화 예전 이벨린', status: '완료', summary: ['설계안 3개를 좋다고 했어요.'], result: 'https://github.com/meca12944/thor-like-game/issues/207' },
  ]));
  const claudeReport = {
    id: 'claude-keep-1', empName: '팀장', time: '2026-11-11T05:00:00.000Z', task: '몹 점검 표 다시 뽑기',
    text: '표를 다시 뽑았어요.\napi_key=supersecret 이 줄은 숨겨요\n빨간 칸은 없어요.\n결과 https://github.com/meca12944/thor-like-game/issues/207',
    toBoss: true, needBoss: false, isError: false, stopped: false, keep: '그대로',
  };
  fs.writeFileSync(path.join(dataDir, 'state.json'), JSON.stringify({
    settings: { botUrl: `http://127.0.0.1:${hookPort}/hook`, botKey: secret, reportsFile: driveFile },
    reports: [
      claudeReport,
      { id: 'claude-skip', empName: '몬스터', time: '2026-11-11T06:00:00.000Z', task: '직원끼리', text: '사장님 카드가 아니에요.', toBoss: false, needBoss: true, isError: false },
      { id: 'claude-ask', empName: '팀장', time: '2026-11-11T04:00:00.000Z', task: '표 확인', text: '일을 끝냈어요.\n@전달 몬스터: 다시 봐 줘\n```js\nconsole.log("숨김")\n```\n빨간 칸은 없어요.', toBoss: true, needBoss: true, isError: false, stopped: false },
      { id: 'claude-stop', empName: '팀장', time: '2026-11-11T03:00:00.000Z', task: '멈춘 일', text: '중간에 멈췄어요.', toBoss: true, needBoss: false, isError: false, stopped: true },
      { id: 'claude-pref', empName: '팀장', time: '2026-11-11T02:00:00.000Z', task: '요약 있는 일', text: '@전달 효과: 빼 주세요\n본문은 쓰지 마요.', summary: ['요약 칸을 먼저 썼어요.'], status: '진행 중', toBoss: true, needBoss: false, isError: false },
    ],
  }));
  const kstStamp = (ms) => {
    const t = new Date(ms + 9 * 60 * 60 * 1000);
    const p = (n) => String(n).padStart(2, '0');
    return t.getUTCFullYear() + '-' + p(t.getUTCMonth() + 1) + '-' + p(t.getUTCDate()) + ' ' + p(t.getUTCHours()) + ':' + p(t.getUTCMinutes());
  };
  fs.writeFileSync(path.join(dataDir, 'company-reports.json'), JSON.stringify([
    { id: 'rpt-local-zero', time: '2026-11-11 16:30', target: '제로폰', command: '오늘 정책 확인해서 보고해', status: '접수', summary: ['명령을 받았어요.'], source: '그록' },
    { id: 'rpt-same', time: '2026-11-11 16:00', target: 'AI 협력', command: '옛 접수', status: '접수', summary: ['아직 접수'], source: '그록' },
    { id: 'rpt-old', time: '2026-11-11 10:00', target: '없는부서', command: '예전 일', status: '완료', summary: ['예전 파일에는 부서가 없어요.'] },
    { id: 'rpt-live', time: kstStamp(Date.now() - 60 * 1000), target: 'AI 협력·연결', dept: 'AI 협력·연결', command: '진행 기록 시험', status: '접수', summary: ['명령을 받았어요.'], source: '그록', cmdId: 'abcd1234' },
    { id: 'rpt-boss', time: kstStamp(Date.now() - 60 * 1000), target: '홍보', dept: '홍보', command: '확인 부탁', status: '접수', summary: ['명령을 받았어요.'], source: '그록', cmdId: 'boss5678' },
    { id: 'rpt-quiet', time: kstStamp(Date.now() - 20 * 60 * 1000), target: '제로폰', dept: '제로폰', command: '오래된 접수', status: '접수', summary: ['명령을 받았어요.'], source: '그록', cmdId: 'quiet001' },
  ]));

  const child = spawn(process.execPath, ['server.js'], {
    cwd: root,
    env: { ...process.env, OFFICE_DATA: dataDir, OFFICE_PORT: String(appPort), OFFICE_CLAUDE: 'false', OFFICE_GH_API: `http://127.0.0.1:${hookPort}` },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let log = '';
  child.stdout.on('data', (c) => (log += c));
  child.stderr.on('data', (c) => (log += c));
  const stop = () => { try { child.kill('SIGTERM'); } catch (e) { /* */ } };
  const timer = setTimeout(() => { stop(); console.error(log); process.exit(1); }, 40000);
  try {
    for (let i = 0; i < 50 && !log.includes('문 열림'); i++) {
      if (child.exitCode !== null) throw new Error('서버가 바로 끝났어요\n' + log);
      await sleep(100);
    }
    assert.ok(log.includes('문 열림'), log);
    await sleep(400);
    const before = readJson(path.join(dataDir, 'state.json')).reports.find((r) => r.id === 'claude-keep-1');
    const got = await getRaw(appPort, '/api/company/reports');
    assert.strictEqual(got.status, 200);
    const body = JSON.parse(got.body);
    assert.ok(Array.isArray(body.items), 'items 배열이어야 해요');
    const list = body.items;
    const ids = list.map((r) => r.id);
    assert.strictEqual(ids.filter((id) => id === 'rpt-same').length, 1);
    const same = list.find((r) => r.id === 'rpt-same');
    assert.strictEqual(same.status, '완료');
    assert.ok(same.summary.join(' ').includes('설계안 3개'));
    assert.ok(!same.summary.join(' ').includes('아직 접수'));
    const zero = list.find((r) => r.id === 'rpt-local-zero');
    assert.ok(zero && zero.status === '접수' && zero.dept === '제로폰');
    assert.ok(!ids.includes('claude-skip'));
    const ask = list.find((r) => r.id === 'claude-ask');
    assert.ok(ask && ask.status === '완료' && ask.needBoss === true);
    assert.ok(!ask.summary.join('\n').includes('@전달') && !ask.summary.join('\n').includes('숨김'));
    assert.strictEqual(list.find((r) => r.id === 'claude-stop').status, '문제 있음');
    const pref = list.find((r) => r.id === 'claude-pref');
    assert.strictEqual(pref.status, '진행 중');
    assert.strictEqual(pref.summary.join(''), '요약 칸을 먼저 썼어요.');
    const claude = list.find((r) => r.id === 'claude-keep-1');
    assert.strictEqual(claude.source, '클로드');
    assert.ok(!claude.summary.join('\n').includes('supersecret'));
    assert.ok(!JSON.stringify(list).includes(secret));
    assert.ok(!JSON.stringify(list).includes('그대로'));
    for (let i = 1; i < list.length; i++) {
      const prev = Date.parse(String(list[i - 1].time).replace(' ', 'T') + ':00+09:00');
      const cur = Date.parse(String(list[i].time).replace(' ', 'T') + ':00+09:00');
      assert.ok(prev >= cur, list[i - 1].time + ' / ' + list[i].time);
    }

    const n0 = readJson(path.join(dataDir, 'company-reports.json')).length;
    const empty = await post(appPort, '/api/bot/command', { target: '제로폰', command: '  ' });
    assert.strictEqual(empty.ok, false);
    assert.strictEqual(readJson(path.join(dataDir, 'company-reports.json')).length, n0);
    const ok = await post(appPort, '/api/bot/command', { target: '제로폰', command: '오늘 시세 확인해' });
    assert.strictEqual(ok.ok, true);
    assert.ok(seen[0].reportId);
    assert.strictEqual(seen[0].source, '알들 컴퍼니 명령창');
    assert.match(seen[0].cmdId, /^[0-9a-f]{8}$/);
    assert.ok(!JSON.stringify(seen[0]).includes(secret));
    const list2 = JSON.parse((await getRaw(appPort, '/api/company/reports')).body).items;
    const made = list2.find((r) => r.id === seen[0].reportId);
    assert.ok(made && made.status === '접수' && made.cmdId === seen[0].cmdId);
    const quiet = list2.find((r) => r.id === 'rpt-quiet');
    assert.ok(quiet && quiet.silent === true && quiet.status === '접수');
    const bad = await post(appPort, '/api/bot/command', { target: '홍보', command: '블로그 초안 써 줘' });
    assert.strictEqual(bad.ok, false);
    const failed = JSON.parse((await getRaw(appPort, '/api/company/reports')).body).items.find((r) => r.id === seen[1].reportId);
    assert.ok(failed && failed.status === '문제 있음');
    assert.ok(!failed.summary.join(' ').includes('127.0.0.1'));
    const pc = await post(appPort, '/api/bot/command', { target: 'AI 협력·연결', command: '현황판에서 보낸 일', source: 'PC' });
    assert.strictEqual(pc.ok, false);
    const pcHook = seen.find((row) => row && row.command === '현황판에서 보낸 일');
    assert.ok(pcHook, 'PC에서 보낸 일이 봇에게 가야 해요');
    assert.strictEqual(pcHook.source, 'PC');
    assert.strictEqual(pcHook.via, 'PC에서 보냄');
    assert.ok(!('via' in seen[0]), '예전 보내기에는 PC 표시가 없어요');
    const old = list.find((r) => r.id === 'rpt-old');
    assert.ok(old && old.dept === 'AI 협력·연결' && Array.isArray(old.artifacts) && old.artifacts.length === 0);
    const st = JSON.parse((await getRaw(appPort, '/api/state')).body);
    assert.deepStrictEqual(body.depts.map((d) => d.name), st.botTargets.depts.map((d) => d.name));
    const png = path.join(dataDir, 'shot.png');
    fs.writeFileSync(png, Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64'));
    const denied = await post(appPort, '/api/company/reports', { command: '몰래', dept: '홍보' }, { authorization: 'Bearer nope' });
    assert.strictEqual(denied._status, 401);
    assert.ok(!readJson(path.join(dataDir, 'company-reports.json')).some((r) => r.command === '몰래'));
    const posted = await post(appPort, '/api/company/reports', {
      dept: '홍보', target: '홍보', command: '결과물 시험', status: '완료',
      summary: ['요약을 적었어요.'],
      artifacts: [
        { kind: 'text', text: '포스터 문구를 다듬었어요.' },
        { kind: 'text', text: 'api_key=supersecret 숨김' },
        { kind: 'link', name: '합치기 부탁', url: 'https://github.com/meca12944/thor-like-game/pull/1' },
        { kind: 'photo', name: 'shot.png', path: png },
        { kind: 'file', name: 'memo.txt', path: path.join(dataDir, 'memo.txt') },
      ],
    }, { authorization: 'Bearer ' + secret });
    assert.strictEqual(posted.ok, true);
    fs.writeFileSync(path.join(dataDir, 'memo.txt'), 'memo');
    const rich = JSON.parse((await getRaw(appPort, '/api/company/reports')).body);
    const madeArt = rich.items.find((r) => r.command === '결과물 시험');
    assert.ok(madeArt && madeArt.dept === '홍보' && madeArt.status === '완료');
    const kinds = madeArt.artifacts.map((a) => a.kind).sort();
    assert.ok(kinds.indexOf('text') >= 0 && kinds.indexOf('link') >= 0 && kinds.indexOf('photo') >= 0 && kinds.indexOf('file') >= 0);
    assert.ok(!JSON.stringify(madeArt).includes('supersecret'));
    const photo = madeArt.artifacts.find((a) => a.kind === 'photo');
    assert.ok(photo && photo.src && photo.src.indexOf('/file?c=') === 0);
    const img = await getRaw(appPort, photo.src);
    assert.strictEqual(img.status, 200);
    assert.ok(img.type.indexOf('image/png') === 0);
    const hired = await post(appPort, '/api/employee', { name: '시험직원', role: '시험 역할', dept: 'zero', folder: dataDir });
    assert.strictEqual(hired.ok, true);
    await sleep(400);
    const beforeEmp = readJson(path.join(dataDir, 'state.json')).employees.find((e) => e.id === hired.id);
    const blank = await post(appPort, '/api/employee', { id: hired.id, rename: true, name: '  ', role: '다른 일' });
    assert.strictEqual(blank.ok, false);
    const renamed = await post(appPort, '/api/employee', { id: hired.id, rename: true, name: '안내담당', role: '고객 안내' });
    assert.strictEqual(renamed.ok, true);
    await sleep(400);
    const afterEmp = readJson(path.join(dataDir, 'state.json')).employees.find((e) => e.id === hired.id);
    assert.strictEqual(afterEmp.name, '안내담당');
    assert.strictEqual(afterEmp.role, '고객 안내');
    assert.strictEqual(afterEmp.folder, beforeEmp.folder);
    assert.strictEqual(afterEmp.sessionId, beforeEmp.sessionId);
    const other = await post(appPort, '/api/employee', { name: '다른직원', role: '다른 일', dept: 'promo', folder: dataDir });
    assert.strictEqual(other.ok, true);
    const dup = await post(appPort, '/api/employee', { id: hired.id, rename: true, name: '다른직원', role: '고객 안내' });
    assert.strictEqual(dup.ok, false);
    assert.strictEqual(readJson(path.join(dataDir, 'state.json')).employees.find((e) => e.id === hired.id).name, '안내담당');
    const nick = await post(appPort, '/api/bot/nick', { name: '제로폰 홈페이지', nick: '폰팀' });
    assert.strictEqual(nick.ok, true);
    const pub = JSON.parse((await getRaw(appPort, '/api/state')).body);
    assert.strictEqual(pub.botNicks['제로폰 홈페이지'], '폰팀');
    assert.ok(pub.botTargets.bots.some((b) => b.name === '제로폰 홈페이지'));
    const iso = (ms) => new Date(ms).toISOString();
    const cmt = (id, ms, body) => ({ id, created_at: iso(ms), body, html_url: 'https://github.com/meca12944/thor-like-game/issues/207#issuecomment-' + id });
    const nowMs = Date.now();
    ghComments.push(
      cmt(1, nowMs - 5 * 60 * 1000, '[그록] 안녕'),
      cmt(2, nowMs - 4 * 60 * 1000, '[그록 상태] [cmd:abcd1234] 접수함'),
      cmt(3, nowMs - 3 * 60 * 1000, '[그록 상태] [cmd:abcd1234] 그록 답안 작성 중\n그록 안: 표부터 볼게요'),
      cmt(4, nowMs - 2 * 60 * 1000, '[그록 상태] [cmd:abcd1234] 문제 있음\napi_key=supersecret'),
      cmt(5, nowMs - 60 * 1000, '[그록 상태] [cmd:abcd1234] 클로드와 토의 중 (2/3)\n그록 안: 짧게\n클로드 의견: 좋아요\n합의: 이렇게 가요'),
      cmt(6, nowMs - 30 * 1000, '[그록 상태] [cmd:boss5678] 사장님 확인 필요\n합의: 사장님이 봐 주세요'),
      cmt(7, nowMs - 20 * 1000, '[그록 상태] [cmd:nope9999] 완료\n없는 번호'),
      cmt(8, nowMs - 10 * 1000, '[그록 상태] [cmd:abcd1234] 알 수 없는 단계'),
    );
    await getRaw(appPort, '/api/coop/chat?refresh=1');
    await sleep(1000);
    const moved = JSON.parse((await getRaw(appPort, '/api/company/reports')).body).items;
    const live = moved.find((r) => r.id === 'rpt-live');
    assert.ok(live && live.status === '진행 중' && live.stage === '클로드와 토의 중 (2/3)');
    assert.ok(live.history && live.history.length === 4);
    assert.strictEqual(live.history[0].stage, '접수함');
    assert.strictEqual(live.history[3].stage, '클로드와 토의 중 (2/3)');
    assert.ok(live.summary.join(' ').includes('합의: 이렇게 가요'));
    assert.ok(live.history.some((h) => h.stage === '문제 있음' && !(h.notes || []).join(' ').includes('supersecret')));
    assert.ok(!JSON.stringify(live).includes('supersecret'));
    assert.ok(!JSON.stringify(live).includes('알 수 없는 단계'));
    const boss = moved.find((r) => r.id === 'rpt-boss');
    assert.ok(boss && boss.needBoss === true && boss.status === '진행 중' && boss.stage === '사장님 확인 필요');
    assert.ok(!moved.some((r) => r.cmdId === 'nope9999'));
    const chat = JSON.parse((await getRaw(appPort, '/api/coop/chat')).body);
    assert.ok((chat.items || []).some((c) => c.kind === 'talk' && String(c.text || '').includes('안녕')));
    assert.ok(!(chat.items || []).some((c) => c.kind !== 'cmd' && String(c.text || '').includes('[그록 상태]')));
    const bundle = (chat.items || []).find((c) => c.kind === 'cmd' && c.cmdId === 'abcd1234');
    assert.ok(bundle && bundle.command === '진행 기록 시험' && bundle.history.length === 4 && bundle.dept === 'AI 협력·연결');
    const ordered = await post(appPort, '/api/order', { to: hired.id, text: '부서 일 시험', dept: '제로폰' });
    assert.strictEqual(ordered.ok, true);
    const queued = JSON.parse((await getRaw(appPort, '/api/company/reports')).body).items.find((r) => r.command === '부서 일 시험');
    assert.ok(queued && queued.status === '접수' && queued.dept === '제로폰');
    await sleep(500);
    const after = readJson(path.join(dataDir, 'state.json')).reports.find((r) => r.id === 'claude-keep-1');
    assert.deepStrictEqual(after, before);
    console.log('보고 창 시험 통과');
  } finally {
    clearTimeout(timer);
    stop();
    await new Promise((resolve) => hook.close(resolve));
    await sleep(100);
  }
}
main().catch((e) => { console.error(e && e.stack || e); process.exit(1); });
