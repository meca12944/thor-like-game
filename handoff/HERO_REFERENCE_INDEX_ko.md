# 「필멸자」 주인공 레퍼런스 공식 인덱스 (2026-10-18 작성)

이 폴더의 파일은 원본을 **복사**한 것이다. 원본은 옮기거나 지우지 않았다. 주인공 작업은 **여기 있는 것만** 기준으로 쓴다.
시각은 모두 파일 mtime 기준이며 KST로 표기한다.

## 1. 공식(확정) 레퍼런스
| # | 파일 | 원본 경로 | 날짜 (KST) | 기준 용도 |
|---|---|---|---|---|
| 01 | 01_master_illustration.jpg | char_v4/work/hero_master_try1.jpg | 10-18 15:28 | **주인공 마스터 일러스트**: 정면·측면·후면 턴어라운드. 긴 흑발, 금장 트림 검은 코트, 붉은 망토 안감, 금 견갑은 캐릭터 **왼쪽 어깨에만**, 망토 유지 |
| 02 | (없음) 02_profile_normal | **현행 확정본 없음.** 아래 3절 후보 참고 | – | 일반형 프로필·대화 바스트 |
| 03 | 03_demon_A_illust_candidate.png | char_v4/pixellab/hero/maou_design/illust/maouA_illust_try1.png | 10-18 15:31 | 마왕형 A안 「잠식」 일러스트(README_A 기준 "초상용"). 전신 턴어라운드라 바스트는 아님. **03 프로필 후보** |
| 04 | 04_pixel_idle_front_master.png | char_v4/pixellab/hero/vid/px_idle5h5_down/000.png | 10-18 21:37 | **픽셀 얼굴·머리 마스터**: 배포된 idle_down 정면 |
| 04b | 04b_pixel_idle_front_v5h_base.png | char_v4/pixellab/hero/vid/v5h/base/idle_down/000.png | 10-18 21:38 | v5h base idle_down (px_idle5h5_down에서 빌드. 21:38에 다른 작업자가 갱신해서 04와 바이트가 다름) |
| 05 | 05_pixel_front_walk_r4_f000.png | char_v4/pixellab/hero/vid/v5h/r4/walk_down/000.png | 10-18 21:31 | 정면 걷기 = 3/4 방향 스터디 r4 (전체 프레임은 원본 r4/walk_down/000-011) |
| 05b | 05b_front_walk_r4_check.png | v5h/r4/preview/v5h-r4_front_walk_check.png | 10-18 21:31 | r4 검수 시트 |
| 06 | 06_combo_trail_a45_hits.png | v5h/fx/preview/v5h-fxw1_hits_a45.png (= v5h/base/preview/v5h-base_combo3_fx_a45_hits.png) | 10-18 21:15 | combo3 검 + 궤적 **a45 (투명도 55%)** 승인본. 프레임 원본: v5h/fx/trail_w1_a45/, v5h/base/atk_combo3_* |
| 07 | 07_user_3q_ref.jpg | /workspace/yt_study/walkdir/user_ref/three_quarter_ref.jpg | 10-18 21:06 | 사용자가 준 3/4 방향 레퍼런스 |
| 08 | 08_demon_A_final_board.png | maou_design/maou_A_final_board.png | 10-18 15:31 | 마왕형 A안 「잠식」 최종 보드 |
| 09 | 09_demon_A_turnaround.png | maou_design/maou_A_turnaround.png | 10-18 15:31 | 마왕형 A 픽셀 턴어라운드 (비율 수정판 base8_A/recolor_v3) |
| 10 | 10_r1_front_render_check.png | v5h/r1/preview/v5h-r1_front_check.png | 10-18 20:20 | 정면 r1 렌더링 승인본 검수 시트 |
| 11 | 11_v5h_CURRENT.md | v5h/CURRENT.md | 10-18 21:15 | v5h 모션별 최신 폴더 표 |

개요 시트: HERO_REFERENCE_sheet.png (01, 03, 04, 05, 06, 07, 09를 나란히 배치)

