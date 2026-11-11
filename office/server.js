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
// 알들 컴퍼니 회사 화면과 같은 부서·봇 이름.
// 중계가 이름을 한 글자까지 맞춰 찾으므로, 여기 이름은 회사 화면의 name 과 같게 둔다.
// 고르는 곳: 「전체」 → 부서 7개 → 부서별 팀원. 「클로드」는 게임 필멸자 팀장으로 들어 있다.
const BOT_TARGETS = {
  all: '전체',
  depts: [
    { id: 'game', name: '게임 필멸자', sub: '게임 코드·그림·영상·음악', icon: '🎮', lead: '클로드', grokLead: '게임만들기' },
    { id: 'zero', name: '제로폰', sub: '사이트·정책·개통 안내', icon: '📱', lead: '제로폰 홈페이지' },
    { id: 'promo', name: '홍보', sub: '블로그·마케팅·영상', icon: '📣', lead: '제로폰 홍보 · 제로폰 관리' },
    { id: 'admin', name: '경영지원', sub: '해피콜·안내·생산·투자', icon: '💼', lead: '폰클매니저 미래 오케이' },
    { id: 'stco', name: 'STCO', sub: '온라인·오프라인', icon: '🛍', lead: 'STCO 인동점 SEO·홍보' },
    { id: 'video', name: '영상 기획팀', sub: '영상 기획·대본', icon: '🎬', lead: '영상 기획 팀장', grokLead: '영상 기획 팀장' },
    { id: 'ai', name: 'AI 협력·연결', sub: '명령 중계·보고 창·클로드 연결', icon: '🔗', lead: '그록봇 최적화 예전 이벨린' },
  ],
  bots: [
    { name: '클로드', dept: 'game', role: '게임 코드·문서·검수 (사장님 구독 클로드 팀)', lead: true },
    { name: '게임만들기', dept: 'game', role: '그록 쪽 게임 그림·영상 총괄', grokLead: true },
    { name: '게임 스토리 작가', dept: 'game', role: '스토리와 대사 작성' },
    { name: '게임 일러스트 작가', dept: 'game', role: '큰그림 일러스트 제작' },
    { name: '게임 음악 담당', dept: 'game', role: '배경음악과 효과음' },
    { name: '주인공 모션', dept: 'game', role: '주인공 픽셀 모션 제작' },
    { name: '히로인 모션 - 이벨린', dept: 'game', role: '히로인 이벨린 캐릭터·모션' },
    { name: '히로인 모션 - 마렌', dept: 'game', role: '히로인 마렌 캐릭터·모션' },
    { name: '히로인 모션 - 유나', dept: 'game', role: '히로인 유나 캐릭터·모션' },
    { name: '히로인 모션 - 베일라', dept: 'game', role: '히로인 베일라 캐릭터·모션' },
    { name: '히로인 모션 - 로자린드', dept: 'game', role: '히로인 로자린드 캐릭터·모션' },
    { name: '히로인 모션 - 자이라', dept: 'game', role: '히로인 자이라 캐릭터·모션' },
    { name: '게임 맵 제작', dept: 'game', role: '마을·던전 맵 제작' },
    { name: '제로폰 홈페이지', dept: 'zero', role: '사이트 작업 조율과 배포', lead: true },
    { name: '제로폰 홈페이지2', dept: 'zero', role: 'zeropon.co.kr 화면 작업' },
    { name: '제로폰 홈페이지3', dept: 'zero', role: '시세표·가격 페이지' },
    { name: '제로폰 홈페이지4', dept: 'zero', role: '유입경로 분석과 사이트 작업' },
    { name: '제로폰 개통 안내', dept: 'zero', role: '고객 개통 안내 이미지' },
    { name: '제로폰 홍보 · 제로폰 관리', dept: 'promo', role: '블로그 글·홍보·영상 관리', lead: true },
    { name: '네이버 판매자센터', dept: 'promo', role: '네이버 판매자센터 관리' },
    { name: '간판디자인', dept: 'promo', role: '간판과 홍보 디자인 시안' },
    { name: '폰클매니저 미래 오케이', dept: 'admin', role: '폰클 관리·개통·정산 확인', lead: true },
    { name: '알들폰 해피콜 시스템', dept: 'admin', role: '고객 해피콜 관리' },
    { name: '알들폰 고객 안내사항 제작', dept: 'admin', role: '매장 고객 안내문 제작' },
    { name: '원오프 셋업 생산', dept: 'admin', role: '원오프 셋업 의류 생산 관리' },
    { name: '음봉일지', dept: 'admin', role: '주식 매매 일지' },
    { name: '철강주 동국제강 이익추정', dept: 'admin', role: '동국제강 이익 추정' },
    { name: 'STCO 인동점 SEO·홍보', dept: 'stco', role: '인동점 쇼핑몰 검색 노출과 홍보', lead: true },
    { name: 'STCO 인동점 포스&홈페이지', dept: 'stco', role: '인동점 포스와 홈페이지' },
    { name: 'STCO 인동점 포스&홈페이지 2', dept: 'stco', role: '인동점 포스와 홈페이지 보조' },
    { name: '영상 기획 팀장', dept: 'video', role: '그록 쪽 영상 기획 팀장', lead: true },
    { name: '영상 기획 2', dept: 'video', role: '영상 기획 보조' },
    { name: '그록봇 최적화 예전 이벨린', dept: 'ai', role: '회사 전체 연결·명령 중계·보고 창 관리', lead: true },
    { name: '알들 컴퍼니 보고 담당', dept: 'ai', role: '보고 정리·클로드에게 답 전달' },
    { name: '알들 컴퍼니 개발 담당', dept: 'ai', role: '프로그램 개선 PR' },
    { name: '클로드 (API · tunnel.py)', dept: 'ai', role: '게임 외 부서의 클로드 도움' },
  ],
};
function companyTargetOk(name) {
  if (name === BOT_TARGETS.all || name === '클로드') return true;
  return BOT_TARGETS.depts.some((d) => d.name === name) || BOT_TARGETS.bots.some((b) => b.name === name);
}
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
// 게임·AI 말고 다른 부서의 클로드 기본 팀. 각 부서 맨 앞 사람이 팀장.
// 사장님 11-11 「팀원에 클로드도 다 배치」. dept 칸은 부서 id. 자리는 켤 때 만들지 않고, 사장님이 만들기를 누르거나 폴더를 고를 때만 만들어요.
const DEPT_CLAUDE_EXTRA = [
  { dept: 'zero', name: '제로폰팀장', role: '사이트와 정책을 나눠 맡고, 결과를 모아 보고', lead: true },
  { dept: 'zero', name: '제로폰사이트', role: '홈페이지 화면과 안내 글' },
  { dept: 'zero', name: '제로폰정책', role: '요금과 개통 규칙 정리' },
  { dept: 'promo', name: '홍보팀장', role: '블로그와 광고를 나눠 맡고, 결과를 모아 보고', lead: true },
  { dept: 'promo', name: '블로그글', role: '블로그에 올릴 글' },
  { dept: 'promo', name: '광고문안', role: '광고에 쓸 짧은 글과 시안' },
  { dept: 'promo', name: '클로드 홍보2', role: '블로그 글 초안 검수·키워드·노출 분석. 결과는 글 제안만, 게시·광고 수정은 안 함' },
  { dept: 'admin', name: '경영팀장', role: '고객 안내와 서류 정리를 나눠 맡고, 결과를 모아 보고', lead: true },
  { dept: 'admin', name: '고객안내', role: '고객에게 보낼 안내 글' },
  { dept: 'admin', name: '서류정리', role: '할 일과 서류 정리' },
  { dept: 'stco', name: 'STCO팀장', role: '쇼핑몰과 검색 노출을 나눠 맡고, 결과를 모아 보고', lead: true },
  { dept: 'stco', name: '쇼핑몰글', role: '상품 글과 쇼핑몰 화면' },
  { dept: 'stco', name: '검색노출', role: '검색에 잘 나오게 제목과 글 정리' },
  { dept: 'video', name: '영상 기획 팀장', role: '영상 기획·콘티·대본 총괄', lead: true },
  { dept: 'video', name: '영상 기획 직원', role: '대본·장면 목록·자막' },
];
// 직원 부서. 예전 저장 파일에 dept 가 없으면 게임 필멸자, AI협력팀만 AI 협력·연결.
function empDeptId(e) {
  if (e && BOT_TARGETS.depts.some((d) => d.id === e.dept)) return e.dept;
  if (e && (e.partner || e.name === 'AI협력팀')) return 'ai';
  return 'game';
}
function empDeptName(e) {
  const id = empDeptId(e);
  const d = BOT_TARGETS.depts.find((x) => x.id === id);
  return d ? d.name : '게임 필멸자';
}
function claudeRoster() {
  const rows = BASIC_TEAM.map(([name, role, partner]) => {
    const dept = partner || name === 'AI협력팀' ? 'ai' : 'game';
    const lead = (dept === 'game' && name === '팀장') || (dept === 'ai' && !!partner);
    return { name, role, dept, partner: !!partner, lead };
  });
  return rows.concat(DEPT_CLAUDE_EXTRA.map((x) => ({ partner: false, lead: false, ...x })));
}
let deptTouched = false;
for (const e of state.employees) {
  const id = empDeptId(e);
  if (e.dept !== id) { e.dept = id; deptTouched = true; }
  if (e.lead == null && ((e.dept === 'game' && e.name === '팀장') || (e.dept === 'ai' && (e.name === 'AI협력팀' || e.partner)))) {
    e.lead = true; deptTouched = true;
  }
  e.status = e.queue && e.queue.length ? 'idle' : 'idle'; e.now = ''; e.queue = e.queue || [];
}

