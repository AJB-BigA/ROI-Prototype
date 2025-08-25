from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QPainter, QPen, QColor
from PySide6.QtCore import Qt, Slot
from collections import deque
import numpy as np
from Transect_Window import TransectWindow
from enum import Enum, auto

class Tool(Enum):
    """Holds the switch for the tools"""
    DRAW     = auto()
    FILL     = auto()
    CIRCLE   = auto()
    TRANSECT = auto()

class CanvasLabel(QtWidgets.QLabel):
    """Class for the drawing funnction, creates an invisable layer projected over a dicom image"""
    def __init__(self, pen: QPen, ds = None, scroll_loader = None):
        super().__init__()
        self.pen = pen
        self.last_point = None
        self.first_point = None
        self.t_window = None
        self.current_tool = Tool.DRAW
        self.dicom_data = ds
        self.scrol_loader = scroll_loader
        self.ds_is_active = False
        
        # sets the canvas and the mouse tracking
        self.canvas = QPixmap(512, 512)
        self.canvas.fill(Qt.transparent)
        self.setPixmap(self.canvas)
        self.setMouseTracking(True)

        # default pen width
        self.pen.setWidth(12)

        # variables for different tools
        self.did_draw = False
        self.max_alpha = 255
        self.mid_point = []
        self.midpoint = (0,0)
        self.pixel_lock = 0               # will become a np.bool_ array [H,W]
        self.line_points = 0
        self.transect_array = []
        self.pixel_array = 0              # DICOM HU array [H,W]
        self.slope = 1.0
        self.intercept = 0.0

        # stores the pixmaps after each draw to allow for an undo button
        self.draw_history = [self.canvas.copy()]
        self.redo_history = []

        # pen setup
        self.pen = QPen()
        self.pen.setWidth(12)
        self.pen.setColor(Qt.blue)
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)

        # transect Pen
        self.t_pen = QPen()
        self.t_pen.setWidth(2)
        self.t_pen.setColor(QColor(255, 105, 180))
        self.t_pen.setCapStyle(Qt.FlatCap)
        self.t_pen.setJoinStyle(Qt.MiterJoin)

        # drawing setup
        self.max_range = 6000
        self.min_range = -1000
        self.dicom_data_set = None

    def set_tool(self, tool_num):
        self.current_tool = Tool(tool_num)
        print(self.current_tool.name)

    def mousePressEvent(self, event: QMouseEvent):
        if not self.ds_is_active:
            self.set_pixel_layer(self.dicom_data.ds_data[self.scrol_loader.value()])
            self.ds_is_active = True
        self.last_point = event.position().toPoint()
        self.first_point = event.position().toPoint()
        if self.current_tool is Tool.FILL:
            self.pixel_fill((self.first_point.x(), self.first_point.y()))
            self._enforce_lock_after_stroke()         # NEW: enforce after fill
            self.draw_history.append(self.canvas.copy())  # CHANGED: record after enforcement
            self.redo_history.clear()
            self.setPixmap(self.canvas)

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() and (self.current_tool is Tool.DRAW or self.current_tool is Tool.CIRCLE):
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
        drew_something = False

        if self.current_tool is Tool.CIRCLE:
            # close the stroke then fill interior
            self.pen_fill_tool(event)
            drew_something = True

        elif self.did_draw:
            drew_something = True
            self.did_draw = False

        # If a stroke/fill occurred and it's not the TRANSECT overlay, enforce lock
        if drew_something and self.current_tool is not Tool.TRANSECT:
            self._enforce_lock_after_stroke()             # NEW

            # Save history AFTER enforcement so undo/redo has the corrected image
            self.draw_history.append(self.canvas.copy())  # CHANGED
            self.redo_history.clear()

        self.mid_point.clear()

        # Transect handling (kept as-is, not subject to lock)
        if self.current_tool is Tool.TRANSECT:
            self.transect_array.append(self.last_point)
            self.line_points += 1
            if self.line_points == 2:
                self.transect_method()

        self.last_point = None

    def transect_method(self):
        """Draws the transect line and runs the transect protcall"""
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

    def transect_window(self):
        """Creates the transect window"""
        p1_x = int(self.transect_array[0].x())
        p1_y = int(self.transect_array[0].y())
        p2_x = int(self.transect_array[1].x())
        p2_y = int(self.transect_array[1].y())
        # y = mx + b
        gradient = (p2_y - p1_y) / (p2_x - p1_x)
        b = p1_y - gradient * p1_x

        inbetweeners = abs(p1_x - p2_x)
        transeced_values = []
        if p1_x > p2_x:
            p1_x, p2_x = p2_x, p1_x

        for i in range(inbetweeners):
            nx = p1_x + i
            ny = int(nx * gradient + b)
            transeced_values.append(self.pixel_array[ny, nx])

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
        # (history is now handled in mouseReleaseEvent after enforcement)

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
            i += 1
        average = (int(x / i), int(y / i))
        return average

    # not the things from halo
    def flood(self, mid_p):
        """Simple BFS flood fill on current canvas"""
        direction = [(0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
        queue = deque([])
        visited = set()
        fill = QPainter(self.canvas)
        fill.setCompositionMode(QPainter.CompositionMode_Source)
        colour_contrast = self.pen.color()
        colour_contrast.setAlpha(self.max_alpha)
        fill.setBrush(QColor(colour_contrast))
        fill.setPen(Qt.NoPen)

        x, y = mid_p
        queue.append((x, y))
        visited.add((x, y))
        image = self.canvas.toImage()
        target_color = image.pixelColor(x, y)

        while queue:
            x, y = queue.popleft()
            fill.drawRect(x, y, 1, 1)
            for dx, dy in direction:
                nx, ny = dx + x, dy + y
                if 0 <= nx < image.width() and 0 <= ny < image.height():
                    colour = image.pixelColor(nx, ny)
                    if colour == target_color and (nx, ny) not in visited:
                        queue.append((nx, ny))
                        visited.add((nx, ny))
        fill.end()

    def undo_draw(self):
        """Reloads the last saved pixmap"""
        if len(self.draw_history) > 1:
            self.redo_history.append(self.canvas.copy())
            self.draw_history.pop()
            self.canvas = self.draw_history[-1].copy()
            self.setPixmap(self.canvas)

    def redo_draw(self):
        """Opposite of undo"""
        if self.redo_history:
            self.draw_history.append(self.redo_history[-1].copy())
            self.canvas = self.redo_history.pop()
            self.setPixmap(self.canvas)

    def set_pixel_layer(self, ds):
        """Locks the pixels out of range based on max and min values"""
        self.pixel_array = ds.pixel_array.astype(np.int16)
        self.lock_pixel()

    def lock_pixel(self):
        """Creates the lock values for the drawing images"""
        # pixel_lock == True means "locked" (outside allowed HU)
        lock_mask = ~((self.pixel_array >= self.min_range) & (self.pixel_array <= self.max_range))
        self.pixel_lock = lock_mask

    def pixel_fill(self, mid_p):
        """Fill tool that respects pixel_lock at expansion time"""
        x, y = mid_p 
        direction = [(0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
        fill = QPainter(self.canvas)
        fill.setCompositionMode(QPainter.CompositionMode_Source)
        colour_contrast = self.pen.color()
        colour_contrast.setAlpha(self.max_alpha)
        fill.setBrush(QColor(colour_contrast))
        fill.setPen(Qt.NoPen)

        h, w = self.pixel_lock.shape
        for (y, x), val in np.ndenumerate(self.pixel_lock):
            if val:  # only act if pixel is "locked"
                for dx, dy in direction:   # e.g. [(-1,0), (1,0), (0,-1), (0,1)]
                    nx, ny = x + dx, y + dy
                    if 0 <= ny < h and 0 <= nx < w:   # inside bounds
                        if self.pixel_lock[ny, nx] == 0:  # some condition
                            fill.drawRect(nx, ny, 1, 1)
        fill.end()
        # (history now handled in mouseReleaseEvent after enforcement)

    #AI Vibe coded part
    # --------------- NEW: lock enforcement helpers ---------------

    def _draw_mask_bool(self) -> np.ndarray:
        """Alpha>0 where anything has been drawn on the canvas."""
        img = self.canvas.toImage().convertToFormat(QImage.Format_ARGB32)
        h, w = img.height(), img.width()

        # memoryview (read-only is fine for reading)
        ptr = img.constBits()

        # View as bytes with row padding respected via bytesPerLine()
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape(h, img.bytesPerLine())

        # Keep only the real pixel bytes (drop padding), then take alpha channel
        row_bytes = arr[:, : w * 4]   # ARGB32 = 4 bytes per pixel
        alpha = row_bytes[:, 3::4]    # every 4th byte starting at index 3
        return alpha > 0

    def _allowed_mask_bool(self) -> np.ndarray:
        """
        True where drawing is allowed by HU lock.
        (pixel_lock==True means locked; invert it)
        """
        if isinstance(self.pixel_lock, np.ndarray):
            return ~self.pixel_lock
        # If lock isn't ready yet, allow everywhere
        return np.ones((self.canvas.height(), self.canvas.width()), dtype=bool)

    def _enforce_lock_after_stroke(self):
        """
        Check drawn pixels against the lock, and erase anything outside the lock.
        """
        # Guard: need a HU array to have a meaningful lock
        if not isinstance(self.pixel_array, np.ndarray):
            return

        draw_mask = self._draw_mask_bool()
        allow_mask = self._allowed_mask_bool()

        if draw_mask.shape != allow_mask.shape:
            # Sizes must match; if not, do nothing to avoid errors
            print(f"[lock] Size mismatch: draw={draw_mask.shape}, allow={allow_mask.shape}")
            return

        outside = draw_mask & ~allow_mask
        if not outside.any():
            return  # nothing to fix

        # Build an 8-bit alpha image (255 where allowed to keep, 0 where blocked => erased)
        h, w = allow_mask.shape
        mask_img = QImage(w, h, QImage.Format_Alpha8)
        mask_img.fill(0)

        # Writable memoryview
        mptr = mask_img.bits()
        marr = np.frombuffer(mptr, dtype=np.uint8).reshape(h, mask_img.bytesPerLine())

        # Fill only the active width (there may be padding on the right)
        marr[:, :w] = np.where(allow_mask, 255, 0).astype(np.uint8)

        # Apply as alpha mask
        p = QPainter(self.canvas)
        p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        p.drawImage(0, 0, mask_img)
        p.end()
        self.setPixmap(self.canvas)


        # DestinationIn keeps destination pixels only where mask alpha > 0
        p = QPainter(self.canvas)
        p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        p.drawImage(0, 0, mask_img)
        p.end()

        self.setPixmap(self.canvas)
        print(f"[lock] Erased {int(outside.sum())} px outside HU range.")


#end of AI Gen
    @Slot(bool)
    def change_layout_bool(self, v:bool):
        """Changes the values of ds_is_active to remind the drawer to reset the pixmap
          once the scroll loader changes value"""
        self.ds_is_active = v
