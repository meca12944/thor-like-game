# 옛 펠트 그림 보관 (2026-10-25, map-a7)

사장님 지시 「기존 구버전 그림 자료는 모두 이동시켜」 — 펠트 v5(tools/hd/fields/build_felt5.py → assets/world/felt5/)로 새로 그리면서
옛 펠트 전용 그림을 지우지 않고 여기로 옮겼다. 게임은 이 폴더를 읽지 않는다.

- 다른 맵이 함께 쓰는 그림(prologue_grave·필드)은 assets/world/felt/ 에 그대로 남겼다:
  g2_burnt_stump_a, g4_deadtree_1, g4_debris_0..3, g4_far_castle, g4_firepit, g4_gate_wall, mausoleum, rubble, sign_post, stone_low, tombs
- 옛 빌드 스크립트·원본 데이터: tools/hd/_archive_old_felt/ (build_felt.py, build_felt2~4.py, orig_felt.json, src_felt.json)
