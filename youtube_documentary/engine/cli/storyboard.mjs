// Storyboard renderer + Gate A/B QC driver.
// Usage: DEPS_DIR=/tmp/probe3 LD_LIBRARY_PATH=/tmp/deblibs node storyboard.mjs <scene.json> <projectDir> <outDir>
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { resolveScene } from '../src/scene-model.mjs';
import { qcAssets, qcLayout, gateStatus } from '../src/qc.mjs';

const [scenePath, projectDir, outDir] = process.argv.slice(2);
if (!scenePath || !projectDir || !outDir) { console.error('args: <scene.json> <projectDir> <outDir>'); process.exit(2); }
const DEPS = process.env.DEPS_DIR || '/tmp/probe3';
const require = createRequire(path.join(DEPS, 'package.json'));
const puppeteer = require('puppeteer-core');
const timelinePath = path.join(projectDir, '../../../renders/vo_full/timeline.json');
const manifestPath = path.join(projectDir, 'assets.manifest.json');
const { scene, words, assets, schedule, tokenCheck, scheduleProblems } =
  resolveScene({ scenePath: path.resolve(scenePath), timelinePath, manifestPath });

const sceneDir = path.dirname(path.resolve(scenePath));
const resolved = JSON.parse(JSON.stringify(scene));
for (const L of resolved.layers) L.fileUrl = 'file://' + path.resolve(sceneDir, L.file);
resolved.words = words.map(w => ({ text: w.text, start: w.start }));
resolved.schedule = schedule;

fs.mkdirSync(outDir, { recursive: true });
const findings = [];
if (!tokenCheck.pass) findings.push({ level: 'FAIL', code: 'TOKEN_MISMATCH', msg: tokenCheck.joined });
for (const p of scheduleProblems) findings.push({ level: 'FAIL', code: 'SYNC_SCHEDULE', msg: p });
findings.push(...qcAssets(scene, assets));

let browser;
try {
  const chromiumPkg = require('@sparticuz/chromium');
  const exe = await (chromiumPkg.default || chromiumPkg).executablePath();
  browser = await puppeteer.launch({
    args: [...(chromiumPkg.default || chromiumPkg).args, '--no-sandbox', '--allow-file-access-from-files',
           '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-dev-shm-usage'],
    executablePath: exe, headless: true });
} catch (e) { console.error('launch failed', e); process.exit(1); }

const page = await browser.newPage();
await page.setViewport({ width: 1920, height: 1080 });
page.on('pageerror', e => console.log('[pageerror]', String(e).slice(0, 200)));
const runtimeUrl = 'file://' + path.resolve(new URL('.', import.meta.url).pathname, '../runtime/scene.html');
await page.goto(runtimeUrl, { waitUntil: 'load', timeout: 60000 });
await page.evaluate(`window.__boot(${JSON.stringify(resolved)})`);
await page.waitForFunction('window.__engine && window.__engine.ready', { timeout: 30000 });

const measures = {};
for (const t of scene.storyboardTimes) {
  await page.evaluate(`window.__setTime(${t})`);
  const name = `sb_t${t.toFixed(2).replace('.', '_')}.png`;
  await page.screenshot({ path: path.join(outDir, name), type: 'png' });
  measures[name] = await page.evaluate('window.__measure()');
  const lay = qcLayout(measures[name]);
  findings.push(...lay.map(f => ({ ...f, frame: name })));
  console.log('shot', name, '| text rects:', measures[name].textRects.length, '| layout findings:', lay.length);
}
await browser.close();

const report = { scene: scene.id, strategy: scene.strategy, tokenCheck, schedule,
                 findings, gateAB: gateStatus(findings), measures };
fs.writeFileSync(path.join(outDir, 'qc_report.json'), JSON.stringify(report, null, 2));
console.log('GATE A/B:', report.gateAB, '| findings:', findings.length);
for (const f of findings) console.log(' ', f.level, f.code, '-', f.msg);
