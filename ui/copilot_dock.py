from qgis.PyQt.QtWidgets import QDockWidget


class CopilotDockWidget(QDockWidget):
    """SPAGeo AI Assistant / Copilot UI component."""

    def __init__(self, parent=None):
        super().__init__("SPAGeo Copilot", parent)
