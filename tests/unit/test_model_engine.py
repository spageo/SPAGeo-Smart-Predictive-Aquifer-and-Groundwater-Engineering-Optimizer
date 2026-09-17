import unittest
import numpy as np
from spageo.core.model_engine import ModelEngine


class TestModelEngine(unittest.TestCase):
    """Test ModelEngine class."""

    def setUp(self):
        """Set up test environment."""
        self.engine = ModelEngine()

    def test_create_model(self):
        """Test model creation."""
        grid_config = {
            'nlay': 2,
            'nrow': 10,
            'ncol': 10,
            'delr': 100,
            'delc': 100,
            'top': 100,
            'botm': [50, 0]
        }

        boundary_conditions = {
            'recharge': 0.001
        }

        aquifer_properties = {
            'k': 1.0,
            'icelltype': 1
        }

        result = self.engine.create_model(
            grid_config,
            boundary_conditions,
            aquifer_properties
        )

        self.assertTrue(result)
        self.assertIsNotNone(self.engine.model)

    def test_run_simulation(self):
        """Test simulation execution."""
        # Create model first
        grid_config = {
            'nlay': 1,
            'nrow': 5,
            'ncol': 5,
            'delr': 100,
            'delc': 100,
            'top': 100,
            'botm': [0]
        }

        self.engine.create_model(
            grid_config,
            {'recharge': 0.001},
            {'k': 1.0}
        )

        time_config = {
            'nper': 1,
            'perlen': [365],
            'nstp': [1],
            'tsmult': [1.0]
        }

        results = self.engine.run_simulation(time_config)

        self.assertIsNotNone(results)
        self.assertIn('heads', results)

        # Check shape
        self.assertEqual(results['heads'].shape, (1, 5, 5))


if __name__ == '__main__':
    unittest.main()
