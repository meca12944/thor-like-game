# 이야기 그림을 그록에 맡길지 — 회의 결과 (2026-10-24, 팀장 마을배경방)

결론: **큰 감정 장면 4장만 그록 고해상 일러스트로 바꾸고, 물건 클로즈업·작은 장면은 지금 도트 그대로.**
- 그록 장점: 한 장 1536×864, 얼굴·감정·빛이 살아 있음. 사장님이 고른 대표 그림(그록 펠트)과 같은 화풍 → 세계관이 하나로 묶임.
- PixelLab 한계: 한 장 400px(게임 그림 384×216) → 인물 얼굴·표정이 뭉개짐. 컷신에서 가장 손해.
- 위험: 그록은 캐릭터 모습이 장마다 달라짐 → **기준 그림을 꼭 같이 주고, 게임 그림과 나란히 검수**.

## 바꿀 4장 (우선순위)
1. 기억 조각 — 불타는 왕도 한가운데 선 주인공, 가슴에서 붉은 실
2. 아라크네 최후 — 실이 풀리며 무너지는 아라크네, 칼 내린 주인공
3. 리네트 첫 만남 — 무너진 왕실 의상실, 바늘 둘 들고 돌아보는 리네트
4. 펠트 도착 — 언덕 위 뒷모습 + 불탄 왕성 (대표 그림과 같은 시점)
(도트 유지: 펠릭스 목도리, 폐공방 문 앞, 숨은 방 아라크네의 과거는 2차 검토)

## 순서
1. **캐릭터 시트 먼저** (그록 3장): 주인공·리네트·아라크네 각각 정면·옆·뒤 한 장. 기준 그림 = 주인공 `handoff/claude/hero_v6_mini/ref/turnaround_v7.jpg` + 게임 도트, 리네트 게임 도트(정면 원화 없음), 아라크네 `art/mobs/arachne/arachne.png` + `test128/assets/portraits/c1_arachne.png`. 사장님 OK 받은 시트만 이후 기준.
2. 장면 4장: 아래 프롬프트 + 캐릭터 시트를 같이 넣기, 16:9 (1536×864).
3. 받으면 팀이 넣기(크레딧 0): 우리 32색 쪽으로 색 보정·채도 낮춤, 모서리 어둡게, 아주 옅은 알갱이, 검은 띠 + 가는 붉은 실 테두리, 아래 1/3 어둡게(대화창), WebP 200~400KB, 지역 들어설 때 미리 불러오기, 큰 그림은 부드럽게 그리기. 그림 위 효과(불씨·붉은 실)는 그대로.

## 꼭 지킬 특징
- 주인공: 길고 검은 머리, 남색 코트, **금색 어깨받이**, 붉은 안감 검은 망토, 장검 **오른손**·칼날 보임.
- 리네트: 금발 포니테일 **파란 리본**, 붉은 상의·치마, **은색 긴 바늘 둘**, 주인공 키의 89%.
- 아라크네: **나무 실패 몸통(강철색 실)** + 바늘 끝 다리 8, 창백한 여자 윗몸, 긴 검은 머리, 낡은 회색 재봉 앞치마, 녹슨 큰 가위, 허리 이음새 **붉은 바늘땀**. 붉은 실 = 늘 아라크네의 실.

## 그록 프롬프트 (복사해서 쓰기, 캐릭터 시트 그림 같이 넣기)
공통 끝말: `dark fantasy, painterly semi-realistic illustration, muted sepia and ash grey palette with a single accent of glowing red thread, cinematic lighting, 16:9, no text`

1. 기억 조각: `A tall swordsman with long black hair, navy coat with gold shoulder guards and a black cape lined in red, holding a longsword in his right hand, stands alone in the middle of a burning royal capital at night. Towers collapse in flames around him. Glowing red threads burst from his chest and spread into the burning city like veins. His face is half in shadow, expressionless. Low angle, epic and tragic.`
2. 아라크네 최후: `A monstrous tailor: a pale woman's upper body stitched with red stitches onto a giant wooden thread-spool spider body with eight needle-tipped legs, long black tangled hair, worn grey sewing apron, rusty giant shears on the floor. She collapses as her threads unravel into falling ash and white silk, her face finally peaceful and sad. A swordsman (long black hair, gold shoulder guards, black cape) stands nearby with his sword lowered. Dark lair lit by dim red light, hanging cocoons.`
3. 리네트 첫 만남: `A young blonde seamstress with a ponytail tied with a blue ribbon, red top and skirt, holding two long silver needles like weapons, turns around startled inside a ruined royal tailor's workshop. Torn noble gowns on headless mannequins, faded drapes, dust in a shaft of light from a broken arched window. Brave but scared expression.`
4. 펠트 도착: `Seen from behind, a tall swordsman with long black hair and a black cape lined in red stands on a hill of ash at dusk, looking down at a poor ruined slum village built at the foot of a huge burned royal castle. Thin smoke rises, embers float in the air. Lonely and ominous.`
