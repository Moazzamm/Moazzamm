import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, DISPLAY, TEXT} from '../theme';
import {ramp, lerp, win, easeOut, shake, pop, rnd} from '../lib/anim';
import {beats, cueFrame, type SceneTiming} from '../lib/timing';
import {Snailfish, Amphipod, Isopod, ColossalSquid, Glow} from '../components/Creatures';
import {ZoneTitle} from '../components/Ocean';
import {BigStat, Tag, Panel, RealInsert} from '../components/Ui';

// ---------- WHY ----------
export const whyDepth = (s: SceneTiming, f: number) => lerp(2600, 4200, ramp(f, 0, s.durationInFrames, 0, 1, (t) => t));

const Card: React.FC<{n: number; title: string; line: string; x: number; y: number; at: number; until: number; children: React.ReactNode}> = ({n, title, line, x, y, at, until, children}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const sp = pop(f, at);
  const o = 1 - ramp(f, until - 10, 10);
  return (
    <div style={{position: 'absolute', left: x, top: y, width: 500, height: 210, opacity: o, transform: `scale(${Math.min(sp, 1.04)})`, background: 'rgba(4,20,34,0.78)', border: '1px solid rgba(92,242,224,0.35)', borderRadius: 14, overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: 24, top: 18, fontFamily: DISPLAY, fontWeight: 800, fontSize: 52, color: C.cyan}}>{n}</div>
      <div style={{position: 'absolute', left: 80, top: 26, fontFamily: DISPLAY, fontWeight: 800, fontSize: 30, color: C.white, textTransform: 'uppercase'}}>{title}</div>
      <div style={{position: 'absolute', left: 80, top: 66, width: 230, fontFamily: TEXT, fontSize: 16, color: C.dim, lineHeight: 1.35}}>{line}</div>
      <div style={{position: 'absolute', right: 0, top: 0, width: 200, height: 210}}>{children}</div>
    </div>
  );
};

