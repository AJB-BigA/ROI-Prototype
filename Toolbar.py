
from PySide6.QtWidgets import QToolBar, QColorDialog
from PySide6.QtGui import QAction

class CutsomToolbar(QToolBar):
    """Class to hold the draw ROI features"""
    def __init__(self, parent=None, canvas_label = None, left_label = None):
        super().__init__("Toolbar", parent)
        self.parent = parent
        self.canvas_label = canvas_label
        self.left_label = left_label
        colourAction = QAction("Choose Colour",self)
        colourAction.triggered.connect(self.change_colour)
        self.addAction(colourAction)
        
    def change_colour(self):
        """Allows us to change the colour of the pen"""
        dialog = QColorDialog()
        on_clicked_ok = dialog.exec()
        if on_clicked_ok:
            self.canvas_label.pen.setColor(dialog.currentColor())
        self.left_label.last_colour = dialog.currentColor()
        print(self.left_label.last_colour)