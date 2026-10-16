#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sheet_slice.py — قصّ نافذة زمنية من صفحة فيلمستريب وترتيبها بشرائح مكبّرة للقراءة الدقيقة.

ليش؟ صفحات الفيلمستريب @2fps عنا 10 تايل بالصف → التايل 156px عرضًا، النص الصغير
عالشاشة بيصير غير مقروء. هالأداة بتقصّ **بس** التايلات يلي بتقع بالنافذة الزمنية
المطلوبة وبتكبّرها (×2 افتراضيًا) → صورة صغيرة واضحة لكل نافذة.

الاستخدام:
  python3 tools/sheet_slice.py PAGE.jpg 120.0 129.5 --out win.jpg [--zoom 2] [--cols 5]
  python3 tools/sheet_slice.py PAGE.jpg --from-breakdown BREAKDOWN_AR.md --page 5 --out gaps.jpg

بيقرا الحدود من اسم الملف: pNN_of_MM.jpg → رقم الصفحة. معدّل الفريم الافتراضي 2fps
(بارامتر --base-fps)، و 60 تايل بالصفحة (يُستنتج من الصفحة نفسها بتحليل الفراغات).
"""
import argparse, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def parse_page_no(path: Path):
    m = re.search(r"p(\d+)_of_(\d+)", path.name)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def load_font(size=18):
    for cand in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(cand, size)
        except Exception:
            continue
    return ImageFont.load_default()


def slice_window(img, page_no, t0, t1, base_fps=2.0, tiles_per_page=60, tiles_per_row=10,
                 zoom=2.0, label=True):
    """يقصّ التايلات يلي بتقع بـ[t0,t1] من صفحة رقم page_no ويرجع صورة مركّبة."""
    W, H = img.size
    rows = tiles_per_page // tiles_per_row
    cw, ch = W // tiles_per_row, H // rows
    page_start = (page_no - 1) * (tiles_per_page / base_fps)
    k0 = max(0, int((t0 - page_start) * base_fps))
    k1 = min(tiles_per_page - 1, int(round((t1 - page_start) * base_fps - 1e-6)))
    ks = list(range(k0, k1 + 1))
    if not ks:
        return None, 0
    ncols = min(len(ks), 5)
    nrows = (len(ks) + ncols - 1) // ncols
    zw, zh = int(cw * zoom), int(ch * zoom)
    pad, tl, gap = 6, 22 if label else 0, 6
    out = Image.new("RGB", (ncols * zw + (ncols + 1) * pad,
                            nrows * (zh + tl) + (nrows + 1) * pad), (18, 18, 18))
    d = ImageDraw.Draw(out)
    f = load_font(16)
    for i, k in enumerate(ks):
        r, c = divmod(k, tiles_per_row)
        tile = img.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)).resize((zw, zh), Image.LANCZOS)
        x = pad + (i % ncols) * (zw + pad)
        y = pad + (i // ncols) * (zh + tl + pad)
        out.paste(tile, (x, y + tl))
        if label:
            t = page_start + k / base_fps
            d.text((x + 2, y + 2), f"{int(t // 60)}:{t % 60:04.1f}", fill=(255, 220, 90), font=f)
    return out, len(ks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page", help="صورة الصفحة pNN_of_MM.jpg")
    ap.add_argument("t0", nargs="?", type=float, help="بداية النافذة بالثواني")
    ap.add_argument("t1", nargs="?", type=float, help="نهاية النافذة")
    ap.add_argument("--base-fps", type=float, default=2.0)
    ap.add_argument("--tiles-per-page", type=int, default=60)
    ap.add_argument("--tiles-per-row", type=int, default=10)
    ap.add_argument("--zoom", type=float, default=2.0)
    ap.add_argument("--out", default="slice.jpg")
    a = ap.parse_args()
    p = Path(a.page)
    no, tot = parse_page_no(p)
    if no is None:
        sys.exit("اسم الملف لازم يكون pNN_of_MM.jpg")
    img = Image.open(p).convert("RGB")
    if a.t0 is None or a.t1 is None:
        a.t0, a.t1 = 0.0, a.tiles_per_page / a.base_fps
    out, n = slice_window(img, no, a.t0, a.t1, a.base_fps, a.tiles_per_page,
                          a.tiles_per_row, a.zoom)
    if out is None:
        sys.exit("ما في تايلات بهالنافذة")
    out.save(a.out, quality=95)
    print(f"[ok] صفحة {no}/{tot} · نافذة {a.t0:.1f}–{a.t1:.1f}s · {n} تايل → {a.out} ({out.size[0]}×{out.size[1]})")


if __name__ == "__main__":
    main()
