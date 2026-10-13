#!/usr/bin/env python3
"""
build_scene.py — ONE COMMAND for a whole scene: config -> frames -> audio -> MP4.

  python3 tools/build_scene.py config/geo_scene01.json

Run from the youtube_documentary/ project root. Config, asset, and engine
paths are resolved relative to that root (not the caller's working directory).

Reads a scene JSON (engine: "board" | "geo" | "story"), renders every frame
with headless Chromium, synthesises the SFX bed from the config's "audio"
event list, and muxes the final MP4. All local, all free, no watermarks.
"""
import asyncio, json, pathlib, subprocess, sys, tempfile, shutil
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]  # tools/ -> youtube_documentary/
sys.path.insert(0, str(ROOT / "tools"))
from playwright.async_api import async_playwright
from synth_sfx_cine import (SR, whoosh, impact, brush, swell, note, riser, step, fft_band,
                            adsr, schroeder, stereo, hp)   # reusable SFX palette

ENGINES = {"board": "board_engine.html", "geo": "geo_engine.html", "story": "story_engine.html"}

FRAME_DIR = ROOT / ".cache" / "scene_frames"

# ------------------------------------------------------------------ audio
CFG_REVERB = {}
def synth_audio(events, dur, out_wav):
    n = int(SR * dur)
    buf = np.zeros((n, 2))
    def place(sig, t, pan=0.0, gain=1.0):
        i0 = int(t * SR); i1 = min(n, i0 + len(sig))
        if i1 <= i0: return
        s = sig[: i1 - i0] * gain
        l = np.sqrt(0.5 * (1 - pan)); r = np.sqrt(0.5 * (1 + pan))
        buf[i0:i1, 0] += s * l * 1.41
        buf[i0:i1, 1] += s * r * 1.41
    for i, e in enumerate(events):
        kind = e.get("sfx", "brush"); g = float(e.get("gain", 0.08)); t = float(e.get("t", 0))
        pan = float(e.get("pan", 0.0))
        if kind == "whoosh":
            place(whoosh(float(e.get("dur", 0.6)), float(e.get("lo", 170)), float(e.get("hi", 2500)), g, seed=11 + i), t, pan)
        elif kind == "whooshUp":
            place(whoosh(float(e.get("dur", 0.9)), float(e.get("lo", 200)), float(e.get("hi", 3200)), g, up=True, seed=31 + i), t, pan)
        elif kind == "impact":
            place(impact(float(e.get("dur", 0.7)), float(e.get("f0", 96)), float(e.get("f1", 44)), g, seed=51 + i), t, pan)
        elif kind == "brush":
            place(brush(float(e.get("dur", 0.4)), g, seed=71 + i, tone=float(e.get("tone", 0.5))), t, pan)
        elif kind == "swell":
            place(swell(float(e.get("dur", 1.9)), float(e.get("f0", 96)), g, seed=91 + i), t, pan)
        elif kind == "note":
            place(note(float(e.get("freq", 110.0)), float(e.get("dur", 3.0)), g,
                       float(e.get("bright", 0.28)), seed=111 + i), t, pan)
        elif kind == "riser":
            place(riser(float(e.get("dur", 1.1)), g, seed=131 + i), t, pan)
        elif kind == "step":
            place(step(float(e.get("dur", 0.17)), g, seed=151 + i), t, pan)
        else:
            print("  ! unknown sfx:", kind)
    rv = CFG_REVERB
    mono = buf[:, 0] * 0.72 + buf[:, 1] * 0.72
    wet = schroeder(mono, mix=rv.get("mix", 0.12), decay=rv.get("decay", 1.5), damp=rv.get("damp", 0.5))
    st = stereo(wet, width=1.0, haas_ms=rv.get("haas", 8.0))
    st = np.tanh(st * 1.18) * 0.92
    peak = np.max(np.abs(st)) or 1.0
    st = st / peak * 0.27
    pcm = (st * 32767).astype(np.int16)
    import wave
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    x = pcm.astype(np.int32).reshape(-1, 2)
    jump = int(np.abs(np.diff(x, axis=0)).max())
    print(f"  audio: {out_wav.name} ({dur}s) | max jump {jump} ({jump/32768*100:.1f}% FS)")

