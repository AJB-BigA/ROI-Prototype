
from PySide6.QtWidgets import QToolBar, QColorDialog
from PySide6.QtGui import QAction

class CutsomToolbar(QToolBar):
    """Class to hold the draw ROI features"""
    def __init__(self, parent=None, pen = None):
        super().__init__("Toolbar", parent)
        self.parent = parent
        
        self.pen = pen 
        colourAction = QAction("Choose Colour",self)
        colourAction.triggered.connect(self.change_colour)
        self.addAction(colourAction)
        
    def change_colour(self):
        """Allows us to change the colour of the pen"""
        dialog = QColorDialog()
        on_clicked_ok = dialog.exec()
        if on_clicked_ok:
            self.pen.setColor(dialog.currentColor())