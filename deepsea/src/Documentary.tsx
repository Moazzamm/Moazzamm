import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {TIMING, type SceneTiming} from './lib/timing';
import {Ocean, DepthMeter} from './components/Ocean';
import {Captions} from './components/Ui';
import {Hook, hookDepth, Sunlight, sunlightDepth} from './scenes/HookSunlight';
import {Twilight, twilightDepth, Midnight, midnightDepth} from './scenes/TwilightMidnight';
import {Why, whyDepth, Trench, trenchDepth, End, endDepth} from './scenes/WhyTrenchEnd';
import {Title} from './scenes/Title';

type DepthFn = (s: SceneTiming, f: number) => number;
const SCENES: Record<string, [React.FC<{s: SceneTiming}>, DepthFn]> = {
  hook: [Hook, hookDepth], sunlight: [Sunlight, sunlightDepth], twilight: [Twilight, twilightDepth], midnight: [Midnight, midnightDepth],
  why: [Why, whyDepth], trench: [Trench, trenchDepth], end: [End, endDepth],
};
const KEYWORDS: Record<string, string[]> = {
  hook: ['colossal', 'squid', 'baby', 'seven', 'tonne', 'largest', 'giants', 'invisible', 'eight'],
  sunlight: ['zero', 'four', 'japanese', 'largest', 'beginning'],
  twilight: ['two', 'twilight', 'oarfish', 'eight', 'longest', 'siphonophore', 'forty-five', 'whale', 'colony', 'clones'],
  midnight: ['thousand', 'freezing', 'snow', 'greenland', 'six', 'centimetre', 'hundred', 'isopod', 'woodlouse', 'five', 'forty-three'],
  why: ['gigantism', 'four', 'cold', 'oxygen', 'hunger', 'time', 'tiny', 'millimetre', 'enormous'],
  trench: ['six', 'hadal', 'hades', 'eight', 'hundred', 'snailfish', 'deepest', 'tmao', 'invisible', 'challenger', 'eleven'],
  end: ['thousandth', 'percent', 'deeper', 'subscribe'],
};

// Global timeline: [startFrame, scene | 'title'].
const LAYOUT: {start: number; dur: number; s?: SceneTiming}[] = (() => {
  const out: {start: number; dur: number; s?: SceneTiming}[] = [];
  let c = 0;
  for (const s of TIMING.scenes) {
    out.push({start: c, dur: s.durationInFrames, s});
    c += s.durationInFrames;
    if (s.id === 'hook') {
      out.push({start: c, dur: TIMING.titleCardFrames});
      c += TIMING.titleCardFrames;
    }
  }
  return out;
})();

export const depthAt = (g: number) => {
  const seg = LAYOUT.find((x) => g >= x.start && g < x.start + x.dur) ?? LAYOUT[LAYOUT.length - 1];
  if (!seg.s) return 0; // title card: back at the surface
  return SCENES[seg.s.id][1](seg.s, g - seg.start);
};

const World: React.FC = () => {
  const g = useCurrentFrame();
  const d = depthAt(g);
  const speed = Math.abs(d - depthAt(Math.max(0, g - 1)));
  return <Ocean depth={d} speed={Math.min(speed, 60)} />;
};

// Depth gauge sits above every scene; it hides on the title card and fades during the explainer and ending.
const Meter: React.FC = () => {
  const g = useCurrentFrame();
  const seg = LAYOUT.find((x) => g >= x.start && g < x.start + x.dur) ?? LAYOUT[LAYOUT.length - 1];
  let o = 1;
  if (!seg.s) o = 0;
  else if (seg.s.id === 'why' || seg.s.id === 'end') {
    const local = g - seg.start;
    o = Math.max(0, 1 - local / 20) + (seg.s.id === 'why' ? Math.max(0, (local - (seg.dur - 20)) / 20) : 0);
  }
  return <DepthMeter depth={depthAt(g)} opacity={Math.min(1, o)} />;
};

export const Documentary: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <World />
    {LAYOUT.map((seg, i) => {
      if (!seg.s) {
        return (
          <Sequence key="title" from={seg.start} durationInFrames={seg.dur} name="Title">
            <Title />
            <Audio src={staticFile('audio/sfx_boom.wav')} volume={0.55} />
          </Sequence>
        );
      }
      const s = seg.s;
      const Comp = SCENES[s.id][0];
      return (
        <Sequence key={s.id} from={seg.start} durationInFrames={seg.dur} name={s.id}>
          <Comp s={s} />
          <Sequence from={Math.round(s.leadIn * TIMING.fps)}>
            <Audio src={staticFile(s.vo)} />
          </Sequence>
          {i > 0 ? <Audio src={staticFile('audio/sfx_sonar.wav')} volume={0.35} /> : null}
          <Captions cues={s.cues} keywords={KEYWORDS[s.id]} />
        </Sequence>
      );
    })}
    <Meter />
    <Audio src={staticFile('audio/music_score.wav')} volume={0.26} />
  </AbsoluteFill>
);
