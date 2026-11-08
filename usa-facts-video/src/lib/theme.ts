import { loadFont as loadAnton } from "@remotion/google-fonts/Anton";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

export const { fontFamily: HEAD } = loadAnton("normal", { weights: ["400"], subsets: ["latin"] });
export const { fontFamily: BODY } = loadInter("normal", {
  weights: ["500", "700", "900"],
  subsets: ["latin"],
});

export const C = {
  bg: "#0a0f1c",
  bg2: "#111a2e",
  ink: "#ffffff",
  dim: "#9fb0cc",
  red: "#ff3b4e",
  blue: "#3d8bff",
  gold: "#ffc93c",
  green: "#2ee6a6",
  copper: "#c8743a",
  patina: "#5fb8a0",
  water: "#1d6fd6",
  land: "#1c2a45",
  landHi: "#2c4372",
};

export const FPS = 30;
export const W = 1920;
export const H = 1080;
