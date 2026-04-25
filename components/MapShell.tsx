"use client";

import { toPng } from "html-to-image";
import { useEffect, useRef, useState } from "react";
import { BivariateLegend } from "@/components/BivariateLegend";
import { EditorialMap } from "@/components/EditorialMap";
import { InsetMap } from "@/components/InsetMap";
import { SourceNote } from "@/components/SourceNote";
import { loadMapSpec, loadSectionsGeoJSON } from "@/lib/loadMapSpec";
import { formatMetric, getBivariateClassLabel, normalizeEditorialText } from "@/lib/presentation";
import type { EditorialMapSpec, SectionFeatureProperties, SectionsGeoJSON } from "@/lib/types";

function normalizeFeatureWarnings(sections: SectionsGeoJSON, spec: EditorialMapSpec): SectionsGeoJSON {
  const classMap = spec.class_color_map;
  const neutralColor = spec.no_data_style.fill ?? classMap.no_data ?? "#CFCFCF";

  let missingColorCount = 0;
  let unknownClassCount = 0;

  const features = sections.features.map((feature) => {
    const properties = { ...(feature.properties ?? {}) } as SectionFeatureProperties;
    if (!properties.color_hex) {
      properties.color_hex = neutralColor;
      missingColorCount += 1;
    }
    if (!(properties.bivariate_class in classMap)) {
      unknownClassCount += 1;
      console.warn(
        `[MapShell] bivariate_class fuera de class_color_map: ${properties.bivariate_class} (section_id=${properties.section_id}).`
      );
    }
    return { ...feature, properties };
  });

  if (missingColorCount > 0) {
    console.warn(`[MapShell] ${missingColorCount} secciones sin color_hex; aplicado color neutral.`);
  }
  if (unknownClassCount > 0) {
    console.warn(`[MapShell] ${unknownClassCount} secciones con bivariate_class fuera de class_color_map.`);
  }

  return { ...sections, features };
}

