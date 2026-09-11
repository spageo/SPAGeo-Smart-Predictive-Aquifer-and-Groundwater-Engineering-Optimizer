import ee
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
from typing import Dict, List, Optional, Tuple


class SatelliteProcessor:
    """Process satellite imagery for model generation."""

    def __init__(self):
        """Initialize Earth Engine."""
        # Initialize Earth Engine
        ee.Initialize(project='spageo')

        # Landsat collections
        self.landsat_collection = ee.ImageCollection(
            "LANDSAT/LC08/C02/T1_L2"
        )
        self.sentinel_collection = ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )

    def delineate_watershed(self, point: Tuple[float, float]) -> gpd.GeoDataFrame:
        """
        Delineate watershed using elevation data.

        Args:
            point: (latitude, longitude) tuple

        Returns:
            GeoDataFrame: Watershed boundary
        """
        # Get elevation data
        elevation = ee.Image("USGS/SRTMGL1_003")

        # Get watershed delineation
        watershed = self._get_watershed(point, elevation)

        # Convert to GeoDataFrame
        return self._ee_to_gdf(watershed)

    def _get_watershed(self, point: Tuple[float, float], elevation):
        """Delineate watershed from elevation data."""
        import ee

        # Create point geometry
        point_geom = ee.Geometry.Point(point[1], point[0])

        # Get watershed using hydroSHEDS
        watershed = ee.Image("WWF/HydroSHEDS/15ACC")

        # Use watershed delineation algorithms
        # Return watershed geometry
        return ee.FeatureCollection([ee.Feature(point_geom.buffer(1000))])

    def classify_land_use(self, geometry) -> Dict:
        """
        Classify land use using machine learning.

        Following GeoAI approach for land cover classification[citation:2].

        Args:
            geometry: AOI geometry

        Returns:
            Dict: Land use classes and areas
        """
        # Get recent Sentinel-2 imagery
        image = (
            self.sentinel_collection
            .filterBounds(geometry)
            .filterDate("2021-01-01", "2022-01-01")
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
            .sort("CLOUDY_PIXEL_PERCENTAGE")
            .first()
        )
        # Load classification model
        classifier = ee.Classifier.smileRandomForest(
            numberOfTrees=50,
            variablesPerSplit=None,
            minLeafPopulation=2,
            bagFraction=0.5,
            seed=0
        )

        # Perform classification
        # Using GeoAI's approach for water body detection
        land_use = self._classify_image(image, classifier, geometry)

        return self._parse_land_use(land_use, geometry)

    def estimate_hydraulic_conductivity(self, land_use: Dict) -> np.ndarray:
        """
        Estimate hydraulic conductivity based on land use.

        Uses empirical relationships for typical K values.
        """
        # Mapping from land use to K values (m/day)
        k_mapping = {
            'water': 0.001,
            'wetland': 5.0,
            'forest': 10.0,
            'agriculture': 1.0,
            'urban': 0.1,
            'barren': 0.01,
            'grassland': 0.5
        }

        # Create K array based on land use classification
        k_array = np.zeros(land_use['shape'])
        for class_name, class_id in land_use['classes'].items():
            k_value = k_mapping.get(class_name, 1.0)
            k_array[land_use['classification'] == class_id] = k_value

        return k_array

    def _ee_to_gdf(self, ee_feature) -> gpd.GeoDataFrame:
        """Convert Earth Engine feature to GeoDataFrame."""
        import json
        # Get geometry
        feature_json = ee_feature.getInfo()
        geometry = feature_json['geometry']

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features([feature_json])
        return gdf

    def _classify_image(self, image, classifier, geometry):
        """Train and apply the Earth Engine Random Forest classifier."""
        # Sentinel-2 bands used for land-use classification
        bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']
        image = image.select(bands)

        # WorldCover 2021 reference labels
        worldcover = ee.Image(
            "ESA/WorldCover/v200/2021"
        ).select('Map')

        # Convert WorldCover classes to SPAGeo's seven land-use classes:
        # 80 -> 1 water
        # 90 -> 2 wetland
        # 10 -> 3 forest
        # 40 -> 4 agriculture
        # 50 -> 5 urban
        # 60 -> 6 barren
        # 30 -> 7 grassland
        class_values = [80, 90, 10, 40, 50, 60, 30]
        spageo_classes = [1, 2, 3, 4, 5, 6, 7]

        labels = worldcover.remap(
            class_values,
            spageo_classes,
            0
        ).rename('class')

        # Keep only the seven required SPAGeo classes
        labels = labels.updateMask(labels.gt(0))

        # Combine Sentinel-2 spectral bands with reference labels
        training_image = image.addBands(labels)

        # Generate balanced training samples
        samples = training_image.stratifiedSample(
            numPoints=200,
            classBand='class',
            region=geometry,
            scale=10,
            seed=42,
            geometries=False,
            tileScale=4
        )

        # Train the supplied Random Forest classifier
        trained_classifier = classifier.train(
            features=samples,
            classProperty='class',
            inputProperties=image.bandNames()
        )

        # Apply the trained classifier
        classified = image.classify(trained_classifier)

        return classified

    def _parse_land_use(self, ee_result, geometry):
        """Parse Earth Engine classification result into NumPy land-use data."""

        import os
        import tempfile
        import urllib.request

        # SPAGeo land-use class mapping
        class_mapping = {
            'water': 1,
            'wetland': 2,
            'forest': 3,
            'agriculture': 4,
            'urban': 5,
            'barren': 6,
            'grassland': 7
        }

        # Convert the native classification to a 100 m majority-class raster.
        classified_100m = (
            ee_result
            .reduceResolution(
                reducer=ee.Reducer.mode(),
                maxPixels=100
            )
            .reproject(
                crs=ee_result.projection().crs(),
                scale=100
            )
        )

        # Download the 100 m classification for NumPy/Rasterio processing.
        with tempfile.TemporaryDirectory() as temp_dir:

            output_path = os.path.join(
                temp_dir,
                "spageo_land_use_100m.tif"
            )

            download_url = classified_100m.getDownloadURL({
                'region': geometry.bounds(),
                'scale': 100,
                'format': 'GEO_TIFF'
            })

            urllib.request.urlretrieve(
                download_url,
                output_path
            )

            # Read the downloaded classification raster.
            with rasterio.open(output_path) as src:
                classification = src.read(1)

        # Validate the classification values.
        valid_classes = set(class_mapping.values())

        unique_classes = set(np.unique(classification))

        unexpected_classes = (
                unique_classes - valid_classes
        )

        if unexpected_classes:
            raise ValueError(
                f"Unexpected land-use class values found: "
                f"{sorted(unexpected_classes)}"
            )

        # Calculate class areas using Earth Engine pixel area.
        area_image = (
            ee.Image.pixelArea()
            .rename('area')
            .addBands(
                classified_100m.rename('classification')
            )
        )

        grouped = (
            area_image
            .reduceRegion(
                reducer=ee.Reducer.sum().group(
                    groupField=1,
                    groupName='classification'
                ),
                geometry=geometry,
                scale=100,
                maxPixels=1e9,
                tileScale=4
            )
            .get('groups')
            .getInfo()
        )

        # Initialize all seven classes with zero area.
        areas = {
            class_name: 0.0
            for class_name in class_mapping
        }

        # Convert Earth Engine class IDs back to SPAGeo names.
        id_to_name = {
            class_id: class_name
            for class_name, class_id in class_mapping.items()
        }

        for group in grouped or []:
            class_id = int(group['classification'])
            area_m2 = float(group['sum'])

            class_name = id_to_name.get(class_id)

            if class_name is not None:
                areas[class_name] = area_m2

        return {
            'shape': classification.shape,
            'classes': class_mapping,
            'classification': classification,
            'areas': areas
        }