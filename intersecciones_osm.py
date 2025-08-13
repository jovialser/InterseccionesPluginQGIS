from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject
import os

from .intersecciones_osm_dialog import InterseccionesPluginDialog

class InterseccionesOSM:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dlg = None
        self.action = None

    def initGui(self):
        icon = QIcon()  # Podés usar QIcon(os.path.join(self.plugin_dir, "icon.png")) si tenés un ícono
        self.action = QAction(icon, "Intersecciones OSM", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Intersecciones OSM", self.action)

    def unload(self):
        if self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("Intersecciones OSM", self.action)

    def run(self):
        if not self.dlg:
            self.dlg = InterseccionesPluginDialog()
        self.dlg.show()
