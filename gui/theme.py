"""Light Pink Liquid Glass Dashboard theme for ClaudyKey.

Design principles:
  • Soft, luminous light-pink to pale-blue liquid gradient (`#fad0c4` -> `#ff9a9e` -> `#fecfef`).
  • Frosted-glass panels with light reflection styling.
  • Text uses darker pinkish-gray `#4e3a46` for legibility and visual comfort instead of pure white.
  • Bright, smooth pills for buttons with vibrant pink/cyan glow states.
"""

"""Light and Dark Liquid Glass Themes."""

def get_theme_qss(is_dark: bool) -> str:
    if not is_dark:
        # ── LIGHT THEME ──
        return """
* { outline: none; font-family: "Microsoft YaHei UI", "SF Pro Display", -apple-system, sans-serif; }
QWidget { color: #333333; font-size: 13px; }

QMainWindow, QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #ffafcc, stop:0.4 #fecfef, stop:1 #a1c4fd
    );
}

/* Scrollbars */
QScrollBar:vertical { background: transparent; width: 6px; margin: 2px; }
QScrollBar::handle:vertical { background: rgba(0,0,0,0.15); border-radius: 3px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: rgba(0,0,0,0.25); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; }
QScrollBar:horizontal { background: transparent; height: 6px; margin: 2px; }
QScrollBar::handle:horizontal { background: rgba(0,0,0,0.15); border-radius: 3px; min-width: 20px; }

/* Panels */
QFrame#sidebar { background-color: rgba(255, 255, 255, 0.45); border-radius: 12px; }
QFrame#macros_panel { background-color: rgba(255, 255, 255, 0.35); border-radius: 12px; }
QFrame#editor_panel { background-color: rgba(255, 255, 255, 0.25); border-radius: 12px; }
QFrame#status_bar { background-color: rgba(255, 255, 255, 0.4); border-radius: 12px; }

/* Traffic Lights */
QPushButton#mac_red { background-color: #ff5f56; border-radius: 6px; border: none; }
QPushButton#mac_yel { background-color: #ffbd2e; border-radius: 6px; border: none; }
QPushButton#mac_grn { background-color: #27c93f; border-radius: 6px; border: none; }

/* Sidebar Navigation */
QPushButton#btn_nav {
    background-color: transparent; color: #444; text-align: left;
    padding-left: 12px; border-radius: 10px; font-weight: bold; font-size: 12px; height: 40px;
}
QPushButton#btn_nav:hover { background-color: rgba(255,255,255,0.4); }
QPushButton#btn_nav:checked {
    background-color: rgba(255,255,255,0.8);
    border-left: 4px solid #0078d7; border-top-left-radius: 10px; border-bottom-left-radius: 10px;
}

QPushButton#btn_macro_mgr {
    background-color: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.9);
    border-radius: 12px; font-weight: bold; color: #444;
}
QPushButton#btn_macro_mgr:hover { background-color: rgba(255,255,255,0.9); }

/* List Widget (Macros) */
QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { background: rgba(255,255,255,0.5); border-radius: 10px; padding: 10px; margin: 4px; color: #333; }
QListWidget::item:hover { background: rgba(255,255,255,0.7); }
QListWidget::item:selected { background: rgba(255,255,255,0.9); border: 1px solid #ffffff; font-weight: bold; }

/* Labels */
QLabel#lbl_title { font-size: 16px; font-weight: bold; color: #222; }
QLabel#lbl_status { font-size: 12px; color: #333; }

/* Pills (Actions in Editor) */
QFrame#action_pill {
    background: rgba(255,255,255,0.6);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 12px;
}
QPushButton#btn_icon_tool { background: transparent; border: none; color: #444; font-size: 16px; padding: 4px; }
QPushButton#btn_icon_tool:hover { background: rgba(255,255,255,0.8); border-radius: 6px; }

/* Sub Controls */
QLineEdit, QSpinBox {
    background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.9);
    border-radius: 8px; padding: 4px 8px; color: #333;
}
QComboBox {
    background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.9);
    border-radius: 8px; padding: 4px 8px; color: #333;
}
QComboBox::drop-down { border: none; }
QComboBox::down-arrow { border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #444; }
"""
    else:
        # ── DARK THEME ──
        return """
* { outline: none; font-family: "Microsoft YaHei UI", "SF Pro Display", -apple-system, sans-serif; }
QWidget { color: #e0e0e0; font-size: 13px; }

QMainWindow, QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460
    );
}

/* Scrollbars */
QScrollBar:vertical { background: transparent; width: 6px; margin: 2px; }
QScrollBar::handle:vertical { background: rgba(255,255,255,0.15); border-radius: 3px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.3); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; }
QScrollBar:horizontal { background: transparent; height: 6px; margin: 2px; }
QScrollBar::handle:horizontal { background: rgba(255,255,255,0.15); border-radius: 3px; min-width: 20px; }

/* Panels */
QFrame#sidebar { background-color: rgba(20, 20, 35, 0.4); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
QFrame#macros_panel { background-color: rgba(30, 30, 50, 0.35); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
QFrame#editor_panel { background-color: rgba(30, 30, 50, 0.25); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
QFrame#status_bar { background-color: rgba(20, 20, 35, 0.4); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }

/* Traffic Lights */
QPushButton#mac_red { background-color: #ff5f56; border-radius: 6px; border: none; }
QPushButton#mac_yel { background-color: #ffbd2e; border-radius: 6px; border: none; }
QPushButton#mac_grn { background-color: #27c93f; border-radius: 6px; border: none; }

/* Sidebar Navigation */
QPushButton#btn_nav {
    background-color: transparent; color: #aaa; text-align: left;
    padding-left: 12px; border-radius: 10px; font-weight: bold; font-size: 12px; height: 40px;
}
QPushButton#btn_nav:hover { background-color: rgba(255,255,255,0.08); color: #ddd; }
QPushButton#btn_nav:checked {
    background-color: rgba(255,255,255,0.12);
    border-left: 4px solid #00f0ff; color: #fff; border-top-left-radius: 10px; border-bottom-left-radius: 10px;
}

QPushButton#btn_macro_mgr {
    background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px; font-weight: bold; color: #ddd;
}
QPushButton#btn_macro_mgr:hover { background-color: rgba(255,255,255,0.15); border-color: rgba(255,255,255,0.3); }

/* List Widget (Macros) */
QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 10px; margin: 4px; color: #ddd; }
QListWidget::item:hover { background: rgba(255,255,255,0.1); }
QListWidget::item:selected { background: rgba(0, 240, 255, 0.1); border: 1px solid #a855f7; font-weight: bold; color: #fff; }

/* Labels */
QLabel#lbl_title { font-size: 16px; font-weight: bold; color: #f0f0f0; }
QLabel#lbl_status { font-size: 12px; color: #bbb; }

/* Pills (Actions in Editor) */
QFrame#action_pill {
    background: rgba(40, 40, 60, 0.4);
    border: 1px solid rgba(0, 240, 255, 0.3);
    border-radius: 12px;
}
QPushButton#btn_icon_tool { background: transparent; border: none; color: #ccc; font-size: 16px; padding: 4px; }
QPushButton#btn_icon_tool:hover { background: rgba(255,255,255,0.15); border-radius: 6px; color: #fff; }

/* Sub Controls */
QLineEdit, QSpinBox {
    background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px; padding: 4px 8px; color: #e0e0e0;
}
QComboBox {
    background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px; padding: 4px 8px; color: #e0e0e0;
}
QComboBox::drop-down { border: none; }
QComboBox::down-arrow { border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #aaa; }
"""

