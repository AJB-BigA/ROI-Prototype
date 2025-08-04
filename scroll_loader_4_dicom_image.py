from PySide6.QtWidgets import QSlider

class Scroll_Wheel(QSlider):
    """Creates a scroll wheel for the dicom image loader"""
    def __init__(self, dicom_image_set = None):
        super().__init__()
        self.dicom_image_set = dicom_image_set

        self.setMaximum(len(self.dicom_image_set.qimage_array))

        self.valueChanged.connect(self.dicom_image_set.spin_box_value_changed)
