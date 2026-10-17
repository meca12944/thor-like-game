# 장비와 외형 시스템

> 전체 아이템 목록과 출처는 [ITEMS.md](ITEMS.md). 데이터: `data/towns.json` → `catalog`, `equipment`. (아직 게임에 구현하지 않음 — 설계만)

## 장비 칸 (4칸)

| 칸 | 레이어 | 외형 변화 |
|---|---|---|
| 무기 | `weapon` | 검 스프라이트(날 모양·색)와 베기 궤적 색이 바뀐다. 3단 콤보(횡베기·찌르기·돌려베기)와 스킬 포즈 모두에 적용. |
| 방어구 | `armor` | 튜닉/갑옷 레이어. 몸통·팔·허리 부분 외형이 바뀐다. |
| 투구 | `helmet` | 머리 장비(선택). 비우면 기본 갈색 머리가 그대로 보인다. |
| 보조무기 | `offhand` | 방패·팔보호대·투척무기·오브·부적·반지·장화. 방패는 왼팔, 팔보호대는 팔뚝, 투척무기는 허리 주머니+던질 때 왼손, 오브는 어깨 옆에 떠다니는 FX, 부적은 가슴, 반지는 손가락 반짝임, 장화는 발 레이어로 보인다. |

방어구 30종은 몸 16 + 투구 14로 나뉜다(같은 「방어구」 분류, 칸은 2개).

**외형상점(코스메틱)**: 외형상점 아이템은 능력치가 없는 순수 외형 덮어쓰기. 망토 색은 망토 레이어 팔레트를, 의상 스킨은 방어구 레이어의 그림만(능력치는 장착 방어구 유지), 머리 장식은 투구 레이어가 비었거나 "투구 숨기기"일 때 표시, 궤적 스킨은 무기 궤적 색을 덮어쓴다.

## 그리기 방식: 레이어 페이퍼돌

주인공을 한 장의 그림이 아니라 여러 레이어를 겹쳐 그린다. 모든 레이어 시트는 **같은 프레임 배치·같은 앵커(발 중심)** 를 쓴다. 그래서 몸 프레임 번호 하나로 모든 레이어의 같은 칸을 겹치면 된다.

기본 순서 (아래 → 위): **몸 → (타락 눈·핏줄) → 장화 → 방어구 → 투구 → (후광·뿔) → 망토 → (오라) → 무기·보조무기**

| 방향 | 실제 그리는 순서 (아래→위) | 이유 |
|---|---|---|
| 아래(정면) | 오라(뒤) → 망토 → 몸 → 타락 눈 → 장화 → 방어구 → 투구 → 방패·오브(왼쪽) → 무기 → 오라(앞) | 망토가 등 뒤에 있음 |
| 위(뒷면) | 무기 → 방패 → 몸 → 장화 → 방어구 → 투구 → 망토 → 오라 | 망토가 몸을 덮고, 무기·방패는 몸 앞쪽(화면 안쪽)에 가려짐 |
| 오른쪽 | 방패(왼팔, 뒤쪽 팔) → 망토 → 몸 → 타락 눈 → 장화 → 방어구 → 투구 → 무기 | 왼팔은 몸 뒤, 오른손 검은 앞 |
| 왼쪽 | 오른쪽을 좌우 반전 (방패·무기 손 위치도 반전되는 것은 허용 — 기존 데모와 같은 방식) | 시트 절약 |

- 프레임 단위: 걷기 4방향×4, 3단 콤보(횡베기 2·찌르기 2·돌려베기 5, 위/아래 각 3), 스킬 포즈 약 40프레임, 피격 1, 잠수/수영 2. 프레임마다 각 레이어 그림이 따로 있다.
- 돌려베기 회전 프레임에서는 프레임마다 방향 순서를 따로 적용한다 (데이터에 프레임별 layerOrder 오버라이드 칸).
- **팔레트 스왑**: 방어구·투구·무기·방패 시트는 회색 4단계 원본으로 한 번만 그리고, 실행할 때 아이템의 `palette`(4색 램프)로 치환한다. 외곽선(검정)과 피부·눈 색은 치환하지 않는다.
- 치환 사본은 장착을 바꿀 때 1회 오프스크린 캔버스에 캐시한다. 매 프레임 비용 없음.
- 강화 외형(+4 발광, +7 오라, +9 최대 오라)은 무기 레이어 위에 코드로 덧그린다 (SYSTEMS.md).
- 투척무기: 평소엔 허리·허벅지·등의 작은 오버레이로 보이고, 보조 키(Shift)로 던질 때만 왼손 던지기 포즈 1프레임 + 투사체 스프라이트. 오브: 몸 레이어와 별개로 어깨 옆을 천천히 도는 FX(정면에선 앞, 뒷면에선 뒤). 반지: 손 위치에 2px 반짝임만.
- 쌍검(`wpn_twin`)을 들면 보조무기 칸이 잠기고 왼손에 같은 날을 하나 더 그린다.
- 코스메틱: 망토 색은 망토 레이어 팔레트 교체, 의상 스킨은 방어구 레이어 그림 교체(능력치는 그대로), 머리 장식은 투구 칸이 비었을 때(또는 「투구 숨기기」) 투구 자리에, 궤적 스킨은 무기 `trail` 색 교체.

## 선악에 따른 타락 외형

선악 수치(SYSTEMS.md 3장)가 내려가면 페이퍼돌에 타락 레이어가 추가된다. 코스메틱으로 가릴 수 없다(마왕 등급부터는 망토·의상 코스메틱도 덮어씀).

