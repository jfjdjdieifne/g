// Deterministic camera director: keyframed position/lookAt/fov with smoothstep
// interpolation. Pure function of time — no randomness, no wall-clock.
export const clamp01 = (x) => Math.max(0, Math.min(1, x));
export const smoothstep = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
export const easeInOut = smoothstep;

function lerp(a, b, t) { return a + (b - a) * t; }
function lerp3(a, b, t) { return [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)]; }

/** keys: [{t, pos:[x,y,z], look:[x,y,z], fov}] sorted by t. */
export function cameraPose(keys, t) {
  if (!keys || keys.length === 0) throw new Error('camera: no keyframes');
  if (t <= keys[0].t) return clone(keys[0]);
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1];
    if (t >= a.t && t <= b.t) {
      const u = smoothstep((t - a.t) / (b.t - a.t));
      return { pos: lerp3(a.pos, b.pos, u), look: lerp3(a.look, b.look, u), fov: lerp(a.fov ?? 40, b.fov ?? 40, u) };
    }
  }
  return clone(keys[keys.length - 1]);
}
function clone(k) { return { pos: [...k.pos], look: [...k.look], fov: k.fov ?? 40 }; }

/** opacity/property track: keys [[t, value], ...] with smoothstep between. */
export function trackValue(keys, t) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [ta, va] = keys[i], [tb, vb] = keys[i + 1];
    if (t >= ta && t <= tb) return lerp(va, vb, smoothstep((t - ta) / (tb - ta)));
  }
  return keys[keys.length - 1][1];
}
