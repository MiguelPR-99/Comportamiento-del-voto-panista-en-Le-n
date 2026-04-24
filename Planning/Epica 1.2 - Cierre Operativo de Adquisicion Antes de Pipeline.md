# Epica 1.2 - Cierre Operativo de Adquisicion Antes de Pipeline

## Resumen
- Corregir [10-fuentes-oficiales.md](C:\Users\migue\Desktop\Salem\docs\10-fuentes-oficiales.md), [11-estrategia-join-2018-2021.md](C:\Users\migue\Desktop\Salem\docs\11-estrategia-join-2018-2021.md), [12-data-acquisition-plan.md](C:\Users\migue\Desktop\Salem\docs\12-data-acquisition-plan.md) y [14-epic-1-open-issues.md](C:\Users\migue\Desktop\Salem\docs\14-epic-1-open-issues.md) para que Epica 2 pueda iniciar con adquisicion manual aceptable, sin exigir endpoint directo.
- Criterio de pase confirmado: una ruta es usable si existe portal oficial confirmado, pasos manuales claros, carpeta destino, nombre sugerido, formato esperado, columnas minimas y criterio de aceptacion del archivo.
- No se modifican producto, frontend, pipeline ni contrato de `no_data`; solo se cierra adquisicion operativa y normalizacion de llaves.

## Cambios clave

### 1. Fuentes oficiales con doble nivel: institucion vs descarga operativa
Actualizar `docs/10` para que cada insumo minimo tenga una tabla con estas columnas:
- `insumo requerido`
- `institucion oficial`
- `portal institucional confirmado`
- `archivo/endpoint de descarga confirmado`
- `estado de descarga`
- `ruta manual de adquisicion`
- `accion siguiente`
- `bloquea pipeline`

Aplicar esta matriz a:
- marco seccional INE para Guanajuato/Leon
- resultados IEEG 2018 para diputacion local
- resultados IEEG 2021 para diputacion local
- contexto INEGI opcional
- capa roja/coral opcional

Decisiones de contenido:
- `portal institucional confirmado` debe documentar la pagina oficial ya verificada, aunque el archivo final no este expuesto en enlace directo.
- `archivo/endpoint de descarga confirmado` puede quedar `no confirmado` si solo hay navegacion manual.
- `estado de descarga` debe usar un conjunto cerrado: `confirmado`, `pendiente`, `extraccion_manual_probable`.
- `bloquea pipeline` debe ser `si` solo para los tres insumos minimos obligatorios de Epica 2: marco seccional INE, resultados IEEG 2018, resultados IEEG 2021.
- `INEGI contexto` y `capa roja/coral` deben quedar como `no` bloqueantes.

Fuentes y evidencias a reflejar:
- INE: usar el hallazgo de productos cartograficos especializados/descargables y documentar que el Marco Geografico Seccional y catalogos existen institucionalmente, pero que la obtencion puede requerir solicitud o navegacion manual.
- IEEG 2018: documentar que el portal de computos esta confirmado y que existe al menos consulta oficial; la descarga puede quedar como `extraccion_manual_probable` si no hay endpoint directo validado.
- IEEG 2021: documentar pagina institucional del proceso + portal de computos 2021 como ruta oficial combinada; si no hay archivo directo, dejar pasos manuales claros.
- INEGI: mantener oficialidad confirmada y dejarla como fuente contextual opcional.

### 2. Ruta operativa de adquisicion por archivo
Actualizar `docs/12` para que la tabla por carpeta quede con estas columnas:
- `carpeta destino`
- `nombre sugerido`
- `formato esperado`
- `columnas minimas esperadas`
- `fuente`
- `estado actual`
- `accion manual pendiente`
- `criterio de aceptacion del archivo`
- `obligatorio para Epica 2`

Completar filas para:
- `data/raw/ine/`
- `data/raw/ieeg/2018/`
- `data/raw/ieeg/2021/`
- `data/raw/inegi/`
- `data/raw/manual/`

Definir criterios de aceptacion concretos por archivo:
- Marco seccional INE:
  `sirve` si incluye Guanajuato, geometria valida y columnas equivalentes a entidad/municipio/seccion.
- Catalogo geoelectoral:
  `sirve` si expone claves oficiales que permitan validar `cve_ent`, `cve_mun`, `cve_secc`.
- Resultados IEEG 2018 y 2021:
  `sirve` si permite reconstruir a nivel seccion, ya sea por columna `seccion` directa o por agregacion desde casilla, y contiene votos PAN y total de votos.
- INEGI vial/contexto:
  `sirve` solo para overlay opcional o contexto; no bloquea Epica 2.
