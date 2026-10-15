#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
director.py — المخرج الآلي: سكربت → خطة فيديو كاملة (لقطة-بلقطة).

شو بيعمل بالضبط؟
  1) بيفهم السكربت: كل جملة = نبضة (beat). النية (intent) إما مكتوبة بالسكربت أو بتُستنتج
     من الكلمات (عربي/إنكليزي).
  2) بيعطي كل نبضة: **تقنية** (من بنك `technique_db.json` بدليلها)، **موشن** (اسم من معجم
     الحركة + بارامترات)، **صوت** (بد من `sound_bank.json` + SFX بالحدث)، و**استمرارية**
     (خيط بصري/كاميرا/صوتي/موتيف + انتقال داخلي أو قطع).
  3) بيجمّع **بلوكات**: إذا المشاهد بمنطقة وحدة ونفس المزاج → **لقطة وحدة** (one-shot) تتنتقل
     بين العناصر بحركة داخلية بدل القطع (match_cut_shape / zoom_through / morph_match …).
  4) **بيبتكر بحدود**: أي اختيار برّا البنك بينحسب «ابتكار» ولازم إله أساس (basis)، وميزانية
     الابتكار (افتراضي 25%) إذا فاتت → FAIL.
  5) بيطلّع: PLAN.md (عربي، للمالك) + plan.json (للتنفيذ) + engine_tasks.json (شو لازم يتبرمج
     بالمحرك حتى تنفّذ الخطة).

الفلسفة: **بلا عشوائية**. كل قرار محسوب بقاعدة وبدليل. الابتكار مسموح بس مقيّد ومبرَّر.

الاستخدام:
  python3 tools/director.py --script engine/database/scripts/escobar_intro.json --out analysis/director/escobar
  python3 tools/director.py --validate analysis/director/escobar/plan.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

from production_policy import display_errors, design_errors

ROOT = Path(__file__).resolve().parents[1]
TECH_DB = ROOT / "engine" / "database" / "technique_db.json"
SOUND_DB = ROOT / "engine" / "database" / "sound_bank.json"
VOCAB = ROOT / "11_MOTION_VOCABULARY.md"

# ---------------------------------------------------------------- النوايا

INTENT_ORDER = ["chapter", "hook", "date", "map", "character", "numbers", "product", "danger",
                "proof", "quote", "compare", "emphasis", "transition", "archive", "crowd",
                "comedy", "closer", "text", "mix", "color"]

KEYWORDS = {
    "date":       ["سنة", "عام", "في 19", "في 20", "year", "19", "20"],
    "numbers":    ["مليون", "مليار", "ألف", "كيلو", "طن", "دولار", "نسبة", "٪", "%", "أرقام", "عدد"],
    "map":        ["خريطة", "مدينة", "منطقة", "حدود", "شمال", "جنوب", "شرق", "غرب", "بلد", "كولومبيا", "ميديين", "map"],
    "character":  ["بابلو", "إسكوبار", "الرئيس", "الزعيم", "قائد", "مهرب", "المحقق", "الطيار", "أخوه", "اسمه", "يدعى"],
    "danger":     ["قتل", "قتال", "حرب", "موت", "مات", "خطر", "انفجار", "دم", "هدد", "سجن", "رصاص", "جثة"],
    "proof":      ["وثيقة", "تقرير", "محكمة", "قضية", "تسجيل", "تحقيق", "دليل", "مستند", "صورة"],
    "quote":      ["قال", "يقول", "تصريح", "اقتباس", "كلماته", "اعترف", "شهد"],
    "compare":    ["مقابل", "بينما", "قبله", "بعده", "توقعات", "واقع", "لكن", "بالعكس", "من جهة"],
    "emphasis":   ["أهم", "المفاجأة", "نقطة التحول", "الحقيقة", "المفتاح", "خصوصًا", "بالضبط"],
    "transition": ["ثم", "بعدها", "بعد ذلك", "انتقل", "غادر", "وصل", "لاحقًا", "بعد سنتين", "رجعت"],
    "archive":    ["أرشيف", "قديم", "الماضي", "تاريخي", "وثائقي", "شريط"],
    "crowd":      ["الناس", "الحشد", "الجمهور", "مظاهرة", "سكان", "مواطنين", "الشعب"],
    "product":    ["الكوكايين", "الشحنة", "الطائرة", "البضاعة", "السلاح", "الشاحنة", "المخدرات"],
    "chapter":    ["الفصل", "الجزء", "نبدأ", "نرجع", "نوقف هنا", "القصة تبدأ"],
    "closer":     ["النهاية", "انتهى", "خسر", "رحل", "بقي", "سقط", "هيك خلص"],
    "comedy":     ["مزحة", "سخرية", "طبعًا", "بالطبع"],
}

