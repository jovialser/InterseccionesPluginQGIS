InterseccionesPlugin/
├── __init__.py
├── InterseccionesPlugin.py
├── InterseccionesPluginDialog.py
├── resources.qrc
├── recursos/
│   └── localidades_censales.csv
├── ui/
│   └── InterseccionesPlugin.ui
├── metadata.txt
└── README.md

# 🧭 InterseccionesPlugin

**InterseccionesPlugin** es un complemento para QGIS que permite generar análisis espacial de intersecciones viales en localidades de Argentina, utilizando datos de OpenStreetMap y CSVs de incidentes geolocalizados. El plugin identifica intersecciones críticas, genera diagramas de Voronoi para análisis espacial y visualiza la siniestralidad vial según diferentes categorías de accidentes

---

## 🚀 Funcionalidades


🔍 Búsqueda de localidades argentinas por provincia y nombre
🗺️ Descarga automática de redes viales desde OpenStreetMap
⚠️ Identificación de intersecciones y puntos críticos en la red vial
📊 Análisis de siniestralidad mediante diagramas de Voronoi
🎨 Visualización con codificación por colores según gravedad de accidentes
📥 Importación de datos de accidentes desde archivos CSV
🌍 Determinación automática de zona UTM para proyección precisa

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
Instalación
Descarga el repositorio completo
Copia la carpeta del plugin en el directorio de plugins de QGIS:
Windows: C:\Users\[tu_usuario]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
macOS: ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
Linux: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
Reinicia QGIS
Activa el plugin en el Administrador de Plugins de QGIS
Uso
Abre el plugin desde el menú "Plugins" → "Intersecciones OSM"
Selecciona una provincia y localidad en los dropdowns correspondientes
El plugin detectará automáticamente la zona UTM apropiada
Selecciona una carpeta de salida para los resultados
Carga un archivo CSV con datos de accidentes (requiere columnas "latitud" y "longitud")
Ajusta los pesos para diferentes tipos de accidentes según su gravedad
Haz clic en "Generar" para crear el análisis
Los resultados se cargarán automáticamente en QGIS con una capa base de OpenStreetMap
Consideraciones importantes sobre el uso de los servidores de OpenStreetMap
⚠️ IMPORTANTE: Cumplimiento de políticas de uso

Este plugin utiliza los servidores de tiles de OpenStreetMap, los cuales tienen políticas estrictas de uso:

"You've reached the OpenStreetMap.org tile server (piasa.openstreetmap.org)

If you are a developer...
Please be aware of the tile usage policy.
This service is sponsored by Fastly." 

Directrices para usuarios responsables:
Evita ejecutar múltiples análisis en corto tiempo - Las descargas frecuentes sobrecargan los servidores
No uses este plugin para análisis masivos o automatizados - Los servidores están diseñados para uso humano normal
Considera usar servicios alternativos para proyectos intensivos - Para trabajos extensos, utiliza espejos regionales o servicios comerciales
Siempre mantén visible la capa base - Los datos de OpenStreetMap deben ser visualizados con su respectiva atribución
Los desarrolladores del plugin han implementado medidas para minimizar el impacto en los servidores, pero los usuarios deben ser conscientes de su responsabilidad al usar este servicio.

Contribución
¡Las contribuciones son bienvenidas! Si deseas mejorar este plugin:

Haz un fork del repositorio
Crea una nueva rama (git checkout -b mi-nueva-funcionalidad)
Realiza tus cambios
Haz commit de tus cambios (git commit -am 'Añade nueva funcionalidad')
Sube la rama (git push origin mi-nueva-funcionalidad)
Crea un nuevo Pull Request
Licencia
Este proyecto está licenciado bajo la licencia GNU General Public License v3.0 - ver el archivo LICENSE para más detalles.

Atribución
Datos geoespaciales: © OpenStreetMap contributors
Servicio de tiles patrocinado por: Fastly
Plugin desarrollado para análisis de seguridad vial en Argentina
