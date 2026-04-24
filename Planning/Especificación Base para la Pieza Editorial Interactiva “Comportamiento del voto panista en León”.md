# Especificación Base para la Pieza Editorial Interactiva “Comportamiento del voto panista en León”

## Resumen
- Partimos de un workspace greenfield y la referencia visual autorizada es [Imagen_referencia.png](C:\Users\migue\Desktop\Salem\Imagen_referencia.png).
- La pieza se define como una réplica editorial interactiva `desktop-first`, no como dashboard, con microinteracciones discretas y sin exploración cartográfica libre como comportamiento principal.
- La fase actual no escribe código ni descarga datos; deja cerrada la estructura documental, la lectura visual del mapa, la arquitectura preliminar y los criterios de aceptación para arrancar después el pipeline geográfico.

## Estructura inicial de `/docs`
- `docs/README.md`
  - Propósito del dossier.
  - Orden de lectura recomendado.
  - Qué queda resuelto en esta fase y qué se difiere al pipeline geográfico.
- `docs/01-product-brief.md`
  - `Resumen ejecutivo`
  - `Objetivo editorial`
  - `Audiencia principal`
  - `Promesa de producto`
  - `No objetivos`
  - `Alcance v1`
  - `Interacciones permitidas`
  - `Métricas de calidad`
- `docs/02-reverse-engineering-visual.md`
  - `Lectura general de la composición`
  - `Formato y proporciones`
  - `Jerarquía tipográfica`
  - `Sistema cromático`
  - `Mapa principal`
  - `Inset urbano`
  - `Leyenda bivariante 3x3`
  - `Sin Datos`
  - `Escala, fuentes y créditos`
  - `Traducción a comportamiento interactivo`
- `docs/03-arquitectura-preliminar.md`
  - `Principios de arquitectura`
  - `Separación pipeline / frontend`
  - `Contratos de datos`
  - `Responsabilidades de Python + GeoPandas`
  - `Responsabilidades de Next.js`
  - `Responsabilidades de MapLibre`
  - `Estrategia de render editorial`
  - `Preparación para fase geográfica`
- `docs/04-criterios-de-aceptacion.md`
  - `Aceptación visual`
  - `Aceptación cartográfica`
  - `Aceptación funcional`
  - `Aceptación responsive`
  - `Aceptación técnica`
  - `QA manual y regresión visual`
- `docs/05-decisiones-y-riesgos.md`
  - `Decisiones cerradas`
  - `Decisiones abiertas`
  - `Riesgos`
  - `Mitigaciones`
  - `Dependencias para la siguiente fase`

## Contenido que debe quedar documentado

### 1. Product brief
- Definir el producto como una pieza editorial interactiva de lectura guiada, centrada en explicar la variación del voto panista por sección electoral entre 2018 y 2021 para diputación local en León.
- Fijar como objetivo principal: conservar la autoridad visual del mapa impreso y traducirla a web sin perder densidad cartográfica ni sobriedad editorial.
- Definir audiencia principal: lectores con interés cívico, periodístico, académico o territorial; audiencia secundaria: equipo de diseño, desarrollo y análisis electoral.
- Establecer no objetivos:
  - no convertir la pieza en dashboard multi-filtro;
  - no abrir navegación geográfica libre como experiencia dominante;
  - no introducir series o métricas que no estén en el original durante v1.
- Cerrar alcance v1:
  - mapa principal;
  - inset urbano;
  - leyenda bivariante 3x3;
  - categoría `Sin Datos`;
  - tooltip editorial;
  - resaltado sincronizado entre mapa e inset;
  - créditos, fuente y nota metodológica.
- Dejar métricas de calidad enfocadas en fidelidad visual, claridad interpretativa, rendimiento percibido y estabilidad del layout.

### 2. Reverse engineering visual
- Documentar que la imagen base tiene proporción aproximada `1.414` (`1024x724`), cercana a formato editorial tipo A-series, y que esa proporción debe orientar el layout hero en desktop.
- Fijar la lectura compositiva:
  - columna editorial izquierda con título en cuatro líneas;
  - subtítulo metodológico alineado arriba a la derecha;
  - mapa principal ocupando el centro de la pieza;
  - leyenda y `Sin Datos` anclados abajo a la izquierda fuera del cuerpo del mapa;
  - escala gráfica en el cuadrante superior derecho;
  - inset urbano cuadrado en la esquina inferior derecha;
  - créditos y fuentes como cierre tipográfico pequeño en la base.