# نبضة النية → (موشن من المعجم، بارامترات، محرك مقترح)
MOTION_BY_INTENT = {
    "hook":       ("push_in_reveal",     {"zoom_pct": [10, 18], "dur_s": [1.4, 2.4]}, "story"),
    "date":       ("photo_fit_reveal",   {"dur_s": [0.6, 1.0]},                      "board"),
    "map":        ("map_descent",        {"dur_s": [1.6, 3.0]},                      "geo"),
    "character":  ("photo_fit_reveal",   {"then": "signature_trace"},                "board"),
    "numbers":    ("counter_countup",    {"ramp": "escalating", "dur_s": [1.2, 2.0]}, "story"),
    "product":    ("push_in_reveal",     {"zoom_pct": [8, 14]},                      "story"),
    "danger":     ("zoom_snap",          {"dur_s": [0.3, 0.45]},                     "docengine"),
    "proof":      ("callout_trace",      {"zoom_pct": [8, 18], "dur_s": [1.5, 3.0]}, "docengine"),
    "quote":      ("word_reveal_sync",   {"chunk_words": [2, 4]},                    "docengine"),
    "compare":    ("match_cut_shape",    {"panels": 2},                              "docengine"),
    "emphasis":   ("staggered_build",    {"dur_s": [0.8, 1.6]},                      "docengine"),
    "transition": ("whip_pan_bridge",    {"dur_s": [0.3, 0.5]},                      "docengine"),
    "archive":    ("parallax_depth",     {"layers": [2, 4], "amp_px": [6, 18]},      "docengine"),
    "crowd":      ("locked_off_tension", {"dur_s": [1.5, 3.0]},                      "story"),
    "comedy":     ("anticipation_release", {"beat_s": [0.6, 1.2]},                   "docengine"),
    "closer":     ("pull_back_context",  {"zoom_pct": [-14, -6]},                    "story"),
    "chapter":    ("locked_off_tension", {"dur_s": [2.0, 3.0], "then": "word_reveal_sync"}, "docengine"),
    "text":       ("word_reveal_sync",   {"chunk_words": [2, 4]},                    "docengine"),
    "color":      ("light_sweep_reveal", {"dur_s": [0.8, 1.4]},                      "board"),
    "mix":        ("mask_wipe",          {"dur_s": [0.4, 0.9]},                      "docengine"),
}

# المزاج المطلوب حسب النية (إذا السكربت ما حدّد mood للمشهد)
MOOD_BY_INTENT = {"hook": "cold_open", "date": "cold_open", "map": "tension_rise", "character": "dread",
                  "numbers": "scale_awe", "product": "greed_glow", "danger": "dread", "proof": "resolve",
                  "quote": "aftermath", "compare": "resolve", "emphasis": "tension_rise", "crowd": "dread",
                  "comedy": "aftermath", "closer": "aftermath", "chapter": "cold_open", "archive": "grief"}

# الانتقالات الداخلية (جوّا اللقطة الواحدة) والانتقالات بين البلوكات
IN_SHOT_TRANSITIONS = ["match_cut_shape", "zoom_through", "morph_match", "occlusion_reveal",
                       "parallax_depth", "whip_pan_bridge", "light_sweep_reveal"]
CUT_TRANSITIONS = ["smoke_wipe", "tool_cut_archive", "black_beat_inscene", "white_space_pause"]

INTENT_TO_TECH_INTENTS = {
    "hook": ["cold_open", "attention", "evidence"], "date": ["date", "chapter", "context"],
    "map": ["map", "spread", "label"], "character": ["character", "identity", "introduce"],
    "numbers": ["numbers", "scale", "growth"], "product": ["product", "scale", "impact"],
    "danger": ["danger", "threat", "icon"], "proof": ["proof", "document", "credibility"],
    "quote": ["quote", "text", "speech"], "compare": ["compare", "contrast", "explain"],
    "emphasis": ["emphasis", "explain"], "transition": ["scene_change", "cover_edit", "mood_shift"],
    "archive": ["archive", "past", "texture"], "crowd": ["crowd", "public", "scale"],
    "comedy": ["comedy", "beat"], "closer": ["ending", "close", "fade"],
    "chapter": ["chapter", "structure", "reset"], "text": ["text", "label"],
}
SFX_BY_INTENT = {"numbers": ["landing_thud"], "proof": ["paper_breath"], "character": ["pen_stroke"],
                 "danger": ["sub_boom"], "quote": ["type_key_single"], "map": ["swoosh_air"],
                 "transition": ["swoosh_air"], "chapter": [], "emphasis": ["felt_hit_soft"],
                 "comedy": [], "closer": ["shimmer_soft"], "archive": ["paper_breath"],
                 "hook": ["riser_tension"], "product": ["swoosh_air"], "date": ["type_key_single"],
                 "crowd": ["felt_hit_soft"], "compare": ["felt_hit_soft"]}

# ================================================== طبقة الفهم (ليش — مو حفظ)
# مرجع كل سبب: قوانين MONTAGE_THEORY.md (L1..L10). ما في قرار بلا سبب مكتوب.

UNDERSTANDING_KEYS = ["meaning", "role", "why_visual", "why_motion", "why_sound", "link_reason"]

# شو بتعطي الجملة (معلومة) و شو المفروض يحس المشاهد
READ_BY_INTENT = {
    "hook":      ("بتفتح الملف وتشد الانتباه — إعلان إنه في شي مهم جاي", "توجّه وانتظار"),
    "date":      ("بتثبّت الزمن — متى صار كل شي", "ترتيب بالرأس"),
    "map":       ("بتنقل المشاهد لمكان — العنوان الجغرافي للقصة", "توجّه وفضول"),
    "character": ("بتعرّف شخص — مين رح تتابع رحلته", "ألفة ومسؤولية"),
    "numbers":   ("بتعطي حجم/رقم — قياس لما صار", "صدمة محسوبة"),
    "product":   ("بتورّي الشي الأساسي بالقصة (المادة/الشحنة)", "خطورة مغرية"),
    "danger":    ("بتقول إنه في شي مهدّد/ممنوع/قاتل", "خوف مباشر"),
    "proof":     ("بتحضر دليل موثّق — على شو مبني الحكي", "ثقة واقتناع"),
    "quote":     ("بتحكي كلام حد — بصوتو (أو بالكتابة)", "قرب من الشخص"),
    "compare":   ("بتقارن حالتين — قبل/بعد، توقع/واقع", "مفارقة"),
    "emphasis":  ("بتشد على فكرة وتقف عليها", "اتنبه — هاد المهم"),
    "transition":("بتنقل المشاهد لمكان/زمان جديد", "استعداد للتغيير"),
    "archive":   ("بترجع بالزمن — مادة قديمة/أرشيف", "حنين أو رهبة تاريخية"),
    "crowd":     ("بتحكي عن الناس/العام", "وزن اجتماعي"),
    "comedy":    ("بترخي التوتر بنكتة أو مفارقة", "ارتخاء"),
    "closer":    ("بتقفل الفكرة (خاتمة/حكم)", "إحساس النهاية"),
    "chapter":   ("بتفتح فصل جديد — قسم بالحكاية", "استعداد إعادة تركيز"),
    "text":      ("بتوضّح كلمة/مصطلح/عنوان", "فهم فوري"),
    "color":     ("بتبدّل المزاج البصري", "تغيّر إحساس"),
}

