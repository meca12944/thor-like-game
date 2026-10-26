# 3D 캐릭터 교본 (고도 2.5D) — 팀장, 2026-10-26

> 사장님 10-26: 「2D 도트 느낌이 아니라 2D처럼 부드러운 게 맞다」 「초안부터 얼굴이 잘못 나왔다. 여기에 우리가 경험이 없다. 팀원들과 캐릭 2.5D로 잘 뽑는 법 회의 10분, 연구하고 와라.」
> 회의(10분): 팀장 + 조사 팀원 3(화풍 / AI 인형 만들기 / 고도 코드). 팀원 방 연결이 끊겨 조사 팀원을 새로 불러 진행.

## 0. 이번에 틀린 것 (원인)
1. 입력 그림을 「얼굴이 잘 나오는 조건」으로 준비하지 않음 — 7등신, 머리카락이 얼굴을 덮음, 원근 있는 설정화.
2. 빛 코드 실수 — light()에서 ALBEDO를 또 곱하고, LIGHT_COLOR에 PI가 들어 있는데 안 나눔 → 얼굴·손이 하얗게 날아감.
3. 7등신 인형의 뼈를 키워 꼬마로 만듦 → 얼굴·옷이 늘어나고 머리카락 덩어리만 커짐(틀린 방법).
4. 키 110~160px 캐릭터의 얼굴은 15~20px — AI 3D 얼굴은 이 크기에서 안 읽힘(구조적 한계).

## 1. 결론 — 다음 판 순서
1. **입력 그림 = 그록 설정화 그대로 (사장님 10-26 「7~8등신으로 가야 돼」)**: 꼬마 비율 안 씀. 정면·옆·뒷면 원근 없이 같은 크기, 고른 빛, 한 색 바탕, A자세(팔 살짝 내림), 1024px 이상, **머리카락을 얼굴 뒤로 넘겨 이마·눈이 보이게**, 눈 크고 진하게, 망토 짧게, 칼 없음.
2. **Meshy 설정 (시험 9에서 확인)**: ai_model `meshy-7.1`, Multi-Image(앞·옆·뒤, 흰 바탕), 그림과 같은 자세(`t-pose`), `image_enhancement:false`(그림 모습 그대로), `remove_lighting:true`, **`texture_image_urls`에 같은 앞·옆·뒤 그림**(글 설명 대신 그림으로 색칠 → 옷·망토 색이 설정화와 거의 같음), 4K. 비율은 그림 그대로 — 뼈 크기 키우기 금지. 몸 정리(remesh) → 관절 → 움직임.
3. **얼굴은 AI에 맡기지 않음 — 설정화 앞모습을 머리에 비춰 입히기 (시험 9, 크레딧 0)**: 불러올 때 정점마다 UV2 = 그림 자리(인형 키 = 그림 키 918px, 머리 가운데 맞춤), COLOR.g = Head 뼈 무게 × 앞쪽 → 셰이더가 그 자리에 그림(art_front.png)을 그대로 칠함. 앞에서 보면 설정화 얼굴 그대로. 위에서 내려다보는 카메라라 머리를 15도 들어 줌(HEAD_UP).
   - 주의: Meshy 인형은 Skin 이름이 비어 있음 → 뼈 이름은 Skeleton에서 `get_bone_name(get_bind_bone(i))`로 찾기(시험 8까지 얼굴 표시가 안 걸렸던 원인).
   - (예전 계획) 눈·눈썹·입을 2D 그림으로 따로 붙이기: 눈·눈썹·입을 2D 그림(그록 얼굴 8방향 그림 활용)으로 얼굴 앞에 따로 붙임(얼굴 판/데칼). 얼굴은 그림자 없이 평평하게, 테두리 빛 끔, 밝기 상한 0.95.
   - 고도에서 얼굴 찾기: 불러올 때 정점마다 Head 뼈 무게 → 정점 색 COLOR.r(UV 자리는 AI 모델이라 믿지 않음).
4. **빛 셰이더**: light()에서 ALBEDO 곱하지 않기, `LIGHT_COLOR / PI`, 2칸(밝음/그림자) + 그림자 색은 검정 대신 보랏빛·따뜻한 갈색, 텍스처 `source_color`, 해 하나·세기 1, tonemap Linear.
5. **외곽선**: 뒤집은 껍질, 화면 픽셀 굵기 일정, 얼굴 안쪽(COLOR.r)은 0.2배.
6. **움직임**: 부드럽게 재생(사장님 결정, 12장 끊기 안 씀). 공격만 준비 이음(천천히 시작) + 맞는 순간 0.06초 멈춤 + 잔상·눌림.
7. (나중 선택) 하데스식: 3D를 방향별 2D 그림 묶음으로 미리 찍고 얼굴만 손으로 고치기 — 가장 확실·가벼움, 일은 늘어남.

