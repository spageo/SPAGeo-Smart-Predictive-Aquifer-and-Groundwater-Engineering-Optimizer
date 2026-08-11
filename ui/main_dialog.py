from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTabWidget,
    QWidget,
)
from qgis.PyQt.QtCore import Qt, pyqtSignal


class SPAGeoMainDialog(QDialog):
    """Main SPAGeo user interface."""

    model_created = pyqtSignal()
    simulation_started = pyqtSignal()
    simulation_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            "SPAGeo — Smart Predictive Aquifer & Groundwater "
            "Engineering Optimizer"
        )

        self.setMinimumSize(900, 600)

        self._build_ui()

    def _build_ui(self):
        """Build the main SPAGeo workspace."""

        layout = QVBoxLayout()
        self.setLayout(layout)

        # ---------------------------------------------------------
        # Header
        # ---------------------------------------------------------

        title = QLabel("SPAGeo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "Smart Predictive Aquifer & Groundwater "
            "Engineering Optimizer"
        )
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(subtitle)

        # ---------------------------------------------------------
        # Separator
        # ---------------------------------------------------------

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        layout.addWidget(separator)

        # ---------------------------------------------------------
        # Main workflow tabs
        # ---------------------------------------------------------

        self.tabs = QTabWidget()

        # Data & GIS
        data_tab = self._create_placeholder_tab(
            "Data & GIS",
            "Data import, GIS layers, preprocessing, "
            "and groundwater data management will be integrated here."
        )

        # Model Configuration
        model_tab = self._create_placeholder_tab(
            "Model Configuration",
            "Groundwater model configuration will be integrated here."
        )

        # Simulation
        simulation_tab = self._create_placeholder_tab(
            "Simulation",
            "Simulation controls and model execution "
            "will be integrated here."
        )

        # Results & Visualization
        results_tab = self._create_placeholder_tab(
            "Results & Visualization",
            "Simulation results, analysis, maps, charts, "
            "and visualization will be integrated here."
        )

        # AI Assistant
        ai_tab = self._create_placeholder_tab(
            "AI Assistant",
            "The SPAGeo AI Assistant / Copilot will be "
            "integrated here in a later development phase."
        )

        self.tabs.addTab(data_tab, "Data & GIS")
        self.tabs.addTab(model_tab, "Model Configuration")
        self.tabs.addTab(simulation_tab, "Simulation")
        self.tabs.addTab(results_tab, "Results & Visualization")
        self.tabs.addTab(ai_tab, "AI Assistant")

        layout.addWidget(self.tabs)

        # ---------------------------------------------------------
        # Close button
        # ---------------------------------------------------------

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        layout.addWidget(close_button)

    def _create_placeholder_tab(self, title, description):
        """Create a temporary placeholder for a workflow component."""

        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        heading = QLabel(title)
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        description_label = QLabel(description)
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)

        tab_layout.addStretch()
        tab_layout.addWidget(heading)
        tab_layout.addWidget(description_label)
        tab_layout.addStretch()

        return tab


    def _on_model_created(self):
        """Handle model-created event."""
        pass

    def _on_simulation_started(self):
        """Handle simulation-started event."""
        pass

    def _on_simulation_completed(self):
        """Handle simulation-completed event."""
        pass
