#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ww2demo.py — رندر ديمو اختبار Rulebook v1.3 (نمط OverSimplified) لإسكوبار، بلا VO.

المصدر الوحيد للقرارات: engine/projects/ww2_demo/cocktail/plan.json
(كل نبضة كرت من بنك الأفكار: فيديو@توقيت — vaping / ww2p1 / ww2p2).

الإخراج: mp4 1920×1080@24fps + صوت (bed + SFX تحت الجو) + ملصق QC.
الأرض: مضلّعات حقيقية (world.geo.json) تُرسم لكل فريم بإسقاط مباشر — النقاط كلها على البَر.
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
GEO = Path('/home/user/build/geo10')
FRAMES = BUILD / 'frames'
W, H, FPS = 1920, 1080, 24
DUR = 23.0

FONT_AR = str(ROOT / 'assets_global/fonts/NotoNaskhArabic-Regular.ttf')
FONT_DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

SEA       = (11, 16, 30)
LAND      = (58, 76, 120)
LAND_FOCUS= (74, 96, 146)
LAND_EDGE = (132, 152, 196)
RED       = (206, 58, 46)
GREEN     = (58, 152, 74)
YELLOW    = (240, 195, 62)
INK       = (245, 242, 234)
BLACK     = (8, 8, 11)
GREY      = (150, 156, 172)
AR_DIGITS = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')

CODES = ['COL', 'PAN', 'VEN', 'ECU', 'PER', 'BRA', 'CRI', 'NIC', 'HND', 'GTM',
         'MEX', 'CUB', 'USA', 'PRI', 'HTI', 'DOM', 'JAM', 'TTO']

# نحمّل المضلعات مرة وحدة (دقة 10m — مفحوصة: ميديين جوّا كولومبيا)
WORLD = {}
def load_world():
    data = json.loads((GEO / 'by_code.json').read_text())
    for c, g in data.items():
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        WORLD[c] = [rings[0] for rings in polys]
load_world()

def pip_ring(pt, ring):
    """ray-casting: نقطة داخل مضلع؟"""
    x, y = pt; inside = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < xi:
                inside = not inside
    return inside

def on_land_geo(lon, lat, code=None):
    codes = [code] if code else WORLD.keys()
    for c in codes:
        for ring in WORLD.get(c, []):
            if pip_ring((lon, lat), ring):
                return True
    return False

def snap_to_land(lon, lat, max_deg=0.6, step=0.02):
    """يلزق النقطة على البَر إذا وقعت بالماء (قانون المشروع: ما في نقطة بحر)."""
    if on_land_geo(lon, lat):
        return lon, lat, 0.0
    r = step
    while r <= max_deg:
        for k in range(16):
            ang = k * math.pi / 8
            for sgn in (1, -1):
                nlon = lon + sgn * r * math.cos(ang) / max(math.cos(math.radians(lat)), 0.3)
                nlat = lat + sgn * r * math.sin(ang)
                if on_land_geo(nlon, nlat):
                    return nlon, nlat, r
        r += step
    return lon, lat, -1.0

def ar(txt, size):
    f = ImageFont.truetype(FONT_AR, size)
    s = get_display(arabic_reshaper.reshape(txt))
    return f, s

def label(d, xy, txt, size, fill=INK, halo=3, anchor='mm'):
    f, s = ar(txt, size)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=halo, stroke_fill=(0, 0, 0))

def latin(d, xy, txt, size, fill=GREY, anchor='mm'):
    f = ImageFont.truetype(FONT_DEJA, size)
    d.text(xy, txt, font=f, fill=fill, anchor=anchor, stroke_width=2, stroke_fill=(0, 0, 0))

class View:
    """إسقاط مباشر لفريم واحد: (span_lon, center) → شاشة 1920×1080."""
    def __init__(self, span_lon, lon0, lat0):
        self.k = W / span_lon
        self.cos = math.cos(math.radians(lat0))
        self.lon0, self.lat0 = lon0, lat0
    def xy(self, lon, lat):
        return ((lon - self.lon0) * self.cos * self.k + W / 2,
                -(lat - self.lat0) * self.k + H / 2)