| 등급 | 추가·변경 레이어 |
|---|---|
| 성자 (+60 이상) | halo_fx: 머리 뒤 옅은 흰 금빛 원 (투구 위에 그림)<br>cape 팔레트를 흰·하늘색 쪽으로 15% 보정<br>이슬 보석 흰빛 |
| 의인 · 평범 | 변화 없음 |
| 악명 (-20 ~ -59) | eyes_corrupt_1: 눈동자 붉은 기 (몸 레이어 바로 위, 투구보다 아래)<br>veins_1: 손등·목에 검은 핏줄 (방어구 아래)<br>cape 팔레트 명도 -30% + 채도 -30%<br>베기 궤적 끝에 검붉은 잔상 1줄 |
| 마왕 (-60 ~ -89) | eyes_corrupt_2: 붉게 빛나는 눈 (투구 위에 덧그림, 투구로도 가려지지 않음)<br>veins_2: 얼굴까지 번진 핏줄<br>aura_dark_back / aura_dark_front: 몸 뒤·앞의 검보라 입자 오라 (방향별 순서는 망토와 같음)<br>cape → cape_tattered 시트 교체 (찢어진 검은 망토, 코스메틱 망토 색 무시) |
| 마왕화 (-90 이하) | horns: 투구 위 작은 검은 뿔 2개<br>그림자 레이어: 발밑 그림자가 머리 셋 달린 용 모양으로 일렁임<br>외형상점 의상 스킨 적용 불가 (타락 외형이 덮어씀) |

## 앞으로 필요한 스프라이트 시트

1. `body_base` — 기본 신체(얼굴·갈색 머리·맨손), 위 프레임 전부. 기존 걷기/콤보/스킬 시트를 다시 그려 분리.
2. `body_*` 회색 원본: tunic, quilted, leather, light, mail, plate, fur, coat, shell, scale (10종 형태) × 전 프레임.
3. `head_*` 회색 원본: hood, circlet, cap_lamp, turban, shell, helm_horn, helm_fur, helm_visor, mask, witch, plume, crown (12종) × 4방향 + 콤보/스킬 오프셋 표.
4. `cape` 회색 원본 1종(펄럭임 포함) + `cape_tattered`(타락) + 코스메틱 장식 레이어.
5. `wpn_*` 회색 원본: straight, straight_long, leaf, crystal, broad, curved, wavy, ornate, dagger, machete, harpoon, scepter, whip, flame, spear, twin (16종 날 모양) × 손 위치 프레임.
6. 보조무기: `off_shield_round`, `off_shield_kite`, `off_shield_tower`, `acc_bracer`, `acc_amulet`, `acc_boots`, `acc_ring`(반짝임 FX), `off_orb`(떠다니는 구슬 4프레임), `off_throw_*`(sling, knife, pick, ring, javelin, star — 몸 오버레이 + 투사체 1~2프레임) + 던지기 포즈 4방향.
7. `head_deco`, `neck_deco` 코스메틱 오버레이.
8. 타락: `eyes_corrupt_1/2`, `veins_1/2`, `horns`, `halo_fx`, `aura_dark`(입자), 3두 용 그림자.

제작 팁: 기존 파이프라인(마젠타 배경 시트 → 크로마키 → 연결 요소 분리)을 그대로 쓰되, 레이어 시트는 「몸 실루엣 위에 해당 부분만」 그린 시트로 주문하고 몸과 같은 칸 배치·같은 크기로 맞춘다.

## 장비 외형 설명 (팔레트 색 포함)

