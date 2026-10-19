# 뼈대(스켈레톤) 방식 이동 모션 — PixelLab animate-with-skeleton-v3

걷기·달리기 같은 반복 동작은 이 방식이 가장 낫다(2026-10-19 주인공 달리기로 검증, 사장님 OK).
디자인과 얼굴이 유지되고 4방향 박자가 같다. 비용은 12장에 3, 15장에 4 크레딧.

1. `run_ref.py` 출발 그림: 대기 그림을 참조로 `edit-images-v2 edit_with_reference`(10)를 돌려 "같은 캐릭터, 달리는 자세, 무기 위치"만 고친다.
   - 반드시 **진짜 캐릭터 그림**에서 출발한다. 따로 생성한 후보 그림에서 출발하면 디자인이 달라진다.
2. `POST /v2/estimate-skeleton`: 출발 그림의 18관절을 얻는다(0.1).
3. 프레임별 관절 좌표 만들기
   - 옆모습: `runcycle_ref.py` (무기 든 팔 고정, 반대 팔 흔들기, 몸 숙임)
   - 정면·뒷모습: `runcycle_fb.py <kp.json> <out.json> 12`
4. `animate_skel.py <first.png> <first_kp.json> <frames_kp.json> <east|south|north> <outdir> <seed>`
5. 게임에 넣기: 몸 키 중앙값을 기존 모션(약 119px)에 맞추고, 발을 (128,189)에 맞춘다. 왼쪽은 오른쪽을 반전한다.

※ 스크립트 안의 경로는 1번 작업방 임시 폴더 기준이므로 각자 고쳐 쓴다. 키는 환경변수 `PIXELLAB_API_KEY`로만 쓴다.
