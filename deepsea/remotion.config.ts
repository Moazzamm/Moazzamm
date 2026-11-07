import {Config} from '@remotion/cli/config';

// 854x480 (480p, 16:9). JPEG frames keep the render light; H.264 output.
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(90);
Config.setConcurrency(4);
Config.setChromiumOpenGlRenderer('swangle');
