import type { BivariateClass } from "@/lib/types";

const BIVARIATE_CLASS_LABELS: Record<BivariateClass, string> = {
  growth_low: "Crecimiento + bajo apoyo",
  growth_mid: "Crecimiento + apoyo medio",
  growth_high: "Crecimiento + alto apoyo",
  stable_low: "Estable + bajo apoyo",
  stable_mid: "Estable + apoyo medio",
  stable_high: "Estable + alto apoyo",
  decline_low: "Ca\u00edda + bajo apoyo",
  decline_mid: "Ca\u00edda + apoyo medio",
  decline_high: "Ca\u00edda + alto apoyo",
  no_data: "Sin datos"
};

const TEXT_REPLACEMENTS: Array<[RegExp, string]> = [
  [/Le\u00c3\u00b3n/g, "Le\u00f3n"],
  [/Variaci\u00c3\u00b3n/g, "Variaci\u00f3n"],
  [/secci\u00c3\u00b3n/g, "secci\u00f3n"],
  [/Secci\u00c3\u00b3n/g, "Secci\u00f3n"],
  [/Variacion/g, "Variaci\u00f3n"],
  [/variacion/g, "variaci\u00f3n"],
  [/Seccion/g, "Secci\u00f3n"],
  [/seccion/g, "secci\u00f3n"],
  [/Exportacion/g, "Exportaci\u00f3n"],
  [/exportacion/g, "exportaci\u00f3n"],
  [/Creditos/g, "Cr\u00e9ditos"],
  [/creditos/g, "cr\u00e9ditos"]
];

export function getBivariateClassLabel(bivariateClass: BivariateClass): string {
  return BIVARIATE_CLASS_LABELS[bivariateClass] ?? bivariateClass;
}

export function formatMetric(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "N/D";
  }
  return value.toFixed(2);
}

export function normalizeEditorialText(text: string): string {
  let normalized = text;
  for (const [pattern, replacement] of TEXT_REPLACEMENTS) {
    normalized = normalized.replace(pattern, replacement);
  }
  return normalized;
}
