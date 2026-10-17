# 그림 생성 명세 (모두 오리지널; 기존 게임/ROM 그림 사용 금지)

공통 스타일: soft hand-painted illustrated mobile RPG art, 3/4 top-down view, warm lighting, gentle outlines, cute chibi proportions (head ~1/3 of body).
기준 그림: 사용자가 승인한 컨셉 이미지를 reference 로 사용.

- 스프라이트(캐릭터·적·소품):
  - "full body, single character, centered, plain flat solid #00FF00 background, no shadow on ground, no text"
  - 1:1 비율로 요청합니다.
  - 그 다음 `tools/asset_pipeline.py sprite` 로 배경을 지웁니다(초록 의상이 있는 망토 주인공은 #FF00FF 배경 사용).
- 방 배경:
  - `assets_src/guides/<방>_layout.png` 을 reference 로 넣고 "same layout, walls/water/houses exactly where the reference has them, no characters, no chests, no text" 로 요청합니다.
  - 4:3 비율로 요청한 뒤 `bg` 명령으로 처리합니다.

| 파일 | 내용 | 프레임 | 처리 높이 |
|---|---|---|---|
| hero_{d,u,r}_idle | 갈색 머리 소년 영웅, 초록 망토, 한손검; d=정면, u=뒷모습, r=오른쪽 옆모습 | 2 (숨쉬기) | 144 |
| hero_{d,u,r}_walk | 걷기 사이클 | 4 | 144 |
| hero_{d,u,r}_atk | 칼 휘두르기(예비동작→베기→끝) | 3 | 144 |
| hero_{d,u,r}_jump / _hurt | 점프 / 맞고 움찔 | 1 | 144 |
| enemy_slime | 귀여운 젤리 슬라임 | 2 | 80 |
| enemy_bat | 동굴 박쥐(날개 위/아래) | 2 | 80 |
| enemy_wisp | 보랏빛 도깨비불 | 2 | 88 |
| enemy_skel | 해골 병사(창) | 2 | 128 |
| enemy_knight | 검은 갑옷 기사 | 2 | 144 |
| enemy_mage | 모래 로브 마법사 | 2 | 136 |
| enemy_snapper | 식인초 | 2 | 112 |
| boss_golem | 이끼 덮인 돌 골렘(거대) | 2 | 240 |
| boss_wyvern | 밤하늘색 와이번(날개 펼침) | 2 | 232 |
| boss_priest | 흑요석 지팡이를 든 후드 사제 | 2 | 216 |
| spirit_water/fire/shadow/plant | 물(파랑, 컨셉의 빛나는 정령)/불/그림자/풀 정령, 빛나는 반투명 | 1 | 96 |
| npc_elder, npc_smith, npc_inn, npc_girl, npc_boy, npc_merchant, npc_inn2, npc_sailor, npc_villager | 촌장(흰 수염), 대장장이, 여관 주인, 소녀, 꼬마, 무기상, 항구 여관 주인, 늙은 선원, 일반 주민 | 1 | 136 |
| prop_tree, prop_rock, prop_block, prop_chest, prop_chest_open, prop_torch, prop_altar | 둥근 활엽수, 바위, 밀 수 있는 돌 블록, 보물상자(닫힘/열림), 횃불 받침, 정령 제단 | 1 | 224/72/88/68/68/96/104 |
| bg_town1, bg_town2 | 돌길 마을, 청기와 목조 집, 꽃밭 / 모래 항구 마을 | - | 1280x960 |
| bg_plain, bg_canyon | 은빛 평원 / 붉은 협곡 | - | 1280x960 |
| bg_d1a, bg_d1b | 이끼 동굴 / 골렘의 굴 | - | 1280x960 |
| bg_d2a, bg_d2b, bg_d2c | 그림자 탑 1층, 2층, 옥상 | - | 1280x960 |
| bg_d3a, bg_d3b | 뿌리 신전 / 흑요의 제단 | - | 1280x960 |
| title | 타이틀 일러스트(섬, 노을, 정령들) — 위쪽 1/3은 로고 자리로 비움 | - | 1280x960 |
