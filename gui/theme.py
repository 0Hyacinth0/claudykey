"""Premium light-pink glassmorphism theme for ClaudyKey.

Design principles:
  • Soft pink-lavender gradient background provides depth
  • Frosted-glass panels with translucent white + subtle borders
  • Elevated cards with layered shadow borders
  • Pill-shaped buttons with gradient fills
  • Modern typography with generous spacing
"""

THEME_QSS = """
/* ══════════════════ Global Reset ══════════════════ */
* {
    outline: none;
    font-family: "Microsoft YaHei UI", "Segoe UI", "SF Pro Display",
                 -apple-system, "Noto Sans SC", sans-serif;
}

QWidget {
    color: #4e3a46;
    font-size: 13px;
}

/* ── Main window gradient background ── */
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0   #fdf2f8,
        stop:0.3 #fce7f3,
        stop:0.6 #f3e8ff,
        stop:1   #ede9fe
    );
}
QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #fdf2f8, stop:1 #f3e8ff
    );
}

/* ══════════════════ Scrollbars (barely visible) ══════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    border-radius: 3px;
    margin: 4px 1px;
}
QScrollBar::handle:vertical {
    background: rgba(219, 160, 190, 0.45);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(215, 130, 170, 0.65); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; height: 0; }

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    border-radius: 3px;
    margin: 1px 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(219, 160, 190, 0.45);
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: rgba(215, 130, 170, 0.65); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; width: 0; }

/* ══════════════════ Frosted-Glass Panels ══════════════════ */
QFrame#toolbar {
    background-color: rgba(255, 255, 255, 0.55);
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.5);
}

QFrame#sidebar {
    background-color: rgba(255, 255, 255, 0.35);
    border: none;
    border-right: 1px solid rgba(255, 255, 255, 0.45);
}

QFrame#statusbar_frame {
    background-color: rgba(255, 255, 255, 0.45);
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.5);
}

QFrame#panel_card {
    background-color: rgba(255, 255, 255, 0.50);
    border: 1px solid rgba(255, 255, 255, 0.65);
    border-radius: 14px;
    padding: 6px;
}

QFrame#glass_card {
    background-color: rgba(255, 255, 255, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: 16px;
}

/* ══════════════════ Buttons — Pill Style ══════════════════ */
QPushButton {
    background-color: rgba(255, 255, 255, 0.55);
    color: #6b4e5e;
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 10px;
    padding: 7px 16px;
    min-height: 28px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.80);
    border: 1px solid rgba(244, 184, 204, 0.6);
    color: #c94080;
}
QPushButton:pressed {
    background-color: rgba(252, 231, 243, 0.85);
    border: 1px solid rgba(236, 152, 186, 0.7);
    padding-top: 8px;
    padding-bottom: 6px;
}
QPushButton:disabled {
    color: rgba(150, 130, 140, 0.5);
    background-color: rgba(245, 240, 242, 0.35);
    border-color: rgba(220, 210, 215, 0.3);
}

/* ── Run button (gradient pink pill) ── */
QPushButton#btn_run {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(251, 191, 213, 0.85),
        stop:1 rgba(244, 144, 184, 0.85));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-radius: 14px;
    font-weight: bold;
    font-size: 14px;
    min-width: 100px;
    padding: 8px 20px;
    letter-spacing: 0.5px;
}
QPushButton#btn_run:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(252, 207, 224, 0.95),
        stop:1 rgba(248, 162, 198, 0.95));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.65);
}
QPushButton#btn_run:disabled {
    background: rgba(230, 215, 222, 0.4);
    color: rgba(180, 160, 170, 0.6);
    border: 1px solid rgba(220, 210, 215, 0.3);
}

/* ── Stop button (gradient rose pill) ── */
QPushButton#btn_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(254, 178, 178, 0.80),
        stop:1 rgba(248, 130, 130, 0.80));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-radius: 14px;
    font-weight: bold;
    font-size: 14px;
    min-width: 100px;
    padding: 8px 20px;
}
QPushButton#btn_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 195, 195, 0.95),
        stop:1 rgba(252, 150, 150, 0.95));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.65);
}
QPushButton#btn_stop:disabled {
    background: rgba(230, 215, 218, 0.4);
    color: rgba(180, 160, 165, 0.6);
    border: 1px solid rgba(220, 210, 215, 0.3);
}

/* ── Accent button ── */
QPushButton#btn_accent {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ec8db7, stop:1 #d35d8e);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    font-weight: bold;
}
QPushButton#btn_accent:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f0a3c6, stop:1 #db72a0);
    border: 1px solid rgba(255, 255, 255, 0.5);
}

/* ── Icon-only mini button ── */
QPushButton#btn_icon {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 4px 8px;
    min-height: 24px;
    max-height: 28px;
    font-size: 14px;
    color: #a0889a;
}
QPushButton#btn_icon:hover {
    background: rgba(255, 255, 255, 0.65);
    border-color: rgba(244, 184, 210, 0.5);
    color: #c94080;
}

/* ── Test macro button ── */
QPushButton#btn_test_macro {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(167, 139, 250, 0.60),
        stop:1 rgba(192, 132, 252, 0.60));
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 10px;
    font-weight: bold;
    padding: 8px 18px;
}
QPushButton#btn_test_macro:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(167, 139, 250, 0.80),
        stop:1 rgba(192, 132, 252, 0.80));
    border: 1px solid rgba(255, 255, 255, 0.55);
}

/* ══════════════════ Input Fields — Glass Style ══════════════════ */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: rgba(255, 255, 255, 0.50);
    color: #4e3a46;
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: 10px;
    padding: 6px 12px;
    min-height: 28px;
    selection-background-color: rgba(236, 141, 183, 0.5);
    selection-color: white;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background-color: rgba(255, 255, 255, 0.75);
    border: 1.5px solid rgba(236, 141, 183, 0.55);
}
QLineEdit:read-only {
    background-color: rgba(255, 255, 255, 0.25);
    color: #8a7080;
}

QComboBox::drop-down {
    border: none;
    width: 26px;
    subcontrol-position: right center;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid rgba(180, 140, 165, 0.7);
    width: 0; height: 0;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: 10px;
    selection-background-color: rgba(252, 231, 243, 0.85);
    selection-color: #c94080;
    color: #4e3a46;
    outline: none;
    padding: 4px;
}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 22px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(252, 231, 243, 0.5);
    border-radius: 4px;
}
QSpinBox::up-arrow {
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-bottom: 4px solid rgba(180, 140, 165, 0.65);
    width: 0; height: 0;
}
QSpinBox::down-arrow {
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid rgba(180, 140, 165, 0.65);
    width: 0; height: 0;
}

/* ══════════════════ List Widget — Glass Cards ══════════════════ */
QListWidget {
    background-color: rgba(255, 255, 255, 0.30);
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-radius: 12px;
    outline: none;
    padding: 6px;
}
QListWidget::item {
    border-radius: 8px;
    padding: 9px 14px;
    margin: 2px 0;
    color: #5c4553;
}
QListWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.55);
    color: #c94080;
}
QListWidget::item:selected {
    background-color: rgba(255, 255, 255, 0.65);
    color: #be3a72;
    border-left: 4px solid rgba(236, 141, 183, 0.75);
    font-weight: bold;
}

/* ══════════════════ Labels ══════════════════ */
QLabel {
    background: transparent;
    color: #5c4553;
}
QLabel#lbl_section {
    color: rgba(160, 100, 135, 0.85);
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: transparent;
    padding: 10px 0 4px 2px;
}
QLabel#lbl_status_ok  { color: #22a861; font-weight: bold; }
QLabel#lbl_status_run { color: #d4781a; font-weight: bold; }
QLabel#lbl_status_err { color: #dc4343; font-weight: bold; }

QLabel#lbl_logo {
    color: transparent;
    font-size: 16px;
    font-weight: 900;
    letter-spacing: 1px;
}

/* ══════════════════ Sliders ══════════════════ */
QSlider::groove:horizontal {
    height: 5px;
    background: rgba(219, 190, 210, 0.35);
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(236, 141, 183, 0.65);
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: white;
    border-color: rgba(225, 100, 155, 0.8);
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(251, 191, 213, 0.75),
        stop:1 rgba(236, 141, 183, 0.75));
    border-radius: 2px;
}

/* ══════════════════ Tabs ══════════════════ */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: rgba(140, 110, 125, 0.7);
    border: none;
    border-radius: 10px;
    padding: 8px 22px;
    margin-right: 4px;
    margin-bottom: 4px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.6);
    color: #c94080;
    font-weight: bold;
    border: 1px solid rgba(255, 255, 255, 0.5);
}
QTabBar::tab:hover:!selected {
    background: rgba(255, 255, 255, 0.35);
    color: #7a5c6d;
}

/* ══════════════════ GroupBox ══════════════════ */
QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 14px;
    margin-top: 18px;
    padding-top: 14px;
    background-color: rgba(255, 255, 255, 0.2);
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 10px;
    color: rgba(160, 100, 135, 0.85);
    font-size: 11px;
    font-weight: bold;
}

/* ══════════════════ CheckBox ══════════════════ */
QCheckBox {
    color: #5c4553;
    spacing: 10px;
    background: transparent;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(200, 175, 190, 0.6);
    border-radius: 5px;
    background: rgba(255, 255, 255, 0.5);
}
QCheckBox::indicator:hover {
    border-color: rgba(236, 141, 183, 0.7);
    background: rgba(255, 255, 255, 0.75);
}
QCheckBox::indicator:checked {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #ec8db7, stop:1 #d35d8e);
    border-color: rgba(236, 141, 183, 0.8);
    image: none;
}

/* ══════════════════ Tooltip ══════════════════ */
QToolTip {
    background-color: rgba(255, 255, 255, 0.92);
    color: #4e3a46;
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}

/* ══════════════════ Splitter ══════════════════ */
QSplitter::handle {
    background: rgba(219, 190, 210, 0.3);
    border-radius: 2px;
}
QSplitter::handle:hover {
    background: rgba(219, 160, 190, 0.5);
}

/* ══════════════════ Separators ══════════════════ */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: rgba(255, 255, 255, 0.4);
    background-color: rgba(255, 255, 255, 0.4);
}

/* ══════════════════ Menu Bar ══════════════════ */
QMenuBar {
    background: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}
QMenuBar::item {
    background: transparent;
    color: #6b4e5e;
    padding: 6px 14px;
    border-radius: 6px;
}
QMenuBar::item:selected {
    background: rgba(255, 255, 255, 0.55);
}
QMenu {
    background-color: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 10px;
    padding: 6px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 6px;
    color: #4e3a46;
}
QMenu::item:selected {
    background-color: rgba(252, 231, 243, 0.8);
    color: #c94080;
}

/* ══════════════════ Progress Bar ══════════════════ */
QProgressBar {
    background: rgba(255, 255, 255, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-radius: 6px;
    height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #ec8db7, stop:1 #d35d8e);
    border-radius: 5px;
}
"""
