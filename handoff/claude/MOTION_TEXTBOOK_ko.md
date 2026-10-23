# 모션 교과서 (필멸자 캐릭터·몬스터 모션의 유일한 문서)

> 사장님 2026-10-23: **"모션교과서 한곳으로, 앞으로 그곳만 사용"**
> - 모션(그리기·고치기·크기 맞추기·게임 연결)에 관한 순서·규칙·실패 기록은 **이 문서에만** 쓴다. 다른 문서를 새로 만들지 않는다.
> - 새로 배운 것은 1부(모두 지킬 규칙)나 2부(캐릭터별 기록)에 바로 덧붙인다. 작업 폴더의 README는 "무엇을 만들었나"만 짧게.
> - 옛 문서 `CHARACTER_PIPELINE_ko.md`, `MOTION_NS_KEYPOSE_ko.md`의 내용은 모두 여기로 옮겼다(그 파일들은 이곳을 가리키는 안내만 남음).

목차: 1부 공통 규칙·최종 순서 / 부록 A 정면·뒷면·대각선 핵심 자세 상세 / 2부 캐릭터별 기록(리네트·주인공·주인공2·몬스터) / 3부 찾아보기

---

# 1부. 공통 규칙 · 최종 순서 (모든 캐릭터)

## 용어
- 주인공의 피하기 = **회피대시**(옛 이름 구르기·dash·roll, 코드 이름 `dash`/`roll`은 그대로). 대시 잔상은 장마다 색 필터를 쓰지 말고 한 번 색칠해 둔 그림을 다시 쓴다(필터는 폰에서 프레임당 50~600ms 끊김, 10-23).

## 1-0. 작업 전에 꼭 (2026-10-23 주인공 작업에서 배움)
- **모습 먼저 확인**: 새로 그리거나 고치기 전에 정면/비스듬/옆, 어느 방향인지 사장님께 먼저 확인한다. 기존 그림 각도를 그대로 따라 그리지 않는다. (주인공 "아래쪽"은 원래 비스듬한 그림이라 따라 그렸다가 버림, 18)
- **이미 만든 것부터 찾기**: 새로 그리기 전에 저장된 그림(샌드박스 아틀라스 `test128/sandbox/assets/hero_sbx.json`, 다른 방 브랜치의 handoff 폴더)을 먼저 찾는다. 주인공 정면·뒷면 걷기·달리기는 샌드박스 파일에 이미 있었다.
- **다듬기는 비교 영상 먼저**: 고친 뒤 모습을 짧은 전·후 영상으로 먼저 보여 주고, 좋다고 하면 넣는다. (정면 달리기 "튀는 높이 줄이기"가 오히려 뻣뻣해져 되돌림)
- **크기·위치는 동작 하나에 한 번만** 맞춘다(같은 배율·같은 이동). 장마다 키를 같게 하거나 발·몸 가운데를 장마다 고정하면 몸이 오르내리고 흔들리는 움직임이 지워져 **뻣뻣**해진다.
  땅 밑으로 파고드는 장만 들어 올리되, 그 때문에 머리가 튀면 들지 않는다.
- **움직임 숫자 비교**(`tools/anim/motioncheck/audit2.py`): 보내기 전에 머리 오르내림·발 오르내림·몸 좌우 흔들림·키 변화를 수정 전과 비교한다.
  자연스러운 값: 걷기 머리 3~9px·몸 좌우 2~4px / 달리기 머리 4~6px·발 15~25px. 수정 후 크게 줄었으면 뻣뻣해진 것.
  AI가 그린 걷기에 좌우 흔들림이 1px대면 한 바퀴에 한 번 ±2px 몸무게 옮김을 코드로 더한다(`hero8_front_v1/assemble.py`의 `sway()`).
- **반복 이음새**: 서기·걷기·달리기는 마지막 장 → 첫 장 변화가 다른 장 평균의 1.8배를 넘으면 끊겨 보인다(audit2 "반복 이음새 튐"). 서기에서 칼·머리카락이 점점 바뀌는 클립은 비슷한 장만 골라 왕복(핑퐁)한다.
- 숫자로 거르는 것은 AI가 잘하고, "느낌(빠르다·답답하다)"은 사장님 눈이 정확하다 → 숫자로 의심 번호를 뽑고 **모션 점검표**(`tools/anim/motioncheck/board.py`, 번호 붙은 영상)로 사장님이 번호로 지적.

### 0. 공통 규칙
- PixelLab 키는 환경변수 `PIXELLAB_API_KEY`만 쓴다(출력·커밋 금지). 공용 계정이라 **작업 전후 잔액(`/v2/balance`) 확인 + 내 작업 사용량(job usage 합계)을 따로 보고**. 잔액 차이가 크면 다른 방 사용분이라고 밝힌다.
- 256 캔버스, 발 기준점 (128,189), 키 약 117px(여자 히로인, 주인공 124보다 작게).
- 왼쪽 = 오른쪽 좌우 반전, ↙↖ = ↘↗ 반전.
- 이펙트(검흔·마법진·불)는 그림에 굽지 않고 **게임 코드가 그린다**. 모든 프롬프트에 `no effects`.
- 한 방향 시험 → 통과하면 나머지. 사장님께는 **MP4 영상 + 프레임 시트**로 보인다(GIF 안 됨).
- 크기를 바꿀 때는 무조건 `linette_final_v1/pxscale.py`.
- 머지는 사장님 "세팅" 후에만. 브랜치 `claude/<주제>`.

### 1. 원본 8방향 정지 그림 (약 30)
1. `create-character-v3`(8방향) → south / south-east / east / north-east / north … 리네트 = `7e26e0f3`.
2. 크기 후보를 주인공 옆에 나란히 놓고 고른다(리네트 117). 결과 `linette_8dir/final_117/<dir>.png` = **모든 동작의 출발 그림**.

### 2. 얼굴 (약 4)
- 서 있는 옆 그림 1장을 손으로 보정(눈 진하게·흰 반짝임, 코, 입술, 턱선, 눈 밑 잡티 제거) → 그 그림을 첫 장으로 **서기 동작을 PixelLab에서 다시 그린다**(animate-with-skeleton-v3, 3 + 뼈대 추출 0.8). 손 보정만으로는 장마다 얼굴이 달라진다.

### 3. 서기
- 옆: 위 2번 결과. 바늘이 튀는 장은 빼고 앞 장들을 왕복.
- 대각선: 주인공 대각선 서기 뼈대 + 팔은 옆 서기 팔(몸에 붙이고 바늘 아래, `diag_arms_like_side.py`), 3.

