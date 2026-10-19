# PixelLab 실전 가이드 (탑다운 픽셀 액션 RPG · 주인공 약 124px / 256 캔버스 · 4방향)
작성 2026-10-19 (KST). 근거: 공식 문서·API v2 OpenAPI, 커뮤니티 글, 그리고 우리 작업 기록(hero/v3gen_20261018, heroines_v4px_20261018의 run.log와 스크립트).

## 1. 기능 한눈에 보기 (API v2 기준)
| 기능 | 엔드포인트 / 도구 | 하는 일 | 256 캔버스 비용 |
|---|---|---|---|
| 캐릭터 생성(회전) | `create-character-v3` | 정면(south) 그림 1장을 8방향으로 회전한다. 4방향은 `n_directions:4` | 참조 모드는 `ceil(w*h*8/65536)`라서 256이면 **8**. 처음부터 그리면 +1. 네 방향을 모두 넣으면 가져오기만 해서 **0.25** |
| 8방향 Pro | `create-character-pro`, 웹의 8-rotations Pro | 컨셉 그림이나 스타일을 받아 8방향을 만든다. 프레임당 최대 168px | 10~25 |
| 상태(State) | `create-character-state` | 같은 캐릭터에 텍스트로 변경(자세·복장 등)을 4/8방향 모두 똑같이 적용해 새 캐릭터로 저장한다 | – |
| 텍스트 애니메이션 | `characters/animations` (mode `v3`), `animate-with-text-v3` | 시작 프레임과 동작 설명으로 4~16프레임(짝수)을 만든다. 256에서는 픽셀 예산 때문에 **최대 8프레임** | 256: 4프레임 **4**, 8프레임 **8** |
| 시작·끝 지정 | 같은 엔드포인트의 `custom_start_frame`, `end_frame` | 시작 포즈와 끝 포즈 사이를 보간한다. 동작이 대기 자세로 돌아오게 할 때 유용하다 | 같음 |
| PixMiniMax(베타) | mode `pixminimax` | 4의 배수로 최대 40프레임 | 시간 기준 과금, 최대 6 |
| 스켈레톤 애니 | `animate-with-skeleton-v3`, mode `template`/`skeleton-v3` | 프레임마다 뼈대 포즈를 준다. skeleton-v3는 다시 그리지 않고 **캐릭터 자체를 움직인다**(디자인 유지) | 캔버스 크기와 무관하게 3프레임 2, 8프레임 3, 15프레임 4 |
| 이미지 편집 | `edit-images-v2` (Pro: 텍스트 또는 참조), `edit-image-pixen` | 한 장을 텍스트나 참조 그림으로 고친다 | Pro 256: **10** / pixen: **1** |
| 애니메이션 편집 | `edit-animation-v2` (Pro) | 같은 지시를 모든 프레임에 일관되게 적용한다. 171~256px은 2×2 그리드라 **최대 4프레임** | 256: **25** (129~170px는 15, 128px 이하는 10) |
| 복장 전이 | `transfer-outfit-v2` | 참조 그림의 복장을 애니메이션에 입힌다. 256에서는 최대 3프레임 | 256: 25 |
| 인페인팅 | `inpaint-v3` | 마스크 부분만 다시 그리고 나머지는 그대로 둔다. Tier 1은 변당 256까지 | 10 |
| 회전(구형) | `rotate`, `generate-8-rotations-v3` | 방향을 바꾼다. 구형 rotate는 128 이하만 가능 | – |
| 리사이즈 | `resize` | 픽셀아트를 다시 그려 크기를 바꾼다. **면적이 200×200 이하만 가능**하고, 한 번에 2배 확대 또는 50% 축소까지 권장 | 우리가 써 보니 1 |
| 스타일 참조 생성 | `generate-with-style-v2` | 스타일 그림 1~4장의 화풍으로 새 에셋을 만든다 | 171~256px이면 1장에 10 |
| 타일셋/맵 | `create-tileset`(Wang 16/25타일), `create-tiles-pro`, `map-objects` | 하단·상단 지형 전환 타일, 맵 오브젝트 | 표준 1~4, Pro 10~25. 실패한 작업은 과금 안 됨 |

※ 모든 생성은 비동기다. `background_job_id`를 받아 `GET /background-jobs/{id}`로 상태를 확인한다. 잔액은 `GET /balance`로 본다(무료).

