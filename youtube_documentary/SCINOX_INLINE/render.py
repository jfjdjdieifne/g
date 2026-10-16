from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path
import subprocess, imageio_ffmpeg, math

ROOT=Path(__file__).parent
W,H=1920,1080
NAVY=(8,20,35); PANEL=(15,34,52); CYAN=(74,211,220); WHITE=(238,244,247); MUTED=(167,187,199); ORANGE=(255,174,82)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
chapters=[
 ('خلاط ساينكس الخطي','شرح تعليمي عن الموديل آي إم إس سي','مبدأ العمل • الفك والتركيب • التصنيع • الصيانة','تحقق من دليل موديلك قبل أي تدخل'),
 ('كيف يتحرك المنتج؟','مسار العملية','دخول المنتج  ←  غرفة التجانس  ←  الخروج','الدوّار يسحب ويدفع؛ والستاتور يحقق التجانس'),
 ('رأس التجانس','Rotor + Stator','دوّار متحرك داخل ستاتور ثابت','القصّ العالي يخفف التكتلات ويحسن التجانس'),
 ('المكوّنات الرئيسية','حسب وصف Scinox','غرفة التجانس  •  رأس التجانس  •  قاعدة بأرجل قابلة للضبط','المضخة والأختام والتجميعة تختلف حسب التكوين'),
 ('قبل الفك: اعزل الطاقة','سلامة أولاً','إيقاف • عزل كهربائي • قفل وبطاقة • تفريغ الضغط','تحقق من الصفر والطراوة الحرارية قبل الفتح'),
 ('الفك: لا تعتمد على التخمين','الترتيب من دليل الموديل','وثّق الاتجاه  •  استخدم الأداة المناسبة  •  لا تضرب العمود','تسلسل الفك الدقيق غير منشور على صفحة المنتج'),
 ('التركيب والتحقق','اتبع مواصفات المصنع','أختام مطابقة • محاذاة • عزم وخلوص موثّقان','لا تخمّن العزم أو الخلوص؛ اختبر حسب بروتوكول الموقع'),
 ('التصنيع: ما هو منشور','مواد وتشطيب','316L لملامسة المنتج  •  304 للأجزاء غير الملامسة','لحام TIG ومداري • داخل مرآتي • خارج مطفي'),
 ('التنظيف والصيانة','حافظ على حالة المعدّة','افحص التسريب والاهتزاز والأختام والأسطح','لا مواد كاشطة؛ نظّف وفق إجراء معتمد ومتحقق منه'),
 ('الخلاصة','شرح عام وليس كتيب خدمة','المبدأ واضح؛ أما الفك والتصنيع التفصيلي فمرجعهما المصنع','Scinox I-MSC  |  راجع الوثائق المعتمدة لمعدتك')]

def rtl(s): return get_display(arabic_reshaper.reshape(s))
def txt(draw, xy, s, font, fill, anchor=None): draw.text(xy,rtl(s),font=font,fill=fill,anchor=anchor)