### 4. 걷기·달리기 8방향 (동작당 약 18) — 핵심 자세 1장 + 한 주기 8장
방향 5개(→ 옆, ↓ 정면, ↑ 뒷면, ↘, ↗) × 걷기·달리기 = 10개.
1. 핵심 자세 1장: `linette_thrust_v1/edit_pose.py <원본> <out> <tag> "<프롬프트>"` (edit-images-v2, 10).
   - 다리: 걷기 = 앞발 뒤꿈치 닿고 뒷발 발끝, 달리기 = 앞 무릎 올라가고 뒷발 차고 나감. 정면·뒷면 = `feet hip width apart, not crossed`.
   - 팔: 걷기 `arms swing naturally opposite to the legs (one arm forward, the other back), each hand holding its thin silver needle`,
     달리기 `arms pump energetically opposite to the legs (one arm forward with the elbow bent, the other back)`, 정면 달리기 `neither hand is raised above the chest`.
   - 뒷모습 `the red bikini top and its thin back strap are clearly visible across her back`.
   - 꼬리 `Keep the exact same character design, colors, face, outfit, size and the two thin silver needles, full body, no effects, same facing direction.`
2. 한 주기 8장: `linette_ns_keys_v1/tween.py key.png key.png <out> 8 "one complete natural human walking|running cycle … ending back in this exact starting pose; legs alternate cleanly, one crossing per step, arms …"` (animate-with-text-v3, 8). 결과 9장 중 0~7.
   - 대각선 뒷모습: `STRICT three-quarter BACK view … her face is never visible, she never turns to a side view`.
3. 걷기는 `cycle8.py`로 장마다 키 맞춤(pxscale), 달리기는 원본 그대로(웅크림이 자연스러움).
4. 틱 걷기 [6]*8, 달리기 [4]*8.

### 5. 짧은 동작 (대시·맞기·사망, 약 25)
- 옆: `linette_skel_v1/pose_keys.py`(몸 숙임·허벅지·무릎·팔 각도를 숫자로) → animate-with-skeleton-v3(3).
- 정면·대각선 대시: 발은 몸 밑, 무릎만 굽히고 상체만 숙임(다리 벌리면 게다리), 팔은 몸에 붙여 작게(벌리면 T자).
- 맞기·사망은 대각선 없이 옆 그림(마지막 좌우 방향).

### 6. 점프 (약 10)
- 제자리: 주인공 점프 뼈대 → 리네트(3). 높이는 코드 60px.
- 달리기 점프: 주인공 rjump 스켈레톤(`hero_runjump_v1/skeleton_east.json`, CMU 127_25)을 리네트 뼈 길이로 맞추고 **출발 그림 = 리네트 달리기 프레임**(`rjump_from_heroskel.py`), 12장(3). 높이 72px, 앞으로 3px/틱.

### 7. 공격 (현재 컨셉, 0)
- **공격 자세 없음**: 몸은 서기·걷기·달리기·점프를 계속하고 **검흔만** 앞으로 찔러 나감(창끝 모양, 앞머리가 쭉 뻗고 꼬리가 따라 붙음, 3타 두 줄 굵게).
- 좌우 검흔·판정은 수평 고정, 위·아래는 수직, 대각선 입력은 45°.
- 공속 ATK_SPEED=2, 공격키 누르고 있으면 연타, 맞았을 때만 히트스톱·흔들림.
- atk1~3 클립은 타이밍·검흔 위치 데이터로만 씀. (공격 그림이 필요하면 찌른 자세 지정: edit 10 + end_frame 애니 8, 2타 다른 손은 팔만 바꾼 연타.)

### 8. 스킬
- 주인공 마법진·불꽃 자산(`hero8_castfx`, `hero8_castfire`)을 그대로, 시전 동작은 옆·대각선 cast 클립.

### 9. 조립 (0) — `linette_final_v1/`
`assemble.py` → `polish.py` → `build_atlas.py` → `thrust_fx.py` → `test128/assets/anim/` 복사 + html `?v=` 올림.
- polish: 발 기준 정렬(클립마다 한 번만 이동), 크기 = 머리(리본)→치마 아랫단 길이를 옆 서기와 같게, 위치 = 치마 가운데 x=128, 걷기 발 땅에 붙임, 달리기 4px 이상 안 뜨고 땅 밑으로 안 묻힘, 리사이즈는 pxscale.
- 확인: `circle_check.py frames_polished out.png` + 8방향 걷기→달리기 영상.

### 10. 게임 연결 (test128/linette.html)
- 이동: 좌우만 → 옆 / 위·아래만 → 정면·뒷면 / 대각선 입력 → 대각선. 멈추면 마지막 방향의 서기.
- 키: 방향키·WASD, Shift 달리기(L 토글), J/Z 공격(누르면 연타), K/X·방향키 두 번 대시, Space 점프(달리며 = 달리기 점프), U/C 스킬, H/G. 키보드 쓰면 터치 패드 숨김, 방향키·Space로 스크롤 안 됨, 포커스 잃으면 키 해제.

### 11. 보내기 전 체크리스트
- [ ] 8방향 크기·그림체 같음(동그라미 검사), 방향 바꿀 때 옆으로 안 튐
- [ ] 다리 번갈아(강아지 X), 꼬임·게다리 없음, 대각선 달리기 교차 정상
- [ ] 모든 방향 팔 흔들림, 한쪽 팔 고정 없음
- [ ] 뒷모습 옷 있음, 대각선 뒷모습이 옆으로 안 돔
- [ ] 얼굴(눈·코) 보임, 동작끼리 얼굴·머리 크기 같음
- [ ] 도트 거칠지 않음, 발 뜨거나 묻히지 않음
- [ ] 크레딧 보고(내 사용량 / 잔액 차이)

### 12. 비용 (처음부터 1부만 쓸 때, 1명)
원본 30 + 얼굴·서기 16 + 걷기·달리기 180 + 대시·맞기·사망 25 + 점프 10 + 공격 0 ≈ **260** (+고칠 장 장당 10).
리네트 실제 누적은 시행착오 포함 약 1,300~1,400.

---

# 부록 A. 정면·뒷면·대각선 걷기·달리기 — 핵심 자세 방식 상세 (옛 MOTION_NS_KEYPOSE_ko.md)

### 0. 결론 한 줄
정면·뒷면 이동은 **뼈대(스켈레톤)로 만들지 않는다.** PixelLab 이미지 편집으로 **핵심 자세 2장**(오른발 앞 / 왼발 앞)을 정확히 그리고,
그 사이를 PixelLab `animate-with-text-v3`(첫 장 + 마지막 장)로 이어 8장 주기를 만든다.

