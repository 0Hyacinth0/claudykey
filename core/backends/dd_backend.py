"""DD虚拟驱动 input backend.

Requires the DD virtual driver (dd.dll / dd64.dll) to be installed.
Users configure the DLL path in Settings → Input Driver.

DD driver download: https://www.ddxoft.com/
"""
import ctypes
import os
import time
from typing import Optional

from core.input_backend import InputBackend, register_backend

# ── DD key code table (VK name → DD key code) ──────────────────────
# DD uses its own numbering. 0 means unsupported.
# Reference: https://www.ddxoft.com/  (DD虚拟键盘驱动说明)
_DD_KEY: dict[str, int] = {
    # Letters A-Z → DD codes 1-26
    **{chr(ord('a') + i): i + 1 for i in range(26)},
    # Digits 0-9
    '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
    '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,
    # Function keys
    'f1': 112, 'f2': 113, 'f3': 114, 'f4': 115,
    'f5': 116, 'f6': 117, 'f7': 118, 'f8': 119,
    'f9': 120, 'f10': 121, 'f11': 122, 'f12': 123,
    # Modifiers
    'ctrl': 162, 'control': 162,
    'shift': 160,
    'alt': 164,
    'win': 91, 'windows': 91, 'super': 91,
    # Navigation
    'up': 38, 'down': 40, 'left': 37, 'right': 39,
    'home': 36, 'end': 35, 'pageup': 33, 'pgup': 33,
    'pagedown': 34, 'pgdn': 34, 'insert': 45, 'delete': 46, 'del': 46,
    # Common
    'enter': 13, 'return': 13,
    'space': 32, 'tab': 9,
    'esc': 27, 'escape': 27,
    'backspace': 8,
}

# DD mouse button codes
_DD_BTN_DOWN = {'left': 1, 'right': 4, 'middle': 16}
_DD_BTN_UP   = {'left': 2, 'right': 8, 'middle': 32}

_dll_instance: Optional[ctypes.CDLL] = None
_dll_path_cache: str = ''


def _load_dll(path: str) -> Optional[ctypes.CDLL]:
    global _dll_instance, _dll_path_cache
    if _dll_instance is not None and path == _dll_path_cache:
        return _dll_instance
    try:
        dll = ctypes.CDLL(path)
        # Verify it has the expected functions
        _ = dll.DD_kbd
        _ = dll.DD_mov
        _ = dll.DD_btn
        _dll_instance = dll
        _dll_path_cache = path
        return dll
    except Exception:
        return None


def _get_default_dll_path() -> str:
    """Look for dd.dll / dd64.dll next to the executable or in common paths."""
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(here, 'drivers', 'dd64.dll'),
        os.path.join(here, 'drivers', 'dd.dll'),
        os.path.join(here, 'dd64.dll'),
        os.path.join(here, 'dd.dll'),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return ''


@register_backend
class DDBackend(InputBackend):
    """DD虚拟驱动 backend — kernel-level key/mouse simulation."""

    def __init__(self, dll_path: str = ''):
        self._dll_path = dll_path or _get_default_dll_path()
        self._dll: Optional[ctypes.CDLL] = _load_dll(self._dll_path) if self._dll_path else None

    @classmethod
    def name(cls) -> str:
        return 'dd'

    @classmethod
    def display_name(cls) -> str:
        return 'DD虚拟驱动'

    @classmethod
    def is_available(cls) -> bool:
        path = _get_default_dll_path()
        return bool(path and _load_dll(path))

    @classmethod
    def unavailable_reason(cls) -> str:
        return ('未找到 dd.dll / dd64.dll。\n'
                '请下载 DD虚拟驱动 并将 DLL 放入 drivers/ 目录，\n'
                '或在驱动设置中手动指定路径。')

    def _kbd(self, dd_code: int, state: int) -> None:
        """state: 1=press, 2=release"""
        if self._dll and dd_code:
            self._dll.DD_kbd(dd_code, state)

    def _resolve(self, key: str) -> int:
        return _DD_KEY.get(key.strip().lower(), 0)

    # ── Mouse ──
    def mouse_move(self, x: int, y: int) -> None:
        if self._dll:
            # DD_movR for relative, DD_mov for absolute (requires DD_todc first)
            # Use absolute via SetCursorPos + DD_mov
            self._dll.DD_mov(x, y)

    def mouse_click(self, x: int, y: int, button: str = 'left', count: int = 1) -> None:
        if not self._dll:
            return
        self._dll.DD_mov(x, y)
        time.sleep(0.04)
        for _ in range(count):
            self._dll.DD_btn(_DD_BTN_DOWN.get(button, 1))
            time.sleep(0.02)
            self._dll.DD_btn(_DD_BTN_UP.get(button, 2))
            if count > 1:
                time.sleep(0.05)

    def mouse_scroll(self, dx: int, dy: int) -> None:
        if self._dll:
            # DD_whl: direction 1=up 2=down, amount
            if dy > 0:
                self._dll.DD_whl(1, abs(dy))
            elif dy < 0:
                self._dll.DD_whl(2, abs(dy))

    # ── Keyboard ──
    def key_press(self, key: str) -> None:
        self._kbd(self._resolve(key), 1)

    def key_release(self, key: str) -> None:
        self._kbd(self._resolve(key), 2)
