# 그록 아이템 아이콘 → 정본 아이템 짝 (2026-10-25, 2번방)

- 원본: `part1~7.png` (그록, 10-24). 칸마다 잘라 이름 글자·바탕을 뺀 투명 PNG = `cut/<id>.png` (그림체 그대로, 섞지 않음).
- 게임용: `test128/assets/icons/grok/<id>_32.png`, `_64.png`, `_128.webp`. 게임 아이템 표에 `"gi":1` 이 있으면 이 그림을 쓴다 (가방·상점·퀵칸·줍기 알림).
- id: 14개는 claude/gear-slots 정본 장비 id 그대로, `potion` = 게임의 회복약(평범한 회복 물약). 나머지 116개는 새로 붙인 제안 id (아이템을 게임에 넣을 때 이 id를 쓴다).
- 그림 131개 = 정본 문서(MASTER_PLAN_아이템배치) 이름과 모두 짝지어짐 → **짝 없는 그림 0개**.
- **그림 없는 정본 아이템**: 「왕실 특수 천」(리네트가 건네는 천, 카일라에게 전달). 정본 제목은 151개라고 하지만 문서에 이름이 나오는 아이템은 132개뿐이라, 나머지 19개는 이름이 아직 없다(스토리방 확인 필요).
- 같은 물건 다른 이름(그림 하나로 씀): 「왕실 천」=왕실 특수 천, 「불타는 외투」=불타는 귀족의 외투, 「자드의 나선 열쇠」=잊혀진 나선 열쇠(추정).