# ------------------------------------------------------------------ frames
def resolve(v):
    if not v: return None
    if v.startswith("file:"): return pathlib.Path(v[7:])
    p = pathlib.Path(v)
    if p.is_absolute(): return p
    parts = [q for q in p.parts if q not in ("..", ".")]
    return (ROOT.joinpath(*parts)).resolve()

async def render_frames(cfg, outdir):
    engine = cfg.get("engine", "board")
    html = ROOT / "tools/engines" / ENGINES.get(engine, "board_engine.html")
    dur = float(cfg.get("timing", {}).get("dur", 10.0))
    fps = 30; n = int(round(fps * dur))
    if outdir.exists(): shutil.rmtree(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for k in ("hero_img", "sil_img", "rim_img", "signature", "tex"):
        if cfg.get(k):
            p = resolve(cfg[k])
            if p and p.exists(): cfg[k] = p.as_uri()
            elif p: raise SystemExit(f"missing asset {k}: {p}")
    if isinstance(cfg.get("assets"), dict):     # story engine: named asset map
        for name, v in cfg["assets"].items():
            p = resolve(v)
            if p and p.exists(): cfg["assets"][name] = p.as_uri()
            elif p: raise SystemExit(f"missing asset '{name}': {p}")
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--force-color-profile=srgb", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script(f"window.SCENE_CONFIG = {json.dumps(cfg)};")
        await pg.goto(html.as_uri())
        for _ in range(80):     # wait for textures / images / fonts
            ok = await pg.evaluate("window.ready ? window.ready() : true")
            if ok: break
            await pg.wait_for_timeout(100)
        await pg.wait_for_timeout(600)
        stage = await pg.query_selector("#stage")
        for i in range(n):
            await pg.evaluate(f"window.seek({i/fps:.6f})")
            await stage.screenshot(path=str(outdir / f"f{i:04d}.png"), timeout=30000)
            if i % 90 == 0: print(f"  frame {i}/{n}", flush=True)
        await b.close()
    if errs: print("  ! page errors:", errs[:2])
    return n, fps

# ------------------------------------------------------------------ main
def main(scene_json, out_name=None, poster_t=None):
    global CFG_REVERB
    scene_path = pathlib.Path(scene_json)
    if not scene_path.is_absolute() and not scene_path.exists():
        candidate = ROOT / scene_path  # resolve relative to the project root
        if candidate.exists(): scene_path = candidate
    cfg = json.loads(scene_path.read_text(encoding="utf-8"))
    CFG_REVERB = cfg.get("reverb", {}) or {}
    dur = float(cfg.get("timing", {}).get("dur", 10.0))
    rid = cfg.get("id", scene_path.stem)
    print(f"[1/3] frames  ({cfg.get('engine','board')} engine, {dur}s)")
    n, fps = asyncio.run(render_frames(cfg, FRAME_DIR))
    tmp = ROOT / ".cache"
    wav = tmp / f"{rid}.wav"
    print("[2/3] audio")
    synth_audio(cfg.get("audio", []), dur, wav)
    if poster_t is not None:
        shutil.copy(FRAME_DIR / f"f{int(float(poster_t)*fps):04d}.png", FRAME_DIR / "poster.png")
    out = ROOT / "renders" / (out_name or f"{rid}.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    print("[3/3] mux")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(fps),"-i",str(FRAME_DIR/"f%04d.png"),
                    "-i",str(wav),"-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p",
                    "-profile:v","high","-level","4.1","-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
                    "-movflags","+faststart","-shortest",str(out)], check=True)
    print("  ->", out)
    return out

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2] if len(a) > 2 else None, a[3] if len(a) > 3 else None)
