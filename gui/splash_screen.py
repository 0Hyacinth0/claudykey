"""Modern Splash Screen with animations.

提供现代化的启动画面，与主界面深色主题一致。
特性：大圆角、渐变边框发光、粒子动画、脉冲Logo、多阶段进度条。
"""
import math
import random

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF, pyqtProperty
from PyQt6.QtGui import (
    QPainter, QColor, QLinearGradient, QRadialGradient,
    QFont, QPen, QPainterPath,
)


class _Particle:
    """A single floating particle for the background animation."""
    __slots__ = ('x', 'y', 'vx', 'vy', 'size', 'alpha', 'color')

    def __init__(self, w: int, h: int):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.5, -0.1)
        self.size = random.uniform(1.5, 4.0)
        self.alpha = random.randint(40, 120)
        # Randomly pick between primary purple and accent cyan
        self.color = random.choice([
            QColor(124, 110, 248, self.alpha),
            QColor(99, 102, 241, self.alpha),
            QColor(6, 182, 212, self.alpha),
        ])

    def update(self, w: int, h: int):
        self.x += self.vx
        self.y += self.vy
        # Wrap around
        if self.y < -10:
            self.y = h + 5
            self.x = random.uniform(0, w)
        if self.x < -10:
            self.x = w + 5
        elif self.x > w + 10:
            self.x = -5


class ModernSplashScreen(QWidget):
    """现代化启动画面 — 与主界面深色毛玻璃主题一致。"""

    def __init__(self):
        super().__init__()

        self._opacity = 1.0
        self._pulse_phase = 0.0
        self._glow_phase = 0.0
        self._scan_x = 0.0

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(560, 300)

        # Particles
        self._particles = [_Particle(560, 300) for _ in range(30)]

        self._setup_ui()
        self._start_animations()

    # ═══════════════════════════════════════════════ UI
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 0, 40, 0)
        layout.setSpacing(0)

        # Logo
        self._logo_label = QLabel('⌨  ClaudyKey')
        self._logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_label.setStyleSheet("""
            QLabel {
                color: #8b8cf8;
                font-size: 44px;
                font-weight: 900;
                letter-spacing: 3px;
                background: transparent;
            }
        """)

        # Subtitle
        self._subtitle_label = QLabel('AI 智能连点器')
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(165, 180, 252, 0.6);
                font-size: 15px;
                font-weight: 500;
                letter-spacing: 2px;
                background: transparent;
            }
        """)

        # Version badge
        self._version_label = QLabel('v2.0')
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._version_label.setStyleSheet("""
            QLabel {
                color: rgba(124, 110, 248, 0.4);
                font-size: 11px;
                letter-spacing: 1px;
                background: transparent;
            }
        """)

        # Status
        self._status_label = QLabel('正在初始化...')
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("""
            QLabel {
                color: rgba(94, 234, 212, 0.7);
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            }
        """)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(3)
        self._progress.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 0.06);
                border: none;
                border-radius: 1px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:0.5 #7c6ef8, stop:1 #06b6d4);
                border-radius: 1px;
            }
        """)

        layout.addStretch(2)
        layout.addWidget(self._logo_label)
        layout.addSpacing(6)
        layout.addWidget(self._subtitle_label)
        layout.addSpacing(4)
        layout.addWidget(self._version_label)
        layout.addStretch(2)
        layout.addWidget(self._status_label)
        layout.addSpacing(14)
        layout.addWidget(self._progress)
        layout.addSpacing(28)

    # ═══════════════════════════════════════════════ Animations
    def _start_animations(self):
        # Main render loop (particles + glow + pulse)
        self._render_timer = QTimer(self)
        self._render_timer.timeout.connect(self._tick)
        self._render_timer.start(25)  # ~40fps

        # Progress crawl
        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.start(30)

    def _tick(self):
        self._pulse_phase += 0.06
        self._glow_phase += 0.04
        self._scan_x += 1.5
        if self._scan_x > self.width() + 100:
            self._scan_x = -100

        # Update particles
        w, h = self.width(), self.height()
        for p in self._particles:
            p.update(w, h)

        # Animate logo opacity via pulse
        alpha = int(200 + 55 * math.sin(self._pulse_phase))
        self._logo_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(139, 140, 248, {alpha});
                font-size: 44px;
                font-weight: 900;
                letter-spacing: 3px;
                background: transparent;
            }}
        """)

        self.update()

    def _update_progress(self):
        current = self._progress.value()
        if current < 90:
            self._progress.setValue(current + 1)

    # ═══════════════════════════════════════════════ Painting
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        radius = 28  # larger rounded corners

        # ── 1. Outer glow (subtle pulsing) ──
        glow_alpha = int(25 + 15 * math.sin(self._glow_phase))
        glow = QColor(99, 102, 241, glow_alpha)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawRoundedRect(
            self.rect().adjusted(-3, -3, 3, 3), radius + 3, radius + 3)

        # ── 2. Main background ──
        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0, QColor(12, 12, 24))
        bg.setColorAt(0.3, QColor(15, 15, 30))
        bg.setColorAt(0.7, QColor(18, 19, 35))
        bg.setColorAt(1, QColor(14, 14, 28))
        painter.setBrush(bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), radius, radius)

        # ── 3. Gradient border ──
        border_grad = QLinearGradient(0, 0, w, h)
        phase_shift = math.sin(self._glow_phase * 0.7)
        a1 = int(60 + 30 * phase_shift)
        a2 = int(30 + 20 * math.sin(self._glow_phase * 0.7 + 2))
        a3 = int(50 + 25 * math.sin(self._glow_phase * 0.7 + 4))
        border_grad.setColorAt(0, QColor(99, 102, 241, a1))
        border_grad.setColorAt(0.5, QColor(124, 110, 248, a2))
        border_grad.setColorAt(1, QColor(6, 182, 212, a3))
        painter.setPen(QPen(border_grad, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            self.rect().adjusted(1, 1, -1, -1), radius - 1, radius - 1)

        # ── 4. Scan line (horizontal light sweep) ──
        scan_grad = QRadialGradient(self._scan_x, h / 2, 80)
        scan_grad.setColorAt(0, QColor(124, 110, 248, 18))
        scan_grad.setColorAt(1, QColor(124, 110, 248, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(scan_grad)
        # Clip to rounded rect
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, radius, radius)
        painter.setClipPath(path)
        painter.drawRect(self.rect())

        # ── 5. Particles ──
        for p in self._particles:
            painter.setBrush(p.color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)

        # ── 6. Top-center subtle highlight ──
        highlight = QRadialGradient(w / 2, 0, w * 0.5)
        highlight.setColorAt(0, QColor(124, 110, 248, 15))
        highlight.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setClipping(True)
        painter.setBrush(highlight)
        painter.drawRect(self.rect())

        painter.setClipping(False)

    # ═══════════════════════════════════════════════ Public API
    def set_progress(self, value: int):
        self._progress.setValue(min(100, max(0, value)))

    def set_status(self, text: str):
        self._status_label.setText(text)

    def fade_out(self, duration: int = 400):
        self._progress.setValue(100)
        self._status_label.setText('✦ 准备就绪')
        self._status_label.setStyleSheet("""
            QLabel {
                color: rgba(74, 222, 128, 0.8);
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }
        """)

        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_animation.setDuration(duration)
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_animation.finished.connect(self.close)
        self._fade_animation.start()

        self._render_timer.stop()
        self._progress_timer.stop()
