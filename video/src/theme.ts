// Editorial palette. Amber is reserved for uncertainty or a key measurement.
export const C = {
  navy: '#0B1426',
  navy2: '#13213A',
  navy3: '#1D3050',
  paper: '#F2EDE4',
  paperDim: 'rgba(242,237,228,0.62)',
  paperFaint: 'rgba(242,237,228,0.18)',
  cyan: '#8FD3E8',
  cyanDim: 'rgba(143,211,232,0.35)',
  amber: '#E8A33D',
  amberDim: 'rgba(232,163,61,0.35)',
  ice: '#DCEBF2',
  rock: '#3A3430',
};

export const FONT = "'Inter', 'Inter Display', system-ui, sans-serif";

export const W = 854;
export const H = 480;
// Everything informational stays above this line; captions live below it.
export const SAFE_BOTTOM = 400;

export const T = {
  kicker: {fontFamily: FONT, fontSize: 11, letterSpacing: 2.2, fontWeight: 600, textTransform: 'uppercase' as const},
  label: {fontFamily: FONT, fontSize: 13, fontWeight: 500, lineHeight: 1.3},
  small: {fontFamily: FONT, fontSize: 10.5, fontWeight: 400, lineHeight: 1.35},
  stat: {fontFamily: FONT, fontSize: 40, fontWeight: 700, letterSpacing: -1},
  title: {fontFamily: FONT, fontSize: 34, fontWeight: 700, letterSpacing: -0.8, lineHeight: 1.1},
};
