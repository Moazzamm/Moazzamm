#!/bin/bash
# Stage A: photo check, timeline, parallax/footage shots, sound mix  -> assets/<v>/prep.done
cd "$(dirname "$0")/.."
for v in "$@"; do
  rm -f assets/$v/prep.done
  python3 lib/photocheck.py $v > out/${v}_v2build.log 2>&1
  CLIPS=1 python3 lib/build.py $v --no-audio >> out/${v}_v2build.log 2>&1
  python3 lib/clips.py $v 2 >> out/${v}_v2build.log 2>&1
  python3 -c "import json,sys; sys.path.insert(0,'lib'); import audio2; tl=json.load(open('assets/$v/timeline.json')); audio2.mix(tl,'assets/$v/vo','out/$v.wav')" >> out/${v}_v2build.log 2>&1
  touch assets/$v/prep.done
done
