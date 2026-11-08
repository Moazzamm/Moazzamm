import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { geoAlbersUsa, geoOrthographic, geoPath } from "d3-geo";
import { SceneShell } from "../components/Shell";
import { Center, Chip, Counter, Headline, Layer, Panel, Photo, Sfx, Stamp } from "../components/core";
import { GeoMap, LOWER48 } from "../components/geo";
import { CanyonScene, HotspotScene, ISLAND_NAMES, islandScreenX } from "../components/three3d";
import { BODY, C, HEAD as HF } from "../lib/theme";
import { cue, sceneFrames, voEnd } from "../lib/timeline";
import { EASE, lerp, pop, ramp } from "../lib/anim";

const bg = (x = 50, y = 45) => ({ background: `radial-gradient(circle at ${x}% ${y}%, ${C.bg2}, ${C.bg})` });

/* =============================== #5 WHITNEY vs BADWATER =============================== */
// real profile: distance (mi) -> elevation (ft), Whitney -> Owens Valley -> Inyo Mts -> Panamint Valley -> Panamint Range -> Badwater
const PROFILE: [number, number][] = [
  [0, 14505], [4, 11500], [9, 8000], [13, 3700], [20, 3600], [26, 7000], [30, 10000], [35, 7000], [42, 3000], [50, 1100], [57, 2500], [64, 7500], [70, 11049], [75, 6500], [80, 1500], [85, -282],
];
const PX0 = 180, PX1 = 1740, SEA = 760, FT = 0.035;
const px = (mi: number) => PX0 + (mi / 85) * (PX1 - PX0);
const py = (ft: number) => SEA - ft * FT;

