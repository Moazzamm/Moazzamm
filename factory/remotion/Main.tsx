import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate, Easing, spring} from 'remotion';
import '@fontsource/anton';
import '@fontsource/inter/700.css';
import '@fontsource/inter/800.css';
import '@fontsource/inter/900.css';
import {Globe} from './Globe';

const C = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const EO = Easing.bezier(0.16, 1, 0.3, 1);
const lerp = (a: number, b: number, p: number) => a + (b - a) * p;

type Beat = {s: number; e: number; img?: string; map?: any; dark?: boolean; k: any; fx?: any; seg: string};
type Item = {rank: number; name: string; place: string; s: number; e: number};

const Media: React.FC<{b: Beat; t: number; accent: string}> = ({b, t, accent}) => {
  const p = interpolate(t, [b.s - 0.25, b.e], [0, 1], C);
  const pe = Easing.inOut(Easing.sin)(p);
  const z = lerp(b.k.z0, b.k.z1, pe) * interpolate(t, [b.s - 0.25, b.s + 0.35], [1.07, 1], {...C, easing: EO});
  const x = lerp(b.k.x0, b.k.x1, pe), y = lerp(b.k.y0, b.k.y1, pe);
  if (b.map) return <Globe m={b.map} t={t - b.s} dur={b.e - b.s} accent={accent} />;
  if (!b.img) return <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #142235, #05070c 75%)'}} />;
  if ((b as any).scope) {
    const lt = t - b.s;
    const scan = ((lt * 0.45) % 1) * 100;
    const mag = Math.round(interpolate(lt, [0, 1.2], [40, 1000], {...C, easing: EO}) / 10) * 10;
    return (
      <AbsoluteFill style={{background: '#020604', overflow: 'hidden'}}>
        <div style={{position: 'absolute', left: 960 - 470, top: 540 - 470, width: 940, height: 940, borderRadius: '50%', overflow: 'hidden',
          boxShadow: `0 0 0 6px #0d1f1a, 0 0 80px ${accent}55, inset 0 0 120px rgba(0,0,0,0.95)`}}>
          <Img src={staticFile(b.img)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z * 1.15}) translate(${x}%, ${y}%)`,
            filter: 'grayscale(0.35) contrast(1.35) saturate(1.4) hue-rotate(-20deg) sepia(0.15)'}} />
          <AbsoluteFill style={{background: `radial-gradient(circle, rgba(0,0,0,0) 55%, rgba(0,0,0,0.9) 72%)`}} />
          <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(0,0,0,0) ${scan - 3}%, ${accent}33 ${scan}%, rgba(0,0,0,0) ${scan + 3}%)`}} />
          <svg width={940} height={940} style={{position: 'absolute', left: 0, top: 0}}>
            <line x1={470} y1={60} x2={470} y2={880} stroke={accent} strokeOpacity={0.35} strokeWidth={2} />
            <line x1={60} y1={470} x2={880} y2={470} stroke={accent} strokeOpacity={0.35} strokeWidth={2} />
            {Array.from({length: 17}, (_, i) => <line key={i} x1={470 - 8} x2={470 + 8} y1={150 + i * 40} y2={150 + i * 40} stroke={accent} strokeOpacity={0.5} strokeWidth={2} />)}
            <circle cx={470} cy={470} r={160} fill="none" stroke={accent} strokeOpacity={0.25} strokeWidth={2} strokeDasharray="6 10" />
          </svg>
        </div>
        <div style={{position: 'absolute', left: 80, top: 470, fontFamily: 'Inter', fontWeight: 900, color: accent, fontSize: 30, letterSpacing: 4, lineHeight: 1.6}}>
          <div>MAG ×{mag.toLocaleString('en-US')}</div><div style={{opacity: 0.6, fontSize: 22}}>FOCUS · LOCKED</div></div>
        <div style={{position: 'absolute', right: 80, top: 470, textAlign: 'right', fontFamily: 'Inter', fontWeight: 900, color: '#fff', opacity: 0.55, fontSize: 22, letterSpacing: 4, lineHeight: 1.8}}>
          <div>● REC</div><div>{(lt * 1000 / 30).toFixed(0).padStart(5, '0')}</div></div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: '#000'}}>
      <Img src={staticFile(b.img)} style={{width: '100%', height: '100%', objectFit: 'cover',
        transform: `scale(${z}) translate(${x}%, ${y}%)`, transformOrigin: `${50 + (b.k.fx ?? 0)}% ${50 + (b.k.fy ?? 0)}%`}} />
    </AbsoluteFill>
  );
};

