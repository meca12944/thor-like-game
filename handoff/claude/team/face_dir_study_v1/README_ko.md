# 얼굴 또렷하게 + 8방향 크기 맞추기 공부 (검흔 담당, 10-25, 사장님 「유튜브에서 학습하고 와」, 크레딧 0)

## 먼저: 유튜브는 직접 못 봤음 (정직하게)
- 이 작업실에서 유튜브 영상·자막을 열면 유튜브가 「로봇 확인」(로그인 요구)으로 막음 (yt-dlp · 페이지 · 자막 모두). 그래서 **영상 내용은 요약하지 않음**.
- 확인된 것은 제목·채널뿐 (유튜브 oembed로 확인). 사장님·모션 담당이 폰에서 직접 볼 만한 목록:
  | 제목 | 채널 | 주소 |
  |---|---|---|
  | Draw Tiny Faces in Just 5 Steps / Pixel Art Loomis Method in 32x32 | boogerboy12 | https://www.youtube.com/watch?v=ia21Fm9Ery8 |
  | How to draw a face in pixel art - Pixel art tutorial - Miguel | Jep Jep | https://www.youtube.com/watch?v=jpTGFL1jrtg |
  | Aseprite: How to Draw a Face from Scratch / Tutorial | Things Zone | https://www.youtube.com/watch?v=9erBhgR2PWg |
  | Pixel Art Class - 8 Directional Walk [Part 1] | AdamCYounis | https://www.youtube.com/watch?v=aios4kDJZsc |
  | Pixel Art Class - 8 Directional Walk [Part 2] | AdamCYounis | https://www.youtube.com/watch?v=jUaytU-XJ-U |
  | Pixel Art Tutorial - Character 4 Directions | Adventure Game Dev | https://www.youtube.com/watch?v=OYgh-FrAek4 |
  | Pixel Art Character Design Tutorial - Step By Step! | Saultoons | https://www.youtube.com/watch?v=vXm5VjZA4Ys |
- 대신 **같은 내용을 글로 쓴 강좌를 직접 읽음** (도트 강사 Raymond Schlitter = SLYNYRD, 유튜브 강좌 글판):
  - Pixelblog 55 Top Down Character Animation (8방향): https://www.slynyrd.com/blog/2025/3/24/pixelblog-55-top-down-character-animation
  - Pixelblog 22 Top Down Character Sprites: https://www.slynyrd.com/blog/2019/10/21/pixelblog-22-top-down-character-sprites
  - Pixelblog 17 Human Anatomy (얼굴 비율): https://www.slynyrd.com/blog/2019/5/21/pixelblog-17-human-anatomy

## 1) 얼굴을 또렷하게 (읽은 것)
- 얼굴 자리 규칙 (Pixelblog 17): 눈 = 머리 꼭대기와 턱 가운데 / 얼굴은 머리선~턱을 3등분 / 코 밑 = 눈과 턱 가운데 / 입 = 코 밑~턱의 1/3~1/2 / 두 눈 사이 = 눈 하나 너비 / 입 너비 = 두 눈동자 사이.
- 작은 그림일수록 머리를 크게 (Pixelblog 22): 「작은 그림에서는 머리가 전체의 1/3~1/2」. 우리 5.5등신(키 120~150px)이면 머리 높이 22~27px, 얼굴(피부) 높이 약 13~16px → **눈 2~3px, 눈 사이 2~3px, 입 2~3px 한 줄**.
- 「작은 그림에서는 1px이 큰 차이」(Pixelblog 55) / 검색 글 요약: 눈 1px 옮기면 인상이 바뀜, 눈 하나는 3px 넘기지 않기 (pixnote · 포럼, 깊이 확인은 못 함).
- 얼굴 색: 피부 밝음·중간·그림자 + 눈 어두운색 + 눈 반짝임 정도로 적게 (Pixelblog 29 따라 그린 글: 피부 그림자 1색 · 테두리 · 눈 색 · 흰자).
- 머리카락 반짝임: 「모든 방향에서 같은 자리면 이상하고, 너무 튀면 시끄럽다 → 작은 폭으로 일정한 박자로」(Pixelblog 55).
- 장마다 얼굴이 안 바뀌게: 강사는 **장을 하나씩 손으로 비교하며 맞춤**. 망토·장비는 **따로 층**으로 그려 겹침 (Pixelblog 55 「cape and gear on a separate layer」).

## 2) 8방향 크기·키·머리 크기 맞추기 (읽은 것, Pixelblog 55)
1. 모든 방향의 **대강 그림을 한 장면에 나란히** 그리고, 서로 재면서 몸 크기·자리를 정함.
2. 모든 방향을 **같은 자리에 놓고 「제자리 돌기」 애니메이션으로 틀어 봄** → 나란히 볼 때 안 보이던 잘못이 보임. 돌기가 덜컹거리지 않을 때까지 고침. 「팔다리 두께·길이를 모든 방향에서 같게」.
3. 달리기도 **모든 방향을 원 모양으로 늘어놓고 박자를 맞춰 동시에 틀어 봄** → 머리 위아래(bob), 어깨 축, 팔다리가 가장 멀리 가는 곳을 장끼리 비교.
4. 머리 위아래 리듬 (6장 달리기): 앞 장 대비 아래 1px, 아래 1px, 위 2px (일정한 사인파보다 통통 튀게). 올라갈 때가 더 빠름.
5. 정면 → 뒤 → 옆 → 대각선 순서. 좌우가 같으면 옆·대각선은 뒤집어 5방향만 그림 (우리 주인공은 칼·머리가 비대칭이라 8방향 다 필요).
6. 크기 기준은 타일: 26x32px 몸 = 16px 타일 1x2 (Pixelblog 55). 남·녀·아이·노인 키를 정해 두고 지킴 (Pixelblog 22).

## 우리 방법과 다른 점 · 더할 것
| | 강좌 | 우리 (모션 담당 + 얼굴 도장) | 더할 것 |
|---|---|---|---|
| 얼굴 일정하게 | 손으로 장마다 비교·수정 | 방향별 정본 얼굴 1장을 도장으로 찍기 (C: 피부 자리만 + 밝기 맞춤) | 도장 전에 **얼굴 색을 5~6색 팔레트로 고정** (장마다 피부 빨강 155~165로 흔들리던 것 없앰) |
| 방향별 크기 | 같은 자리에 놓고 **제자리 돌기**로 틀어 보며 맞춤 | 걷기 키·발 위치로 배율 (clips.json) | **돌기 영상 검사**를 도구로: 8방향 서기 장을 발 189·가운데 128에 놓고 머리 꼭대기·눈 높이·어깨 너비를 숫자로 → 어긋난 방향만 고침 |
| 무엇으로 크기를 맞추나 | 팔다리 두께·길이, 머리 위아래 | 몸 키 | **머리 높이·눈 높이**로 맞춤 (앞 달리기 얼굴 11~16% 작음 = 몸 키로 맞춰서 생긴 것) |
| 동작끼리 | 원으로 늘어놓고 동시에 틀기 | 방향마다 따로 확인 | 걷기·달리기 8방향을 한 화면에서 같은 박자로 트는 검사 영상 |
| 망토·장비 | 따로 층 | 한 장에 구움 (PixelLab) | 지금은 그대로 (그림 도구 한계) — 얼굴만 도장 층으로 |
