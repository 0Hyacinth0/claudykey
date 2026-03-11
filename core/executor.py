"""Macro execution engine — runs a MacroSequence in a background thread.

Input backend is provided at construction time via `core.input_backend.get_backend()`.
"""
import random
import threading
import time
from typing import List, Optional, Callable

from .macro import Action, MacroSequence
from . import input_backend as _ib
from . import screen as scr
from . import image_match
from . import ocr as _ocr
import re


class MacroExecutor(threading.Thread):
    """Executes a MacroSequence in a background daemon thread."""

    def __init__(
        self,
        sequence: MacroSequence,
        on_step: Optional[Callable[[int], None]] = None,
        on_done: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(daemon=True, name='MacroExecutor')
        self.sequence = sequence
        self.on_step = on_step
        self.on_done = on_done
        self.on_error = on_error
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def _load_template(self, path: str):
        if not hasattr(self, '_template_cache'):
            self._template_cache = {}
        if path not in self._template_cache:
            try:
                self._template_cache[path] = image_match.load_template(path)
            except Exception:
                self._template_cache[path] = None
        return self._template_cache[path]

    # ------------------------------------------------------------------ helpers
    def _backend(self):
        return _ib.get_backend()

    def _do_action(self, action: Action):
        p = action.params
        t = action.type
        bk = self._backend()

        if t in ('click', 'left_click'):
            bk.mouse_click(p['x'], p['y'], 'left')

        elif t == 'right_click':
            bk.mouse_click(p['x'], p['y'], 'right')

        elif t == 'double_click':
            bk.mouse_click(p['x'], p['y'], 'left', count=2)

        elif t == 'move':
            bk.mouse_move(p['x'], p['y'])

        elif t == 'key':
            keys = [k.strip().lower() for k in p.get('key', '').split('+')]
            bk.combo(keys)

        elif t == 'delay':
            ms = p.get('ms', 1000)
            deadline = time.monotonic() + ms / 1000.0
            while time.monotonic() < deadline:
                if self._stop.is_set():
                    return
                time.sleep(0.02)

    def _check_condition(self, t: str, p: dict) -> bool:
        x, y, w, h = p.get('region', (0, 0, 100, 100))
        if w <= 0 or h <= 0:
            return False
        try:
            img = scr.capture_region(x, y, w, h)
        except Exception:
            return False

        if 'image' in t:
            tmpl_path = p.get('template_path', '')
            tmpl = self._load_template(tmpl_path)
            if tmpl is not None:
                threshold = float(p.get('threshold', 0.80))
                return image_match.find_template(img, tmpl, threshold) is not None
        elif 'text' in t:
            text = _ocr.recognize_text_only(img)
            tgt = str(p.get('target_text', ''))
            mode = p.get('match_mode', 'contains')
            if mode == 'exact':
                return text.strip() == tgt.strip()
            elif mode == 'contains':
                return tgt in text
            elif mode == 'regex':
                return bool(re.search(tgt, text))
            elif mode == 'number':
                nums = re.findall(r'-?\d+\.?\d*', text)
                if nums:
                    val = float(nums[0])
                    cmp = p.get('number_cmp', 'lte')
                    ref_val = float(p.get('number_val', 0.0))
                    if cmp == 'lte':
                        return val <= ref_val
                    elif cmp == 'gte':
                        return val >= ref_val
                    elif cmp == 'eq':
                        return abs(val - ref_val) < 1e-6
        return False

    def _random_sleep(self):
        lo = self.sequence.random_delay_min_ms
        hi = self.sequence.random_delay_max_ms
        if hi > 0 and lo >= 0:
            ms = random.randint(lo, max(lo, hi))
            deadline = time.monotonic() + ms / 1000.0
            while time.monotonic() < deadline:
                if self._stop.is_set():
                    return
                time.sleep(0.01)

    # ------------------------------------------------------------------ runner
    def _run_slice(self, actions: List[Action], start: int, end: int):
        i = start
        while i < end and not self._stop.is_set():
            a = actions[i]
            if a.type == 'loop_start':
                count = a.params.get('count', -1)
                depth, j = 1, i + 1
                while j < end and depth:
                    if actions[j].type == 'loop_start':
                        depth += 1
                    elif actions[j].type == 'loop_end':
                        depth -= 1
                    j += 1
                loop_end_idx = j - 1
                iteration = 0
                while not self._stop.is_set():
                    if count != -1 and iteration >= count:
                        break
                    self._run_slice(actions, i + 1, loop_end_idx)
                    iteration += 1
                i = j
            elif a.type in ('if_image', 'if_text'):
                # Block branch analysis
                j = i + 1
                depth = 1
                branches = []  # List of tuple (start_idx, end_idx, condition_fn_or_None)
                current_branch_start = j
                current_cond = lambda: self._check_condition(a.type, a.params)

                while j < end and depth > 0:
                    t = actions[j].type
                    if t in ('if_image', 'if_text'):
                        depth += 1
                    elif t == 'end_if':
                        depth -= 1
                        if depth == 0:
                            branches.append((current_branch_start, j, current_cond))
                            break
                    elif depth == 1 and t in ('elif_image', 'elif_text', 'else_start'):
                        # End current block
                        branches.append((current_branch_start, j, current_cond))
                        current_branch_start = j + 1
                        if t == 'else_start':
                            current_cond = lambda: True
                        else:
                            # Capture j and a snapshot of actions[j] for lambda
                            a_elif = actions[j]
                            current_cond = lambda a_el=a_elif: self._check_condition(a_el.type, a_el.params)
                    j += 1

                # Evaluate execution top-to-bottom
                for b_start, b_end, cond_check in branches:
                    if cond_check():
                        self._run_slice(actions, b_start, b_end)
                        break  # Only run first matching branch

                i = j if depth == 0 else j + 1
                
            elif a.type in ('loop_end', 'end_if', 'elif_image', 'elif_text', 'else_start'):
                # Should not be hit directly unless unbalanced
                i += 1
            else:
                if self.on_step:
                    self.on_step(i)
                self._random_sleep()
                self._do_action(a)
                i += 1

    def run(self):
        try:
            self._run_slice(self.sequence.actions, 0, len(self.sequence.actions))
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
        finally:
            if self.on_done:
                self.on_done()


# ── Expose KEY_MAP for legacy trigger-action code ────────────────────────────
# Trigger actions in main_window.py use _KEY_MAP to resolve key strings
# when pynput is the backend. We provide a shim here.
try:
    from core.backends.pynput_backend import KEY_MAP as _KEY_MAP
except Exception:
    _KEY_MAP = {}
