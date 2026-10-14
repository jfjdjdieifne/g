#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transition_atlas.py — أطلس الانتقالات والترابط (محرك تعلّم، مو تحليل لمرة وحدة)

شو بيعمل:
  يقرا dossier.json لأي دراسة مرجع (انتاج reference_motion.py) وبيحسب **كيف** الفيديو
  بيربط المشاهد ببعضها — مو بس شو الحركة داخل اللقطة:
    1) منحنى الإيقاع: قطع/دقيقة لكل قسم (quintile) حتى نشوف وين بيسرع ووين بينفّس.
    2) تصنيف كل قطعة حسب سياق الحركة: قطع-بالحركة (إخفاء) / قطع-عالسكون (ترقيم) /
       قطع-خارج-الحركة / قطع-داخل-الحركة  — من طاقة الحركة قبل وبعد القطعة (0.5s buckets).
    3) نسبة «السلس» مقابل «الحاد»: soft_changes مقابل hard_cuts.
    4) ضربات الفصل: أسود × صمت (انتاج chapter_black_silence) وربطها بأقرب قطعة.
    5) عدّادات الانتقالات الناعمة الفعلية (soft changes) وموقعها النسبي.
  المخرجات: transition_atlas.json + TRANSITION_ATLAS.md (عربي، جداول + مصادر زمنية).

الاستعمال:
  python3 tools/transition_atlas.py --study analysis/WW2P1 --study analysis/WW2P2 --out engine/reference_lab
