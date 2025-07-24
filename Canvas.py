import sys
import pydicom
import logging
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QPixmap, QPainter, QPen, QColor, QAction, QBrush
from PySide6.QtCore import QTimer, Qt

      
class CanvasLabel(QtWidgets.QLabel):
    def __init__(self, pen: QPen):
        super().__init__()
        self.pen = pen
        self.last_point = None
        self.canvas = QPixmap(500, 500)
        self.canvas.fill(Qt.white)
        self.setPixmap(self.canvas)
        self.setMouseTracking(True)

    def mousePressEvent(self, event: QMouseEvent):
        self.last_point = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            current_point = event.position().toPoint()
            painter = QPainter(self.canvas)
            painter.setPen(self.pen)
            if self.last_point:
                painter.drawLine(self.last_point, current_point)
            painter.end()
            self.setPixmap(self.canvas)
            self.last_point = current_point

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.last_point = None

    def changeCursor(self):
        """Change cursor"""
        self.setCursor(Qt.OpenHandCursor)