export const Why: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    so: ['So why are there'], sci: ['Scientists call it'], honest: ['And the honest answer'], four: ['There are four leading'],
    cold: ['The cold.'], oxy: ['Oxygen.'], hunger: ['Hunger.'], time: ['Time.'], but: ["But here's what most videos"], tiny: ['Most life on the deep'], groups: ['Gigantism shows up'], enormous: ['It makes a few things'],
  });
  const gridOut = b.but;
  const beat = (t: number, rate: number) => Math.max(0, Math.sin(t * rate)) ** 8;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{opacity: win(f, 0, b.four + 10, 10), alignItems: 'center', justifyContent: 'center'}}>
        <div style={{transform: `scale(${pop(f, 6)})`, fontFamily: DISPLAY, fontWeight: 800, fontSize: 92, color: C.white, textShadow: '0 6px 40px rgba(0,0,0,0.7)'}}>WHY GIANTS?</div>
        <div style={{marginTop: 10, opacity: ramp(f, b.sci, 10), fontFamily: TEXT, fontWeight: 700, letterSpacing: 6, color: C.cyan, fontSize: 20}}>DEEP-SEA GIGANTISM</div>
        <div style={{marginTop: 14, opacity: ramp(f, b.honest, 10), fontFamily: TEXT, fontWeight: 600, letterSpacing: 2, color: C.amber, fontSize: 16}}>NO SINGLE ANSWER · FOUR LEADING IDEAS</div>
      </AbsoluteFill>

      <Card n={1} title="Cold" line="Slow metabolism → slow growth, long life, bigger bodies" x={110} y={90} at={b.cold - 10} until={gridOut}>
        <svg width={200} height={210}>
          <rect x={92} y={30} width={16} height={120} rx={8} fill="none" stroke={C.white} strokeWidth={2} />
          <rect x={95} y={150 - 110 * (1 - ramp(f, b.cold, 60))} width={10} height={110 * (1 - ramp(f, b.cold, 60)) + 4} fill={C.blue} />
          <circle cx={100} cy={162} r={14} fill={C.blue} />
          <path d={`M20 190 ${Array.from({length: 18}).map((_, i) => `L${20 + i * 9} ${190 - beat(f / 30 - i * 0.1, 1 + 2 * (1 - ramp(f, b.cold, 80))) * 20}`).join(' ')}`} stroke={C.coral} strokeWidth={2} fill="none" />
        </svg>
      </Card>
      <Card n={2} title="Oxygen" line="Cold water holds more of it; amphipod size tracks oxygen" x={630} y={90} at={b.oxy - 10} until={gridOut}>
        <svg width={200} height={210}>
          {Array.from({length: 26}).map((_, i) => {
            const y = 190 - ((f * (1 + (i % 3)) + i * 37) % 170);
            return <circle key={i} cx={30 + (i * 53) % 150 + Math.sin(f / 10 + i) * 4} cy={y} r={3 + (i % 3)} fill="none" stroke={C.cyan} strokeWidth={1.5} opacity={ramp(f, b.oxy, 20)} />;
          })}
          <text x={100} y={115} textAnchor="middle" fill={C.white} fontSize={34} fontWeight={800} fontFamily="Inter">O₂</text>
        </svg>
      </Card>
      <Card n={3} title="Hunger" line="Bigger bodies burn less energy per kilo and store more fuel" x={110} y={330} at={b.hunger - 10} until={gridOut}>
        <svg width={200} height={210}>
          <rect x={30} y={140 - 100} width={40} height={100} fill="none" stroke={C.dim} />
          <rect x={30} y={140 - 100 * (1 - 0.6 * ramp(f, b.hunger, 60))} width={40} height={100 * (1 - 0.6 * ramp(f, b.hunger, 60))} fill={C.coral} />
          <rect x={120} y={140 - 100} width={40} height={100} fill="none" stroke={C.dim} />
          <rect x={120} y={140 - 100 * (1 - 0.25 * ramp(f, b.hunger, 60))} width={40} height={100 * (1 - 0.25 * ramp(f, b.hunger, 60))} fill={C.cyan} />
          <text x={50} y={165} textAnchor="middle" fill={C.dim} fontSize={12} fontFamily="Inter">small</text>
          <text x={140} y={165} textAnchor="middle" fill={C.dim} fontSize={12} fontFamily="Inter">big</text>
          <text x={100} y={192} textAnchor="middle" fill={C.dim} fontSize={11} fontFamily="Inter">fuel left (illustrative)</text>
        </svg>
      </Card>
      <Card n={4} title="Time" line="Fewer predators + very long lives = time to grow" x={630} y={330} at={b.time - 10} until={gridOut}>
        <svg width={200} height={210}>
          <path d="M60 30 H140 L100 105 L140 180 H60 L100 105 Z" fill="none" stroke={C.white} strokeWidth={2} />
          <path d={`M${70 + 30 * ramp(f, b.time, 90)} ${40 + 55 * ramp(f, b.time, 90)} H${130 - 30 * ramp(f, b.time, 90)} L100 105 Z`} fill={C.amber} />
          <path d={`M100 ${180 - 60 * ramp(f, b.time, 90)} L${100 - 36 * ramp(f, b.time, 90)} 178 H${100 + 36 * ramp(f, b.time, 90)} Z`} fill={C.amber} />
        </svg>
      </Card>
      <Tag x={640} y={560} at={b.hunger + 90} until={gridOut} align="center" size={16} color={C.dim}>↳ remember the isopod: 5 years without food</Tag>

      {/* the twist: most deep-sea life is tiny */}
      <AbsoluteFill style={{opacity: ramp(f, b.but, 10)}}>
        <AbsoluteFill style={{background: 'rgba(1,6,14,0.6)'}} />
        <BigStat x={640} y={60} at={b.but} value="THE TWIST" size={62} color={C.amber} />
        <svg width={1280} height={720} style={{position: 'absolute'}}>
          <path d="M0 520 Q 640 500 1280 520 L1280 720 L0 720 Z" fill="rgba(40,36,44,0.95)" />
          <circle cx={640} cy={430} r={190 * ramp(f, b.tiny, 20, 0, 1, easeOut)} fill="rgba(20,24,30,0.95)" stroke={C.cyan} strokeWidth={3} />
          {Array.from({length: 120}).map((_, i) => {
            const a = rnd(i) * Math.PI * 2, d = rnd(i + 9) * 170 * ramp(f, b.tiny, 20);
            return <ellipse key={i} cx={640 + Math.cos(a) * d + Math.sin(f / 8 + i) * 2} cy={430 + Math.sin(a) * d} rx={2 + rnd(i + 3) * 3} ry={1.2 + rnd(i + 4) * 1.5} fill={['#E9DCCB', '#BDE7F0', '#F2C7D6'][i % 3]} opacity={0.85} />;
          })}
        </svg>
        <Tag x={640} y={630} at={b.tiny + 20} align="center" size={18}>most life down here is smaller than 1 mm</Tag>
        <AbsoluteFill style={{opacity: ramp(f, b.groups, 12)}}>
          <AbsoluteFill style={{transform: 'scale(0.45)', transformOrigin: '200px 380px'}}><ColossalSquid x={0} y={380} len={420} /></AbsoluteFill>
          <AbsoluteFill style={{transform: 'scale(0.6)', transformOrigin: '1000px 380px'}}><Isopod x={1000} y={380} len={300} /></AbsoluteFill>
          <Tag x={180} y={470} at={b.groups} align="center" size={14} color={C.cyan}>squid</Tag>
          <Tag x={1000} y={470} at={b.groups} align="center" size={14} color={C.cyan}>crustaceans</Tag>
        </AbsoluteFill>
        <BigStat x={640} y={150} at={b.enormous} value="A FEW THINGS · ENORMOUS" size={44} color={C.white} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- TRENCH ----------
