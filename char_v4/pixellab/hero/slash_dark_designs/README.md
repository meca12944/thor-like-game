# 사멸의 궤적 — 주인공 검흔/검기 다크 디자인 6종 (design proposals)

Trail of Extinction: 6 dark sword-slash trail proposals to replace the current bright white-cyan slash.
These are proposals only. No game code or existing assets were changed. Run `python3 make.py` (about 65 s) to rebuild everything here.

## Shape (shared by all 6)
- The arc is a big half-moon centred on the hero's body (centre (128,128) on the 256 canvas; hit 3 uses (128,116)). Radius R = reach × 0.7 = 70 px at the ~124 px hero scale.
- HIT1 is a horizontal swing of 140° (perspective squash 0.55). HIT2 is a reverse diagonal of 140° (plane tilted −28°, squash 0.60). HIT3 is an overhead slam of 170° (squash 0.85; its wind-up part goes behind the head).
- The filled fan is the hitbox. It's drawn behind the hero in three flat tones with a 1 px edge. On fade it collapses outward into the rim.
- Rim trail in front of the hero: it gets thicker and brighter toward the tip and ends in a pointed tip. Also: 3 blade afterimages, a tip sparkle, 2–4 tangential speed lines, then a style-specific fade.
- 8 frames per hit: 0 anticipation, 1–2 swipe, 3 full trail, 4–7 fade. Delays at 60 fps are 100/33/33/33/50/50/50/100 ms (GIF stores 33 as 30 ms), with a 150 ms hold after each hit and 400 ms before the loop.
- Hero = `../dark_v3prop/east.png`. Its hanging blade (pixels x≥146, y≥134) is removed in the preview only, and a swinging blade is drawn each frame. The background is #1a1c22 ground.

## Files
- `style_<n>_<name>.gif`: HIT1 → HIT2 → HIT3 on the hero, crop 192×192 at ×3
- `style_<n>_<name>_sheet_native.png`: native 256-canvas transparent frames (rows A1/A2/A3 × 8 frames) for implementation
- `slash_designs_board.png`: one row per style with key frames (HIT1), the 3-hit strip (full-trail frame), palette and mood
- `slash_designs_all.gif`: all 6 styles side by side (3×2, ×2), looping
- `make.py`: the generator

## Styles

### 1. 잿빛 초승달 (Ashen Crescent): `style_1_ashen_crescent.gif`
Mood: Cold bone-white blade-moon with a dead black heart; embers smoulder off the trailing edge like a pyre going out.

| role | hex |
|---|---|
| outline | `#0a090c` |
| core | `#141118` |
| core2 | `#2b2628` |
| bone_d | `#7f7768` |
| bone | `#b8b09b` |
| bone_h | `#e3ddcc` |
| ash | `#5a544c` |
| emb_d | `#7a2a10` |
| emb | `#cf5f1d` |
| emb_h | `#f19a3c` |
| fan0 | `#1f1c1e` |
| fan1 | `#252121` |
| fan2 | `#2d2826` |
| fanline | `#0e0d10` |

### 2. 심연 균열 (Abyss Rift): `style_2_abyss_rift.gif`
Mood: The swing does not cut the air, it tears it: a black wound in space edged with violet, leaking void shards.

| role | hex |
|---|---|
| void | `#030206` |
| star | `#2a1b52` |
| rim_d | `#2b1d63` |
| rim | `#5d3ba3` |
| rim_h | `#9a6fe6` |
| shard_h | `#c9adff` |
| outline | `#120c26` |
| fan0 | `#0f0b18` |
| fan1 | `#130d20` |
| fan2 | `#191029` |
| fanline | `#07050c` |

### 3. 혈묵 (Blood Ink): `style_3_blood_ink.gif`
Mood: One sumi-e stroke in blood: heavy brush landing, dry-brush (kasure) tail, splatter flicked off the end.

| role | hex |
|---|---|
| edge | `#1c0408` |
| dark | `#420810` |
| body | `#6b0e16` |
| sheen | `#93202a` |
| dry | `#2c060b` |
| fan0 | `#1f1015` |
| fan1 | `#251217` |
| fan2 | `#2c1419` |
| fanline | `#0f0508` |

### 4. 파쇄 강철 (Shattered Steel): `style_4_shattered_steel.gif`
Mood: A cold hairline of tempered steel that cracks and rains down as angular shards, like a blade snapping in the dark.

| role | hex |
|---|---|
| outline | `#0f1318` |
| shadow | `#45515e` |
| body | `#6d7d8d` |
| hi | `#a8b5c1` |
| glint | `#dce3ea` |
| fan0 | `#1a1f27` |
| fan1 | `#1d232c` |
| fan2 | `#222933` |
| fanline | `#0b0e12` |

### 5. 망령 연기 (Wraith Smoke): `style_5_wraith_smoke.gif`
Mood: Grave-smoke dragged behind the blade with a thin ghost-light thread inside; it curls upward and is gone.

| role | hex |
|---|---|
| outline | `#0a0b0f` |
| smoke_d | `#1f222b` |
| smoke | `#2c303c` |
| smoke_l | `#3e4353` |
| core_g | `#8b96a6` |
| core | `#d6dee8` |
| fan0 | `#1d1f26` |
| fan1 | `#21242c` |
| fan2 | `#262a33` |
| fanline | `#0e0f13` |

### 6. 황혼 금선 (Dusk Gilt): `style_6_dusk_gilt.gif`
Mood: A tired gold hairline, the colour of the hero's tarnished trim, shedding ash and a few last embers at dusk.

| role | hex |
|---|---|
| outline | `#1c170c` |
| g_d | `#6b5a2e` |
| g | `#8a7340` |
| g_h | `#a08a55` |
| g_tip | `#c2a96e` |
| ash_d | `#3a3835` |
| ash | `#5a5650` |
| ash_l | `#7e786d` |
| emb_d | `#6a3214` |
| emb | `#b8682a` |
| emb_h | `#e0a050` |
| fan0 | `#1c1c1d` |
| fan1 | `#201f1d` |
| fan2 | `#26231d` |
| fanline | `#0e0d0b` |

Shared colours: blade outline #0d0f13, steel #5d6670/#9aa3ad/#cfd5db, ground #1a1c22/#16181d/#1e2128, shadow #111217.
