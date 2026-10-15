# HANDOFF — وين وصلنا (ملف حي، يتحدّث كل جولة)

> **آخر تحديث:** 2026-10-15 · **آخر كوميت محفوظ:** `0aafe88` · **HEAD الحالي:** `0aafe88`
> هاد الملف مولّد بـ`tools/handoff.py` من `engine/HANDOFF_STATE.json` + فحص فعلي للمستودع.
> **القانون:** كل جولة = تحديث `HANDOFF_STATE.json` + تشغيل `handoff.py` + رفع `HANDOFF.md` عالدرايف. ما في شغل يعتمد على ذاكرة أي أحد.

## 1) خريطة سريعة (فين شو)

| الملف/المجلد | شو فيه |
|---|---|
| `technique_bank` | engine/database/technique_db.json (94 كرت: 43 ww2p1 + 33 ww2p2 + 18 vaping — كل كرت why + qc + مصدر فريمي) |
| `director` | tools/director.py (سكربت→PLAN.md+plan.json+engine_tasks.json، فحص --validate، طبقة فهم إلزامية) |
| `transition_atlas` | tools/transition_atlas.py → engine/reference_lab/TRANSITION_ATLAS.md (قياس الانتقالات والترابط) |
| `sound_bank` | engine/database/sound_bank.json (10 مزاج + 11 SFX + قوانين) |
| `continuity` | engine/CONTINUITY_MODEL.md (4 خيوط + لقطة وحدة + in-shot vs cut) |
| `montage_theory` | engine/MONTAGE_THEORY.md (10 قوانين فهم + منطق القرار) |
| `rulebook` | engine/reference_lab/DIRECTING_RULEBOOK_v1.3.md (29 قسم — آخرها إضافات P2) |
| `engine/runtime/xyz_scene.py + blender_xyz.py` | Runtime XYZ مشترك + backend Cycles جزئي؛ ملف إسكوبار profile إخراج، مو engine مستقل لكل فيلم. |
| `engine/runtime/photo_depth.py` | كاميرا XYZ مشتركة + صفحات وثائق وparallax للصور الأصلية؛2.5Dمصرّح عنه، مو غرفة سجن ولا إعادة بناء تاريخية مساحية. |

## 2) حالة المراجع (الدراسة فريم-فريم)

| المرجع | الحالة | التقدّم | ملفات |
|---|---|---|---|
| **vaping** — Juul: A Villain Origin Story (MagnatesMedia) | ✅ كامل | 27:27 كامل — 356 صف، تغطية 55/55 صفحة، audit PASS | `Vaping_BREAKDOWN_2fps_full_v2.md` · `Vaping_COVERAGE.md` · `Vaping_GAPFILL_2026-10-14.md` |
| **ww2p1** — WW2 — OverSimplified (Part 1) | ✅ كامل | 13:45 كامل — 28/28 صفحة، 46 قاعدة، audit PASS (228 صف · 0 فراغ) | `BREAKDOWN_WW2P1.md` · `DIRECTING_RULEBOOK_v1.2.md` |
| **ww2p2** — WW2 — OverSimplified (Part 2) | ✅ كامل | 15:34 كامل — 32/32 صفحة، 29 قاعدة (47–75)، audit PASS (221 صف · 761 حدث · 0 فراغ) | `BREAKDOWN_WW2P2.md` · `DIRECTING_RULEBOOK_v1.3.md` |

## 3) بنك الأفكار (مفحوص آليًا من الملف)

- **94 كرت** — التوزيع: ww2p1: 43 · ww2p2: 33 · vaping: 18
- جاهز للتنفيذ فورًا: **7** · كل كرت فيه شرح «ليش»: **94/94** · فيه فحوص QC: **94/94**

## 4) الملفات والروابط

