"""Hotkey setup dialog for ClaudyKey."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from pynput import keyboard as pynput_kb
from pynput import mouse as pynput_mouse
from gui.theme import STYLE_HOTKEY_DIALOG_LBL


class HotkeySetDialog(QDialog):
    # Phase 2: Thread Safety. Custom signal to cross from pynput thread to GUI thread
    hotkey_detected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置启停快捷键')
        self.setFixedSize(300, 160)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        lay = QVBoxLayout(self)
        self.lbl = QLabel('正在监听...\n\n请按下任意键盘按键或\n除左键外的鼠标按键。')
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet(STYLE_HOTKEY_DIALOG_LBL)
        lay.addWidget(self.lbl)
        
        self.result_key = None
        
        # Connect strictly to GUI thread handler
        self.hotkey_detected.connect(self._on_hotkey_detected)
        
        self.kb_listener = pynput_kb.Listener(on_press=self.on_key)
        self.mouse_listener = pynput_mouse.Listener(on_click=self.on_mouse)
        self.kb_listener.start()
        self.mouse_listener.start()

    def on_key(self, key):
        if self.result_key: return
        try:
            char = key.char
            if char:
                detected = f"key:{char.lower()}"
            else:
                detected = f"key:<{key.name}>"
        except AttributeError:
            detected = f"key:<{key.name}>"
        
        self.result_key = detected
        self.hotkey_detected.emit(detected)

    def on_mouse(self, x, y, button, pressed):
        if not pressed or self.result_key: return
        if button == pynput_mouse.Button.left:
            return  # block left click
        detected = f"mouse:{button.name}"
        self.result_key = detected
        self.hotkey_detected.emit(detected)

    def _on_hotkey_detected(self, key_str: str):
        """Called safely in GUI thread by signal."""
        self.kb_listener.stop()
        self.mouse_listener.stop()
        self.accept()

    def closeEvent(self, event):
        self.kb_listener.stop()
        self.mouse_listener.stop()
        super().closeEvent(event)
