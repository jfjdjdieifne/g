#!/usr/bin/env python3
"""
synth_sfx_v3.py — professional-feeling SFX bed for board_motion_proto_v3 (10s, no music).
Design goals: smooth, warm, no harsh clicks. All sounds built from filtered noise +
soft tonal layers with click-free envelopes.
"""
import numpy as np, wave, pathlib, sys

SR = 48000
rng = np.random.default_rng(20261013)

# ---------- primitives ----------
def fft_band(dur, lo, hi, tilt=0.0, seed=0):
    """Band-limited noise with soft edges and optional spectral tilt."""
    r = np.random.default_rng(seed)
    n = int(SR * dur)
    x = r.standard_normal(n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.zeros_like(f)
    band = (f >= lo) & (f <= hi)
    m[band] = 1.0
    # soft shoulders (20% of band width)
    w = max(1.0, (hi - lo) * 0.2)
    lo_i, hi_i = np.searchsorted(f, [lo, hi])
    for i in range(1, 60):
        j0 = lo_i - i
        if j0 >= 0: m[j0] = max(m[j0], 1 - i / 60)
        j1 = hi_i + i
        if j1 < len(m): m[j1] = max(m[j1], 1 - i / 60)
    if tilt:  # -tilt = darker, +tilt = brighter
        with np.errstate(divide="ignore"):
            m = m * np.clip((f / max(hi, 1.0)) ** tilt, 0, 1.2)
    y = np.fft.irfft(X * m, n)
    return y / (np.max(np.abs(y)) or 1.0)

def env_smooth(n, attack, release, curve=1.0):
    """Click-free envelope: raised-cosine attack, exponential-ish release."""
    a = max(1, int(n * attack)); r = max(1, n - a)
    e = np.empty(n)
    e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    e[a:] = np.exp(-np.linspace(0, 6 * curve, r))
    e[a:] *= 1 - np.linspace(0, 1, r) * 0.0
    return e

def glide(dur, f0, f1, amp=1.0, kind="exp"):
    n = int(SR * dur); t = np.arange(n) / SR
    if kind == "exp":
        f = f0 * (f1 / f0) ** (t / max(dur, 1e-6))
    else:
        f = f0 + (f1 - f0) * (t / max(dur, 1e-6))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * amp

# ---------- designed sounds ----------
def swoosh(dur=0.55, lo=180, hi=2400, gain=0.30, up=False, seed=11):
    x = fft_band(dur, lo, hi, tilt=-0.4, seed=seed)
    n = len(x)
    if up:
        e = np.sin(np.linspace(0, np.pi / 2, n)) ** 2.2
    else:
        e = env_smooth(n, 0.22, 0.42, curve=1.1)
    # gentle spectral glide illusion: stack two bands cross-faded
    x2 = fft_band(dur, lo * 0.6, hi * 0.55, tilt=-0.5, seed=seed + 7)
    w = np.linspace(0, 1, n)
    y = x * (1 - w) + x2 * w
    return y * e * gain

def landing(dur=0.42, f0=88, f1=52, gain=0.34):
    low = glide(dur, f0, f1, kind="exp")
    e = env_smooth(len(low), 0.06, 1.35, curve=1.0)
    body = fft_band(dur, 60, 420, tilt=-0.6, seed=3) * env_smooth(len(low), 0.05, 1.8, 0.9)
    return (low * 0.9 + body * 0.5) * e * gain

def pen_stroke(dur=0.34, gain=0.085, seed=21, darkness=0.55):
    x = fft_band(dur, 900, 5200, tilt=-darkness, seed=seed)
    n = len(x); t = np.arange(n) / SR
    e = env_smooth(n, 0.28, 0.5, curve=0.8) * (1 + 0.25 * np.sin(2 * np.pi * 9 * t))
    e = np.clip(e, 0, None)
    return x * e * gain

def pen_flourish(dur=0.72, gain=0.10, seed=33):
    """Longer, softer stroke for the signature sweep."""
    x = fft_band(dur, 700, 4200, tilt=-0.6, seed=seed)
    n = len(x); t = np.arange(n) / SR
    e = env_smooth(n, 0.30, 0.75, curve=0.7)
    e *= 1 + 0.18 * np.sin(2 * np.pi * 5.5 * t + 1.2)
    return x * np.clip(e, 0, None) * gain

def type_key(gain=0.10, seed=4, pitch=1.0):
    dur = 0.055
    body = glide(0.05, 420 * pitch, 380 * pitch, kind="exp") * 0.5
    clack = fft_band(dur, 1200, 3200, tilt=-0.7, seed=seed + int(pitch * 10))
    n = min(len(body), len(clack))
    e = env_smooth(n, 0.10, 1.9, curve=1.0)
    return (body[:n] + clack[:n] * 0.8) * e * gain

def felt_thud(dur=0.5, f0=64, f1=44, gain=0.30):
    low = glide(dur, f0, f1) 
    e = env_smooth(len(low), 0.05, 1.9, curve=0.95)
    felt = fft_band(dur, 90, 900, tilt=-0.8, seed=9) * 0.28
    n = min(len(low), len(felt))
    return (low[:n] * 0.85 + felt[:n]) * e[:n] * gain

def shimmer(dur=1.6, gain=0.05, seed=57):
    x = fft_band(dur, 2600, 7600, tilt=-0.3, seed=seed)
    n = len(x)
    e = env_smooth(n, 0.45, 0.65, curve=0.6)
    return x * e * gain

def paper_breath(dur=0.30, gain=0.05, seed=61):
    x = fft_band(dur, 400, 2400, tilt=-0.8, seed=seed)
    n = len(x)
    return x * env_smooth(n, 0.4, 0.6, curve=0.7) * gain

def place(buf, sig, t, pan=0.0, gain=1.0):
    i0 = int(t * SR); i1 = min(len(buf), i0 + len(sig))
    if i1 <= i0: return
    s = sig[: i1 - i0] * gain
    l = 0.5 * (1 - pan); r = 0.5 * (1 + pan)
    buf[i0:i1, 0] += s * l * 1.35
    buf[i0:i1, 1] += s * r * 1.35

def main(out, dur=10.0):
    n = int(SR * dur); buf = np.zeros((n, 2))
    # --- entry ---
    place(buf, swoosh(0.50, 170, 2600, 0.30, seed=101), 0.00)
    place(buf, landing(0.44, 92, 50, 0.34), 0.42)
    place(buf, paper_breath(0.3, 0.045, 111), 0.55, -0.06)
    # --- THIS IS (handwriting) ---
    place(buf, pen_stroke(0.34, 0.075, 121, .5), 0.56, -0.10)
    place(buf, pen_stroke(0.30, 0.065, 122, .5), 0.78, 0.02)
    # --- typed date (three soft keys) ---
    for i, (tt, p) in enumerate([(0.80, 1.00), (0.99, 1.06), (1.20, 0.96), (1.42, 1.03)]):
        place(buf, type_key(0.095, 131 + i, p), tt, 0.04)
    # --- signature: long smooth strokes ---
    place(buf, pen_flourish(0.78, 0.095, 141), 1.04, -0.02)
    place(buf, pen_flourish(0.55, 0.075, 142), 1.42, 0.0)
    place(buf, pen_stroke(0.45, 0.06, 143, .6), 1.72, 0.05)
    # --- transformation ---
    place(buf, felt_thud(0.62, 62, 42, 0.26), 1.92)
    place(buf, fft_band(0.9, 120, 800, tilt=-0.9, seed=151) * env_smooth(int(SR * 0.9), 0.5, 0.7, 0.7) * 0.10, 2.05)
    place(buf, pen_stroke(0.40, 0.07, 152, .45), 2.42, -0.06)   # A
    place(buf, pen_stroke(0.40, 0.07, 153, .45), 2.55, 0.0)     # MYSTERIOUS
    place(buf, pen_stroke(0.36, 0.065, 154, .45), 2.72, 0.06)   # FIGURE
    place(buf, pen_stroke(0.44, 0.075, 155, .5), 2.88, -0.02)   # cool ? stroke
    place(buf, type_key(0.075, 161, 0.9), 3.38, 0.04)           # ? dot -> soft key tick
    # --- silence beat 3.30–3.72 (purposely empty) ---
    # --- pan right ---
    place(buf, swoosh(0.62, 200, 2200, 0.22, seed=171), 3.74)
    place(buf, paper_breath(0.3, 0.04, 172), 3.98, 0.08)
    # --- BUT WHY ---
    place(buf, pen_stroke(0.36, 0.075, 181, .5), 4.46, -0.06)
    place(buf, pen_stroke(0.36, 0.075, 182, .5), 4.74, 0.0)
    place(buf, pen_stroke(0.30, 0.06, 183, .5), 5.06, 0.04)
    place(buf, pen_flourish(0.95, 0.10, 191), 5.46, 0.03)       # big orange ? sweep
    place(buf, type_key(0.085, 201, 0.86), 6.31, 0.06)          # dot
    place(buf, felt_thud(0.55, 78, 50, 0.22), 6.36)             # soft accent on dot
    place(buf, shimmer(2.2, 0.045, 211), 6.45, 0.0)             # airy tail
    # --- closing fade ---
    place(buf, felt_thud(0.9, 55, 36, 0.20), 9.35)
    # --- gentle glue compressor ---
    buf = np.tanh(buf * 1.15) * 0.85
    peak = np.max(np.abs(buf)) or 1.0
    buf = buf / peak * 0.26
    pcm = (buf * 32767).astype(np.int16)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out} ({dur}s, peak 0.26)")
    # click check: max sample-to-sample jump
    d = np.max(np.abs(np.diff(pcm.astype(np.int32))))
    print(f"max sample jump: {d} (lower is smoother; clicks usually > 12000)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/v3_mix.wav",
         float(sys.argv[2]) if len(sys.argv) > 2 else 10.0)
