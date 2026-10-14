#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cocktail.py — خلّاط الأفكار: من بنك الكروت (technique_db) إلى خطة لقطة-بلقطة (كوكتيل).

ليش؟
  ما بدنا «قالب فيديو واحد». بدنا **كوكتيل**: لكل نبضة (beat) من السكربت منختار
  «مكوّن» (كرت فكرة) من أي مرجع — بشرط **تنوّع المصادر**: كل لقطة تفضّل مصدر مختلف
  عن اللقطة يلي قبلها (فكرة من فيديو ١، وبعدها من فيديو ٧…). هيك الفيديو النهائي
  ما بيطلع تقليد لحي، بيطلع «أسلوب خاص» مدموج.

الوظائف:
  --search INTENT        دوّر على مكوّنات بحسب النية (transition / danger / map / quote …)
  --cat CATEGORY         كل المكوّنات بمجال معيّن (transition, typography, sound …)
  --card ID              اعرض كرت كامل (مع المصدر والبارامترات والممنوعات)
  --plan --recipe FILE   ابنِ خطة كاملة: لكل نبضة → الكرت المختار + ليش + بارامترات
  --validate             فحص البنك: حقول ناقصة / مصدر مو مسجّل / QC فاضي / IDs مكررة
  --sources              توزيع المكوّنات عالمراجع

أمثلة:
  python3 tools/cocktail.py --search transition
  python3 tools/cocktail.py --plan --recipe engine/database/recipes/escobar_intro.json --out analysis/cocktail/escobar_intro
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "engine" / "database" / "technique_db.json"

# شو بتعني كل نبضة (role) من ناحية النوايا (intents)
ROLE_INTENTS = {
    "hook": ["cold_open", "attention", "evidence", "hook"],
    "date": ["date", "context", "chapter"],
    "threat": ["danger", "threat", "icon", "scale"],
    "character": ["character", "identity", "introduce", "state"],
    "map": ["map", "spread", "label", "growth"],
    "proof": ["proof", "document", "credibility"],
    "transition": ["scene_change", "cover_edit", "mood_shift", "archive"],
    "emphasis": ["emphasis", "icon", "explain"],
    "equation": ["equation", "metaphor", "explain"],
    "pause": ["pause", "breath", "reset", "impact"],
    "montage": ["acceleration", "burst", "scale", "pacing"],
    "archive": ["archive", "past", "texture"],
    "quote": ["quote", "text", "speech", "escalation"],
    "compare": ["compare", "contrast", "explain"],
    "chapter": ["chapter", "structure", "reset"],
    "text": ["text", "label", "emphasis"],
    "comedy": ["comedy", "beat", "breather"],
    "crowd": ["crowd", "public", "scale"],
    "closer": ["ending", "close", "fade"],
    "mix": ["sound", "mixing", "polish"],
    "color": ["palette", "color", "mood"],
    "product": ["product", "scale", "impact"],
    "numbers": ["numbers", "scale", "growth"],
}