## 2. 웹 vs Aseprite/Pixelorama vs API
- **웹 Characters(캐릭터 생성기)**: 4/8방향 캐릭터와 한 번 클릭으로 걷기·달리기를 만들고 미리 본다. 빠른 시안에 적합하다.
- **Pixelorama(브라우저 편집기)·Aseprite 확장(v1.3 이상, 체험판 불가)**: 인페인팅 레이어, 스켈레톤 편집, init image 강도 조절, Edit animation, Transfer outfit, Resize처럼 **손으로 고치며 반복하는 도구**는 여기에만 있거나 여기서 더 잘 된다.
- **API/MCP**: 일괄 생성, 시드와 요청 기록, 예산 상한 관리. 우리처럼 4방향 × 여러 모션을 찍어낼 때 쓴다. 동시 작업 한도는 Tier 1에서 8개이고 넘으면 429가 나는데, 429는 과금되지 않는다.

## 3. 비용 감각 (문서 + 우리 실측)
- 256 v3 애니메이션: 8프레임 **8**, 4프레임 **4**, 6프레임(시작 포함 7장) **6**. 1프레임당 1이라고 보면 된다. 4방향 × 8프레임 한 모션이면 약 **32**.
- 256 애니메이션 편집(4프레임): **25**. 비싸므로 "다시 뽑기"보다 "꼭 필요한 4프레임만 고치기"에 쓴다.
- 256 이미지 편집(Pro): **10**. pixen 편집: **1**. 리사이즈: **1**.
- 캐릭터 회전: 256 참조 생성 **8**. 방향 그림을 모두 넣어 가져오기만 하면 **0.25**.
- 256에서 frame_count 10을 보내면 422("max frame_count: 8")가 나고 과금되지 않는다. 동작이 길면 4~8프레임 클립 여러 개로 나누거나 end_frame으로 이어 붙인다.
- 시험 단계에서는 128 캔버스에서 동작을 잡은 뒤 256으로 올리는 것이 싸다. 128에서는 8프레임에 약 4, 편집에 10이 든다.

## 4. 프롬프트 패턴 (잘 먹힌 것)
1. **디자인 설명을 매번 통째로 붙인다.** 예: "Same character in every frame: long straight black hair, dark coat with gold trim, cape with red lining, gold pauldron, same face, same proportions and same size as the idle image; longsword in the right hand. Feet stay on the same ground line." 이 문구가 빠지면 머리색, 옷색, 체형이 흘러간다.
2. **동작은 단계 순서대로 쓴다**: 예비 → 타격(+잔상) → 팔로스루 → 대기 자세로 복귀. 칼끝이 궤적을 이끌고, 잔상은 칼끝에 붙으며 앞쪽이 굵다는 식으로 우리 SWORD_ARC 규칙을 문장으로 옮긴다.
3. **방향 문구는 대문자로 강하게, 금지형도 함께 쓴다.**
   - 옆: "STRICT SIDE VIEW every frame: facing RIGHT in profile, chest never turns toward the camera; everything moves toward the RIGHT."
   - 뒤: "BACK VIEW every frame, face never shown … sword and arms stay visible beside or above the body; attacks go up the screen." 맞는 장면이나 피니시에는 "He NEVER turns around"를 추가한다.
   - 정면: "Front view facing the camera; attacks go toward the camera."
4. **잔상(스미어)·이펙트**: "a wide cyan-white crescent slash trail following the blade tip". 색이 몸까지 번지면 "The character's own body and colors never turn white or glow; only effects are bright."를 붙인다.
5. 길고 복잡한 문장보다 **짧은 동작 + 확실한 시작 포즈**가 낫다. 공식 팁(States 기능)도 같다. 대기 자세에서 바로 시작하지 말고, 예비 동작 포즈를 State나 custom_start_frame으로 먼저 만든 뒤 그 포즈부터 애니메이션을 만든다.