def make(i,ch):
 im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im)
 # geometric continuous-flow motif
 d.rectangle((0,0,18,H),fill=CYAN); d.line((95,155,1820,155),fill=(34,66,83),width=2)
 d.ellipse((1540,-260,2110,310),outline=(18,57,72),width=5)
 d.text((105,72),'SCINOX  /  I-MSC',font=ImageFont.truetype(BOLD,25),fill=CYAN)
 d.text((1795,75),f'{i+1:02d}  /  10',font=ImageFont.truetype(BOLD,23),fill=MUTED,anchor='ra')
 # headline/right aligned
 txt(d,(1770,250),ch[0],ImageFont.truetype(BOLD,59),WHITE,anchor='ra')
 d.text((1090,335),ch[1],font=ImageFont.truetype(BOLD,27),fill=CYAN,anchor='ra')
 # graphic zone
 box=(140,420,1780,810); d.rounded_rectangle(box,radius=30,fill=PANEL,outline=(34,68,85),width=2)
 if i in (0,1,2,3,5,6,9):
  p=ROOT/'rotor_stator.png'
  if p.exists():
   diag=Image.open(p).convert('RGB'); diag.thumbnail((850,340)); im.paste(diag,(170,455))
  # explanatory nodes overlay on right side
  labels={0:['غرفة التجانس','دوّار','ستاتور'],1:['دخول','قصّ عالي','خروج'],2:['محور الدوران','فجوة القصّ','ستاتور ثابت'],3:['غرفة','رأس التجانس','قاعدة'],5:['فك حسب الدليل','حماية الأسطح','تجنّب الصدمات'],6:['فحص الأختام','محاذاة','تحقق آمن'],9:['المبدأ','السلامة','الوثائق']}.get(i,[])
  for j,label in enumerate(labels):
   y=505+j*92; d.rounded_rectangle((1110,y,1680,y+62),radius=16,fill=(23,51,67),outline=(44,95,108),width=2)
   txt(d,(1640,y+16),label,ImageFont.truetype(BOLD,23),WHITE,anchor='ra')
   d.ellipse((1130,y+20,1150,y+40),fill=[CYAN,ORANGE,(118,179,255)][j%3])
 else:
  # simplified manufacture/maintenance infographic
  labels=({4:['فصل الكهرباء','عزل الخطوط','صفر ضغط وطاقة'],7:['316L تماس المنتج','لحام TIG / مداري','تشطيب داخلي مرآتي'],8:['تسريب / اهتزاز','أختام وأسـطح','تنظيف معتمد']}[i])
  for j,label in enumerate(labels):
   x=250+j*500; d.ellipse((x,490,x+300,700),fill=(20,50,66),outline=[CYAN,ORANGE,(118,179,255)][j],width=5)
   txt(d,(x+150,570),label,ImageFont.truetype(BOLD,27),WHITE,anchor='mm')
   if j<2: d.line((x+320,595,x+455,595),fill=CYAN,width=7); d.polygon([(x+455,595),(x+430,578),(x+430,612)],fill=CYAN)
 # key message
 txt(d,(1760,890),ch[2],ImageFont.truetype(BOLD,30),WHITE,anchor='ra')
 txt(d,(1760,960),ch[3],ImageFont.truetype(FONT,24),MUTED,anchor='ra')
 d.line((100,1010,1810,1010),fill=(34,66,83),width=2)
 d.text((105,1032),'EDUCATIONAL OVERVIEW  •  OEM MANUAL CONTROLS SERVICE WORK',font=ImageFont.truetype(BOLD,16),fill=(133,159,173))
 path=ROOT/f'frame_{i:02d}.png'; im.save(path); return path

files=[make(i,c) for i,c in enumerate(chapters)]
ff=imageio_ffmpeg.get_ffmpeg_exe()
# total narration duration is 254.7 seconds. The visual chapter beats follow the continuous narration.
concat=ROOT/'frames.txt'
with concat.open('w') as f:
 for p in files:
  f.write(f"file '{p.as_posix()}'\n")
  f.write('duration 25.47\n')
 f.write(f"file '{files[-1].as_posix()}'\n")
# Create consistent pacing, then mux sequential narration clips.
subprocess.run([ff,'-y','-f','concat','-safe','0','-i',str(concat),'-vsync','vfr','-pix_fmt','yuv420p','-c:v','libx264','-preset','medium','-crf','21',str(ROOT/'visuals.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run([ff,'-y','-i',str(ROOT/'narration_ar.mp3'),'-i',str(ROOT/'narration_ar_part2.mp3'),'-filter_complex','[0:a][1:a]concat=n=2:v=0:a=1[a]','-map','[a]','-b:a','128k',str(ROOT/'voice_full.mp3')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run([ff,'-y','-i',str(ROOT/'visuals.mp4'),'-i',str(ROOT/'voice_full.mp3'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(ROOT/'Scinox_I-MSC_Explainer_AR.mp4')],check=True)
print('Rendered',ROOT/'Scinox_I-MSC_Explainer_AR.mp4')
