# C_monsters — 1장 마물 (사멸의 궤적 / Trail of Extinction)

GenerateImage로만 생성 (PixelLab 미사용). 녹색(#00FF00) 배경 포즈 시트를 생성 → `_tools/process.py`로 크로마키(선형 알파+색 분리+녹색 번짐 제거), A_landscape 톤에 맞춘 그레이딩(채도 0.6, 세피아 0.10, 붉은 실만 채도 유지), 포즈별 분리·크롭(여백 4px).

- 모든 최종 파일은 투명 PNG. 이펙트(빛·불·안개·재·참격·마법) 없음, 몸만.
- `*_<pose>.png` = 원본 해상도 마스터, `*_<pose>_game.png` = 게임 크기(히어로 34px 기준, LANCZOS 축소, 알파<40 제거).
- 한 마물 안의 모든 포즈는 같은 배율(포즈 시트 공통 배율). 다른 생성본에서 가져온 포즈는 머리/몸 부위 크기를 재서 배율을 맞춤(README에 표기).
- 게임 크기 높이는 각 마물의 기준 포즈(표기) 높이를 목표 px로 맞춘 것. 무기 등이 튀어나온 포즈는 그보다 큼.
- `<폴더>_contact.jpg` = 확인용 컨택트 시트(위: 어두운 배경, 아래: 밝은 배경에서 같은 마스터를 보여 가장자리 확인용; 라벨에 마스터·게임 크기 px 표기). `_previews/` = 재 타일 위 게임 크기 미리보기(1x, 4x nearest), 빨간 막대 = 히어로 34px.
- #10 거울은 지시대로 제외.

## 전체 비교
- `_previews/all_monsters_side_game1x.png` (298x64), `_previews/all_monsters_side_game4x.png` (1192x256): 9종 side_stand 게임 크기 나란히 + 34px 히어로 막대.

## 1. 누빔 멧돼지 (Quilted Boar) — `01_quilted_boar/`
- 역할/크기: 돌진 네발짐승, 히어로 대비 약 1.0–1.1배 (side_stand 높이 34px 기준)
- 디자인: 누빈 자루천·숯빛 캔버스 몸통을 굵은 실로 꿰맨 멧돼지. 머리는 그을린 나무 실패(스풀), 엄니는 녹슨 바늘, 다리는 붕대 감은 나무 말뚝.
- 포즈: side_stand / front_stand / crouch(돌진 전 웅크림) / charge(돌진)
- 파일 (가로x세로 px):
  - `01_quilted_boar/m01_charge.png` 411x274
  - `01_quilted_boar/m01_charge_game.png` 43x29
  - `01_quilted_boar/m01_crouch.png` 327x295
  - `01_quilted_boar/m01_crouch_game.png` 34x31
  - `01_quilted_boar/m01_front_stand.png` 201x340
  - `01_quilted_boar/m01_front_stand_game.png` 21x36
  - `01_quilted_boar/m01_side_stand.png` 357x335
  - `01_quilted_boar/m01_side_stand_game.png` 37x35
  - `01_quilted_boar_contact.jpg` 1396x780
  - `_previews/01_quilted_boar_game1x.png` 208x64
  - `_previews/01_quilted_boar_game4x.png` 832x256
  - `01_quilted_boar/_meta.json` (포즈별 크기·배율 기록)
- 약점: crouch가 약하게 낮아짐(웅크림이 강하지 않음). 밝은 천 색이 중간 회색 재 바닥과 대비가 낮고, 34px에서 잉크 외곽선이 거의 사라짐.

## 2. 실묶음 허수아비 (Thread-Binder Scarecrow) — `02_thread_binder_scarecrow/`
- 역할/크기: 묶기형, 1.0배 (front_stand 34px)
- 디자인: 넝마 허수아비. 삼베 머리에 붉은 X자 바느질, 등에 실패, 길쭉한 바늘 손가락, 손에 붉은 실 타래.
- 포즈: side_stand / front_stand / throw_windup(실 던지기 준비) / throw_release(던지는 순간)
- 파일 (가로x세로 px):
  - `02_thread_binder_scarecrow/m02_front_stand.png` 261x496
  - `02_thread_binder_scarecrow/m02_front_stand_game.png` 18x35
  - `02_thread_binder_scarecrow/m02_side_stand.png` 201x498
  - `02_thread_binder_scarecrow/m02_side_stand_game.png` 14x35
  - `02_thread_binder_scarecrow/m02_throw_release.png` 429x485
  - `02_thread_binder_scarecrow/m02_throw_release_game.png` 30x34
  - `02_thread_binder_scarecrow/m02_throw_windup.png` 322x485
  - `02_thread_binder_scarecrow/m02_throw_windup_game.png` 22x34
  - `02_thread_binder_scarecrow_contact.jpg` 1313x1096
  - `_previews/02_thread_binder_scarecrow_game1x.png` 160x64
  - `_previews/02_thread_binder_scarecrow_game4x.png` 640x256
  - `02_thread_binder_scarecrow/_meta.json` (포즈별 크기·배율 기록)
- 약점: side_stand가 완전한 옆모습이 아니라 3/4에 가까움. throw_release의 늘어진 실이 일부 끊겨 보임. 게임 크기에서 몸이 가늘어 실루엣이 약함.

## 3. 바늘 사수 (Needle Marksman) — `03_needle_marksman/`
- 역할/크기: 저격형, 0.9배 (front_stand 31px)
- 디자인: 골무/양동이 투구를 쓴 작은 꼽추. 누더기 패치워크 망토, 석궁, 등에 귀 달린 재봉바늘 화살통.
- 포즈: side_stand / front_stand / aim(겨누기) / fire(쏘는 순간)
- 파일 (가로x세로 px):
  - `03_needle_marksman/m03_aim.png` 380x375
  - `03_needle_marksman/m03_aim_game.png` 31x30
  - `03_needle_marksman/m03_fire.png` 340x391
  - `03_needle_marksman/m03_fire_game.png` 27x31
  - `03_needle_marksman/m03_front_stand.png` 280x395
  - `03_needle_marksman/m03_front_stand_game.png` 22x32
  - `03_needle_marksman/m03_side_stand.png` 291x389
  - `03_needle_marksman/m03_side_stand_game.png` 23x31
  - `03_needle_marksman_contact.jpg` 1391x890
  - `_previews/03_needle_marksman_game1x.png` 176x64
  - `_previews/03_needle_marksman_game4x.png` 704x256
  - `03_needle_marksman/_meta.json` (포즈별 크기·배율 기록)
- 약점: 석궁은 평범한 석궁 모양(수틀 등 재봉 모티프 아님). 투구가 골무보다 양동이 투구처럼 읽힘. aim과 fire 차이가 크지 않음.

## 4. 철장 수문병 (Iron-Cage Warden) — `04_iron_cage_warden/`
- 역할/크기: 방패형 정예, 1.3배 (front_stand 44px)
- 디자인: 머리 없는 금 간 마네킹 상체, 녹슨 크리놀린(새장) 치마 안에 검은 넝마, 붉은 실로 묶은 나무 탑방패, 각진 망치(슬레지해머).
- 포즈: side_stand / front_stand / shield_guard(방패 든 서기) / slam_raise(내려찍기 준비) / slam_down(내려찍기)
- 파일 (가로x세로 px):
  - `04_iron_cage_warden/m04_front_stand.png` 281x428
  - `04_iron_cage_warden/m04_front_stand_game.png` 30x45
  - `04_iron_cage_warden/m04_shield_guard.png` 258x431
  - `04_iron_cage_warden/m04_shield_guard_game.png` 27x45
  - `04_iron_cage_warden/m04_side_stand.png` 188x455
  - `04_iron_cage_warden/m04_side_stand_game.png` 20x48
  - `04_iron_cage_warden/m04_slam_down.png` 265x345
  - `04_iron_cage_warden/m04_slam_down_game.png` 28x36
  - `04_iron_cage_warden/m04_slam_raise.png` 286x511
  - `04_iron_cage_warden/m04_slam_raise_game.png` 30x54
  - `04_iron_cage_warden_contact.jpg` 1398x1122
  - `_previews/04_iron_cage_warden_game1x.png` 208x80
  - `_previews/04_iron_cage_warden_game4x.png` 832x320
  - `04_iron_cage_warden/_meta.json` (포즈별 크기·배율 기록)
- 약점: side_stand는 별도 생성본을 크기 맞춤(0.4805배)해 넣어 선이 약간 더 깔끔함. 망치 머리가 발보다 아래로 내려와 바닥 기준선이 약 3px 어긋남. slam_raise는 망치 때문에 54px로 큼. 치마 철장 밑단에 작은 비침 틈이 일부 남음.

## 5. 가위 재단사 (Shear Tailor) — `05_shear_tailor/`
- 역할/크기: 폐공방 연속베기, 1.0배 (front_stand 34px)
- 디자인: 관절 나무 마네킹, 바늘꽂이 머리에 핀 다수, 앞치마와 줄자, 분리한 가위 두 날을 양손에.
- 포즈: side_stand / front_stand / slash1(첫 번째 베기) / slash2(두 날을 합쳐 가위로 자르기)
- 파일 (가로x세로 px):
  - `05_shear_tailor/m05_front_stand.png` 311x504
  - `05_shear_tailor/m05_front_stand_game.png` 21x35
  - `05_shear_tailor/m05_side_stand.png` 217x507
  - `05_shear_tailor/m05_side_stand_game.png` 15x35
  - `05_shear_tailor/m05_slash1.png` 447x456
  - `05_shear_tailor/m05_slash1_game.png` 31x31
  - `05_shear_tailor/m05_slash2.png` 463x457
  - `05_shear_tailor/m05_slash2_game.png` 32x31
  - `05_shear_tailor_contact.jpg` 1538x1114
  - `_previews/05_shear_tailor_game1x.png` 176x64
  - `_previews/05_shear_tailor_game4x.png` 704x256
  - `05_shear_tailor/_meta.json` (포즈별 크기·배율 기록)
- 약점: slash2는 별도 생성본(0.645배 크기 맞춤). 핀 머리가 "핀헤드"를 연상시킬 수 있음. 핀이 게임 크기에서 가늘어 안 보임.

## 6. 실패 거미 (Spool Spider) — `06_spool_spider/`
- 역할/크기: 뛰어들기 무리, 0.8배 (side_stand 27px)
- 디자인: 붉은 실이 감긴 나무 실패 몸통, 구멍 뚫린 철 골무 머리와 검은 구슬 눈, 가위날 송곳니, 가는 바늘 다리 8개.
- 포즈: side_stand / front_stand / crouch(뛰기 전 웅크림) / airborne(공중)
- 파일 (가로x세로 px):
  - `06_spool_spider/m06_airborne.png` 344x284
  - `06_spool_spider/m06_airborne_game.png` 37x31
  - `06_spool_spider/m06_crouch.png` 349x218
  - `06_spool_spider/m06_crouch_game.png` 38x23
  - `06_spool_spider/m06_front_stand.png` 314x271
  - `06_spool_spider/m06_front_stand_game.png` 34x29
  - `06_spool_spider/m06_side_stand.png` 274x260
  - `06_spool_spider/m06_side_stand_game.png` 29x28
  - `06_spool_spider_contact.jpg` 1381x668
  - `_previews/06_spool_spider_game1x.png` 208x64
  - `_previews/06_spool_spider_game4x.png` 832x256
  - `06_spool_spider/_meta.json` (포즈별 크기·배율 기록)
- 약점: crouch는 별도 생성본(0.52배 크기 맞춤)이라 시점이 약간 3/4이고 대비가 조금 더 강함. airborne은 몸이 기울고 다리가 벌어진 정도라 "공중" 느낌이 중간 정도. 다리가 1px 이하로 가늘어 게임 크기에서 거의 몸통만 보임.

## 7. 고치 어미 (Cocoon Mother) — `07_cocoon_mother/`
- 역할/크기: 고치 어미, 1.2배 (front_stand 41px)
- 디자인: 얼굴 없는 거즈 베일을 쓴 키 큰 마네킹 여인, 찢어진 시트 여러 겹 치마, 바늘 손가락. 등과 몸통에 붉은 실로 꿰맨 회색 천 고치 묶음.
- 포즈: side_stand / front_stand / cocoon_burst(고치를 찢어 터뜨리기)
- 파일 (가로x세로 px):
  - `07_cocoon_mother/m07_cocoon_burst.png` 466x681
  - `07_cocoon_mother/m07_cocoon_burst_game.png` 28x41
  - `07_cocoon_mother/m07_front_stand.png` 378x699
  - `07_cocoon_mother/m07_front_stand_game.png` 22x42
  - `07_cocoon_mother/m07_side_stand.png` 377x693
  - `07_cocoon_mother/m07_side_stand_game.png` 22x41
  - `07_cocoon_mother_contact.jpg` 1301x1498
  - `_previews/07_cocoon_mother_game1x.png` 128x64
  - `_previews/07_cocoon_mother_game4x.png` 512x256
  - `07_cocoon_mother/_meta.json` (포즈별 크기·배율 기록)
- 약점: 고치의 붉은 바느질이 야구공처럼 보일 수 있음. 공격 포즈 1개뿐(고치를 옆에서 찢는 모습이라 "터지는" 순간이 크게 강조되지는 않음). 전체가 밝은 흰색이라 밝은 바닥에서는 대비 낮음. 상체에 약한 여성 신체 윤곽 있음(노출 없음).

## 8. 바늘이빨 솜뭉치 (Pin-Tooth Stuffing) — `08_pin_tooth_stuffing/`
- 역할/크기: 작은 떼, 0.5배 (side_stand 17px)
- 디자인: 더러운 솜·헝겊 덩어리를 붉은 실로 꿰맨 몸, 짝짝이 단추 눈, 찢어진 솔기 입에 핀 이빨, 핀으로 된 짧은 다리 4개.
- 포즈: side_stand / front_stand / bite(물기)
- 파일 (가로x세로 px):
  - `08_pin_tooth_stuffing/m08_bite.png` 472x330
  - `08_pin_tooth_stuffing/m08_bite_game.png` 25x18
  - `08_pin_tooth_stuffing/m08_front_stand.png` 308x330
  - `08_pin_tooth_stuffing/m08_front_stand_game.png` 16x18
  - `08_pin_tooth_stuffing/m08_side_stand.png` 321x328
  - `08_pin_tooth_stuffing/m08_side_stand_game.png` 17x18
  - `08_pin_tooth_stuffing_contact.jpg` 1181x760
  - `_previews/08_pin_tooth_stuffing_game1x.png` 112x64
  - `_previews/08_pin_tooth_stuffing_game4x.png` 448x256
  - `08_pin_tooth_stuffing/_meta.json` (포즈별 크기·배율 기록)
- 약점: side_stand가 완전한 옆모습이 아니라 3/4(두 눈이 보임). 이빨이 핀보다는 송곳니처럼 그려짐. 입 안쪽이 짙은 붉은색(살 느낌, 피 표현은 없음).

## 9. 시간 메아리 (Time Echo) — `09_time_echo/`
- 역할/크기: 히든 정예, 1.3배 (front_stand 44px)
- 디자인: 돌로 굳은 옛 왕실 근위 기사. 깃털 장식 그레이트헬름, 해진 돌 망토, 돌 대검. 갈라진 갑옷을 붉은 실이 바느질처럼 얽어 묶음.
- 포즈: side_stand / front_stand / statue(석상 상태, 한쪽 무릎 꿇고 검을 꽂음) / awaken(깨어남, 검을 뽑으며 일어섬) / slam_raise(대검 들어올리기) / slam_down(내려찍기 착지)
- 파일 (가로x세로 px):
  - `09_time_echo/m09_awaken.png` 533x535
  - `09_time_echo/m09_awaken_game.png` 35x35
  - `09_time_echo/m09_front_stand.png` 328x675
  - `09_time_echo/m09_front_stand_game.png` 22x45
  - `09_time_echo/m09_side_stand.png` 371x664
  - `09_time_echo/m09_side_stand_game.png` 25x44
  - `09_time_echo/m09_slam_down.png` 725x458
  - `09_time_echo/m09_slam_down_game.png` 48x30
  - `09_time_echo/m09_slam_raise.png` 403x755
  - `09_time_echo/m09_slam_raise_game.png` 27x50
  - `09_time_echo/m09_statue.png` 372x563
  - `09_time_echo/m09_statue_game.png` 25x37
  - `09_time_echo_contact.jpg` 2872x1610
  - `_previews/09_time_echo_game1x.png` 272x80
  - `_previews/09_time_echo_game4x.png` 1088x320
  - `09_time_echo/_meta.json` (포즈별 크기·배율 기록)
- 약점: awaken·slam_raise는 두 번째 시트(1.18배), slam_down은 별도 생성본(0.70배)으로 투구 크기 기준 맞춤이라 ±5% 정도 오차 가능. awaken에서 어깨 돌조각 일부가 몸에 붙어 남았고 깃털에 약한 초록 기운이 있음. statue 상태에서 고개를 숙이지 않음. 돌 질감이 회색보다 베이지 쪽.

## 기타 폴더
- `_src/`: 생성 원본 JPG(채택본 + `_rejected` 폐기본). 최종 산출물 아님.
- `_tools/`: `process.py`(처리 파이프라인), `edgecheck.py`(가장자리 확인), `m01.json`–`m09.json`(마물별 설정).

## 공통 약점
- 34px 게임 크기에서는 잉크 외곽선과 가는 부품(바늘, 핀, 거미 다리, 실)이 거의 사라짐. 실제 게임에 넣으려면 게임 크기용으로 외곽선 보강/손 픽셀 정리가 필요할 수 있음.
- 그레이딩 후 붉은 실이 조금 탁해짐(채도 유지 처리했지만 원본 자체가 어두운 붉은색).
- 일부 포즈는 별도 생성본이라 선 굵기·명암이 같은 마물의 다른 포즈와 미묘하게 다름(04 side_stand, 05 slash2, 06 crouch, 09 awaken/slam_raise/slam_down).
- 모든 그림은 AI 생성물이라 세부(손가락, 관절, 대칭)가 완벽하지 않을 수 있음.
