import os
import sys
from pathlib import Path

from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtWidgets import QAction

# Add the SPAGeo project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.main_dialog import SPAGeoMainDialog
from ui.copilot_dock import CopilotDockWidget

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

        self.agent = None
        self.model_engine = None
        self.cloud_manager = None

        self.model_config = None
        self.results_viewer = None
        self.data_gis = None
        self.copilot_dock = None

    def initGui(self):

        self.toolbar = self.iface.addToolBar("SPAGeo")
        self.toolbar.setObjectName("SPAGeoToolbar")

        # Create Copilot action
        self.copilot_action = QAction(
            "SPAGeo Copilot",
            self.iface.mainWindow()
        )

        self.copilot_action.triggered.connect(
            self.open_copilot
        )

        self.toolbar.addAction(
            self.copilot_action
        )

        self.actions.append(
            self.copilot_action
        )

        self.iface.addPluginToMenu(
            "&SPAGeo",
            self.copilot_action
        )


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

    # Initialize core component placeholders
        self.initialize_core()

    def initialize_core(self):
        """Initialize core SPAGeo component placeholders."""
        self.agent = None
        self.model_engine = None
        self.cloud_manager = None

    def open_copilot(self):
        """Open the SPAGeo Copilot."""

        if self.copilot_dock is None:
            self.copilot_dock = CopilotDockWidget(
                self.iface.mainWindow()
            )
            self.iface.addDockWidget(
                Qt.RightDockWidgetArea,
                self.copilot_dock
            )

        self.copilot_dock.show()
        self.copilot_dock.raise_()

    def unload(self):
        """Unload SPAGeo plugin."""

        # Remove toolbar
        if self.toolbar:
            del self.toolbar

        # Remove actions
        for action in self.actions:
            self.iface.removePluginMenu(
                "&SPAGeo",
                action
            )
            self.iface.removeToolBarIcon(action)
        # Close dialogs
        if self.main_dialog:
            self.main_dialog.close()

        if self.copilot_dock:
            self.copilot_dock.close()

    def open_main_dialog(self):
        if self.main_dialog is None:
            self.main_dialog = SPAGeoMainDialog(
                self.iface,
                self.agent,
                self.model_engine,
                self.cloud_manager
            )

        self.main_dialog.show()
        self.main_dialog.raise_()
        self.main_dialog.activateWindow()
