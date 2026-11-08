import React, { useMemo } from "react";
import { geoPath, GeoProjection, geoGraticule10 } from "d3-geo";
import { feature } from "topojson-client";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { Feature, FeatureCollection, Geometry } from "geojson";
import usTopo from "us-atlas/states-10m.json";
import worldTopo from "world-atlas/countries-50m.json";
import { C, H, W } from "../lib/theme";

type Props = { name: string };
const us = feature(usTopo as unknown as Topology, (usTopo as unknown as Topology).objects.states as GeometryCollection<Props>) as FeatureCollection<Geometry, Props>;
const world = feature(worldTopo as unknown as Topology, (worldTopo as unknown as Topology).objects.countries as GeometryCollection<Props>) as FeatureCollection<Geometry, Props>;

export const STATES = us.features;
export const COUNTRIES = world.features;
export const LOWER48 = STATES.filter((s) => !["Alaska", "Hawaii", "Puerto Rico", "American Samoa", "Guam", "Commonwealth of the Northern Mariana Islands", "United States Virgin Islands"].includes(s.properties.name));
export const state = (n: string) => STATES.find((s) => s.properties.name === n) as Feature<Geometry, Props>;
export const country = (n: string) => COUNTRIES.find((s) => s.properties.name === n) as Feature<Geometry, Props>;

export const GeoMap: React.FC<{
  projection: GeoProjection;
  stateFill?: (name: string) => string | undefined;
  showWorld?: boolean;
  showStates?: boolean;
  states?: Feature<Geometry, Props>[];
  graticule?: boolean;
  sphere?: boolean;
  children?: (path: ReturnType<typeof geoPath>, proj: GeoProjection) => React.ReactNode;
  worldFill?: string;
  usOutline?: string;
  w?: number;
  h?: number;
}> = ({ w = W, h = H, projection, stateFill, showWorld = true, showStates = true, states = STATES, graticule = false, sphere = false, children, worldFill = "#16223a", usOutline = "rgba(255,255,255,.18)" }) => {
  const path = geoPath(projection);
  const grat = useMemo(() => geoGraticule10(), []);
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
      {sphere && <path d={path({ type: "Sphere" }) ?? ""} fill="#0d2246" stroke="rgba(120,170,255,.35)" strokeWidth={3} />}
      {graticule && <path d={path(grat) ?? ""} fill="none" stroke="rgba(150,190,255,.12)" strokeWidth={1.2} />}
      {showWorld &&
        COUNTRIES.map((c, i) =>
          c.properties.name === "United States of America" && showStates ? null : (
            <path key={i} d={path(c) ?? ""} fill={worldFill} stroke="rgba(255,255,255,.08)" strokeWidth={1} />
          ),
        )}
      {showStates &&
        states.map((s, i) => (
          <path key={`s${i}`} d={path(s) ?? ""} fill={stateFill?.(s.properties.name) ?? C.land} stroke={usOutline} strokeWidth={1.2} />
        ))}
      {children?.(path, projection)}
    </svg>
  );
};