| ID | 아이템 | 칸 | 스프라이트 키 | 팔레트 | 궤적 | 외형 |
|---|---|---|---|---|---|---|
| `w_iron_trainee` | 견습 철검 | 무기 | `wpn_straight` | iron `#3a4250` `#6a7686` `#9aa8b8` `#d8e0e8` | `#d8e0e8` `#9aa8b8` | 짧고 곧은 회색 철날, 갈색 가죽 손잡이. 기본 검보다 날이 한 뼘 길다. |
| `w_bronze_long` | 청동 장검 | 무기 | `wpn_straight_long` | bronze `#4a2a10` `#8a5420` `#c88a3a` `#ffd9a0` | `#ffd9a0` `#c88a3a` | 구릿빛 청동 장검, 둥근 가드. 궤적이 옅은 주황색. |
| `w_mill_steel` | 물레 강철검 | 무기 | `wpn_straight` | steel_blue `#22304a` `#4a6a96` `#7fb0e0` `#e8f4ff` | `#e8f4ff` `#7fb0e0` | 푸른 기가 도는 강철날, 가드에 물레바퀴 문양. |
| `w_reed_leaf` | 갈대잎 검 | 무기 | `wpn_leaf` | reed_green `#1e3a1a` `#3e7a36` `#6ac060` `#e0ffd0` | `#e0ffd0` `#6ac060` | 버들잎처럼 가운데가 불룩한 초록빛 날. 휘두르면 연두색 잔상. |
| `w_crystal_edge` | 수정날 검 | 무기 | `wpn_crystal` | crystal_cyan `#0e4a5a` `#2a9aaa` `#5ee0e0` `#e0ffff` | `#e0ffff` `#5ee0e0` | 반투명 하늘색 수정 날, 날 안쪽에서 빛이 일렁인다. 궤적에 수정 파편 반짝임. |
| `w_miner_broad` | 광부의 두꺼운 검 | 무기 | `wpn_broad` | dark_iron_copper `#1a1a20` `#3a3a44` `#a86a3a` `#f0d0b0` | `#f0d0b0` `#a86a3a` | 넓고 두꺼운 검은 철날에 구리 띠 세 줄. 묵직한 갈색 궤적. |
| `w_desert_crescent` | 사막 초승달검 | 무기 | `wpn_curved` | desert_gold `#5a3a08` `#a0700a` `#e0b030` `#fff0b0` | `#fff0b0` `#e0b030` | 초승달처럼 휜 금빛 곡도, 붉은 술 장식. 금색 궤적. |
| `w_sun_sigil` | 태양 문양 검 | 무기 | `wpn_straight_long` | sun_gold `#6a4000` `#b08000` `#ffcf40` `#fffbe0` | `#fffbe0` `#ffcf40` | 곧은 금날 전체에 태양 문양 음각, 가드 중앙에 붉은 보석. |
| `w_wave_blade` | 파도 검 | 무기 | `wpn_wavy` | sea_blue `#0a2a5a` `#1a5aa0` `#30a0e0` `#e0f8ff` | `#e0f8ff` `#30a0e0` | 물결치듯 구불구불한 바다색 날(플랑베르주형). 궤적이 물보라처럼 흩어진다. |
| `w_anchor_great` | 닻 대검 | 무기 | `wpn_broad` | anchor_steel `#2a3038` `#4a5664` `#6a7a8a` `#f0f0f0` | `#f0f0f0` `#6a7a8a` | 닻 모양 가드가 달린 넓은 회철 대검, 손잡이에 밧줄 감김. |
| `w_obsidian` | 흑요석 검 | 무기 | `wpn_crystal` | obsidian_ember `#0a0a10` `#20202a` `#ff6a20` `#ffd0a0` | `#ffd0a0` `#ff6a20` | 검은 유리 같은 흑요석 날, 가장자리만 주황 불씨처럼 빛남. 주황 궤적. |
| `w_forge_great` | 용광로 대검 | 무기 | `wpn_broad` | forge_red `#1a0e0a` `#3a1a10` `#ff3a10` `#fff0c0` | `#fff0c0` `#ff3a10` | 넓은 흑철 날 가운데 금 간 홈에서 붉은 용암빛이 새어 나온다. |
| `w_frost_crystal` | 서리 결정검 | 무기 | `wpn_crystal` | ice_pale `#3a5a7a` `#6a9ac0` `#a0d8ff` `#ffffff` | `#ffffff` `#a0d8ff` | 얼음 결정이 겹겹이 자란 창백한 하늘색 날, 서리 김이 피어오름. |
| `w_northwind` | 북풍 장검 | 무기 | `wpn_straight_long` | silver_fur `#4a505a` `#8a92a0` `#c0c8d8` `#f8fbff` | `#f8fbff` `#c0c8d8` | 은빛 장검, 손잡이에 흰 털가죽, 가드 끝에 늑대 머리. |
| `w_royal_knight` | 왕실 기사검 | 무기 | `wpn_ornate` | royal_silver_gold `#3a3a50` `#8a8ca0` `#ffd860` `#ffffff` | `#ffffff` `#ffd860` | 은날에 금 상감, 십자 가드에 파란 왕실 보석. 흰·금 이중 궤적. |
| `w_mithril` | 미스릴 장검 | 무기 | `wpn_straight_long` | mithril `#2a4a5a` `#4a8aa0` `#80e0ff` `#f0ffff` | `#f0ffff` `#80e0ff` | 은청색으로 은은히 빛나는 미스릴 장검, 날 위로 룬 문자가 흐른다. |
| `b_cloth_tunic` | 천 튜닉 | 방어구(몸) | `body_tunic` | tunic_blue `#0e1a3a` `#1e3a7a` `#2e5ab0` `#5a8ae0` | — | 기본과 같은 파란 튜닉에 갈색 허리띠 (컨셉 아트 기본 모습). |
| `b_quilted` | 누빔 갑옷 | 방어구(몸) | `body_quilted` | quilted_beige `#4a3a2a` `#8a7458` `#c8b090` `#f0e2c8` | — | 베이지색 누빔 천 갑옷, 가슴에 마름모 박음질. |
| `b_miner_vest` | 광부 가죽 조끼 | 방어구(몸) | `body_leather` | leather_brown `#2a1608` `#5a3418` `#8a5a2e` `#c08a52` | — | 튜닉 위에 두꺼운 갈색 가죽 조끼와 구리 버클 멜빵. |
| `b_desert_silk` | 사막 비단 경갑 | 방어구(몸) | `body_light` | sand_gold `#5a4420` `#a08050` `#d8c090` `#fff0c8` | — | 모래색 비단 위 얇은 금 테 경갑, 허리에 붉은 띠. |
| `b_scale_mail` | 비늘 사슬갑옷 | 방어구(몸) | `body_mail` | sea_scale `#0a3a3a` `#1a6a64` `#30a090` `#9ae0d0` | — | 청록 물고기 비늘 모양 사슬갑옷, 어깨에 조개 장식. |
| `b_black_plate` | 흑철 판금 흉갑 | 방어구(몸) | `body_plate` | black_iron_red `#0a0a0e` `#24242c` `#4a4a56` `#c02020` | — | 검은 판금 흉갑, 붉은 리벳과 어깨 판갑. |
| `b_snow_fur` | 설원 털가죽 갑옷 | 방어구(몸) | `body_fur` | fur_white_grey `#4a4e56` `#8a909a` `#d8dce4` `#ffffff` | — | 흰 털가죽 깃과 회색 사슬 조끼, 소매 끝 털 장식. |
| `b_mithril_plate` | 미스릴 판금 | 방어구(몸) | `body_plate` | mithril_gold `#2a4a5a` `#5a9ab0` `#a0e8ff` `#ffd860` | — | 은청색 미스릴 판금에 금 테두리, 가슴에 세 용 문장. |
| `h_leather_hood` | 가죽 두건 | 방어구(투구) | `head_hood` | leather_brown `#2a1608` `#5a3418` `#8a5a2e` `#c08a52` | — | 갈색 가죽 두건, 앞머리가 살짝 보인다. |
| `h_steel_circlet` | 강철 머리띠 | 방어구(투구) | `head_circlet` | steel_blue `#22304a` `#4a6a96` `#7fb0e0` `#e8f4ff` | — | 이마를 두르는 얇은 강철 머리띠, 가운데 작은 푸른 돌. |
| `h_miner_helmet` | 광부 헬멧 | 방어구(투구) | `head_cap_lamp` | miner_yellow `#5a4000` `#b08a00` `#f0c820` `#fff4a0` | — | 노란 둥근 헬멧, 앞에 작은 램프 (동굴에서 주변이 약간 밝아짐). |
| `h_turban` | 루비 터번 | 방어구(투구) | `head_turban` | turban_white_ruby `#8a8070` `#d8d0c0` `#ffffff` `#d01030` | — | 흰 터번에 붉은 루비 핀, 뒤로 천 자락이 흩날림. |
| `h_nautilus` | 앵무조개 투구 | 방어구(투구) | `head_shell` | shell_coral `#6a2a3a` `#c05a6a` `#ff9aa0` `#ffe0d8` | — | 앵무조개 껍데기를 깎은 산호빛 투구. |
| `h_horned` | 뿔 달린 흑철 투구 | 방어구(투구) | `head_helm_horn` | black_iron_red `#0a0a0e` `#24242c` `#4a4a56` `#c02020` | — | 검은 투구 양옆에 굽은 뿔, 눈구멍에서 붉은 빛. |
| `h_fur_helm` | 털모자 투구 | 방어구(투구) | `head_helm_fur` | fur_white_grey `#4a4e56` `#8a909a` `#d8dce4` `#ffffff` | — | 쇠 투구 안쪽과 귀덮개에 흰 털. |
| `h_knight_plume` | 깃털 기사 투구 | 방어구(투구) | `head_helm_visor` | royal_silver_gold `#3a3a50` `#8a8ca0` `#ffd860` `#ffffff` | — | 은빛 면갑 투구 위 파란 깃털 장식. |
| `a_wood_round` | 나무 원형방패 | 보조무기 | `off_shield_round` | wood `#3a2410` `#6a4420` `#9a6a36` `#c89a5a` | — | 왼팔에 작은 둥근 나무 방패 (철 테). 정지 상태에서 정면 피해 25% 확률 막기. |
| `a_leather_bracer` | 가죽 팔보호대 | 보조무기 | `acc_bracer` | leather_brown `#2a1608` `#5a3418` `#8a5a2e` `#c08a52` | — | 양 팔뚝에 갈색 가죽 보호대 (버클 2개). |
| `a_ore_amulet` | 광석 부적 | 보조무기 | `acc_amulet` | copper_green `#1a3a30` `#3a7a5a` `#c07a3a` `#a0f0c0` | — | 가슴에 매단 녹청 구리 펜던트, 원석이 박혀 있다. |
| `a_dune_boots` | 사막 질주 장화 | 보조무기 | `acc_boots` | sand_gold `#5a4420` `#a08050` `#d8c090` `#fff0c8` | — | 모래색 긴 장화에 금 버클, 걸을 때 모래 먼지. |
| `a_coral_buckler` | 산호 버클러 | 보조무기 | `off_shield_round` | shell_coral `#6a2a3a` `#c05a6a` `#ff9aa0` `#ffe0d8` | — | 분홍 산호가 박힌 작은 방패. 산호 방패 스킬 퍼펙트 판정 +0.05초. |
| `a_flame_bracer` | 화염 팔찌 | 보조무기 | `acc_bracer` | forge_red `#1a0e0a` `#3a1a10` `#ff3a10` `#fff0c0` | — | 손목의 흑철 팔찌, 붉은 홈이 은은히 빛남. |
| `a_frost_amulet` | 서리 부적 | 보조무기 | `acc_amulet` | ice_pale `#3a5a7a` `#6a9ac0` `#a0d8ff` `#ffffff` | — | 눈송이 모양 얼음 펜던트. |
| `a_royal_kite` | 왕실 문장 방패 | 보조무기 | `off_shield_kite` | royal_silver_gold `#3a3a50` `#8a8ca0` `#ffd860` `#ffffff` | — | 파란 바탕에 금 사자 문장의 연(鳶)형 방패. |
| `w_hunter_machete` | 사냥꾼 마체테 | 무기 | `wpn_machete` | iron `#3a4250` `#6a7686` `#9aa8b8` `#d8e0e8` | `#e0e0e0` `#8a8a8a` | 끝이 넓적한 외날 정글도, 손잡이에 짐승 이빨 장식. 짧고 두꺼운 회색 궤적. |
| `w_harpoon_blade` | 작살검 | 무기 | `wpn_harpoon` | sea_blue `#0a2a5a` `#1a5aa0` `#30a0e0` `#e0f8ff` | `#e0f8ff` `#3a7ab0` | 끝이 미늘 달린 작살촉인 장검, 손잡이 끝에 밧줄 고리. 찌르기(2타) 사거리 +20%. |
| `w_forest_dagger` | 숲의 단검 | 무기 | `wpn_dagger` | forest_leaf `#14301a` `#2e6a34` `#5aa84a` `#c8f0a0` | `#e0ffd0` `#5aa84a` | 나뭇잎 잎맥이 새겨진 짧은 초록 단검, 휘두르면 잎사귀가 흩날린다. |
| `w_boar_tusk` | 돌엄니 송곳검 | 무기 | `wpn_broad` | boar_ivory `#3a2a1a` `#7a5a3a` `#d8c8a0` `#fff8e0` | `#fff8e0` `#a08060` | 거대 멧돼지 엄니를 통째로 깎은 상아빛 칼날, 밑동에 털가죽. |
| `w_spider_fang` | 여왕거미 독니검 | 무기 | `wpn_curved` | spider_violet `#2a1440` `#5a2a8a` `#a070e0` `#e8d8ff` | `#f0e0ff` `#a070e0` | 보랏빛 수정 독니가 휜 날이 된 검, 날 끝에서 독 방울이 떨어진다. |
| `w_sun_sting` | 태양침 독검 | 무기 | `wpn_leaf` | scorpion_amber `#4a2000` `#a05000` `#ffa020` `#fff0b0` | `#fff0b0` `#ff9a20` | 황금 전갈 꼬리 마디로 이은 호박색 날, 끝은 독침. |
| `w_pharaoh_scepter` | 황금가면 왕홀검 | 무기 | `wpn_scepter` | pharaoh_gold `#2a1a40` `#4a3a8a` `#ffc820` `#fff4c0` | `#fff4c0` `#ffc820` | 남색 손잡이 위 금빛 왕홀 머리, 날은 상형문자가 새겨진 짧은 금날. 궤적에 상형문자. |
| `w_kraken_whip` | 크라켄 촉수검 | 무기 | `wpn_whip` | kraken_purple `#200a30` `#4a1a6a` `#9a4ac0` `#e0b0ff` | `#e0b0ff` `#6a2a9a` | 빨판 달린 보라 촉수가 칼날처럼 굳은 채찍검, 돌려베기 범위 +25%. |
| `w_captain_cutlass` | 해적 선장의 커틀러스 | 무기 | `wpn_curved` | pirate_brass `#2a1a10` `#6a4a20` `#c0a050` `#f8f0c0` | `#f8f0c0` `#c0a050` | 놋쇠 바구니 가드의 짧은 곡도, 칼등에 해골 각인. 녹슨 금빛 궤적. |
| `w_hellfire` | 업화의 흑검 | 무기 | `wpn_flame` | hellfire `#100000` `#400a0a` `#ff2a00` `#ffe060` | `#ffe060` `#ff2a00` | 흑기사의 검. 검은 날 전체가 불꽃 모양으로 일렁이며 늘 불이 붙어 있다. |
| `w_storm_spear` | 뇌전 창검 | 무기 | `wpn_spear` | storm_yellow `#1a1a3a` `#3a4a8a` `#ffe040` `#ffffff` | `#ffffff` `#ffe040` | 와이번 뿔로 만든 창날 검, 날 위로 잔번개가 튄다. 노란 지그재그 궤적. |
| `w_shadow_twin` | 그림자 쌍검 | 무기 | `wpn_twin` | shadow_black `#000000` `#14141e` `#3a3a5a` `#9a7aff` | `#9a7aff` `#14141e` | 검은 날 두 자루를 양손에 든다(보조무기 칸 잠김). 보라 잔상이 두 줄로 남는다. |
| `w_dragon_tri` | 삼두 마룡검 | 무기 | `wpn_ornate` | dragon_tri `#0a0a0a` `#5a0a0a` `#3a8ad0` `#b070ff` | `#ff6a20` `#3a8ad0` `#b070ff` | 칼자루에 용머리 셋, 날이 붉은·푸른·보라 세 줄로 갈라져 빛남. 3색 궤적. |
| `w_first_bearer` | 선대의 부러진 검 | 무기 | `wpn_straight_long` | ancient_rust `#2a1a14` `#6a3a2a` `#9a7a6a` `#e8d8c8` | `#e8d8c8` `#7a2020` | 반쯤 부러진 녹슨 장검. 낙인을 지녔던 선대 용사의 검으로, 쥐면 칼날 끝에 붉은 빛의 환영 날이 이어진다. |
| `b_traveler` | 여행자 외투 | 방어구(몸) | `body_coat` | leather_brown `#2a1608` `#5a3418` `#8a5a2e` `#c08a52` | — | 무릎까지 오는 갈색 여행자 외투, 어깨에 둥근 가죽 덧댐. 주머니가 많다. |
| `b_bosun_coat` | 갑판장 코트 | 방어구(몸) | `body_coat` | pirate_brass `#2a1a10` `#6a4a20` `#c0a050` `#f8f0c0` | — | 남색 긴 코트에 놋쇠 단추 두 줄, 옷자락이 바람에 휘날린다. |
| `b_moss_crystal` | 이끼 수정 흉갑 | 방어구(몸) | `body_shell` | moss_crystal `#1a3a20` `#3a6a3a` `#6ad0c0` `#d0fff0` | — | 초록 이끼 위로 하늘색 수정 결정이 돋아난 흉갑. |
| `b_crab_shell` | 거대게 껍질 갑옷 | 방어구(몸) | `body_shell` | crab_red `#4a0a0a` `#a02a1a` `#ff7a5a` `#ffd8c8` | — | 붉은 게 껍질 판을 이어 붙인 갑옷, 어깨에 작은 가시. |
| `b_ghost_coat` | 유령 선장의 코트 | 방어구(몸) | `body_coat` | ghost_teal `#0a2a2a` `#2a5a5a` `#7ad0c0` `#e0fff8` | — | 반투명한 청록 코트, 옷자락 끝이 연기처럼 흩어진다. |
| `b_wyvern_scale` | 뇌전 비늘 갑옷 | 방어구(몸) | `body_scale` | wyvern_blue `#0a1a3a` `#1a4a8a` `#4aa0ff` `#e0f4ff` | — | 짙은 청색 비늘 갑옷, 비늘 틈으로 잔번개가 흐른다. |
| `b_shadow_garb` | 그림자 잠행복 | 방어구(몸) | `body_light` | shadow_black `#000000` `#14141e` `#3a3a5a` `#9a7aff` | — | 몸에 붙는 검은 잠행복과 보라 띠, 움직일 때 윤곽이 흐려진다. |
| `b_dragon_scale` | 마룡 비늘 갑옷 | 방어구(몸) | `body_scale` | dragon_tri `#0a0a0a` `#5a0a0a` `#3a8ad0` `#b070ff` | — | 검붉은 비늘 갑옷, 가슴에 세 갈래 용 문양이 붉게·푸르게·보랏빛으로 맥동. |
| `h_iron_mask` | 용병 쇠가면 | 방어구(투구) | `head_mask` | anchor_steel `#2a3038` `#4a5664` `#6a7a8a` `#f0f0f0` | — | 얼굴 아래 절반을 가리는 투박한 쇠가면, 이마에 긁힌 자국. |
| `h_desert_turban` | 사막의 터번 | 방어구(투구) | `head_turban` | sand_gold `#5a4420` `#a08050` `#d8c090` `#fff0c8` | — | 모래색 긴 터번, 얼굴 가리개가 달려 있다. |
| `h_pharaoh_mask` | 황금 가면 | 방어구(투구) | `head_mask` | pharaoh_gold `#2a1a40` `#4a3a8a` `#ffc820` `#fff4c0` | — | 미라왕의 황금 가면을 머리 위로 올려 쓴다. 눈구멍이 푸르게 빛남. |
| `h_witch_hat` | 화염 마녀의 모자 | 방어구(투구) | `head_witch` | witch_crimson `#1a0a14` `#5a0a2a` `#c02a4a` `#ffb0a0` | — | 끝이 꺾인 진홍색 뾰족 모자, 챙에 불씨가 맴돈다. |
| `h_griffon_helm` | 그리폰 깃털 투구 | 방어구(투구) | `head_plume` | storm_yellow `#1a1a3a` `#3a4a8a` `#ffe040` `#ffffff` | — | 금빛 날개 모양 깃털이 양옆으로 뻗은 투구. |
| `h_void_crown` | 공허의 관 | 방어구(투구) | `head_crown` | void_purple `#0a0014` `#2a0a4a` `#7a2ad0` `#e0c0ff` | — | 머리 위에 떠 있는 보라 고리 관, 작은 시계 바늘이 돈다. |
| `o_sling` | 투석끈 | 보조무기 | `off_throw_sling` | leather_brown `#2a1608` `#5a3418` `#8a5a2e` `#c08a52` | — | 허리에 감은 가죽 투석끈과 돌 주머니. 보조 키(Shift)로 돌 1발. |
| `o_throw_knife` | 투척 단검 묶음 | 보조무기 | `off_throw_knife` | iron `#3a4250` `#6a7686` `#9aa8b8` `#d8e0e8` | — | 허벅지 띠에 꽂힌 단검 5자루. 보조 키로 직선 투척. |
| `o_ore_pick` | 투척 곡괭이 | 보조무기 | `off_throw_pick` | dark_iron_copper `#1a1a20` `#3a3a44` `#a86a3a` `#f0d0b0` | — | 등에 멘 작은 곡괭이 2자루. 포물선으로 던지면 금 간 벽도 부순다. |
| `o_chakram` | 사막 차크람 | 보조무기 | `off_throw_ring` | desert_gold `#5a3a08` `#a0700a` `#e0b030` `#fff0b0` | — | 금빛 원반 칼날. 던지면 부메랑처럼 돌아온다. |
| `o_shell_orb` | 조개 오브 | 보조무기 | `off_orb` | shell_coral `#6a2a3a` `#c05a6a` `#ff9aa0` `#ffe0d8` | — | 어깨 옆에 떠다니는 분홍 진주 조개. 2초마다 가까운 적에게 물방울 탄. |
| `o_forge_tower` | 흑철 대방패 | 보조무기 | `off_shield_tower` | black_iron_red `#0a0a0e` `#24242c` `#4a4a56` `#c02020` | — | 몸을 거의 가리는 검은 사각 대방패, 가운데 붉은 용광로 문양. 이동 -5%. |
| `o_ember_orb` | 불씨 오브 | 보조무기 | `off_orb` | lava_core `#1a0800` `#5a1a00` `#ff6a00` `#ffff80` | — | 주황 불씨가 소용돌이치는 구슬, 1.5초마다 화염탄. |
| `o_ice_javelin` | 얼음 투창 | 보조무기 | `off_throw_javelin` | ice_pale `#3a5a7a` `#6a9ac0` `#a0d8ff` `#ffffff` | — | 등에 꽂힌 얼음 투창 3자루, 맞은 적 둔화. |
| `o_knight_gauntlet` | 기사 건틀릿 | 보조무기 | `acc_bracer` | royal_silver_gold `#3a3a50` `#8a8ca0` `#ffd860` `#ffffff` | — | 팔꿈치까지 오는 은빛 판금 건틀릿, 손등에 금 사자. |
| `o_holy_orb` | 성광 오브 | 보조무기 | `off_orb` | holy_white `#6a6a5a` `#c0c0b0` `#fff8e0` `#ffffff` | — | 순백의 빛 구슬. 자동 사격 + 어둠 속성 피해 2배. |
| `o_wasp_dart` | 여왕벌 독침 다트 | 보조무기 | `off_throw_knife` | scorpion_amber `#4a2000` `#a05000` `#ffa020` `#fff0b0` | — | 노란 독침 다트 6개가 꽂힌 벌집 모양 주머니. |
| `o_bat_ring` | 흡혈 박쥐왕의 반지 | 보조무기 | `acc_ring` | blood_red `#1a0000` `#4a0000` `#a00010` `#ff6060` | — | 붉은 박쥐 날개 모양 반지, 손을 휘두르면 붉은 반짝임. |
| `o_moss_shield` | 이끼 수정 방패 | 보조무기 | `off_shield_round` | moss_crystal `#1a3a20` `#3a6a3a` `#6ad0c0` `#d0fff0` | — | 이끼 낀 둥근 돌 방패에 수정 세 개. |
| `o_worm_fang` | 대지렁이 이빨 부메랑 | 보조무기 | `off_throw_ring` | boar_ivory `#3a2a1a` `#7a5a3a` `#d8c8a0` `#fff8e0` | — | 갈고리 모양 상아빛 이빨 부메랑. |
| `o_golden_scarab` | 황금 풍뎅이 부적 | 보조무기 | `acc_amulet` | scarab_gold `#0a2a2a` `#1a6a5a` `#e0c030` `#fff8b0` | — | 청록 날개의 황금 풍뎅이 펜던트. |
| `o_shark_fin` | 백상어 지느러미 방패 | 보조무기 | `off_shield_kite` | shark_grey `#1a2a3a` `#4a5a6a` `#9aaabb` `#f0f4f8` | — | 회색 상어 지느러미 모양 방패, 가장자리가 톱날. |
| `o_crab_claw` | 거대게 집게 방패 | 보조무기 | `off_shield_round` | crab_red `#4a0a0a` `#a02a1a` `#ff7a5a` `#ffd8c8` | — | 붉은 게 집게를 통째로 방패로 쓴다. 막을 때 집게가 딸깍. |
| `o_lava_core` | 용암 거인의 핵 | 보조무기 | `off_orb` | lava_core `#1a0800` `#5a1a00` `#ff6a00` `#ffff80` | — | 주먹만 한 용암 덩어리가 어깨 위에서 부글거린다. |
| `o_yeti_bracer` | 설인 털 팔보호대 | 보조무기 | `acc_bracer` | yeti_white `#5a5a6a` `#a0a0b0` `#e8e8f0` `#ffffff` | — | 두툼한 흰 털 팔보호대, 손등에 얼음 발톱. |
| `o_shadow_kunai` | 그림자 표창 | 보조무기 | `off_throw_star` | shadow_black `#000000` `#14141e` `#3a3a5a` `#9a7aff` | — | 허리띠에 꽂힌 검보라 표창 8개, 던지면 3갈래로 갈라진다. |
| `o_void_ring` | 공허의 반지 | 보조무기 | `acc_ring` | void_purple `#0a0014` `#2a0a4a` `#7a2ad0` `#e0c0ff` | — | 빛을 빨아들이는 검은 반지, 보라 테두리. |
| `o_dragon_eye` | 마룡의 눈 | 보조무기 | `off_orb` | dragon_tri `#0a0a0a` `#5a0a0a` `#3a8ad0` `#b070ff` | — | 세로 동공의 용 눈알 구슬. 노려본 적에게 3색 광선. |