const Shade: React.FC<{o: number}> = ({o}) => (
  <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(0,0,0,${0.35 * o}) 0%, rgba(0,0,0,${0.55 * o}) 55%, rgba(0,0,0,${0.75 * o}) 100%)`}} />
);

const parseNum = (v: string) => {
  const m = v.match(/^([~$]?)([\d][\d.,]*)(.*)$/);
  if (!m || /[³¹]/.test(v)) return null;
  const n = parseFloat(m[2].replace(/,/g, ''));
  if (!(n >= 5)) return null;
  const dec = (m[2].split('.')[1] || '').length;
  return {pre: m[1], n, dec, comma: m[2].includes(','), suf: m[3]};
};

const Stat: React.FC<{v: string; label: string; t: number; d: number; accent: string}> = ({v, label, t, d, accent}) => {
  const {fps} = useVideoConfig();
  const sp = spring({frame: Math.round(t * fps), fps, config: {damping: 14, mass: 0.7}});
  const out = interpolate(t, [d - 0.3, d], [1, 0], C);
  const pn = parseNum(v);
  let txt = v;
  if (pn) {
    const val = pn.n * interpolate(t, [0, 0.9], [0, 1], {...C, easing: EO});
    const s = val.toFixed(pn.dec);
    txt = pn.pre + (pn.comma ? Number(s).toLocaleString('en-US', {minimumFractionDigits: pn.dec, maximumFractionDigits: pn.dec}) : s) + pn.suf;
  }
  const lab = interpolate(t, [0.25, 0.6], [0, 1], {...C, easing: EO});
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity: out}}>
      <div style={{fontFamily: 'Anton', fontSize: v.length > 9 ? 170 : 230, color: '#fff', transform: `scale(${0.6 + 0.4 * sp})`, opacity: sp,
        textShadow: `0 0 40px ${accent}88, 0 8px 30px rgba(0,0,0,0.8)`, lineHeight: 1, letterSpacing: 2}}>{txt}</div>
      <div style={{width: 520 * lab, height: 10, background: accent, margin: '26px 0 22px', boxShadow: `0 0 24px ${accent}`}} />
      <div style={{fontFamily: 'Inter', fontWeight: 900, fontSize: 46, color: '#fff', letterSpacing: 3, opacity: lab,
        transform: `translateY(${(1 - lab) * 30}px)`, textAlign: 'center', maxWidth: 1400, textShadow: '0 4px 18px #000'}}>{label}</div>
    </AbsoluteFill>
  );
};

const Kinetic: React.FC<{text: string; t: number; d: number; accent: string; big?: boolean}> = ({text, t, d, accent, big}) => {
  const words = text.split(' ');
  const out = interpolate(t, [d - 0.25, d], [1, 0], C);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity: out, padding: '0 140px'}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '10px 30px', maxWidth: 1600}}>
        {words.map((w, i) => {
          const a = interpolate(t, [0.1 + i * 0.09, 0.4 + i * 0.09], [0, 1], {...C, easing: EO});
          const last = i === words.length - 1;
          return <span key={i} style={{fontFamily: 'Anton', fontSize: big ? 150 : 132, lineHeight: 1.05, color: last ? '#111' : '#fff',
            background: last ? accent : 'transparent', padding: last ? '0 18px' : 0, opacity: a,
            transform: `translateY(${(1 - a) * 60}px) scale(${0.8 + 0.2 * a})`, display: 'inline-block',
            textShadow: last ? 'none' : '0 6px 30px rgba(0,0,0,0.9)'}}>{w}</span>;
        })}
      </div>
    </AbsoluteFill>
  );
};

const Title: React.FC<{text: string; series: string; t: number; accent: string}> = ({text, series, t, accent}) => {
  const a = interpolate(t, [0, 0.5], [0, 1], {...C, easing: EO});
  const g = t < 0.35 ? Math.sin(t * 90) * 12 * (0.35 - t) : 0;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <div style={{fontFamily: 'Inter', fontWeight: 900, fontSize: 34, letterSpacing: 14, color: accent, opacity: a, marginBottom: 18}}>{series}</div>
      <div style={{fontFamily: 'Anton', fontSize: 120, color: '#fff', textAlign: 'center', maxWidth: 1500, lineHeight: 1.05,
        transform: `scale(${1.25 - 0.25 * a}) translateX(${g}px)`, opacity: a, textShadow: `${-g / 2}px 0 ${accent}, 0 10px 40px #000`}}>{text}</div>
      <div style={{width: 700 * a, height: 8, background: accent, marginTop: 28}} />
    </AbsoluteFill>
  );
};