def draw_map(v, img=None, focus=('COL',)):
    img = img or Image.new('RGB', (W, H), SEA)
    d = ImageDraw.Draw(img)
    for c, polys in WORLD.items():
        fill = LAND_FOCUS if c in focus else LAND
        for ring in polys:
            pts = [v.xy(lon, lat) for lon, lat in ring]
            if len(pts) < 3:
                continue
            d.polygon(pts, fill=fill)
    for c, polys in WORLD.items():
        for ring in polys:
            pts = [v.xy(lon, lat) for lon, lat in ring]
            if len(pts) >= 3:
                d.line(pts + [pts[0]], fill=LAND_EDGE, width=2)
    return img

def land_mask(v):
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    for c, polys in WORLD.items():
        for ring in polys:
            pts = [v.xy(lon, lat) for lon, lat in ring]
            if len(pts) >= 3:
                d.polygon(pts, fill=255)
    return m

def on_land(v, lon, lat, mask=None, cache={}):
    key = id(v)
    if mask is None:
        mask = cache.get(key) or land_mask(v)
        cache[key] = mask
        if len(cache) > 3:
            cache.clear()
    x, y = v.xy(lon, lat)
    if not (0 <= x < W and 0 <= y < H):
        return False
    return mask.getpixel((int(x), int(y))) > 128

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def clamp01(x): return max(0.0, min(1.0, x))

def seg(t, a, b): return clamp01((t - a) / max(b - a, 1e-6))

def vignette(img, grain_sd=2.6):
    a = np.asarray(img).astype(np.float32)
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= np.clip(1.06 - 0.30 * r ** 2, 0.62, 1.06)[..., None]
    a += np.random.default_rng(hash((h, w)) % 2 ** 31).standard_normal((h, w, 1)).astype(np.float32) * grain_sd
    a[..., 0] *= 1.012; a[..., 2] *= 0.988
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))

# ------------------------------------------------------------------ audio
SR = 48000
def build_audio(path, cues):
    n = int(SR * DUR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    bed = 0.22 * np.sin(2 * np.pi * 55 * t) + 0.11 * np.sin(2 * np.pi * 82.5 * t + 0.4)
    bed += 0.05 * np.sin(2 * np.pi * 110 * t + 1.1) * (1 + 0.5 * np.sin(2 * np.pi * 0.07 * t))
    air = rng.standard_normal(n)
    k = np.hanning(2001); air = np.convolve(air, k / k.sum(), mode='same')
    bed += 0.55 * air * 0.20
    env = np.interp(t, [0, 0.9, 4, 12, 17.5, 21, 22.2, DUR], [0, 0.9, 0.75, 0.9, 0.8, 0.55, 0.18, 0.0])
    mix = bed * env * 0.35

    def env_exp(dur, a=0.01, dec=0.25):
        m = int(dur * SR); tt = np.arange(m) / SR
        return np.minimum(tt / max(a, 1e-3), 1.0) * np.exp(-tt / dec)

    def add(sig, at, gain):
        i = int(at * SR)
        if i < 0:
            sig = sig[-i:]; i = 0
        seg_ = sig[:len(mix) - i]
        if len(seg_) == 0:
            return
        mix[i:i + len(seg_)] += seg_ * gain

    for c in cues:
        kind, at, g = c['k'], c['t'], c.get('g', 0.10)
        if kind == 'riser':
            dur = c.get('d', 1.0); m = int(dur * SR); tt = np.arange(m) / SR
            f = 90 + 240 * (tt / dur) ** 2
            sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / dur) ** 2
            noise = np.convolve(rng.standard_normal(m), np.hanning(401) / 200, mode='same')
            add(sig * 0.8 + noise * 0.5, at - dur, g)
        elif kind == 'impact':
            dur = 0.9; m = int(dur * SR); tt = np.arange(m) / SR
            f = np.linspace(c.get('f0', 90), c.get('f1', 45), m)
            add(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(dur, 0.008, 0.30), at, g)
        elif kind == 'whoosh':
            dur = c.get('d', 0.8); m = int(dur * SR)
            band = np.convolve(rng.standard_normal(m), np.hanning(101) / 50, mode='same')
            add(band * np.sin(np.pi * np.arange(m) / m) ** 2, at, g * 0.6)
        elif kind == 'tick':
            dur = 0.09; m = int(dur * SR)
            add(np.sin(2 * np.pi * 1450 * np.arange(m) / SR) * env_exp(dur, 0.003, 0.02), at, g * 0.55)
        elif kind == 'hit':
            dur = 0.5; m = int(dur * SR)
            sig = (np.sin(2 * np.pi * 140 * np.arange(m) / SR) * 0.7 +
                   np.convolve(rng.standard_normal(m), np.hanning(31) / 15, mode='same') * 0.6) * env_exp(dur, 0.004, 0.12)
            add(sig, at, g)
        elif kind == 'paper':
            dur = 0.7; m = int(dur * SR)
            add(np.convolve(rng.standard_normal(m), np.hanning(301) / 150, mode='same') * env_exp(dur, 0.02, 0.22), at, g * 0.5)
    peak = np.max(np.abs(mix)) or 1.0
    mix = (mix / peak) * 0.82
    st = np.stack([mix, mix * 0.98], axis=1)
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes())

