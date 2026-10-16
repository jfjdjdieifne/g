import asyncio, sys, pathlib
from playwright.async_api import async_playwright

async def main(html, outdir, times):
    html = pathlib.Path(html).resolve()
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":1920,"height":1080}, device_scale_factor=1)
        await pg.goto(f"file://{html}"); await pg.wait_for_timeout(900)
        stage = await pg.query_selector("#stage")
        for t in times:
            await pg.evaluate(f"window.seek({t})")
            await stage.screenshot(path=str(out/f"t{t}.png"))
        await b.close()
    print("spots done")

asyncio.run(main(sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3:]]))
