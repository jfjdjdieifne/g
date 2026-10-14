#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
handoff.py — الهاند-أوف الحي (يُحدَّث بكل جولة، ما يعتمد على ذاكرة أي أحد)

الفكرة: كل جولة (turn) الأيجنت يحدّث `engine/HANDOFF_STATE.json` (قسم صغير يدوي)
ثم يشغّل هالأداة: بتفحص المستودع فعليًا (كروت البنك، الملفات، الـcommit)، وبتطلع
`HANDOFF.md` كامل بالعربي — فيضل عنا «أحدث هاند أوف» دائمًا، وأي أيجنت جديد بيفتح
المستودع بيعرف وين وصلنا بدون ما يرجع لذاكرة حدا.

الاستعمال:
  python3 tools/handoff.py            # توليد HANDOFF.md + طباعة الحالة
  python3 tools/handoff.py --check    # فحص فقط (هل الهاند-أوف متوافق مع الواقع/الـHEAD؟)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "engine" / "HANDOFF_STATE.json"
DB = ROOT / "engine" / "database" / "technique_db.json"
OUT = ROOT / "HANDOFF.md"


def sh(*args):
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def bank_stats():
    if not DB.exists():
        return {}
    db = json.loads(DB.read_text(encoding="utf-8"))
    cards = db.get("cards", [])
    by_ref, ready = {}, 0
    for c in cards:
        ref = (c.get("source") or [{}])[0].get("ref", "?")
        by_ref[ref] = by_ref.get(ref, 0) + 1
        if (c.get("engine") or {}).get("status") == "ready":
            ready += 1
    return {"total": len(cards), "by_ref": by_ref, "ready": ready,
            "with_why": sum(1 for c in cards if c.get("why")),
            "with_qc": sum(1 for c in cards if (c.get("engine") or {}).get("qc"))}


