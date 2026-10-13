#!/usr/bin/env python3
"""
prep_hero_asset.py — build the hero assets for the general board engine
from any source photo:
  1) hero_solo_cc0.jpg          cropped portrait of the subject
  2) hero_silhouette_dark.png   dark silhouette mass (alpha)
  3) hero_rim.png               light trace of the subject's own outlines (alpha)

Usage:
  python3 tools/prep_hero_asset.py <src.jpg> <out_dir> --crop L,T,R,B [--head-trim 0.14]
"""
import argparse, pathlib
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out_dir")
    ap.add_argument("--crop", required=True, help="left,top,right,bottom in pixels of the source")
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--head-trim", type=float, default=0.14, help="fraction of top to ignore (sky/bokeh)")
    ap.add_argument("--foot-trim", type=float, default=0.06)
    a = ap.parse_args()

    out = pathlib.Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    im = Image.open(a.src).convert("RGB")
    L, T, R, B = [int(x) for x in a.crop.split(",")]
    crop = im.crop((L, T, R, B))
    crop = crop.resize((crop.size[0] * a.scale, crop.size[1] * a.scale), Image.LANCZOS)
    crop.save(out / "hero_solo_cc0.jpg", quality=94)

    g = np.asarray(crop.convert("L")).astype(np.float32) / 255.0
    H, W = g.shape

    # --- light trace: edges of the subject's own structure ---
    gs = ndimage.gaussian_filter(g, 2.2)
    sx = ndimage.sobel(gs, axis=1); sy = ndimage.sobel(gs, axis=0)
    mag = np.hypot(sx, sy); mag = mag / (mag.max() or 1.0)
    yy, xx = np.mgrid[0:H, 0:W]
    region = (np.clip(1.0 - (np.abs(xx - W * 0.5) / (W * 0.72)) ** 3.0, 0, 1)
              * np.clip(1.0 - (yy / (H * 0.98)) ** 3.0, 0, 1))
    region[: int(H * a.head_trim), :] = 0
    region[int(H * (1 - a.foot_trim)):, :] = 0
    edge = np.clip((mag - 0.10) / 0.22, 0, 1) * region
    edge = ndimage.gaussian_filter(edge, 1.1)
    edge = ndimage.binary_opening(edge > 0.25, iterations=1).astype(np.float32) * edge
    edge = np.clip(edge * 1.45, 0, 1)

    # --- dark mass ---
    mass = np.clip((g - 0.44) / 0.30, 0, 1)
    mass = ndimage.gaussian_filter(mass, 6.0)
    mass = np.clip(mass * 1.15, 0, 1)
    mass[: int(H * 0.05), :] *= 0.0

    dark = np.zeros((H, W, 4), np.uint8)
    dark[..., 0], dark[..., 1], dark[..., 2] = 8, 10, 15
    dark[..., 3] = (mass * 245).astype(np.uint8)
    Image.fromarray(dark, "RGBA").save(out / "hero_silhouette_dark.png")

    trace = np.zeros((H, W, 4), np.uint8)
    trace[..., 0], trace[..., 1], trace[..., 2] = 168, 219, 244
    trace[..., 3] = (edge * 200).astype(np.uint8)
    Image.fromarray(trace, "RGBA").save(out / "hero_rim.png")

    print(f"wrote hero_solo_cc0.jpg, hero_silhouette_dark.png, hero_rim.png -> {out}")
    print("NOTE: always eyeball the rim/silhouette before shipping — verify the crop is YOUR subject only.")

if __name__ == "__main__":
    main()
