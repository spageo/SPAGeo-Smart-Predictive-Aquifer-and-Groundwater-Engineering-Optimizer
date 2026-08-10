from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from qgis.PyQt.QtCore import Qt

class SPAGeoMainDialog(QDialog):
    """Main SPAGeo user interface."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            "SPAGeo — Smart Predictive Aquifer & Groundwater Engineering Optimizer"
        )

        self.setMinimumSize(700, 500)

        self._build_ui()

    def _build_ui(self):
        """Build the initial SPAGeo main interface."""

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("SPAGeo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(
            "Smart Predictive Aquifer & Groundwater "
            "Engineering Optimizer"
        )
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(subtitle)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        layout.addWidget(separator)

        # Initial workspace message
        workspace = QLabel(
            "SPAGeo Workspace\n\n"
            "This is the initial main interface.\n\n"
            "Future workflow components will be integrated here:\n"
            "• Data & GIS\n"
            "• Model Configuration\n"
            "• Simulation\n"
            "• Results & Visualization\n"
            "• AI Copilot"
        )

        workspace.setAlignment(Qt.AlignCenter)
        layout.addWidget(workspace)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        layout.addWidget(close_button)
