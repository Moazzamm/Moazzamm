import {feature, mesh} from 'topojson-client';
import landTopo from 'world-atlas/land-110m.json';
import countriesTopo from 'world-atlas/countries-110m.json';
import type {FeatureCollection, MultiLineString} from 'geojson';

// Natural Earth 1:110m via world-atlas (public domain).
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const lt = landTopo as any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ct = countriesTopo as any;
export const LAND = feature(lt, lt.objects.land) as unknown as FeatureCollection;
export const BORDERS = mesh(ct, ct.objects.countries, (a: unknown, b: unknown) => a !== b) as unknown as MultiLineString;

// The four locations (lon, lat). Sources: NPS, Christner et al. 2014 drill site, NHM, Commons/ASTER metadata.
export const PLACES = {
  ccz: {lon: -128, lat: 12, name: 'Clarion-Clipperton Zone', barrier: 'Water'},
  whillans: {lon: -153.694, lat: -84.24, name: 'Subglacial Lake Whillans', barrier: 'Ice'},
  lechuguilla: {lon: -104.45, lat: 32.17, name: 'Lechuguilla Cave', barrier: 'Rock'},
  mabu: {lon: 36.4, lat: -16.3, name: 'Mount Mabu', barrier: 'Forest'},
};
