"""Macro execution engine — runs a MacroSequence in a background thread."""
import threading
import time
from typing import List, Optional, Callable

from pynput.mouse import Button, Controller as MouseCtrl
from pynput.keyboard import Key, Controller as KeyCtrl

from .macro import Action, MacroSequence

# Map common key name strings to pynput Key objects
_KEY_MAP = {
    'ctrl': Key.ctrl, 'control': Key.ctrl,
    'alt': Key.alt,
    'shift': Key.shift,
    'win': Key.cmd, 'windows': Key.cmd, 'super': Key.cmd,
    'enter': Key.enter, 'return': Key.enter,
    'space': Key.space,
    'tab': Key.tab,
    'esc': Key.esc, 'escape': Key.esc,
    'backspace': Key.backspace,
    'delete': Key.delete, 'del': Key.delete,
    'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
    'home': Key.home, 'end': Key.end,
    'pageup': Key.page_up, 'pgup': Key.page_up,
    'pagedown': Key.page_down, 'pgdn': Key.page_down,
    **{f'f{i}': getattr(Key, f'f{i}') for i in range(1, 13)},
}


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
        self._mouse = MouseCtrl()
        self._kbd = KeyCtrl()

    def stop(self):
        self._stop.set()

    # ------------------------------------------------------------------ helpers
    def _resolve_key(self, part: str):
        part = part.strip().lower()
        return _KEY_MAP.get(part, part)

    def _do_action(self, action: Action):
        p = action.params
        t = action.type

        if t in ('click', 'left_click'):
            self._mouse.position = (p['x'], p['y'])
            time.sleep(0.04)
            self._mouse.click(Button.left)

        elif t == 'right_click':
            self._mouse.position = (p['x'], p['y'])
            time.sleep(0.04)
            self._mouse.click(Button.right)

        elif t == 'double_click':
            self._mouse.position = (p['x'], p['y'])
            time.sleep(0.04)
            self._mouse.click(Button.left, 2)

        elif t == 'move':
            self._mouse.position = (p['x'], p['y'])

        elif t == 'key':
            keys = [self._resolve_key(k) for k in p.get('key', '').split('+')]
            for k in keys[:-1]:
                self._kbd.press(k)
            self._kbd.press(keys[-1])
            self._kbd.release(keys[-1])
            for k in reversed(keys[:-1]):
                self._kbd.release(k)

        elif t == 'delay':
            ms = p.get('ms', 1000)
            deadline = time.monotonic() + ms / 1000.0
            while time.monotonic() < deadline:
                if self._stop.is_set():
                    return
                time.sleep(0.02)

    # ------------------------------------------------------------------ runner
    def _run_slice(self, actions: List[Action], start: int, end: int):
        """Execute actions[start:end] handling nested loops."""
        i = start
        while i < end and not self._stop.is_set():
            a = actions[i]
            if a.type == 'loop_start':
                count = a.params.get('count', -1)
                # Find the matching loop_end
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
                i = j  # skip past loop_end
            elif a.type == 'loop_end':
                i += 1
            else:
                if self.on_step:
                    self.on_step(i)
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
