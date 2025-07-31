
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

        #Undo feature 
        undo_button = QAction("Undo", self)
        undo_button.triggered.connect(self.undo_button)
        self.addAction(undo_button)

        redo_button = QAction("Redo", self)
        redo_button.triggered.connect(self.redo_button)
        self.addAction(redo_button)


        
    def change_colour(self):
        """Allows us to change the colour of the pen"""
        dialog = QColorDialog()
        on_clicked_ok = dialog.exec()
        if on_clicked_ok:
            colour = dialog.currentColor()
            colour.setAlpha(self.canvas_label.max_alpha)
            self.canvas_label.pen.setColor(colour)
            self.left_label.last_colour = dialog.currentColor()
    
    def undo_button(self):
        """Calls the undo method"""
        self.canvas_label.undo_draw()

    def redo_button(self):
        """Calls the redo fucntion"""
        self.canvas_label.redo_draw()