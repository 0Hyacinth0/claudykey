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
from .logger import get_logger
import re

logger = get_logger(__name__)


class MacroExecutor(threading.Thread):
    """Executes a MacroSequence in a background daemon thread."""

    def __init__(
        self,
        sequence: MacroSequence,
        project=None,
        on_step: Optional[Callable[[int], None]] = None,
        on_done: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(daemon=True, name='MacroExecutor')
        self.sequence = sequence
        self.project = project
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

    def _check_condition(self, trigger_id: str) -> bool:
        """检查触发器条件是否满足。
        
        Args:
            trigger_id: 触发器 ID。
            
        Returns:
            如果条件满足返回 True，否则返回 False。
        """
        if not self.project:
            logger.warning(f"无法检查条件: project 为空")
            return False
        
        trig = next((t for t in self.project.triggers if t.id == trigger_id), None)
        if not trig:
            logger.warning(f"触发器不存在: {trigger_id}")
            return False
        
        if not trig.enabled:
            logger.debug(f"触发器已禁用: {trig.name}")
            return False

        x, y, w, h = trig.region
        if w <= 0 or h <= 0:
            logger.warning(f"触发器 {trig.name} 区域无效: ({x}, {y}) {w}x{h}")
            return False
        
        try:
            img = scr.capture_region(x, y, w, h)
        except Exception as e:
            logger.error(f"触发器 {trig.name} 截图失败: {e}")
            return False

        if trig.type == 'image':
            if not trig.template_path:
                logger.warning(f"触发器 {trig.name} 未设置模板路径")
                return False
            tmpl = self._load_template(trig.template_path)
            if tmpl is None:
                logger.warning(f"触发器 {trig.name} 模板加载失败: {trig.template_path}")
                return False
            result = image_match.find_template(img, tmpl, trig.threshold)
            if result is not None:
                logger.debug(f"触发器 {trig.name} 图像匹配成功，置信度: {result[2]:.3f}")
                return True
            return False
            
        elif trig.type == 'text':
            try:
                allowlist = '0123456789.-%:/ ' if trig.match_mode == 'number' else None
                text = _ocr.recognize_text_only(img, allowlist=allowlist)
            except Exception as e:
                logger.error(f"触发器 {trig.name} OCR 识别失败: {e}")
                return False
            
            tgt = str(trig.target_text)
            mode = trig.match_mode
            
            if mode == 'exact':
                result = text.strip() == tgt.strip()
                logger.debug(f"触发器 {trig.name} 精确匹配: '{text.strip()}' {'==' if result else '!='} '{tgt.strip()}'")
                return result
            elif mode == 'contains':
                result = tgt in text
                logger.debug(f"触发器 {trig.name} 包含匹配: '{tgt}' {'在' if result else '不在'} '{text}'")
                return result
            elif mode == 'regex':
                try:
                    result = bool(re.search(tgt, text))
                    logger.debug(f"触发器 {trig.name} 正则匹配: /{tgt}/ {'匹配' if result else '不匹配'} '{text}'")
                    return result
                except re.error as e:
                    logger.error(f"触发器 {trig.name} 正则表达式无效: {e}")
                    return False
            elif mode == 'number':
                nums = re.findall(r'-?\d+\.?\d*', text)
                if not nums:
                    logger.debug(f"触发器 {trig.name} 未找到数字: '{text}'")
                    return False
                try:
                    val = float(nums[0])
                except ValueError:
                    logger.warning(f"触发器 {trig.name} 数字解析失败: '{nums[0]}'")
                    return False
                    
                cmp = getattr(trig, 'number_cmp', 'lte')
                ref_val = float(getattr(trig, 'number_val', 0.0))
                
                cmp_ops = {
                    'lt': lambda v, r: v < r,
                    'lte': lambda v, r: v <= r,
                    'eq': lambda v, r: abs(v - r) < 1e-6,
                    'gte': lambda v, r: v >= r,
                    'gt': lambda v, r: v > r,
                }
                
                cmp_symbols = {'lt': '<', 'lte': '≤', 'eq': '=', 'gte': '≥', 'gt': '>'}
                
                if cmp not in cmp_ops:
                    logger.warning(f"触发器 {trig.name} 未知比较操作符: {cmp}")
                    return False
                
                result = cmp_ops[cmp](val, ref_val)
                logger.debug(f"触发器 {trig.name} 数值比较: {val} {cmp_symbols.get(cmp, cmp)} {ref_val} = {result}")
                return result
        else:
            logger.warning(f"触发器 {trig.name} 未知类型: {trig.type}")
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
            elif a.type == 'if':
                j = i + 1
                depth = 1
                branches = []
                current_branch_start = j
                
                trigger_id_if = a.params.get('trigger_id', '')
                current_cond = lambda tid=trigger_id_if: self._check_condition(tid)

                while j < end and depth > 0:
                    t = actions[j].type
                    if t == 'if':
                        depth += 1
                    elif t == 'end_if':
                        depth -= 1
                        if depth == 0:
                            branches.append((current_branch_start, j, current_cond))
                            break
                    elif depth == 1 and t in ('elif', 'else_start'):
                        branches.append((current_branch_start, j, current_cond))
                        current_branch_start = j + 1
                        if t == 'else_start':
                            current_cond = lambda: True
                        else:
                            a_elif = actions[j]
                            trigger_id_elif = a_elif.params.get('trigger_id', '')
                            current_cond = lambda tid=trigger_id_elif: self._check_condition(tid)
                    j += 1

                for b_start, b_end, cond_check in branches:
                    if cond_check():
                        logger.debug(f"执行分支: actions[{b_start}:{b_end}]")
                        self._run_slice(actions, b_start, b_end)
                        break

                i = j if depth == 0 else j + 1
                
            elif a.type in ('loop_end', 'end_if', 'elif', 'else_start'):
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
