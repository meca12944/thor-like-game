# 지울 옛 이야기 문서 목록 (스토리 담당, 2026-10-24) — 목록만, 아직 지우지 않음

> 사장님 확정 「새 1장 짓기 순서」(`docs_maps/CH1_BUILD_PLAN_ko.md`) 2번: 새 1장이 게임에서 돌아가면 **정본과 다른 옛 이야기 문서**를 한 번에 지운다 (git 기록에는 남는다).
> 정본: `MASTER_PLAN_정본_20261024_ko.md`(0절 우선) · `MASTER_PLAN_아이템배치_20261024_ko.md`.

## A. 지울 것 — 옛 정본(아스란·9장·히로인 7명·마을 A) 문서
| 파일 | 무엇 | 왜 지우나 |
|---|---|---|
| `docs_story/novel.md` | 옛 소설판 (베일라·바렌 등, 10지역) | 옛 장 구성·옛 히로인. 새 정본과 다름 |
| `docs_story/novel_parts/part_01~16.txt` | 위 소설을 나눈 조각 16개 | 위와 같음 |
| `docs_story/quest_parts/part_01~02.txt` | 옛 퀘스트 조각 | 옛 장·마을 기준 |
| `docs_story/heroine_mainquests.md` | 옛 히로인 7명 메인퀘스트·보스전 동행 | 히로인 배치가 「여성 핵심 인물 6명」으로 바뀜 |
| `docs_story/heroine_quests.md` / `heroine_quests.json` | 옛 히로인 퀘스트 (시작의 숲 리네트 등) | 리네트 = 폐공방 구출로 바뀜 |
| `docs_story/town_A_npcs.md` / `town_A_npcs.json` | 옛 마을 A 사람들 | 옛 마을(townB·townH)과 함께 사라짐 |
| `docs_story/town_A_events_quests.md` / `.json` | 옛 마을 A 사건·퀘스트 | 위와 같음 |
| `docs_story/chests_A_area1.md` / `.json` | 옛 1지역(숲) 상자 | 옛 숲 들판 field00~09와 함께 사라짐 |
| `docs_story/ult_unlock_event.md` | 옛 필살기 해금 사건 (G 오아시스 등 옛 장) | 옛 장 이름·인물 |
| `docs_story/spirit_removal.md` | 정령 지우기 작업 메모 | 작업 끝, 옛 히로인 기준 |
| `docs_story/names_world.md` | 옛 지역·기술 이름표 | 옛 장 지명. 새 정본 지명과 다름 |

## B. 확인 뒤 지우거나 고칠 것 (사장님·담당 결정 필요)
| 파일 | 상태 | 제안 |
|---|---|---|
| `docs_story/ABYSS_POWER_AND_VAULT_ko.md` | 10-23 확정 「심연의 힘·금고」 (장비 마모 없음, 금고 = 펠트 예배당) | 새 정본은 [공허의 마모]·배수진, 수장고 = 5장 대성당. **심연의 힘을 배수진에 합칠지** 2번방(UI)·사장님 결정 뒤 지움 |
| `docs_story/names_eldenring.md` | 엘든링식 이름 짓기 참고 | 이름 짓는 법만 남기고 옛 지명 예시는 지움 (참고용이라 남겨도 됨) |
| `docs_story/MASTER_PLAN_CH1_DIFF_ko.md` | 지금 게임 ↔ 새 정본 차이표 | 새 1장이 다 지어지면 할 일이 끝나므로 지움 |
| `handoff/claude/CH1_MASTER_PLAN_MIGRATION_ko.md` | 옛 1장을 고쳐 옮기는 계획 | 새 1장을 처음부터 짓기로 바뀌어 쓸모 없음 → 지움 |
| `handoff/HANDOFF_필멸자_20261019.md` | 10-19 인수인계 (옛 정본) | 지움 (git 기록으로 충분) |
| `HERO_SKILLS.md` | 옛 장·보스 기준 기술표 (맨 위에 안내 1줄 달아 둠) | 2번방이 새 무기 15종 기준으로 다시 쓰면 지움 |
| `art/mobs/CHAPTER_MAP_ko.md` | 옛 장·보스 몹 지도 | 마물 다시 기획 뒤 몬스터 담당이 새로 씀 → 지움 |
| `docs_art/felt_review/STORY_ANSWERS_ko.md`, `docs_art/felt_review/REPORT_ko.md` | 옛 펠트 검토 (30년 전 화재, 마을 첫 만남) | 새 1장이 다 지어지면 지움 |
| `handoff/claude/felt_grok_layout/README_ko.md`, `handoff/claude/felt_hd/REPORT_ko.md` | 옛 펠트(59×35) 짓기 기록 | 새 1장이 다 지어지면 지움 |

## C. 게임 안 옛 이야기 데이터 (코드 쪽 — 지울 때 같이 보도록 적어 둠, 지우는 건 팀장)
| 파일 | 무엇 |
|---|---|
| `test128/maps/field00.json`, `field02~09.json` | 옛 숲 들판 (안의 표지판·상자 글) |
| `test128/maps/townB.json`, `townH.json` | 옛 마을 (사람·대사) |
| `test128/maps/boss01.json`, `dungeon01_b1.json` | 옛 보스·던전 |
| `test128/maps/quests.json` 의 `q_forest_chiefs`, `q_temple_golem` | 옛 숲·신전 퀘스트 |
| `test128/maps/quests.json` 의 `q_felt_*`, `test128/maps/dialog_ch1.json` | 옛 1장 대사·퀘스트 → 새 1장 대사(`docs_story/CH1_NEW_DIALOGUE_ko.md`)로 바꿈 |

## D. 남길 것 (새 정본)
`MASTER_PLAN_정본_20261024_ko.md` · `MASTER_PLAN_아이템배치_20261024_ko.md` · `CHARACTERS_정본_ko.md` · `main_story.md` · `story_full.md` · `README.md` · `CH1_NEW_DIALOGUE_ko.md` · `handoff/GROK_BRIEFING_ko.md` · `docs_maps/` 전부.
