# 일반 몹 시트 인덱스 (신규 42종)

WORLD_PLAN.md 기준 1~9지역 일반 몹 72종(지역당 8종) 중, ★표시(이미 그림 있음, `town-demo/src/monsters/mobs_*.jpg` 6장에 그려진 MONSTERS.md의 30종)를 뺀 **42종**을 새로 그렸다.
10지역 강화판(타락한 변형)과 챔피언 18종은 제외. id는 `a{지역}_{지역 내 순번(tools/design/craft_data.py AREAS 순서)}_{영문}` 형식.

- 형식: 1280×720, 3열×2행, 칸마다 왼쪽=대기 / 오른쪽=공격 자세, 배경 #FF00FF로 정규화
- `mobs_XX.jpg` = 라벨 없음, `mobs_XX_named.jpg` = 한국어 이름 라벨
- 시트는 지역 순서대로 6칸씩 채움 (시트 하나가 두세 지역에 걸칠 수 있음)

## mobs_01.jpg — 1지역 시작의 숲 + 2지역 수정 동굴

| 칸 | 행,열 | id | 이름 | 지역 | 고유 능력 (공격 자세) |
|---|---|---|---|---|---|
| 1 (좌상) | 1,1 | `a1_06_forest_slime` | 숲 슬라임 (Forest Slime) | 1 시작의 숲 | 분열 |
| 2 (중상) | 1,2 | `a1_07_acorn_squirrel` | 도토리 다람쥐 (Acorn Squirrel) | 1 시작의 숲 | 열매 투척 |
| 3 (우상) | 1,3 | `a1_08_spirit_sprout` | 나무 정령 새싹 (Tree Spirit Sprout) | 1 시작의 숲 | 뿌리 묶기 |
| 4 (좌하) | 2,1 | `a2_06_glow_worm` | 반딧불 지렁이 (Glow Worm) | 2 수정 동굴 | 어둠에서만 보임 |
| 5 (중하) | 2,2 | `a2_07_cave_mole` | 동굴 두더지 (Cave Mole) | 2 수정 동굴 | 땅파기 기습 |
| 6 (우하) | 2,3 | `a2_08_crystal_slime` | 수정 슬라임 (Crystal Slime) | 2 수정 동굴 | 빛 반사 레이저 |

## mobs_02.jpg — 3지역 모래 사막

| 칸 | 행,열 | id | 이름 | 지역 | 고유 능력 (공격 자세) |
|---|---|---|---|---|---|
| 1 (좌상) | 1,1 | `a3_03_sand_viper` | 모래 독사 (Sand Viper) | 3 모래 사막 | 모래 속 기습 |
| 2 (중상) | 1,2 | `a3_04_bald_vulture` | 대머리 독수리 (Bald Vulture) | 3 모래 사막 | 급강하 |
| 3 (우상) | 1,3 | `a3_05_desert_bandit` | 사막 도적 (Desert Bandit) | 3 모래 사막 | 모래 뿌려 시야 가림 |
| 4 (좌하) | 2,1 | `a3_06_sand_spirit` | 모래 정령 (Sand Spirit) | 3 모래 사막 | 회오리 |
| 5 (중하) | 2,2 | `a3_07_camel_tortoise` | 낙타 거북 (Camel Tortoise) | 3 모래 사막 | 등딱지 굴러오기 |
| 6 (우하) | 2,3 | `a3_08_antlion` | 개미귀신 (Antlion) | 3 모래 사막 | 모래 함정 |

## mobs_03.jpg — 4지역 피라미드

| 칸 | 행,열 | id | 이름 | 지역 | 고유 능력 (공격 자세) |
|---|---|---|---|---|---|
| 1 (좌상) | 1,1 | `a4_02_scarab_swarm` | 스카라베 떼 (Scarab Swarm) | 4 피라미드 | 무리 돌진 |
| 2 (중상) | 1,2 | `a4_03_anubis_guard` | 아누비스 경비병 (Anubis Guard) | 4 피라미드 | 창 찌르기 |
| 3 (우상) | 1,3 | `a4_04_cursed_jar` | 저주 항아리 (Cursed Jar) | 4 피라미드 | 독 연기 |
| 4 (좌하) | 2,1 | `a4_05_serpent_statue` | 뱀 머리 석상 (Serpent-Head Statue) | 4 피라미드 | 석화 시선 |
| 5 (중하) | 2,2 | `a4_06_ghost_cat` | 고양이 망령 (Ghost Cat) | 4 피라미드 | 벽 통과 |
| 6 (우하) | 2,3 | `a4_07_slab_golem` | 함정 석판 골렘 (Trap Slab Golem) | 4 피라미드 | 바닥 압사 |

## mobs_04.jpg — 4지역 피라미드 + 5지역 산호 바다