- Registrar el tono visual:
  - fondo papel cálido aproximado `#F2F1EC`;
  - gris contextual para territorio externo y elementos mudos aproximado `#CCCBC7`;
  - azul editorial oscuro para títulos/subtítulos aproximado `#001A6E` a `#1F3E6C`;
  - paleta bivariante basada en lila pálido `#E4CDF9`, violeta magenta `#791680`, violeta profundo `#330A80`, azul-violeta eléctrico `#615CFF`;
  - acento coral para pequeños polígonos o capas lineales secundarias aproximado `#DE6787`.
- Definir la jerarquía tipográfica:
  - título con serif editorial de alto contraste;
  - subtítulo con serif de menor tamaño y ancho más contenido;
  - metadatos, escala y fuentes en cuerpo pequeño sobrio;
  - default web recomendado: `Cormorant Garamond` o familia equivalente, salvo que la fase visual posterior permita una coincidencia más cercana.
- Describir el mapa principal:
  - León aparece como única unidad protagonista;
  - el entorno regional se dibuja como contexto estático y silenciado, sin basemap web genérico;
  - la frontera municipal debe leerse con más peso que la subdivisión interna;
  - etiquetas regionales visibles y discretas se tratan como anotación editorial, no como labels automáticas de proveedor.
- Describir la leyenda:
  - matriz bivariante `3x3`;
  - etiquetas de eje con una variable vertical de variación respecto a 2018 y una horizontal de peso o porcentaje del voto;
  - conteos o frecuencias mostrados dentro de las celdas;
  - bloque `Sin Datos` separado y superior a la matriz, con textura de rayado diagonal.
- Definir traducción interactiva:
  - hover y focus muestran tooltip con identificador de sección y métricas base;
  - resaltar la celda de leyenda correspondiente;
  - resaltar simultáneamente la misma sección en el inset si entra en su ventana;
  - mantener la cámara editorial como vista por defecto;
  - desactivar scroll-zoom por defecto y permitir, si se implementa, sólo zoom acotado mediante controles explícitos.
- Documentar una observación clave:
  - existe una capa lineal roja/coral en el área urbana visible en mapa principal e inset;
  - hasta identificar su fuente, debe tratarse como overlay contextual pendiente y no como capa temática cerrada.

### 3. Arquitectura preliminar
- Cerrar separación de responsabilidades:
  - `Python + GeoPandas` prepara geometrías, joins electorales, métricas y clasificación bivariante.
  - `Next.js` compone la pieza editorial, resuelve layout, textos, accesibilidad y carga de artefactos.
  - `MapLibre` renderiza sólo los mapas y sus capas temáticas/contextuales.
- Definir principio rector:
  - el frontend no clasifica ni recalcula la estadística electoral;
  - el frontend sólo consume artefactos ya preparados por el pipeline.
- Fijar contrato de datos mínimo para la futura fase:
  - `editorial-map-spec.json`
    - `title`
    - `subtitle`
    - `source_lines[]`
    - `author_note`
    - `palette`
    - `legend`
    - `main_view`
    - `inset_view`
    - `scale_bar_km`
    - `no_data_style`
  - `secciones.geojson`
    - `section_id`
    - `pct_pan_2018`
    - `pct_pan_2021`
    - `delta_pan_pp`
    - `vote_share_bin`
    - `delta_bin`
    - `bivariate_class`
    - `has_data`
    - `is_in_inset`
  - `contexto.geojson`
    - límites municipales/regionales mudos;
    - etiquetas curatoriales, si no se hornean en HTML/SVG.
- Fijar estrategia de formatos:
  - artefacto canónico del pipeline: `GeoParquet` para QA interna;
  - artefacto web v1: `GeoJSON` optimizado y simplificado por tratarse de una sola pieza municipal;
  - dejar `PMTiles` como ruta de escalamiento, no como obligación de v1.
- Definir sistema cartográfico:
  - cálculo y métricas en CRS métrico local, default `EPSG:32614`;
  - entrega web en `WGS84 / EPSG:4326` por coherencia con la referencia y MapLibre.
- Definir sistema de render:
  - dos instancias coordinadas de MapLibre, una principal y una para inset;
  - la leyenda, créditos, título, subtítulo y escala se renderizan en HTML/CSS/SVG, no como parte del lienzo del mapa;
  - `Sin Datos` se resuelve con patrón de hatch explícito, no con simple gris plano.
