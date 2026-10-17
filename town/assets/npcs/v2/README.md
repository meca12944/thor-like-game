# v2 NPC sprites (hero-matched proportions, approved 2026-10-17)

- Same proportions as the hero FRONT idle: 4.0 heads (live grid: 28 logical px tall, head 7 px, leg split row 18, sole on the anchor row).
- Sheet `<id>.png`: 4 rows (down, left, right, up) x 12 cells: idle breathing 4 + walk 8. Cell/anchor/ranges in `meta.json`.
  Left = mirrored right. `a_tool` (미라벨) is a static reproportion of the old still (idle only) until her new turnaround exists.
- Built by `town/style_sample/tools/build_live.py` (same pipeline as the 768x432 sample, `build_walk.py`, 56 px).
- Engine: `[npc_v2]` block in index.html / tools/game.template.html (`tools/anim/patch_npc_v2.py`, idempotent).
  NPCs without a v2 sheet keep the old drawNpc path. `NPC_V2_CFG`: frame ticks, patrol speed, stop/face-hero distance, patrol paths (리네트: 130 px loop).
