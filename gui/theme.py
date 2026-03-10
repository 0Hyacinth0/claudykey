"""Liquid Glass Dashboard theme for ClaudyKey.

Design principles:
  • Breathtaking liquid aurora gradient background (cyan-magenta-violet).
  • Translucent frosted-glass panels (`rgba(255, 255, 255, 0.15)`) with white borders.
  • Dashboard Layout: Fixed sidebar + stacked main area.
  • Extreme rounded corners (`16px`, `20px`).
  • Heavy emphasis on contrast and glow states.
"""

THEME_QSS = """
/* ══════════════════ Global Reset ══════════════════ */
* {
    outline: none;
    font-family: "Microsoft YaHei UI", "Segoe UI Variable", "SF Pro Display", -apple-system, sans-serif;
}

QWidget {
    color: #ffffff;
    font-size: 13px;
}

/* ── Main window gradient background (Liquid Mesh Simulation) ── */
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0   #4158D0,
        stop:0.46 #C850C0,
        stop:1   #FFCC70
    );
}

/* Common Dialog Background */
QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #5f2c82, stop:1 #49a09d
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
    background: rgba(255, 255, 255, 0.35);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 0.6); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    border-radius: 3px;
    margin: 1px 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.35);
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: rgba(255, 255, 255, 0.6); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* ══════════════════ Frosted-Glass Panels ══════════════════ */
QFrame#sidebar {
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 20px;
}
QFrame#main_area {
    background-color: transparent;
}
QFrame#glass_card {
    background-color: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 16px;
}
QFrame#sidebar_group {
    background-color: rgba(0, 0, 0, 0.15);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 10px;
}

/* ══════════════════ Labels & Headers ══════════════════ */
QLabel {
    background: transparent;
    color: #ffffff;
}
QLabel#lbl_logo {
    color: #ffffff;
    font-size: 18px;
    font-weight: 900;
    letter-spacing: 1px;
}
QLabel#lbl_section {
    color: rgba(255, 255, 255, 0.85);
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 2px;
}
QLabel#lbl_sidebar_hdr {
    color: rgba(255, 255, 255, 0.5);
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
QLabel#lbl_status_ok  { color: #4ade80; font-weight: bold; }
QLabel#lbl_status_run { color: #facc15; font-weight: bold; }
QLabel#lbl_status_err { color: #f87171; font-weight: bold; }

/* ══════════════════ Buttons — Glass Pills ══════════════════ */
QPushButton {
    background-color: rgba(255, 255, 255, 0.15);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 10px;
    padding: 7px 16px;
    min-height: 28px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.5);
}
QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.8);
    padding-top: 8px; padding-bottom: 6px;
}
QPushButton:disabled {
    color: rgba(255, 255, 255, 0.3);
    background-color: rgba(0, 0, 0, 0.1);
    border-color: rgba(255, 255, 255, 0.1);
}

/* Main Navigation Buttons (Sidebar) */
QPushButton#btn_nav {
    background-color: transparent;
    color: rgba(255, 255, 255, 0.8);
    border: none;
    border-radius: 12px;
    text-align: left;
    padding-left: 20px;
    font-size: 14px;
    height: 40px;
    font-weight: bold;
}
QPushButton#btn_nav:hover {
    background-color: rgba(255, 255, 255, 0.15);
    color: #ffffff;
}
QPushButton#btn_nav:checked {
    background-color: rgba(255, 255, 255, 0.25);
    color: #ffffff;
    border-left: 4px solid #ffffff;
    border-radius: 8px;
}

/* ── Run button (Cyan Glow Pill) ── */
QPushButton#btn_run {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(0, 242, 254, 0.8), stop:1 rgba(79, 172, 254, 0.8));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 14px;
    font-weight: 900;
    font-size: 15px;
    padding: 10px 16px;
    letter-spacing: 1px;
}
QPushButton#btn_run:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(0, 242, 254, 1), stop:1 rgba(79, 172, 254, 1));
    border: 1px solid white;
}
QPushButton#btn_run:disabled {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
}

/* ── Stop button (Magenta Pill) ── */
QPushButton#btn_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 8, 68, 0.7), stop:1 rgba(255, 177, 153, 0.7));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 14px;
    font-weight: 900;
    font-size: 15px;
    padding: 10px 16px;
}
QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 8, 68, 0.9), stop:1 rgba(255, 177, 153, 0.9));
    border: 1px solid white;
}

/* ── Accent button (Test Macro) ── */
QPushButton#btn_test_macro {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(190, 48, 255, 0.6), stop:1 rgba(255, 106, 136, 0.6));
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 10px;
    font-weight: bold;
}
QPushButton#btn_test_macro:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(190, 48, 255, 0.8), stop:1 rgba(255, 106, 136, 0.8));
    border: 1px solid white;
}

/* ── Icon-only mini button ── */
QPushButton#btn_icon {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 4px;
    color: #ffffff;
}
QPushButton#btn_icon:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.6);
}

/* ══════════════════ Input Fields — Dark Glass ══════════════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: rgba(0, 0, 0, 0.25);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 26px;
    selection-background-color: rgba(255, 255, 255, 0.4);
    selection-color: white;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background-color: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.6);
}
QLineEdit:read-only {
    background-color: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.5);
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid rgba(255, 255, 255, 0.8);
    width: 0; height: 0;
}
QComboBox QAbstractItemView {
    background-color: rgba(40, 20, 50, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    selection-background-color: rgba(255, 255, 255, 0.25);
    selection-color: #ffffff;
    color: #ffffff;
    outline: none;
    padding: 4px;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent; border: none; width: 20px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(255, 255, 255, 0.2); border-radius: 4px;
}
QSpinBox::up-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-bottom: 4px solid rgba(255, 255, 255, 0.8);
    width: 0; height: 0;
}
QSpinBox::down-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-top: 4px solid rgba(255, 255, 255, 0.8);
    width: 0; height: 0;
}

/* ══════════════════ List Widget ══════════════════ */
QListWidget {
    background-color: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    outline: none;
    padding: 6px;
}
QListWidget::item {
    border-radius: 6px;
    padding: 10px 12px;
    margin: 2px 0;
    color: rgba(255, 255, 255, 0.85);
}
QListWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.15);
    color: #ffffff;
}
QListWidget::item:selected {
    background-color: rgba(255, 255, 255, 0.25);
    color: #ffffff;
    border-left: 3px solid #00f2fe;
    font-weight: bold;
}

/* ══════════════════ TextEdit (Logs) ══════════════════ */
QTextEdit#log_view {
    background-color: rgba(0, 0, 0, 0.35);
    color: #e2e8f0;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    font-family: Consolas, monospace;
    font-size: 11px;
    padding: 6px;
}

/* ══════════════════ Sliders ══════════════════ */
QSlider::groove:horizontal {
    height: 6px; background: rgba(0, 0, 0, 0.3); border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #C850C0;
    width: 14px; height: 14px; margin: -4px 0; border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    border-color: #4facfe;
    transform: scale(1.1);
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #FFCC70, stop:1 #C850C0);
    border-radius: 3px;
}

/* ══════════════════ Tabs (Trigger Config Inner) ══════════════════ */
QTabWidget::pane { border: none; background: transparent; }
QTabBar::tab {
    background: rgba(0, 0, 0, 0.2); color: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px;
    padding: 8px 16px; margin-right: 6px; margin-bottom: 8px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.25); color: #ffffff;
    font-weight: bold; border: 1px solid rgba(255, 255, 255, 0.5);
}
QTabBar::tab:hover:!selected { background: rgba(255, 255, 255, 0.1); color: #ffffff; }

/* ══════════════════ GroupBox ══════════════════ */
QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px;
    margin-top: 18px; padding-top: 14px;
    background-color: rgba(255, 255, 255, 0.05);
}
QGroupBox::title {
    subcontrol-origin: margin; left: 16px; padding: 0 10px;
    color: rgba(255, 255, 255, 0.8); font-size: 11px; font-weight: bold;
}

/* ══════════════════ CheckBox ══════════════════ */
QCheckBox { color: #ffffff; spacing: 8px; background: transparent; }
QCheckBox::indicator {
    width: 16px; height: 16px; border: 2px solid rgba(255, 255, 255, 0.4);
    border-radius: 4px; background: rgba(0, 0, 0, 0.2);
}
QCheckBox::indicator:hover { border-color: rgba(255, 255, 255, 0.8); }
QCheckBox::indicator:checked {
    background: #00f2fe; border-color: #00f2fe; image: none;
}

/* ══════════════════ Tooltip ══════════════════ */
QToolTip {
    background-color: rgba(20, 10, 30, 0.95); color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.4); border-radius: 6px;
    padding: 6px 10px; font-size: 12px;
}

/* ══════════════════ Separators ══════════════════ */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: rgba(255, 255, 255, 0.2); background-color: rgba(255, 255, 255, 0.2);
}

/* ══════════════════ Progress Bar ══════════════════ */
QProgressBar {
    background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px; height: 8px; text-align: center; color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4facfe, stop:1 #00f2fe);
    border-radius: 4px;
}
"""
