#!/usr/bin/env python3
"""synth_sfx_demo2.py — 10s SFX bed for board_motion_proto_v2_cinematic (no music)."""
import numpy as np, wave, pathlib, sys

SR = 48000

def band_noise(dur, f_lo, f_hi, seed=0):
    rng = np.random.default_rng(seed); n = int(SR * dur)
    x = rng.standard_normal(n); X = np.fft.rfft(x); freqs = np.fft.rfftfreq(n, 1 / SR)
    mask = ((freqs >= f_lo) & (freqs <= hi_or(f_hi))).astype(float)
    y = np.fft.irfft(X * mask, n); m = np.max(np.abs(y)) or 1.0
    return y / m

def hi_or(v): return v

def sine_sweep(dur, f0, f1):
    n = int(SR * dur); t = np.arange(n) / SR
    k = (f1 - f0) / max(dur, 1e-6)
    return np.sin(2 * np.pi * (f0 * t + 0.5 * k * t * t))

def tick(f=2100, dur=0.04, gain=0.13):
    n = int(SR * dur); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 90)
    c = band_noise(dur, 2500, 9000, seed=7) * np.exp(-t * 260) * 0.5
    return (s + c) * gain

def thud(f0=110, f1=62, dur=0.26, gain=0.3):
    s = sine_sweep(dur, f0, f1); n = len(s); t = np.arange(n) / SR
    return s * np.exp(-t * 16) * gain

def paper(dur=0.12, gain=0.09):
    x = band_noise(dur, 1800, 7200, seed=11); n = len(x); t = np.arange(n) / SR
    return x * np.exp(-t * 40) * gain

def whoosh(dur=0.6, f_lo=140, f_hi=2600, gain=0.26, rise=False, seed=3):
    x = band_noise(dur, f_lo, f_hi, seed=seed); n = len(x); t = np.arange(n) / SR
    if rise:
        e = (t / dur) ** 2.2
    else:
        e = np.exp(-np.linspace(0, 5, n) ** 0.9)
        e[: int(n * 0.08)] *= np.linspace(0, 1, int(n * 0.08))
    return x * e * gain

def zipf(dur=0.1, gain=0.11, seed=5):
    x = band_noise(dur, 1600, 6800, seed=seed); n = len(x); t = np.arange(n) / SR
    return x * np.exp(-t * 55) * gain

def swell(dur=0.5, f0=58, f1=50, gain=0.10):
    s = sine_sweep(dur, f0, f1); n = len(s); t = np.arange(n) / SR
    e = np.clip(t / dur, 0, 1) ** 1.5
    return s * e * gain

def place(buf, sig, t, pan=0.0):
    i0 = int(t * SR); i1 = min(len(buf), i0 + len(sig))
    if i1 <= i0: return
    seg = sig[: i1 - i0]
    l = 0.5 * (1 - pan); r = 0.5 * (1 + pan)
    buf[i0:i1, 0] += seg * l * 1.4
    buf[i0:i1, 1] += seg * r * 1.4

def main(out, dur=10.0):
    n = int(SR * dur); buf = np.zeros((n, 2))
    # entry
    place(buf, whoosh(0.42, 140, 2600, 0.28, seed=1), 0.00)
    place(buf, thud(120, 66, 0.22, 0.30), 0.46)
    place(buf, tick(2200, 0.05, 0.12), 0.52, 0.05)
    place(buf, paper(0.12, 0.06), 0.66, -0.1)
    # THIS IS + name writes
    place(buf, tick(2100, 0.04, 0.11), 1.00, -0.10)
    place(buf, tick(2000, 0.04, 0.09), 1.28, 0.0)
    place(buf, tick(2050, 0.04, 0.10), 1.52, 0.10)
    place(buf, zipf(0.09, 0.07, 31), 1.62, 0.0)      # underline
    # transformation
    place(buf, paper(0.18, 0.09), 2.02, -0.06)
    place(buf, swell(0.55, 58, 49, 0.10), 2.10)
    place(buf, thud(70, 44, 0.50, 0.22), 2.30)
    place(buf, zipf(0.10, 0.10, 41), 2.70, -0.05)     # ? stroke
    place(buf, tick(2350, 0.05, 0.09), 3.02, 0.05)     # ? dot
    # 3.30–4.30 silence beat (intentionally empty)
    # pan right + threads
    place(buf, whoosh(0.55, 200, 3000, 0.20, seed=2), 4.32)
    place(buf, zipf(0.08, 0.07, 21), 4.52, -0.08)
    place(buf, zipf(0.08, 0.07, 22), 4.70, 0.0)
    place(buf, zipf(0.08, 0.07, 23), 4.90, 0.08)
    # BUT WHY writes
    place(buf, paper(0.10, 0.05), 5.30, -0.05)
    place(buf, paper(0.10, 0.05), 5.55, 0.05)
    place(buf, paper(0.11, 0.06), 5.80, 0.10)
    place(buf, zipf(0.12, 0.12, 51), 5.95, 0.05)       # big ? stroke
    place(buf, tick(2300, 0.05, 0.10), 6.64, 0.10)     # dot
    place(buf, thud(95, 58, 0.28, 0.20), 6.74)         # WHY pop
    place(buf, zipf(0.10, 0.08, 52), 6.72, 0.0)        # underline sweep
    # finale
    place(buf, tick(1900, 0.05, 0.08), 8.40, -0.05)
    place(buf, thud(60, 40, 0.50, 0.16), 9.80)
    peak = np.max(np.abs(buf)) or 1.0
    buf = buf / peak * 0.30
    pcm = (buf * 32767).astype(np.int16)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out} ({dur}s)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/demo2_mix.wav",
         float(sys.argv[2]) if len(sys.argv) > 2 else 10.0)
