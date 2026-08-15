import os
import sys
from pathlib import Path

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QAction

# Add the SPAGeo project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.main_dialog import SPAGeoMainDialog


class SPAGeoPlugin:

    def __init__(self, iface):
        self.iface = iface

        self.plugin_dir = os.path.dirname(__file__)
        self.settings = QSettings()
        self.actions = []
        self.menu = "SPAGeo"
        self.toolbar = None

        self.action = None
        self.main_dialog = None

        self.model_config = None
        self.results_viewer = None
        self.data_gis = None
        self.copilot_dock = None

    def initGui(self):
        self.toolbar = self.iface.addToolBar("SPAGeo")
        self.toolbar.setObjectName("SPAGeoToolbar")

        self.action = QAction(
            "SPAGeo",
            self.iface.mainWindow()
        )

        self.action.triggered.connect(
            self.open_main_dialog
        )

        self.toolbar.addAction(self.action)
        self.actions.append(self.action)

        self.iface.addPluginToMenu(
            "&SPAGeo",
            self.action
        )

        self.iface.addToolBarIcon(
            self.action
        )

    def unload(self):
        if self.action:
            self.iface.removePluginMenu(
                "&SPAGeo",
                self.action
            )

            self.iface.removeToolBarIcon(
                self.action
            )

    def open_main_dialog(self):
        if self.main_dialog is None:
            self.main_dialog = SPAGeoMainDialog(
                self.iface.mainWindow()
            )

        self.main_dialog.show()
        self.main_dialog.raise_()
        self.main_dialog.activateWindow()
