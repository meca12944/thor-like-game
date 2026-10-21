# 필멸자 캐릭터 제작 순서 — 결과 좋고 효율적인 방법만 (2026-10-21, 리네트 실측 기준)

리네트를 만들며 확정된 방법만 순서대로 모았다. 실패한 방법(글만으로 동작 뽑기, 정면·뒷면 뼈대 등)은 쓰지 않는다.
세부 문서: `MOTION_NS_KEYPOSE_ko.md`(이동), `MOTION_PIPELINE_LINETTE_ko.md`(초기 표준). 스크립트는 브랜치 `claude/linette-8dir`의 `handoff/claude/linette_*`.

## 0. 공통 규칙
- PixelLab 키는 환경변수 `PIXELLAB_API_KEY`만. 작업 전후로 잔액(`/v2/balance`)을 보고 **내 작업 사용량**만 따로 보고한다(공용 계정).
- 256 캔버스, 발 기준점 (128,189), 캐릭터 키 약 117px. 왼쪽 = 오른쪽 좌우 반전(↙↖도 ↘↗ 반전).
- 이펙트(검흔·마법진)는 그림에 굽지 않고 **게임 코드가 그린다**. 프롬프트에 `no effects`.
- 한 방향으로 시험 → 통과하면 나머지 방향. 결과는 MP4 + 프레임 시트로 사장님께 보인다.
- 크기를 바꿀 때는 무조건 `pxscale.py`(도트용). NEAREST 복사는 도트가 거칠어진다.

## 1. 캐릭터 원본 (8방향 정지 그림)
1. `create-character-v3`로 디자인 → 8방향 rotation(south, south-east, east, north-east, north …). 리네트 `7e26e0f3`.
2. 크기 후보를 나란히 보고 고른다(리네트는 117). 결과: `linette_8dir/final_117/<dir>.png` — **이후 모든 동작의 출발 그림**.
3. 얼굴이 흐리면: 서 있는 그림 1장을 손으로 눈·코·턱 보정(0) → 그 그림을 첫 장으로 서기 동작을 PixelLab에서 다시 그림(약 4). 이후 동작은 이 얼굴 기준.

## 2. 서기 (idle)
- 옆: 원래 서기 뼈대 + 얼굴 보정한 첫 장 → `animate-with-skeleton-v3`(8장 3). 바늘이 튀는 장은 빼고 0~5장 왕복.
- 대각선: 같은 방식, 팔은 옆 서기 팔 모양(몸에 붙이고 바늘 아래)로 맞춤(`diag_arms_like_side.py`, 3).

## 3. 걷기·달리기 8방향 — 핵심 자세 + 한 주기 (동작당 약 18)
방향: → (옆), ↓ (정면), ↑ (뒷면), ↘, ↗. 각 방향 걷기·달리기.
1. **핵심 자세 1장** — `linette_thrust_v1/edit_pose.py` (edit-images-v2, 10). 출발 = 그 방향 원본 그림.
   - 다리: 걷기 "앞발 뒤꿈치 닿고 뒷발 발끝", 달리기 "앞 무릎 올라가고 뒷발 차고 나감". 정면·뒷면은 "feet hip width apart, not crossed".
   - 팔: 걷기 `arms swing naturally opposite to the legs …`, 달리기 `arms pump energetically opposite to the legs (elbow bent)`, 정면은 `neither hand is raised above the chest`.
   - 뒷모습: `the red bikini top and its thin back strap are clearly visible across her back`.
   - 공통 꼬리: `Keep the exact same character design, colors, face, outfit, size and the two thin silver needles, full body, no effects, same facing direction.`
2. **한 주기 8장** — `linette_ns_keys_v1/tween.py key.png key.png <out> 8 "one complete natural human walking/running cycle … ending back in this exact starting pose; legs alternate cleanly …"` (animate-with-text-v3, 8). 결과 9장 중 0~7 사용.
   - 대각선 뒷모습은 `STRICT three-quarter BACK view … she never turns to a side view` 추가(안 하면 옆모습으로 돌아감).
3. `cycle8.py`로 장마다 키를 맞춘다(걷기). 달리기는 웅크림이 자연스러우니 원본 그대로.
4. 틱: 걷기 [6]*8, 달리기 [4]*8.
- (핵심 자세 2장 + 사이 장 방식도 되지만, 두 장이 같은 자세로 나오는 함정이 있어 한 주기 방식이 더 싸고 안전)

## 4. 짧은 동작 (대시·맞기·사망)
- 옆: `pose_keys.py`로 자세 뼈대(몸 숙임·무릎·팔 각도 숫자) → animate-with-skeleton-v3 (3).
- 정면·뒷면·대각선: 발은 몸 밑에 두고 무릎만 굽힘(다리 벌리면 게다리). 맞기·사망은 옆 그림을 쓴다.