## 외형상점 아이템 (능력치 없음)

| 아이템 | 종류 | 레이어 | 팔레트 | 외형 | 비고 |
|---|---|---|---|---|---|
| 하늘색 망토 | cape | `cape` | `#1e4a8a` `#3a7ad0` `#7ab8ff` `#d0ecff` | 맑은 하늘색 망토. |  |
| 숲빛 망토 | cape | `cape` | `#1a3a1a` `#2e6a2e` `#4ea04e` `#a0e090` | 짙은 초록 숲빛 망토. |  |
| 밀짚 농부 의상 | outfit | `armor_skin` | `#4a3a20` `#8a7040` `#c8a860` `#f0e0a0` | 멜빵바지와 밀짚모자 세트 (투구 칸이 비면 모자 표시). |  |
| 빨간 머리끈 | head | `head_deco` | `#6a0a10` `#c02030` `#ff5060` `#ffb0b8` | 뒷머리에 묶은 짧은 빨간 끈. |  |
| 강물 쪽빛 망토 | cape | `cape` | `#0a2a4a` `#1a4a7a` `#3a7ab0` `#8ac0e8` | 쪽빛 염색, 끝단이 물결 무늬. |  |
| 뱃사공 밀짚모자 | head | `head_deco` | `#5a4420` `#a08040` `#d8b860` `#fff0b0` | 넓은 챙의 밀짚모자. |  |
| 낚시꾼 조끼 | outfit | `armor_skin` | `#2a3a2a` `#4a6a4a` `#7a9a6a` `#c0d8a8` | 주머니 많은 녹색 조끼와 장화. |  |
| 물결 궤적 | trail | `trail` | `#bff4ff` `#5fd0ff` | 베기 궤적이 물보라처럼 흩어짐. |  |
| 견습 광부 두건 | head | `head_deco` | `#3a2a10` `#6a4a20` `#a07030` `#e0b060` | 흙 묻은 갈색 두건. |  |
| 수정 단추 망토 장식 | cape | `cape_deco` | `#0e4a5a` `#2a9aaa` `#5ee0e0` `#e0ffff` | 망토 목깃에 반짝이는 수정 단추 두 개. |  |
| 보랏빛 망토 | cape | `cape` | `#2a0e3a` `#4e1e6a` `#8040a8` `#c890e8` | 신비한 보랏빛 망토. |  |
| 광부 작업복 | outfit | `armor_skin` | `#2a2a2a` `#5a4a30` `#8a7040` `#c0a060` | 그을린 작업복과 무릎 보호대. |  |
| 노을 비단 망토 | cape | `cape` | `#5a1a10` `#b0401a` `#ff8a30` `#ffd080` | 바람에 날리면 노을빛 그라데이션. |  |
| 별빛 터번 | head | `head_deco` | `#1a1a4a` `#3a3a8a` `#ffffff` `#ffe080` | 남색 터번에 작은 별 자수. |  |
| 사막 유목민 의상 | outfit | `armor_skin` | `#5a4420` `#a08050` `#e0c890` `#fff4d8` | 헐렁한 모래색 겉옷과 허리띠. |  |
| 황금 궤적 | trail | `trail` | `#fff0b0` `#e0b030` | 금가루가 흩날리는 궤적. |  |
| 인어 비늘 망토 | cape | `cape` | `#0a3a4a` `#1a7a8a` `#40c0c0` `#b0fff0` | 청록 비늘 무늬가 반짝이는 망토. |  |
| 해녀 물안경 | head | `head_deco` | `#2a2a2a` `#4a4a4a` `#80d0ff` `#ffffff` | 이마에 걸친 둥근 물안경. |  |
| 선원 줄무늬 옷 | outfit | `armor_skin` | `#0a1a3a` `#1a3a7a` `#ffffff` `#e0e8ff` | 흰·남색 줄무늬 셔츠와 반바지. |  |
| 등대지기 망토 | cape | `cape` | `#3a2a0a` `#8a6a1a` `#e0c040` `#fff4a0` | 노란 방수 망토. |  |
| 불꽃 무늬 망토 | cape | `cape` | `#3a0a0a` `#a01a0a` `#ff6a10` `#ffd040` | 끝단이 불꽃 모양으로 갈라진 망토. |  |
| 불사조 깃털 머리장식 | head | `head_deco` | `#6a1a0a` `#e04010` `#ffa020` `#fff0a0` | 귀 옆에 꽂은 타오르는 깃털. |  |
| 대장장이 앞치마 | outfit | `armor_skin` | `#1a1008` `#4a3018` `#8a5a30` `#c08a52` | 두꺼운 가죽 앞치마와 걷어 올린 소매. |  |
| 불씨 궤적 | trail | `trail` | `#ffd0a0` `#ff6a20` | 궤적 끝에 불씨가 튀는 효과. |  |
| 눈사람 목도리 | head | `neck_deco` | `#6a0a10` `#c02030` `#ffffff` `#ffd0d0` | 빨강·흰 줄무늬 목도리. |  |
| 서리 망토 | cape | `cape` | `#3a5a7a` `#6a9ac0` `#c0e8ff` `#ffffff` | 서리 결정 무늬의 창백한 망토. |  |
| 털 겨울옷 | outfit | `armor_skin` | `#3a2a1a` `#6a4a2a` `#d8ccb8` `#ffffff` | 털 달린 갈색 겨울 코트. |  |
| 서리 궤적 | trail | `trail` | `#ffffff` `#a0d8ff` | 궤적 자리에 잠깐 서리가 맺힘. |  |
| 왕실 청금 망토 | cape | `cape` | `#0a1a4a` `#1a3a9a` `#3a6ae0` `#ffd860` | 남색 바탕에 금 테두리 왕실 망토. |  |
| 귀족 예복 | outfit | `armor_skin` | `#1a0a2a` `#4a1a6a` `#8a4ac0` `#ffd860` | 보라 예복과 금 단추. |  |
| 흑금 망토 | cape | `cape` | `#0a0a0a` `#1a1a1a` `#3a3a3a` `#ffd860` | 검은 망토에 금실 자수. |  |
| 삼룡 무지개 궤적 | trail | `trail` | `#ff4060` `#6aa8ff` `#ffd060` | 빨강·파랑·금 삼색 궤적 (삼룡의 각성 오마주). |  |
| 물방울 무늬 망토 | cape | `cape` | `#1e3a6a` `#3a6ab0` `#9ad8ff` `#ffffff` | 하늘색 바탕에 흰 물방울 무늬. (A6 보상) | 퀘스트 보상 전용 |
| 낙타 방울 망토 장식 | cape_deco | `cape_deco` | `#5a3a08` `#a0700a` `#e0b030` `#fff0b0` | 망토 끝에 달린 작은 금방울, 걸을 때 딸랑. (G2 보상) | 퀘스트 보상 전용 |
| 모래쥐 스카프 | neck_deco | `neck_deco` | `#3a2a1a` `#7a5a3a` `#c09060` `#f0d8b0` | 낡았지만 멋스러운 모래색 스카프. (G4 보상) | 퀘스트 보상 전용 |
| 몰락한 기사의 검은 망토 | cape | `cape` | `#0a0a10` `#1a1a24` `#3a3a4a` `#8a1a1a` | 찢어진 끝단, 안감은 핏빛. (E4 보상) | 퀘스트 보상 전용 |
| 서리 성녀 망토 | cape | `cape` | `#4a6a8a` `#8ab0d0` `#e0f4ff` `#ffffff` | 은은히 빛나는 순백 망토. (C6 보상) | 퀘스트 보상 전용 |
| 왕국 기사단 망토 | cape | `cape` | `#0a1a4a` `#1a3a8a` `#ffffff` `#ffd860` | 기사단 문장이 수놓인 남·백 망토. (D1 보상) | 퀘스트 보상 전용 |
| 공주의 리본 장식 | head | `head_deco` | `#6a1a4a` `#c0408a` `#ff90c8` `#ffe0f0` | 분홍 리본. (D2 보상) | 퀘스트 보상 전용 |
| 대성당 순백 의상 | outfit | `armor_skin` | `#8a8a9a` `#c8c8d8` `#f4f4ff` `#ffd860` | 금 자수의 흰 순례자 의상. (D6 보상) | 퀘스트 보상 전용 |
