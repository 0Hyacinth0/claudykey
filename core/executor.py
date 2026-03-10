"""Macro execution engine — runs a MacroSequence in a background thread.

Input backend is provided at construction time via `core.input_backend.get_backend()`.
"""
import random
import threading
import time
from typing import List, Optional, Callable

from .macro import Action, MacroSequence
from . import input_backend as _ib


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
        self._cancel_event = threading.Event()

    def stop(self):
        self._cancel_event.set()

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
                if self._cancel_event.is_set():
                    return
                time.sleep(0.02)

    def _random_sleep(self):
        lo = self.sequence.random_delay_min_ms
        hi = self.sequence.random_delay_max_ms
        if hi > 0 and lo >= 0:
            ms = random.randint(lo, max(lo, hi))
            deadline = time.monotonic() + ms / 1000.0
            while time.monotonic() < deadline:
                if self._cancel_event.is_set():
                    return
                time.sleep(0.01)

    # ------------------------------------------------------------------ runner
    def _run_slice(self, actions: List[Action], start: int, end: int):
        i = start
        while i < end and not self._cancel_event.is_set():
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
                while not self._cancel_event.is_set():
                    if count != -1 and iteration >= count:
                        break
                    self._run_slice(actions, i + 1, loop_end_idx)
                    iteration += 1
                i = j
            elif a.type == 'loop_end':
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
