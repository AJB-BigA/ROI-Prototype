
from PySide6.QtWidgets import QToolBar, QColorDialog, QComboBox, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class CutsomToolbar(QToolBar):
    """Class to hold the draw ROI features"""
    def __init__(self, parent=None, canvas_label = None, left_label = None, dicom_scroll_loader = None, dicom_data = None):
        super().__init__("Toolbar", parent)
        self.parent = parent
        
        #Sets communication between classes
        self.canvas_label = canvas_label
        self.left_label = left_label
        self.dicom = dicom_scroll_loader
        self.dicom_data = dicom_data

        #sets darwing variables
        self.is_drawing = False
        self.rt_value = False

        colourAction = QAction("Choose Colour",self)
        colourAction.triggered.connect(self.change_colour)
        self.addAction(colourAction)

        #Undo feature / redo feature
        undo_button = QAction("Undo", self)
        undo_button.triggered.connect(self.undo_button)
        self.addAction(undo_button)

        redo_button = QAction("Redo", self)
        redo_button.triggered.connect(self.redo_button)
        self.addAction(redo_button)

        # start draw button
        start_draw = QAction("Start Drawing", self)
        start_draw.triggered.connect(self.activate_draw)
        self.addAction(start_draw)

        # stop draw button
        stop_draw = QAction("Stop Drawing", self)
        stop_draw.triggered.connect(self.stop_and_delete)
        self.addAction(stop_draw)


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
    
    def activate_draw(self):
        """Locks the slider and keeps the user on one slide 
            Caculates the pixel values so that they can only draw on those values"""
        self.dicom.setEnabled(False)
        self.canvas_label.good_to_draw = True
        self.is_drawing = True
        self.canvas_label.hu_values(self.dicom_data.ds_data[self.dicom.value()])


    def stop_and_delete(self):
        """Stops the current drawing and removes all the ROI drawing"""
        if self.is_drawing:
            self.pop_up_to_cancel()
            if self.rt_value:
                self.dicom.setEnabled(True)
                self.canvas_label.good_to_draw = False
                self.canvas_label.canvas.fill(Qt.transparent)
                self.canvas_label.setPixmap(self.canvas_label.canvas)
                self.is_drawing = False
                self.rt_value = False
    
    def pop_up_to_cancel(self):
        """If the user trys to stop without saving it will prompt them to save
            or they can chose to contiue and delete there work"""
        pop_up = QMessageBox()
        pop_up.setIcon(QMessageBox.Warning)
        pop_up.setText("You have no saved the ROI if you cancel now the ROI will be deleted?")
        pop_up.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Abort)

        anw = pop_up.exec()

        if anw == QMessageBox.Save:
            self.left_label.save_button()
        elif anw == QMessageBox.Cancel:
            return
        elif anw == QMessageBox.Abort:
            self.rt_value = True
            
