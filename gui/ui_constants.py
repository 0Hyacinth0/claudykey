"""UI 样式常量和设计系统。

定义应用程序的视觉设计规范，包括颜色、圆角、间距等。
"""

class Colors:
    """颜色系统 - 现代渐变色板。"""
    
    PRIMARY_START = '#6366f1'
    PRIMARY_END = '#4f46e5'
    PRIMARY_LIGHT = '#818cf8'
    PRIMARY_HOVER = '#a5b4fc'
    
    ACCENT_START = '#14b8a6'
    ACCENT_END = '#06b6d4'
    ACCENT_LIGHT = '#5eead4'
    
    DANGER_START = '#ef4444'
    DANGER_END = '#dc2626'
    DANGER_LIGHT = '#f87171'
    
    SUCCESS = '#4ade80'
    WARNING = '#fbbf24'
    
    BG_DARK_START = '#0f0f1a'
    BG_DARK_MID = '#12131a'
    BG_DARK_END = '#171826'
    
    GLASS_BG = 'rgba(255, 255, 255, 0.045)'
    GLASS_BORDER = 'rgba(255, 255, 255, 0.08)'
    GLASS_HOVER = 'rgba(124, 110, 248, 0.15)'
    
    TEXT_PRIMARY = '#e1e4f0'
    TEXT_SECONDARY = '#c8cde8'
    TEXT_MUTED = 'rgba(180, 185, 220, 0.45)'
    
    SIDEBAR_BG = 'rgba(255, 255, 255, 0.04)'
    CARD_BG = 'rgba(255, 255, 255, 0.025)'


class Radius:
    """圆角系统 - 扁平化设计。"""
    
    NONE = '0px'
    SM = '6px'
    MD = '10px'
    LG = '14px'
    XL = '18px'
    XXL = '20px'
    FULL = '9999px'


class Spacing:
    """间距系统。"""
    
    XS = '4px'
    SM = '8px'
    MD = '12px'
    LG = '16px'
    XL = '20px'
    XXL = '24px'


class Shadows:
    """阴影效果。"""
    
    SM = '0 2px 4px rgba(0, 0, 0, 0.1)'
    MD = '0 4px 8px rgba(0, 0, 0, 0.15)'
    LG = '0 8px 16px rgba(0, 0, 0, 0.2)'
    GLOW_PRIMARY = '0 0 20px rgba(99, 102, 241, 0.3)'
    GLOW_ACCENT = '0 0 20px rgba(20, 184, 166, 0.3)'


class Transitions:
    """过渡动画时长。"""
    
    FAST = '150ms'
    NORMAL = '250ms'
    SLOW = '400ms'


class FontSizes:
    """字体大小系统。"""
    
    XS = '10px'
    SM = '11px'
    MD = '13px'
    LG = '14px'
    XL = '16px'
    XXL = '18px'
    XXXL = '24px'


class ZIndex:
    """层级系统。"""
    
    BASE = 0
    DROPDOWN = 100
    STICKY = 200
    FIXED = 300
    MODAL_BACKDROP = 400
    MODAL = 500
    POPOVER = 600
    TOOLTIP = 700


GLASS_EFFECT = """
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.08),
        stop:1 rgba(255, 255, 255, 0.02));
    backdrop-filter: blur(10px);
"""

BUTTON_BASE = f"""
    QPushButton {{
        background-color: {Colors.GLASS_BG};
        color: {Colors.TEXT_SECONDARY};
        border: 1px solid {Colors.GLASS_BORDER};
        border-radius: {Radius.MD};
        padding: 7px 16px;
        min-height: 28px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {Colors.GLASS_HOVER};
        border: 1px solid rgba(124, 110, 248, 0.4);
        color: {Colors.PRIMARY_HOVER};
    }}
    QPushButton:pressed {{
        background-color: rgba(124, 110, 248, 0.25);
        border-color: rgba(124, 110, 248, 0.5);
    }}
    QPushButton:disabled {{
        color: rgba(200, 205, 232, 0.2);
        background-color: rgba(255, 255, 255, 0.02);
        border-color: rgba(255, 255, 255, 0.04);
    }}
"""

INPUT_BASE = f"""
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: rgba(255, 255, 255, 0.05);
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: {Radius.MD};
        padding: 7px 12px;
        min-height: 28px;
        selection-background-color: rgba(124, 110, 248, 0.5);
    }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        background-color: rgba(124, 110, 248, 0.08);
        border: 1px solid rgba(124, 110, 248, 0.55);
    }}
"""
