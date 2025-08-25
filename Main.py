import sys
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtGui import QPen, QKeyEvent
from PySide6.QtCore import Qt
from Toolbar import CutsomToolbar
from Left_P import LeftPannel
from Canvas import CanvasLabel
from Units_Box import UnitsBox
from dicom_scroll_loader import ScrollLoaderUI
from scroll_loader_4_dicom_image import Scroll_Wheel


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

        # Initalises the calsses
        

        self.dicom_data = ScrollLoaderUI(directory_in_string)
        self.scroll_wheel = Scroll_Wheel(self.dicom_data)
        self.canvas_labal = CanvasLabel(self.pen, self.dicom_data,self.scroll_wheel)
        self.units_box = UnitsBox(self, self.pen, self.canvas_labal)
        self.left_label = LeftPannel(self, self.pen, self.canvas_labal,self.scroll_wheel)
        toolbar = CutsomToolbar(self,self.canvas_labal,self.left_label, self.scroll_wheel, self.dicom_data)
        
       #Connecting slots & signals
        self.dicom_data.f_value.connect(self.canvas_labal.change_layout_bool)
        self.scroll_wheel.slider_value.connect(self.canvas_labal.update_pixmap_layer)



        #Drawing Widget 
        drawing_widget = QtWidgets.QWidget()
        drawing_widget.setFixedSize(512,512)

        self.dicom_data.setParent(drawing_widget)
        self.dicom_data.setGeometry(0,0,512,512)
        
        self.canvas_labal.setParent(drawing_widget)
        self.canvas_labal.setGeometry(0,0,512,512)
        self.canvas_labal.raise_()

        img_label = self.dicom_data.image_label
        img_label.setScaledContents(False)
        img_label.setAlignment(Qt.AlignCenter)

        if self.dicom_data.layout():
            self.dicom_data.layout().setContentsMargins(0, 0, 0, 0)
            self.dicom_data.layout().setSpacing(0)

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
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Up:
            self.scroll_wheel.setValue(self.scroll_wheel.value() +1)
            self.canvas_labal.ds_is_active = False
        if event.key() == Qt.Key_Down:
            self.scroll_wheel.setValue(self.scroll_wheel.value() -1)
            self.canvas_labal.ds_is_active = False
        return super().keyPressEvent(event)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = ROI_Drawing()
    widget.show()
    sys.exit(app.exec())

