# خطة كوكتيل — إسكوبار — ديمو اختبار Rulebook v1.3 (23 ث، بلا VO · كوكتيل 3 مراجع)

> المكوّنات من بنك `technique_db.json` · المراجع المسموحة: vaping, ww2p1, ww2p2

| # | الوقت | النبضة | المكوّن | من وين | ليش | حالة المحرك |
|---|---|---|---|---|---|---|
| 1 | 0:00 | chapter | **بطاقة الفصل بعد أسود وصمت** `chapter_black_silence` | vaping@rulebook 0:28-0:36, 11:59 | نية مشتركة: chapter/structure · مصدر مختلف عن اللي قبل | concept |
| 2 | 0:01.6 | map | **التسمية جوّا الخريطة** `map_inline_label` | ww2p1@1:17.5 | نية مشتركة: context/label/map · مصدر مختلف عن اللي قبل | ready |
| 3 | 0:03.4 | map | **خط الإمداد بينرسم** `supply_line_draw` | ww2p2@2:08.5 | نية مشتركة: emphasis/link/map/supply · مصدر مختلف عن اللي قبل | concept |
| 4 | 0:06.0 | map | **خريطة النقاط المنتشرة** `spreading_map_dots` | vaping@0:20-0:23, 0:24-0:28 | نية مشتركة: map · مصدر مختلف عن اللي قبل | ready |
| 5 | 0:08.4 | numbers | **العدّاد التصاعدي على أسود** `counter_escalate_black` | ww2p1@3:32.0, 3:32.5, 3:33.0, 3:44.0 | نية مشتركة: growth/numbers/scale · مصدر مختلف عن اللي قبل | concept |
| 6 | 0:11.0 | emphasis | **السهم المرسوم يعلن** `drawn_arrow_telegraph` | ww2p2@3:23, 7:41, 10:26 | نية مشتركة: emphasis · مصدر مختلف عن اللي قبل | concept |
| 7 | 0:13.0 | archive | **الأرشيف الملوّن بستايل الفيلم** `tinted_archive` | vaping@2:49-2:56, 7:44-7:45.5 | نية مشتركة: archive/texture · مصدر مختلف عن اللي قبل | ready |
| 8 | 0:15.6 | map | **أعلام كأختام تقدّم** `flag_stamp_advance` | ww2p2@11:11, 5:41 | نية مشتركة: control/flag/map/war · مصدر مختلف عن اللي قبل | concept |
| 9 | 0:17.6 | emphasis | **الختم الناسف (stamp)** `stamp_impact_card` | ww2p2@6:09, 8:51.5, 9:29 | نية مشتركة: comedy/stamp/verdict | concept |
| 10 | 0:19.2 | map | **العدّاد على الغرض** `counter_on_object` | vaping@4:14-4:17, 21:03 | نية مشتركة: scale · مصدر مختلف عن اللي قبل | ready |
| 11 | 0:21.4 | closer | **كارت النهاية الثابت** `end_card_static` | ww2p1@13:32.5, 13:44.5 | نية مشتركة: close/ending · مصدر مختلف عن اللي قبل | concept |

## توزيع المصادر (فحص الكوكتيل)

- عدد اللقطات: **11**
- المصادر: **vaping**: 4 · **ww2p1**: 3 · **ww2p2**: 4
- أكبر مصدر: **vaping** (4/11 = 36%)
- ✓ التنوّع سليم (ما في مصدر فوق 60%)

## تفاصيل كل لقطة

### 1. 0:00 — chapter: بطاقة الفصل بعد أسود وصمت (`chapter_black_silence`)
- **الوصف:** أسود + عنوان الجزء: كولومبيا، 1993
- **المصدر:** vaping@rulebook 0:28-0:36, 11:59
- **ليش هالاختيار:** نية مشتركة: chapter/structure · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"black_s": [2.0, 2.5], "silence": true}`
- **ممنوعات:** ما تستعملها كل دقيقة — بتفقد قيمتها
- **بدائل جاهزة:** chapter_question_card, date_card_number, empty_stage_intro

### 2. 0:01.6 — map: التسمية جوّا الخريطة (`map_inline_label`)
- **الوصف:** الخريطة تدخل + تسمية ميديين جوّاها
- **المصدر:** ww2p1@1:17.5
- **ليش هالاختيار:** نية مشتركة: context/label/map · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"anchor": "on_region", "fade_in_s": [0.3, 0.8]}`
- **ممنوعات:** لازم تضل عالبَرّ وضمن المنطقة (زي قانون النقاط)
- **بدائل جاهزة:** army_name_blocks, city_labels_slide, country_dialogue_labels

### 3. 0:03.4 — map: خط الإمداد بينرسم (`supply_line_draw`)
- **الوصف:** خط الإمداد ميديين → ميامي بينرسم
- **المصدر:** ww2p2@2:08.5
- **ليش هالاختيار:** نية مشتركة: emphasis/link/map/supply · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"draw_s": [2, 5], "color": "yellow", "width_px": [4, 8], "curve": "slight"}`
- **ممنوعات:** ما تستعمله أكثر من مرتين بنفس الفصل؛ ما تخليه يقطع التسميات؛ ما تستعمل لون مشغول بالخلفية
- **بدائل جاهزة:** overlay_link_persist, army_name_blocks, drawn_arrow_telegraph

### 4. 0:06.0 — map: خريطة النقاط المنتشرة (`spreading_map_dots`)
- **الوصف:** فيضان أحمر على منطقة العمليات
- **المصدر:** vaping@0:20-0:23, 0:24-0:28
- **ليش هالاختيار:** نية مشتركة: map · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"dot_pop_s": [0.15, 0.3], "on_land": true}`
- **ممنوعات:** النقاط لازم تضل عالبَرّ (land mask)؛ بلا نقاط بالسالب — خطأ بصري
- **بدائل جاهزة:** unit_block_crawl, city_labels_slide, country_dialogue_labels

