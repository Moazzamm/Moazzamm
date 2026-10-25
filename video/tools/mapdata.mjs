// Precompute world map SVG paths + pin coordinates (Natural Earth projection, 1920x1080).
import fs from 'fs';
import { geoNaturalEarth1, geoPath, geoGraticule10 } from 'd3-geo';
import { feature, mesh } from 'topojson-client';
const world = JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-50m.json'));
const proj = geoNaturalEarth1().fitExtent([[40, 60], [1880, 1040]], { type: 'Sphere' });
const path = geoPath(proj);
const land = feature(world, world.objects.land);
const borders = mesh(world, world.objects.countries, (a, b) => a !== b);
const pins = {
  jamestown: [-76.78, 37.21], indiana: [-86.9, 38.1], london: [-0.12, 51.5], kew: [-0.12, 51.5],
  caribbean: [-80.5, 25.2], pennsylvania: [-77.6, 40.9], athens: [23.72, 37.98], lahore: [74.35, 31.55],
  la: [-118.24, 34.05], srilanka: [80.7, 7.9], italy: [11.25, 43.77], scotland: [-3.4, 56.6], waterloo: [-0.115, 51.508],
};
const P = {}; for (const [k, v] of Object.entries(pins)) P[k] = proj(v).map(n => +n.toFixed(1));
const data = { land: path(land), borders: path(borders), grat: path(geoGraticule10()), sphere: path({ type: 'Sphere' }), pins: P };
fs.writeFileSync('build/mapdata.js', 'window.MAP=' + JSON.stringify(data) + ';');
console.log('map ok', (fs.statSync('build/mapdata.js').size / 1024).toFixed(0) + 'KB', P);
