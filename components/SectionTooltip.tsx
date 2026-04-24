import type { SectionFeatureProperties } from "@/lib/types";

type SectionTooltipProps = {
  x: number;
  y: number;
  section: SectionFeatureProperties;
};

function formatNumber(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "N/D";
  }
  return `${value.toFixed(2)}`;
}

export function SectionTooltip({ x, y, section }: SectionTooltipProps) {
  const isNoData = !section.has_data;
  return (
    <aside className="section-tooltip" style={{ left: x + 14, top: y + 14 }} role="status" aria-live="polite">
      <p className="tooltip-row">
        <strong>section_id:</strong> {section.section_id}
      </p>
      <p className="tooltip-row">
        <strong>Seccion:</strong> {section.seccion}
      </p>
      <p className="tooltip-row">
        <strong>% PAN 2018:</strong> {formatNumber(section.pct_pan_2018)}
      </p>
      <p className="tooltip-row">
        <strong>% PAN 2021:</strong> {formatNumber(section.pct_pan_2021)}
      </p>
      <p className="tooltip-row">
        <strong>Delta pp:</strong> {formatNumber(section.delta_pan_pp)}
      </p>
      <p className="tooltip-row">
        <strong>Clase:</strong> {section.bivariate_class}
      </p>
      <p className="tooltip-row">
        <strong>has_data:</strong> {section.has_data ? "true" : "false"}
      </p>
      {isNoData ? <p className="tooltip-warning">Sin datos suficientes</p> : null}
    </aside>
  );
}
