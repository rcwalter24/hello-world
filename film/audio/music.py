"""Procedural score for 'The Source Code of Everything' (180 s, 60 bpm grid).
Act boundaries (s): 0 | 15 | 40 | 70 | 105 | 140 | 168 | 180   -- all land on beats.
Chords change every 5 s (5-beat cycles => a gentle minimalist lilt).
Run:  /opt/mv/bin/python music.py   ->  music.wav
"""
import numpy as np
from scipy.signal import fftconvolve
from scipy.io import wavfile

SR = 44100
T_END = 180.0
N = int(SR * T_END)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)          # dry bus
WL = np.zeros(N); WR = np.zeros(N)        # reverb send


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)


def place(sig, t0, gain=1.0, pan=0.0, wet=0.3):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    sig = sig[: N - i0]
    a = np.sqrt((1 - pan) / 2); b = np.sqrt((1 + pan) / 2)
    L[i0:i0 + len(sig)] += sig * gain * a
    R[i0:i0 + len(sig)] += sig * gain * b
    WL[i0:i0 + len(sig)] += sig * gain * a * wet
    WR[i0:i0 + len(sig)] += sig * gain * b * wet


def tt(dur): return np.arange(int(SR * dur)) / SR


def pluck(f, dur=1.6):
    t = tt(dur)
    s = sum((h ** -1.4) * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (2.5 + 0.9 * h)) for h in range(1, 8))
    return s * np.minimum(t / 0.004, 1)


def bell(f, dur=5.0):
    t = tt(dur)
    parts = [(1.0, 1.0, 3.2), (2.0, 0.55, 2.4), (2.76, 0.45, 1.7), (5.4, 0.22, 1.0), (8.93, 0.10, 0.6)]
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, a, d in parts)
    return s * np.minimum(t / 0.002, 1)


def pad(f, dur, att=1.5, rel=2.0, bright=8):
    t = tt(dur)
    s = np.zeros_like(t)
    for det in (-0.0035, 0.0, 0.0035):
        ph = rng.uniform(0, 2 * np.pi)
        for h in range(1, bright + 1):
            s += (1.0 / h) * np.sin(2 * np.pi * f * (1 + det) * h * t + ph * h)
    env = np.minimum(t / att, 1) * np.minimum((dur - t) / rel, 1).clip(0, 1)
    return s * env / (np.abs(s).max() + 1e-9)


def sub(f, dur, att=0.8, rel=1.5):
    t = tt(dur)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * \
        np.minimum(t / att, 1) * np.minimum((dur - t) / rel, 1).clip(0, 1)


def kick(strength=1.0):
    t = tt(0.55)
    f = 42 + 90 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) * strength


def heart(strength=1.0):            # soft two-thump heartbeat
    s = np.zeros(int(SR * 0.9))
    k = kick(strength)
    s[:len(k)] += k
    k2 = kick(strength * 0.6)[: int(SR * 0.4)]
    s[int(SR * 0.28): int(SR * 0.28) + len(k2)] += k2
    return s


def hat(vol=1.0):
    t = tt(0.09)
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0)                # crude high-pass
    return n * np.exp(-t * 55) * vol


def clap(vol=1.0):
    t = tt(0.25)
    n = rng.standard_normal(len(t))
    n = np.convolve(n, np.ones(3) / 3, mode="same")
    return n * (np.exp(-t * 22)) * vol


def boom(dur=3.0):
    t = tt(dur)
    f = 34 + 60 * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    n = np.convolve(rng.standard_normal(len(t)), np.ones(40) / 40, mode="same") * 6
    return (np.sin(ph) * np.exp(-t * 1.3) + 0.35 * n * np.exp(-t * 3.0))