- `fuentes-manifest.csv`:
  `sirve` si registra insumo, URL, fecha, estado y responsable.
- `equivalencias_seccionales_2018_2021.*`:
  `sirve` si es oficial y describe correspondencias origen-destino; si no existe, debe quedar registrado como ausencia confirmada.

Regla de aprobacion para Epica 2:
- El plan debe declarar que `endpoint directo no es obligatorio`.
- La documentacion pasa si cada insumo bloqueante tiene `ruta manual usable` y `criterio de aceptacion` suficiente para ejecutar la descarga despues.

### 3. Normalizacion exacta de llaves
Actualizar `docs/11` para fijar formato canonico y dejarlo implementable sin decisiones abiertas.

Definir:
- `entidad`: `string` de 2 digitos; Guanajuato = `"11"`.
- `municipio`: `string` de 3 digitos con left padding; asumir estandar oficial `cve_mun` de 3 digitos.
- `seccion`: `string` sin espacios, sin decimales; mantener padding solo si el insumo oficial ya lo usa. Como default documental para pipeline, normalizar a string numerico sin separadores y conservar ceros a la izquierda solo si vienen del origen oficial.
- `section_id`: concatenacion canonica `entidad + municipio + seccion_normalizada`.

Reglas operativas obligatorias:
- trim de espacios en todas las claves.
- eliminar sufijos de casilla si el registro viene a nivel casilla y separar `seccion` del identificador de casilla.
- derivar `seccion` desde casilla cuando el origen venga como seccion + tipo de casilla en un mismo campo.
- agregar casillas por seccion antes del join.
- validar unicidad por `entidad + municipio + seccion`.
- no asignar cero cuando falte 2018 o 2021; usar `no_data`.

Importante:
- si el insumo oficial revela una convención distinta para `seccion` (por ejemplo, padding fijo), el documento debe dejar esa regla subordinada al origen oficial, pero con default claro para arrancar.
- la tabla de equivalencias seccionales debe pasar de “pendiente difuso” a “uso condicional”: ayuda si existe, pero no bloquea el join inicial mientras se etiqueten no-match y `no_data`.

### 4. Reorganizacion de open issues y capa roja/coral
Actualizar `docs/14` para separar explicitamente:

`Bloquean Epica 2`
- falta de ruta usable para marco seccional INE
- falta de ruta usable para resultados 2018
- falta de ruta usable para resultados 2021
- falta de regla de normalizacion de llaves

`No bloquean Epica 2`
- capa roja/coral
- tipografia
- mobile inset
- refinamiento visual
- PMTiles
- animaciones

Cerrar la decision de la capa roja/coral asi:
- excluirla del pipeline tematico electoral v1
- tratarla como overlay contextual opcional
- incluirla solo si se confirma fuente oficial INEGI o si se documenta como anotacion editorial
- declarar expresamente que no afecta la generacion de `secciones.geojson`

Actualizar el cierre del documento con:
- `Estado previo: no aprobado para Epica 2`
- `Estado esperado despues de esta pasada: aprobable si cada fuente bloqueante tiene ruta usable o extraccion manual clara`
- checklist final de pase a Epica 2

## Pruebas y escenarios de validacion
- Verificar que `docs/10` ya no mezcle “portal institucional confirmado” con “archivo descargable confirmado”.
- Verificar que en `docs/12` cada archivo esperado tenga criterio de aceptacion y bandera de obligatoriedad.
- Verificar que `docs/11` deje cerradas las longitudes canónicas: `entidad=2`, `municipio=3`, `section_id` concatenado y reglas de derivacion desde casilla.
- Verificar que `docs/14` mueva la capa roja/coral a no bloqueante y que el checklist final solo dependa de rutas usables y llaves normalizadas.
- Verificar coherencia con [07-data-contract.md](C:\Users\migue\Desktop\Salem\docs\07-data-contract.md) para que `no_data` siga siendo la unica salida valida cuando falte dato clasificatorio.

## Supuestos y defaults
- Se acepta `extraccion_manual_probable` como ruta usable para Epica 2, siempre que el portal sea oficial y el documento deje pasos manuales y criterio de aceptacion claros.
- `cve_mun` se documenta como string de 3 digitos con padding, alineado con el estandar oficial de claves municipales.
- La inexistencia de una tabla oficial de equivalencias no bloquea el arranque del pipeline inicial si la estrategia de no-match y `no_data` ya esta cerrada.
- No se intentara “resolver” endpoints no confirmados inventando URLs; si no hay enlace directo, se documentara la navegacion manual.
