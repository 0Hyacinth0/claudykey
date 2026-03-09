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
        on_log: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(daemon=True, name='TriggerEngine')
        self.triggers = list(triggers)
        self.on_fire = on_fire
        self.on_log = on_log
        self._stop = threading.Event()
        self._template_cache: Dict[str, Optional[np.ndarray]] = {}
        self._cooldown_until: Dict[str, float] = {}

    def stop(self):
        self._stop.set()

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

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
                self._log(f"错误: 无法加载模板图片 {t.template_path}")
                return False
            res = image_match.find_template(img, tmpl, t.threshold)
            matched = res is not None
            if matched:
                self._log(f"图片匹配成功: {t.name} (置信度: {res[2]:.2f})")
            return matched

        elif t.type == 'text':
            text = _ocr.recognize_text_only(img)
            self._log(f"OCR 结果 ({t.name}): '{text}'")
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
        self._log("触发模式启动: 开始巡检环境...")
        while not self._stop.is_set():
            now = time.monotonic()
            fired_event = None
            
            for t in self.triggers:
                if self._stop.is_set():
                    break
                if not t.enabled:
                    continue
                if now < self._cooldown_until.get(t.id, 0):
                    continue
                try:
                    if self._check(t):
                        self._log(f"触发器激活: {t.name}")
                        self._cooldown_until[t.id] = time.monotonic() + t.cooldown_ms / 1000.0
                        fired_event = self.on_fire(t)
                        if fired_event:
                            self._log(f"正在等待宏执行完毕: {t.name}...")
                            break  # Stop checking other conditions while this one runs
                except Exception as e:
                    self._log(f"检查触发器时出错 ({t.name}): {str(e)}")
            
            if fired_event:
                # Wait for the macro to finish before starting the next poll
                while not fired_event.is_set() and not self._stop.is_set():
                    self._stop.wait(0.1)
                # Once it finishes, the loop restarts from the very first trigger (sequential polling)
            else:
                self._stop.wait(0.1)
        self._log("触发模式已停止")
