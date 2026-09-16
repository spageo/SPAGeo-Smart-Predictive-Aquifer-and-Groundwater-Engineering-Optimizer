import os
from typing import Dict, List
import numpy as np
from qgis.PyQt.QtGui import QColor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from qgis.core import (
    QgsRasterLayer,
    QgsProject,
    QgsColorRampShader,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer
)
from qgis.PyQt.QtCore import QRectF


class ResultsVisualizer:
    """Visualize groundwater modeling results."""

    def __init__(self, iface):
        """Initialize visualizer."""
        self.iface = iface

    def visualize_heads(self, results: Dict) -> QgsRasterLayer:
        """
        Visualize hydraulic head results.

        Args:
            results: Simulation results dictionary

        Returns:
            QgsRasterLayer: Head raster layer
        """
        if 'heads' not in results:
            raise ValueError("No head data in results")

        head_data = results['heads']

        # Create raster from numpy array
        raster = self._create_raster(
            head_data,
            "SPAGeo_Heads",
            QgsColorRampShader.Interpolated
        )

        # Add to QGIS project
        QgsProject.instance().addMapLayer(raster)

        return raster

    def visualize_contours(self, head_raster, contour_interval: float = 5.0):
        """
        Generate contour lines from a head raster.

        Args:
            head_raster: QgsRasterLayer containing hydraulic head values
            contour_interval: Contour interval in model units

        Returns:
            QgsVectorLayer: Generated contour line layer
        """
        from qgis.core import (
            QgsVectorLayer,
            QgsFeature,
            QgsGeometry,
            QgsPointXY,
            QgsField
        )
        from qgis.PyQt.QtCore import QVariant
        import matplotlib.pyplot as plt

        if head_raster is None or not head_raster.isValid():
            raise ValueError("Invalid head raster")

        if contour_interval <= 0:
            raise ValueError("Contour interval must be greater than zero")

        provider = head_raster.dataProvider()
        block = provider.block(
            1,
            head_raster.extent(),
            head_raster.width(),
            head_raster.height()
        )

        values = np.array(
            [
                [
                    block.value(row, col)
                    for col in range(head_raster.width())
                ]
                for row in range(head_raster.height())
            ],
            dtype=float
        )

        if not np.isfinite(values).any():
            raise ValueError("Head raster contains no finite values")

        minimum = float(np.nanmin(values))
        maximum = float(np.nanmax(values))

        start = np.ceil(minimum / contour_interval) * contour_interval
        stop = np.floor(maximum / contour_interval) * contour_interval

        if start > stop:
            raise ValueError(
                "Contour interval produces no contour levels "
                "within the raster value range"
            )

        levels = np.arange(
            start,
            stop + contour_interval * 0.5,
            contour_interval
        )

        rows, cols = values.shape
        x = np.arange(cols)
        y = np.arange(rows)

        contour_set = plt.contour(
            x,
            y,
            values,
            levels=levels
        )

        layer = QgsVectorLayer(
            "LineString",
            "SPAGeo_Head_Contours",
            "memory"
        )

        if head_raster.crs().isValid():
            layer.setCrs(head_raster.crs())

        layer.dataProvider().addAttributes([
            QgsField("elevation", QVariant.Double)
        ])
        layer.updateFields()

        extent = head_raster.extent()
        x_resolution = extent.width() / cols
        y_resolution = extent.height() / rows

        features = []

        for level, segments in zip(contour_set.levels, contour_set.allsegs):
            for segment in segments:
                if len(segment) < 2:
                    continue

                if np.allclose(segment, segment[0]):
                    continue

                points = []

                for pixel_x, pixel_y in segment:
                    map_x = extent.xMinimum() + (
                            (pixel_x + 0.5) * x_resolution
                    )

                    map_y = extent.yMaximum() - (
                            (pixel_y + 0.5) * y_resolution
                    )

                    points.append(QgsPointXY(map_x, map_y))

                feature = QgsFeature(layer.fields())
                feature.setGeometry(QgsGeometry.fromPolylineXY(points))
                feature["elevation"] = float(level)
                features.append(feature)

        layer.dataProvider().addFeatures(features)
        layer.updateExtents()

        plt.close(contour_set.figure)

        QgsProject.instance().addMapLayer(layer)

        return layer

    def create_animation(self, time_series: List[np.ndarray]) -> str:
        """
        Create animation of transient results.

        Args:
            time_series: List of head arrays for each timestep

        Returns:
            str: Path to generated animation
        """
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        import tempfile

        fig, ax = plt.subplots(figsize=(10, 8))

        def update(frame):
            ax.clear()
            im = ax.imshow(time_series[frame], cmap='viridis')
            ax.set_title(f'Timestep {frame}')
            return im,

        anim = animation.FuncAnimation(
            fig, update, frames=len(time_series), interval=500
        )

        # Save animation
        output_path = os.path.join(tempfile.gettempdir(), 'spageo_animation.gif')
        anim.save(output_path, writer='pillow')

        return output_path

    def _create_raster(self, data: np.ndarray, name: str, shader_type) -> QgsRasterLayer:
        """Create QGIS raster layer from numpy data."""
        import tempfile
        import rasterio
        from rasterio.transform import from_origin

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)

        with rasterio.open(
                temp_file.name,
                'w',
                driver='GTiff',
                height=data.shape[0],
                width=data.shape[1],
                count=1,
                dtype=data.dtype
        ) as dst:
            dst.write(data, 1)

        # Create QGIS layer
        layer = QgsRasterLayer(temp_file.name, name)

        # Apply color ramp
        shader = QgsRasterShader()
        color_ramp = QgsColorRampShader()
        color_ramp.setColorRampType(shader_type)
        color_ramp.setColorRampItemList([
            QgsColorRampShader.ColorRampItem(
                float(np.min(data)), QColor("#0000FF"), "Low"
            ),
            QgsColorRampShader.ColorRampItem(
                float(np.mean(data)), QColor("#00FF00"), "Mean"
            ),
            QgsColorRampShader.ColorRampItem(
                float(np.max(data)), QColor("#FF0000"), "High"
            )
        ])
        shader.setRasterShaderFunction(color_ramp)

        renderer = QgsSingleBandPseudoColorRenderer(
            layer.dataProvider(),
            1,
            shader)
        layer.setRenderer(renderer)

        return layer

    def generate_report(self, results: Dict, model_config: Dict) -> str:
        """
        Generate a comprehensive report of simulation results.

        Args:
            results: Simulation results
            model_config: Model configuration

        Returns:
            str: Report text
        """
        report = f"""
        ========================================
        SPAGeo Simulation Report
        ========================================

        Model: {model_config.get('name', 'SPAGeo Model')}
        Date: {__import__('datetime').datetime.now()}

        --- Grid Configuration ---
        Layers: {model_config.get('grid', {}).get('nlay', 1)}
        Rows: {model_config.get('grid', {}).get('nrow', 10)}
        Columns: {model_config.get('grid', {}).get('ncol', 10)}

        --- Results Summary ---
        Max Head: {np.max(results.get('heads', [[0]])):.2f} m
        Min Head: {np.min(results.get('heads', [[0]])):.2f} m
        Mean Head: {np.mean(results.get('heads', [[0]])):.2f} m

        --- Water Budget ---
        Total Recharge: {results.get('recharge_total', 0):.2f} m³/day
        Total Discharge: {results.get('discharge_total', 0):.2f} m³/day
        Net Change: {results.get('net_change', 0):.2f} m³/day
        """

        return report
