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

## ★ 실제 모션캡처로 뼈대 만들기 (권장, 2026-10-19)
공식으로 지어낸 뼈대보다 실제 사람 동작을 쓰면 훨씬 자연스럽다.
- 데이터: CMU 모션캡처 BVH(Bruce Hahne 변환판). `READMEFIRST.txt`에 "연구와 상업 프로젝트 모두 무료, 제한 없음"이라고 되어 있다. 크레딧에 CMU를 표기하는 것을 권장한다.
  - 받는 곳: `https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data/0SS/SS_NN.bvh` (예: `data/009/09_01.bvh`, 빠른 달리기)
- `bvh.py`: BVH를 읽고 관절의 3D 위치를 계산한다.
- `cycle.py`: 왼발 착지에서 다음 착지까지 한 주기를 잘라, 제자리 달리기로 바꾸고 N장으로 다시 나눈다.
- `retarget.py <bvh> <출발그림_kp.json> <out.json> 12 RIGHT`: 각도는 모션캡처에서, 뼈 길이는 캐릭터 출발 그림(estimate-skeleton)에서 가져온다. 무기 든 팔은 출발 자세로 고정하고, 발은 바닥에 맞춘다.
- `retarget_x.py ... RIGHT 18 1.25`: **과장**을 넣는다. 상체 18도 숙이기, 다리 휘두름 1.25배. 이스8처럼 역동적으로 보이게 하는 용도다.
- 나머지 과정은 위와 같다: `animate_skel.py`(3 크레딧) → 키 중앙값과 발 위치를 맞춘다.
- 정면·뒷모습은 같은 3D 동작을 카메라만 돌려 투영하면 되므로, 4방향의 박자와 동작이 같아진다(투영 함수 `P2`를 바꿔서 쓴다).
