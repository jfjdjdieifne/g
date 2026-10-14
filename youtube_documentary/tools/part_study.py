#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
part_study.py — منهج «أجزاء ثم ربط»: تحليل مرجع طويل على أجزاء، وبعدها دمج كامل.

ليش؟
  فيديو 57 دقيقة إذا انحلّل بمشغّل واحد: أي انقطاع (تصفير ساندبوكس، خطأ، أوقات طويلة)
  بيروح معه كل الشغل. التقسيم (١٠ دقايق/جزء) بيعطي: استئناف من أي جزء، مراجعة أسهل،
  وربط نهائي بمستر واحد (dossier + metrics + فيلمستريب + تفكيك) — والدقة محفوظة:
  القطع/الأسود/الصمت/القياسات كلها بتوقيت الفيديو الأصلي (المختبر بيزيح الأوقات لحاله)،
  وكل جزء بينحلّل بـ±هامش تداخل (overlap) حتى ما يضيع حدث عالحدود، وبالدمج بنحتفظ
  بس بالأحداث يلي جوّا «القلب» (core) تبع كل جزء.

الأوضاع:
  --plan     يطبع خطة الأجزاء (بدون تشغيل)
  --run      يشغّل مختبر الحركة على كل جزء (بدون فيلمستريب لكل جزء) — ويقدر يكمّل من وين وقف
  --merge    يدمج أجزاء المختبر → dossier + metrics + فيلمستريب ماستر + PARTS.md (+ يجمع التفكيك)
  --verify   يفحص كل جزء لحاله (study_audit --range) وبعدها الماستر — الحكم لازم PASS

أمثلة:
  python3 tools/part_study.py --video V.mp4 --video-id PAYPAL --out analysis/PAYPAL --plan
  python3 tools/part_study.py ... --run --merge      # التشغيل + الدمج
  python3 tools/part_study.py ... --verify
خيارات: --pages-per-part 20 (=١٠ دقايق @2fps/60تايل) · --overlap 1.0 · --from/--to
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference_motion as rm  # noqa: E402


def tc(t: float) -> str:
    m, s = divmod(max(0.0, t), 60)
    return f"{int(m):02d}:{s:05.2f}"


def plan_parts(duration: float, start: float, end: float, pages_per_part: int,
               base_fps: float = 2.0, tiles_per_page: int = 60):
    seg = pages_per_part * tiles_per_page / base_fps
    parts, a, k = [], start, 1
    while a < end - 1e-6:
        b = min(a + seg, end)
        parts.append((k, a, b))
        a, k = b, k + 1
    return parts


def pages_in(parts, base_fps=2.0, tiles_per_page=60):
    per_page = tiles_per_page / base_fps
    return sum(max(1, math.ceil((b - a) / per_page)) for _, a, b in parts)


def part_dir(out: Path, k: int) -> Path:
    return out / "parts" / f"p{k:02d}"


def run_part(video: Path, out: Path, vid: str, k: int, a: float, b: float,
             ov: float, args, duration: float) -> int:
    d = part_dir(out, k)
    (d / "motion").mkdir(parents=True, exist_ok=True)
    a2, b2 = max(0.0, a - ov), min(duration, b + ov)
    cmd = [sys.executable, str(HERE / "reference_motion.py"), str(video),
           "--video-id", f"{vid}_p{k:02d}", "--out", str(d),
           "--start", f"{a2:.3f}", "--end", f"{b2:.3f}",
           "--base-fps", str(args.base_fps), "--event-fps", str(args.event_fps),
           "--motion-hz", str(args.motion_hz), "--bucket", str(args.bucket),
           "--no-strips"]
    if args.no_clips:
        cmd.append("--no-clips")
    print(f"\n[جزء {k}] {tc(a)} → {tc(b)}  (مع هامش {ov:.1f}ث: {tc(a2)}→{tc(b2)})", flush=True)
    t0 = time.time()
    r = subprocess.run(cmd)
    print(f"[جزء {k}] خلص ب {time.time()-t0:.0f}ث (exit {r.returncode})", flush=True)
    return r.returncode


