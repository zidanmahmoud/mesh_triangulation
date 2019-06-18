"""
GUI
"""
import numpy as np
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from delauny_mesh import triangulate


class Window(QtWidgets.QMainWindow):
    """
    Main Window
    """

    def __init__(self):
        super(Window, self).__init__()

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        menu = self.menuBar()
        menu.addMenu("Help").addAction(
            "To insert a point, either\nclick with left mouse on the\ncanvas or use 'Enter a new point'\n dialog."
        )

        self.dialog = None

        figure = Figure()
        axes = figure.add_subplot(111)
        canvas = FigureCanvasQTAgg(figure)
        toolbar = NavigationToolbar2QT(canvas, self)
        cid = canvas.mpl_connect("button_press_event", self._on_press)
        axes.grid(True)

        tri_button = QtWidgets.QPushButton("Triangulate")
        tri_button.clicked.connect(self.triangulate_and_plot)

        coords_button = QtWidgets.QPushButton("Enter a new point")
        coords_button.clicked.connect(self._show_point_coords_dialog)

        self.mesh_size_spinbox = QtWidgets.QDoubleSpinBox()
        self.mesh_size_spinbox.setDecimals(5)
        self.mesh_size_spinbox.setMinimum(0)
        self.mesh_size_spinbox.setValue(1)

        # set the layout
        main_layout = QtWidgets.QHBoxLayout()

        left_layout = QtWidgets.QVBoxLayout()

        left_layout.addSpacerItem(QtWidgets.QSpacerItem(0, 100))
        left_layout.addWidget(coords_button)
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.addWidget(QtWidgets.QLabel("Mesh Size"))
        row_layout.addWidget(self.mesh_size_spinbox)
        row_widget = QtWidgets.QWidget()
        row_widget.setLayout(row_layout)
        left_layout.addWidget(row_widget)
        left_layout.addWidget(tri_button)
        left_layout.addStretch(1)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(toolbar)
        right_layout.addWidget(canvas)

        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(right_layout)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        central_widget.setLayout(main_layout)

        # set some variables
        self.variables = dict()
        self.variables["canvas"] = canvas
        self.variables["ax"] = axes
        self.variables["cid"] = cid
        self.variables["points"] = list()
        self.variables["triangulated"] = False
        self.variables["tripoints"] = None
        self.variables["triindices"] = None

        self.variables["points"] = list()

    def _on_press(self, event):
        if not event.inaxes:
            return
        x, y = event.xdata, event.ydata
        if not event.dblclick and event.button == 1:
            self.variables["points"].append([x, y])
            self.replot()

    def replot(self):
        """
        refresh the plot
        """
        # Clear the plot
        self.variables["ax"].clear()
        self.variables["ax"].grid()

        # Plot the selected points
        p = np.array(self.variables["points"])
        self.variables["ax"].scatter(p[:, 0], p[:, 1], color="red")
        for i, point in enumerate(self.variables["points"]):
            self.variables["ax"].annotate(str(i), point)

        # Plot the triangulation
        if self.variables["triangulated"]:
            self.variables["ax"].triplot(
                self.variables["tripoints"][:, 0],
                self.variables["tripoints"][:, 1],
                self.variables["triindices"],
            )

        self.variables["canvas"].draw()

    def _show_point_coords_dialog(self):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setWindowTitle("Point Coordinates")
        self.dialog.setModal(True)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.dialog.setLayout(layout)

        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(QtWidgets.QLabel("x coordinate"))
        x_spinbox = QtWidgets.QDoubleSpinBox()
        x_spinbox.setDecimals(5)
        row_layout.addWidget(x_spinbox, 1)

        row_widget = QtWidgets.QWidget()
        row_widget.setLayout(row_layout)
        layout.addWidget(row_widget)

        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(QtWidgets.QLabel("y coordinate"))
        y_spinbox = QtWidgets.QDoubleSpinBox()
        y_spinbox.setDecimals(5)
        row_layout.addWidget(y_spinbox, 1)

        row_widget = QtWidgets.QWidget()
        row_widget.setLayout(row_layout)
        layout.addWidget(row_widget)

        ok_button = QtWidgets.QPushButton("Ok")
        ok_button.clicked.connect(lambda: self.add_point([x_spinbox.value(), y_spinbox.value()]))
        layout.addWidget(ok_button)

        self.dialog.exec_()

    def add_point(self, point):
        """
        add a point and refresh the plot.
        used in the point coords dialog
        """
        self.variables["points"].append(point)
        self.replot()
        # self.dialog.close()

    def triangulate_and_plot(self):
        """
        triangulate the points and refresh the plot
        """
        if len(self.variables["points"]) < 3:
            QtWidgets.QMessageBox.critical(self, "Error", "Enter at least 3 points")
            return
        self.variables["canvas"].mpl_disconnect(self.variables["cid"])
        self.variables["tripoints"], self.variables["triindices"] = triangulate(
            self.variables["points"], self.mesh_size_spinbox.value()
        )
        self.variables["triangulated"] = True
        self.replot()


if __name__ == "__main__":
    APP = QtWidgets.QApplication([])
    APP.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

    MAIN = Window()
    MAIN.show()

    APP.exec_()
