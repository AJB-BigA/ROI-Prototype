import sys
import pydicom
import logging
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QPixmap, QPainter, QPen, QColor, QAction, QBrush
from PySide6.QtCore import Qt
from collections import deque
import numpy as np
from Transect_Window import TransectWindow

class CanvasLabel(QtWidgets.QLabel):
    """Class for the drawing funnction, creates an invisable layer projected over a dicom image"""
    def __init__(self, pen: QPen):
        super().__init__()
        self.pen = pen
        self.last_point = None
        self.t_window = TransectWindow()
        #sets the canvas and the mouse tracking
        self.canvas = QPixmap(512, 512)
        self.canvas.fill(Qt.transparent)
        self.setPixmap(self.canvas)
        self.setMouseTracking(True)

        #default pen width
        self.pen.setWidth(12)

        #variables for different tools
        self.circle_tool = False
        self.first_point = None
        self.fill_tool = False
        self.did_draw = False
        self.max_alpha = 255
        self.mid_point = []
        self.midpoint = (0,0)
        self.pixel_lock = None
        self.transect_tool = False
        self.line_points = 0
        self.transect_array = []
        self.hu_array = 0
        self.pixel_array = []
        self.slope = 1.0
        self.intercept = 0.0

        #stores the pixmaps after each draw to allow for an undo button
        self.draw_history = [self.canvas.copy()]
        self.redo_history = []

        #pen setup
        self.pen = QPen()
        self.pen.setWidth(12)
        self.pen.setColor(Qt.blue)
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)

        #transect Pen
        self.t_pen = QPen()
        self.t_pen.setWidth(2)
        self.t_pen.setColor(QColor(255, 105, 180))
        self.t_pen.setCapStyle(Qt.FlatCap)
        self.t_pen.setJoinStyle(Qt.MiterJoin)

        #drawing setup
        self.good_to_draw = False
        self.max_range = 6000
        self.min_range = -1000
        self.dicom_data_set = None

    def mousePressEvent(self, event: QMouseEvent):
        self.last_point = event.position().toPoint()
        self.first_point = event.position().toPoint()
        if self.fill_tool & self.good_to_draw:
            self.pixel_fill((self.first_point.x(), self.first_point.y()))
            self.setPixmap(self.canvas)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.good_to_draw and event.buttons() and self.fill_tool is False and Qt.LeftButton and self.transect_tool is False:
            current_point = event.position().toPoint()
            self.mid_point.append(current_point)
            painter = QPainter(self.canvas)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.setPen(self.pen)
            if self.last_point:
                painter.drawLine(self.last_point, current_point)            
            painter.end()
            self.setPixmap(self.canvas)
            self.last_point = current_point
            self.did_draw = True

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.circle_tool:
            self.pen_fill_tool(event)
            self.draw_history.append(self.canvas.copy())
            self.redo_history.clear()
        elif self.did_draw:
            self.draw_history.append(self.canvas.copy())
            self.redo_history.clear()
            self.did_draw = False
        self.mid_point.clear()

        #Makes sure 2 lines are drawn to use the transect tool
        if self.transect_tool & self.good_to_draw:
            self.transect_array.append(self.last_point)
            self.line_points +=1
            if self.line_points == 2:
                painter = QPainter(self.canvas)
                painter.setCompositionMode(QPainter.CompositionMode_Source)
                painter.setPen(self.t_pen)
                painter.drawLine(self.transect_array[0], self.transect_array[1])
                painter.end()
                self.setPixmap(self.canvas)
                self.draw_history.append(self.canvas.copy())
                self.transect_window()
                self.line_points = 0
                self.transect_array.clear()
        self.last_point = None

    def transect_window(self):
        """Creates the transect window"""
        p1_x = int(self.transect_array[0].x())
        p1_y = int(self.transect_array[0].y())
        p2_x = int(self.transect_array[1].x())
        p2_y = int(self.transect_array[1].y())
        #first calculate the gradient of the line
        #y = mx+b
        gradient = (p2_y - p1_y)/(p2_x - p1_x)
        b = p1_y - gradient * p1_x

        inbetweeners = abs(p1_x - p2_x)
        transeced_values = []
        if p1_x > p2_x:
            p1_x, p2_x = p2_x, p1_x

        for i in range(inbetweeners):
            nx = p1_x+i
            ny = int(nx*gradient + b)
            raw_value = self.pixel_array[ny,nx]
            hu_value = raw_value * self.slope + self.intercept
            transeced_values.append(hu_value)
        
        self.t_window = TransectWindow(transeced_values)
        self.t_window.show()

    def pen_fill_tool(self, event):
        """connects the last two points and fills the insides"""
        current_point = event.position().toPoint()
        painter = QPainter(self.canvas)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setPen(self.pen)
        painter.drawLine(self.first_point, current_point)
        painter.end()
        self.setPixmap(self.canvas)
        ave = self.caculate_average_pixle()
        self.flood(ave)
        self.setPixmap(self.canvas)

    def caculate_average_pixle(self):
        """Caculates the midpoint of the circle/drawing to allow the flood tool to work"""
        i = 1
        x = 0
        y = 0
        while self.mid_point:
            p = self.mid_point[0]
            x += p.x()
            y += p.y()
            self.mid_point.pop(0)
            i +=1
        average = (int(x/i), int(y/i))
        return average

    #not the things from halo
    def flood(self, mid_p):
        """Takes three inputs, x,y and colour. 
        From there it will scan all pixels around it and if any are not the colour specified it will 
        change its colour then run the algorithm again
        """
        #Bredth first search aproach
        #need to add the pixels adjacent to the drawing into an array
        #pop the first pixel can scan to see there values, if any arnt the desired add them to the array
        #then change that blue
        direction = [(0,0), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
        queue = deque([])
        visited = set()
        fill = QPainter(self.canvas)
        fill.setCompositionMode(QPainter.CompositionMode_Source)
        colour_contrast = self.pen.color()
        colour_contrast.setAlpha(self.max_alpha)
        fill.setBrush(QColor(colour_contrast))
        fill.setPen(Qt.NoPen)

        x,y = mid_p
        queue.append((x,y))
        visited.add((x,y))
        image = self.canvas.toImage()
        target_color = image.pixelColor(x, y)

        while queue:
            x,y = queue.popleft()
            fill.drawRect(x,y,1,1)
            for dx, dy in direction:
                nx, ny = dx + x, dy + y
                if 0 <= nx < image.width() and 0 <= ny < image.height():
                    colour = image.pixelColor(nx,ny)
                    if colour == target_color and (nx,ny) not in visited:
                        queue.append((nx,ny))
                        visited.add((nx,ny))
        fill.end()

    def undo_draw(self):
        """Reloads the last saved pixmap 
        pixmaps are saved after the user lifts there pen up"""
        if len(self.draw_history) > 1:
            self.redo_history.append(self.canvas.copy())
            self.draw_history.pop()
            self.canvas = self.draw_history[-1].copy()
            self.setPixmap(self.canvas)

    def redo_draw(self):
        """Oposite of undo"""
        if self.redo_history:
            self.draw_history.append(self.redo_history[-1].copy())
            self.canvas = self.redo_history.pop()
            self.setPixmap(self.canvas)

    def hu_values(self, ds):
        """Locks the pixels out of range based on max and min values"""
        self.pixel_array = ds.pixel_array.astype(np.int16)
        self.slope = float(getattr(ds, "RescaleSlope", 1.0))
        self.intercept = float(getattr(ds, "RescaleIntercept", 0.0))
        self.hu_array = (self.pixel_array * self.slope) + self.intercept
        self.lock_pixel()

    def lock_pixel(self):
        """Creates the lock values for the drawing images"""
        lock_mask = ~((self.hu_array >= self.min_range) & (self.hu_array <= self.max_range))
        self.pixel_lock = lock_mask

    def pixel_fill(self,mid_p):
        """Same as above but will also stop at the border of pixel values
        """
        x,y = mid_p
        if self.pixel_lock[y,x]:
            return
        #Bredth first search aproach
        #need to add the pixels adjacent to the drawing into an array
        #pop the first pixel can scan to see there values,
        #if any arnt the desired add them to the array
        #then change that blue
        direction = [(0,0), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
        queue = deque([])
        visited = set()
        fill = QPainter(self.canvas)
        fill.setCompositionMode(QPainter.CompositionMode_Source)
        colour_contrast = self.pen.color()
        colour_contrast.setAlpha(self.max_alpha)
        fill.setBrush(QColor(colour_contrast))
        fill.setPen(Qt.NoPen)
        #ff pylint u win this battle     
        queue.append((x,y))
        visited.add((x,y))
        image = self.canvas.toImage()
        target_color = image.pixelColor(x, y)

        while queue:
            x,y = queue.popleft()
            fill.drawRect(x,y,1,1)
            for dx, dy in direction:
                nx, ny = dx + x, dy + y
                if 0 <= nx < image.width() and 0 <= ny < image.height():
                    colour = image.pixelColor(nx,ny)
                    if colour == target_color and (nx,ny) not in visited and not self.pixel_lock[ny,nx]:
                        queue.append((nx,ny))
                        visited.add((nx,ny))
        fill.end()
        self.draw_history.append(self.canvas.copy())

