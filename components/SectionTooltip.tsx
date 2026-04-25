import type { SectionFeatureProperties } from "@/lib/types";
import { formatMetric, getBivariateClassLabel } from "@/lib/presentation";

type SectionTooltipProps = {
  x: number;
  y: number;
  section: SectionFeatureProperties;
};

export function SectionTooltip({ x, y, section }: SectionTooltipProps) {
  const isNoData = !section.has_data;
  return (
    <aside className="section-tooltip" style={{ left: x + 14, top: y + 14 }} role="status" aria-live="polite">
      <p className="tooltip-row">
        <strong>section_id:</strong> {section.section_id}
      </p>
      <p className="tooltip-row">
        <strong>{"Secci\u00f3n:"}</strong> {section.seccion}
      </p>
      <p className="tooltip-row">
        <strong>% PAN 2018:</strong> {formatMetric(section.pct_pan_2018)}
      </p>
      <p className="tooltip-row">
        <strong>% PAN 2021:</strong> {formatMetric(section.pct_pan_2021)}
      </p>
      <p className="tooltip-row">
        <strong>Delta pp:</strong> {formatMetric(section.delta_pan_pp)}
      </p>
      <p className="tooltip-row">
        <strong>Clase:</strong> {getBivariateClassLabel(section.bivariate_class)}
      </p>
      <p className="tooltip-row">
        <strong>Datos completos:</strong> {section.has_data ? "S\u00ed" : "No"}
      </p>
      {isNoData ? <p className="tooltip-warning">Sin datos suficientes</p> : null}
    </aside>
  );
}
