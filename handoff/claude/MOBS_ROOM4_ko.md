
## 10-22 전 몹 + 리네트 인게임 배치 (크레딧 0)
- 3번방 대기/공격 스트립 47종 → test128/assets/mobs47 (tools/anim/mobs47/import.py, 왼쪽 보는 그림은 좌우 반전).
- 1지역 기존 8종(독버섯·뿔토끼·말벌·멧돼지·허수아비·슬라임·다람쥐·새싹): AI 그대로, 그림만 새 스트립(키 x1.3).
- 2~9지역 39종: 공통 AI(world_mobs.js s47) — 근접/사격/돌진/주변 장판/발밑 낙하, 전부 예고 후 공격. 지역별 들판 field02~09 새로 만듦(tools/gen_region_fields.py), 월드맵 2~9지역 열림.
- 리네트: 바람길(field00)에서 주인공 따라다니며 근처 몹 찌르기(world.js stepPet/drawPetHi).
- 테스트: test128/tools/test_place_all.py (에러 0).