- Dejar lista la fase geográfica posterior:
  - adquisición de secciones electorales oficiales;
  - unión con resultados 2018 y 2021;
  - documentación de umbrales del bivariado;
  - simplificación geométrica diferenciada para mapa principal e inset;
  - exportación de bundle estático consumible por Next.js.

## Criterios de aceptación y escenarios de prueba
- Visual:
  - la composición desktop reproduce la lógica del original con título a la izquierda, subtítulo arriba a la derecha, leyenda abajo a la izquierda e inset abajo a la derecha;
  - no hay apariencia de dashboard ni de mapa base genérico;
  - la paleta conserva la familia violeta/azul/rosa y el fondo mantiene apariencia de papel editorial.
- Cartográfico:
  - la clasificación bivariante muestra 9 combinaciones más `Sin Datos`;
  - la misma clase cromática se mantiene entre mapa principal, inset y leyenda;
  - `Sin Datos` siempre usa textura distinta y legible en ambos mapas.
- Funcional:
  - hover o focus sobre una sección muestra métricas mínimas y clase;
  - la leyenda responde al estado activo;
  - el inset refleja la misma codificación y resalta la misma selección cuando aplica;
  - no existen filtros, tabs ni paneles analíticos propios de dashboard.
- Responsive:
  - desktop es la referencia principal;
  - en tablet la composición puede reordenar, pero sin perder simultaneidad entre mapa, leyenda y créditos;
  - en mobile se permite apilar título, subtítulo, mapa, leyenda e inset, manteniendo intacta la semántica editorial.
- Técnica:
  - el mapa carga desde artefactos locales estáticos;
  - no depende de tiles externos para el contexto visual principal;
  - la clasificación se valida contra metadatos del pipeline;
  - el bundle inicial debe seguir siendo razonable para una pieza municipal.
- QA sugerido:
  - comparación visual manual y por screenshot contra la imagen de referencia;
  - validación de esquema de `editorial-map-spec.json` y `secciones.geojson`;
  - prueba específica para un caso `Sin Datos`;
  - revisión de contraste y foco de teclado en leyenda y tooltip;
  - revisión de coherencia del inset respecto al bounding box definido.

## Decisiones cerradas, decisiones abiertas y riesgos

### Decisiones cerradas
- La pieza será editorial interactiva, no dashboard.
- La referencia visual autorizada es la imagen original del mapa.
- La experiencia es `desktop-first`.
- La interactividad será conservadora: microinteracciones, no exploración libre como comportamiento principal.
- No se usará un basemap web estándar como fondo visible.
- El pipeline clasifica y el frontend sólo representa.
- La salida web v1 será estática y versionable.
- La documentación se redactará en español.

### Decisiones abiertas
- Confirmar qué representa exactamente la capa lineal roja/coral del centro urbano y si entra a v1.
- Definir el método de corte de la matriz bivariante `3x3`: umbral fijo, cuantiles, terciles dirigidos o criterio editorial.
- Confirmar si el inset reutiliza idéntica geometría o una simplificación específica.
- Elegir la fuente final según licencia y cercanía formal con el original.
- Decidir si mobile conserva un inset activo o lo convierte en bloque secundario no interactivo.

### Riesgos
- Desalineación entre claves geográficas de 2018 y 2021.
- Diferencias entre geometría oficial y geometría usada en el mapa original.
- Pérdida de legibilidad del hatch `Sin Datos` en escalas pequeñas.
- Sobrecarga visual si el contexto regional se resuelve con demasiada información.
- Deriva hacia UI de dashboard si se agregan controles no previstos.
- Problemas de contraste en algunas combinaciones de la paleta bivariante.

### Mitigaciones
- Congelar un contrato de datos antes de programar frontend.
- Hacer QA de topología y correspondencia de ids en la fase de pipeline.
- Probar la textura de `Sin Datos` desde prototipo temprano.
- Mantener labels y contexto como capas curatoriales mínimas.
- Validar la composición con regresión visual antes de sumar interacciones extra.

## Supuestos y defaults
- La imagen de referencia es la fuente de verdad para composición y tono visual.
- Esta fase no crea archivos ni código, pero deja definido qué documentos deben materializarse y qué contenido debe llevar cada uno.
- Si no aparece un requerimiento nuevo, v1 no incluirá búsqueda, filtros por partido, selector temporal ni comparador multi-mapa.
- Si el peso del `GeoJSON` no compromete rendimiento, no se introduce `PMTiles` en la primera implementación.
- El datum final mostrado al usuario será `WGS84`, aunque el análisis interno se haga en CRS métrico local.