export const F5: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f5";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tSide = c("On one side"), tDV = c("And Death Valley");
  const line = PROFILE.map(([m, e], i) => `${i ? "L" : "M"}${px(m)},${py(e)}`).join(" ");
  const area = `${line} L${PX1},900 L${PX0},900 Z`;
  const draw = ramp(f, tSide, c("Badwater") - tSide + 10, EASE);
  return (
    <SceneShell id={id} n={5}>
      <Layer a={0} b={tSide + 6} fade={6}>
        <div style={{ position: "absolute", left: 0, top: 0, width: 960, height: 1080, overflow: "hidden" }}>
          <div style={{ position: "absolute", left: -480, width: 1920, height: 1080 }}>
            <Photo src="whitney.jpg" dur={tSide} zoom={[1.1, 1.2]} dim={0.4} />
          </div>
        </div>
        <div style={{ position: "absolute", left: 960, top: 0, width: 960, height: 1080, overflow: "hidden" }}>
          <div style={{ position: "absolute", left: -480, width: 1920, height: 1080 }}>
            <Photo src="badwater.jpg" dur={tSide} zoom={[1.2, 1.1]} dim={0.4} />
          </div>
        </div>
        <div style={{ position: "absolute", left: 957, top: 0, width: 6, height: 1080, background: "#fff" }} />
        <Center style={{ gap: 6 }}>
          <Headline text="Highest & lowest" at={c("the highest")} size={110} />
          <div style={{ display: "flex", alignItems: "baseline", gap: 26 }}>
            <div style={{ fontFamily: HF, fontSize: 90, color: "#fff", opacity: ramp(f, c("85"), 8) }}>ONLY</div>
            <Counter from={0} to={85} at={c("85")} dur={25} size={190} color={C.gold} />
            <div style={{ fontFamily: HF, fontSize: 90, color: "#fff", opacity: ramp(f, c("85"), 8) }}>MILES APART</div>
          </div>
        </Center>
      </Layer>
      <Layer a={tSide} b={tDV + 6} fade={6} style={bg(50, 30)}>
        <svg width={1920} height={1080} style={{ position: "absolute" }}>
          <defs>
            <linearGradient id="terrain" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#e8eef7" />
              <stop offset="0.25" stopColor="#8a7a6a" />
              <stop offset="0.75" stopColor="#c9a46b" />
              <stop offset="1" stopColor="#7a5a3a" />
            </linearGradient>
            <clipPath id="drawClip">
              <rect x={0} y={0} width={PX0 + (PX1 - PX0) * draw + 2} height={1080} />
            </clipPath>
          </defs>
          <line x1={120} x2={1800} y1={SEA} y2={SEA} stroke="#5aa0ff" strokeWidth={3} strokeDasharray="14 10" />
          <text x={1800} y={SEA - 12} textAnchor="end" fill="#5aa0ff" fontFamily={BODY} fontWeight={900} fontSize={24}>SEA LEVEL</text>
          <g clipPath="url(#drawClip)">
            <path d={area} fill="url(#terrain)" opacity={0.9} />
            <path d={line} fill="none" stroke="#fff" strokeWidth={5} />
          </g>
          {f >= c("Mount Whitney") && <circle cx={px(0)} cy={py(14505)} r={16 * pop(f, c("Mount Whitney"), 10)} fill={C.gold} />}
          {f >= c("Badwater") && <circle cx={px(85)} cy={py(-282)} r={16 * pop(f, c("Badwater"), 10)} fill={C.red} />}
          {f >= c("That's a drop") && (
            <g opacity={ramp(f, c("That's a drop"), 10)}>
              <line x1={PX1 + 60} x2={PX1 + 60} y1={py(14505)} y2={py(-282)} stroke={C.gold} strokeWidth={6} />
              <line x1={px(0)} x2={PX1 + 75} y1={py(14505)} y2={py(14505)} stroke={C.gold} strokeWidth={2} strokeDasharray="8 8" />
            </g>
          )}
        </svg>
        <div style={{ position: "absolute", left: px(0) + 30, top: py(14505) - 40 }}>
          <Panel at={c("Mount Whitney")} style={{ padding: 22 }}>
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 28, color: C.dim, letterSpacing: 3 }}>MOUNT WHITNEY</div>
            <Counter from={0} to={14505} suffix=" FT" at={c("14,505")} dur={25} size={80} color={C.gold} />
          </Panel>
        </div>
        <div style={{ position: "absolute", left: px(85) - 470, top: py(-282) - 230 }}>
          <Panel at={c("Badwater")} style={{ padding: 22 }}>
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 28, color: C.dim, letterSpacing: 3 }}>BADWATER BASIN</div>
            <Counter from={0} to={-282} suffix=" FT" at={c("282")} dur={20} size={80} color={C.red} />
          </Panel>
        </div>
        <div style={{ position: "absolute", left: 1220, top: 260 }}>
          <Panel at={c("That's a drop")} from="right" style={{ padding: 24 }}>
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 28, color: C.dim, letterSpacing: 3 }}>TOTAL DROP</div>
            <Counter from={0} to={14787} suffix=" FT" at={c("That's a drop")} dur={30} size={90} color="#fff" />
          </Panel>
        </div>
        <div style={{ position: "absolute", left: PX0, top: 930, fontFamily: BODY, fontWeight: 700, fontSize: 22, color: "rgba(255,255,255,.45)", opacity: 0 }}>.</div>
        <div style={{ position: "absolute", left: 70, bottom: 28, fontFamily: BODY, fontWeight: 700, fontSize: 22, color: "rgba(255,255,255,.55)" }}>Elevation profile · vertical scale exaggerated</div>
        <Sfx src="pop.wav" at={c("Mount Whitney")} />
        <Sfx src="pop.wav" at={c("Badwater")} />
      </Layer>
      <Layer a={tDV} b={end} fade={6}>
        <Photo src="badwater.jpg" from={tDV} dur={end - tDV} zoom={[1.0, 1.15]} dim={0.5} filter="saturate(1.3) sepia(.25)" />
        <div style={{ position: "absolute", left: 220, top: 200 }}>
          <svg width={160} height={600}>
            <rect x={55} y={10} width={50} height={480} rx={25} fill="rgba(255,255,255,.2)" stroke="#fff" strokeWidth={4} />
            <circle cx={80} cy={530} r={60} fill={C.red} stroke="#fff" strokeWidth={4} />
            <rect x={65} y={490 - 460 * ramp(f, c("134"), 40)} width={30} height={460 * ramp(f, c("134"), 40) + 10} fill={C.red} />
          </svg>
        </div>
        <div style={{ position: "absolute", left: 470, top: 260 }}>
          <Headline text="Hottest air ever measured" at={c("the hottest")} size={84} align="left" />
          <Counter from={60} to={134} suffix="°F" at={c("134")} dur={40} size={260} color={C.red} />
          <Chip at={c("1913")} color={C.red} size={44}>Death Valley · 1913</Chip>
        </div>
        <Sfx src="riser.wav" at={c("134") - 10} volume={0.35} />
        <Sfx src="boom.wav" at={c("134") + 35} volume={0.4} />
      </Layer>
    </SceneShell>
  );
};

