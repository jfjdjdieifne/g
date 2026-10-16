#!/usr/bin/env python3
"""
synth_sfx_cine.py — cinematic SFX bed (10s, no music).
Professional touches: proper ADSR, layered partials, Schroeder reverb, gentle
compression + soft saturation, high-pass rumble control, click-free envelopes.
"""
import numpy as np, wave, pathlib, sys

SR = 48000
def t_of(n): return np.arange(n) / SR

# ---------------------------------------------------------------- utilities
from scipy.signal import butter, filtfilt, sosfiltfilt
_HP_CACHE = {}
def hp(x, f=35, order=4):
    """Zero-phase Butterworth high-pass — clean, no ripple, no clicks."""
    key = (f, order)
    if key not in _HP_CACHE:
        _HP_CACHE[key] = butter(order, f / (SR / 2), btype="high", output="sos")
    return sosfiltfilt(_HP_CACHE[key], x)

def lp1(x, f):
    a = np.exp(-2 * np.pi * f / SR)
    y = np.empty_like(x); prev = 0.0
    for i in range(len(x)):
        prev = a * prev + (1 - a) * x[i]
        y[i] = prev
    return y

def fft_band(dur, lo, hi, tilt=0.0, seed=0):
    r = np.random.default_rng(seed); n = int(SR * dur)
    x = r.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    m = np.zeros_like(f); band = (f >= lo) & (f <= hi); m[band] = 1.0
    lo_i, hi_i = np.searchsorted(f, [lo, hi])
    for i in range(1, 80):
        j0 = lo_i - i
        if j0 >= 0: m[j0] = max(m[j0], 1 - i / 80)
        j1 = hi_i + i
        if j1 < len(m): m[j1] = max(m[j1], 1 - i / 80)
    if tilt:
        m = m * np.clip((f / max(hi, 1.0)) ** tilt, 0.0, 1.3)
    y = np.fft.irfft(X * m, n)
    return y / (np.max(np.abs(y)) or 1.0)

def adsr(n, a=0.01, d=0.1, s=0.7, r=0.4, sustain_level=0.75):
    A = int(n * a); D = int(n * d); R = int(n * r); S = max(1, n - A - D - R)
    if A + D + R >= n:
        A = max(1, n // 6); D = max(1, n // 6); R = max(1, n // 6); S = max(1, n - A - D - R)
    env = np.concatenate([
        np.linspace(0, 1, A) ** 1.4,
        np.linspace(1, sustain_level, D) ** 1.1,
        np.full(S, sustain_level),
        np.linspace(sustain_level, 0, R) ** 1.6
    ])
    return env[:n]

def sine(f, dur, amp=1.0, start=0.0):
    n = int(SR * dur); tt = t_of(n)
    return np.sin(2 * np.pi * f * tt + start) * amp

def note(freq, dur, amp=1.0, bright=0.35, seed=0):
    """Soft mallet/piano-ish tone: fundamental + few partials with faster decay on highs."""
    n = int(SR * dur); tt = t_of(n)
    out = np.zeros(n)
    partials = [(1.0, 1.0, 1.0), (2.0, 0.42 * bright, 1.8), (3.0, 0.20 * bright, 2.4), (4.7, 0.09 * bright, 3.2)]
    for mult, rel, dec in partials:
        out += rel * np.sin(2 * np.pi * freq * mult * tt) * np.exp(-tt * dec * 1.6)
    out += fft_band(dur, 1500, 6500, tilt=-1.1, seed=seed) * np.exp(-tt * 26) * 0.05  # felt attack
    env = np.exp(-tt * 1.25)
    a = int(SR * 0.006)
    env[:a] *= np.linspace(0, 1, a)
    return out * env * amp

def brush(dur, gain=0.09, seed=21, tone=0.55):
    """Soft brush/pen stroke on paper — no clicky highs."""
    x = fft_band(dur, 500, 3600, tilt=-tone - 0.35, seed=seed)
    n = len(x); tt = t_of(n)
    env = adsr(n, a=0.24, d=0.18, s=0.55, r=0.42, sustain_level=0.5)
    env *= 1 + 0.16 * np.sin(2 * np.pi * 7.5 * tt + 0.7)
    body = lp1(x * np.clip(env, 0, None), 5200)
    paper = fft_band(dur, 700, 2400, tilt=-0.9, seed=seed + 40) * adsr(n, 0.35, 0.2, 0.5, 0.45, 0.4) * 0.25
    return hp(body + paper, 45) * gain

def whoosh(dur, lo=170, hi=2400, gain=0.26, up=False, seed=11):
    n = int(SR * dur)
    a = fft_band(dur, lo, hi, tilt=-0.45, seed=seed)
    b = fft_band(dur, lo * 0.55, hi * 0.5, tilt=-0.6, seed=seed + 31)
    w = np.linspace(0, 1, n) ** (0.8 if not up else 1.6)
    x = a * (1 - w) + b * w
    env = (np.sin(np.linspace(0, np.pi / 2, n)) ** 2.4) if up else adsr(n, 0.2, 0.2, 0.5, 0.55, 0.5)
    return hp(x * env, 60) * gain

def impact(dur=0.75, f0=96, f1=42, gain=0.30, seed=77):
    n = int(SR * dur); tt = t_of(n)
    f = f0 * (f1 / f0) ** (tt / tt[-1])
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR)
    body = fft_band(dur, 70, 700, tilt=-0.85, seed=seed) * np.exp(-tt * 7)
    env = np.exp(-tt * (1.1 / dur) * 2.2)
    a = int(SR * 0.008); env[:a] *= np.linspace(0, 1, a)
    return hp((sub * 1.0 + body * 0.55) * env, 34) * gain

