import asyncio, sys, pathlib
from playwright.async_api import async_playwright

async def main(path, out, w, h):
    svg = pathlib.Path(path).read_text(encoding="utf-8")
    html = f"<!doctype html><html><body style='margin:0;background:#fff'>{svg}</body></html>"
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        await pg.set_content(html, wait_until="load")
        await pg.wait_for_timeout(500)
        el = await pg.query_selector("svg")
        await el.screenshot(path=out, timeout=60000)
        await b.close()

asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])))