export const trenchDepth = (s: SceneTiming, f: number) => {
  const a = cueFrame(s, 'At eight thousand');
  const y = cueFrame(s, 'And yet, in 2023');
  const line = cueFrame(s, "That's the invisible line");
  const below = cueFrame(s, 'Below it');
  const endF = s.durationInFrames - 20;
  if (f < 40) return lerp(4200, 6000, ramp(f, 0, 40));
  if (f < a) return lerp(6000, 7600, ramp(f, 40, a - 40, 0, 1, (t) => t));
  if (f < y + 50) return lerp(7600, 8336, ramp(f, a, y + 50 - a, 0, 1, easeOut));
  if (f < line) return lerp(8336, 8380, ramp(f, y + 50, line - y - 50));
  if (f < below) return lerp(8380, 8420, ramp(f, line, below - line));
  return lerp(8420, 10935, ramp(f, below, endF - below, 0, 1, easeOut));
};

export const Trench: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const b = beats(s, {
    six: ['Six thousand metres'], hadal: ['The hadal zone'], press: ['At eight thousand'], yet: ['And yet, in 2023'], deepest: ['The deepest fish ever'],
    may: ['It may be about'], tmao: ['Fish rely on a molecule'], est: ['Scientists estimate that'], line: ["That's the invisible line"], below: ['Below it'], only: ['Only shrimp-like'], bottom: ['all the way to the bottom'],
  });
  const sh = shake(f, b.line, 10, 22);
  const walls = (side: number) => {
    const pts: string[] = [];
    for (let i = 0; i <= 20; i++) {
      const y = i * 40;
      const x = side < 0 ? 140 + Math.sin(i * 1.3 + f * 0.02) * 30 + rnd(i) * 40 : 1140 - Math.sin(i * 1.1 + f * 0.02) * 30 - rnd(i + 5) * 40;
      pts.push(`${x},${(y + f * 3) % 840 - 60}`);
    }
    return pts.sort((p, q) => parseFloat(p.split(',')[1]) - parseFloat(q.split(',')[1])).join(' ');
  };
  const proteinOk = 1 - ramp(f, b.est + 30, 40);
  return (
    <AbsoluteFill style={{transform: `translate(${sh.x}px, ${sh.y}px)`}}>
      <ZoneTitle at={4} title="Hadal Zone" sub="6,000 metres · the trenches" dur={84} />
      <svg width={1280} height={720} style={{position: 'absolute', opacity: 0.85}}>
        <polygon points={`0,-60 ${walls(-1)} 0,780`} fill="#141B26" stroke="rgba(92,242,224,0.25)" strokeWidth={2} />
        <polygon points={`1280,-60 ${walls(1)} 1280,780`} fill="#141B26" stroke="rgba(92,242,224,0.25)" strokeWidth={2} />
      </svg>
      <BigStat x={640} y={80} at={b.press} until={b.yet + 4} value="≈ 800×" label="surface pressure at 8,000 m" size={80} color={C.amber} />

      {/* snailfish at 8,336 m */}
      <AbsoluteFill style={{opacity: win(f, b.yet, b.tmao + 4, 12)}}>
        <Glow x={640} y={380} r={180} color="rgba(255,230,240,0.12)" />
        <Snailfish x={lerp(380, 520, ramp(f, b.yet, 200, 0, 1, (t) => t))} y={380} s={1.5} />
        <BigStat x={640} y={500} at={b.deepest} value="8,336 M" label="deepest fish ever filmed · Izu-Ogasawara Trench" size={70} color={C.cyan} />
        <Tag x={640} y={24} at={b.yet} align="center" size={12} color={C.dim}>Illustration · real footage revealed 2023 by Univ. of Western Australia & Tokyo Univ. of Marine Science and Technology</Tag>
      </AbsoluteFill>

      <RealInsert src="img/snailfish_gerringer_2017.jpg" at={b.deepest + 40} until={b.tmao + 6} x={330} y={120} w={620} h={324} dim={0.45} zoom={[1.0, 1.15]} origin="40% 50%"
        label="Real hadal snailfish at a baited camera · Mariana Trench" credit="Gerringer et al. 2017, Zootaxa · CC BY 3.0 · cropped" />

      {/* TMAO explainer */}
      <AbsoluteFill style={{opacity: win(f, b.tmao, b.line + 6, 10)}}>
        <Panel x={340} y={120} w={600} h={330} at={b.tmao}>
          <svg width={600} height={330}>
            <path d={`M150 ${170} C 200 ${110 - 40 * (1 - proteinOk)}, 260 ${230 + 30 * (1 - proteinOk)}, 300 170 S 420 ${120 + 60 * (1 - proteinOk)}, 450 170`} stroke={proteinOk > 0.5 ? C.cyan : C.coral} strokeWidth={10} fill="none" strokeLinecap="round" />
            {Array.from({length: 18}).map((_, i) => (
              <circle key={i} cx={150 + i * 17} cy={120 + (i % 2) * 100} r={6} fill={C.amber} opacity={i / 18 < proteinOk ? 0.9 : 0.1} />
            ))}
          </svg>
          <div style={{position: 'absolute', left: 0, right: 0, top: 22, textAlign: 'center', fontFamily: TEXT, fontWeight: 700, letterSpacing: 2, color: C.white, fontSize: 18}}>TMAO ● keeps proteins working under pressure</div>
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 22, textAlign: 'center', fontFamily: TEXT, fontWeight: 600, color: C.dim, fontSize: 14}}>schematic</div>
        </Panel>
      </AbsoluteFill>

      {/* the invisible line */}
      <AbsoluteFill style={{opacity: ramp(f, b.line - 4, 10) * (1 - ramp(f, b.only + 60, 14))}}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 340, height: 40, background: 'linear-gradient(transparent, rgba(92,242,224,0.35), transparent)', transform: `scaleX(${ramp(f, b.line, 20, 0, 1, easeOut)})`}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: 359, height: 2, background: C.cyan, boxShadow: `0 0 30px ${C.cyan}`, transform: `scaleX(${ramp(f, b.line, 20, 0, 1, easeOut)})`}} />
        <Tag x={640} y={300} at={b.line + 6} align="center" size={20} color={C.cyan}>≈ 8,200–8,400 m · estimated limit for fish</Tag>
        <Snailfish x={560} y={300 - 40} s={0.8} o={0.8} />
        <Tag x={640} y={400} at={b.below} align="center" size={18} color={C.white}>below: no fish ever found</Tag>
      </AbsoluteFill>
      <AbsoluteFill style={{opacity: ramp(f, b.only, 12)}}>
        {Array.from({length: 9}).map((_, i) => (
          <Amphipod key={i} x={260 + i * 90 + Math.sin(f / 20 + i) * 20} y={470 + (i % 3) * 40 + Math.cos(f / 15 + i) * 8} s={1.1} />
        ))}
        <svg width={1280} height={720} style={{position: 'absolute', opacity: ramp(f, s.durationInFrames - 120, 40)}}>
          <path d="M0 640 Q 640 610 1280 640 L1280 720 L0 720 Z" fill="#14161C" />
        </svg>
        <Tag x={640} y={660} at={s.durationInFrames - 100} align="center" size={18} color={C.amber}>Challenger Deep · ≈ 10,935 m</Tag>
      </AbsoluteFill>
      <RealInsert src="img/trieste_1960_noaa.jpg" at={b.bottom} until={s.durationInFrames - 2} x={200} y={50} w={260} h={421} dim={0.35} tilt={2} zoom={[1.0, 1.08]}
        label="1960 · Walsh & Piccard, first to reach the Challenger Deep" credit="NOAA Ship Collection · public domain" />
    </AbsoluteFill>
  );
};

