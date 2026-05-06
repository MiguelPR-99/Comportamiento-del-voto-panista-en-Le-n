# Visualización geoespacial electoral - León, Guanajuato
Mapa editorial interactivo para analizar la variación del voto PAN entre 2018 y 2021 por sección electoral.

[English](README.md) | Español

## Resumen
Este proyecto transforma datos electorales y geográficos oficiales en un mapa editorial interactivo enfocado en la interpretación territorial.  
Visualiza cómo cambió la proporción de voto PAN entre 2018 y 2021 en las secciones electorales de León mediante una coropleta bivariante.  
El resultado integra análisis de datos, visualización geoespacial y comunicación con enfoque ejecutivo en un producto de datos público.  
Está diseñado como una pieza narrativa, no como dashboard, con salida exportable para reportes y presentaciones.

## Demo pública
Demo pública: [https://voto-panista-leon.vercel.app/](https://voto-panista-leon.vercel.app/)

Screenshot validado / export PNG:

![Mapa bivariante PAN León v1.1.0](public/images/leon_pan_bivariate_v1.1.0.png)

## Por qué importa este proyecto
Este proyecto demuestra cómo los datos electorales y territoriales oficiales pueden convertirse en un producto visual claro que apoya la interpretación territorial, la exploración geográfica y la comunicación de hallazgos en contextos de toma de decisiones.

## Qué demuestra este proyecto
- Limpieza y preparación de datos espaciales.
- Visualización geoespacial con MapLibre.
- Clasificación bivariante y codificación visual.
- Storytelling de datos con enfoque ejecutivo.
- Flujo reproducible de frontend y exportación.
- Validaciones de calidad y supuestos documentados.
- Capacidad para traducir datos complejos en un entregable visual claro.

## Stack técnico
- Next.js + React + TypeScript
- MapLibre GL JS
- html-to-image
- Playwright
- CSS editorial personalizado

## Fuentes de datos
- INE: cartografía seccional.
- IEEG: resultados de diputaciones locales 2018 y 2021.
- INEGI: referencia territorial contextual.

Solo se incluyen artefactos procesados/públicos para la app web; la ingesta de datos crudos está documentada por separado.

Artefactos consumidos por frontend:
- `public/data/secciones.geojson`
- `public/config/editorial-map-spec.json`

## Metodología
- Universo espacial final: `846` secciones electorales en León.
- Clasificación bivariante 3x3 más `no_data`.
- Eje horizontal: `% PAN 2021` (`low <40`, `mid 40-<60`, `high >=60`).
- Eje vertical: cambio respecto a 2018 (`decline <-10`, `stable -10 to 10`, `growth >10`).
- Manejo de faltantes: sin imputar ceros.
- Secciones sin datos clasificatorios suficientes se etiquetan como `no_data`.

## Estructura del repositorio
- `app/`
- `components/`
- `lib/`
- `styles/`
- `public/data/`
- `public/config/`
- `public/images/`
- `scripts/`
- `data/processed/`
- `data/raw/README.md`
- `docs/`
- `reports/`

## Correr localmente
```bash
npm install
npm run dev
npm run lint
npm run build
```

## Exportar PNG
Vía UI:
- Usar el botón `Exportar PNG` dentro de la app.

Vía CLI (recomendada para una salida estable de portafolio):
```bash
npm run export:png
```

Notas:
- URL por defecto para export CLI: `http://127.0.0.1:4173`.
- Si no hay servidor en esa URL, el script inicia uno temporal.
- Para usar otra URL, definir `EXPORT_URL`.
- Si falta Chromium de Playwright, ejecutar:
```bash
npx playwright install chromium
```

Ruta de salida:
- `exports/leon_pan_bivariate_desktop.png`

## Estado del proyecto
- Listo para portafolio `v1.1.0`
- Demo pública disponible
- Mejoras futuras documentadas

## Limitaciones conocidas
- El inset urbano mantiene una definición editorial y puede formalizarse con geometría explícita.
- La escala gráfica es aproximada y depende del zoom/latitud.
- La exportación por UI puede variar según navegador/GPU; la vía más estable es Playwright por CLI.
- Aún no hay una suite completa de regresión visual cross-browser.

## Mejoras futuras
- Formalizar la geometría del inset urbano.
- Mejorar cobertura de accesibilidad.
- Agregar pruebas visuales automatizadas.
- Ampliar documentación de despliegue.
- Adaptar el framework a otros casos territoriales y operativos.
