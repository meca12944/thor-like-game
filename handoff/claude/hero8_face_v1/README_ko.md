# 주인공 얼굴 도장 v1 (모션연구방, 2026-10-23, 사장님 "주인공 얼굴이 모션마다 일정치 않아")

- 원인: 동작마다 따로 그린 그림(시트 7종: idle·fix·front·move2·cast·jump·death)이라 그림 도구가 얼굴을 매번 새로 그림 + 동작마다 크기 배율이 달라(정면 96%, 새 걷기 0.93~1.0) 몇 칸짜리 얼굴의 눈·코가 달라짐 + 밝기도 다름(피부 빨강 215~239).
- `apply.py`: 정면 `idle_down` 0번·옆 `idle_right` 0번 얼굴(+앞머리 2칸)을 걷기·달리기·대시·점프·시전 모든 장에 맞춰 찍음(`facefix.py place2`: 피부 모양이 가장 많이 겹치는 자리, 안 맞으면 안 찍음). 맞기·쓰러지기는 표정이라 그대로. 새 시트 `hero8_face.webp`.
- 확인: `motion_lab/research_v1/videos/hero_faces_before_after.png`, `hero_face_v1.mp4`, 들판·마을·test_place_all 오류 0.
