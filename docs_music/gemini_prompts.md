# Gemini 음악 생성 프롬프트 — 정령의 팔찌 II · 포식의 낙인

기준: `BGM.md` 트랙 목록 + `audio/bgm/bgm.json` + `town/bgm.js` SCENES. **아직 사용자 제공곡(Gemini)이 없는 장면**만 다룹니다 (현재 이 장면들은 자작 임시곡으로 재생 중). 총 29 장면.

이미 사용자 제공곡이 있는 장면(제외): `title`, `area01_forest`, `area01_temple`, `town_a_fountain`, `battle_champion`, `battle_boss`, `battle_boss_phase2`, `user_ref_01`

사용법: 영어 프롬프트를 그대로 Gemini 에 붙여넣기 → 결과 mp3 를 `/workspace/music_ref/` 에 `user_<id>_01.mp3` 처럼 저장 → `matching_table.md` 에 곡 이름 기입.

## 1. 월드맵 (강림 전) — `worldmap` (scene `world`)

**장면:** 탁 트인 대지를 가로지르는 모험의 시작. 밝고 희망찬 이동곡.

```
heroic adventurous overworld theme, open and uplifting, E minor brightening to G major in the B section. Tempo 150 BPM. Instruments: brass melody, strings ostinato, overdriven FM-style guitar lead doubled by violin, timpani, snare, punchy bass. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 2. 대장간·상점 (마을 공용) — `forge_shop` (scene `shop`)

**장면:** 모루 소리가 울리는 활기찬 대장간 겸 상점.

```
cheerful bouncy shop loop, G mixolydian, light and friendly. Tempo 116 BPM. Instruments: pizzicato strings, flute or PSG-style lead, walking bass, offbeat plucks, anvil hits as percussion. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:00-1:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 3. 2지역 수정 동굴 — `area02_cave` (scene `area2`)

**장면:** 빛나는 수정과 메아리, 넬의 자장가 같은 신비로움.

```
mysterious echoing cave exploration, C# minor, gentle lullaby-like motif with underlying tension. Tempo 132 BPM. Instruments: crystal bells and celesta arpeggios with long delay, soft strings, harp, syncopated bass, soft lead. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 4. 3지역 모래 사막 — `area03_desert` (scene `area3`)

**장면:** 태양이 이글거리는 사막을 질주하는 이국적 필드.

```
exotic driving desert field theme, D phrygian dominant, hot and energetic. Tempo 150 BPM. Instruments: oud-like plucked strings, flute ornaments, shakers, frame drums, brass stabs, fast 16th-note strings, slap-style bass. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 5. 4지역 피라미드 — `area04_pyramid` (scene `area4`)

**장면:** 저주받은 황금가면의 회랑. 무겁고 느린 압박감.

```
dark oppressive ancient tomb dungeon, E phrygian, slow and heavy, half-time. Tempo 120 BPM. Instruments: low drone, male choir pads, funeral bell, taiko and low toms, muted brass, dark low-passed lead, sparse harp. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 6. 5지역 산호 바다 (해상) — `area05_coral_sea` (scene `area5`)

**장면:** 푸른 해류 위를 미끄러지는 시원한 항해곡.

```
flowing breezy ocean voyage theme, B dorian, fresh and buoyant. Tempo 144 BPM. Instruments: strings legato melody, glockenspiel and harp arpeggios, ride cymbal, soft overdriven lead, light percussion. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 7. 6지역 해안 절벽 — `area06_cliff` (scene `area6`)

**장면:** 유령 선장이 출몰하는 폭풍의 절벽. 해적풍 질주.

```
stormy ghost-pirate chase, G minor, galloping and swashbuckling. Tempo 168 BPM. Instruments: galloping strings, brass stabs, accordion or harpsichord color, power chords, timpani rolls, fast snare. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 8. 7지역 화산 성채 — `area07_volcano` (scene `area7`)

**장면:** 용암과 업화의 성채. 게임에서 가장 무거운 록 필드.

```
intense fiery fortress dungeon, C harmonic minor, the heaviest rock-orchestral track. Tempo 176 BPM. Instruments: chugging distorted guitar, double-kick drums, aggressive brass, fast string runs, organ, timpani hits. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 9. 8지역 설산 뇌전 탑 — `area08_thunder_tower` (scene `area8`)

**장면:** 눈보라 속 번개 치는 탑을 오르는 상승감 있는 영웅곡.