"""
import argparse
import json
import math
import statistics
from pathlib import Path


def load_dossier(p: Path):
    d = json.loads(p.read_text(encoding='utf-8'))
    probe = d.get('probe', {})
    dur = float(probe.get('duration') or d.get('params', {}).get('duration') or 0.0)
    return d, dur


def ts(x: float) -> str:
    m = int(x // 60)
    s = x - m * 60
    return f"{m}:{s:04.1f}"


def buckets_energy(d):
    out = []
    for b in d.get('motion_summary', []) or []:
        try:
            out.append((float(b['t0']), float(b['t1']), float(b.get('energy') or 0.0)))
        except Exception:
            continue
    return out


def energy_at(buckets, t):
    for t0, t1, e in buckets:
        if t0 <= t < t1:
            return e
    return None


def classify_cuts(d, buckets, win=1.2):
    cuts = [c['t'] for c in d.get('cuts', []) if isinstance(c, dict)]
    if not buckets:
        return [], None, None
    energies = [e for _, _, e in buckets]
    p40 = statistics.quantiles(energies, n=10)[3] if len(energies) > 10 else statistics.median(energies)
    p60 = statistics.quantiles(energies, n=10)[5] if len(energies) > 10 else statistics.median(energies)

    rows = []
    for t in cuts:
        pre = [e for t0, t1, e in buckets if t - win <= (t0 + t1) / 2 < t]
        post = [e for t0, t1, e in buckets if t <= (t0 + t1) / 2 < t + win]
        if not pre or not post:
            continue
        a = statistics.mean(pre)
        b = statistics.mean(post)
        if a >= p60 and b >= p60:
            kind = 'cut_in_motion'      # قطع بالحركة من الجهتين = إخفاء القطع
        elif a <= p40 and b <= p40:
            kind = 'cut_on_still'       # قطع على سكون = ترقيم/تأكيد
        elif a >= p60 > b:
            kind = 'cut_out_of_motion'  # كان يتحرك وسكت فجأة = توقيف مفاجئ
        elif a <= p40 < b:
            kind = 'cut_into_motion'    # ساكن ثم انفجار حركة = كشف
        else:
            kind = 'cut_mixed'
        rows.append({'t': round(t, 2), 'energy_pre': round(a, 3), 'energy_post': round(b, 3), 'kind': kind})
    return rows, round(p40, 3), round(p60, 3)


def chapter_beats(d, dur):
    blacks = [(float(b['t0']), float(b['t1'])) for b in d.get('blacks', []) if isinstance(b, dict)]
    sils = [(float(s['t0']), float(s['t1'])) for s in d.get('silences', []) if isinstance(s, dict)]

    def overlap(a0, a1, b0, b1):
        return max(0.0, min(a1, b1) - max(a0, b0))

    beats = []
    for (a0, a1) in blacks:
        dur_b = a1 - a0
        sil = sum(overlap(a0, a1, s0, s1) for s0, s1 in sils)
        beats.append({'t0': round(a0, 2), 't1': round(a1, 2), 'len_s': round(dur_b, 2),
                      'silence_s': round(sil, 2),
                      'silence_ratio': round(sil / dur_b, 2) if dur_b > 0 else 0.0,
                      'is_chapter': bool(dur_b >= 0.9 and (sil / dur_b if dur_b else 0) >= 0.25)})
    return beats


def quintiles(d, dur, cuts):
    qs = []
    n = 5
    for i in range(n):
        a, b = dur * i / n, dur * (i + 1) / n
        c = [t for t in cuts if a <= t < b]
        span = max(1e-6, b - a)
        qs.append({'from': round(a, 1), 'to': round(b, 1), 'cuts': len(c),
                   'cuts_per_min': round(len(c) / (span / 60.0), 1),
                   'avg_shot_s': round(span / max(1, len(c)), 1)})
    return qs


def analyze(study: Path):
    d, dur = load_dossier(study / 'dossier.json')
    if not dur:
        cut_times = [c['t'] for c in d.get('cuts', [])]
        dur = (max(cut_times) + 10) if cut_times else 0.0
    buckets = buckets_energy(d)
    cuts = [c['t'] for c in d.get('cuts', []) if isinstance(c, dict)]
    softs = [s['t'] for s in d.get('soft_changes', []) if isinstance(s, dict)]

    cut_rows, p40, p60 = classify_cuts(d, buckets)
    kinds = {}
    for r in cut_rows:
        kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
    total_trans = len(cuts) + len(softs)
    res = {
        'video_id': d.get('video_id') or study.name,
        'duration_s': round(dur, 1),
        'hard_cuts': len(cuts), 'soft_changes': len(softs),
        'cuts_per_min': round(len(cuts) / (dur / 60.0), 1) if dur else 0,
        'smooth_ratio_pct': round(100.0 * len(softs) / total_trans, 1) if total_trans else 0,
        'hard_ratio_pct': round(100.0 * len(cuts) / total_trans, 1) if total_trans else 0,
        'motion_thresholds': {'still_p40': p40, 'moving_p60': p60},
        'cut_context': kinds,
        'chapters': chapter_beats(d, dur),
        'rhythm_quintiles': quintiles(d, dur, cuts),
        'cut_rows': cut_rows,
    }
    return res


def md_report(results, out_md: Path):
    L = ["# TRANSITION ATLAS — أطلس الانتقالات والترابط (مقروء آليًا + مدقّق)", "",
         "> مولّد بـ`tools/transition_atlas.py` من dossiers مختبر الحركة (قياسات فعلية، مو انطباع).",
         "> الجواب المختصر: تعلّمنا **كيف** المشاهد ترتبط — مو بس شو الموشنات. هون الأرقام.", ""]

    for r in results:
        L += [f"## {r['video_id']} — {ts(r['duration_s'])} ({r['duration_s']}s)", ""]
        L += ["| القياس | القيمة |", "|---|---|",
              f"| قطع حاد | **{r['hard_cuts']}** ({r['cuts_per_min']}/دقيقة) |",
              f"| انتقالات ناعمة (بلا قطع) | **{r['soft_changes']}** |",
              f"| نسبة السلس ↔ الحاد | **{r['smooth_ratio_pct']}% سلس · {r['hard_ratio_pct']}% حاد** |", ""]
        cc = r['cut_context']
        if cc:
            tot = sum(cc.values())
            L += ["### تصنيف القطعات حسب سياق الحركة (كيف يُخفي القطع)", "",
                  "| النوع | العدد | % | المعنى |", "|---|---|---|---|"]
            meaning = {
                'cut_in_motion': "قطع والجهتين متحركتين → العين مشغولة بالحركة فما تحس بالقطع (إخفاء)",
                'cut_on_still': "قطع على سكون → يعمل «ترقيم»/تأكيد (مثل نقطة بآخر جملة)",
                'cut_out_of_motion': "كان يتحرك فسكت فجأة → توقيف/صدمة",
                'cut_into_motion': "ساكن ثم انفجار حركة → كشف/بداية فصل",
                'cut_mixed': "مختلط",
            }
            for k, v in sorted(cc.items(), key=lambda kv: -kv[1]):
                L.append(f"| `{k}` | {v} | {round(100.0*v/max(1,tot),1)}% | {meaning.get(k,'-')} |")
            L += ["", f"> عتبات الطاقة: سكون ≤ {r['motion_thresholds']['still_p40']} · حركة ≥ {r['motion_thresholds']['moving_p60']} (من p40/p60 لتوزيع الطاقة).", ""]
        if r['rhythm_quintiles']:
            L += ["### منحنى الإيقاع (5 أقسام متساوية)", "",
                  "| القسم | من–إلى | قطع | قطع/دقيقة | طول اللقطة الوسطي |", "|---|---|---|---|---|"]
            for q in r['rhythm_quintiles']:
                L.append(f"| {ts(q['from'])}–{ts(q['to'])} | {q['cuts']} | {q['cuts_per_min']} | {q['avg_shot_s']}ث |")
            L.append("")
        ch = r['chapters']
        if ch:
            L += [f"### ضربات الفصل: أسود × صمت ({len(ch)} حادثة أسود)", "",
                  "| # | الوقت | المدة | صمت داخلها | نسبة الصمت | فصل؟ |", "|---|---|---|---|---|---|"]
            for i, b in enumerate(ch, 1):
                L.append(f"| {i} | {ts(b['t0'])}–{ts(b['t1'])} | {b['len_s']}ث | {b['silence_s']}ث | {b['silence_ratio']} | "
                         f"{'✅' if b['is_chapter'] else '—'} |")
            chap = sum(1 for b in ch if b['is_chapter'])
            L += ["", f"**{chap} ضربة فصل مؤكدة** (أسود ≥0.9ث وصمت ≥25% منه) — هاد يلي بنسميه `chapter_black_silence`.", ""]
        L += ["### عيّنات موثّقة (قطع + سياقه)", ""]
        for row in r['cut_rows'][:12]:
            L.append(f"- {ts(row['t'])} — `{row['kind']}` (طاقة قبل {row['energy_pre']} / بعد {row['energy_post']})")
        L += ["", "---", ""]

    L += ["## الخلاصة (كيف منستعملها)", "",
          "1. **القطع مو كلها قطع**: نسبة معتبرة من الانتقالات ناعمة، والقطع الحاد بيتوزّع حسب سياق الحركة —",
          "   والمخرج عندنا (`director.py`) بيفرّق بين `in-shot transition` و`cut` وبيتحقق `out==in` لكل نبضة.",
          "2. **الترابط إله قياس**: منحنى الإيقاع + ضربات الفصل + سياق القطع = ملف هوية لكل فيلم،",
          "   ومنستخدمو لتحديد `pacing_mode` ولاختيار مكان الانتقال (لقطة وحدة أو قطع).",
          "3. **كل قاعدة فوق مربوطة بمصدر زمني** من الـbreakdown (نفس الفيديو) — راجع `BREAKDOWN_WW2P1.md` و`BREAKDOWN_WW2P2.md`.", ""]
    out_md.write_text("\n".join(L), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description="أطلس الانتقالات والترابط من dossiers مختبر الحركة")
    ap.add_argument('--study', action='append', required=True, help='مجلد دراسة فيه dossier.json (يتكرر)')
    ap.add_argument('--out', default='engine/reference_lab', help='مجلد المخرجات')
    a = ap.parse_args()
    results = []
    for s in a.study:
        p = Path(s)
        if not (p / 'dossier.json').exists():
            print(f"⚠️ تخطّي {s}: ما في dossier.json")
            continue
        r = analyze(p)
        results.append(r)
        print(f"[✓] {r['video_id']}: قطع {r['hard_cuts']} · ناعم {r['soft_changes']} · "
              f"سلس {r['smooth_ratio_pct']}% · فصل {sum(1 for b in r['chapters'] if b['is_chapter'])}")
    if not results:
        raise SystemExit("ما في دراسة صالحة")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'transition_atlas.json').write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding='utf-8')
    md_report(results, out / 'TRANSITION_ATLAS.md')
    print(f"→ {out}/TRANSITION_ATLAS.md + transition_atlas.json")


if __name__ == '__main__':
    main()