export function MapShell() {
  const exportRootRef = useRef<HTMLElement | null>(null);
  const [spec, setSpec] = useState<EditorialMapSpec | null>(null);
  const [sections, setSections] = useState<SectionsGeoJSON | null>(null);
  const [activeSection, setActiveSection] = useState<SectionFeatureProperties | null>(null);
  const [mainMapReady, setMainMapReady] = useState(false);
  const [insetMapReady, setInsetMapReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportingPng, setExportingPng] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const mapsReady = mainMapReady && insetMapReady;

  const waitForMapCanvases = async (): Promise<void> => {
    const timeoutMs = 8000;
    const stepMs = 120;
    const startedAt = Date.now();

    while (Date.now() - startedAt < timeoutMs) {
      const root = exportRootRef.current;
      if (root) {
        const canvases = Array.from(root.querySelectorAll(".maplibregl-canvas"));
        const readyCount = canvases.filter((canvas) => canvas.clientWidth > 0 && canvas.clientHeight > 0).length;
        if (readyCount >= 2) {
          await new Promise((resolve) => window.requestAnimationFrame(() => resolve(undefined)));
          await new Promise((resolve) => window.setTimeout(resolve, 120));
          return;
        }
      }
      await new Promise((resolve) => window.setTimeout(resolve, stepMs));
    }
    throw new Error("Los mapas no terminaron de renderizar para exportaci\u00f3n.");
  };

  const handleExportPng = async () => {
    if (!exportRootRef.current || exportingPng || !mapsReady) {
      return;
    }
    setExportingPng(true);
    setExportError(null);

    try {
      await waitForMapCanvases();
      const dataUrl = await toPng(exportRootRef.current, {
        cacheBust: true,
        pixelRatio: 2,
        backgroundColor: "#efe2cb",
        filter: (node) => !(node instanceof HTMLElement && node.dataset.exportIgnore === "true")
      });
      const link = document.createElement("a");
      link.href = dataUrl;
      link.download = "leon_pan_bivariate_desktop.png";
      link.click();
    } catch (err) {
      const message =
        err instanceof Error
          ? `${err.message} Usa export CLI con Playwright para salida reproducible.`
          : "No fue posible exportar PNG. Usa export CLI con Playwright.";
      setExportError(message);
      console.error(`[MapShell] Error al exportar PNG: ${message}`);
    } finally {
      setExportingPng(false);
    }
  };

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const [loadedSpec, loadedSections] = await Promise.all([loadMapSpec(), loadSectionsGeoJSON()]);
        const normalizedSections = normalizeFeatureWarnings(loadedSections, loadedSpec);
        setSpec(loadedSpec);
        setSections(normalizedSections);
        setActiveSection(null);
        setMainMapReady(false);
        setInsetMapReady(false);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Error inesperado de carga.";
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, []);

  if (loading) {
    return (
      <main className="editorial-root">
        <section className="state-card">
          <h1>Cargando pieza editorial...</h1>
        </section>
      </main>
    );
  }

  if (error || !spec || !sections) {
    return (
      <main className="editorial-root">
        <section className="state-card error-card" role="alert">
          <h1>Error de carga de bundle</h1>
          <p>{error ?? "No se pudo inicializar el frontend editorial."}</p>
          <p>Verifica disponibilidad de /config/editorial-map-spec.json y /data/secciones.geojson.</p>
        </section>
      </main>
    );
  }

  return (
    <main className="editorial-root" ref={exportRootRef} data-export-root="true">
      <header className="editorial-header" aria-labelledby="main-title">
        <h1 id="main-title" className="editorial-title">
          {normalizeEditorialText(spec.title)}
        </h1>
        <div className="editorial-head-right">
          <p className="editorial-subtitle" id="main-subtitle">
            {normalizeEditorialText(spec.subtitle)}
          </p>
          <div className="editorial-actions" data-export-ignore="true">
            <button
              type="button"
              className="export-png-button"
              onClick={handleExportPng}
              disabled={exportingPng || !mapsReady}
              aria-label="Exportar pieza editorial como imagen PNG"
            >
              {exportingPng ? "Exportando..." : mapsReady ? "Exportar PNG" : "Preparando mapas..."}
            </button>
            {exportError ? <p className="export-error">Error de exportaci\u00f3n: {exportError}</p> : null}
            {!mapsReady && !exportError ? <p className="export-hint">Espera a que mapa e inset terminen de renderizar.</p> : null}
          </div>
        </div>
      </header>

      <p className="map-caption" id="map-description">
        {"Mapa interactivo editorial de secciones electorales de Le\u00f3n. Pasa el cursor o haz clic para consultar detalle de una secci\u00f3n; la leyenda y el inset resaltan la misma selecci\u00f3n activa."}
      </p>

      <section className="editorial-main-grid" aria-describedby="map-description">
        <section className="map-area" aria-label="Mapa principal">
          <EditorialMap
            spec={spec}
            sections={sections}
            activeSectionId={activeSection?.section_id ?? null}
            onActiveSectionChange={setActiveSection}
            onMapReadyChange={setMainMapReady}
          />
        </section>
        <section className="legend-area" aria-label={"Leyenda y ficha de secci\u00f3n"}>
          <BivariateLegend spec={spec} activeClass={activeSection?.bivariate_class ?? null} />
          <section className="active-section-panel" aria-live="polite">
            <h2 className="panel-title">{"Secci\u00f3n activa"}</h2>
            {activeSection ? (
              <div className="active-section-grid">
                <p>
                  <strong>section_id:</strong> {activeSection.section_id}
                </p>
                <p>
                  <strong>{"Secci\u00f3n:"}</strong> {activeSection.seccion}
                </p>
                <p>
                  <strong>% PAN 2018:</strong> {formatMetric(activeSection.pct_pan_2018)}
                </p>
                <p>
                  <strong>% PAN 2021:</strong> {formatMetric(activeSection.pct_pan_2021)}
                </p>
                <p>
                  <strong>Delta pp:</strong> {formatMetric(activeSection.delta_pan_pp)}
                </p>
                <p>
                  <strong>Clase:</strong> {getBivariateClassLabel(activeSection.bivariate_class)}
                </p>
                <p>
                  <strong>Datos completos:</strong> {activeSection.has_data ? "S\u00ed" : "No"}
                </p>
                {!activeSection.has_data ? <p className="active-section-warning">Sin datos suficientes</p> : null}
              </div>
            ) : (
              <p className="active-section-empty">{"Sin secci\u00f3n seleccionada. Usa hover o clic sobre el mapa."}</p>
            )}
          </section>
        </section>
        <aside className="inset-area" aria-label="Inset urbano">
          <h2 className="panel-title">Inset urbano</h2>
          <InsetMap
            spec={spec}
            sections={sections}
            activeSectionId={activeSection?.section_id ?? null}
            onActiveSectionChange={setActiveSection}
            onMapReadyChange={setInsetMapReady}
          />
        </aside>
      </section>

      <footer className="editorial-footer" aria-label={"Fuentes y cr\u00e9ditos"}>
        <SourceNote sourceLines={spec.source_lines} authorNote={spec.author_note} />
      </footer>
    </main>
  );
}
