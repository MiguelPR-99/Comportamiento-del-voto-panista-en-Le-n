# Reverse Engineering Visual

## Referencia y formato

- Fuente principal: `C:\\Users\\migue\\Desktop\\Salem\\Imagen_referencia.png`
- Tamano de referencia detectado: `1024 x 724`
- Relacion aproximada: `1.414` (proporcion editorial tipo A-series)

## Composicion general

- Columna izquierda dominante para titulo editorial multilinea.
- Subtitulo metodologico alineado en el cuadrante superior derecho.
- Mapa principal como centro compositivo y narrativo.
- Leyenda y bloque `Sin Datos` en el cuadrante inferior izquierdo.
- Escala grafica en el cuadrante superior derecho.
- Inset urbano cuadrado en el cuadrante inferior derecho.
- Fuente y nota de elaboracion en el borde inferior.

## Jerarquia tipografica

- Titulo: serif editorial de alto contraste, gran tamano, color azul oscuro.
- Subtitulo: serif editorial de menor tamano, tono sobrio.
- Metadatos (fuente, nota, datum, escala): cuerpo pequeno y bajo protagonismo.
- Recomendacion inicial web: familia serif editorial (ej. `Cormorant Garamond` o equivalente con licencia valida).

## Sistema cromatico observado

### Neutros editoriales

- Fondo papel calido aproximado: `#F2F1EC`
- Gris contextual exterior aproximado: `#CCCBC7`
- Azul editorial de texto (rango aproximado): `#001A6E` a `#1F3E6C`

### Paleta bivariante dominante

- Lila claro: `#E4CDF9`
- Violeta magenta: `#791680`
- Violeta profundo: `#330A80`
- Azul-violeta intenso: `#615CFF`
- Acento coral puntual: `#DE6787`

Nota: los hex son aproximaciones por muestreo de imagen y se validaran visualmente en fase UI.

## Elementos cartograficos clave

- Coropleta bivariante `3x3` con nueve clases visuales.
- Categoria separada `Sin Datos`, con hatch/texture diagonal.
- Contexto regional silenciado fuera de Leon.
- Fronteras internas visibles y frontera municipal con mayor jerarquia.
- Etiquetas de contexto regional con bajo contraste.

## Inset urbano

- Enfoque en trama urbana con mayor densidad de secciones pequenas.
- Misma codificacion cromatica que mapa principal.
- Debe permitir lectura detallada sin perder coherencia con la vista principal.

## Leyenda bivariante

- Matriz `3x3` con ejes:
- Eje vertical: variacion respecto a 2018.
- Eje horizontal: peso/porcentaje de votos totales.
- Conteos por celda visibles dentro de cada cuadrante.
- Bloque `Sin Datos` separado de la matriz.

## Traduccion a interaccion web (v1)

- Hover/focus en seccion activa tooltip editorial con metricas base.
- Resaltado de celda correspondiente en la leyenda.
- Sincronizacion de resaltado entre mapa principal e inset cuando aplique.
- Camara inicial fija editorial; zoom/pan acotado y no dominante.
- Sin paneles de control tipo dashboard.

## Pendiente visual a confirmar

- Capa lineal roja/coral observada en zona urbana:
- Confirmar su significado (infraestructura, delimitacion o anotacion).
- Mantener como elemento contextual pendiente hasta validar fuente oficial.