/* =============================== #4 GRAND CANYON =============================== */
export const F4: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f4";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tHike = c("As you hike"), tBottom = c("But at the very"), t40 = c("That's almost"), tRiver = c("And the river");
  const reveal = ramp(f, tHike, 35, EASE);
  const marker = lerp(f, [tBottom, c("1.8") + 10], [0, 1]);
  return (
    <SceneShell id={id} n={4}>
      <Layer a={0} b={tHike + 6} fade={6}>
        <Photo src="canyon_sunset.jpg" dur={tHike} zoom={[1.0, 1.2]} />
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 220 }}>
          <Headline text="The Grand Canyon is a" at={c("The Grand")} size={90} />
          <Headline text="*time machine*" at={c("time machine")} size={200} />
        </AbsoluteFill>
      </Layer>
      <Layer a={tHike} b={t40 + 6} fade={6} style={{ background: "linear-gradient(#0d1a33, #0a0f1c 70%)" }}>
        <AbsoluteFill style={{ left: -260 }}>
          <CanyonScene marker={marker} reveal={reveal} river={1} />
        </AbsoluteFill>
        <div style={{ position: "absolute", right: 110, top: 200, width: 640, display: "flex", flexDirection: "column", gap: 26 }}>
          <Panel at={c("every layer")} from="right" style={{ padding: 26 }}>
            <div style={{ fontFamily: HF, fontSize: 52, color: "#fff", lineHeight: 1.05 }}>EVERY LAYER DOWN IS OLDER</div>
          </Panel>
          <Panel at={c("The rocks at")} from="right" style={{ padding: 26 }}>
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 26, color: C.dim, letterSpacing: 3 }}>AT THE RIM</div>
            <Counter from={0} to={270} suffix=" MILLION YRS" at={c("270")} dur={25} size={70} color="#f2e3c4" />
            {f >= c("older than") && <Chip at={c("older than")} color={C.green} size={30}>Older than dinosaurs</Chip>}
          </Panel>
          <Panel at={tBottom} from="right" style={{ padding: 26 }}>
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 26, color: C.dim, letterSpacing: 3 }}>AT THE BOTTOM</div>
            <Counter from={270} to={1800} suffix=" MILLION YRS" at={c("1.8")} dur={30} size={70} color={C.gold} />
            <div style={{ fontFamily: HF, fontSize: 44, color: C.gold, opacity: ramp(f, c("1.8") + 30, 10) }}>= 1.8 BILLION YEARS</div>
          </Panel>
        </div>
        <Sfx src="whoosh.wav" at={tBottom} volume={0.4} />
        <Sfx src="ding.wav" at={c("1.8") + 30} volume={0.35} />
      </Layer>
      <Layer a={t40} b={tRiver + 6} fade={6} style={bg(50, 40)}>
        <div style={{ position: "absolute", left: 160, top: 240, width: 1600 }}>
          <Headline text="*40%* of Earth's history" at={t40} size={120} align="left" />
          <div style={{ position: "relative", height: 110, marginTop: 70, borderRadius: 18, background: "rgba(255,255,255,.12)", overflow: "hidden" }}>
            <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: `${39.6 * ramp(f, t40 + 10, 35)}%`, background: `repeating-linear-gradient(90deg, #c4633f 0 60px, #9e3d2c 60px 120px, #e9d6a6 120px 150px)` }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16, fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.dim }}>
            <span>EARTH FORMS · 4.5 BILLION YRS AGO</span>
            <span>TODAY</span>
          </div>
          <div style={{ marginTop: 30 }}>
            <Chip at={c("stacked")} color={C.copper} size={44}>Stacked like pages in a book</Chip>
          </div>
        </div>
      </Layer>
      <Layer a={tRiver} b={end} fade={6}>
        <Photo src="canyon_river.jpg" from={tRiver} dur={end - tRiver} zoom={[1.0, 1.2]} dim={0.45} />
        <div style={{ position: "absolute", left: 150, top: 240 }}>
          <Headline text="The river started carving" at={c("It only")} size={80} align="left" />
          <div style={{ fontFamily: HF, fontSize: 190, color: C.gold, opacity: ramp(f, c("5 to"), 10), lineHeight: 1 }}>~5–6 MILLION</div>
          <div style={{ fontFamily: HF, fontSize: 90, color: "#fff", opacity: ramp(f, c("5 to") + 8, 10) }}>YEARS AGO</div>
        </div>
      </Layer>
    </SceneShell>
  );
};

/* =============================== #3 HAWAII =============================== */
const HI: [number, number] = [-155.5, 19.6];
const JP: [number, number] = [139.7, 35.7];

const PacificGlobe: React.FC<{ arrow: number; scale?: number }> = ({ arrow, scale = 760 }) => {
  const f = useCurrentFrame();
  const proj = geoOrthographic().rotate([170, -30]).scale(scale).translate([960, 600]);
  const path = geoPath(proj);
  const hi = proj(HI)!;
  const jp = proj(JP)!;
  // partial great-circle from Hawaii toward Japan
  const mid: [number, number] = [HI[0] + (JP[0] - 360 - HI[0]) * arrow, HI[1] + (JP[1] - HI[1]) * arrow];
  return (
    <GeoMap projection={proj} sphere graticule stateFill={(n) => (n === "Hawaii" ? C.gold : C.land)} worldFill="#1b2b4a">
      {() => (
        <g>
          {arrow > 0 && <path d={path({ type: "LineString", coordinates: [HI, mid] }) ?? ""} stroke={C.gold} strokeWidth={8} fill="none" strokeDasharray="20 12" strokeDashoffset={-f * 2} />}
          <circle cx={hi[0]} cy={hi[1]} r={18 + 6 * Math.sin(f / 5)} fill="none" stroke={C.gold} strokeWidth={5} />
          <circle cx={hi[0]} cy={hi[1]} r={9} fill={C.gold} />
          <circle cx={jp[0]} cy={jp[1]} r={12} fill={C.red} />
          <text x={hi[0] + 30} y={hi[1] + 10} fill="#fff" fontFamily={HF} fontSize={52}>HAWAII</text>
          <text x={jp[0] - 30} y={jp[1] - 26} fill="#fff" fontFamily={HF} fontSize={52} textAnchor="end">JAPAN</text>
        </g>
      )}
    </GeoMap>
  );
};

