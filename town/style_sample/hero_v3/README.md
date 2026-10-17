# Hero v3 motion: hand-built rig (phase 1: turnaround, walk, run, dodge)

None of these frames come from image generation. `tools/hero_v3_pix.py` draws every frame at 1x from explicit joint positions, using aliased polygons, a fixed 17-colour palette, binary alpha, flat light from the upper left, and a 1 px dark outline (silhouette plus part separation). `tools/hero_v3_motion.py` holds the hand-keyed poses. `tools/hero_v3_build.py` builds every file below. To rebuild, run this from this folder: `python3 tools/hero_v3_build.py` (it needs `DOCS_ART`=repo docs_art, ffmpeg, PIL, numpy).

## Single source of truth: `hero_v3_guides.json`
- `bodies.male` / `bodies.female` hold the guide rows on the 768x432 grid (row 0 = crown, sole line 60), plus the half-widths and joints. All 7 heroines use the same grid. They differ only in: crown at row 2 (58 px tall), narrower shoulders and waist, and slightly wider hips. Crotch, knee and sole rows are identical. See `hero_v3_vs_female_silhouette.png`.
- `timing` holds every hold in 60 fps ticks. Gaits are synced to distance, as in the game (`walkT += dt*max(.6,speed/FEEL.walkSpeed)*(run?FEEL.runStride:1)`).
  - walk: 8 x 3 ticks = 24-tick cycle (0.400 s at walk speed, 51.6 grid px per cycle). Drawn stance-foot slip is 3.9 %.
  - run: 8 x 3 anim ticks. At full run the anim rate is 1.9*0.55 = 1.045, giving 2.87 real ticks per frame and a 0.383 s cycle of 93.8 grid px. Slip is 3.6 %. One float frame per step, lean of 2 px.
  - dodge: 2,3,3,3,4,6 ticks (= `dash_*`). The first 15 anim ticks stretch over `FEEL.dashTicks` 13, then `dashRecTicks` 6 for recovery. Travel is 65 grid px. The ghost trail is drawn the way the game draws it (every 2 ticks, 14-tick fade, newest 3).
- `motions` lists the pose names and per-frame `bob`/`lean`. These are the only permitted deviations from the guide rows. ±1 px of bob applies to walk; the run float frame uses -2; the dodge crouch goes up to +4.
- `slots`: paperdoll slots for EQUIPMENT.md layers, the corruption layers and the 마왕 강림 set (helmet/horns, armor, cape variant incl. tattered, back attachment = tentacles, weapon, offhand, aura back/front, shadow). Each one names the anchor it hangs from. Every frame exports those anchors (`frames/hero_v3_<motion>.json`) and a part map (`*_parts.png`, ids listed in `slots.partIds`).

## Files
| file | what |
|---|---|
| `hero_v3_turnaround_check.png` (x6) / `_4x.png` | 4 directions on one baseline, labeled guide lines, measured-row table (`hero_v3_turnaround_measure.csv`) |
| `hero_v3_walk.gif` / `hero_v3_run.gif` / `hero_v3_dodge.gif` | down, right, up, left side by side, x2, at true game speed (delays in 10 ms steps, error-diffused). The ground scrolls at the movement speed so you can judge foot slide |
| `hero_v3_*_60fps.mp4` | every game tick rendered at 60 fps, x2 nearest |
| `hero_v3_walk_run_60fps.mp4` | walk 2 s → 10-tick run start → run 2 s → back to walk → dodge → idle, 4 directions. The gait phase stays continuous across the switch (walk frame i ↔ run frame i, same leg forward) |
| `hero_v3_*_sheet.png` | frames by direction, x4, labeled with pose, ticks and bob |
| `frames/` | 1x RGBA strips for the game (`hero_v3_<motion>_<dir>.png`, canvas 56x66, feet anchor (28, 63)), with json for ticks, bob, lean and anchors |
| `hero_v3_report.json` | uniqueness check, per-frame proportion check, timing tables, foot-slide numbers |

Left is drawn natively: the geometry is mirrored, but the light still comes from the upper left and the pauldron (character's left shoulder) is on the near side. A plain sprite flip also works if needed.
Not wired into `hero_anim.src.json` / `hero.json` yet (phase 2). Phase 2 also has to replace the walk_*/run_* ticks there and the ANIMATION.md "208 px" run note with the numbers above.
