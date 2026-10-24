# Title screen C assets (used by test128/title.js)

| file | source |
|---|---|
| `title_c_bg.mp4` | `docs_art/title_screen/title_c_loop_bg.mp4` re-encoded for the web: H.264 High, CRF 24, faststart, no audio (3.9 MB vs 9.2 MB, SSIM 0.98) |
| `title_c_still.jpg` | frame 0 of `title_c_loop_bg.mp4` (q2 JPEG) — shown only until the looping idle video is playing (no flash), and the fallback if the video fails or autoplay is blocked |
| `title_c_logo.png` | top half (1920x540) of `title_c_overlay.png` without the baked menu / bottom band — `docs_art/title_screen/make_logo_overlay.py` (pixel-identical logo) |
| `nanum_myeongjo_{regular,bold}_sub.woff` | Nanum Myeongjo (SIL Open Font License 1.1) subset to the menu glyphs (새 게임 / 이어하기 / 설정 / 저장 없음) |

Note: `title_bg_c_notext.png` is NOT frame 0 of the video (the hero is drawn larger / in a different spot), so the still is taken from the video itself.
