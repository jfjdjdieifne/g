// Basic visual quality gates (Gate A assets + Gate B composition inputs).
// Measurable checks only; artistic review remains a human/agent visual pass.
export function qcAssets(scene, assets, { maxUpscale = 2.5 } = {}) {
  const findings = [];
  for (const layer of scene.layers || []) {
    const a = assets[layer.asset];
    if (!a) { findings.push({ level: 'FAIL', code: 'ASSET_MISSING', msg: layer.asset }); continue; }
    if (a.status === 'storyboard_only') findings.push({ level: 'WARN', code: 'ASSET_STORYBOARD_ONLY', msg: `${a.id}: replace with licensed full-res before production` });
    if (layer.displayWidthPx) {
      const up = layer.displayWidthPx / a.width;
      if (up > maxUpscale) findings.push({ level: 'WARN', code: 'ASSET_UPSCALE', msg: `${a.id}: upscale ${up.toFixed(2)}x > ${maxUpscale}x` });
    }
    if (/placeholder|rectangle|icon/i.test(a.type || '')) findings.push({ level: 'FAIL', code: 'PLACEHOLDER_ASSET', msg: a.id });
  }
  return findings;
}

/** measure: { textRects:[{text,x,y,w,h}], subjectRects:[{id,x,y,w,h}] } in 1920x1080 space. */
export function qcLayout(measure, { width = 1920, height = 1080, safe = 40, maxSubjectTextOverlap = 0.30 } = {}) {
  const findings = [];
  const rs = measure.textRects || [];
  for (const r of rs) {
    if (r.x < safe || r.y < safe || r.x + r.w > width - safe || r.y + r.h > height - safe)
      findings.push({ level: 'FAIL', code: 'TEXT_OUTSIDE_SAFE', msg: `${r.text} @${Math.round(r.x)},${Math.round(r.y)}` });
    if (r.w <= 0 || r.h <= 0) findings.push({ level: 'FAIL', code: 'TEXT_EMPTY_RECT', msg: r.text });
  }
  for (let i = 0; i < rs.length; i++) for (let j = i + 1; j < rs.length; j++) {
    const a = rs[i], b = rs[j];
    const ox = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x));
    const oy = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
    if (ox * oy > 4) findings.push({ level: 'FAIL', code: 'TEXT_OVERLAP', msg: `${a.text} x ${b.text}` });
  }
  for (const s of measure.subjectRects || []) {
    for (const r of rs) {
      const ox = Math.max(0, Math.min(s.x + s.w, r.x + r.w) - Math.max(s.x, r.x));
      const oy = Math.max(0, Math.min(s.y + s.h, r.y + r.h) - Math.max(s.y, r.y));
      const frac = (ox * oy) / Math.max(1, r.w * r.h);
      if (frac > maxSubjectTextOverlap) findings.push({ level: 'WARN', code: 'TEXT_OVER_SUBJECT', msg: `${r.text} covers ${(frac * 100).toFixed(0)}% over ${s.id}` });
    }
  }
  return findings;
}

export function gateStatus(findings) {
  if (findings.some(f => f.level === 'FAIL')) return 'FAIL';
  if (findings.some(f => f.level === 'WARN')) return 'PASS_WITH_WARNINGS';
  return 'PASS';
}
