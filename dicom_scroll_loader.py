"""Loads DICOM image set to UI and allows user to scroll through images using mouse wheel or a slider bar"""
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSpinBox,QSlider,QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal
from read_dicom_file import read_dicom_file
from inputs_and_outputs import get_qimage_from_dicom_file


class ScrollLoaderUI(QWidget):
    """UI element that will display a dicom image and allow the user to scroll to another image"""
    #signal connects the updated change with the canvas
    #This signal changes the bool value that prevents the pixel lock scan from taking place every click
    f_value = Signal(bool)
    def __init__(self, directory_in_str):
        super().__init__()

        self.qimage_array = self.extract_qimage_data(directory_in_str)
        self.ds_data = self.extract_ds_data(directory_in_str)

        layout = QHBoxLayout()

        self.pixmap = QPixmap()
        self.pixmap = QPixmap.fromImage(self.qimage_array[0])
        self.image_label = QLabel()
        self.image_label.setPixmap(self.pixmap)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def spin_box_value_changed(self, value):
        """Allows the user to change slices using a spin box"""
        if value < len(self.qimage_array):
            self.pixmap = QPixmap.fromImage(self.qimage_array[value])
            self.image_label.setPixmap(self.pixmap)
            self.f_value.emit(False)
   
    def extract_qimage_data(self,directory_path) -> list:
        """Method will extract all valid dicom image data, convert it to 
        qimages add them to an array and return the array"""
        directory = os.fsencode(directory_path)
        qimage_array = []
        files_with_instance = []

        for file in sorted(os.listdir(directory)):
            filename = os.fsdecode(file)
            if filename.endswith(".dcm"):
                try:
                    ds = read_dicom_file(
                        (os.path.join(os.fsdecode(directory), filename)))
                    instance = getattr(ds, "InstanceNumber", None)
                    image = get_qimage_from_dicom_file(ds)
                    if files_with_instance is not None:
                        files_with_instance.append((instance,image))
                    continue
                except Exception as e:
                    print(e)
                    continue
            else:
                continue
        files_with_instance.sort(key = lambda x: x[0])
        qimage_array = [img for _, img in files_with_instance]
        return qimage_array
    
    def extract_ds_data(self,directory_path) -> list:
        """Method will extract all valid dicom data"""
        directory = os.fsencode(directory_path)
        arr = []
        files_with_instance = []

        for file in sorted(os.listdir(directory)):
            filename = os.fsdecode(file)
            if filename.endswith(".dcm"):
                try:
                    ds = read_dicom_file(
                        (os.path.join(os.fsdecode(directory), filename)))
                    instance = getattr(ds, "InstanceNumber", None)
                    if files_with_instance is not None:
                        files_with_instance.append((int(instance),ds))
                    continue
                except Exception as e:
                    print(e)
                    continue
            else:
                continue
        files_with_instance.sort(key = lambda x: x[0])
        arr = [img for _, img in files_with_instance]
        return arr