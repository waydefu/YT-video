#!/usr/bin/env python3
"""Validate MP4 metadata. Framing/anatomy/audio perception still need human QA."""
import argparse
import json
import subprocess
import sys
from fractions import Fraction

def validate(path, width=1920, height=1080):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams",
        "-show_format", "-of", "json", path],
        check=True, capture_output=True, text=True)
    info = json.loads(result.stdout)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not video or not audio:
        raise AssertionError("Expected video AND original audio streams")
    if (video["width"], video["height"]) != (width, height):
        raise AssertionError("Unexpected export dimensions")
    if video["width"] * 9 != video["height"] * 16:
        raise AssertionError("Expected exact 16:9")
    if video.get("codec_name") != "h264" or audio.get("codec_name") != "aac":
        raise AssertionError("Expected H264/AAC")
    if Fraction(video["avg_frame_rate"]) != 24:
        raise AssertionError("Expected 24 fps")
    if audio.get("sample_rate") != "48000":
        raise AssertionError("Expected 48 kHz")
    duration = float(info["format"]["duration"])
    if not (9.75 <= duration <= 10.2):
        raise AssertionError("Unexpected duration " + str(duration))
    print(f"PASS metadata: {width}x{height} 16:9, 24fps, h264/aac, {duration:.3f}s")
    print("NOT VERIFIED by metadata: layout, anatomy, text cropping, motion, smoke realism, perceived sound.")
    return True

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    args = p.parse_args()
    try:
        validate(args.file, args.width, args.height)
    except (AssertionError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as err:
        print("FAIL:", err, file=sys.stderr)
        sys.exit(1)
