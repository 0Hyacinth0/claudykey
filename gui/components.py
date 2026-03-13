"""Modular UI Components for ClaudyKey.

提供可复用的 UI 组件，实现模块化设计。
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt6.QtGui import QColor, QPainter, QLinearGradient, QPen, QFont


class GlassCard(QFrame):
    """毛玻璃效果卡片组件。
    
    特性:
    - 半透明背景
    - 渐变边框
    - 圆角设计
    - 可选阴影效果
    """
    
    def __init__(self, parent=None, title: str = '', show_shadow: bool = True):
        super().__init__(parent)
        self._title = title
        self._show_shadow = show_shadow
        
        self.setObjectName('glass_card')
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        if show_shadow:
            self._setup_shadow()
        
        self._setup_layout()
    
    def _setup_shadow(self):
        """设置阴影效果。"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(60, 50, 120, 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
    
    def _setup_layout(self):
        """设置布局。"""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(16)
        
        if self._title:
            title_label = QLabel(self._title)
            title_label.setObjectName('lbl_section')
            self._layout.addWidget(title_label)
    
    def add_widget(self, widget: QWidget):
        """添加组件到卡片。
        
        Args:
            widget: 要添加的组件。
        """
        self._layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加布局到卡片。
        
        Args:
            layout: 要添加的布局。
        """
        self._layout.addLayout(layout)
    
    def paintEvent(self, event):
        """绘制事件 - 自定义渐变背景。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 14))
        gradient.setColorAt(1, QColor(255, 255, 255, 5))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 20, 20)
        
        border_color = QColor(255, 255, 255, 25)
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 19, 19)


