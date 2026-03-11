import uuid
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple


@dataclass
class Action:
    type: str  # 'click','right_click','double_click','move','key','delay','loop_start','loop_end'
    params: Dict[str, Any] = field(default_factory=dict)

    _ICONS = {
        'click': '🖱',
        'right_click': '🖱',
        'double_click': '🖱🖱',
        'move': '↗',
        'key': '⌨',
        'delay': '⏱',
        'loop_start': '🔁',
        'loop_end': '🔚',
        'if_image': '❓',
        'if_text': '❓',
        'elif_image': '❔',
        'elif_text': '❔',
        'else_start': '⛔',
        'end_if': '🔚',
    }

    def display_text(self) -> str:
        icon = self._ICONS.get(self.type, '•')
        p = self.params
        if self.type == 'click':
            return f"{icon}  点击  ({p.get('x', 0)}, {p.get('y', 0)})"
        elif self.type == 'right_click':
            return f"{icon}  右键  ({p.get('x', 0)}, {p.get('y', 0)})"
        elif self.type == 'double_click':
            return f"{icon}  双击  ({p.get('x', 0)}, {p.get('y', 0)})"
        elif self.type == 'move':
            return f"{icon}  移动  ({p.get('x', 0)}, {p.get('y', 0)})"
        elif self.type == 'key':
            return f"{icon}  按键  {p.get('key', '')}"
        elif self.type == 'delay':
            return f"{icon}  等待  {p.get('ms', 1000)} ms"
        elif self.type == 'loop_start':
            c = p.get('count', -1)
            return f"{icon}  开始循环  {'∞ 次' if c == -1 else f'{c} 次'}"
        elif self.type == 'loop_end':
            return f"{icon}  结束循环"
        elif self.type == 'if_image':
            return f"{icon}  如果出现图像则"
        elif self.type == 'if_text':
            return f"{icon}  如果出现文字则"
        elif self.type == 'elif_image':
            return f"{icon}  否则如果出现图像则"
        elif self.type == 'elif_text':
            return f"{icon}  否则如果出现文字则"
        elif self.type == 'else_start':
            return f"{icon}  否则"
        elif self.type == 'end_if':
            return f"{icon}  结束判断"
        return self.type

    def to_dict(self) -> dict:
        return {'type': self.type, 'params': dict(self.params)}

    @staticmethod
    def from_dict(d: dict) -> 'Action':
        return Action(type=d['type'], params=d.get('params', {}))


@dataclass
class MacroSequence:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = '新建宏'
    actions: List[Action] = field(default_factory=list)
    random_delay_min_ms: int = 50    # Minimum random delay between actions (ms)
    random_delay_max_ms: int = 200   # Maximum random delay between actions (ms)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'actions': [a.to_dict() for a in self.actions],
            'random_delay_min_ms': self.random_delay_min_ms,
            'random_delay_max_ms': self.random_delay_max_ms,
        }

    @staticmethod
    def from_dict(d: dict) -> 'MacroSequence':
        m = MacroSequence(id=d['id'], name=d['name'])
        m.actions = [Action.from_dict(a) for a in d.get('actions', [])]
        m.random_delay_min_ms = d.get('random_delay_min_ms', 50)
        m.random_delay_max_ms = d.get('random_delay_max_ms', 200)
        return m


@dataclass
class TriggerConfig:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = '新建触发器'
    enabled: bool = True
    type: str = 'image'          # 'image' | 'text'
    region: Tuple[int, int, int, int] = (0, 0, 200, 100)
    # Image trigger
    template_path: str = ''
    threshold: float = 0.80
    # Text trigger
    target_text: str = ''
    match_mode: str = 'contains'  # 'contains' | 'exact' | 'regex' | 'number'
    number_cmp: str = 'lte'       # 'lte' | 'gte' | 'eq'
    number_val: float = 0.0
    # On-trigger action
    action_type: str = 'run_macro'   # 'run_macro' | 'click' | 'key'
    action_params: Dict[str, Any] = field(default_factory=dict)
    check_interval_ms: int = 500
    cooldown_ms: int = 2000

    def to_dict(self) -> dict:
        return {
            'id': self.id, 'name': self.name, 'enabled': self.enabled,
            'type': self.type, 'region': list(self.region),
            'template_path': self.template_path, 'threshold': self.threshold,
            'target_text': self.target_text, 'match_mode': self.match_mode,
            'number_cmp': self.number_cmp, 'number_val': self.number_val,
            'action_type': self.action_type, 'action_params': self.action_params,
            'check_interval_ms': self.check_interval_ms, 'cooldown_ms': self.cooldown_ms,
        }

    @staticmethod
    def from_dict(d: dict) -> 'TriggerConfig':
        t = TriggerConfig(id=d['id'], name=d['name'])
        for k in ('enabled', 'type', 'template_path', 'threshold',
                  'target_text', 'match_mode', 'number_cmp', 'number_val',
                  'action_type', 'action_params',
                  'check_interval_ms', 'cooldown_ms'):
            if k in d:
                setattr(t, k, d[k])
        t.region = tuple(d.get('region', [0, 0, 200, 100]))
        return t


class MacroProject:
    def __init__(self):
        self.macros: List[MacroSequence] = []
        self.triggers: List[TriggerConfig] = []
        self.hotkey: str = '<f9>'
        self.mode: str = 'loop'  # 'loop' | 'conditional'
        self.input_backend: str = 'dd'  # 'dd' | 'interception'

    def to_dict(self) -> dict:
        return {
            'macros': [m.to_dict() for m in self.macros],
            'triggers': [t.to_dict() for t in self.triggers],
            'hotkey': self.hotkey,
            'mode': self.mode,
            'input_backend': self.input_backend,
        }

    @staticmethod
    def from_dict(d: dict) -> 'MacroProject':
        p = MacroProject()
        p.macros = [MacroSequence.from_dict(m) for m in d.get('macros', [])]
        p.triggers = [TriggerConfig.from_dict(t) for t in d.get('triggers', [])]
        p.hotkey = d.get('hotkey', '<f9>')
        p.mode = d.get('mode', 'loop')
        p.input_backend = d.get('input_backend', 'dd')
        return p

    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: str) -> 'MacroProject':
        with open(path, 'r', encoding='utf-8') as f:
            return MacroProject.from_dict(json.load(f))
