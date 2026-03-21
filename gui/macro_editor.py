"""Macro sequence editor widget — edit actions, loops, and run a macro."""
import os
from typing import Optional, List

from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QDialog, QFormLayout,
    QSpinBox, QComboBox, QDialogButtonBox, QFrame, QSizePolicy,
    QMenu, QApplication, QStackedWidget,
)

from core.macro import Action, MacroSequence
from .region_selector import PointSelector


# ══════════════════════════════════════════════════════════════
#  Action type → visual tag mapping
#    (label, dot_color, tag_bg, tag_border, tag_text_color)
# ══════════════════════════════════════════════════════════════
_TAG_STYLES = {
    'click':        ('⌖ 点击',     '#3b82f6', 'transparent',  'rgba(59,130,246,0.4)',  '#93c5fd'),
    'right_click':  ('⌖ 右键',     '#3b82f6', 'transparent',  'rgba(59,130,246,0.4)',  '#93c5fd'),
    'double_click': ('⌖ 双击',     '#3b82f6', 'transparent',  'rgba(59,130,246,0.4)',  '#93c5fd'),
    'move':         ('↗ 移动',     '#3b82f6', 'transparent',  'rgba(59,130,246,0.4)',  '#93c5fd'),
    'key':          ('⌘ 按键',     '#22c55e', 'transparent',  'rgba(34,197,94,0.4)',   '#86efac'),
    'delay':        ('⧗ 延时',     '#fbbf24', 'transparent',  'rgba(251,191,36,0.4)',  '#fde68a'),
    'loop_start':   ('⟳ 循环开始', '#a855f7', 'transparent',  'rgba(168,85,247,0.4)',  '#d8b4fe'),
    'loop_end':     ('⟲ 循环结束', '#a855f7', 'transparent',  'rgba(168,85,247,0.4)',  '#d8b4fe'),
    'if':           ('⭃ 如果',     '#06b6d4', 'transparent',  'rgba(6,182,212,0.4)',   '#67e8f9'),
    'elif':         ('⭃ 否则如果', '#06b6d4', 'transparent',  'rgba(6,182,212,0.4)',   '#67e8f9'),
    'else_start':   ('⭃ 否则',     '#06b6d4', 'transparent',  'rgba(6,182,212,0.4)',   '#67e8f9'),
    'end_if':       ('⭃ 结束判断', '#06b6d4', 'transparent',  'rgba(6,182,212,0.4)',   '#67e8f9'),
}

def _param_text(action: Action) -> str:
    """Extract a short parameter summary for display."""
    p = action.params
    if action.type in ('click', 'right_click', 'double_click', 'move'):
        return f"({p.get('x', 0)}, {p.get('y', 0)})"
    elif action.type == 'key':
        return p.get('key', '')
    elif action.type == 'delay':
        return f"{p.get('ms', 1000)} ms"
    elif action.type == 'loop_start':
        c = p.get('count', -1)
        return '∞ 次' if c == -1 else f'{c} 次'
    elif action.type in ('if', 'elif'):
        return p.get('trigger_name', '未选择')
    return ''


def _make_action_widget(action: Action, depth: int = 0) -> QWidget:
    """Build a rich list item widget for an Action."""
    w = QWidget()
    w.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
    w.setFixedHeight(24)
    lay = QHBoxLayout(w)
    lay.setContentsMargins(6 + depth * 20, 0, 8, 0)
    lay.setSpacing(8)
    lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    # Resolve style
    info = _TAG_STYLES.get(action.type, ('•', '#7c6ef8', 'rgba(99,102,241,0.25)', 'rgba(99,102,241,0.3)', '#a5b4fc'))
    label, dot_color, tag_bg, tag_border, tag_fg = info

    # Color dot
    dot = QFrame()
    dot.setFixedSize(8, 8)
    dot.setStyleSheet(f'''
        background: {dot_color};
        border-radius: 4px;
        min-width: 8px; max-width: 8px;
        min-height: 8px; max-height: 8px;
    ''')
    lay.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)

    # Type tag — compact single-line capsule
    tag = QLabel(label)
    tag.setFixedHeight(18)
    tag.setStyleSheet(f'''
        QLabel {{
            background: {tag_bg};
            color: {tag_fg};
            border: 1px solid {tag_border};
            border-radius: 6px;
            padding: 0px 8px;
            font-size: 10px;
            font-weight: bold;
        }}
    ''')
    lay.addWidget(tag, 0, Qt.AlignmentFlag.AlignVCenter)

    # Param text
    pt = _param_text(action)
    if pt:
        param = QLabel(pt)
        param.setStyleSheet('''
            QLabel {
                color: rgba(200, 205, 232, 0.65);
                font-size: 12px;
                background: transparent;
            }
        ''')
        lay.addWidget(param, 0, Qt.AlignmentFlag.AlignVCenter)

    lay.addStretch()
    return w


