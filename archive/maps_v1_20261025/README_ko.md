# 옛 마을·던전 보관본 (2026-10-25)

사장님 지시 (2026-10-25 00:32·00:39 KST): 새 정본(`docs_story/MASTER_PLAN_정본_20261024_ko.md`)에 맞춰 마을·던전을 새로 시작한다.
지금까지 만든 마을·던전은 여기 **복사본**으로 보관한다. `test128/`은 그대로 두고 라이브 테스트 빌드도 바뀌지 않는다.

- `test128/maps/` : 펠트·실내·들판·던전·아라크네·보스 맵 JSON 전부 (src 포함)
- `test128/assets/world/` : 맵 배경·타일·실내 그림
- `test128/assets/mobs_felt/` : 펠트 들판 몹
- `test128/tools/hd/` : 맵 빌드 스크립트
- `felt_props/`, `felt_review/`, `town_layout/` : 그록 프롭·검토 문서·마을 배치 그림
- 펠트 개선 작업(1~3단계)은 브랜치 `claude/felt-upgrade`(3236d758)에 그대로 남아 있다. main에 넣지 않는다.

새 맵은 저장소 루트 `maps_v2/`에서 시작한다.