export const F3: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f3";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tPlate = c("The islands sit"), tDeep = c("Deep below"), tSpeed = c("At this speed");
  const prog = lerp(f, [tDeep, c("older islands") + 30], [0, 1]);
  return (
    <SceneShell id={id} n={3}>
      <Layer a={0} b={tDeep} fade={6} style={bg(50, 50)}>
        <PacificGlobe arrow={ramp(f, c("Hawaii is"), 50)} scale={lerp(f, [0, tPlate + 30], [700, 820])} />
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 150 }}>
          <Headline text="Hawaii is moving to *Japan*" at={c("Hawaii is")} size={96} out={tPlate} />
        </AbsoluteFill>
        <Layer a={tPlate} b={tDeep + 6}>
          <div style={{ position: "absolute", left: 120, top: 220, display: "flex", flexDirection: "column", gap: 20, alignItems: "flex-start" }}>
            <Chip at={c("Pacific Plate")} color={C.blue} size={46}>Pacific Plate</Chip>
            <Panel at={c("4 inches")} style={{ padding: 24 }}>
              <Counter from={0} to={4} suffix=" INCHES" at={c("4 inches")} dur={20} size={110} color={C.gold} />
              <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.dim, letterSpacing: 3 }}>EVERY YEAR · NORTHWEST</div>
            </Panel>
          </div>
        </Layer>
      </Layer>
      <Layer a={tDeep + 3} b={tSpeed + 6} fade={6} style={{ background: "linear-gradient(#0d2246, #0a0f1c)" }}>
        <HotspotScene progress={prog} glow={ramp(f, c("hotspot"), 15)} />
        {ISLAND_NAMES.map((n, i) => {
          const born = [0, 0.22, 0.45, 0.68][i];
          const vis = prog > born + 0.05;
          const x = islandScreenX(i, prog);
          return vis && x > 80 && x < 1840 ? (
            <div key={n} style={{ position: "absolute", left: x - 150, width: 300, top: 300, textAlign: "center", fontFamily: HF, fontSize: 44, color: i === 3 ? C.gold : "#fff", textShadow: "0 4px 14px rgba(0,0,0,.8)", opacity: ramp(f, tDeep + 1, 1) }}>
              {n}
            </div>
          ) : null;
        })}
        <div style={{ position: "absolute", left: 120, top: 180, display: "flex", gap: 20 }}>
          <Chip at={tDeep + 4} color={C.blue} size={38}>← Plate moves</Chip>
          <Chip at={c("hotspot")} color={C.red} size={38}>Hotspot stays put</Chip>
        </div>
        <Layer a={c("like a candle")} b={c("That's why")}>
          <div style={{ position: "absolute", left: 120, top: 260 }}>
            <Chip at={c("like a candle")} color="rgba(0,0,0,.65)" size={36}>Like a candle under moving paper</Chip>
          </div>
        </Layer>
        <Layer a={c("That's why")} b={tSpeed + 6}>
          <div style={{ position: "absolute", right: 110, top: 180, display: "flex", flexDirection: "column", gap: 14, alignItems: "flex-end" }}>
            <Chip at={c("youngest")} color={C.red} size={36}>Youngest · active volcanoes</Chip>
            <Chip at={c("Kauai")} color={C.green} size={36}>Oldest · quiet</Chip>
          </div>
        </Layer>
        <Sfx src="boom.wav" at={c("hotspot")} volume={0.35} />
      </Layer>
      <Layer a={tSpeed + 9} b={end} fade={6} style={bg(50, 50)}>
        <PacificGlobe arrow={ramp(f, tSpeed, 60)} scale={820} />
        <div style={{ position: "absolute", left: 120, top: 200 }}>
          <Panel at={c("63")} style={{ padding: 26 }}>
            <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.dim, letterSpacing: 3 }}>ARRIVAL IN JAPAN</div>
            <Counter from={0} to={63} suffix=" MILLION YRS" at={c("63")} dur={30} size={90} color={C.gold} />
          </Panel>
        </div>
      </Layer>
    </SceneShell>
  );
};

/* =============================== #2 MOUNT RUSHMORE =============================== */
const MOUNTAIN = "M0,900 L0,520 C120,470 220,380 330,330 C420,290 520,250 600,260 L640,520 L700,520 L720,240 C820,200 980,190 1080,230 C1160,260 1220,300 1260,360 L1300,420 C1340,520 1380,620 1420,700 L1500,900 Z";

