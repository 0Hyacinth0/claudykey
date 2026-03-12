"""Dark Professional Theme for ClaudyKey.

Design principles:
  • Deep charcoal/navy base (#12131a → #1a1b26) — premium feel.
  • Frosted glass panels with subtle light refraction.
  • Electric blue-violet accent (#7c6ef8 / #6366f1) for interactive states.
  • Teal-cyan secondary for status indicators and special labels.
  • Clean, readable text (#e1e4f0) for legibility.
"""

THEME_QSS = """
/* ══════════════════ Global Reset ══════════════════ */
* {
    outline: none;
    font-family: "Microsoft YaHei UI", "Segoe UI Variable", "Segoe UI", "SF Pro Display", -apple-system, sans-serif;
}

QWidget {
    color: #dde1f0;
    font-size: 13px;
    background: transparent;
}

/* ── Main window dark gradient ── */
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0   #12131a,
        stop:0.5 #171826,
        stop:1   #11111e
    );
}

/* Common Dialog Background */
QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1b2e, stop:1 #0f0f1a
    );
}

/* ══════════════════ Scrollbars ══════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    border-radius: 3px;
    margin: 4px 1px;
}
QScrollBar::handle:vertical {
    background: rgba(124, 110, 248, 0.35);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(124, 110, 248, 0.6); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    border-radius: 3px;
    margin: 1px 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(124, 110, 248, 0.35);
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: rgba(124, 110, 248, 0.6); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* ══════════════════ Glass Panels ══════════════════ */
QFrame#sidebar {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
}
QFrame#main_area {
    background-color: transparent;
}
QFrame#glass_card {
    background-color: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
}
QFrame#sidebar_group {
    background-color: rgba(255, 255, 255, 0.04);
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.07);
    padding: 10px;
}

/* ══════════════════ Labels ══════════════════ */
QLabel {
    background: transparent;
    color: #dde1f0;
}
QLabel#lbl_logo {
    color: #8b8cf8;
    font-size: 18px;
    font-weight: 900;
    letter-spacing: 1px;
}
QLabel#lbl_section {
    color: #7c6ef8;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 0.5px;
    padding: 2px;
}
QLabel#lbl_sidebar_hdr {
    color: rgba(180, 185, 220, 0.45);
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    margin-bottom: 4px;
    text-transform: uppercase;
}
QLabel#lbl_status_ok  { color: #4ade80; font-weight: bold; }
QLabel#lbl_status_run { color: #a78bfa; font-weight: bold; }
QLabel#lbl_status_err { color: #f87171; font-weight: bold; }

/* ══════════════════ Buttons ══════════════════ */
QPushButton {
    background-color: rgba(255, 255, 255, 0.06);
    color: #c8cde8;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 7px 16px;
    min-height: 28px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: rgba(124, 110, 248, 0.15);
    border: 1px solid rgba(124, 110, 248, 0.4);
    color: #a5b4fc;
}
QPushButton:pressed {
    background-color: rgba(124, 110, 248, 0.25);
    border-color: rgba(124, 110, 248, 0.5);
    padding-top: 8px; padding-bottom: 6px;
}
QPushButton:disabled {
    color: rgba(200, 205, 232, 0.2);
    background-color: rgba(255, 255, 255, 0.02);
    border-color: rgba(255, 255, 255, 0.04);
}

/* Sidebar Navigation */
QPushButton#btn_nav {
    background-color: transparent;
    color: rgba(200, 205, 232, 0.45);
    border: none;
    border-radius: 12px;
    text-align: left;
    padding-left: 18px;
    font-size: 13px;
    height: 42px;
    font-weight: 600;
    margin-bottom: 4px;
}
QPushButton#btn_nav:hover {
    background-color: rgba(124, 110, 248, 0.12);
    color: #a5b4fc;
}
QPushButton#btn_nav:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(99, 102, 241, 0.25), stop:1 rgba(99, 102, 241, 0.05));
    color: #a5b4fc;
    border-left: 3px solid #7c6ef8;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    padding-left: 15px;
}

/* ── Run button (Electric Violet) ── */
QPushButton#btn_run {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #6366f1, stop:1 #4f46e5);
    color: #ffffff;
    border: 1px solid rgba(99, 102, 241, 0.5);
    border-radius: 14px;
    font-weight: 800;
    font-size: 14px;
    padding: 12px 18px;
    letter-spacing: 0.5px;
}
QPushButton#btn_run:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #818cf8, stop:1 #6366f1);
    border-color: rgba(129, 140, 248, 0.7);
}
QPushButton#btn_run:disabled {
    background: rgba(255, 255, 255, 0.05);
    border-color: transparent;
    color: rgba(255, 255, 255, 0.2);
}

/* ── Stop button (Warm Crimson) ── */
QPushButton#btn_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(239, 68, 68, 0.75), stop:1 rgba(220, 38, 38, 0.75));
    color: white;
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 14px;
    font-weight: 800;
    font-size: 14px;
    padding: 12px 18px;
}
QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(248, 113, 113, 0.9), stop:1 rgba(239, 68, 68, 0.9));
    border-color: rgba(248, 113, 113, 0.6);
}
QPushButton#btn_stop:disabled {
    background: rgba(255, 255, 255, 0.05);
    border-color: transparent;
    color: rgba(255, 255, 255, 0.2);
}

/* ── Accent button (Teal-Cyan) ── */
QPushButton#btn_test_macro {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 184, 166, 0.3), stop:1 rgba(6, 182, 212, 0.3));
    color: #5eead4;
    border: 1px solid rgba(20, 184, 166, 0.4);
    border-radius: 10px;
    font-weight: bold;
}
QPushButton#btn_test_macro:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 184, 166, 0.5), stop:1 rgba(6, 182, 212, 0.5));
    color: #99f6e4;
    border-color: rgba(94, 234, 212, 0.65);
}

/* ── Icon-only mini button ── */
QPushButton#btn_icon {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 8px;
    padding: 5px;
    color: #8b8cf8;
}
QPushButton#btn_icon:hover {
    background: rgba(124, 110, 248, 0.18);
    border-color: rgba(124, 110, 248, 0.4);
    color: #c4c6ff;
}

/* ══════════════════ Input Fields ══════════════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: rgba(255, 255, 255, 0.05);
    color: #dde1f0;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 7px 12px;
    min-height: 28px;
    selection-background-color: rgba(124, 110, 248, 0.5);
    selection-color: white;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background-color: rgba(124, 110, 248, 0.08);
    border: 1px solid rgba(124, 110, 248, 0.55);
}
QLineEdit:read-only {
    background-color: rgba(255, 255, 255, 0.02);
    color: rgba(200, 205, 232, 0.35);
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #7c6ef8;
    width: 0; height: 0;
}
QComboBox QAbstractItemView {
    background-color: #1e2033;
    border: 1px solid rgba(124, 110, 248, 0.3);
    border-radius: 10px;
    selection-background-color: rgba(99, 102, 241, 0.4);
    selection-color: #c4c6ff;
    color: #c8cde8;
    outline: none;
    padding: 6px;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent; border: none; width: 24px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(124, 110, 248, 0.2); border-radius: 6px;
}
QSpinBox::up-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-bottom: 4px solid #7c6ef8;
    width: 0; height: 0;
}
QSpinBox::down-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-top: 4px solid #7c6ef8;
    width: 0; height: 0;
}
QDoubleSpinBox::up-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-bottom: 4px solid #7c6ef8;
    width: 0; height: 0;
}
QDoubleSpinBox::down-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-top: 4px solid #7c6ef8;
    width: 0; height: 0;
}

/* ══════════════════ List Widget ══════════════════ */
QListWidget {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    outline: none;
    padding: 6px;
    color: #c8cde8;
}
QListWidget::item {
    border-radius: 8px;
    padding: 10px 14px;
    margin: 2px 0;
    color: #c8cde8;
}
QListWidget::item:hover {
    background-color: rgba(124, 110, 248, 0.1);
    color: #a5b4fc;
}
QListWidget::item:selected {
    background-color: rgba(99, 102, 241, 0.2);
    color: #c4c6ff;
    font-weight: bold;
    border-left: 3px solid #7c6ef8;
}

/* ══════════════════ TextEdit (Logs) ══════════════════ */
QTextEdit#log_view {
    background-color: rgba(10, 10, 20, 0.5);
    color: #7c9cbf;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    font-family: "JetBrains Mono", Consolas, "Cascadia Code", "SF Mono", monospace;
    font-size: 11px;
    padding: 10px;
}

/* ══════════════════ Sliders ══════════════════ */
QSlider::groove:horizontal {
    height: 5px; background: rgba(255, 255, 255, 0.1); border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #7c6ef8;
    border: 2px solid #a5b4fc;
    width: 14px; height: 14px; margin: -5px 0; border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #a5b4fc;
    border-color: #c4cbff;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #4f46e5, stop:1 #7c6ef8);
    border-radius: 3px;
}

/* ══════════════════ Tabs ══════════════════ */
QTabWidget::pane { border: none; background: transparent; }
QTabBar::tab {
    background: rgba(255, 255, 255, 0.04); color: rgba(200, 205, 232, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 9px;
    padding: 7px 18px; margin-right: 6px; margin-bottom: 8px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: rgba(99, 102, 241, 0.2); color: #a5b4fc;
    font-weight: bold; border: 1px solid rgba(124, 110, 248, 0.45);
}
QTabBar::tab:hover:!selected { background: rgba(124, 110, 248, 0.1); color: #a5b4fc; }

/* ══════════════════ GroupBox ══════════════════ */
QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px;
    margin-top: 20px; padding-top: 16px;
    background-color: rgba(255, 255, 255, 0.025);
}
QGroupBox::title {
    subcontrol-origin: margin; left: 16px; padding: 0 10px;
    color: #7c6ef8; font-size: 11px; font-weight: bold; letter-spacing: 1px;
}

/* ══════════════════ CheckBox ══════════════════ */
QCheckBox { color: #c8cde8; spacing: 10px; background: transparent; }
QCheckBox::indicator {
    width: 17px; height: 17px; border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 5px; background: rgba(255, 255, 255, 0.04);
}
QCheckBox::indicator:hover { border-color: rgba(124, 110, 248, 0.6); }
QCheckBox::indicator:checked {
    background: rgba(99, 102, 241, 0.7); border-color: #7c6ef8;
}

/* ══════════════════ Tooltip ══════════════════ */
QToolTip {
    background-color: #1e2033; color: #c8cde8;
    border: 1px solid rgba(124, 110, 248, 0.35); border-radius: 7px;
    padding: 7px 11px; font-size: 12px;
}

/* ══════════════════ Separators ══════════════════ */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: rgba(255, 255, 255, 0.08); background-color: rgba(255, 255, 255, 0.08);
    max-height: 1px;
}

/* ══════════════════ Progress Bar ══════════════════ */
QProgressBar {
    background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 7px; height: 8px; text-align: center; color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4f46e5, stop:1 #7c6ef8);
    border-radius: 5px;
}
"""
