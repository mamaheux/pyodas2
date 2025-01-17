import cv2
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets


class AcousticImageCalibrationWidget(QtWidgets.QWidget):
    """
    A widget to perform acoustic image calibration.
    """
    def __init__(self, point_radius: int = 8, hflip: bool = True, parent=None) -> None:
        """
        Creates a new AcousticImageWidget.
        :param point_radius: The point radius.
        :param hflip: TODO.
        :param parent: The parent widget
        """
        super().__init__(parent)

        self._point_radius = point_radius
        self._hflip = hflip

        self._graphic_layout_widget = pg.GraphicsLayoutWidget()
        self._image_plot = self._graphic_layout_widget.addPlot()
        self._image_item = pg.ImageItem(axisOrder='row-major')
        self._image_plot.addItem(self._image_item)
        self._image_plot.hideAxis('left')
        self._image_plot.hideAxis('bottom')
        self._image_plot.setAspectLocked(True)
        self._image_plot.invertY()

        self._record_button = QtWidgets.QPushButton("Record")
        self._record_button.setMinimumHeight(100)
        self._record_button.clicked.connect(self._record_button_clicked)

        self._progress_dialog = None

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._graphic_layout_widget)
        layout.addWidget(self._record_button)
        self.setLayout(layout)

        self._targets = np.empty((0, 2))
        self._current_target_index = None

        self._record_requested = False


    def _record_button_clicked(self):
        self._record_requested = True

    @property
    def record_requested(self):
        if self._record_requested:
            self._record_requested = False
            return True
        return False

    def set_camera_image(self, image: np.typing.NDArray[np.uint8]) -> None:
        """
        Updates the displayed camera image
        :param image: A RGB image.
        """
        def update():
            image_with_targets = image.copy()

            for i, point in enumerate(self._targets):
                cv2.circle(image_with_targets, (point[0], point[1]), self._point_radius, (255, 0, 0), -1)
                if i == self._current_target_index:
                    cv2.circle(image_with_targets, (point[0], point[1]), self._point_radius * 2, (0, 255, 0), self._point_radius // 4)

            if self._hflip:
                image_with_targets = cv2.flip(image_with_targets, 1)
            self._image_item.setImage(image_with_targets)

        QtCore.QTimer.singleShot(0, self, update)

    def set_targets(self, targets: np.typing.NDArray[int], current_target_index: int) -> None:
        """
        Updates the targets.
        :param targets: The targets of shape (target count, 2)
        :param current_target_index: The current target index
        """
        def update():
            self._targets = targets
            self._current_target_index = current_target_index

        QtCore.QTimer.singleShot(0, self, update)

    def show_progress_dialog(self) -> None:
        """
        Display a progress dialog
        """
        def update():
            flags = QtCore.Qt.WindowType.Dialog | QtCore.Qt.WindowType.CustomizeWindowHint | QtCore.Qt.WindowType.WindowTitleHint
            self._progress_dialog = QtWidgets.QProgressDialog('Calibrating...', None, 0, 0, self, flags)
            self._progress_dialog.findChild(QtWidgets.QProgressBar).setFormat('%p% (%v/%m)')
            self._progress_dialog.setModal(True)
            self._progress_dialog.show()

        QtCore.QTimer.singleShot(0, self, update)

    def update_process_dialog(self, value: int, maximum: int):
        """
        Update the progress dialog values
        :param value: The current value.
        :param maximum: The maximum value.
        :return:
        """
        def update():
            if self._progress_dialog is not None:
                self._progress_dialog.setMinimum(0)
                self._progress_dialog.setMaximum(maximum)
                self._progress_dialog.setValue(value)

        QtCore.QTimer.singleShot(0, self, update)
