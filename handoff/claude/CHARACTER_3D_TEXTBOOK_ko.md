# 3D 캐릭터 교본 (고도 2.5D) — 팀장, 2026-10-26

> 사장님 10-26: 「2D 도트 느낌이 아니라 2D처럼 부드러운 게 맞다」 「초안부터 얼굴이 잘못 나왔다. 여기에 우리가 경험이 없다. 팀원들과 캐릭 2.5D로 잘 뽑는 법 회의 10분, 연구하고 와라.」
> 회의(10분): 팀장 + 조사 팀원 3(화풍 / AI 인형 만들기 / 고도 코드). 팀원 방 연결이 끊겨 조사 팀원을 새로 불러 진행.

## 0. 이번에 틀린 것 (원인)
1. 입력 그림을 「얼굴이 잘 나오는 조건」으로 준비하지 않음 — 7등신, 머리카락이 얼굴을 덮음, 원근 있는 설정화.
2. 빛 코드 실수 — light()에서 ALBEDO를 또 곱하고, LIGHT_COLOR에 PI가 들어 있는데 안 나눔 → 얼굴·손이 하얗게 날아감.
3. 7등신 인형의 뼈를 키워 꼬마로 만듦 → 얼굴·옷이 늘어나고 머리카락 덩어리만 커짐(틀린 방법).
4. 키 110~160px 캐릭터의 얼굴은 15~20px — AI 3D 얼굴은 이 크기에서 안 읽힘(구조적 한계).

## 1. 결론 — 다음 판 순서
1. **입력 그림 다시 (그록)**: 4~4.5등신 꼬마 비율, 정면·옆·뒷면 원근 없이 같은 크기, 고른 빛, 한 색 바탕, A자세(팔 살짝 내림), 1024px 이상, **머리카락을 얼굴 뒤로 넘겨 이마·눈이 보이게**, 눈 크고 진하게, 망토 짧게, 칼 없음.
2. **Meshy 설정**: ai_model `meshy-7.1`(latest), Multi-Image, `pose_mode:"a-pose"`, `image_enhancement:false`(깨끗한 그림은 끄기), `remove_lighting:true`, texture_prompt에 「큰 애니 눈, 뚜렷한 눈썹·입」. 꼬마 비율은 **처음부터 그림으로** — 뼈 크기 키우기 금지. 몸 정리(remesh) → 관절 → 움직임.
3. **얼굴은 AI에 맡기지 않음**: 눈·눈썹·입을 2D 그림(그록 얼굴 8방향 그림 활용)으로 얼굴 앞에 따로 붙임(얼굴 판/데칼). 얼굴은 그림자 없이 평평하게, 테두리 빛 끔, 밝기 상한 0.95.
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