# ليش هالحركة (منطق الحركة نفسها)
MOTION_WHY = {
    "push_in_reveal":   "الدفع من واسع لقريب بيخلي المشاهد يحس إنه هو اللي عم يكتشف — فيخلق رغبة «شوف أكتر» بلا كلام",
    "pull_back_context":"السحب لبرّا بيفتح الكادر على الصورة الكاملة، فبيقرا كحكم/قفلة — هاد مو حركة عادية، الحركة هي الإقفال",
    "map_descent":      "الهبوط من الكلي للجزئي (عالم → بلد → مدينة) بيتم ترتيب الجغرافيا بنفس ترتيب السؤال الطبيعي: وين؟ وين بالضبط؟",
    "counter_countup":  "العدّاد الصاعد بيسرّع مع الرقم فبيتحنّ الرقم لتجربة (إحساس نموّ/مرور وقت) — العين مستنية لحظة الاستقرار",
    "zoom_snap":        "الزوم المفاجئ حركة حاسمة بتخلي الدرس تنبّه — تناسب التحذير القصير، وبتاكل التفاصيل، فما تنفع لقطة غنية",
    "photo_fit_reveal": "الكشف بهدوء (تصغير + تثبيت) بيعمل الصورة «بطاقة» — يعني الشي الحقيقي يبان بينحترم، مو معروض عرض عادي",
    "signature_trace":  "خط القلم على الاسم هو توقيع الشخص بمعناها الحرفي: بتصير العين معه بيده على الورقة، فيصير التعريف ذكرى",
    "callout_trace":    "التتبّع بقلم/إطار بمشي على الوثيقة بنفس ترتيب قراءتنا، فبيصير عنا دور «محقق حي» بدل صورة جامدة",
    "word_reveal_sync": "ظهور الكلمات مع الإلقاء بيخلي سرعة القراءة = سرعة السماع، فالكلام يدخل الدماغ كأنه مسموع — وهاد يمنع «صفحة نصية»",
    "match_cut_shape":  "الشكل نفسه هو الجسر: العين بتكمل تتبع الشكل ما بين لقطتين، فما تحس إنه في قطع — المعنى بينتقل سلس",
    "staggered_build":  "الدخول بالتسلسل (عنصر بعد عنصر) بيبني الانتباه بالتدريج — بدل ما تعطي الشاشة كاملة مرة وحدة وتغرق",
    "whip_pan_bridge":  "الحركة السريعة عم بتتخطى المسافة، والعين بتقبلها كإشارة انتقال — أسرع طريقة للقطع مع بقاء الإحساس «سلسة»",
    "parallax_depth":   "الطبقات بمشي بسرعات مختلفة فبتخلق إحساس عمق 3D — بتحوّل أرشيف مسطّح لمساحة حيّة",
    "locked_off_tension":"الكادر الثابت بيقول «وقف فكر» — بترفع قيمة الكلام، وبأي حركة بعدها بتصير فرق واضح",
    "anticipation_release":"التمهيد ثم الإطلاق بيحكم التوتر: الجزء الأول بيبني التوقع والجزء الثاني بيفرجو — اليبتسم بدون مقدمة ما بحرّك حدا",
    "light_sweep_reveal":"الضو يالي بيمرق بيكشف العناصر بالتسلسل — تبديل حالة/مزاج بنفس المكان بلا ما نحس إننا غيّرنا مشهد",
    "mask_wipe":        "الستارة/المسك بتنقل المساحة قبل ما ينتبه المشاهد — بديل ناعم للقطع لما ما بدنا نحس بلحظة الخروج",
}