```
soaring heroic ascent through a lightning tower on a snowy peak, B minor. Tempo 172 BPM. Instruments: rising arpeggiated synth bells, tremolo strings, heroic brass, electric guitar lead, double-kick finale, thunder-like timpani. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 10. 9지역 어둠 신전 — `area09_dark_temple` (scene `area9`)

**장면:** 시간이 멈춘 의식의 신전. 공포와 정적.

```
ritualistic horror temple, F harmonic minor with Neapolitan color, eerie and slow. Tempo 112 BPM. Instruments: pipe organ, choir 'ahh' pads, clock-tick hi-hat, funeral bells, low strings, distant gong. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 11. 10지역 마룡의 둥지 (최종 지역) — `area10_dragon_nest` (scene `area10`)

**장면:** 세 머리 마룡의 둥지로 향하는 최후의 진군.

```
epic final-area march, F# harmonic minor, darkness clashing with heroism. Tempo 136 BPM. Instruments: full choir melody, taiko, chugging guitar under heroic brass/guitar lead, strings, organ swells. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:30-3:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 12. B 강변 물레방아 마을 — `town_b_watermill` (scene `townB`)

**장면:** 물레방아가 도는 강가 마을의 6/8 춤곡.

```
pastoral riverside village dance in 6/8, G major, carefree. Tempo 132 BPM. Instruments: flute and recorder melody, pizzicato strings, harp/plucked 6/8 arpeggios, light tambourine, soft bass. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 13. C 설산 산장 마을 — `town_c_snow_lodge` (scene `townC`)

**장면:** 눈 덮인 산장, 벽난로 곁의 따뜻한 왈츠.

```
cozy snowy mountain lodge waltz in 3/4, E-flat major, warm. Tempo 96 BPM. Instruments: electric piano / music box, flute, sleigh bells, soft strings, glockenspiel. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 14. D 성벽 왕도 — `town_d_capital` (scene `townD`)

**장면:** 푸른 지붕의 왕도. 위엄 있는 왕국 행진곡.

```
majestic royal capital march, C major, proud and dignified. Tempo 120 BPM. Instruments: fanfare brass lead, marching snare, strings, flute counter-melody, timpani. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 15. E 화산 기슭 대장장이 마을 — `town_e_forge` (scene `townE`)

**장면:** 쇠를 두드리는 소리가 리듬이 되는 화산 기슭 마을.

```
mid-tempo industrious blacksmith village groove, E minor, sturdy. Tempo 100 BPM. Instruments: anvil on 2 and 4, hammer-rhythm lead (brass/bassoon), low strings, brass stabs, frame drum. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 16. F 남쪽 항구 마을 — `town_f_harbor` (scene `townF`)

**장면:** 등대와 갈매기, 통통 튀는 항구 마을.

```
bright bouncy seaside harbor town, D major, sunny. Tempo 128 BPM. Instruments: accordion or soft lead, offbeat plucks, picked bass, ukulele/mandolin strums, light percussion, gull-like flute trills. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 17. G 사막 바자르 — `town_g_bazaar` (scene `townG`)

**장면:** 향신료 향이 가득한 시장의 흥정.

```
lively desert bazaar, A phrygian dominant, playful haggling mood. Tempo 116 BPM. Instruments: hand percussion (darbuka, riq), camel bells, oud/plucks, flute (ney-like), drone bass. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 18. H 서쪽 광산 마을 — `town_h_mine` (scene `townH`)

**장면:** 등잔불 아래 광부들의 셔플 노동요.

```
shuffling miners' work song, D dorian, hearty and dusty. Tempo 120 BPM. Instruments: walking bass, offbeat plucks, harmonica-like lead, pickaxe/anvil hits, banjo/mandolin, light shuffle drums. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 19. 폐허가 된 마을 (마왕의 길, 8곳 공용) — `town_ruin` (scene `ruin`)

**장면:** 잿더미 위로 종이 울리는 애도의 폐허.

```
mournful ruined-village ambience, E phrygian, slow and grieving. Tempo 70 BPM. Instruments: low drone, choir pads, funeral bell, sparse taiko, low-passed solo lead (oboe/cello). Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 20. 아스란 전투 (원탁의 심연, 숨은 보스) — `battle_aslan` (scene `aslan`)

**장면:** 300년을 지킨 심판자 아스란과의 비장한 결투.

```
tragic noble hidden-boss battle, D harmonic minor with Neapolitan E-flat, solemn bell prologue then fast rock-orchestral combat. Tempo 156 BPM. Instruments: bell prologue, strings, choir, overdriven guitar lead doubled by violin, brass, double-kick drums, timpani. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Vocals: wordless choir only (ahh/ooh), no lyrics. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 21. 승리 징글 — `jingle_victory` (scene `victory`)

