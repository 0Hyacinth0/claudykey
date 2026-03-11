"""DD虚拟驱动 input backend.

Requires the DD virtual driver (dd.dll / dd64.dll) to be installed.
Users configure the DLL path in Settings → Input Driver.

DD driver download: https://github.com/66maer/pydd
"""
import ctypes
import os
import time
import urllib.request
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
    '`': 200, '1': 201, '2': 202, '3': 203, '4': 204, '5': 205, '6': 206, '7': 207, '8': 208, '9': 209, '0': 210, '-': 211, '+': 212, '\\': 213, 'backspace': 214, 'bs': 214,
    'tab': 300, 'q': 301, 'w': 302, 'e': 303, 'r': 304, 't': 305, 'y': 306, 'u': 307, 'i': 308, 'o': 309, 'p': 310, '[': 311, ']': 312, 'enter': 313, 'return': 313,
    'caps': 400, 'capslock': 400, 'a': 401, 's': 402, 'd': 403, 'f': 404, 'g': 405, 'h': 406, 'j': 407, 'k': 408, 'l': 409, ';': 410, "'": 411,
    'shift': 500, 'z': 501, 'x': 502, 'c': 503, 'v': 504, 'b': 505, 'n': 506, 'm': 507, ',': 508, '.': 509, '/': 510,
    'ctrl': 600, 'control': 600, 'win': 601, 'windows': 601, 'super': 601, 'alt': 602, 'space': 603,
    'up': 709, 'down': 711, 'left': 710, 'right': 712, 'delete': 706, 'del': 706,
    # numpad
    'num0': 800, 'num1': 801, 'num2': 802, 'num3': 803, 'num4': 804, 'num5': 805, 'num6': 806, 'num7': 807, 'num8': 808, 'num9': 809,
    'num/': 811, 'num*': 812, 'num-': 813, 'num+': 814, 'numenter': 815, 'num.': 816,
}

# DD mouse button codes
_DD_BTN_DOWN = {'left': 1, 'right': 4, 'middle': 16, 'x4': 64, 'x5': 256}
_DD_BTN_UP   = {'left': 2, 'right': 8, 'middle': 32, 'x4': 128, 'x5': 512}


def _download_dd_driver(target_path: str) -> bool:
    """Download DD driver from pydd github repo."""
    url = "https://github.com/66maer/pydd/raw/main/dd.54900.dll"
    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        print(f"Downloading DD driver from {url}...")
        urllib.request.urlretrieve(url, target_path)
        return True
    except Exception as e:
        print(f"Failed to download DD driver: {e}")
        return False


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
                
    # If not found, download automatically based on pydd
    drivers_dir = os.path.join(here, 'drivers')
    target_path = os.path.join(drivers_dir, 'dd.54900.dll')
    if _download_dd_driver(target_path):
        return target_path
        
    return ''


