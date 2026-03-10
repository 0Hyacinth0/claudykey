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
    color: #5c4051;
    font-size: 13px;
}

/* ── Main window gradient background (Advanced Pearl Blush Liquid Glass) ── */
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0   #fef1f8,
        stop:0.4 #fff1f2,
        stop:1   #fde2e4
    );
}

/* Common Dialog Background */
QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #fef1f8, stop:1 #fde2e4
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
    background: rgba(0, 0, 0, 0.1);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(0, 0, 0, 0.2); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    border-radius: 3px;
    margin: 1px 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: rgba(0, 0, 0, 0.2); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* ══════════════════ Frosted-Glass Panels (Advanced Refractions) ══════════════════ */
QFrame#sidebar {
    background-color: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-right: 1px solid rgba(255, 255, 255, 0.4);
    border-bottom: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 24px;
}
QFrame#main_area {
    background-color: transparent;
}
QFrame#glass_card {
    background-color: rgba(255, 255, 255, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.85);
    border-right: 1px solid rgba(255, 255, 255, 0.35);
    border-bottom: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 20px;
}
QFrame#sidebar_group {
    background-color: rgba(255, 255, 255, 0.35);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.6);
    padding: 12px;
}

/* ══════════════════ Labels & Headers ══════════════════ */
QLabel {
    background: transparent;
    color: #5c4051;
}
QLabel#lbl_logo {
    color: #ff6b9e;
    font-size: 19px;
    font-weight: 900;
    letter-spacing: 1.5px;
}
QLabel#lbl_section {
    color: #a8728a;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 2px;
}
QLabel#lbl_sidebar_hdr {
    color: rgba(92, 64, 81, 0.5);
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1.5px;
    margin-bottom: 6px;
}
QLabel#lbl_status_ok  { color: #00b4d8; font-weight: bold; }
QLabel#lbl_status_run { color: #d946ef; font-weight: bold; }
QLabel#lbl_status_err { color: #ff4d6d; font-weight: bold; }

/* ══════════════════ Buttons — Refined Pills ══════════════════ */
QPushButton {
    background-color: rgba(255, 255, 255, 0.7);
    color: #5c4051;
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    padding: 8px 18px;
    min-height: 28px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid #ffffff;
    color: #ff6b9e;
}
QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.7);
    padding-top: 9px; padding-bottom: 7px;
}
QPushButton:disabled {
    color: rgba(92, 64, 81, 0.3);
    background-color: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.4);
}

/* Main Navigation Buttons (Sidebar) */
QPushButton#btn_nav {
    background-color: transparent;
    color: rgba(92, 64, 81, 0.6);
    border: none;
    border-radius: 16px;
    text-align: left;
    padding-left: 20px;
    font-size: 14px;
    height: 44px;
    font-weight: bold;
    margin-bottom: 6px;
}
QPushButton#btn_nav:hover {
    background-color: rgba(255, 255, 255, 0.5);
    color: #ff6b9e;
}
QPushButton#btn_nav:checked {
    background-color: rgba(255, 255, 255, 0.9);
    color: #ff6b9e;
    border-right: 4px solid #ff6b9e;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}

/* ── Run button (Rosy Pill) ── */
QPushButton#btn_run {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 126, 179, 0.95), stop:1 rgba(255, 117, 140, 0.95));
    color: white;
    border: 1px solid rgba(255, 126, 179, 0.6);
    border-radius: 18px;
    font-weight: 900;
    font-size: 15px;
    padding: 12px 18px;
    letter-spacing: 1px;
}
QPushButton#btn_run:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 126, 179, 1), stop:1 rgba(255, 117, 140, 1));
}
QPushButton#btn_run:disabled {
    background: rgba(255, 255, 255, 0.4);
    border-color: transparent;
    color: rgba(255, 255, 255, 0.8);
}

/* ── Stop button (Soft Lavender Pill) ── */
QPushButton#btn_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(200, 180, 240, 0.95), stop:1 rgba(150, 190, 255, 0.95));
    color: white;
    border: 1px solid rgba(200, 180, 240, 0.6);
    border-radius: 18px;
    font-weight: 900;
    font-size: 15px;
    padding: 12px 18px;
}
QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(200, 180, 240, 1), stop:1 rgba(150, 190, 255, 1));
}

/* ── Accent button (Test Macro) ── */
QPushButton#btn_test_macro {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 154, 158, 0.85), stop:1 rgba(254, 207, 239, 0.85));
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 14px;
    font-weight: bold;
}
QPushButton#btn_test_macro:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 154, 158, 1), stop:1 rgba(254, 207, 239, 1));
    color: #5c4051;
}

