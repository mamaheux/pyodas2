from typing import List, Dict

import numpy as np

import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore

from pyodas2.signals import Doas


AXIS_SIZE = 1.5
SPHERE_RADIUS = 1.0


class SourceLocationWidget(gl.GLViewWidget):
    """
    A PyQtGraph widget to display active source location in 3D.
    """
    def __init__(self, parent=None):
        """
        Create a new SourceLocationWidget.
        :param parent: The parent widget
        """
        super().__init__(parent)
        self.resize(600,600)
        self.setWindowTitle('Source Locations')
        self.setCameraPosition(distance=4)

        self._add_axis_item()
        self._add_xy_plan_item()
        self._add_sphere_item()
        self._add_potential_source_item()
        self._add_tracked_source_item()

    def _add_axis_item(self):
        axis_item = gl.GLAxisItem()
        axis_item.setSize(AXIS_SIZE, AXIS_SIZE, AXIS_SIZE)
        self.addItem(axis_item)

        self.addItem(gl.GLTextItem(pos=(AXIS_SIZE, 0.0, 0.0), text='X', color=(0, 255, 0, 255)))
        self.addItem(gl.GLTextItem(pos=(0.0, AXIS_SIZE, 0.0), text='Y', color=(255, 255, 0, 255)))
        self.addItem(gl.GLTextItem(pos=(0.0, 0.0, AXIS_SIZE), text='Z', color=(0, 0, 255, 255)))

    def _add_xy_plan_item(self):
        verts = np.array([
            [-1, -1, -0.01],
            [-1, 1, -0.01],
            [1, 1, -0.01],
            [1, -1, -0.01],
        ])
        faces = np.array([
            [0, 1, 2],
            [0, 2, 3],
        ])
        colors = np.array([
            [0, 0.5, 0, 0.5],
            [0, 0.5, 0, 0.5],
            [0, 0.5, 0, 0.5],
            [1, 0.5, 0, 0.5]
        ])

        xy_plan_item = gl.GLMeshItem(vertexes=verts, faces=faces, faceColors=colors, smooth=False)
        self.addItem(xy_plan_item)

    def _add_sphere_item(self):
        sphere_data = gl.MeshData.sphere(rows=10, cols=10, radius=1)
        sphere_item = gl.GLMeshItem(
            meshdata=sphere_data,
            drawEdges=True,
            drawFaces=False,
            color=(1, 0, 0, 0)
        )
        self.addItem(sphere_item)

    def _add_potential_source_item(self):
        self._potential_source_item = gl.GLScatterPlotItem()
        self.addItem(self._potential_source_item)

    def _add_tracked_source_item(self):
        self._tracked_source_item = gl.GLScatterPlotItem()
        self.addItem(self._tracked_source_item)

    def set_potential_sources(self, directions: List[Doas.Dir]):
        """
        Update the potential sources.

        :param directions: The potential sources directions
        :return:
        """
        direction_array = np.empty((len(directions), 3))
        for i, d in enumerate(directions):
            direction_array[i, 0] = d.coord.x
            direction_array[i, 1] = d.coord.y
            direction_array[i, 2] = d.coord.z

        self._potential_source_item.setData(pos=direction_array, color=(0, 0, 1, 1), size=5)

    def set_tracked_sources(self, tracked_directions_by_index: Dict[int, Doas.Dir]):
        """
        Update the tracked sources.
        :param tracked_directions_by_index: The tracked sources directions.
        :return:
        """
        direction_array = np.empty((len(tracked_directions_by_index), 3))
        for i, d in enumerate(tracked_directions_by_index.values()):
            direction_array[i, 0] = d.coord.x
            direction_array[i, 1] = d.coord.y
            direction_array[i, 2] = d.coord.z

        def set_data():
            self._tracked_source_item.setData(pos=direction_array, color=(1, 0, 0, 1), size=10)

        QtCore.QTimer.singleShot(0, self, set_data)