| الشي | المسار/الرابط |
|---|---|
| AI Director Kit (فولدر) |  [فولدر درايف](https://drive.google.com/drive/folders/14HxMPs32AKd7V72wMOw2g9M60mvYdTl7) |
| BREAKDOWN_AR (فحص آلي) |  [درايف](https://drive.google.com/file/d/1Im39FaJKTWHblPecNtNhEJDZy-xULiB6/view) |
| BREAKDOWN_WW2P1 (كامل) | `engine/reference_lab/BREAKDOWN_WW2P1.md` [درايف](https://drive.google.com/file/d/1uhTrBNUzL2piNL5wqHk9P_KgkF2I9hpH/view) |
| BREAKDOWN_WW2P2 (كامل) | `engine/reference_lab/BREAKDOWN_WW2P2.md` [درايف](https://drive.google.com/file/d/1JjuXamqgqJpT5SFxEnV3HVmEghSQ_IIl/view) |
| DIRECTING_RULEBOOK_v1.2 | `engine/reference_lab/DIRECTING_RULEBOOK_v1.2.md` [درايف](https://drive.google.com/file/d/1Q5vN_-e-4ONq2u3fgZ6E5y5JP-9yCiIi/view) |
| DIRECTING_RULEBOOK_v1.3 | `engine/reference_lab/DIRECTING_RULEBOOK_v1.3.md` [درايف](https://drive.google.com/file/d/1qrDQhrjNE4t89VfJcT7yUnAo9VU8OXqK/view) |
| PayPal (فيديو — 722MB، أكبر من حد التنزيل) |  [درايف](https://drive.google.com/file/d/1y_stCNW5l9cvN-gUzNmfZW9zzkyt7Emt/view) |
| Ref Studies (فولدر) |  [فولدر درايف](https://drive.google.com/drive/folders/1hYHn40_IawAQkBO1u0zoFPU1h4-6KXYC) |
| TRANSITION_ATLAS (P1+P2) | `engine/reference_lab/TRANSITION_ATLAS.md` [درايف](https://drive.google.com/file/d/1Be1oLFDpVLQMbOtKQkBxblEjLAivZtUj/view) |
| Vaping (فيديو) |  [درايف](https://drive.google.com/file/d/117J6M88EstNWF6NOcHRm1fmfLmu5C0vh/view) |
| WW2 P1 (فيديو) |  [درايف](https://drive.google.com/file/d/10ZD7FJwSS9J5JSkbB2SQeDs_LwJ-FyCs/view) |
| WW2 P2 (فيديو) |  [درايف](https://drive.google.com/file/d/1NPzS-IOkUlEFHrWd392WY7KLQtvSFylj/view) |
| dossier_WW2P1 (قياسات) |  [درايف](https://drive.google.com/file/d/1-op46-a3uDSfIDQS7AoE9d6REyremzxv/view) |
| dossier_WW2P2 (قياسات) |  [درايف](https://drive.google.com/file/d/1SyF_0aG2Hh3axcti4e0ad6WPAt9s4aCa/view) |
| technique_db (94 كرت) | `engine/database/technique_db.json` [درايف](https://drive.google.com/file/d/1Z3LtcQqmrQndLX5YXr6_ADKUSyTo54Ig/view) |
| ديمو WW2-drive v1 (PLAN كوكتيل) | `engine/projects/ww2_demo/cocktail/PLAN.md` [درايف](https://drive.google.com/file/d/1dNWbTLO0FEAgzRw1heYcAwFevuSJWBpe/view) |
| ديمو WW2-drive v1 (فيديو — نسخة أولى) |  [درايف](https://drive.google.com/file/d/11Rn4XAqx0fAExu0X0c_6s3yIs3TFqJ0g/view) |
| ديمو WW2-drive v2 (فيديو) |  [درايف](https://drive.google.com/file/d/1K3eH_RDNoueB7T31CFBAFrRUEAEAIXPg/view) |
| فيلمستريب WW2 P1 (28 صفحة) |  [درايف](https://drive.google.com/file/d/1S5xae1ZNn-MBvDEAUNHRmOBhvb1DCxSS/view) |
| فيلمستريب WW2 P2 (32 صفحة) |  [درايف](https://drive.google.com/file/d/1UVPNR0fA54c_zwkPlwzttIFPoWW-CJzc/view) |
| ديمو WW2-drive v3 (اختبار خرائط غير معتمد) |  [درايف](https://drive.google.com/file/d/1NqNEXeZeNEZToXPue6BbZPecLguo9Dl9/view) |
| خطة اختبار تصميم v3 |  [درايف](https://drive.google.com/file/d/1_1Xlh8vRWggFuTUa9mDKNT26NOCRRAki/view) |
| ديمو WW2-drive v4 (عمق وإنكليزي) |  [درايف](https://drive.google.com/file/d/1xzUM0fyO2T7cyCBUeDlOkbVa4yALg6wq/view) |
| خطة اختبار عمق v4 |  [درايف](https://drive.google.com/file/d/1fSd6WDq6XpvEFzNITt3KAW4oKIxTp8g2/view) |
| سياسة الإنتاج العامة — English / Scene-first |  [درايف](https://drive.google.com/file/d/1eflzeVEYkokGL0dV3BYJMV-Dxr84XLg_/view) |
| Escobar Hook30 v1 REJECTED / voice-02 only approved | `engine/projects/escobar_hook30/delivery.json` [درايف](https://drive.google.com/file/d/1u5iEILmRSzMnIFsGxtDdP3ikXi8j7ufW/view) |
| Previous HANDOFF — archive acquisition only, historical | `HANDOFF.md` [درايف](https://drive.google.com/file/d/1ZqoJ_Ecquvg8agmi9HssjndMm801t4K7/view) |
| Escobar First30 English Revision2 — review cut, not user-approved | `engine/projects/escobar_hook30/revision2/delivery.json` [درايف](https://drive.google.com/file/d/1Wd71BUBgJlAdhXZtcg3f8oI6XbP6uthD/view) |
| Escobar Revision2 actual QC + source/use notes | `engine/projects/escobar_hook30/revision2/QC.md` [درايف](https://drive.google.com/file/d/1UI0miW9oYsDvPfZrPuspX8tYVjxN-gXG/view) |
| Previous HANDOFF — Revision2 delivery before user feedback | `HANDOFF.md` [درايف](https://drive.google.com/file/d/1eOJM4SSeG6Fu0vKyg64XHRVyX3WGMvco/view) |
| Global documentary material and idea policy | `engine/DOCUMENTARY_MATERIALS_AND_IDEAS.md` [درايف](https://drive.google.com/file/d/1HNLb7NPS1EzxyZyKL0PhAIzj-RY6EblF/view) |
| SUPERSEDED — narrow prison-centered draft, do not produce | `engine/projects/escobar_hook30/next_intro/DIRECTION.md` [درايف](https://drive.google.com/file/d/1NlhISYWHmjZDEj-r00eeQUzWgGaJ0WAs/view) |
| Previous HANDOFF — Revision2 feedback before broad opening correction | `HANDOFF.md` [درايف](https://drive.google.com/file/d/1u-M8W6Wc6DZRKZQOu5rFLpDw8l0SKuUC/view) |
| Escobar Expanded Intro Revision3 —63sEnglish, broad/spoiler-free, NOT user-approved | `engine/projects/escobar_intro3/delivery.json` [درايف](https://drive.google.com/file/d/1tL0x2TwY_DYyDOaucqdjEjhFMvdmvab6/view) |
| Escobar Intro3 — actual QC/source-use notes | `engine/projects/escobar_intro3/QC.md` [درايف](https://drive.google.com/file/d/1h0EIxKMduiv7XYPakSIy0JmFZzEIxHw2/view) |
| Escobar Intro3 — source/review packet, not publication clearance |  [درايف](https://drive.google.com/file/d/1r-_FIlhGSO4-_mgNsvj1d-sjgV8w-uzd/view) |

## المشروع النشط — الهوك الحالي

- **scope:** مقدمة إسكوبار: أول30ث المنجزة أساس مراجعة؛ المستخدم لا يريد30ث كسقف يضعف الأفكار. التخطيط يمكن يتوسع، لكن مدة جديدة أو أداء صوتي جديد أو باقي الوثائقي مو معتمدين تلقائياً.
- **status:** المستخدم حبّ تطوّر revision2 والثري دي واللقطات جداً؛ طلب تقوية الفكرة/السكربت والتنوع واستعمال السجن الحقيقي بدل هيمنة المجسّم. لا اعتماد شامل للنص أو النسخة ولا رندر جديد بهالجولة.
- **audio:** voice-02 معتمد 2026-10-15: بحسه شخص عم يحكيلي طبيعي حبيت موافق. canonical engine/projects/escobar_hook30/assets/narrator_approved.mp3؛ ممنوع إعادة توليد الأداء.
- **script:** engine/projects/escobar_hook30/SCRIPT_EN.md
- **archive:** Charlie Rose /12Nov1992، جزء من سؤال استعادي؛ صورة29.8–37.4 وصوت29.8–37.2 من المصدر الرسمي. لا نشرة حية ولا إزالة watermark. تحقق captions+ASR، لا سماع يدوي مُدّعى.
- **plan:** engine/projects/escobar_hook30/revision2/README.md
- **sources:** engine/projects/escobar_hook30/revision2/SOURCES_AND_RIGHTS.md
- **video_drive:** [درايف](https://drive.google.com/file/d/1Wd71BUBgJlAdhXZtcg3f8oI6XbP6uthD/view)
- **delivery:** engine/projects/escobar_hook30/revision2/delivery.json
- **qc:** engine/projects/escobar_hook30/revision2/QC.md
- **actual_qc:** النسخة المصححة:720فريم decode؛ شوهدت140عينة مشفّرة، كل0.5ث+بينية+حدود، وثلاث تفاصيل كاملة.26testsPASS،−16.43LUFS/−1.41dBTP. نموذج540p8fps ومكتب720p8fps→24fps/1080p، ليس native1080p24. لا سماع يدوي ولا شهادة احتراف آلية.
- **scope_reminder:** أول30ث فقط، لا بدء الباقي ولا المرجع التالي تلقائياً.
- **editorial_review:** engine/projects/escobar_hook30/revision2/editorial_review.json
- **preflight:** engine/projects/escobar_hook30/ARCHIVE_PREFLIGHT.json
- **user_clarification:** المستخدم ذكّر بالمراجع: خبر حقيقي عن الموضوع يقول جملة محددة، ثم يدخل الراوي مستلماً معناها. انتقاء الجملة/المقطع الحقيقي أولاً، مو أخبار للزينة أو سكتات جاهزة نملأها. تفكيك Juul الموجود يسجّل مقال/مذيع عند0:00–0:07؛ هذه إحالة لدراسة سابقة لا ادعاء إعادة مشاهدة/سماع الآن.
- **acquisition_run:** https://github.com/jfjdjdieifne/g/actions/runs/38732941054
- **global_user_instruction:** قبل أي تسليم ولكل فيديو: افهم وصفّن بكل مشهد وعاين الناتج بنفسك، أصلح الأخطاء الإخراجية الكبيرة قبل المراجعة. protocol engine/EDITORIAL_REVIEW_PROTOCOL.md؛ لا شهادة احتراف آلية.
- **acquisition_status:** completed_success; لا jobs معلّقة. blob4e7114018505ee78e1aedf93d38f007c6bd2b10b. الدليل المفصل يحفظ أربع عمليات استرجاع ناجحة؛ لا تستأنف old watchers.
- **archive_evidence:** engine/projects/escobar_hook30/archive_research/official_source_evidence.json
- **archive_research:** engine/projects/escobar_hook30/archive_research/SOURCE_REVIEW_2026-10-15.md
- **archive_candidate_handoff:** ...a prison of his own making. → This is Pablo Escobar's prison. He helped design it... لا ترتيب أخبار شكلي ولا سلايدات مكان الكلام.
- **revision_qc:** الفيديو المنجز ومراجعته محفوظان؛ وصّل المستخدم رأيه الإيجابي بالثري دي مع طلب تعديل السكربت/المادة. لا تعِد نفس المونولوج بلقطات أكثر.
- **legacy_rejection:** v1 فقط: engine/projects/escobar_hook30/editorial_review.json؛ production_blocked=true
- **handoff_drive:** [درايف](https://drive.google.com/file/d/1u-M8W6Wc6DZRKZQOu5rFLpDw8l0SKuUC/view)
- **review_notes_drive:** [درايف](https://drive.google.com/file/d/1UI0miW9oYsDvPfZrPuspX8tYVjxN-gXG/view)
- **next_direction:** engine/projects/escobar_hook30/next_intro/DIRECTION.md
- **user_feedback:** engine/projects/escobar_hook30/revision2/USER_FEEDBACK_2026-10-15.json
- **global_material_policy:** engine/DOCUMENTARY_MATERIALS_AND_IDEAS.md
- **new_source_work:** شوهدت مجدداً28عينة تقريبية0:00–13:30 في overview_contact_1 من تجميعةABC/CBS؛ مداخل ومبانٍ وداخلية فعلية كمراجع. العلامات موجودة: ليست ماستر نظيفاً مرخصاً. lead صورة غرفة/AP من بحث فقط، غير مكتسبة/مشاهدة. لا صحف أصلية جديدة بعد.
- **material_policy_tests:** 34 structural tests passed in5.532s; no new footage, generated image or film approval implied.
- **next_direction_drive:** [درايف](https://drive.google.com/file/d/1NlhISYWHmjZDEj-r00eeQUzWgGaJ0WAs/view)
- **global_material_policy_drive:** [درايف](https://drive.google.com/file/d/1HNLb7NPS1EzxyZyKL0PhAIzj-RY6EblF/view)

## 5) الخطوات الجاية (بالترتيب)

1. انتظر حكم المستخدم على Revision3الموسّع63.25ث. المطلوب عن إسكوبار عمومًا: ثروة/صورة شعبية/نفوذ وخوف، مو السجن أو الصفقة، وبلا كشف هروب أو مصير/نهايات. التنفيذ كان مأذونًا بلا سقف30ث، مو باقي الوثائقي. احفظ الأصل وRevision2.
2. PayPal: بدو ≤100MiB (تقسيم المستخدم لجزئين) أو جلسة سكانر — بعدها part_study + كروت
3. باقي المراجع (Crypto / Apple / AI / Saudi / Dubai) واحد واحد
4. بالنهاية: technique_db.md + الجرامر البصرية + خطة التنفيذ + 3 عروض ديمو 6–10 ث

## 6) أسئلة معلّقة (بتنتظر قرار)

- Revision3الجديد ليس معتمدًا من المستخدم. هويةvoice-02معتمدة سابقًا؛ النص/الأداء الجديدين مو معتمدين. فحص الصوت كانASRوقياسات، لا ادعاء استماع يدوي.
- تراخيص نشر الأرشيف/صور الطرف الثالث غير محسومة. حركة العمق2.5Dوفجوات الخلفية إعادة بناء، وليست حركة كاميرا تاريخية. صورة ميديين حديثة ومصرّح بذلك.

## 7) قوانين ثابتة (ما تتغيّر بين الجولات)

- صفر سكيب: كل ثانية وكل لقطة تُقرأ وتُفهم قبل التقدّم
- ما في صف يتكتب بلا فريم مشفوف (ref@timestamp) — ولا اختراع تحليل
- المشاهد مو منفصلة: 4 خيوط + in-shot transitions قبل أي قطع (مفحوص out==in)
- SFX تحت الجو (−7dB قياسيًا) · لا SFX على كل قطعة
- النص ≤6 كلمات، بلا زووم عدواني على نص >4 كلمات (≤10%)
- الخريطة: النقاط عالبَر + دقة جغرافية
- إخراج بالعربي الشامي، رسائل قصيرة (المستخدم على iPhone)
- بعد كل جولة: حدّث ENGINE/HANDOFF_STATE.json ثم شغّل tools/handoff.py → HANDOFF.md + ارفعه
- كل محتوى الفيديو إنكليزي فقط (نصوص + VO)؛ الشامي للتواصل والملاحظات الداخلية. هذا يلغي تعليمات العرض العربي السابقة.
- المشهد وحدة التصميم؛ لا انبثاق وصندوق افتراضي لكل جملة. لا تكفي texture/shadow/bounce لإثبات الاحتراف. اتجاه v3 معتمد ويعمم كسياسة لا قالب.
- قبل أي رندر جديد: engine/PRODUCTION_POLICY.json + tools/production_policy.py؛ المحركات القديمة ليست كلها مربوطة تلقائياً فلا تشغّلها دون البوابة.
- كل أطوال الفيديو: راوي إنكليزي بأسلوب يوتيوبر طبيعي، حكي وتفسير وأخذ وعطا، لا إنشاء وخطب محفوظة أو أسئلة درامية متكررة.
- تصحيح المستخدم الأخير: الافتتاحية عن إسكوبار بشكل أوسع، والسجن مو فرضيتها الأساسية؛ بلا حرق للهروب أو المصير أو نقاط الذروة. طولها مو محدود30ث، لكن مو تفويض لباقي الوثائقي.

## 8) البيئة (بعد أي ريست)

- السانسبوكس بينصفّر بين الجولات: /home/user/build وpip لا يبقون. المستودع (GitHub) + الدرايف هم الحفظ الحقيقي.
- `pip install -q --break-system-packages numpy pillow imageio-ffmpeg`
- `نزّل الفيديو من الدرايف → build/videos/`
- `python3 tools/reference_motion.py build/videos/X.mp4 --video-id ID --out build/analysis/ID`
- `هوك إسكوبار revision2: اقرأ engine/projects/escobar_hook30/revision2/README.md؛ bpy==4.2.23 + bootstrap_bpy_headless.py ثم stills → render-samples → finish → qa. لا ترندر من جديد لتعديل التوثيق فقط؛ الـMP4 النهائي محفوظ بالدرايف.`
- `Revision3: اقرأengine/projects/escobar_intro3/BRIEF.mdوQC.md؛ الصور/التسجيلات الجديدة محفوظة بالمستودع، الأرشيف الأصلي يُستعاد منCI38732941054أو حزمةالمصادر بالدرايف؛ tools/escobar_intro3.py prepare→audio→stills→finish. الـMP4المسلّم محفوظبالدرايف، لا تعِد الرندر لتغيير التوثيق فقط.`

## 9) كيف تكمّل من هون (لأي أيجنت جديد)

1. اقرأ `engine/AGENT_BRIEF.md` (دليل التشغيل) + هالملف.
2. راجع `engine/reference_lab/` (التفكيكات + Rulebook v1.2 + TRANSITION_ATLAS).
3. شغّل `python3 tools/handoff.py --check` للتأكد إنه ما في شي مفقود.
4. كمّل من أول بند بالقسم 5، وبعد أي خطوة: حدّث `HANDOFF_STATE.json` وأعد التوليد.
