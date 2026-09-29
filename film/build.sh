#!/usr/bin/env bash
# Usage: ./build.sh [q]    q = l (480p15 preview) | h (1080p30 final, default)
# Renders every act to its exact budget, concatenates, muxes audio/music.wav.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-/opt/mv/bin/python}
MANIM="$PY -m manim"
Q=${1:-h}
declare -A FILES=( [act0]=act0_point.py [act1]=act1_rotation.py [act2]=act2_minimize.py
                   [act3]=act3_information.py [act4]=act4_selfref.py [act5]=act5_quantum.py
                   [act6]=act6_finale.py )
declare -A CLS=( [act0]=Act0 [act1]=Act1 [act2]=Act2 [act3]=Act3 [act4]=Act4 [act5]=Act5 [act6]=Act6 )
declare -A DUR=( [act0]=15 [act1]=25 [act2]=30 [act3]=35 [act4]=35 [act5]=28 [act6]=12 )
mkdir -p out; : > out/list.txt
for a in act0 act1 act2 act3 act4 act5 act6; do
  [ -f "${FILES[$a]}" ] || { echo "skip $a (missing)"; continue; }
  if [ "$Q" = "l" ]; then RES="--resolution 854,480 --fps 30"; QDIR=480p30; else RES="--resolution 1920,1080 --fps 30"; QDIR=1080p30; fi
  $MANIM $RES --disable_caching --media_dir media/$a "${FILES[$a]}" "${CLS[$a]}" >/dev/null
  STEM=${FILES[$a]%.py}
  SRC=$(find "media/$a/videos/$STEM" -name "${CLS[$a]}.mp4" -not -path "*partial*" -path "*${QDIR}*" | head -1)
  [ -n "$SRC" ] || { echo "no render found for $a"; exit 1; }
  # force exact duration, uniform 1080p30 yuv420p
  ffmpeg -loglevel error -y -i "$SRC" -vf "scale=1920:1080,fps=30,tpad=stop_mode=clone:stop_duration=2,format=yuv420p" \
     -t ${DUR[$a]} -an -c:v libx264 -crf 16 -preset medium out/$a.mp4
  echo "file '$a.mp4'" >> out/list.txt
  echo "rendered $a"
done
ffmpeg -loglevel error -y -f concat -safe 0 -i out/list.txt -c copy out/silent.mp4
if [ -f audio/music.wav ]; then
  ffmpeg -loglevel error -y -i out/silent.mp4 -i audio/music.wav -map 0:v -map 1:a \
     -c:v copy -c:a aac -b:a 192k -shortest out/film.mp4
else cp out/silent.mp4 out/film.mp4; fi
echo "done -> out/film.mp4"