def riser(dur):
    t = tt(dur)
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0)
    swell = (t / dur) ** 2.2
    f = 180 * (12 ** (t / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.25
    return (0.55 * n + tone) * swell


# ---------------------------------------------------------------- harmony
# root MIDI, chord tones (semitones above root)
CH = {
    "Dm": (50, [0, 7, 12, 15, 19]),  "Bb": (46, [0, 7, 12, 16, 19]),
    "F":  (53, [0, 7, 12, 16, 19]),  "C":  (48, [0, 7, 12, 16, 19]),
    "Gm": (55, [0, 7, 12, 15, 19]),  "A":  (45, [0, 7, 12, 16, 19]),
    "D":  (50, [0, 7, 12, 16, 19]),
}
PROG_OPEN = ["Dm", "Bb", "F", "C"]        # acts 1-2, open & hopeful
PROG_DEEP = ["Dm", "Bb", "Gm", "A"]       # acts 3-5, darker with dominant pull


def chord_at(t):
    if t >= 168: return "D"
    k = int(t // 5)
    return (PROG_OPEN if t < 70 else PROG_DEEP)[k % 4]


def arp_notes(name, octave_shift=0):
    root, tones = CH[name]
    return [root + 12 + tn + 12 * octave_shift for tn in tones]


ARP_PAT = [0, 1, 2, 3, 4, 3, 2, 1, 2, 1]                  # 10 eighths / chord


# ---------------------------------------------------------------- act 0  (0-15)
place(bell(hz(74)), 1.6, 0.22, -0.1, 0.5)                  # D5 : the point appears
place(bell(hz(81)), 4.5, 0.30, 0.2, 0.5)                   # A5
place(bell(hz(77)), 7.0, 0.30, -0.2, 0.5)                  # F5 : the line
place(bell(hz(74)), 10.0, 0.3, 0.1, 0.5)                   # D5 : the circle
for i, t0 in enumerate(np.arange(2.0, 15.0, 1.0)):       # heartbeat, fades in
    place(heart(1.0), t0, 0.10 + 0.22 * min(i / 8, 1), 0, 0.15)
place(pad(hz(38), 13.5, 4.0, 2.0, 5), 1.5, 0.28, 0, 0.5)     # D2 drone
place(pad(hz(45), 12.0, 5.0, 2.0, 5), 3.0, 0.18, 0, 0.5)     # A2
place(pad(hz(62), 9.0, 5.0, 3.0, 4), 6.0, 0.06, 0, 0.8)      # D4 air

# ---------------------------------------------------------------- acts 1-5 : per-chord layers
ACTS = [(15, 40), (40, 70), (70, 105), (105, 140), (140, 168)]


def act_of(t):
    for i, (a, b) in enumerate(ACTS):
        if a <= t < b: return i + 1
    return 0


def energy(t):   # 0..1 arc across the film
    knots = [(0, .05), (15, .12), (40, .30), (70, .48), (105, .72), (140, .85), (160, 1.0), (168, .35), (180, .25)]
    xs, ys = zip(*knots); return float(np.interp(t, xs, ys))


for t0 in np.arange(15.0, 168.0, 5.0):
    name = chord_at(t0); a = act_of(t0); e = energy(t0)
    root, tones = CH[name]
    dur = min(5.0, 168.0 - t0)
    # pad chord (3 voices) - grows with energy
    for k, tn in enumerate([0, 7, 12 + (3 if 'm' in name else 4)]):
        place(pad(hz(root + 12 + tn), dur + 1.5, 1.6, 2.0, 6 if a < 4 else 9), t0 - 0.2,
              (0.10 + 0.10 * e) , (k - 1) * 0.5, 0.45)
    # bass
    place(sub(hz(root - 12 + (0 if root > 45 else 12)), dur + 0.3, 0.5, 1.0), t0, 0.32 if a >= 2 else 0.2, 0, 0.1)
    # arpeggio
    notes = arp_notes(name, 1 if a >= 4 else 0)
    if a == 1: step, gain = 1.0, 0.13         # quarter notes
    elif a == 2: step, gain = 0.5, 0.12
    elif a == 3: step, gain = 0.5, 0.13
    elif a == 4: step, gain = 0.25, 0.09
    else: step, gain = 0.5, 0.12
    nsteps = int(round(dur / step))
    for i in range(nsteps):
        idx = ARP_PAT[i % len(ARP_PAT)] if a != 4 else ARP_PAT[(i // 1) % len(ARP_PAT)]
        n = notes[idx % len(notes)] + (12 if (a == 5 and i % 2) else 0)
        place(pluck(hz(n), 1.4), t0 + i * step, gain * (0.85 + 0.3 * ((i % 5) == 0)),
              np.sin(i * 0.7) * 0.5, 0.35)
    # long bell on chord change (top voice)
    place(bell(hz(root + 24 + (3 if 'm' in name else 4) * (a >= 3))), t0, 0.16 + 0.05 * e, rng.uniform(-.4, .4), 0.6)

# rhythm: kick / hats / claps by act
for t0 in np.arange(15.0, 168.0, 1.0):
    a = act_of(t0)
    if a == 1 and int(t0) % 2 == 0: place(heart(1.0), t0, 0.16, 0, 0.1)
    if a == 2: place(kick(0.9), t0, 0.22, 0, 0.08)
    if a >= 3: place(kick(1.0), t0, 0.30 if a == 3 else 0.36, 0, 0.08)
    if a >= 3:
        place(hat(1.0), t0 + 0.5, 0.06 if a == 3 else 0.075, 0.3, 0.2)
        if a >= 4: place(hat(1.0), t0 + 0.25, 0.04, -0.3, 0.2); place(hat(1.0), t0 + 0.75, 0.04, 0.3, 0.2)
    if a >= 4 and int(t0) % 5 in (1, 3): place(clap(1.0), t0, 0.10, 0, 0.5)

# act-boundary hits (impact + rising energy)
for tb, g in [(15, 0.35), (40, 0.4), (70, 0.5), (105, 0.6), (140, 0.65)]:
    place(boom(3.0), tb, g, 0, 0.35)
    place(bell(hz(74 + (0 if tb < 105 else -12))), tb, 0.18, 0, 0.6)

# act 4 dark drone + ζ-zero tolling
for t0 in np.arange(105.0, 140.0, 7.0):
    place(pad(hz(26), 9.0, 3.0, 3.0, 4), t0, 0.22, 0, 0.5)         # D1 rumble
for k, t0 in enumerate([120.5, 122.5, 124.0, 125.5, 127.0, 128.0, 129.5, 130.0]):
    place(bell(hz(86 + (k % 4) * 2 - 4), 4), t0, 0.06, rng.uniform(-.7, .7), 0.7)   # tolling motes

# act 5 braid: counter-melody in bells + big riser
motif = [74, 77, 81, 79, 77, 74, 72, 69]
for i, m in enumerate(motif * 2):
    t = 141 + i * 1.5
    if t < 165: place(bell(hz(m + 12), 3.5), t, 0.10, np.sin(i) * 0.6, 0.6)
place(riser(8.0), 160.0, 0.30, 0, 0.35)
for i, t in enumerate(np.arange(164.0, 168.0, 0.25)):                  # snare-ish roll
    place(clap(1.0), t, 0.05 + 0.10 * (i / 16), 0, 0.3)

# ---------------------------------------------------------------- act 6 (168-180)
place(boom(5.0), 168.0, 0.85, 0, 0.5)
place(riser(0.8)[::-1], 167.2, 0.2, 0, 0.3)
for k, tn in enumerate([0, 7, 12, 16, 19, 24]):                          # D major bloom
    place(pad(hz(50 + tn), 12.5, 1.2, 4.0, 10), 168.0, 0.16, (k - 2.5) * 0.25, 0.55)
place(sub(hz(38), 12.0, 0.3, 4.0), 168.0, 0.4, 0, 0.1)
for t, m, g in [(168.6, 74, .30), (169.6, 81, .22), (170.8, 86, .22), (172.0, 90, .22), (173.4, 93, .20),
                (174.8, 86, .16), (176.0, 90, .14), (177.2, 81, .12), (178.0, 74, .22)]:
    place(bell(hz(m + 0), 6.0), t, g, rng.uniform(-.4, .4), 0.7)

# ---------------------------------------------------------------- reverb + master
def make_ir(sec=3.2):
    t = tt(sec)
    out = []
    for _ in range(2):
        n = rng.standard_normal(len(t)) * np.exp(-t / 0.85)
        k = np.ones(6) / 6                                          # mild lowpass
        n = np.convolve(n, k, mode="same"); out.append(n / np.sqrt((n ** 2).sum()))
    return out


irL, irR = make_ir()
wl = fftconvolve(WL, irL)[:N] * 1.0
wr = fftconvolve(WR, irR)[:N] * 1.0
outL = L + wl; outR = R + wr

# leveler: shape the overall dynamics arc (quiet start -> big finale)
from scipy.ndimage import gaussian_filter1d
mono = 0.5 * (outL + outR)
win = SR
nw = N // win
rms_db = np.array([20 * np.log10(np.sqrt((mono[i * win:(i + 1) * win] ** 2).mean()) + 1e-9) for i in range(nw)])
rms_db = gaussian_filter1d(np.maximum(rms_db, -35), 2.5)
xs, ys = zip(*[(0, -28), (10, -25), (15, -23), (40, -20), (70, -17), (105, -14.5), (140, -13), (165, -12), (168, -14), (176, -16), (180, -19)])
target = np.interp(np.arange(nw) + 0.5, xs, ys)
g_db = gaussian_filter1d(np.clip(target - rms_db, -18, 3), 1.5)
g = np.interp(np.arange(N) / SR, np.arange(nw) + 0.5, g_db)
gain = 10 ** (g / 20)
print("pre-level rms per 10s:", np.round(rms_db[::10],1))
outL = outL * gain; outR = outR * gain

# gentle fade in/out, global energy-shaped gain, soft limiter
tt_all = np.arange(N) / SR
fade = np.minimum(tt_all / 1.0, 1) * np.minimum((T_END - tt_all) / 3.0, 1).clip(0, 1)
def soft(x): return np.tanh(x * 1.6) / np.tanh(1.6)
outL = soft(outL * fade); outR = soft(outR * fade)
peak = max(np.abs(outL).max(), np.abs(outR).max())
scale = 0.89 / peak
stereo = np.stack([outL, outR], axis=1) * scale
wavfile.write("music.wav", SR, (stereo * 32767).astype(np.int16))

# report loudness per act
for name, (a, b) in zip(["a0", "a1", "a2", "a3", "a4", "a5", "a6"],
                        [(0, 15), (15, 40), (40, 70), (70, 105), (105, 140), (140, 168), (168, 180)]):
    seg = stereo[int(a * SR): int(b * SR)]
    print(f"{name}: rms {20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9):6.1f} dBFS  peak {np.abs(seg).max():.2f}")
