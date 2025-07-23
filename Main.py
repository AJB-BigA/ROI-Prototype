import sys
import pydicom
import logging
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QPixmap, QPainter, QPen, QColor, QAction, QBrush
from PySide6.QtCore import QTimer, Qt
from Toolbar import CutsomToolbar
from Left_P import LeftPannel

#Sourcery.ai Is this true
class ROI_Drawing(QtWidgets.QMainWindow):
    """Class to hold the draw ROI features"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI Prototype")

        self.last_point = None

        self.label = QtWidgets.QLabel()
        self.canvas = QPixmap(500, 500)

        # Makes the canvas white, needs to be removed when DICOM images are added
        self.canvas.fill(QColor("white"))

        # Initialize the pen
        self.pen = QPen()
        self.pen.setWidth(6)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setColor("blue")

        self.label.setPixmap(self.canvas)

        # Create the left label (panel)
        self.left_label = LeftPannel(self, self.pen)

        # Set up the central widget
        self.setCentralWidget(self.label)

        # Create a layout to hold the left panel and the main canvas
        main_layout = QtWidgets.QHBoxLayout()

        # Create a QWidget to hold both the left panel and the central label
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)

        # Add the left panel to the layout
        main_layout.addWidget(self.left_label)

        # Add the canvas (label) to the layout
        main_layout.addWidget(self.label)

        # Set the central widget to be our layout container
        self.setCentralWidget(central_widget)

        # Create and add the toolbar
        toolbar = CutsomToolbar(self, self.pen)
        self.addToolBar(toolbar)
        







    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Tracks the mouse movement"""
        current_point = event.position().toPoint()

        # Draw on the underlying pixmap
        painter = QPainter(self.canvas)
        painter.setPen(self.pen)
        if self.last_point:
            painter.drawLine(self.last_point.x(), self.last_point.y(), current_point.x(),current_point.y())
        else:
            painter.drawPoint(current_point)

        painter.drawPoint(current_point.x(),current_point.y())
        painter.end()

        self.label.setPixmap(self.canvas)
            
        self.last_point = current_point

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Sets the last point to none"""
        self.last_point = None
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = ROI_Drawing()
    widget.show()
    sys.exit(app.exec())