"""Main application window for ClaudyKey."""
import os
import uuid
import threading

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QFrame,
    QStackedWidget, QFileDialog, QMessageBox, QSizePolicy,
    QInputDialog, QComboBox, QDialog, QTextEdit,
)
from pynput import keyboard as pynput_kb
from pynput import mouse as pynput_mouse

class HotkeySetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置启停快捷键')
        self.setFixedSize(300, 160)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        lay = QVBoxLayout(self)
        self.lbl = QLabel('正在监听...\n\n请按下任意键盘按键或\n除左键外的鼠标按键。')
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet('font-size: 14px; color: #d15c89; font-weight: bold;')
        lay.addWidget(self.lbl)
        
        self.result_key = None
        
        self.kb_listener = pynput_kb.Listener(on_press=self.on_key)
        self.mouse_listener = pynput_mouse.Listener(on_click=self.on_mouse)
        self.kb_listener.start()
        self.mouse_listener.start()

    def on_key(self, key):
        if self.result_key: return
        try:
            char = key.char
            if char:
                self.result_key = f"key:{char.lower()}"
            else:
                self.result_key = f"key:<{key.name}>"
        except AttributeError:
            self.result_key = f"key:<{key.name}>"
        self.accept_from_thread()

    def on_mouse(self, x, y, button, pressed):
        if not pressed or self.result_key: return
        if button == pynput_mouse.Button.left:
            return  # block left click
        self.result_key = f"mouse:{button.name}"
        self.accept_from_thread()

    def accept_from_thread(self):
        self.kb_listener.stop()
        self.mouse_listener.stop()
        QTimer.singleShot(0, self.accept)

    def closeEvent(self, event):
        self.kb_listener.stop()
        self.mouse_listener.stop()
        super().closeEvent(event)

from core.macro import MacroProject, MacroSequence, TriggerConfig
from core.executor import MacroExecutor
from core.trigger import TriggerEngine
from core import input_backend as _ib
from gui.macro_editor import MacroEditorPanel
from gui.trigger_editor import TriggerEditorPanel
from gui.backend_settings_dialog import BackendSettingsDialog
from gui.theme import THEME_QSS


# ── Signal bridge: relay background-thread events to GUI thread ──
class _Bridge(QObject):
    step_changed   = pyqtSignal(int)
    macro_done     = pyqtSignal()
    macro_error    = pyqtSignal(str)
    trigger_fired  = pyqtSignal(str)   # trigger id
    log            = pyqtSignal(str)   # timestamped log line