### 1. 왜 뼈대가 실패했나 (반복하지 말 것)
| 시도 | 결과 | 원인 |
|---|---|---|
| 주인공 정면·뒷면 그림에서 뼈대 추출 → 오프셋 이식 | "다리가 왜이래" | 다리 폭을 억지로 좁힘(LEGX), 정면 걷기는 발이 거의 안 들림 |
| 주인공 다리 각도(뼈 방향)만 이식 | 발 드는 동작이 사라짐 | 정면·뒷면에서 든 발은 **짧아 보이는 것**(원근)인데 뼈 길이를 고정해서 없어짐 |
| 주인공 다리 모양 그대로 + 길이 비율 | 뼈대는 맞는데 그림이 어색 | PixelLab 뼈대 도구는 평면 좌표만 받음 → "앞으로 나온 다리"를 짧은 다리·든 다리로 그림 |
| 모션캡처(CMU 07_01 걷기, 09_01 달리기)를 정면에서 본 뼈대 | 게다리 / 다리 꼬임 / "강아지처럼 달린다" | 발이 한 줄로 모이면 꼬이고, 엉덩이 밑에 일자로 고정하면 로봇 같고, 두 다리가 같이 굽으면 깡충 |
| PixelLab 자체 글 애니메이션(정면 걷기 8장) | 다리가 앞뒤로 자연스럽게 안 움직임 | 정면 걷기를 글만으로는 제대로 못 그림 |

핵심 원인: **정면·뒷면 걸음은 다리가 카메라 쪽으로 움직여서 2D 좌표로는 표현이 안 된다.** 사람이 그린 것 같은 "디딤·밑창·무릎 앞으로" 같은
자세는 그림(이미지 편집)으로 직접 지정해야 나온다.

### 2. 성공한 순서 (방향마다, 걷기·달리기 각각)
1. **시작 그림**: 캐릭터 정면/뒷면 원본(8방향 rotation의 south / north, 256 캔버스, 발 y≈189). 리네트: `linette_skel_v1/start_idle_south.png`, `start_idle_north.png`.
2. **핵심 자세 2장** — `linette_thrust_v1/edit_pose.py` (edit-images-v2 edit_with_text, 장당 10).
   - 같은 시드(7)로 오른발 앞(R) / 왼발 앞(L) 두 장. 아래 프롬프트를 그대로 쓴다(좌우 단어만 바꿈).
   - 화면 기준 좌우를 꼭 적는다: 정면에서 그녀의 RIGHT 다리 = 그림 왼쪽, 뒷면에서 RIGHT = 그림 오른쪽.
3. **확인**(크레딧 0): 두 장을 나란히 확대해서 본다. 팔이 꼬였거나 한 장만 다르면 **그 장만** 편집으로 고친다
   ("Keep this exact pose … Only change the arms …", 10). 리네트 정면 달리기 R은 팔이 몸 앞에서 꼬여서 1번 고쳤다.
4. **사이 장** — `linette_ns_keys_v1/tween.py` (animate-with-text-v3, first_frame + last_frame, 4프레임 = 4, 결과 5장).
   R→L 한 번, L→R 한 번. 두 번 다 같은 시드.
5. **주기 조립** — `cycle_ns.py <d> <out> [rise]`: R, RL1, RL2, RL3, L, LR1, LR2, LR3 (8장).
   사이 장은 ~5% 크게 그려지고 두 핵심 자세도 몇 % 다를 수 있어서 **모든 장을 발 기준으로 같은 키로 맞추고**, 중간 장만 1~3px 높게(몸 올라옴).
6. **아틀라스** — `linette_final_v1/assemble.py`의 `SRC[...]['south'|'north']`(방향 키 south/north, 좌우 반전 없음),
   틱: 걷기 [6]*8, 달리기 [4]*8. `polish.py`: 달리기는 공중 높이를 4px까지로 제한(그 이상은 깡충으로 보임). 걷기는 그린 땅 그대로.
   `build_atlas.py` DIRS에 'south','north' 포함.
7. **게임**: 위·아래로 움직일 때 `walk_south / walk_north / run_south / run_north`, 멈추면 대각선 서기.
8. **확인 영상**: 오른쪽·왼쪽에서 위 걷기 → 서기 → 아래 걷기 → 서기 → 위·아래 달리기 (playud.js). 시트도 같이 보낸다.

### 3. 프롬프트 (그대로 복사, 좌우만 바꿈)
공통 꼬리: `Keep the exact same character design, colors, outfit, size and the two thin silver needles, full body, no effects.`
- 정면 걷기 R: `Natural human walking pose toward the viewer, mid-stride contact: her RIGHT leg (on the left side of the image) steps forward toward the viewer with the heel touching the ground, that foot slightly lower in the image and slightly bigger; her LEFT leg is behind her, knee slightly bent, standing on the toes. Feet about hip width apart, not crossed. Hips level, torso upright, a slight natural arm swing: left arm a little forward, right arm a little back, needles still pointing down.`
- 뒷면 걷기 R: `Natural human walking pose walking AWAY from the viewer, back view, seen from behind, we see her back and ponytail, mid-stride contact: her RIGHT leg (on the right side of the image) steps forward away from the viewer, heel touching the ground, that foot slightly higher in the image; her LEFT leg is behind her nearer the viewer, knee slightly bent, heel lifted so we see the sole of the boot. Feet about hip width apart, not crossed. Hips level, slight natural arm swing, needles pointing down.`
- 정면 달리기 R: `Natural human RUNNING pose toward the viewer, front view facing the viewer, face visible: her RIGHT knee (left side of the image) drives up and forward toward the viewer, thigh raised, foot off the ground under the knee; her LEFT leg pushes off behind, nearly straight, only the toes touching the ground. Torso leaning slightly forward, both arms at her sides slightly pulled back holding the needles. Not crossed, human proportions.`
  (처음엔 "arms pulled back behind the hips"로 썼다가 팔이 몸 앞에서 꼬였다 → "arms at her sides"로 쓴다)
- 뒷면 달리기 R: `Natural human RUNNING pose running AWAY from the viewer, back view …: her RIGHT knee (right side of the image) drives up and forward away from the viewer; her LEFT leg behind her nearer the viewer is bent with the heel kicked up high so we see the sole of the boot. Torso leaning slightly forward, both arms at her sides slightly pulled back holding the needles pointing down. Not crossed, human proportions.`
- 사이 장(걷기): `natural human walk toward the viewer (/ away from the viewer, back view the whole time): the back leg swings forward past the standing leg, knee bends as it passes, body rises slightly at the passing moment, gentle opposite arm swing, front view the whole time, no effects`
- 사이 장(달리기): `natural human run toward the viewer, front view the whole time: the pushing leg swings through and its knee drives up while the other leg comes down and pushes off, brief moment with both feet off the ground, arms at her sides holding the needles, no effects`
  (뒷면: `… the kicked-up heel swings through and that knee drives forward while the other leg pushes off and its heel kicks up showing the sole …`)

### 4. 비용 (리네트 실측, 이 방식만)
- 동작 1개(한 방향) = 핵심 자세 2×10 + 사이 장 2×4 = **28**. 고칠 장이 있으면 +10.
- 정면·뒷면 걷기·달리기 4개 = 112 (+팔 고침 10 = 122).
- 뼈대 시도로 버린 비용 약 70 — 다음엔 쓰지 않는다.

