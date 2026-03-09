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
    # Windows: enable DPI awareness
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

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
            stop:0 #0d0d2a, stop:1 #0a0a1f);
        border: 1px solid #2a2a6a;
        border-radius: 10px;
    """)
    splash_lbl = QLabel(splash)
    splash_lbl.setGeometry(0, 0, 420, 200)
    splash_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    splash_lbl.setText(
        '<span style="color:#7070ff;font-size:32px;font-weight:bold;">'
        '⌨ ClaudyKey</span><br>'
        '<span style="color:#404080;font-size:13px;">AI 智能连点器  正在启动…</span>'
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
