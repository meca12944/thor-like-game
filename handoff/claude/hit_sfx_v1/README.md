# 타격음 3겹 (타격감 보고서 3-6, 크레딧 0)

영상: hit_sfx_before_after.mp4 (앞 14초 = 전, 뒤 14초 = 후). `tools/sfx_preview.py "<주소>?nosave&worldreset&noscene&go=field_felt&at=27,12&tough=1&arena=c1_unrotting_hound,c1_thread_puppet,c1_needle_spider,c1_silmamul" field_felt <폴더>`

1. 몹 재질 1겹: sfx_synth.js `mat_flesh / mat_thread / mat_bone / mat_shell`, 몹 정의 `D.sfxMat` (world_mobs.js 표 하나, 챔피언은 바탕 몹 것을 물려받음).
   - 살: 버섯·토끼·멧돼지·다람쥐·슬라임·돌엄니 / 실: 허수아비·실마물·실 꼭두각시 / 뼈·갑옷: 골렘 / 껍질: 말벌·여왕 말벌·새싹·바늘 거미·들개·아라크네
2. 콤보 음높이: 1→2→3타 x1.00 / 1.03 / 1.06 (타격음 + 재질음). 합성음 무작위 ±5% → ±2.5% 로 줄여 계단이 들리게.
3. 3타(와 돌진·모으기) 저음 `hit_thud` 1겹.
4. 타이밍: 타격음은 hitMob 안(맞는 그 프레임). 멈춤이 걸린 타는 모두 같은 프레임에 시작(차이 0). 멈춤이 안 걸린 타는 #154 의 0.3초 규칙·한 번 휘두름에 한 번 규칙 때문.
5. 근처(220px)에 남은 적이 없을 때 처치 0.15초 뒤 `fight_end` (보스·챔피언·소환물 제외).
- 소리 크기: 평균 -14.9 → -17.0 dB, 최대 0 → -1.4 dB (안 깨짐). test_openworld 17/17.
- sfx_preview.py: 음높이(rate)도 기록·반영, 몹이 늦게 나오는 지도도 기다림, log.json 저장.
