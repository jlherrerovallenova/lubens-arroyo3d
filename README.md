# Lubens · Portales 9 a 16 (Valladolid) — visor 3D y planos de venta

Web de una sola página con el modelo 3D del edificio (fachadas con los alzados del proyecto, cubierta en mansarda, entorno de calles), plano de disponibilidad, alzados, fichas de vivienda con plano comercial, análisis de soleamiento y comparador.

Publicada en Netlify: https://lubens-arroyo.netlify.app

## Estructura

| Ruta | Qué es |
|---|---|
| `index.html` | La web lista para servir (plantilla + datos incrustados). Es lo que publica Netlify. |
| `netlify.toml` | Publica la raíz tal cual, sin paso de build. |
| `src/app_template.html` | Código de la aplicación (HTML, CSS y JS con three.js r128). Contiene el marcador `/*DATA*/`. |
| `src/data.json` | Datos extraídos del DXF y de los PDF: viviendas, superficies, precios, geometría 3D, alzados, planos comerciales, cubierta. |
| `tools/build.py` | Genera `index.html` a partir de la plantilla y los datos. |
| `tools/pipeline/` | Scripts con los que se extrajeron los datos (DXF → viviendas, superficies oficiales, fachadas, alzados, planos, cubierta). Son de referencia: usan rutas de trabajo locales. |

## Regenerar la web

```bash
python3 tools/build.py   # escribe index.html
```

Los estados de disponibilidad compartidos por el equipo solo funcionan en la versión publicada como artefacto de Claude; en Netlify la web es de solo consulta.