### 5. 체크리스트 (보내기 전)
- [ ] 두 다리가 번갈아 움직이나 (같이 굽으면 강아지)
- [ ] 발이 꼬이지 않나, 다리가 벌어지지 않나 (게다리)
- [ ] 뒷발 밑창/뒤꿈치가 보이나 (뒷면)
- [ ] 장마다 키가 같나 (cycle_ns 출력 h 값), 얼굴·디자인이 원본과 같나
- [ ] 달리기 공중 높이 4px 이하, 걷기는 땅에서 안 뜨나
- [ ] 크레딧은 잔액 앞뒤로 확인, 다른 방 사용분과 구분해서 보고

### 6. 대각선(3/4) 추가 교훈 (2026-10-21)
- 대각선도 같은 방식으로 된다(↘/↗ 원본에서 "the leg nearer to the viewer / the far leg"로 2장, 좌우 단어 대신 near/far).
- **함정**: 대각선 **달리기**는 near/far 두 장이 사실상 같은 자세로 나오는 경우가 있다 → 반 주기마다 다리가 한 바퀴씩 돌아 교차 장이 이상해진다(사장님 "다리교차 프레임 이상").
  확인법: 두 핵심 자세를 나란히 놓고 **뒤로 간 다리가 서로 반대인지** 본다. 같으면 →
  `tween.py key.png key.png tw8_<d> 8 "one complete natural human running cycle … ends back in this exact starting pose; legs alternate cleanly, one crossing per step …"` (8) 한 번으로
  한 주기 8장을 받고 `cycle8.py`로 키를 맞춘다. 이쪽이 더 싸다(8 vs 8+사이장).
- 대각선 걷기는 아래로 걸을 때 몇 장이 7px 뜬다 → polish에서 걷기는 발을 땅선에 붙임(1px 출렁임). 달리기는 4px 이상 뜨지 않게, 땅 아래로 묻히지 않게.
- 리네트 대각선: 핵심 자세 8장 80 + 사이 장 32 + 달리기 한 주기 2회 16 = 128.

### 7. 크기·위치 맞추기 (2026-10-21, 사장님 "동그라미 그려서 봐봐")
- 크기는 **전체 키로 맞추지 않는다**(웅크린 달리기가 커진다). 머리(파란 리본 위) → 치마 아랫단(빨강 최하단) 길이로 모든 서기·걷기·달리기를 옆 서기와 같게(polish.py).
- 위치는 발이 아니라 **몸(치마 가운데)** 기준으로 클립마다 한 번만 x 이동 → 방향 바꿀 때 옆으로 튀지 않는다.
- 확인: `linette_final_v1/circle_check.py frames_polished out.png` — 모든 클립을 같은 원 안에 그려서 크기·튀어나온 곳을 본다.

### 8. 최종 확정본 (2026-10-21 사장님 "이거 좋다")
- **8방향 걷기·달리기 전부 같은 방식**: 방향마다 핵심 자세 1장(팔 흔들기 포함) + `tween.py key key … 8`로 한 주기 8장(`cycle8.py`). 좌우·정면·뒷면·대각선 모두.
  - 핵심 자세 프롬프트에 팔: 걷기 `arms swing naturally opposite to the legs (one arm forward, the other back), each hand holding its thin silver needle`,
    달리기 `arms pump energetically opposite to the legs (one arm forward with the elbow bent, the other back)` + 정면은 `neither hand is raised above the chest`.
  - 뒷모습은 `the red bikini top and its thin back strap are clearly visible across her back` (안 쓰면 위로 뛸 때 브라가 사라짐).
  - 대각선 뒷모습 주기는 `STRICT three-quarter BACK view … her face is never visible, she never turns to a side view` (안 쓰면 옆모습으로 돌아감).
- **크기**: 머리→치마 길이로 옆 서기와 같게, **위치**: 치마 가운데 기준(7절). 확인은 `circle_check.py`.
- **크기 바꿀 때는 무조건 `pxscale.py`** (부드럽게 줄인 뒤 원래 색으로 맞춤). 가장 가까운 픽셀 복사(NEAREST)는 도트 줄이 겹치거나 빠져 "도트가 부드럽지 않다".
- 비용 감각: 동작 1개(한 방향) ≈ 18 (핵심 자세 10 + 한 주기 8). 리네트 8방향 걷기·달리기 + 수정까지 이번 이틀 약 550.

### 9. 크기·위치 맞출 때 움직임을 지우지 말 것 (2026-10-23, 4번방, 사장님 "수정전보다 뻣뻣하다")
- **실수**: 주인공 정면 걷기·달리기를 맞추면서 **장마다** 키를 같게 맞추고 발·몸 가운데를 **장마다** 고정했다.
  → 걷기는 몸이 오르내리던 것(머리 1px만 남음)과 좌우 흔들림이 사라져 로봇처럼 미끄러졌고,
  달리기는 발을 땅에 붙이자 몸이 뛰어오르는 대신 머리가 거꾸로 13px 출렁였다.
- **규칙**
  1. 크기·위치는 **동작 하나에 한 번만** 맞춘다(같은 배율, 같은 이동). 장마다 따로 맞추지 않는다.
  2. 땅 아래로 파고드는 장만 들어 올리되, 그 때문에 머리가 튀면 들지 말고 원래대로 둔다.
  3. 보내기 전에 **움직임 숫자를 수정 전과 비교**한다: 머리 오르내림, 발 오르내림, 몸 좌우 흔들림, 키 변화.
     자연스러운 값: 걷기 머리 3~9px · 몸 좌우 2~4px / 달리기 머리 4~6px · 발 15~25px.
     수정 후 숫자가 크게 줄었으면 뻣뻣해진 것이다.
  4. AI가 그린 걷기에 좌우 흔들림이 거의 없으면(1px대) 한 바퀴에 한 번 ±2px 몸무게 옮김을 코드로 더한다.
- 도구: `tools/anim/motioncheck/audit2.py`(움직임 숫자), `handoff/claude/hero8_front_v1/assemble.py`의 `keep()`(동작 단위로 맞추기), `sway()`.
- 같은 날 추가 규칙(사장님 "이럴거면 왜 새로 그린거야"):
  5. 그리기·고치기 **전에** 모습(정면/비스듬/옆)을 사장님께 먼저 확인한다. 주인공 "아래쪽"은 원래 비스듬한 그림이라 그대로 따라 그렸다가 정면이 아니어서 버렸다(18크레딧).
  6. 다듬기는 **비교 영상을 먼저 보여 주고** 허락받은 뒤 넣는다. 정면 달리기 다듬기(튀는 높이 줄이기)가 오히려 뻣뻣해져서 되돌렸다.

---

# 2부. 캐릭터별 기록

