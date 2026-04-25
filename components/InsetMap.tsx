"use client";

import { useEffect, useMemo, useRef } from "react";
import maplibregl, { type Map } from "maplibre-gl";
import type { EditorialMapSpec, SectionFeatureProperties, SectionsGeoJSON } from "@/lib/types";
import { deriveInsetView, toSectionProps } from "@/lib/sectionFeature";

type InsetMapProps = {
  spec: EditorialMapSpec;
  sections: SectionsGeoJSON;
  activeSectionId: string | null;
  onActiveSectionChange: (section: SectionFeatureProperties | null) => void;
  onMapReadyChange: (ready: boolean) => void;
};

export function InsetMap({ spec, sections, activeSectionId, onActiveSectionChange, onMapReadyChange }: InsetMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);

  const neutralColor = useMemo(
    () => spec.no_data_style.fill ?? spec.class_color_map.no_data ?? "#CFCFCF",
    [spec.class_color_map.no_data, spec.no_data_style.fill]
  );
  const insetView = useMemo(() => deriveInsetView(sections, spec), [sections, spec]);

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
            id: "inset-background",
            type: "background",
            paint: { "background-color": "#efe4d2" }
          }
        ]
      },
      center: insetView.center,
      zoom: insetView.zoom,
      attributionControl: false,
      preserveDrawingBuffer: true
    });

    mapRef.current = map;
    map.scrollZoom.disable();
    map.dragRotate.disable();
    map.touchZoomRotate.disableRotation();
    map.boxZoom.disable();
    map.doubleClickZoom.disable();
    map.keyboard.disable();

    map.on("load", () => {
      let readySent = false;
      const markReady = () => {
        if (readySent) {
          return;
        }
        readySent = true;
        onMapReadyChange(true);
      };

      map.addSource("inset-sections", { type: "geojson", data: sections });
      map.addLayer({
        id: "inset-sections-fill",
        type: "fill",
        source: "inset-sections",
        paint: {
          "fill-color": ["coalesce", ["get", "color_hex"], neutralColor],
          "fill-opacity": 0.92
        }
      });
      map.addLayer({
        id: "inset-sections-line",
        type: "line",
        source: "inset-sections",
        paint: {
          "line-color": "#f5eee3",
          "line-width": 0.5
        }
      });
      map.addLayer({
        id: "inset-sections-active-outline",
        type: "line",
        source: "inset-sections",
        filter: ["==", ["get", "section_id"], ""],
        paint: {
          "line-color": "#2f2235",
          "line-width": 1.5,
          "line-opacity": 0.9
        }
      });

      map.fitBounds(
        [
          [insetView.bounds[0], insetView.bounds[1]],
          [insetView.bounds[2], insetView.bounds[3]]
        ],
        { padding: 20, duration: 0 }
      );

      map.on("mousemove", "inset-sections-fill", (event) => {
        map.getCanvas().style.cursor = "pointer";
        const section = toSectionProps(event.features?.[0]?.properties as Record<string, unknown> | undefined);
        onActiveSectionChange(section);
      });

      map.on("click", "inset-sections-fill", (event) => {
        const section = toSectionProps(event.features?.[0]?.properties as Record<string, unknown> | undefined);
        onActiveSectionChange(section);
      });

      map.on("mouseleave", "inset-sections-fill", () => {
        map.getCanvas().style.cursor = "";
        onActiveSectionChange(null);
      });

      map.on("sourcedata", (event) => {
        if (event.sourceId === "inset-sections" && event.isSourceLoaded) {
          markReady();
        }
      });
      map.once("idle", markReady);
      window.setTimeout(() => {
        if (map.isSourceLoaded("inset-sections")) {
          markReady();
        }
      }, 1200);
    });

    return () => {
      onMapReadyChange(false);
      map.remove();
      mapRef.current = null;
    };
  }, [insetView.bounds, insetView.center, insetView.zoom, neutralColor, onActiveSectionChange, onMapReadyChange, sections]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }
    const source = map.getSource("inset-sections") as maplibregl.GeoJSONSource | undefined;
    if (source) {
      source.setData(sections);
    }
  }, [sections]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.getLayer("inset-sections-active-outline")) {
      return;
    }
    map.setFilter("inset-sections-active-outline", ["==", ["get", "section_id"], activeSectionId ?? ""]);
  }, [activeSectionId]);

  return (
    <div className="inset-map-wrap" role="region" aria-label="Inset urbano de contexto">
      <div className="inset-map-canvas" ref={containerRef} />
      {insetView.isDerivedFromData ? (
        <p className="inset-note">{"Inset urbano: acercamiento al \u00e1rea central de Le\u00f3n."}</p>
      ) : null}
    </div>
  );
}
