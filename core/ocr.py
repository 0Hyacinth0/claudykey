"""EasyOCR wrapper for GPU-accelerated text recognition."""
import cv2
import numpy as np
from typing import List, Tuple, Optional

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        # Supports Simplified Chinese + English; gpu=True uses CUDA
        _reader = easyocr.Reader(['ch_sim', 'en'], gpu=True, verbose=False)
    return _reader


def recognize(image: np.ndarray) -> List[Tuple[list, str, float]]:
    """
    Recognize text in a BGR image.
    Returns list of (bbox, text, confidence) tuples.
    """
    reader = _get_reader()
    # EasyOCR expects RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return reader.readtext(rgb)


def recognize_text_only(image: np.ndarray) -> str:
    """Return all recognized text concatenated as a single string."""
    results = recognize(image)
    return ' '.join(r[1] for r in results)


def is_ready() -> bool:
    """Return True if the OCR reader has been initialized."""
    return _reader is not None


def warm_up():
    """Pre-initialize the OCR reader (call at startup to avoid first-use delay)."""
    _get_reader()