let saveTimer = null;
function save() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    const tmp = STATE_FILE + '.tmp';
    fs.writeFileSync(tmp, JSON.stringify(state, null, 1));
    fs.renameSync(tmp, STATE_FILE);
  }, 300);
}
if (deptTouched) save(); // 예전 저장에 부서를 채워 넣음 (없으면 게임 필멸자)
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
// 위험한 일: 지우기·배포·결제·push → 「허락」을 눌러도 기억하지 않고 매번 물어요 (사장님 11-11)
// 명령 한 토막(&&·|·; 로 나눈 것)마다 맨 앞 낱말로 본다. 읽기만 하는 명령(grep·git log 등)은 글 속에 낱말이 있어도 괜찮음.
const DANGER = [
  ['지우기', /^(rm|rmdir|del|erase|rd|unlink|shred|format|Remove-Item|ri|Clear-Content)(\s|$)|^git\s+(rm|clean)\b|^git\s+branch\s.*(-d|-D|--delete)\b|^git\s+reset\s.*--hard\b|^git\s+(stash\s+(drop|clear)|worktree\s+remove)\b|^(gh|npm|docker|kubectl)\s.*\b(delete|rm|rmi|prune|unpublish)\b/i],
  ['배포', /^(\S+\s+){0,2}(deploy|publish)\b|^(vercel|netlify|firebase|wrangler|fly|flyctl|heroku|gh-pages|surge)(\s|$)|^gh\s+(release\s+(create|upload)|workflow\s+run)\b|^(terraform|kubectl|helm)\s+(apply|install|upgrade)\b/i],
  ['결제', /\b(pay|payment|purchase|billing|charge|subscribe|stripe|paypal)\b|결제|구매/i],
  ['push', /^git\s+(-\S+\s+\S+\s+)*push\b|^(docker|podman|helm)\s+push\b|^gh\s+pr\s+merge\b|^gh\s+repo\s+sync\b/i],
];
const READ_ONLY = /^(grep|rg|findstr|echo|cat|type|head|tail|less|more|ls|dir|wc|Select-String|sls|Get-Content|gc|git\s+(log|show|diff|status|grep|blame))(\s|$)/i;
function dangerOfText(one) {
  const s = String(one || '').trim().replace(/^(sudo|&)\s+/, '').replace(/^cmd(\.exe)?\s+\/c\s+/i, '');
  if (READ_ONLY.test(s)) return '';
  for (const [kind, re] of DANGER) if (re.test(s)) return kind;
  return '';
}
// 위험하면 종류(지우기·배포·결제·push)를, 아니면 '' 를 돌려줌. 셸 명령 말고 연결 도구(MCP)도 이름으로 봄
function isDanger(tool, input) {
  if (tool === 'Bash' || tool === 'PowerShell') { for (const one of splitShell(input && input.command)) { const k = dangerOfText(one); if (k) return k; } return ''; }
  const name = String(tool || '');
  if (/(delete|trash|remove|destroy|purge)/i.test(name)) return '지우기';
  if (/(deploy|publish|release)/i.test(name)) return '배포';
  if (/(pay|billing|purchase|checkout|charge|stripe|subscription)/i.test(name)) return '결제';
  if (/(^|_|-)push(_|-|$)|merge_pull/i.test(name)) return 'push';
  return '';
}
// 규칙 자체가 위험한 일인지 (⚙ 설정 허락 목록에 「⚠ 매번 물어요」 표시)
function ruleIsDanger(rule) {
  const m = String(rule).match(/^(Bash|PowerShell)\((.*)\)$/);
  return m ? !!dangerOfText(m[2].replace(/:\*$/, '')) : !!isDanger(String(rule).replace(/\(.*$/, ''), {});
}
// 클로드 코드에 미리 넘겨도 되는 허락인지. 위험한 일까지 통째로 푸는 규칙(셸 전체·git:*·rm:* 등)은 빼서 회사 창구에서 한 번 더 봄
function safeForCli(rule) {
  const m = String(rule).match(/^([^(]+)(?:\((.*)\))?$/);
  if (!m) return true;
  if (m[1] === 'Bash' || m[1] === 'PowerShell') {
    if (!m[2]) return false;
    const pre = m[2].replace(/:\*$/, '').trim();
    return !dangerOfText(pre) && !BASH_TWO.includes(pre) && !/^(sh|bash|cmd|cmd\.exe|sudo|env|xargs|eval)$/i.test(pre);
  }
  return !isDanger(m[1], {});
}
function isAllowed(tool, input) {
  if (isDanger(tool, input)) return false;
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
  const p = { id: uid(), emp: empId, empName: emp ? emp.name : empId, tool, input, danger: isDanger(tool, input), label: describeTool(tool, input), detail: tool === 'Bash' || tool === 'PowerShell' ? input.command : JSON.stringify(input).slice(0, 400), rules: makeRules(tool, input), time: now(), res };
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
  if (answer === 'always' && p.danger) answer = 'once'; // 위험한 일은 기억하지 않음
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
  const deptName = empDeptName(emp);
  return `# 클로드 작업장 (알들 컴퍼니 「${deptName}」 부서, 사장님 PC의 업무 화면)
너는 「클로드 작업장」의 직원 **${emp.name}** 이고, 맡은 일은 **${emp.role}** 이다. 소속 부서는 **${deptName}** 이다.
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
    const cliRules = state.rules.filter(safeForCli);
    if (cliRules.length) a.push('--allowedTools', ...cliRules);
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
  if (state.settings.pixellabKey) env.PIXELLAB_API_KEY = state.settings.pixellabKey; // 🎨 PixelLab (출력·커밋 금지는 CLAUDE.md 규칙)
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
  const rep = { id: uid(), emp: emp.id, empName: emp.name, time: now(), from: task.from, kind: task.kind || 'ask', toBoss, task: task.text, text, files: findMedia(emp, text), cost: run.cost, denials: run.denials, isError: run.isError, stopped: !!run.stopped, needBoss: asks.length > 0, asks, read: false, forwards: [],
    summary: text.split('\n').map((l) => l.trim()).filter(Boolean).slice(0, 3), // 보고 글 앞쪽 3줄
    status: run.isError || run.stopped ? '문제 있음' : '완료' };
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

// 부서 클로드 팀은 사장님이 「만들기」를 누르거나 폴더를 직접 고를 때만 만들어요. 켤 때는 폴더를 비워 둡니다.
function workspaceReady() {
  try {
    const repo = state.settings.gameRepo;
    return !!(repo && fs.existsSync(path.join(repo, '.git')));
  } catch (e) { return false; }
}
function safeEmpDir(name) {
  return String(name || '직원').replace(/[\\/:*?"<>|\s]+/g, '_') || '직원';
}
function addClaudeMember(spec, picked) {
  return new Promise((resolve) => {
    const finish = (err, dir) => {
      if (err) return resolve({ name: spec.name, err });
      try {
        state.employees.push({
          id: uid(), name: spec.name, role: spec.role, dept: spec.dept, partner: !!spec.partner, lead: !!spec.lead,
          folder: dir, mode: '', model: '', sessionId: crypto.randomUUID(), started: false, queue: [], status: 'idle', now: '',
        });
        changed();
        resolve({ name: spec.name, made: true });
      } catch (e) { resolve({ name: spec.name, err: e }); }
    };
    try {
      if (state.employees.some((x) => x.name === spec.name)) return resolve({ name: spec.name, skipped: true });
      if (picked) {
        const dir = path.join(picked, safeEmpDir(spec.name));
        fs.mkdirSync(dir, { recursive: true });
        return finish(null, dir);
      }
      makeFolder(spec.name, finish);
    } catch (e) { resolve({ name: spec.name, err: e }); }
  });
}
let teamChain = Promise.resolve();
function ensureDeptClaude(opt) {
  const job = teamChain.then(() => ensureDeptClaudeNow(opt));
  teamChain = job.then(() => {}, () => {});
  return job;
}
async function ensureDeptClaudeNow(opt) {
  const onlyDept = opt && typeof opt.dept === 'string' ? opt.dept.trim() : '';
  const picked = opt && typeof opt.folder === 'string' ? opt.folder.trim() : '';
  if (onlyDept && !BOT_TARGETS.depts.some((d) => d.id === onlyDept)) {
    const err = new Error('없는 부서예요.');
    err.code = 'NO_DEPT';
    throw err;
  }
  if (picked) {
    let okDir = false;
    try { okDir = fs.statSync(picked).isDirectory(); } catch (e) { okDir = false; }
    if (!okDir) {
      const err = new Error('고른 폴더가 없어요. 폴더 주소를 확인해 주세요.');
      err.code = 'NO_FOLDER';
      throw err;
    }
  } else if (!workspaceReady()) {
    const err = new Error('설정에서 「게임 폴더」를 먼저 정해 주세요. 또는 폴더 주소를 직접 적으세요.');
    err.code = 'NO_REPO';
    throw err;
  }
  const made = [];
  const errors = [];
  for (const spec of claudeRoster()) {
    if (onlyDept && spec.dept !== onlyDept) continue;
    if (state.employees.some((e) => e.name === spec.name)) continue;
    const r = await addClaudeMember(spec, picked);
    if (r.err) errors.push(r.name + ': ' + (r.err.message || r.err));
    else if (r.made) made.push(r.name);
  }
  return { made, errors };
}
// 부서로 보낸 일을 그 부서 클로드 팀장 줄에도 넣어요. 그록에게 보내는 것은 그대로 둡니다.
function claudeLeadFor(target) {
  const d = grokDeptOf(target);
  if (!d) return null;
  const list = state.employees.filter((e) => empDeptId(e) === d.id);
  return list.find((e) => e.lead) || list.find((e) => /팀장$/.test(String(e.name || ''))) || null;
}
function assignDeptToClaude(target, command) {
  const lead = claudeLeadFor(target);
  if (!lead) return '';
  const text = `[${target} 부서 일]\n${String(command || '').trim()}\n너는 이 부서 클로드 팀장이다. 할 일을 나눠 맡고, 끝나면 쉬운 말로 짧게 보고해.`;
  order(lead.id, text, '사장님');
  return lead.name;
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
// 그록 답 첫 줄 [그록] [부서:이름] [relay:번호] 는 본문에서 빼요. 번호 찾기는 원문으로 해요. (#207 에서 맞춘 형식)
function stripRelayHead(text) {
  let s = String(text || '').replace(/^\s*\[(?:그록|클로드)\]\s*/, '');
  const lines = s.split('\n');
  if (lines.length) lines[0] = lines[0].replace(/\[부서:[^\]]*\]\s*/g, '').replace(/\[relay:[0-9a-f]+\]\s*/ig, '').trim();
  return lines.join('\n').replace(/\[relay:[0-9a-f]+\]\s*/i, '').trim();
}
async function sendToBot(item) {
  const cfg = botConfig(); if (!cfg) return;
  const emp = findEmp(item.emp);
  // 직원 저장 dept 는 id. 웹훅과 대화방 첫 줄 [부서:…] 는 이름(예: 홍보). 이름이 없을 때만 받는 곳을 'AI 협력'으로 둬요.
  const dept = emp ? empDeptName(emp) : '';
  const target = dept || 'AI 협력';
  const head = dept ? `[그록] [부서:${dept}] [relay:${item.id}]` : `[그록] [relay:${item.id}]`;
  const command = `${item.relay.paste}\n\n— 답은 깃허브 「AI협력 대화방」 ${ISSUE_URL()} 에 댓글로 달아 주세요. 첫 줄은 ${head} 로 적어 주세요.`;
  const body = JSON.stringify({ target, command, source: '클로드 회사', sentAt: new Date().toISOString(), relayId: item.id, replyTo: ISSUE_URL(), dept });
  try {
    const r = await fetch(cfg.url, { method: 'POST', headers: { authorization: 'Bearer ' + cfg.key, 'content-type': 'application/json; charset=utf-8' }, body });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    item.relay.sent = true; item.relay.sendError = '';
  } catch (e) { item.relay.sent = false; item.relay.sendError = '그록 봇에게 못 보냈어요 (' + e.message + '). 직접 붙여 넣어 주세요.'; }
  changed(); pollSoon();
}
// 깃허브 대화방 확인
let coopChat = [];
let pollTimer = null, etag = '', rateLeft = 60, rateReset = 0, coopStatus = { ok: false, at: '' };
function pollSoon(ms) { clearTimeout(pollTimer); pollTimer = setTimeout(pollIssue, ms || 1500); }
function nextPoll() {
  const waiting = state.grokLog.some((g) => g.relay && g.relay.state === 'waiting');
  let ms = state.settings.ghToken ? 20000 : waiting ? 20000 : grokWay() === 'bot' ? 180000 : 300000;
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
  // 그록 봇이 안 이어졌어도 「클로드↔그록 대화」 창을 위해 #207 은 천천히 읽어요
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
      coopChat = list.map((c) => {
        const body = String(c.body || '');
        const who = /^\s*\[그록\]/.test(body) ? 'grok' : /claude-workshop|^\s*\[클로드\]/.test(body) ? 'claude' : 'boss';
        const text = stripRelayHead(body.replace(/<!--[\s\S]*?-->/g, '').replace(/\n---\n_Generated by[\s\S]*$/, ''));
        return { id: c.id, who, time: c.created_at, text: text.slice(0, 6000), url: c.html_url };
      });
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
  let text = stripRelayHead(body);
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
  const e = findEmp(emp);
  const deptName = e ? empDeptName(e) : '';
  const deptTag = deptName ? `[부서:${deptName}] ` : '';
  const speaker = emp === 'boss' ? '[사장님]' : `[클로드 ${empName}]`;
  let paste = kind === 'image' ? `${deptTag}${speaker} 그림 그려 줘: ${text}` : kind === 'video' ? `${deptTag}${speaker} 영상 만들어 줘: ${text}` : `${deptTag}${speaker} ${text}`;
  if (!state.relayStarted) { paste = `(우리 팀 업무 공유판이야. 처음이면 먼저 읽고 여기 결정·규칙을 따라 줘: ${BOARD_URL})\n\n` + paste; state.relayStarted = true; }
  if (e) { e.status = 'waiting'; e.now = '그록 답 기다리는 중 (사장님이 옮겨 주는 중)'; }
  push('relay', {});
  const item = roomPost({ emp, empName, kind: emp === 'boss' ? 'boss' : 'ask', text: deptTag + (kind === 'image' ? '🎨 ' : kind === 'video' ? '🎬 ' : '') + text, files: files || [], relay: { state: 'waiting', kind, paste, way: grokWay() } });
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
  const { xaiKey, botKey, ghToken, pixellabKey, ...safeSettings } = state.settings; // 키는 화면에도 안 보냄
  const bc = botConfig();
  return {
    settings: { ...safeSettings, hasXaiKey: !!xaiKey, hasBotKey: !!botKey, hasGhToken: !!ghToken, hasPixellab: !!pixellabKey, botFrom: bc ? bc.from : '', grokWay: grokWay(), coop: coopStatus, grokSpent, grokPaste: grokWay() !== 'api', issueUrl: ISSUE_URL() },
    botTargets: BOT_TARGETS,
    botHistory: state.botHistory.slice(0, 50),
    grokLog: state.grokLog.slice(-150).map((g) => ({ ...g, files: g.files.map((f, i) => ({ i, name: path.basename(f), kind: /\.(mp4|webm|mov)$/i.test(f) ? 'video' : 'image' })) })),
    rules: state.rules,
    rulesAsk: state.rules.filter(ruleIsDanger), // 목록에 있어도 매번 다시 묻는 규칙 (⚙ 설정에 ⚠ 표시)
    claude: { ok: claude.ok, version: claude.version, error: claude.error, modes: claude.modes },
    employees: state.employees.map((e) => ({ id: e.id, name: e.name, role: e.role, dept: empDeptId(e), lead: !!e.lead, partner: !!e.partner, folder: e.folder, mode: e.mode, model: e.model, status: e.status, now: e.now, queue: e.queue.length, wait: (e.queue && e.queue[0]) ? String(e.queue[0].text).replace(/\s+/g, ' ').slice(0, 160) : '', task: e.task ? e.task.text : '', taskFrom: e.task ? e.task.from : '', startedAt: e.startedAt, hasSession: !!e.started })),
    reports: state.reports.slice(0, 120).map((r) => ({ ...r, files: r.files.map((f, i) => ({ i, name: path.basename(f), kind: /\.(mp4|webm|mov)$/i.test(f) ? 'video' : 'image' })) })),
    pending: [...pending.values()].map((p) => ({ id: p.id, emp: p.emp, empName: p.empName, tool: p.tool, danger: p.danger || '', label: p.label, detail: p.detail, rules: p.rules, time: p.time })),
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
    if (p === '/api/coop/chat') { if (u.searchParams.get('refresh')) pollSoon(200); return json(res, { items: coopChat, issueUrl: ISSUE_URL(), at: coopStatus.at }); }
    if (p === '/api/company/reports') {
      // 그록이 사장님 구글 드라이브에 쓰는 회사 보고 (사장님 11-11 「좋아」: 공개 저장소 대신 드라이브)
      const f = state.settings.reportsFile;
      if (!f) return json(res, grokFillCompanyReports({ ok: false, error: '아직 「☁ 회사 보고 폴더」를 정하지 않았어요.', items: [] }));
      try {
        const st = fs.statSync(f);
        let raw = JSON.parse(fs.readFileSync(f, 'utf8').replace(/^\uFEFF/, ''));
        if (!Array.isArray(raw)) raw = raw.reports || raw.items || [];
        const str = (v, n) => String(v == null ? '' : v).slice(0, n);
        const items = raw.slice(-200).map((r) => ({
          id: str(r.id, 80),
          time: str(r.time || r.sentAt || r.at, 40), target: str(r.target || r.dept, 80), command: str(r.command, 500), lead: str(r.lead || r.leader, 80),
          status: str(r.status, 40), summary: (Array.isArray(r.summary) ? r.summary : String(r.summary || '').split('\n')).map((x) => str(x, 300)).filter(Boolean).slice(0, 5),
          result: str(r.result || r.output || r.where, 300),
        })).sort((a, b) => String(b.time).localeCompare(String(a.time)));
        return json(res, grokFillCompanyReports({ ok: true, items, at: st.mtime }));
      } catch (e) { return json(res, grokFillCompanyReports({ ok: false, error: '보고 파일을 못 읽었어요: ' + e.message, items: [] })); }
    }
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
    if (p === '/api/conn/check') {
      const repo = state.settings.gameRepo;
      const run = (cmd, args, opt) => new Promise((ok) => execFile(cmd, args, { windowsHide: true, timeout: 120000, ...opt }, (err, out, errOut) => ok({ err, out: String(out || ''), errOut: String(errOut || '') })));
      if (b.id === 'github') {
        if (!repo || !fs.existsSync(path.join(repo, '.git'))) return json(res, { ok: false, error: '먼저 🎮 게임 폴더를 정해 주세요.' });
        // 실제로 올리지 않고(--dry-run) 올릴 수 있는지만 봄. 로그인이 안 돼 있으면 깃허브 로그인 창이 떠요.
        const r = await run('git', ['-C', repo, 'push', '--dry-run', 'origin', 'HEAD:refs/heads/claude/login-check']);
        const name = (await run('git', ['-C', repo, 'config', 'user.name'])).out.trim();
        const email = (await run('git', ['-C', repo, 'config', 'user.email'])).out.trim();
        const okPush = !r.err;
        const msg = okPush ? '올릴 수 있어요.' : /denied|403|Authentication|could not read|terminal prompts/i.test(r.errOut) ? '깃허브 로그인이 필요해요. 뜬 창에서 로그인한 뒤 다시 눌러 주세요.' : '확인 못 했어요: ' + r.errOut.trim().split('\n').slice(-2).join(' ');
        state.settings.ghPush = { ok: okPush, at: now(), msg, name, email };
        changed(); return json(res, { ok: true, result: state.settings.ghPush });
      }
      if (b.id === 'mcp') {
        if (!claude.ok) return json(res, { ok: false, error: '먼저 🧠 클로드 코드가 켜져 있어야 해요.' });
        const r = await run(claude.path, ['mcp', 'list'], { cwd: repo && fs.existsSync(repo) ? repo : ROOT, shell: claude.useShell, timeout: 60000 });
        const text = (r.out + r.errOut).trim() || '(답이 없어요)';
        state.settings.mcpList = { at: now(), text: text.slice(0, 3000), count: (text.match(/^\S.*?:/gm) || []).filter((l) => !/No MCP|Checking/i.test(l)).length };
        changed(); return json(res, { ok: true, result: state.settings.mcpList });
      }
      return json(res, { ok: false, error: '모르는 연결이에요.' });
    }
    if (p === '/api/bot/command') {
      // 「🏢 회사 일 시키기」: 바탕화면 명령창과 같은 곳으로 보냄.
      // 몸: {target, command, source: "알들 컴퍼니 명령창", sentAt, reportId}. 접속 정보는 🔌 연결 → 🤖 그록 봇에 저장된 것을 쓴다.
      const target = String(b.target || '').trim(), command = String(b.command || '').trim();
      if (!command) return json(res, { ok: false, error: '할 일을 적어 주세요. 예: 제로폰 오늘 정책 확인해서 보고해' });
      if (!target) return json(res, { ok: false, error: '보낼 곳을 골라 주세요.' });
      if (!companyTargetOk(target)) return json(res, { ok: false, error: '목록에 없는 이름이에요. 부서나 팀원을 골라 주세요.' });
      let claudeLead = '';
      try { claudeLead = assignDeptToClaude(target, command); } catch (e) { claudeLead = ''; }
      const cfg = botConfig();
      if (!cfg) {
        const extra = claudeLead ? ' 클로드 팀장 ' + claudeLead + '에게는 일을 넣어 두었어요.' : '';
        return json(res, { ok: false, error: '먼저 🔌 연결 → 🤖 그록 봇을 이어 주세요.' + extra, claudeLead });
      }
      const h = { id: uid(), time: now(), target, command, ok: false, result: '' };
      const reportId = grokReportIntake(target, command);
      try {
        const r = await fetch(cfg.url, { method: 'POST', headers: { authorization: 'Bearer ' + cfg.key, 'content-type': 'application/json; charset=utf-8' }, body: JSON.stringify({ target, command, source: '알들 컴퍼니 명령창', sentAt: new Date().toISOString(), reportId }) });
        h.ok = r.ok; h.result = r.ok ? '보냄' : '실패 ' + r.status;
      } catch (e) { h.result = '실패: ' + e.message; }
      grokReportSent(reportId, h.ok);
      state.botHistory.unshift(h); if (state.botHistory.length > 100) state.botHistory.length = 100;
      changed();
      return json(res, { ok: h.ok, error: h.ok ? '' : '못 보냈어요 (' + h.result + ')', claudeLead });
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
        let dept = (typeof b.dept === 'string' && BOT_TARGETS.depts.some((d) => d.id === b.dept)) ? b.dept : (e.dept || '');
        if (!BOT_TARGETS.depts.some((d) => d.id === dept)) dept = b.partner ? 'ai' : 'game';
        Object.assign(e, { name, role: String(b.role || '').trim() || '무엇이든', folder, mode: b.mode || '', model: String(b.model || '').trim(), partner: !!b.partner, dept });
        if (e.lead == null && ((dept === 'game' && e.name === '팀장') || (dept === 'ai' && (e.name === 'AI협력팀' || e.partner)))) e.lead = true;
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
      // 사장님이 만들기를 눌렀거나 폴더를 골랐을 때만. dept 가 있으면 그 부서만, 폴더가 있으면 그 안에 만들어요.
      try {
        const r = await ensureDeptClaude({ dept: typeof b.dept === 'string' ? b.dept : '', folder: typeof b.folder === 'string' ? b.folder : '' });
        if (r.errors.length) return json(res, { ok: false, error: r.errors[0], made: r.made });
        return json(res, { ok: true, made: r.made });
      } catch (e) { return json(res, { ok: false, error: e.message || '팀을 만들지 못했어요', made: [] }); }
    }
    if (p === '/api/employee/delete') { const e = findEmp(b.id); if (e) { stopEmp(e, true); state.employees = state.employees.filter((x) => x !== e); changed(); } return json(res, { ok: !!e }); }
    if (p === '/api/settings') {
      for (const k of ['gameRepo', 'workspace', 'defaultMode', 'claudeCmd', 'grokDir']) if (typeof b[k] === 'string') state.settings[k] = b[k].trim();
      if (typeof b.xaiKey === 'string' && b.xaiKey.trim()) state.settings.xaiKey = b.xaiKey.trim();
      if (b.xaiKeyClear) state.settings.xaiKey = '';
      if (b.grokBudget !== undefined && b.grokBudget !== '') state.settings.grokBudget = Math.max(0, Number(b.grokBudget) || 0);
      if (typeof b.grokDir === 'string') grokKnown = null;
      if (['paste', 'api', 'bot'].includes(b.grokMode)) state.settings.grokMode = b.grokMode;
      for (const k of ['botUrl', 'botTarget', 'companyUrl', 'reportsFile']) if (typeof b[k] === 'string') state.settings[k] = b[k].trim().replace(/^"|"$/g, '');
      if (typeof b.botKey === 'string' && b.botKey.trim()) state.settings.botKey = b.botKey.trim();
      if (typeof b.ghToken === 'string' && b.ghToken.trim()) state.settings.ghToken = b.ghToken.trim();
      if (b.botKeyClear) { state.settings.botKey = ''; state.settings.botUrl = ''; }
      if (b.ghTokenClear) state.settings.ghToken = '';
      if (typeof b.pixellabKey === 'string' && b.pixellabKey.trim()) state.settings.pixellabKey = b.pixellabKey.trim();
      if (b.pixellabClear) state.settings.pixellabKey = '';
      // 🐙 깃허브: 직원이 커밋할 때 쓸 이름·이메일 (게임 폴더 설정에 적음)
      for (const k of ['gitName', 'gitEmail']) {
        if (typeof b[k] === 'string' && b[k].trim() && state.settings.gameRepo) {
          execFile('git', ['-C', state.settings.gameRepo, 'config', k === 'gitName' ? 'user.name' : 'user.email', b[k].trim()], { windowsHide: true }, () => {});
        }
      }
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
  // 켤 때 직원 자리를 만들지 않아요. 부서 화면의 「만들기」나 직접 고른 폴더로만 만들어요.
  detectClaude().then(() => {
    console.log(claude.ok ? `클로드 코드 찾음 (${claude.version})` : '클로드 코드를 못 찾았어요. 설치 안내를 보세요.');
    changed();
    for (const e of state.employees) next(e); // 꺼지기 전에 남아 있던 일 이어서
  });
});

// ── 그록: 보고 창 더하기 ──
// 새 주소는 만들지 않아요. 위의 /api/company/reports 가 준 items 뒤에
// 접수 기록과 사장님께 가는 클로드 보고만 더합니다. state.reports 는 읽기만 해요.
const GROK_REPORT_STATUSES = new Set(['접수', '진행 중', '완료', '문제 있음']);
function grokReportFile() { return path.join(DATA, 'company-reports.json'); }
function grokReadArray(file) {
  try {
    const data = JSON.parse(fs.readFileSync(file, 'utf8'));
    return Array.isArray(data) ? data : [];
  } catch (e) { return []; }
}
function grokWriteLocal(list) {
  fs.mkdirSync(DATA, { recursive: true });
  const file = grokReportFile();
  const tmp = file + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(list, null, 1));
  fs.renameSync(tmp, file);
}
function grokKst(d) {
  const base = d instanceof Date ? d : new Date(d);
  const ms = base.getTime();
  if (Number.isNaN(ms)) return '';
  const t = new Date(ms + 9 * 60 * 60 * 1000);
  const p = (n) => String(n).padStart(2, '0');
  return t.getUTCFullYear() + '-' + p(t.getUTCMonth() + 1) + '-' + p(t.getUTCDate()) + ' ' + p(t.getUTCHours()) + ':' + p(t.getUTCMinutes());
}
function grokTimeText(time) {
  const s = String(time || '').trim();
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}/.test(s)) return s.slice(0, 16);
  return grokKst(s) || grokKst(new Date());
}
function grokReportMs(time) {
  const s = String(time || '').trim();
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}/.test(s)) {
    const ms = Date.parse(s.slice(0, 16).replace(' ', 'T') + ':00+09:00');
    if (!Number.isNaN(ms)) return ms;
  }
  const ms = Date.parse(s);
  return Number.isNaN(ms) ? 0 : ms;
}
function grokSafeUrl(u) {
  const s = String(u || '').trim();
  if (!/^https?:\/\//i.test(s)) return '';
  if (/[\s"'<>]/.test(s)) return '';
  return s;
}
function grokSafeLine(s) {
  const t = String(s || '').replace(/\s+/g, ' ').trim();
  if (!t) return '';
  if (/[A-Za-z]:\\/.test(t) || /\/Users\/|\/home\//.test(t)) return '';
  if (/bearer\s|api[_-]?key|webhook|비밀번호|암호|시크릿|secret|token/i.test(t)) return '';
  return t.slice(0, 180);
}
function grokDeptOf(target) {
  const t = String(target || '').trim();
  if (!t || t === '전체') return null;
  let d = BOT_TARGETS.depts.find((x) => x.name === t);
  if (!d) d = BOT_TARGETS.depts.find((x) => x.name.startsWith(t));
  if (!d) {
    const bot = BOT_TARGETS.bots.find((b) => b.name === t);
    if (bot) d = BOT_TARGETS.depts.find((x) => x.id === bot.dept);
  }
  return d || null;
}
function grokDeptName(name) {
  const t = String(name || '').trim();
  if (BOT_TARGETS.depts.some((d) => d.name === t)) return t;
  const d = grokDeptOf(t);
  return d ? d.name : '';
}
function grokCleanLines(lines) {
  const out = [];
  let inCode = false;
  for (const raw of lines) {
    const line = String(raw || '').trim();
    if (!line) continue;
    if (/^```/.test(line)) { inCode = !inCode; continue; }
    if (inCode || /```/.test(line) || /@전달/.test(line)) continue;
    const safe = grokSafeLine(line);
    if (safe) out.push(safe);
    if (out.length >= 3) break;
  }
  return out;
}
function grokClaudeStatus(r) {
  if (GROK_REPORT_STATUSES.has(r.status)) return r.status;
  if (r.stopped || r.isError) return '문제 있음';
  return '완료';
}
function grokClaudeCard(r) {
  if (!r || r.toBoss !== true) return null;
  const given = grokCleanLines(Array.isArray(r.summary) ? r.summary : []);
  const plain = String(r.text || '').replace(/```[\s\S]*?```/g, '\n');
  const lines = given.length ? given : grokCleanLines(plain.split('\n'));
  const found = plain.split('\n').filter((line) => !/@전달/.test(line)).join('\n').match(/https?:\/\/[^\s"'<>)]+/);
  const emp = state.employees.find((e) => (r.emp && e.id === r.emp) || (r.empName && e.name === r.empName));
  const deptName = emp ? empDeptName(emp) : '게임 필멸자';
  const card = {
    id: String(r.id || '').slice(0, 80),
    time: grokTimeText(r.time),
    target: deptName,
    command: String(r.task || r.command || '').split('\n')[0].replace(/\s+/g, ' ').trim().slice(0, 500),
    lead: String(r.lead || r.empName || '클로드').slice(0, 80),
    status: grokClaudeStatus(r),
    summary: lines.length ? lines : ['보고가 도착했어요.'],
    result: grokSafeUrl(r.result || r.where || (found ? found[0] : '')),
    source: '클로드',
    dept: deptName,
  };
  if (r.needBoss === true) card.needBoss = true;
  return card.id ? card : null;
}
function grokLocalCard(r) {
  if (!r || !r.id) return null;
  const target = String(r.target || '').trim().slice(0, 80);
  const dept = grokDeptOf(target);
  return {
    id: String(r.id).slice(0, 80),
    time: grokTimeText(r.time),
    target,
    command: String(r.command || '').replace(/\s+/g, ' ').trim().slice(0, 500),
    lead: String(r.lead || (dept && dept.lead) || '').slice(0, 80),
    status: GROK_REPORT_STATUSES.has(r.status) ? r.status : '접수',
    summary: grokCleanLines(Array.isArray(r.summary) ? r.summary : []).slice(0, 3),
    result: grokSafeUrl(r.result || r.where),
    source: '그록',
    dept: dept ? dept.name : '',
  };
}
function grokPublicItem(r) {
  if (!r || typeof r !== 'object') return null;
  const target = String(r.target || '').trim().slice(0, 80);
  const id = String(r.id || '').trim().slice(0, 80);
  const known = GROK_REPORT_STATUSES.has(r.status) ? r.status : String(r.status || '').trim().slice(0, 40);
  const item = {
    time: grokTimeText(r.time),
    target,
    command: String(r.command || '').replace(/\s+/g, ' ').trim().slice(0, 500),
    lead: String(r.lead || '').trim().slice(0, 80),
    status: known || '완료',
    summary: grokCleanLines(Array.isArray(r.summary) ? r.summary : String(r.summary || '').split('\n')),
    result: grokSafeUrl(r.result),
    source: r.source === '클로드' ? '클로드' : '그록',
    dept: grokDeptName(target),
  };
  if (id) item.id = id;
  if (r.needBoss === true) item.needBoss = true;
  return item;
}
function grokFillCompanyReports(payload) {
  try {
    const base = payload && typeof payload === 'object' ? { ...payload } : { ok: false, items: [] };
    const items = (Array.isArray(base.items) ? base.items : []).map(grokPublicItem).filter(Boolean);
    const ids = new Set(items.map((it) => it.id).filter(Boolean));
    for (const raw of grokReadArray(grokReportFile())) {
      const card = grokLocalCard(raw);
      if (!card || ids.has(card.id)) continue;
      ids.add(card.id);
      items.push(card);
    }
    for (const r of state.reports.slice(0, 120)) {
      const card = grokClaudeCard(r);
      if (!card || ids.has(card.id)) continue;
      ids.add(card.id);
      items.push(card);
    }
    items.sort((a, b) => grokReportMs(b.time) - grokReportMs(a.time));
    base.items = items;
    return base;
  } catch (e) {
    return payload || { ok: false, items: [] };
  }
}
function grokReportIntake(target, command) {
  const id = 'rpt-' + uid();
  const dept = grokDeptOf(target);
  const item = {
    id,
    time: grokKst(new Date()),
    target,
    command: String(command || '').replace(/\s+/g, ' ').trim().slice(0, 500),
    lead: dept && dept.lead ? dept.lead : '',
    status: '접수',
    summary: ['명령을 받았어요. 팀장이 확인하면 진행으로 바뀌어요.'],
    result: '',
    source: '그록',
    dept: dept ? dept.name : '',
  };
  try {
    const list = grokReadArray(grokReportFile());
    list.unshift(item);
    if (list.length > 200) list.length = 200;
    grokWriteLocal(list);
  } catch (e) { console.error('[보고 창] 접수 기록을 저장하지 못했어요'); }
  return id;
}
function grokReportSent(id, ok) {
  if (!id || ok) return;
  try {
    const list = grokReadArray(grokReportFile());
    const i = list.findIndex((r) => r && r.id === id);
    if (i < 0) return;
    list[i] = { ...list[i], status: '문제 있음', summary: ['그록 봇에게 일을 넘기지 못했어요. 연결을 확인한 뒤 다시 보내 주세요.'] };
    grokWriteLocal(list);
  } catch (e) { console.error('[보고 창] 문제 상태를 저장하지 못했어요'); }
}
