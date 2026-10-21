# 주인공2 (hero_v6 미니 캐릭터, v7 디자인) — 2026-10-21 저장·정리

사장님 지시: 망토와 코트 자락은 구현이 어려워 주인공을 다시 디자인. 원화 `ref/turnaround_v7.jpg`(최종), `ref/turnaround_v6.jpg`(앞 판).

## 게임에 쓸 것 → `final/`
- `final/<동작>/<방향>/000.png..` + `timing.json`(프레임별 틱, 60틱/초), 전체 목록 `final/manifest.json`
- 256 캔버스, 발 기준점 (128, 189), 키 124px(기존 미니와 같은 SD 비율)
- 방향: south, south-east, east, north-east, north. **west / south-west / north-west는 east / south-east / north-east 좌우 반전**
- 8방향 정지 그림: `final/rot/`
- 확인: `hero_v6_all_sheet.png`(전 프레임), `hero_v6_all_motions.mp4`(3동작 × 5방향 재생)

| 동작 | 남 | 남동 | 동 | 북동 | 북 |
|---|---|---|---|---|---|
| 대기 | 6프레임/48틱 | 6/48 | 6/48 | 6/48 | 6/48 |
| 걷기 | 8/48 | 8/48 | 9/52 | 10/50 | 8/48 |
| 달리기 | 8/40 | 8/40 | 10/44 | 9/36 | 8/40 |

다시 뽑기: `python3 export_final.py` (원본 위치는 `make_sheet_src.py`), 확인 시트·영상은 `python3 make_sheet.py`.

## 디자인
`ref/south_ref_256_v7.png` — 짧은 헝클어진 머리, 엉덩이에서 끝나는 남색 상의(코트 자락 없음), 금색 장식 견갑, 가운데 금색 자수, 갈색 토시, 금색 무릎 보호대, 버클 장화, 오른손에 아래로 든 장검. 원화를 그대로 줄이면 머리가 작고 몸이 가늘어져서(어깨 41px vs 기존 77px), 기존 정면 스프라이트를 v7 겉모습으로 편집해 만들었다. 8방향 PixelLab 캐릭터는 `rot/pick.json`.

## 만든 방법
- **옆·북동** (`anim.py` → `seam.py`/`pick_seam.py` 이음새 보간 → `post_run.py` → `check_run.py`): 바닥선 189 고정, 몸통 x 5프레임 원형 평균, 틱은 디딘 발 이동 거리 ÷ 속도. 옆 달리기 발 미끄러짐 51.8 → 8.6px.
- **정면·뒷면·남동** (핵심 자세 방식, `handoff/claude/MOTION_NS_KEYPOSE_ko.md`): `ns_keys.py` 오른발·왼발 자세 2장 → `ns_tween.py` 사이 프레임 → `ns_cycle.py` 8프레임 → `ns_polish2.py`.
- **대기**: `idle_pingpong.py` (0-1-2-3-2-1 왕복).

### 정면 달리기·정면 대각 수정 기록
원인:
1. 정면 달리기 키 포즈의 왼손이 허리에 붙어 있고 사이 프레임은 팔을 흔들어서, 키 프레임마다 팔이 튐. 칼 각도 ±7°.
2. 예전 `ns_polish.py`가 프레임마다 따로 높이를 잘라서 머리가 박자 없이 최대 6px 출렁임.
3. 남동은 글자 지시 애니메이션이 옆모습 쪽으로 돌아가며 칼이 뒤집히고(-80° → +27°) 달리기가 뻣뻣함.

해결: `ns_polish2.py`(클립 단위 바닥 맞춤 + 걸음 박자 머리 높이, 걷기 1px·달리기 2px), `ns_pixfix.py`로 정면 달리기 키의 팔만 고쳐(R s71, L s72) 다시 생성(칼 ±4°), 남동은 핵심 자세 방식으로 새로 만듦.

## 남은 것
- 북동 걷기·달리기는 글자 지시 방식이라 옆모습 쪽으로 도는 경향이 있을 수 있음. 리네트 방 최종 방식(동작당 약 18)으로 다시 하면 약 36.
- 정면 달리기 7번째 프레임 실루엣 변화가 조금 큼(눈에 크게 띄지 않음).
- 공격·대시·점프·피격·사망·시전(`plan.json` phaseB)은 별도 견적.
- `test128` 게임 연결(`hero8.json` 형식 변환)은 아직 안 함.

## 사용량: 412회 (`usage.jsonl`)
편집(Pro) 150, 캐릭터 동작 128, 사이 프레임 68, 회전 24, 도트 변환 20, Pixen 편집 18, 배경 제거 4.

## 폴더
- `final/` 게임용 최종본 · `ref/` 원화·기준 그림 · `rot/s4` 쓰는 회전 · `anim/`, `ns/` 작업 원본(스크립트가 이 경로를 씀)
- `old/` 쓰지 않는 판(허리 손 정면 달리기, 편집 v2 팔 수정판, 글자 지시 남동, 회전 s1~s3 등)
- `compare/` 비교 그림·옛 확인 영상 · `logs/` 실행 기록
- 스크립트: `pl.py` API(키는 환경변수 `PIXELLAB_API_KEY`에서만), `rotate.py`, `anim.py`, `seam.py`, `pick_seam.py`, `post_run.py`, `check_run.py`, `idle_pingpong.py`, `ns_*.py`, `edit_*.py`, `to_pixel.py`, `cut_refs.py`, `make_sheet*.py`, `export_final.py`
