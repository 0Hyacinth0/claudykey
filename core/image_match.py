"""OpenCV template matching for icon/image detection on screen."""
import cv2
import numpy as np
from typing import Optional, Tuple


def load_template(path: str) -> np.ndarray:
    """Load a template image as BGR numpy array.
    Uses PIL to avoid OpenCV libpng ICC profile stderr warnings.
    """
    try:
        from PIL import Image
        with Image.open(path) as pil_img:
            # Convert to RGB to discard alpha or handle grayscale, then to BGR
            img = np.array(pil_img.convert('RGB'))[:, :, ::-1].copy()
            return img
    except Exception:
        # Fallback to OpenCV
        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError(f"Cannot load template image: {path}")
        return img


def find_template(
    screen: np.ndarray,
    template: np.ndarray,
    threshold: float = 0.80,
) -> Optional[Tuple[int, int, float]]:
    """
    Find template in screen using normalized cross-correlation.
    Returns (center_x, center_y, confidence) if found above threshold,
    or None if not matched.
    """
    if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
        return None
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        return (cx, cy, float(max_val))
    return None


def find_all_templates(
    screen: np.ndarray,
    template: np.ndarray,
    threshold: float = 0.80,
) -> list:
    """
    Find all occurrences of template in screen above threshold.
    Returns list of (center_x, center_y, confidence).
    """
    if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
        return []
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    locs = np.where(result >= threshold)
    h, w = template.shape[:2]
    matches = []
    for pt in zip(*locs[::-1]):
        cx = pt[0] + w // 2
        cy = pt[1] + h // 2
        conf = float(result[pt[1], pt[0]])
        matches.append((cx, cy, conf))
    return matches
