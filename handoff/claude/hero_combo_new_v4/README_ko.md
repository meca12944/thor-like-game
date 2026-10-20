# hero_combo_new v4 (2026-10-20, 저장만 · 게임 미적용) — 8방향
- 옆(→/←): v1 그림(frames_side). 대각 ↘(se)/↗(ne): frames_diag/<hit>_<se|ne>_NN.png, ↙↖ = 좌우 반전.
- 대각 뼈대: skeleton/design34.py — 옆 설계를 3/4로 투영(앞 x*0.71, y±0.41), 몸 폭·머리·칼 든 손은 3/4 회전 키포인트(q34/se_kp, ne_kp). 빈손은 몸 뒤(손 교차 → 칼 손 바뀜 방지), 3타는 두 손이 칼자루 한 점에서 만나는 IK.
- 생성: PixelLab animate-with-skeleton-v3, 시작 = 3/4 회전 그림, 1→2→3 사슬 (skeleton/run_chain.sh).
- ↘ 3타: animate 결과에 PixelLab edit-animation-v2 로 양손 잡기 수정(11장, 75크레딧), 휘두르기 순서 재배열 [0,1,2,3,4,6,5,9,10,8,7,11,12,13,14].
- ↗ 3타: 10번 이후 몸이 화면 쪽으로 돌아서 10번에서 멈춤.
- 속도/효과: v3 와 동일 (빠른 연결, 1·3타 리네트 효과, 2타 없음). 영상 hero_newcombo_3dir_v3.mp4.
- 대각 작업 PixelLab 합계: 약 130 크레딧(실패 재생성 포함). 잔액 1,976 (PixelLab 확인).
