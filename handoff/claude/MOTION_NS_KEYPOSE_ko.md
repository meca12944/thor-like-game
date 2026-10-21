# 정면·뒷면(남·북) 걷기·달리기 — 핵심 자세 방식 (2026-10-21 사장님 "성공", "다음엔 실수 없이")

리네트 정면(남)·뒷면(북) 걷기·달리기를 만들면서 5번 실패한 뒤 성공한 방법이다. 다른 캐릭터도 **처음부터 이 순서**로 만든다.
결과물: `handoff/claude/linette_ns_keys_v1/` (브랜치 `claude/linette-8dir`), 게임 반영 브랜치 `claude/linette-ns`.

## 0. 결론 한 줄
정면·뒷면 이동은 **뼈대(스켈레톤)로 만들지 않는다.** PixelLab 이미지 편집으로 **핵심 자세 2장**(오른발 앞 / 왼발 앞)을 정확히 그리고,
그 사이를 PixelLab `animate-with-text-v3`(첫 장 + 마지막 장)로 이어 8장 주기를 만든다.

## 1. 왜 뼈대가 실패했나 (반복하지 말 것)
| 시도 | 결과 | 원인 |
|---|---|---|
| 주인공 정면·뒷면 그림에서 뼈대 추출 → 오프셋 이식 | "다리가 왜이래" | 다리 폭을 억지로 좁힘(LEGX), 정면 걷기는 발이 거의 안 들림 |
| 주인공 다리 각도(뼈 방향)만 이식 | 발 드는 동작이 사라짐 | 정면·뒷면에서 든 발은 **짧아 보이는 것**(원근)인데 뼈 길이를 고정해서 없어짐 |
| 주인공 다리 모양 그대로 + 길이 비율 | 뼈대는 맞는데 그림이 어색 | PixelLab 뼈대 도구는 평면 좌표만 받음 → "앞으로 나온 다리"를 짧은 다리·든 다리로 그림 |
| 모션캡처(CMU 07_01 걷기, 09_01 달리기)를 정면에서 본 뼈대 | 게다리 / 다리 꼬임 / "강아지처럼 달린다" | 발이 한 줄로 모이면 꼬이고, 엉덩이 밑에 일자로 고정하면 로봇 같고, 두 다리가 같이 굽으면 깡충 |
| PixelLab 자체 글 애니메이션(정면 걷기 8장) | 다리가 앞뒤로 자연스럽게 안 움직임 | 정면 걷기를 글만으로는 제대로 못 그림 |

핵심 원인: **정면·뒷면 걸음은 다리가 카메라 쪽으로 움직여서 2D 좌표로는 표현이 안 된다.** 사람이 그린 것 같은 "디딤·밑창·무릎 앞으로" 같은
자세는 그림(이미지 편집)으로 직접 지정해야 나온다.

## 2. 성공한 순서 (방향마다, 걷기·달리기 각각)
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

## 3. 프롬프트 (그대로 복사, 좌우만 바꿈)
공통 꼬리: `Keep the exact same character design, colors, outfit, size and the two thin silver needles, full body, no effects.`
- 정면 걷기 R: `Natural human walking pose toward the viewer, mid-stride contact: her RIGHT leg (on the left side of the image) steps forward toward the viewer with the heel touching the ground, that foot slightly lower in the image and slightly bigger; her LEFT leg is behind her, knee slightly bent, standing on the toes. Feet about hip width apart, not crossed. Hips level, torso upright, a slight natural arm swing: left arm a little forward, right arm a little back, needles still pointing down.`
- 뒷면 걷기 R: `Natural human walking pose walking AWAY from the viewer, back view, seen from behind, we see her back and ponytail, mid-stride contact: her RIGHT leg (on the right side of the image) steps forward away from the viewer, heel touching the ground, that foot slightly higher in the image; her LEFT leg is behind her nearer the viewer, knee slightly bent, heel lifted so we see the sole of the boot. Feet about hip width apart, not crossed. Hips level, slight natural arm swing, needles pointing down.`
- 정면 달리기 R: `Natural human RUNNING pose toward the viewer, front view facing the viewer, face visible: her RIGHT knee (left side of the image) drives up and forward toward the viewer, thigh raised, foot off the ground under the knee; her LEFT leg pushes off behind, nearly straight, only the toes touching the ground. Torso leaning slightly forward, both arms at her sides slightly pulled back holding the needles. Not crossed, human proportions.`
  (처음엔 "arms pulled back behind the hips"로 썼다가 팔이 몸 앞에서 꼬였다 → "arms at her sides"로 쓴다)
- 뒷면 달리기 R: `Natural human RUNNING pose running AWAY from the viewer, back view …: her RIGHT knee (right side of the image) drives up and forward away from the viewer; her LEFT leg behind her nearer the viewer is bent with the heel kicked up high so we see the sole of the boot. Torso leaning slightly forward, both arms at her sides slightly pulled back holding the needles pointing down. Not crossed, human proportions.`
- 사이 장(걷기): `natural human walk toward the viewer (/ away from the viewer, back view the whole time): the back leg swings forward past the standing leg, knee bends as it passes, body rises slightly at the passing moment, gentle opposite arm swing, front view the whole time, no effects`
- 사이 장(달리기): `natural human run toward the viewer, front view the whole time: the pushing leg swings through and its knee drives up while the other leg comes down and pushes off, brief moment with both feet off the ground, arms at her sides holding the needles, no effects`
  (뒷면: `… the kicked-up heel swings through and that knee drives forward while the other leg pushes off and its heel kicks up showing the sole …`)

## 4. 비용 (리네트 실측, 이 방식만)
- 동작 1개(한 방향) = 핵심 자세 2×10 + 사이 장 2×4 = **28**. 고칠 장이 있으면 +10.
- 정면·뒷면 걷기·달리기 4개 = 112 (+팔 고침 10 = 122).
- 뼈대 시도로 버린 비용 약 70 — 다음엔 쓰지 않는다.

## 5. 체크리스트 (보내기 전)
- [ ] 두 다리가 번갈아 움직이나 (같이 굽으면 강아지)
- [ ] 발이 꼬이지 않나, 다리가 벌어지지 않나 (게다리)
- [ ] 뒷발 밑창/뒤꿈치가 보이나 (뒷면)
- [ ] 장마다 키가 같나 (cycle_ns 출력 h 값), 얼굴·디자인이 원본과 같나
- [ ] 달리기 공중 높이 4px 이하, 걷기는 땅에서 안 뜨나
- [ ] 크레딧은 잔액 앞뒤로 확인, 다른 방 사용분과 구분해서 보고