def merge(out: Path, parts, args, duration: float, video: Path):
    cuts, soft, blacks, freezes, sils, events, metrics = [], [], [], [], [], [], []
    per = []
    for k, a, b in parts:
        d = part_dir(out, k)
        dj_p = d / "dossier.json"
        if not dj_p.exists():
            print(f"[!] الجزء {k}: ما في dossier.json — تجاهلنا (شغّل --run)")
            continue
        dj = json.loads(dj_p.read_text(encoding="utf-8"))
        core = lambda t: (a - 1e-6) <= t < (b - 1e-6)          # القلب فقط
        cuts += [c for c in dj.get("cuts", []) if core(c["t"])]
        soft += [c for c in dj.get("soft_changes", []) if core(c["t"])]
        blacks += [x for x in dj.get("blacks", []) if core(x["t0"])]
        freezes += [x for x in dj.get("freezes", []) if core(x["t0"])]
        sils += [x for x in dj.get("silences", []) if core(x["t0"])]
        events += [e for e in dj.get("events", []) if core(float(e.get("t", e.get("t0", 0))))]
        mp = d / "motion" / "metrics_0.5s.json"
        nb = 0
        if mp.exists():
            for m in json.loads(mp.read_text(encoding="utf-8")):
                if core(m["t0"]):
                    metrics.append(m)
                    nb += 1
        per.append({"part": k, "t0": a, "t1": b, "cuts": sum(1 for c in dj.get("cuts", []) if core(c["t"])),
                    "soft": sum(1 for c in dj.get("soft_changes", []) if core(c["t"])),
                    "blacks": sum(1 for x in dj.get("blacks", []) if core(x["t0"])),
                    "silences": sum(1 for x in dj.get("silences", []) if core(x["t0"])),
                    "events": sum(1 for e in dj.get("events", []) if core(float(e.get("t", e.get("t0", 0))))),
                    "buckets": nb})
        print(f"[merge] جزء {k}: cuts={per[-1]['cuts']} soft={per[-1]['soft']} "
              f"blacks={per[-1]['blacks']} sil={per[-1]['silences']} buckets={nb}")

    counts = {"hard_cuts": len(cuts), "soft_changes": len(soft), "blacks": len(blacks),
              "freezes": len(freezes), "silences": len(sils), "events": len(events),
              "strip_pages": 0}
    probe = rm.probe(video)
    master = {"video_id": args.video_id, "source": str(video), "probe": probe,
              "params": {"cut_thresh": args.cut_thresh, "soft_thresh": args.soft_thresh,
                         "motion_hz": args.motion_hz, "bucket": args.bucket,
                         "event_fps": args.event_fps, "base_fps": args.base_fps,
                         "parted": True, "pages_per_part": args.pages_per_part,
                         "overlap_s": args.overlap},
              "counts": counts, "cuts": cuts, "soft_changes": soft, "blacks": blacks,
              "freezes": freezes, "silences": sils, "motion_summary": metrics,
              "events": events, "parts": per, "elapsed_s": None}
    out.mkdir(parents=True, exist_ok=True)
    (out / "dossier.json").write_text(json.dumps(master, ensure_ascii=False), encoding="utf-8")
    (out / "motion").mkdir(parents=True, exist_ok=True)
    (out / "motion" / "dossier.json").write_text(json.dumps(master, ensure_ascii=False), encoding="utf-8")
    (out / "motion" / "metrics_0.5s.json").write_text(
        json.dumps(metrics, ensure_ascii=False), encoding="utf-8")

    print(f"\n[merge] ماستر: cuts={len(cuts)} soft={len(soft)} blacks={len(blacks)} "
          f"freeze={len(freezes)} sil={len(sils)} events={len(events)} buckets={len(metrics)}")

    print("[merge] فيلمستريب ماستر @2fps ...", flush=True)
    t0 = time.time()
    made = rm.base_filmstrips(video, args.base_fps, out / "filmstrip2fps",
                              start=0.0, end=None)
    master["counts"]["strip_pages"] = made
    for p in (out / "dossier.json", out / "motion" / "dossier.json"):
        p.write_text(json.dumps(master, ensure_ascii=False), encoding="utf-8")
    print(f"[merge] صفحات: {made} ({time.time()-t0:.0f}ث)")

    # جمع تفكيك الأجزاء (إذا موجود) بمستر واحد
    parts_md, merged_bd = [], []
    for k, a, b in parts:
        bf = out / f"BREAKDOWN_p{k:02d}.md"
        if bf.exists():
            merged_bd.append(bf.read_text(encoding="utf-8").rstrip())
            parts_md.append(f"| {k} | {tc(a)}–{tc(b)} | ✅ | `BREAKDOWN_p{k:02d}.md` |")
        else:
            parts_md.append(f"| {k} | {tc(a)}–{tc(b)} | ⬜ لسا | `BREAKDOWN_p{k:02d}.md` |")
    if merged_bd:
        (out / "BREAKDOWN_AR.md").write_text("\n\n---\n\n".join(merged_bd) + "\n", encoding="utf-8")
        print(f"[merge] BREAKDOWN_AR.md = {len(merged_bd)} جزء مدمج")

    lines = [f"# خطة/حالة الأجزاء — {args.video_id}", "",
             f"- المدة: **{tc(probe['duration'])}** · {args.pages_per_part} صفحة/جزء "
             f"({args.pages_per_part*30/60:.0f} دقيقة) · تداخل {args.overlap:.1f} ث", "",
             "| # | المجال | التفكيك | الملف |", "|---|---|---|---|"]
    lines += parts_md
    lines += ["", "## أرقام كل جزء (بعد الدمج)", "",
              "| # | المجال | قطع | ناعم | أسود | صمت | أحداث مراجعة | buckets |", "|---|---|---|---|---|---|---|---|"]
    for p in per:
        lines.append(f"| {p['part']} | {tc(p['t0'])}–{tc(p['t1'])} | {p['cuts']} | {p['soft']} | "
                     f"{p['blacks']} | {p['silences']} | {p['events']} | {p['buckets']} |")
    lines += ["", f"**المجموع (ماستر):** {len(cuts)} قطعة · {len(blacks)} أسود · {len(sils)} صمت · "
                  f"{len(events)} حدث مراجعة · {made} صفحة فيلمستريب"]
    (out / "PARTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[merge] PARTS.md + dossier + metrics + filmstrip2fps → {out}")


