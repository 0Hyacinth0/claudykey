"""Trigger configuration editor — image trigger and text trigger setup."""
import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QCheckBox, QComboBox, QSlider, QSpinBox,
    QPushButton, QFrame, QFileDialog, QGroupBox,
)

from core.macro import TriggerConfig, MacroProject
from .region_selector import RegionSelector


class TriggerEditorPanel(QWidget):
    """Full editing panel for a single TriggerConfig."""
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trigger: TriggerConfig | None = None
        self.project: MacroProject | None = None
        self._sel: RegionSelector | None = None
        self._building = False
        self._build_ui()

    # ──────────────────────────────────────────── UI construction
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # ── Header row ──
        hdr = QHBoxLayout()
        name_lbl = QLabel('触发器名称:')
        name_lbl.setFixedWidth(80)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('输入触发器名称…')
        self.name_edit.textEdited.connect(lambda v: self._set('name', v))
        self.enabled_chk = QCheckBox('启用')
        self.enabled_chk.stateChanged.connect(
            lambda: self._set('enabled', self.enabled_chk.isChecked()))
        hdr.addWidget(name_lbl)
        hdr.addWidget(self.name_edit, 1)
        hdr.addWidget(self.enabled_chk)
        root.addLayout(hdr)

        # ── Type selector ──
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel('触发类型:'))
        self.type_combo = QComboBox()
        self.type_combo.addItem('🖼  图像识别', 'image')
        self.type_combo.addItem('📝  文字识别  (OCR)', 'text')
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_combo, 1)
        root.addLayout(type_row)

        # ── Detection region ──
        reg_grp = QGroupBox('检测区域')
        reg_layout = QHBoxLayout(reg_grp)
        self.region_lbl = QLabel('未设置')
        self.region_lbl.setStyleSheet('color:#5050a0;')
        btn_sel = QPushButton('🔲  框选区域')
        btn_sel.setObjectName('btn_accent')
        btn_sel.clicked.connect(self._select_region)
        reg_layout.addWidget(self.region_lbl, 1)
        reg_layout.addWidget(btn_sel)
        root.addWidget(reg_grp)

        # ── Image trigger group ──
        self.img_grp = QGroupBox('图像识别设置')
        img_layout = QVBoxLayout(self.img_grp)

        tmpl_row = QHBoxLayout()
        self.tmpl_lbl = QLabel('无模板')
        self.tmpl_lbl.setStyleSheet('color:#5050a0;')
        btn_capture = QPushButton('📷  截取模板')
        btn_capture.setObjectName('btn_accent')
        btn_capture.clicked.connect(self._capture_template)
        btn_load = QPushButton('📁  选择文件')
        btn_load.clicked.connect(self._load_template_file)
        self.tmpl_preview = QLabel()
        self.tmpl_preview.setFixedSize(80, 50)
        self.tmpl_preview.setStyleSheet(
            'border:1px solid #2a2a55;border-radius:4px;background:#0a0a1a;')
        self.tmpl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tmpl_row.addWidget(self.tmpl_lbl, 1)
        tmpl_row.addWidget(btn_capture)
        tmpl_row.addWidget(btn_load)
        img_layout.addLayout(tmpl_row)
        img_layout.addWidget(self.tmpl_preview)

        thr_row = QHBoxLayout()
        thr_row.addWidget(QLabel('相似度阈值:'))
        self.thr_slider = QSlider(Qt.Orientation.Horizontal)
        self.thr_slider.setRange(50, 100)
        self.thr_slider.setValue(80)
        self.thr_slider.valueChanged.connect(self._on_threshold_changed)
        self.thr_val_lbl = QLabel('0.80')
        self.thr_val_lbl.setFixedWidth(36)
        thr_row.addWidget(self.thr_slider, 1)
        thr_row.addWidget(self.thr_val_lbl)
        img_layout.addLayout(thr_row)
        root.addWidget(self.img_grp)

        # ── Text trigger group ──
        self.txt_grp = QGroupBox('文字识别设置  (OCR)')
        txt_layout = QFormLayout(self.txt_grp)
        self.txt_edit = QLineEdit()
        self.txt_edit.setPlaceholderText('目标文字…')
        self.txt_edit.textEdited.connect(lambda v: self._set('target_text', v))
        self.match_combo = QComboBox()
        self.match_combo.addItem('包含', 'contains')
        self.match_combo.addItem('精确匹配', 'exact')
        self.match_combo.addItem('正则表达式', 'regex')
        self.match_combo.currentIndexChanged.connect(
            lambda: self._set('match_mode', self.match_combo.currentData()))
        txt_layout.addRow('目标文字:', self.txt_edit)
        txt_layout.addRow('匹配方式:', self.match_combo)
        root.addWidget(self.txt_grp)

        # ── Action on trigger ──
        act_grp = QGroupBox('触发后执行')
        act_layout = QFormLayout(act_grp)
        self.act_combo = QComboBox()
        self.act_combo.addItem('执行宏', 'run_macro')
        self.act_combo.addItem('鼠标点击', 'click')
        self.act_combo.addItem('发送按键', 'key')
        self.act_combo.currentIndexChanged.connect(self._on_act_changed)

        self.macro_combo = QComboBox()   # shown for run_macro
        self.act_key_edit = QLineEdit()  # shown for key
        self.act_key_edit.setPlaceholderText('例: ctrl+v')
        self.act_row_macro = QHBoxLayout()
        self.act_row_macro.addWidget(self.macro_combo)
        act_layout.addRow('动作:', self.act_combo)
        act_layout.addRow('宏:', self.macro_combo)
        act_layout.addRow('按键:', self.act_key_edit)
        root.addWidget(act_grp)

        # ── Intervals ──
        iv_row = QHBoxLayout()
        iv_row.addWidget(QLabel('检测间隔:'))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 10000)
        self.interval_spin.setSingleStep(100)
        self.interval_spin.setSuffix(' ms')
        self.interval_spin.setValue(500)
        self.interval_spin.valueChanged.connect(
            lambda v: self._set('check_interval_ms', v))
        iv_row.addWidget(self.interval_spin)
        iv_row.addSpacing(16)
        iv_row.addWidget(QLabel('冷却时间:'))
        self.cooldown_spin = QSpinBox()
        self.cooldown_spin.setRange(200, 30000)
        self.cooldown_spin.setSingleStep(200)
        self.cooldown_spin.setSuffix(' ms')
        self.cooldown_spin.setValue(2000)
        self.cooldown_spin.valueChanged.connect(
            lambda v: self._set('cooldown_ms', v))
        iv_row.addWidget(self.cooldown_spin)
        iv_row.addStretch()
        root.addLayout(iv_row)
        root.addStretch()

    # ──────────────────────────────────────────── Load data
    def load_trigger(self, trigger: TriggerConfig, project: MacroProject):
        self._building = True
        self.trigger = trigger
        self.project = project
        self.name_edit.setText(trigger.name)
        self.enabled_chk.setChecked(trigger.enabled)
        idx = self.type_combo.findData(trigger.type)
        self.type_combo.setCurrentIndex(max(0, idx))
        self._update_region_label(trigger.region)
        self.thr_slider.setValue(int(trigger.threshold * 100))
        self.txt_edit.setText(trigger.target_text)
        idx_m = self.match_combo.findData(trigger.match_mode)
        self.match_combo.setCurrentIndex(max(0, idx_m))
        # Template
        self._update_template_preview(trigger.template_path)
        # Macro combos
        self._refresh_macro_combo()
        idx_a = self.act_combo.findData(trigger.action_type)
        self.act_combo.setCurrentIndex(max(0, idx_a))
        self.act_key_edit.setText(trigger.action_params.get('key', ''))
        self.interval_spin.setValue(trigger.check_interval_ms)
        self.cooldown_spin.setValue(trigger.cooldown_ms)
        self._building = False
        self._on_type_changed()
        self._on_act_changed()

    def _refresh_macro_combo(self):
        self.macro_combo.clear()
        if self.project:
            for m in self.project.macros:
                self.macro_combo.addItem(m.name, m.id)
        if self.trigger:
            mid = self.trigger.action_params.get('macro_id', '')
            idx = self.macro_combo.findData(mid)
            self.macro_combo.setCurrentIndex(max(0, idx))

    # ──────────────────────────────────────────── Helpers
    def _set(self, attr: str, value):
        if self.trigger and not self._building:
            setattr(self.trigger, attr, value)
            self.changed.emit()

    def _update_region_label(self, region):
        x, y, w, h = region
        self.region_lbl.setText(f'({x}, {y})  {w} × {h} px')
        self.region_lbl.setStyleSheet('color:#7070ff;')

    def _update_template_preview(self, path: str):
        if path and os.path.exists(path):
            self.tmpl_lbl.setText(os.path.basename(path))
            pix = QPixmap(path).scaled(
                78, 48, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.tmpl_preview.setPixmap(pix)
        else:
            self.tmpl_lbl.setText('无模板')

    def _on_type_changed(self):
        t = self.type_combo.currentData()
        self.img_grp.setVisible(t == 'image')
        self.txt_grp.setVisible(t == 'text')
        if not self._building:
            self._set('type', t)

    def _on_threshold_changed(self, v: int):
        val = v / 100.0
        self.thr_val_lbl.setText(f'{val:.2f}')
        if not self._building:
            self._set('threshold', val)

    def _on_act_changed(self):
        t = self.act_combo.currentData()
        self.macro_combo.setVisible(t == 'run_macro')
        self.act_key_edit.setVisible(t == 'key')
        if not self._building and self.trigger:
            self.trigger.action_type = t
            if t == 'run_macro':
                self.trigger.action_params = {
                    'macro_id': self.macro_combo.currentData() or ''}
            elif t == 'key':
                self.trigger.action_params = {'key': self.act_key_edit.text()}
            self.changed.emit()

    # ──────────────────────────────────────────── Region / Template
    def _select_region(self):
        self._sel = RegionSelector()
        self._sel.region_selected.connect(self._on_region_selected)

    def _on_region_selected(self, x, y, w, h):
        if self.trigger:
            self.trigger.region = (x, y, w, h)
            self._update_region_label((x, y, w, h))
            self.changed.emit()

    def _capture_template(self):
        if not self.trigger:
            return
        path = self._make_template_path()
        self._sel = RegionSelector(capture_template=True, template_path=path)
        self._sel.region_selected.connect(
            lambda x, y, w, h: self._on_template_captured(path, x, y, w, h))

    def _on_template_captured(self, path, x, y, w, h):
        if self.trigger:
            self.trigger.template_path = path
            self.trigger.region = (x, y, w, h)
            self._update_region_label((x, y, w, h))
            self._update_template_preview(path)
            self.changed.emit()

    def _load_template_file(self):
        if not self.trigger:
            return
        fname, _ = QFileDialog.getOpenFileName(
            self, '选择模板图像', '',
            'Images (*.png *.jpg *.bmp *.webp);;All Files (*)')
        if fname:
            self.trigger.template_path = fname
            self._update_template_preview(fname)
            self.changed.emit()

    def _make_template_path(self) -> str:
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tmpl_dir = os.path.join(here, 'assets', 'templates')
        os.makedirs(tmpl_dir, exist_ok=True)
        tid = self.trigger.id if self.trigger else 'tmp'
        return os.path.join(tmpl_dir, f'trigger_{tid}.png')