const Compare: React.FC<{rows: [string, number][]; unit: string; t: number; accent: string}> = ({rows, unit, t, accent}) => {
  const max = Math.max(...rows.map((r) => r[1]));
  return (
    <AbsoluteFill style={{justifyContent: 'center', padding: '0 170px', gap: 70}}>
      {rows.map(([lab, val], i) => {
        const p = interpolate(t, [0.3 + i * 0.6, 1.5 + i * 0.6], [0, 1], {...C, easing: EO});
        const hl = i === rows.length - 1;
        return (
          <div key={i}>
            <div style={{fontFamily: 'Inter', fontWeight: 900, fontSize: 40, color: '#fff', letterSpacing: 3, marginBottom: 14, opacity: interpolate(t, [i * 0.6, 0.3 + i * 0.6], [0, 1], C)}}>{lab}</div>
            <div style={{display: 'flex', alignItems: 'center', gap: 30}}>
              <div style={{height: 90, width: (1300 * val / max) * p, background: hl ? accent : '#6b7a8c', boxShadow: hl ? `0 0 30px ${accent}` : 'none'}} />
              <div style={{fontFamily: 'Anton', fontSize: 80, color: hl ? accent : '#fff'}}>{Math.round(val * p).toLocaleString('en-US')} {unit}</div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const RankCard: React.FC<{it: Item; t: number; accent: string}> = ({it, t, accent}) => {
  const {fps} = useVideoConfig();
  const sp = spring({frame: Math.round(t * fps), fps, config: {damping: 11, mass: 0.9, stiffness: 160}});
  const out = interpolate(t, [2.25, 2.6], [1, 0], C);
  const nameIn = interpolate(t, [0.3, 0.75], [0, 1], {...C, easing: EO});
  const flash = interpolate(t, [0, 0.18], [0.7, 0], C);
  return (
    <AbsoluteFill style={{opacity: out}}>
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, rgba(0,0,0,0.35), rgba(0,0,0,0.85))'}} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{fontFamily: 'Anton', fontSize: 330, lineHeight: 0.9, color: accent, transform: `scale(${2.2 - 1.2 * sp})`,
          opacity: Math.min(1, sp * 1.5), textShadow: '0 12px 60px rgba(0,0,0,0.9)'}}>
          {it.rank === 1 ? '#1' : `#${it.rank}`}
        </div>
        <div style={{fontFamily: 'Anton', fontSize: 96, color: '#fff', letterSpacing: 3 + (1 - nameIn) * 30, opacity: nameIn, marginTop: 10,
          textAlign: 'center', maxWidth: 1700, textShadow: '0 8px 30px #000'}}>{it.name}</div>
        <div style={{marginTop: 22, opacity: nameIn, fontFamily: 'Inter', fontWeight: 800, fontSize: 34, color: '#ddd', letterSpacing: 6,
          borderTop: `4px solid ${accent}`, paddingTop: 14}}>{it.place}</div>
      </AbsoluteFill>
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    </AbsoluteFill>
  );
};

const Chip: React.FC<{it: Item; t: number; accent: string}> = ({it, t, accent}) => {
  const a = interpolate(t, [2.4, 2.8], [0, 1], {...C, easing: EO});
  const out = interpolate(t, [it.e - it.s - 0.4, it.e - it.s], [1, 0], C);
  return (
    <div style={{position: 'absolute', left: 60, top: 54, display: 'flex', alignItems: 'center', opacity: a * out, transform: `translateX(${(1 - a) * -40}px)`}}>
      <div style={{fontFamily: 'Anton', fontSize: 58, background: accent, color: '#111', padding: '2px 18px'}}>#{it.rank}</div>
      <div style={{fontFamily: 'Inter', fontWeight: 900, fontSize: 28, color: '#fff', background: 'rgba(0,0,0,0.6)', padding: '18px 22px', letterSpacing: 2}}>{it.name}</div>
    </div>
  );
};

const Ladder: React.FC<{cur: number; t: number; accent: string}> = ({cur, accent}) => (
  <div style={{position: 'absolute', right: 56, top: 62, display: 'flex', gap: 8}}>
    {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map((n) => {
      const on = n === cur, done = n > cur;
      return <div key={n} style={{width: 58, height: 58, display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: 'Anton', fontSize: 34, color: on ? '#111' : done ? 'rgba(255,255,255,0.35)' : '#fff',
        background: on ? accent : 'rgba(0,0,0,0.45)', border: `2px solid ${on ? accent : 'rgba(255,255,255,0.25)'}`}}>
        {n === 1 && cur !== 1 ? '?' : n}</div>;
    })}
  </div>
);

const Captions: React.FC<{caps: any[]; t: number; accent: string}> = ({caps, t, accent}) => {
  const c = caps.find((x) => t >= x.s && t < x.e);
  if (!c) return null;
  const a = interpolate(t, [c.s, c.s + 0.12], [0, 1], C);
  return (
    <div style={{position: 'absolute', bottom: 92, width: '100%', display: 'flex', justifyContent: 'center', opacity: a}}>
      <div style={{display: 'flex', columnGap: 24, rowGap: 4, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 1500, padding: '0 40px'}}>
        {c.words.map((w: any, i: number) => {
          const on = t >= w.s && t < w.e + 0.05;
          const said = t >= w.s;
          return <span key={i} style={{fontFamily: 'Inter', fontWeight: 900, fontSize: 64, color: on ? accent : '#fff',
            opacity: said ? 1 : 0.92, transform: `scale(${on ? 1.04 : 1})`, transformOrigin: '50% 80%', display: 'inline-block',
            textShadow: '0 0 6px #000, 0 4px 0 #000, 0 6px 22px rgba(0,0,0,0.9)', WebkitTextStroke: '2px #000'}}>{w.w}</span>;
        })}
      </div>
    </div>
  );
};

const Subscribe: React.FC<{t: number; accent: string; d: number}> = ({t, accent, d}) => {
  const a = interpolate(t, [0, 0.5], [0, 1], {...C, easing: EO});
  const out = interpolate(t, [d - 0.4, d], [1, 0], C);
  const clicked = t > 1.6;
  const cx = interpolate(t, [0.4, 1.5], [1500, 1085], {...C, easing: EO}), cy = interpolate(t, [0.4, 1.5], [900, 640], {...C, easing: EO});
  const press = t > 1.5 && t < 1.7 ? 0.92 : 1;
  const bar = interpolate(t, [1.8, 3.2], [0, 0.02], {...C, easing: EO});
  return (
    <AbsoluteFill style={{opacity: a * out}}>
      <AbsoluteFill style={{background: 'rgba(0,0,0,0.55)'}} />
      <div style={{position: 'absolute', left: 460, top: 360, width: 1000, padding: 44, background: 'rgba(15,15,18,0.92)', borderRadius: 26,
        transform: `translateY(${(1 - a) * 60}px)`, border: '2px solid rgba(255,255,255,0.08)'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 30}}>
          <div style={{width: 110, height: 110, borderRadius: 55, background: accent, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Anton', fontSize: 58, color: '#111'}}>?!</div>
          <div style={{flex: 1, fontFamily: 'Inter', fontWeight: 900, fontSize: 44, color: '#fff'}}>Help us reach 10,000</div>
          <div style={{transform: `scale(${press})`, background: clicked ? '#3a3a3a' : '#ff0033', color: '#fff', fontFamily: 'Inter', fontWeight: 900,
            fontSize: 34, padding: '20px 34px', borderRadius: 40, letterSpacing: 1}}>{clicked ? 'SUBSCRIBED ✓' : 'SUBSCRIBE'}</div>
        </div>
        <div style={{marginTop: 36, height: 22, background: 'rgba(255,255,255,0.12)', borderRadius: 11, overflow: 'hidden'}}>
          <div style={{width: `${Math.max(1.5, bar * 100)}%`, height: '100%', background: accent}} />
        </div>
        <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 12, fontFamily: 'Inter', fontWeight: 800, fontSize: 26, color: '#aaa'}}>
          <span>ROAD TO 10K</span><span>YOU'RE PART OF IT</span></div>
      </div>
      <svg style={{position: 'absolute', left: cx, top: cy}} width={60} height={60} viewBox="0 0 24 24"><path d="M3 2l7 19 2.5-7.5L20 11z" fill="#fff" stroke="#000" strokeWidth={1.2} /></svg>
    </AbsoluteFill>
  );
};

const EndCard: React.FC<{t: number; tl: any}> = ({t, tl}) => {
  const a = interpolate(t, [0, 0.6], [0, 1], {...C, easing: EO});
  return (
    <AbsoluteFill style={{opacity: a}}>
      <AbsoluteFill style={{background: 'rgba(3,5,9,0.78)'}} />
      <div style={{position: 'absolute', left: 120, top: 150, fontFamily: 'Inter', fontWeight: 900, fontSize: 44, color: tl.accent, letterSpacing: 8}}>WATCH NEXT</div>
      <div style={{position: 'absolute', left: 120, top: 230, width: 1000, height: 562, border: `6px solid ${tl.accent}`, overflow: 'hidden', transform: `scale(${0.94 + 0.06 * a})`, boxShadow: `0 0 60px ${tl.accent}55`}}>
        {tl.next?.img && <Img src={staticFile(tl.next.img)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.05 + t * 0.006})`}} />}
        <AbsoluteFill style={{background: 'linear-gradient(0deg, rgba(0,0,0,0.85), rgba(0,0,0,0) 60%)'}} />
        <div style={{position: 'absolute', left: 36, bottom: 28, right: 36, fontFamily: 'Anton', fontSize: 70, color: '#fff', lineHeight: 1.05}}>{tl.next?.title}</div>
      </div>
      <div style={{position: 'absolute', left: 1330, top: 300, width: 400, height: 400, borderRadius: 200, border: '6px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: 'Anton', fontSize: 64, color: '#fff', background: 'rgba(255,0,51,0.85)', transform: `scale(${0.9 + 0.1 * a})`}}>SUBSCRIBE</div>
    </AbsoluteFill>
  );
};

export const Main: React.FC<any> = (tl) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const beats: Beat[] = tl.beats;
  const vis = beats.filter((b) => t >= b.s - 0.25 && t < b.e + 0.02);
  const item: Item | undefined = tl.items.find((it: Item) => t >= it.s && t < it.e);
  const cur = item ? item.rank : (tl.items.filter((it: Item) => t >= it.e).length ? 0 : 11);
  const inCard = item && t - item.s < 2.45;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {vis.map((b) => (
        <AbsoluteFill key={b.s} style={{opacity: interpolate(t, [b.s - 0.25, b.s + 0.02], [0, 1], C)}}>
          <Media b={b} t={t} accent={tl.accent} />
        </AbsoluteFill>
      ))}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.6) 100%)'}} />
      {vis.filter((b) => b.fx && t >= b.s).map((b) => {
        const lt = t - b.s, d = b.e - b.s, fx = b.fx;
        const sh = interpolate(lt, [0, 0.3, d - 0.3, d], [0, 1, 1, 0], C);
        return (
          <AbsoluteFill key={'fx' + b.s}>
            {!fx.sub && !fx.end && <Shade o={sh} />}
            {fx.stat && <Stat v={fx.stat[0]} label={fx.stat[1]} t={lt - 0.15} d={d - 0.15} accent={tl.accent} />}
            {fx.text && <Kinetic text={fx.text} t={lt - 0.1} d={d - 0.1} accent={tl.accent} />}
            {fx.title && <Title text={fx.title} series={tl.series} t={lt} accent={tl.accent} />}
            {fx.compare && <Compare rows={fx.compare} unit={fx.unit} t={lt} accent={tl.accent} />}
            {fx.sub && <Subscribe t={lt} d={d} accent={tl.accent} />}
            {fx.end && <EndCard t={lt} tl={tl} />}
          </AbsoluteFill>
        );
      })}
      {item && !inCard && <Ladder cur={item.rank} t={t} accent={tl.accent} />}
      {item && <Chip it={item} t={t - item.s} accent={tl.accent} />}
      {item && inCard && <RankCard it={item} t={t - item.s} accent={tl.accent} />}
      {!inCard && !vis.some((b) => b.fx?.title && t >= b.s) && <Captions caps={tl.captions} t={t} accent={tl.accent} />}
      <AbsoluteFill style={{backgroundImage: `url(${staticFile('grain.png')})`, backgroundPosition: `${(frame * 137) % 512}px ${(frame * 291) % 512}px`, opacity: 0.045, mixBlendMode: 'overlay'}} />
    </AbsoluteFill>
  );
};

export const Thumb: React.FC<any> = (p) => (
  <AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
    <Img src={staticFile(p.img)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${p.zoom ?? 1.1}) translateX(${p.tx ?? 0}%)`, transformOrigin: p.origin ?? '50% 50%',
      filter: `contrast(1.18) saturate(1.3) brightness(${p.bright ?? 0.95})`}} />
    <AbsoluteFill style={{background: p.side === 'right' ? 'linear-gradient(270deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 62%)' : 'linear-gradient(90deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 62%)'}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 50%, rgba(0,0,0,0.7) 100%)'}} />
    <div style={{position: 'absolute', [p.side === 'right' ? 'right' : 'left']: 50, top: 70, width: 640, display: 'flex', flexDirection: 'column', gap: 6,
      alignItems: p.side === 'right' ? 'flex-end' : 'flex-start'}}>
      {p.lines.map((l: any, i: number) => (
        <div key={i} style={{fontFamily: 'Anton', fontSize: l.size ?? 128, lineHeight: 0.98, color: l.bg ? '#111' : (l.color ?? '#fff'), background: l.bg ?? 'transparent',
          padding: l.bg ? '4px 18px' : 0, textShadow: l.bg ? 'none' : '0 0 2px #000, 5px 5px 0 #000, 0 10px 30px rgba(0,0,0,0.9)', transform: `rotate(${l.rot ?? 0}deg)`}}>{l.t}</div>
      ))}
    </div>
    {p.badge && <div style={{position: 'absolute', right: p.side === 'right' ? undefined : 40, left: p.side === 'right' ? 40 : undefined, bottom: 40, fontFamily: 'Anton', fontSize: 64,
      color: '#fff', background: '#e00', padding: '6px 22px', transform: 'rotate(-3deg)', boxShadow: '0 6px 20px rgba(0,0,0,0.6)'}}>{p.badge}</div>}
    {p.circle && <div style={{position: 'absolute', left: p.circle[0], top: p.circle[1], width: p.circle[2], height: p.circle[2], borderRadius: '50%',
      border: '12px solid #ff2a2a', boxShadow: '0 0 30px rgba(255,0,0,0.8), inset 0 0 20px rgba(255,0,0,0.5)'}} />}
  </AbsoluteFill>
);
