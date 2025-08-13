# 🧭 InterseccionesPlugin

**InterseccionesPlugin** es un complemento para QGIS que permite generar análisis espacial de intersecciones viales en localidades de Argentina, utilizando datos de OpenStreetMap y CSVs de incidentes geolocalizados.

---

## 🚀 Funcionalidades

- 📍 Detecta intersecciones viales en una localidad seleccionada
- 🧮 Fusiona puntos cercanos y genera centroides
- 📊 Crea diagramas de Voronoi para análisis territorial
- 📈 Cuenta incidentes por tipo dentro de cada celda Voronoi
- 🗂️ Exporta shapefiles de intersecciones, centroides y polígonos Voronoi
- 🗺️ Carga capa base de OpenStreetMap automáticamente

---

## 🛠️ Requisitos

- QGIS 3.x
- Python 3
- Paquetes:
  - `osmnx`
  - `geopandas`
  - `pandas`
  - `shapely`

---

## 📦 Instalación

1. Cloná o descargá este repositorio:

```bash
git clone https://github.com/tu-usuario/InterseccionesPlugin.git

---
Este software es propiedad del autor. Se permite su uso, modificación y distribución únicamente con fines personales, educativos o de investigación.  
Queda estrictamente prohibido su uso comercial, su integración en productos con fines de lucro, o su redistribución por empresas sin autorización escrita del autor.
