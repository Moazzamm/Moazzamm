import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {C} from './theme';
import {TIMING, type SceneTiming} from './lib/timing';
import {KineticCaptions} from './components/Captions';
import {Sting} from './components/Sting';
import {Intro} from './scenes/Intro';
import {OlympusMons} from './scenes/OlympusMons';
import {Hexagon} from './scenes/Hexagon';
import {RedSpot} from './scenes/RedSpot';
import {NeutronStar} from './scenes/NeutronStar';
import {Magnetar} from './scenes/Magnetar';
import {M87} from './scenes/M87';
import {MostDistant} from './scenes/MostDistant';
import {Outro} from './scenes/Outro';
import {TitleCard} from './scenes/TitleCard';

const SCENES: Record<string, React.FC<{s: SceneTiming}>> = {
  intro: Intro, n7: OlympusMons, n6: Hexagon, n5: RedSpot, n4: NeutronStar, n3: Magnetar, n2: M87, n1: MostDistant, outro: Outro,
};
// Words highlighted in the kinetic captions (numbers are always highlighted).
const KEYWORDS: Record<string, string[]> = {
  intro: ['storm', 'jupiter', 'earth', 'five', 'huge', 'dense', 'violent', 'everest', 'billion', 'seven', 'extreme'],
  n7: ['olympus', 'everest', 'twenty-five', 'three', 'arizona', 'cliffs', 'six', 'tectonic', 'lava'],
  n6: ['straight', 'six-sided', 'thirty', 'two', 'earths', 'hurricane', 'voyager', 'cassini', 'hundred'],
  n5: ['wider', 'sixteen', 'one', 'shrinking', 'two', 'juno', 'three', 'hundred', 'fifty', 'deeper'],
  n4: ['sugar', 'neutron', 'city', 'densest', 'billion', 'mountain', 'hundreds', 'lighthouse'],
  n3: ['magnetar', 'strongest', 'sixth', 'credit', 'fifty', 'thousand', 'tenth', 'hundred'],
  n2: ['black', 'photographed', 'shadow', 'fifty-five', 'million', 'billion', 'forty', 'swallow'],
  n1: ['distant', 'mom-z14', 'webb', 'thirteen', 'billion', 'hundred', 'two', 'percent', 'baby', 'bright'],
  outro: ['real', 'comments'],
};

export const Documentary: React.FC = () => {
  let cursor = 0;
  const blocks: React.ReactNode[] = [];
  TIMING.scenes.forEach((s) => {
    const Comp = SCENES[s.id];
    blocks.push(
      <Sequence key={s.id} from={cursor} durationInFrames={s.durationInFrames} name={s.id}>
        <Comp s={s} />
        {s.num ? <Sting num={s.num} name={s.title} total={s.durationInFrames} /> : null}
        <Sequence from={Math.round(s.leadIn * TIMING.fps)} name={`VO ${s.id}`}>
          <Audio src={staticFile(s.vo)} />
        </Sequence>
        {s.num ? (
          <>
            <Audio src={staticFile('audio/sfx_whoosh.wav')} volume={0.55} />
            <Sequence from={8}><Audio src={staticFile('audio/sfx_boom.wav')} volume={0.7} /></Sequence>
          </>
        ) : null}
        <KineticCaptions cues={s.cues} keywords={KEYWORDS[s.id]} />
      </Sequence>,
    );
    cursor += s.durationInFrames;
    if (s.id === 'intro') {
      blocks.push(
        <Sequence key="title" from={cursor} durationInFrames={TIMING.titleCardFrames} name="Title">
          <TitleCard />
          <Audio src={staticFile('audio/sfx_boom.wav')} volume={0.6} />
        </Sequence>,
      );
      cursor += TIMING.titleCardFrames;
    }
  });
  return (
    <AbsoluteFill style={{backgroundColor: C.space}}>
      {blocks}
      <Audio src={staticFile('audio/music_bed.wav')} volume={0.22} />
      <AbsoluteFill style={{pointerEvents: 'none', background: 'radial-gradient(ellipse at 50% 45%, transparent 60%, rgba(0,0,0,0.5) 100%)'}} />
    </AbsoluteFill>
  );
};
