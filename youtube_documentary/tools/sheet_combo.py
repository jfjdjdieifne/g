#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sheet_combo.py — تجميع عدة نوافذ زمنية من صفحات فيلمستريب بـ«لوح مراجعة» واحد.

ليش؟ إذا عندنا عشرات الفراغات الصغيرة (١–٣ ثواني)، منقراها بـ4 لوحات كبيرة
بدل 40 صورة. كل نافذة إلها عنوان (رقم الصفحة + المجال الزمني) فوقها.

الاستخدام:
  python3 tools/sheet_combo.py --pages-dir DIR --windows "p05:122:145;p06:167:178" --out combo.jpg
  python3 tools/sheet_combo.py --pages-dir DIR --gaps gaps.txt --out combo.jpg --per-image 12 --max-images 4
حيث gaps.txt أسطر بالشكل: p05 122.0 145.0
"""
import argparse, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from sheet_slice import slice_window, parse_page_no, load_font


def build_combo(entries, pages_dir, zoom=1.3, per_row=2, fonts=(26, 20)):
    """entries: [(page_path, page_no, t0, t1, label)] → صورة واحدة"""
    tiles = []
    for p, no, t0, t1, lab in entries:
        no = int(str(no).lstrip('p'))
        img = Image.open(p).convert("RGB")
        out, n = slice_window(img, no, t0, t1, zoom=zoom, label=True)
        if out is not None:
            tiles.append((lab, out))
    if not tiles:
        return None
    pad, hdr, gap = 8, 34, 10
    col_w = [0] * per_row
    for i, (lab, im) in enumerate(tiles):
        col_w[i % per_row] = max(col_w[i % per_row], im.size[0])
    rows_n = math.ceil(len(tiles) / per_row)
    row_h = []
    for r in range(rows_n):
        h = 0
        for c in range(per_row):
            i = r * per_row + c
            if i < len(tiles):
                h = max(h, tiles[i][1].size[1])
        row_h.append(h)
    W = sum(col_w) + (per_row + 1) * pad
    H = sum(row_h) + (rows_n + 1) * (pad + hdr)
    combo = Image.new("RGB", (W, H), (12, 12, 14))
    d = ImageDraw.Draw(combo)
    f1, f2 = load_font(fonts[0]), load_font(fonts[1])
    y = pad
    for r in range(rows_n):
        x = pad
        for c in range(per_row):
            i = r * per_row + c
            if i >= len(tiles):
                continue
            lab, im = tiles[i]
            d.text((x + 4, y), lab, fill=(120, 220, 255), font=f1)
            combo.paste(im, (x, y + hdr))
            x += col_w[c] + pad
        y += row_h[r] + hdr + pad
    return combo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages-dir", required=True)
    ap.add_argument("--windows", help='p05:122:145;p06:167:178')
    ap.add_argument("--gaps", help="ملف: كل سطر pNN t0 t1")
    ap.add_argument("--out", default="combo.jpg")
    ap.add_argument("--zoom", type=float, default=1.3)
    ap.add_argument("--per-image", type=int, default=12)
    ap.add_argument("--pad", type=float, default=0.5, help="هامش حوالين كل نافذة (ث)")
    a = ap.parse_args()
    pdir = Path(a.pages_dir)
    entries = []
    if a.windows:
        for w in a.windows.split(";"):
            parts = w.split(":")
            rows = parts[:1] + parts[1:]
            if len(rows) != 3:
                sys.exit(f"نافذة غلط: {w}")
            pg, t0, t1 = rows[0], float(rows[1]), float(rows[2])
            entries.append((pdir / f"{pg}_of_{0}.jpg", pg, t0, t1, f"{pg} {t0:.1f}–{t1:.1f}"))
    if a.gaps:
        for line in Path(a.gaps).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pg, t0, t1 = line.split()
            t0, t1 = float(t0), float(t1)
            entries.append((None, pg, t0, t1, f"{pg} {t0:.1f}–{t1:.1f}"))
    # حلّ المسارات (نبحث عن أي ملف بيبلش بـpNN_of_)
    fixed = []
    for p, pg, t0, t1, lab in entries:
        found = sorted(pdir.glob(f"{pg}_of_*.jpg"))
        if not found:
            print(f"[skip] ما لقيت صفحة {pg} بـ{pdir}")
            continue
        fixed.append((found[0], pg, t0 - a.pad, t1 + a.pad, lab))
    n = a.per_image
    imgs = []
    for i in range(0, len(fixed), n):
        chunk = fixed[i:i + n]
        c = build_combo(chunk, pdir, zoom=a.zoom)
        if c:
            imgs.append((i, c))
    base = Path(a.out)
    for idx, (offset, c) in enumerate(imgs):
        out = base.with_name(f"{base.stem}_{idx+1:02d}{base.suffix}")
        c.save(out, quality=92)
        print(f"[ok] {out} ({c.size[0]}×{c.size[1]}) — نوافذ {offset+1}..{offset+len(chunk) if False else min(offset+n, len(fixed))}")
    print(f"[ok] {len(fixed)} نافذة → {len(imgs)} لوحة")


if __name__ == "__main__":
    main()
