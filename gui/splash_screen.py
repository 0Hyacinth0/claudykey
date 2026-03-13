"""Modern Splash Screen with animations.

提供现代化的启动画面，包含渐变背景、动画效果和加载进度。
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen


class ModernSplashScreen(QWidget):
    """现代化启动画面。
    
    特性:
    - 渐变背景
    - 脉冲动画 Logo
    - 进度条动画
    - 淡入淡出效果
    """
    
    def __init__(self):
        super().__init__()
        
        self._opacity = 1.0
        self._pulse_value = 0.0
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(520, 280)
        
        self._setup_ui()
        self._start_animations()
    
    def _setup_ui(self):
        """设置 UI 组件。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._logo_label = QLabel('⌨ ClaudyKey')
        self._logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_label.setStyleSheet("""
            QLabel {
                color: #8b8cf8;
                font-size: 42px;
                font-weight: 900;
                letter-spacing: 2px;
                background: transparent;
            }
        """)
        
        self._subtitle_label = QLabel('AI 智能连点器')
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(180, 185, 220, 0.7);
                font-size: 16px;
                font-weight: 500;
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        
        self._status_label = QLabel('正在初始化...')
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("""
            QLabel {
                color: rgba(124, 110, 248, 0.8);
                font-size: 12px;
                background: transparent;
            }
        """)
        
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(4)
        self._progress.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b8cf8);
                border-radius: 2px;
            }
        """)
        
        layout.addStretch()
        layout.addWidget(self._logo_label)
        layout.addSpacing(8)
        layout.addWidget(self._subtitle_label)
        layout.addStretch()
        layout.addWidget(self._status_label)
        layout.addSpacing(16)
        layout.addWidget(self._progress)
        layout.addSpacing(24)
    
    def _start_animations(self):
        """启动动画。"""
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.start(30)
        
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.start(20)
    
    def _update_pulse(self):
        """更新脉冲动画。"""
        self._pulse_value = (self._pulse_value + 0.05) % (2 * 3.14159)
        self.update()
    
    def _update_progress(self):
        """更新进度条。"""
        current = self._progress.value()
        if current < 90:
            self._progress.setValue(current + 1)
    
    def set_progress(self, value: int):
        """设置进度值。
        
        Args:
            value: 进度值 (0-100)。
        """
        self._progress.setValue(min(100, max(0, value)))
    
    def set_status(self, text: str):
        """设置状态文本。
        
        Args:
            text: 状态文本。
        """
        self._status_label.setText(text)
    
    def paintEvent(self, event):
        """绘制事件 - 绘制渐变背景和装饰元素。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(15, 15, 26))
        gradient.setColorAt(0.5, QColor(18, 19, 38))
        gradient.setColorAt(1, QColor(23, 24, 38))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 20, 20)
        
        border_gradient = QLinearGradient(0, 0, self.width(), self.height())
        border_gradient.setColorAt(0, QColor(99, 102, 241, 80))
        border_gradient.setColorAt(0.5, QColor(124, 110, 248, 40))
        border_gradient.setColorAt(1, QColor(99, 102, 241, 80))
        
        pen = QPen(border_gradient, 1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 19, 19)
        
        glow_alpha = int(30 + 20 * (0.5 + 0.5 * (1 if self._pulse_value > 3.14159 else -1)))
        glow_color = QColor(124, 110, 248, glow_alpha)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow_color)
        painter.drawRoundedRect(self.rect().adjusted(-2, -2, 2, 2), 22, 22)
    
    def fade_out(self, duration: int = 300):
        """淡出动画。
        
        Args:
            duration: 动画时长(毫秒)。
        """
        self._progress.setValue(100)
        self._status_label.setText('准备就绪!')
        
        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_animation.setDuration(duration)
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._fade_animation.finished.connect(self.close)
        self._fade_animation.start()
        
        self._pulse_timer.stop()
        self._progress_timer.stop()