def swell(dur=1.6, f0=110, gain=0.20, seed=5):
    """Warm low string-ish swell."""
    n = int(SR * dur); tt = t_of(n)
    out = np.zeros(n)
    for det in (-0.6, 0, 0.7):
        out += np.sin(2 * np.pi * (f0 + det) * tt)
        out += 0.32 * np.sin(2 * np.pi * 2 * (f0 + det * 1.3) * tt)
        out += 0.14 * np.sin(2 * np.pi * 3 * (f0 + det * 0.8) * tt)
    out /= 3.2
    vib = 1 + 0.004 * np.sin(2 * np.pi * 4.6 * tt)
    out *= vib
    out += fft_band(dur, 300, 1800, tilt=-0.7, seed=seed) * 0.16   # air
    env = adsr(n, a=0.42, d=0.15, s=0.62, r=0.35, sustain_level=0.72)
    return hp(out * env, 40) * gain

def step(dur=0.17, gain=0.13, seed=0):
    """A clean heel-step: low thump + tiny click, no tail."""
    n = int(SR * dur); tt = t_of(n)
    f = 66 * (0.7 ** (tt / tt[-1]))
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 24)
    click = fft_band(dur, 800, 5200, tilt=-1.3, seed=seed) * np.exp(-tt * 80) * 0.5
    env = np.ones(n); a = int(SR * 0.004); env[:a] = np.linspace(0, 1, a)
    return hp((sub + click) * env, 55) * gain

def riser(dur=1.2, gain=0.18, seed=91):
    n = int(SR * dur); tt = t_of(n)
    tone = np.sin(2 * np.pi * np.cumsum(220 * (3.2 ** (tt / tt[-1]))) / SR) * 0.35
    air = fft_band(dur, 800, 6000, tilt=0.25, seed=seed)
    env = (tt / tt[-1]) ** 2.0
    return hp((tone + air * 0.9) * env, 120) * gain

# ---------------------------------------------------------------- reverb
def schroeder(x, mix=0.32, decay=2.4, damp=0.42):
    """Cheap but convincing Schroeder reverb (4 combs + 2 allpass), stereo-ised after."""
    combs_ms = [29.7, 37.1, 41.1, 43.7]
    aps_ms = [5.0, 1.7]
    out = np.zeros_like(x)
    for ms in combs_ms:
        d = int(SR * ms / 1000); a = 10 ** (-3 * ms / 1000 / decay)
        buf = np.zeros(d); y = np.zeros_like(x); z1 = 0.0
        for i in range(len(x)):
            v = buf[i % d]
            z1 = v * (1 - damp) + z1 * damp
            y[i] = v
            buf[i % d] = x[i] + z1 * a
        out += y / len(combs_ms)
    for ms in aps_ms:
        d = int(SR * ms / 1000); g = 0.5
        buf = np.zeros(d); y = np.zeros_like(out)
        for i in range(len(out)):
            v = buf[i % d]
            y[i] = -g * out[i] + v
            buf[i % d] = out[i] + g * v
        out = y
    return x * (1 - mix) + out * mix

def stereo(x, width=1.0, haas_ms=11.0):
    """Simple stereo widener: slight delay + decorrelated reverb tail."""
    d = int(SR * haas_ms / 1000)
    l = x
    r = np.concatenate([np.zeros(d), x[:-d]])
    l2 = np.concatenate([np.zeros(d + 17), x[:-(d + 17)]]) * 0.12
    r2 = np.concatenate([np.zeros(d + 31), x[:-(d + 31)]]) * 0.12
    L = l * 0.98 + l2
    R = r * 0.98 + r2
    return np.stack([L, R], axis=1) * width