class ModernButton(QPushButton):
    """现代化按钮组件。
    
    支持多种预设样式:
    - primary: 主要操作按钮
    - danger: 危险操作按钮
    - accent: 强调按钮
    - ghost: 透明按钮
    """
    
    STYLES = {
        'primary': """
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6366f1, stop:1 #4f46e5);
                color: white;
                border: 1px solid rgba(99, 102, 241, 0.6);
                border-radius: {radius}px;
                padding: {padding}px {padding_h}px;
                font-weight: 700;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #818cf8, stop:1 #6366f1);
                border-color: rgba(129, 140, 248, 0.8);
            }}
            QPushButton:disabled {{
                background: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.25);
                border-color: transparent;
            }}
        """,
        'danger': """
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(239, 68, 68, 0.8), stop:1 rgba(220, 38, 38, 0.8));
                color: white;
                border: 1px solid rgba(239, 68, 68, 0.5);
                border-radius: {radius}px;
                padding: {padding}px {padding_h}px;
                font-weight: 700;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(248, 113, 113, 0.95), stop:1 rgba(239, 68, 68, 0.95));
            }}
            QPushButton:disabled {{
                background: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.25);
            }}
        """,
        'accent': """
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 184, 166, 0.35), stop:1 rgba(6, 182, 212, 0.35));
                color: #5eead4;
                border: 1px solid rgba(20, 184, 166, 0.5);
                border-radius: {radius}px;
                padding: {padding}px {padding_h}px;
                font-weight: 600;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 184, 166, 0.55), stop:1 rgba(6, 182, 212, 0.55));
                color: #99f6e4;
            }}
        """,
        'ghost': """
            QPushButton {{
                background: transparent;
                color: #c8cde8;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {radius}px;
                padding: {padding}px {padding_h}px;
                font-weight: 600;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background: rgba(124, 110, 248, 0.15);
                border-color: rgba(124, 110, 248, 0.4);
                color: #a5b4fc;
            }}
        """
    }
    
    def __init__(
        self,
        text: str = '',
        style: str = 'ghost',
        icon: str = '',
        parent=None
    ):
        super().__init__(parent)
        
        self._style_name = style
        self._apply_style()
        
        display_text = f'{icon} {text}' if icon else text
        self.setText(display_text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _apply_style(self):
        """应用样式。"""
        style_template = self.STYLES.get(self._style_name, self.STYLES['ghost'])
        
        style_str = style_template.format(
            radius=12,
            padding=10,
            padding_h=20,
            font_size=13
        )
        
        self.setStyleSheet(style_str)


class StatusIndicator(QWidget):
    """状态指示器组件。
    
    显示运行状态，支持动画效果。
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status = 'idle'
        self._animation_value = 0.0
        
        self.setFixedSize(12, 12)
        
        self._animation_timer = None
    
    def set_status(self, status: str):
        """设置状态。
        
        Args:
            status: 状态 ('idle', 'running', 'error', 'success')。
        """
        self._status = status
        
        if status == 'running':
            self._start_animation()
        else:
            self._stop_animation()
        
        self.update()
    
    def _start_animation(self):
        """启动动画。"""
        if self._animation_timer is None:
            self._animation_timer = QTimer(self)
            self._animation_timer.timeout.connect(self._animate)
        self._animation_timer.start(50)
    
    def _stop_animation(self):
        """停止动画。"""
        if self._animation_timer:
            self._animation_timer.stop()
        self._animation_value = 0.0
    
    def _animate(self):
        """动画更新。"""
        self._animation_value = (self._animation_value + 0.1) % 1.0
        self.update()
    
    def paintEvent(self, event):
        """绘制状态指示器。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = {
            'idle': QColor(180, 185, 220, 150),
            'running': QColor(167, 139, 250),
            'error': QColor(248, 113, 113),
            'success': QColor(74, 222, 128)
        }
        
        color = colors.get(self._status, colors['idle'])
        
        if self._status == 'running':
            alpha = int(150 + 105 * (0.5 + 0.5 * (1 if self._animation_value > 0.5 else -1)))
            color.setAlpha(alpha)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(self.rect())
        
        if self._status == 'running':
            glow_color = QColor(color)
            glow_color.setAlpha(80)
            painter.setBrush(glow_color)
            painter.drawEllipse(self.rect().adjusted(-2, -2, 2, 2))


class SidebarNavigation(QWidget):
    """侧边栏导航组件。
    
    提供模块化的导航菜单。
    """
    
    nav_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._buttons = []
        self._current_index = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI。"""
        self.setObjectName('sidebar')
        self.setFixedWidth(260)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 24, 16, 24)
        self._layout.setSpacing(8)
        
        logo = QLabel('✦ ClaudyKey')
        logo.setObjectName('lbl_logo')
        self._layout.addWidget(logo)
        self._layout.addSpacing(24)
        
        nav_label = QLabel('工作区')
        nav_label.setObjectName('lbl_sidebar_hdr')
        self._layout.addWidget(nav_label)
    
    def add_nav_item(self, text: str, icon: str = '', index: int = -1):
        """添加导航项。
        
        Args:
            text: 导航文本。
            icon: 图标字符。
            index: 索引，默认追加到末尾。
        """
        btn = QPushButton(f'{icon}  {text}' if icon else text)
        btn.setObjectName('btn_nav')
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if index < 0:
            index = len(self._buttons)
        
        btn.clicked.connect(lambda checked, idx=index: self._on_nav_clicked(idx))
        
        self._buttons.append(btn)
        self._layout.addWidget(btn)
        
        if len(self._buttons) == 1:
            btn.setChecked(True)
    
    def _on_nav_clicked(self, index: int):
        """导航点击处理。
        
        Args:
            index: 点击的索引。
        """
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
        
        self._current_index = index
        self.nav_changed.emit(index)
    
    def add_stretch(self):
        """添加弹性空间。"""
        self._layout.addStretch()
    
    def add_widget(self, widget: QWidget):
        """添加组件。
        
        Args:
            widget: 要添加的组件。
        """
        self._layout.addWidget(widget)
    
    def paintEvent(self, event):
        """绘制事件。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 15))
        gradient.setColorAt(1, QColor(255, 255, 255, 5))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 24, 24)
        
        border_color = QColor(255, 255, 255, 20)
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 23, 23)
