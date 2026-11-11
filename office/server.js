// 클로드 작업장 (옛 이름: 클로드 회사) — 본체
// 사장님 PC에서 돌아가는 작은 서버. 직원(클로드 코드)들에게 일을 시키고, 보고·허락 요청을 한 화면에 모은다.
// 따로 설치할 것 없음 (Node.js 기본 기능만 씀).
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { spawn, execFile } = require('child_process');

const ROOT = __dirname;
const DATA = process.env.OFFICE_DATA || path.join(ROOT, 'data');
const STATE_FILE = path.join(DATA, 'state.json');
const IS_WIN = process.platform === 'win32';
fs.mkdirSync(path.join(DATA, 'prompts'), { recursive: true });
fs.mkdirSync(path.join(DATA, 'logs'), { recursive: true });

// ───────── 저장 ─────────
const DEFAULT_RULES = ['Read', 'Glob', 'Grep', 'Edit', 'Write', 'NotebookEdit', 'TodoWrite', 'WebSearch',
  'Bash(git status:*)', 'Bash(git log:*)', 'Bash(git diff:*)', 'Bash(git show:*)', 'Bash(git branch:*)',
  'Bash(grok:*)', 'Bash(ls:*)', 'Bash(dir:*)', 'Bash(cat:*)', 'Bash(head:*)', 'Bash(tail:*)', 'Bash(wc:*)', 'Bash(pwd:*)', 'Bash(echo:*)'];
let state = {
  settings: { port: Number(process.env.OFFICE_PORT) || 7788, claudeCmd: process.env.OFFICE_CLAUDE || 'claude', gameRepo: '', workspace: '', defaultMode: 'auto', maxHops: 6, grokDir: '', xaiKey: '', grokBudget: 5, grokMode: 'bot', botUrl: '', botKey: '', botTarget: 'AI 협력', ghToken: '', coopIssue: 207, companyUrl: 'https://cursor.com/canvas/store-6b845294-f0e8-4bad-ba45-aefe07f68d6a/0ced3cdd-d091-452c-94b1-bb0a223f0807' },
  rules: DEFAULT_RULES.slice(),
  employees: [],
  reports: [],
  grokLog: [],
  botHistory: [],
};
// 알들 컴퍼니 명령창(그록 command.ps1)과 같은 대상 목록 — 그록과 같이 고침 (공동 개발)
const BOT_TARGETS = ["전체", "제로폰", "블로그", "마케팅 홍보", "경영지원", "STCO 온라인 쇼핑몰", "STCO 오프라인", "게임 필멸자", "영상 제작", "AI 협력", "제로폰 홈페이지", "제로폰 홈페이지2", "제로폰 홈페이지3", "제로폰 홈페이지4", "제로폰 개통 안내", "제로폰 홍보 · 제로폰 관리", "네이버 판매자센터", "간판디자인", "폰클매니저 미래 오케이", "알들폰 해피콜 시스템", "알들폰 고객 안내사항 제작", "원오프 셋업 생산", "음봉일지", "철강주 동국제강 이익추정", "STCO 인동점 SEO·홍보", "STCO 인동점 포스&홈페이지", "STCO 인동점 포스&홈페이지 2", "게임만들기", "게임 스토리 작가", "게임 일러스트 작가", "히로인 모션 - 유나"];
try { const s = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')); state = { ...state, ...s, settings: { ...state.settings, ...(s.settings || {}) } }; } catch (e) { /* 처음 */ }
if (process.env.OFFICE_PORT) state.settings.port = Number(process.env.OFFICE_PORT);
if (process.env.OFFICE_CLAUDE) state.settings.claudeCmd = process.env.OFFICE_CLAUDE;
if (!state.rules.includes('Bash(grok:*)')) state.rules.push('Bash(grok:*)');
state.grokLog = state.grokLog || [];
state.botHistory = state.botHistory || [];
// 11-11 그록 봇 연결이 생김: 예전 기본값(반자동)이던 판은 봇 연결로 (봇 설정이 없으면 저절로 반자동)
if (!state.settings.grokV2) { if (state.settings.grokMode === 'paste') state.settings.grokMode = 'bot'; state.settings.grokV2 = true; }
if (!state.settings.gameRepo) {
  const guess = path.join(process.env.USERPROFILE || process.env.HOME || '', 'thor-like-game');
  if (fs.existsSync(path.join(guess, '.git'))) state.settings.gameRepo = guess;
}
const BASIC_TEAM = [
  ['팀장', '사장님 말을 받아 직원에게 일을 나누고, 결과를 모아 확인·합치기·보고. 팀 회의 교본 관리'],
  ['UI', 'UI·스킬 (화면·조작·카메라)'],
  ['스토리', '소품·스토리·정본 문서'],
  ['몬스터', '몹·보스 만들기와 몹 점검 (몬스터 교본)'],
  ['효과', '검기·효과'],
  ['모션', '그림·움직임 (모션 교과서)'],
  ['AI협력팀', '다른 AI(그록 등)와 협력: 부탁 문서 쓰기, 그록 폴더 확인, 받은 것 검사해서 맞는 직원에게 넘기기', true],
];
for (const e of state.employees) { e.status = e.queue && e.queue.length ? 'idle' : 'idle'; e.now = ''; e.queue = e.queue || []; }

let saveTimer = null;
function save() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    const tmp = STATE_FILE + '.tmp';
    fs.writeFileSync(tmp, JSON.stringify(state, null, 1));
    fs.renameSync(tmp, STATE_FILE);
  }, 300);
}
const uid = () => crypto.randomBytes(6).toString('hex');
const now = () => new Date().toISOString();

