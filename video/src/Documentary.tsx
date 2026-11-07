import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, interpolate} from 'remotion';
import {C} from './theme';
import {TIMING, sceneById, type SceneTiming} from './lib/timing';
import {Captions} from './components/Captions';
import {Vignette} from './components/Grain';
import {MapReveal} from './scenes/MapReveal';
import {Descent} from './scenes/Descent';
import {IceCutaway} from './scenes/IceCutaway';
import {CaveSurvey} from './scenes/CaveSurvey';
import {ForestView} from './scenes/ForestView';
import {FinalReturn} from './scenes/FinalReturn';
import {TitleCard} from './scenes/TitleCard';

const COMPONENTS: Record<string, React.FC<{s: SceneTiming}>> = {
  open: MapReveal,
  ocean: Descent,
  ice: IceCutaway,
  cave: CaveSurvey,
  forest: ForestView,
  final: FinalReturn,
};

// Ambience sits ~20 dB under narration; fades at scene edges.
const bedVolume = (dur: number) => (f: number) =>
  interpolate(f, [0, 20, dur - 25, dur], [0, 0.9, 0.9, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

export const Documentary: React.FC = () => {
  let cursor = 0;
  const blocks: React.ReactNode[] = [];
  TIMING.scenes.forEach((s) => {
    const Comp = COMPONENTS[s.id];
    blocks.push(
      <Sequence key={s.id} from={cursor} durationInFrames={s.durationInFrames} name={s.title}>
        <Comp s={s} />
        <Sequence from={Math.round(s.leadIn * TIMING.fps)} name={`VO ${s.id}`}>
          <Audio src={staticFile(s.vo)} />
        </Sequence>
        <Audio src={staticFile(`audio/amb_${s.id}.wav`)} volume={bedVolume(s.durationInFrames)} />
        <Captions cues={s.cues} />
      </Sequence>,
    );
    cursor += s.durationInFrames;
    if (s.id === 'open') {
      blocks.push(
        <Sequence key="title" from={cursor} durationInFrames={TIMING.titleCardFrames} name="Title">
          <TitleCard />
          <Audio src={staticFile('audio/amb_open.wav')} startFrom={Math.round(40 * TIMING.fps)} volume={0.5} />
        </Sequence>,
      );
      cursor += TIMING.titleCardFrames;
    }
  });
  void sceneById;
  return (
    <AbsoluteFill style={{backgroundColor: C.navy}}>
      {blocks}
      <Vignette />
      {/* Film grain is added in post (ffmpeg noise filter) — far cheaper than per-frame SVG turbulence. */}
    </AbsoluteFill>
  );
};
