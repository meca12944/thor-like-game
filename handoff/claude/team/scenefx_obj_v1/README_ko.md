# 경관 효과 물체 `scenefx` (효과 담당, 10-24, 새 1장 짓기 준비)

지도 JSON `objects` 에 넣으면 코드로 그려진다 (그림에 굽지 않음, 크레딧 0).
```json
{"type":"scenefx", "kind":"shade",   "x":40, "y":20, "w":24, "h":3, "arches":3, "ray":0.22, "slant":0.5}
{"type":"scenefx", "kind":"ashfall", "x":60, "y":10, "w":2,  "h":10}
{"type":"scenefx", "kind":"updraft", "x":20, "y":30, "w":8,  "h":4, "rise":42}
{"type":"scenefx", "kind":"thread",  "x":10, "y":40, "w":14, "h":-8, "sway":6, "red":true}
{"type":"scenefx", "kind":"lake",    "x":70, "y":40, "w":10, "h":6, "water":true, "a":0.8}
```
- 좌표는 타일, `x,y` = 왼쪽 위 (compose 지도에서도 부분 지도 좌표 그대로, 자동으로 옮겨짐). thread 는 (x,y) → (x+w, y+h) 선.
- 층: updraft·lake = 땅 위 인물 아래 / shade·ashfall·thread = 인물 위.
- shade: 수도교 그늘 띠 + 아치 사이 비스듬한 빛줄기(숨쉬듯 밝아졌다 어두워짐).
- ashfall: 좁은 기둥 안에서 빠르게 떨어지는 재 + 밑동 재 안개 (drawAshFall 과 같은 해시 방식).
- updraft: 구덩이(타원) 둘레에서 재가 안쪽으로 기울며 위로 빨려 오름 + 구덩이 어둠 (구덩이 그림이 오면 그림이 대신함).
- thread: 붉은 실 흔들림 + 심장 박동 빛 + 실 끝 반짝임 (threadLine·heartbeat 재사용).
- lake: 검은 물(water:false 면 땅 그림의 물 위에 비침만) + 비친 회색 하늘 + 거꾸로 비친 왕성 탑 임시 실루엣이 물결에 흔들림. 그록 탑 그림이 오면 `lakeTower` 만 바꾸면 됨.

비용 (CPU 4배, field_felt, 다섯 개를 한 화면에 모두 켬, 6초 프로파일 3번): 한 장면 0.85 / 0.89 / 0.90ms → 목표 1ms 아래.
하나씩: shade ~0.2, ashfall 0.19, updraft 0.19, thread 0.18, lake 0.28ms. 화면 밖 물체는 건너뜀. 그라데이션·그늘·물은 물체마다 한 번만 그려 두고 drawImage.
시험: test_openworld 17/17, 페이지 오류 0. 영상 `scenefx_v1.mp4` = 그늘·빛줄기 → 잿가루 폭포 → 구덩이 위 재 → 붉은 실 → 검은 호수 순.
