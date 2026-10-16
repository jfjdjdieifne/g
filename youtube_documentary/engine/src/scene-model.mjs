// Scene model: resolves a declarative scene JSON + project timeline into a
// fully-scheduled render scene. Also enforces exact-script typography:
// visible tokens must equal the script sentence, word for word.
import fs from 'node:fs';
import path from 'node:path';
import { scheduleWords, validateSchedule, EMPHASIS_DEFAULTS } from './typography.mjs';

export function loadJson(p) { return JSON.parse(fs.readFileSync(p, 'utf8')); }

export function resolveScene({ scenePath, timelinePath, manifestPath }) {
  const scene = loadJson(scenePath);
  const timeline = loadJson(timelinePath);
  const manifest = loadJson(manifestPath);
  const assets = Object.fromEntries(manifest.assets.map(a => [a.id, a]));

  const words = timeline.words.filter(w => w.sentence === scene.sentence);
  if (words.length === 0) throw new Error(`scene ${scene.id}: no words for sentence ${scene.sentence}`);

  // Exact narration check: timeline tokens joined == declared script sentence.
  const joined = words.map(w => w.text).join(' ');
  const tokenCheck = { pass: joined === scene.sentenceText, joined, expected: scene.sentenceText };

  const emphSet = new Set();
  for (const ph of scene.phrases) for (const ix of ph.emphasis || []) emphSet.add(ix);
  const schedule = scheduleWords(words.map(w => ({ text: w.text, start: w.start })), emphSet, EMPHASIS_DEFAULTS, scene.preRoll || 'on_screen');
  const scheduleProblems = validateSchedule(schedule);

  for (const layer of scene.layers || []) {
    if (!assets[layer.asset]) throw new Error(`scene ${scene.id}: unknown asset ${layer.asset}`);
    layer.assetMeta = assets[layer.asset];
  }
  return { scene, words, assets, schedule, tokenCheck, scheduleProblems };
}

export function assetPath(manifestDir, rel) { return path.resolve(manifestDir, rel); }