def verify(out: Path, parts, args, duration: float):
    ok = True
    for k, a, b in parts:
        bf = out / f"BREAKDOWN_p{k:02d}.md"
        cmd = [sys.executable, str(HERE / "study_audit.py"), "--study", str(out),
               "--video-duration", f"{duration:.2f}", "--verify", "--range", f"{a:.1f}", f"{b:.1f}"]
        if bf.exists():
            cmd += ["--breakdown", str(bf)]
        print(f"\n[verify جزء {k}] {tc(a)}–{tc(b)}", flush=True)
        r = subprocess.run(cmd)
        ok &= (r.returncode == 0)
    print(f"\n[verify ماستر] كل المدة", flush=True)
    r = subprocess.run([sys.executable, str(HERE / "study_audit.py"), "--study", str(out),
                        "--video-duration", f"{duration:.2f}", "--verify"])
    ok &= (r.returncode == 0)
    print(f"\n[verify] {'PASS ✅' if ok else 'FAIL ❌'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="منهج الأجزاء ثم الربط لدراسة مرجع طويل")
    ap.add_argument("--video", required=True)
    ap.add_argument("--video-id", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages-per-part", type=int, default=20, help="20 صفحة = 10 دقايق @2fps")
    ap.add_argument("--overlap", type=float, default=1.0, help="هامش تداخل حول كل جزء (ث)")
    ap.add_argument("--from", dest="t_from", type=float, default=0.0)
    ap.add_argument("--to", dest="t_to", type=float, default=None)
    ap.add_argument("--base-fps", type=float, default=2.0)
    ap.add_argument("--event-fps", type=float, default=15.0)
    ap.add_argument("--motion-hz", type=float, default=8.0)
    ap.add_argument("--bucket", type=float, default=0.5)
    ap.add_argument("--cut-thresh", type=float, default=0.15)
    ap.add_argument("--soft-thresh", type=float, default=0.12)
    ap.add_argument("--no-clips", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if not (a.plan or a.run or a.merge or a.verify):
        a.plan = True

    video = Path(a.video)
    out = Path(a.out)
    info = rm.probe(video)
    vid = a.video_id or video.stem.split(" - ")[0]
    end = a.t_to or info["duration"]
    parts = plan_parts(info["duration"], a.t_from, end, a.pages_per_part, a.base_fps)

    if a.plan:
        print(f"[خطة] {video.name}: {tc(info['duration'])} · {len(parts)} جزء · "
              f"متوقع {pages_in(parts, a.base_fps)} صفحة فيلمستريب")
        for k, x, y in parts:
            print(f"  جزء {k}: {tc(x)} → {tc(y)}  ({y-x:.0f}ث)")
        out.mkdir(parents=True, exist_ok=True)
        (out / "PARTS_PLAN.json").write_text(json.dumps(
            {"video": str(video), "video_id": vid, "duration": info["duration"],
             "pages_per_part": a.pages_per_part, "overlap_s": a.overlap,
             "parts": [{"part": k, "t0": x, "t1": y} for k, x, y in parts]},
            ensure_ascii=False, indent=1), encoding="utf-8")

    if a.run:
        for k, x, y in parts:
            if (part_dir(out, k) / "dossier.json").exists():
                print(f"[جزء {k}] موجود من قبل — نطّناه (امسح المجلد إذا بدك تعيده)")
                continue
            if run_part(video, out, vid, k, x, y, a.overlap, a, info["duration"]) != 0:
                print(f"[!] الجزء {k} فشل — نوقف. أعد التشغيل ليكمل من هون.")
                sys.exit(2)

    if a.merge:
        merge(out, parts, a, info["duration"], video)

    if a.verify:
        sys.exit(verify(out, parts, a, info["duration"]) if a.run or a.merge or a.verify else 0)


if __name__ == "__main__":
    main()
