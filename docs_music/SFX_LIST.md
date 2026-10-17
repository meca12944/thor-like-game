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
| `sfx_draft/swing_sword_1.ogg` | 검 1타 휘두르기 | 0.12 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/swing_sword_2.ogg` | 검 2타 휘두르기 | 0.13 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/swing_sword_3.ogg` | 검 3타(피니시) 휘두르기 | 0.17 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/swing_spear.ogg` | 창 휘두르기/찌르기 | 0.22 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/swing_axe.ogg` | 도끼 무거운 휘두르기 | 0.34 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/hit_normal.ogg` | 일반 타격 | 0.2 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/hit_finisher.ogg` | 피니시 타격 (묵직) | 0.57 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 · '샥!' 밝은 금속 핑 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/hit_critical.ogg` | 크리티컬 타격 (금속 링) | 0.44 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/combo_hit.ogg` | 콤보 카운트 틱 | 0.08 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/dash_attack.ogg` | 대시 공격 | 0.36 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/charge_stage1.ogg` | 차지 1단계 모으기 | 0.42 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/charge_stage2.ogg` | 차지 2단계 도달 | 0.32 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/charge_release.ogg` | 차지 해방 | 0.42 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/dodge_afterimage.ogg` | 잔상 회피 | 0.24 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/just_dodge.ogg` | 저스트 회피 성공 | 0.47 | Ys VIII-style original synthesis, no Falcom assets — 경쾌한 휘익 → 3음 '팅!' | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/footstep.ogg` | 달리기 발소리 | 0.08 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skid.ogg` | 급정지 미끄러짐 | 0.34 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/player_hurt.ogg` | 플레이어 피격 | 0.16 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/level_up.ogg` | 레벨 업 | 0.9 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/ult_raikou.ogg` | 궁극기 천광낙뢰 | 1.22 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/ult_demon_descent.ogg` | 궁극기 멸계강림 | 1.62 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/ult_ice_sword.ogg` | 궁극기 찬검·해동 | 0.99 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/magic_cast.ogg` | 마법 (Q) | 0.52 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/monster_attack.ogg` | 몬스터 공격 | 0.27 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/monster_death.ogg` | 몬스터 사망 | 0.32 | Ys VIII-style original synthesis, no Falcom assets — 짧고 드라이, 밝은 금속 링 + 타이트한 저역 펀치 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/boss_warning.ogg` | 보스 패턴 경고 | 0.56 | 짧고 펀치 있게 | P1 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/chest_open.ogg` | 상자 열기 | 0.82 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/chest_locked.ogg` | 잠긴 상자 | 0.29 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/item_pickup.ogg` | 아이템 획득 | 0.33 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/potion.ogg` | 포션 사용 | 0.68 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/menu_move.ogg` | 메뉴 이동 | 0.06 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/menu_confirm.ogg` | 메뉴 결정 | 0.22 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/menu_cancel.ogg` | 메뉴 취소 | 0.22 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/dialogue_advance.ogg` | 대사 넘김 | 0.05 | 짧고 펀치 있게 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/shop_buy.ogg` | 상점 구매 | 0.37 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/door_open.ogg` | 문 열기 | 0.42 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/warp.ogg` | 워프 | 0.94 | 짧고 펀치 있게 | P3 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_01.ogg` | 스킬 1: 대지의 수정 — 바위 솟음 + 수정 울림 | 0.79 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_02.ogg` | 스킬 2: 수정 실 — 가는 실 연속 튕김 | 0.32 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_03.ogg` | 스킬 3: 사중 잠행 — 모래 파고들기 → 솟구침 타격 | 1.09 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_04.ogg` | 스킬 4: 망자의 계약 — 저음 망령 신음·드론 | 1.82 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_05.ogg` | 스킬 5: 해류의 숨결 — 물거품 + 물살 | 0.52 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_06.ogg` | 스킬 6: 산호 방패 — 결계 화음 (흡수 30) | 1.52 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_07.ogg` | 스킬 7: 업화의 검 — 불꽃 휘두름 + 타격 | 0.79 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_08.ogg` | 스킬 8: 뇌광 질주 — 번개 크랙 돌진 | 0.37 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_09.ogg` | 스킬 9: 시간 정지 — 하강 피치 + 시계 틱 | 1.02 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/skill_10.ogg` | 스킬 10: 삼룡의 각성 — 3중 포효 + 대폭발 | 1.17 | v2: 스킬별 전용 디자인 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/step_dirt.ogg` | 발소리: 흙 | 0.13 | v2: 지면별 발소리 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/step_stone.ogg` | 발소리: 돌 | 0.09 | v2: 지면별 발소리 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/step_wood.ogg` | 발소리: 나무 | 0.12 | v2: 지면별 발소리 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |
| `sfx_draft/step_grass.ogg` | 발소리: 풀 | 0.12 | v2: 지면별 발소리 | P2 | numpy 합성 (자작) | 자작, CC0 로 배포 가능 |

비고: 기존 `swing_light/heavy`, `hit_*` 와 기능이 겹치는 초안(swing_sword_*, hit_*)은 무기별·단계별 세분화 후보.


스킬 매핑 출처: `town/index.html` 의 `SKILLS` 배열 (1~10번 순서). 기존 `footstep.ogg` 은 공통 발소리로 유지.

### 라우드니스 (v4)
ffmpeg ebur128 로 최종 ogg 측정 (1초 패딩 후 Integrated). 목표: 일반 SFX -14 LUFS, UI 틱(menu/dialogue/combo) -17, 발소리 -18, swing 1/2 는 swing 3 보다 1~2 dB 낮게. True peak ≤ -1 dBFS (hit_normal -0.8 은 Vorbis 오버슈트).