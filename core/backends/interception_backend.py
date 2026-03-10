"""Interception driver input backend.

Requires the Interception kernel driver to be installed.
  GitHub: https://github.com/oblitum/Interception
  Python binding: pip install pyinterception

Install driver (run as Administrator, Windows test-signing or DSEC off):
  interception\\command line installer\\install-interception.exe /install

Then restart Windows.
"""
import time
from typing import Optional, Any

from core.input_backend import InputBackend, register_backend

# Virtual-key → scan-code mapping (subset, enough for most macro keys)
_VK_TO_SCAN: dict[str, int] = {
    'a': 0x1e, 'b': 0x30, 'c': 0x2e, 'd': 0x20, 'e': 0x12,
    'f': 0x21, 'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24,
    'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31, 'o': 0x18,
    'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1f, 't': 0x14,
    'u': 0x16, 'v': 0x2f, 'w': 0x11, 'x': 0x2d, 'y': 0x15, 'z': 0x2c,
    '0': 0x0b, '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05,
    '5': 0x06, '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0a,
    'f1': 0x3b, 'f2': 0x3c, 'f3': 0x3d, 'f4': 0x3e,
    'f5': 0x3f, 'f6': 0x40, 'f7': 0x41, 'f8': 0x42,
    'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,
    'enter': 0x1c, 'return': 0x1c,
    'space': 0x39, 'tab': 0x0f,
    'esc': 0x01, 'escape': 0x01,
    'backspace': 0x0e, 'delete': 0xe053, 'del': 0xe053,
    'shift': 0x2a, 'ctrl': 0x1d, 'control': 0x1d,
    'alt': 0x38, 'win': 0xe05b, 'windows': 0xe05b, 'super': 0xe05b,
    'up': 0xe048, 'down': 0xe050, 'left': 0xe04b, 'right': 0xe04d,
    'home': 0xe047, 'end': 0xe04f,
    'pageup': 0xe049, 'pgup': 0xe049,
    'pagedown': 0xe051, 'pgdn': 0xe051,
    'insert': 0xe052,
}

_context: Optional[Any] = None   # interception context handle


def _get_context():
    """Lazily create the interception context (one per process)."""
    global _context
    if _context is None:
        import interception
        _context = interception.interception()
        _context.begin()
    return _context


@register_backend
class InterceptionBackend(InputBackend):
    """Kernel-mode input backend via Interception driver."""

    def __init__(self):
        self._ctx = None   # created lazily on first use

    @classmethod
    def name(cls) -> str:
        return 'interception'

    @classmethod
    def display_name(cls) -> str:
        return 'Interception驱动'

    @classmethod
    def is_available(cls) -> bool:
        try:
            import interception  # noqa
            ctx = interception.interception()
            # If the driver isn't installed, begin() raises
            ctx.begin()
            ctx.end()
            return True
        except Exception:
            return False

    @classmethod
    def unavailable_reason(cls) -> str:
        return (
            'Interception 驱动未安装或 pyinterception 未安装。\n'
            '1. pip install pyinterception\n'
            '2. 以管理员身份运行 install-interception.exe /install\n'
            '3. 重启 Windows\n'
            '（可能需要关闭驱动强制签名验证）'
        )

    def _ctx_(self):
        if self._ctx is None:
            self._ctx = _get_context()
        return self._ctx

    def _resolve_scan(self, key: str) -> int:
        return _VK_TO_SCAN.get(key.strip().lower(), 0)

    # ── Mouse ──
    def mouse_move(self, x: int, y: int) -> None:
        try:
            import interception
            ctx = self._ctx_()
            stroke = interception.mouse_stroke()
            stroke.state = 0
            stroke.flags = interception.INTERCEPTION_MOUSE_MOVE_ABSOLUTE
            # Interception absolute coords are 0-65535 normalised
            import ctypes
            sw = ctypes.windll.user32.GetSystemMetrics(0)
            sh = ctypes.windll.user32.GetSystemMetrics(1)
            stroke.x = int(x * 65535 / sw)
            stroke.y = int(y * 65535 / sh)
            ctx.send_mouse(1, stroke)
        except Exception:
            pass

    def mouse_click(self, x: int, y: int, button: str = 'left', count: int = 1) -> None:
        try:
            import interception
            btn_map = {
                'left':   (interception.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN,
                           interception.INTERCEPTION_MOUSE_LEFT_BUTTON_UP),
                'right':  (interception.INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN,
                           interception.INTERCEPTION_MOUSE_RIGHT_BUTTON_UP),
                'middle': (interception.INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN,
                           interception.INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP),
            }
            down, up = btn_map.get(button, btn_map['left'])
            ctx = self._ctx_()
            self.mouse_move(x, y)
            time.sleep(0.04)
            for _ in range(count):
                s = interception.mouse_stroke()
                s.state = down; s.flags = 0; s.x = 0; s.y = 0
                ctx.send_mouse(1, s)
                time.sleep(0.02)
                s.state = up
                ctx.send_mouse(1, s)
                if count > 1:
                    time.sleep(0.05)
        except Exception:
            pass

    def mouse_scroll(self, dx: int, dy: int) -> None:
        try:
            import interception
            ctx = self._ctx_()
            s = interception.mouse_stroke()
            s.state = interception.INTERCEPTION_MOUSE_WHEEL
            s.rolling = dy * 120   # Windows WHEEL_DELTA = 120
            s.flags = 0; s.x = 0; s.y = 0
            ctx.send_mouse(1, s)
        except Exception:
            pass

    # ── Keyboard ──
    def _send_key(self, key: str, up: bool) -> None:
        try:
            import interception
            scan = self._resolve_scan(key)
            if not scan:
                return
            ctx = self._ctx_()
            s = interception.key_stroke()
            # Extended keys (e0xx) need E0 flag
            if scan > 0xff:
                s.code  = scan & 0xff
                s.state = (interception.INTERCEPTION_KEY_UP if up
                           else interception.INTERCEPTION_KEY_DOWN) | interception.INTERCEPTION_KEY_E0
            else:
                s.code  = scan
                s.state = (interception.INTERCEPTION_KEY_UP if up
                           else interception.INTERCEPTION_KEY_DOWN)
            ctx.send_keyboard(1, s)
        except Exception:
            pass

    def key_press(self, key: str) -> None:
        self._send_key(key, up=False)

    def key_release(self, key: str) -> None:
        self._send_key(key, up=True)