# ليش هالانتقال (بين العناصر جوّا اللقطة، أو قطع)
TRANSITION_WHY = {
    "match_cut_shape": "شكل من اللقطة الأولى = شكل بالثانية، فالعين بتكمل تتبعو وما بتحس بمفصل (L4)",
    "zoom_through":    "منفوت بعنصر (صفحة/ثقب) ومنطلع بمكان جديد — بيغيّر المقاس والمستوى بنفس الحركة (L4)",
    "morph_match":     "نفس المادة بتتحوّل (ورقة → خريطة/وجه → منشور): المعنى تغيّر والمادة وحدة، فبيحسها المشاهد تطور مو تبديل (L4)",
    "occlusion_reveal":"عنصر بيغطي الكادر وبنبدّل ورّا التغطية — أسرع تغيير مساحة بلا قطع مرئي (L4)",
    "parallax_depth":  "طبقات بتتحرك بسرعات مختلفة = إحساس عمق، فالعين بتصدّق إنه في مساحة 3D أصلًا (L4)",
    "whip_pan_bridge": "حركة سريعة بتعمل تصوير ضبابي؛ العين بتقبله كإشارة قطع مع إحساس سلس (L4/L5)",
    "light_sweep_reveal":"الضو بيكشف المساحة من جديد — بنفس المكان، حالة جديدة (L4)",
    "smoke_wipe":      "الدخان بيغطي ١٠٠% فبتنحذف اللحظة، والمشاهد الجديد بيبدأ نظيف — كمان بينفّذ تبديل مزاج/لون بدل القطع المباشر (L4)",
    "tool_cut_archive":"أداة فيزيائية بتقطع المادة بعين المشاهد: تعليق بصري + نكتة + توقيع قناة (L6)",
    "black_beat_inscene":"الأسود جوّا المشهد = نهاية جملة ونَفَس — بيفصل فكرتين بلا تغيير مكان (L5/L2)",
    "white_space_pause":"الفراغ (بلا صوت) بيعطي راحة للعين فبتقبل المشهد الجاي — الراحة جزء من الإيقاع مو ضياع وقت (L5/L3)",
    "chapter_black_silence":"أسود ٢–٢.٥ ث + صمت = فراغ قبل الكارت، وبلا هالفراغ الكارت بيبان حشو (L3/L5)",
}

# ليش هالمزاج (الانفعال يلي بدنا ياه هلق)
MOOD_WHY = {
    "cold_open":   "جو بارد بلا إيقاع واضح = ما في انفعال محدد بعد، فكل المزاجات الجاية بتبان تصعيد",
    "dread":       "خوف ثابت بينزل بشوي بشوي — الطبقة الافتراضية للمواضيع الخطرة (الخطر بيقعد بالخلفية)",
    "tension_rise":"التوتر بيصعد بدرجة معقولة — بتحضّر الانفجار بلا ما تحرقه",
    "peak_impact": "هون الانفجار: الشدة عالية والأوركسترا عاليا — لحظة ما بينفع تخافلها أرضية أهدى",
    "grief":       "الحزن بيوقف الجو: المشاهد بيرتاح يحسّ إنسانيًا — قيمة القصة البشرية",
    "resolve":     "الاستقرار بيقلب الدور: صرنا نحن نفهم أكتر من الشخص — إحساس الحسم",
    "scale_awe":   "الرهبة تنبني بالتدرج (وصول بطيء + تفاصيل آلات) — الأرقام بتحسّ حجم",
    "greed_glow":  "دفء باللون والموسيقى بيلفّ الغلطة بشي مغري — لهيك التحذير بيجي أقوى لما ينكشف",
    "pulse_drive": "الدفع بالنبض بيرفع السرعة مع الحركة — للمونتاج السريع بلا ما يضيع الانفعال",
    "aftermath":   "جو ما بعد الحدث: هدوء متعب محلول — بيعطي مكان للحكي والتفكير",
}

# ليش هالمؤثر (SFX) — دائمًا تحت الجو
SFX_WHY = {
    "whoosh_smoke_wipe":"ال swoosh بيوافق المسحة فبيخلي التبديل يتجسّد بالسمع مو بس بالصورة",
    "swoosh_air":      "الهوا بيرسم المسافة — يحس أننا انتقلنا/قطعنا خط",
    "landing_thud":    "ضربة ناعمة عند هبوط الرقم بتقفلو بإحساس فيزيائي — الرقم بيتذكّر",
    "paper_breath":    "نفس الورقة بيجيب إحساس ملمس الوثيقة — بترفع المصداقية بلا كلام",
    "pen_stroke":      "صوت القلم/الخط بيربطنا بيد الشخص — لحظة شخصية",
    "type_key_single": "طقّة واحدة تكتب التاريخ بمكانه — الزمن تثبّت بحركة",
    "riser_tension":   "الصاعدة بتنبّه: شي جاي — بتجهّز المشاهد للانفجار",
    "sub_boom":        "الضربة العميقة بتحسّها بالجسم مو بالأذن — وزن الحدث",
    "shimmer_soft":    "لمعة خفيفة بالإقفال بتعطي إحساس خلاص ناعم — ما بتزنّ",
    "clock_tick":      "دقّة ساعة بتقيس الوقت المحرّج — بتزيد الانتظار",
    "felt_hit_soft":   "ضربة مخملية بتميّز اللحظة بلا ما تنبّه إلى نفسها — المؤثر بتحسّه ولا تسمعه",
}


def story_role(frac: float) -> str:
    if frac < 0.25:
        return "فتحة — هون منبني الوعد وبنشد الانتباه"
    if frac >= 0.80:
        return "خاتمة/حكم — هون منوفّي الوعد وبنقفل اللغة نفسها"
    return "تطوير — هون منكبّر الفكرة ونضيّق الحلقة"


def understanding(intent, card, motion, mood, sfx, role, bed):
    info, feel = READ_BY_INTENT.get(intent, READ_BY_INTENT["text"])
    m = motion.replace("_hold", "")
    why_motion = MOTION_WHY.get(m, "حركة من المعجم — متبرّرة من نية الجملة (راجع 11_MOTION_VOCABULARY)")
    if motion.endswith("_hold"):
        why_motion += " · (_hold: تخفيف لكرمة التكرار — نفس الحركة بتفقد أثرها بالتكرار، فالـ_hold بيمنع الإحساس بالاستنساخ)"
    notes = (bed or {}).get("notes") or ""
    why_sound = f"المزاج {mood}: {notes}" if notes else f"المزاج {mood} حسب النية"
    if sfx and sfx[0] in SFX_WHY:
        why_sound += f" · المؤثر {sfx[0]}: {SFX_WHY[sfx[0]]} (تحت الجو −7dB، L3)"
    return {
        "meaning": f"الجملة {info} — المفروض يحس المشاهد: {feel}. (L1: فكرة وحدة بالنبضة)",
        "role": role,
        "why_visual": (card.get("why") if card else "") or f"بلا كرت بالبنك — محرك أصلي ({intent}): السبب مسجّل كابتكار مع أساسه (L9)",
        "why_motion": why_motion,
        "why_sound": why_sound,
        "link_reason": None,
    }


