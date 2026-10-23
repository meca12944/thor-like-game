#!/bin/bash
# per NPC: hero-proportion ref (edit 10) -> 8-dir rotation (8) -> walk/idle jobs (s/e/n). Key from env only.
n=$1; D=$(dirname "$(readlink -f "$0")"); cd "$D"
d=$(cat ../felt_npc_v1/desc_$n.txt)
[ -f ref_$n.png ] || python3 edit_pose.py hero_ref_s.png ref_$n.png r$n "Replace the swordsman with a different person: $d Keep EXACTLY the same body proportions as the input: same big head size, same short chibi-like body (about 3 heads tall), same height, same standing pose, same camera angle, same pixel art style and dark outline. No sword, no cape. No effects." 3
[ -f rot_$n/south.png ] || python3 rot.py $n ${2:-1}
python3 jobs.py $n | tr '\n' '\0' | xargs -0 -P 1 -I{} python3 runjob.py {}
echo "CHAIN DONE $n"
