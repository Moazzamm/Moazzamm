import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';

// Restrained film grain: SVG turbulence, reseeded every 3 frames, very low opacity.
export const Grain: React.FC<{opacity?: number}> = ({opacity = 0.07}) => {
  const frame = useCurrentFrame();
  const seed = Math.floor(frame / 3) % 50;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'overlay', opacity}}>
      <svg width="100%" height="100%">
        <filter id={`g${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={seed} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#g${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

// Soft vignette for depth without decoration.
export const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      pointerEvents: 'none',
      background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)',
    }}
  />
);
