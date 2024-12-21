import time

from typing import List, Dict, Iterable

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from pyodas2.signals import Doas


FRAME_RATE = 30


class ElevationAzimuthWidget(pg.GraphicsLayoutWidget):
    """
    A PyQtGraph widget to display the elevation and azimuth of sources over time.
    """
    def __init__(self,
                 sample_rate: float = 16000,
                 hop_length: int = 128,
                 history_duration_s: float = 5,
                 parent=None):
        """
        Creates a new ElevationAzimuthWidget.
        :param sample_rate: The sample rate of the sound.
        :param hop_length: The number of samples in each processed audio frame, also named num_shifts.
        :param history_duration_s: The duration of the history in seconds
        :param parent:
        """
        super().__init__(parent)
        self.setWindowTitle("Source Elevation and Azimuth")
        self.resize(1000, 600)

        self._add_source_elevation_plot(history_duration_s)
        self._add_source_azimuth_plot(history_duration_s)

        self._max_point_count = int((history_duration_s * sample_rate) / hop_length)
        self._times = -np.array([i * history_duration_s / self._max_point_count for i in reversed(range(self._max_point_count))])

        self._elevation_potential_sources = [[] for _ in range(self._max_point_count)]
        self._elevation_tracked_sources = [[] for _ in range(self._max_point_count)]
        self._azimuth_potential_sources = [[] for _ in range(self._max_point_count)]
        self._azimuth_tracked_sources = [[] for _ in range(self._max_point_count)]

        self._last_potential_source_update_time = time.time()
        self._last_tracked_source_update_time = time.time()

    def _add_source_elevation_plot(self, history_duration_s):
        self._source_elevation_plot = self.addPlot(title='Source Elevation', row=0, col=0)
        self._source_elevation_plot.setLabel('left', 'Elevation', units='°')
        self._source_elevation_plot.setLabel('bottom', 'Time', units='s')
        self._source_elevation_plot.addLegend()
        self._source_elevation_plot.setXRange(-history_duration_s, 0, padding=0)
        self._source_elevation_plot.setYRange(-180, 180, padding=0)

        self._elevation_potential_source_item = pg.ScatterPlotItem()
        self._source_elevation_plot.addItem(self._elevation_potential_source_item)

        self._elevation_tracked_source_item = pg.ScatterPlotItem()
        self._source_elevation_plot.addItem(self._elevation_tracked_source_item)

    def _add_source_azimuth_plot(self, history_duration_s):
        self._source_azimuth_plot = self.addPlot(title='Source Azimuth', row=1, col=0)
        self._source_azimuth_plot.setLabel('left', 'Azimuth', units='°')
        self._source_azimuth_plot.setLabel('bottom', 'Time', units='s')
        self._source_azimuth_plot.addLegend()
        self._source_azimuth_plot.setXRange(-history_duration_s, 0, padding=0)
        self._source_azimuth_plot.setYRange(-180, 180, padding=0)

        self._azimuth_potential_source_item = pg.ScatterPlotItem()
        self._source_azimuth_plot.addItem(self._azimuth_potential_source_item)

        self._azimuth_tracked_source_item = pg.ScatterPlotItem()
        self._source_azimuth_plot.addItem(self._azimuth_tracked_source_item)

    def add_potential_sources(self, directions: List[Doas.Dir]):
        """
        Add the potential sources.

        :param directions: The potential sources directions
        :return:
        """
        elevations, azimuths = self._directions_to_elevation_azimuth(directions)

        def update():
            self._elevation_potential_sources.append(elevations)
            self._elevation_potential_sources.pop(0)

            self._azimuth_potential_sources.append(azimuths)
            self._azimuth_potential_sources.pop(0)

            self._update_potential_sources()

        QtCore.QTimer.singleShot(0, self, update)

    def _update_potential_sources(self):
        c = sum(map(lambda x: len(x), self._elevation_potential_sources))
        all_elevations = np.zeros((c, 2))
        all_azimuths = np.zeros((c, 2))

        i = 0
        for t in range(self._max_point_count):
            c = len(self._elevation_potential_sources[t])

            all_elevations[i:i+c, 0] = self._times[t]
            all_elevations[i:i+c, 1] = self._elevation_potential_sources[t]
            all_azimuths[i:i+c, 0] = self._times[t]
            all_azimuths[i:i+c, 1] = self._azimuth_potential_sources[t]

            i += c

        if (time.time() - self._last_potential_source_update_time) > 1 / FRAME_RATE:
            self._elevation_potential_source_item.setData(all_elevations[:, 0], all_elevations[:, 1], pen=(0, 0, 255), name='Potential Sources')
            self._azimuth_potential_source_item.setData(all_azimuths[:, 0], all_azimuths[:, 1], pen=(0, 0, 255), name='Potential Sources')
            self._last_potential_source_update_time = time.time()

    def add_tracked_sources(self, tracked_directions_by_index: Dict[int, Doas.Dir]):
        """
        Add the tracked sources.
        :param tracked_directions_by_index: The tracked sources directions.
        :return:
        """
        elevations, azimuths = self._directions_to_elevation_azimuth(tracked_directions_by_index.values())

        def update():
            self._elevation_tracked_sources.append(elevations)
            self._elevation_tracked_sources.pop(0)
            self._azimuth_tracked_sources.append(azimuths)
            self._azimuth_tracked_sources.pop(0)

            self._update_tracked_sources()

        QtCore.QTimer.singleShot(0, self, update)

    def _update_tracked_sources(self):
        c = sum(map(lambda x: len(x), self._elevation_tracked_sources))
        all_elevations = np.zeros((c, 2))
        all_azimuths = np.zeros((c, 2))

        i = 0
        for t in range(self._max_point_count):
            c = len(self._elevation_tracked_sources[t])

            all_elevations[i:i+c, 0] = self._times[t]
            all_elevations[i:i+c, 1] = self._elevation_tracked_sources[t]
            all_azimuths[i:i+c, 0] = self._times[t]
            all_azimuths[i:i+c, 1] = self._azimuth_tracked_sources[t]

            i += c

        if (time.time() - self._last_tracked_source_update_time) > 1 / FRAME_RATE:
            self._elevation_tracked_source_item.setData(all_elevations[:, 0], all_elevations[:, 1], pen=(255, 0, 0), name='Tracked Sources')
            self._azimuth_tracked_source_item.setData(all_azimuths[:, 0], all_azimuths[:, 1], pen=(255, 0, 0), name='Tracked Sources')
            self._last_tracked_source_update_time = time.time()

    def _directions_to_elevation_azimuth(self, directions: Iterable[Doas.Dir]):
        directions = list(directions)

        x = np.zeros(len(directions))
        y = np.zeros(len(directions))
        z = np.zeros(len(directions))

        for i, d in enumerate(directions):
            x[i] = d.coord.x
            y[i] = d.coord.y
            z[i] = d.coord.z

        hxy = np.hypot(x, y)
        elevations = np.rad2deg(np.arctan2(z, hxy))
        azimuth = np.rad2deg(np.arctan2(y, x))

        return elevations, azimuth
