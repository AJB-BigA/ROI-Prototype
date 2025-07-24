import sys
import pydicom
import logging
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QPixmap, QPainter, QPen, QColor, QAction, QBrush
from PySide6.QtCore import QTimer, Qt
from Toolbar import CutsomToolbar
from Left_P import LeftPannel
from Canvas import CanvasLabel

#Sourcery.ai Is this true
class ROI_Drawing(QtWidgets.QMainWindow):
    """Class to hold the draw ROI features"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI Prototype")

        self.last_point = None

        # Initialize the pen
        self.pen = QPen()
        self.pen.setWidth(6)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setColor("blue")

        self.canvas_labal = CanvasLabel(self.pen)

        # Create the left label (panel)
        self.left_label = LeftPannel(self, self.pen, self.canvas_labal)

        # Set up the central widget
        self.setCentralWidget(self.canvas_labal)

        # Create a layout to hold the left panel and the main canvas
        main_layout = QtWidgets.QHBoxLayout()

        # Create a QWidget to hold both the left panel and the central label
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)

        # Add the left panel to the layout
        main_layout.addWidget(self.left_label)

        # Add the canvas (label) to the layout
        main_layout.addWidget(self.canvas_labal)

        # Set the central widget to be our layout container
        self.setCentralWidget(central_widget)

        # Create and add the toolbar
        toolbar = CutsomToolbar(self,self.canvas_labal,self.left_label)
        self.addToolBar(toolbar)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = ROI_Drawing()
    widget.show()
    sys.exit(app.exec())

