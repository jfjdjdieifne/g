#!/usr/bin/env python3
"""
synth_sfx.py — tiny SFX synthesizer (numpy) for the board prototype.
Outputs a 48k stereo WAV with soft, sparse, movement-linked SFX (no music).
"""
import numpy as np, wave, struct, sys, pathlib

SR = 48000

def band_noise(dur, f_lo, f_hi, seed=0):
    rng = np.random.default_rng(seed)
    n = int(SR * dur)
    x = rng.standard_normal(n)
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    lo, hi = f_lo, f_hi
    mask = np.zeros_like(freqs)
    b1 = (freqs >= lo) & (freqs <= hi)
    mask[b1] = 1.0
    # soft edges
    e = max(1, int(len(freqs) * 0.02))
    for i in range(1, e):
        mask[max(0, np.searchsorted(freqs, lo) - i)] = i / e
        j = np.searchsorted(freqs, hi) + i
        if j < len(mask):
            mask[j] = 1 - i / e
    y = np.fft.irfft(X * mask, n)
    m = np.max(np.abs(y)) or 1.0
    return y / m

def env_ad(n, atk=0.05, dec=0.5, power=1.5):
    a = max(1, int(n * atk)); d = n - a
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 1.2
    e[a:] = np.exp(-np.linspace(0, 6, d) * dec ** -0.5) if dec > 0 else 1
    return e

def sine_sweep(dur, f0, f1):
    n = int(SR * dur); t = np.arange(n) / SR
    k = (f1 - f0) / max(dur, 1e-6)
    ph = 2 * np.pi * (f0 * t + 0.5 * k * t * t)
    return np.sin(ph)

def tick(f=2100, dur=0.04, gain=0.13):
    n = int(SR * dur); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 90)
    c = band_noise(dur, 2500, 9000, seed=7) * np.exp(-t * 260) * 0.5
    return (s + c) * gain

def thud(f0=110, f1=62, dur=0.26, gain=0.3):
    s = sine_sweep(dur, f0, f1)
    n = len(s); t = np.arange(n) / SR
    return s * np.exp(-t * 16) * gain

def paper(dur=0.12, gain=0.09):
    x = band_noise(dur, 1800, 7200, seed=11)
    n = len(x); t = np.arange(n) / SR
    return x * np.exp(-t * 40) * gain

def whoosh(dur=0.6, f_lo=140, f_hi=2600, gain=0.26, rise=False, seed=3):
    x = band_noise(dur, f_lo, f_hi, seed=seed)
    n = len(x); t = np.arange(n) / SR
    if rise:
        e = (t / dur) ** 2.2
    else:
        e = np.exp(-np.linspace(0, 5, n) ** 0.9)
        e[: int(n * 0.08)] *= np.linspace(0, 1, int(n * 0.08))
    return x * e * gain

def zipf(dur=0.1, gain=0.11, seed=5):
    x = band_noise(dur, 1600, 6800, seed=seed)
    n = len(x); t = np.arange(n) / SR
    return x * np.exp(-t * 55) * gain

def place(buf, sig, t, pan=0.0):
    i0 = int(t * SR)
    i1 = min(len(buf), i0 + len(sig))
    if i1 <= i0:
        return
    seg = sig[: i1 - i0]
    l = 0.5 * (1 - pan); r = 0.5 * (1 + pan)
    buf[i0:i1, 0] += seg * l * 2 * 0.7
    buf[i0:i1, 1] += seg * r * 2 * 0.7

def main(out, dur=8.0):
    n = int(SR * dur)
    buf = np.zeros((n, 2), dtype=np.float64)

    # ---- event map (times must match the animation timeline) ----
    place(buf, whoosh(0.55, 160, 2400, 0.24, seed=1), 0.02, 0.0)          # entry swoop
    place(buf, thud(115, 64, 0.24, 0.32), 1.02)                            # name stamp
    place(buf, tick(2100, 0.05, 0.14), 1.03, 0.05)
    place(buf, paper(0.12, 0.08), 1.04, -0.1)
    place(buf, tick(1950, 0.04, 0.12), 2.05, -0.12)                        # money settles
    place(buf, tick(2050, 0.04, 0.12), 2.55, 0.0)                          # jet settles
    place(buf, tick(1900, 0.04, 0.12), 3.25, 0.12)                         # doc settles
    place(buf, zipf(0.09, 0.10, 21), 4.35, -0.08)                          # thread 1
    place(buf, zipf(0.09, 0.10, 22), 4.62, 0.0)                            # thread 2
    place(buf, zipf(0.09, 0.10, 23), 4.88, 0.06)                           # thread 3
    place(buf, tick(1750, 0.05, 0.10), 5.07, 0.0)                          # map labels
    place(buf, whoosh(0.78, 180, 4200, 0.28, rise=True, seed=2), 5.56)     # zoom-through rise
    place(buf, thud(72, 46, 0.55, 0.20), 6.16)                             # arrive at globe
    place(buf, tick(1600, 0.05, 0.10), 6.62, -0.08)                        # arc starts
    place(buf, thud(95, 60, 0.3, 0.2), 7.42)                               # Miami pulse
    place(buf, tick(2300, 0.05, 0.11), 7.44, 0.1)

    # gentle safety limiter + normalize to a soft peak
    peak = np.max(np.abs(buf)) or 1.0
    buf = buf / peak * 0.32
    pcm = (buf * 32767).astype(np.int16)

    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out} ({dur}s, peak normalized to 0.32)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/demo_mix.wav",
         float(sys.argv[2]) if len(sys.argv) > 2 else 8.0)
