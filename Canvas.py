import sys
import pydicom
import logging
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QPixmap, QPainter, QPen, QColor, QAction, QBrush
from PySide6.QtCore import QTimer, Qt
from collections import deque

class CanvasLabel(QtWidgets.QLabel):
    def __init__(self, pen: QPen):
        super().__init__()
        self.pen = pen
        self.last_point = None

        #sets the canvas and the mouse tracking
        self.canvas = QPixmap(500, 500)
        self.canvas.fill(Qt.transparent)
        self.setPixmap(self.canvas)
        self.setMouseTracking(True)

        #default pen width
        self.pen.setWidth(12)

        #variables for different tools
        self.circle_tool = False
        self.first_point = None
        self.did_draw = False
        self.max_alpha = 255
        self.mid_point = []
        self.midpoint = (0,0)

        #stores the pixmaps after each draw to allow for an undo button
        self.draw_history = [self.canvas.copy()]
        self.redo_history = []

        #pen setup
        self.pen = QPen()
        self.pen.setWidth(12)
        self.pen.setColor(Qt.blue)
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)

    def mousePressEvent(self, event: QMouseEvent):
        self.last_point = event.position().toPoint()
        self.first_point = event.position().toPoint()
        

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
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
        self.last_point = None
        if self.circle_tool:
            self.pen_fill_tool(event)
            self.draw_history.append(self.canvas.copy())
            self.redo_history.clear()
        elif self.did_draw:
            self.draw_history.append(self.canvas.copy())
            self.redo_history.clear()
            self.did_draw = False
        self.mid_point.clear()

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

    def change_cursor(self):
        """Change cursor"""
        self.setCursor(Qt.OpenHandCursor)

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