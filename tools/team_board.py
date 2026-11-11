#!/usr/bin/env python3
"""업무 공유판 자동 채우기.

handoff/GROK_BRIEFING_ko.md 안의 <!-- AUTO:START --> ~ <!-- AUTO:END --> 칸을
저장소 기록(게임 반영 PR, 팀 회의 교본 회의 기록·미정, 진행 중 브랜치, CLAUDE.md 게임 핵심)으로 새로 채운다.
그록·다른 클로드 같은 AI 동료가 주소 하나만 읽으면 지금 일을 알 수 있게 한다.

쓰는 법:  python3 tools/team_board.py [--main origin/main]
(깃허브 액션 .github/workflows/team-board.yml 이 main 에 올라올 때마다 저절로 돌린다)
"""
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / 'handoff' / 'GROK_BRIEFING_ko.md'
BOOK = ROOT / 'handoff' / 'claude' / 'TEAM_MEETING_TEXTBOOK_ko.md'
RAW = 'https://raw.githubusercontent.com/meca12944/thor-like-game/main/'
KST = timezone(timedelta(hours=9))


def git(*a):
    try:
        return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except Exception:
        return ''


def main_ref():
    if '--main' in sys.argv:
        return sys.argv[sys.argv.index('--main') + 1]
    for r in ('origin/main', 'main', 'HEAD'):
        if git('rev-parse', '--verify', '-q', r).strip():
            return r
    return 'HEAD'


def shipped(ref, n=12):
    """main 에 들어간 PR (최근 n개)"""
    out = []
    for line in git('log', ref, '--merges', '--first-parent', '--format=%cs\x1f%s\x1f%b\x1e', '-n', '80').split('\x1e'):
        p = line.strip().split('\x1f')
        if len(p) < 3:
            continue
        m = re.match(r'Merge pull request #(\d+) from \S+', p[1])
        if not m:
            continue
        title = p[2].strip().split('\n')[0] or p[1]
        out.append(f'- {p[0][5:]} · #{m.group(1)} {title}')
        if len(out) >= n:
            break
    return out


def in_progress(ref, days=10):
    """main 에 아직 안 들어간, 최근에 움직인 작업 브랜치"""
    out = []
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = git('for-each-ref', '--sort=-committerdate', '--format=%(refname:short)\x1f%(committerdate:iso-strict)\x1f%(subject)', 'refs/remotes/origin/')
    for line in rows.splitlines():
        name, when, subj = (line.split('\x1f') + ['', '', ''])[:3]
        if name in ('origin/main', 'origin/HEAD', 'origin') or not when:
            continue
        try:
            t = datetime.fromisoformat(when)
        except ValueError:
            continue
        if t < since:
            break
        if subprocess.run(['git', 'merge-base', '--is-ancestor', name, ref], cwd=ROOT, capture_output=True).returncode == 0:
            continue  # 이미 게임에 들어감
        out.append(f'- {t.astimezone(KST):%m-%d} · `{name.replace("origin/", "")}` — {subj[:120]}')
        if len(out) >= 10:
            break
    return out


def book_meetings(n=10):
    s = BOOK.read_text(encoding='utf-8')
    k = s.find('# 10. 회의 기록 목록')
    if k < 0:
        return []
    rows = [l for l in s[k:].split('\n---')[0].splitlines() if l.startswith('| ') and not l.startswith('| 날짜') and not l.startswith('|---')]
    out = []
    for l in rows[-n:][::-1]:
        c = [x.strip() for x in l.strip('|').split('|')]
        if len(c) < 4:
            continue
        concl = c[3] if len(c[3]) <= 260 else c[3][:257] + '…'
        out.append(f'- **{c[0]} {c[1]}** — {concl}')
    return out


def book_open():
    s = BOOK.read_text(encoding='utf-8')
    k = s.find('# 부록. 미정·확인할 것')
    return [l for l in s[k:].splitlines()[1:] if l.startswith('- ')] if k >= 0 else []


