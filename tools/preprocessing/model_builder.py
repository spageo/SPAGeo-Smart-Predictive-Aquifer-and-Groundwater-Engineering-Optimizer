from typing import Dict, List, Optional
import numpy as np
import ee
from shapely.geometry import mapping
from .satellite_processor import SatelliteProcessor
from ..core.model_engine import ModelEngine


class ModelBuilder:
    """
    Automatically build groundwater models from GIS data and satellite imagery.

    This addresses the pain point identified in APEXMOD development:
    spatial linking is "a slow, tedious, and error-prone process"[citation:1].
    """

    def __init__(self):
        """Initialize model builder."""
        self.sat_processor = SatelliteProcessor()
        self.model_engine = ModelEngine()

    def build_from_area(self,
                        geometry,
                        resolution: int = 100,
                        layers: int = 1) -> Dict:
        """
        Build complete model from area geometry.

        Args:
            geometry: AOI geometry
            resolution: Cell size in meters
            layers: Number of model layers

        Returns:
            Dict: Model configuration
        """
        # 1. Delineate watershed
        watershed = self.sat_processor.delineate_watershed(
            (geometry.centroid.y, geometry.centroid.x)
        )


        # 2. Classify land use
        # Convert Shapely AOI to Earth Engine geometry for satellite processing.
        ee_geometry = ee.Geometry(mapping(geometry))
        land_use = self.sat_processor.classify_land_use(ee_geometry)
        # 3. Estimate hydraulic conductivity
        k_array = self.sat_processor.estimate_hydraulic_conductivity(land_use)

        # 4. Build grid

        grid_config = self._build_grid(
            geometry,
            resolution,
            k_shape=k_array.shape
        )

        # 5. Configure model
        model_config = {
            'name': 'Auto_Model',
            'grid': grid_config,
            'aquifer': {
                'k': k_array,
                'icelltype': 1,
                'storage': 0.001
            },
            'boundary': {
                'recharge': self._estimate_recharge(land_use),
                'wells': self._detect_wells(geometry)
            },
            'time': {
                'nper': 1,
                'perlen': [365.0],
                'nstp': [12],
                'tsmult': [1.0]
            }
        }

        return model_config

    def _build_grid(
            self,
            geometry,
            resolution: int,
            k_shape=None
    ) -> Dict:
        """Build model grid from geometry."""
        # Get bounding box
        bbox = geometry.bounds
        xmin, ymin, xmax, ymax = bbox

        # Calculate grid dimensions
        width = xmax - xmin
        height = ymax - ymin

        ncol = int(np.ceil(width / resolution))
        nrow = int(np.ceil(height / resolution))

        if k_shape is not None:
            nrow, ncol = k_shape

        return {
            'nlay': 1,
            'nrow': nrow,
            'ncol': ncol,
            'cell_size_x': resolution,
            'cell_size_y': resolution,
            'top': 100.0,  # Simplified
            'botm': [0.0]
        }

    def _estimate_recharge(self, land_use: Dict) -> float:
        """Estimate recharge based on land use."""
        # Simplified: use land use to estimate recharge
        # In practice, use more sophisticated methods
        return 0.001  # 1 mm/day

    def _detect_wells(self, geometry) -> List:
        """Detect wells from GIS data."""
        # Use QGIS layers to find well locations
        from qgis.core import QgsProject

        project = QgsProject.instance()
        well_layers = [l for l in project.mapLayers().values()
                       if 'well' in l.name().lower()]

        wells = []
        for layer in well_layers:
            for feature in layer.getFeatures():
                if feature.geometry().within(geometry):
                    wells.append({
                        'x': feature.geometry().asPoint().x(),
                        'y': feature.geometry().asPoint().y(),
                        'rate': feature.attribute('rate', 0.0)
                    })

        return wells