def load_db(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    return d, d.get("cards", []), d.get("sources", {})


def matches(card, intents):
    return sorted(set(card.get("intents", [])) & set(intents))


def match_quality(card, intents):
    """الأولوية للنوايا المتقدّمة: idx0=1.0 · idx1=0.7 · else 0.45"""
    ci = card.get("intents", [])
    best = 0.0
    for i, it in enumerate(intents):
        if it in ci:
            best = max(best, 1.0 if i == 0 else (0.7 if i == 1 else 0.45))
    return best


def pick_for_beat(card_list, intents, used, prev_source, stats):
    """اختيار المكوّن: جودة التطابق أولًا، بعدها تنوّع/توازن المصادر، وأقل تكرار."""
    cands = []
    for c in card_list:
        m = matches(c, intents)
        if not m:
            continue
        csrc = c["source"][0]["ref"] if c.get("source") else "?"
        q = match_quality(c, intents)
        score = 3.5 * q                                        # جودة التطابق أولًا
        score += 0.9 if csrc != prev_source else 0.0           # التنوّع لقطة-بلقطة
        smax = max(stats.values()) if stats else 0
        score += 0.7 if stats.get(csrc, 0) < smax else 0.0     # توازن: المصدر المتأخّر ياخد فرصة
        score -= 0.8 * used.get(c["id"], 0)                    # كرر أقل
        score += 0.4 if (c.get("engine", {}).get("status") == "ready") else 0.0
        cands.append((score, c, m, csrc))
    cands.sort(key=lambda x: (-x[0], x[1]["id"]))
    return cands


def cmd_search(cards, intents, cat=None, limit=50):
    out = []
    for c in cards:
        if cat and c.get("cat") != cat:
            continue
        m = matches(c, intents) if intents else []
        if intents and not m:
            continue
        out.append((c, m))
    print(f"# لقينا {len(out)} مكوّن" + (f" · النية: {'/'.join(intents)}" if intents else "") +
          (f" · المجال: {cat}" if cat else ""))
    for c, m in out[:limit]:
        src = ", ".join(f"{s['ref']}@{s['at']}" for s in c.get("source", []))
        st = c.get("engine", {}).get("status", "?")
        print(f"- [{c['id']}] {c['name_ar']} ({c['cat']}, {st}) — {src}" + (f" · نية: {','.join(m)}" if m else ""))
    return out


def cmd_card(cards, cid):
    for c in cards:
        if c["id"] == cid:
            print(json.dumps(c, ensure_ascii=False, indent=1))
            return 0
    print(f"[x] ما في كرت بالمعرّف: {cid}")
    return 1


def cmd_sources(cards, sources):
    from collections import Counter
    cnt = Counter(c["source"][0]["ref"] for c in cards if c.get("source"))
    print("# توزيع المكوّنات عالمراجع")
    for ref, n in cnt.most_common():
        t = sources.get(ref, {}).get("title", "?")
        print(f"- {ref}: {n} مكوّن — {t}")
    st = Counter(c.get("engine", {}).get("status", "?") for c in cards)
    print(f"\n# الجاهزية للمحرك: " + " · ".join(f"{k}: {v}" for k, v in st.most_common()))
    ready = [c["id"] for c in cards if c.get("engine", {}).get("status") == "ready"]
    print(f"  ready ({len(ready)}): " + ", ".join(ready))
    return 0


def cmd_validate(path: Path):
    d, cards, sources = load_db(path)
    problems, ids = [], set()
    req = ["id", "name_ar", "cat", "intents", "how", "when", "params", "anti", "engine", "source"]
    for c in cards:
        for k in req:
            if not c.get(k):
                problems.append(f"[{c.get('id', '?')}] ناقص: {k}")
        if c["id"] in ids:
            problems.append(f"[{c['id']}] معرّف مكرر")
        ids.add(c["id"])
        for s in c.get("source", []):
            if s.get("ref") not in sources:
                problems.append(f"[{c['id']}] مصدر مو مسجّل: {s.get('ref')}")
        if not c.get("engine", {}).get("qc"):
            problems.append(f"[{c['id']}] ما في فحص QC")
        if not c.get("anti"):
            problems.append(f"[{c['id']}] ما في ممنوعات")
    print(f"[i] البنك: {len(cards)} كرت · {len(sources)} مراجع · مشاكل: {len(problems)}")
    for p in problems:
        print("   ❌", p)
    print(f"[{'✓' if not problems else 'x'}] {'PASS' if not problems else 'FAIL'}")
    return 0 if not problems else 1


def cmd_plan(db_path: Path, recipe_path: Path, outdir: Path):
    d, cards, sources = load_db(db_path)
    rec = json.loads(recipe_path.read_text(encoding="utf-8"))
    allowed = rec.get("sources_allowed") or list(sources.keys())
    pool = [c for c in cards if c.get("source") and c["source"][0]["ref"] in allowed]
    used, stats, prev_src, rows = {}, {}, None, []
    for i, beat in enumerate(rec.get("beats", []), 1):
        intents = beat.get("intents") or ROLE_INTENTS.get(beat.get("role", ""), [])
        cands = pick_for_beat(pool, intents, used, prev_src, stats)
        if not cands:
            rows.append({"n": i, "t": beat.get("t"), "role": beat.get("role"), "card": None,
                         "why": f"ما في مكوّن بنية: {'/'.join(intents)}"})
            print(f"[!] نبضة {i} ({beat.get('role')}): ما لقينا مكوّن لـ {'/'.join(intents)}")
            continue
        score, c, m, csrc = cands[0]
        used[c["id"]] = used.get(c["id"], 0) + 1
        stats[csrc] = stats.get(csrc, 0) + 1
        rows.append({"n": i, "t": beat.get("t"), "role": beat.get("role"), "note": beat.get("note"),
                     "card": c["id"], "name_ar": c["name_ar"], "cat": c["cat"],
                     "src": csrc, "src_at": ", ".join(f"{s['at']}" for s in c["source"]),
                     "why": f"نية مشتركة: {'/'.join(m)}" + (f" · مصدر مختلف عن اللي قبل" if csrc != prev_src else ""),
                     "params": c.get("params"), "anti": c.get("anti"),
                     "engine": c.get("engine", {}).get("status"),
                     "alts": [x[1]["id"] for x in cands[1:4]]})
        prev_src = csrc
    # تقرير التنوّع
    from collections import Counter
    dist = Counter(r["src"] for r in rows if r.get("src"))
    total = sum(dist.values()) or 1
    maxref, maxn = (dist.most_common(1)[0] if dist else ("-", 0))
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "plan.json").write_text(json.dumps(
        {"recipe": rec.get("title"), "db": str(db_path), "rows": rows,
         "source_distribution": dict(dist)}, ensure_ascii=False, indent=1), encoding="utf-8")
    L = [f"# خطة كوكتيل — {rec.get('title', recipe_path.stem)}", "",
         f"> المكوّنات من بنك `{db_path.name}` · المراجع المسموحة: {', '.join(allowed)}", "",
         "| # | الوقت | النبضة | المكوّن | من وين | ليش | حالة المحرك |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        if not r.get("card"):
            L.append(f"| {r['n']} | {r.get('t','')} | {r.get('role','')} | — | — | {r['why']} | — |")
            continue
        L.append(f"| {r['n']} | {r.get('t','')} | {r.get('role','')} | **{r['name_ar']}** `{r['card']}` | "
                 f"{r['src']}@{r['src_at']} | {r['why']} | {r['engine']} |")
    L += ["", "## توزيع المصادر (فحص الكوكتيل)", "",
          f"- عدد اللقطات: **{len([r for r in rows if r.get('card')])}**",
          f"- المصادر: " + " · ".join(f"**{k}**: {v}" for k, v in dist.items()),
          f"- أكبر مصدر: **{maxref}** ({maxn}/{total} = {100*maxn/total:.0f}%)",
          ("- ⚠️ تنبيه: مصدر واحد فوق 60% — قريب يصير «قالب» بدل كوكتيل" if maxn / total > 0.6
           else "- ✓ التنوّع سليم (ما في مصدر فوق 60%)"),
          "", "## تفاصيل كل لقطة", ""]
    for r in rows:
        if not r.get("card"):
            continue
        L += [f"### {r['n']}. {r.get('t','')} — {r['role']}: {r['name_ar']} (`{r['card']}`)",
              f"- **الوصف:** {rec.get('beats',[{}])[r['n']-1].get('note','')}",
              f"- **المصدر:** {r['src']}@{r['src_at']}",
              f"- **ليش هالاختيار:** {r['why']}",
              f"- **البارامترات:** `{json.dumps(r['params'], ensure_ascii=False)}`",
              f"- **ممنوعات:** {'؛ '.join(r['anti']) if r['anti'] else '—'}",
              f"- **بدائل جاهزة:** {', '.join(r['alts']) if r['alts'] else '—'}", ""]
    (outdir / "PLAN.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[✓] {outdir/'PLAN.md'} + plan.json — {len([r for r in rows if r.get('card')])} لقطة")
    print(f"    توزيع المصادر: {dict(dist)}" +
          (f" · ⚠️ {maxref} {100*maxn/total:.0f}%" if maxn / total > 0.6 else " · ✓ تنوّع سليم"))
    return 0


def main():
    ap = argparse.ArgumentParser(description="خلّاط الأفكار — كوكتيل من بنك المكوّنات")
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--search", nargs="+", help="نيات: transition danger map …")
    ap.add_argument("--cat", help="مجال: transition/typography/color/…")
    ap.add_argument("--card", help="اعرض كرت")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--recipe")
    ap.add_argument("--out", default="analysis/cocktail/plan")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--sources", action="store_true")
    a = ap.parse_args()
    db = Path(a.db)
    if not db.exists():
        sys.exit(f"[x] ما في بنك: {db}")
    d, cards, sources = load_db(db)

    if a.validate:
        sys.exit(cmd_validate(db))
    if a.sources:
        sys.exit(cmd_sources(cards, sources))
    if a.card:
        sys.exit(cmd_card(cards, a.card))
    if a.plan:
        if not a.recipe:
            sys.exit("--plan بدو --recipe")
        sys.exit(cmd_plan(db, Path(a.recipe), Path(a.out)))
    if a.search or a.cat:
        cmd_search(cards, a.search or [], a.cat)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