| 이름 | id | 종류 | 게임에 있음 | 원본 칸 |
|---|---|---|---|---|
| 연금술사의 수은검 | `w_alch_mercury` | 무기 |  | part6.png 1줄 4칸 |
| 아라크네의 붉은 척추검 | `w_ara_spine` | 무기 | ✔ | part5.png 1줄 2칸 |
| 숨겨진 요람의 목검 | `w_cradle_wood` | 무기 |  | part7.png 1줄 1칸 |
| 망각된 집행관의 참수검 | `w_executioner` | 무기 |  | part7.png 1줄 2칸 |
| 1회차 루프의 태초검 | `w_first_loop` | 무기 |  | part6.png 2줄 3칸 |
| 근위대의 꺾인 창검 | `w_guard_spear` | 무기 |  | part6.png 1줄 3칸 |
| 초침을 부수는 대검 | `w_hand_breaker` | 무기 |  | part6.png 2줄 1칸 |
| 저주받은 이단의 대검 | `w_heretic_great` | 무기 |  | part6.png 1줄 1칸 |
| 껍데기들의 거울검 | `w_husk_mirror` | 무기 |  | part6.png 1줄 2칸 |
| 철혈의 부러진 대검 | `w_iron_broken` | 무기 |  | part5.png 1줄 3칸 |
| 박제된 군주의 대검 | `w_king_great` | 무기 |  | part6.png 2줄 2칸 |
| 닳아빠진 루프의 장검 | `w_loop_long` | 무기 | ✔ | part5.png 1줄 1칸 |
| 귀족의 그을린 세검 | `w_noble_rapier` | 무기 |  | part5.png 1줄 5칸 |
| 맹세의 흑연검 | `w_oath_ink` | 무기 |  | part5.png 1줄 4칸 |
| 사멸의 진검 | `w_true_death` | 무기 |  | part6.png 2줄 4칸 |
| 태초의 잿빛 흉갑 | `a_first_ash` | 갑옷 |  | part1.png 1줄 1칸 |
| 마모 저항 방어구 | `a_wear_guard` | 갑옷 |  | part1.png 1줄 2칸 |
| 연금술사의 석회 망토 | `c_alch_lime` | 망토 |  | part7.png 2줄 4칸 |
| 아라크네의 실크 망토 | `c_ara_silk` | 망토 | ✔ | part5.png 2줄 2칸 |
| 대서고의 양피지 망토 | `c_archive_parch` | 망토 |  | part5.png 2줄 4칸 |
| 닳아빠진 잿빛 망토 | `c_ash_cloak` | 망토 | ✔ | part5.png 2줄 1칸 |
| 불타는 귀족의 외투 | `c_burning_noble` | 망토 |  | part5.png 2줄 5칸 |
| 시계태엽의 황동 망토 | `c_clock_brass` | 망토 |  | part6.png 3줄 2칸 |
| 태초의 잿빛 망토 | `c_first_ash` | 망토 |  | part7.png 2줄 1칸 |
| 이안의 붉은 소년 망토 | `c_ian_red` | 망토 |  | part6.png 3줄 4칸 |
| 철혈기사의 무쇠망토 | `c_iron_knight` | 망토 |  | part5.png 2줄 3칸 |
| 박제된 군주의 망토 | `c_king` | 망토 |  | part6.png 3줄 3칸 |
| 오스왈드의 철염주 망토 | `c_oswald_rosary` | 망토 |  | part6.png 3줄 1칸 |
| 그림자 도둑의 망토 | `c_shadow_thief` | 망토 |  | part1.png 1줄 3칸 |
| 수장고의 뼈 망토 | `c_vault_bone` | 망토 |  | part7.png 2줄 3칸 |
| 기록관의 렌즈 반지 | `r_archivist_lens` | 반지 |  | part6.png 5줄 2칸 |
| 잿가루 낀 철환 | `r_ash_iron` | 반지 | ✔ | part5.png 3줄 1칸 |
| 피 묻은 바늘 반지 | `r_blood_needle` | 반지 | ✔ | part7.png 3줄 3칸 |
| 부서진 톱니 반지 | `r_broken_cog` | 반지 |  | part5.png 3줄 2칸 |
| 멍든 수은 반지 | `r_bruise_mercury` | 반지 |  | part6.png 4줄 3칸 |
| 불타는 낙인 반지 | `r_burning_brand` | 반지 |  | part7.png 4줄 1칸 |
| 파열된 철갑 반지 | `r_burst_plate` | 반지 |  | part7.png 4줄 4칸 |
| 망자의 눈물 반지 | `r_dead_tear` | 반지 |  | part7.png 3줄 4칸 |
| 사멸의 핵철 반지 | `r_death_core` | 반지 |  | part4.png 4줄 4칸 |
| 재앙의 흑요석 반지 | `r_doom_obsidian` | 반지 |  | part7.png 3줄 1칸 |
| 처형인의 무쇠 반지 | `r_executioner` | 반지 |  | part7.png 3줄 2칸 |
| 태초의 공허 반지 | `r_first_void` | 반지 |  | part4.png 4줄 3칸 |
| 묘지의 뼛조각 반지 | `r_grave_bone` | 반지 |  | part6.png 4줄 2칸 |
| 탐욕의 루비 반지 | `r_greed_ruby` | 반지 |  | part6.png 5줄 1칸 |
| 탐욕의 무게 반지 | `r_greed_weight` | 반지 |  | part3.png 4줄 1칸 |
| 버려진 껍데기 반지 | `r_husk` | 반지 |  | part4.png 4줄 1칸 |
| 타임키퍼의 부러진 반쪽 반지 | `r_keeper_half` | 반지 |  | part6.png 4줄 1칸 |
| 광기의 톱니 반지 | `r_mad_cog` | 반지 |  | part7.png 5줄 1칸 |
| 거울 파편 반지 | `r_mirror_shard` | 반지 |  | part7.png 4줄 2칸 |
| 낡은 은반지 | `r_old_silver` | 반지 | ✔ | part5.png 3줄 5칸 |
| 붉은 실타래 반지 | `r_red_thread` | 반지 | ✔ | part4.png 4줄 2칸 |
| 도굴꾼의 그림자 반지 | `r_robber_shadow` | 반지 |  | part6.png 5줄 3칸 |
| 수색가의 낡은 반지 | `r_seeker_old` | 반지 | ✔ | part7.png 5줄 4칸 |
| 석화된 해골 반지 | `r_stone_skull` | 반지 |  | part5.png 3줄 4칸 |
| 멈춰버린 모래시계 반지 | `r_stopped_glass` | 반지 |  | part6.png 5줄 4칸 |
| 조율사의 귀마개 반지 | `r_tuner_plug` | 반지 |  | part7.png 5줄 2칸 |
| 공허의 핏빛 반지 | `r_void_blood` | 반지 |  | part5.png 3줄 3칸 |
| 공허의 소용돌이 반지 | `r_void_swirl` | 반지 |  | part7.png 4줄 3칸 |
| 방랑자의 징검다리 반지 | `r_wander_step` | 반지 | ✔ | part7.png 5줄 3칸 |
| 철사 감긴 묵주반지 | `r_wire_rosary` | 반지 |  | part6.png 4줄 4칸 |
| 닳아버린 결혼반지 | `r_worn_wedding` | 반지 |  | part3.png 1줄 1칸 |
| 잿빛 화염병 | `ash_firebomb` | 소모품 | ✔ | part1.png 3줄 4칸 |
| 잿빛 정화제 | `ash_purifier` | 소모품 | ✔ | part2.png 5줄 3칸 |
| 검은 이끼 물약 | `black_moss_potion` | 소모품 |  | part2.png 4줄 1칸 |
| 안개 진화 물약 | `mist_douse` | 소모품 |  | part3.png 1줄 4칸 |
| 평범한 회복 물약 | `potion` | 소모품 | ✔ | part1.png 4줄 1칸 |
| 석화된 연금술사의 물약병 | `stone_alch_vial` | 소모품 |  | part4.png 5줄 1칸 |
| 던지기용 투척 나이프 | `throw_knife` | 소모품 | ✔ | part1.png 4줄 2칸 |
| 특수 숫돌 | `whetstone_sp` | 소모품 | ✔ | part4.png 5줄 2칸 |
| 연금술 조제도구 | `k_alch_kit` | 열쇠·퀘스트 |  | part2.png 2줄 4칸 |
| 최초의 배교자 심장 | `k_apostate_heart` | 열쇠·퀘스트 |  | part3.png 2줄 2칸 |
| 피 묻은 기록관의 안경 | `k_archivist_glasses` | 열쇠·퀘스트 |  | part4.png 3줄 3칸 |
| 잿빛 장비 수리 망치 | `k_ash_hammer` | 열쇠·퀘스트 |  | part1.png 4줄 4칸 |
| 잿빛 이끼 | `k_ash_moss` | 열쇠·퀘스트 |  | part3.png 3줄 4칸 |
| 닳지 않는 잿빛유물 | `k_ash_relic` | 열쇠·퀘스트 |  | part2.png 1줄 1칸 |
| 가시 박힌 철사 | `k_barbed_wire` | 열쇠·퀘스트 |  | part3.png 3줄 1칸 |
| 눈먼 자의 귀마개 | `k_blind_plugs` | 열쇠·퀘스트 |  | part3.png 4줄 2칸 |
| 부러진 검의 날 | `k_broken_blade` | 열쇠·퀘스트 |  | part2.png 3줄 1칸 |
| 부러진 검병 | `k_broken_hilt` | 열쇠·퀘스트 |  | part3.png 5줄 3칸 |
| 암호화된 금서 | `k_cipher_book` | 열쇠·퀘스트 |  | part1.png 2줄 3칸 |
| 시계태엽 부품 | `k_clock_parts` | 열쇠·퀘스트 |  | part2.png 1줄 2칸 |
| 사멸의 파편 | `k_death_shard` | 열쇠·퀘스트 |  | part3.png 4줄 4칸 |
| 가문의 마지막 맹세 | `k_family_oath` | 열쇠·퀘스트 |  | part2.png 5줄 4칸 |
| 굳어진 연회용 칼 | `k_feast_knife` | 열쇠·퀘스트 |  | part2.png 5줄 1칸 |
| 성문 기어 손잡이 | `k_gate_gear` | 열쇠·퀘스트 |  | part1.png 2줄 2칸 |
| 황금 톱니바퀴 | `k_gold_cog` | 열쇠·퀘스트 |  | part4.png 2줄 1칸 |
| 부러진 근위대의 창 | `k_guard_spear_broken` | 열쇠·퀘스트 |  | part4.png 3줄 1칸 |
| 이안의 붉은 가죽 공 | `k_ian_ball` | 열쇠·퀘스트 |  | part1.png 3줄 1칸 |
| 카일라의 덧대기 키트 | `k_kaila_kit` | 열쇠·퀘스트 |  | part1.png 3줄 3칸 |
| 타임키퍼의 해체 공구 | `k_keeper_tools` | 열쇠·퀘스트 |  | part4.png 3줄 2칸 |
| 기사의 부서진 투구 | `k_knight_helm` | 열쇠·퀘스트 |  | part2.png 2줄 1칸 |
| 붉은 마지막 기록 실타래 | `k_last_thread` | 열쇠·퀘스트 |  | part7.png 1줄 3칸 |
| 가죽 팔토시 | `k_leather_bracer` | 열쇠·퀘스트 |  | part2.png 3줄 2칸 |
| 석회화된 유골 | `k_lime_bones` | 열쇠·퀘스트 |  | part2.png 2줄 3칸 |
| 루프의 잔해 파편 | `k_loop_shard` | 열쇠·퀘스트 |  | part4.png 1줄 4칸 |
| 잊혀진 양피지 | `k_lost_parch` | 열쇠·퀘스트 |  | part2.png 1줄 3칸 |
| 루카의 현 끊어진 비파 | `k_luca_lute` | 열쇠·퀘스트 |  | part1.png 3줄 2칸 |
| 녹은 펜던트 | `k_melt_pendant` | 열쇠·퀘스트 |  | part3.png 1줄 2칸 |
| 수은 정화통 | `k_mercury_can` | 열쇠·퀘스트 |  | part3.png 5줄 1칸 |
| 수은 필터 | `k_mercury_filter` | 열쇠·퀘스트 |  | part7.png 1줄 4칸 |
| 연금술용 수은관 | `k_mercury_tube` | 열쇠·퀘스트 |  | part2.png 4줄 4칸 |
| 닳아빠진 바늘 상자 | `k_needle_box` | 열쇠·퀘스트 |  | part3.png 5줄 2칸 |
| 불탄 귀족의 외투 조각 | `k_noble_scrap` | 열쇠·퀘스트 |  | part3.png 3줄 2칸 |
| 꺾인 맹세의 검병 | `k_oath_grip` | 열쇠·퀘스트 |  | part4.png 2줄 2칸 |
| 부서진 맹세의 칼자루 | `k_oath_hilt` | 열쇠·퀘스트 |  | part3.png 2줄 3칸 |
| 낡은 무쇠 망치 | `k_old_iron_hammer` | 열쇠·퀘스트 |  | part2.png 3줄 3칸 |
| 낡은 열쇠 꾸러미 | `k_old_keys` | 열쇠·퀘스트 |  | part2.png 2줄 2칸 |
| 정화의 송진 | `k_pure_resin` | 열쇠·퀘스트 |  | part4.png 2줄 4칸 |
| 붉은 인광석 | `k_red_glowstone` | 열쇠·퀘스트 |  | part3.png 5줄 4칸 |
| 붉은 목도리 | `k_red_scarf` | 열쇠·퀘스트 |  | part4.png 1줄 1칸 |
| 왕가의 열쇠 | `k_royal_key` | 열쇠·퀘스트 |  | part1.png 2줄 1칸 |
| 녹슨 해체톱 | `k_rust_saw` | 열쇠·퀘스트 |  | part2.png 4줄 2칸 |
| 녹슨 군번줄 | `k_rust_tags` | 열쇠·퀘스트 |  | part4.png 1줄 2칸 |
| 시간이 봉인된 기름 | `k_sealed_oil` | 열쇠·퀘스트 |  | part4.png 2줄 3칸 |
| 두꺼운 흡음 천 | `k_sound_cloth` | 열쇠·퀘스트 |  | part1.png 2줄 4칸 |
| 잊혀진 나선 열쇠 | `k_spiral_key` | 열쇠·퀘스트 |  | part3.png 1줄 3칸 |
| 굳어버린 안경테 | `k_stiff_glasses` | 열쇠·퀘스트 |  | part3.png 3줄 3칸 |
| 영혼이 꿰매진 인형 | `k_stitched_doll` | 열쇠·퀘스트 |  | part4.png 5줄 3칸 |
| 시간이 굳은 핏방울 | `k_time_blood` | 열쇠·퀘스트 |  | part4.png 5줄 4칸 |
| 시간의 양피지 | `k_time_parch` | 열쇠·퀘스트 |  | part4.png 1줄 3칸 |
| 시간이 굳은 모래 | `k_time_sand` | 열쇠·퀘스트 |  | part3.png 4줄 3칸 |
| 찢어진 염주 | `k_torn_beads` | 열쇠·퀘스트 |  | part2.png 3줄 4칸 |
| 조율사의 시약병 | `k_tuner_vial` | 열쇠·퀘스트 |  | part4.png 3줄 4칸 |
| 재가 되지 못한 편지 | `k_unburnt_letter` | 열쇠·퀘스트 |  | part3.png 2줄 1칸 |
| 수장고의 낡은 사슬 | `k_vault_chain` | 열쇠·퀘스트 |  | part2.png 5줄 2칸 |
| 공허의 핏방울 | `k_void_drop` | 열쇠·퀘스트 |  | part2.png 1줄 4칸 |
| 순백의 관현 | `k_white_pipe` | 열쇠·퀘스트 |  | part3.png 2줄 4칸 |
| 투박한 나무 의수 | `k_wood_arm` | 열쇠·퀘스트 |  | part1.png 1줄 4칸 |
| 닳아버린 의복 조각 | `k_worn_cloth` | 열쇠·퀘스트 |  | part7.png 2줄 2칸 |
| 닳아빠진 장갑 | `k_worn_gloves` | 열쇠·퀘스트 |  | part2.png 4줄 3칸 |
| 닳은 등불 | `k_worn_lamp` | 열쇠·퀘스트 |  | part1.png 4줄 3칸 |
