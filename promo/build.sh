#!/usr/bin/env bash
# Render every scene, stitch them together and add the synthesized soundtrack.
# usage: ./build.sh [quality]   quality: l (480p15, preview) | h (1080p30, default)
set -euo pipefail
cd "$(dirname "$0")"
Q=${1:-h}
MEDIA=${MEDIA_DIR:-build/media}
OUT=output
mkdir -p "$OUT"
case $Q in
  l) FLAGS="-ql"; RES=480p15 ;;
  h) FLAGS="-qh --fps 30"; RES=1080p30 ;;
esac

SCENES=(
  "ch0_opening S00_Opening"
  "ch1_number S01_Number"
  "ch2_shape S02_Shape"
  "ch3_change S03_Change"
  "ch4_waves S04_Waves"
  "ch5_light S05a_Maxwell"
  "ch5_light S05b_EMWave"
  "ch5_light S05c_Quantum"
  "ch6_compute S06a_Turing"
  "ch6_compute S06b_Life"
  "ch6_compute S06c_Mandelbrot"
  "ch7_learning S07_Learning"
  "ch8_frontier S08a_Spacetime"
  "ch8_frontier S08b_Qubit"
  "ch8_frontier S08c_Riemann"
  "ch8_frontier S08d_Questions"
  "ch9_finale S09_Finale"
)

LIST="$OUT/concat.txt"; : > "$LIST"
for entry in "${SCENES[@]}"; do
  set -- $entry
  echo ">> rendering $2"
  manim $FLAGS --disable_caching --progress_bar none --media_dir "$MEDIA" "$1.py" "$2" > /dev/null
  echo "file '$(realpath "$MEDIA/videos/$1/$RES/$2.mp4")'" >> "$LIST"
done

ffmpeg -v error -y -f concat -safe 0 -i "$LIST" -c copy "$OUT/silent.mp4"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/silent.mp4")
echo ">> composing ${DUR}s of music"
python music.py "$DUR" "$OUT/music.wav"
ffmpeg -v error -y -i "$OUT/silent.mp4" -i "$OUT/music.wav" -c:v libx264 -crf 20 -preset slow \
  -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart \
  "$OUT/the_unreasonable_beauty.mp4"
rm -f "$OUT/silent.mp4" "$OUT/music.wav" "$LIST"
echo ">> done: $OUT/the_unreasonable_beauty.mp4"