## 5. 우리가 겪은 함정과 대응
- **옆모습인데 몸이 카메라 쪽으로 돈다**(공격 정점, 맞는 동작, 대시): 3번의 STRICT SIDE / NEVER turns 문구를 넣는다. 그래도 돌면 그 프레임만 edit-animation으로 고치거나, end_frame을 옆모습 대기 자세로 고정한다.
- **뒷모습에서 돌아서 얼굴이 나온다 / 팔과 칼이 몸에 가려 안 보인다**: "face never shown"과 "sword and arms stay visible beside or above"를 넣고, 어깨 회전을 크게 하라고 쓴다.
- **디자인이 흘러간다**(머리가 파래짐, 옷이 밝아짐, 다른 사람이 됨): 디자인 설명 전체 + "never changes into a different character"를 넣는다. 고칠 때는 해당 프레임만 이미지 편집(참조=대기 프레임)으로 맞춘다. 장당 10이 든다.
- **크기가 커진다**: 애니메이션 캔버스가 자동으로 커지고(64→84, 128→176), 편집이나 재생성 과정에서 인물도 커진다. 결과물마다 **발 기준선과 키 124px를 로컬에서 다시 맞추는** 후처리(bbox, 발 정렬)를 필수로 한다. 프롬프트에도 "same size as the idle image"를 넣는다.
- **반대편 장식이 뒤바뀐다**: 서쪽 방향에서 견갑이 반대쪽 어깨에 붙는다. 좋은 방향은 `direction_images`로 고정하고, 나쁜 쪽만 좌우 반전하거나 pixen 편집(1)으로 고친 뒤 가져오기(0.25)한다. 전체를 다시 뽑지 않는다.
- **히로인이 주인공을 베낀다**: 주인공 그림을 스타일 참조로 쓸 때 히로인 디자인 설명을 빼면, 얼굴·옷·칼까지 주인공처럼 나온다. 참조는 화풍용으로만 쓰고 **본인 외형 설명은 항상 끝까지 쓴다.**
- **재시도가 결과를 덮어쓴다**: 같은 이름과 경로로 다시 돌리면 이전 후보가 사라진다. 출력 경로에 **태그·방향·시드를 반드시 넣는다**(예: `_cand/<tag>/<motion>/<dir>_s<seed>/`). 서버에서도 같은 animation group의 방향은 409가 나므로 새 이름이나 그룹으로 만든다.
- 기타: "heavy load" 실패가 나면 잠시 후 다시 시도한다. 결과 PNG 다운로드는 User-Agent가 없으면 403이 난다. API 키는 환경변수로만 쓰고 로그에서는 가린다.

## 6. 권장 작업 흐름 (우리 게임용)
1. **베이스 캐릭터**: 정면 기준 그림(124px/256, 발 위치 고정, 눈색 등 확정)으로 `create-character-v3`(4방향, 8)를 돌린다. 방향마다 정지 그림을 검수하고, 틀린 방향만 고친 뒤 가져오기(0.25)로 확정한다. **애니메이션 전에 4방향 정지 그림부터 승인받는다.**
2. **모션별 생성**: 한 번 호출에 한 방향씩, 256·8프레임(8)으로 만든다. 프롬프트는 [동작 단계] + [방향 문구] + [디자인 공통 문구]로 짠다. 시드 2~3개를 후보로 뽑는다(4방향 × 3시드 ≈ 96). 공격처럼 대기 자세로 돌아와야 하는 동작은 `end_frame`=대기 자세로 둔다. 걷기·달리기·대기처럼 디자인이 중요한 반복 동작은 skeleton-v3/template(저렴, 디자인 유지)도 비교해 본다.
3. **선별·정렬(로컬, 무료)**: 시트와 GIF로 비교한다. 발 기준선과 키를 정규화하고, 잔상은 가능하면 별도 FX 레이어로 둔다(MOTION_RULES).
4. **수정**: 문제가 4프레임 안에 있으면 edit-animation(25). 한두 장이면 이미지 편집 Pro(10, 참조=대기 프레임). 작은 부위면 pixen 편집(1)이나 인페인팅(10). 전체를 다시 뽑는 것은 마지막 수단이다.
5. **기록**: run.log에 요청, 시드, 사용량, 잔액을 남기고 작업마다 예산 상한(예: 400)을 둔다.

## 출처
- https://www.pixellab.ai/docs , /docs/ways-to-use-pixellab , /docs/faq , /docs/guides/rotating-a-character
- https://www.pixellab.ai/docs/tools/animate-with-text-new , /tools/animate-with-text-pro , /tools/animate-with-skeleton , /tools/animation , /tools/animation-to-animation
- https://www.pixellab.ai/docs/tools/edit-animation-pro , /tools/edit-image-pro , /tools/inpaint-v3 , /tools/resize , /tools/consistent-style , /tools/create-8-rotations-pro , /tools/transfer-outfit-pro , /tools/create-tileset
- https://api.pixellab.ai/v2/docs , https://api.pixellab.ai/v2/openapi.json , https://api.pixellab.ai/v2/llms.txt
- YouTube "This Feature Saves Hours of Animation Work"(States): https://www.youtube.com/watch?v=OZWtWFBeGCA
- Reddit r/aigamedev 작업 흐름 토론: https://www.reddit.com/r/aigamedev/comments/1wo6frq/best_aiworkflow_for_pixel_art_characters_and/
- 내부: town-demo/char_v4/pixellab/hero/NOTES.md, hero/v3gen_20261018/tools/*.py와 */run.log, heroines_v4px_20261018/*, yt_study/MOTION_RULES_ko.md, yt_study/sword/SWORD_ARC_RULES_ko.md
