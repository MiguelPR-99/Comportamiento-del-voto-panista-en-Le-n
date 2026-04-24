# Epica 1 - Open Issues Reales (Epica 1.2)

## Estado de aprobacion

- Estado previo: `no aprobado` para Epica 2.
- Estado esperado despues de esta pasada: `aprobable` si cada insumo bloqueante tiene ruta usable (incluyendo extraccion manual clara).

## A) Bloquean Epica 2

| ID | Pendiente bloqueante | Estado | Criterio de cierre |
|---|---|---|---|
| `E1-01` | Falta de ruta usable para marco seccional INE | Cerrado documentalmente | Portal oficial confirmado + pasos manuales claros + criterio de aceptacion del archivo |
| `E1-02` | Falta de ruta usable para resultados IEEG 2018 | Cerrado documentalmente | Ruta de extraccion oficial (directa o manual) + campos minimos de votos PAN y total |
| `E1-03` | Falta de ruta usable para resultados IEEG 2021 | Cerrado documentalmente | Ruta de extraccion oficial (directa o manual) + campos minimos de votos PAN y total |
| `E1-04` | Falta de regla operativa de normalizacion de llaves en ejecucion de datos | Cerrado en docs, pendiente de aplicacion en corrida de adquisicion | Validar en QA que `entidad=2`, `municipio=3`, `seccion` normalizada y `section_id` canonico |

## B) No bloquean Epica 2

| ID | Pendiente no bloqueante | Estado | Tratamiento |
|---|---|---|---|
| `E1-NB-01` | Capa roja/coral | Cerrado como no bloqueante | Excluir del pipeline tematico electoral v1; manejar como overlay contextual opcional |
| `E1-NB-02` | Tipografia final | Abierto | Resolver en fase editorial, no en pipeline |
| `E1-NB-03` | Comportamiento exacto de inset en mobile | Abierto | Resolver en frontend |
| `E1-NB-04` | Refinamiento visual fino | Abierto | Resolver en fase UI |
| `E1-NB-05` | Escalamiento a PMTiles | Abierto | Resolver solo si payload lo exige |
| `E1-NB-06` | Animaciones o transiciones | Abierto | Resolver en fase UI |

## Decision final v1 sobre capa roja/coral

- Se excluye del pipeline tematico electoral v1.
- Se marca como overlay contextual opcional.
- Solo se incluye si:
- se confirma fuente oficial INEGI, o
- se documenta como anotacion editorial.
- No afecta la generacion de `secciones.geojson`.

## Regla transversal de faltantes

- No imputar cero cuando falta dato clasificatorio.
- Aplicar `no_data` segun contrato y metodologia bivariante v1.

## Checklist para avanzar a Epica 2

- [x] Marco seccional INE con ruta usable documentada.
- [x] Resultados IEEG 2018 con ruta usable documentada.
- [x] Resultados IEEG 2021 con ruta usable documentada.
- [x] Regla de normalizacion de llaves documentada en `docs/11`.
- [x] Capa roja/coral movida a no bloqueante.
- [x] Plan de adquisicion con criterio de aceptacion por archivo en `docs/12`.
- [x] Regla `no_data` coherente con contrato vigente.

## Veredicto de esta pasada documental

Epica 1 queda `aprobada` para iniciar Epica 2 a nivel documental. La descarga y resguardo de archivos se ejecuta en Epica 2 siguiendo las rutas manuales ya definidas.
