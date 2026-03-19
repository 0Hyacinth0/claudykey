"""Modern Dark Professional Theme for ClaudyKey.

设计原则:
  • 深色渐变背景 (#0f0f1a → #171826) — 高端质感
  • 毛玻璃面板效果 — 现代视觉
  • 电蓝紫主色调 (#7c6ef8 / #6366f1) — 交互状态
  • 青色辅助色 — 状态指示
  • 统一圆角设计 — 扁平化风格
  • 清晰可读的文字 (#e1e4f0) — 易读性
"""

from .ui_constants import Colors, Radius, Spacing, Shadows, FontSizes


THEME_QSS = """
/* ══════════════════════════════════════════════════════════════
   Global Reset & Base Styles
   ══════════════════════════════════════════════════════════════ */
* {
    outline: none;
    font-family: "Microsoft YaHei UI", "Segoe UI Variable", "Segoe UI", 
                 "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif;
}

QWidget {
    color: #dde1f0;
    font-size: 13px;
    background: transparent;
}

/* ══════════════════════════════════════════════════════════════
   Main Window - Dark Gradient Background
   ══════════════════════════════════════════════════════════════ */
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0   #0f0f1a,
        stop:0.3 #12131a,
        stop:0.7 #171826,
        stop:1   #11111e
    );
}

QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1b2e, stop:1 #0f0f1a
    );
    border: 1px solid rgba(124, 110, 248, 0.15);
    border-radius: 16px;
}

/* ══════════════════════════════════════════════════════════════
   Scrollbars - Minimal & Elegant
   ══════════════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 4px 2px;
}
QScrollBar::handle:vertical {
    background: rgba(124, 110, 248, 0.3);
    border-radius: 4px;
    min-height: 40px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(124, 110, 248, 0.5);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 2px 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(124, 110, 248, 0.3);
    border-radius: 4px;
    min-width: 40px;
}
QScrollBar::handle:horizontal:hover {
    background: rgba(124, 110, 248, 0.5);
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* ══════════════════════════════════════════════════════════════
   Glass Panels - Frosted Glass Effect
   ══════════════════════════════════════════════════════════════ */
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.06),
        stop:1 rgba(255, 255, 255, 0.02));
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
}

QFrame#main_area {
    background-color: transparent;
}

QFrame#glass_card {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.055),
        stop:1 rgba(255, 255, 255, 0.02));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
}

QFrame#sidebar_group {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.05),
        stop:1 rgba(255, 255, 255, 0.02));
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 12px;
}

QFrame#panel_card {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.04),
        stop:1 rgba(255, 255, 255, 0.01));
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px;
}

/* ══════════════════════════════════════════════════════════════
   Labels - Typography System
   ══════════════════════════════════════════════════════════════ */
QLabel {
    background: transparent;
    color: #dde1f0;
}

QLabel#lbl_logo {
    color: #8b8cf8;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 1.5px;
}

QLabel#lbl_section {
    color: #7c6ef8;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 0.5px;
    padding: 4px;
}

QLabel#lbl_sidebar_hdr {
    color: rgba(180, 185, 220, 0.5);
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    margin-bottom: 6px;
    text-transform: uppercase;
}

QLabel#lbl_status_ok {
    color: #4ade80;
    font-weight: bold;
}

QLabel#lbl_status_run {
    color: #a78bfa;
    font-weight: bold;
}

QLabel#lbl_status_err {
    color: #f87171;
    font-weight: bold;
}

/* ══════════════════════════════════════════════════════════════
   Buttons - Interactive Elements
   ══════════════════════════════════════════════════════════════ */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.08),
        stop:1 rgba(255, 255, 255, 0.03));
    color: #c8cde8;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 8px 18px;
    min-height: 32px;
    font-weight: 600;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(124, 110, 248, 0.2),
        stop:1 rgba(124, 110, 248, 0.1));
    border: 1px solid rgba(124, 110, 248, 0.5);
    color: #a5b4fc;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(124, 110, 248, 0.3),
        stop:1 rgba(124, 110, 248, 0.15));
    border-color: rgba(124, 110, 248, 0.6);
    padding-top: 9px;
    padding-bottom: 7px;
}

QPushButton:disabled {
    color: rgba(200, 205, 232, 0.25);
    background: rgba(255, 255, 255, 0.02);
    border-color: rgba(255, 255, 255, 0.05);
}

/* ── Navigation Buttons ── */
QPushButton#btn_nav {
    background: transparent;
    color: rgba(200, 205, 232, 0.5);
    border: none;
    border-radius: 14px;
    text-align: left;
    padding-left: 20px;
    font-size: 13px;
    height: 46px;
    font-weight: 600;
    margin-bottom: 6px;
}

QPushButton#btn_nav:hover {
    background: rgba(124, 110, 248, 0.15);
    color: #a5b4fc;
}

QPushButton#btn_nav:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(99, 102, 241, 0.3),
        stop:0.5 rgba(99, 102, 241, 0.15),
        stop:1 rgba(99, 102, 241, 0.05));
    color: #a5b4fc;
    border-left: 3px solid #7c6ef8;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    padding-left: 17px;
}

/* ── Primary Action Button (Electric Violet) ── */
QPushButton#btn_run {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #6366f1, stop:1 #4f46e5);
    color: #ffffff;
    border: 1px solid rgba(99, 102, 241, 0.6);
    border-radius: 16px;
    font-weight: 800;
    font-size: 14px;
    padding: 14px 22px;
    letter-spacing: 0.5px;
}

QPushButton#btn_run:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #818cf8, stop:1 #6366f1);
    border-color: rgba(129, 140, 248, 0.8);
}

QPushButton#btn_run:disabled {
    background: rgba(255, 255, 255, 0.05);
    border-color: transparent;
    color: rgba(255, 255, 255, 0.25);
}

/* ── Danger Button (Warm Crimson) ── */
QPushButton#btn_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(239, 68, 68, 0.8),
        stop:1 rgba(220, 38, 38, 0.8));
    color: white;
    border: 1px solid rgba(239, 68, 68, 0.5);
    border-radius: 16px;
    font-weight: 800;
    font-size: 14px;
    padding: 14px 22px;
}

QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(248, 113, 113, 0.95),
        stop:1 rgba(239, 68, 68, 0.95));
    border-color: rgba(248, 113, 113, 0.7);
}

QPushButton#btn_stop:disabled {
    background: rgba(255, 255, 255, 0.05);
    border-color: transparent;
    color: rgba(255, 255, 255, 0.25);
}

/* ── Accent Button (Teal-Cyan) ── */
QPushButton#btn_accent {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 184, 166, 0.35),
        stop:1 rgba(6, 182, 212, 0.35));
    color: #5eead4;
    border: 1px solid rgba(20, 184, 166, 0.5);
    border-radius: 12px;
    font-weight: bold;
}

QPushButton#btn_accent:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 184, 166, 0.55),
        stop:1 rgba(6, 182, 212, 0.55));
    color: #99f6e4;
    border-color: rgba(94, 234, 212, 0.7);
}

/* ── Test Macro Button ── */
QPushButton#btn_test_macro {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 184, 166, 0.35),
        stop:1 rgba(6, 182, 212, 0.35));
    color: #5eead4;
    border: 1px solid rgba(20, 184, 166, 0.5);
    border-radius: 12px;
    font-weight: bold;
}

QPushButton#btn_test_macro:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 184, 166, 0.55),
        stop:1 rgba(6, 182, 212, 0.55));
    color: #99f6e4;
    border-color: rgba(94, 234, 212, 0.7);
}

/* ── Icon Mini Button ── */
QPushButton#btn_icon {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 6px;
    color: #8b8cf8;
}

QPushButton#btn_icon:hover {
    background: rgba(124, 110, 248, 0.2);
    border-color: rgba(124, 110, 248, 0.5);
    color: #c4c6ff;
}

/* ══════════════════════════════════════════════════════════════
   Input Fields - Modern Inputs
   ══════════════════════════════════════════════════════════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.07),
        stop:1 rgba(255, 255, 255, 0.03));
    color: #dde1f0;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 8px 14px;
    min-height: 32px;
    selection-background-color: rgba(124, 110, 248, 0.5);
    selection-color: white;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(124, 110, 248, 0.12),
        stop:1 rgba(124, 110, 248, 0.06));
    border: 1px solid rgba(124, 110, 248, 0.6);
}

QLineEdit:read-only {
    background: rgba(255, 255, 255, 0.02);
    color: rgba(200, 205, 232, 0.4);
}

QLineEdit::placeholder {
    color: rgba(200, 205, 232, 0.35);
}

/* ── ComboBox ── */
QComboBox::drop-down {
    border: none;
    width: 32px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #7c6ef8;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #1e2033;
    border: 1px solid rgba(124, 110, 248, 0.35);
    border-radius: 12px;
    selection-background-color: rgba(99, 102, 241, 0.45);
    selection-color: #c4c6ff;
    color: #c8cde8;
    outline: none;
    padding: 8px;
}

/* ── SpinBox Buttons ── */
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 28px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(124, 110, 248, 0.25);
    border-radius: 8px;
}

QSpinBox::up-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #7c6ef8;
    width: 0;
    height: 0;
}

QSpinBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #7c6ef8;
    width: 0;
    height: 0;
}

QDoubleSpinBox::up-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #7c6ef8;
    width: 0;
    height: 0;
}

QDoubleSpinBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #7c6ef8;
    width: 0;
    height: 0;
}

/* ══════════════════════════════════════════════════════════════
   List Widget - Modern Cards
   ══════════════════════════════════════════════════════════════ */
QListWidget {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    outline: none;
    padding: 8px;
    color: #c8cde8;
}

QListWidget::item {
    border-radius: 10px;
    padding: 12px 16px;
    margin: 3px 0;
    color: #c8cde8;
}

QListWidget::item:hover {
    background: rgba(124, 110, 248, 0.12);
    color: #a5b4fc;
}

QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(99, 102, 241, 0.25),
        stop:1 rgba(99, 102, 241, 0.1));
    color: #c4c6ff;
    font-weight: bold;
    border-left: 3px solid #7c6ef8;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    padding-left: 13px;
}

/* ══════════════════════════════════════════════════════════════
   TextEdit (Logs) - Terminal Style
   ══════════════════════════════════════════════════════════════ */
QTextEdit#log_view {
    background: rgba(10, 10, 20, 0.6);
    color: #7c9cbf;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    font-family: "JetBrains Mono", "Fira Code", Consolas, 
                 "Cascadia Code", "SF Mono", monospace;
    font-size: 11px;
    padding: 12px;
}

/* ══════════════════════════════════════════════════════════════
   Sliders - Modern Range Input
   ══════════════════════════════════════════════════════════════ */
QSlider::groove:horizontal {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #7c6ef8;
    border: 2px solid #a5b4fc;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: #a5b4fc;
    border-color: #c4cbff;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4f46e5, stop:1 #7c6ef8);
    border-radius: 3px;
}

/* ══════════════════════════════════════════════════════════════
   Tabs - Modern Tab Bar
   ══════════════════════════════════════════════════════════════ */
QTabWidget::pane {
    border: none;
    background: transparent;
}

QTabBar::tab {
    background: rgba(255, 255, 255, 0.04);
    color: rgba(200, 205, 232, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 8px 22px;
    margin-right: 8px;
    margin-bottom: 10px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(99, 102, 241, 0.25),
        stop:1 rgba(99, 102, 241, 0.1));
    color: #a5b4fc;
    font-weight: bold;
    border: 1px solid rgba(124, 110, 248, 0.5);
}

QTabBar::tab:hover:!selected {
    background: rgba(124, 110, 248, 0.12);
    color: #a5b4fc;
}

/* ══════════════════════════════════════════════════════════════
   GroupBox - Card Container
   ══════════════════════════════════════════════════════════════ */
QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    margin-top: 24px;
    padding-top: 20px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.03),
        stop:1 rgba(255, 255, 255, 0.01));
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 18px;
    padding: 0 12px;
    color: #7c6ef8;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}

/* ══════════════════════════════════════════════════════════════
   CheckBox - Toggle Style
   ══════════════════════════════════════════════════════════════ */
QCheckBox {
    color: #c8cde8;
    spacing: 12px;
    background: transparent;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.18);
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.04);
}

QCheckBox::indicator:hover {
    border-color: rgba(124, 110, 248, 0.7);
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(99, 102, 241, 0.8),
        stop:1 rgba(99, 102, 241, 0.6));
    border-color: #7c6ef8;
}

/* ══════════════════════════════════════════════════════════════
   Tooltip - Informative Overlay
   ══════════════════════════════════════════════════════════════ */
QToolTip {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #252640, stop:1 #1e2033);
    color: #c8cde8;
    border: 1px solid rgba(124, 110, 248, 0.4);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 12px;
}

/* ══════════════════════════════════════════════════════════════
   Progress Bar - Animated Progress
   ══════════════════════════════════════════════════════════════ */
QProgressBar {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    height: 10px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4f46e5, stop:1 #7c6ef8);
    border-radius: 6px;
}

/* ══════════════════════════════════════════════════════════════
   Menu - Dropdown Menus
   ══════════════════════════════════════════════════════════════ */
QMenu {
    background: #1e2033;
    border: 1px solid rgba(124, 110, 248, 0.3);
    border-radius: 12px;
    padding: 8px;
    color: #c8cde8;
}

QMenu::item {
    border-radius: 8px;
    padding: 8px 24px;
}

QMenu::item:selected {
    background: rgba(99, 102, 241, 0.35);
    color: #c4c6ff;
}

QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
    margin: 6px 12px;
}

/* ══════════════════════════════════════════════════════════════
   Message Box - Dialog Alerts
   ══════════════════════════════════════════════════════════════ */
QMessageBox {
    background: #1a1b2e;
}

QMessageBox QLabel {
    color: #dde1f0;
    font-size: 13px;
}

/* ══════════════════════════════════════════════════════════════
   Dialog Button Box
   ══════════════════════════════════════════════════════════════ */
QDialogButtonBox QPushButton {
    min-width: 80px;
    padding: 8px 20px;
}

/* ══════════════════════════════════════════════════════════════
   Toolbar Button Group - Compact Labels
   ══════════════════════════════════════════════════════════════ */
QPushButton#btn_toolbar {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 6px 14px;
    min-height: 28px;
    color: rgba(200, 205, 232, 0.7);
    font-size: 12px;
    font-weight: 600;
}

QPushButton#btn_toolbar:hover {
    background: rgba(124, 110, 248, 0.18);
    border-color: rgba(124, 110, 248, 0.45);
    color: #a5b4fc;
}

QPushButton#btn_toolbar:pressed {
    background: rgba(124, 110, 248, 0.28);
    border-color: rgba(124, 110, 248, 0.6);
}

/* ── Toolbar Separator ── */
QFrame#toolbar_separator {
    background: rgba(255, 255, 255, 0.08);
    max-width: 1px;
    min-width: 1px;
    margin: 4px 6px;
}

/* ══════════════════════════════════════════════════════════════
   Action List Item - Rich Content
   ══════════════════════════════════════════════════════════════ */
QWidget#action_item_widget {
    background: transparent;
}

QLabel#action_type_tag {
    background: rgba(99, 102, 241, 0.25);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

QLabel#action_type_tag_mouse {
    background: rgba(59, 130, 246, 0.2);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#action_type_tag_key {
    background: rgba(34, 197, 94, 0.18);
    color: #86efac;
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#action_type_tag_delay {
    background: rgba(251, 191, 36, 0.18);
    color: #fde68a;
    border: 1px solid rgba(251, 191, 36, 0.3);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#action_type_tag_loop {
    background: rgba(168, 85, 247, 0.2);
    color: #d8b4fe;
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#action_type_tag_cond {
    background: rgba(6, 182, 212, 0.18);
    color: #67e8f9;
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#action_param_text {
    color: rgba(200, 205, 232, 0.65);
    font-size: 12px;
    background: transparent;
}

/* ── Action Dot Indicator ── */
QFrame#action_dot {
    border-radius: 5px;
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
}

/* ══════════════════════════════════════════════════════════════
   Empty State Placeholder
   ══════════════════════════════════════════════════════════════ */
QLabel#empty_state {
    color: rgba(180, 185, 220, 0.3);
    font-size: 14px;
    font-weight: 500;
    background: transparent;
    padding: 40px;
}

QLabel#empty_state_icon {
    color: rgba(124, 110, 248, 0.2);
    font-size: 36px;
    background: transparent;
}

/* ══════════════════════════════════════════════════════════════
   Threshold Color Indicators
   ══════════════════════════════════════════════════════════════ */
QLabel#thr_low {
    color: #f87171;
    font-weight: bold;
    background: transparent;
}
QLabel#thr_mid {
    color: #fbbf24;
    font-weight: bold;
    background: transparent;
}
QLabel#thr_high {
    color: #4ade80;
    font-weight: bold;
    background: transparent;
}

/* ══════════════════════════════════════════════════════════════
   Template Preview Empty State
   ══════════════════════════════════════════════════════════════ */
QLabel#tmpl_empty {
    border: 2px dashed rgba(124, 110, 248, 0.25);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.02);
    color: rgba(180, 185, 220, 0.35);
    font-size: 11px;
}
"""
