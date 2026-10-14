#!/usr/bin/env python3
"""Reference video ingest for frame-level motion analysis.
Runs wherever a reference video file is legally available (sandbox network blocks
video CDNs; user may upload reference files to the project Drive folder).

Outputs (into --outdir):
  <name>_meta.json      duration, fps, resolution (ffprobe)
  <name>_cuts.csv       shot-boundary timestamps (ffmpeg scene detection)
  <name>_sheet_NN.png   contact sheets (grid of frames, --every seconds)
  <name>_clips/         optional short motion samples around cuts (--clips)

Usage:
  python3 reference_ingest.py /path/ref.mp4 --every 2 --outdir reference_frames
Requires ffmpeg (any recent build) and Python3. No network needed.
"""
import argparse, csv, json, os, shutil, subprocess, sys

def ffprobe_bin():
    c = shutil.which('ffprobe')
    return c

def ffmpeg_bin():
    c = shutil.which('ffmpeg')
    if c: return c
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inputs', nargs='+')
    ap.add_argument('--every', type=float, default=2.0, help='contact sheet frame interval (s)')
    ap.add_argument('--scene', type=float, default=0.30, help='scene-change threshold')
    ap.add_argument('--outdir', default='reference_frames')
    ap.add_argument('--cols', type=int, default=5)
    ap.add_argument('--thumb-h', type=int, default=180)
    ap.add_argument('--clips', action='store_true', help='extract 2s clips around each cut')
    a = ap.parse_args()
    ff, fp = ffmpeg_bin(), ffprobe_bin()
    if not ff: sys.exit('ffmpeg required')
    os.makedirs(a.outdir, exist_ok=True)
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit('Pillow required for contact sheets')
    for inp in a.inputs:
        name = os.path.splitext(os.path.basename(inp))[0]
        pr = subprocess.run([ff, '-i', inp], capture_output=True)
        info = pr.stderr.decode('utf8', 'ignore')
        import re as _re
        m = _re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', info)
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0
        fm = _re.search(r'(\d+(?:\.\d+)?) fps', info)
        fps = float(fm.group(1)) if fm else 30.0
        wm = _re.search(r'(\d{3,5})x(\d{3,5})', info)
        json.dump({'file': inp, 'duration': dur, 'fps': fps,
                   'width': int(wm.group(1)) if wm else None, 'height': int(wm.group(2)) if wm else None,
                   'probe': 'ffmpeg -i fallback' if not fp else 'ffprobe'},
                  open(os.path.join(a.outdir, f'{name}_meta.json'), 'w'), indent=2)
        # scene cuts
        pr2 = subprocess.run(
            [ff, '-i', inp, '-an', '-vf',
             f'select=gt(scene\\,{a.scene}),showinfo', '-f', 'null', '-'],
            capture_output=True)
        cuts = pr2.stderr.decode('utf8', 'ignore')
        times = []
        for line in cuts.splitlines():
            if 'pts_time:' in line:
                t = float(line.split('pts_time:')[1].split()[0])
                times.append(round(t, 3))
        with open(os.path.join(a.outdir, f'{name}_cuts.csv'), 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(['cut_time_s', 'shot_len_s'])
            for i, t in enumerate(times):
                nxt = times[i+1] if i+1 < len(times) else dur
                w.writerow([t, round(nxt - t, 3)])
        lens = [round((times[i+1] if i+1 < len(times) else dur) - times[i], 2) for i in range(len(times))]
        if lens:
            lens_sorted = sorted(lens)
            print(f'{name}: {len(times)} cuts · median shot {lens_sorted[len(lens_sorted)//2]}s '
                  f'· p90 {lens_sorted[int(len(lens_sorted)*0.9)]}s')
        # contact sheets
        tmp = os.path.join(a.outdir, f'_{name}_frames'); os.makedirs(tmp, exist_ok=True)
        subprocess.check_call([ff, '-v', 'error', '-i', inp, '-vf',
                               f'fps=1/{a.every},scale=-2:{a.thumb_h}',
                               os.path.join(tmp, 'f%05d.png')])
        frames = sorted(os.listdir(tmp))
        per_sheet = a.cols * 6
        for si in range(0, len(frames), per_sheet):
            batch = frames[si:si+per_sheet]
            rows = (len(batch) + a.cols - 1) // a.cols
            tw = a.thumb_h * 16 // 9
            sheet = Image.new('RGB', (a.cols * tw, rows * a.thumb_h), (10, 10, 10))
            d = ImageDraw.Draw(sheet)
            for i, f in enumerate(batch):
                im = Image.open(os.path.join(tmp, f))
                x, y = (i % a.cols) * tw, (i // a.cols) * a.thumb_h
                sheet.paste(im, (x, y))
                t = (si + i) * a.every
                d.text((x + 6, y + 4), f'{t:.0f}s', fill=(255, 210, 90))
            out = os.path.join(a.outdir, f'{name}_sheet_{si//per_sheet:02d}.png')
            sheet.save(out)
        shutil.rmtree(tmp)
        if a.clips:
            cdir = os.path.join(a.outdir, f'{name}_clips'); os.makedirs(cdir, exist_ok=True)
            for i, t in enumerate(times):
                subprocess.check_call([ff, '-v', 'error', '-ss', str(max(0, t-1)), '-t', '2',
                                       '-i', inp, '-c', 'copy',
                                       os.path.join(cdir, f'cut{i:03d}_{t:.1f}s.mp4')])
        print(f'{name}: {len(frames)} thumbs · {len(times)} cuts → {a.outdir}')

if __name__ == '__main__':
    main()
