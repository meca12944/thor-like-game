#!/bin/sh
# Downloads the free sample libraries used by render2.py into $SAMPLES (default /workspace/samples). Not committed (size).
#  - GeneralUser GS 2.0 (S. Christian Collins) — "use without restriction for your own music creation, private or commercial"
#  - VSCO 2 Community Edition (Versilian Studios) — CC0 1.0 (percussion, timpani, organ, strings, horns, flute)
#  - FluidR3_GM (Frank Wen) — MIT  (apt: fluid-soundfont-gm)
set -e
S=${SAMPLES:-/workspace/samples}; mkdir -p "$S"; cd "$S"
[ -f GeneralUser-GS.sf2 ] || { git clone -q --depth 1 https://github.com/mrbumpy409/GeneralUser-GS.git gu && cp gu/GeneralUser-GS.sf2 gu/documentation/LICENSE.txt . && rm -rf gu; }
if [ ! -d VSCO ]; then
  git clone -q --filter=blob:none --no-checkout --depth 1 https://github.com/sgossner/VSCO-2-CE.git VSCO
  cd VSCO && git sparse-checkout init --no-cone
  printf '/Strings/Violin Section/\n/Strings/Viola Section/\n/Strings/Cello Section/\n/Percussion/*.wav\n/Percussion/Timpani/\n/Keys/Organ/\n/Brass/F Horn/\n/Brass/Tenor Trombone/\n/Woodwinds/Flute/\n/LICENSE\n/README.md\n' > .git/info/sparse-checkout
  git checkout -q master
fi
command -v fluidsynth >/dev/null || echo "install: sudo apt-get install fluidsynth fluid-soundfont-gm guitarix-lv2 lilv-utils"
