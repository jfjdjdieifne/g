#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reference_motion.py — إزالة العمى عن التحليل: مختبر الحركة الفريم-دقيق للمراجع.

ليش موجود:
  الدراسة بـ 2fps بتغطي "المحتوى" بس بتفوّت أي حركة أقصر من 0.5 ثانية
  (مسحات دخان، whip pans، دخول/خروج نص سريع، فلاشات). هالأداة بتشتغل على
  مستوى الفريم الواحد وبتطلّع لكل حدث "ملف مراجعة" + قياسات رقمية.

شنو بتعمل (4 طبقات):
  1) كشف الأحداث بالملي: cuts (scene score)، فترات أسود، تجمّد صورة، صمت.
  2) قياس حركة الكاميرا رقميًا: طاقة الحركة + إزاحة (phase correlation)
     + زووم ودوران (log-polar phase correlation) — لكل 1/hz ثانية.
  3) مقاطع مراجعة: لكل حدث، clip صغير mp4 (±نافذة) + شريط فريمات دقيق
     (event_fps، افتراضي 15fps) مع تايم كود محروق. هاي هي "الفريم ورا فريم"
     للجزء يلي فيه الحركة.
  4) فيلمستريب أساسي (base_fps، افتراضي 2fps) لكل الفيديو + dossier.json
     + MOTION_INDEX.md بالعربي (جدول كل الأحداث مع القياسات وروابط المقاطع).

الاستخدام:
  python3 tools/reference_motion.py VIDEO.mp4 --video-id xkfctt5038w \
      --out analysis/xkfctt5038w [--from 0 --to 60] [--event-fps 15] [--selftest]

الاعتماديات (بعد أي reset):
  pip install -q --break-system-packages numpy pillow imageio-ffmpeg
  (ffmpeg يجي من imageio-ffmpeg — ما في ffmpeg نظامي)

قيود مقصودة:
  - الميموري منخفض: كل الفريمات بتتقري streaming، ما بنخزّن إلا قياسات (أرقام).
  - الميديا الكبيرة بتنكتب على القرص (مو /tmp).
  - المقاطع مقصوصة بالـ fast seek (-ss قبل -i): دقة ±فريم للعرض، مو للقياس.
    القياسات (1 و2) من فك الترميز الكامل — دقيقة بالملي.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

try:
    import imageio_ffmpeg

    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:  # pragma: no cover
    FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def sh(cmd, **kw):
    """Run ffmpeg with common flags. Returns CompletedProcess."""
    full = [FFMPEG, "-hide_banner", *cmd]
    return subprocess.run(full, capture_output=True, text=True, **kw)


