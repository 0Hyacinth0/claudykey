"""Macro sequence editor widget — edit actions, loops, and run a macro."""
import os
from typing import Optional, List

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QDialog, QFormLayout,
    QSpinBox, QComboBox, QDialogButtonBox, QFrame, QSizePolicy,
    QMenu, QApplication,
)

from core.macro import Action, MacroSequence
from .region_selector import PointSelector


# ══════════════════════════════════════════════════════════════
#  Action dialog — create / edit a single Action
# ══════════════════════════════════════════════════════════════
class ActionDialog(QDialog):
    ACTION_TYPES = [
        ('click',        '🖱  左键点击'),
        ('right_click',  '🖱  右键点击'),
        ('double_click', '🖱🖱 双击'),
        ('move',         '↗  移动鼠标'),
        ('key',          '⌨  按键'),
        ('delay',        '⏱  等待延时'),
        ('loop_start',   '🔁  开始循环'),
        ('loop_end',     '🔚  结束循环'),
    ]

    def __init__(self, action: Optional[Action] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('编辑动作')
        self.setMinimumWidth(360)
        self.setModal(True)
        self._picker: Optional[PointSelector] = None
        self._picked_x = QSpinBox()
        self._picked_y = QSpinBox()

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel('动作类型:'))
        self.type_combo = QComboBox()
        for code, label in self.ACTION_TYPES:
            self.type_combo.addItem(label, code)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_combo, 1)
        layout.addLayout(type_row)

        # Parameter form (dynamic)
        self.form_frame = QFrame()
        self.form_frame.setObjectName('panel_card')
        self.form_layout = QFormLayout(self.form_frame)
        self.form_layout.setSpacing(8)
        layout.addWidget(self.form_frame)

        # Stored param values (survive widget recreation)
        self._val_x = 0
        self._val_y = 0
        self._val_key = ''
        self._val_ms = 500
        self._val_count = 3

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

    def _on_type_changed(self):
        self._clear_form()
        t = self.type_combo.currentData()
        # Reset widget refs
        self._w_x = self._w_y = self._w_key = self._w_ms = self._w_count = None

        if t in ('click', 'right_click', 'double_click', 'move'):
            self._w_x = QSpinBox(); self._w_x.setRange(-9999, 9999); self._w_x.setValue(self._val_x)
            self._w_y = QSpinBox(); self._w_y.setRange(-9999, 9999); self._w_y.setValue(self._val_y)
            btn_pick = QPushButton('🎯  屏幕拾取坐标')
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
            hint.setStyleSheet('color:#5050a0;font-size:11px;')
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
            hint.setStyleSheet('color:#5050a0;font-size:11px;')
            self.form_layout.addRow('', hint)
        elif t == 'loop_end':
            lbl = QLabel('无参数 — 配合"开始循环"使用')
            lbl.setStyleSheet('color:#5050a0;')
            self.form_layout.addRow(lbl)

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
        root.setSpacing(8)

        # Name row
        name_row = QHBoxLayout()
        name_lbl = QLabel('宏名称:')
        name_lbl.setFixedWidth(56)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('输入宏名称…')
        self.name_edit.textEdited.connect(self._on_name_edited)
        name_row.addWidget(name_lbl)
        name_row.addWidget(self.name_edit)
        root.addLayout(name_row)

        # Random delay row
        delay_row = QHBoxLayout()
        delay_row.addWidget(QLabel('🎲 随机延迟:'))
        self._delay_min = QSpinBox()
        self._delay_min.setRange(0, 5000)
        self._delay_min.setSuffix(' ms')
        self._delay_min.setValue(50)
        self._delay_min.setToolTip('每个动作前的最小随机延迟')
        self._delay_min.valueChanged.connect(self._on_delay_changed)
        delay_row.addWidget(self._delay_min)
        delay_row.addWidget(QLabel('~'))
        self._delay_max = QSpinBox()
        self._delay_max.setRange(0, 5000)
        self._delay_max.setSuffix(' ms')
        self._delay_max.setValue(200)
        self._delay_max.setToolTip('每个动作前的最大随机延迟')
        self._delay_max.valueChanged.connect(self._on_delay_changed)
        delay_row.addWidget(self._delay_max)
        delay_hint = QLabel('拟真')
        delay_hint.setStyleSheet('color:#5050a0;font-size:11px;')
        delay_row.addWidget(delay_hint)
        delay_row.addStretch()
        root.addLayout(delay_row)

        # Toolbar
        tb = QHBoxLayout()
        self._btn_add = self._tb_btn('➕', '添加动作', self._add_action)
        self._btn_edit = self._tb_btn('✏️', '编辑动作', self._edit_action)
        self._btn_del = self._tb_btn('🗑', '删除动作', self._delete_action)
        self._btn_up = self._tb_btn('⬆', '上移', self._move_up)
        self._btn_dn = self._tb_btn('⬇', '下移', self._move_down)
        for b in (self._btn_add, self._btn_edit, self._btn_del,
                  self._btn_up, self._btn_dn):
            tb.addWidget(b)
        tb.addStretch()
        root.addLayout(tb)

        # Action list
        self.list = QListWidget()
        self.list.setAlternatingRowColors(False)
        self.list.itemDoubleClicked.connect(self._edit_action)
        self.list.setFont(QFont("Consolas", 12))
        root.addWidget(self.list, 1)

        # Run this macro button
        run_row = QHBoxLayout()
        self._btn_run_solo = QPushButton('▶  运行此宏')
        self._btn_run_solo.setObjectName('btn_run')
        self._btn_run_solo.clicked.connect(self._run_solo)
        run_row.addStretch()
        run_row.addWidget(self._btn_run_solo)
        root.addLayout(run_row)

    @staticmethod
    def _tb_btn(icon: str, tip: str, slot) -> QPushButton:
        b = QPushButton(icon)
        b.setObjectName('btn_icon')
        b.setToolTip(tip)
        b.setFixedWidth(36)
        b.clicked.connect(slot)
        return b

    # ------------------------------------------------------------------ data
    def load_sequence(self, seq: MacroSequence):
        self.sequence = seq
        self.name_edit.setText(seq.name)
        self._delay_min.setValue(seq.random_delay_min_ms)
        self._delay_max.setValue(seq.random_delay_max_ms)
        self._refresh_list()

    def _refresh_list(self):
        self.list.clear()
        if not self.sequence:
            return
        for i, action in enumerate(self.sequence.actions):
            indent = self._indent(i)
            item = QListWidgetItem(f'{indent}{action.display_text()}')
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.list.addItem(item)

    def _indent(self, index: int) -> str:
        """Return leading spaces to visually indent loop body actions."""
        if not self.sequence:
            return ''
        depth = 0
        for i, a in enumerate(self.sequence.actions[:index]):
            if a.type == 'loop_start':
                depth += 1
            elif a.type == 'loop_end':
                depth = max(0, depth - 1)
        return '    ' * depth

    def _on_delay_changed(self):
        if self.sequence:
            self.sequence.random_delay_min_ms = self._delay_min.value()
            self.sequence.random_delay_max_ms = self._delay_max.value()
            self.changed.emit()

    def highlight_step(self, index: int):
        self._current_step = index
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == index:
                item.setBackground(QColor(30, 60, 30))
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
        dlg = ActionDialog(parent=self)
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
        dlg = ActionDialog(action=self.sequence.actions[idx], parent=self)
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