/* ── Icon-only mini button ── */
QPushButton#btn_icon {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 10px;
    padding: 6px;
    color: #ff6b9e;
}
QPushButton#btn_icon:hover {
    background: rgba(255, 255, 255, 0.9);
}

/* ══════════════════ Input Fields — Ultra Soft Fields ══════════════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: rgba(255, 255, 255, 0.65);
    color: #5c4051;
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    padding: 8px 12px;
    min-height: 28px;
    selection-background-color: #ffb8d1;
    selection-color: white;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid #ff6b9e;
}
QLineEdit:read-only {
    background-color: rgba(255, 255, 255, 0.4);
    color: rgba(92, 64, 81, 0.5);
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #ff6b9e;
    width: 0; height: 0;
}
QComboBox QAbstractItemView {
    background-color: #fffafb;
    border: 1px solid #ffb8d1;
    border-radius: 12px;
    selection-background-color: #ffb8d1;
    selection-color: #ffffff;
    color: #5c4051;
    outline: none;
    padding: 6px;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent; border: none; width: 24px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(255, 255, 255, 0.5); border-radius: 6px;
}
QSpinBox::up-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-bottom: 4px solid #ff6b9e;
    width: 0; height: 0;
}
QSpinBox::down-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-top: 4px solid #ff6b9e;
    width: 0; height: 0;
}

/* ══════════════════ List Widget ══════════════════ */
QListWidget {
    background-color: rgba(255, 255, 255, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: 14px;
    outline: none;
    padding: 8px;
    color: #5c4051;
}
QListWidget::item {
    border-radius: 8px;
    padding: 12px 14px;
    margin: 3px 0;
    color: #5c4051;
}
QListWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.6);
    color: #ff6b9e;
}
QListWidget::item:selected {
    background-color: rgba(255, 255, 255, 0.9);
    color: #ff6b9e;
    font-weight: bold;
    /* Soft glowing border on the left rather than solid line */
    border-left: 4px solid #ff6b9e;
}

/* ══════════════════ TextEdit (Logs) ══════════════════ */
QTextEdit#log_view {
    background-color: rgba(255, 255, 255, 0.65);
    color: #8c6a7a;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.85);
    font-family: Consolas, "SF Mono", monospace;
    font-size: 11px;
    padding: 10px;
}

/* ══════════════════ Sliders ══════════════════ */
QSlider::groove:horizontal {
    height: 6px; background: rgba(255, 255, 255, 0.6); border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #ffb8d1;
    width: 16px; height: 16px; margin: -5px 0; border-radius: 9px;
}
QSlider::handle:horizontal:hover {
    border-color: #ff6b9e;
    transform: scale(1.1);
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #fef1f8, stop:1 #ffb8d1);
    border-radius: 3px;
}

/* ══════════════════ Tabs (Trigger Config Inner) ══════════════════ */
QTabWidget::pane { border: none; background: transparent; }
QTabBar::tab {
    background: rgba(255, 255, 255, 0.5); color: rgba(92, 64, 81, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.7); border-radius: 10px;
    padding: 8px 20px; margin-right: 8px; margin-bottom: 10px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.95); color: #ff6b9e;
    font-weight: bold; border: 1px solid #ffffff;
}
QTabBar::tab:hover:!selected { background: rgba(255, 255, 255, 0.8); color: #ff6b9e; }

/* ══════════════════ GroupBox ══════════════════ */
QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.7); border-radius: 16px;
    margin-top: 22px; padding-top: 18px;
    background-color: rgba(255, 255, 255, 0.25);
}
QGroupBox::title {
    subcontrol-origin: margin; left: 18px; padding: 0 12px;
    color: #ff6b9e; font-size: 12px; font-weight: bold;
}

/* ══════════════════ CheckBox ══════════════════ */
QCheckBox { color: #5c4051; spacing: 10px; background: transparent; }
QCheckBox::indicator {
    width: 18px; height: 18px; border: 2px solid rgba(255, 255, 255, 0.9);
    border-radius: 6px; background: rgba(255, 255, 255, 0.6);
}
QCheckBox::indicator:hover { border-color: #ffb8d1; }
QCheckBox::indicator:checked {
    background: #ffb8d1; border-color: #ffb8d1; image: none;
}

/* ══════════════════ Tooltip ══════════════════ */
QToolTip {
    background-color: #fffafb; color: #5c4051;
    border: 1px solid #ffb8d1; border-radius: 8px;
    padding: 8px 12px; font-size: 12px;
}

/* ══════════════════ Separators ══════════════════ */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: rgba(255, 255, 255, 0.7); background-color: rgba(255, 255, 255, 0.7);
}

/* ══════════════════ Progress Bar ══════════════════ */
QProgressBar {
    background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 8px; height: 10px; text-align: center; color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #fef1f8, stop:1 #ffb8d1);
    border-radius: 6px;
}
"""
