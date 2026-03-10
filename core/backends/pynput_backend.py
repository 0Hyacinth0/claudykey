"""pynput-based input backend (default, works everywhere pynput is installed)."""
import time
from pynput.mouse import Button, Controller as MouseCtrl
from pynput.keyboard import Key, Controller as KeyCtrl

from core.input_backend import InputBackend, register_backend

# Map canonical key names → pynput Key objects
_KEY_MAP: dict = {
    'ctrl': Key.ctrl, 'control': Key.ctrl,
    'alt': Key.alt,
    'shift': Key.shift,
    'win': Key.cmd, 'windows': Key.cmd, 'super': Key.cmd,
    'enter': Key.enter, 'return': Key.enter,
    'space': Key.space,
    'tab': Key.tab,
    'esc': Key.esc, 'escape': Key.esc,
    'backspace': Key.backspace,
    'delete': Key.delete, 'del': Key.delete,
    'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
    'home': Key.home, 'end': Key.end,
    'pageup': Key.page_up, 'pgup': Key.page_up,
    'pagedown': Key.page_down, 'pgdn': Key.page_down,
    'insert': Key.insert,
    'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
    'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
    'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
}

_BTN_MAP = {
    'left': Button.left,
    'right': Button.right,
    'middle': Button.middle,
}


@register_backend
class PynputBackend(InputBackend):
    def __init__(self):
        self._mouse = MouseCtrl()
        self._kbd = KeyCtrl()

    @classmethod
    def name(cls) -> str:
        return 'pynput'

    @classmethod
    def display_name(cls) -> str:
        return 'pynput（默认）'

    @classmethod
    def is_available(cls) -> bool:
        try:
            from pynput.mouse import Controller  # noqa
            return True
        except Exception:
            return False

    # ── Mouse ──
    def mouse_move(self, x: int, y: int) -> None:
        self._mouse.position = (x, y)

    def mouse_click(self, x: int, y: int, button: str = 'left', count: int = 1) -> None:
        self._mouse.position = (x, y)
        time.sleep(0.04)
        self._mouse.click(_BTN_MAP.get(button, Button.left), count)

    def mouse_scroll(self, dx: int, dy: int) -> None:
        self._mouse.scroll(dx, dy)

    # ── Keyboard ──
    def _resolve(self, key: str):
        k = key.strip().lower()
        return _KEY_MAP.get(k, k)

    def key_press(self, key: str) -> None:
        self._kbd.press(self._resolve(key))

    def key_release(self, key: str) -> None:
        self._kbd.release(self._resolve(key))


# Re-export the key map so executor can use it for trigger actions
KEY_MAP = _KEY_MAP
