#!/usr/bin/env bash
# Example faceless episode, built end to end with free tools only:
# Kokoro voice → motion graphics → timeline → sound design → master → QC.
#   bash episodes/example-faceless/build.sh
# Output: episodes/example-faceless/final.mp4
#
# Voicing one TTS file per line gives exact line timings without transcription,
# so every graphic and SFX lands on its sentence.
set -euo pipefail
EP="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$EP/../.." && pwd)"
KIT="$ROOT/studio/motion-kit"
W="$EP/work"; G="$EP/gfx"
mkdir -p "$W" "$G"
HF="npx --yes hyperframes@0.8.143"
dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }

# 1. Voice: one file per line (Kokoro, documentary male voice)
LINES=(
  "In twenty-ten, a landslide blocked a river... drowned a highway... and created a turquoise lake."
  "This is Attabad Lake, in Pakistan's Hunza Valley."
  "To reach it, you drive about six hundred kilometres north from Islamabad, up the Karakoram Highway."
  "The lake formed in January twenty-ten. Today, travellers come from all over the world to see it."
)
for i in "${!LINES[@]}"; do
  [ -f "$W/vo_$i.wav" ] || $HF tts "${LINES[$i]}" -v am_michael -s 0.95 -o "$W/vo_$i.wav" >/dev/null
done

# 2. Section lengths: each graphic stretches (its "length" variable) to fit its voice line
GLEN=(5 5 6 4.5)
LEN=(); STARTS=(); T=0
for i in 0 1 2 3; do
  L=$(python3 -c "print(round(max(${GLEN[$i]}, $(dur "$W/vo_$i.wav") + 0.9), 1))")
  LEN+=("$L"); STARTS+=("$T")
  T=$(python3 -c "print(round($T + $L, 2))")
done

# 3. Graphics (text and timing come from --variables; nothing hand-edited)
cd "$KIT"
r() { [ -f "$G/$2" ] || $HF render -c "$1" -q delivery ${3:+--format "$3"} --variables "$4" -o "$G/$2" >/dev/null; }
r kinetic-text.html kt.mp4 "" '{"line1":"In 2010 a landslide","line2":"DROWNED A HIGHWAY","line3":"and created a turquoise lake.","length":'"${LEN[0]}"'}'
r title-card.html title.mp4 "" '{"kicker":"HUNZA VALLEY · PAKISTAN","title":"ATTABAD LAKE","subtitle":"born from a disaster","coords":"36.3° N · 74.8° E","length":'"${LEN[1]}"'}'
r route-map.html route.mp4 "" '{"from":"ISLAMABAD","to":"HUNZA","distance":600,"unit":"KM","mode":"car","duration":"VIA THE KARAKORAM HIGHWAY","length":'"${LEN[2]}"'}'
r stat-counter.html stat.mov mov '{"label":"THE LAKE FORMED IN","prefix":"","value":2010,"separator":false,"note":"after the January 2010 landslide","length":'"${LEN[3]}"'}'

# 4. Picture: sections back to back (in a real episode, B-roll sits under the cards)
cd "$EP"
SEC=(kt.mp4 title.mp4 route.mp4 STAT)
: > "$W/concat.txt"
for i in 0 1 2 3; do
  L=${LEN[$i]}
  if [ "${SEC[$i]}" = STAT ]; then  # transparent stat card over a slowly drifting brand gradient
    ffmpeg -v error -y -f lavfi -i "gradients=s=1920x1080:c0=0x0B1620:c1=0x1A4A5C:x0=0:y0=0:x1=1920:y1=1080:speed=0.012:r=30:d=$L" -i "$G/stat.mov" \
      -filter_complex "[0]vignette=PI/5[b];[b][1]overlay=eof_action=pass,format=yuv420p" -t "$L" -c:v libx264 -crf 16 "$W/sec_$i.mp4"
  else
    ffmpeg -v error -y -i "$G/${SEC[$i]}" -vf "fps=30,tpad=stop_mode=clone:stop_duration=1,format=yuv420p" -t "$L" -an -c:v libx264 -crf 16 "$W/sec_$i.mp4"
  fi
  echo "file 'sec_$i.mp4'" >> "$W/concat.txt"
done
ffmpeg -v error -y -f concat -safe 0 -i "$W/concat.txt" -c copy "$W/picture.mp4"

# 5. Voice track: each line starts 0.3 s into its section
VO_IN=(); VO_F=""
for i in 0 1 2 3; do
  VO_IN+=(-i "$W/vo_$i.wav")
  VO_F+="[$i:a]aresample=48000,adelay=$(python3 -c "print(int((${STARTS[$i]}+0.3)*1000))"):all=1[v$i];"
done
ffmpeg -v error -y "${VO_IN[@]}" -filter_complex "${VO_F}[v0][v1][v2][v3]amix=inputs=4:normalize=0[a]" -map "[a]" "$W/vo.wav"

# 6. Sound plan: hook tension bed → warm bed, SFX on every graphic beat
S1=${STARTS[1]}; S2=${STARTS[2]}; S3=${STARTS[3]}
python3 - "$W/plan.json" "$T" "$S1" "$S2" "$S3" <<'PY'
import json, sys
out, total, s1, s2, s3 = sys.argv[1], *map(float, sys.argv[2:])
sfx = "../../../studio/assets/sfx/"
plan = {
  "voice": "vo.wav",
  "music": [
    {"file": sfx + "bed_drone_suspense.wav", "start": 0, "end": s1 + 0.6, "gain_db": -12, "fade_in": 0.2, "fade_out": 0.6},
    {"file": sfx + "bed_drone_warm.wav", "start": s1, "end": total, "gain_db": -15, "fade_in": 1.0, "fade_out": 1.5},
  ],
  "sfx": [
    {"file": "hit_soft", "at": 0.15, "gain_db": -12},
    {"file": "impact_boom", "at": 0.95, "gain_db": -9},
    {"file": "riser_2s", "at": s1 - 1.7, "gain_db": -16},
    {"file": "passport_stamp", "at": s1 + 0.35, "gain_db": -9},
    {"file": "whoosh_long", "at": s2 + 0.6, "gain_db": -14},
    {"file": "map_ping", "at": s2 + 0.35, "gain_db": -13},
    {"file": "map_ping", "at": s2 + 3.55, "gain_db": -12},
    {"file": "pop", "at": s3 + 0.15, "gain_db": -15},
    {"file": "chime", "at": s3 + 2.0, "gain_db": -16},
  ],
  "length": total,
}
json.dump(plan, open(out, "w"), indent=2)
PY
python3 "$ROOT/studio/tools/mix.py" "$W/plan.json" --video "$W/picture.mp4" --out "$EP/final.mp4"

# 7. Finisher
python3 "$ROOT/studio/tools/qc.py" "$EP/final.mp4"
