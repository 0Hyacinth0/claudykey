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

# ── DD key code table (Standard DD_kbd) ──────────────────────
# Reference: https://www.ddxoft.com/
_DD_KBD_KEY: dict[str, int] = {
    **{chr(ord('a') + i): i + 1 for i in range(26)},
    '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
    '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,
    'f1': 112, 'f2': 113, 'f3': 114, 'f4': 115,
    'f5': 116, 'f6': 117, 'f7': 118, 'f8': 119,
    'f9': 120, 'f10': 121, 'f11': 122, 'f12': 123,
    'ctrl': 162, 'control': 162, 'shift': 160, 'alt': 164, 'win': 91, 'windows': 91, 'super': 91,
    'up': 38, 'down': 40, 'left': 37, 'right': 39,
    'home': 36, 'end': 35, 'pageup': 33, 'pgup': 33, 'pagedown': 34, 'pgdn': 34, 'insert': 45, 'delete': 46, 'del': 46,
    'enter': 13, 'return': 13, 'space': 32, 'tab': 9, 'esc': 27, 'escape': 27, 'backspace': 8,
}

# ── DD key code table (Custom DD_key variant e.g. pydd) ────────
_DD_KEY_KEY: dict[str, int] = {
    'esc': 100, 'f1': 101, 'f2': 102, 'f3': 103, 'f4': 104, 'f5': 105, 'f6': 106, 'f7': 107, 'f8': 108, 'f9': 109, 'f10': 110, 'f11': 111, 'f12': 112,
    '`': 200, '1': 201, '2': 202, '3': 203, '4': 204, '5': 205, '6': 206, '7': 207, '8': 208, '9': 209, '0': 210, '-': 211, '+': 212, '\\': 213, 'backspace': 214,
    'tab': 300, 'q': 301, 'w': 302, 'e': 303, 'r': 304, 't': 305, 'y': 306, 'u': 307, 'i': 308, 'o': 309, 'p': 310, '[': 311, ']': 312, 'enter': 313, 'return': 313,
    'caps': 400, 'capslock': 400, 'a': 401, 's': 402, 'd': 403, 'f': 404, 'g': 405, 'h': 406, 'j': 407, 'k': 408, 'l': 409, ';': 410, "'": 411,
    'shift': 500, 'z': 501, 'x': 502, 'c': 503, 'v': 504, 'b': 505, 'n': 506, 'm': 507, ',': 508, '.': 509, '/': 510,
    'ctrl': 600, 'control': 600, 'win': 601, 'windows': 601, 'super': 601, 'alt': 602, 'space': 603,
    'up': 709, 'down': 711, 'left': 710, 'right': 712, 'delete': 706, 'del': 706,
    # numpad
    'num0': 800, 'num1': 801, 'num2': 802, 'num3': 803, 'num4': 804, 'num5': 805, 'num6': 806, 'num7': 807, 'num8': 808, 'num9': 809,
}

# DD mouse button codes
_DD_BTN_DOWN = {'left': 1, 'right': 4, 'middle': 16}
_DD_BTN_UP   = {'left': 2, 'right': 8, 'middle': 32}

_dll_instance: Optional[ctypes.CDLL] = None
_dll_path_cache: str = ''
_dll_mode: str = 'standard'  # 'standard' or 'custom'


def _load_dll(path: str) -> Optional[ctypes.CDLL]:
    global _dll_instance, _dll_path_cache, _dll_mode
    if _dll_instance is not None and path == _dll_path_cache:
        return _dll_instance
    try:
        # Try WinDLL first (standard for many Windows API-like DLLs), fallback to CDLL
        try:
            win_dll_cls = getattr(ctypes, 'WinDLL', ctypes.CDLL)
            dll = win_dll_cls(path)
            _ = dll.DD_btn
        except Exception:
            dll = ctypes.CDLL(path)
            
        # Verify it has the expected functions
        _ = dll.DD_mov
        _ = dll.DD_btn
        
        # Check driver variant
        mode = 'standard'
        if hasattr(dll, 'DD_key'):
            mode = 'custom'
            # custom drivers generally require initialization
            try:
                dll.DD_btn(0)
            except Exception:
                pass
        elif hasattr(dll, 'DD_kbd'):
            mode = 'standard'
            try:
                dll.DD_btn(0)
            except Exception:
                pass
        else:
            return None # Must have keyboard func

        _dll_mode = mode
        _dll_instance = dll
        _dll_path_cache = path
        return dll
    except Exception as e:
        return None


def _get_default_dll_path() -> str:
    """Look for dd*.dll / DD*.dll next to the executable or in common paths."""
    import glob
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    search_dirs = [os.path.join(here, 'drivers'), here]
    
    for d in search_dirs:
        # Match any DLL that starts with dd or DD
        matches = glob.glob(os.path.join(d, '[dD][dD]*.dll'))
        for c in matches:
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
        return ('未找到 DD 驱动文件。\n'
                '请将 dll 文件（如 dd.dll 或 dd64.dll）放入 drivers/ 目录，\n'
                '或在驱动设置中手动指定路径。')

    def _kbd(self, dd_code: int, state: int) -> None:
        """state: 1=press, 2=release"""
        if self._dll and dd_code:
            try:
                if _dll_mode == 'custom':
                    self._dll.DD_key(dd_code, state)
                else:
                    self._dll.DD_kbd(dd_code, state)
            except Exception:
                pass

    def _resolve(self, key: str) -> int:
        k = key.strip().lower()
        if _dll_mode == 'custom':
            return _DD_KEY_KEY.get(k, 0)
        return _DD_KBD_KEY.get(k, 0)

    # ── Mouse ──
    def mouse_move(self, x: int, y: int) -> None:
        if self._dll:
            try:
                self._dll.DD_mov(x, y)
            except Exception:
                pass

    def mouse_click(self, x: int, y: int, button: str = 'left', count: int = 1) -> None:
        if not self._dll:
            return
        self.mouse_move(x, y)
        time.sleep(0.04)
        for _ in range(count):
            try:
                self._dll.DD_btn(_DD_BTN_DOWN.get(button, 1))
                time.sleep(0.02)
                self._dll.DD_btn(_DD_BTN_UP.get(button, 2))
            except Exception:
                pass
            if count > 1:
                time.sleep(0.05)

    def mouse_scroll(self, dx: int, dy: int) -> None:
        if self._dll:
            try:
                if dy > 0:
                    self._dll.DD_whl(1)
                elif dy < 0:
                    self._dll.DD_whl(2)
            except Exception:
                pass

    # ── Keyboard ──
    def key_press(self, key: str) -> None:
        self._kbd(self._resolve(key), 1)

    def key_release(self, key: str) -> None:
        self._kbd(self._resolve(key), 2)
