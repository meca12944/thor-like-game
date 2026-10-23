#!/bin/sh
# run_south keys: replace the hand-on-hip arms with natural running arms (opposite to the legs), then the 2 in-betweens again
. ~/.config/pixellab/env; export HERO_CAP=420
python3 ns_fix.py run_south R "Keep this exact pose, legs, face, outfit, size and position. Only change the arms: natural running arms, both elbows bent, his LEFT arm (on the right side of the image) swings forward toward the viewer, his RIGHT arm (on the left side of the image) holding the sword swings back, the sword pointing down. No hand on the hip. Full body, no effects." 7 &
python3 ns_fix.py run_south L "Keep this exact pose, legs, face, outfit, size and position. Only change the arms: natural running arms, both elbows bent, his RIGHT arm (on the left side of the image) holding the sword swings forward toward the viewer with the sword pointing down, his LEFT arm (on the right side of the image) swings back. No hand on the hip. Full body, no effects." 7 &
wait
mv ns/tw_run_south_RL ns/tw_run_south_RL_hip; mv ns/tw_run_south_LR ns/tw_run_south_LR_hip
python3 ns_tween.py run_south
echo ARMFIX_DONE
