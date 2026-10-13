#!/usr/bin/env python3
"""
qa_frame.py — engine QA: seek an engine to given times, screenshot, and report
screen-space bounding boxes of chosen elements (flags anything out of frame).

Run from the youtube_documentary/ project root:

  python3 tools/qa_frame.py <engine.html> <config.json> <t1,t2,...> [selector] [outdir]

Engine, config, asset, and output paths are resolved relative to that root
(not the caller's working directory).
"""
import asyncio, json, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]  # tools/ -> youtube_documentary/

def resolve(v):
    if not v: return None
    p = pathlib.Path(v)
    if p.is_absolute(): return p
    return ROOT.joinpath(*[q for q in p.parts if q not in ("..", ".")]).resolve()

def project_path(v):
    """Resolve v relative to the project root, unless it already exists as given."""
    p = pathlib.Path(v)
    if p.is_absolute() or p.exists(): return p
    candidate = ROOT / p
    return candidate if candidate.exists() else p

async def run(engine, cfg_path, times, sel, outdir):
    engine_path = project_path(engine)
    cfg = json.loads(project_path(cfg_path).read_text(encoding="utf-8"))
    for k in ("hero_img", "sil_img", "rim_img", "signature", "tex",
              "bg_a", "bg_b", "bg_c", "walker", "walker2"):
        if cfg.get(k):
            p = resolve(cfg[k])
            cfg[k] = p.as_uri() if p.exists() else cfg[k]
    if isinstance(cfg.get("assets"), dict):
        for name, v in cfg["assets"].items():
            p = resolve(v)
            cfg["assets"][name] = p.as_uri() if p.exists() else v
    out = pathlib.Path(outdir)
    if not out.is_absolute(): out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--force-color-profile=srgb", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
        await pg.add_init_script(f"window.SCENE_CONFIG = {json.dumps(cfg)};")
        await pg.goto(engine_path.resolve().as_uri())
        for _ in range(60):
            ok = await pg.evaluate("window.ready ? window.ready() : !!window.seek")
            if ok: break
            await pg.wait_for_timeout(100)
        await pg.wait_for_timeout(700)
        stage = await pg.query_selector("#stage")
        for t in times:
            await pg.evaluate(f"window.seek({t})")
            await pg.wait_for_timeout(60)
            shot = out / f"{engine_path.stem}_t{t:05.2f}.png"
            await stage.screenshot(path=str(shot))
            boxes = await pg.evaluate(
                """(sel)=>{const st=document.getElementById('stage').getBoundingClientRect();
                   const out=[];
                   document.querySelectorAll(sel).forEach(e=>{
                     const r=e.getBoundingClientRect();
                     const vis=getComputedStyle(e).opacity;
                     if(r.width<1||r.height<1||parseFloat(vis)<0.02) return;
                     out.push({id:e.id||e.className, x:Math.round(r.left-st.left), y:Math.round(r.top-st.top),
                               w:Math.round(r.width), h:Math.round(r.height),
                               r:Math.round(r.right-st.left), b:Math.round(r.bottom-st.top), op:vis});});
                   return out;}""", sel)
            print(f"t={t:5.2f}  {shot.name}")
            for bx in boxes:
                oob = []
                if bx["x"] < 0: oob.append(f"LEFT {bx['x']}")
                if bx["r"] > 1920: oob.append(f"RIGHT +{bx['r']-1920}")
                if bx["y"] < 0: oob.append(f"TOP {bx['y']}")
                if bx["b"] > 1080: oob.append(f"BOTTOM +{bx['b']-1080}")
                flag = ("  *** OUT: " + ", ".join(oob)) if oob else ""
                print(f"    {bx['id']:12s} x[{bx['x']:5d}..{bx['r']:5d}] y[{bx['y']:5d}..{bx['b']:5d}] op={bx['op']}{flag}")
        await b.close()
    if errs: print("! page errors:", errs[:3])

if __name__ == "__main__":
    a = sys.argv
    asyncio.run(run(a[1], a[2], [float(x) for x in a[3].split(",")],
        a[4] if len(a) > 4 else "#capTop,#capLine,#whyWrap,#qCool,#qWarm,#nameWrap,#sigWrap,#dateWrap,#heroPhoto",
        a[5] if len(a) > 5 else ".cache/qa"))
