#!/usr/bin/env python3
"""Original procedural score, no borrowed samples."""
import argparse
import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 48000
DURATION = 10.0
RNG = random.Random(20261106)

def envelope(t, a, b, attack=0.07, release=0.22):
    return max(0.0, min(1.0, (t-a)/attack, (b-t)/release))

def hit(t, when, decay=.42):
    d = t - when
    return math.exp(-d / decay) if 0 <= d < 2 else 0

def make_audio(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    filt_l = filt_r = 0.0
    frames = bytearray()
    for i in range(int(SAMPLE_RATE * DURATION)):
        t = i / SAMPLE_RATE
        n = RNG.uniform(-1, 1)
        filt_l = .988 * filt_l + .012 * n
        filt_r = .982 * filt_r + .018 * n
        ambient = math.sin(2 * math.pi * 42 * t) * .11 + math.sin(2 * math.pi * 57 * t) * .065
        leftbeam = envelope(t, .85, 1.96, .25, .3)
        rightbeam = envelope(t, 2.15, 3.22, .25, .3)
        entrance = envelope(t, 3.35, 4.8, .4, .55) * math.sin(2 * math.pi * (80*t + 2.5*t*t)) * .10
        fracture = hit(t, 5.72, .50) * .19
        final = hit(t, 8.7, .70) * .22
        tone = math.sin(2 * math.pi * 68*t) + .36*math.sin(2 * math.pi * 101*t)
        shared = ambient + entrance + (fracture + final) * tone
        dust = envelope(t, 5.7, 8.6, .12, .4) * n * .055
        l = shared + leftbeam * (.17*filt_l + .08) + dust + .028*filt_l
        r = shared + rightbeam * (.17*filt_r + .08) + dust + .028*filt_r
        frames.extend(struct.pack("<hh", int(max(-.82, min(.82, l))*32767),
                                  int(max(-.82, min(.82, r))*32767)))
    with wave.open(str(path), "wb") as wav:
        wav.setframerate(SAMPLE_RATE)
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.writeframes(frames)
    print("Original procedural score:", path)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("output")
    make_audio(p.parse_args().output)