## 2. 출처
- 길티기어 Xrd GDC: https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf
- 하이파이 러쉬 툰: https://80.lv/articles/the-making-of-hi-fi-rush-s-3d-toon-rendering-style
- 고도 애니 얼굴 셰이더: https://godotshaders.com/shader/anime-style-face-shader/
- SDF 얼굴 그림자: https://destiny-fine-0ac.notion.site/SDF-Shadowmap-9527f23116aa42dc89e3c9e17a54ddf3
- 고도 4.3 spatial 셰이더: https://docs.godotengine.org/en/4.3/tutorials/shaders/shader_reference/spatial_shader.html
- Meshy Multi-Image: https://docs.meshy.ai/api/multi-image-to-3d.md · 변경 기록 https://docs.meshy.ai/api/changelog · 관절 https://docs.meshy.ai/en/webapp/guides/3d-model/rigging

## 3. 검흔 = 칼이 지나간 길 (사장님 10-26 「3D니까 검흔이 따로 나올 필요 없잖아, 이제 자유롭게 표현되니까」)
- 주인공 보통 공격의 검흔은 따로 그린 2D 베기 그림을 쓰지 않는다. 3D 칼끝·칼밑이 실제로 지나간 길을 띠로 그린다(코드, 그림에 굽지 않음).
- 그래서 베기 동작을 고르는 기준 = **칼이 그리는 길이 크고 시원한가**(위→아래, 옆으로 쓸기, 한 바퀴 등). 동작만 바꾸면 검흔도 저절로 맞는다.
- 아틀라스로 굳혀도 같다: 찍을 때 칸마다 칼끝·칼밑 자리를 함께 저장(atlas.json tips) → 게임에서 그 자리로 검흔을 그림.
- 칼 길이·굵기·색·남는 시간·멈칫 때 번쩍임은 숫자로 조절. 날아가는 검기(멀리 베기)만 따로 만든다.

## 4. 2시간 회의·연구·개발 (2026-10-26, 사장님 「팀원들하고 회의·연구·검색·개발 2시간, 크레딧 200 안에서 주인공 자유롭게, 설정화처럼 최대한 2D 작화처럼」)
- 참석: 팀장 + 조사 팀원 3 (그림 표현 / 움직임 / 3D 인형). 팀원 방 연결이 끊겨 조사 팀원을 새로 불러 진행.
- 크레딧: 새 인형 2개 시험 70 + 몸 줄이기 5 + 관절 5 + 동작 12개 36 = **116** (잔액 704).

### 결론 (순서 = 효과 큰 순)
1. **설정화로 다시 칠하기 (가장 큰 효과, 크레딧 0)**: `godot25d/art_bake.py <인형.glb> <앞> <옆(오른쪽 봄)> <뒤> <출력.png>` — 인형이 그림과 같은 T자세라서, 색 그림 칸마다 앞·뒤·양옆 그림에서 그 자리 색을 가져옴(깊이로 가려진 곳 거름, 법선 방향 무게). 20초. 설정화의 붓 자국·주름·테두리가 그대로 올라감 → `art/art_bake.png`. 그림에 그림자가 이미 있으니 게임 그림자는 얕게(shade_tint 0.84,0.8,0.9).
2. **새 인형 = 한 장(앞모습) 그림으로 만들기**: Image-to-3D, meshy-7.1, `should_remesh:false`, `geometry_resolution:"2k"`(35), 입력은 같은 크기·여백 10%·1024px 정사각. 앞·옆·뒤 3장보다 **망토 폭·머리숱이 설정화와 비슷**. 그 뒤 Remesh 40000(5) → 관절(5) → 동작. 뒷면이 짐작이어도 1번으로 다시 칠하니 괜찮음.
3. **머리·머리카락 둥근 빛**: 머리 뼈 무게(COLOR.b)만큼 법선을 머리 가운데에서 바깥 방향으로 → AI 인형의 울퉁불퉁한 그림자 조각이 사라짐(head_c 매 프레임).
4. **아틀라스로 굳히기**: 2배 크기(1600px)로 찍고 묶을 때 절반으로 줄임 → 테두리가 그림처럼 부드러움. 방향 4개를 동시에 찍어 8분(`BAKE=1 BAKE2X=1 BAKEDIRS=down` …, `PACK_SCALE=0.5 python3 pack_atlas.py`). 그림판은 비스듬히 서 있어 발끝이 땅에 잘림 → `no_depth_test`.
5. **칼**: 임시 막대 → 쇠색 날·구리색 코등이·짙은 가죽 손잡이(설정화 색). 진짜 칼 인형은 다음.
- 안 하기로 한 것: 셰이더에서 그림을 실시간으로 비추기(움직이면 미끄러짐 — 얼굴만 예외로 유지), 길티기어식 UV 선(UV를 다시 펴야 함), 실시간 화면 외곽선 후처리(무거움).

### 출처
- 길티기어 Xrd GDC https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf · 하데스 3D→2D https://steamcommunity.com/app/1145360/discussions/0/1738883810796606862 · 그랑블루 릴링크 https://blogs.autodesk.com/media-and-entertainment/2024/11/27/granblue-fantasy-relink-brings-iconic-2d-aesthetics-into-3d-with-flexible-creative-tools/ · 하이파이 러쉬 https://80.lv/articles/the-making-of-hi-fi-rush-s-3d-toon-rendering-style · Meshy 문서 https://docs.meshy.ai/api/image-to-3d.md , https://docs.meshy.ai/api/remesh.md , https://docs.meshy.ai/api/pricing.md
