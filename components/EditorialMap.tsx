"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import maplibregl, { type Map } from "maplibre-gl";
import { SectionTooltip } from "@/components/SectionTooltip";
import type { EditorialMapSpec, SectionFeatureProperties, SectionsGeoJSON } from "@/lib/types";
import { toSectionProps } from "@/lib/sectionFeature";

type EditorialMapProps = {
  spec: EditorialMapSpec;
  sections: SectionsGeoJSON;
  activeSectionId: string | null;
  onActiveSectionChange: (section: SectionFeatureProperties | null) => void;
  onMapReadyChange: (ready: boolean) => void;
};

type TooltipState = {
  x: number;
  y: number;
  section: SectionFeatureProperties;
} | null;

type ScaleState = {
  label: string;
  widthPx: number;
};

function niceScaleKilometers(rawKm: number): number {
  const candidates = [0.2, 0.5, 1, 2, 3, 5, 10, 15, 20, 30];
  for (const candidate of candidates) {
    if (rawKm <= candidate) {
      return candidate;
    }
  }
  return 50;
}

function getScaleState(map: Map): ScaleState {
  const targetWidthPx = 120;
  const center = map.getCenter();
  const zoom = map.getZoom();
  const metersPerPixel = (156543.03392 * Math.cos((center.lat * Math.PI) / 180)) / 2 ** zoom;
  const rawKm = (metersPerPixel * targetWidthPx) / 1000;
  const km = niceScaleKilometers(rawKm);
  const widthPx = Math.max(48, Math.min((km * 1000) / metersPerPixel, 150));
  const label = Number.isInteger(km) ? `${km} km` : `${km.toFixed(1)} km`;
  return { label, widthPx };
}

export function EditorialMap({ spec, sections, activeSectionId, onActiveSectionChange, onMapReadyChange }: EditorialMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState>(null);
  const [scaleState, setScaleState] = useState<ScaleState>({ label: `${spec.scale_bar_km} km`, widthPx: 96 });

  const neutralColor = useMemo(
    () => spec.no_data_style.fill ?? spec.class_color_map.no_data ?? "#CFCFCF",
    [spec.class_color_map.no_data, spec.no_data_style.fill]
  );

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return;
    }

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {},
        layers: [
          {
            id: "background",
            type: "background",
            paint: {
              "background-color": "#efe4d2"
            }
          }
        ]
      },
      center: spec.main_view.center,
      zoom: spec.main_view.zoom,
      attributionControl: false,
      preserveDrawingBuffer: true
    });

    mapRef.current = map;
    map.scrollZoom.disable();
    map.dragRotate.disable();
    map.touchZoomRotate.disableRotation();
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");

    map.on("load", () => {
      let readySent = false;
      const markReady = () => {
        if (readySent) {
          return;
        }
        readySent = true;
        onMapReadyChange(true);
      };

      map.addSource("sections", { type: "geojson", data: sections });
      map.addLayer({
        id: "sections-fill",
        type: "fill",
        source: "sections",
        paint: {
          "fill-color": ["coalesce", ["get", "color_hex"], neutralColor],
          "fill-opacity": 0.92
        }
      });
      map.addLayer({
        id: "sections-line",
        type: "line",
        source: "sections",
        paint: {
          "line-color": "#f6efe2",
          "line-width": 0.6
        }
      });
      map.addLayer({
        id: "sections-active-outline",
        type: "line",
        source: "sections",
        filter: ["==", ["get", "section_id"], ""],
        paint: {
          "line-color": "#2f2235",
          "line-width": 1.9,
          "line-opacity": 0.92
        }
      });

      const bounds = spec.main_view.bounds;
      if (bounds && bounds.length === 4) {
        map.fitBounds(
          [
            [bounds[0], bounds[1]],
            [bounds[2], bounds[3]]
          ],
          { padding: 10, duration: 0 }
        );
      }

      map.on("mousemove", "sections-fill", (event) => {
        map.getCanvas().style.cursor = "pointer";
        const section = toSectionProps(event.features?.[0]?.properties as Record<string, unknown> | undefined);
        if (!section) {
          setTooltip(null);
          onActiveSectionChange(null);
          return;
        }
        setTooltip({ x: event.point.x, y: event.point.y, section });
        onActiveSectionChange(section);
      });

      map.on("click", "sections-fill", (event) => {
        const section = toSectionProps(event.features?.[0]?.properties as Record<string, unknown> | undefined);
        if (!section) {
          setTooltip(null);
          onActiveSectionChange(null);
          return;
        }
        setTooltip({ x: event.point.x, y: event.point.y, section });
        onActiveSectionChange(section);
      });

      map.on("mouseleave", "sections-fill", () => {
        map.getCanvas().style.cursor = "";
        setTooltip(null);
        onActiveSectionChange(null);
      });

      const refreshScale = () => {
        setScaleState(getScaleState(map));
      };
      refreshScale();
      map.on("move", refreshScale);

      map.on("sourcedata", (event) => {
        if (event.sourceId === "sections" && event.isSourceLoaded) {
          markReady();
        }
      });
      map.once("idle", markReady);
      window.setTimeout(() => {
        if (map.isSourceLoaded("sections")) {
          markReady();
        }
      }, 1200);
    });

    return () => {
      onMapReadyChange(false);
      onActiveSectionChange(null);
      map.remove();
      mapRef.current = null;
    };
  }, [sections, spec.main_view.bounds, spec.main_view.center, spec.main_view.zoom, neutralColor, onActiveSectionChange, onMapReadyChange]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }
    const source = map.getSource("sections") as maplibregl.GeoJSONSource | undefined;
    if (source) {
      source.setData(sections);
    }
  }, [sections]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.getLayer("sections-active-outline")) {
      return;
    }
    map.setFilter("sections-active-outline", ["==", ["get", "section_id"], activeSectionId ?? ""]);
  }, [activeSectionId]);

  return (
    <div
      className="editorial-map-card"
      role="region"
      aria-label="Mapa principal de secciones electorales"
      aria-describedby="map-description"
    >
      <div className="editorial-map-canvas" ref={containerRef} />
      <div className="map-scale-overlay" aria-label={"Escala gr\u00e1fica en kil\u00f3metros"}>
        <span className="map-scale-label">{scaleState.label}</span>
        <span className="map-scale-bar" style={{ width: `${scaleState.widthPx}px` }} />
      </div>
      {tooltip ? <SectionTooltip x={tooltip.x} y={tooltip.y} section={tooltip.section} /> : null}
    </div>
  );
}