def tc(sec: float, ms: bool = True) -> str:
    """mm:ss.mmm timecode."""
    if sec < 0:
        sec = 0.0
    m = int(sec // 60)
    s = sec - 60 * m
    return f"{m:02d}:{s:06.3f}" if ms else f"{m:02d}:{int(s):02d}"


def parse_ffmpeg_meta(stderr: str) -> dict:
    info = {"duration": 0.0, "fps": 0.0, "width": 0, "height": 0, "has_audio": False}
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", stderr)
    if m:
        info["duration"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    m = re.search(r"Stream #\d+:\d+.*?: Video:.*?, (\d+)x(\d+)", stderr)
    if m:
        info["width"], info["height"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d+\.?\d*)\s*fps", stderr)
    if m:
        info["fps"] = float(m.group(1))
    info["has_audio"] = bool(re.search(r"Stream #\d+:\d+.*?: Audio:", stderr))
    return info


def probe(path: Path) -> dict:
    r = sh(["-i", str(path)])
    info = parse_ffmpeg_meta(r.stderr)
    if info["duration"] <= 0:
        raise RuntimeError(f"can't probe {path}")
    return info


# ----------------------------------------------------------------------------
# layer 1 — event detection (frame accurate, from full decode)
# ----------------------------------------------------------------------------

def detect_cuts(path: Path, thresh: float, work: Path, soft_thresh: float = 0.12):
    """Returns (hard_cuts, soft_changes). Each item: {'t': float, 'score': float}."""
    work = Path(work)
    meta = work / "scene_meta.txt"
    vf = f"select='gt(scene,{soft_thresh})',metadata=print:file={meta}"
    sh(["-i", str(path), "-an", "-vf", vf, "-f", "null", "-"])
    hard, soft = [], []
    if meta.exists():
        cur_t, cur_s = None, None
        for line in meta.read_text(errors="ignore").splitlines():
            if line.startswith("frame:"):
                m = re.search(r"pts_time:([0-9.]+)", line)
                cur_t = float(m.group(1)) if m else None
            elif "scene_score" in line:
                m = re.search(r"scene_score=([0-9.]+)", line)
                cur_s = float(m.group(1)) if m else None
                if cur_t is not None and cur_s is not None:
                    (hard if cur_s >= thresh else soft).append({"t": cur_t, "score": cur_s})
    # dedupe: keep strongest within 0.15s
    return _dedupe(hard, 0.15), _dedupe(soft, 0.15, keep="first")


def _dedupe(items, gap, keep="max"):
    items = sorted(items, key=lambda d: d["t"])
    out = []
    for it in items:
        if out and it["t"] - out[-1]["t"] < gap:
            if keep == "max" and it["score"] > out[-1]["score"]:
                out[-1] = it
            continue
        out.append(it)
    return out


def _detect_interval_filter(path: Path, vf: str = None, af: str = None, pat=()):
    args = ["-i", str(path)]
    if vf:
        args += ["-vf", vf]
    if af:
        args += ["-af", af]
    args += ["-f", "null", "-"]
    r = sh(args)
    out = {}
    for name, rx in pat:
        out[name] = [float(x) for x in re.findall(rx, r.stderr)]
    return out


def detect_blacks(path: Path):
    d = _detect_interval_filter(path, vf="blackdetect=d=0.15:pix_th=0.10",
                                pat=[("start", r"black_start:([0-9.]+)"),
                                     ("end", r"black_end:([0-9.]+)")])
    return [{"t0": a, "t1": b} for a, b in zip(d.get("start", []), d.get("end", []))]


def detect_freezes(path: Path):
    d = _detect_interval_filter(path, vf="freezedetect=n=-60dB:d=0.5",
                                pat=[("start", r"freeze_start:\s*([0-9.]+)"),
                                     ("end", r"freeze_end:\s*([0-9.]+)")])
    return [{"t0": a, "t1": b} for a, b in zip(d.get("start", []), d.get("end", []))]


def detect_silences(path: Path, has_audio: bool):
    if not has_audio:
        return []
    d = _detect_interval_filter(path, af="silencedetect=noise=-35dB:d=0.30",
                                pat=[("start", r"silence_start:\s*([0-9.]+)"),
                                     ("end", r"silence_end:\s*([0-9.]+)")])
    return [{"t0": a, "t1": b} for a, b in zip(d.get("start", []), d.get("end", []))]


# ----------------------------------------------------------------------------
# layer 2 — numeric motion metrics (streaming, block-affine: pan + zoom + rotate)
# ----------------------------------------------------------------------------

def _hann(h, w):
    return np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)


def _highpass(img: np.ndarray, r: int = 2) -> np.ndarray:
    """img - boxblur(img, r) via integral image. Kills flat areas so block
    matching is driven by edges/texture instead of static background."""
    h, w = img.shape
    I = np.cumsum(np.cumsum(img, axis=0), axis=1)
    I = np.pad(I, ((1, 0), (1, 0)))
    ys = np.arange(h)
    xs = np.arange(w)
    y0 = np.clip(ys - r, 0, h - 1); y1 = np.clip(ys + r + 1, 0, h)
    x0 = np.clip(xs - r, 0, w - 1); x1 = np.clip(xs + r + 1, 0, w)
    A = I[np.ix_(y1, x1)]; B = I[np.ix_(y0, x1)]
    C = I[np.ix_(y1, x0)]; D = I[np.ix_(y0, x0)]
    area = ((y1 - y0)[:, None] * (x1 - x0)[None, :]).astype(np.float32)
    return img - (A - B - C + D) / area


def _windows(img, block, step):
    """Batch of (block,block) windows on a grid. Returns (N,block,block), ys, xs."""
    sw = np.lib.stride_tricks.sliding_window_view(np.ascontiguousarray(img), (block, block))
    ny = (sw.shape[0] - 1) // step + 1
    nx = (sw.shape[1] - 1) // step + 1
    ys = np.minimum(np.arange(ny) * step, sw.shape[0] - 1)
    xs = np.minimum(np.arange(nx) * step, sw.shape[1] - 1)
    return sw[np.ix_(ys, xs)].reshape(-1, block, block).astype(np.float32), ys, xs


def _peak_subpix(r):
    """Sub-pixel peak of a batch of correlation surfaces r:(N,H,W) -> dy,dx,peak."""
    N, H, W = r.shape
    flat = r.reshape(N, -1)
    idx = flat.argmax(1)
    cy = (idx // W).astype(np.int64)
    cx = (idx % W).astype(np.int64)
    rp = np.concatenate([r[:, :, -1:], r, r[:, :, :1]], axis=2)
    rp = np.concatenate([rp[:, -1:, :], rp, rp[:, :1, :]], axis=1)
    iy = cy + 1
    ix = cx + 1
    ar = np.arange(N)
    c = rp[ar, iy, ix]
    left, right = rp[ar, iy, ix - 1], rp[ar, iy, ix + 1]
    up, down = rp[ar, iy - 1, ix], rp[ar, iy + 1, ix]
    denx = left - 2 * c + right
    deny = up - 2 * c + down
    dxs = np.where(np.abs(denx) > 1e-9, 0.5 * (left - right) / np.where(denx == 0, 1, denx), 0.0)
    dys = np.where(np.abs(deny) > 1e-9, 0.5 * (up - down) / np.where(deny == 0, 1, deny), 0.0)
    dx = cx + np.clip(dxs, -0.5, 0.5)
    dy = cy + np.clip(dys, -0.5, 0.5)
    dx = np.where(dx > W / 2, dx - W, dx)
    dy = np.where(dy > H / 2, dy - H, dy)
    return dy.astype(np.float64), dx.astype(np.float64), c.astype(np.float64)


def block_affine(f, prev, block, step, min_var):
    """Per-frame motion: translation (px) + scale (fraction/frame) + rotation (rad/frame).
    Model: dx = tx + s*px + r*py ; dy = ty + s*py - r*px   (px,py relative to centre).
    Robust LSQ with one IRLS reweighting round. Returns dict or None."""
    H, W = f.shape
    if H < block or W < block:
        return None
    wf, ys, xs = _windows(f, block, step)
    wp, _, _ = _windows(prev, block, step)
    var = wf.reshape(len(wf), -1).var(1)
    thr = max(min_var, 0.25 * float(np.median(var)))
    keep = var > thr
    if keep.sum() < 6:
        return None
    wf, wp = wf[keep], wp[keep]
    # rebuild grids after masking
    # window grid positions must reproduce the original flatten order (ny, nx) row-major
    ny_ = (np.lib.stride_tricks.sliding_window_view(np.zeros((H, W), np.uint8), (block, block)).shape[0] - 1) // step + 1
    nx_ = (np.lib.stride_tricks.sliding_window_view(np.zeros((H, W), np.uint8), (block, block)).shape[1] - 1) // step + 1
    gx, gy = np.meshgrid(np.minimum(np.arange(nx_) * step, W - block),
                         np.minimum(np.arange(ny_) * step, H - block))
    gx = gx.reshape(-1)[keep]
    gy = gy.reshape(-1)[keep]
    wvar = var[keep]
    A = np.fft.rfft2(wf - wf.mean((1, 2), keepdims=True), axes=(-2, -1))
    B = np.fft.rfft2(wp - wp.mean((1, 2), keepdims=True), axes=(-2, -1))
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-9
    rr = np.fft.irfft2(R, s=(block, block), axes=(-2, -1))
    dy, dx, peak = _peak_subpix(rr)
    # peak-ratio test: a long straight edge correlates equally well anywhere along
    # itself (aperture problem) -> its correlation surface has a ridge, not a peak.
    N = rr.shape[0]
    gy_, gx_ = np.mgrid[0:block, 0:block]
    m = (np.abs(gy_[None] - (dy % block)[:, None, None]) <= 3) & \
        (np.abs(gx_[None] - (dx % block)[:, None, None]) <= 3)
    side = np.max(np.where(m, -1e9, rr), axis=(1, 2))
    ratio = peak / np.maximum(side, 1e-6)
    lim = 0.38 * block   # beyond this a block match can wrap around (aliasing)
    good = (peak > 0.05) & (ratio > 1.35) & (np.abs(dx) < lim) & (np.abs(dy) < lim)
    if good.sum() < 6:
        return None
    dx, dy = dx[good], dy[good]
    gx, gy = gx[good], gy[good]
    wvar = wvar[good]
    if len(dx) < 10:
        return None
    pkw = np.sqrt(np.maximum(wvar, 1e-3))
    pkw = pkw / pkw.mean()
    px = gx + block / 2.0 - W / 2.0
    py = gy + block / 2.0 - H / 2.0
    n = len(dx)
    M = np.zeros((2 * n, 4), np.float64)
    M[:n, 0] = 1.0; M[:n, 2] = px; M[:n, 3] = py
    M[n:, 1] = 1.0; M[n:, 2] = py; M[n:, 3] = -px
    b = np.concatenate([dx, dy])
    w = np.tile(pkw, 2)
    sol = None
    for _ in range(3):
        Mw = M * w[:, None]
        sol, *_ = np.linalg.lstsq(Mw, b * w, rcond=None)
        res = b - M @ sol
        sig = max(1e-3, 1.4826 * float(np.median(np.abs(res - np.median(res)))))
        w = 1.0 / (1.0 + (res / (2.5 * sig)) ** 2)
    tx, ty, sfrac, rrot = [float(v) for v in sol]
    resid = float(np.sqrt(np.mean((b - M @ sol) ** 2)))
    return {"tx": tx, "ty": ty, "scale": sfrac, "rot": -rrot, "resid": resid,
            "blocks": int(n), "peak": float(np.mean(peak[good])),
            "ratio": float(np.mean(ratio[good]))}


def _global_shift(f, prev, win, ups=20):
    """Accurate whole-frame translation with DFT-upsampled sub-pixel refinement
    (Guizar-Sicairos style). Returns (dx, dy, peak) in analysis-pixels."""
    A = np.fft.rfft2((f - f.mean()) * win)
    B = np.fft.rfft2((prev - prev.mean()) * win)
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-9
    r = np.fft.irfft2(R, s=f.shape)
    iy, ix = np.unravel_index(int(np.argmax(r)), r.shape)
    peak = float(r[iy, ix])
    if peak < 0.03:
        return 0.0, 0.0, peak, False
    H, W = r.shape
    if iy > H // 2: iy -= H
    if ix > W // 2: ix -= W
    # evaluate the exact DFT of r on a fine grid around the integer peak
    fr = np.arange(-ups // 2, ups // 2 + 1) / float(ups)
    ys = iy + fr
    xs = ix + fr
    m = np.arange(H); n = np.arange(W)
    Ey = np.exp(-2j * np.pi * np.outer(ys, m) / H)
    Ex = np.exp(-2j * np.pi * np.outer(xs, n) / W)
    U = Ey @ r.astype(np.complex64) @ Ex.T
    iy2, ix2 = np.unravel_index(int(np.argmax(np.abs(U))), U.shape)
    dy = float(ys[iy2]); dx = float(xs[ix2])
    return dx, dy, peak, True


def motion_scan(path: Path, hz: float, work: Path, width=320, block=32, step=16,
                min_var=6.0, progress_every=4000, bucket=0.5):
    work = Path(work)
    """Full-decode streaming scan; keeps scalars only (low RAM)."""
    info = probe(path)
    W0, H0 = info["width"], info["height"]
    w = width
    h = int(round(w * H0 / W0 / 2.0)) * 2
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-i", str(path),
           "-vf", f"fps={hz},scale={w}:{h},format=gray", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n_bytes = w * h
    keys = ("t", "energy", "dx", "dy", "scale", "rot", "peak", "resid")
    acc = {k: [] for k in keys}
    per = max(1, int(round(bucket * hz))) if bucket else 0
    g_t, g_x, g_y, g_ok = [], [], [], []
    win_g = _hann(h, w)
    prev = None
    prev_b = None
    i = 0
    while True:
        buf = p.stdout.read(n_bytes)
        if not buf or len(buf) < n_bytes:
            break
        f = np.frombuffer(buf, dtype=np.uint8).reshape(h, w).astype(np.float32)
        if prev is None:
            acc["t"].append(0.0); acc["energy"].append(0.0)
            for k in ("dx", "dy", "scale", "rot", "resid"): acc[k].append(0.0)
            acc["peak"].append(0.0)
        else:
            energy = float(np.abs(f - prev).mean())
            res = {"tx": 0.0, "ty": 0.0, "scale": 0.0, "rot": 0.0, "resid": 0.0, "peak": 0.0}
            if energy > 0.25:
                hf, hp_ = _highpass(f), _highpass(prev)
                est = block_affine(hf, hp_, block, step, min_var)
                if est:
                    res = est
            acc["t"].append(i / hz); acc["energy"].append(energy)
            acc["dx"].append(res["tx"]); acc["dy"].append(res["ty"])
            acc["scale"].append(res["scale"]); acc["rot"].append(res["rot"])
            acc["peak"].append(res.get("peak", 0.0)); acc["resid"].append(res.get("resid", 0.0))
        if per and i > 0 and i % per == 0 and prev_b is not None:
            # whole-frame estimate: no block-size limit, sub-pixel accurate.
            # A cut inside the bucket collapses the correlation peak -> rejected.
            dxg, dyg, pk, ok = _global_shift(f, prev_b, win_g)
            if ok and pk >= 0.10:
                g_t.append((i - per) / hz)
                g_x.append(dxg / w * 100.0)
                g_y.append(dyg / h * 100.0)
                g_ok.append(True)
            prev_b = None
        if per and i % per == 0:
            prev_b = f.copy()
        prev = f
        i += 1
        if progress_every and i % progress_every == 0:
            print(f"    ... motion scan {i} frames ({tc(i / hz)})", flush=True)
    p.stdout.close(); p.wait()
    out = {k: np.array(v) for k, v in acc.items()}
    out.update({"hz": hz, "w": w, "h": h, "block": block, "step": step, "bucket": bucket,
                "g_t": np.array(g_t), "g_x": np.array(g_x), "g_y": np.array(g_y)})
    return out


def summarize_metrics(m: dict, bucket=0.5):
    """Per-bucket numbers + labels. Pan in %width/s, zoom %/s, rotation deg/s."""
    hz, w, h = m["hz"], m["w"], m["h"]
    n = len(m["t"])
    per = max(1, int(round(bucket * hz)))
    rows = []
    for b0 in range(0, n, per):
        sl = slice(b0, min(b0 + per, n))
        dur = (sl.stop - sl.start) / hz
        if dur <= 0:
            continue
        e = float(m["energy"][sl].mean())
        tx_pct = float(m["dx"][sl].sum() / w * 100.0) / dur
        ty_pct = float(m["dy"][sl].sum() / h * 100.0) / dur
        s_mean = float(np.clip(m["scale"][sl], -0.2, 0.2).mean())
        sc = ((1.0 + s_mean) ** hz - 1.0) * 100.0
        rot = float(np.degrees(m["rot"][sl].mean() * hz))  # rad/frame -> deg/s
        labels = []
        if e < 0.25:
            labels.append("static")
        else:
            if tx_pct > 0.8: labels.append("content_moves_right")
            elif tx_pct < -0.8: labels.append("content_moves_left")
            if ty_pct > 0.8: labels.append("content_moves_down")
            elif ty_pct < -0.8: labels.append("content_moves_up")
            if sc > 1.5: labels.append("zoom_in")
            elif sc < -1.5: labels.append("zoom_out")
            if abs(rot) > 1.5: labels.append("rotate")
            if e > 4.0 and len(labels) == 0: labels.append("complex_burst")
            elif e > 1.5 and not labels: labels.append("motion")
        # per-sample displacement (px at analysis width): the real accuracy driver
        disp_local = max(abs(float(np.median(m["dx"][sl]))), abs(float(np.median(m["dy"][sl]))),
                         abs(float(np.median(m["scale"][sl]))) * w / 2.0)
        global_x = global_y = None
        if len(m.get("g_t", [])):
            j = int(np.argmin(np.abs(m["g_t"] - float(m["t"][sl.start]))))
            if abs(float(m["g_t"][j]) - float(m["t"][sl.start])) <= 1e-6:
                global_x = float(m["g_x"][j]) / dur
                global_y = float(m["g_y"][j]) / dur
        conf = "high" if disp_local >= 0.8 else ("subtle" if disp_local >= 0.3 else "low")
        if global_x is not None:
            tx_pct, ty_pct = global_x, global_y
            conf = "high"
            labels = [l for l in labels if l not in ("content_moves_right", "content_moves_left",
                                                     "content_moves_up", "content_moves_down")]
            if tx_pct > 0.8: labels.append("content_moves_right")
            elif tx_pct < -0.8: labels.append("content_moves_left")
            if ty_pct > 0.8: labels.append("content_moves_down")
            elif ty_pct < -0.8: labels.append("content_moves_up")
            if not labels: labels = ["motion"]
        elif conf != "high" and e > 0.25:
            labels = [l for l in labels if l in ("zoom_in", "zoom_out", "rotate")]
            labels = ["subtle_motion"] + labels
        rows.append({
            "confidence": conf,
            "pan_source": "global" if global_x is not None else "local",
            "t0": round(float(m["t"][sl.start]), 3),
            "t1": round(float(m["t"][sl.stop - 1]) + 1.0 / hz, 3),
            "energy": round(e, 3),
            "shift_x_pct_per_s": round(tx_pct, 2),
            "shift_y_pct_per_s": round(ty_pct, 2),
            "zoom_pct_per_s": round(sc, 2),
            "rot_deg_per_s": round(rot, 2),
            "resid": round(float(m["resid"][sl].mean()), 3),
            "labels": labels,
        })
    return rows


# ----------------------------------------------------------------------------
# layer 3 — review artifacts per event
# ----------------------------------------------------------------------------

def event_clip(path: Path, t0: float, dur: float, out: Path, has_audio: bool, width=640):
    args = ["-ss", f"{max(0.0, t0):.3f}", "-i", str(path), "-t", f"{dur:.3f}",
            "-vf", f"scale={width}:-2", "-c:v", "libx264", "-crf", "30",
            "-preset", "veryfast", "-pix_fmt", "yuv420p"]
    args += ["-c:a", "aac", "-b:a", "64k"] if has_audio else ["-an"]
    args += ["-y", str(out)]
    sh(args)


def event_sheet(path: Path, t0: float, dur: float, fps: float, out: Path, tile_w=320, title=""):
    info = probe(path)
    W, H = info["width"], info["height"]
    w = tile_w
    h = int(round(w * H / W / 2.0)) * 2
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-ss", f"{max(0.0, t0):.3f}",
           "-i", str(path), "-t", f"{dur:.3f}",
           "-vf", f"fps={fps},scale={w}:{h},format=rgb24", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    frames = []
    n_bytes = w * h * 3
    while True:
        buf = p.stdout.read(n_bytes)
        if not buf or len(buf) < n_bytes:
            break
        frames.append(np.frombuffer(buf, dtype=np.uint8).reshape(h, w, 3).copy())
    p.stdout.close()
    p.wait()
    if not frames:
        return 0
    cols = 8
    rows = math.ceil(len(frames) / cols)
    lab = 18
    canvas = Image.new("RGB", (cols * w, rows * (h + lab) + 26), (12, 12, 14))
    d = ImageDraw.Draw(canvas)
    d.text((6, 5), title, fill=(235, 235, 235))
    for i, arr in enumerate(frames):
        c, r = i % cols, i // cols
        x, y = c * w, 26 + r * (h + lab)
        canvas.paste(Image.fromarray(arr), (x, y))
        d.text((x + 4, y + h + 4), f"{tc(t0 + i / fps)}", fill=(150, 200, 255))
    canvas.save(out, quality=84)
    return len(frames)


# ----------------------------------------------------------------------------
# layer 4 — base filmstrips + dossier + index
# ----------------------------------------------------------------------------

def base_filmstrips(path: Path, fps: float, outdir: Path, tile_w=260, cols=10, rows=6, start=0.0, end=None):
    info = probe(path)
    W, H = info["width"], info["height"]
    w = tile_w
    h = int(round(w * H / W / 2.0)) * 2
    dur = (end - start) if end else info["duration"] - start
    per_page = cols * rows / fps
    pages = max(1, math.ceil(dur / per_page))
    outdir.mkdir(parents=True, exist_ok=True)
    lab = 14
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-ss", f"{start:.3f}", "-i", str(path), "-t", f"{dur:.3f}",
           "-vf", f"fps={fps},scale={w}:{h},format=rgb24", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n_bytes = w * h * 3
    page, idx, made = None, 0, 0
    t = start
    page_no = 1
    while True:
        buf = p.stdout.read(n_bytes)
        if not buf or len(buf) < n_bytes:
            break
        arr = np.frombuffer(buf, dtype=np.uint8).reshape(h, w, 3).copy()
        if page is None:
            page = Image.new("RGB", (cols * w, rows * (h + lab) + 18), (12, 12, 14))
            pd = ImageDraw.Draw(page)
            pd.text((5, 4), f"{path.stem}  {tc(t)} -> page {page_no}/{pages}  @{fps}fps", fill=(235, 235, 235))
        c, r = idx % cols, idx // cols
        x, y = c * w, 18 + r * (h + lab)
        page.paste(Image.fromarray(arr), (x, y))
        ImageDraw.Draw(page).text((x + 3, y + h + 2), tc(t), fill=(150, 200, 255))
        idx += 1
        t += 1.0 / fps
        if idx >= cols * rows:
            page.save(outdir / f"p{page_no:02d}_of_{pages:02d}.jpg", quality=82)
            made += 1
            page, page_no, idx = None, page_no + 1, 0   # BUGFIX: idx لازم ينصفّر مع كل صفحة وإلا كل فريم بيصير صفحة لحاله
    if page is not None and idx > 0:
        page.save(outdir / f"p{page_no:02d}_of_{pages:02d}.jpg", quality=82)
        made += 1
    p.stdout.close()
    p.wait()
    return made


def build_events(cuts, blacks, freezes, silences, summary, max_events, pre, post):
    evs = []
    for c in cuts:
        if c["t"] < 0.15:      # opening frame of the file, not a cut
            continue
        cls = "hard_cut" if c["score"] >= 0.35 else "soft_cut"
        evs.append({"type": cls, "t": c["t"], "score": c["score"],
                    "t0": max(0.0, c["t"] - pre), "t1": c["t"] + post})
    for b in blacks:
        evs.append({"type": "black", "t": b["t0"], "score": 0.0,
                    "t0": max(0.0, b["t0"] - 0.3), "t1": b["t1"] + 0.3})
    # motion bursts: buckets with high energy that are not inside a cut window
    if summary:
        energies = np.array([r["energy"] for r in summary])
        med = float(np.median(energies)) if len(energies) else 0.0
        thr = max(6.0, med * 3.0 + 2.0)
        run = []
        for r in summary:
            if r["energy"] >= thr:
                run.append(r)
            else:
                if len(run) >= 2:  # at least 1.0s of sustained motion
                    t0, t1 = run[0]["t0"], run[-1]["t1"]
                    if not any(e["t0"] - 0.2 <= t0 <= e["t1"] + 0.2 or e["t0"] - 0.2 <= t1 <= e["t1"] + 0.2
                               for e in evs):
                        evs.append({"type": "motion_burst", "t": t0, "score": round(float(np.mean([x["energy"] for x in run])), 2),
                                    "t0": max(0.0, t0 - 0.3), "t1": t1 + 0.3})
                run = []
        if len(run) >= 2:
            t0, t1 = run[0]["t0"], run[-1]["t1"]
            evs.append({"type": "motion_burst", "t": t0, "score": round(float(np.mean([x["energy"] for x in run])), 2),
                        "t0": max(0.0, t0 - 0.3), "t1": t1 + 0.3})
    evs.sort(key=lambda e: e["t0"])
    # dedupe heavy overlaps (keep first = earlier)
    kept = []
    for e in evs:
        if kept and e["t0"] < kept[-1]["t1"] - 0.4 and e["type"] not in ("hard_cut", "soft_cut"):
            continue
        kept.append(e)
    if max_events and len(kept) > max_events:
        # priority: cuts first, then bursts, then blacks
        order = {"hard_cut": 0, "soft_cut": 1, "motion_burst": 2, "black": 3}
        kept = sorted(sorted(kept, key=lambda e: (order.get(e["type"], 3), -e.get("score", 0)))[:max_events],
                      key=lambda e: e["t0"])
    return kept


def bucket_lookup(summary, t):
    for r in summary:
        if r["t0"] <= t < r["t1"]:
            return r
    return None


def write_index(evdir_rel: str, events, summary, out: Path, video_name: str):
    lines = [f"# فهرس الحركة — {video_name}", "",
             "> مقطّعات المراجعة هون هي «الفريم ورا فريم» للحركة: كل حدث إله clip + شريط فريمات.",
             "> القياسات من فك الترميز الكامل (fps متغيّر) — دقيقة، والـclip للعرض السريع.", "",
             "| # | الوقت | النوع | تفاصيل | الحركة المقاسة (وقت الحدث) | ملفات المراجعة |",
             "|---|---|---|---|---|---|"]
    for i, e in enumerate(events, 1):
        b = bucket_lookup(summary, e["t"]) or {}
        lab = "، ".join(b.get("labels", [])) or "-"
        mov = (f"{lab} · طاقة {b.get('energy','-')} · "
               f"إزاحة x {b.get('shift_x_pct_per_s','-')}%/ث · y {b.get('shift_y_pct_per_s','-')}%/ث · "
               f"زووم {b.get('zoom_pct_per_s','-')}%/ث · دوران {b.get('rot_deg_per_s','-')}°/ث")
        det = (f"{'قطعة حادة' if e['type']=='hard_cut' else 'قطعة ناعمة/تغيير'} (score {e.get('score',0):.2f})" if e["type"] in ("hard_cut", "soft_cut") else
               "أسود" if e["type"] == "black" else
               f"عنقود حركة (طاقة {e.get('score')})")
        stem = e["file_stem"]
        lines.append(f"| {i} | {tc(e['t'])} | {e['type']} | {det} | {mov} | "
                     f"[clip]({evdir_rel}/{stem}.mp4) · [strip]({evdir_rel}/{stem}.jpg) |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------
# orchestration
# ----------------------------------------------------------------------------

def analyze(video: Path, outdir: Path, video_id: str, args) -> dict:
    t_start = time.time()
    outdir.mkdir(parents=True, exist_ok=True)
    motion_dir = outdir / "motion"
    evdir = motion_dir / "events"
    evdir.mkdir(parents=True, exist_ok=True)
    work = Path(args.work) if args.work else (outdir / ".work")
    work.mkdir(parents=True, exist_ok=True)

    info = probe(video)
    print(f"[i] {video.name}: {info['width']}x{info['height']} {info['duration']:.2f}s "
          f"{info['fps']:.3f}fps audio={info['has_audio']}", flush=True)

    t_from, t_to = args.start, args.end
    # FIXED 2026-10-14: كنا نقطّع بس إذا البداية > 0؛ هيك جزء يبلش من 0 مع --end
    # كان يحلّل الفيديو كامل (350+ ث بدل ~20 ث). هلأ منقطّع إذا في بداية > 0 أو نهاية < المدة.
    if t_from > 0 or (t_to is not None and t_to < info["duration"] - 0.5):
        # analyze a slice: cut a working copy (stream copy, no re-encode)
        sliced = work / f"slice_{int(t_from)}_{int(t_to or info['duration'])}.mp4"
        if not sliced.exists():
            dur = (t_to or info["duration"]) - t_from
            sh(["-ss", f"{t_from:.3f}", "-i", str(video), "-t", f"{dur:.3f}",
                "-c", "copy", "-y", str(sliced)])
        src = sliced
    else:
        src = video

    print("[1/5] كشف الأحداث (cuts / black / freeze / silence) ...", flush=True)
    cuts, soft = detect_cuts(src, args.cut_thresh, work, args.soft_thresh)
    blacks = detect_blacks(src)
    freezes = detect_freezes(src)
    silences = detect_silences(src, info["has_audio"])
    offset = float(t_from)
    for c in cuts:
        c["t"] += offset
    for c in soft:
        c["t"] += offset
    for b in blacks:
        b["t0"] += offset
        b["t1"] += offset
    for b in freezes:
        b["t0"] += offset
        b["t1"] += offset
    for b in silences:
        b["t0"] += offset
        b["t1"] += offset
    print(f"    cuts={len(cuts)} soft={len(soft)} black={len(blacks)} "
          f"freeze={len(freezes)} silence={len(silences)}", flush=True)

    print("[2/5] قياس الحركة رقميًا ...", flush=True)
    m = motion_scan(src, args.motion_hz, work, width=args.motion_width,
                    block=args.block, step=args.step, min_var=args.min_var)
    if offset:
        m["t"] = m["t"] + offset
    summary = summarize_metrics(m, bucket=args.bucket)
    np.savez_compressed(motion_dir / "metrics_raw.npz",
                        t=m["t"], energy=m["energy"], dx=m["dx"], dy=m["dy"],
                        scale=m["scale"], rot=m["rot"], peak=m["peak"])
    with open(motion_dir / "metrics_0.5s.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False)
    print(f"    buckets={len(summary)} → motion/metrics_0.5s.json", flush=True)

    print("[3/5] بناء قائمة الأحداث + مقاطع المراجعة ...", flush=True)
    events = build_events(cuts, blacks, freezes, silences, summary,
                          args.max_events, args.event_pre, args.event_post)
    made = 0
    for i, e in enumerate(events, 1):
        stem = f"e{i:03d}_{int(e['t']//60):02d}m{int(e['t']%60):02d}s_{e['type']}"
        e["file_stem"] = stem
        dur = max(0.6, min(e["t1"] - e["t0"], args.event_max)) if e["t1"] > e["t0"] else 1.2
        t0 = max(0.0, e["t0"])
        rel_t0 = t0 - offset
        if not args.no_clips:
            event_clip(src, rel_t0, dur, evdir / f"{stem}.mp4", info["has_audio"])
        if not args.no_sheets:
            n = event_sheet(src, rel_t0, dur, args.event_fps, evdir / f"{stem}.jpg",
                            title=f"{stem}  {tc(t0)}  @{args.event_fps}fps")
            e["sheet_frames"] = n
        made += 1
        if made % 25 == 0:
            print(f"    ... {made}/{len(events)}", flush=True)
    print(f"    events={len(events)} (clips+sheets في motion/events/)", flush=True)

    print(f"[4/5] فيلمستريب أساسي @{args.base_fps}fps ...", flush=True)
    pages = 0
    if not args.no_strips:
        pages = base_filmstrips(video, args.base_fps, outdir / "filmstrip",
                                start=float(t_from), end=(float(t_to) if args.end else None))
        print(f"    pages={pages}", flush=True)

    print("[5/5] كتابة dossier + الفهرس ...", flush=True)
    dossier = {
        "video_id": video_id,
        "source": str(video),
        "probe": info,
        "params": {
            "cut_thresh": args.cut_thresh, "soft_thresh": args.soft_thresh,
            "motion_hz": args.motion_hz, "bucket": args.bucket,
            "event_fps": args.event_fps, "base_fps": args.base_fps,
            "event_window": [args.event_pre, args.event_post],
        },
        "counts": {"hard_cuts": len(cuts), "soft_changes": len(soft),
                   "blacks": len(blacks), "freezes": len(freezes), "silences": len(silences),
                   "events": len(events), "strip_pages": pages},
        "cuts": cuts,
        "soft_changes": soft,
        "blacks": blacks,
        "freezes": freezes,
        "silences": silences,
        "motion_summary": summary,
        "events": events,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    with open(outdir / "dossier.json", "w", encoding="utf-8") as f:
        json.dump(dossier, f, ensure_ascii=False, indent=1)
    write_index("events", events, summary, motion_dir / "MOTION_INDEX.md", video.name)
    print(f"[✓] خلص بـ {dossier['elapsed_s']}s → {outdir}", flush=True)
    return dossier


# ----------------------------------------------------------------------------
# self-test (synthetic video with known ground truth)
# ----------------------------------------------------------------------------

def _synth_video(out: Path, h=360, w=640, fps=30, dur=24.0):
    """Video with KNOWN cuts/motions, photographic-like texture (multi-octave noise).
    Ground truth returned so the selftest can grade every layer."""
    n = int(dur * fps)

    def texture(seed, octaves=((4, 40), (8, 22), (20, 12), (1, 9))):
        rng = np.random.default_rng(seed)
        t = np.zeros((h + 200, w + 200), np.float32)
        for cell, amp in octaves:
            small = rng.random((h // cell + 3, w // cell + 3)).astype(np.float32) - 0.5
            big = np.asarray(Image.fromarray((small * 127 + 128).astype(np.uint8)).resize(
                (w + 200, h + 200), Image.BICUBIC), np.float32) - 128.0
            t += big * (amp / 60.0)
        t = 128 + t * 60.0
        return t

    p = subprocess.Popen([FFMPEG, "-hide_banner", "-nostdin", "-y",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                          "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    texA = texture(11)
    texB = texture(29)
    ox, oy = 100, 100  # keep sampling away from borders

    def sample(tex, X, Y, tint):
        Xi = np.clip(X + ox, 0, tex.shape[1] - 1).astype(np.int32)
        Yi = np.clip(Y + oy, 0, tex.shape[0] - 1).astype(np.int32)
        g = tex[Yi, Xi]
        f = np.dstack([g * tint[0], g * tint[1], g * tint[2]])
        return np.clip(f, 0, 255)

    for i in range(n):
        t = i / fps
        if t < 3.0:                       # 0-3  PAN right 200px/s (content moves right)
            dx = -200.0 * t
            f = sample(texA, xx + dx, yy, (1.0, 0.94, 0.90))
        elif t < 6.0:                     # 3-6  ZOOM IN +4%/s  (cut at 3.0)
            sc = 1.0 / (1.0 + 0.04 * (t - 3.0))
            f = sample(texB, (xx - cx) * sc + cx, (yy - cy) * sc + cy, (0.86, 0.92, 1.0))
        elif t < 6.5:                     # 6.0 hard CUT
            f = sample(texA, xx, yy, (0.80, 1.0, 0.85))
        elif t < 8.0:                     # 6.5 fade to black -> black
            k = max(0.0, 1.0 - (t - 6.5) / 1.0) if t < 7.5 else 0.0
            f = sample(texA, xx, yy, (0.80, 1.0, 0.85)) * k
        elif t < 12.0:                    # 8.0 CUT : PAN left 150px/s
            dx = 150.0 * (t - 8.0)
            f = sample(texB, xx + dx, yy + 30.0 * (t - 8.0), (1.0, 0.95, 0.80))
        elif t < 20.0:                    # 12.0 CUT : ROTATE +6deg/s and ZOOM OUT 3%/s
            ang = math.radians(6.0 * (t - 12.0))
            sc = 1.0 + 0.03 * (t - 12.0)
            ux, uy = xx - cx, yy - cy
            X = (ux * math.cos(-ang) - uy * math.sin(-ang)) * sc + cx
            Y = (ux * math.sin(-ang) + uy * math.cos(-ang)) * sc + cy
            f = sample(texA, X, Y, (0.95, 0.88, 1.0))
        else:                             # 20.0 CUT : static
            f = sample(texB, xx, yy, (0.9, 0.9, 0.92))
        p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()

    wav = out.with_suffix(".wav")
    sr = 22050
    with wave.open(str(wav), "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        buf = bytearray()
        for i in range(int(dur * sr)):
            tt = i / sr
            amp = 0 if 6.5 <= tt < 8.0 else 0.25
            buf += int(amp * 32767 * math.sin(2 * math.pi * 220 * tt)).to_bytes(2, "little", signed=True)
        wf.writeframes(bytes(buf))
    final = out.with_name(out.stem + "_av.mp4")
    sh(["-i", str(out), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
        "-shortest", "-y", str(final)])
    os.unlink(wav)
    gt = {"cuts": [3.0, 6.0, 8.0, 12.0, 20.0],
          "black": (7.5, 8.0), "silence": (6.5, 8.0),
          "pan_right": (0.0, 3.0, +25.0),    # %width/s  (200px/s / 640 * 100 /(320/640 scale) -> same %)
          "zoom_in": (3.0, 6.0, +4.0),
          "pan_left_up": (8.0, 12.0, -18.75),
          "zoom_out_rotate": (12.0, 20.0, -3.0, 6.0),
          "static": (20.0, 24.0, 0.0)}
    return final, gt


def selftest(args) -> int:
    outroot = Path(args.work or "/home/user/build/motion_test") / "selftest"
    if outroot.exists():
        shutil.rmtree(outroot)
    outroot.mkdir(parents=True, exist_ok=True)
    raw = outroot / "synth.mp4"
    print("[selftest] generating synthetic video with known ground truth ...", flush=True)
    video, gt = _synth_video(raw)
    print(f"[selftest] {video}", flush=True)
    ns = argparse.Namespace(**vars(args))
    ns.start, ns.end = 0, None
    ns.max_events = 200
    d = analyze(video, outroot / "analysis", "selftest", ns)

    ok = True
    print("\n[selftest] results vs ground truth")
    got = sorted([c["t"] for c in d["cuts"]])
    for want in gt["cuts"]:
        near = [g for g in got if abs(g - want) <= 0.12]
        print(f"  cut@{want:.2f}s  -> {'OK' if near else 'MISS'} (got {[round(g,3) for g in got]})")
        ok &= bool(near)
    bl = [b for b in d["blacks"] if abs(b["t0"] - gt["black"][0]) < 0.25]
    print(f"  black {gt['black']} -> {'OK' if bl else 'MISS'}")
    ok &= bool(bl)
    sil = [s for s in d["silences"] if abs(s["t0"] - gt["silence"][0]) < 0.35]
    print(f"  silence {gt['silence']} -> {'OK' if sil else 'MISS'}")
    ok &= bool(sil)

    def seg(t0, t1):
        rows = [r for r in d["motion_summary"] if r["t0"] >= t0 and r["t1"] <= t1]
        if not rows:
            return {}
        return {
            "energy": round(float(np.mean([r["energy"] for r in rows])), 2),
            "x": round(float(np.mean([r["shift_x_pct_per_s"] for r in rows])), 2),
            "y": round(float(np.mean([r["shift_y_pct_per_s"] for r in rows])), 2),
            "zoom": round(float(np.mean([r["zoom_pct_per_s"] for r in rows])), 2),
            "rot": round(float(np.mean([r["rot_deg_per_s"] for r in rows])), 2),
        }

    def near(v, want, tol):
        return abs(v - want) <= tol

    checks = [
        ("pan right 0-3s: x≈+25%/s ±25%", seg(0.5, 2.9),
         lambda s: near(s.get("x", 0), 25.0, 6.5)),
        ("zoom in 3-6s: zoom≈+4%/s ±50%", seg(3.5, 5.9),
         lambda s: near(s.get("zoom", 0), 4.0, 2.0)),
        ("pan left+up 8-12s: x≈-18.8%/s, y≈-8.3%/s", seg(8.5, 11.9),
         lambda s: near(s.get("x", 0), -18.75, 5.0) and near(s.get("y", 0), -8.33, 2.5)),
        ("zoom out+rotate 12-20s: zoom≈-3, rot≈+6°/s", seg(12.5, 19.9),
         lambda s: near(s.get("zoom", 0), -3.0, 1.8) and near(s.get("rot", 0), 6.0, 3.0)),
        ("static 20-24s: energy<0.6", seg(20.5, 23.9), lambda s: s.get("energy", 99) < 0.6),
        ("no false motion on static (|x|<1, |zoom|<1)", seg(20.5, 23.9),
         lambda s: abs(s.get("x", 0)) < 1.0 and abs(s.get("zoom", 0)) < 1.0),
    ]
    print()
    for name, s, fn in checks:
        good = fn(s)
        ok &= good
        print(f"  {name:<52} {'OK' if good else 'FAIL'}   {s}")

    idx = (outroot / "analysis" / "motion" / "MOTION_INDEX.md")
    print(f"\n[selftest] artifacts: {idx} ({'exists' if idx.exists() else 'MISSING'}), "
          f"events={d['counts']['events']} pages={d['counts']['strip_pages']}")
    print(f"[selftest] {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="frame-accurate motion lab for reference studies")
    ap.add_argument("video", nargs="?", help="input video")
    ap.add_argument("--video-id", default=None)
    ap.add_argument("--out", default=None, help="output root (default analysis/<video-id>)")
    ap.add_argument("--work", default=None, help="scratch dir (default <out>/.work)")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--cut-thresh", type=float, default=0.15,
                    help="scene-score threshold for a candidate change (recorded with its score)")
    ap.add_argument("--soft-thresh", type=float, default=0.12)
    ap.add_argument("--motion-hz", type=float, default=8.0)
    ap.add_argument("--motion-width", type=int, default=384,
                    help="analysis width; measurement floor is ~1px/frame at this width")
    ap.add_argument("--block", type=int, default=32)
    ap.add_argument("--min-var", type=float, default=6.0)
    ap.add_argument("--step", type=int, default=16)
    ap.add_argument("--bucket", type=float, default=0.5)
    ap.add_argument("--event-fps", type=float, default=15.0)
    ap.add_argument("--event-pre", type=float, default=0.8)
    ap.add_argument("--event-post", type=float, default=0.8)
    ap.add_argument("--event-max", type=float, default=3.0)
    ap.add_argument("--max-events", type=int, default=400)
    ap.add_argument("--base-fps", type=float, default=2.0)
    ap.add_argument("--no-clips", action="store_true")
    ap.add_argument("--no-sheets", action="store_true")
    ap.add_argument("--no-strips", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest(args))
    if not args.video:
        ap.error("video path required (or --selftest)")
    video = Path(args.video)
    vid = args.video_id or video.stem.split(" - ")[0].strip()
    out = Path(args.out) if args.out else Path("analysis") / vid
    analyze(video, out, vid, args)


if __name__ == "__main__":
    main()