def game_core():
    s = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
    m = re.search(r'## 게임 핵심[^\n]*\n(.*?)\n## ', s, re.S)
    return m.group(1).strip() if m else ''


def build():
    ref = main_ref()
    head = git('log', '-1', ref, '--format=%h %cs').strip()
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    L = []
    L.append(f'> 🔄 이 칸은 **저절로 채워져요** (마지막: {now} 한국 시각, main `{head}`). 고치지 말고 `tools/team_board.py` 를 고쳐요.')
    L.append('')
    L.append('## 0. AI 동료에게 (그록 · 다른 클로드) — 먼저 읽기')
    L.append('- 이 문서 주소 하나로 지금 일을 알 수 있어요: ' + RAW + 'handoff/GROK_BRIEFING_ko.md')
    L.append('- 팀: **사장님**(결정·허락) · **클로드 팀**(팀장·UI·스토리·몬스터·효과·모션·AI협력팀, 게임 코드와 문서) · **그록**(그림·영상·아이디어).')
    L.append('- 말은 **한국어, 쉬운 말**로. 사장님 말씀(「」)이 가장 높고, 나중 말씀이 먼저 말씀을 이겨요.')
    L.append('- 정해진 것은 아래 「최근 결정」과 정본 문서를 따르세요. 정본에 없는 생각은 「제안」이라고 밝혀 주세요.')
    L.append('- 열쇠(API 키)·비밀번호는 서로 달라고 하지 않아요. 결과 파일은 공유 드라이브 폴더(「★ 그록 부탁」)에 올려요.')
    L.append('- 이 문서에 없는 것을 아는 척하지 마세요. 모르면 「모름」이라고 쓰고 사장님께 물어요.')
    L.append('')
    core = game_core()
    if core:
        L.append('## 게임 핵심 (사장님 결정, CLAUDE.md 그대로)')
        L.append(core)
        L.append('')
    L.append('## 최근 게임에 들어간 것 (main, 새것부터)')
    L += shipped(ref) or ['- (기록 없음)']
    L.append('')
    prog = in_progress(ref)
    if prog:
        L.append('## 지금 하고 있는 작업 (아직 게임 밖, 최근 10일)')
        L += prog
        L.append('')
    L.append('## 최근 결정 (팀 회의 교본 10장, 새것부터)')
    L += book_meetings() or ['- (기록 없음)']
    L.append('')
    op = book_open()
    if op:
        L.append('## 아직 안 정한 것 (교본 부록)')
        L += op
        L.append('')
    L.append('## 정본 문서 바로가기 (글 그대로 읽기)')
    for name, p in [('팀 회의 교본 (모든 결정)', 'handoff/claude/TEAM_MEETING_TEXTBOOK_ko.md'),
                    ('모션 교과서 (그림·움직임)', 'handoff/claude/MOTION_TEXTBOOK_ko.md'),
                    ('몬스터 교본', 'handoff/claude/MONSTER_TEXTBOOK_ko.md'),
                    ('세계·이야기 정본', 'docs_story/MASTER_PLAN_정본_20261024_ko.md'),
                    ('작업 규칙 (CLAUDE.md)', 'CLAUDE.md')]:
        if (ROOT / p).exists():
            L.append(f'- {name}: {RAW}{p}')
    L.append('- 게임 해 보기: https://meca12944.github.io/thor-like-game/test128/')
    return '\n'.join(L)


def main():
    s = BOARD.read_text(encoding='utf-8')
    a, b = '<!-- AUTO:START -->', '<!-- AUTO:END -->'
    if a not in s or b not in s:
        sys.exit('업무판에 AUTO 표시가 없어요')
    new = s[:s.index(a) + len(a)] + '\n' + build() + '\n' + s[s.index(b):]
    stamp = lambda t: re.sub(r'^> 🔄.*$', '', t, flags=re.M)
    if stamp(new) != stamp(s):
        BOARD.write_text(new, encoding='utf-8')
        print('업무 공유판을 새로 채웠어요')
    else:
        print('바뀐 것 없음')


if __name__ == '__main__':
    main()
