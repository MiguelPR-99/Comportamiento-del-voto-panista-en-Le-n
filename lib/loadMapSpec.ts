import type { EditorialMapSpec, SectionsGeoJSON } from "@/lib/types";

async function fetchJson<T>(url: string, label: string): Promise<T> {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`No fue posible cargar ${label} (${response.status}).`);
  }
  return (await response.json()) as T;
}

export function loadMapSpec(): Promise<EditorialMapSpec> {
  return fetchJson<EditorialMapSpec>("/config/editorial-map-spec.json", "editorial-map-spec.json");
}

export function loadSectionsGeoJSON(): Promise<SectionsGeoJSON> {
  return fetchJson<SectionsGeoJSON>("/data/secciones.geojson", "secciones.geojson");
}