@register_backend
class DDBackend(InputBackend):
    """DD虚拟驱动 backend — kernel-level key/mouse simulation."""

    def __init__(self, dll_path: str = ''):
        self._dll_path = dll_path or _get_default_dll_path()
        self._dll: Optional[ctypes.CDLL] = None
        self._dll_mode = 'standard'
        
        if self._dll_path and os.path.exists(self._dll_path):
            try:
                # Based on pydd.py simplified python interface
                self._dll = ctypes.windll.LoadLibrary(self._dll_path)
                
                # Check for string output support
                if hasattr(self._dll, 'DD_str'):
                    self._dll.DD_str.argtypes = [ctypes.c_char_p]
                    self._dll.DD_str.restype = ctypes.c_int
                    
                # Determine mode
                if hasattr(self._dll, 'DD_key'):
                    self._dll_mode = 'custom'
                
                # Initialize driver (Must return 1 on success for pydd driver)
                res = self._dll.DD_btn(0)
                if res != 1 and self._dll_mode == 'custom':
                    print("Warning: DD_btn(0) did not return 1 (driver initialization issue?)")
            except Exception as e:
                print(f"DDBackend init error: {e}")
                self._dll = None

    @classmethod
    def name(cls) -> str:
        return 'dd'

    @classmethod
    def display_name(cls) -> str:
        return 'DD虚拟驱动'

    @classmethod
    def is_available(cls) -> bool:
        path = _get_default_dll_path()
        return bool(path and os.path.exists(path))

    @classmethod
    def unavailable_reason(cls) -> str:
        return ('未找到 DD 驱动文件或下载失败。\n'
                '请确保网络正常或手动将 dll 文件（如 dd.54900.dll）放入 drivers/ 目录，\n'
                '或在驱动设置中手动指定路径。')

    def _kbd(self, code: int, state: int) -> None:
        """state: 1=press, 2=release"""
        if self._dll and code:
            try:
                if self._dll_mode == 'custom':
                    self._dll.DD_key(code, state)
                else:
                    self._dll.DD_kbd(code, state)
            except Exception:
                pass

    def _resolve(self, key: str) -> int:
        k = key.strip().lower()
        if self._dll_mode == 'custom':
            return _DD_KEY_KEY.get(k, 0)
        return _DD_KBD_KEY.get(k, 0)

    # ── Mouse ──
    def mouse_move(self, x: int, y: int) -> None:
        if self._dll:
            try:
                self._dll.DD_mov(x, y)
            except Exception:
                pass

    def mouse_move_relative(self, dx: int, dy: int) -> None:
        if self._dll:
            try:
                self._dll.DD_movR(dx, dy)
            except Exception:
                pass

    def set_mouse_down(self, button: str = 'left') -> None:
        if self._dll:
            try:
                code = _DD_BTN_DOWN.get(button.lower(), 1)
                self._dll.DD_btn(code)
            except Exception:
                pass

    def set_mouse_up(self, button: str = 'left') -> None:
        if self._dll:
            try:
                code = _DD_BTN_UP.get(button.lower(), 2)
                self._dll.DD_btn(code)
            except Exception:
                pass

    def mouse_click(self, x: int, y: int, button: str = 'left', count: int = 1) -> None:
        if not self._dll:
            return
        
        # Only move if x, y provided properly; input backend semantics allow x, y = 0
        self.mouse_move(x, y)
        time.sleep(0.04)
        
        down_code = _DD_BTN_DOWN.get(button.lower(), 1)
        up_code = _DD_BTN_UP.get(button.lower(), 2)
        
        for _ in range(count):
            try:
                self._dll.DD_btn(down_code)
                time.sleep(0.02)
                self._dll.DD_btn(up_code)
            except Exception:
                pass
            if count > 1:
                time.sleep(0.05)

    def mouse_scroll(self, dx: int, dy: int) -> None:
        if self._dll:
            try:
                # dy is vertical scroll
                if dy != 0:
                    scroll_code = 1 if dy > 0 else 2
                    count = abs(dy)
                    for i in range(count):
                        self._dll.DD_whl(scroll_code)
                        if i < count - 1:
                            time.sleep(0.1)
            except Exception:
                pass

    # ── Keyboard ──
    def key_press(self, key: str) -> None:
        self._kbd(self._resolve(key), 1)

    def key_release(self, key: str) -> None:
        self._kbd(self._resolve(key), 2)

    def type_text(self, text: str) -> None:
        """Type text directly using pydd DD_str if available."""
        if not self._dll or not text:
            return
        if hasattr(self._dll, 'DD_str'):
            text_bytes = text.encode("ascii", errors="ignore")
            if text_bytes:
                self._dll.DD_str(text_bytes)
        else:
            # Fallback
            for char in text:
                if char.isspace():
                    self.key_press('space')
                    time.sleep(0.01)
                    self.key_release('space')
                else:
                    self.key_press(char)
                    time.sleep(0.01)
                    self.key_release(char)
