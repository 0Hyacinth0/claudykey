"""ClaudyKey — AI-powered macro clicker entry point."""
import sys
import os
import threading

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QSplashScreen, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from gui.theme import THEME_QSS


def _warm_up_ocr():
    """Pre-load EasyOCR model in background so first use is instant."""
    try:
        from core import ocr
        ocr.warm_up()
    except Exception:
        pass


def main():
    # Qt6 handles high-DPI natively, no manual ctypes call needed
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName('ClaudyKey')
    app.setApplicationDisplayName('ClaudyKey')
    app.setStyle('Fusion')
    app.setStyleSheet(THEME_QSS)

    # Splash screen
    splash = QSplashScreen()
    splash.setFixedSize(420, 200)
    splash.setStyleSheet("""
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #fff0f5, stop:1 #ffe6ee);
        border: 1px solid #f2c2d6;
        border-radius: 10px;
    """)
    splash_lbl = QLabel(splash)
    splash_lbl.setGeometry(0, 0, 420, 200)
    splash_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    splash_lbl.setText(
        '<span style="color:#d15c89;font-size:32px;font-weight:bold;">'
        '⌨ ClaudyKey</span><br>'
        '<br><span style="color:#9c7b8c;font-size:13px;">AI 智能连点器  正在启动…</span>'
    )
    splash_lbl.setTextFormat(Qt.TextFormat.RichText)
    splash.show()
    app.processEvents()

    # Start OCR warm-up in background
    threading.Thread(target=_warm_up_ocr, daemon=True).start()

    # Import and create main window
    from gui.main_window import MainWindow
    window = MainWindow()

    def _show():
        splash.finish(window)
        window.show()

    QTimer.singleShot(800, _show)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