def link_reason(t, a, b):
    base = TRANSITION_WHY.get(t, f"انتقال {t}")
    th = b["continuity"]["threads"]
    if a["block"] == b["block"]:
        wire = f"نفس اللقطة `{a['block']}` بلا قطع: كاميرا {th['camera']} · موتيف {th['motif']} · لوحة {th['palette']}"
    else:
        mood_note = "المزاج متابع" if a["mood"] == b["mood"] else f"المزاج من {a['mood']} لـ {b['mood']} (كروس فيد)"
        wire = f"قطع مبرَّر بين لقطتين: {mood_note} · كاميرا {th['camera']} · لوحة {th['palette']}"
    return (f"طلعنا بـ {t}: {base} — {wire}",
            f"دخلنا بـ {t}: {base} — {wire}")



def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def vocab_names() -> set:
    if not VOCAB.exists():
        return set()
    txt = VOCAB.read_text(encoding="utf-8")
    return set(re.findall(r"`([a-z_]{4,})`", txt))


def infer_intents(text: str, explicit=None):
    if explicit:
        ex = [explicit] if isinstance(explicit, str) else list(explicit)
        # المتابعة بتكمّل
        ints = ex
    else:
        ints = []
    low = text.lower()
    for it in INTENT_ORDER:
        if it in ints:
            continue
        if any(k in low for k in KEYWORDS.get(it, [])):
            ints.append(it)
    if not ints:
        ints = ["text"]
    return ints


def est_dur(sentence: str, words_per_s: float = 2.4):
    w = len([x for x in re.split(r"\s+", sentence.strip()) if x])
    return max(1.2, w / words_per_s)


def pick_card(cards, intent, used, prev_card):
    ti = INTENT_TO_TECH_INTENTS.get(intent, ["emphasis"])
    best = None
    for c in cards:
        ci = c.get("intents", [])
        q = 0.0
        for i, t in enumerate(ti):
            if t in ci:
                q = max(q, 1.0 if i == 0 else (0.7 if i == 1 else 0.45))
        if q <= 0:
            continue
        s = 3.0 * q
        s += 0.6 if c["id"] != prev_card else -1.2
        s -= 0.7 * used.get(c["id"], 0)
        s += 0.3 if c.get("engine", {}).get("status") == "ready" else 0.0
        if best is None or s > best[0]:
            best = (s, c)
    return best[1] if best else None


def build_blocks(beats, max_beats=4, max_dur=18.0):
    """بلوك = لقطة وحدة: نبضات متتالية بنفس المشهد + نفس البلوك الخيوط."""
    blocks, cur = [], []
    for b in beats:
        same_scene = bool(cur) and cur[-1]["scene"] == b["scene"]
        cross_ok = (bool(cur) and not same_scene and cur[-1].get("scene_one_shot")
                    and b.get("scene_one_shot") and cur[-1]["mood"] == b["mood"])
        joined = (bool(cur) and (same_scene or cross_ok)
                  and b["intents"][0] not in ("chapter", "transition", "closer")
                  and not cur[-1].get("chapter_after"))
        dur = sum(x["dur"] for x in cur) + b["dur"]
        if cur and (not joined or len(cur) >= max_beats or dur > max_dur or b.get("force_cut")):
            blocks.append(cur); cur = []
        cur.append(b)
    if cur:
        blocks.append(cur)
    out = []
    for i, bs in enumerate(blocks, 1):
        for j, b in enumerate(bs):
            b["block"] = f"one_take_{i:02d}" if len(bs) > 1 else f"shot_{i:02d}"
            b["block_first"], b["block_last"] = (j == 0), (j == len(bs) - 1)
        out.append(bs)
    return out


