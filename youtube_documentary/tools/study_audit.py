#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
study_audit.py — ضمانة «ما يروح ولا لقطة ولا ثانية» بالدليل، مو بالوعد.

شو بيعمل:
  1) يبني «دفتر تغطية» (COVERAGE.md): كل صفحة فيلمستريب + كل حدث (قطعة/أسود/صمت/عنقود حركة)
     مع حالة كل واحدة (موجودة؟ مقروءة؟).
  2) يفحص التفكيك (BREAKDOWN_AR.md) ويفشل (exit 1) إذا:
     - ناقص صفحات فيلمستريب (عدد أو حجم — يكشف التايلز المقطوعة يلي صارت سابقًا).
     - في فراغ زمني بالتفكيك (مقطع من الفيديو ما إله صف مكتوب).
     - في حدث (قطعة/أسود/صمت) واقع **برّا أي صف** من صفوف التفكيك → يعني ما حدا كتب عنه.
  3) يطبع تقرير واضح + يكتب COVERAGE.md بجداول عربية.

الاستخدام (من مجلد المشروع youtube_documentary/):
  # 1) دفتر التغطية فقط (قبل ما نبلش نقرا)
  python3 tools/study_audit.py --study analysis/DwTK_VT54OY --video-duration 3456 --emit-ledger

  # 2) بعد ما ينكتب التفكيك — الفحص الصارم
  python3 tools/study_audit.py --study analysis/DwTK_VT54OY --video-duration 3456 --verify

  # 3) اختبار ذاتي للأداة (يبني مجلد دراسة وهمي ويمتحن PASS/FAIL)
  python3 tools/study_audit.py --selftest

بيقرا الأحداث من أحد المصدرين تلقائيًا:
  - motion/dossier.json  (مخرَج مختبر الحركة reference_motion.py)
  - metrics.json         (مخرَج analyze_pipeline.py: cuts / silences / blacks)
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# parsing helpers
# ---------------------------------------------------------------------------

TS = r"(?:\d+:\d{1,2}(?::\d{1,2})?(?:[.,]\d{1,3})?)"
ROW_RANGE = re.compile(rf"({TS})\s*(?:[–—\-—]|to|→|الى|إلى)\s*({TS})")
ROW_SINGLE = re.compile(rf"({TS})")


def parse_ts(s: str) -> float:
    s = s.strip().replace(",", ".")
    parts = s.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        return float(parts[0])
    except ValueError:
        return float("nan")


def parse_breakdown(text: str):
    """Extracts (t0, t1, raw_row) from markdown table rows that carry timecodes.

    Rows without an explicit range get a zero-width interval at the single time.
    Returns list sorted by t0.
    """
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        if set(first) <= set("-: "):          # separator row
            continue
        m = ROW_RANGE.search(first)
        if m:
            t0, t1 = parse_ts(m.group(1)), parse_ts(m.group(2))
            if t1 < t0:
                t0, t1 = t1, t0
        else:
            m2 = ROW_SINGLE.search(first)
            if not m2:
                continue
            t0 = t1 = parse_ts(m2.group(1))
        if math.isnan(t0) or math.isnan(t1):
            continue
        rows.append({"t0": t0, "t1": t1, "raw": line.strip()})
    rows.sort(key=lambda r: (r["t0"], r["t1"]))
    return rows


def merge_intervals(rows, min_gap=0.0):
    out = []
    for r in rows:
        if out and r["t0"] <= out[-1]["t1"] + min_gap:
            out[-1]["t1"] = max(out[-1]["t1"], r["t1"])
        else:
            out.append({"t0": r["t0"], "t1": r["t1"]})
    return out


def find_gaps(intervals, duration, min_gap=1.0):
    gaps = []
    cur = 0.0
    for iv in intervals:
        if iv["t0"] - cur > min_gap:
            gaps.append((cur, iv["t0"]))
        cur = max(cur, iv["t1"])
    if duration - cur > min_gap:
        gaps.append((cur, duration))
    return gaps


