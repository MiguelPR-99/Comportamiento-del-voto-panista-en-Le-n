import type { FeatureCollection, Geometry } from "geojson";
import type { EditorialMapSpec, SectionFeatureProperties, SectionsGeoJSON } from "@/lib/types";

type BBox = [number, number, number, number];

function asString(value: unknown, fallback = ""): string {
  if (value === null || value === undefined) {
    return fallback;
  }
  return String(value);
}

function asNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function asBoolean(value: unknown): boolean {
  return String(value).toLowerCase() === "true";
}

function visitCoordinates(geometry: Geometry, callback: (lon: number, lat: number) => void): void {
  if (!geometry || !("coordinates" in geometry)) {
    return;
  }

  const walk = (node: unknown): void => {
    if (!Array.isArray(node)) {
      return;
    }
    if (node.length >= 2 && typeof node[0] === "number" && typeof node[1] === "number") {
      callback(node[0], node[1]);
      return;
    }
    for (const child of node) {
      walk(child);
    }
  };

  walk(geometry.coordinates);
}

export function toSectionProps(properties: Record<string, unknown> | undefined): SectionFeatureProperties | null {
  if (!properties) {
    return null;
  }
  return {
    schema_version: asString(properties.schema_version, "1.0.0"),
    section_id: asString(properties.section_id),
    entidad: asString(properties.entidad),
    municipio: asString(properties.municipio),
    municipio_nombre: properties.municipio_nombre ? asString(properties.municipio_nombre) : null,
    distrito_local: properties.distrito_local ? asString(properties.distrito_local) : null,
    seccion: asString(properties.seccion),
    pan_2018_votos: asNumber(properties.pan_2018_votos),
    pan_2021_votos: asNumber(properties.pan_2021_votos),
    total_2018: asNumber(properties.total_2018),
    total_2021: asNumber(properties.total_2021),
    pct_pan_2018: asNumber(properties.pct_pan_2018),
    pct_pan_2021: asNumber(properties.pct_pan_2021),
    delta_pan_pp: asNumber(properties.delta_pan_pp),
    vote_share_bin: asString(properties.vote_share_bin, "no_data") as SectionFeatureProperties["vote_share_bin"],
    delta_bin: asString(properties.delta_bin, "no_data") as SectionFeatureProperties["delta_bin"],
    bivariate_class: asString(properties.bivariate_class, "no_data") as SectionFeatureProperties["bivariate_class"],
    color_hex: properties.color_hex ? asString(properties.color_hex) : null,
    has_data: asBoolean(properties.has_data),
    is_in_inset: asBoolean(properties.is_in_inset),
    issue_type: asString(properties.issue_type, "none")
  };
}

export function computeSectionsBBox(sections: SectionsGeoJSON): BBox | null {
  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;

  for (const feature of sections.features) {
    if (!feature.geometry) {
      continue;
    }
    visitCoordinates(feature.geometry, (lon, lat) => {
      if (lon < minX) minX = lon;
      if (lat < minY) minY = lat;
      if (lon > maxX) maxX = lon;
      if (lat > maxY) maxY = lat;
    });
  }

  if (!Number.isFinite(minX) || !Number.isFinite(minY) || !Number.isFinite(maxX) || !Number.isFinite(maxY)) {
    return null;
  }
  return [minX, minY, maxX, maxY];
}

function shrinkBounds(bounds: BBox, factor: number): BBox {
  const [minX, minY, maxX, maxY] = bounds;
  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;
  const halfWidth = ((maxX - minX) * factor) / 2;
  const halfHeight = ((maxY - minY) * factor) / 2;
  return [centerX - halfWidth, centerY - halfHeight, centerX + halfWidth, centerY + halfHeight];
}

export function deriveInsetView(sections: FeatureCollection, spec: EditorialMapSpec): {
  center: [number, number];
  zoom: number;
  bounds: BBox;
  isDerivedFromData: boolean;
} {
  const mainBounds = spec.main_view.bounds;
  const bboxFromData = computeSectionsBBox(sections as SectionsGeoJSON);
  const baseBounds = bboxFromData ?? mainBounds ?? [-101.812659, 20.863254, -101.37249, 21.336565];
  const insetBounds = shrinkBounds(baseBounds, 0.42);
  const center: [number, number] = [
    spec.inset_view.center?.[0] ?? (insetBounds[0] + insetBounds[2]) / 2,
    spec.inset_view.center?.[1] ?? (insetBounds[1] + insetBounds[3]) / 2
  ];
  const zoom = spec.inset_view.zoom ?? spec.main_view.zoom + 1.6;

  return {
    center,
    zoom,
    bounds: insetBounds,
    isDerivedFromData: !spec.inset_view.enabled
  };
}

