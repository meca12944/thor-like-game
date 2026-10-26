# Trail of Extinction: hero pose illustrations (D_hero_illust)

All images made with GenerateImage only. Every call used 3 reference images: `01_hero_sheet.jpg`, `face_8dir_aligned.jpg` and `PROPORTION_STANDARD_walk.jpg`.
Style: Japanese hand-drawn ink line, flat cel shading, light watercolour wash and muted sepia tones. The hero is empty-handed, with no effects.
Each pose was drawn on a flat #00FF00-style chroma background. The background was removed with PIL (key.py): alpha comes from greenness (g − max(r,b)), then the green is despilled, partial-alpha edges are un-premultiplied against the measured background colour, and small specks are removed. Each image is cropped with 24 px padding.
Edges were checked on near-black and off-white backgrounds, with hair strands and fingers zoomed in. No visible green fringe was found.

## Files (transparent PNG, all at the SAME head/body scale; boots end 24·scale px above bottom edge)
| file | pose | px |
|---|---|---|
| 01_hit_down.png | 1 맞기 ↓: hit from the front, arched back, facing the viewer | 693×948 |
| 02_hit_right.png | 2 맞기 →: knocked back, side view facing right | 745×968 |
| 03_atk1.png | 3 정면 1타 중간: horizontal sweep to his left | 740×1045 |
| 04_atk2.png | 4 정면 2타 중간: rising diagonal sweep to upper right | 677×992 |
| 05_atk3.png | 5 정면 3타: clasped hands raised overhead (main pick) | 686×1102 |
| 05b_atk3_alt.png | 5 alternative: hands wound up beside the right of the head (lower, less "raised high") | 682×1016 |
| 06_dash_ur.png | 6 회피대시 ↗: back three-quarter view, heading upper right, both feet down | 820×936 |
| 07_dash_dr.png | 7 회피대시 ↘: front three-quarter view, heading lower right, low, both feet down | 797×833 |
| contact_sheet.jpg | 4×2 sheet with Korean labels (Nanum Pen Script), file names and sizes | 4000×2500 |
| alignment_preview.jpg | all poses at equal scale on a shared ground line, with head-unit guides | 6020×1302 |

Other folders and scripts: `raw/` holds the original generations (`raw/rejected/` keeps the rejected ones, each named for the reason it was rejected). `work/` holds the unscaled cutouts. `key.py` and `finalize.py` are the scripts.

## How the shared scale was set
Each pose was scaled by the average of two measurements: eye-to-chin distance and boot height (cuff to sole). The factors are 0.86, 0.91, 0.93, 0.88, 0.96, 0.91 (5b), 1.03 and 0.98. All but one shrink the image, so lines stay crisp. Expect about ±5% error, because the measurements were taken by eye on poses with tilted heads and foreshortened legs.

## Honest weak points
- **Resolution:** the cutouts are about 0.7–0.8k px wide and 0.83–1.1k px tall. The generator outputs at most 864×1152 or 1024×1024, so I could not go bigger without upscaling.
- **2 맞기 →** is a horizontal MIRROR. The generator kept drawing him facing left. Mirroring puts the bronze pauldron on the near shoulder, which matches the side view on the sheet. The coat details and the side the hair is parted on are reversed.
- **5 3타:** the arms are high and straight with the hands clasped. That is not a V-shaped 만세, but it is close to vertical. The more natural wind-up (05b) sits lower than "raised high". One attempt drew a sword hilt and was rejected.
- **6 ↗** is a fairly upright stride rather than a very low crouch. The face is hidden because it is a back view.
- **3 and 4** are fairly calm "martial-arts" poses rather than strong mid-swing motion. The hands are open or semi-open, not empty grip shapes.
- **Small detail drift between poses:** some poses have fingerless gauntlets and some have bare hands, and the chest ornament and pauldron trim vary. The face matches the reference well, but the eyes are a bit sharper in some poses.
- **Proportions:** about 6.5–7 heads tall, matching the walk standard by eye (not 5-head). The cel and watercolour look is close to the hero sheet but still slightly "clean digital".
