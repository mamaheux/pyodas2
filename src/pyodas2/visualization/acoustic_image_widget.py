import cv2
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

DEFAULT_COLOR_MAP = 'Jet'
COLOR_MAPS = {
    'Autumn': cv2.COLORMAP_AUTUMN,
    'Bone': cv2.COLORMAP_BONE,
    'Jet': cv2.COLORMAP_JET,
    'Winter': cv2.COLORMAP_WINTER,
    'Rainbow': cv2.COLORMAP_RAINBOW,
    'Ocean': cv2.COLORMAP_OCEAN,
    'Summer': cv2.COLORMAP_SUMMER,
    'Spring': cv2.COLORMAP_SPRING,
    'Cool': cv2.COLORMAP_COOL,
    'HSV': cv2.COLORMAP_HSV,
    'Pink': cv2.COLORMAP_HOT,
    'Parula': cv2.COLORMAP_PARULA,
    'Magma': cv2.COLORMAP_MAGMA,
    'Inferno': cv2.COLORMAP_INFERNO,
    'Plasma': cv2.COLORMAP_PLASMA,
    'Viridis': cv2.COLORMAP_VIRIDIS,
    'Cividis': cv2.COLORMAP_CIVIDIS,
    'Twilight': cv2.COLORMAP_TWILIGHT,
    'Swilight Shifted': cv2.COLORMAP_TWILIGHT_SHIFTED,
    'Turbo': cv2.COLORMAP_TURBO,
    'Deepgreen': cv2.COLORMAP_DEEPGREEN,
}


class AcousticImageWidget(QtWidgets.QWidget):
    """
    A widget to display an acoustic image.
    """

    def __init__(self, hflip: bool = True, parent=None) -> None:
        """
        Creates a new AcousticImageWidget.

        :param hflip: If True, the image is flipped horizontally.
        :param parent: The parent widget
        """
        super().__init__(parent)

        self._hflip = hflip

        self._graphic_layout_widget = pg.GraphicsLayoutWidget()
        self._image_plot = self._graphic_layout_widget.addPlot()
        self._image_item = pg.ImageItem(axisOrder='row-major')
        self._image_plot.addItem(self._image_item)
        self._image_plot.hideAxis('left')
        self._image_plot.hideAxis('bottom')
        self._image_plot.setAspectLocked(True)
        self._image_plot.invertY()

        self._alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._alpha_slider.setRange(0, 100)
        self._alpha_slider.setValue(50)

        self._color_map_combo_box = QtWidgets.QComboBox()
        self._color_map_combo_box.addItems(list(COLOR_MAPS.keys()))
        self._color_map_combo_box.setCurrentText(DEFAULT_COLOR_MAP)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._graphic_layout_widget)
        layout.addWidget(QtWidgets.QLabel('Alpha'))
        layout.addWidget(self._alpha_slider)
        layout.addWidget(QtWidgets.QLabel('Color Map'))
        layout.addWidget(self._color_map_combo_box)
        self.setLayout(layout)

    def set_images(self, rgb_image: np.typing.NDArray[np.uint8], acoustic_image: np.typing.NDArray[np.uint8]) -> None:
        """
        Updates the displayed camera image

        :param rgb_image: A RGB image.
        :param acoustic_image: An acoustic image.
        """

        def update():
            alpha = self._alpha_slider.value() / 100
            beta = 1 - alpha

            color_map = COLOR_MAPS[self._color_map_combo_box.currentText()]
            mapped_acoustic_image = cv2.applyColorMap(acoustic_image, color_map)
            mapped_acoustic_image = cv2.cvtColor(mapped_acoustic_image, cv2.COLOR_BGR2RGB)
            mixed_image = cv2.addWeighted(rgb_image, beta, mapped_acoustic_image, alpha, 0.0)

            if self._hflip:
                mixed_image = cv2.flip(mixed_image, 1)
            self._image_item.setImage(mixed_image)

        QtCore.QTimer.singleShot(0, self, update)