export const F2: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f2";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const t1938 = c("In 1938"), t1998 = c("Then, in 1998"), tClosed = c("It's closed");
  const tunLen = 420 * Math.min(0.7, ramp(f, c("tunnel"), 45));
  const box = pop(f, c("A titanium"), 12);
  const slab = ramp(f, c("1,200"), 10, EASE);
  return (
    <SceneShell id={id} n={2}>
      <Layer a={0} b={t1938 + 6} fade={6}>
        <Photo src="rushmore.jpg" dur={t1938} zoom={[1.0, 1.25]} pan={["0px 0px", "-80px -20px"]} />
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 170 }}>
          <Headline text="A *secret room*" at={c("There's a secret")} size={150} out={c("Sculptor")} />
        </AbsoluteFill>
        <Layer a={c("Sculptor")} b={t1938 + 6}>
          <div style={{ position: "absolute", left: 120, top: 560 }}>
            <Panel at={c("Sculptor")} from="left" style={{ padding: 26 }}>
              <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 28, color: C.gold, letterSpacing: 4 }}>SCULPTOR</div>
              <div style={{ fontFamily: HF, fontSize: 80, color: "#fff", lineHeight: 1 }}>GUTZON BORGLUM</div>
            </Panel>
          </div>
          <div style={{ position: "absolute", right: 120, top: 200, display: "flex", flexDirection: "column", gap: 18, alignItems: "flex-end" }}>
            <Chip at={c("Hall of Records")} color={C.red} size={52}>The Hall of Records</Chip>
            <Chip at={c("a vault")} color={C.blue} size={38}>A vault for future civilizations</Chip>
          </div>
        </Layer>
      </Layer>
      <Layer a={t1938} b={tClosed + 6} fade={6} style={{ background: "linear-gradient(#11203e, #0a0f1c)" }}>
        <svg width={1920} height={1080} style={{ position: "absolute" }}>
          <path d={MOUNTAIN} fill="#6f7480" stroke="#9aa1ad" strokeWidth={4} />
          {/* carved faces on the front cliff (schematic) */}
          {[0, 1, 2, 3].map((k) => (
            <ellipse key={k} cx={1190 + k * 38} cy={330 + k * 40} rx={34} ry={46} fill="#8b909b" stroke="#b6bcc6" strokeWidth={3} />
          ))}
          <text x={1330} y={300} fill="#fff" fontFamily={BODY} fontWeight={900} fontSize={26}>THE FACES</text>
          {/* canyon behind the faces + tunnel */}
          <text x={600} y={235} fill="#fff" fontFamily={BODY} fontWeight={900} fontSize={24}>CANYON BEHIND</text>
          <rect x={700} y={470} width={tunLen} height={50} fill="#1a1c22" />
          <rect x={700 + tunLen - 6} y={470} width={6} height={50} fill={C.gold} opacity={f < c("But the money") ? 0.6 + 0.4 * Math.sin(f) : 0} />
          {/* vault */}
          {f >= c("A titanium") && (
            <g transform={`translate(${700 + 60}, ${470 - (1 - box) * 300})`}>
              <rect x={0} y={4} width={120} height={46} rx={4} fill="url(#ti)" stroke="#fff" strokeWidth={2} />
            </g>
          )}
          {f >= c("1,200") && <rect x={700} y={470 - (1 - slab) * 260} width={60} height={50} fill="#4a4e57" stroke="#fff" strokeWidth={3} />}
          <defs>
            <linearGradient id="ti" x1="0" x2="1">
              <stop offset="0" stopColor="#c9ced6" />
              <stop offset="1" stopColor="#7d838f" />
            </linearGradient>
          </defs>
        </svg>
        <div style={{ position: "absolute", left: 70, bottom: 28, fontFamily: BODY, fontWeight: 700, fontSize: 22, color: "rgba(255,255,255,.55)" }}>Illustration · not to scale</div>
        <Layer a={t1938} b={t1998 + 4} fade={6}>
          <div style={{ position: "absolute", left: 680, top: 560, display: "flex", gap: 16 }}>
            <Chip at={t1938} color={C.blue} size={34}>1938 · tunnel starts</Chip>
            {f >= c("Borglum died") && <Chip at={c("Borglum died")} color={C.red} size={34}>1941 · Borglum dies</Chip>}
          </div>
        </Layer>
        <div style={{ position: "absolute", left: 330, top: 300 }}>
          <Stamp text="Unfinished" at={c("unfinished")} color={C.red} size={70} rotate={-8} />
        </div>
        <Layer a={t1998} b={tClosed + 6}>
          <div style={{ position: "absolute", left: 120, top: 600, width: 560 }}>
            <Panel at={t1998} from="left" style={{ padding: 26 }}>
              <div style={{ fontFamily: HF, fontSize: 90, color: C.gold, lineHeight: 1 }}>1998</div>
              <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 28, color: C.dim, letterSpacing: 3 }}>SEALED · ~60 YEARS LATER</div>
            </Panel>
          </div>
          <div style={{ position: "absolute", left: 760, top: 570, display: "grid", gridTemplateColumns: "repeat(8, 64px)", gap: 8 }}>
            {Array.from({ length: 16 }, (_, i) => {
              const p = pop(f, c("16 porcelain") + i * 2, 12);
              return <div key={i} style={{ width: 64, height: 84, borderRadius: 6, background: "linear-gradient(#ffffff,#dfe6f0)", scale: String(p), boxShadow: "0 6px 14px rgba(0,0,0,.4)" }}>
                <div style={{ margin: "14px 10px", height: 4, background: "#9aa6bd", boxShadow: "0 12px 0 #9aa6bd, 0 24px 0 #9aa6bd, 0 36px 0 #9aa6bd" }} />
              </div>;
            })}
            <div style={{ gridColumn: "1 / span 8", fontFamily: BODY, fontWeight: 900, fontSize: 28, color: C.dim, letterSpacing: 3, marginTop: 8, opacity: ramp(f, c("16 porcelain"), 10) }}>16 PORCELAIN PANELS · IN A TITANIUM VAULT</div>
          </div>
          <div style={{ position: "absolute", right: 120, top: 180 }}>
            <Panel at={c("1,200")} from="right" style={{ padding: 24 }}>
              <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 28, color: C.dim, letterSpacing: 3 }}>GRANITE CAPSTONE</div>
              <Counter from={0} to={1200} suffix=" LB" at={c("1,200")} dur={20} size={100} color="#fff" />
            </Panel>
          </div>
        </Layer>
        <Sfx src="whoosh.wav" at={c("tunnel")} volume={0.4} />
        <Sfx src="stamp.wav" at={c("unfinished")} volume={0.6} />
        <Sfx src="pop.wav" at={c("A titanium")} />
        <Sfx src="boom.wav" at={c("1,200") + 8} volume={0.7} />
      </Layer>
      <Layer a={tClosed} b={end} fade={6}>
        <Photo src="rushmore.jpg" from={tClosed} dur={end - tClosed} zoom={[1.25, 1.1]} dim={0.6} />
        <Center style={{ gap: 26 }}>
          <Chip at={tClosed} color={C.red} size={50}>Closed to the public</Chip>
          <Headline text="A message for the *future*" at={c("It's a message")} size={120} />
        </Center>
      </Layer>
    </SceneShell>
  );
};

