#!/bin/sh
# 새 그록 주인공 그림이 오면 한 번에 (크레딧 0): 자르기·배경·그림자·먼지 → 공격 몸/검기 나누기 → 크기 한 번·발 189 조립 → 숫자
#   sh motion_lab/grok_hero/make_all.sh <그림 폴더> [정면 걷기 키 px, 기본 164]
#   그림 폴더에 hero_walk_4dir.jpg · hero_run_4dir.jpg · hero_attack3_4dir.jpg (지금과 같은 배치: 4줄 = 정면·오른쪽·뒷면·왼쪽, 6장)
set -e
D=$(cd "$(dirname "$0")" && pwd); SRC=${1:-$D/../../docs_art/grok_hero_20261024}; H=${2:-164}
cd "$D"
python3 cut.py "$SRC"
python3 cut_attack.py "$SRC"
python3 assemble.py --height "$H"
python3 audit.py > /dev/null && echo "audit.json 완료"