# ------------------------------------------------------------------ shots
MED_RAW = (6.25, -75.56)      # ميديين
MIA_RAW = (25.76, -80.19)     # ميامي
ROAD_RAW = [(9.6, -74.9), (8.7, -75.3), (7.8, -75.6), (6.9, -75.7), MED_RAW]
# لزق على البَر (قانون المشروع) — يُنفّذ مرة وحدة وبنطبع تقريره
_lon, _lat, _d = snap_to_land(MED_RAW[1], MED_RAW[0]); MED = (_lat, _lon)
_lon, _lat, _d2 = snap_to_land(MIA_RAW[1], MIA_RAW[0]); MIA = (_lat, _lon)
ROAD = []
for _lat0, _lon0 in ROAD_RAW:
    _lon, _lat, _dd = snap_to_land(_lon0, _lat0)
    ROAD.append((_lat, _lon))
print(f"[i] لزق على البَر: ميديين {_d:.3f}° · ميامي {_d2:.3f}°")
def scr(v, pt):
    """(lat,lon) → شاشة"""
    return v.xy(pt[1], pt[0])

class Demo:
    def __init__(self):
        print('[i] تحميل المضلعات...')
        self.photo = Image.open(ROOT / 'DEMO1_ESCOBAR/assets/candidate_portrait.jpg').convert('RGB')
        g = self.photo.convert('L')
        lo = Image.new('RGB', g.size, (30, 26, 28)); hi = Image.new('RGB', g.size, (228, 216, 198))
        self.photo_t = Image.composite(hi, lo, g)

    # ---------- 1) chapter_black_silence ----------
    def shot1(self, t):
        img = Image.new('RGB', (W, H), BLACK); d = ImageDraw.Draw(img)
        p = seg(t, 0.6, 1.4)
        if p > 0:
            # كشف بمسحة أفقية (بدل تفكيك الحروف — العربي بيكتب متّصل)
            f, s = ar('كولومبيا', 118)
            layer = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
            ld.text((W / 2, 130), s, font=f, fill=INK + (255,), anchor='mm')
            wfrac = ease_out(p)
            rect = Image.new('L', layer.size, 0); rd = ImageDraw.Draw(rect)
            half = int(W / 2 * wfrac)
            rd.rectangle([W / 2 - half, 0, W / 2 + half, layer.height], fill=255)
            m = ImageChops.multiply(layer.split()[3], rect)   # حروف فقط — بلا مستطيل أسود
            img.paste(layer.convert('RGB'), (0, int(H / 2 - 200)), m)
            d = ImageDraw.Draw(img)
            if p > 0.55:
                label(d, (W / 2, H / 2 + 60), '١٩٩٣', 110, fill=YELLOW, halo=0)
        pw = 240 * ease_out(seg(t, 0.75, 1.5))
        d.line([(W / 2 - pw, H / 2 + 170), (W / 2 + pw, H / 2 + 170)], fill=(74, 74, 80), width=2)
        return img

    # ---------- 2) map_inline_label ----------
    def shot2(self, t, a, b):
        p = seg(t, a, b)
        z = 1.06 - 0.06 * ease_out(p)
        v = View(13.2 / z, -74.9, 6.2)
        img = draw_map(v); d = ImageDraw.Draw(img)
        img = vignette_open(img, p)
        d = ImageDraw.Draw(img)
        mx, my = scr(v, MED)
        pulse = 1 + 0.25 * math.sin(t * 6)
        d.ellipse([mx - 8 * pulse, my - 8 * pulse, mx + 8 * pulse, my + 8 * pulse], fill=INK)
        d.ellipse([mx - 2.6, my - 2.6, mx + 2.6, my + 2.6], fill=RED)
        if p > 0.3:
            label(d, (mx + 30, my - 28), 'ميديين', 44, anchor='lm')
            latin(d, (mx + 30, my + 12), 'MEDELLÍN', 22, anchor='lm')
        label(d, (W / 2, H - 74), 'كولومبيا · مقاطعة أنتيوكيا', 36, anchor='mm')
        return img

    # ---------- 3) supply_line_draw ----------
    def shot3(self, t, a, b):
        p = seg(t, a, b)
        v = View(46.0, -78.0, 15.0)
        img = draw_map(v); d = ImageDraw.Draw(img)
        gx0, gy0 = scr(v, MED); gx1, gy1 = scr(v, MIA)
        nx, ny = -(gy1 - gy0), (gx1 - gx0)
        L = math.hypot(nx, ny) or 1
        mx, my = (gx0 + gx1) / 2 + nx / L * 130, (gy0 + gy1) / 2 + ny / L * 130
        pts = []
        for i in range(91):
            u = i / 90
            pts.append(((1 - u) ** 2 * gx0 + 2 * (1 - u) * u * mx + u ** 2 * gx1,
                        (1 - u) ** 2 * gy0 + 2 * (1 - u) * u * my + u ** 2 * gy1))
        drawn = int(len(pts) * ease(seg(t, a + 0.35, a + 1.7)))
        if drawn > 2:
            d.line(pts[:drawn], fill=YELLOW, width=5, joint='curve')
            hx, hy = pts[drawn - 1]
            d.ellipse([hx - 6, hy - 6, hx + 6, hy + 6], fill=YELLOW)
        d.ellipse([gx0 - 7, gy0 - 7, gx0 + 7, gy0 + 7], fill=INK)
        label(d, (gx0 + 26, gy0 - 24), 'ميديين', 38, anchor='lm')
        if drawn >= len(pts) - 2:
            d.ellipse([gx1 - 8, gy1 - 8, gx1 + 8, gy1 + 8], fill=YELLOW)
            label(d, (gx1 + 26, gy1 - 24), 'ميامي', 38, anchor='lm')
            latin(d, (gx1 + 26, gy1 + 10), 'MIAMI', 18, anchor='lm')
        label(d, (W / 2, H - 74), 'خط الإمداد: بحرًا وجوًّا', 38, anchor='mm')
        return img

    # ---------- 4) spreading_map_dots + red flood ----------
    def shot4(self, t, a, b):
        p = seg(t, a, b)
        z = 0.95 + 0.06 * ease(p)
        v = View(12.4 / z, -74.6, 6.1)
        img = draw_map(v)
        mask = land_mask(v)
        mx, my = scr(v, MED)
        r = 60 + 700 * ease_out(p)
        flood = Image.new('L', (W, H), 0); fd = ImageDraw.Draw(flood)
        fd.ellipse([mx - r, my - r * 0.9, mx + r, my + r * 0.9], fill=235)
        for i, (dl, dt) in enumerate([(-1, 0), (1, 0), (0, 1), (0, -1), (-0.6, 0.75), (0.75, -0.6)]):
            rr = r * (0.5 + 0.05 * i)
            fd.ellipse([mx + dl * r * 0.55 - rr, my + dt * r * 0.45 - rr * 0.8,
                        mx + dl * r * 0.55 + rr, my + dt * r * 0.45 + rr * 0.8], fill=205)
        flood = flood.filter(ImageFilter.GaussianBlur(30))
        flood = Image.composite(flood, Image.new('L', (W, H), 0), mask)
        red = Image.new('RGB', (W, H), RED)
        img = Image.composite(red, img, flood.point(lambda x: int(x * 0.85)))
        d = ImageDraw.Draw(img)
        for i, (lat, lon) in enumerate([(6.9, -75.9), (7.5, -75.1), (5.6, -75.9), (8.2, -74.8), (6.0, -74.3)]):
            al = ease(seg(t, a + 0.5 + i * 0.22, a + 1.0 + i * 0.22))
            if al <= 0 or not on_land_geo(lon, lat):
                continue
            x, y = v.xy(lon, lat); rr = 10 + 8 * al
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=INK, width=3)
        d.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=INK)
        label(d, (mx + 26, my - 30), 'ميديين', 40, anchor='lm')
        label(d, (W / 2, H - 74), 'منطقة العمليات: الحصار صبغها أحمر', 38, anchor='mm')
        return img

    # ---------- 5) counter_escalate_black ----------
    def shot5(self, t, a, b):
        img = Image.new('RGB', (W, H), BLACK); d = ImageDraw.Draw(img)
        p = seg(t, a, b)
        val = int(round(525 * ease_out(min(1.0, p / 0.72))))
        f, s = ar(f'{val}'.translate(AR_DIGITS), 250)
        d.text((W / 2, H / 2 - 40), s, font=f, fill=INK, anchor='mm')
        label(d, (W / 2, H / 2 + 140), 'طن كوكايين · سنة واحدة', 52, fill=(196, 200, 214), halo=0)
        label(d, (W / 2, H / 2 + 220), 'تقدير رسمي', 30, fill=(120, 124, 140), halo=0)
        return img

    # ---------- 6) drawn_arrow_telegraph ----------
    def shot6(self, t, a, b):
        p = seg(t, a, b)
        v = View(12.6, -74.9, 7.6)
        img = draw_map(v); d = ImageDraw.Draw(img)
        gx0, gy0 = v.xy(-74.6, 9.9)
        gx1, gy1 = v.xy(-75.6, 6.9)
        u = ease(p)
        hx, hy = gx0 + (gx1 - gx0) * u, gy0 + (gy1 - gy0) * u
        ang = math.atan2(gy1 - gy0, gx1 - gx0)
        d.line([(gx0, gy0), (hx, hy)], fill=INK, width=9)
        L, Wd = 48, 27
        d.polygon([(hx, hy),
                   (hx - L * math.cos(ang) + Wd * math.sin(ang), hy - L * math.sin(ang) - Wd * math.cos(ang)),
                   (hx - L * math.cos(ang) - Wd * math.sin(ang), hy - L * math.sin(ang) + Wd * math.cos(ang))], fill=INK)
        mx, my = scr(v, MED)
        d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=RED)
        label(d, (mx + 26, my + 8), 'ميديين', 38, anchor='lm')
        label(d, (W / 2, H - 74), 'الإمداد يمرّ من الشمال', 38, anchor='mm')
        return img

    # ---------- 7) tinted_archive ----------
    def shot7(self, t, a, b):
        p = seg(t, a, b)
        ph = self.photo_t
        target = W / H
        phw, phh = ph.size
        ch = phh; cw = int(ch * target)
        if cw > phw:
            cw = phw; ch = int(cw / target)
        z = 1.0 + 0.10 * ease(p)
        cw2, ch2 = int(cw / z), int(ch / z)
        x0 = int((phw - cw2) * 0.5 + (0.5 - p) * 60)
        y0 = int((phh - ch2) * 0.45)
        x0 = max(0, min(phw - cw2, x0)); y0 = max(0, min(phh - ch2, y0))
        img = ph.crop((x0, y0, x0 + cw2, y0 + ch2)).resize((W, H), Image.LANCZOS)
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rectangle([0, H - 150, W, H], fill=(8, 8, 10, 130))
        img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
        d = ImageDraw.Draw(img)
        label(d, (70, H - 92), 'بيت صغير · ميديين', 42, anchor='lm')
        latin(d, (W - 70, H - 92), 'ARCHIVE 1993', 24, anchor='rm')
        return img

    # ---------- 8) flag_stamp_advance ----------
    def shot8(self, t, a, b):
        v = View(11.4, -74.7, 6.4)
        img = draw_map(v)
        mask = land_mask(v)
        d = ImageDraw.Draw(img)
        mx, my = scr(v, MED)
        r = 78
        safe = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(safe)
        sd.ellipse([mx - r, my - r * 0.82, mx + r, my + r * 0.82], fill=200)
        safe = safe.filter(ImageFilter.GaussianBlur(18))
        safe = Image.composite(safe, Image.new('L', (W, H), 0), mask)
        img = Image.composite(Image.new('RGB', (W, H), GREEN), img, safe)
        d = ImageDraw.Draw(img)
        for i in range(len(ROAD) - 1):
            u = ease(seg(t, a + 0.12 * i, a + 0.45 + 0.12 * i))
            if u <= 0:
                continue
            lat0, lon0 = ROAD[i]; lat1, lon1 = ROAD[i + 1]
            lon, lat = lon0 + (lon1 - lon0) * u, lat0 + (lat1 - lat0) * u
            x, y = v.xy(lon, lat)
            d.rectangle([x - 12, y - 9, x + 12, y + 9], fill=RED, outline=INK, width=2)
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=INK)
        d.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=INK)
        label(d, (mx + 28, my - 34), 'ميديين', 40, anchor='lm')
        label(d, (W / 2, H - 74), 'الوحدات قفلت الطرق · المنطقة الآمنة ضاقت', 38, anchor='mm')
        return img

    # ---------- 9) stamp_impact_card ----------
    def shot9(self, t, a, b):
        v = View(11.4, -74.7, 6.4)
        img = draw_map(v)
        mask = land_mask(v)
        d = ImageDraw.Draw(img)
        mx, my = scr(v, MED)
        r = 78
        safe = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(safe)
        sd.ellipse([mx - r, my - r * 0.82, mx + r, my + r * 0.82], fill=170)
        safe = safe.filter(ImageFilter.GaussianBlur(18))
        safe = Image.composite(safe, Image.new('L', (W, H), 0), mask)
        img = Image.composite(Image.new('RGB', (W, H), GREEN), img, safe)
        d = ImageDraw.Draw(img)
        for lat, lon in ROAD:
            x, y = v.xy(lon, lat)
            d.rectangle([x - 12, y - 9, x + 12, y + 9], fill=RED, outline=INK, width=2)
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=INK)
        d.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=INK)
        label(d, (mx + 28, my - 34), 'ميديين', 40, anchor='lm')
        p = seg(t, a, b)
        u = ease(seg(t, a + 0.12, a + 0.4))
        sc = 2.3 - 1.3 * u
        rot = (1 - u) * -14
        cw, chh = 320 * sc, 150 * sc
        layer = Image.new('RGBA', (int(cw * 1.7), int(chh * 1.7)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        lx, ly = layer.width / 2, layer.height / 2
        ld.rounded_rectangle([lx - cw / 2, ly - chh / 2, lx + cw / 2, ly + chh / 2], radius=14 * sc,
                             fill=(212, 58, 46, int(230)), outline=(245, 242, 234, 255), width=max(2, int(4 * sc)))
        f, s = ar('١٩٩٣', int(84 * sc))
        ld.text((lx, ly - 12 * sc), s, font=f, fill=(245, 242, 234, 255), anchor='mm')
        f2, s2 = ar('آخر سنة', int(26 * sc))
        ld.text((lx, ly + 60 * sc), s2, font=f2, fill=(248, 236, 220, 235), anchor='mm')
        layer = layer.rotate(rot, expand=True, resample=Image.BICUBIC)
        img.paste(layer, (int(W / 2 - layer.width / 2), int(H / 2 - 150 - layer.height / 2)), layer)
        return img

    # ---------- 10) counter_on_object ----------
    def shot10(self, t, a, b):
        p = seg(t, a, b)
        img = Image.new('RGB', (W, H), (14, 18, 28)); d = ImageDraw.Draw(img)
        cx, cy = W / 2, H / 2 + 60
        d.rounded_rectangle([cx - 100, cy - 65, cx + 100, cy + 65], radius=12, fill=(92, 72, 50), outline=INK, width=3)
        for dx in (-33, 33):
            d.line([(cx + dx, cy - 65), (cx + dx, cy + 65)], fill=(58, 44, 32), width=3)
        d.line([(cx - 100, cy), (cx + 100, cy)], fill=(58, 44, 32), width=3)
        val = int(round(25 * ease_out(clamp01(p / 0.6))))
        f, s = ar(f'{val}'.translate(AR_DIGITS), 170)
        d.text((cx, cy - 190), s, font=f, fill=INK, anchor='mm')
        label(d, (cx, cy + 130), 'طن اخترقت الحدود', 46, fill=(198, 202, 216), halo=0)
        return img

    # ---------- 11) end_card_static ----------
    def shot11(self, t, a, b):
        img = Image.new('RGB', (W, H), BLACK); d = ImageDraw.Draw(img)
        p = seg(t, a, b)
        al = ease(seg(t, a + 0.15, a + 0.7))
        if al > 0:
            col = tuple(int(BLACK[i] + (INK[i] - BLACK[i]) * al) for i in range(3))
            label(d, (W / 2, H / 2 - 20), 'يتبع', 62, fill=col, halo=0)
            label(d, (W / 2, H / 2 + 70), 'اختبار Rulebook v1.3', 30, fill=(118, 122, 132), halo=0)
        if p > 0.82:
            img = Image.blend(img, Image.new('RGB', (W, H), BLACK), ease(seg(t, b - 0.4, b)))
        return img

def vignette_open(img, p):
    """فتحة من الأسود (بداية اللقطة)."""
    if p < 0.3:
        return Image.blend(Image.new('RGB', (W, H), BLACK), img, ease(p / 0.3))
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
    cues = [
        {'k': 'riser', 't': 1.05, 'd': 0.9, 'g': 0.10},
        {'k': 'impact', 't': 1.10, 'f0': 96, 'f1': 42, 'g': 0.16},
        {'k': 'whoosh', 't': 1.62, 'd': 0.9, 'g': 0.12},
        {'k': 'whoosh', 't': 3.45, 'd': 0.8, 'g': 0.10},
        {'k': 'impact', 't': 6.05, 'f0': 74, 'f1': 40, 'g': 0.13},
    ]
    for i in range(26):
        cues.append({'k': 'tick', 't': 8.55 + i * 0.055, 'g': 0.085})
    cues += [
        {'k': 'paper', 't': 13.05, 'g': 0.12},
        {'k': 'whoosh', 't': 15.58, 'd': 0.5, 'g': 0.09},
        {'k': 'hit', 't': 17.78, 'g': 0.14},
        {'k': 'tick', 't': 19.6, 'g': 0.07}, {'k': 'tick', 't': 19.9, 'g': 0.07},
        {'k': 'tick', 't': 20.2, 'g': 0.07}, {'k': 'tick', 't': 20.5, 'g': 0.07},
    ]
    build_audio(BUILD / 'audio.wav', cues)

    # فحص الجغرافيا الصارم: كل نقطة/تسمية على البَر (ray-casting على geo10)
    checks = [('ميديين', MED), ('ميامي', MIA)] + [(f'نقطة طريق {i+1}', p) for i, p in enumerate(ROAD)]
    bad = 0
    for name, (lat, lon) in checks:
        ok = on_land_geo(lon, lat)
        bad += (not ok)
        print(f"   {'✓ على البَر' if ok else '✗ على البحر!'} {name} ({lat:.2f},{lon:.2f})")
    if bad:
        raise SystemExit('تحقق الجغرافيا فشل — ما منكمّل رندر.')

    total = int(round(DUR * FPS))
    print(f'[i] رندر {total} فريم @ {FPS}fps ...')
    for n in range(total):
        t = n / FPS
        img = None
        for (a, b, fn) in shots:
            if a <= t < b:
                img = fn(t, a, b) if fn.__code__.co_argcount == 4 else fn(t)
                break
        if img is None:
            img = Image.new('RGB', (W, H), BLACK)
        vignette(img).save(FRAMES / f'f{n:04d}.jpg', quality=92)
        if n % 96 == 0:
            print(f'    ... {n}/{total}')
    out = BUILD / 'escobar_ww2drive_demo_v1.mp4'
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, '-y', '-framerate', str(FPS), '-i', str(FRAMES / 'f%04d.jpg'),
                    '-i', str(BUILD / 'audio.wav'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-crf', '19', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', str(out)], check=True, capture_output=True)
    print('[✓] الفيديو:', out, round(out.stat().st_size / 1e6, 2), 'MB')

    picks = [0.8, 2.4, 4.6, 7.2, 9.6, 12.0, 14.2, 16.6, 18.4, 20.3, 22.2]
    cols = 4; rows = math.ceil(len(picks) / cols)
    tw, th = 480, 270
    sheet = Image.new('RGB', (cols * tw, rows * th), (12, 12, 14))
    for i, tp in enumerate(picks):
        im = Image.open(FRAMES / f'f{int(tp * FPS):04d}.jpg').resize((tw, th), Image.LANCZOS)
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(BUILD / 'qc_sheet.jpg', quality=92)
    print('[✓] ملصق الفحص:', BUILD / 'qc_sheet.jpg')

if __name__ == '__main__':
    main()
