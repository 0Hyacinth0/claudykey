"""ClaudyKey — AI-powered macro clicker entry point."""
import sys
import os
import threading

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QProgressBar, QLabel
from PyQt6.QtCore import Qt, QTimer, qInstallMessageHandler, QtMsgType
from PyQt6.QtGui import QFont

from gui.theme import get_theme_qss

class CyberSplash(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 360)

        # Main background (Deep cyber wave mockup)
        self.bg = QFrame(self)
        self.bg.setGeometry(0, 0, 600, 360)
        self.bg.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0f101f, stop:0.4 #170b2e, stop:0.7 #0c1a2e, stop:1 #0f101f);
                border-radius: 12px;
            }
        """)

        # Mac Dots
        dots_lay = QHBoxLayout()
        dots_lay.setContentsMargins(12, 12, 0, 0)
        dots_lay.setSpacing(8)
        for c in ['#ff5f56', '#ffbd2e', '#27c93f']:
            d = QFrame()
            d.setFixedSize(12, 12)
            d.setStyleSheet(f"background-color: {c}; border-radius: 6px;")
            dots_lay.addWidget(d)
        dots_lay.addStretch()

        # Center Card
        self.card = QFrame(self.bg)
        self.card.setGeometry(75, 80, 450, 200)
        self.card.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(187, 134, 252, 0.4);
                border-radius: 16px;
            }
        """)

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(40, 50, 40, 30)
        
        h_lay = QHBoxLayout()
        h_lay.setSpacing(20)
        
        icon_lbl = QLabel("⌨")
        icon_lbl.setStyleSheet("font-size: 64px; color: rgba(255,255,255,0.8); background: transparent; border: none;")
        h_lay.addWidget(icon_lbl)
        
        text_lay = QVBoxLayout()
        text_lay.setSpacing(4)
        title = QLabel("ClaudyKey")
        title.setStyleSheet("font-family: 'Segoe UI', Arial; font-size: 38px; font-weight: bold; color: white; background: transparent; border: none;")
        sub = QLabel("AI 智能连点器 正在启动...")
        sub.setStyleSheet("font-family: Arial; font-size: 14px; color: #a1a1aa; background: transparent; border: none;")
        text_lay.addWidget(title)
        text_lay.addWidget(sub)
        text_lay.addStretch()
        
        h_lay.addLayout(text_lay)
        h_lay.addStretch()
        
        card_lay.addLayout(h_lay)
        card_lay.addStretch()
        
        self.bar = QProgressBar()
        self.bar.setFixedHeight(4)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00f2fe, stop:1 #d53369);
                border-radius: 2px;
            }
        """)
        self.bar.setValue(0)
        card_lay.addWidget(self.bar)

        main_lay = QVBoxLayout(self.bg)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.addLayout(dots_lay)
        main_lay.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step)
        self.timer.start(10)

    def _step(self):
        v = self.bar.value() + 2
        if v > 100: v = 100
        self.bar.setValue(v)

def _warm_up_ocr():
    """Pre-load EasyOCR model in background so first use is instant."""
    try:
        from core import ocr
        ocr.warm_up()
    except Exception:
        pass


def _qt_message_handler(mode, context, message):
    if "iCCP" in message or "incorrect sRGB profile" in message:
        return
    import sys
    sys.stderr.write(f"{message}\\n")

def main():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    qInstallMessageHandler(_qt_message_handler)

    app.setApplicationName('ClaudyKey')
    app.setApplicationDisplayName('ClaudyKey')
    app.setStyle('Fusion')
    app.setStyleSheet(get_theme_qss(is_dark=False))

    splash = CyberSplash()
    splash.show()
    app.processEvents()

    threading.Thread(target=_warm_up_ocr, daemon=True).start()

    from gui.main_window import MainWindow
    window = MainWindow()

    def _show():
        splash.close()
        window.show()

    QTimer.singleShot(800, _show)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
