import type { BivariateClass, EditorialMapSpec } from "@/lib/types";
import { getBivariateClassLabel, normalizeEditorialText } from "@/lib/presentation";

type BivariateLegendProps = {
  spec: EditorialMapSpec;
  activeClass: string | null;
};

const ROWS = ["growth", "stable", "decline"] as const;
const COLS = ["low", "mid", "high"] as const;

export function BivariateLegend({ spec, activeClass }: BivariateLegendProps) {
  const classMap = spec.class_color_map;
  const counts = spec.legend.class_counts;

  return (
    <section className="legend-panel" aria-label="Leyenda bivariante">
      <h2 className="panel-title">Leyenda 3x3</h2>
      <p className="axis-label axis-y">{normalizeEditorialText(spec.legend.y_axis_label)}</p>
      <div className="legend-grid" role="grid" aria-label="Matriz bivariante 3 por 3">
        {ROWS.map((row) =>
          COLS.map((col) => {
            const cellClass = `${row}_${col}`;
            const color = classMap[cellClass] ?? spec.no_data_style.fill;
            const count = counts[cellClass] ?? 0;
            const readableLabel = getBivariateClassLabel(cellClass as BivariateClass);
            return (
              <div
                key={cellClass}
                className={`legend-cell ${activeClass === cellClass ? "legend-cell-active" : ""}`}
                style={{ backgroundColor: color }}
                role="gridcell"
                aria-label={`${readableLabel}: ${count} secciones`}
              >
                <span className="legend-name">{readableLabel}</span>
                <span className="legend-count">{count}</span>
              </div>
            );
          })
        )}
      </div>
      <p className="axis-label axis-x">{normalizeEditorialText(spec.legend.x_axis_label)}</p>
      <div className={`legend-no-data ${activeClass === "no_data" ? "legend-no-data-active" : ""}`}>
        <span className="legend-chip" style={{ backgroundColor: classMap.no_data }} />
        <span>Sin datos ({counts.no_data ?? 0})</span>
      </div>
    </section>
  );
}
