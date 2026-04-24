# Fuentes Oficiales Curadas (Epica 1.2)

## Regla de uso para pase a Epica 2

- `Endpoint directo no es obligatorio` para v1.
- Una fuente se considera `ruta usable` si tiene:
- portal oficial confirmado,
- pasos manuales claros para llegar al archivo,
- criterio de aceptacion para validar que el archivo sirve.

## Estados cerrados para descarga

- `confirmado`
- `pendiente`
- `extraccion_manual_probable`

## Fuentes primarias y ruta operativa

| Insumo requerido | Institucion oficial | Portal institucional confirmado | Archivo/endpoint de descarga confirmado | Estado de descarga | Ruta manual de adquisicion | Accion siguiente | Bloquea pipeline |
|---|---|---|---|---|---|---|---|
| Marco seccional INE para Guanajuato/Leon | INE | https://portal.ine.mx/voto-y-elecciones/especializados/ | No confirmado (el portal institucional esta confirmado, la descarga puede requerir navegacion manual o solicitud) | extraccion_manual_probable | Entrar al portal oficial -> localizar seccion de productos/cartografia electoral -> ubicar marco seccional de Guanajuato -> descargar paquete oficial | Documentar URL final usada y registrar en `data/raw/manual/fuentes-manifest.csv` | si |
| Resultados IEEG 2018 (diputacion local) | IEEG | https://sistemas.ieeg.mx/computos-finales-2018/ | No confirmado (consulta oficial validada; export puede ser manual) | extraccion_manual_probable | Abrir portal de computos 2018 -> navegar a diputaciones locales -> identificar opcion de export/descarga por seccion o casilla -> guardar archivo fuente | Confirmar granularidad util (seccion o casilla agregable a seccion) y campos de votos PAN/total | si |
| Resultados IEEG 2021 (diputacion local) | IEEG | https://ieeg.mx/proceso-electoral-2020-2021/ y https://computosgto2021.ieeg.mx/ | No confirmado (ruta institucional y portal operativo confirmados; endpoint directo pendiente) | extraccion_manual_probable | Ingresar desde pagina institucional del proceso -> abrir portal de computos 2021 -> localizar resultados de diputaciones -> exportar tabla util | Confirmar estructura de columnas y registrar URL exacta de descarga si existe | si |
| Contexto INEGI (vial/territorial) opcional | INEGI | https://www.inegi.org.mx/app/buscador/default.html?q=red+nacional+de+caminos#tabMCcollapse-Indicadores y https://www.inegi.org.mx/servicios/Ruteo/Default.html | Pendiente (depende del dataset elegido para contexto) | pendiente | Buscar dataset oficial de red vial o contexto territorial -> descargar capa para recorte Leon si se usa | Definir si se usa solo contexto vial o tambien territorial general | no |
| Capa roja/coral (overlay contextual) opcional | INEGI (si se usa fuente vial oficial) / Editorial (si se documenta anotacion) | Misma ruta INEGI de contexto | No confirmado | pendiente | Solo procesar despues de cerrar fuente: INEGI oficial o anotacion editorial documentada | Mantener fuera del pipeline tematico electoral de v1 | no |

## Fuentes secundarias y no aceptables como primaria

| Fuente | URL | Clasificacion | Uso permitido |
|---|---|---|---|
| Documento UAM citado en reporte base | https://dcsh.izt.uam.mx/licenciatura/geografiahumana/wp-content/uploads/2021/11/6_Cartel-documento-fusionado.pdf | Fuente secundaria / contextual | Contexto metodologico, no adquisicion primaria |
| Repositorio de terceros | https://github.com/emagar/mxDistritos | No aceptable como fuente primaria | Excluido de adquisicion de datos oficiales |
