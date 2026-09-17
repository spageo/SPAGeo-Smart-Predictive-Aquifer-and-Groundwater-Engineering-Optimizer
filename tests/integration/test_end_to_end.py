"""End-to-end integration tests."""

import unittest
import tempfile
import os
from qgis.core import QgsApplication
from spageo.core.model_engine import ModelEngine
from spageo.core.ai_agent import SPAGeoAgent


class TestEndToEnd(unittest.TestCase):
    """End-to-end workflow tests."""

    @classmethod
    def setUpClass(cls):
        """Set up QGIS application."""
        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()

    @classmethod
    def tearDownClass(cls):
        """Clean up QGIS application."""
        cls.qgs.exitQgis()

    def test_full_workflow(self):
        """Test complete modeling workflow."""
        # 1. Create model
        engine = ModelEngine()
        grid_config = {
            'nlay': 1,
            'nrow': 20,
            'ncol': 20,
            'cell_size_x': 50,
            'cell_size_y': 50,
            'top': 100,
            'botm': [0]
        }

        engine.create_model(
            grid_config,
            {'recharge': 0.001},
            {'k': 1.0}
        )

        # 2. Run simulation
        time_config = {
            'nper': 2,
            'perlen': [365, 365],
            'nstp': [1, 1],
            'tsmult': [1.0, 1.0]
        }

        results = engine.run_simulation(time_config)
        self.assertIsNotNone(results)

        # 3. Export results
        # ... test export functionality