# ---------------------------------------------------------------- assembly
def place(buf, sig, t, pan=0.0, gain=1.0):
    i0 = int(t * SR); i1 = min(len(buf), i0 + len(sig))
    if i1 <= i0: return
    s = sig[: i1 - i0] * gain
    l = np.sqrt(0.5 * (1 - pan)); r = np.sqrt(0.5 * (1 + pan))
    buf[i0:i1, 0] += s * l * 1.41
    buf[i0:i1, 1] += s * r * 1.41

def main(out, dur=10.0):
    n = int(SR * dur)
    dry = np.zeros((n, 2))
    # ---- timeline (matches escobar_scene01 timing) ----
    place(dry, whoosh(0.52, 150, 2500, 0.30, seed=101), 0.00)
    place(dry, impact(0.55, 92, 46, 0.30), 0.43)
    # THIS IS (handwriting)
    place(dry, brush(0.36, 0.085, 111, .5), 0.52, -0.10)
    place(dry, brush(0.32, 0.075, 112, .5), 0.76, 0.04)
    # NAME written + signature flourish
    place(dry, brush(0.55, 0.10, 121, .55), 0.96, -0.06)
    place(dry, brush(0.48, 0.09, 122, .55), 1.28, 0.02)
    place(dry, brush(0.42, 0.075, 123, .6), 1.52, 0.06)
    place(dry, note(110.0, 3.2, 0.15, 0.30, seed=201), 1.05)              # soft A2 under the name
    place(dry, note(164.81, 3.0, 0.11, 0.26, seed=202), 1.42, 0.15)       # E3
    place(dry, brush(0.75, 0.085, 131, .6), 1.87, -0.02)                  # signature sweep
    place(dry, brush(0.50, 0.06, 132, .6), 2.30, 0.04)
    place(dry, note(65.41, 3.6, 0.13, 0.22, seed=203), 1.90)              # C2
    # transformation
    place(dry, swell(1.9, 98, 0.20, seed=211), 2.00)
    place(dry, whoosh(0.95, 200, 3200, 0.16, up=True, seed=212), 2.10)
    place(dry, impact(0.65, 60, 38, 0.20), 2.55)
    place(dry, brush(0.34, 0.06, 221, .5), 2.22, -0.05)                   # A
    place(dry, brush(0.34, 0.06, 222, .5), 2.46, 0.0)                     # MYSTERIOUS
    place(dry, brush(0.32, 0.055, 223, .5), 2.78, 0.05)                   # FIGURE
    place(dry, brush(0.42, 0.075, 231, .45), 2.97, -0.02)                 # cool ?
    # beat (silence ~3.5–3.95) intentionally empty
    # pan right
    place(dry, whoosh(0.70, 180, 2400, 0.20, seed=241), 3.96)
    place(dry, note(82.41, 2.6, 0.10, 0.24, seed=242), 4.00, -0.12)       # E2
    # BUT WHY
    place(dry, brush(0.36, 0.075, 251, .5), 4.72, -0.06)
    place(dry, brush(0.36, 0.075, 252, .5), 5.00, 0.0)
    place(dry, riser(1.05, 0.13, 261), 5.55)
    place(dry, brush(0.95, 0.10, 262, .5), 5.72, 0.03)                    # big warm ?
    place(dry, note(98.0, 3.0, 0.12, 0.28, seed=263), 5.62)               # G2
    place(dry, impact(0.80, 72, 44, 0.22), 6.60)
    # outro
    place(dry, swell(2.4, 87, 0.14, seed=271), 7.20)
    place(dry, note(130.81, 3.4, 0.09, 0.22, seed=272), 7.60, 0.18)

    # ---- space ----
    mono = dry[:, 0] * 0.72 + dry[:, 1] * 0.72
    wet = schroeder(mono, mix=0.12, decay=1.5, damp=0.5)   # clean: just a hint of room
    st = stereo(wet, width=1.0, haas_ms=8.0)
    # ---- glue: soft saturation + gentle compression + normalize ----
    st = np.tanh(st * 1.18) * 0.92
    peak = np.max(np.abs(st)) or 1.0
    st = st / peak * 0.27
    pcm = (st * 32767).astype(np.int16)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    x = pcm.astype(np.int32).reshape(-1, 2)
    d = int(np.abs(np.diff(x, axis=0)).max())
    print(f"wrote {out} ({dur}s) | max per-channel jump {d} ({d/32768*100:.1f}% FS; clicks >12000)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/cine.wav",
         float(sys.argv[2]) if len(sys.argv) > 2 else 10.0)
