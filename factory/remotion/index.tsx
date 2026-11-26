import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {Main, Thumb} from './Main';

const Root: React.FC = () => (
  <>
    <Composition id="Video" component={Main} width={1920} height={1080} fps={30} durationInFrames={300}
      defaultProps={{dur: 10, beats: [], items: [], captions: [], accent: '#fff', series: ''} as any}
      calculateMetadata={({props}: any) => ({durationInFrames: Math.ceil(props.dur * 30)})} />
    <Composition id="Thumb" component={Thumb} width={1280} height={720} fps={30} durationInFrames={1}
      defaultProps={{img: 'grain.png', lines: []} as any} />
  </>
);
registerRoot(Root);
