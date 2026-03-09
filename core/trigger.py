"""Background trigger engine — monitors screen regions and fires callbacks."""
import re
import threading
import time
from typing import List, Callable, Dict, Optional

import numpy as np

from .macro import TriggerConfig
from . import screen as scr, image_match, ocr as _ocr


class TriggerEngine(threading.Thread):
    """Monitors screen regions for image or text conditions and fires callbacks."""

    def __init__(
        self,
        triggers: List[TriggerConfig],
        on_fire: Callable[[TriggerConfig], None],
    ):
        super().__init__(daemon=True, name='TriggerEngine')
        self.triggers = list(triggers)
        self.on_fire = on_fire
        self._stop = threading.Event()
        self._template_cache: Dict[str, Optional[np.ndarray]] = {}
        self._cooldown_until: Dict[str, float] = {}

    def stop(self):
        self._stop.set()

    def _load_template(self, path: str) -> Optional[np.ndarray]:
        if path not in self._template_cache:
            try:
                self._template_cache[path] = image_match.load_template(path)
            except Exception:
                self._template_cache[path] = None
        return self._template_cache[path]

    def _check(self, t: TriggerConfig) -> bool:
        x, y, w, h = t.region
        if w <= 0 or h <= 0:
            return False
        try:
            img = scr.capture_region(x, y, w, h)
        except Exception:
            return False

        if t.type == 'image':
            tmpl = self._load_template(t.template_path)
            if tmpl is None:
                return False
            return image_match.find_template(img, tmpl, t.threshold) is not None

        elif t.type == 'text':
            text = _ocr.recognize_text_only(img)
            tgt = t.target_text
            if t.match_mode == 'exact':
                return text.strip() == tgt.strip()
            elif t.match_mode == 'contains':
                return tgt in text
            elif t.match_mode == 'regex':
                return bool(re.search(tgt, text))
        return False

    def invalidate_template_cache(self):
        self._template_cache.clear()

    def run(self):
        while not self._stop.is_set():
            now = time.monotonic()
            for t in self.triggers:
                if not t.enabled:
                    continue
                if now < self._cooldown_until.get(t.id, 0):
                    continue
                try:
                    if self._check(t):
                        self._cooldown_until[t.id] = now + t.cooldown_ms / 1000.0
                        self.on_fire(t)
                except Exception:
                    pass
            self._stop.wait(0.1)
