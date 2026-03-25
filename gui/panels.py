"""Independent UI panels for ClaudyKey to componentize MainWindow."""
import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QTextEdit, QInputDialog, QFileDialog,
    QGraphicsDropShadowEffect
)

from gui.controller import AppController, AppState
from gui.backend_settings_dialog import BackendSettingsDialog
from gui.hotkey_dialog import HotkeySetDialog
from gui.theme import STYLE_HINT_LBL, STYLE_STATE_IDLE, STYLE_STATE_RUNNING, STYLE_STATE_ERROR
from core import input_backend as _ib


class SidebarPanel(QFrame):
    """The left-side navigation, settings, and run controls."""
    nav_changed = pyqtSignal(int)
    
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        self.setObjectName('sidebar')
        self.setFixedWidth(300)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(60, 50, 120, 100))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)
        
        self._build_ui()
        self._bind_controller()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 20, 16, 20)
        lay.setSpacing(16)

        logo = QLabel('✦  ClaudyKey')
        logo.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        logo.setObjectName('lbl_logo')
        lay.addWidget(logo)
        lay.addSpacing(16)

        # Settings Group
        frm_set = QFrame()
        frm_set.setObjectName('sidebar_group')
        sl = QVBoxLayout(frm_set)
        sl.setContentsMargins(0, 0, 0, 0)
        
        sl.addWidget(QLabel('全局热键', objectName='lbl_sidebar_hdr'))
        self._hotkey_btn = QPushButton('设置: 取消')
        self._hotkey_btn.clicked.connect(self._on_hotkey_setup)
        sl.addWidget(self._hotkey_btn)
        sl.addSpacing(8)

        # Input driver
        bd_row = QHBoxLayout()
        bd_row.setContentsMargins(0, 0, 0, 0)
        sl.addWidget(QLabel('输入驱动', objectName='lbl_sidebar_hdr'))
        self._backend_combo = QComboBox()
        self._populate_backend_combo()
        self._backend_combo.currentIndexChanged.connect(self._on_backend_changed)
        
        bd_cfg_btn = QPushButton('⛭')
        bd_cfg_btn.setObjectName('btn_icon')
        bd_cfg_btn.setFixedWidth(30)
        bd_cfg_btn.clicked.connect(self._on_backend_settings)
        bd_row.addWidget(self._backend_combo, 1)
        bd_row.addWidget(bd_cfg_btn)
        sl.addLayout(bd_row)
        lay.addWidget(frm_set)
        
        lay.addSpacing(16)

        # Navigation
        nav_lbl = QLabel('工作区')
        nav_lbl.setObjectName('lbl_sidebar_hdr')
        lay.addWidget(nav_lbl)
        
        self._btn_nav_macro = QPushButton('⊞  宏管理')
        self._btn_nav_macro.setObjectName('btn_nav')
        self._btn_nav_macro.setCheckable(True)
        self._btn_nav_macro.setChecked(True)
        self._btn_nav_macro.clicked.connect(lambda: self._switch_nav(0))
        
        self._btn_nav_trig = QPushButton('⭃  条件触发器')
        self._btn_nav_trig.setObjectName('btn_nav')
        self._btn_nav_trig.setCheckable(True)
        self._btn_nav_trig.clicked.connect(lambda: self._switch_nav(1))
        
        lay.addWidget(self._btn_nav_macro)
        lay.addWidget(self._btn_nav_trig)
        lay.addStretch()

        # File Config
        file_lay = QHBoxLayout()
        file_lay.setContentsMargins(0, 0, 0, 0)
        file_lay.setSpacing(4)
        
        self._proj_combo = QComboBox()
        self._proj_combo.setToolTip("选择配置文件")
        self._proj_combo.currentIndexChanged.connect(self._on_proj_combo_changed)
        file_lay.addWidget(self._proj_combo, 1)

        b_save = QPushButton('⤓')
        b_save.setToolTip('保存配置')
        b_save.setObjectName('btn_icon')
        b_save.setFixedWidth(28)
        b_save.clicked.connect(self.controller.save_project)
        file_lay.addWidget(b_save)

        b_new = QPushButton('＋')
        b_new.setToolTip('新建配置')
        b_new.setObjectName('btn_icon')
        b_new.setFixedWidth(28)
        b_new.clicked.connect(self._new_project_prompt)
        file_lay.addWidget(b_new)

        b_open = QPushButton('◿')
        b_open.setToolTip('浏览本地')
        b_open.setObjectName('btn_icon')
        b_open.setFixedWidth(28)
        b_open.clicked.connect(self._open_project)
        file_lay.addWidget(b_open)

        lay.addLayout(file_lay)
        lay.addSpacing(12)

        # Controls
        self._btn_run = QPushButton('▶ 启动')
        self._btn_run.setObjectName('btn_run')
        self._btn_run.clicked.connect(lambda: self.controller.run_macro(None))

        self._btn_stop = QPushButton('■ 停止')
        self._btn_stop.setObjectName('btn_stop')
        self._btn_stop.clicked.connect(self.controller.stop_execution)
        self._btn_stop.setEnabled(False)

        lay.addWidget(self._btn_run)
        lay.addWidget(self._btn_stop)

    def _bind_controller(self):
        self.controller.state_changed.connect(self._on_state_changed)
        self.controller.project_loaded.connect(self._on_project_loaded)
        self.controller.hotkey_registered.connect(self._on_hotkey_registered)

    def _on_state_changed(self, state: str):
        if state == AppState.IDLE:
            self._btn_run.setEnabled(True)
            self._btn_stop.setEnabled(False)
        elif state == AppState.RUNNING:
            self._btn_run.setEnabled(False)
            self._btn_stop.setEnabled(True)
        elif state == AppState.ERROR:
            self._btn_run.setEnabled(True)
            self._btn_stop.setEnabled(False)

    def _on_project_loaded(self, project, path: str):
        self._refresh_proj_combo()
        self._populate_backend_combo()

    def _on_hotkey_registered(self, display: str):
        self._btn_run.setText(f'▶  运行  ({display})')
        self._btn_stop.setText(f'■  停止  ({display})')
        self._hotkey_btn.setText(f'设置: {display}')

    def _switch_nav(self, idx: int):
        self._btn_nav_macro.setChecked(idx == 0)
        self._btn_nav_trig.setChecked(idx == 1)
        self.nav_changed.emit(idx)

    # Project List Combo
    def _refresh_proj_combo(self):
        self._proj_combo_updating = True
        self._proj_combo.clear()
        
        folder = os.path.dirname(self.controller.DEFAULT_PROJ)
        os.makedirs(folder, exist_ok=True)
        
        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        files.sort()
        if not files:
            files = ['default.json']
            
        for f in files:
            self._proj_combo.addItem(f, os.path.join(folder, f))
            
        idx = self._proj_combo.findData(self.controller.current_proj_path)
        if idx >= 0:
            self._proj_combo.setCurrentIndex(idx)
        self._proj_combo_updating = False

    def _on_proj_combo_changed(self, idx: int):
        if getattr(self, '_proj_combo_updating', False) or idx < 0:
            return
        path = self._proj_combo.itemData(idx)
        if path and path != self.controller.current_proj_path:
            self.controller.save_project()
            self.controller.load_project(path)

    def _new_project_prompt(self):
        name, ok = QInputDialog.getText(self, '新建配置', '输入新配置名称:', text='config')
        if ok and name:
            self.controller.new_project(name)

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '打开项目', os.path.dirname(self.controller.DEFAULT_PROJ),
            'ClaudyKey 项目 (*.json);;All Files (*)')
        if path:
            self.controller.save_project()
            self.controller.load_project(path)

    def _on_hotkey_setup(self):
        dlg = HotkeySetDialog(self)
        if dlg.exec() and dlg.result_key:
            self.controller.set_hotkey(dlg.result_key)

    # Input backend
    def _populate_backend_combo(self):
        _ib._ensure_defaults_registered()
        self._backend_combo.blockSignals(True)
        self._backend_combo.clear()
        
        for cls in _ib.get_available_backends():
            label = cls.display_name()
            if not cls.is_available():
                label += ' ⚠'
            self._backend_combo.addItem(label, userData=cls.name())
            
        current = getattr(self.controller.project, 'input_backend', 'dd')
        for i in range(self._backend_combo.count()):
            if self._backend_combo.itemData(i) == current:
                self._backend_combo.setCurrentIndex(i)
                break
        self._backend_combo.blockSignals(False)

    def _on_backend_changed(self, _idx: int):
        backend_name = self._backend_combo.currentData()
        if backend_name:
            self.controller.switch_input_backend(backend_name)

    def _on_backend_settings(self):
        dlg = BackendSettingsDialog(self)
        dlg.exec()
        self._populate_backend_combo()


