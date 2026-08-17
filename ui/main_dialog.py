import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QDialog, QWidget


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        "spageo_main.ui"
    )
)


class SPAGeoMainDialog(QDialog, FORM_CLASS):
    """Main SPAGeo user interface."""

    model_created = pyqtSignal()
    simulation_started = pyqtSignal()
    simulation_completed = pyqtSignal()

    def __init__(
        self,
        iface=None,
        agent=None,
        model_engine=None,
        cloud_manager=None,
        parent=None
    ):
        super().__init__(parent)

        self.iface = iface
        self.agent = agent
        self.model_engine = model_engine
        self.cloud_manager = cloud_manager

        self.setupUi(self)

        # Setup tabs
        self.setup_tabs()

        # Connect signals
        self.connect_signals()

        # Future component attachment points
        self.model_config = None
        self.results_viewer = None
        self.copilot_dock = None
        self.data_gis = None

        self.model_created.connect(self._on_model_created)
        self.simulation_started.connect(self._on_simulation_started)
        self.simulation_completed.connect(self._on_simulation_completed)

    def setup_tabs(self):
        """Setup main tabbed interface."""

        # Tab 1: Data Preprocessing
        self.tab_data = self.findChild(QWidget, "tab_data")

        # Tab 2: Model Configuration
        self.tab_config = self.findChild(QWidget, "tab_config")

        # Tab 3: Simulation Control
        self.tab_simulation = self.findChild(QWidget, "tab_simulation")

        # Tab 4: Results Visualization
        self.tab_results = self.findChild(QWidget, "tab_results")

        # Tab 5: AI Assistant
        self.tab_ai = self.findChild(QWidget, "tab_ai")

    def connect_signals(self):
        """Connect UI signals."""

        # Import data button
        self.btn_import_data.clicked.connect(
            self.import_data
        )

        # Auto-build model button
        self.btn_auto_build.clicked.connect(
            self.auto_build_model
        )

        # Run simulation button
        self.btn_run_simulation.clicked.connect(
            self.run_simulation
        )

        # Export results button
        self.btn_export_results.clicked.connect(
            self.export_results
        )

    def _on_model_created(self):
        """Handle model-created event."""
        pass

    def _on_simulation_started(self):
        """Handle simulation-started event."""
        pass

    def _on_simulation_completed(self):
        """Handle simulation-completed event."""
        pass

    def import_data(self):
        """Import GIS data for modeling."""
        # Implementation will be detailed in Phase 3
        pass

    def auto_build_model(self):
        """Automatically build conceptual model using AI."""
        # Implementation will be detailed in Phase 6
        pass

    def run_simulation(self):
        """Run groundwater simulation."""
        # Implementation will be detailed in Phase 3
        pass

    def export_results(self):
        """Export simulation results."""
        # Implementation will be detailed in Phase 7
        pass

    def set_model_config(self, component):
        """Attach the model configuration component."""
        self.model_config = component

    def set_results_viewer(self, component):
        """Attach the results viewer component."""
        self.results_viewer = component

    def set_copilot_dock(self, component):
        """Attach the AI Copilot component."""
        self.copilot_dock = component

    def set_data_gis(self, component):
        """Attach the Data & GIS component."""
        self.data_gis = component