### 5. 0:08.4 — numbers: العدّاد التصاعدي على أسود (`counter_escalate_black`)
- **الوصف:** العدّاد: 525 طن
- **المصدر:** ww2p1@3:32.0, 3:32.5, 3:33.0, 3:44.0
- **ليش هالاختيار:** نية مشتركة: growth/numbers/scale · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"values": 3, "hold_s": [0.7, 1.2], "font": "display_sans", "bg": "black"}`
- **ممنوعات:** ما تزيدش عن 3 قيم متتالية؛ ما تحطش شرح مع الرقم
- **بدائل جاهزة:** crowd_rows_counter, disposable_crowd, encirclement_boxes

### 6. 0:11.0 — emphasis: السهم المرسوم يعلن (`drawn_arrow_telegraph`)
- **الوصف:** العدّاد على أسود (الرقم الأصعب)
- **المصدر:** ww2p2@3:23, 7:41, 10:26
- **ليش هالاختيار:** نية مشتركة: emphasis · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"colors": {"white": "mobilise", "blue": "allied_attack", "red": "axis_threat"}, "grow_s": [2, 6], "width_px": [10, 26]}`
- **ممنوعات:** ما تخلي السهم يطلع من اليابسة أو يقطع البحر بزاوية غلط؛ ما تستعمل أكثر من سهمين بنفس اللقطة
- **بدائل جاهزة:** stamp_impact_card, word_quote_accumulate, red_danger_icon

### 7. 0:13.0 — archive: الأرشيف الملوّن بستايل الفيلم (`tinted_archive`)
- **الوصف:** صورة أرشيف حقيقية بتلوين الفيلم
- **المصدر:** vaping@2:49-2:56, 7:44-7:45.5
- **ليش هالاختيار:** نية مشتركة: archive/texture · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"tint": "teal|red", "motion": "slow_push"}`
- **ممنوعات:** بلا اهتزاز مبالغ — الأرشيف مسند لا بطل
- **بدائل جاهزة:** archive_block_caption, archive_with_cartoon_overlay, event_scene_minimal

### 8. 0:15.6 — map: أعلام كأختام تقدّم (`flag_stamp_advance`)
- **الوصف:** وحدات + أعلام سيطرة: الطرق قفلت
- **المصدر:** ww2p2@11:11, 5:41
- **ليش هالاختيار:** نية مشتركة: control/flag/map/war · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"stamps": [2, 4], "enter_s": [0.2, 0.5], "scale": "big", "opacity": [0.8, 1.0]}`
- **ممنوعات:** ما تستعمل أعلام كتير (زحمة)؛ ما تخلي العلم يغطي التسميات؛ ما تخلطه بأراوندل الوحدات الصغيرة
- **بدائل جاهزة:** army_name_blocks, city_labels_slide, comparison_result_card

### 9. 0:17.6 — emphasis: الختم الناسف (stamp) (`stamp_impact_card`)
- **الوصف:** الختم: 1993
- **المصدر:** ww2p2@6:09, 8:51.5, 9:29
- **ليش هالاختيار:** نية مشتركة: comedy/stamp/verdict
- **البارامترات:** `{"words_max": 3, "impact_s": [0.2, 0.5], "rotate_deg": [-8, 8], "sfx": "stamp"}`
- **ممنوعات:** ما تستعمله لكل جملة؛ ما تحط نص طويل عليه؛ ما تخليه يغطي وجه/معلومة مهمّة
- **بدائل جاهزة:** country_dialogue_labels, empty_bubble_silence, gag_beat_pause

### 10. 0:19.2 — map: العدّاد على الغرض (`counter_on_object`)
- **الوصف:** المقياس العالمي: كولومبيا ضمن أميركا
- **المصدر:** vaping@4:14-4:17, 21:03
- **ليش هالاختيار:** نية مشتركة: scale · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"ramp": "escalating", "digits_pad": true, "bg": "object"}`
- **ممنوعات:** بلا أرقام مبهمة — كل رقم بيعني شي
- **بدائل جاهزة:** empire_paint_wave, big_product_crosses, color_language

### 11. 0:21.4 — closer: كارت النهاية الثابت (`end_card_static`)
- **الوصف:** كارت التكلفة/الخاتمة + سكون
- **المصدر:** ww2p1@13:32.5, 13:44.5
- **ليش هالاختيار:** نية مشتركة: close/ending · مصدر مختلف عن اللي قبل
- **البارامترات:** `{"hold_s": [8, 15], "motion": "none", "music": "none", "last_silence_s": [0.6, 1.0]}`
- **ممنوعات:** ما تحط موسيقى أو حركة بالكارت؛ ما تطول أكتر من 15 ث
- **بدائل جاهزة:** color_drain_aftermath, cost_number_card, meta_self_reference

