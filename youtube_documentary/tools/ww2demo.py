#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ww2demo.py — ديمو اختبار Rulebook v1.3 (إسكوبار، نمط OverSimplified) — v2.

تعديلات v2 (حسب ملاحظات المستخدم):
 1) ما في «مربعات فاضية»: كل نص عربي بيرسم بمحرّك خطوط هجين (Noto Naskh + DejaVu)
    — أي رمز ناقص بالخط العربي بيتسحل من DejaVu تلقائيًا.
 2) التسميات/الشارات: chip واضح + خيط دلالة (leader) + دائرة هدف (reticle) — مو «مرسوم بالرسام».
 3) السهم: منحنى متقطّع بشعيرات (chevron) ورأس مُصمَّم — بدل الخط المستقيم + مثلث.
 4) الختم: ختم حبر بحواف خشنة + ظل + ارتداد (overshoot) + رجّة — مو مستطيل برتقالي.
 5) الخرائط: بحر متدرّج، حدود ملساء (رسم بـ2× ثم تصغير)، تمييز البلد المقصود، تعتيم الخلفية عند التركيز.
 6) كل النصوص عربية واضحة، واللاتيني بعرض ثانوي.

القرارات من: engine/projects/ww2_demo/cocktail/plan.json (كروت البنك: فيديو@توقيت).
"""
import json, math, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import imageio_ffmpeg

ROOT = Path('/home/user/g/youtube_documentary')
BUILD = Path('/home/user/build/ww2_demo')
FRAMES = BUILD / 'frames'
W, H, FPS, DUR = 1920, 1080, 24, 23.0
SS = 2                                   # رندر الخرائط بضعف الدقة ثم تصغير (حواف ملساء)

GEO_JSON = ROOT / 'assets_global/geo/latam_10m.json'
F_AR = str(ROOT / 'assets_global/fonts/NotoNaskhArabic-Regular.ttf')
F_ARB = str(ROOT / 'assets_global/fonts/NotoNaskhArabic-Bold.ttf')
F_LAT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

SEA_TOP = (14, 20, 38); SEA_BOT = (7, 10, 20)
LAND      = (46, 60, 96)
LAND_FOC  = (64, 84, 128)
EDGE      = (120, 141, 186)
EDGE_FOC  = (176, 196, 236)
RED       = (206, 58, 46)
RED_D     = (150, 38, 30)
GREEN     = (58, 152, 74)
YELLOW    = (240, 195, 62)
INK       = (245, 242, 234)
BLACK     = (8, 8, 11)
GREY      = (152, 158, 174)
AR_DIGITS = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')

# ------------------------------------------------------------------ خطوط هجينة
_cmaps, _fcache = {}, {}
def _cmap(path):
    if path not in _cmaps:
        from fontTools.ttLib import TTFont
        _cmaps[path] = set(TTFont(path).getBestCmap().keys()) if Path(path).exists() else set()
    return _cmaps[path]

def _font(path, size):
    key = (path, size)
    if key not in _fcache:
        _fcache[key] = ImageFont.truetype(path, size)
    return _fcache[key]

def runs(text, size, arabic=True, bold=False):
    """يرجّع [(char, font)] مع تشكيل عربي + bidi واحتياطي لأي رمز ناقص."""
    s = get_display(arabic_reshaper.reshape(text)) if arabic else text
    main = F_ARB if bold else F_AR
    cm = _cmap(main)
    out = []
    for ch in s:
        if ord(ch) == 32 or ord(ch) in cm:
            out.append((ch, _font(main, size)))
        else:
            out.append((ch, _font(F_LAT, int(size * 0.92))))
    return out

def runs_w(rs):
    return sum(f.getlength(ch) for ch, f in rs)

def draw_runs(d, xy, rs, fill, anchor='la', halo=0, halo_fill=(0, 0, 0)):
    tw = runs_w(rs)
    x, y = xy
    if anchor[0] == 'm':
        x -= tw / 2
    elif anchor[0] == 'r':
        x -= tw
    for ch, f in rs:
        d.text((x, y), ch, font=f, fill=fill, anchor='l' + anchor[1],
               stroke_width=halo, stroke_fill=halo_fill)
        x += f.getlength(ch)

def T(d, xy, text, size, fill=INK, anchor='mm', halo=3, bold=False, arabic=True):
    draw_runs(d, xy, runs(text, size, arabic=arabic, bold=bold), fill, anchor=anchor, halo=halo)

# ------------------------------------------------------------------ عناصر مُصمَّمة
def reticle(d, x, y, r=11, color=INK, dark=(0, 0, 0), t=0.0, pulse=True):
    """دائرة هدف: هالة سودا + حلقة + نقطة."""
    pr = r * (1.0 + 0.35 * (0.5 + 0.5 * math.sin(t * 5))) if pulse else r
    d.ellipse([x - pr - 2, y - pr - 2, x + pr + 2, y + pr + 2], outline=dark, width=4)
    d.ellipse([x - pr, y - pr, x + pr, y + pr], outline=color, width=3)
    d.ellipse([x - r * 0.36 - 2, y - r * 0.36 - 2, x + r * 0.36 + 2, y + r * 0.36 + 2], fill=dark)
    d.ellipse([x - r * 0.36, y - r * 0.36, x + r * 0.36, y + r * 0.36], fill=color)

def chip(d, x, y, ar=None, lat=None, size=38, anchor='lm', pad=(20, 12), fill=(10, 13, 22, 226),
         border=(156, 172, 208, 214), txt=INK, lat_size=None):
    """شارة نصّية بزوايا مدوّرة + ظل — النص جوّا الصندوق (v2)."""
    if not ar and not lat:
        return
    rs = runs(ar, size, bold=True) if ar else []
    ls = lat_size or int(size * 0.55)
    rs2 = runs(lat, ls, arabic=False, bold=True) if lat else []
    tw = max([runs_w(rs)] + ([runs_w(rs2)] if rs2 else [0]))
    lh = size * 1.12
    lh2 = ls * 1.25
    bh = int(pad[1] * 2 + (lh if ar else 0) + (lh2 if lat else 0) + 4)
    bw = int(tw + pad[0] * 2)
    box = Image.new('RGBA', (bw, bh), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    bd.rounded_rectangle([1, 1, bw - 2, bh - 2], radius=11, fill=fill, outline=border, width=2)
    bd.rectangle([1, 1, 5, bh - 2], fill=(206, 58, 46, 230))       # شريط أحمر تعريفي
    yy = pad[1] + 2
    if ar:
        draw_runs(bd, (pad[0], yy + lh / 2), rs, txt, anchor='lm'); yy += lh
    if lat:
        draw_runs(bd, (pad[0], yy + lh2 / 2 - 2), rs2, (188, 196, 216), anchor='lm')
    # ظل
    sh = Image.new('RGBA', (bw + 26, bh + 26), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), (13, 16), box.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    x0 = int(x if anchor[0] == 'l' else (x - bw if anchor[0] == 'r' else x - bw / 2))
    y0 = int(y if anchor[1] == 't' else (y - bh if anchor[1] == 'b' else y - bh / 2))
    d._image.paste(sh, (x0 - 13, y0 - 13), sh)
    d._image.paste(box, (x0, y0), box)

def leader(d, x0, y0, x1, y1, color=(226, 230, 242), width=2, dark=True):
    """خيط دلالة رفيع من العلامة للشارة."""
    if dark:
        d.line([(x0, y0), (x1, y1)], fill=(0, 0, 0), width=width + 2)
    d.line([(x0, y0), (x1, y1)], fill=color, width=width)
    d.ellipse([x1 - 3, y1 - 3, x1 + 3, y1 + 3], fill=color)

def dashed_path(d, pts, color, width=5, dash=26, gap=18, phase=0.0, dark=(0, 0, 0), halo=3):
    """خط متقطّع متحرك على طول مسار (نقاط كثيفة)."""
    # حساب الأطوال
    segs, total = [], 0.0
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        segs.append((x0, y0, x1, y1, L, total)); total += L
    pos = -(phase % (dash + gap))
    while pos < total:
        a, b = pos, pos + dash
        for (x0, y0, x1, y1, L, off) in segs:
            s0, s1 = max(a, off), min(b, off + L)
            if s1 <= s0:
                continue
            u0, u1 = (s0 - off) / L, (s1 - off) / L
            p0 = (x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0)
            p1 = (x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1)
            if halo:
                d.line([p0, p1], fill=dark, width=width + halo)
            d.line([p0, p1], fill=color, width=width, joint='curve')
        pos += dash + gap

def chevron_head(d, x, y, ang, size=30, color=INK, dark=(0, 0, 0), width=6):
    """رأس سهم بشعيرتين (chevron) — شكل مُصمَّم، مو مثلث مصمت."""
    for k in (1.0, 0.62):
        for sgn in (1, -1):
            ax = x - size * k * math.cos(ang) + sgn * size * k * 0.75 * math.sin(ang)
            ay = y - size * k * math.sin(ang) - sgn * size * k * 0.75 * math.cos(ang)
            d.line([(x, y), (ax, ay)], fill=dark, width=width + 3)
            d.line([(x, y), (ax, ay)], fill=color, width=width)

def pennant(d, x, y, color, dark=(0, 0, 0), w=22, h=15):
    """علم صغير (راية) للوحدات."""
    d.line([(x, y), (x, y - h - 8)], fill=(20, 20, 24), width=4)
    d.line([(x, y), (x, y - h - 8)], fill=INK, width=2)
    d.polygon([(x, y - h - 8), (x + w, y - h - 4), (x, y)], fill=dark)
    d.polygon([(x + 1, y - h - 7), (x + w - 2, y - h - 4), (x + 1, y - 2)], fill=color)

def unit_block(d, x, y, color=RED, scale=1.0, flag=True):
    """بلوك وحدة: مستطيل مدوّر بحلقة وسطية + راية."""
    w, h = 26 * scale, 18 * scale
    d.rounded_rectangle([x - w / 2 + 2, y - h / 2 + 2, x + w / 2 + 2, y + h / 2 + 2], radius=4, fill=(0, 0, 0))
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=4, fill=color, outline=INK, width=2)
    d.ellipse([x - 3.2 * scale, y - 3.2 * scale, x + 3.2 * scale, y + 3.2 * scale], fill=INK)
    if flag:
        pennant(d, x + w / 2, y - h / 2, color)

def rough_stamp(text_ar, sub_ar, cx, cy, scale=1.0, rot=-9.0, alpha=235, t=0.0):
    """ختم حبر بحواف خشنة + ظل."""
    w, h = int(430 * scale), int(210 * scale)
    pad = 40
    layer = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    box = [pad, pad, pad + w, pad + h]
    ld.rounded_rectangle(box, radius=int(22 * scale), fill=(196, 46, 34, alpha))
    ld.rounded_rectangle([box[0] + 9, box[1] + 9, box[2] - 9, box[3] - 9],
                         radius=int(16 * scale), outline=(252, 246, 232, 255), width=max(2, int(4 * scale)))
    rs = runs(text_ar, int(96 * scale), bold=True)
    draw_runs(ld, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - h * 0.12), rs, INK + (255,), anchor='mm')
    rs2 = runs(sub_ar, int(30 * scale), bold=True)
    draw_runs(ld, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + h * 0.26), rs2, (250, 232, 214, 240), anchor='mm')
    # خشونة الحواف: قناع ضوضاء (نفس مقاس الصورة النهائية)
    base = Image.new('L', layer.size, 0)
    md = ImageDraw.Draw(base)
    md.rounded_rectangle(box, radius=int(22 * scale), fill=255)
    arr = np.random.default_rng(int(abs(t) * 997) % 9999).random((layer.size[1], layer.size[0]))
    noise = Image.fromarray((arr * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))
    mask = ImageChops.multiply(base, noise.point(lambda v: 255 if v > 42 else 0))
    layer.putalpha(ImageChops.multiply(layer.split()[3], mask))
    # ظل
    sh = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), (0, 0), layer.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    layer = layer.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = sh.rotate(rot, expand=True, resample=Image.BICUBIC)
    return sh, layer, (cx, cy)

# ------------------------------------------------------------------ جغرافيا
WORLD = json.loads(GEO_JSON.read_text())
def pip_ring(pt, ring):
    x, y = pt; inside = False; n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                inside = not inside
    return inside

AREA = {}
for _c, _g in WORLD.items():
    _polys = _g['coordinates'] if _g['type'] == 'MultiPolygon' else [_g['coordinates']]
    AREA[_c] = [rings[0] for rings in _polys]

def on_land_geo(lon, lat, code=None):
    for c in ([code] if code else AREA):
        for ring in AREA.get(c, []):
            if pip_ring((lon, lat), ring):
                return True
    return False

def snap_to_land(lon, lat, max_deg=0.8, step=0.02):
    if on_land_geo(lon, lat):
        return lon, lat, 0.0
    r = step
    while r <= max_deg:
        for k in range(16):
            a = k * math.pi / 8
            for s in (1, -1):
                nlon = lon + s * r * math.cos(a) / max(math.cos(math.radians(lat)), 0.3)
                nlat = lat + s * r * math.sin(a)
                if on_land_geo(nlon, nlat):
                    return nlon, nlat, r
        r += step
    return lon, lat, -1.0

class View:
    def __init__(self, span_lon, lon0, lat0, w=W, h=H):
        self.k, self.cos = w / span_lon, math.cos(math.radians(lat0))
        self.lon0, self.lat0, self.w, self.h = lon0, lat0, w, h
    def xy(self, lon, lat):
        return ((lon - self.lon0) * self.cos * self.k + self.w / 2,
                -(lat - self.lat0) * self.k + self.h / 2)

def sea_bg(w, h):
    y = np.linspace(0, 1, h)[:, None]          # (h,1)
    base = np.stack([SEA_TOP[i] + (SEA_BOT[i] - SEA_TOP[i]) * y[:, 0] for i in range(3)], axis=1)  # (h,3)
    img = np.repeat(base[:, None, :], w, axis=1)                                                   # (h,w,3)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w * 0.5) / (w * 0.62)) ** 2 + ((yy - h * 0.45) / (h * 0.7)) ** 2)           # (h,w)
    img = img * np.clip(1.22 - 0.42 * r, 0.72, 1.22)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype('uint8'))

def map_base(v, focus=('COL',), dim=None, ss=SS):
    """خريطة ملساء: تُرسم بدقة 2× ثم تُصغَّر."""
    w, h = v.w * ss, v.h * ss
    vv = View((v.lon0 and 0) or 1, 0, 0)  # placeholder (ما منستعملها)
    # نعيد بناء إسقاط بمقاس كبير
    big = View.__new__(View)
    big.k, big.cos = w / ((v.w / v.k) ), math.cos(math.radians(v.lat0))
    big.lon0, big.lat0, big.w, big.h = v.lon0, v.lat0, w, h
    img = sea_bg(w, h)
    d = ImageDraw.Draw(img)
    for c, rings in AREA.items():
        fill = LAND_FOC if c in focus else LAND
        for ring in rings:
            pts = [big.xy(lon, lat) for lon, lat in ring]
            if len(pts) >= 3:
                d.polygon(pts, fill=fill)
    for c, rings in AREA.items():
        ecol = EDGE_FOC if c in focus else EDGE
        ew = 3 if c in focus else 2
        for ring in rings:
            pts = [big.xy(lon, lat) for lon, lat in ring]
            if len(pts) >= 3:
                d.line(pts + [pts[0]], fill=ecol, width=ew, joint='curve')
    out = img.resize((v.w, v.h), Image.LANCZOS)
    if dim:
        # تعتيم كل شي إلا منطقة التركيز
        m = Image.new('L', (v.w, v.h), 0); md = ImageDraw.Draw(m)
        md.ellipse([v.w / 2 - dim[0], v.h / 2 - dim[1], v.w / 2 + dim[0], v.h / 2 + dim[1]], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(130))
        out = Image.composite(out, Image.blend(out, Image.new('RGB', out.size, (6, 8, 16)), 0.55), m)
    return out

def land_mask(v):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for rings in AREA.values():
        for ring in rings:
            pts = [v.xy(lon, lat) for lon, lat in ring]
            if len(pts) >= 3:
                d.polygon(pts, fill=255)
    return m

# ------------------------------------------------------------------ نفع عام
def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def ease_in(x):
    x = max(0.0, min(1.0, x)); return x * x

def seg(t, a, b): return max(0.0, min(1.0, (t - a) / max(b - a, 1e-6)))

def grade(img, grain=2.4, vig=0.30):
    a = np.asarray(img).astype(np.float32)
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= np.clip(1.05 - vig * r ** 2, 0.66, 1.05)[..., None]
    a += np.random.default_rng(hash((h, w, 7)) % 2 ** 31).standard_normal((h, w, 1)).astype(np.float32) * grain
    a[..., 0] *= 1.012; a[..., 2] *= 0.988
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))

# ------------------------------------------------------------------ صوت
SR = 48000
def build_audio(path, cues):
    n = int(SR * DUR); t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    bed = 0.24 * np.sin(2 * np.pi * 55 * t) + 0.12 * np.sin(2 * np.pi * 82.5 * t + 0.4)
    bed += 0.05 * np.sin(2 * np.pi * 110 * t + 1.1) * (1 + 0.5 * np.sin(2 * np.pi * 0.07 * t))
    air = rng.standard_normal(n); k = np.hanning(2001)
    bed += 0.11 * np.convolve(air, k / k.sum(), mode='same')
    env = np.interp(t, [0, 1.0, 4, 12, 17.5, 21, 22.3, DUR], [0, 0.9, 0.72, 0.9, 0.8, 0.5, 0.15, 0.0])
    mix = bed * env * 0.35
    def env_exp(dur, a=0.01, dec=0.25):
        m = int(dur * SR); tt = np.arange(m) / SR
        return np.minimum(tt / max(a, 1e-3), 1.0) * np.exp(-tt / dec)
    def add(sig, at, gain):
        i = int(at * SR)
        if i < 0:
            sig = sig[-i:]; i = 0
        s = sig[:len(mix) - i]
        if len(s):
            mix[i:i + len(s)] += s * gain
    for c in cues:
        kd, at, g = c['k'], c['t'], c.get('g', 0.10)
        if kd == 'riser':
            dur = c.get('d', 1.0); m = int(dur * SR); tt = np.arange(m) / SR
            f = 90 + 260 * (tt / dur) ** 2
            sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / dur) ** 2
            add(sig * 0.8 + np.convolve(rng.standard_normal(m), np.hanning(401) / 200, mode='same') * 0.5, at - dur, g)
        elif kd == 'impact':
            dur = 0.9; m = int(dur * SR)
            f = np.linspace(c.get('f0', 90), c.get('f1', 45), m)
            add(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(dur, 0.008, 0.30), at, g)
        elif kd == 'whoosh':
            dur = c.get('d', 0.8); m = int(dur * SR)
            band = np.convolve(rng.standard_normal(m), np.hanning(101) / 50, mode='same')
            add(band * np.sin(np.pi * np.arange(m) / m) ** 2, at, g * 0.6)
        elif kd == 'tick':
            dur = 0.09; m = int(dur * SR)
            add(np.sin(2 * np.pi * 1450 * np.arange(m) / SR) * env_exp(dur, 0.003, 0.02), at, g * 0.5)
        elif kd == 'hit':
            dur = 0.5; m = int(dur * SR)
            sig = (np.sin(2 * np.pi * 140 * np.arange(m) / SR) * 0.7 +
                   np.convolve(rng.standard_normal(m), np.hanning(31) / 15, mode='same') * 0.6) * env_exp(dur, 0.004, 0.12)
            add(sig, at, g)
        elif kd == 'paper':
            dur = 0.7; m = int(dur * SR)
            add(np.convolve(rng.standard_normal(m), np.hanning(301) / 150, mode='same') * env_exp(dur, 0.02, 0.22), at, g * 0.5)
    peak = np.max(np.abs(mix)) or 1.0
    mix = (mix / peak) * 0.82
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(np.stack([mix, mix * 0.98], 1), -1, 1) * 32767).astype('<i2').tobytes())

# ------------------------------------------------------------------ النقاط
MED_RAW = (6.25, -75.56); MIA_RAW = (25.76, -80.19)
ROAD_RAW = [(9.8, -74.6), (10.4, -75.0), (10.6, -75.7), (9.6, -76.0), (8.4, -75.8), (7.2, -75.7), MED_RAW]
_l, MED = None, None
def _init_points():
    global MED, MIA, ROAD, P_MED, P_MIA
    lon, lat, d1 = snap_to_land(MED_RAW[1], MED_RAW[0]); MED = (lat, lon)
    lon, lat, d2 = snap_to_land(MIA_RAW[1], MIA_RAW[0]); MIA = (lat, lon)
    ROAD = []
    for la, lo in ROAD_RAW:
        lo2, la2, _ = snap_to_land(lo, la)
        ROAD.append((la2, lo2))
    P_MED = (MED[1], MED[0]); P_MIA = (MIA[1], MIA[0])
    print(f'[i] لزق على البَر: ميديين {d1:.3f}° · ميامي {d2:.3f}°')
_init_points()

class Demo:
    def __init__(self):
        ph = Image.open(ROOT / 'DEMO1_ESCOBAR/assets/candidate_portrait.jpg').convert('RGB')
        g = ph.convert('L')
        lo = Image.new('RGB', g.size, (28, 24, 26)); hi = Image.new('RGB', g.size, (230, 218, 198))
        self.photo_t = Image.composite(hi, lo, g)

    # 1) chapter_black_silence
    def shot1(self, t, a, b):
        img = Image.new('RGB', (W, H), BLACK); d = ImageDraw.Draw(img)
        p = seg(t, 0.55, 1.35)
        if p > 0:
            rs = runs('كولومبيا', 122, bold=True)
            lay = Image.new('RGBA', (W, 300), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            draw_runs(ld, (W / 2, 150), rs, INK + (255,), anchor='mm')
            m = Image.new('L', lay.size, 0); md = ImageDraw.Draw(m)
            half = int(W / 2 * ease_out(p))
            md.rectangle([W / 2 - half, 0, W / 2 + half, lay.height], fill=255)
            mm = ImageChops.multiply(lay.split()[3], m)
            img.paste(lay.convert('RGB'), (0, int(H / 2 - 210)), mm)
        if p > 0.5:
            d = ImageDraw.Draw(img)
            T(d, (W / 2, H / 2 + 70), '١٩٩٣', 112, fill=YELLOW, halo=0, bold=True)
        pw = 250 * ease_out(seg(t, 0.75, 1.5))
        d.line([(W / 2 - pw, H / 2 + 185), (W / 2 + pw, H / 2 + 185)], fill=(70, 74, 84), width=2)
        return img

    # 2) map_inline_label
    def shot2(self, t, a, b):
        p = seg(t, a, b)
        v = View(15.0 - 1.8 * ease(p), -74.9, 6.1)
        img = map_base(v, focus=('COL',)); d = ImageDraw.Draw(img)
        mx, my = v.xy(*P_MED)
        reticle(d, mx, my, 12, INK, t=t)
        lx, ly = mx + 130, my - 96
        leader(d, mx + 14, my - 10, lx - 6, ly + 16)
        chip(d, lx, ly, ar='ميديين', lat='MEDELLÍN', size=40)
        T(d, (v.xy(-73.4, 3.2)[0], v.xy(-73.4, 3.2)[1]), 'كولومبيا', 62,
          fill=(226, 232, 244), halo=4, bold=True)
        T(d, (W / 2, H - 82), '١٩٩٣ · آخر معقل', 40, fill=(222, 228, 240), halo=3)
        return img

    # 3) supply_line_draw
    def shot3(self, t, a, b):
        p = seg(t, a, b)
        v = View(44.0 - 3.0 * ease(p), -77.5, 15.5)
        img = map_base(v, focus=('COL', 'USA', 'VEN', 'PAN', 'CUB'))
        d = ImageDraw.Draw(img)
        g0, g1 = v.xy(*P_MED), v.xy(*P_MIA)
        nx, ny = -(g1[1] - g0[1]), (g1[0] - g0[0]); L = math.hypot(nx, ny) or 1
        c = ((g0[0] + g1[0]) / 2 + nx / L * 150, (g0[1] + g1[1]) / 2 + ny / L * 150)
        pts = [((1 - u) ** 2 * g0[0] + 2 * (1 - u) * u * c[0] + u ** 2 * g1[0],
                (1 - u) ** 2 * g0[1] + 2 * (1 - u) * u * c[1] + u ** 2 * g1[1]) for u in np.linspace(0, 1, 121)]
        drawn = pts[:max(3, int(len(pts) * ease(seg(t, a + 0.35, a + 1.9))))]
        dashed_path(d, drawn, YELLOW, width=5, dash=30, gap=20, phase=(t - a) * 90)
        hx, hy = drawn[-1]
        ang = math.atan2(hy - drawn[-3][1], hx - drawn[-3][0])
        chevron_head(d, hx, hy, ang, size=34, color=YELLOW, width=7)
        reticle(d, g0[0], g0[1], 11, INK, t=t)
        chip(d, g0[0] + 150, g0[1] - 66, ar='ميديين', lat='MEDELLÍN', size=36)
        leader(d, g0[0] + 12, g0[1] - 8, g0[0] + 138, g0[1] - 58)
        if len(drawn) > len(pts) - 4:
            reticle(d, g1[0], g1[1], 12, YELLOW, t=t)
            chip(d, g1[0] + 160, g1[1] - 70, ar='ميامي', lat='MIAMI', size=36)
            leader(d, g1[0] + 12, g1[1] - 10, g1[0] + 148, g1[1] - 62)
        T(d, (W / 2, H - 84), 'خط الإمداد: بحرًا وجوًّا', 42, halo=3, bold=True)
        return img

    # 4) spreading_map_dots (فيضان + وحدات)
    def shot4(self, t, a, b):
        p = seg(t, a, b)
        v = View(13.4 - 1.0 * ease(p), -74.5, 6.0)
        img = map_base(v, focus=('COL',), dim=(560, 360))
        mask = land_mask(v)
        mx, my = v.xy(*P_MED)
        r = 70 + 760 * ease_out(p)
        fl = Image.new('L', (W, H), 0); fd = ImageDraw.Draw(fl)
        fd.ellipse([mx - r, my - r * 0.92, mx + r, my + r * 0.92], fill=225)
        for i, (dl, dt) in enumerate([(-1, 0.1), (1, 0), (0, 1), (0, -1), (-0.6, 0.75), (0.75, -0.6)]):
            rr = r * (0.52 + 0.05 * i)
            fd.ellipse([mx + dl * r * 0.55 - rr, my + dt * r * 0.45 - rr * 0.8,
                        mx + dl * r * 0.55 + rr, my + dt * r * 0.45 + rr * 0.8], fill=200)
        fl = fl.filter(ImageFilter.GaussianBlur(34))
        fl = Image.composite(fl, Image.new('L', (W, H), 0), mask)
        img = Image.composite(Image.new('RGB', (W, H), RED), img, fl.point(lambda x: int(x * 0.82)))
        # حلقة حمرا متوهّجة على الحد
        glow = Image.new('L', (W, H), 0); gd = ImageDraw.Draw(glow)
        gd.ellipse([mx - r, my - r * 0.92, mx + r, my + r * 0.92], outline=230, width=10)
        glow = glow.filter(ImageFilter.GaussianBlur(22))
        img = Image.composite(Image.new('RGB', (W, H), (255, 96, 70)), img, glow.point(lambda x: int(x * 0.55)))
        glow2 = Image.new('L', (W, H), 0); g2 = ImageDraw.Draw(glow2)
        pr = r * (0.75 + 0.25 * (0.5 + 0.5 * math.sin(t * 3.2)))
        g2.ellipse([mx - pr, my - pr * 0.92, mx + pr, my + pr * 0.92], outline=180, width=4)
        img = Image.composite(Image.new('RGB', (W, H), (255, 150, 120)), img,
                              glow2.filter(ImageFilter.GaussianBlur(1)).point(lambda x: int(x * 0.7)))
        d = ImageDraw.Draw(img)
        for i, (lat, lon) in enumerate([(7.0, -75.9), (7.6, -75.0), (5.6, -75.7), (8.2, -74.7)]):
            u = ease(seg(t, a + 0.6 + i * 0.3, a + 1.15 + i * 0.3))
            if u <= 0 or not on_land_geo(lon, lat):
                continue
            x, y = v.xy(lon, lat)
            unit_block(d, x, y, RED, scale=1.15 * (0.7 + 0.3 * u))
        reticle(d, mx, my, 11, INK, t=t)
        chip(d, mx + 150, my + 92, ar='ميديين', lat='MEDELLÍN', size=36)
        leader(d, mx + 12, my + 10, mx + 138, my + 84)
        T(d, (W / 2, H - 84), 'منطقة العمليات', 44, halo=3, bold=True)
        return img

    # 5) counter_escalate_black
    def shot5(self, t, a, b):
        img = Image.new('RGB', (W, H), BLACK); d = ImageDraw.Draw(img)
        p = seg(t, a, b)
        val = int(round(525 * ease_out(min(1.0, p / 0.7))))
        T(d, (W / 2, H / 2 - 40), f'{val}'.translate(AR_DIGITS), 250, fill=INK, halo=0, bold=True)
        d.line([(W / 2 - 210, H / 2 + 118), (W / 2 + 210, H / 2 + 118)], fill=(72, 76, 86), width=2)
        T(d, (W / 2, H / 2 + 178), 'طن كوكايين', 58, fill=(206, 212, 226), halo=0, bold=True)
        T(d, (W / 2, H / 2 + 246), 'تقدير رسمي', 32, fill=(126, 132, 148), halo=0)
        for i in range(5):
            if ease(seg(t, a + 0.9 + i * 0.12, a + 1.05 + i * 0.12)) > 0:
                d.rectangle([W / 2 + 240 + i * 26, H / 2 - 96, W / 2 + 252 + i * 26, H / 2 - 44], fill=RED)
        return img

    # 6) drawn_arrow_telegraph
    def shot6(self, t, a, b):
        p = seg(t, a, b)
        v = View(13.6, -74.9, 7.4)
        img = map_base(v, focus=('COL',), dim=(520, 380)); d = ImageDraw.Draw(img)
        g0 = v.xy(-74.35, 10.6)
        g1 = v.xy(*P_MED)
        pts = []
        for u in np.linspace(0, 1, 90):
            x = (1 - u) ** 2 * g0[0] + 2 * (1 - u) * u * (g0[0] + 190) + u ** 2 * g1[0]
            y = (1 - u) ** 2 * g0[1] + 2 * (1 - u) * u * (g0[1] + 90) + u ** 2 * g1[1]
            pts.append((x, y))
        u = ease(p)
        head = int(len(pts) * u)
        if head > 4:
            dashed_path(d, pts[:head], INK, width=6, dash=26, gap=16, phase=(t - a) * 110)
            hx, hy = pts[head - 1]
            ang = math.atan2(hy - pts[max(0, head - 4)][1], hx - pts[max(0, head - 4)][0])
            chevron_head(d, hx, hy, ang, size=36, color=INK, width=7)
        reticle(d, g1[0], g1[1], 12, INK, t=t)
        chip(d, pts[10][0] + 44, pts[10][1] + 74, ar='من الشمال', size=36)
        leader(d, pts[12][0], pts[12][1], pts[10][0] + 40, pts[10][1] + 64)
        chip(d, g1[0] + 150, g1[1] + 84, ar='ميديين', lat='MEDELLÍN', size=36)
        leader(d, g1[0] + 12, g1[1] + 8, g1[0] + 138, g1[1] + 78)
        return img

    # 7) tinted_archive
    def shot7(self, t, a, b):
        p = seg(t, a, b)
        ph = self.photo_t; phw, phh = ph.size
        ch = phh; cw = int(ch * W / H)
        if cw > phw:
            cw = phw; ch = int(cw * H / W)
        z = 1.0 + 0.09 * ease(p)
        cw2, ch2 = int(cw / z), int(ch / z)
        x0 = max(0, min(phw - cw2, int((phw - cw2) * 0.5 + (0.5 - p) * 54)))
        y0 = max(0, min(phh - ch2, int((phh - ch2) * 0.45)))
        img = ph.crop((x0, y0, x0 + cw2, y0 + ch2)).resize((W, H), Image.LANCZOS)
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rectangle([0, H - 168, W, H], fill=(8, 8, 10, 158))
        od.rectangle([0, H - 168, W, H - 164], fill=(206, 58, 46, 200))
        img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
        d = ImageDraw.Draw(img)
        T(d, (74, H - 92), 'بيت صغير · ميديين', 44, anchor='lm', bold=True)
        T(d, (W - 74, H - 92), 'ARCHIVE 1993', 30, fill=(216, 208, 198), anchor='rm', arabic=False)
        return img

    # 8) flag_stamp_advance (وحدات + منطقة آمنة)
    def shot8(self, t, a, b):
        v = View(11.8, -74.7, 6.2)
        img = map_base(v, focus=('COL',), dim=(540, 390)); d = ImageDraw.Draw(img)
        mx, my = v.xy(*P_MED)
        # منطقة آمنة: حلقة متقطعة خضرا (مو بلوب أخضر)
        rr = 120
        ring = Image.new('L', (W, H), 0); rd = ImageDraw.Draw(ring)
        rd.ellipse([mx - rr, my - rr * 0.8, mx + rr, my + rr * 0.8], outline=210, width=6)
        ring = ring.filter(ImageFilter.GaussianBlur(0.6))
        img = Image.composite(Image.new('RGB', (W, H), (30, 80, 44)), img,
                              ImageChops.multiply(ring, land_mask(v)).point(lambda x: int(x * 0.5)))
        d = ImageDraw.Draw(img)
        dashed_path(d, [((mx + rr * math.cos(k * 0.4)) , (my + rr * 0.8 * math.sin(k * 0.4))) for k in np.linspace(0, 2 * math.pi, 40)],
                    GREEN, width=4, dash=18, gap=12, phase=-(t - a) * 40, halo=2)
        # وحدات على الطريق
        for i in range(len(ROAD) - 1):
            u = ease(seg(t, a + 0.14 * i, a + 0.5 + 0.14 * i))
            if u <= 0:
                continue
            la0, lo0 = ROAD[i]; la1, lo1 = ROAD[i + 1]
            x, y = v.xy(lo0 + (lo1 - lo0) * u, la0 + (la1 - la0) * u)
            unit_block(d, x, y, RED, scale=1.15, flag=(i % 2 == 0))
        reticle(d, mx, my, 11, INK, t=t)
        chip(d, mx + 160, my + 96, ar='المنطقة الآمنة', size=34, border=(120, 190, 140, 220))
        leader(d, mx + 14, my + 12, mx + 148, my + 88)
        T(d, (W / 2, H - 82), 'الوحدات قفلت الطرق', 44, halo=3, bold=True)
        return img

    # 9) stamp_impact_card
    def shot9(self, t, a, b):
        img = self.shot8(t, a, b)          # نفس المشهد (ترابط: نمط P2 - نفس الخريطة)
        d = ImageDraw.Draw(img)
        p = seg(t, a, b)
        u = ease_out(seg(t, a + 0.10, a + 0.36))
        over = 1.0 + 0.28 * math.exp(-((p - 0.36) ** 2) / 0.0025)   # ارتداد
        sc = (2.05 - 1.05 * u) * over
        shake = 0.0
        if 0.30 < p < 0.46:
            shake = 9 * math.exp(-((p - 0.36) ** 2) / 0.002)
        sh, layer, (cx, cy) = rough_stamp('١٩٩٣', 'آخر سنة', 0, 0, scale=sc, rot=-9 * u, t=t)
        px, py = int(W * 0.315 + shake * 0.7), int(H * 0.335 + shake * 0.4)
        img.paste(Image.alpha_composite(Image.new('RGBA', layer.size, (0, 0, 0, 0)), sh).convert('RGB'),
                  (int(px - sh.width / 2), int(py - sh.height / 2)), sh)
        img.paste(layer.convert('RGB'), (int(px - layer.width / 2), int(py - layer.height / 2)), layer)
        return img

    # 10) counter_on_object
    def shot10(self, t, a, b):
        p = seg(t, a, b)
        img = Image.new('RGB', (W, H), (13, 17, 27)); d = ImageDraw.Draw(img)
        cx, cy = W / 2, H / 2 + 90
        # صندوق بمنظور بسيط
        d.polygon([(cx - 150, cy - 60), (cx - 60, cy - 110), (cx + 160, cy - 110), (cx + 70, cy - 60)], fill=(120, 96, 64))
        d.rectangle([cx - 150, cy - 60, cx + 70, cy + 90], fill=(96, 76, 52), outline=(30, 24, 18), width=3)
        d.polygon([(cx - 150, cy - 60), (cx + 70, cy - 60), (cx + 160, cy - 110), (cx - 60, cy - 110)],
                  fill=(126, 100, 66), outline=(30, 24, 18), width=3)
        for k in (-60, 10, 70):
            d.line([(cx - 150 + k + 20, cy - 60), (cx - 150 + k + 20, cy + 90)], fill=(72, 56, 38), width=6)
        val = int(round(25 * ease_out(min(1.0, p / 0.6))))
        T(d, (cx, cy - 230), f'{val}'.translate(AR_DIGITS), 180, fill=INK, halo=0, bold=True)
        d.line([(cx - 150, cy + 150), (cx + 150, cy + 150)], fill=(70, 74, 84), width=2)
        T(d, (cx, cy + 205), 'طن اخترقت الحدود', 46, fill=(206, 212, 226), halo=0, bold=True)
        return img

    # 11) end_card_static
    def shot11(self, t, a, b):
        img = Image.new('RGB', (W, H), BLACK); d = ImageDraw.Draw(img)
        p = seg(t, a, b)
        al = ease(seg(t, a + 0.15, a + 0.7))
        if al > 0:
            col = tuple(int(BLACK[i] + (INK[i] - BLACK[i]) * al) for i in range(3))
            T(d, (W / 2, H / 2 - 30), 'يتبع', 66, fill=col, halo=0, bold=True)
            d.line([(W / 2 - 130, H / 2 + 40), (W / 2 + 130, H / 2 + 40)], fill=(70, 74, 84), width=2)
            T(d, (W / 2, H / 2 + 96), 'اختبار Rulebook v1.3', 30, fill=(120, 124, 138), halo=0)
        if p > 0.82:
            img = Image.blend(img, Image.new('RGB', (W, H), BLACK), ease(seg(t, b - 0.4, b)))
        return img

def main():
    FRAMES.mkdir(parents=True, exist_ok=True)
    d = Demo()
    shots = [
        (0.00, 1.60, d.shot1), (1.60, 3.40, d.shot2), (3.40, 6.00, d.shot3),
        (6.00, 8.40, d.shot4), (8.40, 11.00, d.shot5), (11.00, 13.00, d.shot6),
        (13.00, 15.60, d.shot7), (15.60, 17.60, d.shot8), (17.60, 19.20, d.shot9),
        (19.20, 21.40, d.shot10), (21.40, 23.00, d.shot11),
    ]
    cues = [{'k': 'riser', 't': 1.00, 'd': 0.9, 'g': 0.10}, {'k': 'impact', 't': 1.05, 'f0': 96, 'f1': 42, 'g': 0.16},
            {'k': 'whoosh', 't': 1.62, 'd': 0.9, 'g': 0.12}, {'k': 'whoosh', 't': 3.45, 'd': 0.8, 'g': 0.10},
            {'k': 'impact', 't': 6.05, 'f0': 74, 'f1': 40, 'g': 0.13}, {'k': 'whoosh', 't': 8.45, 'd': 0.6, 'g': 0.10},
            {'k': 'whoosh', 't': 11.05, 'd': 0.7, 'g': 0.10}, {'k': 'paper', 't': 13.05, 'g': 0.12},
            {'k': 'whoosh', 't': 15.58, 'd': 0.5, 'g': 0.09}, {'k': 'impact', 't': 17.70, 'f0': 120, 'f1': 52, 'g': 0.15},
            {'k': 'hit', 't': 17.74, 'g': 0.13}]
    for i in range(26):
        cues.append({'k': 'tick', 't': 8.55 + i * 0.055, 'g': 0.085})
    for i in range(4):
        cues.append({'k': 'tick', 't': 19.7 + i * 0.3, 'g': 0.07})
    build_audio(BUILD / 'audio.wav', cues)

    checks = [('ميديين', MED), ('ميامي', MIA)] + [(f'طريق {i+1}', p) for i, p in enumerate(ROAD)]
    bad = 0
    for nm, (lat, lon) in checks:
        ok = on_land_geo(lon, lat)
        bad += (not ok)
        print(f"   {'✓' if ok else '✗ على البحر!'} {nm} ({lat:.2f},{lon:.2f})")
    if bad:
        raise SystemExit('تحقق الجغرافيا فشل.')

    total = int(round(DUR * FPS))
    print(f'[i] رندر {total} فريم ...')
    for n in range(total):
        t = n / FPS
        img = None
        for (a, b, fn) in shots:
            if a <= t < b:
                img = fn(t, a, b) if fn.__code__.co_argcount == 4 else fn(t)
                break
        if img is None:
            img = Image.new('RGB', (W, H), BLACK)
        grade(img).save(FRAMES / f'f{n:04d}.jpg', quality=92)
        if n % 120 == 0:
            print(f'    ... {n}/{total}')
    out = BUILD / 'escobar_ww2drive_demo_v2.mp4'
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, '-y', '-framerate', str(FPS), '-i', str(FRAMES / 'f%04d.jpg'), '-i', str(BUILD / 'audio.wav'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', str(out)], check=True, capture_output=True)
    print('[✓] الفيديو:', out, round(out.stat().st_size / 1e6, 2), 'MB')
    picks = [0.8, 2.5, 4.7, 7.3, 9.8, 12.0, 14.3, 16.8, 18.2, 20.4, 22.2]
    cols = 4; rows = math.ceil(len(picks) / cols); tw, th = 480, 270
    sheet = Image.new('RGB', (cols * tw, rows * th), (12, 12, 14))
    for i, tp in enumerate(picks):
        sheet.paste(Image.open(FRAMES / f'f{int(tp * FPS):04d}.jpg').resize((tw, th), Image.LANCZOS),
                    ((i % cols) * tw, (i // cols) * th))
    sheet.save(BUILD / 'qc_sheet_v2.jpg', quality=92)
    print('[✓] ملصق الفحص:', BUILD / 'qc_sheet_v2.jpg')

if __name__ == '__main__':
    main()