/* =============================== #1 ALASKA =============================== */
const DateLineClock: React.FC<{ x: number; at: number; day: string; time: string; color: string }> = ({ x, at, day, time, color }) => (
  <div style={{ position: "absolute", left: x, top: 640 }}>
    <Panel at={at} style={{ padding: 22, textAlign: "center", width: 360 }}>
      <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 28, color, letterSpacing: 3 }}>{day}</div>
      <div style={{ fontFamily: HF, fontSize: 80, color: "#fff", lineHeight: 1 }}>{time}</div>
    </Panel>
  </div>
);

export const F1: React.FC = () => {
  const f = useCurrentFrame();
  const id = "f1";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tReal = c("But the real"), tHow = c("Here's how"), tWeird = c("And it gets");
  const usProj = geoAlbersUsa().scale(1500).translate([960, 560]);
  const zoomT = lerp(f, [tHow, c("180th") + 10], [0, 1]);
  const rotLon = interpolate(zoomT, [0, 1], [150, 178]);
  const sc = interpolate(zoomT, [0, 1], [900, 2300]);
  const glob = geoOrthographic().rotate([rotLon, -57]).scale(sc).translate([960, 560]);
  const gp = geoPath(glob);
  const semi = glob([179.6, 51.95]);
  return (
    <SceneShell id={id} n={1}>
      <Sfx src="riser.wav" at={0} volume={0.4} />
      <Layer a={0} b={tReal + 6} fade={6} style={bg(50, 50)}>
        <GeoMap projection={usProj} states={LOWER48} showWorld={false} stateFill={(n) => (n === "Maine" && f >= c("Maine") ? C.red : C.landHi)} />
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 150 }}>
          <Headline text="The *easternmost* state?" at={c("What's the")} size={110} />
        </AbsoluteFill>
        <div style={{ position: "absolute", left: 1450, top: 260 }}>
          <Chip at={c("Maine")} color={C.red} size={56}>Maine?</Chip>
        </div>
        <Sfx src="pop.wav" at={c("Maine")} />
      </Layer>
      <Layer a={tReal} b={tWeird + 6} fade={6} style={bg(50, 50)}>
        <GeoMap projection={glob} sphere graticule stateFill={(n) => (n === "Alaska" ? C.gold : C.land)} worldFill="#1b2b4a">
          {() => (
            <g>
              {f >= c("180th") && (
                <path
                  d={gp({ type: "LineString", coordinates: [[180, 85], [180, 60], [180, 40], [180, 20]] }) ?? ""}
                  stroke={C.red}
                  strokeWidth={7}
                  fill="none"
                  strokeDasharray="3000"
                  strokeDashoffset={3000 * (1 - ramp(f, c("180th"), 25))}
                />
              )}
              {f >= c("farthest east") && semi && (
                <g>
                  <circle cx={semi[0]} cy={semi[1]} r={40 + 8 * Math.sin(f / 5)} fill="none" stroke={C.gold} strokeWidth={6} />
                </g>
              )}
            </g>
          )}
        </GeoMap>
        <Layer a={tReal} b={tHow + 4}>
          <AbsoluteFill style={{ alignItems: "center", paddingTop: 150 }}>
            <Headline text="It's *Alaska*" at={c("is Alaska")} size={160} />
          </AbsoluteFill>
          <div style={{ position: "absolute", right: 110, top: 380, display: "flex", flexDirection: "column", gap: 22, alignItems: "flex-end" }}>
            <Chip at={c("northernmost")} color={C.blue} size={48}>Northernmost ✓</Chip>
            <Chip at={c("westernmost")} color={C.blue} size={48}>Westernmost ✓</Chip>
            <Chip at={c("easternmost", 1)} color={C.red} size={48}>Easternmost ✓</Chip>
          </div>
          <Sfx src="stamp.wav" at={c("is Alaska")} volume={0.6} />
          <Sfx src="pop.wav" at={c("northernmost")} />
          <Sfx src="pop.wav" at={c("westernmost")} />
          <Sfx src="pop.wav" at={c("easternmost", 1)} />
        </Layer>
        <Layer a={c("180th")} b={tWeird + 6}>
          <div style={{ position: "absolute", left: 120, top: 200, fontFamily: HF, fontSize: 54, color: "#fff", opacity: ramp(f, c("the line that"), 10), textShadow: "0 4px 14px #000" }}>EASTERN<br />HEMISPHERE</div>
          <div style={{ position: "absolute", right: 120, top: 200, fontFamily: HF, fontSize: 54, color: "#fff", opacity: ramp(f, c("the line that"), 10), textAlign: "right", textShadow: "0 4px 14px #000" }}>WESTERN<br />HEMISPHERE</div>
          <div style={{ position: "absolute", left: 790, top: 175, fontFamily: BODY, fontWeight: 900, fontSize: 30, color: C.red, letterSpacing: 2, textShadow: "0 3px 10px #000" }}>180° MERIDIAN</div>
          {semi && (
            <div style={{ position: "absolute", left: semi[0] - 560, top: semi[1] + 60 }}>
              <Chip at={c("farthest east")} color={C.gold} size={34} style={{ color: "#1a1a1a" }}>Farthest east point of the U.S.</Chip>
            </div>
          )}
        </Layer>
      </Layer>
      <Layer a={tWeird} b={end} fade={6} style={{ background: "#0f2f57" }}>
        <svg width={1920} height={1080} style={{ position: "absolute" }}>
          <path d="M520,330 C600,250 760,260 800,340 C840,430 760,520 640,520 C540,520 470,420 520,330 Z" fill="#3a4b66" stroke="#fff" strokeWidth={3} opacity={ramp(f, tWeird + 4, 12)} />
          <path d="M1170,380 C1220,340 1300,350 1310,400 C1320,450 1260,480 1210,470 C1160,460 1140,420 1170,380 Z" fill="#2c5aa0" stroke="#fff" strokeWidth={3} opacity={ramp(f, c("Diomede"), 12)} />
          <line x1={980} x2={980} y1={120} y2={1000 * ramp(f, c("But the international"), 25) + 120} stroke={C.red} strokeWidth={6} strokeDasharray="22 14" />
          {f >= c("2.4") && (
            <g opacity={ramp(f, c("2.4"), 10)}>
              <line x1={810} x2={1160} y1={420} y2={420} stroke={C.gold} strokeWidth={5} />
              <line x1={810} x2={810} y1={400} y2={440} stroke={C.gold} strokeWidth={5} />
              <line x1={1160} x2={1160} y1={400} y2={440} stroke={C.gold} strokeWidth={5} />
            </g>
          )}
        </svg>
        <div style={{ position: "absolute", left: 830, top: 440, width: 320, textAlign: "center" }}>
          {f >= c("2.4") && <Counter from={0} to={2.4} decimals={1} suffix=" MI" at={c("2.4")} dur={20} size={80} color={C.gold} />}
        </div>
        <div style={{ position: "absolute", left: 990, top: 130, fontFamily: BODY, fontWeight: 900, fontSize: 28, color: C.red, letterSpacing: 2, opacity: ramp(f, c("But the international"), 10) }}>INTERNATIONAL DATE LINE</div>
        <div style={{ position: "absolute", left: 470, top: 200, fontFamily: HF, fontSize: 52, color: "#fff", opacity: ramp(f, c("Russia's"), 10) }}>BIG DIOMEDE · RUSSIA</div>
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 150 }}>
          <Headline text="It gets *weirder*" at={tWeird} size={110} out={c("Diomede") - 4} />
        </AbsoluteFill>
        <div style={{ position: "absolute", left: 1110, top: 250, fontFamily: HF, fontSize: 52, color: "#fff", opacity: ramp(f, c("Diomede"), 10) }}>LITTLE DIOMEDE · USA</div>
        <DateLineClock x={460} at={c("almost a full")} day="TUESDAY" time="12:00 PM" color={C.gold} />
        <DateLineClock x={1110} at={c("almost a full")} day="MONDAY" time="3:00 PM" color={C.dim} />
        <div style={{ position: "absolute", left: 0, right: 0, top: 545, textAlign: "center", opacity: 1 - ramp(f, c("They're nicknamed"), 8) }}>
          {f >= c("almost a full") && <Chip at={c("almost a full") + 10} color={C.red} size={40}>≈ 21 hours apart</Chip>}
        </div>
        <div style={{ position: "absolute", left: 420, top: 560 }}>
          <Stamp text="Tomorrow Island" at={c("Tomorrow")} color={C.gold} size={54} rotate={-4} />
        </div>
        <div style={{ position: "absolute", left: 1120, top: 560 }}>
          <Stamp text="Yesterday Island" at={c("Yesterday")} color={C.blue} size={54} rotate={4} />
        </div>
        <div style={{ position: "absolute", left: 70, bottom: 28, fontFamily: BODY, fontWeight: 700, fontSize: 22, color: "rgba(255,255,255,.55)" }}>Simplified map · not to scale</div>
        <Sfx src="ding.wav" at={c("almost a full") + 10} volume={0.35} />
        <Sfx src="stamp.wav" at={c("Yesterday")} volume={0.5} />
        <Sfx src="stamp.wav" at={c("Tomorrow")} volume={0.5} />
      </Layer>
    </SceneShell>
  );
};

