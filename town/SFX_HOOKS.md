# File SFX hooks (town/index.html `SFX.ev`, world.js `sfx()`)
Assets: `town/assets/sfx/fx/*.ogg` + `.m4a` (Safari), built by `python3 town/tools/sfx/make_fx.py` from `docs_music/sfx_draft/`
(hit/hurt trimmed to short versions, attenuated to true peak <= -1 dBTP and <= -14 LUFS). Loaded after the audio unlock (trickle preload),
volume = `FEEL.sfxVol`, `?sfx=0` mutes, `?sfxdraft=0` = old built-in swings. Voices: 12 total, per-key caps (footsteps 2, hits 3), pitch jitter per key.
Built-in synth SFX (swing_light/heavy, hit_light/heavy/crit, kill, spin_dark, wave, ult_cutin, ult_boom) unchanged.

Hooks with NO trigger yet (call them from the new code):
- `SFX.ev.chargeLv1()` / `chargeLv2()` / `chargeRelease()` — charge attack: lv1 / lv2 reached while holding, charged slash released (town + world.js)
- `SFX.ev.dashAttack()` — fires on the roll->leap slash (swing with `leap`) and the 돌진베기 dash attack (run + attack; town + world.js)
- `SFX.ev.chest()` / `locked()` — town has no chests (world.js wired)
- `SFX.ev.door()` / `warp()` — world.js only
- `SFX.ev.ult(id)` — wired in town castUlt; world.js ult (gated by another worker) only plays the built-in cutin/boom: add `sfx('ult', U.id)`
- `SFX.ev.monsterAttack()` — town slimes have no attack (contact only); boar charge + world hazards wired
