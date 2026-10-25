# 경관 시제품 효과: 먼 안개 띠 + 잿가루 바람 (검흔·효과, 10-24)
- `drawFarFog`: 화면 위쪽 38%에 아래로 옅어지는 안개 한 장 (1x64 그라데이션 캔버스를 한 번 만들고 drawImage 1번). `m.fog`(기본 .32), 전망 줌으로 물러나면(S.vz<1) 최대 2.2배까지 진해짐. 던전(m.dark)·ash 아닌 지도는 안 그림.
- `drawAshFall`: 바람 `m.wind=[x,y]` px/초 (기본 [9,0]) + 느린 돌풍, 개수 = `m.ash`(기본 46) x 화면 넓이 비례 (최대 160). compose 지도는 구역(area)의 wind·ash·fog 를 씀.
- 고친 버그: `updateCam` 의 `// look-ahead + hit kick clock` 주석이 같은 줄 뒤의 줌 코드를 삼켜 **viewZoom/구역 zoom 이 전혀 안 먹었음** (95da13a1 부터). → felt 마을 viewZoom 1.3 이 다시 켜짐 (화면이 1.3배 가까워짐), 전망 줌도 이제 작동.
- 비용 (CPU 4배, field_felt, 6초, `shot.js`): 두 함수 합계 한 장면 0.13~0.19ms (줌 1 / 0.72). 목표 1ms 아래.
- 시험: test_openworld 17/17. 영상 `vista_fog_ash_v1.mp4` (폰 가로 화면, 줌 1 → 0.72 → 1).