// ---------- END ----------
export const endDepth = () => 10935;

export const End: React.FC<{s: SceneTiming}> = ({s}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const b = beats(s, {humbling: ["And here's the most humbling"], every: ['Every giant in this video'], real: ["So the real question"], what: ["It's what's still down there"], sub: ['If this dive blew']});
  const out = ramp(f, b.humbling, 30, 0, 1, easeOut);
  // ocean column: 0–11 km mapped to y 120 → 620
  const yOf = (m: number) => 120 + (m / 11000) * 500;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{opacity: out * (1 - ramp(f, b.real - 6, 10))}}>
        <AbsoluteFill style={{background: 'rgba(1,4,9,0.7)'}} />
        <svg width={1280} height={720} style={{position: 'absolute'}}>
          <defs>
            <linearGradient id="col" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#3DB4E6" />
              <stop offset="0.1" stopColor="#0A3F70" />
              <stop offset="0.4" stopColor="#021226" />
              <stop offset="1" stopColor="#000206" />
            </linearGradient>
          </defs>
          <rect x={180} y={yOf(0)} width={180} height={yOf(10935) - yOf(0)} fill="url(#col)" stroke={C.faint} />
          {[0, 200, 1000, 4000, 6000, 10935].map((m) => (
            <g key={m}>
              <line x1={170} x2={370} y1={yOf(m)} y2={yOf(m)} stroke={C.faint} />
              <text x={160} y={yOf(m) + 4} fill={C.dim} fontSize={12} textAnchor="end" fontFamily="Inter">{m.toLocaleString('en-US')} m</text>
            </g>
          ))}
          <path d={`M270 ${yOf(0)} L270 ${yOf(10935 * ramp(f, b.humbling, 40))}`} stroke={C.cyan} strokeWidth={3} strokeDasharray="6 6" />
        </svg>
        <BigStat x={820} y={210} at={b.humbling + 30} value="< 0.001%" label="of the deep seafloor ever seen by cameras" size={90} color={C.cyan} />
        <Tag x={820} y={350} at={b.humbling + 50} align="center" size={13} color={C.dim}>Bell et al., Science Advances, 2025</Tag>
        <Tag x={820} y={420} at={b.every} align="center" size={18} color={C.white}>every giant here was found by looking deeper</Tag>
        {['spider_crab_krentzel', 'oarfish_1996_usnavy', 'greenland_shark_noaa_2013', 'isopod_noaa_okeanos'].map((n, i) => {
          const p = pop(f, b.every + 20 + i * 9);
          return (
            <div key={n} style={{position: 'absolute', left: 480 + i * 174, top: 462, width: 160, height: 107, opacity: f > b.every + 20 + i * 9 ? 1 : 0, transform: `translateY(${(1 - p) * 30}px) scale(${p}) rotate(${(i % 2 ? 3 : -3) * (1 - p) + (i % 2 ? 1.5 : -1.5)}deg)`, border: '3px solid rgba(255,255,255,0.92)', borderRadius: 5, overflow: 'hidden', boxShadow: '0 14px 30px rgba(0,0,0,0.8)'}}>
              <Img src={staticFile(`img/${n}.jpg`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
            </div>
          );
        })}
      </AbsoluteFill>
      <AbsoluteFill style={{opacity: ramp(f, b.real, 12), alignItems: 'center', justifyContent: 'center', flexDirection: 'column'}}>
        <div style={{fontFamily: DISPLAY, fontWeight: 300, fontSize: 40, color: C.dim, letterSpacing: 2, opacity: ramp(f, b.real, 12)}}>not how big they get…</div>
        <div style={{marginTop: 14, fontFamily: DISPLAY, fontWeight: 800, fontSize: 70, color: C.white, transform: `scale(${pop(f, b.what)})`, opacity: f > b.what ? 1 : 0, textShadow: `0 0 40px rgba(92,242,224,0.35)`}}>WHAT&apos;S STILL DOWN THERE?</div>
        <div style={{marginTop: 34, transform: `scale(${pop(f, b.sub + 10)})`, opacity: f > b.sub + 10 ? 1 : 0, background: '#E5322D', color: '#fff', fontFamily: TEXT, fontWeight: 800, fontSize: 20, letterSpacing: 2, padding: '12px 28px', borderRadius: 6}}>SUBSCRIBE</div>
      </AbsoluteFill>
      <AbsoluteFill style={{background: '#000', opacity: ramp(f, durationInFrames - 30, 28)}} />
    </AbsoluteFill>
  );
};