**장면:** 보스·챔피언 격파 후 짧은 팡파르 (1회 재생).

```
short triumphant victory fanfare, C major, ending on a bVI-bVII-I cadence. Tempo 150 BPM. Instruments: brass fanfare, guitar/strings flourish, timpani roll, cymbal crash. One-shot (not looping). Length: 5-8 seconds, one-shot, NOT looping, clean ending. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 22. 게임 오버 징글 — `jingle_gameover` (scene `gameover`)

**장면:** 꺼져 가는 등불처럼 조용히 사라지는 패배 음악 (1회).

```
sad gentle game-over jingle, A minor with borrowed F minor chord, fading. Tempo 72 BPM. Instruments: solo flute or oboe, soft strings, music box, single funeral bell at the end. One-shot (not looping). Length: 10-15 seconds, one-shot, NOT looping, quiet ending. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 23. 마왕 강림 컷신 — `demon_awaken` (scene `awaken`)

**장면:** 선악 -60 도달 순간. 심장 박동 → 합창 → 폭발.

```
dark cinematic awakening cutscene, E phrygian, heartbeat build to an explosive climax. Tempo 64 BPM. Instruments: heartbeat kick, sub drone, choir swelling, organ, sub impacts, screaming distorted lead, gong. One-shot (not looping). Length: 35-40 seconds, one-shot, builds and ends on a huge hit. Vocals: dark wordless choir chant, no lyrics. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 24. 마왕 필드 (강림 후 월드맵·검은 성채·공성) — `demon_field` (scene `demon`)

**장면:** 세상을 멸하러 가는 마왕의 행진.

```
apocalyptic dark march, D phrygian, half-time heavy. Tempo 129 BPM. Instruments: taiko march, choir chant, pipe organ, chugging distorted guitar, low brass, funeral bells. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:00-2:30. Vocals: wordless or pseudo-Latin choir chant, no lyrics. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 25. 잠수·수중 (분수 아래, 산호 바다 해저, 원탁의 심연 입장) — `underwater` (scene `dive`)

**장면:** 떠다니는 물빛, 고요한 수중.

```
floating dreamy underwater ambience, E-flat lydian, no drums. Tempo 84 BPM. Instruments: warm pads, celesta/bell arpeggios with long delay and reverb, harp, soft strings. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 1:30-2:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 26. 진엔딩 「받은 힘」 — `ending_true` (scene `endTrue`)

**장면:** 희망과 해방. 받은 힘으로 맞이한 진짜 결말.

```
hopeful liberating ending theme, F major, warm and emotional, building to a broad finale. Tempo 84 BPM. Instruments: electric piano, flute, strings, brass lead in the second half, soft drums. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 3:00-4:00 (can also have a natural ending). Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 27. 빛의 엔딩 「빛의 계승」 — `ending_light` (scene `endLight`)

**장면:** 금 간 팔찌, 씁쓸하지만 영웅적인 결말.

```
bittersweet heroic ballad ending, D major. Tempo 96 BPM. Instruments: clean electric guitar ballad lead, strings, piano, half-time drums, gentle brass. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 3:00-4:00. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 28. 비극 엔딩 「낙인의 끝」 — `ending_tragic` (scene `endTragic`)

**장면:** 봉인, 슬픔, 꽃 한 송이.

```
sorrowful tragic ending, A minor, intimate and quiet, no drums. Tempo 72 BPM. Instruments: solo flute, electric piano, soft strings, one final bell. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 2:30-3:30. Instrumental only, no vocals. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```

## 29. 마왕 엔딩 「새로운 검은 왕」 (특별판 「잿더미의 왕」 공용) — `ending_demon` (scene `endDemon`)

**장면:** 장엄한 어둠, 새로운 검은 왕의 즉위.

```
majestic dark throne ending, E phrygian, grand and ominous. Tempo 129 BPM. Instruments: sub drone, pipe organ, choir, bells, chugging guitar, slow mournful lead. Seamlessly loopable: short intro, then a main section that loops cleanly back to its start with no fade-out at the loop point. Length: 3:00-4:00. Vocals: dark wordless choir, no lyrics. Original composition, no imitation of any existing song. 16-bit SNES-era inspired orchestral game music in the style of 1990s Japanese action RPGs (like Story of Thor / Beyond Oasis), warm sampled-synth orchestra with crisp retro character.
```