## 2-1. 리네트 (2번방, 2026-10-21)
형식: **상황 → 사장님 지적 → 원인 → 수정 → 크레딧**

### A. 캐릭터 원본
1. 8방향 생성(create-character-v3) → 주인공과 크기 비교 → "117이 맞지싶은데 / 여자니까 117이 더 좋네" → 117 확정. (원본 생성비 포함)

### B. 첫 동작 세트 (글만으로 뽑기) — 가장 큰 낭비
1. `characters/animations` v3에 동작 설명만 주고 10동작 × 방향을 뽑음 → 공격이 휘두르기·T자, 정면·뒷면 대시·맞기가 "게다리", 얼굴·크기 제각각 → 대부분 버림. **약 288**.
   - 교훈: 글만으로는 원하는 자세가 안 나온다. **자세를 그림이나 뼈대로 지정해야 한다.**

### C. 공격 (찌르기 1·2·3타)
1. 글로 찌르기 → "1타 2타 3타 찌르기가 모션이 다 이상하다" → 휘두르기·T자 → **찌른 자세 그림을 먼저 edit로 만들고 end_frame으로 애니**(자세 10 + 애니 8). 공격 실험 다수로 크레딧 많이 씀.
2. "1타 오른손 2타 왼손인데 둘다 오른손" → 몸 뒤쪽 팔은 edit가 안 먹음 → 1타 찌른 자세에서 **뼈대로 팔만 바꾼 연타**(`swap_arms.py`+`atk2_chain.py`, 2~3).
3. "앞에 찌르기 할때 흔적 남겨야지 / 막타는 양손흔 두개 크게" → 검흔을 코드로(`fx.py`, `thrust_fx.py`가 바늘 끝 자동 측정), 3타 두 줄.
4. "앞뒤 모션이 없네" → 정면·뒷면 찌르기 시도 → 읽히지 않음 → **"아래위 삭제"** → 위·아래 공격은 대각선 그림 + 좌우 반전(downl/upl).
5. "아래 위 공격도 대각선이라 느낌이 안살아" → 위·아래 공격 검흔을 수직으로, 돌진·히트스톱·흔들림·3타 충격파 추가(0).
6. "2타 3타 얼굴크기랑 머리크기가 커지고 표정이 다 틀리다" → 장마다 PixelLab이 따로 그려 머리 비율이 커짐 → 새 얼굴을 첫 장으로 2·3타를 뼈대로 다시 그림, 2타 번진 다리는 첫 장 다리 붙임(7.7).
7. "왼쪽 오른쪽 히트박스가 왜 대각선위야" → 새 그림에서 바늘이 위로 들림 → 좌우 검흔·판정 **수평 고정**(0).
8. **공격 컨셉 전환**: "사람은 가만히 있고 특수효과만" → "검흔만" → "동작 모션 없이" → **"개좋잖아, 이 컨셉으로 간다"** → 걷기·달리기·점프 중 어디서든 공격, 검흔은 월드 좌표로 날아감(0).
9. "공속 빠르게 / 너무 느리다" → ATK_SPEED 2배 + 누르고 있으면 연타(0).
10. "좀더 앞으로 찌르는 듯한 검흔" → 창끝 모양으로 쭉 뻗고 꼬리가 따라붙는 찌르기 줄기(0).
11. "대각선 방향이 왜 없지" → 대각선 입력이면 대각선 그림 + 45° 검흔(0).

### D. 달리기 팔
1. "달릴때 팔과 무기를 뒤로빼고" → 4가지 후보 → "1번" → 이후 "리네트는 두팔다 뒤로" → "팔위치를 허리위 기존 모션처럼" → 손 허리·팔 뒤 버전(`arms_back.py`).
2. (최종) **"모든 모션 팔을 흔드는걸로 가자"** → 2부 L 참고.

### E. 방향 규칙 변화
1. "남북 방향은 전부 안쓴다, 대각선으로 대신" → 위·아래는 대각선 + 마지막 좌우로 반전, 맞기·사망은 옆.
2. (이후) "아래위 북쪽 남쪽 걷기 뛰기 만들라고" → 정면·뒷면 다시 도입 → 2부 J~K. 결국 **8방향 전부** 사용.

### F. 스킬 시전
1. 주인공 마법진 불러와 → "더 길게, 마법진에 불이 동그랗게 회전하듯" → PixelLab 불꽃 링 + 코드로 한 바퀴 → 리네트에 적용 → "대각선도 보여줘야지" → 대각선 시전 클립.
2. "크레딧 너무 많이 쓴다 / 대각선 다 있잖아" → 이미 만든 그림을 재활용(0)하는 습관.

### G. 얼굴
1. "가만히 서있는 얼굴에 코가 없다, 윤곽이 없음" → 손으로 코 1px → 티 안 남 → 코·입술·턱선 → (0)
2. "눈도 보이게" → 눈 추가 → "선명하지 않고 눈물 흘리는거 같아" → 눈 밑 연보라 점이 눈물처럼 보였음 → 지우고 2×2 진한 눈동자 + 흰 반짝임(0).
3. **"이거 표정 픽셀랩에 새로 찍어라"** → 보정한 얼굴을 첫 장으로 서기 동작을 PixelLab에서 다시 → 자연스러워짐, 눈은 파랑("이대로 하자")(3.8).
4. "걸을때 다시 얼굴이 이상" → 걷기만 옛 얼굴 → 새 얼굴로 걷기 다시(6.1).
   - 교훈: **얼굴을 바꾸면 그 얼굴을 첫 장으로 모든 동작을 다시** 그려야 동작 간 얼굴이 같다.

### H. 점프
1. 주인공 점프 뼈대로 제자리 점프(옆·대각선).
2. 달리기 점프 v1: 주인공 rjump 그림에서 뼈대 추출 + 출발 = 서기 → **"왜이리 엉성해?"** → 바늘 처짐(서기 출발), 웅크린 채 도약감 없음, 높이 34px → (4.8 버림)
3. **"스켈레톤 주인공꺼 다시 불러와"** → 주인공 rjump 스켈레톤 원본을 리네트 뼈 길이로 + **출발 = 리네트 달리기 프레임** + 높이 72px → 통과(3).
4. "더높이 뛰도록" → 제자리 점프 30 → 60px(0).

### I. 대각선 팔 (1차)
1. "밑으로 대각선 양 방향 팔위치 좌우랑 틀리다" → 대각선은 팔을 벌리거나 처짐 → 옆 동작 팔 뼈대를 대각선에 이식(`diag_arms_like_side.py`)해서 서기·걷기·달리기 다시(9.3).
2. 위 대각선도 같은 방식(9.3) → 사장님 "머야 이거 삭제해, 내말은 남북" → 롤백(미리보기 되돌림). 나중에 대각선 입력 도입 때 다시 씀.
   - 교훈: 요청 단어("아래위")를 **정면·뒷면인지 대각선인지** 먼저 확인.

