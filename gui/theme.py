"""Light pink glassmorphism commercial theme for ClaudyKey."""

THEME_QSS = """
/* ══════════════════ Global ══════════════════ */
QWidget {
    background-color: #faf7f9;
    color: #4a3b42;
    font-family: "Microsoft YaHei UI", "Segoe UI", -apple-system, sans-serif;
    font-size: 13px;
    outline: none;
}
QMainWindow, QDialog {
    background-color: #faf7f9;
}

/* ══════════════════ Scroll bars ══════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: rgba(235, 185, 205, 0.6);
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: rgba(225, 155, 185, 0.8); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: rgba(235, 185, 205, 0.6);
    border-radius: 5px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: rgba(225, 155, 185, 0.8); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ══════════════════ Buttons ══════════════════ */
QPushButton {
    background-color: rgba(255, 255, 255, 0.7);
    color: #5c4553;
    border: 1px solid rgba(240, 200, 215, 0.8);
    border-radius: 8px;
    padding: 6px 14px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: rgba(255, 240, 248, 0.9);
    border-color: #f4b8cc;
    color: #d15c89;
}
QPushButton:pressed {
    background-color: rgba(245, 220, 235, 0.9);
    border-color: #e593b4;
    padding-top: 7px;
    padding-bottom: 5px;
}
QPushButton:disabled {
    color: #a89f102;
    background-color: rgba(250, 245, 248, 0.5);
    border-color: rgba(230, 220, 225, 0.5);
}

QPushButton#btn_run {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #fcf3f8, stop:1 #f4dce8);
    color: #ab4472;
    border: 1px solid #f2c2d6;
    border-radius: 10px;
    font-weight: bold;
    font-size: 14px;
    min-width: 90px;
}
QPushButton#btn_run:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ffffff, stop:1 #fadeed);
    border-color: #eba5c3;
    color: #d1306b;
}

QPushButton#btn_stop {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #fff5f5, stop:1 #fcd5d5);
    color: #c94040;
    border: 1px solid #f2b1b1;
    border-radius: 10px;
    font-weight: bold;
    font-size: 14px;
    min-width: 90px;
}
QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ffffff, stop:1 #fac8c8);
    border-color: #e89595;
}

QPushButton#btn_accent {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #f0a3c2, stop:1 #e074a0);
    color: white;
    border: 1px solid #d45f8f;
    border-radius: 8px;
    font-weight: bold;
}
QPushButton#btn_accent:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #f5b0cd, stop:1 #e88ab1);
}

QPushButton#btn_icon {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 24px;
    max-height: 28px;
    font-size: 14px;
}
QPushButton#btn_icon:hover {
    background: rgba(255, 255, 255, 0.8);
    border-color: rgba(240, 190, 210, 0.6);
}

/* ══════════════════ Input Fields ══════════════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: rgba(255, 255, 255, 0.65);
    color: #4a3b42;
    border: 1px solid rgba(230, 200, 215, 0.7);
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 26px;
    selection-background-color: #f4b8cc;
    selection-color: white;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background-color: white;
    border: 1px solid #e593b4;
}

QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow {
    image: none; /* Can replace with custom caret */
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #cc8ea4;
    width: 0; height: 0;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid #f2c2d6;
    border-radius: 6px;
    selection-background-color: #fdf0f5;
    selection-color: #d15c89;
    color: #5c4553;
    outline: none;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 20px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(245, 220, 230, 0.6);
}
QSpinBox::up-arrow { border-left: 3px solid transparent; border-right: 3px solid transparent; border-bottom: 3px solid #cc8ea4; width:0; height:0;}
QSpinBox::down-arrow { border-left: 3px solid transparent; border-right: 3px solid transparent; border-top: 3px solid #cc8ea4; width:0; height:0;}

/* ══════════════════ List Widget ══════════════════ */
QListWidget {
    background-color: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(240, 215, 225, 0.8);
    border-radius: 8px;
    outline: none;
    padding: 6px;
}
QListWidget::item {
    border-radius: 6px;
    padding: 8px 12px;
    margin: 2px 0;
    color: #634b58;
}
QListWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.7);
    color: #d15c89;
}
QListWidget::item:selected {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #fef4f8, stop:1 #fae6f0);
    color: #bd3f71;
    border-left: 4px solid #e074a0;
    font-weight: bold;
}

/* ══════════════════ Labels ══════════════════ */
QLabel#lbl_section {
    color: #ab6a84;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1.5px;
    background: transparent;
    padding: 8px 0 2px 0;
}
QLabel#lbl_status_ok  { color: #1fa357; }
QLabel#lbl_status_run { color: #d6871a; }
QLabel#lbl_status_err { color: #d94141; }

/* ══════════════════ Sliders ══════════════════ */
QSlider::groove:horizontal {
    height: 6px;
    background: rgba(240, 215, 225, 0.6);
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: white;
    border: 2px solid #e074a0;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 9px;
}
QSlider::handle:horizontal:hover { background: #fdf0f5; }
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #f0a3c2, stop:1 #e074a0);
    border-radius: 3px;
}

/* ══════════════════ Frames / Panels ══════════════════ */
QFrame#sidebar {
    background-color: rgba(252, 245, 249, 0.85);
    border-right: 1px solid rgba(240, 215, 225, 0.8);
}
QFrame#panel_card {
    background-color: rgba(255, 255, 255, 0.65);
    border: 1px solid rgba(245, 225, 235, 0.9);
    border-radius: 12px;
}
QFrame#toolbar {
    background-color: rgba(252, 245, 249, 0.9);
    border-bottom: 1px solid rgba(240, 215, 225, 0.8);
}
QFrame#statusbar_frame {
    background-color: rgba(252, 245, 249, 0.95);
    border-top: 1px solid rgba(240, 215, 225, 0.8);
}

/* ══════════════════ Tabs ══════════════════ */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #9c7b8c;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    margin-right: 4px;
    margin-bottom: 4px;
}
QTabBar::tab:selected {
    background: white;
    color: #d15c89;
    font-weight: bold;
    box-shadow: 0px 2px 5px rgba(220, 180, 200, 0.2);
    border: 1px solid rgba(240, 215, 225, 0.8);
}
QTabBar::tab:hover:!selected {
    background: rgba(255, 255, 255, 0.4);
    color: #805c6d;
}

/* ══════════════════ GroupBox ══════════════════ */
QGroupBox {
    border: 1px solid rgba(235, 205, 220, 0.8);
    border-radius: 10px;
    margin-top: 16px;
    padding-top: 12px;
    background-color: rgba(255, 255, 255, 0.2);
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: #ab6a84;
    font-size: 11px;
    font-weight: bold;
}

/* ══════════════════ CheckBox ══════════════════ */
QCheckBox {
    color: #634b58;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(220, 190, 205, 0.8);
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.7);
}
QCheckBox::indicator:hover { border-color: #f4b8cc; }
QCheckBox::indicator:checked {
    background: #e074a0;
    border-color: #e074a0;
    image: url(''); /* In pure CSS Qt, we rely on color, ideally a check icon SVG goes here */
}

/* ══════════════════ Tooltip ══════════════════ */
QToolTip {
    background-color: rgba(255, 255, 255, 0.95);
    color: #5c4553;
    border: 1px solid #f2c2d6;
    border-radius: 6px;
    padding: 6px 10px;
}

/* ══════════════════ Separators ══════════════════ */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: rgba(240, 215, 225, 0.8);
    background-color: rgba(240, 215, 225, 0.8);
}
"""