def fmt(t: float) -> str:
    m = int(max(0.0, t) // 60)
    s = max(0.0, t) - 60 * m
    return f"{m:02d}:{s:06.3f}"


# ---------------------------------------------------------------------------
# event loading (both shapes)
# ---------------------------------------------------------------------------

def load_events(study: Path):
    """Returns (events, source) where events = [{'t','t1','type','label'}]."""
    dossier = study / "motion" / "dossier.json"
    if dossier.exists():
        d = json.loads(dossier.read_text(encoding="utf-8"))
        evs = []
        for c in d.get("cuts", []):
            t = float(c.get("t", c) if isinstance(c, dict) else c)
            evs.append({"t": t, "t1": t, "type": "cut", "label": f"قطعة (score {float(c.get('score', 0)):.2f})" if isinstance(c, dict) else "قطعة"})
        for b in d.get("blacks", []):
            evs.append({"t": float(b["t0"]), "t1": float(b["t1"]), "type": "black", "label": "أسود"})
        for b in d.get("freezes", []):
            evs.append({"t": float(b["t0"]), "t1": float(b["t1"]), "type": "freeze", "label": "تجمّد"})
        for b in d.get("silences", []):
            evs.append({"t": float(b["t0"]), "t1": float(b["t1"]), "type": "silence", "label": "صمت"})
        for e in d.get("events", []):
            evs.append({"t": float(e.get("t", e.get("t0", 0))), "t1": float(e.get("t1", e.get("t", 0))),
                        "type": "review", "label": f"حدث مراجعة ({e.get('type','?')})"})
        if evs:
            return evs, "motion/dossier.json"

    metrics = study / "metrics.json"
    if metrics.exists():
        d = json.loads(metrics.read_text(encoding="utf-8"))
        evs = []

        def add(key, kind, label):
            v = d.get(key)
            if not v:
                return
            for it in v:
                if isinstance(it, (int, float)):
                    evs.append({"t": float(it), "t1": float(it), "type": kind, "label": label})
                elif isinstance(it, dict):
                    t0 = it.get("t0", it.get("t", it.get("start")))
                    t1 = it.get("t1", it.get("t", it.get("end", t0)))
                    if t0 is None:
                        continue
                    evs.append({"t": float(t0), "t1": float(t1), "type": kind, "label": label})

        add("cuts", "cut", "قطعة")
        add("silences", "silence", "صمت")
        add("blacks", "black", "أسود")
        if evs:
            return evs, "metrics.json"
    return [], "none"


# ---------------------------------------------------------------------------
# filmstrip pages
# ---------------------------------------------------------------------------

PAGE_RE = re.compile(r"^p(\d+)_of_(\d+)\.(jpg|jpeg|png)$", re.I)


def scan_pages(study: Path):
    for sub in ("filmstrip2fps", "filmstrip", "motion/filmstrip"):
        d = study / sub
        if d.is_dir():
            pages = []
            for f in sorted(d.iterdir()):
                m = PAGE_RE.match(f.name)
                if m:
                    pages.append({"idx": int(m.group(1)), "of": int(m.group(2)),
                                  "file": f, "size": f.stat().st_size})
            if pages:
                return sub, pages
    return None, []


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

def audit(study: Path, duration: float, args) -> dict:
    report = {"study": str(study), "duration": duration, "problems": [], "warnings": [], "checks": {}}
    pages_dir, pages = scan_pages(study)
    tiles = args.tiles_per_page
    page_span = tiles / args.base_fps
    expected = max(1, math.ceil(duration / page_span))
    declared = max([p["of"] for p in pages], default=0)
    sizes = [p["size"] for p in pages]
    tiny = [p for p in pages if p["size"] < args.min_page_bytes]
    missing_idx = sorted(set(range(1, expected + 1)) - {p["idx"] for p in pages})
    report["page_rows"] = [{"idx": pp["idx"], "name": pp["file"].name,
                            "size_kb": pp["size"] // 1024} for pp in pages]
    report["checks"]["pages"] = {
        "dir": pages_dir, "found": len(pages), "expected": expected, "declared_total": declared,
        "missing": missing_idx[:50], "missing_count": len(missing_idx),
        "tiny": [f"{p['file'].name} ({p['size']//1024}KB)" for p in tiny][:20], "tiny_count": len(tiny),
        "min_size_kb": (min(sizes) // 1024) if sizes else 0,
    }
    if pages_dir is None:
        report["problems"].append("ما في مجلد فيلمستريب (filmstrip2fps/ أو filmstrip/).")
    else:
        if len(pages) < expected:
            report["problems"].append(f"صفحات ناقصة: {len(pages)} موجودة من أصل {expected} "
                                      f"(الفيديو {fmt(duration)} @{args.base_fps}fps، {tiles} تايل/صفحة).")
        if missing_idx:
            report["problems"].append(f"في فهارس صفحات مفقودة: {missing_idx[:10]}"
                                      f"{' ...' if len(missing_idx) > 10 else ''}")
        if tiny:
            report["problems"].append(f"في {len(tiny)} صفحة صغيرة/مشكوكة (<{args.min_page_bytes//1024}KB) — غالبًا تايلز مقطوعة.")
        if declared and declared != expected:
            report["problems"].append(f"عنوان الصفحات يقول «of {declared}» بينما المتوقع {expected} (تعارض بالعدد).")

    events, src = load_events(study)
    report["checks"]["events"] = {"source": src, "count": len(events),
                                  "by_type": {k: sum(1 for e in events if e["type"] == k)
                                              for k in sorted({e["type"] for e in events})}}
    if not events:
        msg = ("ما لقيت أي أحداث (لا dossier.json ولا metrics.json) — الأحداث هي أساس ضمان عدم التخطي."
               " شغّل مختبر الحركة: tools/reference_motion.py VIDEO --video-id ID --out analysis/ID")
        if args.allow_missing_events:
            report["warnings"].append(msg + " [تحذير فقط: --allow-missing-events شغّال، التغطية الزمنية تتكلم]")
        else:
            report["problems"].append(msg)

    bd = Path(args.breakdown) if args.breakdown else (study / "BREAKDOWN_AR.md")
    rows = []
    if bd.exists():
        rows = parse_breakdown(bd.read_text(encoding="utf-8", errors="ignore"))
    report["checks"]["breakdown"] = {"file": str(bd), "exists": bd.exists(), "rows": len(rows)}
    if not bd.exists() and args.verify:
        report["problems"].append(f"ملف التفكيك غير موجود: {bd}")

    if rows:
        intervals = merge_intervals([{"t0": r["t0"], "t1": max(r["t1"], r["t0"])} for r in rows], min_gap=0.0)
        gaps = find_gaps(intervals, duration, min_gap=args.max_gap)
        report["checks"]["coverage"] = {
            "intervals": len(intervals),
            "covered_s": round(sum(min(i["t1"], duration) - i["t0"] for i in intervals), 1),
            "gaps": [(round(a, 1), round(b, 1)) for a, b in gaps][:40],
            "gap_count": len(gaps),
            "gap_total_s": round(sum(b - a for a, b in gaps), 1),
        }
        if args.verify and gaps:
            report["problems"].append(
                f"في {len(gaps)} فراغ زمني بالتفكيك (مجموع {sum(b-a for a,b in gaps):.1f} ث) — "
                f"يعني في مقاطع ما إلها صف مكتوب: " +
                "، ".join(f"{fmt(a)}→{fmt(b)}" for a, b in gaps[:6]) +
                (" ..." if len(gaps) > 6 else ""))
        # events outside every written row
        uncovered = []
        for e in events:
            if not any(r["t0"] - args.tolerance <= e["t"] <= r["t1"] + args.tolerance for r in rows):
                uncovered.append(e)
        report["checks"]["events_uncovered"] = {"count": len(uncovered),
                                                "sample": [f"{fmt(e['t'])} {e['label']}" for e in uncovered[:25]]}
        if args.verify and uncovered:
            report["problems"].append(
                f"{len(uncovered)} حدث واقع برّا أي صف تفكيك (يعني ما انكتب عنه): " +
                "، ".join(f"{fmt(e['t'])} {e['label']}" for e in uncovered[:8]) +
                (" ..." if len(uncovered) > 8 else ""))
    else:
        report["checks"]["coverage"] = {"intervals": 0, "gaps": [], "gap_count": 0, "gap_total_s": 0}

    report["verdict"] = "PASS" if not report["problems"] else "FAIL"
    return report


def write_ledger(report: dict, study: Path, args) -> Path:
    out = study / "COVERAGE.md"
    c = report["checks"]
    p = c["pages"]
    e = c["events"]
    cov = c.get("coverage", {})
    L = []
    L.append(f"# دفتر التغطية — {study.name}")
    L.append("")
    L.append(f"> القاعدة: **ما يروح ولا لقطة ولا ثانية بدون فهم**. هالملف بيتولّد آليًا، "
             f"وبيتأكد إنّو: (1) كل صفحات الفيلمستريب موجودة وسليمة، (2) كل حدث إله صف بالتفكيك، (3) ما في فراغ زمني.")
    L.append("")
    L.append(f"- المدة المستهدفة: **{fmt(report['duration'])}** · قاعدة الفريم: **{args.base_fps}fps** · "
             f"{args.tiles_per_page} تايل/صفحة (صفحة = {args.tiles_per_page/args.base_fps:.0f} ث)")
    L.append(f"- صفحات الفيلمستريب: **{p['found']}** موجودة، المتوقع **{p['expected']}**، "
             f"أصغر حجم صفحة {p['min_size_kb']}KB")
    L.append(f"- الأحداث: **{e['count']}** (المصدر: `{e['source']}`) — "
             f"{'، '.join(f'{k}: {v}' for k, v in e['by_type'].items()) if e['by_type'] else 'لا شيء'}")
    L.append(f"- صفوف التفكيك: **{c['breakdown']['rows']}** · مغطّى **{cov.get('covered_s', 0)} ث** · "
             f"فراغات: **{cov.get('gap_count', 0)}** (مجموع {cov.get('gap_total_s', 0)} ث)")
    L.append(f"- **الحكم: {report['verdict']}**")
    if report.get("warnings"):
        L.append("")
        L.append("## ⚠️ تحذيرات (ما بتوقف الحكم)")
        for w in report["warnings"]:
            L.append(f"- {w}")
    L.append("")
    if report["problems"]:
        L.append("## ❌ مشاكل لازم تنحل")
        for i, pr in enumerate(report["problems"], 1):
            L.append(f"{i}. {pr}")
        L.append("")
    L.append("## 1) الصفحات")
    L.append("")
    L.append("| # | من | إلى | الملف | الحجم | الحالة |")
    L.append("|---|---|---|---|---|---|")
    have = {pp["idx"]: pp for pp in report.get("page_rows", [])}
    for k in range(1, p["expected"] + 1):
        t0 = (k - 1) * (args.tiles_per_page / args.base_fps)
        t1 = min(report["duration"], k * (args.tiles_per_page / args.base_fps))
        pp = have.get(k)
        name = pp["name"] if pp else f"p{k:02d}_of_{p['expected']:02d}.jpg"
        size = f"{pp['size_kb']}KB" if pp else "—"
        if k in p["missing"]:
            status = "❌ ناقصة"
        elif pp and pp["size_kb"] * 1024 < args.min_page_bytes:
            status = "⚠️ صغيرة/مقطوعة"
        else:
            status = "✅"
        L.append(f"| {k} | {fmt(t0)} | {fmt(t1)} | {name} | {size} | {status} |")
    L.append("")
    if p["tiny"]:
        L.append(f"⚠️ صفحات صغيرة/مشكوكة: {'، '.join(p['tiny'])}")
        L.append("")
    L.append("## 2) الفراغات الزمنية (المقاطع يلي ما إلها صف)")
    L.append("")
    if cov.get("gap_count"):
        L.append("| من | إلى | المدة |")
        L.append("|---|---|---|")
        for a, b in cov["gaps"]:
            L.append(f"| {fmt(a)} | {fmt(b)} | {b-a:.1f} ث |")
    else:
        L.append("ما في فراغات — كل الثانية إلها صف مكتوب. ✅")
    L.append("")
    L.append("## 3) الأحداث غير المذكورة بالتفكيك")
    L.append("")
    unc = c.get("events_uncovered", {})
    if unc.get("count"):
        L.append(f"**{unc['count']}** حدث واقع برّا أي صف:")
        L.append("")
        for s in unc["sample"]:
            L.append(f"- {s}")
    else:
        L.append("كل حدث مغطّى بصف تفكيك. ✅")
    L.append("")
    L.append("## 4) كيف نستخدمه")
    L.append("")
    L.append("```bash")
    L.append(f"python3 tools/study_audit.py --study {study} --video-duration {report['duration']:.0f} --emit-ledger")
    L.append(f"python3 tools/study_audit.py --study {study} --video-duration {report['duration']:.0f} --verify   # لازم يطلع PASS")
    L.append("```")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

def _mk_fake_study(root: Path, duration=120.0, break_rows=None, pages=4, tiny_page=False,
                   event_at=90.0, break_end=None, no_events=False):
    if root.exists():
        shutil.rmtree(root)
    (root / "filmstrip2fps").mkdir(parents=True)
    (root / "motion").mkdir(parents=True)
    span = 30.0  # 60 tiles @2fps
    for k in range(1, pages + 1):
        f = root / "filmstrip2fps" / f"p{k:02d}_of_{math.ceil(duration/span):02d}.jpg"
        data = b"x" * (300 * 1024 if not (tiny_page and k == 2) else 1024)
        f.write_bytes(data)
    cuts = [{"t": 10.0, "score": 0.9}, {"t": event_at, "score": 0.7}]
    dossier = {"probe": {"duration": duration}, "cuts": cuts,
               "blacks": [{"t0": 40.0, "t1": 41.0}], "freezes": [], "silences": [{"t0": 60.0, "t1": 61.0}],
               "events": []}
    if no_events:
        (root / "motion" / "dossier.json").unlink(missing_ok=True)
    else:
        (root / "motion" / "dossier.json").write_text(json.dumps(dossier), encoding="utf-8")
    rows = break_rows if break_rows is not None else [("00:00.000", "01:00.000"), ("01:00.000", "02:00.000")]
    if break_end is not None:
        rows = [("00:00.000", break_end)]
    md = ["# تفكيك وهمي", "", "| الوقت | شو بيصير | القاعدة |", "|---|---|---|"]
    for a, b in rows:
        md.append(f"| {a}–{b} | شيء | قاعدة |")
    (root / "BREAKDOWN_AR.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return root


def selftest(args) -> int:
    root = Path("/home/user/build/motion_test/audit_selftest")
    ok = True
    print("[selftest 1] دراسة سليمة كاملة (المفروض PASS)")
    s = _mk_fake_study(root / "good", duration=120.0)
    r = audit(s, 120.0, argparse.Namespace(base_fps=2.0, tiles_per_page=60, breakdown=None,
                                           tolerance=0.75, max_gap=1.0, min_page_bytes=20480, verify=True))
    print("   verdict:", r["verdict"], "| problems:", len(r["problems"]))
    for p in r["problems"]:
        print("     -", p)
    ok &= r["verdict"] == "PASS"

    print("[selftest 2] تفكيك واقف عند 1:00 (بدو يكشف فراغ 60→120 + الحدث عند 90)")
    s = _mk_fake_study(root / "gap", duration=120.0, break_end="01:00.000")
    r = audit(s, 120.0, argparse.Namespace(base_fps=2.0, tiles_per_page=60, breakdown=None,
                                           tolerance=0.75, max_gap=1.0, min_page_bytes=20480, verify=True))
    print("   verdict:", r["verdict"], "| gaps:", r["checks"]["coverage"]["gap_count"],
          "| uncovered events:", r["checks"]["events_uncovered"]["count"])
    ok &= r["verdict"] == "FAIL" and r["checks"]["coverage"]["gap_count"] >= 1 \
        and r["checks"]["events_uncovered"]["count"] >= 1

    print("[selftest 3] صفحة فيلمستريب مقطوعة/صغيرة (بدو يكشفها)")
    s = _mk_fake_study(root / "tiny", duration=120.0, tiny_page=True)
    r = audit(s, 120.0, argparse.Namespace(base_fps=2.0, tiles_per_page=60, breakdown=None,
                                           tolerance=0.75, max_gap=1.0, min_page_bytes=20480, verify=True))
    print("   verdict:", r["verdict"], "| tiny:", r["checks"]["pages"]["tiny_count"])
    ok &= r["verdict"] == "FAIL" and r["checks"]["pages"]["tiny_count"] >= 1

    print("[selftest 4] صفحات ناقصة (4 من أصل 5)")
    s = _mk_fake_study(root / "short", duration=150.0, pages=4)
    r = audit(s, 150.0, argparse.Namespace(base_fps=2.0, tiles_per_page=60, breakdown=None,
                                           tolerance=0.75, max_gap=1.0, min_page_bytes=20480, verify=True))
    print("   verdict:", r["verdict"], "| found/expected:", r["checks"]["pages"]["found"], "/",
          r["checks"]["pages"]["expected"])
    ok &= r["verdict"] == "FAIL" and r["checks"]["pages"]["found"] < r["checks"]["pages"]["expected"]

    print("[selftest 5] دفتر التغطية ينكتب بدون أخطاء")
    s = root / "good"
    ns = argparse.Namespace(base_fps=2.0, tiles_per_page=60, breakdown=None,
                            tolerance=0.75, max_gap=1.0, min_page_bytes=20480, verify=True,
                            allow_missing_events=False)
    led = write_ledger(audit(s, 120.0, ns), s, ns)
    print("   ledger:", led, "exists:", led.exists(), "size:", led.stat().st_size)
    ok &= led.exists() and led.stat().st_size > 500

    print("[selftest 6] تغطية 100% بلا ملف أحداث (مختبر الحركة ما اشتغل)")
    s = _mk_fake_study(root / "noevents", duration=120.0, no_events=True)
    ns_strict = argparse.Namespace(base_fps=2.0, tiles_per_page=60, breakdown=None, tolerance=0.75,
                                   max_gap=1.0, min_page_bytes=20480, verify=True, allow_missing_events=False)
    ns_soft = argparse.Namespace(base_fps=2.0, tiles_per_page=60, breakdown=None, tolerance=0.75,
                                 max_gap=1.0, min_page_bytes=20480, verify=True, allow_missing_events=True)
    r_strict, r_soft = audit(s, 120.0, ns_strict), audit(s, 120.0, ns_soft)
    print("   strict:", r_strict["verdict"], "| soft:", r_soft["verdict"],
          "| warnings:", len(r_soft.get("warnings", [])))
    ok &= bool(r_strict["verdict"] == "FAIL" and r_soft["verdict"] == "PASS" and r_soft["warnings"])

    print("\n[selftest]", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="ضمانة تغطية كاملة لدراسة مرجع (لا لقطة/ثانية بدون تفكيك)")
    ap.add_argument("--study", help="مجلد الدراسة analysis/<video_id>")
    ap.add_argument("--video-duration", type=float, default=None, help="مدة الفيديو بالثواني")
    ap.add_argument("--base-fps", type=float, default=2.0)
    ap.add_argument("--tiles-per-page", type=int, default=60)
    ap.add_argument("--breakdown", default=None, help="مسار ملف التفكيك (افتراضي: study/BREAKDOWN_AR.md)")
    ap.add_argument("--tolerance", type=float, default=0.75, help="سماحية مطابقة الحدث مع الصف (ث)")
    ap.add_argument("--max-gap", type=float, default=1.0, help="أقصى فراغ زمني مسموح بين الصفوف (ث)")
    ap.add_argument("--min-page-bytes", type=int, default=20480)
    ap.add_argument("--verify", action="store_true", help="يفشل (exit 1) إذا في مشاكل")
    ap.add_argument("--allow-missing-events", action="store_true",
                    help="إذا الأحداث (dossier/metrics) غير متوفرة (مختبر الحركة ما اشتغل بعد) — تحذير بدل FAIL. "
                         "لا تستعمله إلا إذا ملف التفكيك مغطي 100% من الزمن.")
    ap.add_argument("--emit-ledger", action="store_true", help="يكتب COVERAGE.md")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest(args))
    if not args.study:
        ap.error("--study مطلوب (أو --selftest)")

    study = Path(args.study)
    if not study.is_dir():
        print(f"[x] ما في مجلد: {study}")
        sys.exit(2)

    duration = args.video_duration
    if duration is None:
        for cand in (study / "motion" / "dossier.json",):
            if cand.exists():
                duration = float(json.loads(cand.read_text())["probe"]["duration"])
                break
        if duration is None:
            metrics = study / "metrics.json"
            if metrics.exists():
                d = json.loads(metrics.read_text())
                duration = float(d.get("duration", 0) or 0) or None
    if not duration:
        ap.error("--video-duration مطلوب (ما قدرنا نستنتجه)")

    report = audit(study, duration, args)
    (study / "coverage_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.emit_ledger:
        led = write_ledger(report, study, args)
        print(f"[✓] دفتر التغطية: {led}")
    c = report["checks"]
    print(f"[i] صفحات: {c['pages']['found']}/{c['pages']['expected']} · أحداث: {c['events']['count']} · "
          f"صفوف التفكيك: {c['breakdown']['rows']} · فراغات: {c['coverage']['gap_count']} "
          f"({c['coverage']['gap_total_s']} ث)")
    for w in report.get("warnings", []):
        print("   ⚠️", w)
    for p in report["problems"]:
        print("   ❌", p)
    print(f"[{'✓' if report['verdict']=='PASS' else 'x'}] {report['verdict']}")
    sys.exit(0 if report["verdict"] == "PASS" or not args.verify else 1)


if __name__ == "__main__":
    main()
