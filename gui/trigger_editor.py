"""Trigger configuration editor — image trigger and text trigger setup."""
import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QCheckBox, QComboBox, QSlider, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QFileDialog, QGroupBox, QMessageBox
)
import re
from core.macro import TriggerConfig, MacroProject
from .region_selector import RegionSelector
from core import screen as scr, image_match, ocr as _ocr


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
        root.setSpacing(12)

        # ── Header card: name + enabled + type ──
        hdr_card = QFrame()
        hdr_card.setObjectName('panel_card')
        hc_lay = QVBoxLayout(hdr_card)
        hc_lay.setContentsMargins(16, 14, 16, 14)
        hc_lay.setSpacing(10)

        # Row 1: name + enabled
        name_row = QHBoxLayout()
        name_lbl = QLabel('触发器名称')
        name_lbl.setObjectName('lbl_section')
        name_lbl.setFixedWidth(86)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('输入触发器名称…')
        self.name_edit.textEdited.connect(lambda v: self._set('name', v))
        self.enabled_chk = QCheckBox('启用')
        self.enabled_chk.stateChanged.connect(
            lambda: self._set('enabled', self.enabled_chk.isChecked()))
        name_row.addWidget(name_lbl)
        name_row.addWidget(self.name_edit, 1)
        name_row.addWidget(self.enabled_chk)
        hc_lay.addLayout(name_row)

        # Row 2: type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel('触发类型:'))
        self.type_combo = QComboBox()
        self.type_combo.addItem('⛶  图像识别', 'image')
        self.type_combo.addItem('≡  文字识别  (OCR)', 'text')
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_combo, 1)
        hc_lay.addLayout(type_row)

        root.addWidget(hdr_card)

        # ── Detection region ──
        reg_grp = QGroupBox('检测区域')
        reg_layout = QHBoxLayout(reg_grp)
        reg_layout.setContentsMargins(16, 20, 16, 14)

        # Region info column
        reg_info = QVBoxLayout()
        self.region_lbl = QLabel('未设置')
        self.region_lbl.setStyleSheet('color:rgba(180,185,220,0.4); font-size:13px;')
        reg_hint = QLabel('框选屏幕区域用于检测触发条件')
        reg_hint.setStyleSheet('color:rgba(180,185,220,0.25); font-size:11px;')
        reg_info.addWidget(self.region_lbl)
        reg_info.addWidget(reg_hint)
        reg_layout.addLayout(reg_info, 1)

        btn_sel = QPushButton('⛶  框选区域')
        btn_sel.setObjectName('btn_accent')
        btn_sel.clicked.connect(self._select_region)
        reg_layout.addWidget(btn_sel)
        root.addWidget(reg_grp)

        # ── Image trigger group ──
        self.img_grp = QGroupBox('图像识别设置')
        img_layout = QVBoxLayout(self.img_grp)
        img_layout.setContentsMargins(16, 20, 16, 14)
        img_layout.setSpacing(12)

        # Template row
        tmpl_row = QHBoxLayout()
        tmpl_row.setSpacing(12)

        # Preview (larger)
        self.tmpl_preview = QLabel()
        self.tmpl_preview.setFixedSize(120, 75)
        self.tmpl_preview.setObjectName('tmpl_empty')
        self.tmpl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tmpl_preview.setText('⌖ 截取模板')
        tmpl_row.addWidget(self.tmpl_preview)

        # Template info + buttons
        tmpl_info = QVBoxLayout()
        tmpl_info.setSpacing(6)
        self.tmpl_lbl = QLabel('无模板')
        self.tmpl_lbl.setStyleSheet('color:rgba(180,185,220,0.4); font-size:12px;')
        tmpl_info.addWidget(self.tmpl_lbl)

        tmpl_btns = QHBoxLayout()
        tmpl_btns.setSpacing(6)
        btn_capture = QPushButton('⌖  截取模板')
        btn_capture.setObjectName('btn_accent')
        btn_capture.clicked.connect(self._capture_template)
        btn_load = QPushButton('▤  选择文件')
        btn_load.clicked.connect(self._load_template_file)
        tmpl_btns.addWidget(btn_capture)
        tmpl_btns.addWidget(btn_load)
        tmpl_info.addLayout(tmpl_btns)
        tmpl_row.addLayout(tmpl_info, 1)

        img_layout.addLayout(tmpl_row)

        # Threshold row with color indicator
        thr_row = QHBoxLayout()
        thr_row.setSpacing(8)
        thr_row.addWidget(QLabel('相似度阈值:'))
        self.thr_slider = QSlider(Qt.Orientation.Horizontal)
        self.thr_slider.setRange(50, 100)
        self.thr_slider.setValue(80)
        self.thr_slider.valueChanged.connect(self._on_threshold_changed)
        self.thr_val_lbl = QLabel('0.80')
        self.thr_val_lbl.setFixedWidth(42)
        self.thr_val_lbl.setObjectName('thr_mid')
        thr_row.addWidget(self.thr_slider, 1)
        thr_row.addWidget(self.thr_val_lbl)
        img_layout.addLayout(thr_row)
        root.addWidget(self.img_grp)

        # ── Text trigger group ──
        self.txt_grp = QGroupBox('文字识别设置  (OCR)')
        txt_layout = QFormLayout(self.txt_grp)
        txt_layout.setContentsMargins(16, 20, 16, 14)
        txt_layout.setSpacing(10)

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
        self.num_cmp_card = QFrame()
        self.num_cmp_card.setObjectName('panel_card')
        ncl = QHBoxLayout(self.num_cmp_card)
        ncl.setContentsMargins(12, 10, 12, 10)
        ncl.setSpacing(8)

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
            
        ncl.addWidget(QLabel('比较:'))
        ncl.addWidget(self.num_cmp_combo, 1)
        ncl.addWidget(QLabel('值:'))
        ncl.addWidget(self.num_val_spin, 1)
        
        txt_layout.addRow('目标文字:', self.txt_edit)
        txt_layout.addRow('匹配方式:', self.match_combo)
        self.txt_layout_label_target = txt_layout.labelForField(self.txt_edit)
        txt_layout.addRow('数值条件:', self.num_cmp_card)
        self.txt_layout_label_num = txt_layout.labelForField(self.num_cmp_card)
        
        self.match_combo.currentIndexChanged.connect(self._on_match_mode_changed)
        
        root.addWidget(self.txt_grp)

        # ── Bottom Test Button ──
        test_card = QFrame()
        test_card.setObjectName('panel_card')
        tc_lay = QVBoxLayout(test_card)
        tc_lay.setContentsMargins(14, 10, 14, 10)
        
        self.btn_test = QPushButton('▶  测试当前触发条件')
        self.btn_test.setObjectName('btn_run')
        self.btn_test.clicked.connect(self._test_trigger)
        tc_lay.addWidget(self.btn_test)
        
        hint_lbl = QLabel('仅运行一次检测，验证识别范围、阈值或文字内容是否设置正确')
        hint_lbl.setStyleSheet('color: rgba(180,185,220,0.3); font-size: 11px;')
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tc_lay.addWidget(hint_lbl)
        
        root.addWidget(test_card)
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
        
        self._on_type_changed()
        self._building = False

    # ──────────────────────────────────────────── Helpers
    def _set(self, attr: str, value):
        if self.trigger and not self._building:
            setattr(self.trigger, attr, value)
            self.changed.emit()

    def _update_region_label(self, region):
        x, y, w, h = region
        self.region_lbl.setText(f'⌖ ({x}, {y})  →  {w} × {h} px')
        self.region_lbl.setStyleSheet('color:#a5b4fc; font-weight:bold; font-size:13px;')

    def _update_template_preview(self, path: str):
        if path and os.path.exists(path):
            self.tmpl_lbl.setText(os.path.basename(path))
            self.tmpl_lbl.setStyleSheet('color:#a5b4fc; font-weight:bold; font-size:12px;')
            pix = QPixmap(path).scaled(
                116, 71, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.tmpl_preview.setPixmap(pix)
            self.tmpl_preview.setObjectName('')  # clear empty state style
            self.tmpl_preview.setStyleSheet(
                'border:1px solid rgba(255,255,255,0.08);border-radius:8px;'
                'background:rgba(255,255,255,0.02);')
        else:
            self.tmpl_lbl.setText('无模板')
            self.tmpl_lbl.setStyleSheet('color:rgba(180,185,220,0.4); font-size:12px;')
            self.tmpl_preview.clear()
            self.tmpl_preview.setText('⌖ 截取模板')
            self.tmpl_preview.setObjectName('tmpl_empty')
            self.tmpl_preview.setStyleSheet('')  # let QSS handle it

    def _on_type_changed(self):
        t = self.type_combo.currentData()
        self.img_grp.setVisible(t == 'image')
        self.txt_grp.setVisible(t == 'text')
        if not self._building:
            self._set('type', t)
            
    def _on_match_mode_changed(self):
        """匹配模式改变时的处理函数。"""
        m = self.match_combo.currentData()
        is_num = (m == 'number')

        # Toggle text input visibility
        self.txt_edit.setVisible(not is_num)
        if self.txt_layout_label_target is not None:
            self.txt_layout_label_target.setVisible(not is_num)
        
        # Toggle number comparison card visibility
        self.num_cmp_card.setVisible(is_num)
        if self.txt_layout_label_num is not None:
            self.txt_layout_label_num.setVisible(is_num)

    def _on_threshold_changed(self, v: int):
        val = v / 100.0
        self.thr_val_lbl.setText(f'{val:.2f}')
        # Color indicator based on threshold level
        if val < 0.70:
            self.thr_val_lbl.setObjectName('thr_low')
        elif val <= 0.85:
            self.thr_val_lbl.setObjectName('thr_mid')
        else:
            self.thr_val_lbl.setObjectName('thr_high')
        # Force style refresh
        self.thr_val_lbl.style().unpolish(self.thr_val_lbl)
        self.thr_val_lbl.style().polish(self.thr_val_lbl)
        if not self._building:
            self._set('threshold', val)

    # ──────────────────────────────────────────── Region / Template
    def _select_region(self):
        self.window().setWindowOpacity(0.5)
        self._sel = RegionSelector()
        self._sel.region_selected.connect(self._on_region_selected)

    def _on_region_selected(self, x, y, w, h):
        self.window().setWindowOpacity(1.0)
        if self.trigger:
            self.trigger.region = (x, y, w, h)
            self._update_region_label((x, y, w, h))
            self.changed.emit()

    def _capture_template(self):
        if not self.trigger:
            return
        self.window().setWindowOpacity(0.5)
        path = self._make_template_path()
        self._sel = RegionSelector(capture_template=True, template_path=path)
        self._sel.region_selected.connect(
            lambda x, y, w, h: self._on_template_captured(path, x, y, w, h))

    def _on_template_captured(self, path, x, y, w, h):
        self.window().setWindowOpacity(1.0)
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

    # ──────────────────────────────────────────── Trigger Testing
    def _test_trigger(self):
        if not self.trigger:
            return

        x, y, w, h = self.trigger.region
        if w <= 0 or h <= 0:
            QMessageBox.warning(self, "区域无效", "请先框选一个有效的检测区域。")
            return

        try:
            img = scr.capture_region(x, y, w, h)
        except Exception as e:
            QMessageBox.critical(self, "截图失败", f"无法截取屏幕区域:\n{e}")
            return

        if self.trigger.type == 'image':
            if not self.trigger.template_path or not os.path.exists(self.trigger.template_path):
                QMessageBox.warning(self, "模板无效", "请先截取或选择一个有效的模板图像。")
                return
            
            try:
                tmpl = image_match.load_template(self.trigger.template_path)
                result = image_match.find_template(img, tmpl, self.trigger.threshold)
                
                if result is not None:
                    score = result[2]
                    QMessageBox.information(
                        self, 
                        "识别成功", 
                        f"在屏幕区域中成功匹配到了模板！\n\n置信度 (Score): {score:.4f}  (设定阈值: {self.trigger.threshold:.2f})"
                    )
                else:
                    QMessageBox.warning(
                        self, 
                        "识别失败", 
                        f"在屏幕区域中未找到满足阈值 ({self.trigger.threshold:.2f}) 的图像。"
                    )
            except Exception as e:
                QMessageBox.critical(self, "图像匹配出错", f"执行图像匹配时发生错误:\n{e}")

        elif self.trigger.type == 'text':
            if self.trigger.match_mode != 'number' and not str(self.trigger.target_text).strip():
                QMessageBox.warning(self, "目标无效", "请填写需要识别的文字内容，否则无法进行匹配。")
                return
            try:
                allowlist = '0123456789.-%:/ ' if self.trigger.match_mode == 'number' else None
                text = _ocr.recognize_text_only(img, allowlist=allowlist)
            except Exception as e:
                QMessageBox.critical(self, "OCR 错误", f"执行 OCR 识别时发生错误:\n{e}")
                return

            tgt = str(self.trigger.target_text)
            mode = self.trigger.match_mode
            
            is_match = False
            match_detail = ""
            
            if mode == 'exact':
                is_match = (text.strip() == tgt.strip())
                match_detail = f"精准匹配目标: '{tgt}'"
            elif mode == 'contains':
                is_match = (tgt in text)
                match_detail = f"包含目标文本: '{tgt}'"
            elif mode == 'regex':
                try:
                    is_match = bool(re.search(tgt, text))
                    match_detail = f"正则表达式: '{tgt}'"
                except re.error as e:
                    QMessageBox.warning(self, "正则错误", f"正则表达式无效: {e}")
                    return
            elif mode == 'number':
                nums = re.findall(r'-?\d+\.?\d*', text)
                if not nums:
                    QMessageBox.warning(self, "未找到数字", f"识别到的文本中不包含有效数字。\n\n【实际识别内容】:\n{text}")
                    return
                try:
                    val = float(nums[0])
                    cmp_op = getattr(self.trigger, 'number_cmp', 'lte')
                    ref_val = float(getattr(self.trigger, 'number_val', 0.0))
                    
                    cmp_ops = {
                        'lt': lambda v, r: v < r, 'lte': lambda v, r: v <= r,
                        'eq': lambda v, r: abs(v - r) < 1e-6,
                        'gte': lambda v, r: v >= r, 'gt': lambda v, r: v > r,
                    }
                    cmp_symbols = {'lt': '<', 'lte': '≤', 'eq': '=', 'gte': '≥', 'gt': '>'}
                    sym = cmp_symbols.get(cmp_op, cmp_op)
                    
                    if cmp_op in cmp_ops:
                        is_match = cmp_ops[cmp_op](val, ref_val)
                    match_detail = f"数值比较: 取出数值 {val}  {sym}  参考值 {ref_val}"
                except ValueError:
                    QMessageBox.warning(self, "数字解析错误", f"无法将识别出的部分解析为数字: {nums[0]}")
                    return

            icon = QMessageBox.Icon.Information if is_match else QMessageBox.Icon.Warning
            title = "匹配成功" if is_match else "匹配失败"
            msg = QMessageBox(self)
            msg.setIcon(icon)
            msg.setWindowTitle(title)
            msg.setText(f"【OCR 实际识别文本】:\n\n{text if text.strip() else '(未识别到任何带意义的文字)'}\n\n---\n判断条件: {match_detail}\n判定结果: {'✅ 满足条件 (True)' if is_match else '❌ 不满足 (False)'}")
            msg.exec()
