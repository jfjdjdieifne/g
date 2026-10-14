import fs from 'fs';
import { feature } from 'topojson-client';
const topo = JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-10m.json', 'utf8'));
const fc = feature(topo, topo.objects.countries);
const WANT = new Set(['170','862','591','218','604','76','188','558','340','320','484','192','840','630','332','214','388','780']); // ISO numeric
const out = {};
for (const f of fc.features) {
  const id = String(f.id);
  if (!WANT.has(id)) continue;
  out[id] = f.geometry;
}
fs.mkdirSync('/home/user/build/geo10', { recursive: true });
fs.writeFileSync('/home/user/build/geo10/countries.json', JSON.stringify(out));
// ملاحظة: 10m = أدق ملف متاح بمكتبة world-atlas
const byName = {};
const nameMap = {'170':'COL','862':'VEN','591':'PAN','218':'ECU','604':'PER','76':'BRA','188':'CRI','558':'NIC','340':'HND','320':'GTM','484':'MEX','192':'CUB','840':'USA','630':'PRI','332':'HTI','214':'DOM','388':'JAM','780':'TTO'};
for (const [k,v] of Object.entries(out)) byName[nameMap[k]] = v;
fs.writeFileSync('/home/user/build/geo10/by_code.json', JSON.stringify(byName));
console.log('countries:', Object.keys(byName).length, 'size', fs.statSync('/home/user/build/geo10/by_code.json').size);
