# 「필멸자」 히로인 7명 현행 레퍼런스 인덱스 (2026-10-18 21:55 KST 작성)

> **갱신 2026-10-18 22:37 KST (유나)**: 오너가 유나를 **try2 바디슈트 디자인**으로 확정. option1/try3를 대체한다. try3 파일은 참고용으로만 보관. 아래 유나 행 참고. (`HEROINE_OVERVIEW_sheet.png`는 21:55 기준이라 유나 열이 아직 try1이다. 다시 만들지 않았다.)

이 폴더에는 새로 만든 파일만 있다. 원본은 복사·수정·이동하지 않았고, 시트는 원본을 읽어서 합성했다 (`make_overview.py`).

## 파일
- `HEROINE_OVERVIEW_sheet.png`: 메인 시트. 열마다 히로인 1명. 위에는 승인 마스터 일러스트 정면(턴어라운드에서 정면 그림만 잘라 300px 높이로 맞춤), 아래에는 **117px 미니 픽셀(heroines_vid 신규 세트)의 정면 서 있는 자세**를 3x nearest로 키운 것. 배경은 회색.
- `HEROINE_ingame_test128_v2_sheet.png`: 보조 시트. test128(`index128.html`)이 **지금 실제로 그리는** NPC v2 스프라이트 (`assets/npcs/v2/<id>.png`, down 행 idle 0~3, 4x).
- `HEROINE_minis_idle_ingame_v2.gif`: 위 v2 idle(down) 4프레임 애니메이션 (4x, 프레임당 250ms = `NPC_V2_CFG.idleTicks` 15틱 @60fps).
  - 117px 신규 세트에는 idle 모션이 **아예 없다** (walk/run/atk1-3/dash/hit/cast(skill)만 있음). 그래서 요청한 `HEROINE_minis_idle.gif`는 신규 세트로 만들 수 없었다. 대신 게임 내 v2 idle로 만들었고, 신규 세트로 오해하지 않도록 파일 이름에 `_ingame_v2`를 붙였다.

## 판정 근거 (공통)
- mtime: town-demo 안의 히로인 원본은 전부 10-18 15:28~15:30 KST에 한꺼번에 복사된 것이라 **mtime으로는 신·구를 구분할 수 없다**. 그래서 문서 기록과 실제 이미지 확인으로 판정했다.
- 일러스트: `char_v4/heroines_progress.md` (히로인 표), `char_v4/cast_progress.md` (리네트 행 "try2 CONFIRMED by owner"), `heroines_vid/yuna/README.md` 19번 항목.
- 미니: `char_v4/pixellab/heroines_vid/<name>/` (히로인별 전담 봇이 만든 8모션×8방향 117px 세트). 각 NOTES/README에는 "test128 미연동, 커밋 안 함"으로 적혀 있다. 프레임은 기본 자세(base)의 정면 픽셀판을 썼고, 정면 픽셀 base가 없는 마렌·유나는 walk 정면 000 프레임을 썼다 (영상의 첫 프레임 = 기본 자세 이미지).
- 실제 게임 내: `index128.html` 975~988행 `[npc_v2]` 블록이 `assets/npcs/v2/<id>.png`를 불러온다 (README 기준 "approved 2026-10-17"). heroines_vid 세트를 참조하는 곳은 빌드 어디에도 없다.

