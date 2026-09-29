"""Synthesize an ambient soundtrack with NumPy.

usage: python music.py <duration_seconds> <out.wav>

Slow evolving pad chords (detuned saws through a soft low-pass), a sub bass,
and a sparse bell arpeggio, with a simple feedback-delay "reverb".
"""
import sys
import wave

import numpy as np
from scipy.signal import lfilter

SR = 44100


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    return lfilter([1 - a], [1, -a], x)  # one-pole low-pass


def pad_note(freq, dur, rng):
    t = np.arange(int(dur * SR)) / SR
    sig = np.zeros_like(t)
    for det in (-0.12, 0.0, 0.13):
        f = freq * 2 ** (det / 12)
        ph = rng.random()
        sig += 2 * ((f * t + ph) % 1.0) - 1  # saw
    sig /= 3
    return sig


def env(n, attack, release):
    e = np.ones(n)
    a = int(attack * SR); r = int(release * SR)
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def bell(freq, dur):
    t = np.arange(int(dur * SR)) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2.76 * t)
         + 0.15 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t * 3))
    return s * np.exp(-t * 1.6) * np.minimum(1, t * 400)


def reverb(x, delays=(0.113, 0.171, 0.233, 0.297), fb=0.55, mix=0.35):
    out = x.copy()
    for d in delays:
        n = int(d * SR)
        y = x.copy()
        for k in range(1, 7):
            if k * n >= len(x):
                break
            y[k * n:] += x[:-k * n] * fb ** k
        out += mix * y / len(delays)
    return out


def main(duration, path):
    rng = np.random.default_rng(42)
    total = int((duration + 1) * SR)
    L = np.zeros(total); R = np.zeros(total)
    # D minor-ish, hopeful progression: Dm9 - Bbmaj7 - Fmaj7 - C6/9  (in MIDI)
    chords = [
        [50, 57, 62, 65, 69, 76],
        [46, 53, 58, 62, 65, 69],
        [41, 53, 57, 60, 64, 69],
        [48, 55, 62, 64, 67, 74],
    ]
    bar = 8.0
    t0 = 0.0
    ci = 0
    while t0 < duration:
        ch = chords[ci % 4]
        dur = bar + 3.0
        n = int(dur * SR)
        s = int(t0 * SR)
        e = min(total, s + n)
        pad = np.zeros(n)
        for m in ch[1:]:
            pad += pad_note(midi(m), dur, rng) * 0.12
        pad = lowpass(pad, 900 + 500 * np.sin(ci))
        pad *= env(n, 2.5, 3.0)
        t = np.arange(n) / SR
        sub = np.sin(2 * np.pi * midi(ch[0] - 12) * t) * 0.22 * env(n, 1.5, 3.0)
        pan = 0.5 + 0.2 * np.sin(np.arange(n) / SR * 0.3 + ci)
        L[s:e] += (pad * pan + sub)[: e - s]
        R[s:e] += (pad * (1 - pan) + sub)[: e - s]
        # bells: a slow arpeggio over the upper chord tones
        if ci >= 1:
            tones = ch[2:] + [ch[3] + 12]
            for k in range(8):
                bt = t0 + 0.5 + k * 1.0 + (0.5 if k % 3 == 2 else 0)
                if bt >= duration - 2:
                    break
                f = midi(tones[(k * 3 + ci) % len(tones)] + 12)
                b = bell(f, 3.5) * 0.07
                bs = int(bt * SR); be = min(total, bs + len(b))
                p = rng.random()
                L[bs:be] += b[: be - bs] * p
                R[bs:be] += b[: be - bs] * (1 - p)
        t0 += bar
        ci += 1
    L = reverb(L); R = reverb(R, delays=(0.127, 0.181, 0.241, 0.311))
    # global fade in / out
    fade = np.ones(total)
    fi, fo = int(3 * SR), int(6 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    end = int(duration * SR)
    fade[end - fo:end] = np.linspace(1, 0, fo)
    fade[end:] = 0
    L *= fade; R *= fade
    peak = max(np.abs(L).max(), np.abs(R).max())
    L = L / peak * 0.8; R = R / peak * 0.8
    data = (np.stack([L, R], 1)[:end] * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    main(float(sys.argv[1]), sys.argv[2])
