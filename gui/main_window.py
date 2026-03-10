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
from gui.macro_editor import MacroEditorPanel
from gui.trigger_editor import TriggerEditorPanel
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
            self._new_macro()

    # ══════════════════════════════════════════════════════════════
    #  UI construction
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_toolbar())
        root.addWidget(self._build_body(), 1)
        root.addWidget(self._build_statusbar())

    def _build_toolbar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName('toolbar')
        bar.setFixedHeight(60)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(10)

        # Logo
        logo = QLabel('⌨  ClaudyKey')
        logo.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        logo.setStyleSheet('color: qlineargradient(x1:0,y1:0,x2:1,y2:0,'
                           'stop:0 #d15c89, stop:1 #a855f7);'
                           'font-size:16px; font-weight:900; letter-spacing:1px;'
                           'color:#d15c89;')
        lay.addWidget(logo)
        lay.addSpacing(24)

        # ── Mode Selector ──
        mode_lay = QHBoxLayout()
        mode_lay.setSpacing(0)
        self._btn_mode_loop = QPushButton('🔁 循环模式')
        self._btn_mode_cond = QPushButton('🔍 条件模式')
        self._btn_mode_loop.setCheckable(True)
        self._btn_mode_cond.setCheckable(True)
        
        # Style them like a toggle group
        self._btn_mode_loop.setStyleSheet('''
            QPushButton { border-top-right-radius: 0; border-bottom-right-radius: 0; border-right: none; }
            QPushButton:checked { background: rgba(251,191,213,0.85); color: white; border-color: rgba(255,255,255,0.6); }
        ''')
        self._btn_mode_cond.setStyleSheet('''
            QPushButton { border-top-left-radius: 0; border-bottom-left-radius: 0; }
            QPushButton:checked { background: rgba(251,191,213,0.85); color: white; border-color: rgba(255,255,255,0.6); }
        ''')
        
        self._btn_mode_loop.clicked.connect(lambda: self._set_mode('loop'))
        self._btn_mode_cond.clicked.connect(lambda: self._set_mode('conditional'))
        
        mode_lay.addWidget(self._btn_mode_loop)
        mode_lay.addWidget(self._btn_mode_cond)
        lay.addLayout(mode_lay)
        lay.addSpacing(24)

        # ── Control group ──
        self._btn_run = QPushButton('▶  运行')
        self._btn_run.setObjectName('btn_run')
        self._btn_run.clicked.connect(self._start_all)

        self._btn_stop = QPushButton('■  停止')
        self._btn_stop.setObjectName('btn_stop')
        self._btn_stop.clicked.connect(self._stop_all)
        self._btn_stop.setEnabled(False)

        lay.addWidget(self._btn_run)
        lay.addWidget(self._btn_stop)
        lay.addSpacing(16)

        # ── Hotkey ──
        hk_lbl = QLabel('⚡ 快捷键')
        hk_lbl.setStyleSheet('color:#a0889a; font-size:12px;')
        lay.addWidget(hk_lbl)
        self._hotkey_btn = QPushButton('设置: F9')
        self._hotkey_btn.setToolTip('点击设置全局启动/停止的热键')
        self._hotkey_btn.clicked.connect(self._on_hotkey_setup)
        self._hotkey_btn.setFixedWidth(120)
        lay.addWidget(self._hotkey_btn)

        lay.addStretch()

        # ── File buttons ──
        for label, tip, slot in [
            ('📂 打开', '打开项目', self._open_project),
            ('💾 保存', '保存项目', self._save_project),
            ('📄 新建', '新建项目', self._new_project),
        ]:
            b = QPushButton(label)
            b.setToolTip(tip)
            b.clicked.connect(slot)
            lay.addWidget(b)

        return bar

    def _build_body(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(5)
        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_editor_area())
        splitter.setSizes([250, 850])
        return splitter

    def _build_sidebar(self) -> QFrame:
        side = QFrame()
        side.setObjectName('sidebar')
        side.setFixedWidth(240)
        lay = QVBoxLayout(side)
        lay.setContentsMargins(12, 14, 12, 12)
        lay.setSpacing(6)

        # ── Macro list ──
        macro_hdr = QHBoxLayout()
        lbl = QLabel('宏 MACROS')
        lbl.setObjectName('lbl_section')
        btn_add_macro = QPushButton('＋')
        btn_add_macro.setObjectName('btn_icon')
        btn_add_macro.setFixedSize(24, 24)
        btn_add_macro.setToolTip('新建宏')
        btn_add_macro.clicked.connect(self._new_macro)
        btn_del_macro = QPushButton('－')
        btn_del_macro.setObjectName('btn_icon')
        btn_del_macro.setFixedSize(24, 24)
        btn_del_macro.setToolTip('删除宏')
        btn_del_macro.clicked.connect(self._delete_macro)
        macro_hdr.addWidget(lbl, 1)
        macro_hdr.addWidget(btn_add_macro)
        macro_hdr.addWidget(btn_del_macro)
        lay.addLayout(macro_hdr)

        self.macro_list = QListWidget()
        self.macro_list.currentRowChanged.connect(self._on_macro_selected)
        lay.addWidget(self.macro_list, 1)

        # ── Trigger list ──
        self._trigger_container = QWidget()
        trig_lay = QVBoxLayout(self._trigger_container)
        trig_lay.setContentsMargins(0, 0, 0, 0)

        trig_hdr = QHBoxLayout()
        lbl2 = QLabel('触发器 TRIGGERS')
        lbl2.setObjectName('lbl_section')
        btn_add_trig = QPushButton('＋')
        btn_add_trig.setObjectName('btn_icon')
        btn_add_trig.setFixedSize(24, 24)
        btn_add_trig.setToolTip('新建触发器')
        btn_add_trig.clicked.connect(self._new_trigger)
        btn_del_trig = QPushButton('－')
        btn_del_trig.setObjectName('btn_icon')
        btn_del_trig.setFixedSize(24, 24)
        btn_del_trig.setToolTip('删除触发器')
        btn_del_trig.clicked.connect(self._delete_trigger)
        trig_hdr.addWidget(lbl2, 1)
        trig_hdr.addWidget(btn_add_trig)
        trig_hdr.addWidget(btn_del_trig)
        trig_lay.addLayout(trig_hdr)

        self.trigger_list = QListWidget()
        self.trigger_list.setMinimumHeight(80)
        self.trigger_list.currentRowChanged.connect(self._on_trigger_selected)
        trig_lay.addWidget(self.trigger_list, 1)

        lay.addWidget(self._trigger_container, 1)

        return side

    def _build_editor_area(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(6)

        self.stack = QStackedWidget()

        # Page 0: placeholder
        placeholder = QLabel('← 从左侧选择宏或触发器')
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet('color:rgba(160,100,135,0.5);font-size:16px;font-weight:bold;')
        self.stack.addWidget(placeholder)

        # Page 1: macro editor
        self.macro_editor = MacroEditorPanel()
        self.macro_editor.changed.connect(self._on_project_changed)
        self.stack.addWidget(self.macro_editor)

        # Page 2: trigger editor
        self.trigger_editor = TriggerEditorPanel()
        self.trigger_editor.changed.connect(self._on_project_changed)
        self.stack.addWidget(self.trigger_editor)

        outer.addWidget(self.stack, 1)

        # ── Log panel ──
        log_hdr = QHBoxLayout()
        log_lbl = QLabel('📜 运行日志')
        log_lbl.setObjectName('lbl_section')
        self._btn_clear_log = QPushButton('清空')
        self._btn_clear_log.setFixedWidth(48)
        self._btn_clear_log.setObjectName('btn_icon')
        self._btn_clear_log.clicked.connect(lambda: self._log_view.clear())
        log_hdr.addWidget(log_lbl, 1)
        log_hdr.addWidget(self._btn_clear_log)
        outer.addLayout(log_hdr)

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setFixedHeight(120)
        self._log_view.setObjectName('log_view')
        self._log_view.setStyleSheet(
            '#log_view { background: rgba(30,10,20,0.55); '
            'color: #e8b4cc; border-radius: 8px; '
            'font-family: Consolas, monospace; font-size: 11px; '
            'border: 1px solid rgba(200,130,170,0.25); }'
        )
        outer.addWidget(self._log_view)

        return w

    def _build_statusbar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName('statusbar_frame')
        bar.setFixedHeight(32)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(18, 0, 18, 0)
        self._status_lbl = QLabel('就绪')
        self._status_lbl.setObjectName('lbl_status_ok')
        self._hotkey_lbl = QLabel('全局热键: 未知')
        self._hotkey_lbl.setStyleSheet('color: rgba(140, 110, 125, 0.6); font-size: 11px;')
        self._file_lbl = QLabel('')
        self._file_lbl.setStyleSheet('color: rgba(140, 110, 125, 0.6); font-size: 11px;')
        lay.addWidget(self._status_lbl)
        lay.addStretch()
        lay.addWidget(self._file_lbl)
        lay.addWidget(self._hotkey_lbl)
        return bar

    # ══════════════════════════════════════════════════════════════
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
        self.stack.setCurrentIndex(1)

    def _on_trigger_selected(self, row: int):
        if row < 0 or row >= len(self.project.triggers):
            return
        self.macro_list.clearSelection()
        trig = self.project.triggers[row]
        self.trigger_editor.load_trigger(trig, self.project)
        self.stack.setCurrentIndex(2)

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
        self.stack.setCurrentIndex(0)

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
        self.stack.setCurrentIndex(0)

    # ══════════════════════════════════════════════════════════════
    #  Project file I/O
    # ══════════════════════════════════════════════════════════════
    def _on_project_changed(self):
        self._refresh_macro_list()
        self._refresh_trigger_list()
        # Re-refresh trigger editor macro options
        if self.stack.currentIndex() == 2:
            self.trigger_editor._refresh_macro_combo()

    def _new_project(self):
        self._stop_all()
        self.project = MacroProject()
        self._current_proj_path = ''
        self._refresh_macro_list()
        self._refresh_trigger_list()
        self.stack.setCurrentIndex(0)
        self._file_lbl.setText('')
        self._register_hotkey()
        self._new_macro()

    def _save_project(self):
        if not self._current_proj_path:
            path, _ = QFileDialog.getSaveFileName(
                self, '保存项目', self.DEFAULT_PROJ,
                'ClaudyKey 项目 (*.json);;All Files (*)')
            if not path:
                return
            self._current_proj_path = path
        os.makedirs(os.path.dirname(self._current_proj_path), exist_ok=True)
        self.project.save(self._current_proj_path)
        self._file_lbl.setText(os.path.basename(self._current_proj_path))
        self._set_status('已保存', 'ok')

    def _open_project(self):
        self._stop_all()
        path, _ = QFileDialog.getOpenFileName(
            self, '打开项目', '',
            'ClaudyKey 项目 (*.json);;All Files (*)')
        if path:
            self._load_project(path)

    def _load_project(self, path: str):
        try:
            self.project = MacroProject.load(path)
            self._current_proj_path = path
            self._refresh_macro_list()
            self._refresh_trigger_list()
            self.stack.setCurrentIndex(0)
            self._file_lbl.setText(os.path.basename(path))
            self._register_hotkey()
            self._update_ui_for_mode()
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
        self._btn_mode_loop.setChecked(m == 'loop')
        self._btn_mode_cond.setChecked(m == 'conditional')
        
        # Toggle trigger container visibility
        if hasattr(self, '_trigger_container'):
            self._trigger_container.setVisible(m == 'conditional')
            
        if m == 'loop':
            self._btn_run.setText('▶  开始循环')
            self._btn_stop.setText('■  停止循环')
            # If a trigger was selected, switch to macro 0 or empty to keep UI clean
            if self.stack.currentWidget() == self.trigger_editor:
                self.trigger_list.clearSelection()
                if self.project.macros:
                    self.macro_list.setCurrentRow(0)
                else:
                    self.stack.setCurrentIndex(0)
        else:
            self._btn_run.setText('🔍  开始巡检')
            self._btn_stop.setText('■  停止巡检')

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
        self._btn_run.setEnabled(False)
        self._btn_stop.setEnabled(True)
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
            from pynput.mouse import Controller as MC, Button
            mc = MC()
            x = trigger.action_params.get('x', 0)
            y = trigger.action_params.get('y', 0)
            mc.position = (x, y)
            mc.click(Button.left)
            done_event.set()
        elif trigger.action_type == 'key':
            from pynput.keyboard import Controller as KC
            from core.executor import _KEY_MAP
            kc = KC()
            keys = [_KEY_MAP.get(k.strip().lower(), k.strip())
                    for k in trigger.action_params.get('key', '').split('+')]
            if keys:
                for k in keys[:-1]:
                    kc.press(k)
                kc.press(keys[-1])
                kc.release(keys[-1])
                for k in reversed(keys[:-1]):
                    kc.release(k)
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
