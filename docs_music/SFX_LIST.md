# SFX 목록

## A. 게임에 이미 있는 SFX (사용 중)
`town/index.html` 의 `SFX_DATA` (base64 ogg 내장), `SFX.play()` 로 호출 (index.html, world.js). 수정하지 않음.

| key | 설명 | 상태 |
|---|---|---|
| `swing_light` | 검 약공격 휘두르기 | 사용 중 |
| `swing_heavy` | 강공격/피니시 휘두르기 | 사용 중 |
| `hit_light` | 일반 타격 | 사용 중 |
| `hit_heavy` | 강타격 | 사용 중 |
| `hit_crit` | 크리티컬 | 사용 중 |
| `kill` | 적 처치 | 사용 중 |
| `spin_dark` | 타이틀 회전베기(어둠) | 사용 중 |
| `wave` | 검기/웨이브 | 사용 중 |
| `ult_cutin` | 궁극기 컷인 | 사용 중 |
| `ult_boom` | 궁극기 폭발 | 사용 중 |

## B. 빠진 SFX → 초안 제작 (`docs_music/sfx_draft/`)
느낌 목표: 이스 VIII 같은 짧고 펀치 있는 타격감(빠른 어택, 저역 바디 + 고역 크랙, 짧은 꼬리). **초안**은 box 에서 numpy 로 합성한 자작음 (CC0 상당, 외부 샘플 없음) — 실제 게임 투입 전 교체/다듬기 권장.

| file | 한국어 설명 | 길이(초) | 느낌 | 우선순위 | 출처 | 라이선스 |
|---|---|---|---|---|---|---|
| `sfx_draft/swing_sword_1.ogg` | 검 1타 휘두르기 | 0.16 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/swing_sword_2.ogg` | 검 2타 휘두르기 | 0.18 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/swing_sword_3.ogg` | 검 3타(피니시) 휘두르기 | 0.3 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/swing_spear.ogg` | 창 휘두르기/찌르기 | 0.2 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/swing_axe.ogg` | 도끼 무거운 휘두르기 | 0.32 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/hit_normal.ogg` | 일반 타격 | 0.18 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/hit_finisher.ogg` | 피니시 타격 (묵직) | 0.4 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/hit_critical.ogg` | 크리티컬 타격 (금속 링) | 0.4 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/combo_hit.ogg` | 콤보 카운트 틱 | 0.08 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/dash_attack.ogg` | 대시 공격 | 0.35 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/charge_stage1.ogg` | 차지 1단계 모으기 | 0.6 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/charge_stage2.ogg` | 차지 2단계 도달 | 0.4 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/charge_release.ogg` | 차지 해방 | 0.5 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/dodge_afterimage.ogg` | 잔상 회피 | 0.22 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/just_dodge.ogg` | 저스트 회피 성공 | 0.6 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/footstep.ogg` | 달리기 발소리 | 0.06 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skid.ogg` | 급정지 미끄러짐 | 0.3 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/player_hurt.ogg` | 플레이어 피격 | 0.25 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/level_up.ogg` | 레벨 업 | 0.88 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/ult_raikou.ogg` | 궁극기 천광낙뢰 | 1.2 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/ult_demon_descent.ogg` | 궁극기 멸계강림 | 1.6 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/ult_ice_sword.ogg` | 궁극기 찬검·해동 | 0.95 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/magic_cast.ogg` | 마법 (Q) | 0.5 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/monster_attack.ogg` | 몬스터 공격 | 0.25 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/monster_death.ogg` | 몬스터 사망 | 0.6 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/boss_warning.ogg` | 보스 패턴 경고 | 0.54 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/chest_open.ogg` | 상자 열기 | 0.8 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/chest_locked.ogg` | 잠긴 상자 | 0.27 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/item_pickup.ogg` | 아이템 획득 | 0.31 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/potion.ogg` | 포션 사용 | 0.66 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/menu_move.ogg` | 메뉴 이동 | 0.04 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/menu_confirm.ogg` | 메뉴 결정 | 0.2 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/menu_cancel.ogg` | 메뉴 취소 | 0.2 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/dialogue_advance.ogg` | 대사 넘김 | 0.03 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/shop_buy.ogg` | 상점 구매 | 0.35 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/door_open.ogg` | 문 열기 | 0.4 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/warp.ogg` | 워프 | 0.92 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_01.ogg` | 스킬 1 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_02.ogg` | 스킬 2 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_03.ogg` | 스킬 3 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_04.ogg` | 스킬 4 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_05.ogg` | 스킬 5 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_06.ogg` | 스킬 6 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_07.ogg` | 스킬 7 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_08.ogg` | 스킬 8 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_09.ogg` | 스킬 9 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_10.ogg` | 스킬 10 (임시 공통, 스킬별 맞춤 필요) | 0.35 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |

비고: 기존 `swing_light/heavy`, `hit_*` 와 기능이 겹치는 초안(swing_sword_*, hit_*)은 무기별·단계별 세분화 후보.
