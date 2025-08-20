import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from shapely.ops import voronoi_diagram
import os
import pandas as pd
from qgis.utils import iface
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QDialog, QFileDialog
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsRasterLayer,
    QgsFillSymbol,
    QgsSimpleFillSymbolLayer,
    QgsSingleSymbolRenderer,
    QgsRuleBasedRenderer,  
    QgsMarkerSymbol
)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'intersecciones_osm_dialog_base.ui'))
class InterseccionesPluginDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButtonSeleccionarRuta.clicked.connect(self.seleccionar_ruta)
        self.pushButtonGenerar.clicked.connect(self.generar_intersecciones)
        self.pushButtonBuscarCSV.clicked.connect(self.abrir_csv)
        csv_path = os.path.join(os.path.dirname(__file__), "localidades_censales.csv")
        try:
            self.df_localidades = pd.read_csv(csv_path)
            provincias = sorted(self.df_localidades["provincia_nombre"].dropna().unique())
            self.comboBoxProvincia.addItems(provincias)
            self.comboBoxProvincia.currentIndexChanged.connect(self.actualizar_localidades)
            self.comboBoxLocalidad.currentIndexChanged.connect(self.actualizar_zona_utm)
            self.actualizar_localidades()
        except Exception as e:
            self.labelEstado.setText(f"⚠️ Error al cargar CSV: {str(e)}")
    def actualizar_localidades(self):
        provincia = self.comboBoxProvincia.currentText()
        filtrado = self.df_localidades[self.df_localidades["provincia_nombre"] == provincia]
        localidades = sorted(filtrado["nombre"].dropna().unique())
        self.comboBoxLocalidad.clear()
        self.comboBoxLocalidad.addItems(localidades)
        if localidades:
            ciudad = f"{localidades[0]}, {provincia}, Argentina"
            self.detectar_zona_utm(ciudad)
    def actualizar_zona_utm(self):
        localidad = self.comboBoxLocalidad.currentText()
        provincia = self.comboBoxProvincia.currentText()
        ciudad = f"{localidad}, {provincia}, Argentina"
        self.detectar_zona_utm(ciudad)
    def detectar_zona_utm(self, ciudad):
        try:
            gdf_ciudad = ox.geocode_to_gdf(ciudad)
            centroide = gdf_ciudad.geometry.centroid.iloc[0]
            lon = centroide.x
            zona = int((lon + 180) / 6) + 1
            epsg = 32700 + zona
            self.labelZonaUTM.setText(f"Zona UTM: {zona} (EPSG:{epsg})")
            return epsg
        except Exception as e:
            self.labelZonaUTM.setText("Zona UTM: ❌ Error")
            return None
    def seleccionar_ruta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if carpeta:
            self.lineEditRuta.setText(carpeta)    
    def abrir_csv(self):
        ruta_csv, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo CSV", "", "CSV (*.csv)")
        if ruta_csv:
            self.lineEditRutaCSV.setText(ruta_csv)
            self.cargar_csv_como_capa(ruta_csv)
            #QTimer.singleShot(3000, self.accept)
    def cargar_csv_como_capa(self, ruta_csv):
        try:
            df = pd.read_csv(ruta_csv)
            if 'latitud' not in df.columns or 'longitud' not in df.columns:
                self.labelEstado.setText("❌ El CSV debe tener columnas 'latitud' y 'longitud'.")
                return
            df['geometry'] = df.apply(lambda row: Point(row['longitud'], row['latitud']), axis=1)
            gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
            nombre = os.path.splitext(os.path.basename(ruta_csv))[0]
            ruta_temp = os.path.join(os.path.dirname(ruta_csv), f"{nombre}_temp.shp")
            gdf.to_file(ruta_temp)
            layer = QgsVectorLayer(ruta_temp, f"Capa CSV - {nombre}", "ogr")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                self.labelEstado.setText(f"✅ Capa cargada desde CSV:\n{ruta_temp}")                
            else:
                self.labelEstado.setText("⚠️ No se pudo cargar la capa en QGIS.")
        except Exception as e:
            self.labelEstado.setText(f"❌ Error al cargar CSV: {str(e)}")
    def agregar_capa_base_osm(self):
        url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        capa_osm = QgsRasterLayer(url, "OpenStreetMap", "wms")
        if capa_osm.isValid():
            QgsProject.instance().addMapLayer(capa_osm, False)
            root = QgsProject.instance().layerTreeRoot()
            root.insertLayer(0, capa_osm)
            self.capa_base_osm = capa_osm  
    def generar_voronoi(self, gdf_puntos, gdf_contorno):
        multipunto = MultiPoint(gdf_puntos.geometry.tolist())
        voronoi = voronoi_diagram(multipunto, envelope=gdf_contorno.unary_union)
        gdf_voronoi = gpd.GeoDataFrame(geometry=[poly for poly in voronoi.geoms], crs=gdf_puntos.crs)
        gdf_clipped = gpd.overlay(gdf_voronoi, gdf_contorno, how='intersection')
        return gdf_clipped
    def generar_intersecciones(self):
        nombre_localidad = self.comboBoxLocalidad.currentText()
        nombre_provincia = self.comboBoxProvincia.currentText()
        ciudad = f"{nombre_localidad}, {nombre_provincia}, Argentina"
        epsg_utm = self.detectar_zona_utm(ciudad)
        if epsg_utm is None:
            self.labelEstado.setText("❌ No se pudo determinar la zona UTM.")
            return
        try:
            G = ox.graph_from_place(ciudad, network_type='drive')
            nodes, edges = ox.graph_to_gdfs(G)
            intersec = nodes[nodes['street_count'] > 1].copy()
            intersec['geometry'] = intersec.apply(lambda row: Point(row['x'], row['y']), axis=1)
            gdf = gpd.GeoDataFrame(intersec, geometry='geometry', crs='EPSG:4326')
            gdf_utm = gdf.to_crs(epsg=epsg_utm)
            gdf_ciudad = ox.geocode_to_gdf(ciudad).to_crs(epsg=epsg_utm)
            buffers = gdf_utm.buffer(20)
            union = buffers.unary_union
            if union.geom_type == 'Polygon':
                centroides = [union.centroid]
            elif union.geom_type == 'MultiPolygon':
                centroides = [geom.centroid for geom in union.geoms if geom.area > 0]
            else:
                self.labelEstado.setText("⚠️ No se pudo generar geometrías fusionadas.")
                return
            gdf_utm_fusionados = gpd.GeoDataFrame(geometry=centroides, crs=gdf_utm.crs)
                # Puntos medios de calles (solo si longitud > 70m)
            edges_utm = edges.to_crs(epsg=epsg_utm)
            edges_filtradas = edges_utm[edges_utm.geometry.length > 70].copy()
            edges_filtradas['midpoint'] = edges_filtradas.geometry.apply(lambda line: line.interpolate(0.5, normalized=True))
            gdf_midpoints = gpd.GeoDataFrame(geometry=edges_filtradas['midpoint'], crs=edges_utm.crs)
            #-----
            # Crear buffers de 20 metros alrededor de los puntos medios
            buffers_midpoints = gdf_midpoints.buffer(20)
            # Unir los buffers en una sola geometría
            union_midpoints = buffers_midpoints.unary_union
            # Calcular centroides de la geometría fusionada
            if union_midpoints.geom_type == 'Polygon':
                centroides_midpoints = [union_midpoints.centroid]
            elif union_midpoints.geom_type == 'MultiPolygon':
                centroides_midpoints = [geom.centroid for geom in union_midpoints.geoms if geom.area > 0]
            else:
                self.labelEstado.setText("⚠️ No se pudo generar geometrías fusionadas de puntos medios.")
                return
            # Crear GeoDataFrame con los centroides de puntos medios
            gdf_centroides_midpoints = gpd.GeoDataFrame(geometry=centroides_midpoints, crs=gdf_midpoints.crs)
            #----
            if len(gdf_utm_fusionados) < 3:
                self.labelEstado.setText("⚠️ No hay suficientes puntos para generar Voronoi.")
                return
            #
            # Combinar centroides de intersecciones y puntos medios
            gdf_centroides_combinados_para_voronoi = gpd.GeoDataFrame(
                pd.concat([gdf_utm_fusionados, gdf_centroides_midpoints], ignore_index=True),
                crs=gdf_utm_fusionados.crs
            )
            # Generar Voronoi con todos los centroides combinados
            gdf_voronoi = self.generar_voronoi(gdf_centroides_combinados_para_voronoi, gdf_ciudad)
            #
            ruta_csv = self.lineEditRutaCSV.text().strip()
            df_csv = pd.read_csv(ruta_csv)
            if 'latitud' not in df_csv.columns or 'longitud' not in df_csv.columns:
                self.labelEstado.setText("❌ El CSV no contiene columnas 'latitud' y 'longitud'.")
                return
            df_csv['geometry'] = df_csv.apply(lambda row: Point(row['longitud'], row['latitud']), axis=1)
            gdf_csv = gpd.GeoDataFrame(df_csv, geometry='geometry', crs='EPSG:4326').to_crs(epsg=epsg_utm)
            gdf_voronoi['voronoi_id'] = range(len(gdf_voronoi))
            gdf_join = gpd.sjoin(gdf_csv, gdf_voronoi, how='left', predicate='intersects')
            conteo_categorico = (
                gdf_join.groupby(['voronoi_id', 'id'])
                .size()
                .unstack(fill_value=0)
                .reset_index()
            )
            columnas_renombradas = {
                'atropello de peatones': 'atropello',
                'colisión entre vehículos': 'colision',
                'vuelco': 'vuelco'
            }
            conteo_categorico.rename(columns=columnas_renombradas, inplace=True)
            conteo_categorico['total_inci'] = conteo_categorico[list(columnas_renombradas.values())].sum(axis=1)
            gdf_voronoi = gdf_voronoi.merge(conteo_categorico, on='voronoi_id', how='left')
            for col in list(columnas_renombradas.values()) + ['total_inci']:
                gdf_voronoi[col] = gdf_voronoi[col].fillna(0).astype(int)
            gdf_utm_fusionados['centroide_id'] = range(len(gdf_utm_fusionados))
            #---
            gdf_utm_fusionados = gpd.sjoin(
                gdf_utm_fusionados,
                gdf_voronoi[['voronoi_id'] + list(columnas_renombradas.values()) + ['total_inci', 'geometry']],
                how='left',
                predicate='intersects'
            )
            for col in list(columnas_renombradas.values()) + ['total_inci']:
                gdf_utm_fusionados[col] = gdf_utm_fusionados[col].fillna(0).astype(int)
            #---
            gdf_centroides_midpoints = gpd.sjoin(
                gdf_centroides_midpoints,
                gdf_voronoi[['voronoi_id'] + list(columnas_renombradas.values()) + ['total_inci', 'geometry']],
                how='left',
                predicate='intersects'
            )
            for col in list(columnas_renombradas.values()) + ['total_inci']:
                gdf_centroides_midpoints[col] = gdf_centroides_midpoints[col].fillna(0).astype(int)
            #------    
            gdf_voronoi = gpd.sjoin(gdf_voronoi, gdf_utm, how='left', predicate='intersects')
            gdf_final = gdf_voronoi.to_crs(epsg=4326)
            nombre = ciudad.replace(",", "").replace(" ", "_")
            carpeta = self.lineEditRuta.text().strip()
            if not carpeta:
                self.labelEstado.setText("❌ Por favor seleccioná una carpeta de salida.")
                return
            if not os.path.isdir(carpeta):
                self.labelEstado.setText("⚠️ La carpeta seleccionada no existe.")
                return
            if not os.access(carpeta, os.W_OK):
                self.labelEstado.setText("🚫 No tenés permisos de escritura en esa carpeta.")
                return
            ruta_voronoi = os.path.join(carpeta, f"voronoi_intersecciones_{nombre}.shp")
            ruta_puntos = os.path.join(carpeta, f"intersecciones_{nombre}.shp")
            ruta_centroides = os.path.join(carpeta, f"centroides_fusionados_{nombre}.shp")
            #
            # Guardar puntos medios como shapefile
            ruta_centroides_midpoints = os.path.join(carpeta, f"centroides_puntos_medios_{nombre}.shp")
            gdf_centroides_midpoints.to_crs(epsg=4326).to_file(ruta_centroides_midpoints)
            #
            gdf_final.to_file(ruta_voronoi)
            gdf.to_file(ruta_puntos)
            #gdf_utm_fusionados.to_crs(epsg=4326).to_file(ruta_centroides)
            gdf_centroides_midpoints['tipo'] = 'punto_medio'
            gdf_utm_fusionados['tipo'] = 'centroide'
            gdf_centroides_combinados = gpd.GeoDataFrame(
                pd.concat([gdf_utm_fusionados, gdf_centroides_midpoints], ignore_index=True),
                crs=gdf_utm_fusionados.crs
            ).to_crs(epsg=4326)
            gdf_centroides_combinados.to_file(ruta_centroides)
            #----
            self.agregar_capa_base_osm()
            layer_voronoi = QgsVectorLayer(ruta_voronoi, f"Voronoi - {nombre}", "ogr")
            layer_puntos = QgsVectorLayer(ruta_puntos, f"Intersecciones - {nombre}", "ogr")
            layer_centroides = QgsVectorLayer(ruta_centroides, f"Centroides Fusionados - {nombre}", "ogr")
            if layer_puntos.isValid():
                symbol = layer_puntos.renderer().symbol()
                symbol.setColor(QColor(0, 100, 255))
                symbol.setSize(2.5)
                QgsProject.instance().addMapLayer(layer_puntos)
            #---
            layer_centroides_midpoints = QgsVectorLayer(ruta_centroides_midpoints, f"Centroides Puntos Medios - {nombre}", "ogr")
            if layer_centroides_midpoints.isValid():
                symbol = layer_centroides_midpoints.renderer().symbol()
                symbol.setColor(QColor(255, 0, 255))  # fucsia
                symbol.setSize(2.5)
                QgsProject.instance().addMapLayer(layer_centroides_midpoints)
            #---
            nodo_puntos = QgsProject.instance().layerTreeRoot().findLayer(layer_puntos.id())
            if nodo_puntos:
                nodo_puntos.setItemVisibilityChecked(False)
            if layer_centroides.isValid():
                renderer = QgsRuleBasedRenderer(QgsMarkerSymbol.createSimple({}))
                root_rule = renderer.rootRule()
                regla_1 = QgsRuleBasedRenderer.Rule(QgsMarkerSymbol.createSimple({'color': '0,255,0', 'size': '3'}))
                regla_1.setLabel("Baja o nula siniestralidad")
                regla_1.setFilterExpression('"total_inci" >= 0 AND "total_inci" <= 1')                
                root_rule.appendChild(regla_1)
                regla_2 = QgsRuleBasedRenderer.Rule(QgsMarkerSymbol.createSimple({'color': '255,255,0', 'size': '3.5'}))
                regla_2.setLabel("media siniestralidad")
                regla_2.setFilterExpression('"total_inci" >= 2 AND "total_inci" <= 4')
                root_rule.appendChild(regla_2)
                regla_3 = QgsRuleBasedRenderer.Rule(QgsMarkerSymbol.createSimple({'color': '255,0,0', 'size': '4'}))
                regla_3.setLabel("Alta siniestralidad")
                regla_3.setFilterExpression('"total_inci" > 4')
                root_rule.appendChild(regla_3)
                layer_centroides.setRenderer(renderer)
                QgsProject.instance().addMapLayer(layer_centroides)
            if layer_voronoi.isValid():
                fill_layer = QgsSimpleFillSymbolLayer()
                fill_layer.setFillColor(QColor(0, 100, 255, 64))
                fill_layer.setStrokeColor(QColor(0, 100, 255))
                fill_layer.setStrokeWidth(0.5)
                symbol = QgsFillSymbol()
                symbol.changeSymbolLayer(0, fill_layer)
                layer_voronoi.setRenderer(QgsSingleSymbolRenderer(symbol))
                QgsProject.instance().addMapLayer(layer_voronoi)
            nodo_voronoi = QgsProject.instance().layerTreeRoot().findLayer(layer_voronoi.id())
            if nodo_voronoi:
                nodo_voronoi.setItemVisibilityChecked(False)
                iface.mapCanvas().setExtent(layer_voronoi.extent())
                iface.mapCanvas().refresh()
            nodo_voronoi = QgsProject.instance().layerTreeRoot().findLayer(layer_voronoi.id())
            if nodo_voronoi:
                nodo_voronoi.setItemVisibilityChecked(False)
                iface.mapCanvas().setExtent(layer_voronoi.extent())
                iface.mapCanvas().refresh()
            root = QgsProject.instance().layerTreeRoot()
            nodo_base = root.findLayer(self.capa_base_osm.id())
            if nodo_base:
                root.insertChildNode(5, nodo_base.clone())
                root.removeChildNode(nodo_base)
            self.labelEstado.setText(f"✅ Shapefiles guardados y cargados en QGIS:\n{ruta_voronoi}")
        except Exception as e:
            self.labelEstado.setText(f"❌ Error: {str(e)}")