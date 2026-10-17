# 아이템 아이콘 (art/icons)

인벤토리 · 장비 · 상점 · 대장간 창에서 아이템을 **아이콘**으로 표시하기 위한 아틀라스입니다.

- `icons32.png` — 32×32 (가방 칸 · 목록), `icons64.png` — 64×64 (툴팁). 16열 그리드, 두 장의 배치는 같음.
- `icons.json` — `icons[id] = {i, r32:[x,y,w,h], r64:[x,y,w,h], name, kind, rarity, src, variant?}`.
- `sheets/` — 원본 생성 시트 (자홍 배경, 글자 없음). `cons_1~3.jpg` 소모품 60, `mat_1~7.jpg` 재료 기본 아이콘.
- `preview_icons64.png` — 전체 아이콘 미리보기.
- 빌드: 데모 폴더에서 `python3 tools/icons.py` (장비 시트 `src/items/*`, 생성 시트 `src/icons/*`, `data/towns.json`, `ITEMS.md` 사용). 프롬프트 · 순서는 `tools/icon_prompts.py`.

## 개수

| 분류 | 개수 | 출처 |
|---|---|---|
| 무기 | 30 | art/items weapons_1~3 (5×2, ITEMS.md 순서) |
| 방어구 | 30 | armor_1~3 |
| 보조무기 | 30 | offhand_1~3 |
| 숨겨진 전설검 | 3 | hidden_swords.jpg (탁검 · 규검), chan_sword.jpg (찬검) — 어두운 배경 키잉, 45° 회전 |
| 소모품 | 60 | sheets/cons_1~3 (카탈로그 순서) |
| 재료 | 172 | sheets/mat_1~7 — 고유 135 (완성 두루마리 포함) + 파생 37 |
| UI | 3 | 금화 · 가방 · 대장간 (mat_7 #18~20) |
| **합계** | **328** | 아이템 325 + UI 3 |

## 재료 아이콘 방식

- 재료 172종 중 **135종은 각자 고유 아이콘** (mat_1~7 생성 시트, 134 + 완성 두루마리).
- **타락 재료 27종(`x_*`)**: 원본 재료 아이콘을 회색조로 바꾼 뒤 보라 램프(#7a2ad0 계열)로 75% 물들이고 짙은 보라 오라를 둘렀습니다 (`corrupt()`).
- **지역 레시피 두루마리 조각 10종(`scroll_area1~10`)**: 같은 두루마리 조각 아이콘(mat_1 #20)의 빨간 봉랍을 티어 색으로 바꿈 (`reseal()`).
- `scroll_first_bearer` 는 완성 두루마리 아이콘(mat_7 #16), `tk_mago` 는 mat_7 #17 (mat_6 #8 은 메달이 아닌 모자만 그려져 버림).

| 봉랍 색 (티어 1→10) | `#c8302a` `#e07a20` `#d8b020` `#5aa83a` `#2a9ad0` `#3a5ad8` `#8a4ad8` `#d04aa0` `#e8e8f0` `#202028` |
|---|---|

## 등급 테두리 색

| 등급 | 색 | 기준 |
|---|---|---|
| 일반 | `#9aa0a8` | 티어 1~2 |
| 고급 | `#5ac85a` | 티어 3~4 (보스 · 챔피언 · 퀘스트 · 잠수 장비는 한 단계 위) |
| 희귀 | `#3a8ef0` | 티어 5~6 |
| 영웅 | `#b050f0` | 티어 7~8 |
| 전설 | `#ffb020` | 티어 9~10 |
| 유일 | `#ff5a3a` | 숨겨진 전설검 3종 |
| 타락 | `#8a2ae0` | `x_*` 타락 재료 |

## 파생 아이콘 목록

| id | 파생 방식 |
|---|---|
| `x_m_a1_shared` | m_a1_shared + 타락 보라 틴트·오라 |
| `x_m_a2_shared` | m_a2_shared + 타락 보라 틴트·오라 |
| `x_m_a3_shared` | m_a3_shared + 타락 보라 틴트·오라 |
| `x_m_a4_shared` | m_a4_shared + 타락 보라 틴트·오라 |
| `x_m_a5_shared` | m_a5_shared + 타락 보라 틴트·오라 |
| `x_m_a6_shared` | m_a6_shared + 타락 보라 틴트·오라 |
| `x_m_a7_shared` | m_a7_shared + 타락 보라 틴트·오라 |
| `x_m_a8_shared` | m_a8_shared + 타락 보라 틴트·오라 |
| `x_m_a9_shared` | m_a9_shared + 타락 보라 틴트·오라 |
| `x_m_c_tusk` | m_c_tusk + 타락 보라 틴트·오라 |
| `x_m_c_queen_gland` | m_c_queen_gland + 타락 보라 틴트·오라 |
| `x_m_c_blood_wing` | m_c_blood_wing + 타락 보라 틴트·오라 |
| `x_m_c_fuse` | m_c_fuse + 타락 보라 틴트·오라 |
| `x_m_c_sun_tail` | m_c_sun_tail + 타락 보라 틴트·오라 |
| `x_m_c_silk_cape` | m_c_silk_cape + 타락 보라 틴트·오라 |
| `x_m_c_twin_mask` | m_c_twin_mask + 타락 보라 틴트·오라 |
| `x_m_c_curse_staff` | m_c_curse_staff + 타락 보라 틴트·오라 |
| `x_m_c_shark_fin` | m_c_shark_fin + 타락 보라 틴트·오라 |
| `x_m_c_abyss_lamp` | m_c_abyss_lamp + 타락 보라 틴트·오라 |
| `x_m_c_cursed_coin` | m_c_cursed_coin + 타락 보라 틴트·오라 |
| `x_m_c_great_claw` | m_c_great_claw + 타락 보라 틴트·오라 |
| `x_m_c_giant_heart` | m_c_giant_heart + 타락 보라 틴트·오라 |
| `x_m_c_flame_hair` | m_c_flame_hair + 타락 보라 틴트·오라 |
| `x_m_c_silver_fur` | m_c_silver_fur + 타락 보라 틴트·오라 |
| `x_m_c_thunder_plume` | m_c_thunder_plume + 타락 보라 틴트·오라 |
| `x_m_c_shadow_edge` | m_c_shadow_edge + 타락 보라 틴트·오라 |
| `x_m_c_gravity_core` | m_c_gravity_core + 타락 보라 틴트·오라 |
| `scroll_area1` | scroll_area + 봉랍 색 #c8302a (티어 1) |
| `scroll_area2` | scroll_area + 봉랍 색 #e07a20 (티어 2) |
| `scroll_area3` | scroll_area + 봉랍 색 #d8b020 (티어 3) |
| `scroll_area4` | scroll_area + 봉랍 색 #5aa83a (티어 4) |
| `scroll_area5` | scroll_area + 봉랍 색 #2a9ad0 (티어 5) |
| `scroll_area6` | scroll_area + 봉랍 색 #3a5ad8 (티어 6) |
| `scroll_area7` | scroll_area + 봉랍 색 #8a4ad8 (티어 7) |
| `scroll_area8` | scroll_area + 봉랍 색 #d04aa0 (티어 8) |
| `scroll_area9` | scroll_area + 봉랍 색 #e8e8f0 (티어 9) |
| `scroll_area10` | scroll_area + 봉랍 색 #202028 (티어 10) |

## 전체 매핑

| # | id | 이름 | 분류 | 등급 | 원본 |
|---|---|---|---|---|---|
| 0 | `w_bronze_long` | 청동 장검 | 무기 | common | src/items/weapons_1.jpg#0 |
| 1 | `w_iron_trainee` | 견습 철검 | 무기 | common | src/items/weapons_1.jpg#1 |
| 2 | `w_boar_tusk` | 돌엄니 송곳검 | 무기 | uncommon | src/items/weapons_1.jpg#2 |
| 3 | `w_forest_dagger` | 숲의 단검 | 무기 | uncommon | src/items/weapons_1.jpg#3 |
| 4 | `w_crystal_edge` | 수정날 검 | 무기 | common | src/items/weapons_1.jpg#4 |
| 5 | `w_hunter_machete` | 사냥꾼 마체테 | 무기 | common | src/items/weapons_1.jpg#5 |
| 6 | `w_mill_steel` | 물레 강철검 | 무기 | common | src/items/weapons_1.jpg#6 |
| 7 | `w_miner_broad` | 광부의 두꺼운 검 | 무기 | common | src/items/weapons_1.jpg#7 |
| 8 | `w_reed_leaf` | 갈대잎 검 | 무기 | common | src/items/weapons_1.jpg#8 |
| 9 | `w_spider_fang` | 여왕거미 독니검 | 무기 | uncommon | src/items/weapons_1.jpg#9 |
| 10 | `w_desert_crescent` | 사막 초승달검 | 무기 | uncommon | src/items/weapons_2.jpg#0 |
| 11 | `w_sun_sting` | 태양침 독검 | 무기 | rare | src/items/weapons_2.jpg#1 |
| 12 | `w_sun_sigil` | 태양 문양 검 | 무기 | uncommon | src/items/weapons_2.jpg#2 |
| 13 | `w_pharaoh_scepter` | 황금가면 왕홀검 | 무기 | rare | src/items/weapons_2.jpg#3 |
| 14 | `w_harpoon_blade` | 작살검 | 무기 | rare | src/items/weapons_2.jpg#4 |
| 15 | `w_wave_blade` | 파도 검 | 무기 | rare | src/items/weapons_2.jpg#5 |
| 16 | `w_kraken_whip` | 크라켄 촉수검 | 무기 | epic | src/items/weapons_2.jpg#6 |
| 17 | `w_anchor_great` | 닻 대검 | 무기 | rare | src/items/weapons_2.jpg#7 |
| 18 | `w_captain_cutlass` | 해적 선장의 커틀러스 | 무기 | epic | src/items/weapons_2.jpg#8 |
| 19 | `w_forge_great` | 용광로 대검 | 무기 | epic | src/items/weapons_2.jpg#9 |
| 20 | `w_obsidian` | 흑요석 검 | 무기 | epic | src/items/weapons_3.jpg#0 |
| 21 | `w_hellfire` | 업화의 흑검 | 무기 | epic | src/items/weapons_3.jpg#1 |
| 22 | `w_frost_crystal` | 서리 결정검 | 무기 | epic | src/items/weapons_3.jpg#2 |
| 23 | `w_northwind` | 북풍 장검 | 무기 | epic | src/items/weapons_3.jpg#3 |
| 24 | `w_storm_spear` | 뇌전 창검 | 무기 | epic | src/items/weapons_3.jpg#4 |
| 25 | `w_mithril` | 미스릴 장검 | 무기 | legendary | src/items/weapons_3.jpg#5 |
| 26 | `w_royal_knight` | 왕실 기사검 | 무기 | legendary | src/items/weapons_3.jpg#6 |
| 27 | `w_first_bearer` | 선대의 부러진 검 | 무기 | legendary | src/items/weapons_3.jpg#7 |
| 28 | `w_shadow_twin` | 그림자 쌍검 | 무기 | legendary | src/items/weapons_3.jpg#8 |
| 29 | `w_dragon_tri` | 삼두 마룡검 | 무기 | legendary | src/items/weapons_3.jpg#9 |
| 30 | `b_cloth_tunic` | 천 튜닉 | 방어구 | common | src/items/armor_1.jpg#0 |
| 31 | `b_traveler` | 여행자 외투 | 방어구 | common | src/items/armor_1.jpg#1 |
| 32 | `h_leather_hood` | 가죽 두건 | 방어구 | common | src/items/armor_1.jpg#2 |
| 33 | `b_moss_crystal` | 이끼 수정 흉갑 | 방어구 | uncommon | src/items/armor_1.jpg#3 |
| 34 | `b_miner_vest` | 광부 가죽 조끼 | 방어구 | common | src/items/armor_1.jpg#4 |
| 35 | `b_quilted` | 누빔 갑옷 | 방어구 | common | src/items/armor_1.jpg#5 |
| 36 | `h_iron_mask` | 용병 쇠가면 | 방어구 | common | src/items/armor_1.jpg#6 |
| 37 | `h_miner_helmet` | 광부 헬멧 | 방어구 | common | src/items/armor_1.jpg#7 |
| 38 | `h_steel_circlet` | 강철 머리띠 | 방어구 | common | src/items/armor_1.jpg#8 |
| 39 | `b_desert_silk` | 사막 비단 경갑 | 방어구 | uncommon | src/items/armor_1.jpg#9 |
| 40 | `h_turban` | 루비 터번 | 방어구 | uncommon | src/items/armor_2.jpg#0 |
| 41 | `h_desert_turban` | 사막의 터번 | 방어구 | rare | src/items/armor_2.jpg#1 |
| 42 | `h_pharaoh_mask` | 황금 가면 | 방어구 | rare | src/items/armor_2.jpg#2 |
| 43 | `b_bosun_coat` | 갑판장 코트 | 방어구 | rare | src/items/armor_2.jpg#3 |
| 44 | `b_scale_mail` | 비늘 사슬갑옷 | 방어구 | rare | src/items/armor_2.jpg#4 |
| 45 | `h_nautilus` | 앵무조개 투구 | 방어구 | rare | src/items/armor_2.jpg#5 |
| 46 | `b_crab_shell` | 거대게 껍질 갑옷 | 방어구 | epic | src/items/armor_2.jpg#6 |
| 47 | `b_ghost_coat` | 유령 선장의 코트 | 방어구 | epic | src/items/armor_2.jpg#7 |
| 48 | `b_black_plate` | 흑철 판금 흉갑 | 방어구 | epic | src/items/armor_2.jpg#8 |
| 49 | `h_horned` | 뿔 달린 흑철 투구 | 방어구 | epic | src/items/armor_2.jpg#9 |
| 50 | `h_witch_hat` | 화염 마녀의 모자 | 방어구 | epic | src/items/armor_3.jpg#0 |
| 51 | `b_snow_fur` | 설원 털가죽 갑옷 | 방어구 | epic | src/items/armor_3.jpg#1 |
| 52 | `h_fur_helm` | 털모자 투구 | 방어구 | epic | src/items/armor_3.jpg#2 |
| 53 | `b_wyvern_scale` | 뇌전 비늘 갑옷 | 방어구 | epic | src/items/armor_3.jpg#3 |
| 54 | `h_griffon_helm` | 그리폰 깃털 투구 | 방어구 | epic | src/items/armor_3.jpg#4 |
| 55 | `b_mithril_plate` | 미스릴 판금 | 방어구 | legendary | src/items/armor_3.jpg#5 |
| 56 | `h_knight_plume` | 깃털 기사 투구 | 방어구 | legendary | src/items/armor_3.jpg#6 |
| 57 | `b_shadow_garb` | 그림자 잠행복 | 방어구 | legendary | src/items/armor_3.jpg#7 |
| 58 | `h_void_crown` | 공허의 관 | 방어구 | legendary | src/items/armor_3.jpg#8 |
| 59 | `b_dragon_scale` | 마룡 비늘 갑옷 | 방어구 | legendary | src/items/armor_3.jpg#9 |
| 60 | `a_wood_round` | 나무 원형방패 | 보조무기 | common | src/items/offhand_1.jpg#0 |
| 61 | `o_sling` | 투석끈 | 보조무기 | common | src/items/offhand_1.jpg#1 |
| 62 | `o_moss_shield` | 이끼 수정 방패 | 보조무기 | uncommon | src/items/offhand_1.jpg#2 |
| 63 | `o_wasp_dart` | 여왕벌 독침 다트 | 보조무기 | uncommon | src/items/offhand_1.jpg#3 |
| 64 | `a_leather_bracer` | 가죽 팔보호대 | 보조무기 | common | src/items/offhand_1.jpg#4 |
| 65 | `a_ore_amulet` | 광석 부적 | 보조무기 | common | src/items/offhand_1.jpg#5 |
| 66 | `o_ore_pick` | 투척 곡괭이 | 보조무기 | common | src/items/offhand_1.jpg#6 |
| 67 | `o_throw_knife` | 투척 단검 묶음 | 보조무기 | common | src/items/offhand_1.jpg#7 |
| 68 | `o_bat_ring` | 흡혈 박쥐왕의 반지 | 보조무기 | uncommon | src/items/offhand_1.jpg#8 |
| 69 | `o_chakram` | 사막 차크람 | 보조무기 | uncommon | src/items/offhand_1.jpg#9 |
| 70 | `o_worm_fang` | 대지렁이 이빨 부메랑 | 보조무기 | rare | src/items/offhand_2.jpg#0 |
| 71 | `a_dune_boots` | 사막 질주 장화 | 보조무기 | uncommon | src/items/offhand_2.jpg#1 |
| 72 | `o_golden_scarab` | 황금 풍뎅이 부적 | 보조무기 | rare | src/items/offhand_2.jpg#2 |
| 73 | `a_coral_buckler` | 산호 버클러 | 보조무기 | rare | src/items/offhand_2.jpg#3 |
| 74 | `o_shell_orb` | 조개 오브 | 보조무기 | rare | src/items/offhand_2.jpg#4 |
| 75 | `o_shark_fin` | 백상어 지느러미 방패 | 보조무기 | epic | src/items/offhand_2.jpg#5 |
| 76 | `o_crab_claw` | 거대게 집게 방패 | 보조무기 | epic | src/items/offhand_2.jpg#6 |
| 77 | `a_flame_bracer` | 화염 팔찌 | 보조무기 | epic | src/items/offhand_2.jpg#7 |
| 78 | `o_ember_orb` | 불씨 오브 | 보조무기 | epic | src/items/offhand_2.jpg#8 |
| 79 | `o_forge_tower` | 흑철 대방패 | 보조무기 | epic | src/items/offhand_2.jpg#9 |
| 80 | `o_lava_core` | 용암 거인의 핵 | 보조무기 | epic | src/items/offhand_3.jpg#0 |
| 81 | `a_frost_amulet` | 서리 부적 | 보조무기 | epic | src/items/offhand_3.jpg#1 |
| 82 | `o_ice_javelin` | 얼음 투창 | 보조무기 | epic | src/items/offhand_3.jpg#2 |
| 83 | `o_yeti_bracer` | 설인 털 팔보호대 | 보조무기 | epic | src/items/offhand_3.jpg#3 |
| 84 | `a_royal_kite` | 왕실 문장 방패 | 보조무기 | legendary | src/items/offhand_3.jpg#4 |
| 85 | `o_holy_orb` | 성광 오브 | 보조무기 | legendary | src/items/offhand_3.jpg#5 |
| 86 | `o_knight_gauntlet` | 기사 건틀릿 | 보조무기 | legendary | src/items/offhand_3.jpg#6 |
| 87 | `o_shadow_kunai` | 그림자 표창 | 보조무기 | legendary | src/items/offhand_3.jpg#7 |
| 88 | `o_void_ring` | 공허의 반지 | 보조무기 | legendary | src/items/offhand_3.jpg#8 |
| 89 | `o_dragon_eye` | 마룡의 눈 | 보조무기 | legendary | src/items/offhand_3.jpg#9 |
| 90 | `hs_tak` | 탁검 | 숨겨진 전설검 | unique | src/items/hidden_swords.jpg |
| 91 | `hs_gyu` | 규검 | 숨겨진 전설검 | unique | src/items/hidden_swords.jpg |
| 92 | `hs_chan` | 찬검 | 숨겨진 전설검 | unique | src/items/chan_sword.jpg |
| 93 | `herb_red` | 빨간 약초 | 소모품 | common | src/icons/cons_1.jpg#0 |
| 94 | `potion` | 회복약 | 소모품 | common | src/icons/cons_1.jpg#1 |
| 95 | `potion_m` | 중급 회복약 | 소모품 | common | src/icons/cons_1.jpg#2 |
| 96 | `riceball` | 광부 주먹밥 | 소모품 | common | src/icons/cons_1.jpg#3 |
| 97 | `potion_regen` | 재생의 물약 | 소모품 | common | src/icons/cons_1.jpg#4 |
| 98 | `potion_hi` | 고급 회복약 | 소모품 | common | src/icons/cons_1.jpg#5 |
| 99 | `elixir` | 생명의 영약 | 소모품 | common | src/icons/cons_1.jpg#6 |
| 100 | `spirit` | 정령수 | 소모품 | common | src/icons/cons_1.jpg#7 |
| 101 | `spirit_tea` | 정령 찻잎 | 소모품 | common | src/icons/cons_1.jpg#8 |
| 102 | `spirit_hi` | 상급 정령수 | 소모품 | common | src/icons/cons_1.jpg#9 |
| 103 | `panacea_full` | 만능 영약 | 소모품 | common | src/icons/cons_1.jpg#10 |
| 104 | `antidote` | 해독초 | 소모품 | common | src/icons/cons_1.jpg#11 |
| 105 | `quick_powder` | 날쌘 가루 | 소모품 | common | src/icons/cons_1.jpg#12 |
| 106 | `water_skin` | 물주머니 | 소모품 | common | src/icons/cons_1.jpg#13 |
| 107 | `holy_water` | 정화의 성수 | 소모품 | common | src/icons/cons_1.jpg#14 |
| 108 | `clear_eye` | 맑은 눈약 | 소모품 | common | src/icons/cons_1.jpg#15 |
| 109 | `burn_salve` | 화상 연고 | 소모품 | common | src/icons/cons_1.jpg#16 |
| 110 | `thaw` | 해빙 연고 | 소모품 | common | src/icons/cons_1.jpg#17 |
| 111 | `insulate` | 절연 송진 | 소모품 | common | src/icons/cons_1.jpg#18 |
| 112 | `cure_all` | 만병통치약 | 소모품 | common | src/icons/cons_1.jpg#19 |
| 113 | `atk_s` | 힘의 열매 | 소모품 | common | src/icons/cons_2.jpg#0 |
| 114 | `atk_l` | 분노의 물약 | 소모품 | common | src/icons/cons_2.jpg#1 |
| 115 | `def_s` | 단단 껍질차 | 소모품 | common | src/icons/cons_2.jpg#2 |
| 116 | `def_l` | 철벽의 물약 | 소모품 | common | src/icons/cons_2.jpg#3 |
| 117 | `spd_s` | 바람 사탕 | 소모품 | common | src/icons/cons_2.jpg#4 |
| 118 | `spd_l` | 질풍의 물약 | 소모품 | common | src/icons/cons_2.jpg#5 |
| 119 | `crit_s` | 매의 눈 향초 | 소모품 | common | src/icons/cons_2.jpg#6 |
| 120 | `crit_l` | 사냥꾼의 집중약 | 소모품 | common | src/icons/cons_2.jpg#7 |
| 121 | `berserk` | 광전사의 피 | 소모품 | common | src/icons/cons_2.jpg#8 |
| 122 | `pearl` | 생명의 진주 | 소모품 | rare | src/icons/cons_2.jpg#9 |
| 123 | `heart_piece` | 하트 조각 | 소모품 | rare | src/icons/cons_2.jpg#10 |
| 124 | `spirit_drop` | 정령의 물방울 | 소모품 | rare | src/icons/cons_2.jpg#11 |
| 125 | `giant_fruit` | 거인의 열매 | 소모품 | rare | src/icons/cons_2.jpg#12 |
| 126 | `turtle_fruit` | 거북 등껍질 열매 | 소모품 | rare | src/icons/cons_2.jpg#13 |
| 127 | `dragon_heart` | 용의 심장 조각 | 소모품 | rare | src/icons/cons_2.jpg#14 |
| 128 | `wind_plume` | 바람새 깃털 | 소모품 | rare | src/icons/cons_2.jpg#15 |
| 129 | `feather` | 귀환의 깃털 | 소모품 | common | src/icons/cons_2.jpg#16 |
| 130 | `smoke` | 연막 구슬 | 소모품 | common | src/icons/cons_2.jpg#17 |
| 131 | `escape_rope` | 탈출 밧줄 | 소모품 | common | src/icons/cons_2.jpg#18 |
| 132 | `warp_stone` | 이동의 돌 | 소모품 | common | src/icons/cons_2.jpg#19 |
| 133 | `gate_bell` | 문지기의 종 | 소모품 | common | src/icons/cons_3.jpg#0 |
| 134 | `invis_dust` | 투명 가루 | 소모품 | common | src/icons/cons_3.jpg#1 |
| 135 | `goggles_oil` | 잠수 기름 | 소모품 | common | src/icons/cons_3.jpg#2 |
| 136 | `air_bubble` | 공기 방울 병 | 소모품 | common | src/icons/cons_3.jpg#3 |
| 137 | `swim_fin` | 물갈퀴 기름 | 소모품 | common | src/icons/cons_3.jpg#4 |
| 138 | `deep_lamp` | 심해 등불 | 소모품 | common | src/icons/cons_3.jpg#5 |
| 139 | `mermaid_scale` | 인어 비늘 | 소모품 | common | src/icons/cons_3.jpg#6 |
| 140 | `torch` | 횃불 | 소모품 | common | src/icons/cons_3.jpg#7 |
| 141 | `bomb` | 작은 폭탄 | 소모품 | common | src/icons/cons_3.jpg#8 |
| 142 | `big_bomb` | 큰 폭탄 | 소모품 | common | src/icons/cons_3.jpg#9 |
| 143 | `lure` | 미끼 고기 | 소모품 | common | src/icons/cons_3.jpg#10 |
| 144 | `map_scroll` | 탐험 지도 | 소모품 | common | src/icons/cons_3.jpg#11 |
| 145 | `skeleton_key` | 만능 열쇠 | 소모품 | common | src/icons/cons_3.jpg#12 |
| 146 | `coin_charm` | 황금 동전 | 소모품 | common | src/icons/cons_3.jpg#13 |
| 147 | `charm_guard` | 수호의 부적 | 소모품 | common | src/icons/cons_3.jpg#14 |
| 148 | `charm_luck` | 행운의 숫돌 | 소모품 | common | src/icons/cons_3.jpg#15 |
| 149 | `pardon` | 면죄 증서 | 소모품 | common | src/icons/cons_3.jpg#16 |
| 150 | `candle` | 참회의 촛불 | 소모품 | common | src/icons/cons_3.jpg#17 |
| 151 | `poison_vial` | 맹독 병 | 소모품 | common | src/icons/cons_3.jpg#18 |
| 152 | `blood_tonic` | 검은 피의 비약 | 소모품 | common | src/icons/cons_3.jpg#19 |
| 153 | `m_iron_ingot` | 철 주괴 | 재료 | common | src/icons/mat_6.jpg#12 |
| 154 | `m_leather_strap` | 질긴 가죽끈 | 재료 | common | src/icons/mat_5.jpg#2 |
| 155 | `m_hardwood` | 단단한 목재 | 재료 | common | src/icons/mat_1.jpg#10 |
| 156 | `m_steel_ingot` | 강철 주괴 | 재료 | uncommon | src/icons/mat_6.jpg#15 |
| 157 | `m_magic_thread` | 마력 실 | 재료 | uncommon | src/icons/mat_2.jpg#7 |
| 158 | `m_blacksteel_ingot` | 흑철 주괴 | 재료 | rare | src/icons/mat_7.jpg#2 |
| 159 | `m_mithril_ingot` | 미스릴 주괴 | 재료 | legendary | src/icons/mat_7.jpg#11 |
| 160 | `m_a1_shared` | 초록 정기 조각 | 재료 | common | src/icons/mat_4.jpg#5 |
| 161 | `m_spore` | 독버섯 포자 | 재료 | common | src/icons/mat_4.jpg#6 |
| 162 | `m_rabbit_horn` | 뿔토끼 뿔 | 재료 | common | src/icons/mat_1.jpg#0 |
| 163 | `m_wasp_sting` | 말벌 독침 | 재료 | common | src/icons/mat_1.jpg#1 |
| 164 | `m_boar_hide` | 멧돼지 가죽 | 재료 | common | src/icons/mat_5.jpg#3 |
| 165 | `m_pumpkin_vine` | 호박 덩굴 | 재료 | common | src/icons/mat_2.jpg#0 |
| 166 | `m_forest_gel` | 숲 슬라임 젤 | 재료 | common | src/icons/mat_4.jpg#7 |
| 167 | `m_acorn_shell` | 단단한 도토리 껍질 | 재료 | common | src/icons/mat_1.jpg#11 |
| 168 | `m_sprout_wood` | 정령 새싹 가지 | 재료 | common | src/icons/mat_1.jpg#12 |
| 169 | `m_a2_shared` | 동굴 수정 파편 | 재료 | common | src/icons/mat_3.jpg#15 |
| 170 | `m_thorn_vine` | 가시덩굴 줄기 | 재료 | common | src/icons/mat_1.jpg#14 |
| 171 | `m_bat_wing` | 박쥐 날개 | 재료 | common | src/icons/mat_5.jpg#4 |
| 172 | `m_beetle_shell` | 수정 딱정벌레 껍질 | 재료 | common | src/icons/mat_5.jpg#13 |
| 173 | `m_spider_silk` | 거미 명주실 | 재료 | common | src/icons/mat_2.jpg#3 |
| 174 | `m_goblin_pick` | 도깨비 곡괭이 날 | 재료 | common | src/icons/mat_6.jpg#14 |
| 175 | `m_glow_gland` | 반딧불 발광샘 | 재료 | common | src/icons/mat_4.jpg#9 |
| 176 | `m_mole_claw` | 두더지 발톱 | 재료 | common | src/icons/mat_1.jpg#3 |
| 177 | `m_crystal_gel` | 수정 슬라임 핵 | 재료 | common | src/icons/mat_3.jpg#16 |
| 178 | `m_a3_shared` | 사막 모래철 | 재료 | uncommon | src/icons/mat_6.jpg#16 |
| 179 | `m_scorpion_sac` | 전갈 독주머니 | 재료 | uncommon | src/icons/mat_4.jpg#10 |
| 180 | `m_cactus_spine` | 선인장 가시 | 재료 | uncommon | src/icons/mat_1.jpg#15 |
| 181 | `m_viper_scale` | 독사 비늘 | 재료 | uncommon | src/icons/mat_5.jpg#6 |
| 182 | `m_vulture_feather` | 독수리 깃털 | 재료 | uncommon | src/icons/mat_2.jpg#4 |
| 183 | `m_bandit_cloth` | 도적의 터번천 | 재료 | uncommon | src/icons/mat_2.jpg#5 |
| 184 | `m_sand_dust` | 모래 정령 가루 | 재료 | uncommon | src/icons/mat_4.jpg#11 |
| 185 | `m_camel_shell` | 낙타 거북 등딱지 | 재료 | uncommon | src/icons/mat_5.jpg#14 |
| 186 | `m_antlion_jaw` | 개미귀신 턱 | 재료 | uncommon | src/icons/mat_1.jpg#4 |
| 187 | `m_a4_shared` | 저주받은 금박 | 재료 | uncommon | src/icons/mat_6.jpg#18 |
| 188 | `m_mummy_wrap` | 미라 붕대 | 재료 | uncommon | src/icons/mat_2.jpg#8 |
| 189 | `m_scarab_wing` | 스카라베 날개딱지 | 재료 | uncommon | src/icons/mat_5.jpg#15 |
| 190 | `m_anubis_blade` | 아누비스 창날 | 재료 | uncommon | src/icons/mat_6.jpg#19 |
| 191 | `m_cursed_shard` | 저주 항아리 파편 | 재료 | uncommon | src/icons/mat_1.jpg#18 |
| 192 | `m_statue_gem` | 석상 눈알 보석 | 재료 | uncommon | src/icons/mat_3.jpg#17 |
| 193 | `m_ghostcat_fur` | 망령 고양이 털 | 재료 | uncommon | src/icons/mat_4.jpg#12 |
| 194 | `m_slab_chunk` | 석판 골렘 조각 | 재료 | uncommon | src/icons/mat_7.jpg#0 |
| 195 | `m_bowstring` | 해골 궁수 활시위 | 재료 | uncommon | src/icons/mat_2.jpg#9 |
| 196 | `m_a5_shared` | 심해 비늘 조각 | 재료 | rare | src/icons/mat_5.jpg#16 |
| 197 | `m_fishman_scale` | 어인 비늘 | 재료 | rare | src/icons/mat_5.jpg#7 |
| 198 | `m_jelly_tendril` | 해파리 촉수 | 재료 | rare | src/icons/mat_4.jpg#13 |
| 199 | `m_puffer_spine` | 복어 가시 | 재료 | rare | src/icons/mat_1.jpg#5 |
| 200 | `m_shark_tooth` | 상어 이빨 | 재료 | rare | src/icons/mat_1.jpg#6 |
| 201 | `m_ink_sac` | 문어 먹물주머니 | 재료 | rare | src/icons/mat_4.jpg#14 |
| 202 | `m_eel_organ` | 뱀장어 발전기관 | 재료 | rare | src/icons/mat_4.jpg#15 |
| 203 | `m_angler_lure` | 아귀 등불 | 재료 | rare | src/icons/mat_3.jpg#19 |
| 204 | `m_conch_shell` | 소라 껍데기 | 재료 | rare | src/icons/mat_5.jpg#17 |
| 205 | `m_a6_shared` | 바다 소금 결정 | 재료 | rare | src/icons/mat_4.jpg#1 |
| 206 | `m_claw_shell` | 집게 껍질 | 재료 | rare | src/icons/mat_5.jpg#18 |
| 207 | `m_gull_feather` | 갈매기 깃털 | 재료 | rare | src/icons/mat_2.jpg#10 |
| 208 | `m_pirate_bone` | 해적 해골 뼈 | 재료 | rare | src/icons/mat_1.jpg#7 |
| 209 | `m_barnacle_plate` | 따개비 판 | 재료 | rare | src/icons/mat_5.jpg#19 |
| 210 | `m_turtle_plate` | 바다거북 등판 | 재료 | rare | src/icons/mat_6.jpg#0 |
| 211 | `m_wave_drop` | 파도 정령 물방울 | 재료 | rare | src/icons/mat_4.jpg#16 |
| 212 | `m_starfish_flesh` | 불가사리 재생살 | 재료 | rare | src/icons/mat_5.jpg#9 |
| 213 | `m_parrot_plume` | 앵무새 꽁지깃 | 재료 | rare | src/icons/mat_2.jpg#11 |
| 214 | `m_a7_shared` | 용암석 조각 | 재료 | epic | src/icons/mat_7.jpg#4 |
| 215 | `m_lava_gel` | 용암 슬라임 핵 | 재료 | epic | src/icons/mat_4.jpg#17 |
| 216 | `m_fire_gland` | 도롱뇽 불주머니 | 재료 | epic | src/icons/mat_4.jpg#18 |
| 217 | `m_magma_heart` | 용암 바위 심 | 재료 | epic | src/icons/mat_7.jpg#5 |
| 218 | `m_imp_trident` | 임프 삼지창 끝 | 재료 | epic | src/icons/mat_7.jpg#6 |
| 219 | `m_ash_feather` | 불사조 잿깃 | 재료 | epic | src/icons/mat_2.jpg#12 |
| 220 | `m_cursed_plate` | 저주 갑옷 파편 | 재료 | epic | src/icons/mat_7.jpg#7 |
| 221 | `m_hound_fang` | 화염 사냥개 송곳니 | 재료 | epic | src/icons/mat_1.jpg#8 |
| 222 | `m_obsidian_tip` | 흑요석 화살촉 | 재료 | epic | src/icons/mat_4.jpg#2 |
| 223 | `m_a8_shared` | 영구 서리 결정 | 재료 | epic | src/icons/mat_4.jpg#3 |
| 224 | `m_wolf_pelt` | 서리 늑대 모피 | 재료 | epic | src/icons/mat_5.jpg#10 |
| 225 | `m_ice_gel` | 얼음 슬라임 젤 | 재료 | epic | src/icons/mat_4.jpg#19 |
| 226 | `m_yeti_fur` | 설인 새끼 털 | 재료 | epic | src/icons/mat_5.jpg#11 |
| 227 | `m_fairy_wing` | 서리 요정 날개 | 재료 | epic | src/icons/mat_2.jpg#14 |
| 228 | `m_penguin_helm` | 펭귄 기사 깃털 투구 | 재료 | epic | src/icons/mat_7.jpg#9 |
| 229 | `m_storm_feather` | 뇌운 새 깃털 | 재료 | epic | src/icons/mat_2.jpg#15 |
| 230 | `m_ice_shell` | 얼음 거북 등딱지 | 재료 | epic | src/icons/mat_6.jpg#2 |
| 231 | `m_gargoyle_shard` | 가고일 날개 석편 | 재료 | epic | src/icons/mat_7.jpg#10 |
| 232 | `m_a9_shared` | 공허의 먼지 | 재료 | legendary | src/icons/mat_5.jpg#0 |
| 233 | `m_skeleton_femur` | 해골 창병 대퇴골 | 재료 | legendary | src/icons/mat_1.jpg#9 |
| 234 | `m_goblin_pouch` | 고블린 도둑 주머니 | 재료 | legendary | src/icons/mat_2.jpg#17 |
| 235 | `m_wisp_essence` | 도깨비불 정수 | 재료 | legendary | src/icons/mat_5.jpg#1 |
| 236 | `m_grimoire_page` | 마도서 쪽 | 재료 | legendary | src/icons/mat_2.jpg#18 |
| 237 | `m_shadow_cloth` | 그림자 천 | 재료 | legendary | src/icons/mat_2.jpg#19 |
| 238 | `m_void_lens` | 공허 눈알 수정체 | 재료 | legendary | src/icons/mat_4.jpg#4 |
| 239 | `m_heartstone` | 가고일 심장석 | 재료 | legendary | src/icons/mat_7.jpg#12 |
| 240 | `m_doll_stuffing` | 저주 인형 솜 | 재료 | legendary | src/icons/mat_7.jpg#14 |
| 241 | `m_c_tusk` | 돌엄니의 거대 엄니 | 재료 | common | src/icons/mat_1.jpg#2 |
| 242 | `m_c_queen_gland` | 여왕벌 왕관 독샘 | 재료 | common | src/icons/mat_4.jpg#8 |
| 243 | `m_c_blood_wing` | 박쥐왕의 피날개 | 재료 | common | src/icons/mat_5.jpg#5 |
| 244 | `m_c_fuse` | 도깨비 대장의 폭약 심지 | 재료 | common | src/icons/mat_1.jpg#17 |
| 245 | `m_c_sun_tail` | 태양침의 황금 꼬리 | 재료 | uncommon | src/icons/mat_6.jpg#17 |
| 246 | `m_c_silk_cape` | 도적 두목의 비단 망토천 | 재료 | uncommon | src/icons/mat_2.jpg#6 |
| 247 | `m_c_twin_mask` | 쌍둥이의 황금 가면 조각 | 재료 | uncommon | src/icons/mat_7.jpg#1 |
| 248 | `m_c_curse_staff` | 대신관의 저주 홀 조각 | 재료 | uncommon | src/icons/mat_3.jpg#18 |
| 249 | `m_c_shark_fin` | 백상어 장군의 지느러미 | 재료 | rare | src/icons/mat_5.jpg#8 |
| 250 | `m_c_abyss_lamp` | 아귀 여왕의 심해 등불 | 재료 | rare | src/icons/mat_4.jpg#0 |
| 251 | `m_c_cursed_coin` | 유령 선장의 저주 금화 | 재료 | rare | src/icons/mat_7.jpg#3 |
| 252 | `m_c_great_claw` | 바닷가재의 대집게 | 재료 | rare | src/icons/mat_6.jpg#1 |
| 253 | `m_c_giant_heart` | 용암 거인의 심장석 | 재료 | epic | src/icons/mat_7.jpg#8 |
| 254 | `m_c_flame_hair` | 화염 마녀의 불꽃 머리칼 | 재료 | epic | src/icons/mat_2.jpg#13 |
| 255 | `m_c_silver_fur` | 어미 설인의 은빛 털 | 재료 | epic | src/icons/mat_5.jpg#12 |
| 256 | `m_c_thunder_plume` | 그리폰의 뇌전 깃털 | 재료 | epic | src/icons/mat_2.jpg#16 |
| 257 | `m_c_shadow_edge` | 쌍검사의 그림자 칼날 | 재료 | legendary | src/icons/mat_7.jpg#13 |
| 258 | `m_c_gravity_core` | 수문장의 중력핵 | 재료 | legendary | src/icons/mat_3.jpg#9 |
| 259 | `m_core_moss` | 이끼 수정 핵 | 재료 | common | src/icons/mat_3.jpg#0 |
| 260 | `m_core_spider` | 여왕거미의 수정 심장 | 재료 | common | src/icons/mat_3.jpg#1 |
| 261 | `m_core_sandworm` | 대지렁이의 모래 핵 | 재료 | uncommon | src/icons/mat_3.jpg#2 |
| 262 | `m_core_pharaoh` | 미라왕의 황금 심장 | 재료 | uncommon | src/icons/mat_3.jpg#3 |
| 263 | `m_core_kraken` | 크라켄의 심연 핵 | 재료 | rare | src/icons/mat_3.jpg#4 |
| 264 | `m_core_crab` | 거대게의 산호 심장 | 재료 | rare | src/icons/mat_3.jpg#6 |
| 265 | `m_core_hellfire` | 흑기사의 업화 핵 | 재료 | epic | src/icons/mat_3.jpg#7 |
| 266 | `m_core_storm` | 와이번의 뇌전 핵 | 재료 | epic | src/icons/mat_3.jpg#8 |
| 267 | `m_core_void` | 대사제의 공허 핵 | 재료 | legendary | src/icons/mat_3.jpg#10 |
| 268 | `m_core_dragon` | 마룡의 삼두 핵 | 재료 | legendary | src/icons/mat_3.jpg#11 |
| 269 | `x_m_a1_shared` | 타락한 초록 정기 조각 | 재료 | corrupt | src/icons/mat_4.jpg#5 |
| 270 | `x_m_a2_shared` | 타락한 동굴 수정 파편 | 재료 | corrupt | src/icons/mat_3.jpg#15 |
| 271 | `x_m_a3_shared` | 타락한 사막 모래철 | 재료 | corrupt | src/icons/mat_6.jpg#16 |
| 272 | `x_m_a4_shared` | 타락한 저주받은 금박 | 재료 | corrupt | src/icons/mat_6.jpg#18 |
| 273 | `x_m_a5_shared` | 타락한 심해 비늘 조각 | 재료 | corrupt | src/icons/mat_5.jpg#16 |
| 274 | `x_m_a6_shared` | 타락한 바다 소금 결정 | 재료 | corrupt | src/icons/mat_4.jpg#1 |
| 275 | `x_m_a7_shared` | 타락한 용암석 조각 | 재료 | corrupt | src/icons/mat_7.jpg#4 |
| 276 | `x_m_a8_shared` | 타락한 영구 서리 결정 | 재료 | corrupt | src/icons/mat_4.jpg#3 |
| 277 | `x_m_a9_shared` | 타락한 공허의 먼지 | 재료 | corrupt | src/icons/mat_5.jpg#0 |
| 278 | `x_m_c_tusk` | 타락한 돌엄니의 거대 엄니 | 재료 | corrupt | src/icons/mat_1.jpg#2 |
| 279 | `x_m_c_queen_gland` | 타락한 여왕벌 왕관 독샘 | 재료 | corrupt | src/icons/mat_4.jpg#8 |
| 280 | `x_m_c_blood_wing` | 타락한 박쥐왕의 피날개 | 재료 | corrupt | src/icons/mat_5.jpg#5 |
| 281 | `x_m_c_fuse` | 타락한 도깨비 대장의 폭약 심지 | 재료 | corrupt | src/icons/mat_1.jpg#17 |
| 282 | `x_m_c_sun_tail` | 타락한 태양침의 황금 꼬리 | 재료 | corrupt | src/icons/mat_6.jpg#17 |
| 283 | `x_m_c_silk_cape` | 타락한 도적 두목의 비단 망토천 | 재료 | corrupt | src/icons/mat_2.jpg#6 |
| 284 | `x_m_c_twin_mask` | 타락한 쌍둥이의 황금 가면 조각 | 재료 | corrupt | src/icons/mat_7.jpg#1 |
| 285 | `x_m_c_curse_staff` | 타락한 대신관의 저주 홀 조각 | 재료 | corrupt | src/icons/mat_3.jpg#18 |
| 286 | `x_m_c_shark_fin` | 타락한 백상어 장군의 지느러미 | 재료 | corrupt | src/icons/mat_5.jpg#8 |
| 287 | `x_m_c_abyss_lamp` | 타락한 아귀 여왕의 심해 등불 | 재료 | corrupt | src/icons/mat_4.jpg#0 |
| 288 | `x_m_c_cursed_coin` | 타락한 유령 선장의 저주 금화 | 재료 | corrupt | src/icons/mat_7.jpg#3 |
| 289 | `x_m_c_great_claw` | 타락한 바닷가재의 대집게 | 재료 | corrupt | src/icons/mat_6.jpg#1 |
| 290 | `x_m_c_giant_heart` | 타락한 용암 거인의 심장석 | 재료 | corrupt | src/icons/mat_7.jpg#8 |
| 291 | `x_m_c_flame_hair` | 타락한 화염 마녀의 불꽃 머리칼 | 재료 | corrupt | src/icons/mat_2.jpg#13 |
| 292 | `x_m_c_silver_fur` | 타락한 어미 설인의 은빛 털 | 재료 | corrupt | src/icons/mat_5.jpg#12 |
| 293 | `x_m_c_thunder_plume` | 타락한 그리폰의 뇌전 깃털 | 재료 | corrupt | src/icons/mat_2.jpg#16 |
| 294 | `x_m_c_shadow_edge` | 타락한 쌍검사의 그림자 칼날 | 재료 | corrupt | src/icons/mat_7.jpg#13 |
| 295 | `x_m_c_gravity_core` | 타락한 수문장의 중력핵 | 재료 | corrupt | src/icons/mat_3.jpg#9 |
| 296 | `tf_cloth` | 피 묻은 천 조각 | 재료 | common | src/icons/mat_2.jpg#1 |
| 297 | `tf_scrap` | 녹슨 쇠붙이 | 재료 | common | src/icons/mat_1.jpg#16 |
| 298 | `tf_herb` | 말린 약초 다발 | 재료 | common | src/icons/mat_1.jpg#13 |
| 299 | `tf_tool` | 손때 묻은 연장 | 재료 | common | src/icons/mat_6.jpg#13 |
| 300 | `tf_jewel` | 작은 장신구 | 재료 | common | src/icons/mat_3.jpg#13 |
| 301 | `tf_page` | 찢어진 책장 | 재료 | common | src/icons/mat_2.jpg#2 |
| 302 | `tf_holy` | 성물 조각 | 재료 | common | src/icons/mat_3.jpg#14 |
| 303 | `tf_soul` | 원한 서린 혼석 | 재료 | rare | src/icons/mat_3.jpg#5 |
| 304 | `tk_kalbaram` | 칼바람의 징표 | 재료 | epic | src/icons/mat_6.jpg#3 |
| 305 | `tk_sol` | 매눈 솔의 징표 | 재료 | epic | src/icons/mat_6.jpg#4 |
| 306 | `tk_gomsoe` | 곰쇠의 징표 | 재료 | epic | src/icons/mat_6.jpg#5 |
| 307 | `tk_zahra` | 자흐라의 징표 | 재료 | epic | src/icons/mat_6.jpg#6 |
| 308 | `tk_mago` | 마고의 징표 | 재료 | epic | src/icons/mat_7.jpg#16 |
| 309 | `tk_garon` | 가론의 징표 | 재료 | epic | src/icons/mat_6.jpg#8 |
| 310 | `tk_hanbing` | 한빙의 징표 | 재료 | epic | src/icons/mat_6.jpg#9 |
| 311 | `tk_grim` | 그림의 징표 | 재료 | epic | src/icons/mat_6.jpg#10 |
| 312 | `m_aeon_core` | 영겁의 핵 | 재료 | legendary | src/icons/mat_3.jpg#12 |
| 313 | `m_round_shard` | 원탁의 파편 | 재료 | legendary | src/icons/mat_6.jpg#11 |
| 314 | `scroll_area1` | 1지역 레시피 두루마리 조각 | 재료 | common | src/icons/mat_1.jpg#19 |
| 315 | `scroll_area2` | 2지역 레시피 두루마리 조각 | 재료 | common | src/icons/mat_1.jpg#19 |
| 316 | `scroll_area3` | 3지역 레시피 두루마리 조각 | 재료 | uncommon | src/icons/mat_1.jpg#19 |
| 317 | `scroll_area4` | 4지역 레시피 두루마리 조각 | 재료 | uncommon | src/icons/mat_1.jpg#19 |
| 318 | `scroll_area5` | 5지역 레시피 두루마리 조각 | 재료 | rare | src/icons/mat_1.jpg#19 |
| 319 | `scroll_area6` | 6지역 레시피 두루마리 조각 | 재료 | rare | src/icons/mat_1.jpg#19 |
| 320 | `scroll_area7` | 7지역 레시피 두루마리 조각 | 재료 | epic | src/icons/mat_1.jpg#19 |
| 321 | `scroll_area8` | 8지역 레시피 두루마리 조각 | 재료 | epic | src/icons/mat_1.jpg#19 |
| 322 | `scroll_area9` | 9지역 레시피 두루마리 조각 | 재료 | legendary | src/icons/mat_1.jpg#19 |
| 323 | `scroll_area10` | 10지역 레시피 두루마리 조각 | 재료 | legendary | src/icons/mat_1.jpg#19 |
| 324 | `scroll_first_bearer` | 레시피 두루마리: 선대의 부러진 검 복원 | 재료 | legendary | src/icons/mat_7.jpg#15 |
| 325 | `ui_coins` | 금화 | UI | common | src/icons/mat_7.jpg#17 |
| 326 | `ui_bag` | 가방 | UI | common | src/icons/mat_7.jpg#18 |
| 327 | `ui_anvil` | 대장간 | UI | common | src/icons/mat_7.jpg#19 |
