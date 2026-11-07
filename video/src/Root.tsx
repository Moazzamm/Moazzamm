import React from 'react';
import {Composition} from 'remotion';
import {Documentary} from './Documentary';
import {TIMING} from './lib/timing';
import {W, H} from './theme';

export const RemotionRoot: React.FC = () => (
  <Composition id="Documentary" component={Documentary} durationInFrames={TIMING.totalFrames} fps={TIMING.fps} width={W} height={H} />
);
