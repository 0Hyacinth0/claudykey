"""Light Pink Liquid Glass Dashboard theme for ClaudyKey.

Design principles:
  • Soft, luminous light-pink to pale-blue liquid gradient (`#fad0c4` -> `#ff9a9e` -> `#fecfef`).
  • Frosted-glass panels with light reflection styling.
  • Text uses darker pinkish-gray `#4e3a46` for legibility and visual comfort instead of pure white.
  • Bright, smooth pills for buttons with vibrant pink/cyan glow states.
"""

THEME_QSS = """
/* ══════════════════ Global Reset ══════════════════ */
* {
    outline: none;
    font-family: "Microsoft YaHei UI", "Segoe UI Variable", "SF Pro Display", -apple-system, sans-serif;
}

QWidget {
    color: #4e3a46;
    font-size: 13px;
}

/* ── Main window gradient background (Light Pink Liquid Glass) ── */
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0   #fad0c4,
        stop:0.5 #ffd1ff,
        stop:1   #a1c4fd
    );
}

/* Common Dialog Background */
QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #fbc2eb, stop:1 #a6c1ee
    );
}

/* ══════════════════ Scrollbars (Glassy & Slim) ══════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    border-radius: 3px;
    margin: 4px 1px;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.6);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 0.9); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    border-radius: 3px;
    margin: 1px 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.6);
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: rgba(255, 255, 255, 0.9); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* ══════════════════ Frosted-Glass Panels ══════════════════ */
QFrame#sidebar {
    background-color: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: 20px;
}
QFrame#main_area {
    background-color: transparent;
}
QFrame#glass_card {
    background-color: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 16px;
}
QFrame#sidebar_group {
    background-color: rgba(255, 255, 255, 0.25);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    padding: 10px;
}

/* ══════════════════ Labels & Headers ══════════════════ */
QLabel {
    background: transparent;
    color: #4e3a46;
}
QLabel#lbl_logo {
    color: #c94080;
    font-size: 18px;
    font-weight: 900;
    letter-spacing: 1px;
}
QLabel#lbl_section {
    color: #6d4b5d;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 2px;
}
QLabel#lbl_sidebar_hdr {
    color: rgba(78, 58, 70, 0.6);
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
QLabel#lbl_status_ok  { color: #0ea5e9; font-weight: bold; }
QLabel#lbl_status_run { color: #d946ef; font-weight: bold; }
QLabel#lbl_status_err { color: #f43f5e; font-weight: bold; }

/* ══════════════════ Buttons — Glass Pills ══════════════════ */
QPushButton {
    background-color: rgba(255, 255, 255, 0.6);
    color: #4e3a46;
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    padding: 7px 16px;
    min-height: 28px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid #ffffff;
    color: #c94080;
}
QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.8);
    padding-top: 8px; padding-bottom: 6px;
}
QPushButton:disabled {
    color: rgba(78, 58, 70, 0.4);
    background-color: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
}

/* Main Navigation Buttons (Sidebar) */
QPushButton#btn_nav {
    background-color: transparent;
    color: rgba(78, 58, 70, 0.7);
    border: none;
    border-radius: 12px;
    text-align: left;
    padding-left: 20px;
    font-size: 14px;
    height: 40px;
    font-weight: bold;
}
QPushButton#btn_nav:hover {
    background-color: rgba(255, 255, 255, 0.4);
    color: #c94080;
}
QPushButton#btn_nav:checked {
    background-color: rgba(255, 255, 255, 0.7);
    color: #c94080;
    border-left: 4px solid #c94080;
    border-radius: 8px;
}

/* ── Run button (Cyan Glow Pill) ── */
QPushButton#btn_run {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(100, 200, 255, 0.9), stop:1 rgba(150, 100, 255, 0.9));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 14px;
    font-weight: 900;
    font-size: 15px;
    padding: 10px 16px;
    letter-spacing: 1px;
}
QPushButton#btn_run:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(100, 200, 255, 1), stop:1 rgba(150, 100, 255, 1));
    border: 1px solid white;
}
QPushButton#btn_run:disabled {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.4);
    color: rgba(255, 255, 255, 0.7);
}

/* ── Stop button (Pink Pill) ── */
QPushButton#btn_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 117, 140, 0.9), stop:1 rgba(255, 126, 179, 0.9));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 14px;
    font-weight: 900;
    font-size: 15px;
    padding: 10px 16px;
}
QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 117, 140, 1), stop:1 rgba(255, 126, 179, 1));
    border: 1px solid white;
}

/* ── Accent button (Test Macro) ── */
QPushButton#btn_test_macro {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(250, 112, 154, 0.8), stop:1 rgba(254, 225, 64, 0.8));
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 10px;
    font-weight: bold;
}
QPushButton#btn_test_macro:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(250, 112, 154, 1), stop:1 rgba(254, 225, 64, 1));
    border: 1px solid white;
    color: #4e3a46;
}

/* ── Icon-only mini button ── */
QPushButton#btn_icon {
    background: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 8px;
    padding: 4px;
    color: #c94080;
}
QPushButton#btn_icon:hover {
    background: rgba(255, 255, 255, 0.8);
    border-color: #ffffff;
}

/* ══════════════════ Input Fields — Light Frosted Glass ══════════════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: rgba(255, 255, 255, 0.6);
    color: #4e3a46;
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 26px;
    selection-background-color: #ff9a9e;
    selection-color: white;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid #c94080;
}
QLineEdit:read-only {
    background-color: rgba(255, 255, 255, 0.3);
    color: rgba(78, 58, 70, 0.6);
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #c94080;
    width: 0; height: 0;
}
QComboBox QAbstractItemView {
    background-color: #fdfbfb;
    border: 1px solid #ff9a9e;
    border-radius: 8px;
    selection-background-color: #ff9a9e;
    selection-color: #ffffff;
    color: #4e3a46;
    outline: none;
    padding: 4px;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent; border: none; width: 20px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(255, 255, 255, 0.5); border-radius: 4px;
}
QSpinBox::up-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-bottom: 4px solid #c94080;
    width: 0; height: 0;
}
QSpinBox::down-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-top: 4px solid #c94080;
    width: 0; height: 0;
}

/* ══════════════════ List Widget ══════════════════ */
QListWidget {
    background-color: rgba(255, 255, 255, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 10px;
    outline: none;
    padding: 6px;
    color: #4e3a46;
}
QListWidget::item {
    border-radius: 6px;
    padding: 10px 12px;
    margin: 2px 0;
    color: #4e3a46;
}
QListWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.5);
    color: #c94080;
}
QListWidget::item:selected {
    background-color: rgba(255, 255, 255, 0.8);
    color: #c94080;
    border-left: 3px solid #ff9a9e;
    font-weight: bold;
}

/* ══════════════════ TextEdit (Logs) ══════════════════ */
QTextEdit#log_view {
    background-color: rgba(255, 255, 255, 0.6);
    color: #6d4b5d;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.7);
    font-family: Consolas, monospace;
    font-size: 11px;
    padding: 6px;
}

/* ══════════════════ Sliders ══════════════════ */
QSlider::groove:horizontal {
    height: 6px; background: rgba(255, 255, 255, 0.5); border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #ff9a9e;
    width: 14px; height: 14px; margin: -4px 0; border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    border-color: #c94080;
    transform: scale(1.1);
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #fad0c4, stop:1 #ff9a9e);
    border-radius: 3px;
}

/* ══════════════════ Tabs (Trigger Config Inner) ══════════════════ */
QTabWidget::pane { border: none; background: transparent; }
QTabBar::tab {
    background: rgba(255, 255, 255, 0.4); color: rgba(78, 58, 70, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.6); border-radius: 8px;
    padding: 8px 16px; margin-right: 6px; margin-bottom: 8px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.9); color: #c94080;
    font-weight: bold; border: 1px solid #ffffff;
}
QTabBar::tab:hover:!selected { background: rgba(255, 255, 255, 0.7); color: #c94080; }

/* ══════════════════ GroupBox ══════════════════ */
QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.6); border-radius: 12px;
    margin-top: 18px; padding-top: 14px;
    background-color: rgba(255, 255, 255, 0.2);
}
QGroupBox::title {
    subcontrol-origin: margin; left: 16px; padding: 0 10px;
    color: #c94080; font-size: 11px; font-weight: bold;
}

/* ══════════════════ CheckBox ══════════════════ */
QCheckBox { color: #4e3a46; spacing: 8px; background: transparent; }
QCheckBox::indicator {
    width: 16px; height: 16px; border: 2px solid rgba(255, 255, 255, 0.9);
    border-radius: 4px; background: rgba(255, 255, 255, 0.5);
}
QCheckBox::indicator:hover { border-color: #ff9a9e; }
QCheckBox::indicator:checked {
    background: #ff9a9e; border-color: #ff9a9e; image: none;
}

/* ══════════════════ Tooltip ══════════════════ */
QToolTip {
    background-color: #fdfbfb; color: #4e3a46;
    border: 1px solid #ff9a9e; border-radius: 6px;
    padding: 6px 10px; font-size: 12px;
}

/* ══════════════════ Separators ══════════════════ */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: rgba(255, 255, 255, 0.6); background-color: rgba(255, 255, 255, 0.6);
}

/* ══════════════════ Progress Bar ══════════════════ */
QProgressBar {
    background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 6px; height: 8px; text-align: center; color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #fad0c4, stop:1 #ff9a9e);
    border-radius: 4px;
}
"""
