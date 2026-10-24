# 이야기 그림 위 효과 v1 (CG 회의 10-24 결론, 이펙트 담당) — 브랜치 claude/scene-fx (claude/linette-8dir 위), main 합치지 않음
`test128/world.js` SCENE_FX 표 + drawSceneFx (대화창 그림 drawDialog 안, 그림과 같이 1.00→1.03 확대 따라감). 모두 코드, 크레딧 0.
- 규칙(회의): 그림당 1종, 1~2px, 얼굴 위 금지, 처음 0.4초 정지 후 0.8초에 걸쳐 나타남, 붉은 실 색 = 2페이즈 실(THR) 하나.
- cg_felt_arrival · cg_memory_fire = 재·불씨 떠오름 / cg_arachne_end = 붉은 실 5가닥 흔들림 + 쿵-쿵(1.1초) / cg_linette_meet · cg_felix_scarf = 빛줄기 먼지 / cg_arachne_past = 촛불 둘레 따뜻한 먼지.
- cg_memory_fire 마지막 말(withArt 가 그 그림의 마지막 줄에 cgLast 표시): 가슴(151,102)에서 실 5가닥이 0.25초에 팽팽 → 하얀 번쩍 + 붉은 기운 0.35초.
- 새 그림 넣을 때: SCENE_FX 에 파일 이름(확장자 없이) 한 줄 — 좌표는 그림 픽셀 384x216.
영상 scene_fx_v1.mp4 (도착 → 리네트 → 마지막 기록 → 목도리 → 보스 처치 → 기억 조각 + 번쩍). test_openworld 17/17.
