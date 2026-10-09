"""
SPAGeo Standalone Desktop Application

Standalone Windows host for the SPAGeo QGIS-based application.

This file hosts:
    - QGIS application/runtime
    - QGIS map canvas
    - Existing SPAGeo main dialog

The existing plugin files and UI are intentionally left unchanged.
"""

import os
import sys
import gc

# ----------------------------------------------------------------------
# QGIS standalone runtime bootstrap
# ----------------------------------------------------------------------

QGIS_ROOT = r"C:\PROGRA~1\QGIS34~1.12"
QGIS_PREFIX = os.path.join(QGIS_ROOT, "apps", "qgis-ltr")
QGIS_PYTHON = os.path.join(QGIS_PREFIX, "python")
QGIS_BIN = os.path.join(QGIS_PREFIX, "bin")
QT_BIN = os.path.join(QGIS_ROOT, "apps", "Qt5", "bin")
QT_PLUGINS = os.path.join(QGIS_ROOT, "apps", "Qt5", "plugins")

if QGIS_PYTHON not in sys.path:
    sys.path.insert(0, QGIS_PYTHON)

os.environ["QGIS_PREFIX_PATH"] = QGIS_PREFIX
os.environ["QT_PLUGIN_PATH"] = QT_PLUGINS

os.environ["PATH"] = (
    QGIS_BIN
    + os.pathsep
    + QT_BIN
    + os.pathsep
    + os.environ.get("PATH", "")
)

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(QGIS_BIN)
    os.add_dll_directory(QT_BIN)


from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QWidget,
)

from qgis.core import QgsApplication, QgsProject
from qgis.gui import QgsMapCanvas


# ----------------------------------------------------------------------
# Project path
# ----------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ----------------------------------------------------------------------
# Minimal standalone interface adapter
# ----------------------------------------------------------------------

class StandaloneInterface:
    """
    Minimal replacement for the QGIS plugin 'iface' object.

    The existing SPAGeoMainDialog expects:
        iface.mapCanvas()
        iface.activeLayer()

    We provide those methods without modifying the plugin dialog.
    """

    def __init__(self, map_canvas):
        self._map_canvas = map_canvas

    def mapCanvas(self):
        """Return the standalone QGIS map canvas."""
        return self._map_canvas

    def activeLayer(self):
        """
        Return the currently active layer.

        Standalone layer-selection support will be added later.
        """
        return None


# ----------------------------------------------------------------------
# Standalone main window
# ----------------------------------------------------------------------

class SPAGeoStandaloneWindow(QMainWindow):
    """Main window for the standalone SPAGeo desktop application."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SPAGeo - Smart Predictive Aquifer and Groundwater Engineering Optimizer")
        self.resize(1600, 900)

        # --------------------------------------------------------------
        # QGIS map canvas
        # --------------------------------------------------------------

        self.map_canvas = QgsMapCanvas()
        self.map_canvas.setCanvasColor(Qt.white)

        # --------------------------------------------------------------
        # Interface adapter
        # --------------------------------------------------------------

        self.iface = StandaloneInterface(self.map_canvas)

        # --------------------------------------------------------------
        # Existing SPAGeo dialog
        # --------------------------------------------------------------

        from ui.main_dialog import SPAGeoMainDialog

        self.spageo_dialog = SPAGeoMainDialog(
            iface=self.iface
        )

        # The existing object is a QDialog.
        # Convert it into an embeddable QWidget for the standalone host.
        self.spageo_dialog.setParent(self)
        self.spageo_dialog.setWindowFlags(Qt.Widget)

        # --------------------------------------------------------------
        # Side-by-side application layout
        # --------------------------------------------------------------

        splitter = QSplitter(Qt.Horizontal)

        splitter.addWidget(self.map_canvas)
        splitter.addWidget(self.spageo_dialog)

        # Give the map canvas more initial space than the control panel.
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self.setCentralWidget(splitter)

        # --------------------------------------------------------------
        # Initial project layers
        # --------------------------------------------------------------

        self.refresh_map_canvas()

    def refresh_map_canvas(self):
        """Display currently loaded QGIS project layers on the map canvas."""

        layers = list(QgsProject.instance().mapLayers().values())

        if layers:
            self.map_canvas.setLayers(layers)
            self.map_canvas.zoomToFullExtent()


# ----------------------------------------------------------------------
# Application entry point
# ----------------------------------------------------------------------

def main():
    """Start the standalone SPAGeo application."""

    print("Starting SPAGeo standalone application...")
    print(f"Project root: {PROJECT_ROOT}")

    # True = GUI application.
    qgs_app = QgsApplication([], True)

    try:
        # Initialize the QGIS runtime.
        qgs_app.initQgis()

        print("QGIS initialization: PASS")
        print(f"QGIS version: {QgsApplication.applicationVersion()}")
        print(f"QGIS prefix path: {QgsApplication.prefixPath()}")

        # Create the Qt main window.
        window = SPAGeoStandaloneWindow()

        window.show()
        window.raise_()
        window.activateWindow()

        print("SPAGeo standalone window visible:", window.isVisible())
        print("Standalone application: PASS")
        print("Close the SPAGeo window to finish the test.")

        # Start Qt event loop.
        exit_code = qgs_app.exec()

        return exit_code


    finally:

        # Release the standalone window before shutting down QGIS.

        if "window" in locals() and window is not None:
            window.close()

            window.deleteLater()

            qgs_app.processEvents()

            del window

            gc.collect()

            qgs_app.processEvents()

        # Shut down the QGIS runtime after releasing its widgets.

        qgs_app.exitQgis()

        print("QGIS shutdown: PASS")

if __name__ == "__main__":
    sys.exit(main())
