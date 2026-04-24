# Epic 0 Closure

## Estado de aprobacion

- Estado antes de Epica 0.6: `no aprobado` para iniciar Epica 1.
- Estado esperado despues de Epica 0.6: `aprobable` si quedan cerrados contrato operativo, metodologia bivariante v1 y criterios verificables.

## Decisiones cerradas

- Pieza editorial interactiva de alto estandar visual.
- `Desktop-first` como prioridad.
- Replica fiel del mapa estatico + microinteracciones.
- No dashboard, no explorador cartografico libre como eje.
- Arquitectura por capas definida para `Python + GeoPandas + Next.js + MapLibre`.
- Contrato de datos operativo versionado en [07-data-contract.md](C:\Users\migue\Desktop\Salem\docs\07-data-contract.md).
- Metodologia bivariante v1 cerrada en [08-bivariate-classification.md](C:\Users\migue\Desktop\Salem\docs\08-bivariate-classification.md).
- Criterios de aceptacion convertidos a checks verificables en [04-criterios-de-aceptacion.md](C:\Users\migue\Desktop\Salem\docs\04-criterios-de-aceptacion.md).

## Decisiones abiertas que bloquean Epica 1

- Confirmar estrategia de join 2018-2021 con llave oficial y reglas para casos sin match.
- Confirmar fuentes oficiales definitivas de geometria y resultados.
- Resolver capa roja/coral con decision explicita: incluir, excluir o dejar como overlay pendiente de v1.

## Decisiones abiertas que no bloquean Epica 1

- Tipografia final exacta.
- Comportamiento fino del inset en mobile.
- Refinamiento visual fino de espaciados y detalles microeditoriales.
- Simplificacion diferencial avanzada mapa principal/inset.
- Animaciones o transiciones de entrada.

## Riesgos principales (vigentes)

- Desalineacion de identificadores entre procesos electorales.
- Diferencias entre geometria oficial y referencia editorial.
- Legibilidad insuficiente del hatch `no_data` en algunos tamanos.
- Payload geografico superior al umbral definido.

## Dependencias para Epica 1

- Geometrias oficiales de secciones electorales para Leon.
- Resultados PAN 2018 y 2021 para diputacion local.
- Confirmacion documental de llaves de join y cobertura de datos.
- Definicion final sobre capa roja/coral.

## Checklist final para avanzar a Epica 1

- [x] Product brief aprobado y direccion de producto estable.
- [x] Reverse engineering visual consolidado con referencia fuente de verdad.
- [x] Arquitectura desacoplada pipeline/frontend.
- [x] Contrato de datos operativo con tipos, reglas y validaciones.
- [x] Metodo bivariante v1 cerrado (9 clases + `no_data`, sin cuantiles).
- [x] Criterios de aceptacion redactados como checks verificables.
- [ ] Confirmar fuentes oficiales y estrategia de join 2018-2021.
- [ ] Cerrar decision de capa roja/coral (incluir/excluir/overlay pendiente).

## Veredicto de cierre de fase

Epica 0 queda en estado `aprobable` para iniciar Epica 1 tan pronto se marquen como completados los dos checks pendientes del bloque de dependencias.