// ───────── 화면에 알리기 (실시간) ─────────
const clients = new Set();
function push(type, data) {
  const msg = `event: ${type}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const c of clients) c.write(msg);
}
let stateTimer = null;
function changed() { save(); clearTimeout(stateTimer); stateTimer = setTimeout(() => push('state', publicState()), 120); }

// ───────── 클로드 코드 찾기 ─────────
const claude = { ok: false, version: '', path: '', useShell: false, flags: {}, modes: [], error: '' };
function detectClaude() {
  return new Promise((resolve) => {
    const cmd = state.settings.claudeCmd || 'claude';
    const finish = (p, shell) => {
      claude.path = p; claude.useShell = shell;
      run(['--version'], (err, out) => {
        if (err) { claude.ok = false; claude.error = '클로드 코드를 찾을 수 없어요'; return resolve(); }
        claude.version = out.trim().split('\n')[0];
        run(['--help'], (err2, help) => {
          help = help || '';
          claude.ok = true; claude.error = '';
          for (const f of ['--permission-prompt-tool', '--append-system-prompt-file', '--strict-mcp-config', '--permission-prompts']) claude.flags[f] = help.includes(f);
          claude.flags['--permission-prompt-tool'] = true; // 도움말에 안 나와도 있음 (시험 확인)
          const m = help.match(/--permission-mode[\s\S]*?\(choices:([^)]*)\)/);
          claude.modes = m ? (m[1].match(/"([^"]+)"/g) || []).map((x) => x.replace(/"/g, '')) : ['acceptEdits', 'bypassPermissions', 'default', 'plan'];
          resolve();
        });
      });
    };
    const run = (args, cb) => {
      const p = spawn(quoteIf(claude.path), args.map(quoteIf), { shell: claude.useShell, windowsHide: true });
      const t = setTimeout(() => { try { p.kill(); } catch (e) { /* */ } }, 15000);
      p.on('close', () => clearTimeout(t));
      let out = '';
      p.stdout.on('data', (d) => (out += d));
      p.on('error', (e) => cb(e));
      p.on('close', (code) => cb(code === 0 ? null : new Error('code ' + code), out));
    };
    if (IS_WIN && !/[\\/]/.test(cmd)) {
      execFile('where', [cmd], { windowsHide: true }, (err, out) => {
        const list = (out || '').split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
        const exe = list.find((s) => /\.exe$/i.test(s));
        if (exe) return finish(exe, false);
        const other = list.find((s) => /\.(cmd|bat)$/i.test(s));
        if (other) return finish(other, true);
        // 기본 설치 자리도 찾아봄
        const guess = path.join(process.env.USERPROFILE || '', '.local', 'bin', 'claude.exe');
        if (fs.existsSync(guess)) return finish(guess, false);
        claude.ok = false; claude.error = '클로드 코드를 찾을 수 없어요'; resolve();
      });
    } else finish(cmd, IS_WIN && /\.(cmd|bat)$/i.test(cmd));
  });
}
function quoteIf(a) {
  if (!claude.useShell) return a;
  return '"' + String(a).replace(/"/g, '""') + '"';
}

// ───────── 허락 규칙 ─────────
const BASH_TWO = ['git', 'npm', 'npx', 'pnpm', 'yarn', 'python', 'python3', 'py', 'pip', 'pip3', 'node', 'gh', 'cargo', 'go', 'dotnet', 'docker', 'powershell', 'pwsh'];
function splitShell(cmd) { return String(cmd || '').split(/&&|\|\||;|\||\n/).map((s) => s.trim()).filter(Boolean); }
function bashPrefix(one) {
  const w = one.replace(/^(sudo|cd\s+\S+\s*&&)\s+/, '').split(/\s+/).filter((x) => !/^[A-Z_]+=/.test(x));
  if (!w.length) return '';
  return BASH_TWO.includes(w[0]) && w[1] && !w[1].startsWith('-') ? w[0] + ' ' + w[1] : w[0];
}
function makeRules(tool, input) {
  if (tool === 'Bash' || tool === 'PowerShell') {
    const parts = splitShell(input.command).map(bashPrefix).filter(Boolean);
    return [...new Set(parts)].map((p) => `${tool}(${p}:*)`);
  }
  if (tool === 'WebFetch' && input.url) { try { return [`WebFetch(domain:${new URL(input.url).hostname})`]; } catch (e) { /* */ } }
  return [tool];
}
function ruleMatches(rule, tool, input) {
  const m = rule.match(/^([^(]+)(?:\((.*)\))?$/);
  if (!m || m[1] !== tool) return false;
  if (!m[2]) return true;
  if (tool === 'Bash' || tool === 'PowerShell') {
    const pre = m[2].replace(/:\*$/, '');
    return (one) => one === pre || one.startsWith(pre + ' ');
  }
  if (tool === 'WebFetch' && m[2].startsWith('domain:')) { try { return new URL(input.url).hostname === m[2].slice(7); } catch (e) { return false; } }
  return false;
}
function isAllowed(tool, input) {
  if (tool === 'Bash' || tool === 'PowerShell') {
    const parts = splitShell(input.command);
    if (!parts.length) return false;
    const testers = state.rules.map((r) => ruleMatches(r, tool, input)).filter((t) => t);
    if (testers.some((t) => t === true)) return true;
    return parts.every((p) => testers.some((t) => typeof t === 'function' && t(p.replace(/^sudo\s+/, ''))));
  }
  return state.rules.some((r) => ruleMatches(r, tool, input) === true);
}
function describeTool(tool, input) {
  input = input || {};
  const short = (s, n = 90) => { s = String(s || '').replace(/\s+/g, ' ').trim(); return s.length > n ? s.slice(0, n) + '…' : s; };
  const base = (p) => (p ? path.basename(String(p)) : '');
  switch (tool) {
    case 'Bash': case 'PowerShell': return '명령 실행: ' + short(input.description || input.command);
    case 'Read': return '파일 읽는 중: ' + base(input.file_path);
    case 'Edit': case 'MultiEdit': return '파일 고치는 중: ' + base(input.file_path);
    case 'Write': return '파일 만드는 중: ' + base(input.file_path);
    case 'Glob': case 'Grep': return '찾는 중: ' + short(input.pattern, 50);
    case 'WebFetch': return '인터넷 보는 중: ' + short(input.url, 60);
    case 'WebSearch': return '인터넷 검색: ' + short(input.query, 60);
    case 'Task': case 'Agent': return '도우미에게 맡기는 중: ' + short(input.description, 60);
    case 'TodoWrite': case 'TaskCreate': case 'TaskUpdate': return '할 일 정리 중';
    default: return tool + ' 쓰는 중';
  }
}

// ───────── 허락 요청 (직원 → 사장님) ─────────
const pending = new Map(); // id → {id, emp, tool, input, label, rules, res, time}
function askPermission(empId, tool, input, res) {
  if (isAllowed(tool, input)) return res.end(JSON.stringify({ allow: true }));
  const emp = findEmp(empId);
  const p = { id: uid(), emp: empId, empName: emp ? emp.name : empId, tool, input, label: describeTool(tool, input), detail: tool === 'Bash' || tool === 'PowerShell' ? input.command : JSON.stringify(input).slice(0, 400), rules: makeRules(tool, input), time: now(), res };
  pending.set(p.id, p);
  if (emp) { emp.status = 'waiting'; emp.now = '허락 기다리는 중: ' + p.label; }
  res.on('close', () => { if (pending.has(p.id) && !res.writableEnded) { pending.delete(p.id); const e = findEmp(empId); if (e && e.status === 'waiting' && ![...pending.values()].some((q) => q.emp === empId)) { e.status = procs.has(e.id) ? 'working' : 'idle'; e.now = ''; } changed(); } });
  changed();
  push('ask', { id: p.id });
}
function answerPermission(id, answer) {
  const p = pending.get(id);
  if (!p) return false;
  pending.delete(id);
  if (answer === 'always') { for (const r of p.rules) if (!state.rules.includes(r)) state.rules.push(r); }
  // 같은 규칙으로 풀리는 다른 요청도 같이 풂
  if (answer === 'always') for (const q of [...pending.values()]) if (isAllowed(q.tool, q.input)) { pending.delete(q.id); q.res.end(JSON.stringify({ allow: true })); restoreWorking(q.emp); }
  const allow = answer === 'always' || answer === 'once';
  p.res.end(JSON.stringify(allow ? { allow: true } : { allow: false, message: '사장님이 거절했어요. 다른 방법을 찾거나, 왜 필요한지 보고에 적어 주세요.' }));
  restoreWorking(p.emp);
  changed();
  return true;
}
function restoreWorking(empId) {
  const e = findEmp(empId);
  if (e && e.status === 'waiting' && ![...pending.values()].some((q) => q.emp === empId)) { e.status = 'working'; e.now = '다시 일하는 중'; }
}

// ───────── 직원 ─────────
const procs = new Map(); // empId → child
const logs = new Map(); // empId → [{t, kind, text}]
function findEmp(id) { return state.employees.find((e) => e.id === id || e.name === id); }
function addLog(empId, kind, text) {
  const arr = logs.get(empId) || [];
  const line = { t: now(), kind, text: String(text).slice(0, 4000) };
  arr.push(line); if (arr.length > 400) arr.splice(0, arr.length - 400);
  logs.set(empId, arr);
  fs.appendFile(path.join(DATA, 'logs', empId + '.log'), `[${line.t}] ${kind}: ${line.text}\n`, () => {});
  push('log', { emp: empId, line });
}
function officePrompt(emp) {
  const others = state.employees.filter((e) => e.id !== emp.id).map((e) => `- ${e.name}: ${e.role}`).join('\n') || '- (아직 없음)';
  const partner = emp.partner ? `
## 너는 AI협력팀이다 (다른 AI와 함께 일하기)
- 지금 협력하는 AI: **그록** (그림·영상·일러스트). 방법은 게임 폴더의 \`handoff/claude/TEAM_MEETING_TEXTBOOK_ko.md\` 9장(그록 부탁 방법)을 그대로 따른다.
- 그록과 파일을 주고받는 폴더(사장님 PC에 동기화된 구글 드라이브): ${state.settings.grokDir ? '`' + state.settings.grokDir + '`' : '(아직 설정 안 됨 — 사장님께 설정에서 「그록 폴더」를 정해 달라고 \`@사장님:\` 으로 말한다)'}
- **부탁 보내기**: 다른 직원이 그록 부탁을 넘기면, 9장 규칙대로 부탁 문서를 써서 그록 폴더에 넣고, 사장님이 그록 채팅에 한 번에 붙여 넣을 글을 보고 맨 끝에 \`\`\` 블록 하나로 준다(화면에 「붙여넣기 글 복사」 단추가 생김).
- **폴더 확인**: 「폴더 확인」 또는 「그록 폴더에 새 파일」 일을 받으면 묻지 말고 새 파일(전달 문서·영상·그림)을 열어 보고, 무엇이 왔는지·쓸 수 있는지 보고한다. 쓸 만하면 게임 폴더의 맞는 자리로 옮기고, 맞는 직원에게 \`@전달\` 로 넘긴다. 영상·그림은 경로를 적어 보고함에서 바로 보이게 한다.
- **그록 터널**: 지금 방식 = ${grokWay() === 'bot' ? '**그록 봇 연결** (알들 컴퍼니, 돈 안 듦). `grok ask` 를 쓰면 그록 봇에게 바로 가고, 답은 깃허브 「AI협력 대화방」에서 저절로 돌아온다. 답이 오기까지 몇 분 걸릴 수 있다 → Bash 시간 제한을 600000 으로 두고, 끊기면 `grok wait 번호` 로 이어서 기다린다. 한 번에 꼭 필요한 말만 모아서 묻는다' : grokPaste() ? '**반자동 붙여넣기** (돈 안 듦). \`grok\` 명령을 쓰면 회사 화면에 부탁이 뜨고, 사장님이 그록 앱에 옮겨 주고 답을 붙여 넣어 준다. 답이 오기까지 몇 분 걸릴 수 있다 → Bash 시간 제한을 600000 으로 두고, 끊기면 `grok wait 번호` 로 이어서 기다린다. 사장님 수고를 줄이게 **꼭 필요한 말만 한 번에 모아서** 묻는다' : '**그록 키** (자동, 돈 듦)'}.
  - \`grok ask "질문" --img 참고.png --thread 주제이름\` : 그록에게 묻기 (같은 thread 면 앞 대화를 기억한다. 주제마다 thread 이름을 정한다)
  - \`grok image "그림 설명(영어가 더 정확)" --out 경로.png --n 2 --ref 기준그림.png\` : 그림 받기 (\`--ref\` = 그 그림을 고쳐 그리기)
  - \`grok video "움직임 설명" --img 첫장면.png --sec 6 --out 경로.mp4\` : 영상 받기 (1초에 약 $0.08 — 꼭 필요할 때만, 짧게)
  - \`grok spent\` : 오늘 쓴 돈. 하루 한도 $${state.settings.grokBudget || 5} 를 넘으면 도구가 멈춘다.
  - 그록과 주고받은 말·그림은 회사 화면 「그록 터널」에 저절로 보인다. 받은 그림은 9장 규칙(빛·효과 빼기, 투명 PNG, 기준 그림과 나란히 검수)으로 검사하고, 보고에 경로와 **쓴 돈**을 적는다.
  - 터널이 안 될 때(키 없음·한도)는 예전처럼 드라이브 폴더 + 붙여넣기 글로 한다.
- **업무 공유판**: https://raw.githubusercontent.com/meca12944/thor-like-game/main/handoff/GROK_BRIEFING_ko.md — 그록·다른 AI와 새 대화를 시작할 때 이 주소를 먼저 읽게 한다 (최신 결정·진행이 저절로 채워져 있음).
- 그 밖의 AI(제미나이·챗GPT 등)와 일할 때도 같은 방식: 부탁 글은 \`\`\` 블록으로, 받은 결과는 검사해서 보고.
` : '';
  return `# 클로드 작업장 (알들 컴퍼니 「게임 필멸자」 부서, 사장님 PC의 업무 화면)
너는 「클로드 작업장」의 직원 **${emp.name}** 이고, 맡은 일은 **${emp.role}** 이다.
같은 회사 직원:
${others}

## 보고하는 법
- 사장님은 회사 화면에서 네 **마지막 답만 '보고'로** 읽는다. 일이 끝나면 마지막 답에 결과를 **초등학생도 알아듣게 쉬운 한국어로 짧게** 적는다.
- 만든 영상·그림은 마지막 답에 **파일 경로를 그대로** 적는다 (예: \`out/result.mp4\`). 그러면 보고함에서 바로 재생된다.
- 못 한 것·막힌 것도 정직하게 적는다.

## 다른 직원과 말하기 (사장님이 말을 옮기지 않아도 된다)
- 다른 직원에게 일을 넘기거나 물을 때는 마지막 답에 **한 줄로** \`@전달 이름: 할 말\` 이라고 쓴다. 여러 명이면 줄을 여러 개 쓴다.
- 그 직원이 일을 마치면 그 보고가 **저절로 너에게 돌아온다**. 그때 이어서 일한다.
- 사장님 결정이 꼭 필요할 때만 \`@사장님: 질문\` 이라고 쓴다. 그 밖에는 묻지 말고 가장 좋은 방법으로 끝까지 한다.

## 허락
- 위험할 수 있는 일은 회사 화면이 사장님께 대신 물어본다. 사장님이 한 번 「항상 허락」한 일은 다시 묻지 않는다.
- 거절당하면 다른 방법을 찾고, 그래도 안 되면 보고에 이유를 적는다.
${partner}`;
}
function claudeArgs(emp, promptFile) {
  const a = ['-p', '--output-format', 'stream-json', '--verbose'];
  let mode = emp.mode || state.settings.defaultMode || 'auto';
  if (mode === 'all') a.push('--dangerously-skip-permissions');
  else {
    if (!claude.modes.includes(mode)) mode = 'acceptEdits';
    a.push('--permission-mode', mode);
    const mcpFile = path.join(DATA, 'prompts', emp.id + '.mcp.json');
    fs.writeFileSync(mcpFile, JSON.stringify({ mcpServers: { office: { command: process.execPath, args: [path.join(ROOT, 'perm-mcp.js')], env: { OFFICE_URL: `http://127.0.0.1:${state.settings.port}`, OFFICE_EMP: emp.id } } } }));
    a.push('--mcp-config', mcpFile);
    a.push('--permission-prompt-tool', 'mcp__office__approve');
    if (state.rules.length) a.push('--allowedTools', ...state.rules);
  }
  if (claude.flags['--append-system-prompt-file']) a.push('--append-system-prompt-file', promptFile);
  else a.push('--append-system-prompt', fs.readFileSync(promptFile, 'utf8'));
  if (emp.model) a.push('--model', emp.model);
  if (state.settings.grokDir && fs.existsSync(state.settings.grokDir)) a.push('--add-dir', state.settings.grokDir);
  if (emp.started) a.push('--resume', emp.sessionId); else a.push('--session-id', emp.sessionId);
  return a;
}
function order(empId, text, from = '사장님', hop = 0, kind = 'ask', root = null, extra = {}) {
  const emp = findEmp(empId);
  if (!emp) return false;
  emp.queue.push({ id: uid(), text, from, hop, kind, root: root || emp.id, time: now(), ...extra });
  changed();
  next(emp);
  return true;
}
function next(emp) {
  if (procs.has(emp.id) || !emp.queue.length) return;
  if (!claude.ok) { emp.status = 'error'; emp.now = '클로드 코드가 없어서 쉬는 중'; changed(); return; }
  if (!emp.folder || !fs.existsSync(emp.folder)) { emp.status = 'error'; emp.now = '일하는 폴더가 없어요: ' + emp.folder; changed(); return; }
  const task = emp.queue.shift();
  startRun(emp, task, false);
}
function startRun(emp, task, isRetry) {
  if (!emp.sessionId) { emp.sessionId = crypto.randomUUID(); emp.started = false; }
  const promptFile = path.join(DATA, 'prompts', emp.id + '.md');
  fs.writeFileSync(promptFile, officePrompt(emp));
  const args = claudeArgs(emp, promptFile);
  const env = { ...process.env, MCP_TOOL_TIMEOUT: '86400000', MCP_TIMEOUT: '60000', OFFICE_URL: `http://127.0.0.1:${state.settings.port}`, OFFICE_EMP: emp.id, OFFICE_DATA: DATA, GROK_DAILY_BUDGET: String(state.settings.grokBudget || 5) };
  const pk = Object.keys(env).find((k) => k.toUpperCase() === 'PATH') || 'PATH';
  env[pk] = path.join(ROOT, 'tools', 'bin') + path.delimiter + (env[pk] || '');
  delete env.XAI_API_KEY;
  if (emp.partner && !grokPaste()) env.XAI_API_KEY = state.settings.xaiKey; // 그록 키는 AI협력팀에게만 (키 방식일 때)
  if (emp.partner) { env.BASH_DEFAULT_TIMEOUT_MS = env.BASH_DEFAULT_TIMEOUT_MS || '600000'; env.BASH_MAX_TIMEOUT_MS = env.BASH_MAX_TIMEOUT_MS || '1800000'; }
  const child = spawn(quoteIf(claude.path), args.map(quoteIf), { cwd: emp.folder, shell: claude.useShell, windowsHide: true, env });
  procs.set(emp.id, child);
  emp.status = 'working'; emp.now = '일 시작'; emp.task = task; emp.startedAt = now();
  addLog(emp.id, 'order', `[${task.from}] ${task.text}`);
  changed();
  const run = { text: '', result: null, cost: 0, denials: [], isError: false, stderr: '' };
  let buf = '';
  child.stdout.setEncoding('utf8');
  child.stdout.on('data', (d) => {
    buf += d; let i;
    while ((i = buf.indexOf('\n')) >= 0) { const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1); if (line) onLine(emp, run, line); }
  });
  child.stderr.setEncoding('utf8');
  child.stderr.on('data', (d) => { run.stderr = (run.stderr + d).slice(-4000); });
  child.stdin.on('error', () => {});
  child.stdin.end(task.text);
  child.on('error', (e) => { run.stderr += '\n' + e.message; });
  child.on('close', (code) => {
    procs.delete(emp.id);
    if (buf.trim()) onLine(emp, run, buf.trim());
    for (const [id, p] of pending) if (p.emp === emp.id) { pending.delete(id); try { p.res.end(JSON.stringify({ allow: false, message: '멈춤' })); } catch (e) { /* */ } }
    if (emp.stopped) { emp.stopped = false; finishRun(emp, task, { ...run, text: run.text || '(사장님이 멈춤)', stopped: true }); return; }
    // 이어하기 실패 → 새 대화로 한 번 다시
    if (!run.result && !isRetry && emp.started && /No conversation found|session/i.test(run.stderr)) {
      addLog(emp.id, 'sys', '예전 대화를 못 찾아서 새 대화로 다시 시작');
      emp.sessionId = crypto.randomUUID(); emp.started = false;
      return startRun(emp, task, true);
    }
    // 'auto' 방식이 안 되는 계정 → 파일 고치기만 자동으로 바꿔 다시
    if (!run.result && !isRetry && /auto/i.test(run.stderr) && /mode/i.test(run.stderr)) {
      addLog(emp.id, 'sys', '「알아서」 방식을 못 써서 「파일 고치기 자동」 방식으로 다시');
      emp.mode = 'acceptEdits';
      return startRun(emp, task, true);
    }
    if (!run.result && code !== 0) { run.isError = true; run.text = run.text || '일이 중간에 멈췄어요.\n' + friendlyError(run.stderr); }
    finishRun(emp, task, run);
  });
}
function friendlyError(err) {
  if (/log ?in|auth|credential|401/i.test(err)) return '클로드 코드에 로그인이 안 되어 있어요. 「명령 프롬프트」에서 claude 를 한 번 실행해 로그인해 주세요.';
  if (/rate|limit|429|usage/i.test(err)) return '사용 한도에 걸렸어요. 조금 뒤에 다시 시켜 주세요.';
  return (err || '').trim().split('\n').slice(-6).join('\n');
}
function onLine(emp, run, line) {
  let m; try { m = JSON.parse(line); } catch (e) { return; }
  if (m.type === 'system' && m.subtype === 'init' && m.session_id) { emp.sessionId = m.session_id; emp.started = true; }
  if (m.type === 'assistant' && m.message && Array.isArray(m.message.content)) {
    for (const c of m.message.content) {
      if (c.type === 'text' && c.text.trim()) { run.text = c.text; addLog(emp.id, 'say', c.text); }
      if (c.type === 'tool_use') { emp.now = describeTool(c.name, c.input); addLog(emp.id, 'tool', emp.now); changed(); }
    }
  }
  if (m.type === 'result') {
    run.result = m; run.cost = m.total_cost_usd || 0; run.isError = !!m.is_error;
    if (typeof m.result === 'string' && m.result.trim()) run.text = m.result;
    run.denials = (m.permission_denials || []).map((d) => describeTool(d.tool_name, d.tool_input));
    if (m.session_id) { emp.sessionId = m.session_id; emp.started = true; }
  }
}
const MEDIA = /(?:[A-Za-z]:[\\/]|[\\/]|\.{1,2}[\\/])?[^\s`'"<>|*?()\[\]]+?\.(?:mp4|webm|mov|png|jpe?g|gif|webp)(?![\w])/gi;
function findMedia(emp, text) {
  const out = [];
  for (const raw of new Set(String(text).match(MEDIA) || [])) {
    const p = path.isAbsolute(raw) ? raw : path.join(emp.folder, raw);
    try { if (fs.statSync(p).isFile()) out.push(p); } catch (e) { /* 없음 */ }
    if (out.length >= 8) break;
  }
  return out;
}
function finishRun(emp, task, run) {
  const text = run.text || '(보고 없음)';
  const forwards = [];
  const asks = [];
  for (const l of text.split('\n')) {
    // 「@전달 이름: 말」 또는 「@이름: 말」 (이름이 진짜 직원일 때) 둘 다 받아 줌
    const m = l.match(/^\s*[-*]?\s*\**`?@(?:전달\s*)?([^:：`*]+?)\**\s*[:：]\s*(.+?)`?\s*$/);
    if (!m) continue;
    const to = m[1].trim(), said = m[2].trim();
    if (to === '사장님') asks.push(said);
    else if (to === '모두' || findEmp(to)) forwards.push({ to, text: said });
    else if (/^@전달/.test(l.trim().replace(/^[-*`\s]+/, ''))) forwards.push({ to, text: said });
  }
  // 사장님께 가는 보고 = 사장님이 시킨 직원이 남에게 더 넘기지 않고 낸 답 (또는 사장님 확인·문제)
  const toBoss = (task.root || emp.id) === emp.id && forwards.filter((f) => f.to !== '사장님').length === 0;
  const rep = { id: uid(), emp: emp.id, empName: emp.name, time: now(), from: task.from, kind: task.kind || 'ask', toBoss, task: task.text, text, files: findMedia(emp, text), cost: run.cost, denials: run.denials, isError: run.isError, stopped: !!run.stopped, needBoss: asks.length > 0, asks, read: false, forwards: [] };
  state.reports.unshift(rep);
  if (state.reports.length > 300) state.reports.length = 300;
  emp.status = run.isError ? 'error' : 'idle'; emp.now = run.isError ? '문제가 생겼어요' : ''; emp.task = null;
  if (emp.partner && grokKnown) grokKnown = listGrok();
  if (task.room) roomPost({ emp: emp.id, empName: emp.name, kind: 'claude', text, files: rep.files });
  addLog(emp.id, 'done', text);
  // 다른 직원에게 전달
  if (!run.stopped) {
    for (const f of forwards) {
      if (f.to === '사장님') continue;
      const to = f.to === '모두' ? state.employees.filter((e) => e.id !== emp.id) : [findEmp(f.to)].filter(Boolean);
      if (!to.length) { rep.forwards.push(`${f.to} (그런 직원이 없음)`); continue; }
      if (task.hop + 1 > state.settings.maxHops) { rep.forwards.push(`${f.to} (말이 너무 많이 돌아서 멈춤)`); continue; }
      for (const t of to) { order(t.id, `[${emp.name}이(가) 보낸 말]\n${f.text}`, emp.name, task.hop + 1, 'ask', task.root); rep.forwards.push(t.name); }
    }
    // 다른 직원이 '부탁'한 일이면 결과를 그 직원에게 돌려줌 (돌아온 보고에는 다시 답하지 않음 → 인사 핑퐁 없음)
    const sender = task.kind === 'ask' && task.from !== '사장님' ? findEmp(task.from) : null;
    if (sender && sender.id !== emp.id && task.hop + 1 <= state.settings.maxHops && !forwards.some((f) => f.to === sender.name)) {
      order(sender.id, `[${emp.name}의 보고]\n${text}`, emp.name, task.hop + 1, 'reply', task.root);
      rep.forwards.push(sender.name + '(돌려줌)');
    }
  }
  changed();
  push('report', { id: rep.id });
  setTimeout(() => next(emp), 200);
}
function stopEmp(emp, clearQueue) {
  if (clearQueue) emp.queue = [];
  const c = procs.get(emp.id);
  if (c) {
    emp.stopped = true;
    if (IS_WIN) execFile('taskkill', ['/pid', String(c.pid), '/T', '/F'], { windowsHide: true }, () => {});
    else c.kill('SIGTERM');
  }
  changed();
}

function makeFolder(name, cb) {
  // 게임 원본 폴더가 있으면 직원 전용 작업 공간(git worktree)을 만들어 줌 → 직원끼리 파일이 안 엉킴
  const repo = state.settings.gameRepo;
  const ws = state.settings.workspace || (repo ? path.join(path.dirname(repo), path.basename(repo) + '_직원') : '');
  if (!repo || !fs.existsSync(path.join(repo, '.git'))) return cb(new Error('설정에서 「게임 원본 폴더」를 먼저 정해 주세요.'));
  const dir = path.join(ws, name.replace(/[\\/:*?"<>|\s]+/g, '_'));
  if (fs.existsSync(dir)) return cb(null, dir);
  fs.mkdirSync(ws, { recursive: true });
  execFile('git', ['-C', repo, 'fetch', 'origin', 'main'], { windowsHide: true }, () => {
    execFile('git', ['-C', repo, 'worktree', 'add', '--detach', dir, 'origin/main'], { windowsHide: true }, (err, out, errText) => {
      if (err) return cb(new Error('작업 공간을 못 만들었어요: ' + (errText || err.message)));
      cb(null, dir);
    });
  });
}

// ───────── 대화방 (사장님 · 그록 · AI협력팀 실시간) ─────────
const XAI = (process.env.XAI_BASE_URL || 'https://api.x.ai').replace(/\/$/, '');
const GROK_SYSTEM = '너는 「필멸자」(PC용 2D 액션 게임)를 만드는 팀과 함께 일하는 그록이다. 이 대화방에는 사장님과 클로드 직원(AI협력팀 등)이 함께 있다. 말머리 [사장님] / [클로드 이름] 으로 누가 말하는지 구분해서 그 사람에게 답한다. 쉬운 한국어로 짧고 분명하게 말한다. 그림·효과 규칙: 빛·불·검기 같은 효과는 그림에 넣지 않는다(게임 코드로 그림).';
function roomPost(it) {
  const item = { id: uid(), time: now(), emp: it.emp || '', empName: it.empName || '', kind: it.kind || '', text: String(it.text || '').slice(0, 20000), files: it.files || [], streaming: !!it.streaming, relay: it.relay || null };
  state.grokLog.push(item); if (state.grokLog.length > 400) state.grokLog.splice(0, state.grokLog.length - 400);
  changed(); push('grok', { id: item.id });
  return item;
}
function spendFile() { return path.join(DATA, 'grok', 'spend.json'); }
function spentToday(add) {
  fs.mkdirSync(path.join(DATA, 'grok'), { recursive: true });
  let s = {}; try { s = JSON.parse(fs.readFileSync(spendFile(), 'utf8')); } catch (e) { /* */ }
  const d = new Date().toISOString().slice(0, 10);
  if (add) { s[d] = Math.round(((s[d] || 0) + add) * 1000) / 1000; fs.writeFileSync(spendFile(), JSON.stringify(s)); }
  return s[d] || 0;
}
// ── 반자동 붙여넣기: 그록 키 없이, 사장님이 그록 앱에 옮겨 주고 답을 붙여 넣음 (사장님 11-11 「반자동 붙여넣기」) ──
const BOARD_URL = 'https://raw.githubusercontent.com/meca12944/thor-like-game/main/handoff/GROK_BRIEFING_ko.md';
const relayWait = new Map(); // relay id → [res...]
function grokPaste() { return state.settings.grokMode !== 'api' || !state.settings.xaiKey; }
// ── 그록 봇 연결 (알들 컴퍼니, 사장님 11-11 「응」) ──
// 클로드 → 그록: 알들 컴퍼니 명령창과 같은 웹훅 (주소·키는 사장님이 설정에 한 번 넣음, 이 PC 의 data 폴더에만 저장).
// 그록 → 클로드: 깃허브 「AI협력 대화방」 글(coopIssue)의 댓글을 확인해서 기다리던 클로드에게 넘김.
function botConfig() {
  if (state.settings.botUrl && state.settings.botKey) return { url: state.settings.botUrl, key: state.settings.botKey, from: 'manual' };
  return null;
}
function grokWay() {
  if (state.settings.grokMode === 'api' && state.settings.xaiKey) return 'api';
  if (state.settings.grokMode === 'bot' && botConfig()) return 'bot';
  return 'paste';
}
const ISSUE_URL = () => `https://github.com/meca12944/thor-like-game/issues/${state.settings.coopIssue}`;
async function sendToBot(item) {
  const cfg = botConfig(); if (!cfg) return;
  const command = `${item.relay.paste}\n\n— 답은 깃허브 「AI협력 대화방」 ${ISSUE_URL()} 에 댓글로 달아 주세요. 첫 줄에 [relay:${item.id}] 를 그대로 적어 주세요.`;
  const body = JSON.stringify({ target: state.settings.botTarget || 'AI 협력', command, source: '클로드 회사', sentAt: new Date().toISOString(), relayId: item.id, replyTo: ISSUE_URL() });
  try {
    const r = await fetch(cfg.url, { method: 'POST', headers: { authorization: 'Bearer ' + cfg.key, 'content-type': 'application/json; charset=utf-8' }, body });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    item.relay.sent = true; item.relay.sendError = '';
  } catch (e) { item.relay.sent = false; item.relay.sendError = '그록 봇에게 못 보냈어요 (' + e.message + '). 직접 붙여 넣어 주세요.'; }
  changed(); pollSoon();
}
// 깃허브 대화방 확인
let pollTimer = null, etag = '', rateLeft = 60, rateReset = 0, coopStatus = { ok: false, at: '' };
function pollSoon(ms) { clearTimeout(pollTimer); pollTimer = setTimeout(pollIssue, ms || 1500); }
function nextPoll() {
  const waiting = state.grokLog.some((g) => g.relay && g.relay.state === 'waiting');
  let ms = state.settings.ghToken ? 20000 : waiting ? 20000 : 180000;
  if (!state.settings.ghToken && rateLeft < 4 && rateReset) ms = Math.max(ms, rateReset * 1000 - Date.now() + 2000);
  pollSoon(ms);
}
async function fetchFile(url) {
  try {
    const r = await fetch(url, { headers: { 'user-agent': 'claude-workshop' } });
    if (!r.ok) return null;
    const type = r.headers.get('content-type') || '';
    const ext = /png/.test(type) ? '.png' : /jpe?g/.test(type) ? '.jpg' : /gif/.test(type) ? '.gif' : /webp/.test(type) ? '.webp' : /mp4/.test(type) ? '.mp4' : /webm/.test(type) ? '.webm' : '';
    if (!ext) return null;
    const dir = path.join(DATA, 'grok', 'files'); fs.mkdirSync(dir, { recursive: true });
    const fp = path.join(dir, `bot_${Date.now()}_${Math.random().toString(36).slice(2, 6)}${ext}`);
    fs.writeFileSync(fp, Buffer.from(await r.arrayBuffer()));
    return fp;
  } catch (e) { return null; }
}
async function pollIssue() {
  if (grokWay() !== 'bot') return pollSoon(60000);
  try {
    const headers = { 'user-agent': 'claude-workshop', accept: 'application/vnd.github+json' };
    if (state.settings.ghToken) headers.authorization = 'Bearer ' + state.settings.ghToken;
    if (etag) headers['if-none-match'] = etag;
    const r = await fetch(`${process.env.OFFICE_GH_API || 'https://api.github.com'}/repos/meca12944/thor-like-game/issues/${state.settings.coopIssue}/comments?per_page=100&sort=created&direction=desc`, { headers });
    coopStatus = { ok: r.status === 200 || r.status === 304, at: now() };
    rateLeft = Number(r.headers.get('x-ratelimit-remaining') || rateLeft); rateReset = Number(r.headers.get('x-ratelimit-reset') || 0);
    if (r.status === 200) {
      etag = r.headers.get('etag') || '';
      const list = (await r.json()).sort((a, b) => a.id - b.id);
      if (state.coopLastId === undefined) { state.coopLastId = list.length ? list[list.length - 1].id : 0; save(); }
      for (const c of list) {
        if (c.id <= state.coopLastId) continue;
        state.coopLastId = c.id; save();
        await onBotComment(String(c.body || ''));
      }
    }
  } catch (e) { /* 다음에 다시 */ }
  nextPoll();
}
async function onBotComment(body) {
  if (/<!-- claude-workshop -->/.test(body)) return;
  const m = body.match(/\[relay:([0-9a-f]{6,})\]/i);
  let text = body.replace(/^\s*\[그록\]\s*/, '').replace(/\[relay:[0-9a-f]+\]\s*/i, '').trim();
  const files = [];
  for (const mm of text.matchAll(/!\[[^\]]*\]\((https?:[^)\s]+)\)|<img[^>]+src="(https?:[^"]+)"|(https:\/\/github\.com\/user-attachments\/assets\/[\w-]+)/g)) {
    const fp = await fetchFile(mm[1] || mm[2] || mm[3]); if (fp) files.push(fp);
  }
  const relay = m ? state.grokLog.find((g) => g.id === m[1] && g.relay) : null;
  if (relay && relay.relay.state === 'waiting') return relayAnswer(relay.id, text, files);
  if (!relays().length) {
    // 그록이 먼저 말을 검 → 대화방에 올리고 AI협력팀에게
    roomPost({ emp: 'grok', empName: '그록', kind: 'answer', text, files });
    const team = state.employees.find((e) => e.partner);
    if (team) order(team.id, `[그록 봇이 먼저 보낸 말 (깃허브 대화방)]\n${text}\n\n(필요하면 \`grok ask "답"\` 으로 그록에게 답해라.)`, '그록', 0, 'ask', null, { room: true });
    return;
  }
  relayAnswer(null, text, files); // 번호가 없으면 가장 오래 기다린 부탁의 답으로
}
function relays() { return state.grokLog.filter((g) => g.relay && g.relay.state === 'waiting'); }
function relayCreate({ emp, empName, kind, text, files }) {
  const speaker = emp === 'boss' ? '[사장님]' : `[클로드 ${empName}]`;
  let paste = kind === 'image' ? `${speaker} 그림 그려 줘: ${text}` : kind === 'video' ? `${speaker} 영상 만들어 줘: ${text}` : `${speaker} ${text}`;
  if (!state.relayStarted) { paste = `(우리 팀 업무 공유판이야. 처음이면 먼저 읽고 여기 결정·규칙을 따라 줘: ${BOARD_URL})\n\n` + paste; state.relayStarted = true; }
  const e = findEmp(emp);
  if (e) { e.status = 'waiting'; e.now = '그록 답 기다리는 중 (사장님이 옮겨 주는 중)'; }
  push('relay', {});
  const item = roomPost({ emp, empName, kind: emp === 'boss' ? 'boss' : 'ask', text: (kind === 'image' ? '🎨 ' : kind === 'video' ? '🎬 ' : '') + text, files: files || [], relay: { state: 'waiting', kind, paste, way: grokWay() } });
  if (item.relay.way === 'bot') sendToBot(item);
  return item;
}
function relayAnswer(id, text, files) {
  const item = id ? state.grokLog.find((g) => g.id === id && g.relay) : state.grokLog.find((g) => g.relay && g.relay.state === 'waiting');
  const ans = roomPost({ emp: 'grok', empName: '그록', kind: 'answer', text: text || (files.length ? '' : '(빈 답)'), files });
  if (!item) return ans;
  item.relay.state = 'done'; item.relay.answer = ans.id;
  for (const r of relayWait.get(item.id) || []) { try { r.end(JSON.stringify({ id: item.id, text, files })); } catch (e) { /* */ } }
  relayWait.delete(item.id);
  const e = findEmp(item.emp);
  if (e && e.status === 'waiting' && procs.has(e.id)) { e.status = 'working'; e.now = '그록 답 받음'; }
  changed();
  return ans;
}
function relayHold(id, res, wait) {
  const item = state.grokLog.find((g) => g.id === id && g.relay);
  if (!item) return json(res, { id, error: '그런 부탁 번호가 없어요' }, 404);
  if (item.relay.state === 'done') { const a = state.grokLog.find((g) => g.id === item.relay.answer); return json(res, { id, text: a ? a.text : '', files: a ? a.files : [] }); }
  const list = relayWait.get(id) || []; list.push(res); relayWait.set(id, list);
  const t = setTimeout(() => { const l = relayWait.get(id) || []; const i = l.indexOf(res); if (i >= 0) { l.splice(i, 1); json(res, { id, pending: true }); } }, Math.min(Number(wait) || 540000, 540000));
  res.on('close', () => clearTimeout(t));
}

function roomCheck() {
  if (!state.settings.xaiKey) return '그록 키가 없어요. 설정 → 「그록 키」를 넣어 주세요 (console.x.ai 에서 만들어요).';
  if (spentToday(0) >= (state.settings.grokBudget || 5)) return `오늘 그록 한도 $${state.settings.grokBudget} 를 다 썼어요. 설정에서 한도를 올릴 수 있어요.`;
  return '';
}
async function roomChat(text) {
  const tf = path.join(DATA, 'grok', 'thread_room.json');
  let prev = null; try { prev = JSON.parse(fs.readFileSync(tf, 'utf8')).id; } catch (e) { /* 새 대화 */ }
  roomPost({ emp: 'boss', empName: '사장님', kind: 'boss', text, files: [] });
  const ans = roomPost({ emp: 'grok', empName: '그록', kind: 'answer', text: '', streaming: true });
  const input = [];
  if (!prev) input.push({ role: 'system', content: GROK_SYSTEM });
  input.push({ role: 'user', content: '[사장님] ' + text });
  const body = { model: process.env.GROK_CHAT_MODEL || 'grok-4.7', input, stream: true };
  if (prev) body.previous_response_id = prev;
  let last = 0;
  const flush = (force) => { const t = Date.now(); if (force || t - last > 120) { last = t; push('grokdelta', { id: ans.id, text: ans.text }); } };
  try {
    const r = await fetch(XAI + '/v1/responses', { method: 'POST', headers: { authorization: 'Bearer ' + state.settings.xaiKey, 'content-type': 'application/json', accept: 'text/event-stream' }, body: JSON.stringify(body) });
    if (!r.ok) { const t = await r.text(); throw new Error(`그록이 거절했어요 (${r.status}) ${t.slice(0, 300)}`); }
    let respId = null, buf = '';
    const dec = new TextDecoder();
    const onData = (line) => {
      if (!line.startsWith('data:')) return;
      const d = line.slice(5).trim(); if (!d || d === '[DONE]') return;
      let j; try { j = JSON.parse(d); } catch (e) { return; }
      if (j.type === 'response.output_text.delta' && j.delta) { ans.text += j.delta; flush(false); }
      else if (j.choices && j.choices[0] && j.choices[0].delta && j.choices[0].delta.content) { ans.text += j.choices[0].delta.content; flush(false); }
      const resp = j.response || (j.type === 'response.completed' ? j : null);
      if (resp && resp.id) respId = resp.id;
      if (j.type === 'response.completed' && !ans.text && resp && Array.isArray(resp.output)) for (const it of resp.output) for (const c of it.content || []) if (c.type === 'output_text') ans.text += c.text;
    };
    for await (const chunk of r.body) {
      buf += dec.decode(chunk, { stream: true }); let i;
      while ((i = buf.indexOf('\n')) >= 0) { onData(buf.slice(0, i).trim()); buf = buf.slice(i + 1); }
    }
    if (buf.trim()) onData(buf.trim());
    if (respId) fs.writeFileSync(tf, JSON.stringify({ id: respId, time: now() }));
    spentToday(0.02);
  } catch (e) { ans.text += (ans.text ? '\n' : '') + '⚠ ' + e.message; }
  ans.streaming = false; if (!ans.text) ans.text = '(빈 답)';
  flush(true); changed();
}
function roomMedia(kind, text, sec) {
  const dir = path.join(DATA, 'grok', 'files'); fs.mkdirSync(dir, { recursive: true });
  const out = path.join(dir, `boss_${Date.now()}.${kind === 'video' ? 'mp4' : 'png'}`);
  const args = [path.join(ROOT, 'tools', 'grok.js'), kind, text, '--out', out];
  if (kind === 'video') args.push('--sec', String(Math.max(1, Math.min(15, sec))));
  const env = { ...process.env, XAI_API_KEY: state.settings.xaiKey, OFFICE_URL: `http://127.0.0.1:${state.settings.port}`, OFFICE_EMP: 'boss', OFFICE_DATA: DATA, GROK_DAILY_BUDGET: String(state.settings.grokBudget || 5) };
  const c = spawn(process.execPath, args, { env, windowsHide: true });
  let err = ''; c.stderr.on('data', (d) => (err += d));
  c.on('close', (code) => { if (code !== 0) roomPost({ emp: 'grok', empName: '그록', kind: 'answer', text: '⚠ ' + (err.trim() || '실패'), files: [] }); });
}

let grokKnown = null;
function listGrok() {
  const dir = state.settings.grokDir; const out = new Map();
  if (!dir || !fs.existsSync(dir)) return out;
  const walk = (d, depth) => {
    let items = []; try { items = fs.readdirSync(d, { withFileTypes: true }); } catch (e) { return; }
    for (const it of items) {
      const p = path.join(d, it.name);
      if (it.isDirectory()) { if (depth < 2) walk(p, depth + 1); continue; }
      if (/^(~\$|\.)|\.(tmp|ini)$/i.test(it.name)) continue;
      try { out.set(p, fs.statSync(p).mtimeMs); } catch (e) { /* */ }
    }
  };
  walk(dir, 0); return out;
}
function grokCheck(force) {
  const team = state.employees.find((e) => e.partner);
  const cur = listGrok();
  if (!grokKnown) { grokKnown = cur; return []; }
  if (!force && team && (procs.has(team.id) || team.queue.length)) return []; // 협력팀이 일하는 중이면 나중에
  const fresh = [...cur].filter(([p, t]) => !grokKnown.has(p) || grokKnown.get(p) < t).map(([p]) => p);
  grokKnown = cur;
  if (team && fresh.length) order(team.id, `폴더 확인: 그록 폴더에 새 파일이 왔어요.\n${fresh.slice(0, 30).map((p) => '- ' + path.relative(state.settings.grokDir, p)).join('\n')}`, '그록 폴더', 0, 'ask');
  return fresh;
}
setInterval(() => grokCheck(false), 30000);
pollSoon(5000);

function publicState() {
  let grokSpent = 0;
  try { grokSpent = JSON.parse(fs.readFileSync(path.join(DATA, 'grok', 'spend.json'), 'utf8'))[new Date().toISOString().slice(0, 10)] || 0; } catch (e) { /* */ }
  const { xaiKey, botKey, ghToken, ...safeSettings } = state.settings; // 키는 화면에도 안 보냄
  const bc = botConfig();
  return {
    settings: { ...safeSettings, hasXaiKey: !!xaiKey, hasBotKey: !!botKey, hasGhToken: !!ghToken, botFrom: bc ? bc.from : '', grokWay: grokWay(), coop: coopStatus, grokSpent, grokPaste: grokWay() !== 'api', issueUrl: ISSUE_URL() },
    botTargets: BOT_TARGETS,
    botHistory: state.botHistory.slice(0, 50),
    grokLog: state.grokLog.slice(-150).map((g) => ({ ...g, files: g.files.map((f, i) => ({ i, name: path.basename(f), kind: /\.(mp4|webm|mov)$/i.test(f) ? 'video' : 'image' })) })),
    rules: state.rules,
    claude: { ok: claude.ok, version: claude.version, error: claude.error, modes: claude.modes },
    employees: state.employees.map((e) => ({ id: e.id, name: e.name, role: e.role, partner: !!e.partner, folder: e.folder, mode: e.mode, model: e.model, status: e.status, now: e.now, queue: e.queue.length, task: e.task ? e.task.text : '', taskFrom: e.task ? e.task.from : '', startedAt: e.startedAt, hasSession: !!e.started })),
    reports: state.reports.slice(0, 120).map((r) => ({ ...r, files: r.files.map((f, i) => ({ i, name: path.basename(f), kind: /\.(mp4|webm|mov)$/i.test(f) ? 'video' : 'image' })) })),
    pending: [...pending.values()].map((p) => ({ id: p.id, emp: p.emp, empName: p.empName, tool: p.tool, label: p.label, detail: p.detail, rules: p.rules, time: p.time })),
  };
}

// ───────── 웹 서버 ─────────
function readBody(req) {
  return new Promise((resolve) => { let d = ''; req.setEncoding('utf8'); req.on('data', (c) => (d += c)); req.on('end', () => { try { resolve(d ? JSON.parse(d) : {}); } catch (e) { resolve({}); } }); });
}
function json(res, obj, code = 200) { res.writeHead(code, { 'content-type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)); }
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime', '.ico': 'image/x-icon', '.svg': 'image/svg+xml' };
function sendFile(req, res, p) {
  fs.stat(p, (err, st) => {
    if (err || !st.isFile()) { res.writeHead(404); return res.end('없음'); }
    const type = TYPES[path.extname(p).toLowerCase()] || 'application/octet-stream';
    const range = req.headers.range && req.headers.range.match(/bytes=(\d*)-(\d*)/);
    if (range) {
      const start = range[1] ? Number(range[1]) : 0;
      const end = range[2] ? Math.min(Number(range[2]), st.size - 1) : st.size - 1;
      res.writeHead(206, { 'content-type': type, 'content-range': `bytes ${start}-${end}/${st.size}`, 'accept-ranges': 'bytes', 'content-length': end - start + 1 });
      return fs.createReadStream(p, { start, end }).pipe(res);
    }
    res.writeHead(200, { 'content-type': type, 'content-length': st.size, 'accept-ranges': 'bytes' });
    fs.createReadStream(p).pipe(res);
  });
}
function openPath(p) {
  if (IS_WIN) spawn('explorer', [p], { detached: true, windowsHide: false }).unref();
  else if (process.platform === 'darwin') spawn('open', [p], { detached: true }).unref();
  else spawn('xdg-open', [p], { detached: true, stdio: 'ignore' }).on('error', () => {}).unref();
}

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://x');
  const p = u.pathname;
  try {
    if (req.method === 'GET' && (p === '/' || p.startsWith('/ui/'))) {
      const f = p === '/' ? 'index.html' : p.slice(4);
      const full = path.join(ROOT, 'ui', path.normalize(f).replace(/^(\.\.[\\/])+/, ''));
      return sendFile(req, res, full);
    }
    if (p === '/api/state') return json(res, publicState());
    if (p === '/api/events') {
      res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive' });
      res.write(`event: state\ndata: ${JSON.stringify(publicState())}\n\n`);
      clients.add(res);
      const ping = setInterval(() => res.write(': ping\n\n'), 20000);
      req.on('close', () => { clients.delete(res); clearInterval(ping); });
      return;
    }
    if (p === '/api/log') return json(res, logs.get(u.searchParams.get('id')) || []);
    if (p === '/grokfile') {
      const g = state.grokLog.find((x) => x.id === u.searchParams.get('g'));
      const f = g && g.files[Number(u.searchParams.get('i'))];
      if (!f) { res.writeHead(404); return res.end('없음'); }
      return sendFile(req, res, f);
    }
    if (p === '/file') {
      const r = state.reports.find((x) => x.id === u.searchParams.get('r'));
      const f = r && r.files[Number(u.searchParams.get('i'))];
      if (!f) { res.writeHead(404); return res.end('없음'); }
      return sendFile(req, res, f);
    }
    if (req.method !== 'POST') { res.writeHead(404); return res.end('없음'); }
    const b = await readBody(req);
    if (p === '/api/room/send') {
      const text = String(b.text || '').trim(); if (!text) return json(res, { ok: false, error: '할 말을 적어 주세요.' });
      const team = state.employees.find((e) => e.partner);
      if ((b.mode === 'chat' || b.mode === 'image' || b.mode === 'video') && grokPaste()) { const it = relayCreate({ emp: 'boss', empName: '사장님', kind: b.mode, text }); return json(res, { ok: true, paste: it.relay.way === 'bot' ? '' : it.relay.paste, id: it.id }); }
      if (b.mode === 'chat') { const err = roomCheck(); if (err) return json(res, { ok: false, error: err }); roomChat(text); return json(res, { ok: true }); }
      if (b.mode === 'image' || b.mode === 'video') { const err = roomCheck(); if (err) return json(res, { ok: false, error: err }); roomMedia(b.mode, text, Number(b.sec) || 6); return json(res, { ok: true }); }
      if (!team) return json(res, { ok: false, error: 'AI협력팀 직원이 없어요.' });
      roomPost({ emp: 'boss', empName: '사장님', kind: 'boss', text: (b.mode === 'meeting' ? '🗣 회의 주제: ' : '→ ' + team.name + ': ') + text, files: [] });
      if (b.mode === 'meeting') order(team.id, `[대화방 회의] 주제: ${text}\n그록과 \`grok ask --thread room "[클로드 ${team.name}] 할 말"\` 로 최대 ${Math.max(2, Math.min(12, Number(b.turns) || 6))}번 주고받으며 회의해. 매번 그록의 답을 읽고, 맞는 건 받아들이고 틀린 건 근거를 들어 반박해. 사장님도 이 대화를 실시간으로 본다. 끝나면 결론·할 일을 쉬운 말로 짧게 보고해.`, '사장님', 0, 'ask', null, { room: true });
      else order(team.id, `[대화방] 사장님: ${text}\n(사장님·그록·너가 함께 있는 대화방이다. 그록 의견이 필요하면 \`grok ask --thread room "[클로드 ${team.name}] 할 말"\` 로 물어라. 답은 짧게.)`, '사장님', 0, 'ask', null, { room: true });
      return json(res, { ok: true });
    }
    if (p === '/api/bot/command') {
      // 「🏢 회사 일 시키기」: 알들 컴퍼니 명령창과 똑같이 그록 봇에게 보냄 (사장님이 보낸 명령)
      const cfg = botConfig();
      const target = String(b.target || '').trim(), command = String(b.command || '').trim();
      if (!cfg) return json(res, { ok: false, error: '먼저 🔌 연결 → 🤖 그록 봇을 이어 주세요.' });
      if (!target || !command) return json(res, { ok: false, error: '대상과 할 일을 적어 주세요.' });
      const h = { id: uid(), time: now(), target, command, ok: false, result: '' };
      try {
        const r = await fetch(cfg.url, { method: 'POST', headers: { authorization: 'Bearer ' + cfg.key, 'content-type': 'application/json; charset=utf-8' }, body: JSON.stringify({ target, command, source: '알들 컴퍼니 명령창', sentAt: new Date().toISOString() }) });
        h.ok = r.ok; h.result = r.ok ? '보냄' : '실패 ' + r.status;
      } catch (e) { h.result = '실패: ' + e.message; }
      state.botHistory.unshift(h); if (state.botHistory.length > 100) state.botHistory.length = 100;
      changed();
      return json(res, { ok: h.ok, error: h.ok ? '' : '못 보냈어요 (' + h.result + ')' });
    }
    if (p === '/api/room/relay') {
      const e = findEmp(b.emp);
      const files = (Array.isArray(b.files) ? b.files : []).filter((f) => { try { return fs.statSync(f).isFile(); } catch (x) { return false; } }).slice(0, 6);
      const it = relayCreate({ emp: e ? e.id : 'boss', empName: e ? e.name : '직원', kind: b.kind || 'chat', text: String(b.text || ''), files });
      return json(res, { id: it.id });
    }
    if (p === '/api/room/wait') return relayHold(String(b.id || ''), res, b.wait);
    if (p === '/api/room/answer') {
      const dir = path.join(DATA, 'grok', 'files'); fs.mkdirSync(dir, { recursive: true });
      const files = [];
      for (const [i, f] of (Array.isArray(b.uploads) ? b.uploads : []).slice(0, 8).entries()) {
        const m = String(f.data || '').match(/^data:([^;]+);base64,(.*)$/); if (!m) continue;
        const ext = (path.extname(String(f.name || '')) || '.' + (m[1].split('/')[1] || 'bin').replace('jpeg', 'jpg').replace('quicktime', 'mov')).toLowerCase();
        const fp = path.join(dir, `grok_${Date.now()}_${i}${ext}`);
        fs.writeFileSync(fp, Buffer.from(m[2], 'base64')); files.push(fp);
      }
      const text = String(b.text || '').trim();
      if (!text && !files.length) return json(res, { ok: false, error: '그록 답을 붙여 넣어 주세요.' });
      relayAnswer(b.id || null, text, files);
      return json(res, { ok: true });
    }
    if (p === '/api/room/reset') { state.relayStarted = false; try { fs.unlinkSync(path.join(DATA, 'grok', 'thread_room.json')); } catch (e) { /* */ } roomPost({ emp: 'boss', empName: '회사', kind: 'sys', text: '— 새 대화 시작 (그록이 앞 이야기를 잊어요) —', files: [] }); return json(res, { ok: true }); }
    if (p === '/api/grok/log') {
      const emp = findEmp(b.emp);
      const files = (Array.isArray(b.files) ? b.files : []).filter((f) => { try { return fs.statSync(f).isFile(); } catch (e) { return false; } }).slice(0, 8);
      const isBoss = b.emp === 'boss';
      roomPost({ emp: isBoss ? 'boss' : emp ? emp.id : '', empName: isBoss ? '사장님' : emp ? emp.name : '직원', kind: String(b.kind || ''), text: String(b.text || ''), files });
      if (emp) { emp.now = b.kind === 'ask' ? '그록과 이야기하는 중' : '그록 답 받음'; changed(); }
      return json(res, { ok: true });
    }
    if (p === '/api/perm/ask') return askPermission(b.emp, b.tool_name, b.input || {}, res);
    if (p === '/api/perm/answer') return json(res, { ok: answerPermission(b.id, b.answer) });
    if (p === '/api/order') {
      const ids = b.to === 'all' ? state.employees.map((e) => e.id) : [b.to];
      const ok = ids.map((id) => order(id, String(b.text || '').trim())).some(Boolean);
      return json(res, { ok });
    }
    if (p === '/api/stop') { const e = findEmp(b.id); if (e) stopEmp(e, !!b.clear); return json(res, { ok: !!e }); }
    if (p === '/api/stopAll') { state.employees.forEach((e) => stopEmp(e, true)); return json(res, { ok: true }); }
    if (p === '/api/newChat') { const e = findEmp(b.id); if (e && !procs.has(e.id)) { e.sessionId = crypto.randomUUID(); e.started = false; e.status = 'idle'; e.now = ''; logs.set(e.id, []); changed(); } return json(res, { ok: !!e }); }
    if (p === '/api/open') { const e = findEmp(b.id); if (e && e.folder) openPath(e.folder); return json(res, { ok: !!e }); }
    if (p === '/api/openFile') { const r = state.reports.find((x) => x.id === b.r); const f = r && r.files[b.i]; if (f) openPath(path.dirname(f)); return json(res, { ok: !!f }); }
    if (p === '/api/employee') {
      const name = String(b.name || '').trim();
      if (!name) return json(res, { ok: false, error: '이름을 적어 주세요.' });
      let e = b.id ? findEmp(b.id) : null;
      if (!e && state.employees.some((x) => x.name === name)) return json(res, { ok: false, error: '같은 이름의 직원이 있어요.' });
      const apply = (folder) => {
        if (!e) { e = { id: uid(), sessionId: crypto.randomUUID(), started: false, queue: [], status: 'idle', now: '' }; state.employees.push(e); }
        Object.assign(e, { name, role: String(b.role || '').trim() || '무엇이든', folder, mode: b.mode || '', model: String(b.model || '').trim(), partner: !!b.partner });
        changed(); json(res, { ok: true, id: e.id });
      };
      if (b.autoFolder && !b.folder) return makeFolder(name, (err, dir) => (err ? json(res, { ok: false, error: err.message }) : apply(dir)));
      const folder = String(b.folder || '').trim();
      if (!folder || !fs.existsSync(folder)) return json(res, { ok: false, error: '일하는 폴더가 없어요. 폴더 주소를 확인하거나 「자동으로 만들기」를 골라 주세요.' });
      return apply(folder);
    }
    if (p === '/api/grokCheck') {
      const team = state.employees.find((e) => e.partner);
      if (!team) return json(res, { ok: false, error: 'AI협력팀 직원이 없어요. 직원 고치기에서 「AI협력팀」을 켜 주세요.' });
      const fresh = grokCheck(true);
      if (!fresh.length) order(team.id, '폴더 확인: 그록 폴더를 확인해서 최근에 온 것(전달 문서·영상·그림)이 무엇인지, 쓸 수 있는지 보고해.', '사장님');
      return json(res, { ok: true });
    }
    if (p === '/api/team') {
      const made = [];
      for (const [name, role, partner] of BASIC_TEAM) {
        if (state.employees.some((x) => x.name === name)) continue;
        const r = await new Promise((ok) => makeFolder(name, (err, dir) => ok(err ? { err } : { dir })));
        if (r.err) return json(res, { ok: false, error: r.err.message, made });
        state.employees.push({ id: uid(), name, role, partner: !!partner, folder: r.dir, mode: '', model: '', sessionId: crypto.randomUUID(), started: false, queue: [], status: 'idle', now: '' });
        made.push(name); changed();
      }
      return json(res, { ok: true, made });
    }
    if (p === '/api/employee/delete') { const e = findEmp(b.id); if (e) { stopEmp(e, true); state.employees = state.employees.filter((x) => x !== e); changed(); } return json(res, { ok: !!e }); }
    if (p === '/api/settings') {
      for (const k of ['gameRepo', 'workspace', 'defaultMode', 'claudeCmd', 'grokDir']) if (typeof b[k] === 'string') state.settings[k] = b[k].trim();
      if (typeof b.xaiKey === 'string' && b.xaiKey.trim()) state.settings.xaiKey = b.xaiKey.trim();
      if (b.xaiKeyClear) state.settings.xaiKey = '';
      if (b.grokBudget !== undefined && b.grokBudget !== '') state.settings.grokBudget = Math.max(0, Number(b.grokBudget) || 0);
      if (typeof b.grokDir === 'string') grokKnown = null;
      if (['paste', 'api', 'bot'].includes(b.grokMode)) state.settings.grokMode = b.grokMode;
      for (const k of ['botUrl', 'botTarget', 'companyUrl']) if (typeof b[k] === 'string') state.settings[k] = b[k].trim();
      if (typeof b.botKey === 'string' && b.botKey.trim()) state.settings.botKey = b.botKey.trim();
      if (typeof b.ghToken === 'string' && b.ghToken.trim()) state.settings.ghToken = b.ghToken.trim();
      if (b.botKeyClear) { state.settings.botKey = ''; state.settings.botUrl = ''; }
      if (b.ghTokenClear) state.settings.ghToken = '';
      pollSoon();
      if (b.maxHops) state.settings.maxHops = Math.max(1, Math.min(30, Number(b.maxHops) || 6));
      if (typeof b.claudeCmd === 'string') await detectClaude();
      changed(); return json(res, { ok: true });
    }
    if (p === '/api/rules') { if (Array.isArray(b.rules)) state.rules = b.rules.map(String).filter(Boolean); changed(); return json(res, { ok: true }); }
    if (p === '/api/report/read') { for (const r of state.reports) if (b.all || r.id === b.id) r.read = true; changed(); return json(res, { ok: true }); }
    if (p === '/api/report/delete') { state.reports = state.reports.filter((r) => r.id !== b.id); changed(); return json(res, { ok: true }); }
    if (p === '/api/quit') { json(res, { ok: true }); state.employees.forEach((e) => stopEmp(e, false)); setTimeout(() => process.exit(0), 500); return; }
    res.writeHead(404); res.end('없음');
  } catch (e) { json(res, { ok: false, error: e.message }, 500); }
});

// 문을 먼저 열고(창이 바로 뜨게), 클로드 코드 찾기는 뒤에서 (11-11 PC 첫 실행 「연결을 거부했습니다」 고침)
process.on('uncaughtException', (e) => { console.error('[멈추지 않고 계속] ' + (e && e.stack || e)); });
process.on('unhandledRejection', (e) => { console.error('[멈추지 않고 계속] ' + (e && e.stack || e)); });
server.on('error', (e) => {
  if (e.code === 'EADDRINUSE') { console.log('클로드 작업장이 이미 켜져 있어요. 창만 엽니다.'); process.exit(0); }
  console.error('문을 못 열었어요: ' + e.message); process.exit(1);
});
server.listen(state.settings.port, '127.0.0.1', () => {
  console.log(`클로드 작업장 문 열림: http://127.0.0.1:${state.settings.port}`);
  detectClaude().then(() => {
    console.log(claude.ok ? `클로드 코드 찾음 (${claude.version})` : '클로드 코드를 못 찾았어요. 설치 안내를 보세요.');
    changed();
    for (const e of state.employees) next(e); // 꺼지기 전에 남아 있던 일 이어서
  });
});