def check_state(state, stats):
    head = sh("git", "rev-parse", "--short", "HEAD")
    problems, warns = [], []
    hc = state.get("head_commit")
    if hc and head and hc != head:
        anc = subprocess.run(["git", "-C", str(ROOT.parent), "merge-base", "--is-ancestor", hc, head],
                             capture_output=True).returncode == 0
        if anc:
            warns.append(f"head_commit بالحالة ({hc}) أقدم من HEAD ({head}) — طبيعي: الحالة انكتبت قبل آخر كوميت، وبتصير مطابقة بالجولة الجاية.")
        else:
            warns.append(f"head_commit بالحالة ({hc}) مو بالسجل الحالي ({head}) — راجع الحالة.")
    dirty = subprocess.run(["git", "-C", str(ROOT.parent), "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        files = [l[3:].strip() for l in dirty.splitlines()]
        non_handoff = [f for f in files if not f.endswith("HANDOFF.md")]
        if non_handoff:
            warns.append("في تغييرات غير محفوظة بالمستودع — اكومِت قبل ما تعتمد الهاند-أوف: " + ", ".join(non_handoff[:4]))
    for st in state.get("studies", []):
        for f in st.get("deliverables", []):
            if not (ROOT / f).exists():
                warns.append(f"ملف مذكور بالدراسة {st.get('ref')} غير موجود: {f}")
    for a in state.get("artifacts", []):
        p = a.get("path")
        if p and not (ROOT / p).exists():
            warns.append(f"artifact بمسار غير موجود: {p}")
    if stats and stats.get("total") and "61" not in json.dumps(state.get("engine_state", {})):
        pass
    return head, problems, warns


def render(state, stats, head):
    L = []
    L.append("# HANDOFF — وين وصلنا (ملف حي، يتحدّث كل جولة)")
    L.append("")
    L.append(f"> **آخر تحديث:** {state.get('updated','?')} · **آخر كوميت محفوظ:** `{state.get('head_commit','?')}` "
             f"· **HEAD الحالي:** `{head or '?'}`")
    L.append("> هاد الملف مولّد بـ`tools/handoff.py` من `engine/HANDOFF_STATE.json` + فحص فعلي للمستودع.")
    L.append("> **القانون:** كل جولة = تحديث `HANDOFF_STATE.json` + تشغيل `handoff.py` + رفع `HANDOFF.md` عالدرايف. "
             "ما في شغل يعتمد على ذاكرة أي أحد.")
    L.append("")
    L.append("## 1) خريطة سريعة (فين شو)")
    L.append("")
    L.append("| الملف/المجلد | شو فيه |")
    L.append("|---|---|")
    for k, v in state.get("engine_state", {}).items():
        L.append(f"| `{k}` | {v} |")
    L.append("")
    L.append("## 2) حالة المراجع (الدراسة فريم-فريم)")
    L.append("")
    L.append("| المرجع | الحالة | التقدّم | ملفات |")
    L.append("|---|---|---|---|")
    for s in state.get("studies", []):
        icon = {"complete": "✅ كامل", "in_progress": "🟡 شغّال", "not_started": "⚪ لسا"}.get(s.get("status"), s.get("status"))
        files = " · ".join(f"`{Path(f).name}`" for f in s.get("deliverables", [])) or "—"
        L.append(f"| **{s.get('ref')}** — {s.get('name_ar','')} | {icon} | {s.get('progress','')} | {files} |")
    L.append("")
    if stats:
        L.append("## 3) بنك الأفكار (مفحوص آليًا من الملف)")
        L.append("")
        L.append(f"- **{stats['total']} كرت** — التوزيع: " +
                 " · ".join(f"{k}: {v}" for k, v in sorted(stats["by_ref"].items(), key=lambda kv: -kv[1])))
        L.append(f"- جاهز للتنفيذ فورًا: **{stats['ready']}** · كل كرت فيه شرح «ليش»: **{stats['with_why']}/{stats['total']}** "
                 f"· فيه فحوص QC: **{stats['with_qc']}/{stats['total']}**")
        L.append("")
    L.append("## 4) الملفات والروابط")
    L.append("")
    L.append("| الشي | المسار/الرابط |")
    L.append("|---|---|")
    for a in state.get("artifacts", []):
        did = a.get("drive_id")
        if not did:
            link = "_(محلي — ما بعدُ رُفع)_"
        elif a.get("kind") == "folder":
            link = f"[فولدر درايف](https://drive.google.com/drive/folders/{did})"
        else:
            link = f"[درايف](https://drive.google.com/file/d/{did}/view)"
        path = f"`{a['path']}`" if a.get("path") else ""
        L.append(f"| {a.get('name')} | {path} {link} |")
    L.append("")
    L.append("## 5) الخطوات الجاية (بالترتيب)")
    L.append("")
    for i, s in enumerate(state.get("next_steps", []), 1):
        L.append(f"{i}. {s}")
    L.append("")
    if state.get("open_questions"):
        L.append("## 6) أسئلة معلّقة (بتنتظر قرار)")
        L.append("")
        for q in state["open_questions"]:
            L.append(f"- {q}")
        L.append("")
    L.append("## 7) قوانين ثابتة (ما تتغيّر بين الجولات)")
    L.append("")
    for r in state.get("laws", []):
        L.append(f"- {r}")
    L.append("")
    env = state.get("environment", {})
    if env:
        L.append("## 8) البيئة (بعد أي ريست)")
        L.append("")
        L.append(f"- {env.get('note','')}")
        for c in env.get("rebuild_cmds", []):
            L.append(f"- `{c}`")
        L.append("")
    L.append("## 9) كيف تكمّل من هون (لأي أيجنت جديد)")
    L.append("")
    L.append("1. اقرأ `engine/AGENT_BRIEF.md` (دليل التشغيل) + هالملف.")
    L.append("2. راجع `engine/reference_lab/` (التفكيكات + Rulebook v1.2 + TRANSITION_ATLAS).")
    L.append("3. شغّل `python3 tools/handoff.py --check` للتأكد إنه ما في شي مفقود.")
    L.append("4. كمّل من أول بند بالقسم 5، وبعد أي خطوة: حدّث `HANDOFF_STATE.json` وأعد التوليد.")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="الهاند-أوف الحي")
    ap.add_argument("--check", action="store_true", help="فحص فقط بدون كتابة")
    a = ap.parse_args()
    if not STATE.exists():
        raise SystemExit(f"ما في ملف حالة: {STATE}")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    stats = bank_stats()
    head, problems, warns = check_state(state, stats)
    for w in warns:
        print("⚠️ ", w)
    if a.check:
        print(f"[{'✓' if not warns and not problems else 'i'}] فحص الهاند-أوف: "
              f"{len(state.get('studies', []))} مراجع · {stats.get('total', '?')} كرت · HEAD {head}")
        return 0
    if head:
        state["head_commit"] = head
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    md = render(state, stats, head)
    OUT.write_text(md, encoding="utf-8")
    print(f"[✓] كُتب {OUT.relative_to(ROOT)} — {len(md.splitlines())} سطر · "
          f"{len(state.get('studies', []))} مراجع · {stats.get('total', '?')} كرت")
    return 0


if __name__ == "__main__":
    sys.exit(main())