def plan(script, tech, sound, voc, max_beats=4, max_dur=18.0):
    sp = script.get("style_profile", {}) or {}
    palette = sp.get("palette", "INK & ARCHIVE")
    pacing = sp.get("pacing_mode", "magnates")
    beats = []
    scenes = script.get("scenes")
    if not scenes:  # سكربت مسطّح
        scenes = [{"id": "s01", "mood": script.get("mood", "cold_open"),
                   "sentences": [{"text": s} for s in script.get("sentences", [])]}]
    for sc in scenes:
        for s in sc.get("sentences", []):
            if isinstance(s, str):
                s = {"text": s}
            txt = s["text"]
            ints = infer_intents(txt, s.get("intent"))
            mood = s.get("mood") or sc.get("mood") or MOOD_BY_INTENT.get(ints[0], "cold_open")
            beats.append({"scene": sc["id"], "text": txt, "intents": ints, "mood": mood,
                          "dur": s.get("dur") or est_dur(txt),
                          "one_shot_hint": bool(s.get("one_shot") or sc.get("one_shot")),
                          "scene_one_shot": bool(sc.get("one_shot") or s.get("one_shot")),
                          "force_cut": s.get("cut_before") is True})
    blocks = build_blocks(beats, max_beats=max_beats, max_dur=max_dur)
    used_cards, prev_card, prev_motion, prev_bed, cut_cycle, in_cycle = {}, None, None, None, 0, 0
    rows = []
    for bi, bs in enumerate(blocks, 1):
        for k, b in enumerate(bs):
            intent = b["intents"][0]
            card = pick_card(tech, intent, used_cards, prev_card)
            technique = {"card": card["id"], "source": card.get("source", [{}])[0].get("ref", "?"),
                         "at": ", ".join(s.get("at", "?") for s in card.get("source", []))} if card else None
            if card:
                used_cards[card["id"]] = used_cards.get(card["id"], 0) + 1
                prev_card = card["id"]
            mname, mparams, engine_hint = MOTION_BY_INTENT.get(intent, MOTION_BY_INTENT["text"])
            novelty, basis = [], []
            if not card:
                novelty.append("technique")
                basis.append(f"engine-native ({engine_hint})")
            if mname not in voc:
                novelty.append("motion")
                basis.append("11_MOTION_VOCABULARY")
            if mname == prev_motion and b["intents"][0] not in ("chapter",):
                mname += "_hold"  # ما نكرر نفس الحركة ورا بعض
            prev_motion = mname
            bed = sound["moods"].get(b["mood"], sound["moods"]["cold_open"])
            if prev_bed and prev_bed != b["mood"]:
                bed = dict(bed); bed["transition_in"] = "crossfade 0.6-1.2s"
            prev_bed = b["mood"]
            sfx = SFX_BY_INTENT.get(intent, [])
            pos_frac = (len(rows) + 0.5) / max(1, len(beats))
            und = understanding(intent, card, mname, b["mood"], sfx, story_role(pos_frac), bed)
            # الانتقالات تُحسب لاحقًا زوج-زوج (انتقال واحد بين كل جملتين)
            threads = {"palette": f"{palette} / {'red_lock' if intent in ('danger',) else 'base'}",
                       "camera": ("push_chain" if mname.startswith("push") else
                                  "pull_chain" if mname.startswith("pull") else "bridge"),
                       "motif": {"danger": "x_icon", "numbers": "counter", "map": "map",
                                 "archive": "tinted_archive", "proof": "document"}.get(intent, palette.split()[0].lower())}
            rows.append({
                "n": len(rows) + 1, "t": round(sum(r["dur"] for r in rows) + b["dur"] / 2, 1),
                "scene": b["scene"], "block": b["block"], "text": b["text"],
                "intents": b["intents"], "mood": b["mood"], "dur": round(b["dur"], 1),
                "technique": technique, "motion": {"name": mname, "params": mparams,
                                                   "in_vocab": mname.replace("_hold", "") in voc},
                "sound": {"bed": b["mood"], "bpm": bed.get("bpm"), "key": bed.get("key"),
                          "intensity": bed.get("intensity"), "sfx": sfx,
                          "sfx_gain_db_rel_bed": -7 if sfx else None},
                "understanding": und,
                "continuity": {"in": None, "out": None, "threads": threads},
                "engine": {"target": engine_hint, "status": engine_status(engine_hint, card)},
                "novelty": {"is_new": bool(novelty), "what": novelty, "basis": basis},
            })
    # انتقال واحد بين كل جملتين: داخل البلوك = حركة عنصرية (بلا قطع)، بين البلوكات = قطع مبرَّر
    ci, ii = 0, 0
    for i in range(len(rows) - 1):
        a, bnext = rows[i], rows[i + 1]
        if bnext["intents"][0] == "chapter" or a["intents"][0] == "chapter":
            t = "chapter_black_silence"
        elif a["block"] == bnext["block"]:
            t = IN_SHOT_TRANSITIONS[ii % len(IN_SHOT_TRANSITIONS)]; ii += 1
        else:
            t = CUT_TRANSITIONS[ci % len(CUT_TRANSITIONS)]; ci += 1
        a["continuity"]["out"] = t
        bnext["continuity"]["in"] = t
        a["understanding"]["link_reason"], bnext["understanding"]["link_reason"] = link_reason(t, a, bnext)
    explained = sum(1 for r in rows if r["understanding"]
                    and all(r["understanding"].get(k) for k in UNDERSTANDING_KEYS))
    total = sum(r["dur"] for r in rows) or 1
    n_new = sum(1 for r in rows if r["novelty"]["is_new"])
    shots = len(blocks)
    report = {
        "title": script.get("title", "untitled"), "style_profile": sp,
        "pacing_mode": pacing, "blocks": shots, "beats": len(rows), "rows": rows,
        "summary": {
            "total_s": round(total, 1),
            "blocks": shots,
            "avg_shot_s": round(total / shots, 1) if shots else 0,
            "pacing_target": {"magnates": [5.0, 9.0], "oversimplified": [2.0, 4.5]}.get(pacing, [3.0, 9.0]),
            "one_take_blocks": sum(1 for bs in blocks if len(bs) > 1),
            "multi_scene_one_shot": sum(1 for bs in blocks if len({b['scene'] for b in bs}) > 1),
            "novelty_beats": n_new, "novelty_pct": round(100 * n_new / max(1, len(rows)), 1),
            "explained": f"{explained}/{len(rows)}",
            "hard_cuts": shots - 1, "in_shot_transitions": sum(len(bs) - 1 for bs in blocks if len(bs) > 1),
        },
    }
    policy = load_json(ROOT / "engine/PRODUCTION_POLICY.json")
    report["production_policy"] = policy
    report["display_manifest"] = script.get("display_manifest")
    report["render_ready"] = (bool(report["display_manifest"])
                              and not display_errors(report["display_manifest"])
                              and not design_errors(report["display_manifest"].get("design", {"unit_of_design":"scene"})))
    # Narrative text may stay Arabic internally. It is never a fallback caption.
    report["display_note"] = "Use the English display manifest; never render rows[].text as an implicit caption."
    return report


