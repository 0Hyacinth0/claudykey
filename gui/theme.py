"""Dark cyberpunk theme for ClaudyKey."""

THEME_QSS = """
/* ══════════════════ Global ══════════════════ */
QWidget {
    background-color: #0d0d1f;
    color: #c8ccff;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 13px;
    outline: none;
}
QMainWindow, QDialog {
    background-color: #0d0d1f;
}

/* ══════════════════ Scroll bars ══════════════════ */
QScrollBar:vertical {
    background: #13132a;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #3030a0;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #13132a;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #3030a0;
    border-radius: 4px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ══════════════════ Buttons ══════════════════ */
QPushButton {
    background-color: #1b1b3a;
    color: #c8ccff;
    border: 1px solid #2e2e6a;
    border-radius: 6px;
    padding: 6px 14px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #252558;
    border-color: #5050cc;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #16163a;
    border-color: #7070ff;
}
QPushButton:disabled {
    color: #444466;
    border-color: #1e1e40;
}
QPushButton#btn_run {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0f7a3a, stop:1 #0a5a2a);
    color: #00ff90;
    border: 1px solid #00cc60;
    font-weight: bold;
    font-size: 14px;
    min-width: 90px;
}
QPushButton#btn_run:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #12a04c, stop:1 #0c7035);
}
QPushButton#btn_stop {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #7a1515, stop:1 #5a0f0f);
    color: #ff6060;
    border: 1px solid #cc3030;
    font-weight: bold;
    font-size: 14px;
    min-width: 90px;
}
QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #a01a1a, stop:1 #7a1212);
}
QPushButton#btn_accent {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #2a0a7a, stop:1 #1a1a8a);
    color: #a0b0ff;
    border: 1px solid #5050cc;
}
QPushButton#btn_accent:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #3a0fa0, stop:1 #2525b0);
    color: #ffffff;
}
QPushButton#btn_icon {
    background: transparent;
    border: 1px solid #2a2a55;
    border-radius: 5px;
    padding: 4px 8px;
    min-height: 24px;
    max-height: 28px;
    font-size: 14px;
}
QPushButton#btn_icon:hover {
    background: #252558;
    border-color: #5050cc;
}

/* ══════════════════ Line Edits ══════════════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #11112a;
    color: #c8ccff;
    border: 1px solid #2a2a55;
    border-radius: 5px;
    padding: 4px 8px;
    min-height: 26px;
    selection-background-color: #3a3acc;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: #5a5aff;
    background-color: #14143a;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background-color: #13132a;
    border: 1px solid #3030a0;
    selection-background-color: #2a2a7a;
    color: #c8ccff;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: #1e1e45;
    border: none;
    width: 18px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: #2a2a60;
}

/* ══════════════════ List Widget ══════════════════ */
QListWidget {
    background-color: #0f0f22;
    border: 1px solid #1e1e45;
    border-radius: 6px;
    outline: none;
    padding: 4px;
}
QListWidget::item {
    border-radius: 4px;
    padding: 6px 10px;
    margin: 1px 0;
    color: #b0b4e8;
}
QListWidget::item:hover {
    background-color: #1a1a40;
    color: #e0e4ff;
}
QListWidget::item:selected {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #1e1e6a, stop:1 #2a2a4a);
    color: #ffffff;
    border-left: 3px solid #6060ff;
}

/* ══════════════════ Labels ══════════════════ */
QLabel#lbl_section {
    color: #5a5aff;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.8px;
    background: transparent;
    padding: 6px 0 2px 0;
}
QLabel#lbl_status_ok  { color: #00cc60; }
QLabel#lbl_status_run { color: #ffaa00; }
QLabel#lbl_status_err { color: #ff4444; }

/* ══════════════════ Sliders ══════════════════ */
QSlider::groove:horizontal {
    height: 4px;
    background: #1e1e45;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #5a5aff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #3030cc, stop:1 #6060ff);
    border-radius: 2px;
}

/* ══════════════════ Frames / Panels ══════════════════ */
QFrame#sidebar {
    background-color: #0b0b1e;
    border-right: 1px solid #1a1a40;
}
QFrame#panel_card {
    background-color: #111128;
    border: 1px solid #1e1e45;
    border-radius: 8px;
}
QFrame#toolbar {
    background-color: #0a0a1a;
    border-bottom: 1px solid #1a1a40;
}
QFrame#statusbar_frame {
    background-color: #0a0a1a;
    border-top: 1px solid #1a1a40;
}

/* ══════════════════ Tabs ══════════════════ */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: #11112a;
    color: #7070aa;
    border: 1px solid #1e1e45;
    border-radius: 6px 6px 0 0;
    padding: 8px 18px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #1a1a40;
    color: #c8ccff;
    border-bottom: 2px solid #5a5aff;
}
QTabBar::tab:hover:!selected {
    background: #161635;
    color: #a0a4d0;
}

/* ══════════════════ GroupBox ══════════════════ */
QGroupBox {
    border: 1px solid #1e1e50;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 8px;
    color: #7070cc;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    background-color: #0d0d1f;
}

/* ══════════════════ CheckBox ══════════════════ */
QCheckBox {
    color: #a0a4d0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #3030a0;
    border-radius: 3px;
    background: #11112a;
}
QCheckBox::indicator:checked {
    background: #3a3acc;
    border-color: #6060ff;
}

/* ══════════════════ Tooltip ══════════════════ */
QToolTip {
    background-color: #1a1a40;
    color: #c8ccff;
    border: 1px solid #4040a0;
    border-radius: 4px;
    padding: 4px 8px;
}

/* ══════════════════ Separators ══════════════════ */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #1e1e45;
    background-color: #1e1e45;
}
"""
