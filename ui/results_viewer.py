from qgis.PyQt.QtWidgets import QWidget


class ResultsViewerWidget(QWidget):
    """SPAGeo results and visualization UI component."""

    def __init__(self, parent=None):
        super().__init__(parent)