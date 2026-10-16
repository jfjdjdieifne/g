// Typography director (timing core). Given forced-alignment word onsets and a
// phrase spec, schedule every word so its entrance animation COMPLETES
// (fully readable state) at or before its spoken onset. Emphasized words get
// a deliberate anticipation; standard words land exactly on onset.
// No universal offset: duration and lead are per-emphasis-class parameters.
export const EMPHASIS_DEFAULTS = {
  emphasized: { duration: 0.26, lead: 0.06 },
  standard:   { duration: 0.34, lead: 0.0 },
};

/**
 * words: [{text, start}] global indices preserved. emphSet: Set of word indices.
 * preRoll policy (explicit only, per scene):
 *  - "on_screen": words that cannot finish before frame zero are fully
 *    readable AT t=0 (the scene opener holds them on screen; any global
 *    fade-in from black provides their entrance).
 *  - "compress": clamp animStart to 0 and shorten duration so `readable`
 *    still lands exactly on its scheduled time (never after onset).
 */
export function scheduleWords(words, emphSet = new Set(), params = EMPHASIS_DEFAULTS, preRoll = 'on_screen') {
  return words.map((w, i) => {
    const emph = emphSet.has(i);
    const p = emph ? params.emphasized : params.standard;
    let readable = w.start - p.lead;
    let animStart = readable - p.duration;
    let duration = p.duration;
    let onScreenAtZero = false;
    if (animStart < 0) {
      if (preRoll === 'on_screen') {
        readable = Math.min(readable, w.start);
        if (readable <= 0) { readable = 0; onScreenAtZero = true; animStart = 0; duration = 0; }
        else { duration = readable; animStart = 0; }
      } else { // compress
        duration = readable; animStart = 0;
        if (duration <= 0) { duration = 0; readable = 0; onScreenAtZero = true; }
      }
    }
    return {
      index: i, text: w.text, onset: w.start,
      animStart, readable, duration,
      deltaMs: Math.round((readable - w.start) * 1000), emphasized: emph, onScreenAtZero,
    };
  });
}

/** Validate schedule: readable never after onset; no negative animStart. */
export function validateSchedule(schedule) {
  const problems = [];
  for (const s of schedule) {
    if (s.readable > s.onset + 0.001) problems.push(`${s.text}: readable ${s.readable.toFixed(3)} after onset ${s.onset.toFixed(3)}`);
    if (s.animStart < -0.0001) problems.push(`${s.text}: animStart ${s.animStart.toFixed(3)} < 0 (needs preRoll policy)`);
  }
  return problems;
}