### J. 정면·뒷면 걷기·달리기 — 뼈대 방식 실패 5번 (약 70 버림)
1. 주인공 정면·뒷면 그림에서 뼈대 추출 → 오프셋 이식 + 다리 폭 좁힘(LEGX) + 정면 걷기 인위적 발 들기 → **"다리가 왜이래, 주인공 다리모션 참조"** (18.2)
2. 주인공 다리 **각도**(뼈 방향)만 이식 → 정면·뒷면에서 발 드는 동작이 사라짐(든 발 = 짧아 보이는 다리인데 뼈 길이를 고정) → 버림(12)
3. 주인공 다리 **모양 그대로** + 길이 비율 → 발 들기는 살았지만 달리기에서 몸이 뜨고(11px) 묻힘(15px) → 땅 맞춤(12)
4. **"그냥 스켈레톤 써서 걷는 프레임시트"** → CMU 모캡 걷기(07_01)를 정면에서 본 뼈대(주기 감지가 달리기용이라 0.3초로 잘못 잘림 → 수동 1.08초) → **"게다리 수정해"** (발이 한 줄로 모여 꼬임) → 발을 엉덩이 밑 일자로 → **"이상하다 픽셀랩에 고쳐라"** (6+3)
5. PixelLab 글 애니(정면 걷기 8장) → **"다리가 앞뒤로 자연스럽게 안움직임"** → 모캡 + 깊이 기울기 키움 → 걸음은 보이지만 → **"강아지처럼 달린다"** (8+3+9)
   - 원인 분석(사장님 "원인 분석"): ① 정면·뒷면 걸음은 다리가 카메라 쪽으로 움직여 2D로 표현이 안 됨 ② PixelLab 뼈대 도구는 깊이를 모름 ③ 팔·몸 고정 ④ 다리를 억지로 일자/좁게 ⑤ 장마다 다르게 그림 ⑥ 이동 속도·보폭 불일치.

### K. 정면·뒷면 — 핵심 자세 방식 성공 (122)
1. "2번 해라, 인간의 자연스러운 움직임, 꼭 해내라" → 핵심 자세 2장(오른발 앞/왼발 앞, edit 10) + 사이 장(animate-with-text-v3 first+last, 4) → 8장 주기.
2. 정면 달리기 한 장이 팔이 몸 앞에서 꼬임("arms pulled back behind the hips"가 원인) → 그 장만 "arms at her sides"로 다시(10).
3. 사이 장이 5% 크게 그려짐 → 발 기준으로 키 맞춤. 뒷면 달리기 10px 뜸 → 4px로 제한.
4. **"너무 잘했다, 이거 성공이야"** → 방법 문서화 + 전 방 전파.

