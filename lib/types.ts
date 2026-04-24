import type { Feature, FeatureCollection, Geometry } from "geojson";

export type BivariateClass =
  | "decline_low"
  | "decline_mid"
  | "decline_high"
  | "stable_low"
  | "stable_mid"
  | "stable_high"
  | "growth_low"
  | "growth_mid"
  | "growth_high"
  | "no_data";

export type VoteShareBin = "low" | "mid" | "high" | "no_data";
export type DeltaBin = "decline" | "stable" | "growth" | "no_data";

export type SectionFeatureProperties = {
  schema_version: string;
  section_id: string;
  entidad: string;
  municipio: string;
  municipio_nombre: string | null;
  distrito_local: string | null;
  seccion: string;
  pan_2018_votos: number | null;
  pan_2021_votos: number | null;
  total_2018: number | null;
  total_2021: number | null;
  pct_pan_2018: number | null;
  pct_pan_2021: number | null;
  delta_pan_pp: number | null;
  vote_share_bin: VoteShareBin;
  delta_bin: DeltaBin;
  bivariate_class: BivariateClass;
  color_hex: string | null;
  has_data: boolean;
  is_in_inset: boolean;
  issue_type: string;
};

export type SectionFeature = Feature<Geometry, SectionFeatureProperties>;
export type SectionsGeoJSON = FeatureCollection<Geometry, SectionFeatureProperties>;

export type MainView = {
  layout: string;
  center: [number, number];
  zoom: number;
  bounds?: [number, number, number, number];
};

export type InsetView = {
  layout: string;
  center: [number, number];
  zoom: number;
  enabled?: boolean;
  notes?: string;
};

export type LegendSpec = {
  type: string;
  x_axis_label: string;
  y_axis_label: string;
  bins: {
    vote_share_bin: Record<string, string>;
    delta_bin: Record<string, string>;
  };
  matrix: {
    rows: string[];
    cols: string[];
    class_grid: string[][];
  };
  class_counts: Record<string, number>;
  include_no_data: boolean;
};

export type EditorialMapSpec = {
  schema_version: string;
  project_id: string;
  title: string;
  subtitle: string;
  source_lines: string[];
  author_note: string;
  palette: {
    family: string;
    class_color_map: Record<string, string>;
    neutral_no_data: string;
  };
  class_color_map: Record<string, string>;
  legend: LegendSpec;
  main_view: MainView;
  inset_view: InsetView;
  scale_bar_km: number;
  no_data_style: {
    fill: string;
    hatch: string;
    stroke: string;
  };
  interaction_policy: {
    layout: string;
    mode: string;
    allow_hover: boolean;
    allow_click: boolean;
    allow_scroll_zoom: boolean;
    allow_filters: boolean;
    allow_tabs: boolean;
    allow_sidebar_metrics: boolean;
  };
  data_files: {
    secciones: string;
  };
  qa_summary?: {
    feature_count: number;
    class_counts: Record<string, number>;
    warnings_count: number;
  };
  warnings?: string[];
};

export const ALLOWED_BIVARIATE_CLASSES: BivariateClass[] = [
  "decline_low",
  "decline_mid",
  "decline_high",
  "stable_low",
  "stable_mid",
  "stable_high",
  "growth_low",
  "growth_mid",
  "growth_high",
  "no_data"
];
