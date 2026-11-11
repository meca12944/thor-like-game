// 연결·기능 화면이 읽는 상태. 열쇠·주소 값은 답과 기록에 넣지 않아요.
'use strict';
const fs = require('fs');
const path = require('path');
const { execFile, spawn } = require('child_process');

function createConnStatus(deps) {
  const cache = { claude: null, github: null, githubToken: null };

  function settings() {
    const state = deps.getState() || {};
    return state.settings || {};
  }
  function filled(v) {
    return typeof v === 'string' ? v.trim().length > 0 : !!v;
  }
  function clip(v, n) {
    return String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
  }
  function secretBag() {
    const s = settings();
    const env = process.env || {};
    return [s.botUrl, s.botKey, s.ghToken, s.xaiKey, s.pixellabKey, env.ANTHROPIC_API_KEY, env.ANTHROPIC_AUTH_TOKEN, env.CLAUDE_API_KEY];
  }
  function hideSecrets(value) {
    let t = String(value || '');
    for (const raw of secretBag()) {
      const v = raw == null ? '' : String(raw);
      if (v.trim().length >= 6) t = t.split(v).join('');
    }
    t = t.replace(/https?:\/\/\S+/gi, '');
    t = t.replace(/\b(?:gh[opsur]_|github_pat_|sk-ant-|xai-)[A-Za-z0-9_\-]*/g, '');
    t = t.replace(/\s{2,}/g, ' ').trim();
    return t;
  }
  function clean(value, n, fallback) {
    const t = hideSecrets(clip(value, n));
    return t || fallback || '';
  }
  function loadDoc() {
    try {
      const raw = fs.readFileSync(path.join(deps.ROOT, 'connections.json'), 'utf8').replace(/^\uFEFF/, '');
      const doc = JSON.parse(raw);
      return {
        connections: Array.isArray(doc.connections) ? doc.connections : [],
        features: Array.isArray(doc.features) ? doc.features : [],
        error: '',
      };
    } catch (e) {
      return { connections: [], features: [], error: '연결 목록 파일을 못 읽었어요.' };
    }
  }
  function fileInsideRoot(rel) {
    const norm = path.normalize(String(rel || '')).replace(/^(\.\.(\/|\\|$))+/, '');
    if (!norm || norm === '.' || path.isAbsolute(norm)) return '';
    const root = path.resolve(deps.ROOT);
    const full = path.resolve(root, norm);
    if (full !== root && !full.startsWith(root + path.sep)) return '';
    return full;
  }
  function runFile(cmd, args, timeout) {
    return new Promise((resolve) => {
      let settled = false;
      const done = (row) => { if (!settled) { settled = true; resolve(row); } };
      try {
        execFile(cmd, args, { windowsHide: true, timeout: timeout || 8000, maxBuffer: 32 * 1024 }, (err, out, errOut) => {
          done({
            ok: !err,
            missing: !!(err && err.code === 'ENOENT'),
            text: (String(out || '') + '\n' + String(errOut || '')).slice(0, 2000),
          });
        });
      } catch (e) {
        done({ ok: false, missing: true, text: '' });
      }
    });
  }
  function runClaude(args) {
    const claude = deps.getClaude() || {};
    return new Promise((resolve) => {
      if (!claude.path) return resolve({ ok: false, missing: true, text: '' });
      let settled = false;
      const done = (row) => { if (!settled) { settled = true; resolve(row); } };
      let child;
      try {
        const quote = typeof deps.quoteIf === 'function' ? deps.quoteIf : (x) => x;
        child = spawn(quote(claude.path), args.map(quote), { shell: !!claude.useShell, windowsHide: true });
      } catch (e) {
        return done({ ok: false, missing: true, text: '' });
      }
      const timer = setTimeout(() => { try { child.kill(); } catch (e) { /* */ } done({ ok: false, missing: false, text: '' }); }, 12000);
      let out = '';
      let err = '';
      if (child.stdout) child.stdout.on('data', (d) => { if (out.length < 2500) out += d; });
      if (child.stderr) child.stderr.on('data', (d) => { if (err.length < 2500) err += d; });
      child.on('error', () => { clearTimeout(timer); done({ ok: false, missing: true, text: '' }); });
      child.on('close', (code) => {
        clearTimeout(timer);
        done({ ok: code === 0, missing: false, text: (out + '\n' + err).slice(0, 2500) });
      });
    });
  }
  function loginFrom(text) {
    const s = String(text || '').toLowerCase();
    if (!s.trim()) return null;
    if (/unknown command|not a valid|unrecognized/.test(s)) return null;
    if (/not logged|logged out|please log in|login required/.test(s)) return false;
    if (/"loggedin"\s*:\s*false/.test(s)) return false;
    if (/"loggedin"\s*:\s*true/.test(s) || /logged in/.test(s)) return true;
    return null;
  }
  function safeVersion(v) {
    const s = String(v || '').trim().split('\n')[0].slice(0, 60);
    if (!s || /key|token|secret|sk-|http/i.test(s)) return '';
    return s;
  }
  function claudeOff() {
    return { state: 'off', label: '안 됨', detail: '이 컴퓨터에서 클로드 코드를 못 찾았어요. 폴더의 「처음_설치」를 두 번 누르고 로그인하세요.' };
  }
  function claudeSync() {
    const c = deps.getClaude() || {};
    if (c.ok) {
      if (cache.claude) return cache.claude;
      return { state: 'unknown', label: '확인 안 됨', detail: '프로그램은 있어요. 로그인됐는지는 아직 확인하지 않았어요. 다시 확인을 누르세요.' };
    }
    if (!c.error) return { state: 'unknown', label: '확인 안 됨', detail: '아직 살펴보는 중이에요. 잠시 뒤 다시 확인을 누르세요.' };
    return claudeOff();
  }
  async function claudeFresh() {
    if (typeof deps.detectClaude === 'function') await deps.detectClaude();
    const c = deps.getClaude() || {};
    if (!c.ok) { cache.claude = null; return claudeSync(); }
    const probe = await runClaude(['auth', 'status']);
    const login = probe.missing ? null : loginFrom(probe.text);
    const ver = safeVersion(c.version);
    let row;
    if (login === true) {
      row = { state: 'on', label: '연결됨', detail: '깔려 있고 로그인돼 있어요.' + (ver ? ' 판: ' + ver + '.' : '') };
    } else if (login === false) {
      row = { state: 'off', label: '안 됨', detail: '프로그램은 깔려 있어요. 로그인은 안 돼 있어요. 명령 창에서 클로드를 켜고 로그인한 뒤, 다시 확인을 누르세요.' };
    } else {
      row = { state: 'unknown', label: '확인 안 됨', detail: '프로그램은 있어요. 로그인됐는지는 확인하지 못했어요.' };
    }
    cache.claude = row;
    return row;
  }
  function ghMode(text, ok, missing) {
    if (missing) return 'missing';
    if (ok) return 'in';
    const s = String(text || '');
    if (/Logged in to/i.test(s)) return 'in';
    if (/not logged|no oauth|failed to log|authentication/i.test(s)) return 'out';
    if (/not found|unknown command/i.test(s)) return 'missing';
    return 'unknown';
  }
  function githubRow(hasToken, mode) {
    if (hasToken && mode === 'in') return { state: 'on', label: '연결됨', detail: '깃허브 프로그램에 로그인돼 있고, 저장된 열쇠도 있어요. 값은 안 보여요.' };
    if (hasToken) return { state: 'on', label: '연결됨', detail: '저장된 열쇠가 있어요. 값은 화면에 안 나와요.' };
    if (mode === 'in') return { state: 'on', label: '연결됨', detail: '이 컴퓨터의 깃허브 프로그램에 로그인돼 있어요.' };
    if (mode === 'unknown') return { state: 'unknown', label: '확인 안 됨', detail: '깃허브 프로그램 상태를 확인하지 못했어요. 열쇠 값은 보지 않아요.' };
    return { state: 'off', label: '안 됨', detail: '깃허브 프로그램 로그인도 없고, 저장된 열쇠도 없어요. 명령 창에서 로그인하거나, 맨 위 연결 창에 열쇠를 넣으세요.' };
  }
  function githubSync() {
    const hasToken = filled(settings().ghToken);
    if (cache.github && cache.githubToken === hasToken) return cache.github;
    if (hasToken) return githubRow(true, 'skip');
    return { state: 'unknown', label: '확인 안 됨', detail: '아직 깃허브 로그인을 확인하지 않았어요. 다시 확인을 누르세요. 열쇠 값은 보지 않아요.' };
  }
  async function githubFresh() {
    const hasToken = filled(settings().ghToken);
    const r = await runFile('gh', ['auth', 'status'], 8000);
    const mode = ghMode(r.text, r.ok, r.missing);
    const row = githubRow(hasToken, mode);
    cache.github = row;
    cache.githubToken = hasToken;
    return row;
  }
  function apiStatus() {
    const env = process.env || {};
    const on = ['ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'CLAUDE_API_KEY'].some((n) => filled(env[n]));
    if (on) return { state: 'on', label: '있음', detail: '모델을 부르는 열쇠가 이 프로그램 환경에 있어요. 값은 화면과 기록에 안 나와요. 클로드 코드 로그인과는 따로예요.' };
    return { state: 'off', label: '없음', detail: '이 프로그램 환경에는 열쇠가 없어요. 보통은 괜찮아요. 클로드 코드에 로그인하면 그 구독으로 일해요.' };
  }
  function botStatus() {
    const s = settings();
    if (filled(s.botUrl) && filled(s.botKey)) {
      return { state: 'on', label: '설정 있음', detail: '명령 중계 설정이 저장돼 있어요. 주소와 열쇠는 화면에 안 나와요. 시험 보내기 단추는 없어요. 시험 글이 직원에게 진짜 일로 들어갈 수 있어요.' };
    }
    return { state: 'off', label: '없음', detail: '주소와 열쇠가 둘 다 있어야 해요. 맨 위 연결 창의 그록 봇에서 저장하세요. 값은 여기 안 나와요. 시험 보내기는 하지 않아요.' };
  }
  function gameStatus() {
    const p = String(settings().gameRepo || '').trim();
    if (!p) return { state: 'off', label: '안 됨', detail: '게임 폴더가 아직 정해지지 않았어요. 맨 위 연결 창에서 위치를 정하세요.' };
    let ok = false;
    let git = false;
    try {
      ok = fs.existsSync(p) && fs.statSync(p).isDirectory();
      git = ok && fs.existsSync(path.join(p, '.git'));
    } catch (e) { ok = false; }
    if (!ok) return { state: 'off', label: '안 됨', detail: '정해 둔 폴더를 찾지 못했어요. 연결 창에서 위치를 다시 정하세요.' };
    return { state: 'on', label: '연결됨', detail: git ? '게임 폴더가 있고, 깃 저장소도 있어요.' : '게임 폴더는 있어요. 깃 저장소 표시는 없어요.' };
  }
  function empStatus() {
    const list = ((deps.getState() || {}).employees || []).slice(0, 40).map((e) => {
      let ok = false;
      try { ok = !!(e && e.folder && fs.existsSync(e.folder) && fs.statSync(e.folder).isDirectory()); } catch (err) { ok = false; }
      const dept = typeof deps.empDeptName === 'function' ? deps.empDeptName(e) : '';
      return { name: clip(e && e.name, 40) || '이름 없음', dept: clip(dept, 40), ok };
    });
    if (!list.length) return { state: 'off', label: '안 됨', detail: '아직 직원 폴더가 없어요. 부서 화면의 「만들기」를 누르거나, 홈의 「부서마다 클로드 팀 만들기」를 누르세요.', people: [] };
    const bad = list.filter((x) => !x.ok).length;
    if (!bad) return { state: 'on', label: '연결됨', detail: '직원 폴더 ' + list.length + '개가 모두 있어요.', people: list };
    return { state: 'off', label: '안 됨', detail: '직원 ' + list.length + '명 중 ' + bad + '명 폴더가 없어요.', people: list };
  }
  function fileStatus(rel) {
    const full = fileInsideRoot(rel);
    if (!full) return { state: 'unknown', label: '확인 안 됨', detail: '파일 위치를 확인하지 못했어요.' };
    if (fs.existsSync(full)) return { state: 'on', label: '코드에 있음', detail: '이 프로그램 안에 허락 창구가 들어 있어요. 직원이 위험한 일을 하기 전에 사장님께 물어요.' };
    return { state: 'off', label: '안 됨', detail: '허락 창구 파일을 못 찾았어요.' };
  }
  function grokStatus() {
    return { state: 'unknown', label: '그록 봇에서 관리', detail: '이 컴퓨터에서는 켜졌는지 확인하지 않아요. 그록 봇이 관리해요.' };
  }
  function unknownStatus() {
    return { state: 'unknown', label: '확인 안 됨', detail: '이 항목은 이 프로그램이 아직 확인하지 못해요.' };
  }
  function statusSync(item) {
    const kind = String(item && item.check || '');
    if (kind === 'claude') return claudeSync();
    if (kind === 'bot') return botStatus();
    if (kind === 'github') return githubSync();
    if (kind === 'claude-api') return apiStatus();
    if (kind === 'game-repo') return gameStatus();
    if (kind === 'emp-folders') return empStatus();
    if (kind === 'file') return fileStatus(item.file);
    if (kind === 'grok') return grokStatus();
    return unknownStatus();
  }
  async function statusFresh(item) {
    const kind = String(item && item.check || '');
    if (kind === 'claude') return claudeFresh();
    if (kind === 'github') return githubFresh();
    return statusSync(item);
  }
  function pack(item, status) {
    if (!item || !/^[a-z0-9-]{1,40}$/.test(String(item.id || ''))) return null;
    const st = status && (status.state === 'on' || status.state === 'off') ? status.state : 'unknown';
    const people = Array.isArray(status && status.people) ? status.people.slice(0, 40).map((p) => ({
      name: clean(p.name, 40, '이름 없음'),
      dept: clean(p.dept, 40, ''),
      ok: !!p.ok,
    })) : [];
    const connect = item.connect === 'dialog' || item.connect === 'none' ? item.connect : 'check';
    return {
      id: String(item.id),
      icon: clean(item.icon || '🔗', 8, '🔗'),
      name: clean(item.name, 40, '연결'),
      line: clean(item.line, 220, ''),
      group: clean(item.group, 40, ''),
      steps: (Array.isArray(item.steps) ? item.steps : []).slice(0, 8).map((s) => clean(s, 300, '')).filter(Boolean),
      connect,
      canTest: false,
      state: st,
      label: clean(status && status.label, 40, st === 'on' ? '연결됨' : st === 'off' ? '안 됨' : '확인 안 됨'),
      detail: clean(status && status.detail, 400, '확인했어요.'),
      people,
    };
  }
  function packFeature(f) {
    if (!f || !String(f.name || '').trim()) return null;
    return {
      screen: clean(f.screen, 40, '화면'),
      name: clean(f.name, 40, ''),
      what: clean(f.what, 240, ''),
      when: clean(f.when, 240, ''),
    };
  }
  function snapshot() {
    const doc = loadDoc();
    return {
      ok: !doc.error,
      error: doc.error,
      legend: '초록은 이 프로그램이 직접 확인한 상태예요. 회색은 여기서 확인하지 못해요.',
      connections: doc.connections.map((item) => pack(item, statusSync(item))).filter(Boolean),
      features: doc.features.map(packFeature).filter(Boolean),
    };
  }
  async function check(id) {
    const sid = String(id || '');
    if (!/^[a-z0-9-]{1,40}$/.test(sid)) return { ok: false, error: '어떤 연결인지 모르겠어요.' };
    const doc = loadDoc();
    const item = doc.connections.find((x) => x && x.id === sid);
    if (!item) return { ok: false, error: '목록에 없는 연결이에요.' };
    const row = pack(item, await statusFresh(item));
    if (!row) return { ok: false, error: '이 연결은 보여 줄 수 없어요.' };
    return { ok: true, item: row };
  }
  return { snapshot, check };
}

module.exports = { createConnStatus };