## 5. 점프
- 제자리: 주인공 점프 뼈대를 리네트에 입힘(3). 높이는 코드(60px).
- 달리기 점프: 주인공 rjump 스켈레톤(`hero_runjump_v1/skeleton_east.json`)을 리네트 뼈 길이에 맞추고, **출발 그림 = 리네트 달리기 프레임**(팔 자세 이어짐) → 12장(3). 높이 72px.

## 6. 공격 (현재 컨셉)
- **공격 자세 없음**: 몸은 하던 동작(서기·걷기·달리기·점프) 그대로, **검흔만** 앞으로 찔러 나간다(창끝 모양, 3타는 두 줄). 그림 제작 비용 0.
- 공격 클립(atk1~3)은 타이밍·검흔 위치 데이터용으로만 쓴다. 새로 만들 때는 찌른 자세 지정 방식(edit 10 + end_frame 애니 8, `MOTION_PIPELINE_LINETTE_ko.md` 3절).
- 게임: 공속 배율(ATK_SPEED=2), 누르고 있으면 연타, 맞았을 때만 히트스톱. 8방향(대각선은 45°).

## 7. 스킬 시전
- 주인공 마법진·불꽃 자산(hero8_castfx / castfire)을 그대로 쓰고, 시전 동작은 대각선 포함 기존 cast 클립.

## 8. 조립 (크레딧 0) — `linette_final_v1/`
1. `assemble.py`: 동작·방향별 출처와 틱(SRC). 방향 키: right/left, down/downl(↘↙), up/upl(↗↖), south, north.
2. `polish.py`:
   - 발 기준 정렬(클립마다 한 번만 이동 → 떨림 없음).
   - **크기**: 머리(리본 위)→치마 아랫단 길이로 모든 서기·걷기·달리기를 옆 서기와 같게(전체 키로 맞추면 웅크린 달리기가 커짐).
   - **위치**: 치마 가운데를 x=128로(방향 바꿀 때 옆으로 안 튐).
   - 땅: 걷기는 발을 땅선에 붙임, 달리기는 4px 이상 안 뜨고 땅 밑으로 안 묻힘.
   - 모든 리사이즈는 `pxscale.py`.
3. `build_atlas.py` → `thrust_fx.py`(검흔 데이터) → `test128/assets/anim/linette8*.{json,webp}`, 게임 HTML 캐시 번호 올림.
4. 확인: `circle_check.py frames_polished out.png`(같은 원 안에 모든 동작) + 8방향 걷기→달리기 영상.

## 9. 게임 연결 (test128/linette.html 기준)
- 이동: 좌우만 → 옆, 위·아래만 → 정면/뒷면, 대각선 입력 → 대각선 그림. 멈추면 마지막 방향의 서기.
- 키보드: 방향키/WASD, Shift 달리기(L 토글), J/Z 공격, K/X·방향키 두 번 대시, Space 점프(달리면서 = 달리기 점프), U/C 스킬, H/G 피격·사망. 터치 패드는 키보드 쓰면 숨김.

## 10. 체크리스트 (보내기 전)
- [ ] 8방향 크기·그림체가 같은가(동그라미 검사), 방향 바꿀 때 옆으로 튀지 않는가
- [ ] 다리가 번갈아(강아지 X), 꼬임·게다리 없음, 대각선 달리기 교차 정상
- [ ] 모든 방향 팔이 흔들리는가, 한쪽 팔이 굳지 않았나
- [ ] 뒷모습 옷이 그려졌나, 대각선 뒷모습이 옆으로 돌지 않았나
- [ ] 도트가 거칠지 않은가(pxscale), 발이 뜨거나 묻히지 않는가
- [ ] 크레딧: 잔액 전후 + 내 사용량 보고

## 11. 비용 감각 (처음부터 이 방법만 쓸 때, 1명)
| 항목 | 크레딧 |
|---|---|
| 원본 8방향 + 크기 후보 | 약 30 |
| 서기(옆·대각선 2) + 얼굴 | 약 12 |
| 걷기·달리기 5방향 × 2 = 10개 × 18 | 약 180 |
| 대시·맞기·사망(옆 + 대각선) | 약 25 |
| 점프·달리기 점프 | 약 10 |
| 공격(검흔 컨셉) | 0 |
| **합계** | **약 260** (+고칠 장 장당 10) |
리네트는 시행착오 포함 누적 약 1,300~1,400. 다음 캐릭터는 위 순서대로 하면 1/4~1/5.
