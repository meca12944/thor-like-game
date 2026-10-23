#!/bin/bash
# chain the 3 hits for one 3/4 view: hit2 starts on hit1's last frame, hit3 on hit2's last frame
V=$1;IMG=$2;KP=$3;S=$4;DIR=$5
cd /tmp/claude-0/-home-user-thor-like-game/605da03e-2542-5329-b23f-a50876f99780/scratchpad/skel
source ~/.config/pixellab/env
python3 -c "import json;[json.dump(json.load(open(f'../newatk/{c}_${V}_kp.json'))[-1],open(f'../newatk/{c}_${V}_last_kp.json','w')) for c in ('hit1','hit2')]"
ACTION="lunging forward sword thrust, the sword stays in the same hand the whole time, the straight sword pointing forward" python3 animate_skel_act.py $IMG $KP ../newatk/hit1_${V}_kp.json $DIR ../newatk/out34_hit1_$V $((S+1)) || exit 1
ACTION="from the forward thrust, raise the sword upward in a rising slash, the sword stays in the same hand" python3 animate_skel_act.py ../newatk/out34_hit1_$V/014.png ../newatk/hit1_${V}_last_kp.json ../newatk/hit2_${V}_kp.json $DIR ../newatk/out34_hit2_$V $((S+2)) || exit 1
ACTION="big two-handed overhead sword slash, both hands on the hilt, face visible, the sword swings from high above the head in a big arc down to the front" python3 animate_skel_act.py ../newatk/out34_hit2_$V/014.png ../newatk/hit2_${V}_last_kp.json ../newatk/hit3_${V}_kp.json $DIR ../newatk/out34_hit3_$V $((S+3)) || exit 1
echo CHAIN_DONE $V
