# 몬스터 대기(가만히 서 있기) 애니 v1 (2026-10-20, 저장만 · 게임 미적용)
- 원본: art/mobs/mobs_01~07.jpg 의 42종 대기 자세(칸 왼쪽) + town/assets_src/world/mobs_field.jpg 들판 5종 = 47종.
- 방법(크레딧 0, tools/anim/mobidle/idle.py): 배경색 제거 → 대기 자세만 떼어 → 코드로 8장 반복 대기 애니. 도트가 번지지 않게 줄 단위로만 늘이고 줄임.
  - breathe(숨쉬기, 30종): 발 기준 위아래 2% 늘었다 줄었다 / blob(슬라임·복어): 말랑하게 5% 찌그러짐
  - float(날짐승·정령·해파리·망령): 4px 위아래 둥실 / sway(새싹·버섯): 윗부분이 좌우로 흔들 / still(석상·골렘·항아리): 아주 작게
- sheets/<id>.png = 가로 8장(칸 크기 = manifest.json 의 w,h), 8fps 권장. 영상 monster_idle_all.mp4.

## 공격 모션 v1 (같은 날 추가)
- tools/anim/mobidle/attack.py: 대기 → 준비(움츠리며 뒤로) 2장 → 시트의 공격 자세로 튀어나감(앞으로 밀며 늘어남) → 흔들리며 유지 → 대기로 돌아옴. 12장.
- 공격 자세는 시트 칸 오른쪽 그림 그대로(투척물·레이저·물보라 등 포함), 발 높이와 몸 뒤쪽 끝을 대기 자세에 맞춰 겹침.
- 들판 5종(공격 자세 없음)은 대기 그림으로 몸통 박치기(뒤로 움츠렸다 앞으로 돌진).
- atk/<id>.png = 가로 12장, atk_manifest.json = 칸 크기·발 위치(foot)·장별 틱(ticks, 60fps)·타격 장(hit=4). 영상 monster_idle_attack.mp4 (대기 2바퀴 → 공격 반복).