| 칸 | 행,열 | id | 이름 | 지역 | 고유 능력 (공격 자세) |
|---|---|---|---|---|---|
| 1 (좌상) | 1,1 | `a4_08_sand_skeleton_archer` | 모래 해골 궁수 (Sand Skeleton Archer) | 4 피라미드 | 화살 |
| 2 (중상) | 1,2 | `a5_02_jellyfish` | 해파리 (Jellyfish) | 5 산호 바다 | 감전 |
| 3 (우상) | 1,3 | `a5_03_spiny_puffer` | 가시 복어 (Spiny Puffer) | 5 산호 바다 | 부풀며 가시 발사 |
| 4 (좌하) | 2,1 | `a5_04_shark_trooper` | 상어 돌격병 (Shark Trooper) | 5 산호 바다 | 물속 돌진 |
| 5 (중하) | 2,2 | `a5_05_octopus_inker` | 문어 먹물병 (Octopus Inker) | 5 산호 바다 | 시야 먹물 |
| 6 (우하) | 2,3 | `a5_06_electric_eel` | 전기 뱀장어 (Electric Eel) | 5 산호 바다 | 번개 줄기 |

## mobs_05.jpg — 5지역 산호 바다 + 6지역 해안 절벽

| 칸 | 행,열 | id | 이름 | 지역 | 고유 능력 (공격 자세) |
|---|---|---|---|---|---|
| 1 (좌상) | 1,1 | `a5_07_anglerfish` | 아귀 (Anglerfish) | 5 산호 바다 | 불빛 유인 |
| 2 (중상) | 1,2 | `a5_08_hermit_crab` | 소라게 (Hermit Crab) | 5 산호 바다 | 껍질 숨기 |
| 3 (우상) | 1,3 | `a6_02_seagull` | 갈매기 (Seagull) | 6 해안 절벽 | 물건 낚아채기 |
| 4 (좌하) | 2,1 | `a6_03_pirate_skeleton` | 해적 해골 (Pirate Skeleton) | 6 해안 절벽 | 칼 + 대포 |
| 5 (중하) | 2,2 | `a6_04_barnacle_golem` | 따개비 골렘 (Barnacle Golem) | 6 해안 절벽 | 반사 갑옷 |
| 6 (우하) | 2,3 | `a6_05_turtle_shieldbearer` | 바다 거북 방패병 (Sea Turtle Shieldbearer) | 6 해안 절벽 | 막기 |

## mobs_06.jpg — 6지역 해안 절벽 + 7지역 화산 성채 + 8지역 설산 뇌전 탑

| 칸 | 행,열 | id | 이름 | 지역 | 고유 능력 (공격 자세) |
|---|---|---|---|---|---|
| 1 (좌상) | 1,1 | `a6_06_wave_spirit` | 파도 정령 (Wave Spirit) | 6 해안 절벽 | 밀쳐내기 |
| 2 (중상) | 1,2 | `a6_07_starfish` | 불가사리 (Starfish) | 6 해안 절벽 | 재생 |
| 3 (우상) | 1,3 | `a6_08_pirate_parrot` | 해적 앵무새 (Pirate Parrot) | 6 해안 절벽 | 소리로 적 부르기 |
| 4 (좌하) | 2,1 | `a7_07_flame_hound` | 화염 사냥개 (Flame Hound) | 7 화산 성채 | 불 발자국 |
| 5 (중하) | 2,2 | `a7_08_obsidian_archer` | 흑요석 궁수 (Obsidian Archer) | 7 화산 성채 | 불화살 |
| 6 (우하) | 2,3 | `a8_06_thundercloud_bird` | 뇌운 새 (Thundercloud Bird) | 8 설산 뇌전 탑 | 번개 낙하 |

## mobs_07.jpg — 8지역 설산 뇌전 탑 + 9지역 어둠 신전

| 칸 | 행,열 | id | 이름 | 지역 | 고유 능력 (공격 자세) |
|---|---|---|---|---|---|
| 1 (좌상) | 1,1 | `a8_07_ice_turtle` | 얼음 거북 (Ice Turtle) | 8 설산 뇌전 탑 | 빙판 미끄럼 |
| 2 (중상) | 1,2 | `a8_08_storm_gargoyle` | 폭풍 가고일 (Storm Gargoyle) | 8 설산 뇌전 탑 | 급강하 + 석화 |
| 3 (우상) | 1,3 | `a9_05_shadow_assassin` | 그림자 암살자 (Shadow Assassin) | 9 어둠 신전 | 투명화 |
| 4 (좌하) | 2,1 | `a9_06_void_eye` | 공허 눈알 (Void Eye) | 9 어둠 신전 | 광선 |
| 5 (중하) | 2,2 | `a9_07_gargoyle_statue` | 가고일 석상 (Gargoyle Statue) | 9 어둠 신전 | 움직이면 공격 |
| 6 (우하) | 2,3 | `a9_08_cursed_doll` | 저주 인형 (Cursed Doll) | 9 어둠 신전 | 받은 피해 공유 |
