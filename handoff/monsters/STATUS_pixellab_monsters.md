# Area-1 monster sprites: PAUSED (2026-10-18 02:41 KST)
The owner changed the target style (early hero: src/hero/anim_raw/*.jpg). No animations were generated. Nothing is in flight.

Roster (from maps/field00, field01, dungeon01_b1/b2, boss01 and world_mobs.js):
regulars slime, mushroom, rabbit, wasp, boar, scarecrow, squirrel, sprout; champions champ_boar (돌엄니), champ_wasp (여왕 말벌); boss golem (이끼 수정 골렘).

| id | ref_south.png (concept crop) | raw/frontfix (edit-image-pixen) | rotations (create-character-v3) | character id |
|---|---|---|---|---|
| slime | 96 canvas, mobs/mobs_01 | - | rot_v1 = rot_final OK | e12a586b-4a85-46e6-bcf3-4fe8bb433457 |
| mushroom | 96, mobs_field | - | v1 FAILED (server heavy load, not charged) | - |
| rabbit | 96, mobs_field | s5101 | rot_v1 done; side views look like a bear/beaver with a long tail. Planned fix: import west=concept, east=flip (west_concept.png / east_concept_flip.png ready) | 8c000140-42f5-473c-9372-40cc89312ccf |
| wasp | 96, mobs_field | s5101 | rot_v1 done; sides look bee-like (no wasp waist). Same import fix planned | 5329dc63-2dcb-4893-92b1-11ebcb3ebfe7 |
| boar | 128, mobs_field | s5102 (s5101 too tall, tail up) | rot_v1 = rot_final OK | c90927f0-6fc5-45f7-bbb5-db2f380465d2 |
| scarecrow | 128, mobs_field | - | v1 FAILED (heavy load) | - |
| squirrel | 96, mobs/mobs_01 | s5101 | rot_v1 = rot_final OK | 89232c30-270e-4c55-aed0-735a6fdaf7c0 |
| sprout | 96, mobs/mobs_01 | - | v1 FAILED (heavy load) | - |
| champ_boar | 192, champions/champ01 cell(3,1) | s5101 | rot_v1 = rot_final OK (collar hidden in north) | 0700a274-851a-4e97-a374-5d569fcb102a |
| champ_wasp | 192, champions/champ02 cell(0,0) | s5101 | not submitted | - |
| golem | 256, boss_1_2 (green crystals; attacks/boss01 sheet shows purple, mismatch) | - | not submitted | - |

Reusable tooling in _prep/: make_refs.py (crop + downscale, magenta key), main.py (resumable scheduler: queue.json, cap 5,
429/5xx/heavy-load-failure backoff, running.json), actions.json (per-monster action prompts incl. golem slam/shards/roll),
build.py (frames/, sheet, sheet json, move/all GIFs; not run yet), rotprev.py, prev_*.png previews, usage_log.jsonl.
