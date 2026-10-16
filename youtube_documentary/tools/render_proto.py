#!/usr/bin/env python3
"""
render_proto.py — renders board_motion_proto_v1.html frame-accurately via headless Chromium.
Usage: python3 tools/render_proto.py <html> <outdir> <fps> <duration_seconds> [poster_t]
"""
import asyncio, sys, pathlib
from playwright.async_api import async_playwright

async def main(html, outdir, fps, dur, poster_t=1.15):
    html = pathlib.Path(html).resolve()
    outdir = pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    n = int(fps * dur)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--force-color-profile=srgb"])
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        await pg.goto(f"file://{html}")
        await pg.wait_for_timeout(900)
        stage = await pg.query_selector("#stage")
        for i in range(n):
            t = i / fps
            await pg.evaluate(f"window.seek({t:.6f})")
            await stage.screenshot(path=str(outdir / f"f{i:04d}.png"), timeout=30000)
            if i % 60 == 0:
                print(f"frame {i}/{n}", flush=True)
        await pg.evaluate(f"window.seek({poster_t})")
        await stage.screenshot(path=str(outdir / "poster.png"), timeout=30000)
        await b.close()
    print(f"done: {n} frames -> {outdir}", flush=True)

if __name__ == "__main__":
    a = sys.argv
    asyncio.run(main(a[1], a[2], float(a[3]) if len(a) > 3 else 30,
                     float(a[4]) if len(a) > 4 else 8.0,
                     float(a[5]) if len(a) > 5 else 1.15))
