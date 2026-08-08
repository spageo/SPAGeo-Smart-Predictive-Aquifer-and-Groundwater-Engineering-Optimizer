from qgis.PyQt.QtWidgets import QAction, QMessageBox


class SPAGeoPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("SPAGeo", self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        self.iface.addPluginToMenu("&SPAGeo", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginMenu("&SPAGeo", self.action)
            self.iface.removeToolBarIcon(self.action)

    def run(self):
        QMessageBox.information(
            self.iface.mainWindow(),
            "SPAGeo",
            "SPAGeo plugin loaded successfully!"
        )