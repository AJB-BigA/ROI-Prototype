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
from Units_Box import UnitsBox
from dicom_scroll_loader import ScrollLoaderUI
from scroll_loader_4_dicom_image import Scroll_Wheel
import os


#Sourcery.ai Is this true
class ROI_Drawing(QtWidgets.QMainWindow):
    """Class to hold the draw ROI features"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI Prototype")

        # Temporary hard coded directory path
        directory_in_string = self.choose_file()

        self.last_point = None

        # Initialize the pen
        self.pen = QPen()
        self.pen.setWidth(6)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setColor("blue")

        self.canvas_labal = CanvasLabel(self.pen)

        # Initalises the calsses

        self.units_box = UnitsBox(self, self.pen, self.canvas_labal)

        self.dicom_data = ScrollLoaderUI(directory_in_string)

        self.scroll_wheel = Scroll_Wheel(self.dicom_data)

        self.left_label = LeftPannel(self, self.pen, self.canvas_labal,self.scroll_wheel)

        toolbar = CutsomToolbar(self,self.canvas_labal,self.left_label, self.scroll_wheel, self.dicom_data)

       

        #Drawing Widget 
        drawing_widget = QtWidgets.QWidget()
        drawing_widget.setFixedSize(512,512)

        self.dicom_data.setParent(drawing_widget)
        self.dicom_data.setGeometry(0,0,512,512)
        
        self.canvas_labal.setParent(drawing_widget)
        self.canvas_labal.setGeometry(0,0,512,512)
        self.canvas_labal.raise_()

        # Creates a layout for the tools to fit inside
        tools_layout = QtWidgets.QVBoxLayout()
        tools_container = QtWidgets.QWidget()
        tools_container.setLayout(tools_layout)
        tools_layout.addWidget(self.left_label)
        tools_layout.addWidget(self.units_box)

        # Create a layout to hold the left panel and the main canvas
        main_layout = QtWidgets.QHBoxLayout()

        # Create a QWidget to hold both the left panel and the central label
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)


        # Add the left panel to the layout
        main_layout.addWidget(tools_container)

        main_layout.addWidget(self.scroll_wheel)
        
        # Add the canvas label to the layout
        main_layout.addWidget(drawing_widget)

        # Set the central widget to be our layout container
        self.setCentralWidget(central_widget)

        # Add the toolbar
        self.addToolBar(toolbar)

    def choose_file(self) -> str: 
        file_path = QtWidgets.QFileDialog.getExistingDirectory(self,"Select a file","",QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
        return file_path

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = ROI_Drawing()
    widget.show()
    sys.exit(app.exec())

