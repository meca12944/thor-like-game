# hero_attack_thrust v2 — 찌르기 얼굴 색 + 전진 줄임 + 3타 얼굴 (게임 반영)
- 1·2타: v1 프레임에서 얼굴 피부만 첫 장 색으로 맞춤(그림에서 얼굴을 직접 찾음, 금색 갑옷 제외) → `frames/`, `tools/anim/apply_thrust_v2.py`(같은 칸에 덮어씀)
- 전진 H8.lunge: 18/22/32 → **0/0/16** (1→2→3타 실측 82 → 18). 1·2타는 그림이 앞으로 나감
- 3타: 동작 그대로, 얼굴 피부색만 맞춤(주황·노란 얼굴 → 1타 첫 장 피부색) → `tools/anim/apply_hit3_face.py`, 비교 `hit3_face_before_after.png`
- 공용 도구: `tools/anim/skin_match.py`