### L. 대각선·옆도 같은 방식으로 (128 + 36 + 160 + 18)
1. "대각선이 이상한데, 최신 맞아?" → 대각선만 옛 뼈대 방식이라 정면·뒷면과 이어 보면 어색 → 대각선 걷기·달리기도 핵심 자세 방식(112).
2. **"대각선 달리기 다리교차가 프레임이 이상"** → near/far 두 핵심 자세가 **같은 자세로 그려져** 반 주기마다 다리가 한 바퀴씩 돎 → **같은 장→같은 장 한 주기 8장**(8×2=16). 이 방식이 더 싸서 이후 표준.
3. **"좌우 캐릭터 도트 화질이 크기 차이 나고 자연스럽지 않음"** → 좌우만 옛 뼈대 방식이라 그림체가 다르고 달리기가 108px로 작음 → 좌우도 핵심 자세 1장 + 한 주기(36).
4. **"캐릭 크기가 방향별로 틀려지네 / 위로 뛸때 브라가 없어지고 / 좌우는 팔을 흔드는데 나머지는 팔이 뒤에 → 모든 모션 팔을 흔드는걸로"** → 8개 다시(팔 흔들기 + 뒷모습 비키니 끈 명시), ↗는 주기 중 옆모습으로 돌아가 "STRICT back view"로 재생성(160).
5. **"리네트를 기준으로 동그라미를 그려서 봐봐, 뛸때 좌우 크기가 훨씬커"** → 원인: 전체 키로 맞춰서 웅크린 달리기가 확대됨 + 발 기준 정렬로 몸이 좌우로 치우침(최대 32px) → **머리→치마 길이로 크기, 치마 가운데로 위치** + `circle_check.py`(0).
6. **"아래로 뛸때 한쪽팔 고정 / 아래 위 도트가 좌우만큼 부드럽지 않아"** → 정면 달리기 한 손이 바늘 든 채 굳음 → 양팔 다시(18). 도트: 크기 맞추며 NEAREST로 2~3번 늘이고 줄여 도트 줄이 겹치거나 빠짐 → **pxscale**(부드럽게 줄인 뒤 원래 색으로)(0).
7. **"어 이거 좋다, 결국에는 크레딧 써서 만들어야 자연스러워 지는구나"** → 세팅(PR #49).

### M. 조작
1. "조작 키보드로" → Shift 달리기, Z/X/C 대체키, 스크롤 막기, 키 눌림 해제, 터치 패드 자동 숨김.
2. "앞으로 2번 하면 대쉬, 스페이스 점프" → 같은 방향키 0.26초 안에 두 번 = 대시.

### N. 운영에서 배운 것
- 크레딧: 사장님은 낭비에 민감. 뼈대·실험으로 아끼려다 더 쓴 적이 많다(정면·뒷면 약 70 버림). **처음부터 1부 방법으로 그림을 확실히 지정하는 게 결국 싸다.**
- 매 작업 전후 잔액 확인, 내 사용량과 다른 방 사용분 구분.
- 미리보기는 아티팩트 샌드박스(머지 전 확인용), 최종은 "세팅" 후 GitHub Pages.
- 영상 녹화용 로컬 서버는 `pkill` 패턴이 자기 셸을 죽일 수 있음(백그라운드 실행 권장).
- 다른 방이 같은 브랜치에 푸시하면 fetch → merge 후 푸시.

## 2-2. 주인공 (망토, 지금 게임에 쓰는 주인공 hero8)

### 지금 상태 (2026-10-23)
- 아틀라스: `test128/index.html`의 `/*H8*/` JSON(손으로 고친 부분 있음 — `hero_v4_atlas.py`로 다시 뽑으면 고친 것이 사라짐. `_fix_v1`, `_front_note`, `_idle_note`, `_hurt_note`, `_walk_note` 메모 참고).
- 방향: down(↓)·up(↑)·right(→)·left(←, 오른쪽 좌우 반전 `H8.left=0`). **↓는 똑바른 정면**(서기·걷기·달리기·맞기·대시·점프 = `hero8_front.webp`), ↑는 비스듬한 뒷모습.
- 공격: **칼 베는 몸동작 없음, 검기만 코드로**(`world.js` `SLASH_BODY=false`, 샌드박스 hero_slash_a 초승달). 쏠 때 몸 반동(뒤로 젖힘 → 앞으로 튐 + 살짝 눌림)도 코드.
- 키 124px, 발 기준 (128,189), 게임에서 30 field px.

### 기록 (상황 → 지적 → 원인 → 수정 → 크레딧)
1. 모션 점검표로 숫자 점검 → 달리기↓ 망토·머리 끝 **회색 얼룩**(배경 찌꺼기) → 회색 두 색 중 몸 뒤쪽·바깥과 이어진 것만 지움 + 10px 미만 섬 지움(0).
2. "맞기 칼이 확 올라감"(41·42번) → 마지막 장 뺌, 1-2-3-2-1 왕복(0).
3. 걷기↓ 같은 장 2번 → 멈칫 → 1장 뺌(0).
4. "검 베는 모션은 안쓰려구 / 최종 샌드박스 검기만" → 게임 공격을 검기만으로(0).
5. "부자연스러운 점 정밀 분석" → 서기(→←) 칼이 내려가다 처음으로 **튐**, 멈춤↔걷기↔달리기 칼 위치 순간이동 → 칼 내린 장만 숨 쉬듯 왕복(0). 걷기 앞·뒤 이음새 장 뺌(0).
6. 크레딧 충전 후 다시 그리기(`hero8_fix_v1`, 100): 위로 걷기 칼 아래로(1번 다시), 걷기↓ 다리, 옆 대시 4→10장, 맞기 앞·뒤. **달리기↓는 비스듬하게 그려서 "앞을 안 봄" → 버림(18)**.
7. "둘 다 정면, 예전에 만든 거 있을 텐데" → 샌드박스 `idle_s/walk_s/run_s`를 그대로 넣음(0). 문제점 분석 → 정면 세트(`hero8_front_v1`, 88): 서기 핑퐁, 걷기 새로(1번 다시), 맞기·대시(1번 다시)·점프 정면 새로, 96% 크기.
8. **"정면 걷기·달리기가 수정 전보다 뻣뻣"** → 원인: 장마다 키·발·가운데 고정 → 동작 단위 1번 맞춤 + 걷기 좌우 2px 흔들림 추가, 달리기는 원래 움직임(0). → 1부 1-0 규칙.
9. "이럴거면 왜 새로 그린거야" → 달리기↓는 새로 그린 게 아니라 다듬기였고 결과가 거의 원래대로 → 1부 1-0 "모습 먼저 확인 / 다듬기는 영상 먼저".

### 옛 작업 폴더 (handoff/claude, 1번·2번방 주인공 작업)
- `hero8_fix_v1/` — 기존 주인공(망토) 모션 다시 그리기 v1 (2026-10-22)
- `hero8_front_v1/` — 기존 주인공 정면(↓) 세트 v1 (2026-10-23)
- `hero_afterimage_v2/` — hero_afterimage v2 (2026-10-20, 사장님 OK · 저장만, 게임 미적용)
- `hero_atk_feel_v1/` — hero_atk_feel v1 (2026-10-20, 저장만 · 게임 미적용)
- `hero_atk_feel_v2/` — hero_atk_feel v2 (2026-10-20, 저장만 · 게임 미적용)
- `hero_attack_thrust_v1/` — hero_attack_thrust v1 — 주인공 좌우 1·2타 찌르기 (게임 반영)
- `hero_attack_thrust_v2/` — hero_attack_thrust v2 — 찌르기 얼굴 색 + 전진 줄임 + 3타 얼굴 (게임 반영)
- `hero_attack_thrust_v3/` — hero_attack_thrust v3 (2026-10-20, 사장님 OK · 인게임 세팅)
- `hero_combo_new_v1/` — hero_combo_new v1 (2026-10-20, 사장님 지시 · 저장만, 게임 미적용)
- `hero_combo_new_v2/` — hero_combo_new v2 (2026-10-20, 사장님 "속도 더 빠르게 세팅" · 게임 진입 샌드박스 적용)
- `hero_combo_new_v3/` — hero_combo_new v3 (2026-10-20, 사장님 "좋다 이거 저장" · 저장만, 게임 진입 화면은 v2 속도)
- `hero_combo_new_v4/` — hero_combo_new v4 (2026-10-20, 저장만 · 게임 미적용) — 8방향
- `hero_diag_ingame_v1/` — hero_diag_ingame v1 (2026-10-20, 사장님 OK · 인게임 세팅)
- `hero_entry_sandbox_v1/` — 게임 진입 = 주인공 샌드박스 (2026-10-20, 사장님 지시 · 인게임 세팅)
- `hero_hit3_skyblue_v1/` — hero_hit3_skyblue v1 (2026-10-20, 사장님 "하늘색으로 세팅" · 인게임 적용)
- `hero_lunge_v1/` — hero_lunge v1 (저장만): 공격 전진 H8.lunge = [8, 10, 32]
- `hero_runjump_v1/` — hero_runjump v1 (2026-10-20, 사장님 OK · 인게임 세팅)
- `hero_sandbox_v4/` — hero_sandbox v4 (2026-10-20)
- `hero_sandbox_v5/` — hero_sandbox v5 (2026-10-20)
- `hero_sandbox_v6/` — hero_sandbox v6 (2026-10-20)
- `hero_skills20_ref_v1/` — hero_skills20_ref v1 (owner "일단 저장")
- `hero_skills20_v1/` — hero_skills20 v1 (owner "일단 저장")
- `hero_skills4_v1/` — hero_skills4 v1 (owner "세팅은 4개만 + 스킬창")
- `hero_slash20_v1/` — hero_slash20 v1 (owner "저장")
- `hero_slash_a_v1/` — hero_slash_a v1 (owner 2026-10-20 "저장"; not set in game yet)
- `hero_slash_fx2_v1/` — hero_slash_fx2 v1 (owner 2026-10-20 "저장"): three stylish sword-arc variants, hero stands still
- `hero_slash_legend5_v1/` — hero_slash_legend5 v1 (owner "저장")
- `hero_slash_ys8_v1/` — hero_slash_ys8 v1 (owner 2026-10-20: "좋다 세팅해")
- `hero_stabilize_v1/` — hero_stabilize v1 + hero_diag_hitbox v1 (2026-10-20, 사장님 OK · 인게임 세팅)
- `hero_sword30_fx_v1/` — hero_sword30_fx v1 (owner 2026-10-20 "일단저장")
- `hero_uniform_v1/` — hero_uniform v1 (owner 2026-10-20 "세팅저장")
- `hero_updown_v1/` — hero_updown v1 (owner 2026-10-20 "저장 세팅해")
- `hero_zoom_v1/` — hero_zoom v1 + 샌드박스 모션 일치 (2026-10-20, 사장님 OK · 인게임 세팅)

## 2-3. 주인공2 (망토 없는 새 디자인, **봉인** — 사장님 10-22 "새주인공은 봉인이야")
- 위치: 브랜치 `claude/linette-8dir`의 `handoff/claude/hero_v6_mini/` (게임 미연결). 서기·걷기·달리기 5방향 완성.
#### 디자인
`ref/south_ref_256_v7.png` — 짧은 헝클어진 머리, 엉덩이에서 끝나는 남색 상의(코트 자락 없음), 금색 장식 견갑, 가운데 금색 자수, 갈색 토시, 금색 무릎 보호대, 버클 장화, 오른손에 아래로 든 장검. 원화를 그대로 줄이면 머리가 작고 몸이 가늘어져서(어깨 41px vs 기존 77px), 기존 정면 스프라이트를 v7 겉모습으로 편집해 만들었다. 8방향 PixelLab 캐릭터는 `rot/pick.json`.

#### 만든 방법
- **옆·북동** (`anim.py` → `seam.py`/`pick_seam.py` 이음새 보간 → `post_run.py` → `check_run.py`): 바닥선 189 고정, 몸통 x 5프레임 원형 평균, 틱은 디딘 발 이동 거리 ÷ 속도. 옆 달리기 발 미끄러짐 51.8 → 8.6px.
- **정면·뒷면·남동** (핵심 자세 방식, `handoff/claude/MOTION_NS_KEYPOSE_ko.md`): `ns_keys.py` 오른발·왼발 자세 2장 → `ns_tween.py` 사이 프레임 → `ns_cycle.py` 8프레임 → `ns_polish2.py`.
- **대기**: `idle_pingpong.py` (0-1-2-3-2-1 왕복).

##### 정면 달리기·정면 대각 수정 기록
원인:
1. 정면 달리기 키 포즈의 왼손이 허리에 붙어 있고 사이 프레임은 팔을 흔들어서, 키 프레임마다 팔이 튐. 칼 각도 ±7°.
2. 예전 `ns_polish.py`가 프레임마다 따로 높이를 잘라서 머리가 박자 없이 최대 6px 출렁임.
3. 남동은 글자 지시 애니메이션이 옆모습 쪽으로 돌아가며 칼이 뒤집히고(-80° → +27°) 달리기가 뻣뻣함.

해결: `ns_polish2.py`(클립 단위 바닥 맞춤 + 걸음 박자 머리 높이, 걷기 1px·달리기 2px), `ns_pixfix.py`로 정면 달리기 키의 팔만 고쳐(R s71, L s72) 다시 생성(칼 ±4°), 남동은 핵심 자세 방식으로 새로 만듦.

#### 남은 것
- 북동 걷기·달리기는 글자 지시 방식이라 옆모습 쪽으로 도는 경향이 있을 수 있음. 리네트 방 최종 방식(동작당 약 18)으로 다시 하면 약 36.
- 정면 달리기 7번째 프레임 실루엣 변화가 조금 큼(눈에 크게 띄지 않음).
- 공격·대시·점프·피격·사망·시전(`plan.json` phaseB)은 별도 견적.
- `test128` 게임 연결(`hero8.json` 형식 변환)은 아직 안 함.

#### 사용량: 412회 (`usage.jsonl`)
편집(Pro) 150, 캐릭터 동작 128, 사이 프레임 68, 회전 24, 도트 변환 20, Pixen 편집 18, 배경 제거 4.

#### 폴더
- `final/` 게임용 최종본 · `ref/` 원화·기준 그림 · `rot/s4` 쓰는 회전 · `anim/`, `ns/` 작업 원본(스크립트가 이 경로를 씀)
- `old/` 쓰지 않는 판(허리 손 정면 달리기, 편집 v2 팔 수정판, 글자 지시 남동, 회전 s1~s3 등)
- `compare/` 비교 그림·옛 확인 영상 · `logs/` 실행 기록
- 스크립트: `pl.py` API(키는 환경변수 `PIXELLAB_API_KEY`에서만), `rotate.py`, `anim.py`, `seam.py`, `pick_seam.py`, `post_run.py`, `check_run.py`, `idle_pingpong.py`, `ns_*.py`, `edit_*.py`, `to_pixel.py`, `cut_refs.py`, `make_sheet*.py`, `export_final.py`

## 2-4. 몬스터 (4번방)
- 1장 펠트 몹 4종(`art/mobs/felt`, `tools/anim/feltmobs`): 걷기·공격·사격 = PixelLab animate-with-text-v3(첫 장·끝 장), 8방향 걷기 = 2번방 핵심 자세 1장 + 한 주기 8장 + pxscale.
  - 정면·뒷면이 옆모습으로 나옴(사냥개·망령) → 프롬프트를 더 세게 하거나 정면 그림에서 시작, 망령은 style 이미지만으로 생성.
  - 거미 뒷모습 사이 장에서 실패(실통)가 사라짐 → 다시. 방향별 크기 다름 → 평균 키로 맞춤.
  - 투사체·빛·검흔은 그림에 굽지 않고 코드(`world.js` FELT_SHOT, `projfx.py`).
- 3번방 대기·공격 스트립 47종(`tools/anim/mobs47/import.py`): 왼쪽 보는 그림은 좌우 반전(공격은 코드 돌진), 몸 키 = 스트립 몸 높이 × 0.2(주인공 30).
- 폰 끊김: 큰 스트립을 매 프레임 고품질로 줄이지 말고 크기별로 한 번 줄여 저장해 찍기(`world.js` scaledStrip), 화면 배율 최대 2.
- 기록: `handoff/claude/MOBS_ROOM4_ko.md`(작업 일지).

---

# 3부. 찾아보기
| 무엇 | 어디 |
|---|---|
| PixelLab 호출(키는 환경변수) | `handoff/claude/hero8_fix_v1/pl.py` (edit / anim), 리네트 `linette_*/pl.py`(브랜치) |
| 크기 바꾸기 | `pxscale.py` (`hero8_fix_v1/`, `tools/anim/feltmobs/`, 리네트 `linette_final_v1/`) |
| 움직임 숫자 점검 | `tools/anim/motioncheck/audit.py`, `audit2.py` |
| 모션 점검표 영상(번호) | `tools/anim/motioncheck/board.py` |
| 주인공 아틀라스 | `test128/index.html` `/*H8*/`, 시트 `test128/assets/anim/hero8_*.webp` |
| 주인공 샌드박스 아틀라스(정면·뒷면 원본) | `test128/sandbox/assets/hero_sbx.json` |
| 리네트 아틀라스 | `test128/assets/anim/linette8.json` |
| 몬스터 | `test128/world_mobs.js`, `test128/assets/mobs47`, `assets/mobs_felt` |
| 인게임 녹화·테스트 | `test128/tools/test_place_all.py`, `sfx_preview.py`, 스킬 `ingame-test` |