def engine_status(hint, card):
    if card and card.get("engine", {}).get("status") == "ready":
        return "ready"
    return {"board": "live", "geo": "live", "story": "live", "docengine": "partial"}.get(hint, "concept")


def validate(report, novelty_budget=0.25):
    problems, warns = [], []
    rows = report["rows"]
    if report.get("display_manifest") is not None:
        problems.extend(display_errors(report["display_manifest"]))
        if "design" in report["display_manifest"]:
            problems.extend(design_errors(report["display_manifest"]["design"]))
    else:
        warns.append("English display manifest missing: planning only, NOT render-ready; do not use narrative text as captions.")
    seen_cut_repeat = []
    for r in rows[:-1]:
        if not r["continuity"]["out"]:
            problems.append(f"[{r['n']}] ما في انتقال خارج")
    for i in range(len(rows) - 1):
        if rows[i]["continuity"]["out"] != rows[i + 1]["continuity"]["in"]:
            problems.append(f"[{rows[i]['n']}→{rows[i+1]['n']}] عدم تطابق الانتقال (out≠in)")
    for r in rows:
        if not r["technique"]:
            problems.append(f"[{r['n']}] ما في تقنية")
        s = r["sound"]
        if not s.get("bed") or not s.get("bpm"):
            problems.append(f"[{r['n']}] ما في موسيقى (بد/سرعة)")
        if s.get("sfx") and s.get("sfx_gain_db_rel_bed", 0) > -5:
            problems.append(f"[{r['n']}] SFX فوق الجو (gain {s.get('sfx_gain_db_rel_bed')}dB)")
        if r["novelty"]["is_new"] and not r["novelty"]["basis"]:
            problems.append(f"[{r['n']}] ابتكار بلا أساس (basis مفقود)")
        if not r["motion"]["in_vocab"] and "motion" not in r["novelty"]["what"]:
            problems.append(f"[{r['n']}] موشن مو بالمعجم وما مو مسجّل كابتكار (in_vocab=False)")
    # عقد الفهم: ما في قرار بلا سبب مكتوب
    missing_all = [r["n"] for r in rows if not r.get("understanding")]
    if missing_all and len(missing_all) == len(rows):
        warns.append("الخطة بلا طبقة فهم (نسخة قديمة) — أعد التوليد لتطلع أسباب كل قرار")
    else:
        for r in rows:
            u = r.get("understanding") or {}
            for k in UNDERSTANDING_KEYS:
                if not u.get(k):
                    problems.append(f"[{r['n']}] قرار بلا فهم — السبب '{k}' مفقود")
    # نفس الانتقال belوك مرات كثير
    outs = [r["continuity"]["out"] for r in rows if r["continuity"]["out"]]
    for i in range(2, len(outs) + 1):
        if len(set(outs[i - 2:i])) == 1:
            seen_cut_repeat.append(i)
    if len(seen_cut_repeat) > len(rows) * 0.4:
        warns.append(f"في تكرار انتقالات: {len(seen_cut_repeat)} مرة نفس الانتقال مرتين ورا بعض")
    nov = report["summary"]["novelty_pct"] / 100.0
    if nov > novelty_budget:
        problems.append(f"ميزانية الابتكار انفاتت: {nov*100:.0f}% > {novelty_budget*100:.0f}%")
    lo, hi = report["summary"]["pacing_target"]
    if not (lo * 0.6 <= report["summary"]["avg_shot_s"] <= hi * 1.6):
        warns.append(f"متوسط اللقطة {report['summary']['avg_shot_s']}ث برّا نطاق {lo}-{hi}ث (نمط {report['pacing_mode']})")
    return problems, warns


