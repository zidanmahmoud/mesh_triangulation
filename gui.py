import sys
import numpy as np
from PyQt5 import QtGui, QtWidgets, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from delauny_mesh import triangulate

class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.grid()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.cid = self.canvas.mpl_connect("button_press_event", self._on_press)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.button = QtWidgets.QPushButton('Triangulate')
        self.button.clicked.connect(self._triangulate_and_plot)

        self.coords_button = QtWidgets.QPushButton('Enter a new point')
        self.coords_button.clicked.connect(self._show_point_coords_dialog)

        self.triangulated = False
        self.tripoints = None
        self.triindices = None

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.coords_button)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.points = list()


    def _on_press(self, event):
        if not event.inaxes: return
        x, y = event.xdata, event.ydata
        if not event.dblclick and event.button == 1:
            self.points.append([x, y])
            self._replot()


    def _replot(self):
        # Clear the plot
        self.ax.clear()
        self.ax.grid()

        # Plot the selected points
        p = np.array(self.points)
        self.ax.scatter(p[:, 0], p[:, 1], color="red")
        for i, point in enumerate(self.points):
            self.ax.annotate(str(i), point)
        
        # Plot the triangulation
        if self.triangulated:
            self.ax.triplot(self.tripoints[:, 0], self.tripoints[:, 1], self.triindices)

        self.canvas.draw()


    def _show_point_coords_dialog(self):
        self.dialog = QtWidgets.QDialog(self, QtCore.Qt.Tool |
                                         QtCore.Qt.WindowMaximizeButtonHint |
                                         QtCore.Qt.WindowCloseButtonHint)
        self.dialog.setWindowTitle("Point Coordinates")
        self.dialog.setModal(True)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.dialog.setLayout(layout)

        self.x_option = Option(0)
        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row_layout)
        layout.addWidget(row_widget)
        prefix_widget = QtWidgets.QLabel("x coordinate")
        row_layout.addWidget(prefix_widget)
        x_spinbox = QtWidgets.QDoubleSpinBox()
        x_spinbox.setValue(0)
        x_spinbox.setKeyboardTracking(False)
        row_layout.addWidget(x_spinbox, 1)
        self.x_option.connect(x_spinbox.setValue)
        x_spinbox.valueChanged.connect(self.x_option.change)

        self.y_option = Option(0)
        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row_layout)
        layout.addWidget(row_widget)
        prefix_widget = QtWidgets.QLabel("y coordinate")
        row_layout.addWidget(prefix_widget)
        y_spinbox = QtWidgets.QDoubleSpinBox()
        y_spinbox.setValue(0)
        y_spinbox.setKeyboardTracking(False)
        row_layout.addWidget(y_spinbox, 1)
        self.y_option.connect(y_spinbox.setValue)
        y_spinbox.valueChanged.connect(self.y_option.change)

        ok_button = QtWidgets.QPushButton("Ok")
        ok_button.clicked.connect(self._add_point)
        layout.addWidget(ok_button)

        self.dialog.exec_()

    def _add_point(self):
        point = [self.x_option.value, self.y_option.value]
        self.points.append(point)
        self._replot()
        self.dialog.close()

    def _triangulate_and_plot(self):
        if len(self.points) < 3:
            QtWidgets.QMessageBox.critical(self, "Error", "Enter more points")
            return
        self.canvas.mpl_disconnect(self.cid)
        self.tripoints, self.triindices = triangulate(self.points, 0.1)
        self.triangulated = True
        self._replot()



class Option(QtCore.QObject):
    _changed = QtCore.pyqtSignal(object)

    def __init__(self, value, action=None):
        super(Option, self).__init__()
        self.value = value

        if action:
            self.connect(action)

    def connect(self, action):
        self._changed.connect(action)

    def change(self, value):
        self.value = value

    def __call__(self):
        return self.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.emit()

    def emit(self):
        self._changed.emit(self._value)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())