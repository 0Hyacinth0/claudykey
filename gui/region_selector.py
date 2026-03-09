"""Fullscreen overlay widget for selecting a screen region or picking a point."""
import threading

from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QCursor, QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QApplication


class RegionSelector(QWidget):
    """
    Fullscreen semi-transparent overlay.
    Emits region_selected(x, y, w, h) on drag-release.
    Emits cancelled() on Escape.
    If capture_template=True, the selected pixel region is also saved to
    template_path after selection.
    """
    region_selected = pyqtSignal(int, int, int, int)
    cancelled = pyqtSignal()

    def __init__(self, capture_template: bool = False, template_path: str = ''):
        super().__init__()
        self.capture_template = capture_template
        self.template_path = template_path
        self._start: QPoint | None = None
        self._end: QPoint | None = None
        self._dragging = False

        # Grab a screenshot to show underneath the overlay
        screen = QApplication.primaryScreen()
        self._bg: QPixmap = screen.grabWindow(0)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.setGeometry(screen.geometry())
        self.showFullScreen()
        self.setWindowOpacity(1.0)

    # ------------------------------------------------------------------ paint
    def paintEvent(self, _):
        painter = QPainter(self)
        # Background screenshot
        painter.drawPixmap(0, 0, self._bg)
        # Dark overlay
        painter.fillRect(self.rect(), QColor(255, 240, 248, 120))

        if self._start and self._end:
            rect = QRect(self._start, self._end).normalized()
            # Clear overlay inside selection
            painter.fillRect(rect, QColor(255, 255, 255, 30))
            # Selection border
            pen = QPen(QColor(209, 92, 137), 2)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(rect)
            # Corner handles
            painter.setPen(QPen(QColor(224, 116, 160), 2))
            cs = 8
            for cx, cy in [
                (rect.left(), rect.top()), (rect.right(), rect.top()),
                (rect.left(), rect.bottom()), (rect.right(), rect.bottom()),
            ]:
                painter.drawLine(cx - cs, cy, cx + cs, cy)
                painter.drawLine(cx, cy - cs, cx, cy + cs)
            # Coordinate label
            lbl = f" ({rect.x()}, {rect.y()})  {rect.width()} × {rect.height()} "
            painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            painter.setPen(QColor(99, 75, 88))
            painter.fillRect(rect.x(), rect.y() - 22, len(lbl) * 7, 20,
                             QColor(255, 255, 255, 220))
            painter.drawText(rect.x() + 3, rect.y() - 6, lbl)

        # Instruction hint
        hint_font = QFont("Microsoft YaHei UI", 13)
        painter.setFont(hint_font)
        painter.setPen(QColor(209, 92, 137, 220))
        painter.drawText(self.width() // 2 - 160, 40,
                         "拖动鼠标选择区域   |   ESC 取消")

    # ------------------------------------------------------------------ events
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.pos()
            self._end = event.pos()
            self._dragging = True

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._end = event.pos()
            rect = QRect(self._start, self._end).normalized()
            if rect.width() > 4 and rect.height() > 4:
                if self.capture_template and self.template_path:
                    cropped = self._bg.copy(rect)
                    cropped.save(self.template_path)
                self.close()
                self.region_selected.emit(rect.x(), rect.y(),
                                          rect.width(), rect.height())
            else:
                self._start = self._end = None
                self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.cancelled.emit()


class PointSelector(QWidget):
    """
    Fullscreen overlay for picking a single screen coordinate.
    Emits point_selected(x, y) on left-click.
    """
    point_selected = pyqtSignal(int, int)
    cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen()
        self._bg: QPixmap = screen.grabWindow(0)
        self._cursor_pos = QPoint(0, 0)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.setGeometry(screen.geometry())
        self.showFullScreen()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._bg)
        painter.fillRect(self.rect(), QColor(255, 240, 248, 120))
        # Crosshair
        p = self._cursor_pos
        pen = QPen(QColor(209, 92, 137), 1)
        painter.setPen(pen)
        painter.drawLine(p.x(), 0, p.x(), self.height())
        painter.drawLine(0, p.y(), self.width(), p.y())
        # Coordinate label
        lbl = f" ({p.x()}, {p.y()}) "
        painter.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        painter.fillRect(p.x() + 10, p.y() - 24, len(lbl) * 8, 20,
                         QColor(255, 255, 255, 220))
        painter.setPen(QColor(99, 75, 88))
        painter.drawText(p.x() + 12, p.y() - 8, lbl)
        # Hint
        painter.setFont(QFont("Microsoft YaHei UI", 13))
        painter.setPen(QColor(209, 92, 137, 220))
        painter.drawText(self.width() // 2 - 160, 40,
                         "点击选择坐标   |   ESC 取消")

    def mouseMoveEvent(self, event):
        self._cursor_pos = event.pos()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.close()
            self.point_selected.emit(event.pos().x(), event.pos().y())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.cancelled.emit()