class MainWindow(QMainWindow):
    DEFAULT_PROJ = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config', 'macros', 'default.json')

    def __init__(self):
        super().__init__()
        self.setWindowTitle('ClaudyKey — AI 连点器')
        self.resize(1100, 720)
        self.setStyleSheet(THEME_QSS)

        self.project = MacroProject()
        self._executor: MacroExecutor | None = None
        self._trigger_engine: TriggerEngine | None = None
        self._bridge = _Bridge()
        self._current_proj_path: str = ''
        self._running = False
        self._listener_kb = None
        self._listener_mouse = None

        self._bridge.step_changed.connect(self._on_step)
        self._bridge.macro_done.connect(self._on_macro_done)
        self._bridge.macro_error.connect(self._on_macro_error)
        self._bridge.trigger_fired.connect(self._on_trigger_fired)
        self._bridge.log.connect(self._append_log)

        self._build_ui()
        self._register_hotkey()

        # Auto-load default project
        if os.path.exists(self.DEFAULT_PROJ):
            self._load_project(self.DEFAULT_PROJ)
        else:
            self._current_proj_path = self.DEFAULT_PROJ
            self._new_macro()
            
        self._refresh_proj_combo()

    # ══════════════════════════════════════════════════════════════
    #  UI construction
    # ══════════════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════════════
    #  UI construction
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_main_area(), 1)

    def _build_sidebar(self) -> QFrame:
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        side = QFrame()
        side.setObjectName('sidebar')
        side.setFixedWidth(240)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(230, 190, 210, 60))
        shadow.setOffset(0, 4)
        side.setGraphicsEffect(shadow)
        
        lay = QVBoxLayout(side)
        lay.setContentsMargins(16, 20, 16, 20)
        lay.setSpacing(16)

        # Logo
        logo = QLabel('⌨  ClaudyKey')
        logo.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        logo.setObjectName('lbl_logo')
        lay.addWidget(logo)
        lay.addSpacing(16)

        # (Mode selector removed as condition mode is merged)

        # Settings
        frm_set = QFrame()
        frm_set.setObjectName('sidebar_group')
        sl = QVBoxLayout(frm_set)
        sl.setContentsMargins(0,0,0,0)
        
        # Hotkey
        sl.addWidget(QLabel('全局热键', objectName='lbl_sidebar_hdr'))
        self._hotkey_btn = QPushButton('设置: F9')
        self._hotkey_btn.clicked.connect(self._on_hotkey_setup)
        sl.addWidget(self._hotkey_btn)
        sl.addSpacing(8)

        # Input driver
        bd_row = QHBoxLayout()
        bd_row.setContentsMargins(0,0,0,0)
        sl.addWidget(QLabel('输入驱动', objectName='lbl_sidebar_hdr'))
        self._backend_combo = QComboBox()
        self._populate_backend_combo()
        self._backend_combo.currentIndexChanged.connect(self._on_backend_changed)
        bd_cfg_btn = QPushButton('⚙')
        bd_cfg_btn.setObjectName('btn_icon')
        bd_cfg_btn.setFixedWidth(30)
        bd_cfg_btn.clicked.connect(self._on_backend_settings)
        bd_row.addWidget(self._backend_combo, 1)
        bd_row.addWidget(bd_cfg_btn)
        sl.addLayout(bd_row)
        lay.addWidget(frm_set)
        
        lay.addSpacing(16)

        # Navigation Menu
        nav_lbl = QLabel('工作区')
        nav_lbl.setObjectName('lbl_sidebar_hdr')
        lay.addWidget(nav_lbl)
        
        self._btn_nav_macro = QPushButton('📦  宏管理')
        self._btn_nav_macro.setObjectName('btn_nav')
        self._btn_nav_macro.setCheckable(True)
        self._btn_nav_macro.setChecked(True)
        self._btn_nav_macro.clicked.connect(lambda: self._switch_nav(0))
        
        self._btn_nav_trig = QPushButton('⚡  条件触发器')
        self._btn_nav_trig.setObjectName('btn_nav')
        self._btn_nav_trig.setCheckable(True)
        self._btn_nav_trig.clicked.connect(lambda: self._switch_nav(1))
        
        lay.addWidget(self._btn_nav_macro)
        lay.addWidget(self._btn_nav_trig)

        lay.addStretch()

        # File Config
        file_lay = QHBoxLayout()
        file_lay.setContentsMargins(0,0,0,0)
        file_lay.setSpacing(4)
        
        self._proj_combo = QComboBox()
        self._proj_combo.setToolTip("选择配置文件")
        self._proj_combo.currentIndexChanged.connect(self._on_proj_combo_changed)
        file_lay.addWidget(self._proj_combo, 1)

        b_save = QPushButton('💾')
        b_save.setToolTip('保存配置')
        b_save.setObjectName('btn_icon')
        b_save.setFixedWidth(28)
        b_save.clicked.connect(self._save_project)
        file_lay.addWidget(b_save)

        b_new = QPushButton('➕')
        b_new.setToolTip('新建配置')
        b_new.setObjectName('btn_icon')
        b_new.setFixedWidth(28)
        b_new.clicked.connect(self._new_project_prompt)
        file_lay.addWidget(b_new)

        b_open = QPushButton('📂')
        b_open.setToolTip('浏览本地')
        b_open.setObjectName('btn_icon')
        b_open.setFixedWidth(28)
        b_open.clicked.connect(self._open_project)
        file_lay.addWidget(b_open)

        lay.addLayout(file_lay)
        lay.addSpacing(12)

        # Control area
        self._btn_run = QPushButton('▶ 启动')
        self._btn_run.setObjectName('btn_run')
        self._btn_run.clicked.connect(self._start_all)

        self._btn_stop = QPushButton('■ 停止')
        self._btn_stop.setObjectName('btn_stop')
        self._btn_stop.clicked.connect(self._stop_all)
        self._btn_stop.setEnabled(False)

        lay.addWidget(self._btn_run)
        lay.addWidget(self._btn_stop)

        return side

    def _switch_nav(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self._btn_nav_macro.setChecked(idx == 0)
        self._btn_nav_trig.setChecked(idx == 1)

    def _build_main_area(self) -> QWidget:
        w = QFrame()
        w.setObjectName('main_area')
        
        outer = QVBoxLayout(w)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(12)

        self.stack = QStackedWidget()

        # Page 0: Macro Workspace
        macro_page = QWidget()
        m_lay = QHBoxLayout(macro_page)
        m_lay.setContentsMargins(0,0,0,0)
        
        m_list_cont = QFrame()
        m_list_cont.setObjectName('glass_card')
        m_list_cont.setFixedWidth(240)
        ml_lay = QVBoxLayout(m_list_cont)
        ml_lay.setContentsMargins(10, 10, 10, 10)
        
        m_hdr = QHBoxLayout()
        ml_lbl = QLabel('宏列表')
        ml_lbl.setObjectName('lbl_section')
        m_add = QPushButton('＋', objectName='btn_icon')
        m_add.setFixedSize(24, 24)
        m_add.clicked.connect(self._new_macro)
        m_del = QPushButton('－', objectName='btn_icon')
        m_del.setFixedSize(24, 24)
        m_del.clicked.connect(self._delete_macro)
        m_hdr.addWidget(ml_lbl, 1)
        m_hdr.addWidget(m_add)
        m_hdr.addWidget(m_del)
        ml_lay.addLayout(m_hdr)

        self.macro_list = QListWidget()
        self.macro_list.currentRowChanged.connect(self._on_macro_selected)
        ml_lay.addWidget(self.macro_list, 1)
        
        m_lay.addWidget(m_list_cont)
        
        self.macro_editor = MacroEditorPanel()
        self.macro_editor.changed.connect(self._on_project_changed)
        m_lay.addWidget(self.macro_editor, 1)

        # Page 1: Trigger Workspace
        trig_page = QWidget()
        t_lay = QHBoxLayout(trig_page)
        t_lay.setContentsMargins(0,0,0,0)

        t_list_cont = QFrame()
        t_list_cont.setObjectName('glass_card')
        t_list_cont.setFixedWidth(240)
        tl_lay = QVBoxLayout(t_list_cont)
        tl_lay.setContentsMargins(10, 10, 10, 10)

        t_hdr = QHBoxLayout()
        tl_lbl = QLabel('触发器列表')
        tl_lbl.setObjectName('lbl_section')
        t_add = QPushButton('＋', objectName='btn_icon')
        t_add.setFixedSize(24, 24)
        t_add.clicked.connect(self._new_trigger)
        t_del = QPushButton('－', objectName='btn_icon')
        t_del.setFixedSize(24, 24)
        t_del.clicked.connect(self._delete_trigger)
        t_hdr.addWidget(tl_lbl, 1)
        t_hdr.addWidget(t_add)
        t_hdr.addWidget(t_del)
        tl_lay.addLayout(t_hdr)

        self.trigger_list = QListWidget()
        self.trigger_list.currentRowChanged.connect(self._on_trigger_selected)
        tl_lay.addWidget(self.trigger_list, 1)

        t_lay.addWidget(t_list_cont)

        self.trigger_editor = TriggerEditorPanel()
        self.trigger_editor.changed.connect(self._on_project_changed)
        t_lay.addWidget(self.trigger_editor, 1)

        self.stack.addWidget(macro_page)
        self.stack.addWidget(trig_page)
        outer.addWidget(self.stack, 1)

        # Log Panel
        log_panel = QFrame()
        log_panel.setObjectName('glass_card')
        log_panel.setFixedHeight(140)
        log_lay = QVBoxLayout(log_panel)
        log_lay.setContentsMargins(10, 6, 10, 10)
        
        log_hdr = QHBoxLayout()
        log_lbl = QLabel('📜 运行日志', objectName='lbl_section')
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
        self._hotkey_lbl.setStyleSheet('color: rgba(60,40,50,0.7); font-size: 11px;')
        self._file_lbl = QLabel('')
        self._file_lbl.setStyleSheet('color: rgba(60,40,50,0.7); font-size: 11px;')
        stat_lay.addWidget(self._status_lbl)
        stat_lay.addStretch()
        stat_lay.addWidget(self._file_lbl)
        stat_lay.addSpacing(12)
        stat_lay.addWidget(self._hotkey_lbl)
        log_lay.addLayout(stat_lay)
        
        outer.addWidget(log_panel)
        return w

    #  Sidebar list management
    # ══════════════════════════════════════════════════════════════
    def _refresh_macro_list(self):
        old_row = self.macro_list.currentRow()
        self.macro_list.blockSignals(True)
        self.macro_list.clear()
        for m in self.project.macros:
            item = QListWidgetItem(f'⚡ {m.name}')
            item.setData(Qt.ItemDataRole.UserRole, m.id)
            self.macro_list.addItem(item)
        if 0 <= old_row < self.macro_list.count():
            self.macro_list.setCurrentRow(old_row)
        elif self.macro_list.count() > 0:
            self.macro_list.setCurrentRow(0)
        self.macro_list.blockSignals(False)

    def _refresh_trigger_list(self):
        old_row = self.trigger_list.currentRow()
        self.trigger_list.blockSignals(True)
        self.trigger_list.clear()
        for t in self.project.triggers:
            icon = '🖼' if t.type == 'image' else '📝'
            prefix = '' if t.enabled else '○ '
            item = QListWidgetItem(f'{prefix}{icon} {t.name}')
            item.setData(Qt.ItemDataRole.UserRole, t.id)
            self.trigger_list.addItem(item)
        if 0 <= old_row < self.trigger_list.count():
            self.trigger_list.setCurrentRow(old_row)
        self.trigger_list.blockSignals(False)

    def _on_macro_selected(self, row: int):
        if row < 0 or row >= len(self.project.macros):
            return
        self.trigger_list.clearSelection()
        seq = self.project.macros[row]
        self.macro_editor.project = self.project
        self.macro_editor.load_sequence(seq)


    def _on_trigger_selected(self, row: int):
        if row < 0 or row >= len(self.project.triggers):
            return
        self.macro_list.clearSelection()
        trig = self.project.triggers[row]
        self.trigger_editor.load_trigger(trig, self.project)


    # ══════════════════════════════════════════════════════════════
    #  Macro / Trigger CRUD
    # ══════════════════════════════════════════════════════════════
    def _new_macro(self):
        seq = MacroSequence()
        self.project.macros.append(seq)
        self._refresh_macro_list()
        self.macro_list.setCurrentRow(len(self.project.macros) - 1)

    def _delete_macro(self):
        row = self.macro_list.currentRow()
        if row < 0 or row >= len(self.project.macros):
            return
        self.project.macros.pop(row)
        self._refresh_macro_list()


    def _new_trigger(self):
        t = TriggerConfig()
        self.project.triggers.append(t)
        self._refresh_trigger_list()
        self.trigger_list.setCurrentRow(len(self.project.triggers) - 1)

    def _delete_trigger(self):
        row = self.trigger_list.currentRow()
        if row < 0 or row >= len(self.project.triggers):
            return
        self.project.triggers.pop(row)
        self._refresh_trigger_list()


    # ══════════════════════════════════════════════════════════════
    #  Project file I/O
    # ══════════════════════════════════════════════════════════════
    def _on_project_changed(self):
        self._refresh_macro_list()
        self._refresh_trigger_list()
        # Re-refresh trigger editor macro options
        if self.stack.currentIndex() == 2:
            self.trigger_editor._refresh_macro_combo()

    def _refresh_proj_combo(self):
        self._proj_combo_updating = True
        self._proj_combo.clear()
        
        folder = os.path.dirname(self.DEFAULT_PROJ)
        os.makedirs(folder, exist_ok=True)
        
        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        files.sort()
        if not files:
            MacroProject().save(self.DEFAULT_PROJ)
            files = ['default.json']
            
        for f in files:
            self._proj_combo.addItem(f, os.path.join(folder, f))
            
        if getattr(self, '_current_proj_path', None):
            idx = self._proj_combo.findData(self._current_proj_path)
            if idx >= 0:
                self._proj_combo.setCurrentIndex(idx)
        self._proj_combo_updating = False

    def _on_proj_combo_changed(self, idx: int):
        if getattr(self, '_proj_combo_updating', False) or idx < 0:
            return
        path = self._proj_combo.itemData(idx)
        if path and path != getattr(self, '_current_proj_path', ''):
            self._save_project()
            self._load_project(path)

    def _new_project_prompt(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, '新建配置', '输入新配置名称:', text='config')
        if ok and name:
            if not name.endswith('.json'):
                name += '.json'
            self._save_project()
            self._stop_all()
            
            self.project = MacroProject()
            path = os.path.join(os.path.dirname(self.DEFAULT_PROJ), name)
            self._current_proj_path = path
            self.project.save(path)
            
            self._refresh_proj_combo()
            self._load_project(path)

    def _save_project(self):
        p = getattr(self, '_current_proj_path', '') or self.DEFAULT_PROJ
        os.makedirs(os.path.dirname(p), exist_ok=True)
        self.project.save(p)
        self._current_proj_path = p
        if hasattr(self, '_file_lbl'):
            self._file_lbl.setText(os.path.basename(p))
        self._set_status('已保存配置', 'ok')

    def _open_project(self):
        self._save_project()
        self._stop_all()
        path, _ = QFileDialog.getOpenFileName(
            self, '打开项目', os.path.dirname(self.DEFAULT_PROJ),
            'ClaudyKey 项目 (*.json);;All Files (*)')
        if path:
            self._load_project(path)
            self._refresh_proj_combo()

    def _load_project(self, path: str):
        try:
            self.project = MacroProject.load(path)
            self._current_proj_path = path
            self._refresh_macro_list()
            self._refresh_trigger_list()
    
            self._file_lbl.setText(os.path.basename(path))
            self._register_hotkey()
            self._update_ui_for_mode()
            self._apply_saved_backend()   # restore saved input driver
            self._set_status('项目已加载', 'ok')
        except Exception as e:
            QMessageBox.critical(self, '加载失败', str(e))

    def _update_ui_for_mode(self):
        self._btn_run.setText('▶  运行当前宏')
        self._btn_stop.setText('■  停止运行')

    # ══════════════════════════════════════════════════════════════
    #  Run / Stop
    # ══════════════════════════════════════════════════════════════
    def _start_all(self):
        if self._running:
            return
        if not self.project.macros and not self.project.triggers:
            self._set_status('没有宏或触发器', 'err')
            return
        # Always clean up any surviving engine from a previous run
        if self._trigger_engine and self._trigger_engine.is_alive():
            self._trigger_engine.stop()
            self._trigger_engine = None
        self._running = True
        self._save_project()  # Auto-save changes before running
        self._btn_run.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._set_status('运行中…', 'run')

        seq = None
        row = self.macro_list.currentRow()
        if 0 <= row < len(self.project.macros):
            seq = self.project.macros[row]
        elif getattr(self.macro_editor, 'sequence', None) and self.macro_editor.sequence in self.project.macros:
            seq = self.macro_editor.sequence
        elif self.project.macros:
            seq = self.project.macros[0]
            
        if seq:
            self._append_log(f'开始运行: {seq.name}')
            self._run_macro(seq)
        else:
            self._set_status('没有要运行的宏', 'err')
            self._stop_all()

    def _run_macro(self, seq, on_done_extra=None):
        if self._executor and self._executor.is_alive():
            self._executor.stop()
        
        def done_handler():
            self._bridge.macro_done.emit()
            if on_done_extra: on_done_extra()
            
        def err_handler(e):
            self._bridge.macro_error.emit(e)
            if on_done_extra: on_done_extra()

        self._executor = MacroExecutor(
            seq,
            project=self.project,
            on_step=lambda i: self._bridge.step_changed.emit(i),
            on_done=done_handler,
            on_error=err_handler,
        )
        self._executor.start()

    def _stop_all(self):
        self._append_log('已停止')
        if self._executor:
            self._executor.stop()
            self._executor = None
        if self._trigger_engine:
            self._trigger_engine.stop()
            self._trigger_engine = None
        self._running = False
        self._btn_run.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self.macro_editor.clear_highlight()
        self._set_status('已停止', 'ok')

    # ══════════════════════════════════════════════════════════════
    #  Callbacks from background threads (via _bridge)
    # ══════════════════════════════════════════════════════════════
    def _on_step(self, idx: int):
        self.macro_editor.highlight_step(idx)

    def _on_macro_done(self):
        self._append_log('宏执行完毕')
        if self._running:
            self._set_status('宏执行完毕', 'ok')
        self._running = False
        self._btn_run.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self.macro_editor.clear_highlight()

    def _on_macro_error(self, msg: str):
        self._append_log(f'[ERROR] {msg}')
        self._set_status(f'错误: {msg}', 'err')
        self._stop_all()

    def _on_trigger_fired_bg(self, trigger: TriggerConfig):
        """Called from TriggerEngine thread."""
        self._bridge.log.emit(f'触发器命中: [{trigger.name}]')
        self._bridge.trigger_fired.emit(trigger.id)
        return self._execute_trigger_action(trigger)

    def _on_trigger_fired(self, tid: str):
        """Called on GUI thread via bridge."""
        trig = next((t for t in self.project.triggers if t.id == tid), None)
        if trig:
            self._set_status(f'触发: {trig.name}', 'run')

    def _execute_trigger_action(self, trigger: TriggerConfig) -> threading.Event:
        """Execute the trigger's configured action (called from background thread)."""
        done_event = threading.Event()
        if trigger.action_type == 'run_macro':
            mid = trigger.action_params.get('macro_id', '')
            seq = next((m for m in self.project.macros if m.id == mid), None)
            if seq:
                self._run_macro(seq, on_done_extra=done_event.set)
            else:
                done_event.set()
        elif trigger.action_type == 'click':
            bk = _ib.get_backend()
            x = trigger.action_params.get('x', 0)
            y = trigger.action_params.get('y', 0)
            bk.mouse_click(x, y, 'left')
            done_event.set()
        elif trigger.action_type == 'key':
            bk = _ib.get_backend()
            keys = [k.strip().lower() for k in trigger.action_params.get('key', '').split('+')]
            if keys:
                bk.combo(keys)
            done_event.set()
        return done_event

    # ══════════════════════════════════════════════════════════════
    #  Status bar
    # ══════════════════════════════════════════════════════════════
    def _set_status(self, msg: str, kind: str = 'ok'):
        styles = {
            'ok':  'color:#1fa357;',
            'run': 'color:#d6871a;',
            'err': 'color:#d94141;',
        }
        self._status_lbl.setText(msg)
        self._status_lbl.setStyleSheet(styles.get(kind, ''))

    def _append_log(self, msg: str):
        import datetime
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        self._log_view.append(f'<span style="color:#c490a8">[{ts}]</span> {msg}')
        # Auto-scroll to bottom
        sb = self._log_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ══════════════════════════════════════════════════════════════
    #  Input backend
    # ══════════════════════════════════════════════════════════════
    def _populate_backend_combo(self) -> None:
        """Fill the backend dropdown with available + unavailable options."""
        _ib._ensure_defaults_registered()
        self._backend_combo.blockSignals(True)
        self._backend_combo.clear()
        for cls in _ib.get_available_backends():
            label = cls.display_name()
            if not cls.is_available():
                label += ' ⚠'
            self._backend_combo.addItem(label, userData=cls.name())
        # Select current project choice
        current = getattr(self.project, 'input_backend', 'dd')
        for i in range(self._backend_combo.count()):
            if self._backend_combo.itemData(i) == current:
                self._backend_combo.setCurrentIndex(i)
                break
        self._backend_combo.blockSignals(False)

    def _on_backend_changed(self, _idx: int) -> None:
        backend_name = self._backend_combo.currentData()
        if not backend_name:
            return
        try:
            _ib.set_backend(backend_name)
            self.project.input_backend = backend_name
            self._append_log(f'输入驱动切换 → {backend_name}')
            self._on_project_changed()
        except Exception as e:
            self._append_log(f'[ERROR] 切换驱动失败: {e}')

    def _on_backend_settings(self) -> None:
        dlg = BackendSettingsDialog(self)
        dlg.exec()
        # After the dialog closes, re-check availability and repopulate
        self._populate_backend_combo()

    def _apply_saved_backend(self) -> None:
        """Called after loading a project to activate the saved backend."""
        name = getattr(self.project, 'input_backend', 'dd')
        try:
            _ib.set_backend(name)
        except Exception:
            _ib.set_backend('dd')
        self._populate_backend_combo()

    def _on_hotkey_setup(self):
        dlg = HotkeySetDialog(self)
        if dlg.exec() and dlg.result_key:
            self.project.hotkey = dlg.result_key
            self._register_hotkey()
            self._on_project_changed()

    def _register_hotkey(self):
        if getattr(self, '_listener_kb', None):
            self._listener_kb.stop()
            self._listener_kb = None
        if getattr(self, '_listener_mouse', None):
            self._listener_mouse.stop()
            self._listener_mouse = None

        def toggle():
            if self._running:
                self._bridge.macro_done.emit()  # reuse signal to stop
                self._stop_all()
            else:
                self._start_all()

        key_conf = self.project.hotkey
        if not key_conf.startswith('key:') and not key_conf.startswith('mouse:'):
            key_conf = f"key:<{key_conf.strip('<>')}>"
            self.project.hotkey = key_conf

        try:
            if key_conf.startswith('key:'):
                k = key_conf[4:]
                self._listener_kb = pynput_kb.GlobalHotKeys({k: toggle})
                self._listener_kb.start()
            elif key_conf.startswith('mouse:'):
                m = key_conf[6:]
                def on_click(x, y, button, pressed):
                    if pressed and button.name == m:
                        toggle()
                self._listener_mouse = pynput_mouse.Listener(on_click=on_click)
                self._listener_mouse.start()

            # Update UI labels
            display = key_conf.replace('key:', '').replace('mouse:', 'Mouse ').upper().strip('<>')
            self._btn_run.setText(f'▶  运行  ({display})')
            self._btn_stop.setText(f'■  停止  ({display})')
            self._hotkey_btn.setText(f'设置: {display}')
            self._hotkey_lbl.setText(f'全局热键: {display} 开始 / 停止')
        except Exception as e:
            self._set_status(f"热键绑定失败: {e}", "err")

    # ══════════════════════════════════════════════════════════════
    #  Window close
    # ══════════════════════════════════════════════════════════════
    def closeEvent(self, event):
        self._stop_all()
        self._save_project()
        event.accept()
