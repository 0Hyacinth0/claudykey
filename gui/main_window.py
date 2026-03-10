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
    QInputDialog, QComboBox, QDialog, QTextEdit, QMenu
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
            self._new_macro()

    # ══════════════════════════════════════════════════════════════
    #  UI construction
    # ══════════════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════════════
    #  UI construction
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        self.is_dark_mode = False
        from gui.theme import get_theme_qss
        self.setStyleSheet(get_theme_qss(self.is_dark_mode))

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_main_area(), 1)

    def _build_sidebar(self) -> QFrame:
        side = QFrame()
        side.setObjectName('sidebar')
        side.setFixedWidth(200)
        
        lay = QVBoxLayout(side)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Mac Traffic Lights
        mac_lay = QHBoxLayout()
        mac_lay.setSpacing(8)
        mac_red = QPushButton(objectName='mac_red')
        mac_red.setFixedSize(12, 12)
        mac_yel = QPushButton(objectName='mac_yel')
        mac_yel.setFixedSize(12, 12)
        mac_grn = QPushButton(objectName='mac_grn')
        mac_grn.setFixedSize(12, 12)
        mac_lay.addWidget(mac_red)
        mac_lay.addWidget(mac_yel)
        mac_lay.addWidget(mac_grn)
        mac_lay.addStretch()
        lay.addLayout(mac_lay)
        lay.addSpacing(16)

        # Nav Buttons
        self._btn_run = QPushButton('▶  运行模式', objectName='btn_nav')
        self._btn_run.setCheckable(True)
        self._btn_run.clicked.connect(self._toggle_run_state)
        
        self._btn_hk = QPushButton('⌨  全局热键', objectName='btn_nav')
        self._btn_hk.clicked.connect(self._on_hotkey_setup)
        
        self._btn_drv = QPushButton('⚙  驱动设置', objectName='btn_nav')
        self._btn_drv.clicked.connect(self._on_backend_settings)

        self._btn_theme = QPushButton('🌗  切换主题', objectName='btn_nav')
        self._btn_theme.clicked.connect(self._toggle_theme)

        lay.addWidget(self._btn_run)
        lay.addWidget(self._btn_hk)
        lay.addWidget(self._btn_drv)
        lay.addWidget(self._btn_theme)
        
        lay.addStretch()

        # Bottom MACRO MANAGEMENT
        self._btn_nav_macro = QPushButton('📂\\n宏管理')
        self._btn_nav_macro.setObjectName('btn_macro_mgr')
        self._btn_nav_macro.setFixedHeight(80)
        lay.addWidget(self._btn_nav_macro)

        return side

    def _toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        from gui.theme import get_theme_qss
        self.setStyleSheet(get_theme_qss(self.is_dark_mode))

    def _toggle_run_state(self):
        if self._running:
            self._stop_all()
            self._btn_run.setChecked(False)
        else:
            self._start_all()
            self._btn_run.setChecked(True)

    def _build_main_area(self) -> QWidget:
        w = QWidget()
        right_lay = QVBoxLayout(w)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(16)

        # Upper Area
        split_lay = QHBoxLayout()
        split_lay.setSpacing(16)

        # --- Macro List Column ---
        m_list_cont = QFrame(objectName='macros_panel')
        m_list_cont.setFixedWidth(240)
        ml_lay = QVBoxLayout(m_list_cont)
        ml_lay.setContentsMargins(12, 12, 12, 12)
        
        m_hdr = QHBoxLayout()
        ml_lbl = QLabel('宏列表', objectName='lbl_title')
        m_menu = QPushButton('⋮', objectName='btn_icon_tool')
        m_hdr.addWidget(ml_lbl, 1)
        m_hdr.addWidget(m_menu)
        ml_lay.addLayout(m_hdr)

        mac_menu = QMenu(self)
        mac_menu.addAction('新建宏').triggered.connect(self._new_macro)
        mac_menu.addAction('删除宏').triggered.connect(self._delete_macro)
        m_menu.setMenu(mac_menu)
        m_menu.setStyleSheet("QPushButton::menu-indicator { image: none; }")

        self.macro_list = QListWidget()
        self.macro_list.currentRowChanged.connect(self._on_macro_selected)
        ml_lay.addWidget(self.macro_list, 1)
        split_lay.addWidget(m_list_cont)

        # --- Macro Editor Column ---
        m_editor_cont = QFrame(objectName='editor_panel')
        me_lay = QVBoxLayout(m_editor_cont)
        me_lay.setContentsMargins(0, 0, 0, 0)
        
        self.macro_editor = MacroEditorPanel()
        self.macro_editor.changed.connect(self._on_project_changed)
        # Note: we embed our current editor but its QSS will style it like the mockup.
        me_lay.addWidget(self.macro_editor, 1)
        
        split_lay.addWidget(m_editor_cont, 1)

        # We keep stack for trig list compatibility but it's not strictly 1:1 if we expose it
        self.stack = QStackedWidget()
        macro_page = QWidget()
        mp_lay = QVBoxLayout(macro_page)
        mp_lay.setContentsMargins(0,0,0,0)
        mp_lay.addLayout(split_lay)
        self.stack.addWidget(macro_page)
        self.stack.setCurrentIndex(0)
        
        # We need the trigger list to exist logically so the app doesn't crash on getattr
        self.trigger_list = QListWidget()
        self.trigger_editor = TriggerEditorPanel()

        right_lay.addWidget(self.stack, 1)

        # --- Bottom Status Bar ---
        stat_bar = QFrame(objectName='status_bar')
        stat_bar.setFixedHeight(40)
        stat_lay = QHBoxLayout(stat_bar)
        stat_lay.setContentsMargins(16, 0, 16, 0)

        stat_lay.addWidget(QLabel('运行日志', styleSheet='font-weight: bold;'))
        self._log_lbl = QLabel('等待中...')
        stat_lay.addWidget(self._log_lbl)
        
        stat_lay.addStretch()
        self._file_lbl = QLabel('配置文件已加载')
        stat_lay.addWidget(self._file_lbl)
        
        stat_lay.addStretch()
        self._hotkey_lbl = QLabel('全局热键: 未设置')
        stat_lay.addWidget(self._hotkey_lbl)

        right_lay.addWidget(stat_bar)
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
        self._set_status('已自动保存', 'ok')

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

    def _set_mode(self, mode: str):
        if self._running:
            return
        self.project.mode = mode
        self._update_ui_for_mode()
        self._on_project_changed()

    def _update_ui_for_mode(self):
        m = self.project.mode
        if m == 'loop':
            self._btn_run.setText('▶  运行模式')
        else:
            self._btn_run.setText('▷  巡检模式')

    # ══════════════════════════════════════════════════════════════
    #  Run / Stop
    # ══════════════════════════════════════════════════════════════
    def _start_all(self):
        if self._running:
            return
        if not self.project.macros and not self.project.triggers:
            self._set_status('没有宏或触发器', 'err')
            self._btn_run.setChecked(False)
            return
        # Always clean up any surviving engine from a previous run
        if self._trigger_engine and self._trigger_engine.is_alive():
            self._trigger_engine.stop()
            self._trigger_engine = None
        self._running = True
        self._save_project()  # Auto-save changes before running
        self._btn_run.setText('⏹  停止运行')
        self._set_status('运行中…', 'run')

        if self.project.mode == 'conditional':
            enabled = [t for t in self.project.triggers if t.enabled]
            if enabled:
                self._append_log(f'开始巡检，共 {len(enabled)} 个触发器启用')
                self._trigger_engine = TriggerEngine(
                    enabled, self._on_trigger_fired_bg)
                self._trigger_engine.start()
            else:
                self._set_status('条件模式下没有启用的触发器', 'err')
                self._stop_all()
        else:
            # Loop mode: run exactly the chosen macro
            seq = None
            row = self.macro_list.currentRow()
            if 0 <= row < len(self.project.macros):
                seq = self.project.macros[row]
            elif getattr(self.macro_editor, 'sequence', None) and self.macro_editor.sequence in self.project.macros:
                seq = self.macro_editor.sequence
            elif self.project.macros:
                seq = self.project.macros[0]
                
            if seq:
                self._append_log(f'循环模式启动: {seq.name}')
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
        self._btn_run.setChecked(False)
        self._btn_run.setText('▶  运行模式' if self.project.mode == 'loop' else '▷  巡检模式')
        self.macro_editor.clear_highlight()
        self._set_status('已停止', 'ok')

    # ══════════════════════════════════════════════════════════════
    #  Callbacks from background threads (via _bridge)
    # ══════════════════════════════════════════════════════════════
    def _on_step(self, idx: int):
        self.macro_editor.highlight_step(idx)

    def _on_macro_done(self):
        # In conditional mode the TriggerEngine drives execution;
        # we should NOT reset the running state — the engine keeps going.
        in_conditional = (self.project.mode == 'conditional'
                          and self._trigger_engine is not None
                          and self._trigger_engine.is_alive())
        if in_conditional:
            self._append_log('宏执行完毕 — 继续巡检...')
            self._set_status('宏完成，巡检中…', 'run')
            self.macro_editor.clear_highlight()
        else:
            self._append_log('宏执行完毕')
            if self._running:
                self._set_status('宏执行完毕', 'ok')
            self._running = False
            self._btn_run.setChecked(False)
            self._btn_run.setText('▶  运行模式' if self.project.mode == 'loop' else '▷  巡检模式')
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
        pass  # We don't have a dedicated status text lbl like before, we use _log_lbl

    def _append_log(self, msg: str):
        import datetime
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        self._log_lbl.setText(f'[{ts}] {msg}')

    # ══════════════════════════════════════════════════════════════
    #  Input backend
    # ══════════════════════════════════════════════════════════════



    def _on_backend_settings(self) -> None:
        dlg = BackendSettingsDialog(self)
        dlg.exec()
        current = _ib.get_active_name()
        if getattr(self.project, 'input_backend', '') != current:
            self.project.input_backend = current
            self._append_log(f'输入驱动切换 → {current}')
            self._on_project_changed()

    def _apply_saved_backend(self) -> None:
        """Called after loading a project to activate the saved backend."""
        name = getattr(self.project, 'input_backend', 'dd')
        try:
            _ib.set_backend(name)
        except Exception:
            _ib.set_backend('dd')

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
            self._btn_hk.setText(f'⌨  全局热键 ({display})')
            self._hotkey_lbl.setText(f'全局热键: {display}')
        except Exception as e:
            self._append_log(f"热键绑定失败: {e}")

    # ══════════════════════════════════════════════════════════════
    #  Window close
    # ══════════════════════════════════════════════════════════════
    def closeEvent(self, event):
        self._stop_all()
        self._save_project()
        event.accept()
