#!/usr/bin/env python3
"""Original V4-A/B ident score, no copyrighted music or stock samples.

Creates 6.25 s 48kHz stereo PCM for separate sequential spotlights, ambient
smoke and slow marble emergence. No shattering sounds in this opening shot.
"""
import argparse
import math
import random
import struct
import wave
from pathlib import Path

RATE=48000
DURATION=6.25
RNG=random.Random(20261106)

def ease(x):
    x=max(0.0,min(1.0,x))
    return x*x*(3.0-2.0*x)

def pulse(t,at,duration):
    if t < at or t > at+duration:
        return 0.0
    return math.sin(math.pi*(t-at)/duration)**2

def generate(path):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    lpf_l=lpf_r=0.0
    audio=bytearray()
    peak=0.0
    for i in range(int(RATE*DURATION)):
        t=i/RATE
        lpf_l=.993*lpf_l+.007*RNG.uniform(-1,1)
        lpf_r=.993*lpf_r+.007*RNG.uniform(-1,1)
        left=pulse(t,.72,1.22)
        right=pulse(t,2.12,1.00)
        rise=ease((t-3.35)/2.1)
        drone=(math.sin(2*math.pi*42*t)*.037 + math.sin(2*math.pi*63*t)*.025)
        textured_wind=(lpf_l+lpf_r)*.10
        # Left and right alternately brighten a different channel.
        a=drone+textured_wind+rise*.065*math.sin(2*math.pi*56*t)
        click_l=left*.04*math.sin(2*math.pi*(110*t+16*t*t))
        click_r=right*.04*math.sin(2*math.pi*(104*t+14*t*t))
        L=a+click_l+left*.09*lpf_l+right*.013*lpf_l
        R=a+click_r+right*.09*lpf_r+left*.013*lpf_r
        L*=.88;R*=.88
        peak=max(peak,abs(L),abs(R))
        audio+=struct.pack('<hh',int(max(-.95,min(.95,L))*32767),int(max(-.95,min(.95,R))*32767))
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(audio)
    print(f'Original 6.25 s score: {path}, approximate sample peak={peak:.3f}')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('output')
    generate(p.parse_args().output)
