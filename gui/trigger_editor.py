"""Trigger configuration editor — image trigger and text trigger setup."""
import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QCheckBox, QComboBox, QSlider, QSpinBox, QDoubleSpinBox,
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
        self.region_lbl.setStyleSheet('color:rgba(140,110,125,0.6);')
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
        self.tmpl_lbl.setStyleSheet('color:rgba(140,110,125,0.6);')
        btn_capture = QPushButton('📷  截取模板')
        btn_capture.setObjectName('btn_accent')
        btn_capture.clicked.connect(self._capture_template)
        btn_load = QPushButton('📁  选择文件')
        btn_load.clicked.connect(self._load_template_file)
        self.tmpl_preview = QLabel()
        self.tmpl_preview.setFixedSize(80, 50)
        self.tmpl_preview.setStyleSheet(
            'border:1px solid #f2c2d6;border-radius:4px;background:rgba(255, 255, 255, 0.7);')
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
        self.match_combo.addItem('数值比较', 'number')
        self.match_combo.currentIndexChanged.connect(
            lambda: self._set('match_mode', self.match_combo.currentData()))
        
        # ── Number Comparison Config ──
        self.num_cmp_row = QHBoxLayout()
        self.num_cmp_combo = QComboBox()
        self.num_cmp_combo.addItem('< 小于', 'lt')
        self.num_cmp_combo.addItem('≤ 小于等于', 'lte')
        self.num_cmp_combo.addItem('= 等于', 'eq')
        self.num_cmp_combo.addItem('≥ 大于等于', 'gte')
        self.num_cmp_combo.addItem('> 大于', 'gt')
        self.num_cmp_combo.currentIndexChanged.connect(
            lambda: self._set('number_cmp', self.num_cmp_combo.currentData()))
        
        self.num_val_spin = QDoubleSpinBox()
        self.num_val_spin.setRange(-99999999.0, 99999999.0)
        self.num_val_spin.setDecimals(2)
        self.num_val_spin.valueChanged.connect(
            lambda v: self._set('number_val', v))
            
        self.num_cmp_row.addWidget(self.num_cmp_combo)
        self.num_cmp_row.addWidget(self.num_val_spin)
        
        txt_layout.addRow('目标文字:', self.txt_edit)
        txt_layout.addRow('匹配方式:', self.match_combo)
        self.txt_layout_label_target = txt_layout.labelForField(self.txt_edit)
        txt_layout.addRow('数值条件:', self.num_cmp_row)
        self.txt_layout_label_num = txt_layout.labelForField(self.num_cmp_row)
        
        self.match_combo.currentIndexChanged.connect(self._on_match_mode_changed)
        
        root.addWidget(self.txt_grp)

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
        
        idx_c = self.num_cmp_combo.findData(getattr(trigger, 'number_cmp', 'lte'))
        self.num_cmp_combo.setCurrentIndex(max(0, idx_c))
        self.num_val_spin.setValue(getattr(trigger, 'number_val', 0.0))
        
        # Template
        self._update_template_preview(trigger.template_path)
        
        self._building = False
        self._on_type_changed()

    # ──────────────────────────────────────────── Helpers
    def _set(self, attr: str, value):
        if self.trigger and not self._building:
            setattr(self.trigger, attr, value)
            self.changed.emit()

    def _update_region_label(self, region):
        x, y, w, h = region
        self.region_lbl.setText(f'({x}, {y})  {w} × {h} px')
        self.region_lbl.setStyleSheet('color:#c94080;font-weight:bold;')

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
            
    def _on_match_mode_changed(self):
        m = self.match_combo.currentData()
        is_num = (m == 'number')
        self.txt_edit.setVisible(not is_num)
        if hasattr(self, 'txt_layout_label_target') and self.txt_layout_label_target:
            self.txt_layout_label_target.setVisible(not is_num)
            
        for i in range(self.num_cmp_row.count()):
            w = self.num_cmp_row.itemAt(i).widget()
            if w: w.setVisible(is_num)
        if hasattr(self, 'txt_layout_label_num') and self.txt_layout_label_num:
            self.txt_layout_label_num.setVisible(is_num)

    def _on_threshold_changed(self, v: int):
        val = v / 100.0
        self.thr_val_lbl.setText(f'{val:.2f}')
        if not self._building:
            self._set('threshold', val)

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