## 2. 결정 사항 / 규칙
- 마스터 일러스트 = hero_master_try1. 머리를 키운 v2/v3, 망토를 뺀 try2는 **반려**.
- 픽셀 표준 = **v5h (5등신, 정수리부터 피부 턱까지)**: char_v4/pixellab/hero/vid/v5h/ (CURRENT.md, SCALE_STANDARD_v5h.json)
- 픽셀 얼굴·머리 마스터 = 배포된 idle_down 정면 (px_idle5h5_down / v5h base idle_down)
- 정면은 r1 렌더링 승인. 정면 걷기는 3/4 방향 스터디 r4로 진행 중 (v5h/r4, r4/CHANGES.md)
- combo3 검과 궤적 a45 (투명도 55%) 승인: v5h/base + v5h/fx/trail_w1_a45. a10~a35는 레거시
- 마왕형 = A안 「잠식」 (maou_design/README_A.md). base8_A/src/*.png (약 4등신, 비율 틀림)는 참고용
- 규칙 문서 (/workspace/yt_study/):
  - MOTION_RULES_ko.md (10-18 15:53)
  - sword/SWORD_ARC_RULES_ko.md (17:24)
  - rendering/RENDERING_RULES_ko.md (19:58)
  - rendering/NECK_RULES_ko.md (20:21)
  - turnaround/INDEX.md (19:55)
  - walkdir/WALKDIR_RULES_ko.md (21:01)
  - 사용자 3/4 레퍼런스 walkdir/user_ref/three_quarter_ref.jpg

## 3. 프로필 바스트: 현행본 미확정 (후보 목록)
town-demo, char_v4, portraits_preview, 스토어, thor-docs*, 에이전트 첨부를 이미지로 확인했다. **hero_master_try1(긴 흑발, 검은 코트)과 맞는 일반형 바스트는 찾지 못했다.** 일반형 후보는 모두 구버전 디자인(짧은 머리, 파란 상의)이다.
- 일반형 (전부 구버전, 사용 금지)
  - assets/portraits/hero.png (10-18 15:28): 짧은 머리 남성 픽셀 초상
  - assets/tachie/hero_{neutral,smile,angry,sad,surprised,blush}.png (15:28): 파란 튜닉 + 붉은 망토, 짧은 머리. 다른 워크트리에 사본 있음
  - portraits_preview/expressions_hero.png, dialogue_hero_talking.png, bust_*.png (15:28): 구 디자인 미리보기
  - src/hero/paperdoll_hq/hero_face_ref.png (15:28): 구 paperdoll 계열
- 마왕형
  - 후보: maou_design/illust/maouA_illust_try1.png (15:31). 전신이며 README_A에 "초상용"으로 적혀 있음
  - 구버전: assets/portraits/hero_demon_king.png (15:28). 뿔 달린 픽셀 초상이며 A안 「잠식」 확정 전 디자인
→ try1 기준으로 바스트(일반형/마왕형)를 새로 제작해야 한다. 만들고 나면 02/03에 등록한다.

## 4. 구버전 / 반려 (사용 금지)
- char_v4/work/hero_master_v2.png, hero_master_v3.png (머리 큰 버전, 반려)
- char_v4/work/hero_master_try2_nocape.jpg (망토 없음, 반려)
- assets/portraits/hero.png, assets/portraits/hero_demon_king.png (구 초상)
- assets/tachie/hero_*.png 및 다른 워크트리 사본 (구 디자인 입식)
- portraits_preview/* 주인공 관련 (구 디자인)
- char_v4/hero/* (구 걷기 스프라이트), char_v4/hero_face_compare_v3.png, hero_face_before_after.png
- 스토어 refs/hero_v3/*, style_sample/hero_v3/* (v3 스프라이트 시대)
- char_v4/pixellab/hero/vid/px_*5h* 의 구 폴더 (v5h/base로 대체됨, 단 px_idle5h5_down은 얼굴 마스터로 유지)
- v5h/fx/trail_w1_a10~a35 (구 칼끝 형상 레거시)
- v5h/r2, r3 (r4로 대체됨)
- maou_design/base8_A/src/*.png (비율 틀린 이전 A안), maou_compare_board_PLACEHOLDER.png
- /tmp/pub*, /tmp/t128old, shots_hero8*, tmp/p0_logs/hero8_old (임시/구 빌드)

## 결정 (2026-10-18 22:28 KST, 사장님)
- 미니 캐릭터와 모션은 앞으로 **PixelLab**으로 제작한다. 코드 픽셀 편집(v5h 파이프라인)은 중단하고 참고용으로만 남긴다.
- 기준 캐릭터: PixelLab v3 character fb140a07-3f50-40a1-9a11-ca71de7b3c49 (char_v4/pixellab/hero/v3gen_20261018/v1_1x_descA/, 약 124px, 256 캔버스).
- 고픽셀(v2_2x_hires, 2배 확대본)은 쓰지 않는다.
- 4방향(정면·뒤·오른쪽·왼쪽)을 먼저 만든다.
