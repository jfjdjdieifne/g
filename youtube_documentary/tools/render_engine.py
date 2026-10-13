#!/usr/bin/env python3
"""
render_engine.py — renders tools/engines/board_engine.html with a JSON scene config.
Usage: python3 tools/render_engine.py <scene.json> <outdir> [poster_t]
Config paths for images are resolved relative to the workspace root (/home/user).
"""
import asyncio, sys, json, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path("/home/user")
ENGINE = ROOT / "tools/engines/board_engine.html"

def resolve(v):
    """Resolve any config path to an absolute /home/user path."""
    if v.startswith("file:"):
        return pathlib.Path(v[7:])
    p = pathlib.Path(v)
    if p.is_absolute():
        return p
    # strip leading ../ segments, then anchor at workspace root
    parts = [q for q in p.parts if q not in ("..", ".")]
    return (ROOT.joinpath(*parts)).resolve()

def absolutize(cfg):
    for k in ("hero_img", "sil_img", "signature", "rim_img"):
        v = cfg.get(k)
        if v:
            p = resolve(v)
            if not p.exists():
                raise SystemExit(f"missing asset for {k}: {p}")
            cfg[k] = p.as_uri()
    return cfg

async def main(scene_json, outdir, poster_t=None):
    cfg = json.loads(pathlib.Path(scene_json).read_text(encoding="utf-8"))
    cfg = absolutize(cfg)
    fps = 30
    dur = float(cfg.get("timing", {}).get("dur", 10.0))
    n = int(fps * dur)
    outdir = pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    poster_t = float(poster_t) if poster_t else 1.4
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--force-color-profile=srgb"])
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        await pg.add_init_script(f"window.SCENE_CONFIG = {json.dumps(cfg)};")
        await pg.goto(ENGINE.as_uri())
        await pg.wait_for_timeout(900)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        stage = await pg.query_selector("#stage")
        for i in range(n):
            t = i / fps
            await pg.evaluate(f"window.seek({t:.6f})")
            await stage.screenshot(path=str(outdir / f"f{i:04d}.png"), timeout=30000)
            if i % 60 == 0:
                print(f"frame {i}/{n}", flush=True)
        await pg.evaluate(f"window.seek({poster_t})")
        await stage.screenshot(path=str(outdir / "poster.png"), timeout=30000)
        if errs:
            print("PAGE ERRORS:", errs[:3])
        await b.close()
    print(f"done: {n} frames -> {outdir}")

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