class LogPanel(QFrame):
    """Bottom log console and status bar interface."""
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        self.setObjectName('glass_card')
        self.setFixedHeight(140)
        
        self._build_ui()
        self._bind_controller()

    def _build_ui(self):
        log_lay = QVBoxLayout(self)
        log_lay.setContentsMargins(10, 6, 10, 10)
        
        log_hdr = QHBoxLayout()
        log_lbl = QLabel('≡ 运行日志', objectName='lbl_section')
        self._btn_clear_log = QPushButton('清空', objectName='btn_icon')
        self._btn_clear_log.setFixedWidth(48)
        self._btn_clear_log.clicked.connect(lambda: self._log_view.clear())
        log_hdr.addWidget(log_lbl, 1)
        log_hdr.addWidget(self._btn_clear_log)
        log_lay.addLayout(log_hdr)

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setObjectName('log_view')
        log_lay.addWidget(self._log_view)

        # Status Bar integration into Log Panel
        stat_lay = QHBoxLayout()
        self._status_lbl = QLabel('就绪', objectName='lbl_status_ok')
        self._hotkey_lbl = QLabel('全局热键: 未知')
        self._hotkey_lbl.setStyleSheet(STYLE_HINT_LBL)
        self._file_lbl = QLabel('')
        self._file_lbl.setStyleSheet(STYLE_HINT_LBL)
        
        stat_lay.addWidget(self._status_lbl)
        stat_lay.addStretch()
        stat_lay.addWidget(self._file_lbl)
        stat_lay.addSpacing(12)
        stat_lay.addWidget(self._hotkey_lbl)
        log_lay.addLayout(stat_lay)

    def _bind_controller(self):
        self.controller.state_changed.connect(self._on_state_changed)
        self.controller.log_message.connect(self._append_log_with_kind)
        self.controller.project_loaded.connect(self._on_project_loaded)
        self.controller.project_saved.connect(self._on_project_saved)
        self.controller.hotkey_registered.connect(self._on_hotkey_registered)

    def _on_state_changed(self, state: str):
        styles = {
            AppState.IDLE: ('就绪', STYLE_STATE_IDLE),
            AppState.RUNNING: ('运行中…', STYLE_STATE_RUNNING),
            AppState.ERROR: ('发生错误', STYLE_STATE_ERROR),
        }
        text, style = styles.get(state, ('就绪', 'color:#1fa357;'))
        self._status_lbl.setText(text)
        self._status_lbl.setStyleSheet(style)

    def _append_log_with_kind(self, msg: str, kind: str):
        import datetime
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        color = {
            'err': '#ef4444',
            'ok': '#2dd4bf',
            'run': '#fbbf24',
            'info': '#94a3b8'
        }.get(kind, '#94a3b8')
        
        self._log_view.append(
            f'<span style="color:rgba(255,255,255,0.3)">[{ts}]</span> '
            f'<span style="color:{color}">{msg}</span>')
        sb = self._log_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_project_loaded(self, project, path: str):
        self._file_lbl.setText(os.path.basename(path))

    def _on_project_saved(self, path: str):
        self._file_lbl.setText(os.path.basename(path))

    def _on_hotkey_registered(self, display: str):
        self._hotkey_lbl.setText(f'全局热键: {display} 开始 / 停止')