/* =============================== OUTRO + END SCREEN =============================== */
const TILES: [number, string, string][] = [
  [10, "pennies.jpg", "Penny"], [9, "flag.jpg", "Flag"], [8, "highway.jpg", "Point Roberts"], [7, "statue_green.jpg", "Liberty"], [6, "superior.jpg", "Great Lakes"],
  [5, "badwater.jpg", "Death Valley"], [4, "canyon_sunset.jpg", "Grand Canyon"], [3, "lava.jpg", "Hawaii"], [2, "rushmore.jpg", "Rushmore"], [1, "alaska.jpg", "Alaska"],
];

export const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const id = "outro";
  const c = (p: string, n = 0) => cue(id, p, n);
  const end = sceneFrames(id);
  const tEnd = voEnd(id) + 10;
  const tSub = c("hit subscribe");
  const clicked = f >= tSub + 14;
  return (
    <SceneShell id={id} hud={false} captions={f < tEnd}>
      <Layer a={0} b={tEnd + 6} fade={6} style={bg(50, 40)}>
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 90 }}>
          <Headline text="Which one did you *not* know?" at={2} size={90} />
        </AbsoluteFill>
        <div style={{ position: "absolute", left: 160, top: 225, display: "grid", gridTemplateColumns: "repeat(5, 300px)", gap: 20 }}>
          {TILES.map(([n, img, name], i) => {
            const p = pop(f, 4 + i * 3, 13);
            return (
              <div key={n} style={{ position: "relative", width: 300, height: 200, borderRadius: 18, overflow: "hidden", scale: String(p), boxShadow: "0 14px 30px rgba(0,0,0,.5)" }}>
                <Img src={staticFile(`img/${img}`)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(transparent 40%, rgba(0,0,0,.85))" }} />
                <div style={{ position: "absolute", left: 14, top: 10, fontFamily: HF, fontSize: 46, color: "#fff", background: C.red, padding: "0 12px", borderRadius: 10 }}>#{n}</div>
                <div style={{ position: "absolute", left: 16, bottom: 10, fontFamily: HF, fontSize: 38, color: "#fff" }}>{name.toUpperCase()}</div>
              </div>
            );
          })}
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 690, display: "flex", justifyContent: "center" }}>
          <div
            style={{
              fontFamily: BODY, fontWeight: 900, fontSize: 52, letterSpacing: 2, color: "#fff",
              background: clicked ? "#3a3f4b" : C.red, padding: "18px 56px", borderRadius: 60,
              scale: String(pop(f, tSub - 6, 12) * (f >= tSub + 10 && f < tSub + 16 ? 0.92 : 1)), opacity: ramp(f, tSub - 6, 6),
            }}
          >
            {clicked ? "SUBSCRIBED ✓" : "SUBSCRIBE"}
          </div>
        </div>
        {f >= tSub - 6 && (
          <svg width={1920} height={1080} style={{ position: "absolute" }}>
            <path
              transform={`translate(${lerp(f, [tSub - 6, tSub + 10], [1400, 1000])}, ${lerp(f, [tSub - 6, tSub + 10], [980, 745])}) scale(2)`}
              d="M0,0 L0,34 L9,26 L15,40 L21,37 L15,24 L27,24 Z"
              fill="#fff"
              stroke="#000"
              strokeWidth={2}
            />
          </svg>
        )}
        <Sfx src="tick.wav" at={tSub + 12} volume={0.9} />
        <Sfx src="ding.wav" at={tSub + 14} volume={0.4} />
      </Layer>
      <Layer a={tEnd} b={end + 2} fade={10} style={bg(50, 50)}>
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 110 }}>
          <Headline text="Thanks for *watching*" at={tEnd + 4} size={110} />
        </AbsoluteFill>
        {/* placeholders for YouTube end-screen elements */}
        <div style={{ position: "absolute", left: 150, top: 380, width: 760, height: 428, borderRadius: 24, border: "4px dashed rgba(255,255,255,.35)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: HF, fontSize: 56, color: "rgba(255,255,255,.6)", opacity: ramp(f, tEnd + 8, 10) }}>
          WATCH NEXT
        </div>
        <div style={{ position: "absolute", right: 150, top: 380, width: 760, height: 428, borderRadius: 24, border: "4px dashed rgba(255,255,255,.35)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: HF, fontSize: 56, color: "rgba(255,255,255,.6)", opacity: ramp(f, tEnd + 12, 10) }}>
          BEST FOR YOU
        </div>
      </Layer>
    </SceneShell>
  );
};

export { LOWER48 };
