"""Screen capture using mss (fast, cross-platform)."""
import mss
import numpy as np
from typing import Tuple

_sct = None


def _get_sct() -> mss.base.MSSBase:
    global _sct
    if _sct is None:
        _sct = mss.mss()
    return _sct


def capture_region(x: int, y: int, w: int, h: int) -> np.ndarray:
    """Capture a screen region and return as BGR numpy array."""
    sct = _get_sct()
    monitor = {'left': x, 'top': y, 'width': w, 'height': h}
    screenshot = sct.grab(monitor)
    # mss returns BGRA; drop alpha channel
    return np.array(screenshot)[:, :, :3]


def capture_fullscreen() -> np.ndarray:
    """Capture the primary monitor and return as BGR numpy array."""
    sct = _get_sct()
    monitor = sct.monitors[1]
    screenshot = sct.grab(monitor)
    return np.array(screenshot)[:, :, :3]


def get_screen_size() -> Tuple[int, int]:
    """Return (width, height) of the primary monitor."""
    sct = _get_sct()
    m = sct.monitors[1]
    return m['width'], m['height']