# ══════════════════════════════════════════════════════════════
#  Action dialog — create / edit a single Action
# ══════════════════════════════════════════════════════════════
class ActionDialog(QDialog):
    ACTION_TYPES = [
        ('click',        '⌖  左键点击'),
        ('right_click',  '⌖  右键点击'),
        ('double_click', '⌖  双击'),
        ('move',         '↗  移动鼠标'),
        ('key',          '⌘  按键'),
        ('delay',        '⧗  等待延时'),
        ('loop_start',   '⟳  开始循环'),
        ('loop_end',     '⟲  结束循环'),
        ('if',           '⭃  如果发生触发事件则...'),
        ('elif',         '⭃  否则如果发生触发事件则...'),
        ('else_start',   '⭃  否则...'),
        ('end_if',       '⭃  结束判断'),
    ]

    def __init__(self, action: Optional[Action] = None, parent=None, project=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle('编辑动作')
        self.setMinimumWidth(400)
        self.setModal(True)
        self._picker: Optional[PointSelector] = None
        self._picked_x = QSpinBox()
        self._picked_y = QSpinBox()

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # Type selector in a card
        type_card = QFrame()
        type_card.setObjectName('panel_card')
        tc_lay = QVBoxLayout(type_card)
        tc_lay.setContentsMargins(14, 14, 14, 14)
        type_lbl = QLabel('动作类型')
        type_lbl.setObjectName('lbl_section')
        tc_lay.addWidget(type_lbl)
        self.type_combo = QComboBox()
        for code, label in self.ACTION_TYPES:
            self.type_combo.addItem(label, code)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        tc_lay.addWidget(self.type_combo)
        layout.addWidget(type_card)

        # Parameter form (dynamic)
        self.form_frame = QFrame()
        self.form_frame.setObjectName('panel_card')
        self.form_layout = QFormLayout(self.form_frame)
        self.form_layout.setSpacing(10)
        self.form_layout.setContentsMargins(14, 14, 14, 14)
        layout.addWidget(self.form_frame)

        # Stored param values (survive widget recreation)
        self._val_x = 0
        self._val_y = 0
        self._val_key = ''
        self._val_ms = 500
        self._val_count = 3
        # Condition params
        self._val_trigger_id = ''
        self._val_trigger_name = ''
        
        # External dialogs
        self._sel = None

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        # Load existing action if editing
        if action:
            idx = next((i for i, (c, _) in enumerate(self.ACTION_TYPES)
                        if c == action.type), 0)
            self.type_combo.setCurrentIndex(idx)
            p = action.params
            self._val_x = p.get('x', 0)
            self._val_y = p.get('y', 0)
            self._val_key = p.get('key', '')
            self._val_ms = p.get('ms', 500)
            self._val_count = p.get('count', 3)
            self._val_trigger_id = p.get('trigger_id', '')
            self._val_trigger_name = p.get('trigger_name', '')
        else:
            self.type_combo.setCurrentIndex(0)

        self._on_type_changed()

    def _clear_form(self):
        # Save current widget values before destroying them
        self._sync_values_from_widgets()
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)

    def _sync_values_from_widgets(self):
        """Save current widget values to plain Python vars."""
        if hasattr(self, '_w_x') and self._w_x is not None:
            try:
                self._val_x = self._w_x.value()
                self._val_y = self._w_y.value()
            except RuntimeError:
                pass
        if hasattr(self, '_w_key') and self._w_key is not None:
            try:
                self._val_key = self._w_key.text()
            except RuntimeError:
                pass
        if hasattr(self, '_w_ms') and self._w_ms is not None:
            try:
                self._val_ms = self._w_ms.value()
            except RuntimeError:
                pass
        if hasattr(self, '_w_count') and self._w_count is not None:
            try:
                self._val_count = self._w_count.value()
            except RuntimeError:
                pass
        if hasattr(self, '_w_trigger') and self._w_trigger is not None:
            try:
                selected_items = self._w_trigger.selectedItems()
                ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items if item.data(Qt.ItemDataRole.UserRole)]
                names = [item.text() for item in selected_items]
                self._val_trigger_id = ','.join(ids) if ids else ''
                self._val_trigger_name = ' & '.join(names) if names else ''
            except Exception:
                pass

    def _on_type_changed(self):
        self._clear_form()
        t = self.type_combo.currentData()
        # Reset widget refs
        self._w_x = self._w_y = self._w_key = self._w_ms = self._w_count = None

        if t in ('click', 'right_click', 'double_click', 'move'):
            self._w_x = QSpinBox(); self._w_x.setRange(-9999, 9999); self._w_x.setValue(self._val_x)
            self._w_y = QSpinBox(); self._w_y.setRange(-9999, 9999); self._w_y.setValue(self._val_y)
            btn_pick = QPushButton('⌖  屏幕拾取坐标')
            btn_pick.setObjectName('btn_accent')
            btn_pick.clicked.connect(self._pick_point)
            self.form_layout.addRow('X 坐标:', self._w_x)
            self.form_layout.addRow('Y 坐标:', self._w_y)
            self.form_layout.addRow('', btn_pick)
        elif t == 'key':
            self._w_key = QLineEdit()
            self._w_key.setPlaceholderText('ctrl+c  /  f5  /  enter')
            self._w_key.setText(self._val_key)
            self.form_layout.addRow('按键组合:', self._w_key)
            hint = QLabel('示例: ctrl+c、f5、alt+F4、enter')
            hint.setStyleSheet('color:rgba(180,185,220,0.4);font-size:11px;')
            self.form_layout.addRow('', hint)
        elif t == 'delay':
            self._w_ms = QSpinBox(); self._w_ms.setRange(1, 60000)
            self._w_ms.setSuffix(' ms'); self._w_ms.setValue(self._val_ms)
            self.form_layout.addRow('等待时间:', self._w_ms)
        elif t == 'loop_start':
            self._w_count = QSpinBox(); self._w_count.setRange(-1, 9999)
            self._w_count.setSpecialValueText('∞ 无限循环')
            self._w_count.setValue(self._val_count)
            self.form_layout.addRow('循环次数:', self._w_count)
            hint = QLabel('-1 = 无限循环，直到手动停止')
            hint.setStyleSheet('color:rgba(180,185,220,0.4);font-size:11px;')
            self.form_layout.addRow('', hint)
        elif t == 'loop_end':
            lbl = QLabel('无参数 — 配合"开始循环"使用')
            lbl.setStyleSheet('color:rgba(180,185,220,0.4);')
            self.form_layout.addRow(lbl)
            
        elif t in ('else_start', 'end_if'):
            lbl = QLabel('无参数 — 配合条件控制流使用')
            lbl.setStyleSheet('color:rgba(180,185,220,0.4);')
            self.form_layout.addRow(lbl)
            
        elif t in ('if', 'elif'):
            from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
            self._w_trigger = QListWidget()
            self._w_trigger.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
            self._w_trigger.setFixedHeight(80)
            self._w_trigger.setObjectName('list_trigger_multi')
            self._w_trigger.setStyleSheet('background: rgba(255,255,255,0.02); border-radius: 6px;')
            
            if self.project and getattr(self.project, 'triggers', None):
                saved_ids = [s.strip() for s in self._val_trigger_id.split(',')] if self._val_trigger_id else []
                for trig in self.project.triggers:
                    item = QListWidgetItem(f'{trig.name}')
                    item.setData(Qt.ItemDataRole.UserRole, trig.id)
                    self._w_trigger.addItem(item)
                    if trig.id in saved_ids:
                        item.setSelected(True)
            else:
                self._w_trigger.addItem('未加载或无触发器')
            
            self.form_layout.addRow('选择触发事件:\n(按 Ctrl/Cmd 多选)', self._w_trigger)

    def _select_region(self):
        self._sync_values_from_widgets()
        self.hide()
        from .region_selector import RegionSelector
        self._sel = RegionSelector()
        self._sel.region_selected.connect(self._on_region_selected)

    def _on_region_selected(self, x, y, w, h):
        self._val_region = (x, y, w, h)
        self.show()
        self._on_type_changed()

    def _select_template(self):
        from PyQt6.QtWidgets import QFileDialog
        fname, _ = QFileDialog.getOpenFileName(
            self, '选择模板图像', '',
            'Images (*.png *.jpg *.bmp *.webp);;All Files (*)')
        if fname:
            self._val_template_path = fname
            self._on_type_changed()

    def _pick_point(self):
        self._sync_values_from_widgets()
        self.hide()
        self._picker = PointSelector()
        self._picker.point_selected.connect(self._on_point_picked)
        self._picker.cancelled.connect(self.show)

    def _on_point_picked(self, x: int, y: int):
        self._val_x = x
        self._val_y = y
        self.show()
        self._on_type_changed()  # Rebuild form with new values

    def get_action(self) -> Action:
        self._sync_values_from_widgets()
        t = self.type_combo.currentData()
        params = {}
        if t in ('click', 'right_click', 'double_click', 'move'):
            params = {'x': self._val_x, 'y': self._val_y}
        elif t == 'key':
            params = {'key': self._val_key.strip()}
        elif t == 'delay':
            params = {'ms': self._val_ms}
        elif t == 'loop_start':
            params = {'count': self._val_count}
        elif t in ('if', 'elif'):
            if hasattr(self, '_w_trigger') and self._w_trigger is not None:
                self._val_trigger_id = self._w_trigger.currentData()
                self._val_trigger_name = self._w_trigger.currentText()
            params = {
                'trigger_id': self._val_trigger_id,
                'trigger_name': self._val_trigger_name
            }
        return Action(type=t, params=params)


