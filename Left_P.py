from PySide6 import QtWidgets
from PySide6.QtWidgets import QGroupBox, QGridLayout, QPushButton

class LeftPannel(QtWidgets.QWidget):
    def __init__(self, parent = None, pen = None):
        super().__init__(parent)
        self.parent = parent
        self.pen = pen

        self.set_layout()

    def set_layout(self):
        """Fucntion to set the buttons layout"""

        #Initalises the buttons
        self._grid_group_box = QGroupBox("Tools")
        layout = QGridLayout()
        brush = QPushButton("Brush")
        pen = QPushButton("Pen")
        eraser_roi = QPushButton("Eraser ROI")
        eraser_draw = QPushButton("Eraser Draw")
        smooth = QPushButton("Smooth")
        transect = QPushButton("Transect")
        copy = QPushButton("Copy ROI")
        save = QPushButton("Save")

        #Links the buttons to actions 
        brush.clicked.connect(self.brush_tool)
        pen.clicked.connect(self.pen_tool)
        eraser_roi.clicked.connect(self.eraser_roi_tool)
        eraser_draw.clicked.connect(self.eraser_draw_tool)
        smooth.clicked.connect(self.smooth_tool)
        transect.clicked.connect(self.transect_tool)
        copy.clicked.connect(self.copy_button)
        save.clicked.connect(self.save_button)

        #Sets the buttons in the layout 2 by 3
        layout.addWidget(brush,0,0)
        layout.addWidget(pen, 0,1)
        layout.addWidget(eraser_roi,1,0)
        layout.addWidget(eraser_draw,1,1)
        layout.addWidget(smooth,2,0)
        layout.addWidget(transect,2,1)
        layout.addWidget(copy,3,0)
        layout.addWidget(save,3,1)

        #adds the layout to the grid_group_box
        #Bundles everything up yay!
        self._grid_group_box.setLayout(layout)
        main_layout = QtWidgets.QVBoxLayout()  # Create main layout for the left panel
        main_layout.addWidget(self._grid_group_box)  # Add the group box to the main layout
        self.setLayout(main_layout)  # Set th

    def brush_tool(self):
        """This fucntion changes the draw tool to a brush"""
        print("Now a brush")

    def pen_tool(self):
        """This fucntion changes the draw tool to a pen"""
        print("Now a pen")

    def eraser_roi_tool(self):
        """This fucntion changes the draw tool to the eraser ROI tool"""
        print("Now a Eraser ROI")

    def eraser_draw_tool(self):
        """This fucntion changes the draw tool to a eraser draw tool"""
        print("Now a Eraser Draw")
    

    def smooth_tool(self):
        """This fucntion changes the draw tool to a smooth tool"""
        print("Now a SMooth tool")
    
    def transect_tool(self):
        """This fucntion changes the draw tool to a smooth tool"""
        print("Now a transect tool")
    
    def copy_button(self):
        """This fucntion changes the draw tool to a smooth tool"""
        print("Now a copy tool")

    def save_button(self):
        """This fucntion saves the ROI drawing"""
        print("SAVED!!!!")