def write_outputs(report, outdir: Path, novelty_budget=0.25):
    problems, warns = validate(report, novelty_budget)
    report["validation"] = {"problems": problems, "warnings": warns,
                            "verdict": "PASS" if not problems else "FAIL"}
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "plan.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    # مهام المحرك: شو لازم يتبرمج حتى تنفّذ الخطة
    tasks = {}
    for r in report["rows"]:
        key = (r["engine"]["target"], r["motion"]["name"].replace("_hold", ""), r["technique"]["card"] if r["technique"] else "engine-native")
        d = tasks.setdefault(f"{key[0]}::{key[1]}::{key[2]}", {"target": key[0], "motion": key[1],
                             "technique": key[2], "status": r["engine"]["status"], "beats": []})
        d["beats"].append(r["n"])
    order = {"ready": 0, "live": 1, "partial": 2, "concept": 3}
    tl = sorted(tasks.values(), key=lambda d: (order.get(d["status"], 9), -len(d["beats"])))
    (outdir / "engine_tasks.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")

    S = report["summary"]
    L = [f"# خطة الفيديو — {report['title']}", "",
         f"> مولّدة بالمخرج الآلي (`tools/director.py`) — **بلا عشوائية**: كل قرار بقاعدة وبدليل.",
         f"> النمط: **{report['pacing_mode']}** · اللوحة: **{report['style_profile'].get('palette','-')}**", "",
         "## ملخص", "",
         f"- المدة التقديرية: **{S['total_s']}ث** · اللقطات (بلوكات): **{report['blocks']}** · النبضات: **{report['beats']}**",
         f"- متوسط اللقطة: **{S['avg_shot_s']}ث** (هدف {S['pacing_target'][0]}–{S['pacing_target'][1]}ث)",
         f"- بلوكات «لقطة وحدة»: **{S['one_take_blocks']}** (منها **{S['multi_scene_one_shot']}** بمشاهد متعددة داخل لقطة واحدة)",
         f"- انتقالات داخلية (بلا قطع): **{S['in_shot_transitions']}** · قطع: **{S['hard_cuts']}**",
         f"- ابتكار: **{S['novelty_beats']} نبضة ({S['novelty_pct']}%)** — كلها بأساس موجود",
         f"- فهم: **{S.get('explained', '-')}** نبضة مشروحة (معنى + سبب التقنية + سبب الحركة + سبب الصوت + سبب الوصل)", "",
         f"**الحكم: {'PASS ✅' if report['validation']['verdict']=='PASS' else 'FAIL ❌'}**"]
    for w in warns:
        L.append(f"- ⚠️ {w}")
    for p in problems:
        L.append(f"- ❌ {p}")
    L += ["", "## الخطة لقطة-بلقطة", "",
          "| # | ت | البلوك | الجملة | التقنية (المصدر) | الموشن | الموسيقى | SFX | يِدخل من | يِطلع لـ |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in report["rows"]:
        tech = f"{r['technique']['card']} ({r['technique']['source']}@{r['technique']['at']})" if r["technique"] else "engine-native"
        bed = f"{r['sound']['bed']} · {r['sound']['bpm'][0] if r['sound']['bpm'] else '-'}bpm · {r['sound']['key']}"
        sfx = ", ".join(r["sound"]["sfx"]) or "—"
        L.append(f"| {r['n']} | {r['t']}s | `{r['block']}` | {r['text'][:60]} | {tech} | `{r['motion']['name']}` | {bed} | {sfx} | "
                 f"{r['continuity']['in'] or '—'} | {r['continuity']['out'] or '—'} |")
    L += ["", "## مهام المحرك (شو لازم يتبرمج حتى تنفّذ)", "",
          "| المحرك | الموشن | التقنية | الحالة | نبضات |", "|---|---|---|---|---|"]
    for d in tl:
        L.append(f"| {d['target']} | `{d['motion']}` | {d['technique']} | {d['status']} | {len(d['beats'])} |")
    L += ["", "> ready/live = ينفّذ فورًا · partial = ناقصه أجزاء · concept = تصميم لازم يتحوّل كود أولًا.", "",
          "## 🧠 ليش هالقرار؟ — فهم كل نبضة (مو حفظ)", ""]
    for r in report["rows"]:
        u = r["understanding"]
        L += [f"### نبضة {r['n']} — «{r['text'][:90]}»",
              f"- **فهم الجملة:** {u['meaning']}",
              f"- **الدور بالفيلم:** {u['role']}",
              f"- **ليش هي التقنية:** {u['why_visual']}",
              f"- **ليش هي الحركة:** {u['why_motion']}",
              f"- **ليش هي الموسيقى/SFX:** {u['why_sound']}",
              f"- **سبب الوصل:** {u['link_reason']}", ""]
    L += ["", "> ready/live = ينفّذ فورًا · partial = ناقصه أجزاء · concept = تصميم لازم يتحوّل كود أولًا.", ""]
    (outdir / "PLAN.md").write_text("\n".join(L), encoding="utf-8")
    return problems, warns


def cmd_validate(path: Path, novelty_budget=0.25):
    report = load_json(path)
    problems, warns = validate(report, novelty_budget)
    for w in warns:
        print("   ⚠️", w)
    for p in problems:
        print("   ❌", p)
    print(f"[{'✓' if not problems else 'x'}] {'PASS' if not problems else 'FAIL'}")
    return 0 if not problems else 1


def main():
    ap = argparse.ArgumentParser(description="المخرج الآلي: سكربت → خطة فيديو كاملة")
    ap.add_argument("--script")
    ap.add_argument("--out", default="analysis/director/plan")
    ap.add_argument("--novelty-budget", type=float, default=0.25)
    ap.add_argument("--max-block-beats", type=int, default=4, help="أقصى نبضات داخل لقطة وحدة")
    ap.add_argument("--max-block-s", type=float, default=18.0, help="أقصى مدة للقطة الوحدة (ث)")
    ap.add_argument("--validate")
    a = ap.parse_args()
    if a.validate:
        sys.exit(cmd_validate(Path(a.validate), a.novelty_budget))
    if not a.script:
        ap.error("--script مطلوب (أو --validate plan.json)")
    script = load_json(Path(a.script))
    tech = load_json(TECH_DB)["cards"]
    sound = load_json(SOUND_DB)
    voc = vocab_names()
    report = plan(script, tech, sound, voc, a.max_block_beats, a.max_block_s)
    problems, warns = write_outputs(report, Path(a.out), a.novelty_budget)
    S = report["summary"]
    print(f"[i] {report['title']}: {report['beats']} نبضة · {report['blocks']} لقطة · متوسط {S['avg_shot_s']}ث · "
          f"لقطة وحدة {S['one_take_blocks']} (متعددة المشاهد {S['multi_scene_one_shot']}) · ابتكار {S['novelty_pct']}%")
    print(f"[i] فهم: {S.get('explained', '-')} نبضة مشروحة — ما في قرار بلا سبب")
    for w in warns:
        print("   ⚠️", w)
    for p in problems:
        print("   ❌", p)
    ok = not problems
    print(f"[{'✓' if ok else 'x'}] {'PASS' if ok else 'FAIL'} → {a.out}/PLAN.md + plan.json + engine_tasks.json")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