## 히로인별
| 이름 | id | 일러스트 원본 | 미니 원본 (메인 시트) | 판정 근거 | 의문점 |
|---|---|---|---|---|---|
| 이벨린 | c_priest | `char_v4/work/evelyn_master_try1.jpg` | `char_v4/pixellab/heroines_vid/evelyn/base/px_front.png` (마젠타 배경 키잉) | progress 표에 턴어라운드 = try1(+1b). 미니는 progress.md "COMPLETE" 세트의 base | progress 표 status가 **"made (no-approval run)"**: 오너 승인 기록을 찾지 못했다. try1b는 보조판으로 보고 쓰지 않았다. template3/base/px_front.png(외곽선을 추가한 3방향 템플릿 준비본)도 있지만 모션 세트의 기준이 아니라서 쓰지 않았다 |
| 마렌 | f_diver | `char_v4/work/maren_master_try1.jpg` | `char_v4/pixellab/heroines_vid/maren/frames/walk/down/000.png` | progress 표에 "turnaround confirmed" | 정면 픽셀 base PNG가 없다 (base/는 1280x720 원화, base3/는 3방향 템플릿 준비본). 그래서 walk 정면 0프레임을 썼다. try1b/1c는 쓰지 않았다 |
| 유나 | d_yuna | `char_v4/work/yuna_master_try2.jpg` (`yuna_master_try2_h97.png`: 검은 바디슈트+보라 라인, 은색 어깨·팔 갑옷, 가슴 컷아웃, 힐, 검) | `char_v4/pixellab/heroines_vid/yuna/px_walk_front/000.png` (**try1 디자인 그대로, 아직 try2로 재작업 안 됨**) | **[갱신 2026-10-18 22:37 KST] 오너가 try2 바디슈트 디자인을 확정**. option1/try3(흰 오프숄더+검은 스커트, 작은 가슴 수정판)을 대체한다. 프로필·게임 내 초상화 기준 = try2. 흉상 `docs_art/bust/d_yuna/` = try2 세트(`d_yuna_try2_backup/` 최상위에서 복원), 입절 `assets/tachie/d_yuna_*.png` = try2b(`char_v4/work/yuna_tachie_try2b.py`) | 이전 판정(README 19번 "try1 유지 확정")은 이 결정으로 무효. try1/option1/try3 파일은 **참고용으로만 보관**: `docs_art/bust/d_yuna_try3/`, `d_yuna_try3_backup/`, `assets/tachie/_backup_d_yuna_try3/`, `char_v4/work/yuna_master_try3*.png`, `yuna_bust_base_try3.png`. `assets/tachie/_backup_d_yuna_try2`는 구 벡터풍 그림이라 계속 **사용 금지**. 117px 미니 세트는 아직 try1 의상이다 |
| 베일라 | h_mystic | `char_v4/work/veyla_master_try2.jpg` | `char_v4/pixellab/heroines_vid/veyla/base/base_front_px.png` (마젠타 키잉) | progress 표: "try2 (+2b; old try1 bodysuit superseded)". 미니 NOTES에도 refs = master try2로 적혀 있다 | status "**made (no-approval run)**": 오너 승인 기록 없음. 그리고 `veyla/motions/walk/` 폴더가 **비어 있다** (walk 프레임 누락, 다른 모션은 있음) |
| 로자린드 | e_tailor | `char_v4/work/rosalind_master_try1.jpg` | `char_v4/pixellab/heroines_vid/rosalind/base/px/base_d.png` | progress 표에 "turnaround confirmed" | README에 적힌 `out/<motion>/<dir>/frame_XX.png` 폴더가 이 사본에는 **없다** (PNG 60개뿐: base, sheets, previews). 그래서 개별 모션 프레임은 확인하지 못했고 base 정면만 썼다. template_prep/base3/px/base_d(3방향 템플릿 준비본)는 쓰지 않았다 |
| 자이라 | g_dancer | `char_v4/work/zaira_master_try2.jpg` | `char_v4/pixellab/heroines_vid/zaira/base/zaira_base_front.png` (마젠타 키잉) | progress 표: 턴어라운드 = try2 "turnaround confirmed" | try2b는 쓰지 않았다. 게임 내 v2 스프라이트가 try1(긴 붉은 드레스)인지 try2인지는 32x29 해상도라서 판별하기 어렵다 |
| 리네트 | a_tailor | `char_v4/work/a_tailor_master_try2.jpg` (붉은 비키니 상의 + **붉은 미니스커트**) | `char_v4/pixellab/heroines_vid/linette/base/down.png` | cast_progress.md: "**try2 CONFIRMED by owner**". 붉은 미니스커트 조건과도 일치. 미니 세트는 지시대로 heroines_vid/linette | **주의: 이름이 `a_tailor_master_final.png`인 파일은 구 디자인(파란 원피스)이다.** heroines_progress.md 표가 아직 이 파일을 가리키고 있지만 낡은 기록이다. 쓰면 안 된다. 미니의 머리색이 일러스트보다 연한 금발/핑크 기운이 있다 (NOTES "v2 base: pale skin"). 게임 내 v2 a_tailor는 **구 파란 옷 디자인**이다 (보조 시트에 빨간 경고 표시) |

## 사용 금지 / 구버전 (이번 확인에서 발견)
- `char_v4/work/a_tailor_master_final.png`, `_s0/_s1/_s2`, `_v2/_v3`, `lynette_master_try1.jpg`: 리네트 구 디자인 (파란 원피스)
- ~~`char_v4/work/yuna_master_try2*.jpg`: 유나 try2 (취소됨)~~ → **2026-10-18 22:37 KST 오너가 try2를 다시 확정, 현행 원본이 됨.** 대신 유나 option1/try1·try3(흰 오프숄더+검은 스커트) 파일은 참고용 보관만 한다 (`yuna_master_try1*`, `yuna_master_try3*`, `docs_art/bust/d_yuna_try3*/`, `assets/tachie/_backup_d_yuna_try3/`)
- `assets/tachie/_backup_d_yuna_try2/`: 유나 구 벡터풍 입절 (try2 디자인이지만 그림체가 다름, 사용 금지)
- `char_v4/work/veyla_master_try1.jpg`: 베일라 try1 바디슈트 (대체됨)
- `char_v4/work/zaira_master_try1*.jpg`: 자이라 try1
- `assets/npcs/v2/a_tailor.png`: 게임 내 리네트, 구 디자인
- `char_v4/pixellab/{a_tailor,e_tailor,f_diver,g_dancer}/`: 이전 PixelLab 128 계열. heroines_vid 영상 세트 이전 것으로 판단해서 쓰지 않았다

## 남은 불확실성 요약
1. 이벨린·베일라: progress 표 status가 "no-approval run"이다. 오너 승인 기록이 없다.
2. heroines_vid 117px 세트는 7명 모두 게임(test128)에 연동되지 않았다. 게임이 실제로 쓰는 것은 v2 32x29 스프라이트다 (리네트는 구 디자인).
3. 117px 세트에는 idle 모션이 없다. "정면 대기"는 기본 자세 base/walk 0프레임으로 대신했다.
4. 로자린드는 모션 프레임 폴더가 빠져 있고, 베일라는 walk 폴더가 비어 있다 (이 사본 기준).