# ══════════════════════════════════════════════════════════════
#  Macro editor panel
# ══════════════════════════════════════════════════════════════
class MacroEditorPanel(QWidget):
    """Full editing panel for a single MacroSequence."""
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sequence: Optional[MacroSequence] = None
        self._current_step: int = -1
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # ── Info card: name + random delay ──
        info_card = QFrame()
        info_card.setObjectName('panel_card')
        ic_lay = QVBoxLayout(info_card)
        ic_lay.setContentsMargins(16, 14, 16, 14)
        ic_lay.setSpacing(10)

        # Name row
        name_row = QHBoxLayout()
        name_lbl = QLabel('宏名称')
        name_lbl.setObjectName('lbl_section')
        name_lbl.setFixedWidth(56)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('输入宏名称…')
        self.name_edit.textEdited.connect(self._on_name_edited)
        name_row.addWidget(name_lbl)
        name_row.addWidget(self.name_edit)
        ic_lay.addLayout(name_row)

        # Random delay row
        delay_row = QHBoxLayout()
        delay_icon = QLabel('⚄')
        delay_icon.setFixedWidth(20)
        delay_row.addWidget(delay_icon)
        delay_row.addWidget(QLabel('随机延迟'))
        self._delay_min = QSpinBox()
        self._delay_min.setRange(0, 5000)
        self._delay_min.setSuffix(' ms')
        self._delay_min.setValue(50)
        self._delay_min.setToolTip('每个动作前的最小随机延迟')
        self._delay_min.valueChanged.connect(self._on_delay_changed)
        delay_row.addWidget(self._delay_min)
        sep_lbl = QLabel('~')
        sep_lbl.setStyleSheet('color: rgba(124,110,248,0.5); font-weight: bold;')
        delay_row.addWidget(sep_lbl)
        self._delay_max = QSpinBox()
        self._delay_max.setRange(0, 5000)
        self._delay_max.setSuffix(' ms')
        self._delay_max.setValue(200)
        self._delay_max.setToolTip('每个动作前的最大随机延迟')
        self._delay_max.valueChanged.connect(self._on_delay_changed)
        delay_row.addWidget(self._delay_max)
        delay_hint = QLabel('拟真')
        delay_hint.setStyleSheet('color:rgba(180,185,220,0.35);font-size:11px;')
        delay_row.addWidget(delay_hint)
        delay_row.addStretch()
        ic_lay.addLayout(delay_row)

        root.addWidget(info_card)

        # ── Toolbar ──
        tb = QHBoxLayout()
        tb.setSpacing(4)

        self._btn_add = self._tb_btn('＋ 添加', '添加动作', self._add_action)
        self._btn_edit = self._tb_btn('✎ 编辑', '编辑动作', self._edit_action)
        self._btn_del = self._tb_btn('✕ 删除', '删除动作', self._delete_action)

        tb.addWidget(self._btn_add)
        tb.addWidget(self._btn_edit)
        tb.addWidget(self._btn_del)

        # Separator
        sep = QFrame()
        sep.setObjectName('toolbar_separator')
        sep.setFixedHeight(24)
        tb.addWidget(sep)

        self._btn_up = self._tb_btn('↑ 上移', '上移', self._move_up)
        self._btn_dn = self._tb_btn('↓ 下移', '下移', self._move_down)
        tb.addWidget(self._btn_up)
        tb.addWidget(self._btn_dn)

        tb.addStretch()
        root.addLayout(tb)

        # ── Action list with stacked empty state ──
        list_container = QWidget()
        lc_lay = QVBoxLayout(list_container)
        lc_lay.setContentsMargins(0, 0, 0, 0)
        lc_lay.setSpacing(0)

        self._list_stack = QStackedWidget()

        # Page 0: the actual list
        self.list = QListWidget()
        self.list.setAlternatingRowColors(False)
        self.list.itemDoubleClicked.connect(self._edit_action)
        self._list_stack.addWidget(self.list)

        # Page 1: empty state
        empty_w = QWidget()
        empty_lay = QVBoxLayout(empty_w)
        empty_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon = QLabel('◇')
        empty_icon.setObjectName('empty_state_icon')
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text = QLabel('点击「＋ 添加」创建第一个动作')
        empty_text.setObjectName('empty_state')
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_lay.addWidget(empty_icon)
        empty_lay.addWidget(empty_text)
        self._list_stack.addWidget(empty_w)

        lc_lay.addWidget(self._list_stack)
        root.addWidget(list_container, 1)

        # ── Bottom: test button + hint ──
        bottom_card = QFrame()
        bottom_card.setObjectName('panel_card')
        bc_lay = QVBoxLayout(bottom_card)
        bc_lay.setContentsMargins(14, 10, 14, 10)
        bc_lay.setSpacing(4)

        run_row = QHBoxLayout()
        self._btn_run_solo = QPushButton('▶  测试当前宏')
        self._btn_run_solo.setObjectName('btn_run')
        self._btn_run_solo.clicked.connect(self._run_solo)
        run_row.addStretch()
        run_row.addWidget(self._btn_run_solo)
        run_row.addStretch()
        bc_lay.addLayout(run_row)

        hint_lbl = QLabel('仅运行一次此宏进行测试，不开启全局触发检测')
        hint_lbl.setStyleSheet('color: rgba(180,185,220,0.3); font-size: 11px;')
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bc_lay.addWidget(hint_lbl)

        root.addWidget(bottom_card)

    @staticmethod
    def _tb_btn(text: str, tip: str, slot) -> QPushButton:
        b = QPushButton(text)
        b.setObjectName('btn_toolbar')
        b.setToolTip(tip)
        b.clicked.connect(slot)
        return b

    # ------------------------------------------------------------------ data
    def load_sequence(self, seq: MacroSequence):
        self._building = True
        self.sequence = seq
        self.name_edit.setText(seq.name)
        self._delay_min.setValue(seq.random_delay_min_ms)
        self._delay_max.setValue(seq.random_delay_max_ms)
        self._refresh_list()
        self._building = False

    def _refresh_list(self):
        self.list.clear()
        if not self.sequence or not self.sequence.actions:
            self._list_stack.setCurrentIndex(1)  # show empty state
            return

        self._list_stack.setCurrentIndex(0)  # show list
        for i, action in enumerate(self.sequence.actions):
            depth = self._depth(i)
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, i)
            widget = _make_action_widget(action, depth)
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)

    def _depth(self, index: int) -> int:
        """Calculate nesting depth for indentation."""
        if not self.sequence:
            return 0
        depth = 0
        for i, a in enumerate(self.sequence.actions[:index]):
            if a.type in ('loop_start', 'if'):
                depth += 1
            elif a.type in ('loop_end', 'end_if'):
                depth = max(0, depth - 1)
                
        # Adjust for lines that are closers/branches themselves
        current_a = self.sequence.actions[index]
        if current_a.type in ('loop_end', 'elif', 'else_start', 'end_if'):
            depth = max(0, depth - 1)
            
        return depth

    def _on_delay_changed(self):
        if getattr(self, '_building', False):
            return
        if self.sequence:
            self.sequence.random_delay_min_ms = self._delay_min.value()
            self.sequence.random_delay_max_ms = self._delay_max.value()
            self.changed.emit()

    def highlight_step(self, index: int):
        self._current_step = index
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == index:
                item.setBackground(QColor(99, 102, 241, 50))
            else:
                item.setBackground(QColor(0, 0, 0, 0))

    def clear_highlight(self):
        for i in range(self.list.count()):
            self.list.item(i).setBackground(QColor(0, 0, 0, 0))

    # ------------------------------------------------------------------ actions
    def _on_name_edited(self, text: str):
        if self.sequence:
            self.sequence.name = text
            self.changed.emit()

    def _selected_index(self) -> int:
        items = self.list.selectedItems()
        if not items:
            return -1
        return items[0].data(Qt.ItemDataRole.UserRole)

    def _add_action(self):
        if not self.sequence:
            return
        dlg = ActionDialog(parent=self, project=getattr(self, 'project', None))
        if dlg.exec() == QDialog.DialogCode.Accepted:
            action = dlg.get_action()
            idx = self._selected_index()
            if idx == -1:
                self.sequence.actions.append(action)
            else:
                self.sequence.actions.insert(idx + 1, action)
            self._refresh_list()
            self.changed.emit()

    def _edit_action(self):
        if not self.sequence:
            return
        idx = self._selected_index()
        if idx < 0:
            return
        dlg = ActionDialog(action=self.sequence.actions[idx], parent=self, project=getattr(self, 'project', None))
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.sequence.actions[idx] = dlg.get_action()
            self._refresh_list()
            self.changed.emit()

    def _delete_action(self):
        if not self.sequence:
            return
        idx = self._selected_index()
        if idx < 0:
            return
        del self.sequence.actions[idx]
        self._refresh_list()
        self.changed.emit()

    def _move_up(self):
        if not self.sequence:
            return
        idx = self._selected_index()
        if idx > 0:
            acts = self.sequence.actions
            acts[idx - 1], acts[idx] = acts[idx], acts[idx - 1]
            self._refresh_list()
            self.list.setCurrentRow(idx - 1)
            self.changed.emit()

    def _move_down(self):
        if not self.sequence:
            return
        idx = self._selected_index()
        acts = self.sequence.actions
        if 0 <= idx < len(acts) - 1:
            acts[idx], acts[idx + 1] = acts[idx + 1], acts[idx]
            self._refresh_list()
            self.list.setCurrentRow(idx + 1)
            self.changed.emit()

    def _run_solo(self):
        """Run just this macro — signal to main window."""
        self.run_solo_requested = True
        self.changed.emit()  # main window watches this via a dedicated signal
