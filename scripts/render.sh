#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mode="$1"
case "$mode" in
  smoke|preview|final) ;;
  *) echo "Usage: bash scripts/render.sh smoke|preview|final" >&2; exit 2;;
esac
command -v blender >/dev/null || { echo "Blender 4.x is required." >&2; exit 127; }
command -v ffmpeg >/dev/null || { echo "FFmpeg required." >&2; exit 127; }
command -v ffprobe >/dev/null || { echo "FFprobe required." >&2; exit 127; }
mkdir -p build/renders build/checkpoints
if [[ "$mode" == "smoke" ]]; then
  blender -b -t 2 --python blender/scene.py -- --mode preview --scene-only --output build
  for frame in 38 68 101 138 211; do
    blender -b -t 2 build/BROKE_TRIO.blend -o "//checkpoints/check_" -F PNG -f "$frame"
  done
  echo "SMOKE ONLY: five true-3D frame checkpoints, not an MP4."
  exit 0
fi
blender -b -t 2 --python blender/scene.py -- --mode "$mode" --output build
python3 scripts/soundtrack.py build/original_score.wav
if [[ "$mode" == "preview" ]]; then
  fpsin=12
  output=build/BROKE_TRIO_preview_960x540.mp4
  width=960
  height=540
else
  fpsin=24
  output=build/BROKE_TRIO_final_1920x1080.mp4
  width=1920
  height=1080
fi
ffmpeg -hide_banner -nostdin -loglevel error -y \
  -framerate "$fpsin" -pattern_type glob -i 'build/renders/frame_*.png' \
  -i build/original_score.wav -r 24 -t 10 \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$output"
python3 scripts/validate_media.py "$output" --width "$width" --height "$height"
echo "Render available: $output"
