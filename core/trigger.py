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
        on_fire: Callable[[TriggerConfig], Optional[threading.Event]],
    ):
        super().__init__(daemon=True, name='TriggerEngine')
        self.triggers = list(triggers)
        self.on_fire = on_fire
        self._cancel_event = threading.Event()
        self._template_cache: Dict[str, Optional[np.ndarray]] = {}
        self._cooldown_until: Dict[str, float] = {}

    def stop(self):
        self._cancel_event.set()

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
            elif t.match_mode == 'number':
                nums = re.findall(r'-?\d+\.?\d*', text)
                if not nums:
                    return False
                val = float(nums[0])
                if t.number_cmp == 'lte':
                    return val <= t.number_val
                elif t.number_cmp == 'gte':
                    return val >= t.number_val
                elif t.number_cmp == 'eq':
                    return abs(val - t.number_val) < 1e-6
        return False

    def invalidate_template_cache(self):
        self._template_cache.clear()

    def run(self):
        while not self._cancel_event.is_set():
            now = time.monotonic()
            fired_event = None
            
            for t in self.triggers:
                if self._cancel_event.is_set():
                    break
                if not t.enabled:
                    continue
                if now < self._cooldown_until.get(t.id, 0):
                    continue
                try:
                    if self._check(t):
                        self._cooldown_until[t.id] = time.monotonic() + t.cooldown_ms / 1000.0
                        fired_event = self.on_fire(t)
                        if fired_event:
                            break  # Stop checking other conditions while this one runs
                except Exception:
                    pass
            
            if fired_event:
                # Wait for the macro to finish before starting the next poll
                while not fired_event.is_set() and not self._cancel_event.is_set():
                    self._cancel_event.wait(0.1)
                # Once it finishes, the loop restarts from the very first trigger (sequential polling)
            else:
                self._cancel_event.wait(0.1)
